"""Ponte física do Posto e da van na campanha regional."""
import sys
import tempfile
import unittest
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
        tactical.breach('ZC-HER-0001', 3, 7, 'crowbar')
        world.begin_round()
        tactical.breach('ZC-HER-0001', 3, 7, 'crowbar')
        tactical.move('ZC-HER-0001', 7)
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


if __name__ == '__main__':
    unittest.main()
