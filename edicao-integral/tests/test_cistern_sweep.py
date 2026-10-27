import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from campaign_player02 import CampaignPlayer02
from simulate_cistern_sweep import classify, run_one


class CisternSweepTests(unittest.TestCase):
    def test_h2_constructor_is_hn_with_two(self):
        h2 = CampaignPlayer02.new_h2(22).game
        hn = CampaignPlayer02.new_hn(22, 2).game
        self.assertEqual(h2.founders, hn.founders)
        self.assertEqual(h2.links, hn.links)

    def test_hn_keeps_first_founders_and_draws_one_link_each(self):
        base = CampaignPlayer02.new_h2(7).game
        for size in range(3, 7):
            game = CampaignPlayer02.new_hn(7, size).game
            self.assertEqual(len(game.founders), size)
            self.assertEqual(game.founders[:2], base.founders)
            self.assertEqual(len(set(game.links)), size)
            self.assertEqual(game.links[:2], base.links)

    def test_large_group_attempts_finish_without_engine_errors(self):
        for size in (5, 6):
            player = CampaignPlayer02.new_hn(3, size)
            report = player.attempt_cistern()
            self.assertEqual(report["verified_victory"],
                             "verified_victory" in player.game.rewards)
            if not report["verified_victory"]:
                self.assertIsNone(report["certificate"])

    def test_load_trimming_never_drops_parts_or_equipment(self):
        player = CampaignPlayer02.new_hn(1, 2)
        player.attempt_cistern()
        dropped = [item for item in player.decisions
                   if item["action"] == "drop_task_for_load"]
        self.assertTrue(dropped)
        self.assertTrue(all(item["task"]["kind"] in ("Conserva", "Água")
                            for item in dropped))

    def test_material_kept_for_filter_when_stock_is_short(self):
        player = CampaignPlayer02.new_hn(22, 2)
        player.game.cistern.materials = 0
        trip = type("Trip", (), {"events": [{"event_id": "e", "card_id": "ZC-VIA-0004"}]})
        context = type("Ctx", (), {"materials": 1})
        self.assertEqual(player._choice(trip, "e", context), "pressure")
        player.game.cistern.materials = 5
        self.assertEqual(player._choice(trip, "e", context), "material")

    def test_run_row_is_reproducible_and_classified(self):
        first = run_one(2, 22)
        self.assertEqual(first, run_one(2, 22))
        self.assertEqual(first["cause"], "verified_victory")
        self.assertTrue(run_one(2, 3)["cause"].startswith(
            ("partial_defeat", "expedition_", "missing_part_", "blocked_")))

    def test_classify_reports_partial_defeat_by_hunger(self):
        report = {"verified_victory": False, "days": [], "result": "partial_defeat",
                  "blocked": None,
                  "final_state": {"parts": {"Conexões": 2, "Bomba": 3, "Membrana": 3},
                                  "people": [{"hungry": True, "thirsty": False}]}}
        self.assertEqual(classify(report), "partial_defeat_hunger_or_thirst")


if __name__ == "__main__":
    unittest.main()
