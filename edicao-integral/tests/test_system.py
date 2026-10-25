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

    def test_all_seventy_skill_thresholds_activate_typed_bonus(self):
        for profile in system.DATA['heroes']:
            w=system.World.new(1,[profile['id']],{'food':2,'water':2})
            for skill in profile['skills']:
                old=w.skill_bonus(profile['id'],skill['operation'])
                if skill['xp']:
                    w.award_xp(profile['id'],skill['xp']-w.heroes[profile['id']]['xp'])
                    self.assertEqual(w.skill_bonus(profile['id'],skill['operation']),
                                     old+skill['bonus'])
                else:
                    self.assertGreaterEqual(old,skill['bonus'])

    def test_combat_xp_cap_persists_across_days_until_expedition_returns(self):
        w=world(stock={'food':8,'water':8})
        hero=next(iter(w.heroes))
        w.open_expedition('long',[hero],'EXP-LOC-05')
        self.assertEqual(w.award_xp(hero,20,combat=True),8)
        w.end_day()
        self.assertEqual(w.award_xp(hero,1,combat=True),0)
        for _ in range(3):w.advance_expedition('long')
        w.begin_return('long')
        for _ in range(3):w.advance_expedition('long')
        self.assertEqual(w.award_xp(hero,1,combat=True),1)

    def test_storage_and_lodging_limits(self):
        w=world(); self.assertEqual(w.deposit('food',100),6)
        self.assertEqual(sum(w.stock.values()),w.storage)
        for npc_id in list(system.NPCS)[:6]: self.assertTrue(w.recruit(npc_id))
        self.assertFalse(w.recruit(list(system.NPCS)[6]))

    def test_multiple_equipment_instances_save_and_spatial_rules(self):
        w=world(stock={'food':4,'water':4})
        a,b=list(w.heroes)
        w.give_item(a,'knife-1','EXP-EQU-001','pocket',index=0)
        w.give_item(b,'knife-2','EXP-EQU-001','pocket',index=0)
        w.give_item(a,'bag-1','EXP-EQU-003','torso')
        w.give_item(a,'crowbar-1','EXP-EQU-002','backpack',x=0,y=0)
        with self.assertRaises(ValueError):
            w.give_item(a,'helmet-1','EXP-EQU-004','backpack',x=0,y=0)
        w.give_item(a,'helmet-1','EXP-EQU-004','backpack',x=1,y=0)
        with self.assertRaises(ValueError):
            w.move_item(a,'bag-1','backpack')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'world.json';w.save(path)
            restored=system.World.load(path)
            self.assertEqual(restored.gear,w.gear)

    def test_combat_actions_durability_noise_and_armor(self):
        w=world(seed=42,stock={'food':4,'water':4})
        hero=next(iter(w.heroes))
        w.give_item(hero,'knife','EXP-EQU-001','pocket')
        w.give_item(hero,'helmet','EXP-EQU-004','head')
        w.move_item(hero,'knife','hand',in_combat=True)
        self.assertEqual(w.heroes[hero]['actions'],2)
        result=w.attack_with_item(hero,'knife')
        self.assertEqual(result['noise'],'baixo')
        self.assertEqual(len(result['rolls']),1)
        self.assertEqual(result['durability'],2)
        self.assertEqual(w.heroes[hero]['actions'],1)
        self.assertEqual(w.receive_damage(hero,2,'helmet'),{'absorbed':1,'health':2})
        self.assertEqual(w.gear[hero]['helmet']['durability'],2)
        w.begin_round()
        self.assertEqual(w.heroes[hero]['actions'],3)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'combat.json';w.save(path)
            copy=system.World.load(path)
            self.assertEqual(copy.attack_with_item(hero,'knife'),w.attack_with_item(hero,'knife'))

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

    def test_individual_builder_skill_applies_to_project(self):
        w=world(n=6,stock={'food':8,'water':8,'wood':2,'scrap':2})
        self.assertTrue(w.start_project('garden'))
        bento='ZC-HER-0006'
        self.assertEqual(w.skill_bonus(bento,'build'),1)
        self.assertTrue(w.work_project('garden',1,hero_id=bento))
        self.assertIn('garden',w.structures)

    def test_skill_resource_travel_search_repair_and_storage_hooks(self):
        w=world(n=8,stock={'food':8,'water':8,'wood':2,'scrap':2,'fuel':4})
        rosa='ZC-HER-0008';nara='ZC-HER-0005';caio='ZC-HER-0004';duda='ZC-HER-0007'
        w.award_xp(rosa,12)
        self.assertGreater(w.storage,system.DATA['rules']['storage_base'])
        w.structures['reservoir']={'health':3,'age':0}
        self.assertTrue(w.use_structure('reservoir',nara))
        self.assertGreaterEqual(w.stock['water'],9)
        w.structures['workshop']={'health':1,'age':0}
        w.repair_structure('workshop',hero_id=duda)
        self.assertEqual(w.structures['workshop']['health'],3)
        w.award_xp(caio,12)
        w.open_expedition('fast',[caio],'EXP-LOC-03')
        self.assertEqual(w.expeditions['fast'].segment_cost,1)
        w.advance_expedition('fast')
        self.assertGreaterEqual(w.search('fast',hero_id=caio)['scrap'],3)

    def test_food_rescue_defense_and_infection_skills(self):
        rosa='ZC-HER-0008';lia='ZC-HER-0001';ivo='ZC-HER-0002';yumi='ZC-HER-0010'
        w=system.World.new(17,[lia,ivo,rosa,yumi],
                           {'food':10,'water':10,'medicine':2,'wood':2,'scrap':1})
        self.assertTrue(w.start_project('garden'))
        w.work_project('garden',2)
        w.assign_garden(rosa)
        w.award_xp(lia,20)
        w.heroes[ivo]['health']=0
        self.assertEqual(w.rescue_hero(lia,ivo),2)
        w.guard(ivo)
        self.assertEqual(w.receive_damage(ivo,2)['health'],2)
        result=w.roll_infection(yumi)
        self.assertEqual(result['adjusted'],min(6,result['roll']+w.skill_bonus(yumi,'infection')))
        days=[w.end_day() for _ in range(4)]
        self.assertGreaterEqual(days[-1]['produced']['food'],3)

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
        self.assertEqual(w.search('a'),{'scrap':2})
        self.assertEqual(w.stock,before)
        w.begin_return('a')
        w.advance_expedition('a');w.advance_expedition('a')
        self.assertEqual(w.stock['scrap'],2)
        self.assertEqual(w.stock['fuel'],0)
        self.assertEqual(w.log[-1]['left_behind'],{})

    def test_separate_expeditions_and_return(self):
        w=world(n=4,stock={'food':8,'water':8})
        heroes=list(w.heroes)
        w.open_expedition('A',heroes[:2],'EXP-LOC-02')
        w.open_expedition('B',heroes[2:],'EXP-LOC-03')
        with self.assertRaises(ValueError): w.open_expedition('C',heroes[:1],'EXP-LOC-01')
        self.assertEqual(w.advance_expedition('A'),'arrived')
        self.assertEqual(w.expeditions['B'].segment_cost,1)  # Caio: viagem +1
        self.assertEqual(w.advance_expedition('B'),'arrived')
        w.begin_return('A');self.assertEqual(w.advance_expedition('A'),'returned')
        self.assertEqual(w.heroes[heroes[0]]['location'],'camp')
        self.assertIn('B',w.expeditions)

    def test_vehicle_recovery_fuel_and_round_trip(self):
        w=world(stock={'food':4,'water':4,'fuel':5})
        h=next(iter(w.heroes))
        w.open_expedition('repair',[h],'EXP-LOC-03')
        w.advance_expedition('repair');w.advance_expedition('repair')
        self.assertTrue(w.recover_vehicle('EXP-VEI-01','repair'))
        self.assertEqual(w.stock['fuel'],3)
        w.begin_return('repair')
        w.advance_expedition('repair');w.advance_expedition('repair')
        self.assertEqual(w.vehicles['EXP-VEI-01']['location'],'camp')
        w.open_expedition('drive',[h],'EXP-LOC-01',vehicle_id='EXP-VEI-01')
        self.assertEqual(w.stock['fuel'],1)
        with self.assertRaises(ValueError):
            w.open_expedition('other',[list(w.heroes)[1]],'EXP-LOC-05',vehicle_id='EXP-VEI-01')
        w.validate()

    def test_driver_and_scout_crew_are_absent_from_camp_jobs(self):
        w=world(stock={'food':8,'water':8,'fuel':4})
        self.assertTrue(w.recruit('EXP-NPC-06'))
        self.assertTrue(w.recruit('EXP-NPC-09'))
        w.assign('EXP-NPC-06','driving')
        w.assign('EXP-NPC-09','scouting')
        w.vehicles['EXP-VEI-01']={'location':'camp','health':3}
        h=next(iter(w.heroes))
        w.open_expedition('crew',[h],'EXP-LOC-03',vehicle_id='EXP-VEI-01',
                          npc_ids=['EXP-NPC-06','EXP-NPC-09'])
        self.assertEqual(w.expeditions['crew'].segment_cost,1)
        self.assertEqual(w.stock['fuel'],2)
        self.assertEqual(w.advance_expedition('crew'),'arrived')
        self.assertEqual(w.search('crew'),{'scrap':3})
        w.begin_return('crew');w.advance_expedition('crew')
        self.assertEqual(w.npcs['EXP-NPC-06']['location'],'camp')
        self.assertEqual(w.npcs['EXP-NPC-09']['location'],'camp')
        w.validate()

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

    def test_npc_build_research_and_rescue_daily(self):
        w=world(stock={'food':8,'water':8,'wood':4,'scrap':4,'medicine':1})
        self.assertTrue(w.recruit('EXP-NPC-04'))
        self.assertTrue(w.recruit('EXP-NPC-14'))
        self.assertTrue(w.recruit('EXP-NPC-12'))
        w.assign('EXP-NPC-04','carpentry')
        w.assign('EXP-NPC-14','radio')
        w.assign('EXP-NPC-12','rescue')
        self.assertTrue(w.start_project('garden'))
        hero=next(iter(w.heroes));w.heroes[hero]['health']=2
        w.end_day()
        self.assertEqual(w.projects['garden'],1)
        self.assertEqual(w.clues,1)
        self.assertEqual(w.heroes[hero]['health'],3)
        self.assertEqual(w.stock['medicine'],0)

    def test_structure_actions_cost_limit_and_effect(self):
        w=world(stock={'food':4,'water':4,'scrap':3,'fuel':1,'medicine':1})
        for kind in ('workshop','infirmary','reservoir'):
            w.structures[kind]={'health':3,'age':0}
        hero=next(iter(w.heroes));w.heroes[hero]['health']=2
        self.assertTrue(w.use_structure('workshop'))
        self.assertEqual((w.stock['scrap'],w.stock['ammo']),(1,1))
        self.assertFalse(w.use_structure('workshop'))
        self.assertTrue(w.use_structure('infirmary',hero))
        self.assertEqual(w.heroes[hero]['health'],3)
        self.assertTrue(w.use_structure('reservoir'))
        self.assertEqual((w.stock['fuel'],w.stock['water']),(0,6))
        w.validate()

    def test_data_rebuild_deterministic(self):
        before=(ROOT/'data/system.json').read_bytes()
        import subprocess
        subprocess.run([sys.executable,str(ROOT/'data/build_system_data.py')],check=True)
        self.assertEqual(before,(ROOT/'data/system.json').read_bytes())

    def test_save_mid_expedition_preserves_cargo_and_rng(self):
        w=world(seed=71,stock={'food':4,'water':4})
        h=next(iter(w.heroes))
        w.open_expedition('x',[h],'EXP-LOC-02')
        w.advance_expedition('x');w.search('x');w.begin_return('x')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'world.json';w.save(path)
            restored=system.World.load(path)
            self.assertEqual(restored.expeditions['x'].cargo,w.expeditions['x'].cargo)
            self.assertEqual(restored.advance_expedition('x'),w.advance_expedition('x'))
            self.assertEqual(restored.end_day(),w.end_day())

    def test_integrated_replay_is_reproducible(self):
        spec2=importlib.util.spec_from_file_location('integral_sim',ROOT/'simulate_system.py')
        module=importlib.util.module_from_spec(spec2)
        sys.path.insert(0,str(ROOT))
        try: spec2.loader.exec_module(module)
        finally: sys.path.pop(0)
        self.assertEqual(module.aggregate(123,3),module.aggregate(123,3))
        self.assertEqual(module.aggregate(123,3)['total_replays'],15)

    def test_catalog_validation_and_full_state_roundtrip(self):
        spec3=importlib.util.spec_from_file_location('integral_validator',ROOT/'validate_data.py')
        module=importlib.util.module_from_spec(spec3);spec3.loader.exec_module(module)
        self.assertEqual(module.validate()['unique_ids'],127)
        self.assertEqual(module.validate()['cards'],7)
        self.assertEqual(module.validate()['tactical_maps'],8)
        w=world(seed=9,stock={'food':6,'water':6,'wood':6,'scrap':6,'fuel':3,'ammo':1,'medicine':1})
        hero=next(iter(w.heroes))
        w.give_item(hero,'bag-01','EXP-EQU-003','torso')
        w.give_item(hero,'knife-01','EXP-EQU-001','backpack',x=0,y=0)
        self.assertTrue(w.recruit('EXP-NPC-10'))
        w.assign('EXP-NPC-10','guard')
        self.assertTrue(w.start_project('garden'))
        w.work_project('garden',2)
        self.assertTrue(w.start_project('workshop'))
        w.work_project('workshop')
        w.searches['EXP-LOC-05']=0
        self.assertTrue(w.establish_outpost('EXP-LOC-05','EXP-NPC-10'))
        w.active_crises.append('EXP-CRI-01')
        w.crises_last_day['EXP-CRI-01']=0
        w.damage_structure('garden')
        w.open_expedition('e',[hero],'EXP-LOC-03')
        w.advance_expedition('e');w.advance_expedition('e')
        w.search('e')
        self.assertTrue(w.recover_vehicle('EXP-VEI-01','e'))
        w.begin_return('e')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'state.json';w.save(path)
            loaded=system.World.load(path)
            self.assertEqual(loaded,w)
            for obj in (w,loaded):
                obj.advance_expedition('e');obj.advance_expedition('e');obj.end_day()
            self.assertEqual(loaded,w)


if __name__=='__main__':unittest.main()
