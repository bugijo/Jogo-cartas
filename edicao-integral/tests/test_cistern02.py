import sys
import tempfile
import unittest
from itertools import combinations
from math import ceil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT.parent/'src'))
from cistern02 import Cistern02, LINK_IDS, STARTERS
from rules_engine import consume, family_setup


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
                oracle=family_setup(heroes,[
                    (int(link in LINK_IDS[4:10] or link==LINK_IDS[11]),
                     int(link in LINK_IDS[10:])) for link in draw])
                self.assertEqual(oracle['humans'],game.humans)
                self.assertEqual(oracle['dogs'],game.dogs)
                self.assertEqual(oracle['capacity'],game.capacity)
                self.assertEqual(oracle['food'],sum(game.food))
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
        self.assertEqual(consume(4,4,2),(4,0,2))
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
        game.work(1);game.meal()
        with self.assertRaises(ValueError):game.work(1)

    def test_individual_deprivation_and_dog_alert(self):
        game=Cistern02.new(STARTERS[:2],[LINK_IDS[10],LINK_IDS[0]])
        self.assertEqual(len(game.people),3)
        dog=next(person for person in game.people if person['kind']=='dog')
        humans=[person for person in game.people if person['kind']=='hero']
        game.food=[1];game.water=[1]
        order=[humans[0]['id'],humans[1]['id'],dog['id']]
        first=game.meal(food_priority=order,water_priority=order)
        self.assertEqual((first['food_missing'],first['water_missing']),(2,2))
        self.assertFalse(dog['alert'])
        self.assertEqual(humans[1]['streak'],1)
        game.next_day();game.food=[];game.water=[]
        game.meal()
        self.assertEqual(humans[1]['wounds'],1)
        game.next_day();game.meal()
        self.assertEqual(game.health,0)
        self.assertTrue(humans[1]['hungry'])
        self.assertTrue(humans[1]['thirsty'])

    def test_priority_must_list_each_consumer_once(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        with self.assertRaises(ValueError):game.meal(food_priority=[STARTERS[0]]*2)
        self.assertEqual(game.meal_day,0)

    def test_pressure_queue_and_canonical_siege_losses(self):
        game=Cistern02.new(STARTERS[:2],[LINK_IDS[10],LINK_IDS[0]])
        game.raise_pressure(3)
        game.raise_pressure(1)
        self.assertEqual(game.pending_sieges,['Pressão'])
        result=game.resolve_siege(strength=5,guards=[],rolls=[],ammo=0,
                                  damage_targets=['Portão'])
        self.assertEqual(result['gap'],2)
        self.assertEqual(game.pressure,1)
        self.assertEqual(game.pending_sieges,[])
        self.assertNotIn('Portão',game.structures)
        self.assertEqual(sum(game.food),4)
        with self.assertRaises(ValueError):game.resolve_siege(4,[],[],0,[])

    def test_siege_must_use_preallocated_guards_and_ammo(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.queue_siege('Missão dia 3')
        game.plan_guards([STARTERS[0]])
        with self.assertRaises(ValueError):
            game.resolve_siege(4,[STARTERS[0]],[5],3,[])
        result=game.resolve_siege(4,[STARTERS[0]],[5],1,[])
        self.assertEqual(result['defense'],4)
        self.assertEqual(game.ammo,1)

    def test_rescue_capacity_group_integrity_and_portions(self):
        game=Cistern02.new(STARTERS[:4],LINK_IDS[:4],seed=7)
        self.assertEqual(game.capacity,8)
        result=game.rescue('ZC-MOR-0001','welcome')
        self.assertEqual(result['humans'],2)
        self.assertEqual(game.humans,6)
        self.assertEqual(game.consumers,6)
        with self.assertRaises(ValueError):game.rescue('ZC-MOR-0001','welcome')
        game.rescue('ZC-MOR-0005','welcome')
        self.assertEqual(game.humans,9)
        self.assertEqual(game.temporary_excess,1)
        with self.assertRaises(ValueError):game.rescue('ZC-MOR-0006','welcome')
        game.rescue('ZC-MOR-0006','aid')
        self.assertEqual(game.humans,9)
        self.assertEqual(sum(game.food),5)
        self.assertEqual(sum(game.water),5)

    def test_declined_group_remains_available_without_penalty(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        before=(game.morale,game.health,len(game.intent_deck))
        game.rescue('ZC-MOR-0002','decline')
        self.assertEqual((game.morale,game.health,len(game.intent_deck)),before)
        game.rescue('ZC-MOR-0002','welcome')
        self.assertEqual(game.humans,3)

    def test_hidden_intention_reveals_on_second_night_without_duplication(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=3)
        game.rescue('ZC-MOR-0002','welcome')
        game.meal()
        with self.assertRaises(ValueError):game.next_day()
        self.assertEqual(game.night_intentions(),[])
        game.next_day();game.meal()
        revealed=game.night_intentions()
        self.assertEqual(len(revealed),1)
        self.assertEqual(revealed[0]['id'],'ZC-MOR-0002')
        with self.assertRaises(ValueError):game.night_intentions()

    def test_pending_siege_must_resolve_one_per_night(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.queue_siege('Missão dia 3')
        with self.assertRaises(ValueError):game.next_day()
        with self.assertRaises(ValueError):game.meal()
        game.resolve_siege(4,[],[],0,['Portão'])
        game.meal()
        game.next_day()

    def test_verified_opportunist_leaves_without_stealing(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.intent_deck[0]='ZC-INT-0011'
        game.rescue('ZC-MOR-0002','welcome')
        game.investigate('ZC-MOR-0002',2)
        before=sum(game.food)
        game.meal();result=game.night_intentions()
        self.assertEqual(result[0]['effect'],'left_verified')
        self.assertEqual(game.humans,2)
        self.assertEqual(sum(game.food),before-3)

    def test_temporary_overcrowding_cost_starts_third_night(self):
        game=Cistern02.new(STARTERS[:4],LINK_IDS[:4])
        game.intent_deck[:2]=['ZC-INT-0001','ZC-INT-0002']
        game.rescue('ZC-MOR-0001','welcome')
        game.rescue('ZC-MOR-0005','welcome')
        for expected in (5,5,4):
            game.meal();game.night_intentions()
            self.assertEqual(game.morale,expected)
            if game.day<3:game.next_day()

    def test_day_five_cannot_claim_victory_without_filter(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.food.extend([4,4,4]);game.water.extend([4,4,4])
        for _ in range(4):game.meal();game.next_day()
        game.meal()
        self.assertEqual(game.close_chapter(),'partial_defeat')

    def test_pending_security_night_blocks_final_result(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.food.extend([4,4,4]);game.water.extend([4,4,4])
        for _ in range(4):game.meal();game.next_day()
        game.queue_siege('Pressão')
        game.resolve_siege(2,[],[],0,[])
        game.meal()
        game.queue_siege('Infiltrado tardio')
        with self.assertRaises(ValueError):game.close_chapter()
        game.resolve_siege(2,[],[],0,[],security=True)
        self.assertEqual(game.close_chapter(),'partial_defeat')

    def test_filter_and_full_last_meal_yield_only_provisional_result(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.food.extend([4,4,4]);game.water.extend([4,4,4])
        game.receive_part('Conexões')
        game.meal();game.next_day();game.reserve('A');game.work(1)
        game.receive_part('Bomba');game.receive_part('Membrana')
        game.meal();game.next_day();game.reserve('B');game.reserve('C');game.work(2)
        game.meal();game.next_day();game.work(1)
        game.meal();game.next_day();game.meal()
        self.assertEqual(game.close_chapter(),'candidate_victory')
        self.assertNotIn('cistern_complete',game.__dict__)

    def test_siege_can_disable_completed_filter(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.receive_part('Conexões');game.meal();game.next_day()
        game.reserve('A');game.work(1)
        game.receive_part('Bomba');game.receive_part('Membrana')
        game.meal();game.next_day()
        game.reserve('B');game.reserve('C');game.work(2)
        game.meal();game.next_day();game.work(1)
        self.assertIn('Filtro',game.structures)
        game.meal();game.next_day()
        game.queue_siege('Pressão')
        game.resolve_siege(4,[],[],0,['Filtro'])
        self.assertFalse(game.filter_active)
        water_before=sum(game.water)
        game.materials+=2  # Materiais recuperados: fixture de reparo, não rota de busca.
        game.repair_filter()
        self.assertTrue(game.filter_active)
        self.assertEqual(sum(game.water),water_before)


if __name__=='__main__':unittest.main()
