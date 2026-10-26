"""Consumo regional e efeitos persistentes da regra canônica de Fome/Sede."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verify_campaign_player02 import execute as execute_cistern
from system import NPCS, World


class RegionalNeedsTests(unittest.TestCase):
    @staticmethod
    def migrated_seed22():
        player, _ = execute_cistern(22)
        player.game.transition_to_last_transmission()
        return player.game.world

    def test_migration_preserves_hunger_wounds_health_and_shelter_indicators(self):
        player, _ = execute_cistern(22)
        cistern = player.game.cistern
        expected_people = {person["id"]:person for person in cistern.people}
        player.game.transition_to_last_transmission()
        world = player.game.world
        self.assertEqual(world.shelter_health, cistern.health)
        self.assertEqual(world.shelter_morale, cistern.morale)
        for hero_id in player.game.founders:
            source = expected_people[hero_id]
            hero = world.heroes[hero_id]
            self.assertEqual(hero["health"], 3-source["wounds"])
            self.assertEqual(hero["wounds"], source["wounds"])
            self.assertEqual(hero["hungry"], source["hungry"])
            self.assertEqual(hero["thirsty"], source["thirsty"])
            self.assertEqual(hero["streak"], source["streak"])

    def test_shortage_requires_player_allocation_and_is_atomic(self):
        world = self.migrated_seed22()
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, "distribuição explícita"):
            world.end_day()
        self.assertEqual(world, before)

    def test_food_shortage_assigns_hunger_without_creating_or_losing_portions(self):
        world = self.migrated_seed22()
        people = sorted(world.meal_people())
        self.assertEqual(set(people), {"ZC-HER-0001", "ZC-HER-0003", "R01"})
        plan = {"food_priority": ["ZC-HER-0001", *[p for p in people if p != "ZC-HER-0001"]],
                "water_priority": people}
        result = world.end_day(meal_plan=plan)
        self.assertEqual(result["missing"], {"food": 2, "water": 0})
        self.assertEqual(result["unfed"]["food"], ["R01", "ZC-HER-0003"])
        self.assertEqual(world.stock["food"], 0)
        self.assertFalse(world.heroes["ZC-HER-0001"]["hungry"])
        self.assertTrue(world.heroes["ZC-HER-0003"]["hungry"])
        self.assertTrue(next(p for p in world.continuity_people
                             if p["id"] == "R01")["hungry"])
        self.assertFalse(world.heroes["ZC-HER-0003"]["thirsty"])
        world.begin_round()
        self.assertEqual(world.heroes["ZC-HER-0001"]["actions"], 3)
        self.assertEqual(world.heroes["ZC-HER-0003"]["actions"], 2)

    def test_second_consecutive_deprived_night_causes_one_wound_and_save_load_keeps_it(self):
        world = self.migrated_seed22()
        people = sorted(world.meal_people())
        first = {"food_priority": ["ZC-HER-0001", *[p for p in people if p != "ZC-HER-0001"]],
                 "water_priority": people}
        world.end_day(meal_plan=first)
        second = {"food_priority": people, "water_priority": people}
        world.end_day(meal_plan=second)
        self.assertEqual(world.heroes["ZC-HER-0003"]["health"], 2)
        self.assertEqual(world.heroes["ZC-HER-0003"]["wounds"], 1)
        civilian = next(p for p in world.continuity_people if p["id"] == "R01")
        self.assertEqual(civilian["wounds"], 1)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "world.json"
            world.save(path)
            restored = World.load(path)
        self.assertEqual(restored, world)

    def test_fully_fed_night_clears_conditions_and_streak(self):
        world = self.migrated_seed22()
        people = sorted(world.meal_people())
        world.heroes["ZC-HER-0001"]["hungry"] = True
        world.heroes["ZC-HER-0001"]["thirsty"] = True
        world.heroes["ZC-HER-0001"]["streak"] = 2
        world.heroes["ZC-HER-0001"]["wounds"] = 1
        world.heroes["ZC-HER-0001"]["health"] = 2
        world.stock["food"] = len(people)
        world.stock["water"] = len(people)
        result = world.end_day(meal_plan={"food_priority":people,
                                          "water_priority":people})
        self.assertEqual(result["missing"], {"food": 0, "water": 0})
        hero = world.heroes["ZC-HER-0001"]
        self.assertFalse(hero["hungry"])
        self.assertFalse(hero["thirsty"])
        self.assertEqual(hero["streak"], 0)

    def test_three_deprived_nights_trigger_shelter_collapse_threshold(self):
        world = World.new(7, ["ZC-HER-0001"], {"food":0, "water":1})
        person = next(iter(world.heroes))
        last = None
        for _ in range(3):
            last = world.end_day(meal_plan={"food_priority":[person],
                                            "water_priority":[person]})
        self.assertEqual(world.shelter_health, 0)
        self.assertTrue(world.partial_defeat)
        self.assertTrue(last["partial_defeat"])
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, "Evacuação"):
            world.end_day(meal_plan={"food_priority":[person],
                                     "water_priority":[person]})
        self.assertEqual(world, before)

    def test_deprivation_never_overwrites_injuries_already_taken_in_combat(self):
        world = World.new(13, ["ZC-HER-0001"], {"food":0,"water":1})
        hero = "ZC-HER-0001"
        world.receive_damage(hero, 2)
        self.assertEqual(world.heroes[hero]["wounds"], 2)
        world.heroes[hero]["streak"] = 1
        world.end_day(meal_plan={"food_priority":[hero],
                                 "water_priority":[hero]})
        self.assertEqual(world.heroes[hero]["health"], 0)
        self.assertEqual(world.heroes[hero]["wounds"], 3)

    def test_legacy_incapacitated_save_cannot_be_revived_by_deprivation(self):
        world = World.new(14, ["ZC-HER-0001"], {"food":0,"water":1})
        hero = "ZC-HER-0001"
        # Legacy structurally valid save can have HP without the new mirror.
        world.heroes[hero].update(health=0, wounds=0, streak=1)
        world.end_day(meal_plan={"food_priority":[hero],
                                 "water_priority":[hero]})
        self.assertEqual(world.heroes[hero]["health"], 0)
        self.assertEqual(world.heroes[hero]["wounds"], 3)

    def test_zero_shelter_health_stops_integrated_campaign_at_partial_defeat(self):
        player, _ = execute_cistern(22)
        campaign = player.game
        campaign.transition_to_last_transmission()
        campaign.world.shelter_health = 0  # Unit fixture; no replay victory is claimed.
        order = sorted(campaign.world.meal_people())
        campaign.advance_day(meal_plan={"food_priority":order,
                                        "water_priority":order})
        self.assertEqual(campaign.status, "DEFEAT")
        self.assertEqual(campaign.terminal_reason,
                         "derrota_parcial; evacuação da campanha pendente")

    def test_invalid_priority_does_not_advance_day_or_spend_stock(self):
        world = World.new(8, ["ZC-HER-0001"], {"food":0, "water":1})
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, "cada consumidor uma vez"):
            world.end_day(meal_plan={"food_priority":[], "water_priority":[]})
        self.assertEqual(world, before)

    def test_hunger_thirst_and_fatigue_stack_but_never_reduce_below_one_pa(self):
        world = World.new(10, ["ZC-HER-0001"], {"food":1, "water":1})
        hero = world.heroes["ZC-HER-0001"]
        hero.update(hungry=True, thirsty=True, fatigue=2)
        world.begin_round()
        self.assertEqual(hero["actions"], 1)

    def test_dog_alert_is_suppressed_by_deprivation_and_returns_when_fed(self):
        world = World.new(11, ["ZC-HER-0001"], {"food":1, "water":2})
        world.continuity_people = [{"id":"DOG-01", "kind":"dog"}]
        hero = "ZC-HER-0001"
        ids = [hero, "DOG-01"]
        world.end_day(meal_plan={"food_priority":ids,"water_priority":ids})
        dog = world.continuity_people[0]
        self.assertTrue(dog["hungry"])
        self.assertFalse(dog["alert"])
        world.stock.update(food=2, water=2)
        world.end_day(meal_plan={"food_priority":ids,"water_priority":ids})
        self.assertFalse(dog["hungry"])
        self.assertTrue(dog["alert"])

    def test_deprived_npc_cannot_work_or_produce_before_next_meal(self):
        world = World.new(12, ["ZC-HER-0001"], {"food":5,"water":5})
        self.assertTrue(world.recruit("EXP-NPC-05"))
        world.assign("EXP-NPC-05", "farming")
        world.npcs["EXP-NPC-05"]["hungry"] = True
        with self.assertRaisesRegex(ValueError, "sem condição física"):
            world.assign("EXP-NPC-05", "farming")
        order = sorted(world.meal_people())
        result = world.end_day(meal_plan={"food_priority":order,
                                          "water_priority":order})
        self.assertEqual(result["produced"]["food"], 0)

    def test_npc_medical_automation_keeps_health_and_wounds_consistent(self):
        world = World.new(15, ["ZC-HER-0001"],
                          {"food":4,"water":4,"medicine":1})
        hero = "ZC-HER-0001"
        world._set_hero_health(hero, 2)
        world.worked_today.append(hero)  # Isola a cura do NPC do descanso normal.
        npc_id = next(identifier for identifier, profile in NPCS.items()
                      if profile["output"] == "rescue")
        world.recruit(npc_id)
        world.assign(npc_id, NPCS[npc_id]["job"])
        order = sorted(world.meal_people())
        world.end_day(meal_plan={"food_priority":order,
                                 "water_priority":order})
        self.assertEqual(world.heroes[hero]["health"], 3)
        self.assertEqual(world.heroes[hero]["wounds"], 0)

    def test_fed_civilian_resting_recovers_wound_without_health_field(self):
        world = World.new(18, ["ZC-HER-0001"], {"food":2,"water":2})
        world.continuity_people = [{"id":"CIV-01", "kind":"adult", "wounds":1,
                                    "hungry":False, "thirsty":False, "streak":0}]
        result = world.end_day(meal_plan={"food_priority":["CIV-01", "ZC-HER-0001"],
                                          "water_priority":["CIV-01", "ZC-HER-0001"]})
        self.assertEqual(result["missing"], {"food":0,"water":0})
        self.assertEqual(world.continuity_people[0]["wounds"], 0)

    def test_old_save_adds_wound_mirror_without_changing_health(self):
        world = World.new(16, ["ZC-HER-0001"], {"food":2,"water":2})
        world._set_hero_health("ZC-HER-0001", 1)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "world.json"
            world.save(path)
            import json
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["schema"] = 1
            for state in payload["heroes"].values():
                for field in ("wounds", "hungry", "thirsty", "streak"):
                    state.pop(field, None)
            path.write_text(json.dumps(payload), encoding="utf-8")
            restored = World.load(path)
        hero = restored.heroes["ZC-HER-0001"]
        self.assertEqual(hero["health"], 1)
        self.assertEqual(hero["wounds"], 2)
        self.assertFalse(hero["hungry"])

    def test_save_rejects_inconsistent_health_and_wound_mirror(self):
        world = World.new(17, ["ZC-HER-0001"], {"food":2,"water":2})
        world.heroes["ZC-HER-0001"]["health"] = 1
        with self.assertRaisesRegex(ValueError, "Herói inválido"):
            world.validate()


if __name__ == "__main__":
    unittest.main()
