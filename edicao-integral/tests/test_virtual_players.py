"""Escritório Dev, barra de progresso e jogadores virtuais."""
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import progress
import virtual_players as vp
from campaign_player02 import CampaignPlayer02
from dev_office import SPECIALISTS, route
from simulate_cistern_sweep import auto_settings
from simulate_virtual_players import run_one, table

REFERENCE = {'adaptive': True, 'far_first': False, 'cautious': True, 'retreat': True,
             'escort': True, 'support': True, 'collection': True, 'whole_team': True}


class OfficeTests(unittest.TestCase):
    def test_ten_specialists_with_verifiable_contract(self):
        self.assertEqual(len(SPECIALISTS), 10)
        for role in SPECIALISTS.values():
            for key in ('title', 'responsibilities', 'acceptance', 'deliverables', 'keywords'):
                self.assertTrue(role[key], key)

    def test_route_always_includes_director(self):
        self.assertEqual(route('ajustar baralho de busca')[0], 'diretor')
        self.assertIn('card_games', route('ajustar baralho de busca'))


class ProgressTests(unittest.TestCase):
    def test_percent_comes_from_weights_with_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'progress.json'
            with mock.patch.object(progress, 'STATE', state):
                progress.main(['start', 'T', '--specialist', 'qa',
                               '--criteria', 'a:A:30', 'b:B:70'])
                progress.main(['done', 'b', '--evidence', 'teste'])
                data = json.loads(state.read_text(encoding='utf-8'))
                self.assertEqual(progress.percent(data), 70)
                self.assertEqual(data['specialist'], 'QA de Jogos')
                with self.assertRaises(SystemExit):
                    progress.main(['done', 'x', '--evidence', 'nada'])
                with self.assertRaises(SystemExit):  # sem evidência não conta
                    progress.main(['done', 'a'])


class PersonaTests(unittest.TestCase):
    def test_eighteen_distinct_personas_in_three_groups(self):
        self.assertEqual(len(vp.PERSONAS), 18)
        for group in 'ABC':
            self.assertEqual(sum(p.group == group for p in vp.PERSONAS), 6)
        traits = {tuple(getattr(p, t) for t in vp.TRAITS) for p in vp.PERSONAS}
        self.assertEqual(len(traits), 18)
        prefs = {tuple(sorted(p.preferences(False).items())) for p in vp.PERSONAS}
        self.assertGreaterEqual(len(prefs), 10)

    def test_leader_is_most_assertive_and_cooperative_players_do_not_argue(self):
        personas = [vp.BY_ID[i] for i in ('A13', 'B21', 'C55')]
        vote = vp.table_policy(personas)
        self.assertEqual(vote['leader'], 'B21')
        self.assertNotIn('C55', {c['persona'] for c in vote['conflicts']})

    def test_reference_policy_reproduces_reference_controller(self):
        with mock.patch.object(vp, 'table_policy', lambda ps, pressure=False: {
                'policy': dict(REFERENCE), 'leader': ps[0].id,
                'leader_agreement': 1.0, 'conflicts': []}):
            for size, seed in ((2, 22), (4, 3)):
                table_player = vp.TablePlayer.for_table(seed, list(vp.PERSONAS[:size]))
                ours = table_player.attempt_cistern()
                base = CampaignPlayer02.new_hn(seed, size)
                for key, value in auto_settings(size).items():
                    setattr(base, key, value)
                theirs = base.attempt_cistern()
                self.assertEqual(ours['verified_victory'], theirs['verified_victory'])
                self.assertEqual(ours['decision_count'], theirs['decision_count'])

    def test_rule_probe_never_changes_the_game(self):
        player = vp.TablePlayer.for_table(5, [vp.BY_ID['C70'], vp.BY_ID['A13']])
        before = deepcopy(player.game.__dict__)
        for day in range(1, 6):
            player._probe_rules(day)
        self.assertEqual(player.game.__dict__.keys(), before.keys())
        self.assertEqual(player.game.cistern, before['cistern'])
        self.assertTrue(player.rule_log)
        self.assertTrue(all(row['outcome'] == 'refused_by_engine' for row in player.rule_log))

    def test_tables_and_runs_are_deterministic(self):
        self.assertEqual(table('mista', 4, 7), table('mista', 4, 7))
        self.assertEqual({p.group for p in table('mista', 3, 1)}, {'A', 'B', 'C'})
        self.assertEqual(run_one('C', 3, 2, regional=False), run_one('C', 3, 2, regional=False))


if __name__ == '__main__':
    unittest.main()
