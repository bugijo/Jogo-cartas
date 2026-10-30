"""Controlador regional estratégico (experimental; não muda regras)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from regional_campaign_player import (MARKET, STATION, RegionalCampaignPlayer,
                                      StrategicRegionalPlayer)
from verify_campaign_player02 import execute as execute_cistern


def regional_world():
    player, _ = execute_cistern(22)
    player.game.transition_to_last_transmission()
    world = player.game.world
    world.regional_travel_cards = True
    world.regional_filter_production = True
    return world


def heal(world):
    for state in world.heroes.values():  # fixture: equipe apta para ir longe
        state.update(health=3, wounds=0, fatigue=0, hungry=False, thirsty=False)


class StrategicPlanTests(unittest.TestCase):
    def setUp(self):
        self.world = regional_world()
        heal(self.world)
        self.consumers = len(self.world.meal_people())

    def test_covered_night_goes_for_clue_instead_of_food_loop(self):
        world = self.world
        world.stock['food'] = self.consumers  # cobre só esta noite
        if StrategicRegionalPlayer().next_clue(world) is None:
            self.skipTest('sem contato disponível nesta semente')
        self.assertEqual(RegionalCampaignPlayer().plan(world)[0], 'supply')
        kind, destination, _, _ = StrategicRegionalPlayer().plan(world)
        self.assertEqual((kind, destination), ('clue', STATION))

    def test_uncovered_night_supplies_proportionally(self):
        world = self.world
        world.stock['food'] = 0
        kind, destination, _, objectives = StrategicRegionalPlayer().plan(world)
        self.assertEqual((kind, destination), ('supply', MARKET))
        food = 2  # carta do Mercado
        expected = min(world.searches[MARKET], 4, -(-2 * self.consumers // food))
        self.assertEqual(sum(o['searches'] for o in objectives), expected)

    def test_short_risk_accepts_one_short_night_only_without_streak(self):
        world = self.world
        world.stock['food'] = 0
        player = StrategicRegionalPlayer(risk='short')
        if player.next_clue(world) is None:
            self.skipTest('sem contato disponível nesta semente')
        self.assertEqual(player.plan(world)[0], 'clue')
        next(iter(world.meal_people().values()))['streak'] = 1
        self.assertEqual(player.plan(world)[0], 'supply')

    def test_far_team_leaves_unfit_heroes_home(self):
        world = self.world
        hero = sorted(world.heroes)[0]
        world.heroes[hero]['health'] = 1
        team = StrategicRegionalPlayer.far_team(world)
        self.assertNotIn(hero, team)
        self.assertTrue(all(world.heroes[h]['health'] >= 2 for h in team))


if __name__ == '__main__':
    unittest.main()
