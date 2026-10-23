import sys
import tempfile
import unittest
from itertools import combinations
from math import ceil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cistern02 import Cistern02, LINK_IDS, STARTERS


class Cistern02Tests(unittest.TestCase):
    def test_all_2497_link_draws_match_canonical_preparation(self):
        checked=0
        for heroes in range(2,7):
            for draw in combinations(LINK_IDS,heroes):
                game=Cistern02.new(STARTERS[:heroes],list(draw))
                extra_humans=sum(link in LINK_IDS[4:10] or link==LINK_IDS[11] for link in draw)
                dogs=sum(link in LINK_IDS[10:] for link in draw)
                consumers=heroes+extra_humans+dogs
                self.assertEqual(game.humans,heroes+extra_humans)
                self.assertEqual(game.dogs,dogs)
                self.assertEqual(game.consumers,consumers)
                self.assertEqual(game.capacity,2*max(4,heroes))
                self.assertEqual(len(game.food),ceil(2*consumers/4))
                self.assertEqual(len(game.water),ceil(2*consumers/4))
                self.assertTrue(all(lot==4 for lot in game.food+game.water))
                checked+=1
        self.assertEqual(checked,2497)

    def test_portions_spoilage_and_shared_clock(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.meat=[4]
        meal=game.meal()
        self.assertEqual(meal['food_missing'],0)
        self.assertEqual(meal['water_missing'],0)
        self.assertEqual(meal['meat_expired'],2)
        self.assertEqual(game.food,[4])
        with self.assertRaises(ValueError):game.meal()
        game.spend_segments(8)
        self.assertEqual(game.night_segments,0)
        game.spend_segments(2)
        self.assertEqual(game.night_segments,2)
        with self.assertRaises(ValueError):game.spend_segments(1)

    def test_filter_parts_must_arrive_before_reservation(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.receive_part('Conexões')
        with self.assertRaises(ValueError):game.reserve('A')
        game.meal()
        game.next_day()
        game.reserve('A')
        game.work(1)
        self.assertEqual(game.stage,'B')
        self.assertEqual(game.materials,2)
        game.receive_part('Bomba');game.receive_part('Membrana')
        with self.assertRaises(ValueError):game.reserve('B')
        game.meal()
        game.next_day();game.reserve('B');game.reserve('C')
        game.work(2)
        self.assertEqual(game.stage,'C')
        game.meal()
        game.next_day();game.work(1)
        self.assertTrue(game.filter_active)
        self.assertEqual(sum(game.water),4)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cistern.json';game.save(path)
            self.assertEqual(Cistern02.load(path),game)

    def test_cannot_skip_meal_or_partially_spend_invalid_work(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        with self.assertRaises(ValueError):game.next_day()
        game.receive_part('Conexões');game.meal();game.next_day()
        game.reserve('A')
        with self.assertRaises(ValueError):game.work(2)
        self.assertEqual(game.stage_work,0)
        self.assertEqual(game.works_today,0)


if __name__=='__main__':unittest.main()
