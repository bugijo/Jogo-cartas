import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulate_defense import aggregate, replay


class DefenseSimulationTests(unittest.TestCase):
    def test_repeatable_and_team_sizes(self):
        self.assertEqual(aggregate(3,42),aggregate(3,42))
        report=aggregate(3,42)
        self.assertEqual(len(report['runs']),15)
        self.assertEqual(set(report['counts']),{'2','3','4','5','6'})

    def test_record_uses_real_end_state(self):
        for group in range(2,7):
            result=replay(20261023,group)
            self.assertIn(result['status'],('won','lost','active'))
            self.assertGreaterEqual(result['integrity'],0)
            self.assertLessEqual(result['rounds'],15)


if __name__=='__main__':unittest.main()
