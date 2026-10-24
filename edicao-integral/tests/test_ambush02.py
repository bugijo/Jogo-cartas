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
        ambush.attack("ZC-HER-0001", 1, 6)
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


if __name__ == "__main__":
    unittest.main()
