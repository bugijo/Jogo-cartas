"""Ponte física do Posto e da van na campanha regional."""
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrated_campaign import IntegratedCampaign
from system import LOCATIONS, VEHICLES, World
from tactics import TACTICS, TacticalGame
from arc2 import Arc2
from verify_campaign_player02 import execute as execute_cistern


class PostoVehicleBridgeTests(unittest.TestCase):
    def migrated_seed22(self):
        player, _ = execute_cistern(22)
        game = player.game
        game.transition_to_last_transmission()
        return game

    @staticmethod
    def arrived(world, expedition_id, destination, map_id, special_items=None):
        team = list(world.heroes)
        world.open_expedition(expedition_id, team, destination,
                              special_items=special_items)
        for _ in range(world.expeditions[expedition_id].remaining):
            world.advance_expedition(expedition_id)
        return TacticalGame.start(world, expedition_id, map_id)

    def test_posto_is_playable_and_preserves_canonical_stock_and_van_spec(self):
        self.assertEqual(LOCATIONS['EXP-LOC-07']['name'], 'Posto')
        self.assertEqual(LOCATIONS['EXP-LOC-07']['searches'], 8)
        self.assertEqual(TACTICS['maps']['gas_station_02']['location'], 'EXP-LOC-07')
        self.assertNotIn('reference_only', TACTICS['maps']['gas_station_02'])
        van = VEHICLES['EXP-VEI-02']
        self.assertEqual((van['seats'], van['cargo_capacity'], van['fuel_per_segment']),
                         (6, 12, 2))

    def test_uncollected_cistern_battery_migrates_as_a_unique_workshop_find(self):
        game = self.migrated_seed22()
        self.assertEqual(game.world.unique_items_at_sites['EXP-LOC-03'], ['battery'])
        self.assertNotIn('battery', game.world.special_stock)
        self.assertFalse(game.battery_available)

    def test_battery_pickup_requires_workshop_objective_and_one_action(self):
        world = World.new(22, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.unique_items_at_sites['EXP-LOC-03'] = ['battery']
        tactical = self.arrived(world, 'workshop', 'EXP-LOC-03', 'workshop_02')
        with self.assertRaisesRegex(ValueError, 'objetivo'):
            tactical.pickup_unique_item('ZC-HER-0001', 'battery')
        world.begin_round()
        tactical.state['heroes']['ZC-HER-0001'] = 7  # cenário isolado da regra de coleta
        before = world.heroes['ZC-HER-0001']['actions']
        tactical.pickup_unique_item('ZC-HER-0001', 'battery')
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], before - 1)
        self.assertEqual(world.expeditions['workshop'].special_cargo, ['battery'])
        self.assertEqual(world.unique_items_at_sites['EXP-LOC-03'], [])
        with self.assertRaisesRegex(ValueError, 'indisponível'):
            tactical.pickup_unique_item('ZC-HER-0001', 'battery')

    def test_canonical_battery_can_be_recovered_and_delivered_by_legal_movement(self):
        world = World.new(22, ['ZC-HER-0001', 'ZC-HER-0002'], {'food': 2, 'water': 2})
        world.unique_items_at_sites['EXP-LOC-03'] = ['battery']
        world.give_item('ZC-HER-0001', 'crowbar', 'EXP-EQU-002', 'hand')
        tactical = self.arrived(world, 'battery-trip', 'EXP-LOC-03', 'workshop_02')
        tactical.move('ZC-HER-0001', 2)
        tactical.move('ZC-HER-0001', 3)
        world.begin_round()
        tactical.breach('ZC-HER-0001', 3, 7, 'crowbar')
        tactical.move('ZC-HER-0001', 7)
        world.begin_round()
        tactical.pickup_unique_item('ZC-HER-0001', 'battery')
        world.begin_round()
        tactical.move('ZC-HER-0001', 3)
        tactical.move('ZC-HER-0001', 2)
        world.begin_round()
        tactical.move('ZC-HER-0001', 1)
        tactical.finish()
        world.begin_return('battery-trip')
        for _ in range(2):
            world.advance_expedition('battery-trip')
        self.assertEqual(world.special_stock, ['battery'])
        self.assertEqual(world.unique_items_at_sites['EXP-LOC-03'], [])
        self.assertNotIn('battery-trip', world.expeditions)

    def test_eight_fuel_cards_are_individual_posto_actions_and_cannot_duplicate(self):
        world = World.new(12, ['ZC-HER-0001', 'ZC-HER-0002'], {'food': 2, 'water': 2})
        tactical = self.arrived(world, 'posto', 'EXP-LOC-07', 'gas_station_02')
        with self.assertRaisesRegex(ValueError, 'zona'):
            tactical.pickup_fuel_card('ZC-HER-0001', 1)
        tactical.state['heroes']['ZC-HER-0001'] = 7  # isolamento da ação de saque O1
        for lot in range(1, 9):
            if world.heroes['ZC-HER-0001']['actions'] == 0:
                world.begin_round()
            tactical.pickup_fuel_card('ZC-HER-0001', lot)
        self.assertEqual(world.expeditions['posto'].cargo['fuel'], 8)
        self.assertEqual(world.searches['EXP-LOC-07'], 0)
        self.assertEqual(len(tactical.state['fuel_cards_taken']), 8)
        with self.assertRaisesRegex(ValueError, 'indisponível'):
            tactical.pickup_fuel_card('ZC-HER-0001', 1)

    def test_van_repair_needs_inspection_battery_and_two_actions(self):
        world = World.new(0, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.special_stock.append('battery')
        tactical = self.arrived(world, 'posto', 'EXP-LOC-07', 'gas_station_02',
                                special_items=['battery'])
        world.begin_round()
        tactical.state['heroes']['ZC-HER-0001'] = 7  # cenário isolado de interação no O1
        with self.assertRaisesRegex(ValueError, 'inspeção'):
            tactical.repair_van('ZC-HER-0001')
        tactical.inspect_van('ZC-HER-0001')
        self.assertTrue(tactical.repair_van('ZC-HER-0001'))
        self.assertNotIn('battery', world.special_stock)
        self.assertEqual(world.vehicles['EXP-VEI-02']['location'], 'EXP-LOC-07')
        self.assertEqual(tactical.state['van_state'], 'operational')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'posto.json'
            world.save(path)
            restored = World.load(path)
        self.assertEqual(restored.encounters['posto']['van_state'], 'operational')
        self.assertEqual(restored.vehicles, world.vehicles)

    def test_returning_with_van_spends_fuel_from_expedition_cargo(self):
        world = World.new(4, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.open_expedition('posto-return', ['ZC-HER-0001'], 'EXP-LOC-07')
        for _ in range(2):
            world.advance_expedition('posto-return')
        exp = world.expeditions['posto-return']
        exp.cargo['fuel'] = 8
        world.vehicles['EXP-VEI-02'] = {'location': 'EXP-LOC-07', 'health': 3}
        world.site_states['EXP-LOC-07'] = {'van_state': 'operational'}
        world.begin_return('posto-return', vehicle_id='EXP-VEI-02')
        self.assertEqual(exp.cargo['fuel'], 4)
        self.assertEqual(world.stock['fuel'], 0)
        for _ in range(2):
            world.advance_expedition('posto-return')
        self.assertEqual(world.stock['fuel'], 4)
        self.assertEqual(world.vehicles['EXP-VEI-02']['location'], 'camp')

    def test_return_by_van_requires_a_persisted_successful_repair(self):
        world = World.new(4, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.open_expedition('unrepaired', ['ZC-HER-0001'], 'EXP-LOC-07')
        for _ in range(2):
            world.advance_expedition('unrepaired')
        world.expeditions['unrepaired'].cargo['fuel'] = 8
        world.vehicles['EXP-VEI-02'] = {'location': 'EXP-LOC-07', 'health': 3}
        with self.assertRaisesRegex(ValueError, 'Van operacional'):
            world.begin_return('unrepaired', vehicle_id='EXP-VEI-02')
        self.assertEqual(world.expeditions['unrepaired'].cargo['fuel'], 8)

    def test_legacy_recovery_api_cannot_bypass_canonical_van_repair(self):
        world = World.new(5, ['ZC-HER-0001'], {'food': 2, 'water': 2, 'fuel': 20})
        world.open_expedition('legacy-shortcut', ['ZC-HER-0001'], 'EXP-LOC-03')
        for _ in range(2):
            world.advance_expedition('legacy-shortcut')
        before = dict(world.stock)
        self.assertFalse(world.recover_vehicle('EXP-VEI-02', 'legacy-shortcut'))
        self.assertEqual(world.stock, before)

    def test_continuous_military_gate_rejects_noncanonical_vehicle(self):
        game = self.migrated_seed22()
        game.world.flags.update(radio_code=True, access_card=True)
        game.world.vehicles['EXP-VEI-01'] = {'location': 'camp', 'health': 3}
        with self.assertRaisesRegex(ValueError, 'van canônica'):
            game.authorize_installation('military-shortcut', list(game.world.heroes),
                                        'EXP-VEI-01')
        self.assertNotIn('military_access', game.world.flags)

    def test_authorized_military_expedition_with_card_survives_save_load(self):
        world = World.new(5, ['ZC-HER-0001', 'ZC-HER-0002'],
                          {'food': 2, 'water': 2, 'fuel': 12})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-fixture'}},
        }
        world.flags.update(radio_code=True, access_card=True)
        world.special_stock.append('access_card')
        world.vehicles['EXP-VEI-02'] = {'location': 'camp', 'health': 3}
        Arc2(world).authorize_installation('military', list(world.heroes), 'EXP-VEI-02')
        self.assertEqual(world.expeditions['military'].special_cargo, ['access_card'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'military.json'
            world.save(path)
            restored = World.load(path)
        self.assertEqual(restored.expeditions['military'].special_cargo, ['access_card'])
        self.assertEqual(restored.flags['military_access'], True)

    def test_access_card_is_unique_cargo_and_must_return_before_authorization(self):
        hero = 'ZC-HER-0001'
        world = World.new(7, [hero], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'campaign-migration'}},
        }
        world.flags['radio_code'] = True
        world.open_expedition('station', [hero], 'EXP-LOC-05')
        for _ in range(3):
            world.advance_expedition('station')
        tactical = TacticalGame.start(world, 'station', 'station_02')
        tactical.state['heroes'][hero] = 5  # fixture de presença no setor de busca
        tactical.search(hero)
        Arc2(world).recover_access_card('station')
        self.assertEqual(world.expeditions['station'].special_cargo, ['access_card'])
        self.assertNotIn('access_card', world.special_stock)
        with self.assertRaisesRegex(ValueError, 'transportado ao abrigo'):
            Arc2(world).authorize_installation('military', [hero], 'EXP-VEI-02')
        tactical.state['heroes'][hero] = 1
        tactical.finish()
        world.begin_return('station')
        for _ in range(3):
            world.advance_expedition('station')
        self.assertEqual(world.special_stock, ['access_card'])

    def test_celia_physical_contact_is_persisted_and_far_clock_blocks_return(self):
        hero = 'ZC-HER-0001'
        world = World.new(22, [hero], {'food': 4, 'water': 4})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-fixture'}},
        }
        world.open_expedition('station-contact', [hero], 'EXP-LOC-05')
        for _ in range(world.expeditions['station-contact'].remaining):
            world.advance_expedition('station-contact')
        tactical = TacticalGame.start(world, 'station-contact', 'station_02')
        with self.assertRaisesRegex(ValueError, 'zona de contato'):
            tactical.contact_npc(hero, 'EXP-NPC-02')
        tactical.state['enemies'].clear()  # fixture isola presença e PA de combate
        tactical.state['heroes'][hero]=14
        tactical.investigate_contact(hero, 'EXP-NPC-02')
        with self.assertRaisesRegex(ValueError, 'contato físico'):
            world.recruit('EXP-NPC-02')
        before = world.heroes[hero]['actions']
        receipt = tactical.contact_npc(hero, 'EXP-NPC-02')
        self.assertEqual(receipt['zone'], 14)
        self.assertEqual(world.heroes[hero]['actions'], before - 1)
        self.assertEqual(world.npcs['EXP-NPC-02']['location'], 'station-contact')
        self.assertIn('EXP-NPC-02', world.expeditions['station-contact'].crew)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'celia-contact.json'
            world.save(path)
            world = World.load(path)
            tactical = TacticalGame(world, 'station-contact')
        self.assertEqual(tactical.state['npc_followers'], {'EXP-NPC-02': hero})
        with self.assertRaises(ValueError):
            tactical.finish()
        with self.assertRaises(ValueError):
            world.end_day()
        for _ in range(3):
            tactical.activate()
        result=tactical.activate()
        self.assertTrue(result['round_closed'])
        self.assertFalse(result['return_reserve'])
        self.assertNotEqual(tactical.state['heroes'][hero], tactical.exit_zone)
        with self.assertRaisesRegex(ValueError, 'Equipe fora da saída'):
            tactical.finish()
        world.validate()

    def test_regional_emergency_returns_heroes_and_strands_rescue_without_loot(self):
        heroes=['ZC-HER-0001','ZC-HER-0003']
        world=World.new(22,heroes,{'food':4,'water':4})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-emergency-fixture'}},
        }
        world.special_stock.append('battery')
        world.open_expedition('station-emergency',heroes,'EXP-LOC-05',
                              special_items=['battery'])
        for _ in range(world.expeditions['station-emergency'].remaining):
            world.advance_expedition('station-emergency')
        tactical=TacticalGame.start(world,'station-emergency','station_02')
        tactical.state['enemies'].clear()  # fixture para isolar liquidação de emergência
        tactical.state['heroes'][heroes[0]]=14
        tactical.investigate_contact(heroes[0],'EXP-NPC-02')
        tactical.contact_npc(heroes[0],'EXP-NPC-02')
        expedition=world.expeditions['station-emergency']
        expedition.cargo['food']=2
        world._set_hero_health(heroes[1],0)  # incapacitado também retorna
        receipt=tactical.emergency_return('sem tempo para retorno seguro')
        self.assertEqual(receipt['status'],'failed')
        self.assertEqual(receipt['lost_cargo'],{'food':2})
        self.assertEqual(world.stock['food'],4)
        self.assertEqual(world.special_stock,['battery'])
        self.assertEqual(world.heroes[heroes[0]]['health'],2)
        self.assertEqual(world.heroes[heroes[0]]['fatigue'],3)
        self.assertEqual(world.heroes[heroes[1]]['health'],0)
        self.assertEqual(world.heroes[heroes[1]]['fatigue'],3)
        self.assertEqual(world.heroes[heroes[0]]['location'],'camp')
        self.assertEqual(world.npcs['EXP-NPC-02']['location'],'EXP-LOC-05')
        self.assertNotIn('station-emergency',world.expeditions)
        self.assertNotIn('station-emergency',world.encounters)
        self.assertEqual(world.residents,2)
        self.assertEqual(world.site_states['EXP-LOC-05']['stranded_npcs'],['EXP-NPC-02'])
        world.validate()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'emergency.json'
            world.save(path)
            restored=World.load(path)
        self.assertEqual(asdict(restored),asdict(world))

    def test_emergency_military_trip_keeps_carried_card_but_damages_van(self):
        hero='ZC-HER-0001'
        world=World.new(22,[hero],{'food':2,'water':2,'fuel':12})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-military-emergency-fixture'}},
        }
        world.flags.update(radio_code=True,access_card=True)
        world.special_stock.append('access_card')
        world.vehicles['EXP-VEI-02']={'location':'camp','health':3}
        Arc2(world).authorize_installation('military-emergency',[hero],'EXP-VEI-02')
        self.assertEqual(world.stock['fuel'],0)  # ida/volta reservadas desde o estoque
        for _ in range(3):
            world.advance_expedition('military-emergency')
        tactical=TacticalGame.start(world,'military-emergency','military_installation')
        world.expeditions['military-emergency'].cargo['fuel']=4
        receipt=tactical.emergency_return('abandonar missão militar')
        self.assertEqual(receipt['lost_cargo'],{'fuel':4})
        self.assertEqual(world.special_stock,['access_card'])
        self.assertTrue(world.flags['access_card'])
        self.assertFalse(world.flags['military_access'])
        self.assertEqual(world.vehicles['EXP-VEI-02'],
                         {'location':'EXP-LOC-06','health':0})
        world.validate()

    def test_emergency_dropped_access_card_cannot_be_created_again(self):
        hero='ZC-HER-0001'
        world=World.new(12,[hero],{'food':4,'water':4})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-card-drop-fixture'}},
        }
        world.flags['radio_code']=True
        world.open_expedition('station-card-drop',[hero],'EXP-LOC-05')
        for _ in range(3):
            world.advance_expedition('station-card-drop')
        tactical=TacticalGame.start(world,'station-card-drop','station_02')
        tactical.state['heroes'][hero]=5
        tactical.search(hero)
        Arc2(world).recover_access_card('station-card-drop')
        tactical.emergency_return('teste de perda de cartão')
        self.assertFalse(world.flags['access_card'])
        self.assertEqual(world.unique_items_at_sites['EXP-LOC-05'],['access_card'])
        world.end_day()
        world.open_expedition('station-card-revisit',[hero],'EXP-LOC-05')
        for _ in range(3):
            world.advance_expedition('station-card-revisit')
        revisit=TacticalGame.start(world,'station-card-revisit','station_02')
        revisit.state['heroes'][hero]=5
        revisit.search(hero)
        before=list(world.expeditions['station-card-revisit'].special_cargo)
        with self.assertRaisesRegex(ValueError,'no chão'):
            Arc2(world).recover_access_card('station-card-revisit')
        self.assertEqual(world.expeditions['station-card-revisit'].special_cargo,before)
        self.assertEqual(world.unique_items_at_sites['EXP-LOC-05'],['access_card'])

    def test_celia_contact_does_not_override_real_food_shortage(self):
        game = self.migrated_seed22()
        world = game.world
        hero = 'ZC-HER-0001'
        world.open_expedition('station-no-food', [hero], 'EXP-LOC-05')
        for _ in range(world.expeditions['station-no-food'].remaining):
            world.advance_expedition('station-no-food')
        tactical = TacticalGame.start(world, 'station-no-food', 'station_02')
        tactical.state['heroes'][hero] = 14  # teste isolado do bloqueio de sustento
        tactical.state['enemies'].clear()
        tactical.investigate_contact(hero, 'EXP-NPC-02')
        self.assertLess(world.stock['food'], world.residents + 1)
        actions_after_investigation = world.heroes[hero]['actions']
        with self.assertRaisesRegex(ValueError, 'sustento'):
            tactical.contact_npc(hero, 'EXP-NPC-02')
        self.assertNotIn('EXP-NPC-02', world.npcs)
        self.assertEqual(world.heroes[hero]['actions'], actions_after_investigation)

    def test_celia_contact_is_unavailable_when_founder_is_already_active(self):
        world = World.new(3, ['ZC-HER-0012'], {'food': 4, 'water': 4})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-fixture'}},
        }
        world.open_expedition('duplicate', ['ZC-HER-0012'], 'EXP-LOC-05')
        for _ in range(3):
            world.advance_expedition('duplicate')
        tactical = TacticalGame.start(world, 'duplicate', 'station_02')
        tactical.state['heroes']['ZC-HER-0012'] = 14
        with self.assertRaisesRegex(ValueError, 'Identidade já presente'):
            tactical.investigate_contact('ZC-HER-0012', 'EXP-NPC-02')

    def test_continuous_regional_clock_charges_travel_rounds_and_return(self):
        hero = 'ZC-HER-0001'
        world = World.new(3, [hero], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-clock-fixture'}},
        }
        world.open_expedition('regional-clock', [hero], 'EXP-LOC-02')
        self.assertEqual(world.regional_clock, 0)
        world.advance_expedition('regional-clock')
        self.assertEqual(world.regional_clock, 1)
        tactical = TacticalGame.start(world, 'regional-clock', 'market_intro')
        self.assertEqual(world.regional_clock, 2)
        with self.assertRaisesRegex(ValueError, 'TacticalGame.activate'):
            world.begin_round()
        tactical.activate()
        self.assertEqual(world.regional_clock, 3)
        tactical.finish()
        world.begin_return('regional-clock')
        world.advance_expedition('regional-clock')
        self.assertEqual(world.regional_clock, 4)
        world.end_day()
        self.assertEqual(world.regional_clock, 0)
        self.assertEqual(world.day, 1)

    def test_continuous_regional_clock_refuses_an_eleventh_segment(self):
        hero = 'ZC-HER-0001'
        world = World.new(3, [hero], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-clock-fixture'}},
        }
        world.open_expedition('clock-limit', [hero], 'EXP-LOC-02')
        world.regional_clock = 10
        remaining = world.expeditions['clock-limit'].remaining
        with self.assertRaisesRegex(ValueError, 'dez segmentos'):
            world.advance_expedition('clock-limit')
        self.assertEqual(world.expeditions['clock-limit'].remaining, remaining)

    def test_open_expedition_preflights_one_local_round_and_return_reserve(self):
        hero = 'ZC-HER-0001'
        world = World.new(3, [hero], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'migration-clock-fixture'}},
        }
        world.regional_clock = 8
        with self.assertRaisesRegex(ValueError, 'reserva para ida'):
            world.open_expedition('too-late', [hero], 'EXP-LOC-02')
        self.assertEqual(world.regional_clock, 8)
        self.assertEqual(world.heroes[hero]['location'], 'camp')
        self.assertNotIn('too-late', world.expeditions)

        world.regional_clock = 7
        world.open_expedition('last-safe-trip', [hero], 'EXP-LOC-02')
        world.advance_expedition('last-safe-trip')
        tactical = TacticalGame.start(world, 'last-safe-trip', 'market_intro')
        self.assertEqual(world.regional_clock, 9)
        tactical.finish()
        world.begin_return('last-safe-trip')
        self.assertEqual(world.advance_expedition('last-safe-trip'), 'returned')
        self.assertEqual(world.regional_clock, 10)

    def test_driver_reduction_is_applied_before_shared_clock_preflight(self):
        hero='ZC-HER-0001'
        driver='EXP-NPC-06'
        world=World.new(3,[hero],{'food':2,'water':2,'fuel':4})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-driver-clock-fixture'}},
        }
        world.regional_clock=7
        world.npcs[driver]={'level':1,'job':'driving','health':3,'location':'camp'}
        world.vehicles['EXP-VEI-02']={'location':'camp','health':3}
        world.open_expedition('driver-clock', [hero], 'EXP-LOC-03',
                              vehicle_id='EXP-VEI-02',npc_ids=[driver])
        self.assertEqual(world.expeditions['driver-clock'].segment_cost,1)
        self.assertEqual(world.stock['fuel'],0)
        self.assertEqual(world.vehicles['EXP-VEI-02']['location'],'driver-clock')

    def test_continuous_campaign_limits_one_expedition_per_day(self):
        hero='ZC-HER-0001'
        world=World.new(3,[hero],{'food':4,'water':4})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-one-expedition-fixture'}},
        }
        world.open_expedition('first',[hero],'EXP-LOC-02')
        world.advance_expedition('first')
        TacticalGame.start(world,'first','market_intro').finish()
        world.begin_return('first')
        world.advance_expedition('first')
        with self.assertRaisesRegex(ValueError,'uma expedição por dia'):
            world.open_expedition('second',[hero],'EXP-LOC-02')
        world.end_day()
        world.open_expedition('second',[hero],'EXP-LOC-02')

    def test_exit_does_not_require_clearing_enemies_outside_the_exit_zone(self):
        hero='ZC-HER-0001'
        world=World.new(18,[hero],{'food':2,'water':2})
        world.open_expedition('exit-rule',[hero],'EXP-LOC-02')
        world.advance_expedition('exit-rule')
        tactical=TacticalGame.start(world,'exit-rule','market_intro')
        tactical.spawn('slow',zone=16)
        tactical.finish()
        self.assertNotIn('exit-rule',world.encounters)
        self.assertEqual(world.site_states['EXP-LOC-02']['enemies']['E001']['zone'],16)

    def test_continuous_destination_spawns_initial_group_once_and_station_brute(self):
        heroes=['ZC-HER-0001','ZC-HER-0002']
        world=World.new(12,heroes,{'food':5,'water':5})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-spawn-fixture'}},
        }
        for visit in ('station-first','station-repeat'):
            if visit=='station-repeat':
                world.end_day()
            world.open_expedition(visit,heroes,'EXP-LOC-05')
            for _ in range(world.expeditions[visit].remaining):
                world.advance_expedition(visit)
            tactical=TacticalGame.start(world,visit,'station_02')
            enemies=list(tactical.state['enemies'].values())
            if visit=='station-first':
                self.assertEqual(sum(enemy['kind']=='slow' for enemy in enemies),1)
                self.assertEqual(sum(enemy['kind']=='brute' for enemy in enemies),1)
                self.assertEqual(tactical.state['pressure'],0)
            else:
                self.assertEqual(len(enemies),2)
            tactical.finish(retreat=True)
            world.begin_return(visit)
            for _ in range(world.expeditions[visit].remaining):
                world.advance_expedition(visit)

    def test_regional_pressure_draws_persistent_horde_after_second_round(self):
        hero='ZC-HER-0001'
        world=World.new(123,[hero],{'food':2,'water':2})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-horde-fixture'}},
        }
        world.open_expedition('regional-horde',[hero],'EXP-LOC-02')
        world.advance_expedition('regional-horde')
        tactical=TacticalGame.start(world,'regional-horde','market_intro')
        first=tactical.activate()
        self.assertEqual(first['spawned'],[])
        self.assertEqual(tactical.state['pressure'],1)
        before=world.regional_horde_deck
        second=tactical.activate()
        self.assertGreaterEqual(len(second['spawned']),1)
        self.assertEqual(tactical.state['pressure'],0)
        self.assertNotEqual(world.regional_horde_deck,before)
        self.assertTrue(all(tactical.state['enemies'][enemy]['zone']==16
                            for enemy in second['spawned']))

    def test_regional_horde_and_clock_are_deterministic_across_save_load(self):
        hero='ZC-HER-0001'
        world=World.new(123,[hero],{'food':2,'water':2})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-horde-save-fixture'}},
        }
        world.open_expedition('regional-horde-save',[hero],'EXP-LOC-02')
        world.advance_expedition('regional-horde-save')
        tactical=TacticalGame.start(world,'regional-horde-save','market_intro')
        tactical.activate()
        tactical.activate()  # gatilho de pressão 2 e carta Horda
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'regional-horde-save.json'
            world.save(path)
            first=World.load(path)
            second=World.load(path)
        self.assertEqual(first.regional_clock,world.regional_clock)
        self.assertEqual(first.regional_horde_deck,world.regional_horde_deck)
        self.assertEqual(first.encounters,world.encounters)
        first_result=TacticalGame(first,'regional-horde-save').activate()
        second_result=TacticalGame(second,'regional-horde-save').activate()
        self.assertEqual(first_result,second_result)
        self.assertEqual(first.regional_horde_deck,second.regional_horde_deck)
        self.assertEqual(first.encounters,second.encounters)

    def test_night_segments_add_fatigue_and_a_night_round_draws_horde(self):
        hero='ZC-HER-0001'
        world=World.new(44,[hero],{'food':2,'water':2})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-night-fixture'}},
        }
        world.open_expedition('regional-night',[hero],'EXP-LOC-02')
        world.regional_clock=8  # fixture de limite noturno
        world.advance_expedition('regional-night')
        self.assertEqual(world.regional_clock,9)
        self.assertEqual(world.heroes[hero]['fatigue'],1)
        world.regional_clock=0
        world.expeditions['regional-night'].remaining=0
        world.expeditions['regional-night'].distance='near'
        tactical=TacticalGame.start(world,'regional-night','market_intro')
        tactical.state['first_market_visit']=False
        world.regional_clock=8
        tactical.state['round_clock']=9
        result=tactical.activate()
        self.assertGreaterEqual(len(result['spawned']),1)
        self.assertTrue(all(tactical.state['enemies'][enemy]['zone']==16
                            for enemy in result['spawned']))

    def test_fatigue_reduces_actions_and_a_fed_night_recovers_one(self):
        heroes=['ZC-HER-0001','ZC-HER-0003']
        world=World.new(45,heroes,{'food':4,'water':4})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-fatigue-fixture'}},
        }
        world.heroes[heroes[0]]['fatigue']=2
        world.open_expedition('fatigue-round',heroes,'EXP-LOC-02')
        world.advance_expedition('fatigue-round')
        tactical=TacticalGame.start(world,'fatigue-round','market_intro')
        self.assertEqual(world.heroes[heroes[0]]['actions'],2)
        self.assertEqual(world.heroes[heroes[1]]['actions'],3)
        tactical.finish()
        world.begin_return('fatigue-round')
        world.advance_expedition('fatigue-round')
        result=world.end_day()
        self.assertEqual(result['missing'],{'food':0,'water':0})
        self.assertEqual(world.heroes[heroes[0]]['fatigue'],1)

    def test_fatigue_three_prevents_departure_until_a_fed_night_recovers(self):
        hero='ZC-HER-0001'
        world=World.new(45,[hero],{'food':2,'water':2})
        world.cistern_record={
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'migration-fatigue-lock-fixture'}},
        }
        world.heroes[hero]['fatigue']=3
        with self.assertRaisesRegex(ValueError,'Fadiga 3'):
            world.open_expedition('fatigue-lock',[hero],'EXP-LOC-02')
        world.end_day()
        self.assertEqual(world.heroes[hero]['fatigue'],2)
        world.open_expedition('fatigue-lock',[hero],'EXP-LOC-02')


if __name__ == '__main__':
    unittest.main()
