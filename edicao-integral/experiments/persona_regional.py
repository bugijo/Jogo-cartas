"""Mesas de personas jogando a Cisterna e, se vencem, 15 dias regionais.

Uso: python edicao-integral/experiments/persona_regional.py [--seeds 1-30]
     [--jobs 6] [--prototypes]

Mesmas mesas de `simulate_virtual_players.py` (faixas A, B, C e mista, 2–6
personas). No regional a mesa vota a cada amanhecer (`RegionalTablePlayer`).
`--prototypes` liga G, C2 e D no motor (F é decisão do grupo). Simulação, não
playtest; nada é gravado. 91–120 continuam reservadas.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import simulate_virtual_players as svp  # noqa: E402
from regional_table_player import RegionalTablePlayer  # noqa: E402
from virtual_players import TablePlayer  # noqa: E402

DAYS = 15


def _one(job):
    group, size, seed, prototypes = job
    personas = svp.table(group, size, seed)
    player = TablePlayer.for_table(seed, personas)
    if not player.attempt_cistern()['verified_victory']:
        return {'group': group, 'size': size, 'seed': seed, 'victory': False}
    campaign = player.game
    try:
        campaign.transition_to_last_transmission()
    except (ValueError, NotImplementedError):
        return {'group': group, 'size': size, 'seed': seed, 'victory': True,
                'migrated': False}
    world = campaign.world
    world.regional_travel_cards = True
    world.regional_filter_production = True
    if prototypes:
        world.enable_regional_prototypes('bridge', 'forage', 'garden_build')
    regional = RegionalTablePlayer(personas)
    end = regional.run(campaign, DAYS).world
    days = [d for d in regional.days if 'plan' in d]
    nights = [d['night'] for d in regional.days if d.get('night')]
    consumers = len(end.meal_people())
    policies = Counter(k for row in regional.table_log
                       for k, v in row['policy'].items() if v)
    return {
        'group': group, 'size': size, 'seed': seed, 'victory': True, 'migrated': True,
        'personas': [p.id for p in personas],
        'days': len(days), 'survived': not end.partial_defeat and len(days) == DAYS,
        'plans': dict(Counter(d['plan'] for d in days)),
        'missing_food': sum(n['missing']['food'] for n in nights),
        'consumer_nights': consumers * len(days),
        'clues': sum(r.get('action') == 'collect_regional_evidence' for r in end.log),
        'radio': bool(end.flags.get('radio_code')),
        'structures': sorted(end.structures),
        'regional_garden': any(r.get('action') == 'regional_garden_done' for r in end.log),
        'conflicts': sum(len(r['conflicts']) for r in regional.table_log),
        'leader_agreement': round(sum(r['leader_agreement'] for r in regional.table_log)
                                  / max(1, len(regional.table_log)), 3),
        'pressure_days': sum(r['pressure'] for r in regional.table_log),
        'policy_days': dict(policies),
        'votes': len(regional.table_log),
    }


def summarize(rows):
    out = {}
    buckets = defaultdict(list)
    for row in rows:
        buckets[row['group']].append(row)
    for group, items in sorted(buckets.items()):
        mig = [r for r in items if r.get('migrated')]
        n = len(mig) or 1
        votes = sum(r['votes'] for r in mig) or 1
        policy = sum((Counter(r['policy_days']) for r in mig), Counter())
        plans = sum((Counter(r['plans']) for r in mig), Counter())
        out[group] = {
            'tables': len(items), 'cistern_victories': sum(r['victory'] for r in items),
            'migrated': len(mig), 'survived_15': sum(r['survived'] for r in mig),
            'mean_days': round(sum(r['days'] for r in mig) / n, 2),
            'shortage': round(sum(r['missing_food'] for r in mig)
                              / max(1, sum(r['consumer_nights'] for r in mig)), 3),
            'clues': sum(r['clues'] for r in mig), 'radio': sum(r['radio'] for r in mig),
            'structures': sum(len(r['structures']) for r in mig),
            'regional_gardens': sum(r['regional_garden'] for r in mig),
            'plan_share': {k: round(v / max(1, sum(plans.values())), 2)
                           for k, v in sorted(plans.items())},
            'policy_share': {k: round(v / votes, 2) for k, v in sorted(policy.items())},
            'conflicts_per_table': round(sum(r['conflicts'] for r in mig) / n, 2),
            'leader_agreement': round(sum(r['leader_agreement'] for r in mig) / n, 3),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', default='1-30')
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--prototypes', action='store_true')
    args = parser.parse_args()
    start, stop = map(int, args.seeds.split('-'))
    if start <= 120 and stop >= 91:
        raise SystemExit('Sementes 91–120 reservadas para a validação cega final')
    jobs = [(g, s, seed, args.prototypes) for g in svp.GROUPS for s in svp.SIZES
            for seed in range(start, stop + 1)]
    with Pool(args.jobs) as pool:
        rows = pool.map(_one, jobs, chunksize=2)
    print(json.dumps({'seeds': [start, stop], 'prototypes': args.prototypes,
                      'summary': summarize(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
