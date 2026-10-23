import importlib.util
import random
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("integral_engine", ROOT / "engine.py")
engine = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = engine
SPEC.loader.exec_module(engine)


class EngineTests(unittest.TestCase):
    def test_equipment_ids_and_slots(self):
        self.assertEqual(len(engine.ITEMS), len(engine.EQUIPMENT["items"]))
        inv = engine.Inventory()
        inv.place("EXP-EQU-001", "pocket", index=0)
        inv.place("EXP-EQU-003", "torso")
        inv.place("EXP-EQU-002", "backpack", x=0, y=0)
        inv.place("EXP-EQU-004", "backpack", x=1, y=0)
        self.assertEqual(len(inv.all_items()), 4)
        with self.assertRaises(ValueError):
            inv.place("EXP-EQU-001", "hand", index=0)

    def test_backpack_requires_equipment_and_no_overlap(self):
        inv = engine.Inventory()
        with self.assertRaises(ValueError):
            inv.place("EXP-EQU-002", "backpack")
        inv.place("EXP-EQU-003", "torso")
        inv.place("EXP-EQU-002", "backpack", x=0, y=0)
        with self.assertRaises(ValueError):
            inv.place("EXP-EQU-004", "backpack", x=0, y=0)

    def test_heroes_preserve_existing_id_name_profession(self):
        import json
        old = json.loads((ROOT.parent / "content/catalog.json").read_text(encoding="utf-8"))
        old_by_id = {h["id"]: h for h in old["heroes"]}
        self.assertEqual(len(engine.DATA["heroes"]), 10)
        for hero in engine.DATA["heroes"]:
            self.assertEqual((hero["name"], hero["profession"]),
                             (old_by_id[hero["id"]]["name"], old_by_id[hero["id"]]["profession"]))

    def test_combat_seed_and_armor(self):
        a = engine.attack(random.Random(42), 3, 4, 2, 3, armor=1)
        b = engine.attack(random.Random(42), 3, 4, 2, 3, armor=1)
        self.assertEqual(a, b)
        self.assertEqual(a["damage"] + a["armor_lost"], a["hits"] * 2)

    def test_xp_caps_and_unlocks(self):
        h = engine.Hero("ZC-HER-0001")
        self.assertEqual(h.award_xp(12, combat=True), 8)
        self.assertEqual(h.award_xp(3, combat=True), 0)
        self.assertEqual(h.award_xp(200), 92)
        self.assertEqual(h.unlocks, [0, 5, 12, 20, 35, 50, 75])

    def test_recruit_capacity_and_garden_growth(self):
        c = engine.Camp(2, 3, 12, 12, materials=2)
        self.assertTrue(c.recruit())
        self.assertFalse(c.recruit())
        self.assertTrue(c.build_garden())
        meals = [c.end_day() for _ in range(4)]
        self.assertEqual([m["produced_food"] for m in meals], [0, 0, 0, 1])
        self.assertEqual(meals[-1]["missing_food"], 0)
        self.assertEqual(meals[-1]["missing_water"], 0)

    def test_shortage_nonnegative_and_save_roundtrip(self):
        c = engine.Camp(2, 2, 1, 0)
        result = c.end_day()
        self.assertEqual((result["missing_food"], result["missing_water"]), (1, 2))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            hero = engine.Hero("ZC-HER-0001")
            engine.save(path, [hero], c, 44)
            self.assertEqual(engine.load(path), ([hero], c, 44))

    def test_reject_duplicate_save_heroes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            h = engine.Hero("ZC-HER-0001")
            engine.save(path, [h, h], engine.Camp(2, 2, 4, 4), 1)
            with self.assertRaises(ValueError):
                engine.load(path)


if __name__ == "__main__":
    unittest.main()
