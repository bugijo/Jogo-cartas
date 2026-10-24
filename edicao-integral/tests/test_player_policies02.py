import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cistern02 import LINK_IDS, STARTERS
from integrated_campaign import IntegratedCampaign
from player_policies02 import PROFILES, ProgrammedPlayer


class Policies02Tests(unittest.TestCase):
    def test_eight_profiles_make_reproducible_public_opening_choices(self):
        self.assertEqual(len(PROFILES), 8)
        for count in range(2, 7):
            for name in PROFILES:
                with self.subTest(count=count, name=name):
                    game = IntegratedCampaign.new(112, STARTERS[:count], LINK_IDS[:count])
                    player = ProgrammedPlayer(name, 998)
                    decision = player.choose_expedition(game)
                    self.assertEqual(decision, ProgrammedPlayer(name, 998).choose_expedition(game))
                    self.assertTrue(set(decision.args[1]).issubset(set(game.founders)))
                    destination, team, route = decision.args
                    self.assertIn(destination, {'Mercado','Hospital','Oficina',
                                                'Posto','Condomínio','Estação'})
                    self.assertIn(route, {'short','long'})

    def test_policy_excludes_incapacitated_and_uses_memory(self):
        game = IntegratedCampaign.new(113, STARTERS[:3], LINK_IDS[:3])
        game.cistern.people[0]['wounds'] = 3
        player = ProgrammedPlayer('Explorador', 9)
        decision = player.choose_expedition(game)
        self.assertNotIn(STARTERS[0], decision.args[1])
        self.assertEqual(len(player.history), 1)
        self.assertEqual(player.history[0].reason, decision.reason)

    def test_local_choice_is_executable_without_hidden_information(self):
        game = IntegratedCampaign.new(114, STARTERS[:2], LINK_IDS[:2])
        tactical = game._start_tactical_fixture('Mercado', [STARTERS[0]], 'long')
        player = ProgrammedPlayer('Iniciante', 9)
        action = player.choose_local(tactical)
        self.assertIn(action.kind, {'move', 'open_door', 'end_round', 'return'})
        if action.kind == 'move': tactical.move(*action.args)
        elif action.kind == 'open_door': tactical.open_door(*action.args)
        elif action.kind == 'end_round': tactical.end_round()
        else: game.return_expedition()


if __name__ == '__main__': unittest.main()
