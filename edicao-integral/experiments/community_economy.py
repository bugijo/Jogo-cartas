"""Simulações da Comunidade (Missão Mestre): antes × depois, por cenário.

Uso: python edicao-integral/experiments/community_economy.py --seeds 1-30
     [--configs BASE,STRAT,COMM,...] [--jobs 6] [--json saida.json]

Fluxo de cada partida: A Cisterna com o controlador publicado (modo Horta H1),
migração (com `community=True` nos cenários COMM*), 15 dias regionais com
cartas de Viagem e filtro ligados. Nada é gravado em `replays/`.
Sementes: 1–30 ajuste; 31–90 confirmação; 91–120 reservadas (não usar).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from campaign_player02 import CampaignPlayer02  # noqa: E402
from community_player import CommunityRegionalPlayer  # noqa: E402
from regional_campaign_player import (RegionalCampaignPlayer,  # noqa: E402
                                      StrategicRegionalPlayer)
from simulate_cistern_sweep import auto_settings  # noqa: E402

DAYS = 15
SIZES = (2, 3, 4, 5, 6)
# nome: (controlador, regras Comunidade, opções do controlador)
CONFIGS = {
    'BASE': (RegionalCampaignPlayer, False, {}),
    'STRAT': (StrategicRegionalPlayer, False, {'risk': 'short'}),
    'COMM': (CommunityRegionalPlayer, True, {}),
    'COMM-NOTRIP': (CommunityRegionalPlayer, True, {'trips': False}),
    'COMM-1DAY': (CommunityRegionalPlayer, True, {'max_days': 1}),
    'COMM-HEROTRIP': (CommunityRegionalPlayer, True, {}),
    'COMM-HEROTRIP-G': (CommunityRegionalPlayer, True,
                        {'options': ('priority', 'build', 'bridge')}),
    'COMM-G': (CommunityRegionalPlayer, True, {'options': ('priority', 'build', 'bridge')}),
    'COMM-SHORT': (CommunityRegionalPlayer, True, {'risk': 'short'}),
    'COMM-NOBUILD': (CommunityRegionalPlayer, True, {'options': ('priority',),
                                                      'community_builds': ()}),
}


def _counting(cls):
    """Registra o número de consumidores de cada noite (plano de refeição)."""
    class Counting(cls):
        def meal_plan(self, world):
            plan = super().meal_plan(world)
            self.consumer_counts.append(len(plan['food_priority']))
            return plan

        def run(self, campaign, days, save_dir=None):
            self.consumer_counts = []
            return super().run(campaign, days, save_dir)
    return Counting


def run_one(args):
    config, size, seed = args
    cls, community_on, options = CONFIGS[config]
    import community
    community.TRIPS['heroes_allowed'] = config.startswith('COMM-HEROTRIP')  # só em memória
    player = CampaignPlayer02.new_hn(seed, size)
    for key, value in auto_settings(size).items():
        setattr(player, key, value)
    player.garden = True
    if not player.attempt_cistern()['verified_victory']:
        return None
    campaign = player.game
    try:
        campaign.transition_to_last_transmission(community=community_on)
    except ValueError as exc:
        return {'config': config, 'size': size, 'seed': seed,
                'outcome': 'migration_refused', 'reason': str(exc)[:80]}
    world = campaign.world
    world.regional_travel_cards = True
    world.regional_filter_production = True
    if 'bridge' in options.get('options', ()):
        world.enable_regional_prototypes('bridge')  # G: protótipo não aprovado
    regional = _counting(cls)(discard_water=True, **options)
    campaign = regional.run(campaign, DAYS)
    world = campaign.world
    nights = [row for row in world.log if 'missing' in row and 'stock' in row]
    consumers = [len(row['unfed']['food']) for row in nights]
    plans = Counter(day.get('plan') for day in regional.days if 'plan' in day)
    played = sum(1 for day in regional.days if 'plan' in day)
    returns = [row for row in world.log if row.get('action') == 'worker_trip_return']
    trip_gain = Counter()
    for row in returns:
        for key, value in row['delivered'].items():
            if key in ('food', 'water', 'wood', 'scrap', 'meat'):
                trip_gain[key] += value
    food_missing = sum(row['missing']['food'] for row in nights)
    water_missing = sum(row['missing']['water'] for row in nights)
    counts = regional.consumer_counts[:len(nights)]
    people_nights = sum(counts)
    stock_days = [row['stock']['food'] / max(1, n) for row, n in zip(nights, counts)]
    water_days = [row['stock']['water'] / max(1, n) for row, n in zip(nights, counts)]
    community = world.community or {}
    survived = not world.partial_defeat and played == DAYS
    return {
        'config': config, 'size': size, 'seed': seed,
        'outcome': 'survived' if survived else ('partial_defeat' if world.partial_defeat
                                                else 'stopped'),
        'days': played,
        'food_missing': food_missing, 'water_missing': water_missing,
        'people_nights': people_nights,
        'nights_short': sum(row['missing']['food'] > 0 for row in nights),
        'food_stock_days': round(sum(stock_days) / len(stock_days), 2) if stock_days else 0,
        'water_stock_days': round(sum(water_days) / len(water_days), 2) if water_days else 0,
        'clues': world.clues, 'radio': bool(world.flags.get('radio_code')),
        'access_card': bool(world.flags.get('access_card')),
        'structures': sorted(world.structures) + sorted(community.get('built', [])),
        'market_days': plans.get('supply', 0), 'clue_days': plans.get('clue', 0)
        + plans.get('access_card', 0), 'rest_days': plans.get('rest', 0),
        'trips': len(returns), 'trip_gain': dict(trip_gain),
        'trip_wounds': sum(bool(row['effects'].get('ferimento'))
                           or row['effects'].get('zumbis', 9) <= 2 for row in returns),
        'workers_incapacitated': sum(p.get('wounds', 0) >= 3 for p in world.continuity_people
                                     if p['kind'] == 'adult'),
        'blockers': sorted({row['code'] for row in regional.blockers}),
    }


def summarize(rows):
    out = {}
    for config in dict.fromkeys(r['config'] for r in rows):
        group = [r for r in rows if r['config'] == config]
        migrated = [r for r in group if r['outcome'] != 'migration_refused']
        surv = [r for r in migrated if r['outcome'] == 'survived']
        pn = sum(r['people_nights'] for r in surv) or 1
        out[config] = {
            'victories_cistern': len(group),
            'migration_refused': len(group) - len(migrated),
            'migrated': len(migrated), 'survived': len(surv),
            'survival_rate': round(len(surv) / len(migrated), 3) if migrated else 0,
            'mean_days': round(sum(r['days'] for r in migrated) / max(1, len(migrated)), 2),
            'hunger_in_survivors': round(sum(r['food_missing'] for r in surv) / pn, 3),
            'radio_all': sum(r['radio'] for r in migrated),
            'radio_survivors': sum(r['radio'] for r in surv),
            'clues_mean': round(sum(r['clues'] for r in migrated) / max(1, len(migrated)), 2),
            'structures_mean': round(sum(len(r['structures']) for r in migrated)
                                     / max(1, len(migrated)), 2),
            'market_day_share': round(sum(r['market_days'] for r in migrated)
                                      / max(1, sum(r['days'] for r in migrated)), 3),
            'trips': sum(r['trips'] for r in migrated),
            'trip_gain': dict(sum((Counter(r['trip_gain']) for r in migrated), Counter())),
            'trip_wounds': sum(r['trip_wounds'] for r in migrated),
            'by_size': {s: f"{sum(r['outcome']=='survived' for r in migrated if r['size']==s)}/"
                           f"{sum(r['size']==s for r in migrated)}" for s in SIZES},
            'blockers': dict(Counter(b for r in migrated for b in r['blockers'])),
        }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', default='1-30')
    parser.add_argument('--configs', default='BASE,STRAT,COMM')
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--json')
    args = parser.parse_args()
    first, last = map(int, args.seeds.split('-'))
    if last >= 91:
        raise SystemExit('Sementes 91–120 reservadas para a validação cega final')
    tasks = [(c, s, seed) for c in args.configs.split(',') for s in SIZES
             for seed in range(first, last + 1)]
    with Pool(args.jobs) as pool:
        rows = [r for r in pool.map(run_one, tasks) if r is not None]
    summary = summarize(rows)
    for config, data in summary.items():
        print(config, json.dumps(data, ensure_ascii=False))
    if args.json:
        Path(args.json).write_text(json.dumps({'seeds': [first, last], 'summary': summary,
                                               'rows': rows}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
