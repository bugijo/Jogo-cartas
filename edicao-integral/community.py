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
CAMP_JOBS = ('cozinhar', 'obra', 'cuidar', 'vigiar', 'armadilha', 'canteiro')
KEYS = {'rng', 'professions', 'jobs', 'trips', 'pools', 'meat', 'built', 'projects',
        'deck', 'traps', 'pista_used', 'trip_seq', 'arrival', 'arrival_seq'}


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
             'traps': [], 'pista_used': False, 'trip_seq': 0,
             'arrival': None, 'arrival_seq': 0}
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
    ok = ok and all(state['built'].count(k) <= STRUCTURES[k].get('max', 1) for k in STRUCTURES)
    ok = ok and len(state['traps']) <= RULES['traps']['max']
    if not ok:
        raise ValueError('Estado da Comunidade inválido')


# --- pessoas ---------------------------------------------------------------------
def away(world) -> set[str]:
    trips = (world.community or {}).get('trips', [])
    return ({trip['worker'] for trip in trips}
            | {trip['dog'] for trip in trips if trip.get('dog')})


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
    if hunger_blocks(world, person_id):
        return False
    return person.get('fatigue', 0) < 3 and _wounds(world, person_id) <= max_wounds


def hunger_blocks(world, person_id: str) -> bool:
    """Fome/sede impedem trabalho (RULES l.22), também na Comunidade."""
    person = _person(world, person_id)
    if not (person.get('hungry') or person.get('thirsty')):
        return False
    return True  # medido: liberar 1 noite de fome não mudou o resultado (diretor)


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


def arrival_fatigue(world) -> dict:
    """Travessia: ninguém chega descansado ao regional (Vida máxima na chegada).

    Decisão do diretor (D-17): grupos grandes terminavam a Cisterna mais
    inteiros e chegavam com folga; o teto nivela a chegada sem apagar
    ferimentos piores que ele.
    """
    cap = RULES['arrival']['max_hero_health']
    tired = {}
    for hero_id, hero in sorted(world.heroes.items()):
        if hero['health'] > cap:
            tired[hero_id] = hero['health']
            world._set_hero_health(hero_id, cap)
    return tired


def start_structures(world, level: str = 'normal') -> list[str]:
    """Preparação: obras que o abrigo já tem na chegada (Acolhedor: um canteiro)."""
    if level not in RULES['levels']:
        raise ValueError('Nível de preparação desconhecido')
    built = list(RULES['levels'][level]['start_structures'])
    world.community['built'] += built
    return built


def evacuation_supply(world, level: str = 'normal') -> dict:
    """Suprimento de evacuação: a Ponte entrega 1 ração por consumidor, uma vez.

    Decisão do diretor (2026-10-30): o grupo chega com comida para menos de uma
    noite; sem esta ração as viagens não voltam antes do Colapso.
    """
    per = RULES['levels'][level].get('evacuation_food_per_consumer',
                                     RULES['evacuation_supply']['food_per_consumer'])
    amount = per * len(world.meal_people())
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
    if job == 'canteiro':
        tended = sum(j['job'] == 'canteiro' for j in state['jobs'].values())
        if tended >= state['built'].count('canteiro'):
            raise ValueError('Sem canteiro livre hoje')
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
    limit = STRUCTURES.get(kind, {}).get('max', 1)
    if (kind not in STRUCTURES or state['built'].count(kind) >= limit
            or kind in state['projects']):
        raise ValueError('Obra comunitária indisponível')
    spec = STRUCTURES[kind]
    if spec.get('requires') and spec['requires'] not in world.structures:
        raise ValueError('Obra exige a estrutura do nível anterior')
    if world.free_terrain < spec.get('terrain', 0):
        raise ValueError('Sem terreno livre: amplie a cerca')
    cost = spec['cost']
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
        elif kind == 'canteiro':
            food = STRUCTURES['canteiro']['food_per_worker'] + (
                1 if specialist(world, person_id, 'horta') else 0)
            out.setdefault('canteiro', []).append(
                {'person': person_id, 'food': food, 'stored': world.deposit('food', food)})
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


def morale_night(world, people: dict, fed: dict) -> dict | None:
    """Escassez progressiva: noite com humano sem comer ou beber baixa o Moral.

    `unfed_per_drop` 0 = basta 1 humano sem a porção; N = 1 a cada N humanos
    (arredondado para cima). Noite com todos servidos recupera `recover`.
    Moral 0 já é derrota parcial no motor.
    """
    rule = RULES['morale']
    if world.community is None or not rule['on']:
        return None
    humans = [pid for pid, p in people.items() if p.get('kind') != 'dog']
    unfed = [pid for pid in humans if pid not in fed['food'] or pid not in fed['water']]
    per = rule['unfed_per_drop']
    limit = max(1, -(-len(humans) // per)) if per else 1
    before = world.shelter_morale
    if len(unfed) >= limit:
        world.shelter_morale = max(0, before - 1)
    elif not unfed:
        world.shelter_morale = min(5, before + rule['recover'])
    return {'unfed_humans': len(unfed), 'limit': limit, 'morale': world.shelter_morale,
            'change': world.shelter_morale - before}


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
              rations: int | None = None, dog: str | None = None) -> dict:
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
    home = [i for i, p in world.meal_people().items() if p.get('kind') != 'dog' and i != person_id]
    if not home:
        raise ValueError('O abrigo não pode ficar sem nenhum humano')
    if dog is not None:
        pet = next((p for p in world.continuity_people if p['id'] == dog), None)
        if (pet is None or pet['kind'] != 'dog' or dog in away(world)
                or pet.get('hungry') or pet.get('thirsty')):
            raise ValueError('Cão indisponível para a viagem')
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
            'rations': rations, 'delayed': False, 'dog': dog}
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
    if trip.get('dog'):
        bonus += TRIPS['dog_bonus']  # o cão fareja e carrega
    roll = rng.randint(1, 6)
    nights = trip['days'] + (1 if trip['delayed'] else 0)
    points = (roll + bonus) * trip['days']
    points -= TRIPS['unsupplied_day_cost'] * (nights - trip['rations'])
    if trip.get('dog'):
        points -= TRIPS['dog_cost_per_day'] * nights  # o cão come da viagem
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
    _arrival_roll(world, state, rng)
    if state['arrival']:
        out['arrival'] = dict(state['arrival'])
    _save_rng(state, rng)
    return out or None


def garden_bonus(world, person_id: str) -> int:
    """Agricultor na Horta: +1 comida na colheita (Comunidade)."""
    if world.community is None:
        return 0
    return 1 if specialist(world, person_id, 'horta') else 0


# --- crescimento do abrigo (D-20) -------------------------------------------------
def _sum_built(world, key: str) -> int:
    state = world.community
    if state is None:
        return 0
    return sum(STRUCTURES[k].get(key, 0) for k in state['built'])


def terrain_delta(world) -> int:
    """Cerca amplia o terreno; obras da Comunidade (prontas ou em obra) ocupam."""
    state = world.community
    if state is None:
        return 0
    used = _sum_built(world, 'terrain') + sum(STRUCTURES[k].get('terrain', 0)
                                              for k in state['projects'])
    return _sum_built(world, 'terrain_bonus') - used


def beds_bonus(world) -> int:
    return _sum_built(world, 'beds_bonus')


def storage_bonus(world) -> int:
    return _sum_built(world, 'storage_bonus')


def _arrival_roll(world, state, rng) -> None:
    rule = RULES['arrivals']
    if state['arrival'] is not None:
        # Ninguém decidiu no amanhecer: o grupo seguiu caminho (= recusa).
        _refuse(world, state, 'sem_decisao')
    if world.day in rule['days']:
        roll = rng.randint(1, 6)
        state['arrival'] = {'day': world.day, 'roll': roll, 'people': list(rule['table'][str(roll)])}
        if not state['arrival']['people']:
            state['arrival'] = None
        world.log.append({'day': world.day, 'action': 'arrival', 'roll': roll,
                          'people': list(rule['table'][str(roll)])})


def _refuse(world, state, reason: str) -> None:
    before = world.shelter_morale
    world.shelter_morale = max(0, before - RULES['arrivals']['refuse_morale'])
    world.log.append({'day': world.day, 'action': 'arrival_refused', 'reason': reason,
                      'people': state['arrival']['people'], 'morale': world.shelter_morale})
    state['arrival'] = None


def arrival_fits(world) -> bool:
    state = world.community
    if not state or not state['arrival']:
        return False
    humans = len(state['arrival']['people'])
    return world.residents + humans <= world.beds + bed_allowance(world)


def receive(world, accept: bool) -> dict:
    """Amanhecer de chegada: acolher todo o grupo (exige cama) ou recusar (Moral −1)."""
    _require_dawn(world)
    state = world.community
    if not state['arrival']:
        raise ValueError('Ninguém chegou hoje')
    if not accept:
        people = state['arrival']['people']
        _refuse(world, state, 'recusa')
        return {'accepted': False, 'people': people}
    if not arrival_fits(world):
        raise ValueError('Sem cama para acolher o grupo')
    joined = []
    for kind in state['arrival']['people']:
        state['arrival_seq'] += 1
        person_id = f"N{state['arrival_seq']:02d}"
        world.continuity_people.append({'id': person_id, 'kind': kind, 'family': None,
                                        'hungry': False, 'thirsty': False, 'streak': 0,
                                        'wounds': 0, 'fatigue': 0, 'alert': False})
        if kind == 'adult':
            join(world, person_id)
        joined.append(person_id)
    state['arrival'] = None
    world.log.append({'day': world.day, 'action': 'arrival_accepted', 'people': joined})
    return {'accepted': True, 'people': joined}


def renew_every(world, location_id: str) -> int:
    """Noites por busca renovada num local natural (Horta abandonada: 2)."""
    if world.community is None:
        return 1
    return RULES['location_renew_every'].get(location_id, 1)


def vehicle_trechos(world, distance: str) -> int | None:
    """Trechos de van por sentido (D-21): rota curta 1 (perto/médio), longa 2.

    RULES.md §5 l.29 e §11 l.64 (2 combustíveis por trecho). None fora da
    edição integral: o protótipo certificado usa a distância a pé.
    """
    if world.community is None:
        return None
    return RULES['vehicles']['route_trechos'][distance]


def maintain_weapon(world, hero_id: str, instance_id: str) -> dict:
    """Manutenção (D-22): no amanhecer, herói no abrigo gasta 1 sucata e a arma
    de mão volta à durabilidade máxima. Uma por herói por dia."""
    _require_dawn(world)
    rule = RULES['weapon_maintenance']
    hero = world.heroes.get(hero_id)
    item = (world.gear.get(hero_id) or {}).get(instance_id)
    done = [r for r in world.log if r.get('action') == 'maintain_weapon'
            and r.get('day') == world.day and r.get('hero') == hero_id]
    if (hero is None or hero['location'] != 'camp' or hero_id in away(world)
            or item is None or item['slot'] != 'hand'
            or len(done) >= rule['per_hero_per_day']):
        raise ValueError('Manutenção indisponível')
    top = world_items()[item['template']]['durability']
    if item['durability'] >= top:
        raise ValueError('Arma já está inteira')
    if world.stock['scrap'] < rule['scrap']:
        raise ValueError('Sem sucata para a manutenção')
    world.stock['scrap'] -= rule['scrap']
    before, item['durability'] = item['durability'], top
    row = {'day': world.day, 'action': 'maintain_weapon', 'hero': hero_id,
           'item': instance_id, 'durability': [before, top]}
    world.log.append(row)
    return row


def world_items() -> dict:
    from system import ITEMS  # evita import circular (system importa community)
    return ITEMS


def defense_waves(world, defenders: int) -> list | None:
    """Ondas da defesa final pelo número de heróis que defendem (D-22)."""
    if world.community is None:
        return None
    table = RULES['final_defense_waves']
    key = str(min(max(defenders, int(min(table))), int(max(table))))
    return table[key]


def crowded(world) -> bool:
    return world.community is not None and world.residents > world.beds


def bed_allowance(world) -> int:
    return RULES['crowding']['extra_people'] if world.community is not None else 0
