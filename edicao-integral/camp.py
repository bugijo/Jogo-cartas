"""Acampamento em lotes (D-24..D-26): grade física, barracas, horta, crise.

Modo da Comunidade (`RULES['camp']['on']`): o estado mora em
`world.community['camp']`; None mantém o modelo abstrato anterior (terreno 7,
camas 8, depósito único). Como `community`, não importa `system`.

Mesa: um tabuleiro 4×4 de lotes; o nível N do acampamento abre as linhas e
colunas 1..N+1 (2×2, 3×3, 4×4). Cada lote mostra 1–2 símbolos de categoria e
recebe uma construção (ou até 2 barracas). O painel mostra comida, água,
madeira e metal com o limite atual, a Crise 0–10 e as camas.
"""
from __future__ import annotations

import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent / 'data/community.json')
                   .read_text(encoding='utf-8'))['camp']
GRID = RULES['grid']
CATEGORY = RULES['category']
CRISIS = RULES['crisis']
HORTA = RULES['horta']
KNOWLEDGE = RULES['knowledge']
EFFECTS = RULES['effects']
KEYS = {'level', 'lots', 'pending', 'tents', 'horta_ready', 'crisis', 'deficit_prev',
        'knowledge', 'rain'}


def on(world) -> bool:
    return world.community is not None and world.community.get('camp') is not None


def _state(world) -> dict:
    return world.community['camp']


def lot_level(lot_id: str) -> int:
    row, col = int(lot_id[1]), int(lot_id[3])
    return max(1, max(row, col) - 1)


def open_lots(world) -> list[str]:
    level = _state(world)['level']
    return [lot for lot in GRID if lot_level(lot) <= level]


def _humans(world) -> int:
    return world.residents


# --- estado inicial --------------------------------------------------------------
def new_camp(world, ready_horta: int = 0) -> dict:
    """Clareira 2×2 (fogueira e estoque na borda) e as barracas da evacuação.

    Barracas: 1 para cada 2 humanos (arredondado para cima). Lote livre que
    sobrar recebe a Horta trazida da Cisterna (`ready_horta`), já plantada.
    """
    state = {'level': 1, 'lots': {lot: [] for lot in GRID}, 'pending': {}, 'tents': {},
             'horta_ready': {}, 'crisis': 0, 'deficit_prev': False, 'knowledge': [],
             'rain': False}
    world.community['camp'] = state
    people = -(-_humans(world) // RULES['start_tent_people'])
    state['tents']['barraca'] = people
    pitch_tents(world)
    for _ in range(ready_horta):
        lot = free_lot(world, 'horta')
        if lot is None:
            state['tents']['sementes'] = state['tents'].get('sementes', 0) + 1
            continue
        state['lots'][lot].append('horta')
        state['horta_ready'][lot] = world.day
    return state


def validate(world) -> None:
    state = world.community.get('camp')
    if state is None:
        return
    ok = isinstance(state, dict) and set(state) == KEYS
    ok = ok and 1 <= state['level'] <= 3 and 0 <= state['crisis'] <= CRISIS['max']
    ok = ok and set(state['lots']) == set(GRID)
    for lot, items in (state['lots'].items() if ok else ()):
        items = items + [k for k, l in state['pending'].items() if l == lot]
        if items and lot_level(lot) > state['level']:
            ok = False
        kinds = set(items)
        if len(kinds) > 1 or len(items) > RULES['stack'].get(items[0] if items else '', 1):
            ok = False
    if not ok:
        raise ValueError('Estado do acampamento inválido')


# --- lotes ------------------------------------------------------------------------
def category(kind: str) -> str | None:
    return CATEGORY.get(kind)


def _used(world, lot: str) -> list[str]:
    state = _state(world)
    return state['lots'][lot] + [k for k, l in state['pending'].items() if l == lot]


def free_lot(world, cat: str, kind: str | None = None) -> str | None:
    """Primeiro lote aberto que aceita a categoria (barraca empilha até 2)."""
    stack = RULES['stack'].get(kind or '', 1)
    # Prefere lotes de um símbolo só, para não gastar lotes versáteis à toa.
    candidates = sorted(open_lots(world), key=lambda lot: (len(GRID[lot]), lot))
    for lot in candidates:
        items = _used(world, lot)
        if cat not in GRID[lot]:
            continue
        if not items or (kind and set(items) == {kind} and len(items) < stack):
            return lot
    return None


def free_lots(world) -> int:
    return sum(not _used(world, lot) for lot in open_lots(world))


def claim(world, kind: str, lot: str | None = None) -> str | None:
    """Reserva o lote no início da obra. None: obra sem lote (cozinha, níveis 2)."""
    cat = category(kind)
    if cat is None:
        return None
    state = _state(world)
    if lot is None:
        lot = free_lot(world, cat, kind)
    else:
        items = _used(world, lot)
        if (lot not in open_lots(world) or cat not in GRID[lot]
                or (items and (set(items) != {kind}
                               or len(items) >= RULES['stack'].get(kind, 1)))):
            lot = None
    if lot is None:
        raise ValueError('Sem lote livre dessa categoria: amplie o acampamento')
    state['pending'][kind] = lot
    return lot


def finish(world, kind: str) -> str | None:
    """Obra concluída: a peça entra no lote reservado."""
    state = _state(world)
    lot = state['pending'].pop(kind, None)
    if lot is None:
        return None
    state['lots'][lot].append(kind)
    if kind == 'horta':
        state['horta_ready'][lot] = world.day + HORTA['grow_days']
    return lot


def can_claim(world, kind: str) -> bool:
    cat = category(kind)
    return cat is None or free_lot(world, cat, kind) is not None


def built(world, kind: str) -> int:
    state = _state(world)
    return sum(items.count(kind) for items in state['lots'].values())


def pitch_tents(world) -> list[str]:
    """Barracas guardadas vão para lotes livres (montar não custa trabalho)."""
    state = _state(world)
    pitched = []
    for kind in ('barraca_familiar', 'barraca'):
        while state['tents'].get(kind, 0) > 0:
            lot = free_lot(world, 'barraca', kind)
            if lot is None:
                break
            state['lots'][lot].append(kind)
            state['tents'][kind] -= 1
            pitched.append(lot)
        if state['tents'].get(kind) == 0:
            del state['tents'][kind]
    return pitched


def expand(world, level: int) -> None:
    state = _state(world)
    state['level'] = max(state['level'], level)
    pitch_tents(world)


# --- capacidades ------------------------------------------------------------------
def beds(world) -> int:
    state = _state(world)
    total = sum(RULES['beds'].get(kind, 0) for items in state['lots'].values()
                for kind in items)
    if 'alojamento2' in world.community['built']:
        total += RULES['beds']['alojamento2']
    return total


def capacity(world, resource: str) -> int:
    spec = RULES['storage']
    if resource == 'food':
        food = spec['food']
        return (food['base'] + food['storage'] * ('storage' in world.structures)
                + food['deposito2'] * ('deposito2' in world.community['built']))
    if resource == 'water':
        water = spec['water']
        return water['base'] + water['reservoir'] * ('reservoir' in world.structures)
    if resource in ('wood', 'scrap'):
        return spec[resource]
    return 99  # remédio, munição, combustível, peças: cartas, sem trilha


# --- horta por lotes -------------------------------------------------------------
def ready_horta(world) -> list[str]:
    state = _state(world)
    return sorted(lot for lot, day in state['horta_ready'].items() if day <= world.day)


def tend(world, workers: list[str], specialist, rng) -> dict:
    """Trabalhadores da horta: cada um cuida de 2 lotes (agricultor 4).

    Cada lote cuidado e regado dá `food_per_lot` porções. Dia sem chuva (D6 do
    amanhecer 1–3) gasta 1 água a cada 2 lotes (arredondado para cima). D6 = 1
    de um trabalhador: praga, 1 porção a menos.
    """
    lots = ready_horta(world)
    rain = _state(world)['rain']
    out = []
    for person in workers:
        cap = HORTA['specialist_lots'] if specialist(person) else HORTA['lots_per_worker']
        mine = lots[:cap]
        lots = lots[cap:]
        water_need = 0 if rain else -(-len(mine) // HORTA['lots_per_water'])
        water = min(water_need, world.stock['water'])
        watered = len(mine) if rain else min(len(mine), water * HORTA['lots_per_water'])
        world.stock['water'] -= water
        roll = rng.randint(1, 6)
        bonus = EFFECTS['composteira_food'] if has(world, 'composteira') and watered else 0
        food = watered * HORTA['food_per_lot'] + bonus
        if roll <= HORTA['pest_at']:
            food = max(0, food - 1)
        out.append({'person': person, 'lots': len(mine), 'watered': watered, 'rain': rain,
                    'water': water, 'roll': roll, 'food': food,
                    'stored': world.deposit('food', food)})
    return {'workers': out}


# --- conhecimento -------------------------------------------------------------------
def find_knowledge(world, location_id: str) -> str | None:
    """Primeira busca bem-sucedida no local: a carta de conhecimento do local."""
    if not on(world):
        return None
    state = _state(world)
    card = next((k for k, spec in KNOWLEDGE.items()
                 if spec['location'] == location_id and k not in state['knowledge']), None)
    if card:
        state['knowledge'].append(card)
        world.log.append({'day': world.day, 'action': 'knowledge_found', 'card': card,
                          'location': location_id})
    return card


def has(world, kind: str) -> bool:
    """Melhoria da Comunidade pronta (só no acampamento em lotes)."""
    return on(world) and kind in world.community['built']


# --- crise alimentar 0–10 -------------------------------------------------------
def band(world) -> str:
    level = _state(world)['crisis']
    if level >= CRISIS['max']:
        return 'colapso'
    if level >= CRISIS['grave']:
        return 'grave'
    if level >= CRISIS['moderate']:
        return 'moderada'
    return 'leve' if level else 'calma'


def raise_crisis(world, amount: int, reason: str) -> None:
    state = _state(world)
    state['crisis'] = min(CRISIS['max'], state['crisis'] + amount)
    world.log.append({'day': world.day, 'action': 'crisis', 'reason': reason,
                      'change': amount, 'crisis': state['crisis']})


def night(world, people: dict, fed: dict) -> dict:
    """Depois da refeição: déficit proporcional sobe a Crise; noite servida baixa.

    Falta para até metade dos humanos (arredondado para cima): +1; mais que
    isso: +2; `repeat` soma na noite seguinte com falta (0 na regra adotada). Todos servidos: −1, ou −2 se o estoque
    de comida ainda cobre a próxima noite. Mais de 2 pessoas sem cama: +1.
    """
    state = _state(world)
    humans = [pid for pid, p in people.items() if p.get('kind') != 'dog']
    unfed = [pid for pid in humans if pid not in fed['food'] or pid not in fed['water']]
    before = state['crisis']
    change = 0
    if unfed:
        small = max(1, -(-len(humans) // CRISIS['small_share']))
        change += CRISIS['small'] if len(unfed) <= small else CRISIS['large']
        if state['deficit_prev']:
            change += CRISIS['repeat']
    else:
        reserve = world.stock['food'] >= len(people) and world.stock['water'] >= len(people)
        change -= CRISIS['recover_reserve'] if reserve else CRISIS['recover']
    unhoused = max(0, world.residents - world.beds)
    if unhoused > CRISIS['unhoused_over']:
        change += 1
    state['crisis'] = max(0, min(CRISIS['max'], before + change))
    state['deficit_prev'] = bool(unfed)
    if state['crisis'] >= CRISIS['max']:
        world.partial_defeat = True
    return {'unfed_humans': len(unfed), 'unhoused': unhoused, 'crisis': state['crisis'],
            'change': state['crisis'] - before, 'band': band(world)}


def recovery_slots(world) -> int | None:
    """Só quem tem cama recupera Vida; na crise grave, ninguém recupera."""
    if not on(world):
        return None
    if _state(world)['crisis'] >= CRISIS['grave']:
        return 0
    return world.beds


def conflict(world, rng) -> dict | None:
    """Amanhecer em crise grave: D6 ≤ 2, briga e desvio: perde 1 material."""
    if _state(world)['crisis'] < CRISIS['grave']:
        return None
    roll = rng.randint(1, 6)
    lost = None
    if roll <= CRISIS['conflict_at']:
        lost = max(('wood', 'scrap'), key=lambda r: (world.stock[r], r))
        if world.stock[lost]:
            world.stock[lost] -= 1
        else:
            lost = None
    return {'roll': roll, 'lost': lost}


# --- defesa final (D-23) --------------------------------------------------------------
def defense_shooters(world) -> list[str]:
    """Apoio do acampamento na defesa final: Vigia e guardas aptos atiram 1 por rodada."""
    rule = RULES['defense_support']
    if not on(world) or not rule['on']:
        return []
    shooters = ['vigia'] * rule['watch'] if 'watch' in world.structures else []
    import community  # tardio: community importa este módulo
    away = community.away(world)
    guards = [p for p in sorted(world.community['professions'])
              if world.community['professions'][p] == 'guarda' and p not in away
              and community.able(world, p)]
    return shooters + guards[:rule['guards']]


def heavy(kind: str, spec: dict) -> bool:
    return bool(spec.get('heavy')) or kind in RULES['heavy_kinds']


def work_allowed(world, kind: str, spec: dict) -> str | None:
    """Obra pesada: exige ração de obra no estoque e Crise abaixo de moderada."""
    if not on(world) or not heavy(kind, spec):
        return None
    if _state(world)['crisis'] >= CRISIS['moderate']:
        return 'Crise moderada: obras pesadas paradas'
    if world.stock['food'] < RULES['work_ration']:
        return 'Obra pesada exige ração de obra'
    return None
