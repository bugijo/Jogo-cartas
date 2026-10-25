"""Busca regional custa PA e exige presença no setor de busca do mapa."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from system import World
from tactics import TacticalGame


class RegionalSearchActionTests(unittest.TestCase):
    def ready_world(self):
        world = World.new(3, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-fixture'}},
        }
        world.open_expedition('market', ['ZC-HER-0001'], 'EXP-LOC-02')
        world.advance_expedition('market')
        return world

    def test_migrated_campaign_search_requires_active_map_and_search_sector(self):
        world = self.ready_world()
        with self.assertRaisesRegex(ValueError, 'encontro tático'):
            world.search('market', 'ZC-HER-0001')
        tactical = TacticalGame.start(world, 'market', 'market_intro')
        with self.assertRaisesRegex(ValueError, 'área de busca'):
            tactical.search('ZC-HER-0001')
        self.assertEqual(world.searches['EXP-LOC-02'], 4)

    def test_search_spends_one_action_only_after_validated_result(self):
        world = self.ready_world()
        tactical = TacticalGame.start(world, 'market', 'market_intro')
        tactical.state['heroes']['ZC-HER-0001'] = 5  # fixture do setor de busca B1
        before = world.heroes['ZC-HER-0001']['actions']
        found = tactical.search('ZC-HER-0001')
        self.assertEqual(found, {'food': 2, 'water': 1})
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], before - 1)
        self.assertEqual(world.searches['EXP-LOC-02'], 3)

    def test_search_does_not_consume_action_or_search_when_actor_has_none(self):
        world = self.ready_world()
        tactical = TacticalGame.start(world, 'market', 'market_intro')
        tactical.state['heroes']['ZC-HER-0001'] = 5
        world.heroes['ZC-HER-0001']['actions'] = 0
        with self.assertRaisesRegex(ValueError, 'ação disponível'):
            tactical.search('ZC-HER-0001')
        self.assertEqual(world.searches['EXP-LOC-02'], 4)


if __name__ == '__main__':
    unittest.main()
