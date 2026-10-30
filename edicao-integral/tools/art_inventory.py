#!/usr/bin/env python3
"""Inventário para a direção de arte (D-32): cartas, heróis, sobreviventes,
inimigos e componentes, lido só de `content/` e `data/`.

Gera `edicao-integral/INVENTARIO_DIRECAO_ARTE.md`. Ids estáveis; nomes são
provisórios até a revisão de nomes comerciais.

    python edicao-integral/tools/art_inventory.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

EDITION = Path(__file__).resolve().parents[1]
ROOT = EDITION.parent
OUT = EDITION / 'INVENTARIO_DIRECAO_ARTE.md'
FAMILIES = {'VIN': 'Vínculos (composição do grupo)', 'INT': 'Intenções', 'REC': 'Recursos',
            'PEC': 'Peças de missão', 'EQU': 'Equipamentos', 'SAQ': 'Saque',
            'VIA': 'Viagem', 'HOR': 'Horda', 'CER': 'Cerco', 'EVE': 'Eventos',
            'PRO': 'Projetos de obra 0.2', 'STR': 'Estruturas 0.2', 'MOR': 'Moradores resgatados',
            'MIS': 'Missões', 'VEI': 'Veículo', 'AJU': 'Ajuda/referência'}
EVENTS = {'tranquila': 'Viagem tranquila', 'abundancia': 'Abundância', 'descoberta': 'Descoberta',
          'chuva': 'Chuva', 'atraso': 'Atraso', 'ferimento': 'Ferimento', 'perda': 'Perda de carga',
          'equipamento': 'Equipamento quebrado', 'zumbis': 'Zumbis no caminho', 'pista': 'Pista'}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def table(head: list[str], rows: list[list]) -> list[str]:
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows]
    return out + ['']


def build() -> str:
    catalog = load(ROOT / 'content/catalog.json')
    system = load(EDITION / 'data/system.json')
    community = load(EDITION / 'data/community.json')
    tactics = load(EDITION / 'data/tactics.json')
    last = load(EDITION / 'data/last_transmission.json')
    inventory = load(EDITION / 'data/print_inventory.json')
    lines = ['# Inventário para a direção de arte — Zona Zero', '',
             'Gerado por `tools/art_inventory.py` a partir de `content/` e `data/`. Ids são '
             'estáveis; nomes e textos são provisórios. Nada aqui é arte.', '']

    lines += ['## 1. Heróis', '', '### Catálogo da Cisterna 0.2 (24 heróis; 12 iniciais)', '']
    lines += table(['Id', 'Nome', 'Profissão', 'Inicial', 'Habilidade', 'História'],
                   [[h['id'], h['name'], h.get('profession', ''), 'sim' if h.get('initial') else
                     h.get('unlock', ''), h.get('ability', ''), h.get('story', '')]
                    for h in catalog['heroes']])
    lines += ['### Heróis do motor regional (Última Transmissão)', '']
    lines += table(['Id', 'Nome', 'Profissão', 'Atributos', 'Vida'],
                   [[h['id'], h['name'], h['profession'],
                     ', '.join(f'{k} {v}' for k, v in h['attributes'].items()), h['health']]
                    for h in system['heroes']])

    lines += ['## 2. Sobreviventes', '', '### Especialistas nomeados (15)', '']
    lines += table(['Id', 'Nome', 'Profissão', 'Função no acampamento', 'Produz'],
                   [[n['id'], n['name'], n['profession'], n['job'], n['output']]
                    for n in system['npcs']])
    deck = Counter(community['profession_deck'])
    lines += ['### Profissões da Comunidade (baralho de 12)', '']
    lines += table(['Id', 'Nome', 'Cartas', 'Bônus'],
                   [[k, v['name'], deck.get(k, 0), ', '.join(v['bonus']) or '—']
                    for k, v in community['professions'].items()])
    lines += ['### Sobreviventes comuns (sem nome fixo)', '',
              '- Adultos, crianças e cães migrados da Cisterna ou chegados (dias 4 e 10).',
              '- Ilustração sugerida: 6–8 silhuetas reutilizáveis (adulto, idoso, criança, '
              'família, cão).', '']

    lines += ['## 3. Inimigos', '']
    lines += table(['Id', 'Vida', 'Ataque', 'Movimento', 'Visão', 'XP'],
                   [[k, v['health'], v['attack'], v['move'], v['sight'], v['xp']]
                    for k, v in tactics['enemies'].items()])
    lines += ['Grupos de horda do motor tático: ' + ', '.join(tactics['hordes']) + '.', '']

    lines += ['## 4. Cartas', '', '### Cisterna 0.2 (324, certificadas; reaproveitar ids)', '']
    by_family = defaultdict(Counter)
    for card in catalog['cards']:
        by_family[card['family']][card['name']] += 1
    rows = []
    for family, names in by_family.items():
        listed = '; '.join(f'{n} ×{c}' if c > 1 else n for n, c in names.items())
        rows.append([family, FAMILIES.get(family, family), sum(names.values()), listed])
    lines += table(['Família', 'Tipo', 'Cartas', 'Nomes (×cópias)'], rows)
    lines += ['### Edição integral (novas)', '']
    events = Counter(community['event_deck'])
    lines += ['**Acontecimentos de viagem (12):** ' + '; '.join(
        f'{EVENTS.get(k, k)} ×{c}' if c > 1 else EVENTS.get(k, k) for k, c in events.items()) + '.',
        '']
    lines += ['**Locais regionais (7):**', '']
    lines += table(['Id', 'Local', 'Distância', 'Buscas', 'Renovação'],
                   [[l['id'], l['name'], l['distance'], l['searches'], l['renewal']]
                    for l in system['locations']])
    lines += ['**Crises regionais (5):** ' + '; '.join(
        f"{c['id']} {c['name']}" for c in system['crises']) + '.', '']
    lines += ['**Última Transmissão (5):** ' + '; '.join(
        f"{c['id']} {c['name']}" for c in last['cards']) + '.', '']
    lines += ['**Conhecimento (5):** ' + '; '.join(
        f"{k} {v['name']} ({v['location']})" for k, v in community['camp']['knowledge'].items())
        + '.', '']
    ref = inventory['decks']['referencia_comunidade']['cards']
    lines += ['**Referência da comunidade (8):** ' + ', '.join(ref) + '.', '']
    structures = [[s['id'], s['kind'], s['name']] for s in system['structures']]
    structures += [['COM', k, v['name']] for k, v in community['structures'].items()
                   if v.get('camp', True) and not v.get('expansion')]
    lines += ['**Estruturas (cartas de obra e peças de lote):**', '']
    lines += table(['Id', 'Chave', 'Nome'], structures)

    lines += ['## 5. Componentes', '']
    totals = {k: v['total'] for k, v in inventory['decks'].items()}
    lines += table(['Baralho', 'Cartas'], [[k, v] for k, v in totals.items()]
                   + [['**total**', sum(totals.values())]])
    lines += ['**Peças de lote:** ' + ', '.join(
        f'{k} {v}' for k, v in inventory['tokens_new']['peças de lote'].items()) + '.', '']
    others = {k: v for k, v in inventory['tokens_new'].items() if k != 'peças de lote'}
    lines += ['**Marcadores novos:** ' + ', '.join(f'{k} {v}' for k, v in others.items()) + '.',
              '']
    lines += ['**Marcadores da Cisterna 0.2:** ' + ', '.join(
        f'{k} {v}' for k, v in inventory['tokens_0.2'].items()) + '.', '']
    lines += ['**Mapas táticos:** ' + ', '.join(sorted(tactics['maps'])) + '; Cisterna 0.2: '
              + ', '.join(inventory['boards']['mapas_cisterna_0.2']) + '.', '']
    lines += ['**Tabuleiros da edição integral:** painel do acampamento (2 A4 paisagem), '
              'tabuleiro de lotes 4×4 (A4 retrato), tabuleiro do entorno (A4), montagem da '
              'Horta abandonada (A4).', '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def main() -> int:
    OUT.write_text(build(), encoding='utf-8')
    print('gerado:', OUT.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
