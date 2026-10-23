import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integrated_campaign import IntegratedCampaign, LINK_IDS, STARTERS


class IntegratedCampaignTests(unittest.TestCase):
    def prepared(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        game.cistern.food.extend([4, 4, 4])
        game.cistern.water.extend([4, 4, 4])
        game.collect_part("Conexões")
        game.meal(); game.next_cistern_day()
        game.collect_part("Bomba")
        game.meal(); game.next_cistern_day()
        game.collect_part("Membrana")
        game.meal(); game.next_cistern_day()
        game.cistern.reserve("A"); game.cistern.work(1)
        game.cistern.reserve("B"); game.cistern.work(1)
        game.cistern.reserve("C")
        game.meal(); game.next_cistern_day(); game.cistern.work(2)
        game.meal()
        return game

    def test_parts_require_mission_and_choices_are_persistent(self):
        game = IntegratedCampaign.new(1, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(ValueError): game.collect_part("Conexões", "ignore")
        self.assertNotIn("Conexões", game.cistern.parts)
        game.collect_part("Conexões")
        with self.assertRaises(ValueError): game.collect_part("Conexões")
        self.assertEqual(game.decisions["CIS-MIS-A"], "search")

    def test_transition_needs_real_filter_and_preserves_identity(self):
        game = self.prepared()
        self.assertTrue(game.cistern.filter_completed)
        game.complete_cistern()
        self.assertEqual(game.phase, "last_transmission")
        self.assertTrue(game.world.flags["cistern_complete"])
        self.assertEqual(list(game.world.heroes), list(STARTERS[:2]))
        with self.assertRaises(ValueError): game.complete_cistern()

    def test_save_resume_and_no_duplicate_transition_reward(self):
        game = self.prepared()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            restored = IntegratedCampaign.load(path)
            restored.complete_cistern()
            restored.save(path)
            resumed = IntegratedCampaign.load(path)
            self.assertEqual(resumed.rewards, ["cistern_complete"])
            self.assertEqual(resumed.decisions, game.decisions)
            self.assertEqual(resumed.world.flags["cistern_complete"], True)

    def test_arc_cannot_be_started_before_transition_and_terminal_states_persist(self):
        game = IntegratedCampaign.new(2, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(ValueError): game.final_defense()
        game.mark_impossible("sem_rota_de_progresso")
        self.assertEqual(game.status, "IMPOSSIBLE")
        with self.assertRaises(ValueError): game.advance_day()


if __name__ == "__main__":
    unittest.main()
