"""Regressions for explicit, experimental Arc 2 unlocks."""
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from system import World
from tactics import TACTICS, TacticalGame
from arc2 import Arc2
from regional_player import AdaptiveRegionalPlayer
from verify_campaign_player02 import execute as execute_cistern


class Arc2NarrativeAndFuelExperimentalTests(unittest.TestCase):
    @staticmethod
    def world():
        world = World.new(22, ["ZC-HER-0001", "ZC-HER-0003"],
                          {"food": 6, "water": 6})
        world.cistern_record = {
            "status": "verified_victory", "source": "cistern02",
            "migration": {"receipt": {"id": "test-migration"}},
        }
        return world

    def arrived(self, destination, map_id, trip_id):
        world = self.world()
        team = list(world.heroes)
        world.open_expedition(trip_id, team, destination)
        for _ in range(world.expeditions[trip_id].remaining):
            world.advance_expedition(trip_id)
        return world, TacticalGame.start(world, trip_id, map_id)

    def test_celia_is_found_only_by_pre_radio_station_action_and_not_given_clues(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        self.assertFalse(world.flags.get("radio_code", False))
        self.assertEqual(world.clues, 0)
        self.assertNotIn("EXP-NPC-02", game.state["npc_contacts"])
        game.state["heroes"][hero] = 14  # isolated tactical-action fixture
        game.state["enemies"].clear()
        with self.assertRaises(ValueError):
            game.contact_npc(hero, "EXP-NPC-02")
        before = world.heroes[hero]["actions"]
        receipt = game.investigate_contact(hero, "EXP-NPC-02")
        self.assertEqual(receipt["action_cost"], 1)
        self.assertEqual(world.heroes[hero]["actions"], before - 1)
        self.assertEqual(world.clues, 0)
        self.assertIn("EXP-NPC-02", game.state["npc_contacts"])
        evidence_before = world.heroes[hero]["actions"]
        evidence = game.collect_contact_evidence(hero, "EXP-NPC-02")
        self.assertEqual(evidence["clues_awarded"], 1)
        self.assertEqual(world.clues, 1)
        self.assertEqual(world.heroes[hero]["actions"], evidence_before - 1)
        self.assertNotIn("EXP-NPC-02", world.expeditions["station"].crew)
        with self.assertRaises(ValueError):
            game.collect_contact_evidence(hero, "EXP-NPC-02")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "station.json"
            world.save(path)
            world = World.load(path)
        game = TacticalGame(world, "station")
        receipt = game.contact_npc(hero, "EXP-NPC-02")
        self.assertEqual(receipt["action_cost"], 1)
        self.assertEqual(world.clues, 1)
        self.assertIn("EXP-NPC-02", world.expeditions["station"].crew)

    def test_station_threat_uses_map_spawn_not_survivor_objective_zone(self):
        _, game = self.arrived("EXP-LOC-05", "station_02", "station")
        self.assertEqual({enemy['zone'] for enemy in game.state['enemies'].values()},
                         {game.map['spawn']})

    def test_contact_discovery_and_recruitment_require_safe_physical_zone(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14  # isolated tactical-action fixture
        enemy = next(iter(game.state["enemies"].values()))
        enemy["zone"] = 14
        with self.assertRaisesRegex(ValueError, "ameaça"):
            game.investigate_contact(hero, "EXP-NPC-02")
        game.state["enemies"].clear()
        game.investigate_contact(hero, "EXP-NPC-02")
        game.state["enemies"]["E-test"] = {"kind": "slow", "zone": 14, "health": 1}
        with self.assertRaisesRegex(ValueError, "ameaça"):
            game.contact_npc(hero, "EXP-NPC-02")

    def test_legacy_contact_marker_cannot_bypass_physical_investigation(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14
        game.state["enemies"].clear()
        # Models a legacy/save-loaded marker without the required action receipt.
        game.state["npc_contacts"]["EXP-NPC-02"] = 14
        with self.assertRaisesRegex(ValueError, "investigação prévia"):
            game.contact_npc(hero, "EXP-NPC-02")
        self.assertNotIn("EXP-NPC-02", world.expeditions["station"].crew)

    def test_finding_celia_does_not_require_the_shelter_to_be_able_to_recruit_her(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14
        game.state["enemies"].clear()
        world.stock["food"] = 0
        world.stock["water"] = 0
        decision = __import__('regional_player').AdaptiveRegionalPlayer('leader').step(
            game, {'kind': 'investigate_contact', 'npc': 'EXP-NPC-02'})
        self.assertEqual(decision['action'], 'investigate_contact')
        self.assertEqual(world.clues, 0)

    def test_pre_radio_evidence_cannot_be_collected_after_radio_is_decoded(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14
        game.state["enemies"].clear()
        game.investigate_contact(hero, "EXP-NPC-02")
        # Isolated gate setup: the radio was legitimately decoded elsewhere.
        world.flags["radio_code"] = True
        with self.assertRaisesRegex(ValueError, "indisponível"):
            game.collect_contact_evidence(hero, "EXP-NPC-02")
        self.assertEqual(world.clues, 0)

    def test_legacy_discovery_marker_cannot_create_evidence_without_action_receipt(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14
        game.state["enemies"].clear()
        game.state["npc_contacts"]["EXP-NPC-02"] = 14
        game.state["discovered_npcs"].append("EXP-NPC-02")
        with self.assertRaisesRegex(ValueError, "investigação física"):
            game.collect_contact_evidence(hero, "EXP-NPC-02")
        self.assertEqual(world.clues, 0)

    def test_completed_contact_and_evidence_objectives_survive_site_revisit(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "first-visit")
        world.site_states["EXP-LOC-05"] = {
            "map": "station_02", "discovered_npcs": ["EXP-NPC-02"]
        }
        world.log.extend([
            {"day": 0, "expedition": "first-visit",
             "action": "investigate_physical_contact", "npc": "EXP-NPC-02",
             "location": "EXP-LOC-05"},
            {"day": 0, "expedition": "first-visit",
             "action": "collect_regional_evidence", "npc": "EXP-NPC-02",
             "evidence_id": "EXP-CLUE-001", "location": "EXP-LOC-05",
             "name": "Anotações de Célia", "hero": "ZC-HER-0001",
             "zone": 14, "action_cost": 1, "clues_awarded": 1,
             "total_clues": 1},
        ])
        world.clues = 1
        # The next expedition is a unit fixture for the persisted-site query.
        world.encounters.pop("first-visit")
        world.expeditions.pop("first-visit")
        world.heroes["ZC-HER-0001"]["location"] = "camp"
        world.heroes["ZC-HER-0003"]["location"] = "camp"
        world.daily_expeditions = 0
        world.regional_clock = 0
        world.open_expedition("second-visit", list(world.heroes), "EXP-LOC-05")
        for _ in range(world.expeditions["second-visit"].remaining):
            world.advance_expedition("second-visit")
        revisited = TacticalGame.start(world, "second-visit", "station_02")
        player = AdaptiveRegionalPlayer("leader")
        self.assertTrue(player._objective_done(
            revisited, {"kind": "investigate_contact", "npc": "EXP-NPC-02"}))
        self.assertTrue(player._objective_done(
            revisited, {"kind": "evidence", "npc": "EXP-NPC-02"}))

    def test_save_validation_checks_evidence_receipt_against_catalog_values(self):
        world = self.world()
        world.clues = 1
        world.log.append({
            "day": 0, "expedition": "station", "action": "collect_regional_evidence",
            "evidence_id": "EXP-CLUE-001", "name": "Anotações de Célia",
            "npc": "EXP-NPC-02", "hero": "ZC-HER-0001", "zone": 14,
            "location": "EXP-LOC-05", "action_cost": 1,
            "clues_awarded": 8, "total_clues": 8,
        })
        with self.assertRaisesRegex(ValueError, "recibo de evidência"):
            world.validate()

    def test_save_validation_rejects_clue_receipt_without_prior_physical_investigation(self):
        world = self.world()
        world.clues = 1
        world.log.extend([
            {"day": 0, "expedition": "made-up-trip", "action": "open_expedition",
             "destination": "EXP-LOC-05"},
            {"day": 0, "expedition": "made-up-trip",
             "action": "collect_regional_evidence", "evidence_id": "EXP-CLUE-001",
             "name": "Anotações de Célia", "npc": "EXP-NPC-02",
             "hero": "ZC-HER-0001", "zone": 14, "location": "EXP-LOC-05",
             "action_cost": 1, "clues_awarded": 1, "total_clues": 1},
        ])
        with self.assertRaisesRegex(ValueError, "investigação anterior"):
            world.validate()

    def test_two_regional_clues_require_distinct_physical_evidence_and_safe_return(self):
        world, game = self.arrived("EXP-LOC-05", "station_02", "station")
        first, second = sorted(world.heroes)
        game.state["enemies"].clear()  # isolates evidence acquisition, not a replay
        game.state["heroes"][first] = 14
        game.state["heroes"][second] = 12
        game.investigate_contact(first, "EXP-NPC-02")
        self.assertEqual(world.clues, 0)
        game.collect_contact_evidence(first, "EXP-NPC-02")
        game.investigate_contact(second, "EXP-NPC-14")
        game.collect_contact_evidence(second, "EXP-NPC-14")
        self.assertEqual(world.clues, 2)
        self.assertNotIn("EXP-NPC-02", world.expeditions["station"].crew)
        with self.assertRaisesRegex(ValueError, "retorno ao abrigo"):
            Arc2(world).decode_radio()
        game.state["heroes"] = {key: game.exit_zone for key in game.state["heroes"]}
        game.finish()
        world.begin_return("station")
        for _ in range(world.expeditions["station"].remaining):
            world.advance_expedition("station")
        Arc2(world).decode_radio()
        self.assertTrue(world.flags["radio_code"])
        self.assertEqual(world.clues, 0)
        decoded = [row for row in world.log if row.get("result") == "decoded"][-1]
        self.assertEqual(decoded["clues_spent"], 2)
        self.assertEqual(decoded["clues_remaining"], 0)

    def test_workshop_fuel_cache_is_unique_persistent_noisy_and_physical_cargo(self):
        world, game = self.arrived("EXP-LOC-03", "workshop_02", "workshop")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14  # isolated tactical-action fixture
        game.state["enemies"].clear()
        before = world.heroes[hero]["actions"]
        receipt = game.salvage_fuel_cache(hero)
        self.assertEqual(receipt["fuel"], 8)
        self.assertEqual(receipt["action_cost"], 2)
        self.assertEqual(receipt["noise"], 3)
        self.assertEqual(world.heroes[hero]["actions"], before - 2)
        self.assertEqual(world.expeditions["workshop"].cargo["fuel"], 8)
        self.assertEqual(world.stock["fuel"], 0)
        with self.assertRaises(ValueError):
            game.salvage_fuel_cache(hero)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workshop.json"
            world.save(path)
            world = World.load(path)
        game = TacticalGame(world, "workshop")
        self.assertEqual(game.state["fuel_cache_collected"], True)
        self.assertEqual(world.expeditions["workshop"].cargo["fuel"], 8)
        game.state["heroes"] = {key: game.exit_zone for key in game.state["heroes"]}
        game.finish()
        self.assertTrue(world.site_states["EXP-LOC-03"]["fuel_cache_collected"])
        world.begin_return("workshop")
        for _ in range(world.expeditions["workshop"].remaining):
            world.advance_expedition("workshop")
        self.assertEqual(world.stock["fuel"], 8)

    def test_eight_policies_recover_experimental_cache_from_real_cistern_seed22(self):
        profiles = ('cautious','explorer','builder','combatant','leader','novice',
                    'optimizer','adversarial')
        for profile in profiles:
            with self.subTest(profile=profile):
                player, cistern = execute_cistern(22)
                self.assertEqual(cistern["result"], "verified_victory")
                player.game.transition_to_last_transmission()
                world = player.game.world
                team = list(world.heroes)
                result = AdaptiveRegionalPlayer(profile).run_expedition(
                    world, f"seed22-workshop-cache-{profile}", "EXP-LOC-03", team,
                    "workshop_02", [{"kind": "fuel_cache", "zone": 14},
                                     {"kind": "battery", "zone": 7}],
                    max_steps=120)
                self.assertEqual(result["status"], "returned")
                self.assertEqual(world.stock["fuel"], 8)
                self.assertTrue(world.site_states["EXP-LOC-03"]["fuel_cache_collected"])
                self.assertIn("battery", world.special_stock)
                self.assertEqual(sum(row.get("action") == "salvage_fuel_cache"
                                     for row in world.log), 1)

    def test_station_celia_evidence_and_return_exceed_far_route_local_action_budget(self):
        map_data = TACTICS['maps']['station_02']
        door_costs = {tuple(sorted(door['edge'])):
                      (2 if door['blocked'] else 1)
                      for door in map_data['doors']}
        distances = {map_data['entry']: 0}
        parents = {}
        queue = [map_data['entry']]
        for current in queue:
            for a, b in map_data['edges']:
                if current not in (a, b):
                    continue
                nxt = b if current == a else a
                cost = 1 + door_costs.get(tuple(sorted((current, nxt))), 0)
                candidate = distances[current] + cost
                if nxt not in distances or candidate < distances[nxt]:
                    distances[nxt] = candidate
                    parents[nxt] = current
                    if nxt not in queue:
                        queue.append(nxt)
        contact = 14
        # Return-path doors are already open, leaving only connector moves.
        reverse = {map_data['exit']: 0}
        queue = [map_data['exit']]
        for current in queue:
            for a, b in map_data['edges']:
                if current not in (a, b):
                    continue
                nxt = b if current == a else a
                candidate = reverse[current] + 1
                if nxt not in reverse or candidate < reverse[nxt]:
                    reverse[nxt] = candidate
                    if nxt not in queue:
                        queue.append(nxt)
        shortest_return_moves = reverse[contact]
        minimum_personal_pa = distances[contact] + 1 + 1 + shortest_return_moves
        available_local_rounds = (10 - 3 - 1 - 3)
        self.assertEqual(distances[contact], 7)
        self.assertEqual(shortest_return_moves, 4)
        self.assertEqual(minimum_personal_pa, 13)
        self.assertEqual(available_local_rounds, 3)
        self.assertGreater(minimum_personal_pa, 3 * available_local_rounds)

    def test_lost_cache_cargo_does_not_respawn_after_emergency(self):
        world, game = self.arrived("EXP-LOC-03", "workshop_02", "workshop")
        hero = "ZC-HER-0001"
        game.state["heroes"][hero] = 14
        game.state["enemies"].clear()
        game.salvage_fuel_cache(hero)
        receipt = game.emergency_return("teste de perda do combustível carregado")
        self.assertEqual(receipt["lost_cargo"], {"fuel": 8})
        self.assertTrue(world.site_states["EXP-LOC-03"]["fuel_cache_collected"])
        self.assertEqual(world.stock["fuel"], 0)

    def test_military_fuel_gate_matches_three_segments_each_way_at_two_per_segment(self):
        world = self.world()
        world.stock["fuel"] = 11
        world.vehicles["EXP-VEI-02"] = {"location": "camp", "health": 3}
        world.special_stock.append("access_card")
        world.flags.update({"radio_code": True, "access_card": True})
        before = asdict(world)
        with self.assertRaisesRegex(ValueError, "Combustível insuficiente"):
            Arc2(world).authorize_installation(
                "military-short", list(world.heroes), "EXP-VEI-02")
        self.assertFalse(world.flags.get("military_access"))
        self.assertEqual(world.stock["fuel"], 11)
        self.assertNotIn("military-short", world.expeditions)
        self.assertEqual(before, asdict(world))
        world.stock["fuel"] = 12
        Arc2(world).authorize_installation(
            "military-exact", list(world.heroes), "EXP-VEI-02")
        self.assertEqual(world.stock["fuel"], 0)
        self.assertEqual(world.expeditions["military-exact"].segment_cost, 3)


if __name__ == "__main__":
    unittest.main()
