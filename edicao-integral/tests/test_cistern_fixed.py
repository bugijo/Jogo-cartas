import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from replay_cistern02_fixed import replay


class FixedCisternReplayTests(unittest.TestCase):
    def test_five_days_match_legacy_tactical_oracle_for_h2_to_h6(self):
        for team in range(2,7):
            result=replay(team)
            self.assertEqual(result,replay(team))
            self.assertEqual(len(result['days']),5)
            self.assertEqual(result['ported_result'],'candidate_victory')
            self.assertTrue(result['days'][-1]['filter_active'])
            self.assertTrue(all(day['food_missing']==0 and day['water_missing']==0
                                for day in result['days']))


if __name__=='__main__':unittest.main()
