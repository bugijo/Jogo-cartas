import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from system import World
from arc2 import Arc2, ARC_CARDS


class Arc2Tests(unittest.TestCase):
    def defense_world(self):
        w=World.new(1,['ZC-HER-0001','ZC-HER-0002'],{'food':4,'water':4})
        w.flags.update(cistern_complete=True,radio_code=True,access_card=True,military_access=True)
        w.special_stock.append('transmitter')
        w.give_item('ZC-HER-0001','crowbar','EXP-EQU-002','hand')
        return w

    def test_final_defense_requires_completed_chain(self):
        w=self.defense_world();w.flags['cistern_complete']=False
        with self.assertRaises(ValueError):Arc2(w).final_defense()
        w.flags['cistern_complete']=True
        state=Arc2(w).final_defense()
        self.assertEqual(state['status'],'active')
        with self.assertRaises(ValueError):Arc2(w).final_defense()

    def test_defense_can_be_saved_attacked_and_finished(self):
        w=self.defense_world();arc=Arc2(w);arc.final_defense()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'defense.json';w.save(path)
            restored=World.load(path)
            self.assertEqual(restored.final_defense,w.final_defense)
            arc=Arc2(restored)
            enemy=next(iter(restored.final_defense['enemies']))
            arc.defense_move('ZC-HER-0001',2)
            with self.assertRaises(ValueError):arc.defense_attack('ZC-HER-0001','crowbar',enemy)
            restored.final_defense['enemies'][enemy]['zone']=2
            arc.defense_attack('ZC-HER-0001','crowbar',enemy)
            # A progressão das ondas é testada sem supor que cinco usos da ferramenta
            # bastam para derrotar toda a defesa com uma única peça.
            restored.final_defense['enemies'].clear()
            self.assertEqual(arc.defense_activate()['status'],'active')
            self.assertEqual(restored.final_defense['wave'],2)

    def test_all_waves_enable_free_survival_once(self):
        w=self.defense_world();arc=Arc2(w);arc.final_defense()
        for _ in range(3):
            w.final_defense['enemies'].clear()
            result=arc.defense_activate()
        self.assertEqual(result['status'],'won')
        self.assertTrue(w.flags['free_survival'])
        with self.assertRaises(ValueError):arc.defense_activate()

    def test_retreat_and_objective_loss_are_persistent(self):
        w=self.defense_world();arc=Arc2(w);arc.final_defense()
        arc.defense_retreat()
        self.assertEqual(w.final_defense['status'],'retreated')
        self.assertFalse(w.flags.get('free_survival',False))
        w=self.defense_world();arc=Arc2(w);arc.final_defense()
        w.final_defense['integrity']=1
        w.final_defense['enemies']={'E999':{'kind':'runner','zone':2,'health':1}}
        self.assertEqual(arc.defense_activate()['status'],'lost')

    def test_transmitter_cannot_be_loaded_twice(self):
        heroes=['ZC-HER-0001','ZC-HER-0002']
        w=World.new(1,heroes,{'food':4,'water':4,'fuel':6})
        w.flags['military_access']=True
        w.flags['radio_code']=True
        w.flags['access_card']=True
        w.vehicles['EXP-VEI-01']={'location':'camp','health':3}
        w.open_expedition('a',[heroes[0]],'EXP-LOC-06',vehicle_id='EXP-VEI-01')
        for _ in range(3):w.advance_expedition('a')
        arc=Arc2(w)
        arc.load_transmitter('a')
        with self.assertRaises(ValueError):arc.load_transmitter('a')

    def test_direct_military_trip_cannot_bypass_card_and_code(self):
        w=World.new(1,['ZC-HER-0001'],{'food':2,'water':2,'fuel':6})
        w.vehicles['EXP-VEI-01']={'location':'camp','health':3}
        with self.assertRaises(ValueError):
            w.open_expedition('illegal',['ZC-HER-0001'],'EXP-LOC-06',vehicle_id='EXP-VEI-01')

    def test_code_card_access_and_transport_persist(self):
        w=World.new(8,['ZC-HER-0001','ZC-HER-0002'],
                    {'food':6,'water':6,'fuel':6,'ammo':2})
        arc=Arc2(w)
        with self.assertRaises(ValueError):arc.decode_radio()
        w.flags['cistern_complete']=True
        w.clues=2
        arc.decode_radio()
        self.assertTrue(w.flags['radio_code'])
        with self.assertRaises(ValueError):arc.recover_access_card('trip')
        hero=next(iter(w.heroes))
        w.open_expedition('trip',[hero],'EXP-LOC-05')
        for _ in range(3):w.advance_expedition('trip')
        w.search('trip')
        arc.recover_access_card('trip')
        w.begin_return('trip')
        for _ in range(3):w.advance_expedition('trip')
        w.vehicles['EXP-VEI-01']={'location':'camp','health':3}
        arc.authorize_installation('military',[hero],'EXP-VEI-01')
        for _ in range(3):w.advance_expedition('military')
        arc.load_transmitter('military')
        w.begin_return('military')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'arc.json';w.save(path)
            restored=World.load(path)
            self.assertEqual(restored.flags,w.flags)
            self.assertEqual(restored.expeditions['military'].special_cargo,['transmitter'])
            for _ in range(3):restored.advance_expedition('military')
            self.assertIn('transmitter',restored.special_stock)
        self.assertEqual(len(ARC_CARDS),5)


if __name__=='__main__':unittest.main()
