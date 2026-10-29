"""Horta §61 entre a Cisterna e o regional (alternativa H1, aprovada 2026-10-29)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cistern02 import Cistern02, LINK_IDS, STARTERS
from integrated_campaign import IntegratedCampaign
from system import World
from verify_campaign_player02 import execute as execute_cistern


def condo_rescue(seed, decision='welcome', full=False):
    hero = STARTERS[0]
    game = IntegratedCampaign.new(seed, STARTERS[:2], LINK_IDS[:2])
    tactical = game._start_tactical_fixture('Condomínio', [hero])
    if full:  # fixture: carga do herói já cheia
        tactical.supply_cargo[hero].extend(
            {'id': f'fixture:{n}', 'kind': 'Conserva', 'cards': 1, 'portions': 4,
             'zone': 7, 'hero': hero} for n in range(4 - tactical._load(hero)))
    tactical.positions[hero] = 14  # O2 canônico do Condomínio.
    receipt = tactical.rescue(hero, 'ZC-MOR-0006', decision)
    tactical.positions[hero] = tactical.map['exit']
    tactical.end_round()
    game.return_expedition()
    return game, receipt


def ready_garden():
    """Cistern02 no dia 1 com Sementes de antes (fixture) e 3 Materiais."""
    game = Cistern02.new(STARTERS[:2], LINK_IDS[:2], seed=5)
    game.seeds, game.seeds_day = 1, 0  # fixture
    return game


def build(game, workers):
    game.plan_garden_work(workers)
    game.lock_work_plan([])
    return game.work_garden()


class SeedsTests(unittest.TestCase):
    def test_welcome_delivers_seeds_on_return(self):
        game, receipt = condo_rescue(201)
        self.assertTrue(receipt['seeds'])
        self.assertEqual((game.cistern.seeds, game.cistern.seeds_day), (1, game.cistern.day))
        self.assertIn('condomínio:Sementes:1', game.delivered_objectives)

    def test_no_seeds_without_free_cargo_or_without_welcome(self):
        game, receipt = condo_rescue(202, full=True)
        self.assertFalse(receipt['seeds'])
        self.assertEqual(game.cistern.seeds, 0)
        game, receipt = condo_rescue(203, decision='decline')
        self.assertNotIn('seeds', receipt)
        self.assertEqual(game.cistern.seeds, 0)


class CisternGardenTests(unittest.TestCase):
    def test_reserve_requires_seeds_from_earlier_day_and_two_materials(self):
        game = ready_garden()
        game.seeds_day = game.day  # fixture: Sementes chegaram hoje
        with self.assertRaises(ValueError):
            game.reserve_garden()
        game.seeds_day = game.day - 1
        game.materials = 1
        with self.assertRaises(ValueError):
            game.reserve_garden()
        game.materials = 3
        game.reserve_garden()
        self.assertEqual((game.materials, game.seeds), (1, 0))
        self.assertEqual(game.garden['terrain'], 8)

    def test_two_works_complete_and_production_starts_next_day(self):
        game = ready_garden()
        game.reserve_garden()
        heroes = STARTERS[:2]
        receipt = build(game, list(heroes))
        self.assertTrue(receipt['done'])
        self.assertIn('Horta', game.structures)
        with self.assertRaises(ValueError):  # concluída hoje: produz só amanhã
            game.garden_workers_plan = []
            game.work_plan_locked = False
            game.plan_garden_work([heroes[0]])
        game.meal(); game.night_intentions(); game.next_day()
        food = sum(game.food)
        receipt = build(game, [heroes[0]])
        self.assertEqual(receipt['food'], 4)
        self.assertEqual(sum(game.food), food + 4)

    def test_worker_limits_and_exclusive_jobs(self):
        game = ready_garden()
        game.reserve_garden()
        hero, other = STARTERS[:2]
        with self.assertRaises(ValueError):  # três trabalhadores num projeto
            game.plan_garden_work([hero, other, 'R01'])
        game.plan_garden_work([hero])
        with self.assertRaises(ValueError):
            game.plan_guards([hero])
        with self.assertRaises(ValueError):
            game.lock_work_plan([hero])

    def test_siege_damage_deactivates_garden(self):
        game = ready_garden()
        game.reserve_garden()
        build(game, list(STARTERS[:2]))
        game.raise_pressure(3)  # Pressão 3 enfileira o cerco pelo caminho legal
        encounter = game.reveal_siege()
        defense = 2 + int(any(p['kind'] == 'dog' and p['alert'] for p in game.people))
        gap = max(0, encounter['force'] - defense)
        targets = ['Horta', 'Portão'][:0 if gap == 0 else 1 if gap <= 2 else 2]
        if not targets:
            self.skipTest('carta sorteada não causa dano')
        result = game.resolve_siege(encounter['force'], [], [], 0, targets)
        self.assertIn('Horta', result['damaged'])
        self.assertFalse(game.garden['active'])
        game.validate_snapshot()
        game.meal(); game.night_intentions(); game.next_day()
        with self.assertRaises(ValueError):
            game.plan_garden_work([STARTERS[0]])

    def test_save_load_and_old_saves(self):
        game = ready_garden()
        game.reserve_garden()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'c.json'
            game.save(path)
            self.assertEqual(Cistern02.load(path).garden, game.garden)
            payload = json.loads(path.read_text(encoding='utf-8'))
            for key in ('seeds', 'seeds_day', 'garden', 'garden_workers_plan'):
                payload['state'].pop(key)
            path.write_text(json.dumps(payload), encoding='utf-8')
            old = Cistern02.load(path)
            self.assertEqual((old.seeds, old.garden), (0, None))
        game.garden['work'] = 2  # obra concluída sem estrutura: inválido
        with self.assertRaises(ValueError):
            game.validate_snapshot()


class GardenControllerTests(unittest.TestCase):
    def test_garden_mode_builds_with_legal_resources(self):
        from campaign_player02 import CampaignPlayer02
        from simulate_cistern_sweep import auto_settings
        player = CampaignPlayer02.new_hn(10, 5)  # semente de ajuste (1–30)
        for key, value in auto_settings(5).items():
            setattr(player, key, value)
        player.garden = True
        report = player.attempt_cistern()
        cistern = player.game.cistern
        self.assertTrue(report['verified_victory'])
        self.assertEqual(cistern.rescue_history['ZC-MOR-0006'], 'welcome')
        self.assertTrue(cistern.garden['active'])
        self.assertIn('condomínio:Sementes:1', player.game.delivered_objectives)
        actions = [row['action'] for row in player.decisions]
        self.assertEqual(actions.count('garden_destination'), 1)
        self.assertIn('garden_reserve', actions)

    def test_garden_mode_is_off_by_default(self):
        from campaign_player02 import CampaignPlayer02
        self.assertFalse(CampaignPlayer02.new_hn(22, 2).garden)


def migrated_with_garden(active=True):
    player, _ = execute_cistern(22)
    cistern = player.game.cistern
    # fixture: Horta concluída na Cisterna (o replay da seed 22 não a constrói)
    cistern.garden = {'terrain': 8, 'work': 2, 'done': True, 'active': active,
                      'reserved_day': 3, 'completed_day': 4}
    if active:
        cistern.structures.append('Horta')
    player.game.transition_to_last_transmission()
    return player.game


def end_day(world):
    order = sorted(world.meal_people())
    return world.end_day({'food_priority': order, 'water_priority': order})


class RegionalGardenTests(unittest.TestCase):
    def test_migration_projects_only_active_garden(self):
        world = migrated_with_garden().world
        self.assertEqual(world.continuity_garden,
                         {'source': 'cistern02', 'active': True, 'output': 4, 'worker': None})
        self.assertIn('garden_archived', world.cistern_record['migration']['projection'])
        self.assertIsNone(migrated_with_garden(active=False).world.continuity_garden)

    def test_designated_worker_harvests_before_meal(self):
        world = migrated_with_garden().world
        adult = next(p['id'] for p in world.continuity_people if p['kind'] == 'adult')
        food = world.stock['food']
        world.assign_continuity_garden(adult)
        world.validate()  # civil designado não entra no registro de heróis/NPCs
        day = end_day(world)
        self.assertEqual(day['garden_food'], {'worker': adult, 'produced': 4, 'not_stored': 0})
        eaten = len(world.meal_people()) - day['missing']['food']
        self.assertEqual(world.stock['food'], food + 4 - eaten)
        self.assertIsNone(world.continuity_garden['worker'])
        self.assertNotIn('garden_food', end_day(world))  # sem trabalhador, sem colheita

    def test_hero_worker_cannot_leave_and_storage_is_respected(self):
        world = migrated_with_garden().world
        hero = sorted(world.heroes)[0]
        world.assign_continuity_garden(hero)
        with self.assertRaises(ValueError):
            world.assign_continuity_garden(sorted(world.heroes)[1])  # um por dia
        world.stock['water'] += world.storage - sum(world.stock.values())  # depósito cheio
        day = end_day(world)
        self.assertEqual(day['garden_food']['produced'] + day['garden_food']['not_stored'], 4)
        self.assertLess(day['garden_food']['produced'], 4)

    def test_save_load_and_invalid_garden(self):
        campaign = migrated_with_garden()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'c.json'
            campaign.save(path)
            reloaded = IntegratedCampaign.load(path).world
            self.assertEqual(reloaded.continuity_garden, campaign.world.continuity_garden)
        world = campaign.world
        world.continuity_garden['output'] = 8
        with self.assertRaises(ValueError):
            world.validate()
        fresh = World.new(1, sorted(world.heroes))
        fresh.continuity_garden = {'source': 'cistern02', 'active': True,
                                   'output': 4, 'worker': None}
        with self.assertRaises(ValueError):
            fresh.validate()  # sem Cisterna certificada não há Horta


if __name__ == '__main__':
    unittest.main()
