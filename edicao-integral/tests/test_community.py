"""Regras Comunidade (Missão Mestre): trabalhadores, profissões, viagens."""
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import community
from campaign_player02 import CampaignPlayer02
from simulate_cistern_sweep import auto_settings
from system import World


def migrated(seed=2, size=4, on=True):
    player = CampaignPlayer02.new_hn(seed, size)
    for key, value in auto_settings(size).items():
        setattr(player, key, value)
    player.garden = True
    assert player.attempt_cistern()['verified_victory']
    player.game.transition_to_last_transmission(community=on)
    return player.game


class CommunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = migrated()

    def setUp(self):
        self.campaign = deepcopy(self.base)
        self.world = self.campaign.world
        self.world.stock.update(food=20, water=20)
        self.adults = [p for p in community.workers(self.world)]

    def roll(self, *values):
        """Força os D6 da Comunidade (o resto do RNG segue igual)."""
        values = list(values)
        return mock.patch('random.Random.randint', lambda self, a, b: values.pop(0))

    def plan(self):
        people = self.world.meal_people()
        return {'food_priority': sorted(people), 'water_priority': sorted(people)}

    # --- estado, migração, camas ------------------------------------------------
    def test_off_by_default_and_on_migration(self):
        self.assertIsNone(migrated(on=False).world.community)
        self.assertEqual(set(self.world.community['professions']), set(self.adults))
        self.assertEqual(self.world.water_capacity, 30)

    def test_crowded_shelter_migrates_and_denies_rest_recovery(self):
        world = self.world
        world.continuity_beds -= world.beds - world.residents + 1  # um sem cama
        world.validate()
        self.assertTrue(community.crowded(world))
        hero = sorted(world.heroes)[0]
        world._set_hero_health(hero, 2)
        world.end_day(self.plan())
        self.assertEqual(world.heroes[hero]['health'], 2)
        world.continuity_beds -= 2  # três sem cama: além do limite de +2
        with self.assertRaises(ValueError):
            world.validate()

    def test_water_tanks_do_not_take_food_space(self):
        world = self.world
        world.stock.update(food=0, water=30)
        self.assertEqual(world.deposit('food', 5), 5)
        self.assertEqual(world.deposit('water', 5), 0)
        world.structures['reservoir'] = {'health': 3, 'age': 0}
        self.assertEqual(world.water_capacity, 42)

    # --- trabalho sem heróis ------------------------------------------------------
    def test_workers_produce_with_every_hero_away(self):
        world = self.world
        for hero in world.heroes:
            world.departed_today.append(hero)  # todos os heróis fora hoje
        community.send_trip(world, self.adults[0], 'pesca', 1)
        community.start_build(world, 'coletor') if world.stock['wood'] else None
        with self.roll(4, 1):
            world.end_day(self.plan())
        returns = [r for r in world.log if r.get('action') == 'worker_trip_return']
        self.assertEqual(len(returns), 1)
        self.assertGreater(returns[0]['delivered']['food'], 0)

    def test_one_function_per_worker(self):
        world = self.world
        worker = self.adults[0]
        community.send_trip(world, worker, 'lenha', 2)
        with self.assertRaises(ValueError):
            community.assign_job(world, worker, 'cuidar')
        with self.assertRaises(ValueError):
            community.send_trip(world, worker, 'pesca', 1)
        with self.assertRaises(ValueError):
            world.assign_continuity_garden(worker)

    def test_hero_on_trip_skips_tactical_expedition_and_shelter_meal(self):
        world = self.world
        hero = sorted(world.heroes)[0]
        community.send_trip(world, hero, 'pesca', 2)
        self.assertNotIn(hero, world.meal_people())
        with self.assertRaises(ValueError):
            world.open_expedition('x', [hero], 'EXP-LOC-02')

    def test_evacuation_supply_logged_once(self):
        row = next(r for r in self.world.log if r.get('event') == 'community_rules_on')
        self.assertEqual(row['evacuation_supply']['food'], len(self.base.world.meal_people()))

    # --- viagens: duração, D6 × dias, conversão, consumo, cartas ---------------------
    def test_duration_limits(self):
        for days in (0, 4, True):
            with self.assertRaises(ValueError):
                community.send_trip(self.world, self.adults[0], 'pesca', days)

    def test_rations_replace_shelter_meal_without_double_charge(self):
        world = self.world
        before = len(world.meal_people())
        food = world.stock['food']
        community.send_trip(world, self.adults[0], 'pesca', 2)
        self.assertEqual(world.stock['food'], food - 2)
        self.assertEqual(len(world.meal_people()), before - 1)
        self.assertEqual(world.consumers, before - 1)

    def test_yield_is_d6_times_days_converted_and_capped(self):
        world = self.world
        state = world.community
        state['deck']['order'] = ['tranquila'] * 12
        state['deck']['pos'] = 0
        state['professions'][self.adults[0]] = 'comum'
        community.send_trip(world, self.adults[0], 'lenha', 2)
        wood = world.stock['wood']
        pool = state['pools']['madeira']
        with self.roll(5):  # 5 × 2 dias = 10 pontos → 5 madeira (2 pontos cada)
            world.end_day(self.plan())
            world.end_day(self.plan())
        self.assertEqual(world.stock['wood'], wood + 5)
        ret = next(r for r in world.log if r.get('action') == 'worker_trip_return')
        self.assertEqual((ret['roll'], ret['points'], ret['units']), (5, 10, 5))
        # 1º amanhecer repõe 1 (até 12); no 2º sai a carga e repõe 1.
        self.assertEqual(state['pools']['madeira'], min(12, pool + 1) - 5 + 1)

    def test_specialist_bonus_and_unsupplied_cost(self):
        world = self.world
        state = world.community
        state['deck']['order'] = ['tranquila'] * 12
        state['deck']['pos'] = 0
        state['professions'][self.adults[0]] = 'pescador'
        community.send_trip(world, self.adults[0], 'pesca', 1, rations=0)
        with self.roll(3):  # (3+1) × 1 − 1 (dia sem ração) = 3 pontos
            world.end_day(self.plan())
        ret = next(r for r in world.log if r.get('action') == 'worker_trip_return')
        per = community.ACTIVITIES['pesca']['points_per_unit']
        self.assertEqual((ret['bonus'], ret['points'], ret['units']), (1, 3, 3 // per))

    def test_event_cards_wound_and_lose_cargo(self):
        world = self.world
        state = world.community
        state['deck']['order'] = ['ferimento', 'perda'] + ['tranquila'] * 10
        state['deck']['pos'] = 0
        worker = self.adults[0]
        state['professions'][worker] = 'comum'
        community.send_trip(world, worker, 'caca', 3)  # 3 dias + perigosa = 3 cartas
        for _ in range(3):
            with self.roll(6):
                world.end_day(self.plan())
        ret = next(r for r in world.log if r.get('action') == 'worker_trip_return')
        self.assertEqual(ret['cards'], ['ferimento', 'perda', 'tranquila'])
        person = next(p for p in world.continuity_people if p['id'] == worker)
        self.assertEqual(person['wounds'], 1)
        self.assertEqual(ret['units'], ret['found'] // 2)

    def test_delay_card_returns_next_dawn(self):
        world = self.world
        state = world.community
        state['deck']['order'] = ['atraso'] + ['tranquila'] * 11
        state['deck']['pos'] = 0
        worker = self.adults[0]
        community.send_trip(world, worker, 'pesca', 1)
        with self.roll(4):
            world.end_day(self.plan())
        self.assertIn(worker, community.away(world))
        with self.roll(4):
            world.end_day(self.plan())
        self.assertNotIn(worker, community.away(world))

    # --- comida e água --------------------------------------------------------------
    def test_meat_cooks_into_four_portions_or_two_without_wood(self):
        world = self.world
        state = world.community
        state['meat'] = [{'units': 2, 'spoils': world.day + 2}]
        world.stock['wood'] = 1
        cook, other = self.adults[:2]
        state['professions'][cook] = 'comum'
        state['professions'][other] = 'comum'
        food = world.stock['food']
        community.assign_job(world, cook, 'cozinhar')
        community.assign_job(world, other, 'cozinhar')
        result = community.day_work(world)
        portions = sorted(row['food'] for row in result['cook'])
        self.assertEqual(portions, [2, 4])  # 1 lenha: 4 porções; a outra improvisa
        self.assertEqual(world.stock['food'], food + 6)
        self.assertEqual(world.stock['wood'], 0)

    def test_raw_meat_spoils(self):
        world = self.world
        world.community['meat'] = [{'units': 1, 'spoils': world.day + 1}]
        world.end_day(self.plan())
        self.assertEqual(world.community['meat'], [])

    def test_fruit_feeds_and_partly_hydrates(self):
        world = self.world
        world.stock.update(food=0, water=0)
        out = community._deliver(world, 'fruit', 5)
        self.assertEqual(out, {'food': 5, 'water': 2})

    def test_rain_collector_depends_on_weather_and_capacity(self):
        world = self.world
        world.community['built'].append('coletor')
        world.stock['water'] = 0
        with self.roll(3, *[1] * 20):
            out = community.dawn(world)
        self.assertEqual(out['rain'], {'roll': 3, 'water': 0})
        with self.roll(6, *[1] * 20):
            out = community.dawn(world)
        self.assertEqual(out['rain']['water'], 4)

    def test_raw_water_needs_treatment(self):
        world = self.world
        world.continuity_filter = None
        world.stock.update(water=0, wood=1)
        out = community._deliver(world, 'raw_water', 5)
        self.assertEqual((out['water'], out['wood_boil'], out['untreated_lost']), (3, 1, 2))

    def test_garden_farmer_bonus(self):
        world = self.world
        world.continuity_garden = {'source': 'cistern02', 'active': True, 'output': 4,
                                   'worker': None}
        farmer = self.adults[0]
        world.community['professions'][farmer] = 'agricultor'
        world.assign_continuity_garden(farmer)
        food = world.stock['food']
        night = world.end_day(self.plan())
        self.assertEqual(night['garden_food']['produced'], 5)
        self.assertGreaterEqual(world.stock['food'], food + 5 - len(world.meal_people()))

    # --- construção, cuidado, vigia, resgate ------------------------------------------
    def test_workers_build_without_heroes(self):
        world = self.world
        world.stock.update(wood=2, scrap=1)
        community.start_build(world, 'coletor')
        self.assertEqual(world.stock['wood'], 1)
        community.assign_job(world, self.adults[0], 'obra', 'coletor')
        world.end_day(self.plan())
        self.assertIn('coletor', world.community['built'])

    def test_canteiro_needs_a_worker_and_has_a_limit(self):
        world = self.world
        state = world.community
        state['built'] += ['canteiro']
        a, b = self.adults[:2]
        state['professions'][a] = 'agricultor'
        community.assign_job(world, a, 'canteiro')
        with self.assertRaises(ValueError):  # um trabalhador por canteiro
            community.assign_job(world, b, 'canteiro')
        food = world.stock['food']
        out = community.day_work(world)
        self.assertEqual(out['canteiro'][0]['food'], 3)  # 2 + agricultor
        self.assertEqual(world.stock['food'], food + 3)
        state['built'] += ['canteiro']
        world.stock.update(wood=5, scrap=5)
        with self.assertRaises(ValueError):  # máximo 2
            community.start_build(world, 'canteiro')

    def test_dog_joins_trip_adds_bonus_and_eats_from_it(self):
        world = self.world
        dog = next(p['id'] for p in world.continuity_people if p['kind'] == 'dog')
        state = world.community
        state['deck']['order'] = ['tranquila'] * 12
        state['deck']['pos'] = 0
        state['professions'][self.adults[0]] = 'comum'
        before = len(world.meal_people())
        community.send_trip(world, self.adults[0], 'pesca', 2, dog=dog)
        self.assertEqual(len(world.meal_people()), before - 2)  # pessoa e cão fora
        with self.assertRaises(ValueError):
            community.send_trip(world, self.adults[1], 'coleta', 1, dog=dog)
        with self.roll(4):  # (4+1) × 2 − 2 (o cão come) = 8 pontos
            world.end_day(self.plan())
            world.end_day(self.plan())
        ret = next(r for r in world.log if r.get('action') == 'worker_trip_return')
        self.assertEqual((ret['bonus'], ret['points']), (1, 8))
        self.assertNotIn(dog, community.away(world))

    def test_arrival_fatigue_caps_health_but_keeps_wounds(self):
        tired = next(r for r in self.world.log if r.get('event') == 'community_rules_on')
        self.assertTrue(all(h['health'] <= 2 for h in self.world.heroes.values()))
        self.assertTrue(all(before == 3 for before in tired['arrival_fatigue'].values()))
        base = migrated(on=False).world
        for hero_id, hero in base.heroes.items():
            self.assertEqual(self.world.heroes[hero_id]['health'], min(2, hero['health']))

    def test_trip_cannot_empty_the_shelter(self):
        world = self.world
        worker = self.adults[0]
        dog = next(p for p in world.continuity_people if p['kind'] == 'dog')
        alone = {worker: community._person(world, worker), dog['id']: dog}
        with mock.patch.object(World, 'meal_people', lambda self: alone):
            with self.assertRaisesRegex(ValueError, 'sem nenhum humano'):
                community.send_trip(world, worker, 'coleta', 1)
        community.send_trip(world, worker, 'coleta', 1)  # com gente em casa, sai

    def test_morale_drops_with_scarcity_and_recovers_when_all_eat(self):
        world = self.world
        people = world.meal_people()
        human = next(pid for pid, p in people.items() if p.get('kind') != 'dog')
        world.stock.update(food=len(people) - 1, water=25)
        order = [human] + sorted(pid for pid in people if pid != human)
        world.end_day({'food_priority': order[1:] + [human], 'water_priority': order})
        self.assertEqual(world.shelter_morale, 4)
        world.stock.update(food=20, water=25)
        world.end_day(self.plan())
        self.assertEqual(world.shelter_morale, 5)

    def test_unfed_dog_does_not_lower_morale_and_zero_morale_is_defeat(self):
        world = self.world
        people = world.meal_people()
        dog = next(pid for pid, p in people.items() if p.get('kind') == 'dog')
        world.stock.update(food=len(people) - 1, water=25)
        world.end_day({'food_priority': sorted(pid for pid in people if pid != dog) + [dog],
                       'water_priority': sorted(people)})
        self.assertEqual(world.shelter_morale, 5)
        world.shelter_morale = 1
        people = world.meal_people()
        world.stock.update(food=0, water=25)
        world.end_day({'food_priority': sorted(people), 'water_priority': sorted(people)})
        self.assertEqual(world.shelter_morale, 0)
        self.assertTrue(world.partial_defeat)

    def test_rescued_survivor_brings_baggage_and_profession(self):
        world = self.world
        world.stock.update(food=0)
        with self.roll(4):
            receipt = community.join(world, 'NOVO-01')
        self.assertEqual(receipt['baggage'], {'food': 2})
        self.assertIn(world.community['professions']['NOVO-01'], community.PROFESSIONS)

    def test_guard_prevents_crisis(self):
        world = self.world
        community.assign_job(world, self.adults[0], 'vigiar')
        world.community['professions'][self.adults[0]] = 'guarda'
        with self.roll(3):
            self.assertTrue(community.guard_roll(world)['prevents'])

    def test_traps_catch_meat_from_finite_game(self):
        world = self.world
        state = world.community
        state['traps'] = [{'set_day': 0}]
        state['pools']['caca'] = 1
        with self.roll(6):
            community.dawn(world)
        self.assertEqual(sum(m['units'] for m in state['meat']), 1)
        self.assertLessEqual(state['pools']['caca'], 1)  # pegou 1; reposição do dia

    # --- integridade --------------------------------------------------------------
    def test_save_load_and_no_duplication(self):
        world = self.world
        community.send_trip(world, self.adults[0], 'coleta', 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'w.json'
            world.save(path)
            again = World.load(path)
        self.assertEqual(again.__dict__, world.__dict__)
        total = sum(world.stock.values())
        world.end_day(self.plan())
        night = world.log[-1]
        self.assertLessEqual(sum(world.stock.values()), total + 4 * 6 + 10)
        self.assertNotIn(self.adults[0], night['unfed']['food'])

    def test_hero_arrival_kits_logged_once(self):
        rows = [r for r in self.world.log if r.get('event') == 'community_rules_on']
        self.assertEqual(len(rows), 1)
        self.assertEqual(set(rows[0]['hero_kits']), set(self.world.heroes))
        self.assertTrue(all(1 <= kit['roll'] <= 6 for kit in rows[0]['hero_kits'].values()))

    def test_invalid_state_rejected(self):
        world = self.world
        world.community['pools']['caca'] = 99
        with self.assertRaises(ValueError):
            world.validate()


if __name__ == '__main__':
    unittest.main()
