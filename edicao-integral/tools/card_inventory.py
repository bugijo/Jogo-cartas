#!/usr/bin/env python3
"""Inventário de componentes da edição integral (Cisterna 0.2 + regional + Comunidade).

Conta tudo a partir dos dados do motor e do catálogo 0.2 (nada digitado à mão)
e confere coerência: baralhos da Comunidade batem com `data/community.json`,
estruturas e heróis batem com `data/system.json`, carne física cobre a trilha.

    python edicao-integral/tools/card_inventory.py           # confere e imprime
    python edicao-integral/tools/card_inventory.py --write   # grava data/print_inventory.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITION = ROOT / 'edicao-integral'
OUT = EDITION / 'data' / 'print_inventory.json'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def inventory() -> dict:
    catalog = load(ROOT / 'content/catalog.json')
    system = load(EDITION / 'data/system.json')
    community = load(EDITION / 'data/community.json')
    tactics = load(EDITION / 'data/tactics.json')
    last = load(EDITION / 'data/last_transmission.json')
    families = Counter(card['family'] for card in catalog['cards'])
    meat_cards = sum(card['family'] == 'REC' and card['name'] == 'Carne'
                     for card in catalog['cards'])
    decks = {
        # Cisterna 0.2: reaproveitado sem mudança (certificado).
        'cisterna_0.2': {'source': 'content/catalog.json', 'cards': dict(families),
                         'total': sum(families.values())},
        # Regional + Comunidade: cartas novas da edição integral.
        'acontecimentos_viagem': {'source': 'data/community.json#event_deck',
                                  'cards': dict(Counter(community['event_deck'])),
                                  'total': len(community['event_deck'])},
        'profissoes': {'source': 'data/community.json#profession_deck',
                       'cards': dict(Counter(community['profession_deck'])),
                       'total': len(community['profession_deck'])},
        'estruturas_regionais': {
            'source': 'data/system.json#structures + data/community.json#structures',
            'cards': {**{s['kind']: 1 for s in system['structures']},
                      **{k: 1 for k in community['structures']}},
            'total': len(system['structures']) + len(community['structures'])},
        'locais_regionais': {'source': 'data/system.json#locations',
                             'cards': {l['id']: 1 for l in system['locations']},
                             'total': len(system['locations'])},
        'crises_regionais': {'source': 'data/system.json#crises',
                             'cards': {c['id']: 1 for c in system['crises']},
                             'total': len(system['crises'])},
        'ultima_transmissao': {'source': 'data/last_transmission.json#cards',
                               'cards': {str(c.get('id', i)): 1 for i, c in enumerate(last['cards'])},
                               'total': len(last['cards'])},
        'referencia_comunidade': {'source': 'data/community.json', 'cards': {
            'bagagem_D6': 1, 'viagem_automatica': 1, 'comida_agua': 1, 'clima_coletor': 1,
            'chegadas_D6': 1, 'horta_lotes': 1, 'crise_0_10': 1, 'obras_e_racao': 1},
            'total': 8},
        # D-27: conhecimento encontrado na 1ª busca de cada local
        'conhecimento': {'source': 'data/community.json#camp.knowledge',
                         'cards': {k: 1 for k in community['camp']['knowledge']},
                         'total': len(community['camp']['knowledge'])},
    }
    camp = community['camp']
    pieces = Counter()
    for kind, spec in community['structures'].items():
        if spec.get('expansion') or spec.get('camp') is False:
            continue
        pieces[kind] = spec.get('max', 1)
    for structure in system['structures']:
        if structure['kind'] != 'garden':
            pieces[structure['kind']] = 1
    pieces['barraca'] += 4    # evacuação: até 14 moradores no início (7 barracas)
    pieces['barraca_familiar'] = 4  # chegadas e resgates
    boards = {
        'mapas_cisterna_0.2': [m['id'] for m in catalog['maps']],
        'mapas_taticos_motor': sorted(tactics['maps']),
        'painel_acampamento': ['comida 0–48 com ficha de limite', 'água 0–36 com ficha de limite',
                               'madeira 0–20', 'metal 0–20', 'carne crua (6)',
                               'moradores e camas 0–30', 'Crise 0–10', 'dias 1–25'],
        'tabuleiro_acampamento': sorted(camp['grid']),
        'tabuleiro_entorno': list(community['pools']),
    }
    heroes = {'cisterna_0.2': sum(1 for h in catalog['heroes'] if h.get('initial')),
              'catalogo_0.2_total': len(catalog['heroes']),
              'regional_motor': len(system['heroes'])}
    tokens = dict(Counter(t['kind'] for t in catalog['tokens']))
    tokens_new = {'viajante (marcador de dias)': 6, 'armadilha': community['traps']['max'],
                  'peças de lote': dict(sorted(pieces.items())),
                  'tiras de mato (níveis)': 2, 'ficha de limite': 2,
                  'marcadores de trilha': 8, 'cubo de obra': 6,
                  'peão de trabalhador': 12}
    return {'decks': decks, 'boards': boards, 'heroes': heroes,
            'tokens_0.2': tokens, 'tokens_new': tokens_new,
            'reuse': {'carne_REC_0.2': meat_cards}}


def check(inv: dict) -> list[str]:
    community = load(EDITION / 'data/community.json')
    problems = []
    if inv['reuse']['carne_REC_0.2'] < community['meat']['track']:
        problems.append('Cartas de Carne 0.2 não cobrem a trilha de carne')
    if set(inv['decks']['profissoes']['cards']) != set(community['professions']):
        problems.append('Baralho de profissões não cobre todas as profissões')
    events = set(inv['decks']['acontecimentos_viagem']['cards'])
    handled = {'tranquila', 'abundancia', 'descoberta', 'chuva', 'atraso', 'ferimento',
               'perda', 'equipamento', 'zumbis', 'pista'}
    if events - handled:
        problems.append(f'Cartas de acontecimento sem efeito no motor: {sorted(events - handled)}')
    if inv['tokens_new']['viajante (marcador de dias)'] < 6:
        problems.append('Marcadores de viajante insuficientes')
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    inv = inventory()
    problems = check(inv)
    text = json.dumps(inv, ensure_ascii=False, indent=1) + '\n'
    if args.write:
        OUT.write_text(text, encoding='utf-8')
    elif OUT.exists() and OUT.read_text(encoding='utf-8') != text:
        problems.append('print_inventory.json desatualizado (rode --write)')
    for name, deck in inv['decks'].items():
        print(f"{name}: {deck['total']}")
    for problem in problems:
        print('ERRO:', problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
