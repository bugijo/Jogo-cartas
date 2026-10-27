"""Testes da expedição tática 0.2 sem dependências externas."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cistern02 import Cistern02, LINK_IDS, STARTERS
from cistern_tactics02 import Tactical02, MAPS


def chapter():
    return Cistern02.new(list(STARTERS[:2]), list(LINK_IDS[:2]))


class Tactical02Tests(unittest.TestCase):
    def test_rescue_aid_cannot_spend_the_abrigo_stock_at_the_destination(self):
        c=chapter();h=STARTERS[0]
        t=Tactical02.start(c,'Mercado',[h])
        t.positions[h]=7
        before=(t.ap[h],list(c.food),list(c.water))
        with self.assertRaisesRegex(ValueError,'carga levada'):
            t.rescue(h,'ZC-MOR-0001','aid')
        self.assertEqual((t.ap[h],c.food,c.water),before)

    def test_rescue_rejects_group_already_resolved_in_prior_visit(self):
        c=chapter();h=STARTERS[0]
        t=Tactical02.start(c,'Mercado',[h],taken_before=['ZC-MOR-0001'])
        t.positions[h]=7
        with self.assertRaisesRegex(ValueError,'já resolvido'):
            t.rescue(h,'ZC-MOR-0001','welcome')

    def test_twenty_fifth_map_enemy_marks_loss_and_still_offers_emergency(self):
        c = chapter(); h = STARTERS[0]
        t = Tactical02.start(c, 'Mercado', [h])
        while len(t.enemies) < 24:
            t._spawn('Errante', 1)
        t._spawn('Errante', 1)
        self.assertTrue(t.failed)
        self.assertEqual(len(t.enemies), 24)
        t.emergency()
        self.assertEqual(t.log[-1]['event'], 'emergency')
        self.assertEqual(t.fatigue[h], 3)
        with self.assertRaisesRegex(ValueError, 'encerrada|perdida'):
            t.emergency()

    def test_each_night_segment_spent_on_long_route_adds_fatigue_once(self):
        c = chapter(); h = STARTERS[0]; c.clock = 7
        t = Tactical02.start(c, 'Mercado', [h], route='long')
        # Travel spends segments 8–9; the opening map round spends segment 10.
        self.assertEqual(c.clock, 10)
        self.assertEqual(t.fatigue[h], 2)
        self.assertEqual(c.people[0]['fatigue'], 2)

    def test_legacy_tactical_save_gets_deterministic_horde_shoe(self):
        c = chapter(); t = Tactical02.start(c, 'Mercado', [STARTERS[0]])
        snapshot = t.snapshot()
        snapshot.pop('horde_deck')
        resumed = Tactical02.from_snapshot(c, snapshot)
        self.assertEqual(resumed.horde_deck['seed'], c.seed + 8102)
        self.assertEqual(len(resumed.horde_deck['deck']), 9)

    def test_search_uses_card_from_regional_deck_and_preserves_ground(self):
        c = chapter(); h = STARTERS[0]
        t = Tactical02.start(c, 'Mercado', [h], route='long')
        t.positions[h] = 5  # Unidade de regra B1; movimento é testado à parte.
        found = t.search(h)
        self.assertTrue(found['id'].startswith('ZC-SAQ-'))
        self.assertEqual(t.search_uses['5'], 2)
        self.assertEqual(len(t.search_deck), 5)
        with self.assertRaises(ValueError):
            t.search(h)  # Cada ponto, no máximo uma busca por rodada.

    def test_prior_site_snapshot_from_before_search_feature_loads(self):
        c = chapter(); h = STARTERS[0]
        old = {'doors_open': [[1,5]], 'enemies': [], 'next_enemy': 2}
        t = Tactical02.start(c, 'Mercado', [h], prior_state=old,
                             first_visit=False)
        self.assertEqual(len(t.search_deck), 6)
        self.assertEqual(t.search_uses, {'5':3, '12':3})
    def test_posto_van_consumes_carried_fuel_and_battery(self):
        c = chapter(); h = STARTERS[0]
        t = Tactical02.start(c, 'Posto', [h], equipment={h: ['Pé de cabra', 'Bateria']})
        t.positions[h] = 7  # Isola custos e estoque; navegação tem teste próprio.
        t.inspect_van(h)
        t.pickup_supply(h, 'Combustível', 1)
        t.pickup_supply(h, 'Combustível', 2)
        t.end_round(); t.begin_round()
        self.assertTrue(t.repair_van(h, 6))
        self.assertNotIn('Bateria', t.equipment[h])
        t.positions[h] = 1
        t.end_round(); t.finish(by_van=True)
        self.assertEqual(len([x for x in t.log if x['event']=='fuel_spent']), 2)
        self.assertEqual([x['event'] for x in t.delivery_proof()], ['deliver_van'])

    def test_emergency_fatigue_belongs_to_person_and_blocks_next_dawn(self):
        c = chapter(); h = STARTERS[0]
        t = Tactical02.start(c, 'Mercado', [h])
        t.emergency()
        person = next(p for p in c.people if p['id'] == h)
        self.assertEqual(person['fatigue'], 3)
        with self.assertRaises(ValueError):
            Tactical02.start(c, 'Mercado', [h], first_visit=False)
        c.meal(); c.next_day()
        self.assertEqual(person['fatigue'], 2)
        Tactical02.start(c, 'Mercado', [h], first_visit=False)

    def test_invalid_equipment_does_not_spend_travel_time(self):
        c = chapter(); h = STARTERS[0]
        with self.assertRaises(ValueError):
            Tactical02.start(c, 'Mercado', [h], equipment={h: ['Faca'] * 5})
        self.assertEqual(c.clock, 0)

    def test_equipment_loadout_cannot_carry_three_weapons(self):
        c = chapter(); hero = STARTERS[0]
        with self.assertRaisesRegex(ValueError, 'duas armas'):
            Tactical02.start(c, 'Mercado', [hero], equipment={hero: [
                'Pé de cabra', 'Faca', 'Machado']})
        self.assertEqual(c.clock, 0)

    def test_six_maps_clock_and_geometry(self):
        for name, m in MAPS.items():
            with self.subTest(name=name):
                c = chapter(); t = Tactical02.start(c, name, list(STARTERS[:2]))
                self.assertEqual((len(m['zones']), len(m['edges']), len(m['doors'])), (16,21,5))
                self.assertEqual((c.clock,t.round_no), (2,1))
                self.assertTrue(all(z == m['entry'] for z in t.positions.values()))
                self.assertEqual(len(t.enemies), 2 if name == 'estação' else 1)

    def test_movement_door_and_ap(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h])
        with self.assertRaises(ValueError): t.move(h,5)
        t.open_door(h,5); t.move(h,5)
        self.assertEqual((t.positions[h],t.ap[h]), (5,1))
        with self.assertRaises(ValueError): t.move(h,7)
        with self.assertRaises(ValueError): t.open_door(h,1)

    def test_blocked_door(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h])
        t.positions[h] = 7
        with self.assertRaises(ValueError): t.open_door(h,8)
        t.open_door(h,8,'Pé de cabra')
        self.assertEqual(t.ap[h],1)
        self.assertIn([7,8],t.doors_open)

    def test_combat_natural_rolls_and_ammo(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h])
        t.enemies.clear(); t._spawn('Bruto',1); target=t.enemies[0]['id']
        self.assertFalse(t.attack(h,target,'Pé de cabra',1))
        self.assertTrue(t.attack(h,target,'Pé de cabra',6))
        self.assertEqual(t.enemies[0]['hp'],2)
        with self.assertRaises(ValueError): t.attack(h,target,'Pistola',6)
        t.equipment[h].append('Pistola')
        self.assertTrue(t.attack(h,target,'Pistola',6))
        self.assertEqual(c.ammo,1)

    def test_complete_round_horde_and_exit(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h])
        self.assertFalse(t.can_exit()); t.end_round(); self.assertTrue(t.can_exit())
        with self.assertRaises(ValueError): t.move(h,2)
        t.begin_round(); t.end_round()
        self.assertTrue(any(x['event']=='horde' for x in t.log))
        t.finish(); self.assertEqual(c.clock,4)

    def test_first_market_round_protects_only_first_visit(self):
        c = chapter(); h = STARTERS[0]
        first=Tactical02.start(c,'Mercado',[h])
        first.enemies[0]['zone']=1
        first.end_round()
        self.assertEqual(next(p for p in c.people if p['id']==h)['wounds'],0)
        self.assertEqual(first.local_pressure,1)
        c2=chapter(); later=Tactical02.start(c2,'Mercado',[h],first_visit=False)
        later.enemies[0]['zone']=1
        later.end_round()
        self.assertEqual(next(p for p in c2.people if p['id']==h)['wounds'],1)

    def test_snapshot_and_emergency(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h])
        restored=Tactical02.from_snapshot(c,json.loads(json.dumps(t.snapshot())))
        self.assertEqual(restored.snapshot(),t.snapshot())
        restored.emergency()
        self.assertEqual(restored.fatigue[h],3)
        self.assertEqual(next(p for p in c.people if p['id']==h)['wounds'],1)

    def test_long_route(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Oficina',[h],'long')
        self.assertEqual((c.clock,len(t.enemies)),(3,0))
        t.end_round(); t.finish(); self.assertEqual(c.clock,5)

    def test_part_requires_objective_action_and_safe_return(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Oficina',[h],'long')
        with self.assertRaises(ValueError): t.pickup_part(h,'Conexões')
        t.move(h,2); t.move(h,3)
        t.end_round(); t.begin_round(); t.open_door(h,7,'Pé de cabra'); t.move(h,7)
        t.end_round(); t.begin_round()
        self.assertTrue(t.pickup_part(h,'Conexões'))
        self.assertEqual(t.delivery_proof(),[])
        t.end_round(); t.begin_round(); t.move(h,3); t.move(h,2); t.move(h,1)
        t.end_round(); t.finish()
        proof=t.delivery_proof()
        self.assertEqual([(p['part'],p['zone']) for p in proof],[('Conexões',7)])
        self.assertEqual(c.parts,{})  # integrador aceita certificado uma vez

    def test_unique_part_dropped_by_emergency_is_recovered_once_at_same_zone(self):
        c=chapter(); h=STARTERS[0]
        first=Tactical02.start(c,'Oficina',[h])
        first.positions[h]=7
        self.assertTrue(first.pickup_part(h,'Conexões'))
        first.emergency()
        site=first.site_snapshot()
        self.assertEqual(site['part_ground'],[
            {'part':'Conexões','destination':'oficina','zone':7,'load':1}])
        self.assertIn('Oficina:Conexões',first.taken_before)
        recovered_by=STARTERS[1]
        second=Tactical02.start(c,'Oficina',[recovered_by],first_visit=False,
            taken_before=['Oficina:Conexões'],prior_state=site)
        second.positions[recovered_by]=7
        before=second.ap[recovered_by]
        self.assertTrue(second.pickup_part(recovered_by,'Conexões'))
        self.assertEqual(second.ap[recovered_by],before-1)
        self.assertEqual(second.part_ground,[])
        with self.assertRaises(ValueError): second.pickup_part(recovered_by,'Conexões')
        saved=Tactical02.from_snapshot(c,second.snapshot())
        self.assertEqual(saved.snapshot(),second.snapshot())
        malformed=first.site_snapshot()
        malformed['part_ground']=[{'part':'Conexões','destination':'oficina',
                                   'zone':3,'load':1}]
        with self.assertRaises(ValueError):
            Tactical02.start(c,'Oficina',[STARTERS[1]],first_visit=False,
                prior_state=malformed)

    def test_pump_failure_costs_ap_and_pressure(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Estação',[h])
        t.positions[h]=7
        self.assertFalse(t.pickup_part(h,'Bomba',1))
        self.assertEqual((t.ap[h],c.pressure),(1,1))
        with self.assertRaises(ValueError): t.pickup_part(h,'Bomba',6)

    def test_enemy_breaks_door_before_crossing(self):
        c = chapter(); h = STARTERS[0]; t = Tactical02.start(c,'Mercado',[h],first_visit=False)
        t.enemies.clear(); t._spawn('Errante',5)
        t.end_round()
        self.assertEqual(t.enemies[0]['zone'],5)
        self.assertIn([1,5],t.doors_open)
        t.begin_round(); t.end_round()
        self.assertEqual(t.enemies[0]['zone'],1)
        self.assertEqual(next(p for p in c.people if p['id']==h)['wounds'],0)

    def test_two_shots_spawn_one_errant_not_next_round(self):
        c = chapter(); h=STARTERS[0]; t=Tactical02.start(c,'Mercado',[h],
            equipment={h:['Pé de cabra','Pistola']},first_visit=False)
        t.enemies.clear(); t._spawn('Bruto',1)
        enemy=t.enemies[0]['id']
        t.attack(h,enemy,'Pistola',1); t.attack(h,enemy,'Pistola',1)
        t.end_round()
        self.assertEqual(len(t.enemies),2)
        self.assertEqual(t.enemies[-1]['zone'],16)
        self.assertEqual(c.ammo,0)

    def test_tactical_damage_never_exceeds_three_wounds(self):
        for initial in (2, 3):
            with self.subTest(initial=initial):
                c = chapter(); h = STARTERS[0]
                t = Tactical02.start(c, 'Hospital', [h], first_visit=False)
                person = next(p for p in c.people if p['id'] == h)
                person['wounds'] = initial
                t.enemies.clear(); t._spawn('Bruto', t.positions[h])
                t.end_round()
                self.assertEqual(person['wounds'], 3)


if __name__ == '__main__': unittest.main()
