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

    def test_adaptive_mode_plans_guards_and_work_with_rolled_dice(self):
        player = CampaignPlayer02.new_hn(32, 2)
        player.adaptive = True
        report = player.attempt_cistern()
        actions = {item["action"] for item in player.decisions}
        self.assertIn("adaptive_plan", actions)
        self.assertIn("adaptive_guards", actions)
        sieges = [night["siege"] for day in report["days"]
                  for night in [day.get("night") or {}] if night.get("siege")]
        self.assertTrue(sieges)
        # Antes da correção, vigias planejados nunca rolavam (lista vazia).
        self.assertTrue(any(siege["rolls"] for siege in sieges))

    def test_adaptive_never_sends_filter_workers_on_expedition(self):
        for seed in (31, 32, 33):
            player = CampaignPlayer02.new_hn(seed, 5)
            player.adaptive = True
            player.adaptive_order = ("Estação", "Oficina")
            player.attempt_cistern()
            for plan in (item for item in player.decisions
                         if item["action"] == "adaptive_plan"):
                self.assertFalse(set(plan["workers"]) & set(plan["team"]))

    def test_heldout_auto_policy_is_fixed_before_measurement(self):
        from simulate_cistern_sweep import HELDOUT, SEEDS, auto_settings
        self.assertFalse(set(HELDOUT) & set(SEEDS))
        from simulate_cistern_sweep import previous_settings
        # Política atual: Oficina primeiro em todos os tamanhos.
        self.assertEqual({auto_settings(size)["adaptive_order"][0]
                          for size in range(2, 7)}, {"Oficina"})
        self.assertEqual(previous_settings(6)["adaptive_order"][0], "Estação")

    def test_adaptive_collection_uses_only_idle_people_and_adds_portions(self):
        player = CampaignPlayer02.new_hn(31, 6)
        player.adaptive = True
        player.adaptive_order = ("Estação", "Oficina")
        player.attempt_cistern()
        plans = {item["day"]: item for item in player.decisions
                 if item["action"] == "adaptive_plan"}
        collections = [item for item in player.decisions
                       if item["action"] == "adaptive_collection"]
        self.assertTrue(collections)
        for item in collections:
            self.assertLessEqual(len(item["plan"]), 2)
            workers = {entry["worker"] for entry in item["plan"]}
            plan = plans.get(item["day"], {"team": [], "workers": []})
            self.assertFalse(workers & (set(plan["team"]) | set(plan["workers"])))
        receipts = [receipt for receipt in player.game.cistern.work_receipts
                    if receipt["task"] == "emergency_collection"]
        self.assertEqual(len(receipts), len(collections))

    def test_station_tactics_are_opt_in_and_used_by_adaptive_mode(self):
        fixed = CampaignPlayer02.new_hn(31, 4)
        fixed.attempt_cistern()
        fixed_actions = {item["action"] for item in fixed.decisions}
        self.assertFalse(fixed_actions & {"support_attack", "escort", "retreat_late"})
        player = CampaignPlayer02.new_hn(31, 4)
        player.adaptive = True
        player.attempt_cistern()
        self.assertIn("support_attack", {item["action"] for item in player.decisions})

    def test_empty_tactics_reproduce_previous_adaptive_controller(self):
        from simulate_cistern_sweep import previous_settings
        row = run_one(5, 31, previous_settings(5))
        self.assertNotIn("support", previous_settings(5)["tactics"])
        self.assertEqual(row, run_one(5, 31, previous_settings(5)))

    def test_cautious_path_avoids_spawn_neighbourhood(self):
        from cistern_tactics02 import MAPS
        station = MAPS["estação"]
        opened = [(1, 5), (9, 13), (3, 7), (13, 14)]
        enemies = [{"zone": 11}, {"zone": 15}]
        plain = CampaignPlayer02._path(station, 7, 14, opened, enemies)
        cautious = CampaignPlayer02._path(station, 7, 14, opened, enemies, cautious=True)
        self.assertIn(15, plain)
        self.assertNotIn(15, cautious)

    def test_adaptive_takes_parts_that_fit_and_fixed_still_blocks(self):
        from campaign_player02 import station_day_tasks
        player = CampaignPlayer02.new_hn(22, 2)
        hero = player.game.founders[0]
        loadout = {hero: ["Pé de cabra", "Machado"]}
        parts = [task for task in station_day_tasks() if task["action"] == "pickup_part"]
        with self.assertRaises(ValueError):
            player._assign_or_trim([hero], loadout, [dict(task) for task in parts])
        player.adaptive = True
        tasks = [dict(task) for task in parts]
        assigned = player._assign_or_trim([hero], loadout, tasks)
        self.assertEqual([task["part"] for task in assigned[hero]], ["Bomba"])
        self.assertEqual(player.decisions[-1]["task"]["part"], "Membrana")

    def test_expedition_metrics_do_not_change_certified_trace(self):
        report = CampaignPlayer02.new_h2(22).attempt_cistern()
        self.assertEqual(report["decision_count"], 98)
        self.assertEqual([item["destination"] for item in report["expedition_stats"]],
                         ["Mercado", "Oficina", "Estação"])
        self.assertTrue(all(item["survived_map"] for item in report["expedition_stats"]))

    def test_classify_reports_partial_defeat_by_hunger(self):
        report = {"verified_victory": False, "days": [], "result": "partial_defeat",
                  "blocked": None,
                  "final_state": {"parts": {"Conexões": 2, "Bomba": 3, "Membrana": 3},
                                  "people": [{"hungry": True, "thirsty": False}]}}
        self.assertEqual(classify(report), "partial_defeat_hunger_or_thirst")


if __name__ == "__main__":
    unittest.main()
