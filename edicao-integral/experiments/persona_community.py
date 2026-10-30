"""D-06: as 18 personas jogam a Comunidade no regional e avaliam (simulado).

Uso: python edicao-integral/experiments/persona_community.py --seeds 1-10 [--jobs 6]
     [--json saida.json] [--md edicao-integral/AVALIACOES_PERSONAS.md]

A Cisterna é jogada pelo controlador publicado (as personas não mudam o arco 1
aqui); a cada amanhecer regional a mesa vota (`regional_policy`, peso por
assertividade) e o voto ajusta `CommunityRegionalPlayer`. Erros de leitura são
simulados pela compreensão do líder do dia: ele esquece a carne no fogo ou
manda uma caçada de 1 dia (jogadas legais, só piores). As avaliações de 10
perguntas são **geradas das decisões e números registrados**, não opiniões
humanas. Sementes 91–120 reservadas.
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import community  # noqa: E402
from campaign_player02 import CampaignPlayer02  # noqa: E402
from community_player import CommunityRegionalPlayer  # noqa: E402
from regional_table_player import regional_policy  # noqa: E402
from simulate_cistern_sweep import auto_settings  # noqa: E402
from simulate_virtual_players import GROUPS, SIZES, table  # noqa: E402
from virtual_players import BY_ID, PERSONAS  # noqa: E402

DAYS = 15


class PersonaCommunityPlayer(CommunityRegionalPlayer):
    """A mesa decide; o controlador executa só o que a mesa votou."""

    def __init__(self, personas, seed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personas = list(personas)
        self.seed = seed
        self.table_log, self.mistakes = [], []
        self._slip = None

    @staticmethod
    def pressure(world):
        people = world.meal_people()
        return (world.stock['food'] < len(people)
                or any(p.get('streak', 0) for p in people.values())
                or any(h['health'] <= 1 for h in world.heroes.values()))

    def plan(self, world):
        vote = regional_policy(self.personas, self.pressure(world))
        policy = vote['policy']
        self.risk = 'short' if policy['risk_short'] or policy['progress_first'] else 'covered'
        self.food_days = 3 if policy['reserve_3_days'] else (2 if policy['forage'] else 1)
        self.options = {'priority', 'build'} if policy['invest'] else {'priority'}
        self.community_builds = (('canteiro', 'coletor', 'canteiro', 'cozinha')
                                 if policy['invest'] else ())
        leader = BY_ID[vote['leader']]
        rng = Random(zlib.crc32(f'{self.seed}:{leader.id}:{world.day}'.encode()))
        self._slip = None
        if rng.random() > leader.comprehension:
            self._slip = rng.choice(('esqueceu_carne', 'caca_1_dia'))
            self.mistakes.append({'day': world.day, 'persona': leader.id, 'slip': self._slip})
        self.table_log.append({'day': world.day, **vote})
        return super().plan(world)

    def camp_work(self, world, kind, team):
        if self._slip == 'esqueceu_carne' and world.community and world.community['meat']:
            meat = world.community['meat']
            world.community['meat'] = []          # ninguém foi cozinhar hoje
            done = super().camp_work(world, kind, team)
            world.community['meat'] = meat + world.community['meat']
            return done
        return super().camp_work(world, kind, team)

    def _food_activity(self, world, person, days, planned):
        activity, days = super()._food_activity(world, person, days, planned)
        if self._slip == 'caca_1_dia' and activity and world.community['pools']['caca']:
            return 'caca', 1                       # leitura errada do rendimento
        return activity, days


def run_one(args):
    group, size, seed = args
    personas = table(group, size, seed)
    player = CampaignPlayer02.new_hn(seed, size)
    for key, value in auto_settings(size).items():
        setattr(player, key, value)
    player.garden = True
    if not player.attempt_cistern()['verified_victory']:
        return None
    campaign = player.game
    campaign.transition_to_last_transmission(community=True)
    campaign.world.regional_travel_cards = True
    campaign.world.regional_filter_production = True
    regional = PersonaCommunityPlayer(personas, seed, discard_water=True)
    campaign = regional.run(campaign, DAYS)
    world = campaign.world
    days = [d for d in regional.days if 'plan' in d]
    nights = [row for row in world.log if 'missing' in row and 'stock' in row]
    trips = [r for r in world.log if r.get('action') == 'worker_trip_return']
    conflicts = defaultdict(int)
    for row in regional.table_log:
        for c in row['conflicts']:
            conflicts[c['persona']] += 1
    plans = [d['plan'] for d in days]
    return {
        'group': group, 'size': size, 'seed': seed, 'personas': [p.id for p in personas],
        'survived': not world.partial_defeat and len(days) == DAYS, 'days': len(days),
        'hunger_nights': sum(n['missing']['food'] > 0 for n in nights),
        'food_missing': sum(n['missing']['food'] for n in nights),
        'radio': bool(world.flags.get('radio_code')), 'clues': world.clues,
        'structures': len(world.structures) + len((world.community or {}).get('built', [])),
        'market_days': plans.count('supply'), 'rest_days': plans.count('rest'),
        'clue_days': plans.count('clue') + plans.count('access_card'),
        'trips': len(trips), 'trip_wounds': sum(bool(r['effects'].get('ferimento')) for r in trips),
        'leaders': [row['leader'] for row in regional.table_log],
        'conflicts': dict(conflicts), 'mistakes': len(regional.mistakes),
        'repeated_plan_share': round(max(plans.count(p) for p in set(plans)) / len(plans), 2)
        if plans else 0,
    }


def evaluate(persona, rows):
    """10 respostas geradas dos números das mesas em que a persona jogou."""
    n = len(rows)
    surv = sum(r['survived'] for r in rows)
    hunger = sum(r['hunger_nights'] for r in rows) / max(1, sum(r['days'] for r in rows))
    radio = sum(r['radio'] for r in rows)
    led = sum(r['leaders'].count(persona.id) for r in rows)
    total_days = sum(len(r['leaders']) for r in rows) or 1
    conflicts = sum(r['conflicts'].get(persona.id, 0) for r in rows)
    repeat = sum(r['repeated_plan_share'] for r in rows) / max(1, n)
    builds = sum(r['structures'] for r in rows) / max(1, n)
    trips = sum(r['trips'] for r in rows) / max(1, n)
    wounds = sum(r['trip_wounds'] for r in rows) / max(1, n)
    mistakes = sum(r['mistakes'] for r in rows) / max(1, n)
    wants = ('construções' if persona.planning >= 0.6 else
             'exploração' if persona.exploration >= 0.6 else
             'proteger o grupo' if persona.cooperation >= 0.7 else 'ação rápida')
    return {
        'persona': persona.id, 'grupo': persona.group, 'mesas': n,
        '1_funcionou': f'sobreviveu em {surv}/{n} mesas; rádio em {radio}; '
                       f'{builds:.1f} estruturas por mesa',
        '2_dificil_entender': f'{mistakes:.1f} leituras erradas por mesa (carne esquecida, caça de 1 dia)',
        '3_interessante': f'{trips:.0f} viagens automáticas por mesa; foco preferido: {wants}',
        '4_repetitivo': f'mesmo plano em {repeat:.0%} dos dias (descanso + viagens)',
        '5_injusto': f'{wounds:.1f} ferimentos em viagem por mesa; fome em {hunger:.0%} das noites',
        '6_decisoes_importantes': f'liderou {led} de {total_days} amanheceres; '
                                  'reserva de comida, obras e risco da pista',
        '7_alternativas': f'{conflicts} discordâncias abertas com a mesa',
        '8_lento': 'amanheceres com 4–8 viagens para resolver de uma vez' if trips > 40
                   else 'sem gargalo registrado',
        '9_mudaria': ('menos fome crônica no fim' if hunger > 0.3 else
                      'menos dias repetidos' if repeat > 0.6 else 'manter'),
        '10_jogaria_de_novo': ('provável (números: venceu a maioria)' if surv * 2 >= n
                               else 'incerto (números: perdeu a maioria)'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', default='1-10')
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--json')
    parser.add_argument('--md')
    args = parser.parse_args()
    first, last = map(int, args.seeds.split('-'))
    if last >= 91:
        raise SystemExit('Sementes 91–120 reservadas')
    tasks = [(g, s, seed) for g in GROUPS for s in SIZES for seed in range(first, last + 1)]
    with Pool(args.jobs) as pool:
        rows = [r for r in pool.map(run_one, tasks) if r is not None]
    groups = {}
    for g in GROUPS:
        grp = [r for r in rows if r['group'] == g]
        groups[g] = {'mesas': len(grp), 'sobrevivem': sum(r['survived'] for r in grp),
                     'radio': sum(r['radio'] for r in grp),
                     'fome_noites': round(sum(r['hunger_nights'] for r in grp)
                                          / max(1, sum(r['days'] for r in grp)), 3),
                     'estruturas': round(sum(r['structures'] for r in grp) / max(1, len(grp)), 2),
                     'erros_mesa': round(sum(r['mistakes'] for r in grp) / max(1, len(grp)), 2)}
        print(g, json.dumps(groups[g], ensure_ascii=False))
    evaluations = [evaluate(p, [r for r in rows if p.id in r['personas']]) for p in PERSONAS]
    if args.json:
        Path(args.json).write_text(json.dumps({'groups': groups, 'evaluations': evaluations,
                                               'rows': rows}, ensure_ascii=False, indent=1))
    if args.md:
        lines = [f'# Avaliações simuladas das 18 personas — Comunidade (sementes {first}–{last})',
                 '', 'Geradas por `experiments/persona_community.py` a partir das decisões e '
                 'números registrados. **Não são opiniões humanas.**', '',
                 '| Grupo | Mesas | Sobrevivem | Rádio | Noites com fome | Estruturas/mesa | Erros de leitura/mesa |',
                 '|---|---|---|---|---|---|---|']
        for g, d in groups.items():
            lines.append(f"| {g} | {d['mesas']} | {d['sobrevivem']} | {d['radio']} | "
                         f"{d['fome_noites']:.0%} | {d['estruturas']} | {d['erros_mesa']} |")
        for ev in evaluations:
            lines += ['', f"## {ev['persona']} (grupo {ev['grupo']}, {ev['mesas']} mesas)", '']
            for key, value in ev.items():
                if key[0].isdigit():
                    lines.append(f"- **{key.split('_', 1)[1].replace('_', ' ')}**: {value}")
        Path(args.md).write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
