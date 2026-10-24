"""A camada integrada permanece fechada até portar a expedição 0.2."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integrated_campaign import IntegratedCampaign, LINK_IDS, STARTERS, PART_MISSIONS


class IntegratedCampaignTests(unittest.TestCase):
    def test_mission_references_match_canonical_locations(self):
        self.assertEqual(PART_MISSIONS["Conexões"]["location"], "EXP-LOC-03")
        self.assertEqual(PART_MISSIONS["Bomba"]["location"], "EXP-LOC-05")
        self.assertEqual(PART_MISSIONS["Membrana"]["location"], "EXP-LOC-05")

    def test_part_requires_tactical_receipt(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(NotImplementedError):
            game.collect_part("Conexões")
        self.assertEqual(game.cistern.parts, {})
        self.assertEqual(game.cistern.clock, 0)
        self.assertEqual(game.decisions, {})

    def test_candidate_cannot_drop_state_during_transition(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        game.cistern.filter_completed = True
        game.cistern.filter_active = True
        game.cistern.day = game.cistern.meal_day = 5
        with self.assertRaises(NotImplementedError):
            game.complete_cistern()
        self.assertIsNone(game.world)
        self.assertEqual(game.rewards, [])

    def test_save_resume_preserves_partial_campaign(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        game.decide("rota_dia_1", "mercado")
        game.cistern.meal()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertEqual(resumed.decisions, game.decisions)
        self.assertEqual(resumed.cistern.food, game.cistern.food)
        self.assertEqual(resumed.cistern.water, game.cistern.water)
        self.assertIsNone(resumed.world)

    def test_save_resume_preserves_shared_horde_mid_expedition(self):
        game = IntegratedCampaign.new(608, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [STARTERS[0]])
        tactical._horde()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertEqual(resumed.cistern.horde_deck, game.cistern.horde_deck)
        self.assertEqual(resumed.tactical.snapshot(), game.tactical.snapshot())
        resumed.tactical._horde()
        game.tactical._horde()
        self.assertEqual(resumed.cistern.horde_deck, game.cistern.horde_deck)
        self.assertEqual(resumed.tactical.snapshot(), game.tactical.snapshot())

    def test_terminal_states_persist(self):
        game = IntegratedCampaign.new(2, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(ValueError):
            game.final_defense()
        game.mark_impossible("sem_rota_de_progresso")
        self.assertEqual(game.status, "IMPOSSIBLE")
        with self.assertRaises(ValueError):
            game.advance_day()


if __name__ == "__main__":
    unittest.main()
