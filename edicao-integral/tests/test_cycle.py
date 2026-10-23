import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from campaign import CARDS, apply_event, play_market_day
from simulate_cycle import aggregate
from system import World


class CycleTests(unittest.TestCase):
    def test_event_choice_has_requirements_and_persistent_consequence(self):
        w=World.new(11,['ZC-HER-0001','ZC-HER-0002'],{'food':6,'water':6})
        w.open_expedition('m',list(w.heroes),'EXP-LOC-02')
        w.advance_expedition('m')
        result=apply_event(w,'m','EXP-EVT-001','inspect','ZC-HER-0001')
        self.assertEqual(result['cargo'],{'scrap':1})
        self.assertEqual(w.expeditions['m'].cargo['scrap'],1)
        with self.assertRaises(ValueError):apply_event(w,'m','EXP-EVT-001','inspect','ZC-HER-0001')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'save.json';w.save(p);copy=World.load(p)
            self.assertEqual(copy.decisions,w.decisions)

    def test_replay_complete_day_and_restore(self):
        result=play_market_day(17,'balanced')
        self.assertEqual(result['phases'],['preparation','travel','exploration','event',
                                            'combat','loot','return','camp','save_restore'])
        self.assertEqual(result['state_before_save'],result['state_after_load'])
        self.assertEqual(result['day'],1)
        self.assertIn(result['outcome'],('mission_complete','retreated','defeat'))
        self.assertGreaterEqual(result['searches_used'],1)
        self.assertIn('EXP-MIS-001',CARDS)

    def test_replay_seed_is_deterministic(self):
        self.assertEqual(play_market_day(17,'balanced'),play_market_day(17,'balanced'))

    def test_scenario_handles_weapon_breakage_without_crash(self):
        result=play_market_day(2,'balanced')
        self.assertIn(result['outcome'],('mission_complete','retreated','defeat'))
        self.assertEqual(result['searches_used'],0)

    def test_team_sizes_and_strategy_decisions(self):
        for size in range(2,7):
            result=play_market_day(17,'balanced',team_size=size)
            self.assertEqual(result['team_size'],size)
            self.assertEqual(result['state_before_save'],result['state_after_load'])
        explorer=play_market_day(17,'explorer',team_size=2)
        builder=play_market_day(17,'builder',team_size=2)
        self.assertEqual(explorer['searches_used'],2)
        self.assertTrue(builder['garden_built'])

    def test_aggregate_replays_all_sizes_and_strategies(self):
        a=aggregate(101,2)
        self.assertEqual(a,aggregate(101,2))
        self.assertEqual(a['total_replays'],50)
        self.assertEqual(len(a['groups']),25)


if __name__=='__main__':unittest.main()
