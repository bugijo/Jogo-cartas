import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from campaign_seeded_review import check_all_setups, phase_replay, run_matrix
from validate_campaign_components import run as components
from scaled_tactical_replay import run as tactical_run


class CampaignSeededReviewTests(unittest.TestCase):
    def test_every_link_combination_fits_initial_tents(self):
        rows=check_all_setups()
        self.assertEqual([x['combinations'] for x in rows], [66,66,220,495,792,924])
        self.assertTrue(all(x['all_fit'] for x in rows))

    def test_fifteen_seeded_phase_runs_have_five_days(self):
        result=run_matrix()
        self.assertEqual(len(result['runs']),15)
        self.assertTrue(all(len(r['days'])==5 for r in result['runs']))
        self.assertEqual(result['tactical_replays_within_phase_model'],0)
        self.assertFalse(result['campaign_validated'])

    def test_seed_is_repeatable_and_not_balance_proof(self):
        a=phase_replay(6,6303,'limite')
        b=phase_replay(6,6303,'limite')
        self.assertEqual(a,b)
        self.assertFalse(a['tactical_verified'])
        self.assertTrue(all(d['cargo_needed']<=d['cargo_capacity'] for d in a['days']))

    def test_printed_support_for_all_group_sizes(self):
        result=components()
        self.assertEqual(result['cards'],114)
        self.assertEqual(result['enemies_printed'],24)
        self.assertEqual([x['duplex_sheets'] for x in result['group_components']],[58,67,67,67,67])

    def test_one_legal_five_day_tactical_route_per_group_size(self):
        for h in range(2,7):
            with self.subTest(heroes=h):
                result=tactical_run(h)
                self.assertEqual(result['result'],'vitória nesta trajetória fixa')
                self.assertEqual(len(result['days']),5)
                self.assertTrue(all(x['segments']<=10 for x in result['tactical']))
                self.assertTrue(all(x['peak_enemies']<=24 for x in result['tactical']))
                self.assertEqual(result['tactical'][2]['extra_night_travel'],'ZC-VIA-0002')
                self.assertEqual(result['tactical'][2]['night_fatigue_per_hero'],1)
                self.assertEqual(result['days'][-1]['filter_work'],4)
                self.assertGreaterEqual(result['days'][-1]['food'],0)
                self.assertGreater(result['days'][-1]['water'],0)


if __name__=='__main__':unittest.main()
