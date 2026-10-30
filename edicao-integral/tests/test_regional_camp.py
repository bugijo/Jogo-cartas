"""Acampamento regional: F aprovada; G, C2 e D em protótipo (2026-10-30)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrated_campaign import IntegratedCampaign
from system import GARDEN_BUILD
from verify_campaign_player02 import execute as execute_cistern


def migrated(seeds=0):
    player, _ = execute_cistern(22)
    player.game.cistern.seeds = seeds  # fixture: Sementes guardadas, sem Horta
    player.game.transition_to_last_transmission()
    return player.game


def end_day(world):
    order = sorted(world.meal_people())
    return world.end_day({'food_priority': order, 'water_priority': order})


def feed(world):
    """fixture: comida e água da noite garantidas, dentro do depósito."""
    need = len(world.meal_people())
    for resource in ('food', 'water'):
        world.stock[resource] = max(world.stock[resource], need)
    assert sum(world.stock.values()) <= world.storage


def fill(world, water):
    """fixture: água definida e o resto do depósito ocupado por remédio."""
    world.stock['water'] = water
    world.stock['medicine'] += world.storage - sum(world.stock.values())


def adults(world):
    return [p['id'] for p in world.continuity_people if p['kind'] == 'adult']


class StoragePriorityTests(unittest.TestCase):
    def setUp(self):
        self.world = migrated().world
        self.need = len(self.world.meal_people())

    def test_off_by_default_keeps_old_behaviour(self):
        world = self.world
        self.assertIsNone(world.regional_camp)
        fill(world, self.need + 5)
        self.assertEqual(world.deposit('food', 3), 0)
        self.assertEqual(world.stock['water'], self.need + 5)

    def test_food_first_discards_only_missing_space_and_logs_it(self):
        world = self.world
        world.set_storage_priority(True)
        fill(world, self.need + 5)
        world.stock['medicine'] -= 1  # uma vaga livre
        self.assertEqual(world.deposit('food', 3), 3)
        self.assertEqual(world.stock['water'], self.need + 3)
        self.assertEqual(world.log[-1], {'day': world.day, 'action': 'storage_discard',
                                         'resource': 'water', 'amount': 2, 'for': 'food',
                                         'reason': 'storage_priority'})
        self.assertLessEqual(sum(world.stock.values()), world.storage)

    def test_never_discards_water_needed_tonight(self):
        world = self.world
        world.set_storage_priority(True)
        fill(world, self.need + 1)
        self.assertEqual(world.deposit('food', 4), 1)
        self.assertEqual(world.stock['water'], self.need)

    def test_water_and_other_resources_never_trigger_discard(self):
        world = self.world
        world.set_storage_priority(True)
        fill(world, self.need + 5)
        self.assertEqual(world.deposit('scrap', 2), 0)
        self.assertEqual(world.stock['water'], self.need + 5)


class BridgeRationTests(unittest.TestCase):
    def test_requires_prototype(self):
        with self.assertRaises(ValueError):
            migrated().world.claim_bridge_ration()

    def test_once_on_arrival_through_storage(self):
        world = migrated().world
        world.enable_regional_prototypes('bridge')
        food = world.stock['food']
        receipt = world.claim_bridge_ration()
        self.assertEqual(receipt['food'], len(world.meal_people()))
        self.assertEqual(world.stock['food'], food + receipt['stored'])
        with self.assertRaises(ValueError):
            world.claim_bridge_ration()

    def test_not_after_first_night(self):
        world = migrated().world
        world.enable_regional_prototypes('bridge')
        end_day(world)
        with self.assertRaises(ValueError):
            world.claim_bridge_ration()


class ForageTests(unittest.TestCase):
    def setUp(self):
        self.world = migrated().world
        self.world.enable_regional_prototypes('forage', forage_max=3, forage_regrow=1)
        self.consumers = len(self.world.meal_people())

    def test_one_food_per_worker_counts_as_work(self):
        world = self.world
        worker = adults(world)[0]
        food = world.stock['food']
        world.assign_forage(worker)
        night = end_day(world)
        self.assertEqual(night['forage'], {'workers': [worker], 'gathered': 1,
                                           'stored': 1, 'pool': 2})
        self.assertEqual(world.regional_camp['forage']['pool'], 3)  # +1 no amanhecer
        self.assertGreaterEqual(world.stock['food'] + night['missing']['food'],
                                food + 1 - self.consumers)

    def test_daily_cap_and_finite_pool(self):
        world = self.world
        heroes = sorted(world.heroes)
        people = adults(world) + heroes
        cap = min(-(-self.consumers // 2), 3)
        for person in people[:cap]:
            world.assign_forage(person)
        with self.assertRaises(ValueError):
            world.assign_forage(people[cap])

    def test_worker_cannot_take_two_jobs(self):
        world = self.world
        hero = sorted(world.heroes)[0]
        world.assign_forage(hero)
        with self.assertRaises(ValueError):
            world.assign_forage(hero)
        with self.assertRaises(ValueError):
            world.work_project('garden', 1, hero)

    def test_planned_before_expedition(self):
        world = self.world
        world.daily_expeditions = 1  # fixture: expedição do dia já aberta
        with self.assertRaises(ValueError):
            world.assign_forage(adults(world)[0])


class RegionalGardenBuildTests(unittest.TestCase):
    def test_needs_transported_seeds(self):
        world = migrated().world
        world.enable_regional_prototypes('garden_build')
        world.stock['scrap'] = 2
        with self.assertRaises(ValueError):
            world.start_regional_garden()

    def test_cost_work_and_first_harvest_after_dawn(self):
        world = migrated(seeds=1).world
        world.enable_regional_prototypes('garden_build')
        self.assertEqual(world.regional_seeds_available(), 1)
        with self.assertRaises(ValueError):  # sem sucata
            world.start_regional_garden()
        world.stock['scrap'] = 3  # fixture: sucata trazida da Oficina
        world.start_regional_garden()
        self.assertEqual((world.stock['scrap'], world.regional_seeds_available()), (1, 0))
        first, second, third = (adults(world) + sorted(world.heroes))[:3]
        world.work_regional_garden(first)
        world.work_regional_garden(second)
        with self.assertRaises(ValueError):  # obra completa: não aceita o 3º
            world.work_regional_garden(third)
        feed(world)
        night = end_day(world)
        self.assertTrue(night['garden_build']['done'])
        self.assertEqual(world.continuity_garden,
                         {'source': 'regional_build', 'active': True, 'output': 4,
                          'worker': None})
        self.assertNotIn('garden_food', night)  # concluída hoje: produz no próximo dia
        feed(world)
        world.assign_continuity_garden(third)
        self.assertEqual(end_day(world)['garden_food']['produced'], 4)
        with self.assertRaises(ValueError):  # Sementes gastas: só uma Horta
            world.start_regional_garden()

    def test_save_load_round_trip(self):
        game = migrated(seeds=1)
        world = game.world
        world.enable_regional_prototypes('bridge', 'forage', 'garden_build')
        world.set_storage_priority(True)
        world.stock['scrap'] = 2
        world.start_regional_garden()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'camp.json'
            game.save(path)
            loaded = IntegratedCampaign.load(path).world
        self.assertEqual(loaded.regional_camp, world.regional_camp)
        self.assertEqual(GARDEN_BUILD, {'seeds': 1, 'scrap': 2, 'work': 2})


if __name__ == '__main__':
    unittest.main()
