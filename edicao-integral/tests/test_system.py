import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('integral_system',ROOT/'system.py')
system = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = system
spec.loader.exec_module(system)


def world(seed=17, n=2, stock=None):
    return system.World.new(seed,list(system.HEROES)[:n],stock or {'food':8,'water':8,'wood':4,'scrap':4})


class SystemTests(unittest.TestCase):
    def test_catalog_ids_and_progression(self):
        data = system.DATA
        self.assertEqual((len(data['heroes']),len(data['npcs']),len(data['structures'])),(10,15,7))
        self.assertEqual(len({s['id'] for h in data['heroes'] for s in h['skills']}),70)
        self.assertEqual(set(data['attributes']),{'Força','Agilidade','Percepção','Intelecto','Carisma','Resistência'})
        w=world();h=next(iter(w.heroes));w.award_xp(h,76)
        self.assertEqual(len(w.unlocked_skills(h)),7)
        self.assertEqual(w.award_xp(h,20,True),8)
        self.assertEqual(w.award_xp(h,20,True),0)

    def test_storage_and_lodging_limits(self):
        w=world(); self.assertEqual(w.deposit('food',100),6)
        self.assertEqual(sum(w.stock.values()),w.storage)
        for npc_id in list(system.NPCS)[:6]: self.assertTrue(w.recruit(npc_id))
        self.assertFalse(w.recruit(list(system.NPCS)[6]))

    def test_project_work_repair_and_npc(self):
        w=world(stock={'food':8,'water':8,'wood':4,'scrap':4})
        self.assertTrue(w.start_project('garden'))
        self.assertFalse(w.start_project('garden'))
        self.assertFalse(w.work_project('garden'))
        self.assertTrue(w.work_project('garden'))
        w.damage_structure('garden',2)
        self.assertTrue(w.repair_structure('garden'))
        self.assertTrue(w.recruit('EXP-NPC-05'))
        w.assign('EXP-NPC-05','farming')
        self.assertTrue(w.level_npc('EXP-NPC-05'))
        days=[w.end_day() for _ in range(4)]
        self.assertGreaterEqual(days[-1]['produced']['food'],2)
        self.assertEqual(w.structures['garden']['age'],4)

    def test_search_urban_depletion_natural_renewal(self):
        w=world(n=3,stock={'food':6,'water':6})
        urban='EXP-LOC-02'; natural='EXP-LOC-01'
        heroes=list(w.heroes)
        w.open_expedition('market',heroes[:2],urban)
        w.open_expedition('field',heroes[2:],natural)
        w.advance_expedition('market');w.advance_expedition('field')
        for _ in range(system.LOCATIONS[urban]['searches']): w.search('market')
        self.assertEqual(w.search('market'),{})
        w.search('field');w.end_day()
        self.assertEqual(w.searches[natural],system.LOCATIONS[natural]['searches'])
        self.assertEqual(w.searches[urban],0)

    def test_search_requires_arrival_and_cargo_deposits_on_return(self):
        w=world(stock={'food':2,'water':2})
        hero=next(iter(w.heroes))
        w.open_expedition('a',[hero],'EXP-LOC-03')
        with self.assertRaises(ValueError): w.search('a')
        w.advance_expedition('a');w.advance_expedition('a')
        before=dict(w.stock)
        self.assertEqual(w.search('a'),{'scrap':2,'fuel':1})
        self.assertEqual(w.stock,before)
        w.begin_return('a')
        w.advance_expedition('a');w.advance_expedition('a')
        self.assertEqual(w.stock['scrap'],2)
        self.assertEqual(w.stock['fuel'],1)
        self.assertEqual(w.log[-1]['left_behind'],{})

    def test_separate_expeditions_and_return(self):
        w=world(n=4,stock={'food':8,'water':8})
        heroes=list(w.heroes)
        w.open_expedition('A',heroes[:2],'EXP-LOC-02')
        w.open_expedition('B',heroes[2:],'EXP-LOC-03')
        with self.assertRaises(ValueError): w.open_expedition('C',heroes[:1],'EXP-LOC-01')
        self.assertEqual(w.advance_expedition('A'),'arrived')
        self.assertEqual(w.advance_expedition('B'),'travel')
        self.assertEqual(w.advance_expedition('B'),'arrived')
        w.begin_return('A');self.assertEqual(w.advance_expedition('A'),'returned')
        self.assertEqual(w.heroes[heroes[0]]['location'],'camp')
        self.assertIn('B',w.expeditions)

    def test_rng_save_replay_and_crisis_cooldown(self):
        w=world(seed=2)
        w.structures['garden']={'health':3,'age':0}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'save.json';w.save(path);copy=system.World.load(path)
            self.assertEqual([w.end_day() for _ in range(30)],
                             [copy.end_day() for _ in range(30)])
        for crisis in system.CRISES.values():
            hits=[e['day'] for e in w.log if e['crisis']==crisis['id']]
            self.assertTrue(all(b-a>crisis['cooldown_days'] for a,b in zip(hits,hits[1:])))

    def test_outpost_requires_clearance_keeper_and_repair(self):
        w=world(stock={'food':6,'water':6,'wood':4,'scrap':4})
        self.assertTrue(w.recruit('EXP-NPC-10'))
        loc='EXP-LOC-05'
        self.assertFalse(w.establish_outpost(loc,'EXP-NPC-10'))
        w.searches[loc]=0
        self.assertTrue(w.establish_outpost(loc,'EXP-NPC-10'))
        self.assertFalse(w.establish_outpost(loc,'EXP-NPC-10'))
        w.attack_outpost(loc,2)
        self.assertTrue(w.repair_outpost(loc))
        self.assertEqual(w.outposts[loc]['health'],2)

    def test_defense_requires_watch_ammo_and_sight(self):
        w=world(stock={'food':6,'water':6,'ammo':2})
        self.assertTrue(w.recruit('EXP-NPC-10'))
        w.assign('EXP-NPC-10','guard')
        w.structures['watch']={'health':3,'age':0}
        self.assertEqual(w.npc_defense(2,False),2)
        self.assertEqual(w.npc_defense(2,True),1)
        self.assertEqual(w.stock['ammo'],1)
        w.damage_structure('watch',3)
        self.assertEqual(w.npc_defense(2,True),2)

    def test_data_rebuild_deterministic(self):
        before=(ROOT/'data/system.json').read_bytes()
        import subprocess
        subprocess.run([sys.executable,str(ROOT/'data/build_system_data.py')],check=True)
        self.assertEqual(before,(ROOT/'data/system.json').read_bytes())


if __name__=='__main__':unittest.main()
