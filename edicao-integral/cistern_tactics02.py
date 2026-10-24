"""Expedição tática verificável da Cisterna 0.2.

Camada isolada: não concede saque, objetivos nem recompensas. Esses efeitos
precisam de ações de busca/interação/porte e integração explícita posterior.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from math import ceil
from random import Random

from cistern02 import CATALOG, Cistern02, RESCUE_GROUPS


MAPS = {m['name'].lower(): m for m in CATALOG['maps']}
HEROES = {h['id']: h for h in CATALOG['heroes']}
ENEMIES = {'Errante': (1, 5, 1, 1), 'Corredor': (1, 6, 1, 2),
           'Bruto': (3, 6, 2, 1)}  # vida, defesa, dano, passos
WEAPONS = {'Pé de cabra': (1, 1, False), 'Faca': (1, 1, False),
           'Machado': (2, 2, False), 'Pistola': (1, 1, True),
           'Espingarda': (2, 1, True)}  # dano, PA, tiro
HORDE = ('Arrastar',) * 4 + ('Corrida',) * 2 + ('Aglomerado',) * 2 + ('Peso morto',)
PARTS = {'Oficina': {'Conexões': (7, 1), 'Bateria': (7, 1)},
         'Estação': {'Bomba': (7, 2), 'Membrana': (14, 1)}}
SUPPLY_LOTS = {
    'mercado': {'Conserva': (7, 2), 'Água': (14, 2)},
    'hospital': {'Conserva': (7, 1), 'Água': (14, 1)},
    'oficina': {'Conserva': (7, 1), 'Água': (14, 1)},
    'posto': {'Conserva': (14, 1), 'Água': (14, 1), 'Combustível': (7, 8)},
    'condomínio': {'Conserva': (7, 1), 'Água': (14, 1)},
    'estação': {'Água': (14, 2)},
}
REGIONS = {'mercado':'MER', 'hospital':'HOS', 'oficina':'OFI',
           'posto':'POS', 'condomínio':'CON', 'estação':'EST'}
RESCUE_SITES = {
    'ZC-MOR-0001': ('mercado', 7), 'ZC-MOR-0002': ('oficina', 7),
    'ZC-MOR-0003': ('estação', 14), 'ZC-MOR-0004': ('posto', 14),
    'ZC-MOR-0005': ('hospital', 14), 'ZC-MOR-0006': ('condomínio', 14),
    'ZC-MOR-0007': ('hospital', 14), 'ZC-MOR-0008': ('condomínio', 14),
}
SEARCH_CARDS = {c['id']: c for c in CATALOG['cards'] if c['family']=='SAQ'}


def initial_search_deck(destination: str, seed: int) -> list[str]:
    cards = [c['id'] for c in SEARCH_CARDS.values()
             if c['region']==REGIONS[destination]]
    Random(seed + sum(map(ord,destination))).shuffle(cards)
    return cards


def edge(a: int, b: int) -> tuple[int, int]:
    return tuple(sorted((a, b)))


@dataclass
class Tactical02:
    chapter: Cistern02
    destination: str
    team: list[str]
    route: str = 'short'
    positions: dict[str, int] = field(default_factory=dict)
    doors_open: list[list[int]] = field(default_factory=list)
    enemies: list[dict] = field(default_factory=list)
    ap: dict[str, int] = field(default_factory=dict)
    fatigue: dict[str, int] = field(default_factory=dict)
    round_no: int = 0
    completed_rounds: int = 0
    local_pressure: int = 0
    shots: int = 0
    horde_index: int = 0
    next_enemy: int = 1
    finished: bool = False
    failed: bool = False
    log: list[dict] = field(default_factory=list)
    knife_used: list[str] = field(default_factory=list)
    shotgun_used: list[str] = field(default_factory=list)
    horde_order: list[str] = field(default_factory=lambda: list(HORDE))
    carried: dict[str, list[str]] = field(default_factory=dict)
    equipment: dict[str, list[str]] = field(default_factory=dict)
    taken_before: list[str] = field(default_factory=list)
    pump_attempts: list[str] = field(default_factory=list)
    first_market_visit: bool = False
    supply_cargo: dict[str, list[dict]] = field(default_factory=dict)
    van_state: str = 'abandoned'
    van_attempts: list[str] = field(default_factory=list)
    van_returned: bool = False
    search_deck: list[str] = field(default_factory=list)
    search_uses: dict[str, int] = field(default_factory=lambda: {'5':3, '12':3})
    searched_this_visit: list[int] = field(default_factory=list)
    search_cargo: dict[str, list[dict]] = field(default_factory=dict)
    search_ground: list[dict] = field(default_factory=list)
    part_ground: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.part_ground, list):
            raise ValueError('Peças no chão inválidas')
        seen=set()
        for item in self.part_ground:
            if not isinstance(item,dict):
                raise ValueError('Peça no chão inválida')
            part=item.get('part'); destination=item.get('destination')
            place=next((name for name in PARTS if name.lower()==destination),None)
            spec=PARTS.get(place,{}).get(part)
            marker=(destination,part)
            if (spec is None or marker in seen or item.get('zone')!=spec[0]
                    or item.get('load')!=spec[1]):
                raise ValueError('Peça no chão diverge do objetivo único canônico')
            seen.add(marker)
            key=f'{place}:{part}'
            if key not in self.taken_before:
                self.taken_before.append(key)

    @classmethod
    def start(cls, chapter: Cistern02, destination: str, team: list[str],
              route: str = 'short', horde_order: list[str] | None = None,
              taken_before: list[str] | None = None,
              first_visit: bool = True,
              equipment: dict[str, list[str]] | None = None,
              prior_state: dict | None = None,
              travel_paid: bool = False) -> 'Tactical02':
        if destination.lower() not in MAPS or route not in ('short', 'long'):
            raise ValueError('Destino ou rota inválidos')
        if not team or len(set(team)) != len(team) or any(h not in chapter.founders for h in team):
            raise ValueError('Equipe inválida')
        people = {p['id']: p for p in chapter.people}
        if any(people[h]['wounds'] >= 3 or people[h].get('fatigue',0) >= 3 for h in team):
            raise ValueError('Herói incapacitado ou exausto')
        travel_cost = 0 if travel_paid else (1 if route == 'short' else 2)
        if chapter.result or chapter.clock + travel_cost + 1 > 10:
            raise ValueError('Sem tempo para entrar no mapa')
        if horde_order is not None and (len(horde_order) != 9 or
                                        sorted(horde_order) != sorted(HORDE)):
            raise ValueError('Baralho Horda inválido')
        supplies = deepcopy(equipment) if equipment is not None else {h: ['Pé de cabra'] for h in team}
        if set(supplies) != set(team) or any(len(items) > 4 for items in supplies.values()):
            raise ValueError('Equipamentos da equipe inválidos')
        people = {p['id']: p for p in chapter.people}
        if any(people[h]['wounds'] >= 3 for h in team):
            raise ValueError('Herói incapacitado não sai')
        obj = cls(chapter, destination.lower(), list(team), route,
                  horde_order=list(horde_order) if horde_order else list(HORDE),
                  taken_before=list(taken_before or []),
                  first_market_visit=destination.lower() == 'mercado' and first_visit)
        if not travel_paid:
            chapter.spend_segments(obj.travel_cost)
        obj.positions = {h: obj.map['entry'] for h in team}
        obj.carried = {h: [] for h in team}
        obj.supply_cargo = {h: [] for h in team}
        obj.search_cargo = {h: [] for h in team}
        obj.equipment = supplies
        obj.fatigue = {h: people[h].get('fatigue',0) for h in team}
        if prior_state is not None:
            obj.doors_open = deepcopy(prior_state['doors_open'])
            obj.enemies = deepcopy(prior_state['enemies'])
            obj.next_enemy = prior_state['next_enemy']
            obj.horde_index = prior_state.get('horde_index', 0)
            obj.van_state = prior_state.get('van_state', 'abandoned')
            obj.search_deck = deepcopy(prior_state.get(
                'search_deck', initial_search_deck(obj.destination, chapter.seed)))
            obj.search_uses = deepcopy(prior_state.get(
                'search_uses', {'5':3, '12':3}))
            obj.search_ground = deepcopy(prior_state.get('search_ground', []))
            obj.part_ground = deepcopy(prior_state.get('part_ground', []))
            obj.__post_init__()
        else:
            count = max(0, ceil(len(team)/2) - (route == 'long'))
            for _ in range(count): obj._spawn('Errante', obj.map['spawn'])
            if obj.destination == 'estação': obj._spawn('Bruto', 14)
            obj.search_deck = initial_search_deck(obj.destination, chapter.seed)
        obj._night_fatigue()
        obj.begin_round()
        return obj

    @property
    def map(self) -> dict:
        return MAPS[self.destination]

    @property
    def travel_cost(self) -> int:
        return 1 if self.route == 'short' else 2

    @property
    def opened(self) -> set[tuple[int, int]]:
        return {edge(*e) for e in self.doors_open}

    def _night_fatigue(self) -> None:
        if self.chapter.clock > 8:
            people = {p['id']: p for p in self.chapter.people}
            for hero in self.team:
                self.fatigue[hero] = min(3, self.fatigue[hero]+1)
                people[hero]['fatigue'] = self.fatigue[hero]

    def _spawn(self, kind: str, zone: int) -> None:
        if kind not in ENEMIES: raise ValueError('Inimigo inválido')
        if len(self.enemies) >= 24:
            self.failed = True
            self.log.append({'event': 'overrun', 'zone': zone})
            return
        enemy = {'id': self.next_enemy, 'kind': kind, 'zone': zone,
                 'hp': ENEMIES[kind][0], 'door_target': None, 'door_hits': 0}
        self.next_enemy += 1
        self.enemies.append(enemy)

    def begin_round(self) -> None:
        if self.finished or self.failed: raise ValueError('Expedição encerrada')
        if self.round_no != self.completed_rounds:
            raise ValueError('Rodada anterior não encerrada')
        self.chapter.spend_segments(1)
        self._night_fatigue()
        self.round_no += 1
        self.shots = 0
        self.knife_used = []
        self.shotgun_used = []
        people = {p['id']: p for p in self.chapter.people}
        self.ap = {h: max(1, 3-int(people[h]['hungry'])-int(people[h]['thirsty'])
                          -int(self.fatigue[h] >= 2)) for h in self.team}
        self.log.append({'event': 'round', 'number': self.round_no,
                         'clock': self.chapter.clock, 'ap': self.ap.copy()})

    def _pay(self, hero: str, amount: int) -> None:
        people = {p['id']: p for p in self.chapter.people}
        if (self.finished or self.failed or self.round_no == self.completed_rounds
                or hero not in self.ap or self.ap[hero] < amount
                or people[hero]['wounds'] >= 3):
            raise ValueError('PA indisponíveis')
        self.ap[hero] -= amount

    def _adjacent(self, a: int, b: int) -> bool:
        return list(edge(a, b)) in [sorted(e) for e in self.map['edges']]

    def _open(self, a: int, b: int) -> bool:
        pair = edge(a, b)
        return pair not in {edge(*e) for e in self.map['doors']} or pair in self.opened

    def move(self, hero: str, zone: int) -> None:
        if hero not in self.positions or zone not in self.map['zones']:
            raise ValueError('Herói ou zona inválidos')
        here = self.positions[hero]
        if not self._adjacent(here, zone) or not self._open(here, zone):
            raise ValueError('Passagem fechada ou inexistente')
        cost = 1 + int(any(e['zone'] == here for e in self.enemies))
        self._pay(hero, cost)
        self.positions[hero] = zone
        self.log.append({'event': 'move', 'hero': hero, 'from': here, 'to': zone, 'ap': cost})

    def open_door(self, hero: str, zone: int, tool: str | None = None) -> None:
        if hero not in self.positions: raise ValueError('Herói inválido')
        here = self.positions[hero]
        pair = edge(here, zone)
        if pair not in {edge(*e) for e in self.map['doors']} or pair in self.opened:
            raise ValueError('Não há porta fechada')
        blocked = pair in {edge(*e) for e in self.map['blocked']}
        if blocked and (tool not in ('Pé de cabra', 'Ferramentas')
                        or tool not in self.equipment[hero]):
            raise ValueError('Ferramenta necessária')
        self._pay(hero, 2 if blocked else 1)
        self.doors_open.append(list(pair))
        self.log.append({'event': 'door', 'hero': hero, 'edge': list(pair),
                         'blocked': blocked})

    def attack(self, hero: str, enemy_id: int, weapon: str, die: int) -> bool:
        if hero not in self.positions or weapon not in WEAPONS or not 1 <= die <= 6:
            raise ValueError('Ataque inválido')
        if weapon not in self.equipment[hero]: raise ValueError('Arma não transportada')
        target = next((e for e in self.enemies if e['id'] == enemy_id), None)
        if target is None: raise ValueError('Alvo inexistente')
        damage, cost, ranged = WEAPONS[weapon]
        here, there = self.positions[hero], target['zone']
        if ranged:
            if here != there and not (self._adjacent(here, there) and self._open(here, there)):
                raise ValueError('Alvo fora de alcance ou sem linha de visão')
            if self.chapter.ammo < 1: raise ValueError('Munição insuficiente')
            if weapon == 'Espingarda' and hero in self.shotgun_used:
                raise ValueError('Espingarda já usada nesta rodada')
        elif here != there: raise ValueError('Alvo fora de alcance')
        self._pay(hero, cost)
        if ranged:
            self.chapter.ammo -= 1
            self.shots += 1
            if weapon == 'Espingarda': self.shotgun_used.append(hero)
        bonus = int(weapon == 'Faca' and hero not in self.knife_used)
        if weapon == 'Faca': self.knife_used.append(hero)
        attr = HEROES[hero]['attributes']['Agilidade' if ranged else 'Corpo']
        hit = die == 6 or (die != 1 and die + attr + bonus >= ENEMIES[target['kind']][1])
        if hit:
            target['hp'] -= damage
            if target['hp'] <= 0: self.enemies.remove(target)
        self.log.append({'event': 'attack', 'hero': hero, 'enemy': enemy_id,
                         'weapon': weapon, 'die': die, 'hit': hit})
        return hit

    def pickup_part(self, hero: str, part: str, die: int | None = None) -> bool:
        """Ação auditável de retirada; entrega só é certificada por finish().

        `taken_before` deve conter IDs únicos já entregues em visitas anteriores.
        Carga inicial de armas/provisões deve ser descontada pelo integrador.
        """
        place = next((name for name in PARTS if name.lower() == self.destination), None)
        spec = PARTS.get(place, {}).get(part)
        key = f'{place}:{part}'
        grounded = next((item for item in self.part_ground
                         if item['destination'] == self.destination
                         and item['part'] == part), None)
        recovering = grounded is not None
        if (hero not in self.positions or spec is None
                or (recovering and self.positions[hero] != grounded['zone'])
                or (not recovering and (self.positions[hero] != spec[0]
                                        or key in self.taken_before))
                or any(part in items for items in self.carried.values())):
            raise ValueError('Peça indisponível ou herói fora do objetivo')
        load = grounded['load'] if recovering else spec[1]
        if self._load(hero) + load > 4:
            raise ValueError('Carga acima da capacidade')
        if recovering:
            self._pay(hero, 1)
            self.part_ground.remove(grounded)
            self.carried[hero].append(part)
            self.log.append({'event':'recover_part','id':key,'hero':hero,'part':part,
                             'destination':place,'zone':grounded['zone'],
                             'clock':self.chapter.clock})
            return True
        if part == 'Bomba':
            if hero in self.pump_attempts or die is None or not 1 <= die <= 6:
                raise ValueError('Tentativa Técnica inválida')
            self._pay(hero, 2)
            self.pump_attempts.append(hero)
            score = die + HEROES[hero]['attributes']['Técnica']
            hit = die == 6 or (die != 1 and score >= 6)
            if not hit:
                self.chapter.raise_pressure(1)
                self.log.append({'event': 'pump_failure', 'hero': hero, 'die': die})
                return False
        else:
            self._pay(hero, 1)
        self.carried[hero].append(part)
        self.log.append({'event': 'pickup_part', 'id':key,'hero': hero, 'part': part,
                         'destination': place, 'zone': spec[0],
                         'clock': self.chapter.clock})
        return True

    def _load(self, hero: str) -> int:
        part_place = next((name for name in PARTS if name.lower() == self.destination), None)
        part_load = sum(PARTS[part_place][p][1] for p in self.carried[hero]) if part_place else 0
        return (len(self.equipment[hero]) + part_load
                + sum(item['cards'] for item in self.supply_cargo[hero])
                + sum(item['cards'] for item in self.search_cargo[hero]))

    def search(self, hero: str) -> dict:
        if hero not in self.positions or self.positions[hero] not in (5,12):
            raise ValueError('Busca exige presença em B1/B2')
        zone = self.positions[hero]
        if (zone in self.searched_this_visit or self.search_uses[str(zone)] < 1
                or not self.search_deck):
            raise ValueError('Busca esgotada nesta visita ou campanha')
        self._pay(hero,1)
        card_id = self.search_deck.pop(0)
        card = SEARCH_CARDS[card_id]
        count = sum(card['reward'].values())
        found = {'id':card_id, 'reward':card['reward'].copy(), 'cards':count,
                 'zone':zone, 'hero':hero}
        self.search_uses[str(zone)] -= 1
        self.searched_this_visit.append(zone)
        carried = self._load(hero)+count <= 4
        (self.search_cargo[hero] if carried else self.search_ground).append(found)
        self.log.append({'event':'search', 'id':card_id, 'hero':hero,
                         'zone':zone, 'carried':carried})
        return {**found, 'carried':carried}

    def collect_ground(self, hero: str, card_id: str) -> None:
        found = next((x for x in self.search_ground if x['id']==card_id),None)
        if (hero not in self.positions or found is None
                or self.positions[hero] != found['zone']
                or self._load(hero)+found['cards'] > 4):
            raise ValueError('Achado no chão indisponível ou sem carga')
        self._pay(hero,1)
        self.search_ground.remove(found)
        self.search_cargo[hero].append({**found,'hero':hero})
        self.log.append({'event':'collect_ground','id':card_id,'hero':hero})

    def pickup_supply(self, hero: str, kind: str, lot: int) -> dict:
        """Retira um lote inteiro de 4 porções por carta, ou uma carta de combustível."""
        spec = SUPPLY_LOTS.get(self.destination, {}).get(kind)
        if hero not in self.positions or spec is None or not isinstance(lot, int):
            raise ValueError('Saque inválido')
        zone, count = spec
        key = f'{self.destination}:{kind}:{lot}'
        if (not 1 <= lot <= count or self.positions[hero] != zone
                or key in self.taken_before
                or any(item['id'] == key for items in self.supply_cargo.values() for item in items)):
            raise ValueError('Lote indisponível ou zona incorreta')
        cards = 1 if kind == 'Combustível' else ceil(self.chapter.initial_consumers/4)
        if self._load(hero) + cards > 4:
            raise ValueError('Lote excede capacidade de carga')
        self._pay(hero, 1)
        item = {'id': key, 'kind': kind, 'lot': lot, 'cards': cards,
                'portions': 0 if kind == 'Combustível' else 4*cards,
                'zone': zone, 'hero': hero}
        self.supply_cargo[hero].append(item)
        self.log.append({'event': 'pickup_supply', **item, 'clock': self.chapter.clock})
        return item.copy()

    def inspect_van(self, hero: str) -> None:
        if self.destination != 'posto' or hero not in self.positions or self.positions[hero] != 7:
            raise ValueError('Van fora de alcance')
        if self.van_state != 'abandoned': raise ValueError('Van já inspecionada')
        self._pay(hero, 1)
        self.van_state = 'incomplete'
        self.log.append({'event': 'inspect_van', 'hero': hero, 'zone': 7})

    def repair_van(self, hero: str, die: int) -> bool:
        if (self.destination != 'posto' or hero not in self.positions
                or self.positions[hero] != 7 or self.van_state != 'incomplete'
                or hero in self.van_attempts or not 1 <= die <= 6):
            raise ValueError('Reparo inválido')
        battery_in_cargo = 'Bateria' in self.carried[hero]
        battery_in_equipment = 'Bateria' in self.equipment[hero]
        if not (battery_in_cargo or battery_in_equipment):
            raise ValueError('Bateria necessária')
        self._pay(hero, 2)
        self.van_attempts.append(hero)
        score = die + HEROES[hero]['attributes']['Técnica']
        hit = die == 6 or (die != 1 and score >= 6)
        if hit:
            (self.carried if battery_in_cargo else self.equipment)[hero].remove('Bateria')
            self.van_state = 'operational'
        self.log.append({'event': 'repair_van', 'hero': hero, 'die': die, 'success': hit,
                         'battery_consumed': hit})
        return hit

    def rescue(self, hero: str, group_id: str, decision: str) -> dict:
        """Registra contato de um grupo somente na zona do mapa canônico."""
        site = RESCUE_SITES.get(group_id)
        if (site is None or group_id not in RESCUE_GROUPS or decision not in
                ('welcome', 'aid', 'decline') or site[0] != self.destination
                or hero not in self.positions or self.positions[hero] != site[1]
                or any(item.get('group_id') == group_id for item in self.log)):
            raise ValueError('Resgate indisponível neste mapa ou zona')
        self._pay(hero, 1)
        receipt = {'event': 'rescue', 'group_id': group_id,
                   'decision': decision, 'hero': hero, 'zone': site[1]}
        self.log.append(receipt)
        return receipt.copy()

    def delivery_proof(self) -> list[dict]:
        """Certificado derivado apenas de retirada legal e retorno concluído."""
        if not self.finished or self.failed or not any(x['event'] == 'return' for x in self.log):
            return []
        proof = [x.copy() for x in self.log if x['event'] in
                 ('pickup_part','recover_part','pickup_supply','rescue')
                 and (x['event'] != 'pickup_supply' or x['id'] not in self._spent_fuel_ids())]
        if self.van_returned:
            proof.append({'event': 'deliver_van', 'destination': 'posto',
                          'state': 'operational'})
        proof.extend({'event':'search_reward', **item.copy()}
                     for items in self.search_cargo.values() for item in items)
        return proof

    def _spent_fuel_ids(self) -> set[str]:
        return {x['id'] for x in self.log if x['event'] == 'fuel_spent'}

    def _path(self, start: int, target: int) -> list[int]:
        graph = {z: [] for z in self.map['zones']}
        for a, b in self.map['edges']:
            graph[a].append(b); graph[b].append(a)
        q = deque([(start, [start])]); seen = {start}
        while q:
            z, path = q.popleft()
            if z == target: return path
            for nxt in sorted(graph[z]):
                if nxt not in seen:
                    seen.add(nxt); q.append((nxt, path+[nxt]))
        return []

    def _activate(self) -> None:
        people = {p['id']: p for p in self.chapter.people}
        for enemy in list(self.enemies):
            targets = sorted((len(self._path(enemy['zone'], z)), z, hero)
                             for hero, z in self.positions.items())
            if not targets: continue
            _, _, hero = targets[0]
            if enemy['zone'] == self.positions[hero]:
                people[hero]['wounds'] += ENEMIES[enemy['kind']][2]
                self.log.append({'event': 'wound', 'hero': hero, 'enemy': enemy['id']})
                continue
            for _ in range(ENEMIES[enemy['kind']][3]):
                path = self._path(enemy['zone'], self.positions[hero])
                if len(path) < 2: break
                nxt = path[1]; pair = edge(enemy['zone'], nxt)
                if not self._open(*pair):
                    if enemy['door_target'] != list(pair):
                        enemy['door_target'] = list(pair); enemy['door_hits'] = 0
                    enemy['door_hits'] += 1
                    if enemy['door_hits'] >= (2 if pair in {edge(*e) for e in self.map['blocked']} else 1):
                        self.doors_open.append(list(pair))
                    break
                enemy['zone'] = nxt
                if nxt == self.positions[hero]: break

    def _horde(self) -> None:
        card = self.horde_order[self.horde_index % len(self.horde_order)]
        self.horde_index += 1
        kind, count = {'Arrastar': ('Errante', 1), 'Corrida': ('Corredor', 1),
                       'Aglomerado': ('Errante', ceil(len(self.team)/2)),
                       'Peso morto': ('Bruto', 1)}[card]
        for _ in range(count): self._spawn(kind, self.map['spawn'])
        self.log.append({'event': 'horde', 'card': card})

    def end_round(self) -> None:
        if self.finished or self.failed: raise ValueError('Expedição encerrada')
        if self.completed_rounds == self.round_no:
            raise ValueError('Rodada já encerrada')
        protected = self.first_market_visit and self.round_no == 1
        if not protected:
            self._activate()
            for _ in range(self.shots // 2): self._spawn('Errante', self.map['spawn'])
        self.local_pressure += 1
        if not protected and self.local_pressure >= 2:
            self.local_pressure = 0; self._horde()
        if not protected and self.chapter.clock >= 9: self._horde()
        self.completed_rounds += 1
        self.log.append({'event': 'end_round', 'number': self.round_no,
                         'enemies': len(self.enemies), 'clock': self.chapter.clock})

    def can_exit(self) -> bool:
        return (self.completed_rounds == self.round_no and self.round_no >= 1
                and all(z == self.map['exit'] for z in self.positions.values())
                and not any(e['zone'] == self.map['exit'] for e in self.enemies)
                and not self.failed and not self.finished)

    def finish(self, by_van: bool = False) -> None:
        if not self.can_exit(): raise ValueError('Saída não liberada')
        if self.chapter.clock + self.travel_cost > 10:
            raise ValueError('Retorno excede o relógio; use emergency')
        if by_van:
            if self.destination != 'posto' or self.van_state != 'operational':
                raise ValueError('Van indisponível para retorno')
            fuel = [(hero, item) for hero, items in self.supply_cargo.items()
                    for item in items if item['kind'] == 'Combustível']
            if len(fuel) < 2*self.travel_cost:
                raise ValueError('Combustível insuficiente para retornar com a van')
            for hero, item in fuel[:2*self.travel_cost]:
                self.supply_cargo[hero].remove(item)
                self.log.append({'event': 'fuel_spent', 'id': item['id'], 'hero': hero})
            self.van_returned = True
        self.chapter.spend_segments(self.travel_cost)
        self._night_fatigue()
        self.finished = True
        self.log.append({'event': 'return', 'clock': self.chapter.clock})

    def emergency(self) -> None:
        if self.finished: raise ValueError('Expedição já encerrada')
        people = {p['id']: p for p in self.chapter.people}
        for hero, parts in self.carried.items():
            for part in parts:
                place = next(name for name, items in PARTS.items() if part in items)
                key = f'{place}:{part}'
                ground = {'part':part,'destination':place.lower(),
                          'zone':PARTS[place][part][0],
                          'load':PARTS[place][part][1]}
                if not any(item['destination']==ground['destination']
                           and item['part']==part for item in self.part_ground):
                    self.part_ground.append(ground)
                if key not in self.taken_before:
                    self.taken_before.append(key)
        for hero in self.team:
            people[hero]['wounds'] += 1
            self.fatigue[hero] = 3
            people[hero]['fatigue'] = 3
        self.failed = True; self.finished = True
        self.carried = {hero: [] for hero in self.team}
        self.supply_cargo = {hero: [] for hero in self.team}
        self.search_cargo = {hero: [] for hero in self.team}
        self.log.append({'event': 'emergency', 'clock': self.chapter.clock})

    def snapshot(self) -> dict:
        """Estado tático serializável; salvar também Cistern02.save separadamente."""
        fields = ('destination','team','route','positions','doors_open','enemies','ap',
                  'fatigue','round_no','completed_rounds','local_pressure','shots',
                  'horde_index','next_enemy','finished','failed','log','knife_used',
                  'shotgun_used','horde_order','carried','taken_before','pump_attempts',
                  'first_market_visit','equipment','supply_cargo','van_state',
                  'van_attempts','van_returned','search_deck','search_uses',
                  'searched_this_visit','search_cargo','search_ground','part_ground')
        return deepcopy({name: getattr(self, name) for name in fields})

    def site_snapshot(self) -> dict:
        """Elementos que permanecem no destino entre visitas."""
        return deepcopy({'doors_open': self.doors_open, 'enemies': self.enemies,
                         'next_enemy': self.next_enemy, 'horde_index': self.horde_index,
                         'van_state': 'away' if self.van_returned else self.van_state,
                         'search_deck': self.search_deck, 'search_uses': self.search_uses,
                         'search_ground': self.search_ground,
                         'part_ground': self.part_ground})

    @classmethod
    def from_snapshot(cls, chapter: Cistern02, snap: dict) -> 'Tactical02':
        if snap['destination'] not in MAPS or any(h not in chapter.founders for h in snap['team']):
            raise ValueError('Snapshot incompatível')
        return cls(chapter=chapter, **deepcopy(snap))
