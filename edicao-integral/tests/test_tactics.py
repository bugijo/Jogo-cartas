import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from system import World
from tactics import TacticalGame, TACTICS


class TacticalTests(unittest.TestCase):
    def setup_world(self,seed=4):
        w=World.new(seed,['ZC-HER-0001','ZC-HER-0002'],
                    {'food':6,'water':6,'wood':2,'scrap':2,'ammo':3})
        w.give_item('ZC-HER-0002','crowbar','EXP-EQU-002','hand')
        w.open_expedition('m',['ZC-HER-0001','ZC-HER-0002'],'EXP-LOC-02')
        w.advance_expedition('m')
        return w

    def test_geometry_and_door_breach(self):
        w=self.setup_world()
        game=TacticalGame.start(w,'m','market_intro')
        self.assertEqual(len(TACTICS['maps']['market_intro']['zones']),16)
        with self.assertRaises(ValueError):game.move('ZC-HER-0002',5)
        self.assertTrue(game.breach('ZC-HER-0002',1,5,'crowbar'))
        self.assertEqual(game.move('ZC-HER-0002',5),5)
        self.assertEqual(game.snapshot()['heroes']['ZC-HER-0002'],5)

    def test_los_range_attack_enemy_persistence_and_save(self):
        w=self.setup_world(seed=12)
        game=TacticalGame.start(w,'m','market_intro')
        enemy=game.spawn('slow',zone=1)
        result=game.attack('ZC-HER-0002','crowbar',enemy)
        self.assertIn('damage',result)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'save.json';w.save(p)
            loaded=World.load(p)
            self.assertEqual(loaded.encounters,w.encounters)
            a=TacticalGame(loaded,'m').activate()
            b=game.activate()
            self.assertEqual(a,b)
            self.assertEqual(loaded.encounters,w.encounters)

    def test_noise_horde_activation_and_announcement(self):
        w=self.setup_world(seed=5)
        game=TacticalGame.start(w,'m','market_intro')
        game.spawn('slow',zone=16)
        game.announce_horde('common',1)
        self.assertEqual(game.activate()['spawned'],[])
        game.noise(1,3)
        result=game.activate()
        self.assertGreaterEqual(len(result['spawned']),1)
        self.assertTrue(all(e['health']>0 for e in game.snapshot()['enemies'].values()))

    def test_dead_hero_cannot_attack_and_return_requires_encounter_exit(self):
        w=self.setup_world()
        game=TacticalGame.start(w,'m','market_intro')
        enemy=game.spawn('slow',zone=1)
        w.heroes['ZC-HER-0002']['health']=0
        with self.assertRaises(ValueError):game.attack('ZC-HER-0002','crowbar',enemy)
        with self.assertRaises(ValueError):w.begin_return('m')
        w.heroes['ZC-HER-0002']['health']=1
        game.finish(retreat=True)
        w.begin_return('m')

    def test_line_of_sight_closed_door_and_surprise_horde(self):
        w=self.setup_world()
        game=TacticalGame.start(w,'m','market_intro')
        self.assertFalse(game.line_of_sight(1,5))
        self.assertFalse(game.line_of_sight(1,6))
        game.breach('ZC-HER-0002',1,5,'crowbar')
        self.assertTrue(game.line_of_sight(1,5))
        game.announce_horde('surprise')
        result=game.activate()
        self.assertEqual(len(result['spawned']),1)

    def test_map_graph_matches_preserved_catalog(self):
        import json
        original=json.loads((ROOT.parent/'content/catalog.json').read_text(encoding='utf-8'))
        market=next(m for m in original['maps'] if m['name']=='Mercado')
        new=TACTICS['maps']['market_intro']
        for key in ('zones','edges','entry','exit','spawn','search','objectives'):
            self.assertEqual(new[key],market[key])
        self.assertEqual([d['edge'] for d in new['doors']],market['doors'])


if __name__=='__main__':unittest.main()
