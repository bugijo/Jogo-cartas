"""A transição não pode usar peças nem vitória sem expedição canônica."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrated_campaign import IntegratedCampaign, LINK_IDS, STARTERS


class IntegratedGateTests(unittest.TestCase):
    def test_part_is_not_created_from_clock_segments_alone(self):
        game = IntegratedCampaign.new(91, STARTERS[:2], LINK_IDS[:2])
        before = game.cistern.clock
        with self.assertRaises((ValueError, NotImplementedError)):
            game.collect_part("Conexões")
        self.assertEqual(game.cistern.clock, before)
        self.assertNotIn("Conexões", game.cistern.parts)

    def test_filter_candidate_does_not_unlock_second_arc(self):
        game = IntegratedCampaign.new(91, STARTERS[:2], LINK_IDS[:2])
        game.cistern.filter_completed = True
        game.cistern.filter_active = True
        game.cistern.day = 5
        game.cistern.meal_day = 5
        with self.assertRaises((ValueError, NotImplementedError)):
            game.complete_cistern()
        self.assertIsNone(game.world)
        self.assertEqual(game.rewards, [])


if __name__ == "__main__":
    unittest.main()
