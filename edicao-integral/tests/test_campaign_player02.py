"""Replay de campanha legal e reprodutível; não mede equilíbrio."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_campaign_player02 import execute, trace, verify_artifact, write_artifact


class CampaignPlayer02Tests(unittest.TestCase):
    def test_seed_22_completes_all_five_nights_with_legal_receipts(self):
        player, report = execute(22)
        self.assertEqual(report["result"], "verified_victory")
        self.assertEqual(report["nights_completed"], 5)
        self.assertEqual([day["day"] for day in report["days"]], [1, 2, 3, 4, 5])
        self.assertEqual([day["destination"] for day in report["days"][:3]],
                         ["Mercado", "Oficina", "Estação"])
        self.assertEqual(report["events"], [f"ZC-EVE-{n:04d}" for n in range(1, 6)])
        self.assertEqual({item["id"] for item in report["receipts"]
                          if item.get("event") == "pickup_part"},
                         {"Oficina:Conexões", "Estação:Bomba", "Estação:Membrana"})
        self.assertEqual(report["certificate"]["status"], "verified_victory")
        self.assertIn("verified_victory", player.game.rewards)
        self.assertEqual(len(report["sieges"]), 2)
        self.assertEqual(report["nights_completed"], player.game.cistern.meal_day)
        self.assertEqual(report["days"][3]["travel_events"], [])
        self.assertEqual(report["days"][4]["travel_events"], [])
        return_events = report["days"][0]["travel_events"]
        self.assertIn({"leg": "return", "event_id": "travel-return-001",
                       "card_id": "ZC-VIA-0010",
                       "resolution": {"choice": None,
                                      "effect": {"material_gain": 1}}},
                      return_events)

    def test_same_seed_reproduces_decision_trace_and_terminal_save(self):
        _, first = execute(22)
        _, second = execute(22)
        self.assertEqual(trace(first), trace(second))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.json"
            write_artifact(path)
            verified = verify_artifact(path)
        self.assertEqual(verified, trace(first))


if __name__ == "__main__":
    unittest.main()
