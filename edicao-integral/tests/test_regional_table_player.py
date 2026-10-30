"""Mesa de personas no regional: voto do amanhecer e opções do controlador."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from regional_table_player import RegionalTablePlayer, regional_policy
from virtual_players import PERSONAS


class RegionalVoteTests(unittest.TestCase):
    def test_vote_is_deterministic_and_complete(self):
        table = list(PERSONAS[:4])
        first, second = regional_policy(table), regional_policy(table)
        self.assertEqual(first, second)
        self.assertEqual(set(first['policy']), {'risk_short', 'progress_first',
                                                'reserve_3_days', 'forage', 'invest',
                                                'storage_priority'})
        self.assertIn(first['leader'], {p.id for p in table})

    def test_policy_maps_to_camp_options(self):
        player = RegionalTablePlayer(PERSONAS[:2])
        player.apply_policy({'risk_short': False, 'progress_first': False,
                             'reserve_3_days': True, 'forage': False, 'invest': False,
                             'storage_priority': False})
        self.assertEqual((player.risk, player.food_days, player.options),
                         ('covered', 3, {'bridge'}))
        player.apply_policy({'risk_short': True, 'progress_first': False,
                             'reserve_3_days': False, 'forage': True, 'invest': True,
                             'storage_priority': True})
        self.assertEqual((player.risk, player.food_days), ('short', 2))
        self.assertEqual(player.options,
                         {'bridge', 'priority', 'forage', 'garden', 'build'})

    def test_different_bands_vote_differently(self):
        bands = {g: regional_policy([p for p in PERSONAS if p.group == g][:3])['policy']
                 for g in 'ABC'}
        self.assertGreater(len({tuple(sorted(v.items())) for v in bands.values()}), 1)


if __name__ == '__main__':
    unittest.main()
