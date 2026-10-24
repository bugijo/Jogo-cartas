import json
import sys
import tempfile
import unittest
from collections import Counter
from itertools import combinations
from math import ceil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT.parent/'src'))
from cistern02 import Cistern02, LINK_IDS, STARTERS
from rules_engine import consume, family_setup


class Cistern02Tests(unittest.TestCase):
    @staticmethod
    def _resolve_day_three_event(game):
        if game.pending_sieges and game.pending_sieges[0]=='Barulho no vale':
            # Phase-gate fixture: force4 against gate2 causes one structural loss.
            # Keep this helper independent of exhausted/wounded vigias in tests
            # whose subject is deprivation rather than siege tactics.
            eligible=[name for name in game.structures if name not in ('Barraca','Casa simples')]
            base=(2 if 'Portão' in game.structures else 0)+int('Torre' in game.structures)
            base+=int(any(person['kind']=='dog' and person['alert'] for person in game.people))
            gap=max(0,4-base)
            count=0 if gap==0 else 1 if gap<=2 else 2
            preferred=['Depósito','Cozinha','Portão']
            return game.resolve_siege(4,[],[],0,[name for name in preferred if name in eligible][:count])
        if game.pending_sieges and game.pending_sieges[0]=='Pressão':
            encounter=game.reveal_siege()
            force=encounter['force']
            base=(2 if 'Portão' in game.structures else 0)+int('Torre' in game.structures)
            base+=int(any(person['kind']=='dog' and person['alert'] for person in game.people))
            ammo=max(0,min(2,force-base-2))
            gap=max(0,force-(base+ammo))
            eligible=[name for name in game.structures if name not in ('Barraca','Casa simples')]
            count=min(len(eligible),0 if gap==0 else 1 if gap<=2 else 2)
            preferred=['Depósito','Cozinha','Portão','Filtro']
            targets=[name for name in preferred if name in eligible][:count]
            return game.resolve_siege(force,[],[],ammo,targets)
        return None

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
        game.next_day();self._resolve_day_three_event(game);game.reserve('B');game.reserve('C')
        game.work(2)
        self.assertEqual(game.stage,'C')
        game.meal()
        game.next_day();self._resolve_day_three_event(game);game.work(1)
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
        game.next_day();self._resolve_day_three_event(game);game.food=[];game.water=[]
        game.meal()
        self.assertEqual(humans[1]['wounds'],1)
        game.next_day();self._resolve_day_three_event(game);game.meal()
        self.assertEqual(game.health,0)
        self.assertTrue(humans[1]['hungry'])
        self.assertTrue(humans[1]['thirsty'])

    def test_priority_must_list_each_consumer_once(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        with self.assertRaises(ValueError):game.meal(food_priority=[STARTERS[0]]*2)
        self.assertEqual(game.meal_day,0)

    def test_pressure_queue_and_canonical_siege_losses(self):
        game=Cistern02.new(STARTERS[:2],[LINK_IDS[10],LINK_IDS[0]])
        game.siege_deck=['ZC-CER-0002']
        game.raise_pressure(3)
        game.raise_pressure(1)
        self.assertEqual(game.pending_sieges,['Pressão'])
        encounter=game.reveal_siege()
        ammo=0
        result=game.resolve_siege(strength=encounter['force'],guards=[],rolls=[],ammo=ammo,
                                  damage_targets=['Portão'])
        self.assertEqual(result['gap'],2)
        self.assertEqual(game.pressure,1)
        self.assertEqual(game.pending_sieges,[])
        self.assertNotIn('Portão',game.structures)
        self.assertEqual(sum(game.food),4)
        with self.assertRaises(ValueError):game.resolve_siege(4,[],[],0,[])

    def test_siege_must_use_preallocated_guards_and_ammo(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.meal();game.next_day();game.meal();game.next_day()
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
        game.meal();game.next_day();game.meal();game.next_day()
        with self.assertRaises(ValueError):game.next_day()
        with self.assertRaises(ValueError):game.meal()
        game.resolve_siege(4,[],[],0,['Depósito'])
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
            if game.day<3:
                game.next_day();self._resolve_day_three_event(game)

    def test_day_five_cannot_claim_victory_without_filter(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.food.extend([4,4,4]);game.water.extend([4,4,4])
        for _ in range(4):
            game.meal();game.next_day();self._resolve_day_three_event(game)
        game.meal()
        self.assertEqual(game.close_chapter(),'partial_defeat')

    def test_pending_security_night_blocks_final_result(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.food.extend([4,4,4]);game.water.extend([4,4,4])
        for _ in range(3):
            game.meal();game.next_day();self._resolve_day_three_event(game)
        game.meal();game.next_day()
        self.assertEqual(game.day,5)
        self.assertEqual(game.pending_sieges,['Pressão'])
        encounter=game.reveal_siege();force=encounter['force']
        base=2+int(any(person['kind']=='dog' and person['alert'] for person in game.people))
        ammo=max(0,min(2,force-base-2));gap=max(0,force-(base+ammo))
        eligible=[name for name in game.structures if name not in ('Barraca','Casa simples')]
        count=0 if gap==0 else 1 if gap<=2 else 2;targets=eligible[:count]
        game.resolve_siege(force,[],[],ammo,targets)
        game.pressure=2;game.raise_pressure(1)
        game.meal()
        with self.assertRaises(ValueError):game.close_chapter()
        encounter=game.reveal_siege();force=encounter['force']
        ammo=max(0,min(2,force-base-2));gap=max(0,force-(base+ammo))
        eligible=[name for name in game.structures if name not in ('Barraca','Casa simples')]
        count=0 if gap==0 else 1 if gap<=2 else 2;targets=eligible[:count]
        game.resolve_siege(force,[],[],ammo,targets,security=True)
        self.assertEqual(game.close_chapter(),'partial_defeat')

    def test_filter_and_full_last_meal_yield_only_provisional_result(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        # Isolated shelter-state fixture with enough reserve for both mandatory sieges.
        game.food.extend([4,4,4,4]);game.water.extend([4,4,4])
        game.receive_part('Conexões')
        game.meal();game.next_day();game.reserve('A');game.work(1)
        game.receive_part('Bomba');game.receive_part('Membrana')
        game.meal();game.next_day();self._resolve_day_three_event(game);game.reserve('B');game.reserve('C');game.work(2)
        game.meal();game.next_day();self._resolve_day_three_event(game);game.work(1)
        game.meal();game.next_day();self._resolve_day_three_event(game);game.meal()
        self.assertEqual(game.close_chapter(),'candidate_victory')
        self.assertNotIn('cistern_complete',game.__dict__)

    def test_candidate_victory_cannot_be_certified_without_legal_objectives(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.result='candidate_victory'
        with self.assertRaises(ValueError):
            game.certify_victory([])
        self.assertEqual(game.result,'candidate_victory')

    def test_objective_names_alone_cannot_certify_missing_parts_or_filter(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.result='candidate_victory'
        claimed=['Oficina:Conexões','Estação:Bomba','Estação:Membrana']
        with self.assertRaises(ValueError):
            game.certify_victory(claimed)
        self.assertEqual(game.result,'candidate_victory')
        self.assertEqual(game.parts,{})
        self.assertFalse(game.filter_completed)

    def test_siege_can_disable_completed_filter(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.receive_part('Conexões');game.meal();game.next_day()
        game.reserve('A');game.work(1)
        game.receive_part('Bomba');game.receive_part('Membrana')
        game.meal();game.next_day();self._resolve_day_three_event(game)
        game.reserve('B');game.reserve('C');game.work(2)
        game.meal();game.next_day();self._resolve_day_three_event(game);game.work(1)
        self.assertIn('Filtro',game.structures)
        game.meal();game.next_day()
        self.assertEqual(game.pending_sieges,['Pressão'])
        encounter=game.reveal_siege();force=encounter['force']
        ammo=max(0,min(2,force-4));gap=max(0,force-(2+ammo))
        targets=['Filtro'] if gap<=2 else ['Filtro','Depósito']
        game.resolve_siege(force,[],[],ammo,targets)
        self.assertFalse(game.filter_active)
        water_before=sum(game.water)
        game.materials+=2  # Materiais recuperados: fixture de reparo, não rota de busca.
        game.repair_filter()
        self.assertTrue(game.filter_active)
        self.assertEqual(sum(game.water),water_before)

    def test_pressure_siege_requires_seeded_revealed_card_and_persists_it(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=998)
        game.raise_pressure(3)
        before=game.__dict__.copy()
        with self.assertRaisesRegex(ValueError,'Revele a carta'):
            game.resolve_siege(4,[],[],0,[])
        self.assertEqual(game.__dict__,before)
        revealed=game.reveal_siege()
        self.assertIn(revealed['card_id'],('ZC-CER-0001','ZC-CER-0002','ZC-CER-0003',
                                            'ZC-CER-0004','ZC-CER-0005','ZC-CER-0006'))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cistern.json';game.save(path)
            resumed=Cistern02.load(path)
        self.assertEqual(resumed.reveal_siege(),revealed)
        wrong=2 if revealed['force']!=2 else 3
        with self.assertRaisesRegex(ValueError,'Força do Cerco revelado'):
            resumed.resolve_siege(wrong,[],[],0,[])
        self.assertEqual(resumed.reveal_siege(),revealed)
        game2=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=998)
        game2.raise_pressure(3)
        self.assertEqual(game2.reveal_siege(),revealed)

    def test_only_canonical_pressure_trigger_can_be_queued(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        with self.assertRaisesRegex(ValueError,'Não injete cercos'):
            game.queue_siege('Barulho dia 3')
        with self.assertRaisesRegex(ValueError,'Não injete cercos'):
            game.queue_siege('Infiltrado tardio')

    def test_bridge_relation_changes_only_rival_siege_force(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=1)
        game.siege_deck=['ZC-CER-0005']
        game.raise_pressure(3)
        game.adjust_bridge_relation(2)
        self.assertEqual(game.reveal_siege()['force'],4)
        self.assertEqual(game.bridge_relation,2)

    def test_day_five_guard_assignment_cannot_change_after_meal(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2])
        game.day=5;game.plan_guards([STARTERS[0]])
        game.meal_day=5
        with self.assertRaisesRegex(ValueError,'Vigias inválidos'):
            game.plan_guards([STARTERS[1]])

    def test_hostile_caravan_can_be_cancelled_only_by_paying_real_stock(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=17)
        game.siege_deck=['ZC-CER-0006']
        game.raise_pressure(3)
        game.plan_guards([STARTERS[0]])
        self.assertEqual(game.reveal_siege()['force'],6)
        result=game.resolve_siege(6,[],[],0,[],cancel_rivals=True)
        self.assertTrue(result['cancelled'])
        self.assertEqual(sum(game.food),0)
        self.assertEqual(sum(game.water),0)
        self.assertEqual(game.siege_receipts[-1]['card_id'],'ZC-CER-0006')

    def test_hostile_caravan_cannot_be_cancelled_when_stock_is_short(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=17)
        game.siege_deck=['ZC-CER-0006']
        game.raise_pressure(3);game.reveal_siege()
        game.food=[3]
        with self.assertRaisesRegex(ValueError,'Cancelamento'):
            game.resolve_siege(6,[],[],0,[],cancel_rivals=True)


    def test_canonical_events_apply_once_on_each_cistern_day_and_day_three_siege_is_fixed(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=222)
        self.assertEqual(game.event_history,['ZC-EVE-0001'])
        self.assertEqual(game.pressure,0)
        for expected_day,expected_pressure in ((2,1),(3,1)):
            game.meal()
            game.next_day()
            self.assertEqual(game.day,expected_day)
            self.assertEqual(game.pressure,expected_pressure)
        self.assertEqual(game.pending_sieges,['Barulho no vale'])
        before=game.__dict__.copy()
        with self.assertRaisesRegex(ValueError,'Força fixa 4'):
            game.resolve_siege(5,[],[],0,[])
        self.assertEqual(game.__dict__,before)
        result=game.resolve_siege(4,[],[],0,['Depósito'])
        self.assertEqual(result['trigger'],'Barulho no vale')
        self.assertEqual(result['strength'],4)
        game.meal();game.next_day()
        self.assertEqual(game.day,4)
        self.assertEqual(game.pressure,2)
        game.meal();game.next_day()
        self.assertEqual(game.day,5)
        self.assertEqual(game.pressure,3)
        self.assertEqual(game.pending_sieges,['Pressão'])
        self._resolve_day_three_event(game)
        game.meal()
        self.assertEqual(game.event_history,[f'ZC-EVE-{n:04d}' for n in range(1,6)])

    def test_daily_event_cursor_survives_save_load_and_cannot_be_replayed(self):
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=223)
        game.meal();game.next_day()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cistern.json'
            game.save(path);resumed=Cistern02.load(path)
        self.assertEqual(resumed.event_history,['ZC-EVE-0001','ZC-EVE-0002'])
        self.assertEqual(resumed.event_queue,['ZC-EVE-0003','ZC-EVE-0004','ZC-EVE-0005'])
        pressure=resumed.pressure
        resumed.meal();resumed.next_day()
        self.assertEqual(resumed.pressure,pressure)
        self.assertEqual(resumed.pending_sieges,['Barulho no vale'])

    def test_campaign_horde_and_travel_decks_migrate_and_round_trip(self):
        from dataclasses import asdict
        from travel_deck02 import CARD_IDS
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=608)
        state=asdict(game);state.pop('horde_deck');state.pop('travel_deck')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'legacy.json'
            path.write_text(json.dumps({'schema':1,'state':state}),encoding='utf-8')
            migrated=Cistern02.load(path)
        # Old saves derive both persistent shoes from the recorded campaign seed.
        fresh=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=608)
        self.assertEqual([migrated.draw_horde() for _ in range(9)],
                         [fresh.draw_horde() for _ in range(9)])
        travel=[migrated.draw_travel_card() for _ in range(24)]
        same_travel=[fresh.draw_travel_card() for _ in range(24)]
        self.assertEqual(travel,same_travel)
        self.assertEqual(Counter(travel[:12]),Counter(CARD_IDS))
        self.assertEqual(migrated.travel_deck['reshuffles'],1)

    def test_pre_event_save_migration_marks_past_events_and_applies_current_once(self):
        from dataclasses import asdict
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=609)
        state=asdict(game)
        state.pop('event_queue');state.pop('event_history')
        state.pop('legacy_skipped_events',None)
        state.pop('legacy_event_gap',None)
        state['day']=3
        state['meal_day']=2
        state['pressure']=0
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pre-events.json'
            path.write_text(json.dumps({'schema':1,'state':state}),encoding='utf-8')
            migrated=Cistern02.load(path)
        self.assertEqual(migrated.legacy_skipped_events,
                         ['ZC-EVE-0001','ZC-EVE-0002'])
        self.assertTrue(migrated.legacy_event_gap)
        self.assertEqual(migrated.event_history,['ZC-EVE-0003'])
        self.assertEqual(migrated.pending_sieges,['Barulho no vale'])
        self.assertEqual(migrated.event_queue,['ZC-EVE-0004','ZC-EVE-0005'])

    def test_malformed_horde_and_travel_shoes_are_rejected(self):
        from dataclasses import asdict
        game=Cistern02.new(STARTERS[:2],LINK_IDS[:2],seed=77)
        for field,malformed in (
                ('horde_deck',{'seed':77,'deck':[[]],'discard':[],'reshuffles':0}),
                ('travel_deck',{'seed':77,'deck':'ZC-VIA-0001','discard':[],'reshuffles':0})):
            with self.subTest(field=field),self.assertRaises(ValueError):
                Cistern02(**{**asdict(game),field:malformed})


if __name__=='__main__':unittest.main()
