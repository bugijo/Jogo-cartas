"""Filtro da Cisterna produzindo água na campanha regional (aprovado 2026-10-29)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrated_campaign import IntegratedCampaign
from system import World
from verify_campaign_player02 import execute as execute_cistern


def migrated(production=True):
    player, _ = execute_cistern(22)
    campaign = player.game
    campaign.transition_to_last_transmission()
    campaign.world.regional_filter_production = production
    return campaign


def end_day(world):
    order = sorted(world.meal_people())
    return world.end_day({'food_priority': order, 'water_priority': order})


class ContinuityFilterTests(unittest.TestCase):
    def test_migration_projects_active_filter_without_producing(self):
        player, _ = execute_cistern(22)
        water_before = sum(player.game.cistern.water)
        output = player.game.cistern.initial_consumers
        player.game.transition_to_last_transmission()
        world = player.game.world
        self.assertEqual(world.continuity_filter,
                         {'source': 'cistern02', 'active': True, 'output': output})
        self.assertEqual(world.stock['water'], water_before)  # sem água extra na migração

    def test_daily_production_after_meal(self):
        world = migrated().world
        output = world.continuity_filter['output']
        water = world.stock['water']
        consumers = len(world.meal_people())
        day = end_day(world)
        self.assertEqual(day['filter_water'], {'produced': output, 'not_stored': 0})
        self.assertEqual(world.stock['water'], water - consumers + output)
        self.assertEqual(day['stock']['water'], world.stock['water'])

    def test_production_does_not_feed_the_night_it_follows(self):
        world = migrated().world
        world.stock['water'] = 0  # fixture: sem água na refeição
        day = end_day(world)
        self.assertEqual(day['missing']['water'], len(world.meal_people()))
        self.assertEqual(world.stock['water'], world.continuity_filter['output'])

    def test_storage_limit_is_respected(self):
        world = migrated().world
        world.stock['water'] += world.storage - sum(world.stock.values())  # depósito cheio
        world.continuity_filter['output'] = 20  # fixture: produção maior que o espaço livre
        day = end_day(world)
        free = day['filter_water']['produced']
        self.assertLess(free, 20)
        self.assertEqual(day['filter_water']['not_stored'], 20 - free)
        self.assertEqual(sum(world.stock.values()), world.storage)

    def test_disabled_by_default_and_after_collapse(self):
        world = migrated(production=False).world
        water = world.stock['water']
        day = end_day(world)
        self.assertNotIn('filter_water', day)
        self.assertEqual(world.stock['water'], water - len(world.meal_people()))
        world = migrated().world
        world.partial_defeat = True  # fixture: Colapso já ocorrido
        self.assertEqual(world._continuity_filter_dawn()['produced'], 0)

    def test_save_load_and_old_saves(self):
        campaign = migrated()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'c.json'
            campaign.save(path)
            reloaded = IntegratedCampaign.load(path).world
            self.assertEqual(reloaded.continuity_filter, campaign.world.continuity_filter)
            self.assertTrue(reloaded.regional_filter_production)
            world_path = Path(directory) / 'w.json'
            campaign.world.save(world_path)
            payload = json.loads(world_path.read_text(encoding='utf-8'))
            payload.pop('continuity_filter')
            payload.pop('regional_filter_production')
            world_path.write_text(json.dumps(payload), encoding='utf-8')
            old = World.load(world_path)
            self.assertIsNone(old.continuity_filter)
            self.assertIsNone(old._continuity_filter_dawn())

    def test_invalid_filter_rejected(self):
        world = migrated().world
        world.continuity_filter = {'source': 'cistern02', 'active': True, 'output': 0}
        with self.assertRaises(ValueError):
            world.validate()
        fresh = World.new(1, sorted(world.heroes))
        fresh.continuity_filter = {'source': 'cistern02', 'active': True, 'output': 3}
        with self.assertRaises(ValueError):
            fresh.validate()  # sem Cisterna certificada não há filtro


if __name__ == '__main__':
    unittest.main()
