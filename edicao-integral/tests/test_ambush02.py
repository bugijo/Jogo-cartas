import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ambush02 import Ambush02


class Ambush02Tests(unittest.TestCase):
    def test_m1_starts_with_canonical_positions_and_requires_full_round(self):
        ambush = Ambush02.start(["ZC-HER-0001", "ZC-HER-0002"], clock=3)
        self.assertEqual(ambush.positions, {"ZC-HER-0001": 1, "ZC-HER-0002": 1})
        self.assertEqual(len(ambush.enemies), 1)
        self.assertEqual(ambush.enemies[0]["zone"], 6)
        self.assertEqual(ambush.door_open, False)
        with self.assertRaises(ValueError):
            ambush.finish()

    def test_movement_cannot_cross_closed_door_and_combat_can_clear_ambush(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        with self.assertRaises(ValueError):
            ambush.move("ZC-HER-0001", 5)
        ambush.begin_round()
        ambush.move("ZC-HER-0001", 2)
        ambush.move("ZC-HER-0001", 6)
        ambush.attack("ZC-HER-0001", 1, "Pé de cabra", 6)
        self.assertEqual(ambush.enemies, [])
        ambush.end_round()
        ambush.positions["ZC-HER-0001"] = 1
        ambush.finish()
        self.assertTrue(ambush.returned)
        self.assertEqual(ambush.clock, 4)

    def test_save_load_preserves_pending_ambush_and_no_double_return(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=8)
        ambush.begin_round()
        snapshot = ambush.snapshot()
        resumed = Ambush02.from_snapshot(snapshot)
        self.assertEqual(resumed.snapshot(), snapshot)
        resumed.end_round()
        resumed.positions["ZC-HER-0001"] = 1
        resumed.finish()
        with self.assertRaises(ValueError):
            resumed.finish()

    def test_pre_horde_snapshot_migrates_without_losing_team_or_position(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        snapshot = ambush.snapshot()
        for field in ("equipment", "ammo", "shots", "local_pressure", "horde_deck",
                      "fatigue", "next_enemy", "failed", "knife_used", "shotgun_used",
                      "ap_penalty"):
            snapshot.pop(field)
        resumed = Ambush02.from_snapshot(snapshot)
        self.assertEqual(resumed.team, ambush.team)
        self.assertEqual(resumed.positions, ambush.positions)
        self.assertEqual(resumed.equipment[ambush.team[0]], ["Pé de cabra"])

    def test_enemy_uses_map_path_instead_of_numeric_zone_distance(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        ambush.positions["ZC-HER-0001"] = 1
        ambush.begin_round()
        ambush.end_round()
        # Z6 reaches Z1 through Z2; numeric zone labels are irrelevant.
        self.assertEqual(ambush.enemies[0]["zone"], 2)

    def test_enemy_opens_closed_door_on_its_graph_path(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        ambush.positions["ZC-HER-0001"] = 5
        ambush.enemies[0]["zone"] = 1
        ambush.begin_round()
        ambush.end_round()
        self.assertTrue(ambush.door_open)
        self.assertEqual(ambush.enemies[0]["zone"], 1)

    def test_two_shots_create_noise_errant_and_failed_shots_spend_ammo(self):
        hero = "ZC-HER-0001"
        ambush = Ambush02.start([hero], clock=3,
                                equipment={hero: ["Pistola"]}, ammo=3)
        ambush.begin_round()
        ambush.move(hero, 2)
        self.assertFalse(ambush.attack(hero, 1, "Pistola", 1))
        self.assertFalse(ambush.attack(hero, 1, "Pistola", 1))
        self.assertEqual(ambush.ammo, 1)
        ambush.end_round()
        noise = [enemy for enemy in ambush.enemies
                 if enemy["zone"] == 6 and enemy["id"] != 1]
        self.assertEqual(len(noise), 1)

    def test_pressure_horde_and_save_load_use_persistent_shoe(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        ambush.begin_round(); ambush.enemies.clear(); ambush.end_round()
        self.assertEqual(ambush.local_pressure, 1)
        saved = ambush.snapshot()
        resumed = Ambush02.from_snapshot(saved)
        resumed.begin_round(); resumed.end_round()
        self.assertEqual(resumed.local_pressure, 0)
        horde = [entry for entry in resumed.log if entry["event"] == "horde"]
        self.assertEqual(len(horde), 1)
        self.assertEqual(len(resumed.horde_deck["discard"]), 1)
        self.assertEqual(len(resumed.horde_deck["deck"]), 8)

    def test_night_round_adds_extra_horde_and_night_segment_fatigue(self):
        hero = "ZC-HER-0001"
        ambush = Ambush02.start([hero], clock=8)
        ambush.enemies.clear()
        ambush.begin_round()
        self.assertEqual(ambush.fatigue[hero], 1)
        ambush.end_round()
        self.assertEqual(ambush.local_pressure, 1)
        self.assertEqual(sum(event["event"] == "horde" for event in ambush.log), 1)
        self.assertEqual(len(ambush.horde_deck["discard"]), 1)

    def test_round_action_points_apply_deprivation_and_fatigue_penalties(self):
        hero = "ZC-HER-0001"
        ambush = Ambush02.start([hero], clock=8,
                                fatigue={hero: 1}, ap_penalty={hero: 1})
        ambush.begin_round()  # Night segment raises fatigue to 2.
        self.assertEqual(ambush.ap[hero], 1)

    def test_twenty_fifth_enemy_marks_overrun_and_allows_emergency(self):
        ambush = Ambush02.start(["ZC-HER-0001"], clock=3)
        ambush.enemies = [
            {"id": i + 1, "kind": "Errante", "zone": 6, "hp": 1}
            for i in range(24)]
        ambush.next_enemy = 25
        ambush.begin_round()
        ambush.local_pressure = 1
        ambush.end_round()
        self.assertTrue(ambush.failed)
        self.assertEqual(len(ambush.enemies), 24)
        ambush.emergency_return()
        self.assertTrue(ambush.returned)
        self.assertEqual(ambush.wounds[ambush.team[0]], 1)
        self.assertEqual(ambush.fatigue[ambush.team[0]], 3)


if __name__ == "__main__":
    unittest.main()
