#!/usr/bin/env python3
"""Mesas de jogadores virtuais na Cisterna (e no regional, se vencem).

Mesas da mesma faixa (A, B, C) e mistas, de 2 a 6 personas. Sem `--write`,
compara com o artefato registrado. Resultados são simulação, não playtest.

    simulate_virtual_players.py --seeds 1-3 --write    # piloto
    simulate_virtual_players.py --seeds 1-30 --write   # ampliação
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from random import Random

from regional_campaign_player import RegionalCampaignPlayer
from virtual_players import PERSONAS, TablePlayer

REPLAYS = Path(__file__).resolve().parent / 'replays'


def artifact(seeds: range) -> Path:
    return REPLAYS / f'virtual_players_seeds{seeds.start}-{seeds.stop - 1}.json'
GROUPS = ('A', 'B', 'C', 'mista')
SIZES = range(2, 7)
REGIONAL_DAYS = 15


def table(group: str, size: int, seed: int) -> list:
    rng = Random(seed * 1000 + size * 10 + GROUPS.index(group))
    if group != 'mista':
        return rng.sample([p for p in PERSONAS if p.group == group], size)
    picks = [rng.choice([p for p in PERSONAS if p.group == g]) for g in 'ABC'][:size]
    rest = [p for p in PERSONAS if p not in picks]
    return picks + rng.sample(rest, size - len(picks))


def regional_days(player: TablePlayer) -> int | None:
    campaign = player.game
    try:
        campaign.transition_to_last_transmission()
    except (ValueError, NotImplementedError):
        return None
    campaign.world.regional_travel_cards = True
    campaign.world.regional_filter_production = True
    regional = RegionalCampaignPlayer()
    result = regional.run(campaign, REGIONAL_DAYS)
    return result.world.day - 1 if result.world.partial_defeat else result.world.day


def run_one(group: str, size: int, seed: int, regional: bool = True) -> dict:
    personas = table(group, size, seed)
    player = TablePlayer.for_table(seed, personas)
    cistern = player.game.cistern
    start = {'food': sum(cistern.food), 'water': sum(cistern.water)}
    report = player.attempt_cistern()
    heroes = player.hero_of()
    acts = Counter(row['hero'] for row in player.decisions if row.get('hero') in heroes)
    total = sum(acts.values()) or 1
    people = {p['id']: p for p in cistern.people}
    rules = Counter(row['outcome'] for row in player.rule_log)
    conflicts = [c for row in player.table_log for c in row['conflicts']]
    row = {
        'group': group, 'size': size, 'seed': seed,
        'personas': [p.id for p in personas],
        'scripted': player.scripted,
        'leader': player.table_log[-1]['leader'],
        'leader_agreement': round(sum(r['leader_agreement'] for r in player.table_log)
                                  / len(player.table_log), 3),
        'victory': report['verified_victory'],
        'nights': report['nights_completed'],
        'expeditions': sum(day['destination'] is not None for day in report['days']),
        'emergencies': sum(day['tactical_outcome'].startswith('emergency')
                           for day in report['days']),
        'hero_wounds': sum(people[h]['wounds'] for h in heroes),
        'incapacitated': sum(people[h]['wounds'] >= 3 for h in heroes),
        'food': {'start': start['food'], 'end': sum(cistern.food)},
        'water': {'start': start['water'], 'end': sum(cistern.water)},
        'participation': {heroes[h]: round(acts[h] / total, 3) for h in heroes},
        'conflicts': len(conflicts),
        'conflict_topics': dict(Counter(c['topic'] for c in conflicts)),
        'rule_errors': rules.get('refused_by_engine', 0),
        'rule_misread_legal': rules.get('accepted', 0),
        'pressure_days': sum(r['pressure'] for r in player.table_log if r['day']),
    }
    if regional and row['victory']:
        row['regional_days'] = regional_days(player)
    return row


def summarize(rows: list[dict]) -> dict:
    out = {}
    buckets = defaultdict(list)
    for row in rows:
        buckets[row['group']].append(row)
    for group, items in buckets.items():
        n = len(items)
        top = [max(r['participation'].values()) for r in items]
        regional = [r['regional_days'] for r in items if r.get('regional_days') is not None]
        out[group] = {
            'tables': n,
            'victories': sum(r['victory'] for r in items),
            'scripted_tables': sum(r['scripted'] for r in items),
            'mean_nights': round(sum(r['nights'] for r in items) / n, 2),
            'emergencies': sum(r['emergencies'] for r in items),
            'hero_wounds': sum(r['hero_wounds'] for r in items),
            'incapacitated': sum(r['incapacitated'] for r in items),
            'rule_errors_per_table': round(sum(r['rule_errors'] for r in items) / n, 2),
            'conflicts_per_table': round(sum(r['conflicts'] for r in items) / n, 2),
            'leader_agreement': round(sum(r['leader_agreement'] for r in items) / n, 3),
            'top_participation': round(sum(top) / n, 3),
            'regional_mean_days': round(sum(regional) / len(regional), 2) if regional else None,
        }
    return out


def parse_seeds(text: str) -> range:
    first, _, last = text.partition('-')
    return range(int(first), int(last or first) + 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--seeds', default='1-3')
    parser.add_argument('--no-regional', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    seeds = parse_seeds(args.seeds)
    rows = [run_one(group, size, seed, regional=not args.no_regional)
            for group in GROUPS for size in SIZES for seed in seeds]
    payload = {'schema': 1, 'kind': 'simulação automatizada (não é playtest humano)',
               'seeds': [seeds.start, seeds.stop - 1], 'regional': not args.no_regional,
               'summary': summarize(rows), 'tables': rows}
    text = json.dumps(payload, ensure_ascii=False, indent=1) + '\n'
    path = artifact(seeds)
    if args.write:
        path.write_text(text, encoding='utf-8')
    elif path.exists():
        recorded = json.loads(path.read_text(encoding='utf-8'))
        if recorded != json.loads(text):
            print('virtual players: divergiu do artefato registrado', file=sys.stderr)
            return 1
    for group, data in payload['summary'].items():
        print(group, json.dumps(data, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
