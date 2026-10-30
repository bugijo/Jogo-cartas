#!/usr/bin/env python3
"""Tabuleiros da edição integral (D-08): painel do abrigo, entorno e montagem
da Horta abandonada, em A4 paisagem de uma face (pycairo, vetorial).

Todos os números vêm de `data/` (Comunidade, sistema, mapas táticos); o
manifesto `print/boards_manifest.json` resume o que cada folha mostra e é
conferido no `check.sh full` (`--check`), como o inventário de cartas.

    python edicao-integral/tools/build_boards_integral.py          # gera PDFs + manifesto
    python edicao-integral/tools/build_boards_integral.py --check  # só confere o manifesto
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EDITION = Path(__file__).resolve().parents[1]
OUT = EDITION / 'print'
MANIFEST = OUT / 'boards_manifest.json'
A4_LANDSCAPE = (297, 210)
CREATED = '2026-10-30T00:00:00'
FONT = 'DejaVu Sans'
NAMES = {'caca': 'Caça', 'peixe': 'Peixe', 'madeira': 'Madeira', 'frutas': 'Frutas',
         'sucata': 'Sucata', 'pesca': 'Pesca', 'lenha': 'Lenha', 'coleta': 'Coleta',
         'agua': 'Água', 'meat': 'carne', 'food': 'comida', 'wood': 'madeira',
         'scrap': 'sucata', 'fruit': 'fruta', 'raw_water': 'água bruta'}


def load(name):
    return json.loads((EDITION / 'data' / name).read_text(encoding='utf-8'))


def manifest() -> dict:
    """O que as folhas mostram, derivado só dos dados."""
    community, system, tactics = load('community.json'), load('system.json'), load('tactics.json')
    rules = system['rules']
    level2 = community['structures']
    edge = tactics['maps']['garden_edge_01']
    camp = community['camp']
    food, water = camp['storage']['food'], camp['storage']['water']
    return {
        'painel_abrigo': {
            'comida': [food['base'], food['storage'], food['deposito2']],
            'agua': [water['base'], water['reservoir']],
            'madeira': camp['storage']['wood'], 'metal': camp['storage']['scrap'],
            'carne': community['meat']['track'],
            'carne_noites': community['meat']['keeps_nights'],
            'crise': camp['crisis'], 'camas': camp['beds'],
            'dias': 25, 'chegadas': community['arrivals']['days'],
            'chegada_D6': camp['arrivals_table'], 'chuva': camp['rain_at'],
            'horta': camp['horta'], 'racao_obra': camp['work_ration'],
            'horta_abandonada_renova': community['location_renew_every']['EXP-LOC-01'],
        },
        'tabuleiro_acampamento': {
            'grade': camp['grid'],
            'expansoes': {k: [v['cost'], v['work']] for k, v in level2.items()
                          if v.get('expansion')},
            'categorias': camp['category'],
            'conhecimento': {k: v['location'] for k, v in camp['knowledge'].items()},
        },
        'tabuleiro_entorno': {
            'reservas': {k: [v['start'], v['max'], v['regrow']]
                         for k, v in community['pools'].items()},
            'atividades': {k: [v['points_per_unit'], v['output']]
                           for k, v in community['activities'].items()},
            'viajantes': 6, 'armadilhas': community['traps']['max'],
            'capacidade_viagem': community['trips']['capacity'],
            'baralho_acontecimentos': len(community['event_deck']),
        },
        'montagem_horta_abandonada': {
            'zonas': len(edge['zones']), 'entrada': edge['entry'], 'surgimento': edge['spawn'],
            'buscas': edge['search'], 'cercas': [d['edge'] for d in edge['doors']],
            'loot': next(l['loot'] for l in system['locations'] if l['id'] == 'EXP-LOC-01'),
            'buscas_max': next(l['searches'] for l in system['locations']
                               if l['id'] == 'EXP-LOC-01'),
        },
    }


# --- desenho ------------------------------------------------------------------------
def mm(value: float) -> float:
    return value * 72 / 25.4


class Sheet:
    """Uma página A4 paisagem; coordenadas em milímetros a partir do topo."""

    def __init__(self, surface, cairo):
        self.cairo = cairo
        self.ctx = cairo.Context(surface)
        self.ctx.scale(72 / 25.4, 72 / 25.4)
        self.ctx.set_line_width(0.25)

    def font(self, size, bold=False):
        weight = self.cairo.FONT_WEIGHT_BOLD if bold else self.cairo.FONT_WEIGHT_NORMAL
        self.ctx.select_font_face(FONT, self.cairo.FONT_SLANT_NORMAL, weight)
        self.ctx.set_font_size(size * 0.3528)  # pt → mm

    def text(self, x, y, value, size=8, bold=False, align='left', grey=0.0):
        self.font(size, bold)
        width = self.ctx.text_extents(value).x_advance
        dx = {'left': 0, 'center': -width / 2, 'right': -width}[align]
        self.ctx.set_source_rgb(grey, grey, grey)
        self.ctx.move_to(x + dx, y)
        self.ctx.show_text(value)
        return width

    def para(self, x, y, width, value, size=7, leading=1.35, grey=0.0):
        """Texto corrido com quebra por largura; devolve o y seguinte."""
        self.font(size)
        line, height = '', size * 0.3528 * leading
        for word in value.split():
            trial = f'{line} {word}'.strip()
            if self.ctx.text_extents(trial).x_advance > width and line:
                self.text(x, y, line, size, grey=grey)
                y += height
                line = word
            else:
                line = trial
        if line:
            self.text(x, y, line, size, grey=grey)
            y += height
        return y

    def rect(self, x, y, w, h, fill=None, width=0.25, dash=False):
        self.ctx.save()
        self.ctx.rectangle(x, y, w, h)
        if fill is not None:
            self.ctx.set_source_rgb(fill, fill, fill)
            self.ctx.fill_preserve()
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(width)
        if dash:
            self.ctx.set_dash([1.2, 0.8])
        self.ctx.stroke()
        self.ctx.restore()

    def line(self, x1, y1, x2, y2, width=0.25):
        self.ctx.save()
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.stroke()
        self.ctx.restore()

    def header(self, title, subtitle):
        self.text(12, 15, title, 15, bold=True)
        self.text(12, 21, subtitle, 7.5, grey=0.35)
        self.text(285, 15, 'Zona Zero — edição integral', 7, align='right', grey=0.35)
        self.text(285, 203, 'A4 paisagem, 100%, uma face. Valores de data/ (gerado).',
                  6, align='right', grey=0.45)

    def track(self, x, y, label, count, cell=6.2, start=0, marks=None, shade=None,
              note=None):
        """Trilha de casas numeradas; `marks` = {casa: rótulo} acima da divisa."""
        marks, shade = marks or {}, shade or set()
        self.text(x, y - 1.5, label, 8, bold=True)
        if note:
            self.text(x + cell * count, y - 1.5, note, 6, align='right', grey=0.35)
        for index in range(count):
            value = start + index
            cx = x + index * cell
            self.rect(cx, y, cell, cell, fill=0.88 if value in shade else None)
            self.text(cx + cell / 2, y + cell * 0.68, str(value), 5.5, align='center',
                      grey=0.3)
            if value in marks:
                self.line(cx, y - 0.8, cx, y + cell + 0.8, width=0.9)
                self.text(cx + 0.6, y + cell + 3.4, marks[value], 5.5, grey=0.2)
        return y + cell + (11 if marks else 7.5)


def draw_shelter(cairo, path, data):
    """Painel do acampamento em lotes (D-30): trilhas com ficha de limite, Crise, dias."""
    surface = cairo.PDFSurface(str(path), mm(A4_LANDSCAPE[0]), mm(A4_LANDSCAPE[1]))
    surface.set_metadata(cairo.PDF_METADATA_TITLE, 'Painel do acampamento — edição integral')
    surface.set_metadata(cairo.PDF_METADATA_CREATE_DATE, CREATED)  # bytes estáveis
    sheet = Sheet(surface, cairo)
    sheet.header('Painel do acampamento — estoques',
                 'Um marcador por trilha e uma ficha LIMITE no número do nível atual. '
                 'Cada recurso tem a sua trilha: água não ocupa espaço de comida.')
    base, deposit, deposit2 = data['comida']
    food_cap = base + deposit + deposit2
    marks = {base: 'limite inicial', base + deposit: f'Depósito +{deposit}',
             food_cap: f'Depósito 2 +{deposit2}'}
    y = 34
    y = sheet.track(12, y, 'Comida (porções)', 25, cell=10.8, marks={base: marks[base]})
    y = sheet.track(12, y, 'Comida (25–48)', 24, cell=10.8, start=25,
                    marks={k: v for k, v in marks.items() if k >= 25},
                    shade=set(range(base + 1, food_cap + 1)))
    tank, reservoir = data['agua']
    y = sheet.track(12, y, 'Água', 25, cell=10.8, marks={tank: 'limite inicial'})
    y = sheet.track(12, y, 'Água (25–36)', 12, cell=10.8, start=25,
                    marks={tank + reservoir: f'Reservatório +{reservoir}'},
                    shade=set(range(tank + 1, tank + reservoir + 1)))
    row = y
    sheet.track(12, row, f'Madeira (máx. {data["madeira"]})', data['madeira'] + 1, cell=6.4)
    sheet.track(150, row, f'Metal (máx. {data["metal"]})', data['metal'] + 1, cell=6.4)
    y = row + 15
    meat_x = 12
    sheet.text(meat_x, y - 1.5, f'Carne crua (máx. {data["carne"]})', 8, bold=True)
    for index in range(data['carne']):
        sheet.rect(meat_x + index * 15, y, 14, 10)
        sheet.text(meat_x + index * 15 + 1, y + 3, 'estraga dia', 5, grey=0.4)
    sheet.para(meat_x, y + 15, 95, f'Anote o dia em que estraga (chegada + '
               f'{data["carne_noites"]} noites; defumador +3). Cozinhar: 4 porções com '
               'madeira, Cozinha ou defumador; 2 improvisadas.', 6.5)
    sheet.para(110, y + 1, 170, 'Remédio, munição, combustível, peças e conhecimento ficam '
               'como cartas ao lado do painel (sem trilha). Ração de obra: cada pessoa em obra '
               f'pesada come {data["racao_obra"]} porção a mais no dia.', 6.8)
    surface.show_page()

    # página 2: pessoas, Crise, dias
    sheet = Sheet(surface, cairo)
    crisis = data['crisis'] if 'crisis' in data else data['crise']
    sheet.header('Painel do acampamento — pessoas, Crise e dias',
                 'Moradores e camas na mesma trilha (dois marcadores). A Crise mede fome, '
                 'sede, gente sem cama e recusas.')
    y = sheet.track(12, 34, 'Moradores (marcador redondo) e camas (marcador quadrado)', 31,
                    cell=8.8)
    beds = data['camas']
    sheet.para(12, y - 2, 270, f'Camas: barraca {beds["barraca"]}, barraca familiar '
               f'{beds["barraca_familiar"]}, alojamento {beds["lodging"]} (+{beds["alojamento2"]} '
               'no nível 2). Só quem tem cama recupera Vida à noite (cama vai primeiro a '
               'quem está ferido). Pode haver mais moradores que camas.', 6.8)
    y += 10
    bands = {0: 'calma', 1: 'leve', crisis['moderate']: 'moderada', crisis['grave']: 'grave',
             crisis['max']: 'COLAPSO'}
    y = sheet.track(12, y, 'Crise', crisis['max'] + 1, cell=14, marks=bands,
                    shade={crisis['max']})
    small = crisis['small_share']
    rules = [
        f'Noite com humano sem porção: +{crisis["small"]} (até 1/{small} dos humanos) ou '
        f'+{crisis["large"]} (mais que isso). Todos servidos: −{crisis["recover"]}; '
        f'−{crisis["recover_reserve"]} se o estoque ainda cobre outra noite.',
        f'Mais de {crisis["unhoused_over"]} moradores sem cama: +1. Recusar quem chega: '
        f'+{crisis["refuse"]}.',
        f'Moderada ({crisis["moderate"]}+): obras pesadas param. Grave ({crisis["grave"]}+): '
        f'ninguém recupera Vida; no amanhecer D6 ≤ {crisis["conflict_at"]} perde 1 madeira '
        f'ou metal. {crisis["max"]}: colapso (derrota parcial).',
    ]
    for line in rules:
        y = sheet.para(12, y, 270, line, 6.8)
    y += 4
    sheet.text(12, y, 'Dias da Última Transmissão', 8, bold=True)
    arrivals = set(data['chegadas'])
    renew = data['horta_abandonada_renova']
    for day in range(1, data['dias'] + 1):
        x = 12 + (day - 1) * 10.8
        sheet.rect(x, y + 2, 10.4, 13, fill=0.88 if day in arrivals else None)
        sheet.text(x + 5.2, y + 9, str(day), 8, bold=True, align='center')
        if day in arrivals:
            sheet.text(x + 5.2, y + 13.5, 'CHEGA', 4.2, align='center')
        if day % renew == 0:
            sheet.text(x + 5.2, y + 18.5, 'H.ab+1', 3.8, align='center', grey=0.35)
    y += 26
    names = {'adult': 'adulto', 'child': 'criança'}
    tents = {'barraca': 'barraca', 'barraca_familiar': 'barraca familiar'}
    parts = []
    for face, entry in sorted(data['chegada_D6'].items()):
        who = ' + '.join(names[p] for p in entry['people']) or 'ninguém'
        if entry.get('tent'):
            who += f' (traz {tents[entry["tent"]]})'
        parts.append(f'{face}: {who}')
    y = sheet.para(12, y, 270, 'Chegada (D6 no amanhecer): ' + '; '.join(parts) + '.', 6.8)
    horta = data['horta']
    y = sheet.para(12, y + 1, 270, f'Tempo (D6 a cada amanhecer): {data["chuva"]}–6 chove. '
                   f'Horta: cada pessoa cuida de {horta["lots_per_worker"]} lotes (agricultor '
                   f'{horta["specialist_lots"]}); lote cuidado dá {horta["food_per_lot"]} '
                   f'porções; sem chuva, 1 água a cada {horta["lots_per_water"]} lotes; D6 = '
                   f'{horta["pest_at"]} da pessoa: praga, −1 porção.', 6.8)
    sheet.text(12, y + 4, 'Ordem do dia', 8, bold=True)
    steps = ['1 tempo (D6), retornos de viagem, armadilhas, carne estraga',
             '2 chegada (dias marcados): acolher ou recusar',
             '3 funções nos lotes, viagens e expedição tática',
             '4 fim do dia: horta, obras (ração), cozinha', '5 noite: refeição e Crise',
             '6 recuperação (só com cama), vigia e crise da noite']
    for index, step in enumerate(steps):
        sheet.text(12 + (index // 3) * 140, y + 10 + (index % 3) * 5, step, 6.5)
    surface.finish()


SYMBOLS = {'barraca': 'B', 'horta': 'H', 'agua': 'A', 'estoque': 'E', 'oficina': 'O',
           'defesa': 'D'}
SYMBOL_NAMES = {'B': 'barraca', 'H': 'horta', 'A': 'água', 'E': 'estoque',
                'O': 'oficina/enfermaria', 'D': 'defesa'}


def draw_camp_board(cairo, path, data):
    """Tabuleiro 4×4 de lotes (45 mm) em A4 retrato; níveis por tiras de mato."""
    width, height = A4_LANDSCAPE[1], A4_LANDSCAPE[0]
    surface = cairo.PDFSurface(str(path), mm(width), mm(height))
    surface.set_metadata(cairo.PDF_METADATA_TITLE, 'Tabuleiro do acampamento — edição integral')
    surface.set_metadata(cairo.PDF_METADATA_CREATE_DATE, CREATED)
    sheet = Sheet(surface, cairo)
    sheet.text(12, 15, 'Tabuleiro do acampamento (lotes)', 15, bold=True)
    sheet.text(12, 21, 'Funcional, sem arte. Nível 1 = 2×2; 2 = 3×3; 3 = 4×4.', 7.5, grey=0.35)
    lot, x0, y0 = 45, 15, 40
    sheet.rect(x0 - 2, y0 - 12, 4 * lot + 4, 10, fill=0.9)
    sheet.text(x0 + 2 * lot, y0 - 5.5, 'FOGUEIRA E ESTOQUE INICIAL (fora dos lotes)', 7,
               bold=True, align='center')
    for lot_id, cats in data['grade'].items():
        row, col = int(lot_id[1]) - 1, int(lot_id[3]) - 1
        x, y = x0 + col * lot, y0 + row * lot
        level = max(1, max(row, col))
        sheet.rect(x, y, lot, lot, fill=None if level == 1 else (0.95 if level == 2 else 0.9))
        sheet.text(x + 2, y + 5, lot_id.upper(), 6, grey=0.4)
        sheet.text(x + lot - 2, y + 5, f'nível {level}', 5.5, align='right', grey=0.4)
        letters = [SYMBOLS[c] for c in cats]
        sheet.text(x + lot / 2, y + lot / 2 + 4, ' / '.join(letters), 16, bold=True,
                   align='center')
    y = y0 + 4 * lot + 8
    legend = '; '.join(f'{k} = {v}' for k, v in SYMBOL_NAMES.items())
    y = sheet.para(12, y, width - 24, 'Símbolos: ' + legend + '. Um lote recebe uma '
                   'construção ou até 2 barracas pequenas; símbolo duplo = escolha.', 7)
    costs = []
    for kind, (cost, work) in sorted(data['expansoes'].items()):
        paid = ' + '.join(f'{n} {NAMES.get(r, r)}' for r, n in cost.items())
        costs.append(f'{kind}: {paid}, {work} trabalhos (obra pesada)')
    y = sheet.para(12, y + 1, width - 24, 'Expansões: ' + '; '.join(costs) + '. A 4×4 exige '
                   'Depósito, Oficina ou Vigia pronta. Na expansão, retire as tiras de mato.', 7)
    places = '; '.join(f'{k} ({v})' for k, v in data['conhecimento'].items())
    sheet.para(12, y + 1, width - 24, 'Conhecimento (1ª busca do local): ' + places + '.', 7)
    sheet.text(width - 12, height - 7, 'A4 retrato, 100%, uma face. Valores de data/ (gerado).',
               6, align='right', grey=0.45)
    surface.finish()


def draw_surroundings(cairo, path, data):
    surface = cairo.PDFSurface(str(path), mm(A4_LANDSCAPE[0]), mm(A4_LANDSCAPE[1]))
    surface.set_metadata(cairo.PDF_METADATA_TITLE, 'Entorno — edição integral')
    surface.set_metadata(cairo.PDF_METADATA_CREATE_DATE, CREATED)  # bytes estáveis
    sheet = Sheet(surface, cairo)
    sheet.header('Entorno do abrigo — floresta, rio e ruínas',
                 'Reservas finitas: viagens automáticas tiram unidades daqui; algumas '
                 'crescem a cada amanhecer até o máximo.')
    y = 33
    for key, (start, top, regrow) in data['reservas'].items():
        note = (f'começa em {start}, +{regrow}/amanhecer' if regrow
                else f'começa em {start}, não renova')
        y = sheet.track(12, y, f'{NAMES[key]} (máx. {top})', top + 1, cell=9.5,
                        shade={start}, note=note)
    sheet.text(12, y - 2, 'Casa cinza = valor inicial.', 6, grey=0.35)
    y += 5
    sheet.text(12, y, 'Viajantes', 8, bold=True)
    for index in range(data['viajantes']):
        sheet.rect(12, y + 3 + index * 8.5, 128, 7.5)
        sheet.text(14, y + 8 + index * 8.5,
                   'quem: ______  atividade: ______  dias: __  volta no dia: __  cão: __',
                   6, grey=0.45)
    y += 3 + data['viajantes'] * 8.5 + 6
    sheet.text(12, y, f'Armadilhas (máx. {data["armadilhas"]}): 1 madeira; D6 no amanhecer '
               '— 5–6 tira 1 carne da caça, 1 quebra.', 6.5)
    for index in range(data['armadilhas']):
        sheet.rect(12 + index * 18, y + 2.5, 16, 11, dash=True)
    # atividades
    x0, y0 = 150, 33
    sheet.text(x0, y0 - 1.5, 'Atividades de viagem', 8, bold=True)
    sheet.rect(x0, y0, 135, 6 * 7 + 7)
    sheet.text(x0 + 2, y0 + 5, 'atividade', 6.5, bold=True)
    sheet.text(x0 + 40, y0 + 5, 'pontos por unidade', 6.5, bold=True)
    sheet.text(x0 + 85, y0 + 5, 'traz', 6.5, bold=True)
    for index, (key, (ppu, output)) in enumerate(data['atividades'].items()):
        yy = y0 + 12 + index * 7
        sheet.line(x0, yy - 4.5, x0 + 135, yy - 4.5)
        sheet.text(x0 + 2, yy, NAMES[key], 7)
        sheet.text(x0 + 40, yy, str(ppu), 7)
        sheet.text(x0 + 85, yy, NAMES[output], 7)
    yy = sheet.para(x0, y0 + 56, 135,
                    f'Pontos = (D6 + profissão + cão) × dias − 1 por noite sem ração − 1 por '
                    f'noite do cão. Unidades = pontos ÷ custo, no máximo '
                    f'{data["capacidade_viagem"]} e o que houver na reserva. Cartas de '
                    'acontecimento: 1 por viagem; +1 em caça/sucata; +1 em viagem de 3 dias. '
                    'Fruta: 1 água a cada 2. Água bruta: ferver 1 madeira a cada 3.', 6.5)
    yy += 4
    # baralho de acontecimentos em tamanho de carta (63 × 88 mm)
    sheet.text(x0, yy, f'Acontecimentos ({data["baralho_acontecimentos"]} cartas)', 8,
               bold=True)
    for index, label in enumerate(('pilha', 'descarte')):
        sheet.rect(x0 + index * 67, yy + 3, 63, 88, dash=True)
        sheet.text(x0 + index * 67 + 31.5, yy + 49, label, 7, align='center', grey=0.4)
    surface.finish()


def draw_garden_map(cairo, path, data):
    surface = cairo.PDFSurface(str(path), mm(A4_LANDSCAPE[0]), mm(A4_LANDSCAPE[1]))
    surface.set_metadata(cairo.PDF_METADATA_TITLE, 'Montagem — Horta abandonada')
    surface.set_metadata(cairo.PDF_METADATA_CREATE_DATE, CREATED)  # bytes estáveis
    sheet = Sheet(surface, cairo)
    sheet.header('Montagem — Horta abandonada (EXP-LOC-01)',
                 'Use os quatro módulos comuns do mapa; esta folha diz como jogar o '
                 'campo aberto.')
    size, x0, y0 = 36, 14, 30
    fences = [tuple(edge) for edge in data['cercas']]
    for zone in range(1, data['zonas'] + 1):
        row, col = divmod(zone - 1, 4)
        x, y = x0 + col * size, y0 + row * size
        special = zone in data['buscas'] or zone in (data['entrada'], data['surgimento'])
        sheet.rect(x, y, size, size, fill=0.9 if zone in data['buscas'] else None)
        sheet.text(x + 2, y + 6, f'Z{zone}', 9, bold=special)
        if zone == data['entrada']:
            sheet.text(x + size / 2, y + 22, 'ENTRADA', 7, bold=True, align='center')
            sheet.text(x + size / 2, y + 27, 'e saída', 6, align='center')
        if zone == data['surgimento']:
            sheet.text(x + size / 2, y + 22, 'SURGIMENTO', 7, bold=True, align='center')
        if zone in data['buscas']:
            sheet.text(x + size / 2, y + 22, 'BUSCA', 7, bold=True, align='center')
    for a, b in fences:
        (ra, ca), (rb, cb) = divmod(a - 1, 4), divmod(b - 1, 4)
        if ra == rb:   # vizinhas na mesma fileira: divisa vertical
            x = x0 + max(ca, cb) * size
            sheet.line(x, y0 + ra * size + 4, x, y0 + ra * size + size - 4, width=1.6)
            sheet.text(x + 1, y0 + ra * size + size / 2, 'cerca', 5.5)
        else:          # vizinhas na mesma coluna: divisa horizontal
            y = y0 + max(ra, rb) * size
            sheet.line(x0 + ca * size + 4, y, x0 + ca * size + size - 4, y, width=1.6)
            sheet.text(x0 + ca * size + size / 2, y - 1, 'cerca', 5.5, align='center')
    food = data['loot'].get('food', 0)
    tx = x0 + 4 * size + 12
    y = sheet.para(tx, 36, 120,
                   'Campo aberto: ignore as paredes desenhadas nos módulos comuns. Zonas '
                   'vizinhas (lado com lado) sempre se conectam, exceto pelas cercas.', 8)
    y = sheet.para(tx, y + 3, 120,
                   'Cerca: porta comum fechada (abrir custa 1 PA), como as portas dos '
                   'módulos comuns.', 8)
    y = sheet.para(tx, y + 3, 120,
                   f'Buscas: {data["buscas_max"]} no local, {food} comida cada, nas zonas '
                   f'{" e ".join("Z" + str(z) for z in data["buscas"])}. Na edição integral '
                   'renova 1 busca a cada 2 noites (dias pares), até o máximo.', 8)
    y = sheet.para(tx, y + 3, 120,
                   'Risco próprio: as buscas ficam no centro (Z11 a duas zonas do '
                   'surgimento) e não há paredes para se esconder.', 8)
    sheet.para(tx, y + 3, 120,
               'Distância: perto (1 trecho de viagem). Horda, cartas de Viagem e Emboscada '
               'como em qualquer local.', 8, grey=0.3)
    surface.finish()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    data = manifest()
    text = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    if args.check:
        ok = MANIFEST.exists() and MANIFEST.read_text(encoding='utf-8') == text
        missing = [name for name in data if not (OUT / f'{name}.pdf').exists()]
        if not ok or missing:
            print('ERRO: tabuleiros desatualizados (rode build_boards_integral.py)',
                  missing, file=sys.stderr)
            return 1
        print('tabuleiros:', ', '.join(data))
        return 0
    import cairo
    OUT.mkdir(exist_ok=True)
    draw_shelter(cairo, OUT / 'painel_abrigo.pdf', data['painel_abrigo'])
    draw_camp_board(cairo, OUT / 'tabuleiro_acampamento.pdf', data['tabuleiro_acampamento'])
    draw_surroundings(cairo, OUT / 'tabuleiro_entorno.pdf', data['tabuleiro_entorno'])
    draw_garden_map(cairo, OUT / 'montagem_horta_abandonada.pdf',
                    data['montagem_horta_abandonada'])
    MANIFEST.write_text(text, encoding='utf-8')
    print('gerados:', ', '.join(f'{name}.pdf' for name in data))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
