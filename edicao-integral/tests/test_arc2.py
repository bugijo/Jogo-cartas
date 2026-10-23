import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from system import World
from arc2 import Arc2, ARC_CARDS


class Arc2Tests(unittest.TestCase):
    def test_final_defense_is_explicitly_unfinished(self):
        w=World.new(1,['ZC-HER-0001'],{'food':2,'water':2})
        with self.assertRaises(NotImplementedError):Arc2(w).final_defense()

    def test_transmitter_cannot_be_loaded_by_two_teams(self):
        heroes=['ZC-HER-0001','ZC-HER-0002']
        w=World.new(1,heroes,{'food':4,'water':4})
        w.flags['military_access']=True
        for label,hero in zip(('a','b'),heroes):
            w.open_expedition(label,[hero],'EXP-LOC-06')
            for _ in range(3):w.advance_expedition(label)
        arc=Arc2(w)
        arc.load_transmitter('a')
        with self.assertRaises(ValueError):arc.load_transmitter('b')

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
