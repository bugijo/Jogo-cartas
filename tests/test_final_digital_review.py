import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from final_digital_review import setups, independent_route_ledgers, pdf_index_check, wilson
from scaled_tactical_replay import run


class FinalDigitalReviewTest(unittest.TestCase):
    def test_all_founder_setups_and_independent_stocks(self):
        rows = setups()
        self.assertEqual(sum(x['combinations'] for x in rows), 2497)
        self.assertEqual([x['capacity'] for x in rows], [8, 8, 8, 10, 12])
        self.assertEqual([x['end_food'] for x in independent_route_ledgers()], [7, 7, 7, 2, 0])

    def test_alternate_rescue_is_a_real_resource_decision(self):
        for h in range(2, 6):
            accepted = run(h, True)
            declined = run(h, False)
            self.assertEqual(declined['days'][-1]['food'] - accepted['days'][-1]['food'], 4)
        with self.assertRaises(AssertionError) as failure:
            run(6, True)
        self.assertIn('(6, 5, -4, 11)', str(failure.exception))

    def test_print_index_matches_actual_pdf_pages(self):
        totals = pdf_index_check()['totals']
        self.assertEqual(totals['duplex']['sheets'], 58)
        self.assertEqual(totals['manual']['sheets'], 72)

    def test_interval_is_about_model_sampling(self):
        self.assertEqual(wilson(0, 10)[0], 0)
        self.assertEqual(wilson(10, 10)[1], 1)


if __name__ == '__main__': unittest.main()
