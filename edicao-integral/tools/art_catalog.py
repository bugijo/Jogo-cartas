#!/usr/bin/env python3
"""Catálogo artístico (D-33): as 400 cartas, pessoas, inimigos, locais, mapas e
marcadores, com a camada de arte de `data/art/` cruzada com os dados oficiais.

Ids, nomes, quantidades e textos mecânicos vêm de `content/catalog.json` e
`data/*.json` (nunca da camada de arte). Gera:

- `edicao-integral/CATALOGO_ARTISTICO.md` (revisão humana)
- `edicao-integral/data/art/catalogo_artistico.json` (produção)

    python edicao-integral/tools/art_catalog.py           # gera
    python edicao-integral/tools/art_catalog.py --check   # confere (check.sh full)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path

EDITION = Path(__file__).resolve().parents[1]
ROOT = EDITION.parent
ART = EDITION / 'data' / 'art'
OUT_MD = EDITION / 'CATALOGO_ARTISTICO.md'
OUT_JSON = ART / 'catalogo_artistico.json'
FAMILY = {'VIN': 'Vínculo', 'INT': 'Intenção', 'REC': 'Recurso', 'PEC': 'Peça de missão',
          'EQU': 'Equipamento', 'SAQ': 'Saque', 'VIA': 'Viagem', 'HOR': 'Horda',
          'CER': 'Cerco', 'EVE': 'Evento do dia', 'PRO': 'Projeto de obra',
          'STR': 'Estrutura', 'MOR': 'Morador resgatado', 'MIS': 'Missão',
          'VEI': 'Veículo', 'AJU': 'Ajuda'}
RES = {'food': 'comida', 'water': 'água', 'wood': 'madeira', 'scrap': 'sucata',
       'medicine': 'remédio', 'fuel': 'combustível', 'ammo': 'munição'}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def cost(spec: dict) -> str:
    return ' + '.join(f'{n} {RES.get(r, r)}' for r, n in spec.items()) or 'sem material'


def structure_text(kind: str, spec: dict, camp: dict, system_kind: bool) -> str:
    """Texto mecânico a partir dos dados (custo, trabalho, efeito)."""
    parts = [f'Custo {cost(spec.get("cost", {}))}; {spec.get("work", 0)} trabalho(s).']
    cat = camp['category'].get(kind)
    if cat:
        parts.append(f'Ocupa 1 lote de {cat}.')
    effects = {
        'storage': f'+{camp["storage"]["food"]["storage"]} de limite de comida.',
        'deposito2': f'+{camp["storage"]["food"]["deposito2"]} de limite de comida (exige Depósito).',
        'reservoir': f'+{camp["storage"]["water"]["reservoir"]} de limite de água; água bruta sem ferver.',
        'lodging': f'{camp["beds"]["lodging"]} camas.',
        'alojamento2': f'+{camp["beds"]["alojamento2"]} camas (exige Alojamento).',
        'barraca': f'{camp["beds"]["barraca"]} camas; até 2 por lote.',
        'horta': (f'Pronta {camp["horta"]["grow_days"]} amanheceres depois; cuidada dá '
                  f'{camp["horta"]["food_per_lot"]} porções.'),
        'watch': 'Na defesa final, atira 1 por rodada; vigia contra a crise da noite.',
        'workshop': 'Oficina do acampamento (reparos, fabricar munição).',
        'infirmary': 'Cura com remédio; exigida pelo Ambulatório.',
        'garden': 'Modelo abstrato: 2 comida por amanhecer depois de 4 dias.',
        'coletor': 'Chuva: D6 4–5 +2 água, 6 +4.',
        'cozinha': 'Carne cozida rende 4 porções sem madeira; +1 carne por cozinheiro.',
        'canteiro': 'Modelo abstrato: 2 comida por trabalhador.',
        'cerca': 'Modelo abstrato: +3 terreno.',
        'expansao2': 'Abre o acampamento 3×3 (obra pesada).',
        'expansao3': 'Abre o 4×4; exige Depósito, Oficina ou Vigia (obra pesada).',
        'composteira': f'+{camp["effects"]["composteira_food"]} porção por pessoa na horta (exige K-AGR).',
        'defumador': f'Carne dura +{camp["effects"]["defumador_nights"]} noites e cozinha sem madeira (exige K-CON).',
        'bancada': f'+{camp["effects"]["bancada_units"]} trabalho por pessoa em obra (exige K-FER).',
        'ambulatorio': (f'+{camp["effects"]["ambulatorio_people"]} pessoa nos cuidados; função remédio: '
                        f'{camp["effects"]["remedio_food"]} porções → 1 remédio (exige K-SAU e Enfermaria).'),
        'filtro': 'Água bruta vira potável sem ferver (exige K-AGU).',
    }
    parts.append(effects.get(kind, ''))
    if kind in camp['heavy_kinds'] or spec.get('heavy'):
        parts.append('Obra pesada: ração de obra.')
    return ' '.join(p for p in parts if p)


def build() -> dict:
    catalog = load(ROOT / 'content/catalog.json')
    system = load(EDITION / 'data/system.json')
    community = load(EDITION / 'data/community.json')
    last = load(EDITION / 'data/last_transmission.json')
    style = load(ART / 'style.json')
    cis = load(ART / 'cisterna.json')
    integral = load(ART / 'integral.json')
    world = load(ART / 'world.json')
    camp = community['camp']
    problems = []
    cards = []

    # --- Cisterna 0.2 -------------------------------------------------------------------
    groups = OrderedDict()
    for card in catalog['cards']:
        groups.setdefault((card['family'], card['name']), []).append(card)
    saque = cis['saque']
    for (family, name), copies in groups.items():
        key = f'{family}:{name}'
        if family == 'SAQ':
            region, resource = name.split(': ')
            art = {'i': f'Arte do recurso {resource} com faixa do local {region} sobre o mapa.',
                   'e': [f'faixa {region}', f'arte {saque["resource_art"][resource]}'],
                   'a': f'compartilhada:{saque["resource_art"][resource]}'}
            back = f'V-SAQ ({region})'
        else:
            art = cis['arts'].get(key)
            back = f'V-{family}'
        if art is None:
            problems.append(f'sem arte: {key}')
            continue
        cards.append({
            'ids': [c['id'] for c in copies], 'nome': name, 'nome_sugerido': art.get('s'),
            'familia': family, 'categoria': FAMILY[family], 'copias': len(copies),
            'texto': copies[0]['text'], 'ilustracao': art['i'], 'elementos': art['e'],
            'verso': back, 'arte': art.get('a', 'exclusiva'), 'chave_arte': key,
            'origem': 'Cisterna 0.2 (certificada)'})

    # --- edição integral ---------------------------------------------------------------
    def add(ident, name, family, category, copies, text, art, back, key, engine):
        if art is None or ('i' not in art and 'a' not in art):
            problems.append(f'sem arte: {key}')
            return
        cards.append({'ids': ident, 'nome': name, 'nome_sugerido': art.get('nome_sugerido'),
                      'familia': family, 'categoria': category, 'copias': copies,
                      'texto': text, 'ilustracao': art.get('i', ''), 'elementos': art.get('e', []),
                      'verso': back, 'arte': art.get('a', 'exclusiva'), 'chave_arte': key,
                      'chave_motor': engine, 'origem': 'edição integral', 'obs': art.get('obs')})

    deck = Counter(community['event_deck'])
    seq = 0
    for key, count in deck.items():
        spec = integral['acontecimentos'][key]
        ids = [f'ZI-ACO-{seq + n + 1:02d}' for n in range(count)]
        seq += count
        add(ids, spec['nome'], 'ACO', 'Acontecimento de viagem', count, spec['texto'], spec,
            'V-ACO', f'ACO:{key}', key)
    deck = Counter(community['profession_deck'])
    seq = 0
    for key, count in deck.items():
        prof = community['professions'][key]
        spec = integral['profissoes'][key]
        ids = [f'ZI-PRF-{seq + n + 1:02d}' for n in range(count)]
        seq += count
        bonus = ', '.join(prof['bonus']) or 'nenhuma (faz qualquer função com rendimento normal)'
        add(ids, spec.get('nome', prof['name']), 'PRF', 'Profissão', count,
            f'Especialista em: {bonus}.', spec, 'V-PRF', f'PRF:{key}', key)
    for s in system['structures']:
        spec = integral['estruturas'][s['kind']]
        add([s['id']], s['name'], 'OBR', 'Estrutura regional', 1,
            structure_text(s['kind'], s, camp, True), spec, 'V-OBR', f'OBR:{s["kind"]}', s['kind'])
    seq = 0
    for kind, s in community['structures'].items():
        seq += 1
        spec = integral['estruturas'][kind]
        add([f'ZI-OBR-{seq:02d}'], spec.get('nome', s['name']), 'OBR', 'Obra da Comunidade', 1,
            structure_text(kind, s, camp, False), spec, 'V-OBR', f'OBR:{kind}', kind)
    for loc in system['locations']:
        spec = dict(integral['locais'][loc['id']])
        local = loc['name']
        spec.setdefault('i', world['locais'][local]['i'])
        spec.setdefault('e', world['locais'][local]['e'])
        loot = cost(loc['loot']) if loc['loot'] else 'sem saque comum'
        text = (f'Distância {loc["distance"]}; {loc["searches"]} busca(s); saque {loot}; '
                f'renovação {loc["renewal"]}.')
        know = [k for k, v in camp['knowledge'].items() if v['location'] == loc['id']]
        if know:
            text += f' 1ª busca: conhecimento {know[0]}.'
        add([loc['id']], local, 'LOC', 'Local regional', 1, text, spec, 'V-LOC',
            f'LOC:{loc["id"]}', loc['id'])
    for c in system['crises']:
        loss = cost(c['effect']['loss']) if c['effect']['loss'] else 'nada'
        text = (f'Alvo: {c["target"]}; dano {c["effect"]["damage"]}; perde {loss}; '
                f'intervalo {c["cooldown_days"]} dias.')
        add([c['id']], c['name'], 'CRI', 'Crise regional', 1, text, integral['crises'][c['id']],
            'V-CRI', f'CRI:{c["id"]}', c['id'])
    for c in last['cards']:
        req = ', '.join(f'{k} {v}' for k, v in c.get('requires', {}).items())
        eff = ', '.join(f'{e.get("key", e.get("item", e.get("value")))}' for e in c.get('effects', []))
        add([c['id']], c['name'], 'UTR', 'Última Transmissão', 1,
            f'Exige: {req or "—"}. Custo: {cost(c.get("cost", {})) if c.get("cost") else "—"}. '
            f'Efeito: {eff or "—"}.', integral['ultima_transmissao'][c['id']], 'V-UTR',
            f'UTR:{c["id"]}', c['id'])
    seq = 0
    for key, spec in integral['referencia'].items():
        seq += 1
        art = {'i': 'Sem ilustração: ícones e diagrama sobre prancheta.', 'e': ['ícones'],
               'a': 'compartilhada:diagrama'}
        add([f'ZI-REF-{seq:02d}'], spec['nome'], 'REF', 'Referência da comunidade', 1,
            spec['texto'], art, 'V-REF', f'REF:{key}', key)
    for key, k in camp['knowledge'].items():
        unlock = next(s for s, v in community['structures'].items() if v.get('knowledge') == key)
        add([key], k['name'], 'CON', 'Conhecimento', 1,
            f'1ª busca em {k["location"]}. Libera a obra {community["structures"][unlock]["name"]}.',
            integral['conhecimento'][key], 'V-CON', f'CON:{key}', key)

    # --- contagem de ilustrações --------------------------------------------------------
    total_cards = sum(c['copias'] for c in cards)
    exclusive = [c for c in cards if c['arte'] == 'exclusiva']
    people = world['people']
    heroes = {h['id']: h for h in catalog['heroes']}
    for hid in heroes:
        if hid not in people:
            problems.append(f'sem retrato: {hid}')
    for npc in system['npcs']:
        if (npc['source_hero_id'] or npc['id']) not in people:
            problems.append(f'sem retrato: {npc["id"]}')
    enemy_arts = sum(e['arts'] for e in world['enemies'].values())
    counts = OrderedDict([
        ('cartas', total_cards), ('artes_de_carta_exclusivas', len(exclusive)),
        ('retratos', len(people)), ('inimigos', enemy_arts),
        ('artes_chave_de_local', len(world['locais'])),
        ('pinturas_de_mapa', len({m['local'] for m in world['maps'].values()})),
        ('tabuleiros', len(world['boards'])), ('versos', len(style['backs']) + 5),
    ])
    counts['ilustracoes_total'] = (counts['artes_de_carta_exclusivas'] + counts['retratos']
                                   + counts['inimigos'] + counts['artes_chave_de_local']
                                   + counts['pinturas_de_mapa'])
    if total_cards != 400:
        problems.append(f'total de cartas {total_cards} ≠ 400')
    return {'style': style, 'cards': cards, 'counts': counts, 'heroes': catalog['heroes'],
            'npcs': system['npcs'], 'regional_heroes': [h['id'] for h in system['heroes']],
            'world': world, 'problems': problems}


def markdown(data: dict) -> str:
    style, counts = data['style'], data['counts']
    d = style['direction']
    lines = ['# Catálogo artístico — Sobreviventes: Zona Zero', '',
             'Para revisão antes da produção das artes. Gerado por `tools/art_catalog.py`: '
             'ids, nomes, quantidades e textos mecânicos vêm dos dados oficiais; descrição '
             'de arte vem de `data/art/`. Nenhuma mecânica foi alterada.', '',
             '## 1. Direção artística', '']
    titles = {'estilo': 'Estilo', 'ambiente': 'Ambiente', 'pessoas': 'Pessoas',
              'atmosfera': 'Atmosfera', 'luz': 'Luz', 'cartas': 'Cartas',
              'tabuleiros': 'Tabuleiros', 'uso_do_vermelho': 'Uso do vermelho',
              'proibicoes': 'Proibições'}
    for key, title in titles.items():
        lines.append(f'- **{title}:** {d[key]}')
    lines += ['- **Paleta:** ' + ', '.join(f'{k.replace("_", " ")} `{v}`'
                                            for k, v in d['paleta'].items()), '']
    lines += ['## 2. Quantas ilustrações', '', '| Item | Quantidade |', '|---|---|']
    labels = {'cartas': 'Cartas no total', 'artes_de_carta_exclusivas': 'Ilustrações de carta (exclusivas)',
              'retratos': 'Retratos de pessoas', 'inimigos': 'Ilustrações de inimigos',
              'artes_chave_de_local': 'Artes-chave de local', 'pinturas_de_mapa': 'Pinturas de mapa tático',
              'tabuleiros': 'Tabuleiros (layout)', 'versos': 'Versos (desenhos de verso)',
              'ilustracoes_total': '**Ilustrações a pintar**'}
    lines += [f'| {labels[k]} | {v} |' for k, v in counts.items()] + ['']
    lines += ['Cartas repetidas dividem a ilustração; Saque usa a arte do Recurso com faixa do '
              'local; Projeto usa a arte da Estrutura com sobreposição de croqui; Missão e '
              'Local usam a arte-chave do local; Ajuda e Referência são diagramas.', '']
    lines += ['## 3. Inconsistências documentadas (sem mudar mecânica)', '',
              '1. **Heróis e especialistas são as mesmas pessoas.** Os 15 especialistas '
              '(EXP-NPC-01..14) são os heróis ZC-HER-0011..0024 do catálogo quando não '
              'jogados; só Lúcia (EXP-NPC-15) não tem ficha de herói. São 25 pessoas, '
              'um retrato cada (não 39).',
              '2. **Dois sistemas de atributos.** O catálogo da Cisterna usa Corpo/Agilidade/'
              'Técnica; o motor regional usa Força, Agilidade, Percepção, Intelecto, Carisma e '
              'Resistência para os 10 heróis regionais. A ficha precisa decidir a apresentação '
              '(fila D-09).',
              '3. **Material, sucata e metal.** O mesmo recurso aparece como Material (Cisterna), '
              'sucata (motor) e metal (painel). Sugestão: “Material (sucata)” na carta e '
              '“Material” no painel.',
              '4. **Canteiro e Cerca ampliada** só existem no modelo abstrato; no acampamento em '
              'lotes não se imprimem (as 2 cartas continuam no inventário para o modelo antigo).',
              '5. **Bancada** é peça de missão da Cisterna (ZC-PEC-0006) e obra de conhecimento '
              '(Bancada de ferramentas): nomes sugeridos diferentes para não confundir.',
              '6. **Cartas sem id físico** (acontecimentos, profissões, obras da Comunidade, '
              'referência) recebem ids ZI-*; as chaves do motor não mudam.',
              '7. **Imagens conceituais:** nomes vistos nelas não são personagens oficiais; '
              'valem só os ids e nomes deste catálogo.', '']
    lines += ['## 4. Cartas (400) por família', '']
    by_family = OrderedDict()
    for card in data['cards']:
        by_family.setdefault((card['origem'], card['categoria']), []).append(card)
    for (origin, category), group in by_family.items():
        total = sum(c['copias'] for c in group)
        arts = sum(c['arte'] == 'exclusiva' for c in group)
        lines += [f'### {category} — {origin} ({total} cartas, {arts} ilustrações exclusivas)', '']
        for c in group:
            ids = c['ids'][0] if len(c['ids']) == 1 else f'{c["ids"][0]}…{c["ids"][-1]}'
            name = c['nome'] + (f' → **{c["nome_sugerido"]}**' if c.get('nome_sugerido') else '')
            lines += [f'**{ids}** — {name} · {c["familia"]} · ×{c["copias"]} · verso {c["verso"]} · '
                      f'arte {c["arte"]}',
                      f'- Texto: {c["texto"]}',
                      f'- Ilustração: '
                      + ('variação opcional sobre a arte compartilhada — '
                         if c['arte'] != 'exclusiva' and c['chave_arte'][:4] in ('OBR:', 'PRO:')
                         else '') + c['ilustracao'],
                      f'- Obrigatório: {", ".join(c["elementos"])}']
            if c.get('obs'):
                lines.append(f'- Obs.: {c["obs"]}')
            lines.append('')
    lines += ['## 5. Pessoas (25 retratos)', '', '| Id | Nome | Profissão | Uso | Retrato |',
              '|---|---|---|---|---|']
    npc_of = {n['source_hero_id']: n['id'] for n in data['npcs'] if n['source_hero_id']}
    people = data['world']['people']
    for h in data['heroes']:
        uses = ['herói inicial' if h.get('initial') else 'herói resgatável']
        if h['id'] in data['regional_heroes']:
            uses.append('regional')
        if h['id'] in npc_of:
            uses.append(f'especialista {npc_of[h["id"]]}')
        lines.append(f'| {h["id"]} | {h["name"]} | {h["profession"]} | {", ".join(uses)} | '
                     f'{people[h["id"]]["i"]} |')
    lucia = next(n for n in data['npcs'] if n['id'] == 'EXP-NPC-15')
    lines += [f'| EXP-NPC-15 | {lucia["name"]} | {lucia["profession"]} | só especialista | '
              f'{people["EXP-NPC-15"]["i"]} |', '']
    w = data['world']
    lines += ['## 6. Inimigos', '', '| Id | Nome | Ilustrações | Descrição |', '|---|---|---|---|']
    lines += [f'| {k} | {v["nome"]} | {v["arts"]} | {v["i"]} |' for k, v in w['enemies'].items()]
    lines += ['', '## 7. Locais e mapas', '', '| Local | Arte-chave |', '|---|---|']
    lines += [f'| {k} | {v["i"]} |' for k, v in w['locais'].items()]
    lines += ['', '| Mapa | Local | Uso |', '|---|---|---|']
    lines += [f'| {k} | {v["local"]} | {v["uso"]} |' for k, v in w['maps'].items()]
    lines += ['', w['map_rules'], '', '## 8. Construções (peças de lote) e tabuleiros', '',
              w['pieces']['note'], '',
              f'- Barraca familiar: {w["pieces"]["barraca_familiar"]["i"]}']
    lines += [f'- {k}: {v}' for k, v in w['boards'].items()]
    lines += ['', '## 9. Marcadores', '', '| Marcador | Qtd. | Arte |', '|---|---|---|']
    lines += [f'| {k} | {v["qtd"]} | {v["i"]} |' for k, v in w['tokens'].items()]
    lines += ['', '## 10. Versos', '', '| Verso | Desenho |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in style['backs'].items()]
    lines += ['', 'V-SAQ tem 6 variações (uma por local).', '', '## 11. Molduras', '']
    lines += [f'- **{k}:** {v}' for k, v in style['frames'].items()]
    return '\n'.join(lines).rstrip('\n') + '\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    data = build()
    md = markdown(data)
    payload = {k: data[k] for k in ('counts', 'cards')}
    text = json.dumps(payload, ensure_ascii=False, indent=1) + '\n'
    problems = list(data['problems'])
    if args.check:
        if not OUT_MD.exists() or OUT_MD.read_text(encoding='utf-8') != md:
            problems.append('CATALOGO_ARTISTICO.md desatualizado (rode art_catalog.py)')
        if not OUT_JSON.exists() or OUT_JSON.read_text(encoding='utf-8') != text:
            problems.append('catalogo_artistico.json desatualizado (rode art_catalog.py)')
    else:
        OUT_MD.write_text(md, encoding='utf-8')
        OUT_JSON.write_text(text, encoding='utf-8')
    for problem in problems:
        print('ERRO:', problem, file=sys.stderr)
    print('catálogo artístico:', json.dumps(data['counts'], ensure_ascii=False))
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
