"""O controlador regional usa ações públicas e navega sem mutar estado por atalhos."""
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from regional_player import AdaptiveRegionalPlayer
from system import World
from tactics import TacticalGame
from verify_campaign_player02 import execute as execute_cistern


class RegionalPlayerTests(unittest.TestCase):
    def setup_market(self):
        world = World.new(41, ['ZC-HER-0001'], {'food': 2, 'water': 2})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'test-only-migration'}},
        }
        world.give_item('ZC-HER-0001', 'crowbar', 'EXP-EQU-002', 'hand')
        world.open_expedition('regional-agent-test', ['ZC-HER-0001'], 'EXP-LOC-02')
        self.assertEqual(world.advance_expedition('regional-agent-test'), 'arrived')
        tactical = TacticalGame.start(world, 'regional-agent-test', 'market_intro')
        return world, tactical

    def test_objective_completion_is_not_reported_as_exit_while_enemy_blocks_exit(self):
        world, tactical = self.setup_market()
        world.gear['ZC-HER-0001'].clear()
        tactical.spawn('brute', zone=tactical.exit_zone)
        player = AdaptiveRegionalPlayer('explorer')

        result = player.run_objectives(
            tactical, [{'kind': 'zone', 'zone': tactical.exit_zone}], max_steps=1)

        self.assertEqual(result['status'], 'step_limit')
        self.assertIn(tactical.id, world.encounters)

    def test_adaptive_player_executes_search_and_returns_using_public_actions(self):
        world, tactical = self.setup_market()
        player = AdaptiveRegionalPlayer('explorer')
        result = player.run_objective(tactical, {'kind': 'search', 'zone': 5}, max_steps=20)

        self.assertEqual(result['status'], 'objective_completed_and_exited')
        self.assertEqual(result['searches'], 1)
        self.assertNotIn('regional-agent-test', world.encounters)
        self.assertTrue(any(row.get('action') == 'search' for row in world.log))
        self.assertTrue(any(row.get('encounter') == 'regional-agent-test'
                            for row in world.log))
        self.assertEqual(world.heroes['ZC-HER-0001']['location'], 'regional-agent-test')
        # The controller stops at the tactical exit; the public campaign API
        # still owns the return trip and its segment cost.
        world.begin_return('regional-agent-test')
        self.assertEqual(world.advance_expedition('regional-agent-test'), 'returned')

    def test_expedition_controller_owns_public_outbound_tactical_and_return_cycle(self):
        world = World.new(41, ['ZC-HER-0001'], {'food':2,'water':2})
        world.cistern_record = {
            'status':'verified_victory','source':'cistern02',
            'migration':{'receipt':{'id':'test-only-migration'}},
        }
        world.give_item('ZC-HER-0001','crowbar','EXP-EQU-002','hand')
        agent=AdaptiveRegionalPlayer('explorer')
        report=agent.run_expedition(
            world,'agent-managed-trip','EXP-LOC-02',['ZC-HER-0001'],
            'market_intro',{'kind':'search','zone':5})
        self.assertEqual(report['status'],'returned')
        self.assertEqual(report['outbound'],['arrived'])
        self.assertEqual(report['return'],['returned'])
        self.assertEqual(world.regional_clock,4)
        self.assertNotIn('agent-managed-trip',world.expeditions)
        self.assertEqual(world.heroes['ZC-HER-0001']['location'],'camp')
        with self.assertRaisesRegex(ValueError,'veículos'):
            agent.run_expedition(world,'no-fuel-policy','EXP-LOC-02',
                ['ZC-HER-0001'],'market_intro',{'kind':'search','zone':5},
                vehicle_id='EXP-VEI-02')

    def test_hungry_posto_team_emergency_loses_fuel_but_preserves_battery(self):
        # Controller/rules regression, not a full campaign replay. The first
        # regional night leaves this migrated H2 team hungry; the resulting PA
        # loss makes the Posto extraction fail. Fuel is lost by the printed
        # emergency rule while the unique battery remains at the team.
        campaign, _ = execute_cistern(22)
        campaign.game.transition_to_last_transmission()
        world = campaign.game.world
        team = list(world.heroes)
        player = AdaptiveRegionalPlayer('builder')

        workshop = player.run_expedition(
            world, 'posto-repair-regression-battery', 'EXP-LOC-03', team,
            'workshop_02', {'kind':'battery','zone':7}, max_steps=120)
        self.assertEqual(workshop['status'], 'returned')
        self.assertIn('battery', world.special_stock)
        meal_order = sorted(world.meal_people())
        night = world.end_day(meal_plan={"food_priority":meal_order,
                                         "water_priority":meal_order})
        self.assertEqual(night['missing']['food'], 2)

        trip = 'posto-repair-regression'
        objectives = ([{'kind':'fuel','zone':7,'lot':lot}
                       for lot in range(1,9)]
                      + [{'kind':'inspect_van','zone':7},
                         {'kind':'repair_van','zone':7}])
        posto = player.run_expedition(
            world, trip, 'EXP-LOC-07', team, 'gas_station_02', objectives,
            max_steps=200, special_items=['battery'],
            return_vehicle_id='EXP-VEI-02')

        self.assertEqual(posto['status'], 'local_defeat_emergency')
        self.assertEqual(posto['local']['status'], 'blocked_during_extraction')
        self.assertEqual(len(world.site_states['EXP-LOC-07']['fuel_cards_taken']), 8)
        self.assertEqual(world.stock['fuel'], 0)
        self.assertEqual(posto['emergency']['lost_cargo'], {'fuel':8})
        self.assertIn('battery', posto['emergency']['retained_special_items'])
        self.assertNotIn('battery', posto['emergency']['lost_special_items'])
        self.assertEqual({row['hero'] for row in world.log
                          if row.get('action')=='repair_van'}, set(team))
        self.assertIn('battery', world.special_stock)
        self.assertFalse(any(row.get('action') == 'repair_van'
                             and row.get('success') for row in world.log))

    def test_controller_never_moves_through_a_closed_door_without_breaching(self):
        world, tactical = self.setup_market()
        player = AdaptiveRegionalPlayer('explorer')
        decision = player.step(tactical, {'kind': 'search', 'zone': 5})
        self.assertEqual(decision['action'], 'open_door')
        self.assertTrue(tactical.state['doors']['1-5']['open'])
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], 2)

    def test_controller_is_deterministic_from_same_observable_state(self):
        _, tactical_a = self.setup_market()
        _, tactical_b = self.setup_market()
        a = AdaptiveRegionalPlayer('balanced').step(tactical_a, {'kind': 'search', 'zone': 5})
        b = AdaptiveRegionalPlayer('balanced').step(tactical_b, {'kind': 'search', 'zone': 5})
        self.assertEqual(a, b)

    def test_controller_and_world_resume_identically_after_save_load(self):
        world_a, tactical_a = self.setup_market()
        world_b, tactical_b = self.setup_market()
        player_a = AdaptiveRegionalPlayer('explorer')
        player_b = AdaptiveRegionalPlayer('explorer')
        objective_a = {'kind': 'search', 'zone': 5, 'searches':2}
        objective_b = {'kind': 'search', 'zone': 5, 'searches':2}
        for _ in range(3):
            self.assertEqual(player_a.step(tactical_a, objective_a),
                             player_b.step(tactical_b, objective_b))
        self.assertEqual(next(iter(player_a.search_progress.values())),1)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'regional-world.json'
            world_a.save(path)
            world_a = World.load(path)
        player_a = AdaptiveRegionalPlayer.from_snapshot(player_a.snapshot())
        tactical_a = TacticalGame(world_a, 'regional-agent-test')
        result_a = player_a.run_objective(tactical_a, objective_a, max_steps=20)
        result_b = player_b.run_objective(tactical_b, objective_b, max_steps=20)
        self.assertEqual(result_a, result_b)
        self.assertEqual(asdict(world_a), asdict(world_b))
        self.assertEqual(player_a.snapshot(), player_b.snapshot())

    def test_controller_uses_an_available_teammate_before_advancing_shared_clock(self):
        world = World.new(41, ['ZC-HER-0001', 'ZC-HER-0003'],
                          {'food': 4, 'water': 4})
        world.cistern_record = {
            'status': 'verified_victory', 'source': 'cistern02',
            'migration': {'receipt': {'id': 'test-only-migration'}},
        }
        world.open_expedition('shared-actions', list(world.heroes), 'EXP-LOC-02')
        world.advance_expedition('shared-actions')
        tactical = TacticalGame.start(world, 'shared-actions', 'market_intro')
        first, second = sorted(world.heroes)
        world.heroes[first]['actions'] = 0
        world.heroes[second]['actions'] = 3
        player = AdaptiveRegionalPlayer('leader')

        decision = player.step(tactical, {'kind': 'zone', 'zone': 5})

        self.assertNotEqual(decision['action'], 'activate')
        self.assertEqual(world.regional_clock, 2)
        self.assertEqual(world.heroes[second]['actions'], 2)

    def test_extraction_waits_for_exit_zone_threat_instead_of_treating_exit_as_action(self):
        world, tactical = self.setup_market()
        hero = 'ZC-HER-0001'
        world.gear[hero].clear()
        tactical.state['heroes'][hero] = tactical.exit_zone
        tactical.state['enemies'] = {
            'exit-threat': {'kind': 'slow', 'zone': tactical.exit_zone, 'health': 1}
        }
        decision = AdaptiveRegionalPlayer('novice').step(
            tactical, {'kind': 'exit'})
        self.assertIn(decision['action'], ('activate', 'blocked'))

    def test_incapacitated_team_returns_a_blocked_result_without_state_mutation(self):
        world, tactical = self.setup_market()
        world._set_hero_health('ZC-HER-0001', 0)
        before = asdict(world)
        result = AdaptiveRegionalPlayer('cautious').step(
            tactical, {'kind': 'search', 'zone': 5})
        self.assertEqual(result['action'], 'blocked')
        self.assertEqual(asdict(world), before)

    def test_celia_can_be_physically_discovered_before_radio_without_free_clue(self):
        from verify_campaign_player02 import execute as execute_cistern
        player02, _ = execute_cistern(22)
        campaign = player02.game
        campaign.transition_to_last_transmission()
        world = campaign.world
        team = sorted(world.heroes)
        expedition = 'test-celia-before-radio'
        world.open_expedition(expedition, team, 'EXP-LOC-05')
        # Testa o controlador tático/local depois da migração. A integração de
        # cartas de Viagem ainda é pendente; isto não se apresenta como replay
        # completo de expedição regional.
        for _ in range(world.expeditions[expedition].segment_cost):
            world.advance_expedition(expedition)
        tactical = TacticalGame.start(world, expedition, 'station_02')
        agent = AdaptiveRegionalPlayer('stealth')
        result = agent.run_objective(
            tactical, {'kind':'investigate_contact','npc':'EXP-NPC-02'}, max_steps=40)
        self.assertEqual(result['status'], 'objective_completed_and_exited')
        receipt = next(row for row in world.log
                       if row.get('action') == 'investigate_physical_contact'
                       and row.get('npc') == 'EXP-NPC-02')
        self.assertEqual(receipt['clues_awarded'], 0)
        self.assertEqual(world.clues, 0)
        self.assertNotIn('EXP-NPC-02', world.npcs)
        self.assertFalse(world.flags.get('radio_code', False))

    def test_seed22_extracts_one_physical_celia_clue_but_cannot_decode_radio(self):
        from arc2 import Arc2
        player02, _ = execute_cistern(22)
        campaign = player02.game
        campaign.transition_to_last_transmission()
        world = campaign.world
        team = sorted(world.heroes)
        expedition = 'test-celia-evidence-seed22'
        world.open_expedition(expedition, team, 'EXP-LOC-05')
        # Ações de deslocamento atuais preservam segmentos e posição, porém
        # a camada regional ainda não revela cartas de Viagem.
        for _ in range(world.expeditions[expedition].segment_cost):
            world.advance_expedition(expedition)
        tactical = TacticalGame.start(world, expedition, 'station_02')
        agent = AdaptiveRegionalPlayer('stealth')
        result = agent.run_objectives(tactical, [
            {'kind':'investigate_contact','npc':'EXP-NPC-02'},
            {'kind':'evidence','npc':'EXP-NPC-02'},
        ], max_steps=60)
        self.assertEqual(result['status'], 'objective_completed_and_exited')
        self.assertEqual(world.clues, 1)
        self.assertEqual(sum(row.get('clues_awarded', 0) for row in world.log
                             if row.get('action') == 'collect_regional_evidence'), 1)
        self.assertFalse(world.flags.get('radio_code', False))
        world.begin_return(expedition)
        while expedition in world.expeditions:
            world.advance_expedition(expedition)
        self.assertEqual(world.regional_clock, 10)
        with self.assertRaisesRegex(ValueError, 'duas pistas'):
            Arc2(world).decode_radio()

    def test_unavailable_contact_is_not_mistaken_for_recruitment(self):
        world, tactical = self.setup_market()
        objective = {'kind':'contact','npc':'EXP-NPC-02'}
        # The market has no Célia contact. Absence from the map is not a
        # successful contact receipt and must not satisfy the objective.
        player = AdaptiveRegionalPlayer('leader')
        player.completed.add(player._key(tactical, objective))  # stale/corrupt policy save
        result = player.run_objective(tactical, objective, max_steps=3)
        self.assertEqual(result['status'], 'blocked')
        self.assertNotIn('EXP-NPC-02', world.expeditions['regional-agent-test'].crew)
        self.assertFalse(any(row.get('action') == 'physical_contact_recruit'
                             for row in world.log))
        self.assertFalse(any(key[1] == 'contact' for key in player.completed))

    def test_invalid_map_does_not_open_or_charge_an_expedition(self):
        world = World.new(41, ['ZC-HER-0001'], {'food':2,'water':2})
        world.cistern_record = {
            'status':'verified_victory', 'source':'cistern02',
            'migration':{'receipt':{'id':'test-only-migration'}},
        }
        before = asdict(world)
        with self.assertRaisesRegex(ValueError, '[Mm]apa'):
            AdaptiveRegionalPlayer('explorer').run_expedition(
                world, 'invalid-map', 'EXP-LOC-02', ['ZC-HER-0001'],
                'not-a-map', {'kind':'search','zone':5})
        self.assertEqual(asdict(world), before)

    def test_controller_takes_legal_detour_when_shortest_map_path_needs_missing_tool(self):
        world, tactical = self.setup_market()
        hero = 'ZC-HER-0001'
        # Isolated path-planning fixture: zone 11 reaches zone 8 directly by
        # the blocked 7-8 door or by open connector 11-12-8.
        tactical.state['heroes'][hero] = 11
        world.gear[hero].clear()
        decision = AdaptiveRegionalPlayer('explorer').step(
            tactical, {'kind':'zone','zone':8})
        self.assertEqual(decision['action'], 'move')
        self.assertEqual(decision['from'], 11)
        self.assertEqual(decision['to'], 12)
        self.assertFalse(tactical.state['doors']['7-8']['open'])

    def test_common_door_costs_one_action_and_blocked_door_costs_two(self):
        world, tactical = self.setup_market()
        with self.assertRaisesRegex(ValueError, 'não bloqueada'):
            tactical.breach('ZC-HER-0001', 1, 5, 'crowbar')
        tactical.open_door('ZC-HER-0001', 1, 5)
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], 2)

        # Isolated API test: moving the hero to a blocked connector is setup,
        # not evidence of a legal campaign route.
        tactical.state['heroes']['ZC-HER-0001'] = 8
        world.heroes['ZC-HER-0001']['actions'] = 1
        prior_durability = world.gear['ZC-HER-0001']['crowbar']['durability']
        with self.assertRaisesRegex(ValueError, '2 PA'):
            tactical.breach('ZC-HER-0001', 7, 8, 'crowbar')
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], 1)
        self.assertEqual(world.gear['ZC-HER-0001']['crowbar']['durability'], prior_durability)

    def test_blocked_door_opens_in_one_two_action_tool_interaction(self):
        world, tactical = self.setup_market()
        # Isolated door-action fixture: use the physical side of the printed
        # blocked connector. This does not assert the route to zone 7.
        tactical.state['heroes']['ZC-HER-0001'] = 8
        world.heroes['ZC-HER-0001']['actions'] = 2
        durability = world.gear['ZC-HER-0001']['crowbar']['durability']
        self.assertTrue(tactical.breach('ZC-HER-0001', 8, 7, 'crowbar'))
        self.assertTrue(tactical.state['doors']['7-8']['open'])
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], 0)
        self.assertEqual(world.gear['ZC-HER-0001']['crowbar']['durability'], durability)
        self.assertEqual(tactical.state['noise'], [])

    def test_leaving_enemy_zone_requires_extra_action(self):
        world, tactical = self.setup_market()
        enemy_id = tactical.spawn('slow', zone=1)
        world.heroes['ZC-HER-0001']['actions'] = 1
        with self.assertRaisesRegex(ValueError, '2 PA'):
            tactical.move('ZC-HER-0001', 2)
        self.assertEqual(tactical.state['heroes']['ZC-HER-0001'], 1)
        self.assertIn(enemy_id, tactical.state['enemies'])
        world.heroes['ZC-HER-0001']['actions'] = 2
        tactical.move('ZC-HER-0001', 2)
        self.assertEqual(world.heroes['ZC-HER-0001']['actions'], 0)


if __name__ == '__main__':
    unittest.main()
