"""Regras Comunidade: trabalhadores, profissões, expedições automáticas.

Aprovadas pelo criador na Missão Mestre (2026-10-30); números provisórios em
`data/community.json`. O estado mora em `World.community` (None = regras
desligadas: saves e replays certificados ficam idênticos). Este módulo não
importa `system`: recebe o World e usa só seus campos e métodos públicos.

Relógio: o mesmo dia regional. Amanhecer → trabalhos e viagens planejados →
expedição tática dos heróis → `day_work` (cozinha, obras) → refeição →
`after_meal` (cuidados) → `dawn` do dia seguinte (retornos, reservas, chuva,
armadilhas, carne que estraga).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

RULES = json.loads((Path(__file__).parent / 'data/community.json').read_text(encoding='utf-8'))
PROFESSIONS = RULES['professions']
ACTIVITIES = RULES['activities']
TRIPS = RULES['trips']
STRUCTURES = RULES['structures']
CAMP_JOBS = ('cozinhar', 'obra', 'cuidar', 'vigiar', 'armadilha')
KEYS = {'rng', 'professions', 'jobs', 'trips', 'pools', 'meat', 'built', 'projects',
        'deck', 'traps', 'pista_used', 'trip_seq'}


def _lists(value):
    return [_lists(item) for item in value] if isinstance(value, (list, tuple)) else value


def _tuples(value):
    return tuple(_tuples(item) for item in value) if isinstance(value, list) else value


def _rng(state: dict) -> random.Random:
    rng = random.Random()
    rng.setstate(_tuples(state['rng']))
    return rng


def _save_rng(state: dict, rng: random.Random) -> None:
    state['rng'] = _lists(rng.getstate())


def new_state(world) -> dict:
    """Estado inicial na chegada ao regional: sorteia profissões dos adultos."""
    rng = random.Random(world.seed * 7919 + 17)
    deck = list(RULES['profession_deck'])
    rng.shuffle(deck)
    professions = {}
    for index, person in enumerate(p for p in world.continuity_people if p['kind'] == 'adult'):
        professions[person['id']] = deck[index % len(deck)]
    events = list(RULES['event_deck'])
    rng.shuffle(events)
    state = {'professions': professions, 'jobs': {}, 'trips': [], 'meat': [],
             'pools': {name: spec['start'] for name, spec in RULES['pools'].items()},
             'built': [], 'projects': {}, 'deck': {'order': events, 'pos': 0},
             'traps': [], 'pista_used': False, 'trip_seq': 0}
    _save_rng(state, rng)
    return state


def validate(world) -> None:
    state = world.community
    if state is None:
        return
    ok = isinstance(state, dict) and set(state) == KEYS
    ok = ok and all(prof in PROFESSIONS for prof in state['professions'].values())
    ok = ok and set(state['pools']) == set(RULES['pools']) and all(
        isinstance(v, int) and 0 <= v <= RULES['pools'][k]['max']
        for k, v in state['pools'].items())
    ok = ok and all(job.get('job') in CAMP_JOBS for job in state['jobs'].values())
    ok = ok and all(trip['activity'] in ACTIVITIES for trip in state['trips'])
    ok = ok and sum(m['units'] for m in state['meat']) <= RULES['meat']['track']
    ok = ok and set(state['built']) <= set(STRUCTURES) and set(state['projects']) <= set(STRUCTURES)
    ok = ok and len(state['traps']) <= RULES['traps']['max']
    if not ok:
        raise ValueError('Estado da Comunidade inválido')


# --- pessoas ---------------------------------------------------------------------
def away(world) -> set[str]:
    return {trip['worker'] for trip in (world.community or {}).get('trips', [])}


def profession(world, person_id: str) -> str:
    state = world.community
    if person_id in state['professions']:
        return state['professions'][person_id]
    npc = world.npcs.get(person_id)
    if npc is not None:
        from system import NPCS  # import tardio: system importa este módulo
        return RULES['npc_professions'].get(NPCS[person_id]['job'], 'comum')
    return 'comum'


def specialist(world, person_id: str, activity: str) -> bool:
    return activity in PROFESSIONS[profession(world, person_id)]['bonus']


def busy(world) -> set[str]:
    state = world.community or {}
    out = set(world.worked_today) | set(world.departed_today) | away(world)
    out |= set(state.get('jobs', {}))
    camp = world.regional_camp or {}
    out |= set((camp.get('forage') or {}).get('workers', []))
    out |= set((camp.get('garden_build') or {}).get('workers', []))
    if (world.continuity_garden or {}).get('worker'):
        out.add(world.continuity_garden['worker'])
    return out


def _person(world, person_id: str) -> dict | None:
    if person_id in world.heroes:
        return world.heroes[person_id]
    if person_id in world.npcs:
        return world.npcs[person_id]
    return next((p for p in world.continuity_people if p['id'] == person_id), None)


def _wounds(world, person_id: str) -> int:
    person = _person(world, person_id)
    if person_id in world.heroes or 'health' in person:
        return 3 - person['health']
    return person.get('wounds', 0)


def able(world, person_id: str, max_wounds: int = 2) -> bool:
    """Apto a trabalhar hoje: sem fome/sede, fadiga < 3, ferimentos ≤ limite."""
    person = _person(world, person_id)
    if person is None or person_id in busy(world):
        return False
    if person_id in world.heroes:
        if person['location'] != 'camp':
            return False
    elif person_id in world.npcs:
        if person.get('location') != 'camp' or person.get('job') is not None:
            return False  # especialista com trabalho fixo já produz
    elif person['kind'] != 'adult':
        return False
    return (not person.get('hungry') and not person.get('thirsty')
            and person.get('fatigue', 0) < 3 and _wounds(world, person_id) <= max_wounds)


def workers(world) -> list[str]:
    """Trabalhadores da comunidade (não heróis), em ordem estável."""
    ids = [p['id'] for p in world.continuity_people if p['kind'] == 'adult']
    ids += sorted(n for n, s in world.npcs.items() if s.get('location') == 'camp'
                  and s.get('job') is None)
    return ids


def _require_dawn(world) -> None:
    if world.community is None:
        raise ValueError('Regras Comunidade desligadas nesta campanha')
    if world.partial_defeat or world.expeditions or world.daily_expeditions:
        raise ValueError('Trabalhos e viagens se planejam no amanhecer, antes da expedição')


# --- chegada de sobreviventes -----------------------------------------------------
def join(world, person_id: str) -> dict:
    """Resgate: profissão (NPC usa a sua; demais sorteiam) e bagagem (D6)."""
    state = world.community
    rng = _rng(state)
    if person_id not in world.npcs and person_id not in state['professions']:
        state['professions'][person_id] = rng.choice(RULES['profession_deck'])
    roll = rng.randint(1, 6)
    _save_rng(state, rng)
    stored = {res: world.deposit(res, amount)
              for res, amount in RULES['baggage'][str(roll)].items()}
    receipt = {'day': world.day, 'action': 'community_join', 'person': person_id,
               'profession': profession(world, person_id), 'baggage_roll': roll,
               'baggage': stored}
    world.log.append(receipt)
    return receipt


def arrival_kits(world) -> dict:
    """Recursos iniciais aleatórios dos heróis: cada um rola a tabela de bagagem.

    Aplicado uma vez, na chegada ao regional (a Cisterna não muda).
    """
    state = world.community
    rng = _rng(state)
    kits = {}
    for hero in sorted(world.heroes):
        roll = rng.randint(1, 6)
        kits[hero] = {'roll': roll, 'stored': {res: world.deposit(res, amount) for res, amount
                                               in RULES['baggage'][str(roll)].items()}}
    _save_rng(state, rng)
    return kits


def evacuation_supply(world) -> dict:
    """Suprimento de evacuação: a Ponte entrega 1 ração por consumidor, uma vez.

    Decisão do diretor (2026-10-30): o grupo chega com comida para menos de uma
    noite; sem esta ração as viagens não voltam antes do Colapso.
    """
    amount = RULES['evacuation_supply']['food_per_consumer'] * len(world.meal_people())
    return {'food': amount, 'stored': world.deposit('food', amount)}


# --- trabalhos do acampamento -------------------------------------------------------
def assign_job(world, person_id: str, job: str, target: str | None = None) -> None:
    """Uma função por pessoa por dia, sem supervisão de herói."""
    _require_dawn(world)
    if job not in CAMP_JOBS:
        raise ValueError('Trabalho desconhecido')
    if not able(world, person_id):
        raise ValueError('Trabalhador indisponível hoje')
    state = world.community
    if job == 'obra':
        if target not in world.projects and target not in state['projects']:
            raise ValueError('Sem obra iniciada para esse alvo')
    if job == 'cozinhar' and not state['meat']:
        raise ValueError('Sem carne para cozinhar')
    if job == 'armadilha':
        if len(state['traps']) >= RULES['traps']['max']:
            raise ValueError('Limite de armadilhas')
        if world.stock['wood'] < RULES['traps']['cost_wood']:
            raise ValueError('Armadilha exige madeira')
    state['jobs'][person_id] = {'job': job, 'target': target}
    if person_id in world.heroes:
        world.worked_today.append(person_id)


def start_build(world, kind: str) -> None:
    """Obra comunitária (coletor de chuva, cozinha): paga o custo na largada."""
    _require_dawn(world)
    state = world.community
    if kind not in STRUCTURES or kind in state['built'] or kind in state['projects']:
        raise ValueError('Obra comunitária indisponível')
    cost = STRUCTURES[kind]['cost']
    if any(world.stock[res] < n for res, n in cost.items()):
        raise ValueError('Recursos insuficientes para a obra')
    for res, n in cost.items():
        world.stock[res] -= n
    state['projects'][kind] = 0
    world.log.append({'day': world.day, 'action': 'community_build_start', 'kind': kind,
                      'paid': dict(cost)})


def _cook(world, person_id: str) -> dict:
    state = world.community
    rules = RULES['cooking']
    capacity = (rules['meat_per_job'] + (rules['specialist_extra']
                if specialist(world, person_id, 'cozinhar') else 0)
                + (rules['kitchen_extra'] if 'cozinha' in state['built'] else 0))
    meat = 0
    while capacity and state['meat']:
        lot = state['meat'][0]
        lot['units'] -= 1
        meat += 1
        capacity -= 1
        if lot['units'] == 0:
            state['meat'].pop(0)
    wood = 0
    if 'cozinha' in state['built']:
        portions = RULES['meat']['portions_cooked']
    elif world.stock['wood'] >= 1:
        world.stock['wood'] -= 1
        wood = 1
        portions = RULES['meat']['portions_cooked']
    else:
        portions = RULES['meat']['portions_improvised']
    food = meat * portions
    return {'meat': meat, 'wood': wood, 'food': food, 'stored': world.deposit('food', food)}


def _build(world, person_id: str, target: str) -> dict:
    state = world.community
    units = 1 + (1 if specialist(world, person_id, 'obra') else 0)
    if target in state['projects']:
        state['projects'][target] += units
        done = state['projects'][target] >= STRUCTURES[target]['work']
        if done:
            del state['projects'][target]
            state['built'].append(target)
        return {'target': target, 'units': units, 'done': done}
    if target not in world.projects:
        return {'target': target, 'units': 0, 'done': False, 'reason': 'sem obra'}
    if person_id in world.heroes:
        world.worked_today.remove(person_id)  # work_project registra o herói de novo
        done = world.work_project(target, units, person_id)
    else:
        done = world.work_project(target, units)
    return {'target': target, 'units': units, 'done': done}


def day_work(world) -> dict | None:
    """Fim do dia, antes da refeição: resolve cozinha, obras e armadilhas."""
    state = world.community
    if state is None or not state['jobs']:
        return None
    out = {}
    for person_id, job in sorted(state['jobs'].items()):
        if person_id not in world.worked_today:
            world.worked_today.append(person_id)  # sem recuperação §25 hoje
        kind = job['job']
        if kind == 'cozinhar':
            out.setdefault('cook', []).append({'person': person_id, **_cook(world, person_id)})
        elif kind == 'obra':
            out.setdefault('build', []).append({'person': person_id,
                                                **_build(world, person_id, job['target'])})
        elif kind == 'armadilha':
            world.stock['wood'] -= RULES['traps']['cost_wood']
            state['traps'].append({'set_day': world.day})
            out['traps_set'] = out.get('traps_set', 0) + 1
    return out or None


def after_meal(world, people: dict) -> dict | None:
    """Depois da refeição: cuidados do enfermeiro (só em quem comeu e bebeu)."""
    state = world.community
    if state is None:
        return None
    healed = []
    for person_id, job in sorted(state['jobs'].items()):
        if job['job'] != 'cuidar':
            continue
        care = RULES['care']
        slots = care['specialist_people'] if specialist(world, person_id, 'cuidar') else care['people']
        candidates = sorted((pid for pid, p in people.items() if pid != person_id
                             and p.get('kind') != 'dog' and not p.get('hungry')
                             and not p.get('thirsty') and _wounds(world, pid) > 0
                             and pid not in healed),
                            key=lambda pid: (-_wounds(world, pid), pid))
        for pid in candidates[:slots]:
            person = people[pid]
            if pid in world.heroes:
                world._set_hero_health(pid, min(3, person['health'] + 1))
            elif 'health' in person:
                person['health'] = min(3, person['health'] + 1)
                person['wounds'] = 3 - person['health']
            else:
                person['wounds'] = max(0, person['wounds'] - 1)
            healed.append(pid)
    return {'healed': healed} if healed else None


def guard_roll(world) -> dict | None:
    """Vigia: rola antes da crise da noite; com sucesso a crise não acontece."""
    state = world.community
    guards = [pid for pid, job in sorted((state or {}).get('jobs', {}).items())
              if job['job'] == 'vigiar']
    if not guards:
        return None
    rng = _rng(state)
    rolls = {pid: rng.randint(1, 6) for pid in guards}
    _save_rng(state, rng)
    need = {pid: RULES['guard']['specialist_prevent_at'] if specialist(world, pid, 'vigiar')
            else RULES['guard']['prevent_at'] for pid in guards}
    return {'rolls': rolls, 'prevents': any(rolls[p] >= need[p] for p in guards)}


# --- viagens automáticas --------------------------------------------------------
def send_trip(world, person_id: str, activity: str, days: int,
              rations: int | None = None) -> dict:
    """Trabalhador sai sozinho por `days` dias; volta no amanhecer do dia + days.

    Ração: 1 comida + 1 água por dia levadas do depósito (no máximo `days`).
    Dia sem ração custa 2 pontos do rendimento. Fora do abrigo a pessoa não
    entra na refeição do abrigo (sem cobrança dupla).
    """
    _require_dawn(world)
    if person_id in world.heroes and not TRIPS.get('heroes_allowed'):
        raise ValueError('Heróis fazem expedições táticas, não viagens automáticas')
    if activity not in ACTIVITIES:
        raise ValueError('Atividade desconhecida')
    if (not isinstance(days, int) or isinstance(days, bool)
            or not TRIPS['min_days'] <= days <= TRIPS['max_days']):
        raise ValueError('Duração fora do permitido')
    if ((person_id not in workers(world) and person_id not in world.heroes)
            or not able(world, person_id, TRIPS['depart_max_wounds'])):
        raise ValueError('Trabalhador indisponível para viagem')
    top = min(days, world.stock['food'], world.stock['water'])
    rations = top if rations is None else rations
    if not isinstance(rations, int) or not 0 <= rations <= top:
        raise ValueError('Ração inválida')
    world.stock['food'] -= rations
    world.stock['water'] -= rations
    state = world.community
    state['trip_seq'] += 1
    trip = {'id': state['trip_seq'], 'worker': person_id, 'activity': activity,
            'days': days, 'depart': world.day, 'return_day': world.day + days,
            'rations': rations, 'delayed': False}
    state['trips'].append(trip)
    world.log.append({'day': world.day, 'action': 'worker_trip_depart', **trip})
    return dict(trip)


def _draw(state: dict, rng: random.Random) -> str:
    deck = state['deck']
    if deck['pos'] >= len(deck['order']):
        deck['order'] = list(RULES['event_deck'])
        rng.shuffle(deck['order'])
        deck['pos'] = 0
    card = deck['order'][deck['pos']]
    deck['pos'] += 1
    return card


def _wound(world, person_id: str) -> None:
    person = _person(world, person_id)
    if person_id in world.heroes:
        world._set_hero_health(person_id, max(0, person['health'] - 1))
    elif 'health' in person:
        person['health'] = max(0, person['health'] - 1)
        person['wounds'] = 3 - person['health']
    else:
        person['wounds'] = min(3, person.get('wounds', 0) + 1)


def _resolve_trip(world, trip: dict, rng: random.Random) -> dict | None:
    state = world.community
    spec = ACTIVITIES[trip['activity']]
    cards = [_draw(state, rng)]
    if trip['days'] >= TRIPS['long_trip_days']:
        cards.append(_draw(state, rng))
    if trip['activity'] in TRIPS['dangerous']:
        cards.append(_draw(state, rng))
    if 'atraso' in cards and not trip['delayed']:
        trip['delayed'] = True
        trip['return_day'] += 1
        return None  # volta no próximo amanhecer; sorteia de novo então
    worker = trip['worker']
    bonus = TRIPS['specialist_bonus'] if specialist(world, worker, trip['activity']) else 0
    roll = rng.randint(1, 6)
    nights = trip['days'] + (1 if trip['delayed'] else 0)
    points = (roll + bonus) * trip['days']
    points -= TRIPS['unsupplied_day_cost'] * (nights - trip['rations'])
    effects = {}
    for card in cards:
        if card == 'abundancia':
            extra = rng.randint(1, 6)
            points += extra
            effects['abundancia'] = extra
        elif card == 'chuva':
            points -= 2
            effects['chuva'] = -2
    person = _person(world, worker)
    if points < 0:
        # Comeu o que achou e não bastou: volta com fome e sede.
        person['hungry'] = person['thirsty'] = True
        person['streak'] = person.get('streak', 0) + 1
        points = 0
    units = min(points // spec['points_per_unit'], TRIPS['capacity'])
    if spec['pool'] is not None:
        units = min(units, state['pools'][spec['pool']])
        state['pools'][spec['pool']] -= units
    found = units
    for card in cards:
        if card == 'ferimento':
            _wound(world, worker)
            effects['ferimento'] = True
        elif card == 'perda':
            effects['perda'] = units - units // 2
            units //= 2
        elif card == 'equipamento':
            if world.stock['scrap']:
                world.stock['scrap'] -= 1
                effects['equipamento'] = 'scrap'
            else:
                units = max(0, units - 1)
                effects['equipamento'] = 'unit'
        elif card == 'zumbis':
            danger = rng.randint(1, 6)
            if danger <= 2:
                _wound(world, worker)
                units //= 2
            elif danger <= 4:
                units = max(0, units - 1)
            effects['zumbis'] = danger
        elif card == 'descoberta':
            effects['descoberta'] = world.deposit('scrap', 1)
        elif card == 'pista' and not state['pista_used']:
            state['pista_used'] = True
            world.clues += 1
            effects['pista'] = 1
    delivered = _deliver(world, spec['output'], units)
    return {'trip': trip['id'], 'worker': worker, 'activity': trip['activity'],
            'days': trip['days'], 'roll': roll, 'bonus': bonus, 'points': points,
            'found': found, 'units': units, 'cards': cards, 'effects': effects,
            'delivered': delivered}


def _deliver(world, output: str, units: int) -> dict:
    state = world.community
    if units <= 0:
        return {}
    if output == 'meat':
        room = RULES['meat']['track'] - sum(m['units'] for m in state['meat'])
        kept = min(units, room)
        if kept:
            state['meat'].append({'units': kept,
                                  'spoils': world.day + RULES['meat']['keeps_nights']})
        return {'meat': kept, 'meat_lost': units - kept}
    if output == 'fruit':
        water = units // RULES['fruit_water_every']
        return {'food': world.deposit('food', units), 'water': world.deposit('water', water)}
    if output == 'raw_water':
        treated = units
        wood = 0
        if not ((world.continuity_filter or {}).get('active')
                or 'reservoir' in world.structures):
            per = RULES['raw_water_per_wood']
            wood = min(world.stock['wood'], -(-units // per))
            treated = min(units, wood * per)
            world.stock['wood'] -= wood
        return {'water': world.deposit('water', treated), 'wood_boil': wood,
                'untreated_lost': units - treated}
    return {output: world.deposit(output, units)}


def dawn(world) -> dict | None:
    """Amanhecer (depois do dia avançar): retornos, reservas, chuva, armadilhas."""
    state = world.community
    if state is None:
        return None
    rng = _rng(state)
    out = {}
    for trip in sorted(state['trips'], key=lambda t: t['id']):
        if trip['return_day'] != world.day:
            continue
        result = _resolve_trip(world, trip, rng)
        if result is None:
            out.setdefault('delayed', []).append(trip['id'])
            continue
        state['trips'].remove(trip)
        world.log.append({'day': world.day, 'action': 'worker_trip_return', **result})
        out.setdefault('returns', []).append(result)
    for name, spec in RULES['pools'].items():
        if spec['regrow'] and world.day % spec['every'] == 0:
            state['pools'][name] = min(spec['max'], state['pools'][name] + spec['regrow'])
    if 'coletor' in state['built']:
        roll = rng.randint(1, 6)
        rain = min(STRUCTURES['coletor']['rain'].get(str(roll), 0),
                   STRUCTURES['coletor']['capacity'])
        out['rain'] = {'roll': roll, 'water': world.deposit('water', rain) if rain else 0}
    caught = 0
    for trap in list(state['traps']):
        roll = rng.randint(1, 6)
        if roll == 1:
            state['traps'].remove(trap)  # quebrou
        elif roll >= RULES['traps']['catch_at'] and state['pools']['caca'] > 0:
            state['pools']['caca'] -= 1
            caught += _deliver(world, 'meat', 1).get('meat', 0)
    if state['traps'] or caught:
        out['traps'] = {'active': len(state['traps']), 'meat': caught}
    spoiled = sum(m['units'] for m in state['meat'] if m['spoils'] <= world.day)
    state['meat'] = [m for m in state['meat'] if m['spoils'] > world.day]
    if spoiled:
        out['meat_spoiled'] = spoiled
    state['jobs'] = {}
    _save_rng(state, rng)
    return out or None


def garden_bonus(world, person_id: str) -> int:
    """Agricultor na Horta: +1 comida na colheita (Comunidade)."""
    if world.community is None:
        return 0
    return 1 if specialist(world, person_id, 'horta') else 0


def crowded(world) -> bool:
    return world.community is not None and world.residents > world.beds


def bed_allowance(world) -> int:
    return RULES['crowding']['extra_people'] if world.community is not None else 0
