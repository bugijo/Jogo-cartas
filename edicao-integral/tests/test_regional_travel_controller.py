"""Controlador regional resolvendo cartas de Viagem e Emboscadas."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from regional_player import AdaptiveRegionalPlayer
from travel_deck02 import CARD_IDS, TravelDeck02
from verify_campaign_player02 import execute as execute_cistern

MARKET = ("EXP-LOC-02", "market_intro", {"kind": "search", "zone": 5})


def migrated(first: list[str]):
    player, _ = execute_cistern(22)
    player.game.transition_to_last_transmission()
    world = player.game.world
    world.regional_travel_cards = True
    rest = [card for card in CARD_IDS if card not in first]
    world.regional_travel_deck = TravelDeck02(world.seed, first + rest, []).snapshot()
    return world


def run(world, player=None):
    player = player or AdaptiveRegionalPlayer("explorer")
    destination, map_id, objective = MARKET
    return player, player.run_expedition(world, "e1", destination, sorted(world.heroes),
                                         map_id, objective, max_steps=40)


class RegionalTravelControllerTests(unittest.TestCase):
    def test_choice_cards_use_only_options_without_carried_cargo(self):
        world = migrated(["ZC-VIA-0002", "ZC-VIA-0004"])
        player, result = run(world)
        self.assertEqual(result["status"], "returned")
        choices = [(row["card"], row["choice"]) for row in player.history
                   if row["action"] == "travel_choice"]
        self.assertEqual(choices, [("ZC-VIA-0002", "fatigue"), ("ZC-VIA-0004", "pressure")])
        self.assertEqual(world.regional_travel_archive["pressure"], 1)

    def test_ambush_attacks_roll_world_dice_and_trip_continues(self):
        world = migrated(["ZC-VIA-0005", "ZC-VIA-0001"])
        rng_before = world.rng_state
        original = world.start_regional_ambush

        def start_with_enemy_at_entry(expedition_id):
            ambush = original(expedition_id)
            ambush.enemies[0]["zone"] = 1  # fixture: força combate na entrada
            world.store_regional_ambush(expedition_id, ambush)
            return ambush

        world.start_regional_ambush = start_with_enemy_at_entry
        player, result = run(world)
        attacks = [row for row in world.log if row.get("action") == "regional_ambush_attack"]
        self.assertTrue(attacks)
        self.assertTrue(all(1 <= row["die"] <= 6 for row in attacks))
        self.assertNotEqual(world.rng_state, rng_before)
        self.assertIn(result["status"], ("returned", "returned_with_objective_incomplete"))
        self.assertEqual(player.history[0]["action"], "regional_ambush")

    def test_regional_ambush_does_not_consume_durability(self):
        # Decisão aprovada em 2026-10-29: o M1 da 0.2 não tem durabilidade.
        world = migrated(["ZC-VIA-0005", "ZC-VIA-0001"])
        original = world.start_regional_ambush

        def start_with_enemy_at_entry(expedition_id):
            ambush = original(expedition_id)
            ambush.enemies[0]["zone"] = 1  # fixture: força combate na entrada
            world.store_regional_ambush(expedition_id, ambush)
            return ambush

        world.start_regional_ambush = start_with_enemy_at_entry
        before = {hero: {item: dict(state) for item, state in gear.items()}
                  for hero, gear in world.gear.items()}
        run(world)
        attacks = [row for row in world.log if row.get("action") == "regional_ambush_attack"]
        self.assertTrue(attacks)
        self.assertTrue(any(gear for gear in before.values()))
        for hero, gear in before.items():
            for item, state in gear.items():
                if item in world.gear[hero]:
                    self.assertEqual(world.gear[hero][item]["durability"], state["durability"])

    def test_ambush_without_time_becomes_road_emergency(self):
        world = migrated(["ZC-VIA-0005"])
        original = world.start_regional_ambush

        def late_start(expedition_id):
            world.regional_clock = 10
            return original(expedition_id)

        world.start_regional_ambush = late_start
        player, result = run(world)
        self.assertEqual(result["status"], "road_emergency_outbound")
        self.assertNotIn("e1", world.expeditions)
        for state in world.heroes.values():
            self.assertEqual((state["location"], state["fatigue"]), ("camp", 3))

    def test_disabled_cards_keep_previous_controller_behaviour(self):
        world = migrated(["ZC-VIA-0005"])
        world.regional_travel_cards = False
        before = dict(world.regional_travel_deck)
        _, result = run(world)
        self.assertEqual(result["status"], "returned")
        self.assertEqual(world.regional_travel_deck, before)


if __name__ == "__main__":
    unittest.main()
