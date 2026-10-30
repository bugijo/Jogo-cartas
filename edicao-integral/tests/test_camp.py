"""Acampamento em lotes (D-24..D-26): grade, barracas, horta, Crise, ração de obra."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import camp
import community
from tests.test_community import migrated


class CampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = migrated(lots=True)

    def setUp(self):
        self.world = deepcopy(self.base).world
        self.world.stock.update(food=20, water=20, wood=10, scrap=6)
        self.state = self.world.community['camp']
        self.adults = community.workers(self.world)
        patcher = mock.patch.dict(community.RULES['arrivals'], {'days': []})
        patcher.start()
        self.addCleanup(patcher.stop)

    def roll(self, *values):
        values = list(values)
        return mock.patch('random.Random.randint', lambda self, a, b: values.pop(0))

    def plan(self):
        people = self.world.meal_people()
        return {'food_priority': sorted(people), 'water_priority': sorted(people)}

    def finish(self, kind, workers=None):
        """Obra comunitária até o fim, um dia por vez (ração já no estoque)."""
        while kind in self.world.community['projects']:
            for person in workers or self.adults[:1]:
                community.assign_job(self.world, person, 'obra', kind)
            self.world.end_day(self.plan())

    # --- grade e barracas ---------------------------------------------------------
    def test_clearing_starts_two_by_two_with_core_and_tents(self):
        world, state = self.world, self.state
        self.assertLess(world.residents, camp.RULES['start_level_humans']['2'])
        self.assertEqual(state['level'], 1)
        self.assertEqual(camp.open_lots(world), ['r1c1', 'r1c2', 'r2c1', 'r2c2'])
        tents = camp.built(world, 'barraca')
        self.assertEqual(tents, -(-world.residents // 2))
        self.assertEqual(world.beds, 2 * tents)
        self.assertEqual(world.water_capacity, 24)
        self.assertEqual(world.storage, 24)
        self.assertIsNone(migrated(lots=False).world.community['camp'])

    def test_welcoming_level_opens_three_by_three_with_two_planted_lots(self):
        world = migrated(lots=True, level='acolhedor').world
        state = world.community['camp']
        self.assertEqual(state['level'], 2)
        self.assertEqual(camp.built(world, 'horta'), 2)
        self.assertEqual(len(camp.ready_horta(world)), 2)

    def test_large_group_arrives_with_the_three_by_three_cleared(self):
        world = migrated(2, 5, lots=True).world   # 12 humanos
        self.assertGreaterEqual(world.residents, camp.RULES['start_level_humans']['2'])
        self.assertEqual(world.community['camp']['level'], 2)

    def test_lot_categories_and_stacked_tents(self):
        world = self.world
        self.assertIsNone(camp.free_lot(world, 'oficina'))
        lot = camp.free_lot(world, 'barraca', 'barraca')
        self.assertIn('barraca', camp.GRID[lot])
        world.community['camp']['lots']['r1c1'] = ['barraca', 'barraca']
        world.community['camp']['lots']['r2c2'] = ['barraca', 'barraca']
        world.community['camp']['lots']['r1c2'] = ['barraca', 'barraca']
        world.community['camp']['lots']['r2c1'] = ['barraca', 'barraca']
        with self.assertRaisesRegex(ValueError, 'amplie'):
            community.start_build(world, 'horta')
        self.assertFalse(world.start_project('storage'))  # sem lote de estoque no 2×2

    def test_expansion_opens_three_by_three_and_needs_preparation_for_four(self):
        world = self.world
        with self.assertRaisesRegex(ValueError, 'nível anterior'):
            community.start_build(world, 'expansao3')
        community.start_build(world, 'expansao2')
        self.assertEqual(world.stock['wood'], 7)
        self.finish('expansao2', self.adults[:2])
        self.assertEqual(self.state['level'], 2)
        self.assertEqual(len(camp.open_lots(world)), 9)
        with self.assertRaisesRegex(ValueError, 'Depósito, Oficina ou Vigia'):
            community.start_build(world, 'expansao3')

    def test_family_arrival_brings_its_tent(self):
        world = self.world
        world.community['arrival'] = {'day': world.day, 'roll': 5,
                                      'people': ['adult', 'adult', 'child'],
                                      'tent': 'barraca_familiar'}
        beds = world.beds
        free = world.free_terrain
        community.receive(world, True)
        if free:
            self.assertEqual(world.beds, beds + 4)
        else:
            self.assertEqual(self.state['tents'], {'barraca_familiar': 1})

    # --- horta por lotes ------------------------------------------------------------
    def test_horta_needs_growth_workers_and_water(self):
        world = self.world
        community.start_build(world, 'horta')
        community.assign_job(world, self.adults[0], 'obra', 'horta')
        world.end_day(self.plan())
        self.assertEqual(camp.built(world, 'horta'), 1)
        with self.assertRaisesRegex(ValueError, 'lote de horta pronto'):
            community.assign_job(world, self.adults[0], 'horta')
        world.community['camp']['horta_ready'] = {lot: world.day for lot in
                                                  world.community['camp']['horta_ready']}
        community.assign_job(world, self.adults[0], 'horta')
        with self.assertRaisesRegex(ValueError, 'lote de horta pronto'):
            community.assign_job(world, self.adults[1], 'horta')
        water = world.stock['water']
        world.community['camp']['rain'] = False
        with self.roll(4):
            result = community.day_work(world)['horta']['workers'][0]
        per = camp.HORTA['food_per_lot']
        self.assertEqual((result['lots'], result['water'], result['food']), (1, 1, per))
        self.assertEqual(world.stock['water'], water - 1)

    def test_horta_worker_tends_two_lots_farmer_four_and_pest(self):
        world = self.world
        state = self.state
        state['lots'].update(r1c2=['horta'], r2c2=['horta'])
        state['horta_ready'] = {'r1c2': world.day, 'r2c2': world.day}
        state['rain'] = False
        worker = next(p for p in self.adults
                      if not community.specialist(world, p, 'horta'))
        community.assign_job(world, worker, 'horta')
        with self.roll(1):
            result = community.day_work(world)['horta']['workers'][0]
        per = camp.HORTA['food_per_lot']
        self.assertEqual((result['lots'], result['water'], result['food']), (2, 1, 2 * per - 1))
        world.stock['water'] = 0
        world.community['jobs'] = {}
        world.worked_today = []
        community.assign_job(world, worker, 'horta')
        with self.roll(6):
            result = community.day_work(world)['horta']['workers'][0]
        self.assertEqual(result['food'], 0)  # sem água, a horta não rende
        state['rain'] = True
        world.community['jobs'] = {}
        world.worked_today = []
        community.assign_job(world, worker, 'horta')
        with self.roll(6):
            result = community.day_work(world)['horta']['workers'][0]
        self.assertEqual((result['water'], result['food']), (0, 2 * per))  # choveu
        self.assertEqual(camp.HORTA['specialist_lots'], 4)

    # --- Crise 0–10 -----------------------------------------------------------------
    def test_crisis_rises_with_deficit_repeats_and_recovers(self):
        world, state = self.world, self.state
        people = world.meal_people()
        humans = [p for p in people if people[p].get('kind') != 'dog']
        world.stock['food'] = len(people) - 1
        plan = {'food_priority': humans + [p for p in people if p not in humans],
                'water_priority': sorted(people)}
        world.end_day(plan)  # só um cão sem comida: humanos servidos
        self.assertEqual(state['crisis'], 0)
        world.stock.update(food=len(people) - len(humans) // 2 - 1, water=20)
        world.end_day({'food_priority': sorted(people), 'water_priority': sorted(people)})
        first = state['crisis']
        self.assertIn(first, (1, 2))
        world.stock.update(food=0, water=20)
        world.end_day({'food_priority': sorted(people), 'water_priority': sorted(people)})
        self.assertEqual(state['crisis'], first + camp.CRISIS['large'] + camp.CRISIS['repeat'])
        world.stock.update(food=24, water=24)
        before = state['crisis']
        world.end_day(self.plan())
        self.assertEqual(state['crisis'], before - camp.CRISIS['recover_reserve'])

    def test_crisis_ten_collapses_and_refusal_raises_it(self):
        world, state = self.world, self.state
        world.community['arrival'] = {'day': world.day, 'roll': 1, 'people': ['adult']}
        community.receive(world, False)
        self.assertEqual(state['crisis'], 1)
        self.assertEqual(world.shelter_morale, self.base.world.shelter_morale)
        state['crisis'] = 9
        world.stock['food'] = 0
        people = world.meal_people()
        world.end_day({'food_priority': sorted(people), 'water_priority': sorted(people)})
        self.assertTrue(world.partial_defeat)

    def test_crisis_is_the_only_collective_collapse_in_lots(self):
        world = self.world
        people = world.meal_people()
        for _ in range(3):
            world.stock.update(food=0, water=24)
            world.end_day({'food_priority': sorted(people), 'water_priority': sorted(people)})
        self.assertLess(self.state['crisis'], camp.CRISIS['max'])
        self.assertFalse(world.partial_defeat)  # 3 noites sem comida: Crise alta, sem colapso §25

    def test_only_bedded_people_recover_and_grave_crisis_stops_recovery(self):
        world, state = self.world, self.state
        heroes = sorted(world.heroes)
        for hero in heroes:
            world._set_hero_health(hero, 2)
        state['lots'] = {lot: [] for lot in camp.GRID}
        state['lots']['r2c1'] = ['barraca']  # 2 camas
        world.end_day(self.plan())
        recovered = sum(world.heroes[h]['health'] == 3 for h in heroes)
        self.assertEqual(recovered, min(2, len(heroes)))
        for hero in heroes:
            world._set_hero_health(hero, 2)
        state['lots']['r2c1'] = ['barraca', 'barraca']
        state['lots']['r1c2'] = ['barraca', 'barraca']
        state['crisis'] = camp.CRISIS['grave']
        world.stock.update(food=24, water=24)
        world.end_day(self.plan())
        self.assertTrue(all(world.heroes[h]['health'] == 2 for h in heroes))

    # --- esforço das obras ----------------------------------------------------------
    def test_heavy_work_eats_a_ration_and_stops_in_moderate_crisis(self):
        world, state = self.world, self.state
        community.start_build(world, 'expansao2')
        food = world.stock['food']
        community.assign_job(world, self.adults[0], 'obra', 'expansao2')
        out = community.day_work(world)['build'][0]
        self.assertEqual(out['ration'], 1)
        self.assertEqual(world.stock['food'], food - 1)
        state['crisis'] = camp.CRISIS['moderate']
        world.community['jobs'] = {}
        world.worked_today = []
        with self.assertRaisesRegex(ValueError, 'Crise moderada'):
            community.assign_job(world, self.adults[0], 'obra', 'expansao2')
        state['crisis'] = 0
        community.start_build(world, 'barraca')
        food = world.stock['food']
        community.assign_job(world, self.adults[1], 'obra', 'barraca')
        out = community.day_work(world)['build'][0]
        self.assertEqual((out['ration'], world.stock['food']), (0, food))  # obra leve

    # --- conhecimento e profissões --------------------------------------------------
    def test_knowledge_found_once_per_location_unlocks_build(self):
        world = self.world
        with self.assertRaisesRegex(ValueError, 'conhecimento'):
            community.start_build(world, 'composteira')
        self.assertEqual(camp.find_knowledge(world, 'EXP-LOC-01'), 'K-AGR')
        self.assertIsNone(camp.find_knowledge(world, 'EXP-LOC-01'))
        self.assertIsNone(camp.find_knowledge(world, 'EXP-LOC-07'))  # Posto: sem carta
        community.start_build(world, 'composteira')
        self.finish('composteira')
        self.assertTrue(camp.has(world, 'composteira'))
        state = self.state
        state['lots']['r1c1'] = ['horta']
        state['horta_ready'] = {'r1c1': world.day}
        state['rain'] = True
        world.community['jobs'] = {}
        world.worked_today = []
        community.assign_job(world, self.adults[0], 'horta')
        with self.roll(6):
            result = community.day_work(world)['horta']['workers'][0]
        self.assertEqual(result['food'], camp.HORTA['food_per_lot'] + 1)

    def test_tools_bench_and_remedy_without_specialist(self):
        world = self.world
        state = self.state
        state['knowledge'] += ['K-FER', 'K-SAU']
        world.community['built'] += ['bancada', 'ambulatorio']
        community.start_build(world, 'horta')
        worker = next(p for p in self.adults if not community.specialist(world, p, 'obra'))
        community.assign_job(world, worker, 'obra', 'horta')
        out = community.day_work(world)['build'][0]
        self.assertEqual(out['units'], 2)  # sem carpinteiro, a bancada compensa
        world.community['jobs'] = {}
        world.worked_today = []
        nurse = next(p for p in self.adults if not community.specialist(world, p, 'cuidar'))
        community.assign_job(world, nurse, 'remedio')
        medicine, food = world.stock['medicine'], world.stock['food']
        with self.roll(3):
            out = community.day_work(world)['remedio'][0]
        self.assertEqual((out['medicine'], world.stock['food']), (0, food - 2))
        world.community['jobs'] = {}
        world.worked_today = []
        community.assign_job(world, nurse, 'remedio')
        with self.roll(4):
            out = community.day_work(world)['remedio'][0]
        self.assertEqual(world.stock['medicine'], medicine + 1)

    def test_merged_professions_keep_every_activity_covered(self):
        bonuses = {b for spec in community.PROFESSIONS.values() for b in spec['bonus']}
        self.assertTrue({'caca', 'pesca', 'lenha', 'coleta', 'agua', 'horta', 'obra',
                         'cozinhar', 'cuidar', 'vigiar', 'sucata'} <= bonuses)
        self.assertEqual(len(community.RULES['profession_deck']), 12)
        self.assertEqual(len(community.PROFESSIONS), 9)

    # --- situação H: dependências sem ciclo ----------------------------------------
    def test_every_build_has_a_legal_path_from_the_clearing(self):
        """Fecho por níveis: obra entra quando o lote, o requisito e o conhecimento existem."""
        from system import LOCATIONS, STRUCTURES as SYSTEM
        builds = {k: s for k, s in community.STRUCTURES.items() if s.get('camp', True)}
        builds.update({k: {'cost': s['cost']} for k, s in SYSTEM.items() if k != 'garden'})
        known = {spec['location'] for spec in camp.KNOWLEDGE.values()}
        self.assertTrue(known <= set(LOCATIONS))
        level, done = 1, set()
        for _ in range(len(builds) + 3):
            cats = {c for lot, cs in camp.GRID.items() if camp.lot_level(lot) <= level for c in cs}
            for kind, spec in builds.items():
                cat = camp.category(kind)
                req = spec.get('requires')
                if ((cat is None or cat in cats) and (not req or req in done)
                        and (not spec.get('requires_any') or set(spec['requires_any']) & done)
                        and (not spec.get('expansion') or spec['expansion'] == level + 1)):
                    done.add(kind)
                    level = max(level, spec.get('expansion', level))
        self.assertEqual(set(builds) - done, set())

    def test_heroes_away_for_days_while_camp_keeps_working(self):
        """Situação E: heróis em viagem de 3 dias; horta e refeição seguem sem eles."""
        world, state = self.world, self.state
        state['lots']['r1c1'] = ['horta']
        state['horta_ready'] = {'r1c1': world.day}
        heroes = sorted(world.heroes)[:2]
        for hero in heroes:
            world._set_hero_health(hero, 3)
            community.send_trip(world, hero, 'pesca', 3)
        away = community.away(world)
        self.assertTrue(set(heroes) <= away)
        for _ in range(3):
            people = world.meal_people()
            self.assertFalse(set(heroes) & set(people))  # comem a própria ração
            community.assign_job(world, self.adults[0], 'horta')
            world.stock.update(food=min(24, world.stock['food'] + 5), water=20)
            world.end_day(self.plan())
        self.assertFalse(set(heroes) & community.away(world))
        self.assertTrue(any(r.get('action') == 'worker_trip_return' for r in world.log))

    def test_watch_and_guards_shoot_in_the_final_defense(self):
        from arc2 import Arc2
        world = self.world
        world.flags.update(radio_code=True, access_card=True, military_access=True)
        world.special_stock += ['access_card', 'transmitter']
        world.structures['watch'] = {'health': 3, 'age': 0}
        guard = self.adults[0]
        world.community['professions'][guard] = 'guarda'
        with mock.patch.dict(camp.RULES['defense_support'], {'on': True}):
            self.assertEqual(camp.defense_shooters(world), ['vigia', guard])
            arc = Arc2(world)
            defense = arc.final_defense()
            health = sum(e['health'] for e in defense['enemies'].values())
            arc.defense_activate()
            self.assertEqual(len(defense['support'][0]), 2)
            left = sum(e['health'] for e in defense['enemies'].values())
            self.assertLessEqual(left, health - 2)
        self.assertEqual(camp.defense_shooters(world), [])  # regra desligada no padrão

    def test_water_has_its_own_track(self):
        world = self.world
        world.stock.update(water=24, food=0)
        self.assertEqual(world.deposit('food', 5), 5)
        self.assertEqual(world.free_space('wood'), 20 - world.stock['wood'])


if __name__ == '__main__':
    unittest.main()
