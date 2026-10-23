"""Motor determinístico experimental para recursos, campanha e expedições.

Todas as constantes de conteúdo vêm de data/system.json. Não substitui RULES.md.
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

DATA = json.loads((Path(__file__).parent / 'data/system.json').read_text(encoding='utf-8'))
EQUIPMENT = json.loads((Path(__file__).parent / 'data/equipment.json').read_text(encoding='utf-8'))
ITEMS = {item['id']:item for item in EQUIPMENT['items']}
HEROES = {h['id']: h for h in DATA['heroes']}
NPCS = {n['id']: n for n in DATA['npcs']}
STRUCTURES = {s['kind']: s for s in DATA['structures']}
LOCATIONS = {l['id']: l for l in DATA['locations']}
CRISES = {c['id']: c for c in DATA['crises']}
RESOURCES = ('food', 'water', 'wood', 'scrap', 'medicine', 'fuel', 'ammo')


@dataclass
class Expedition:
    id: str
    heroes: list[str]
    destination: str
    distance: str
    remaining: int
    returning: bool = False
    cargo: dict[str, int] = field(default_factory=dict)


@dataclass
class World:
    seed: int
    day: int = 0
    heroes: dict[str, dict] = field(default_factory=dict)
    npcs: dict[str, dict] = field(default_factory=dict)
    stock: dict[str, int] = field(default_factory=lambda: dict.fromkeys(RESOURCES, 0))
    structures: dict[str, dict] = field(default_factory=dict)
    projects: dict[str, int] = field(default_factory=dict)
    searches: dict[str, int] = field(default_factory=dict)
    crises_last_day: dict[str, int] = field(default_factory=dict)
    active_crises: list[str] = field(default_factory=list)
    expeditions: dict[str, Expedition] = field(default_factory=dict)
    outposts: dict[str, dict] = field(default_factory=dict)
    gear: dict[str, dict] = field(default_factory=dict)
    camp_xp: int = 0
    clues: int = 0
    rng_state: object = None
    log: list[dict] = field(default_factory=list)

    @classmethod
    def new(cls, seed: int, hero_ids: list[str], stock: dict[str, int] | None = None) -> 'World':
        if not hero_ids or len(set(hero_ids)) != len(hero_ids) or any(h not in HEROES for h in hero_ids):
            raise ValueError('Heróis iniciais inválidos')
        world = cls(seed=seed)
        world.heroes = {h:{'xp':0,'health':3,'combat_xp':0,'location':'camp'} for h in hero_ids}
        world.gear = {h:{} for h in hero_ids}
        world.searches = {key:loc['searches'] for key,loc in LOCATIONS.items()}
        world.stock.update(stock or {})
        world.rng_state = _lists(random.Random(seed).getstate())
        world.validate()
        return world

    @property
    def beds(self) -> int:
        return DATA['rules']['beds_base'] + sum(STRUCTURES[k]['beds_bonus'] for k in self.structures)

    @property
    def storage(self) -> int:
        return DATA['rules']['storage_base'] + sum(STRUCTURES[k]['storage_bonus'] for k in self.structures)

    @property
    def residents(self) -> int:
        return len(self.heroes) + len(self.npcs)

    @property
    def free_terrain(self) -> int:
        return DATA['rules']['terrain_base'] - sum(STRUCTURES[k]['terrain'] for k in self.structures) - sum(STRUCTURES[k]['terrain'] for k in self.projects)

    def validate(self) -> None:
        if any(v < 0 or not isinstance(v,int) for v in self.stock.values()):
            raise ValueError('Estoque inválido')
        if any(k not in RESOURCES for k in self.stock) or sum(self.stock.values()) > self.storage:
            raise ValueError('Depósito excedido')
        if self.residents > self.beds or self.free_terrain < 0:
            raise ValueError('Capacidade excedida')
        if any(v < 0 for v in self.searches.values()):
            raise ValueError('Contador de busca negativo')
        if any(h not in HEROES or state['xp'] > 100 or state['health'] < 0 for h,state in self.heroes.items()):
            raise ValueError('Herói inválido')
        if any(n not in NPCS or not 1 <= state['level'] <= 3 for n,state in self.npcs.items()):
            raise ValueError('NPC inválido')
        active_heroes = set()
        for key, exp in self.expeditions.items():
            if (key != exp.id or exp.destination not in LOCATIONS or exp.remaining < 0
                    or len(set(exp.heroes)) != len(exp.heroes)
                    or active_heroes.intersection(exp.heroes)
                    or any(h not in self.heroes or self.heroes[h]['location'] != key
                           for h in exp.heroes)
                    or any(r not in RESOURCES or n < 0 for r,n in exp.cargo.items())
                    or sum(exp.cargo.values()) > 6 * len(exp.heroes)):
                raise ValueError('Expedição/carga inválida')
            active_heroes.update(exp.heroes)
        if any(h['location'] != 'camp' for hero_id,h in self.heroes.items()
               if hero_id not in active_heroes):
            raise ValueError('Herói fora de expedição')
        if any(loc not in LOCATIONS or state['health'] < 0 or state['health'] > 3
               for loc,state in self.outposts.items()):
            raise ValueError('Posto avançado inválido')
        if set(self.gear) != set(self.heroes):
            raise ValueError('Inventário sem herói')
        seen = set()
        for hero_id, instances in self.gear.items():
            occupied = set()
            slots = set()
            has_bag = any(i['template']=='EXP-EQU-003' and i['slot']=='torso' for i in instances.values())
            for instance_id, item in instances.items():
                if instance_id in seen or item['template'] not in ITEMS:
                    raise ValueError('Instância duplicada/desconhecida')
                seen.add(instance_id)
                spec = ITEMS[item['template']]
                slot = item['slot']
                if slot not in spec['slots']:
                    raise ValueError('Slot incompatível')
                if slot == 'backpack':
                    if not has_bag:
                        raise ValueError('Mochila ausente')
                    x,y = item['x'],item['y']
                    width,height = spec['size']
                    cols,rows = EQUIPMENT['backpack_grid']
                    if min(x,y)<0 or x+width>cols or y+height>rows:
                        raise ValueError('Fora da grade')
                    cells = {(cx,cy) for cx in range(x,x+width) for cy in range(y,y+height)}
                    if occupied & cells:
                        raise ValueError('Sobreposição na mochila')
                    occupied |= cells
                else:
                    key = (slot,item.get('index',0))
                    if key in slots or (slot in ('pocket','hand') and not 0<=key[1]<2):
                        raise ValueError('Slot ocupado')
                    slots.add(key)

    def give_item(self, hero_id: str, instance_id: str, template_id: str,
                  slot: str, index: int = 0, x: int = 0, y: int = 0) -> None:
        if hero_id not in self.heroes or template_id not in ITEMS:
            raise ValueError('Herói/item inválido')
        if any(instance_id in inventory for inventory in self.gear.values()):
            raise ValueError('Instância já usada')
        item={'template':template_id,'slot':slot,'index':index,'x':x,'y':y,
              'durability':ITEMS[template_id]['durability']}
        self.gear[hero_id][instance_id]=item
        try:
            self.validate()
        except ValueError:
            del self.gear[hero_id][instance_id]
            raise

    def move_item(self, hero_id: str, instance_id: str, slot: str,
                  index: int = 0, x: int = 0, y: int = 0) -> None:
        item=self.gear[hero_id][instance_id]
        old=dict(item)
        item.update(slot=slot,index=index,x=x,y=y)
        try:
            self.validate()
        except ValueError:
            item.clear();item.update(old)
            raise

    def deposit(self, resource: str, amount: int) -> int:
        if resource not in RESOURCES or amount < 0:
            raise ValueError('Recurso inválido')
        accepted = min(amount, self.storage - sum(self.stock.values()))
        self.stock[resource] += accepted
        return accepted

    def recruit(self, npc_id: str) -> bool:
        if (npc_id not in NPCS or npc_id in self.npcs or self.residents >= self.beds
                or self.stock['food'] < self.residents + 1
                or self.stock['water'] < self.residents + 1):
            return False
        self.npcs[npc_id] = {'level':1,'job':None,'health':3}
        return True

    def assign(self, npc_id: str, job: str) -> None:
        if npc_id not in self.npcs or job != NPCS[npc_id]['job']:
            raise ValueError('Trabalho incompatível')
        self.npcs[npc_id]['job'] = job

    def level_npc(self, npc_id: str) -> bool:
        if npc_id not in self.npcs or self.npcs[npc_id]['level'] >= 3:
            return False
        self.npcs[npc_id]['level'] += 1
        return True

    def unlocked_skills(self, hero_id: str) -> list[str]:
        xp = self.heroes[hero_id]['xp']
        return [skill['id'] for skill in HEROES[hero_id]['skills'] if xp >= skill['xp']]

    def skill_bonus(self, hero_id: str, operation: str) -> int:
        if hero_id not in self.heroes:
            raise ValueError('Herói indisponível')
        xp = self.heroes[hero_id]['xp']
        return sum(skill['bonus'] for skill in HEROES[hero_id]['skills']
                   if skill['operation'] == operation and xp >= skill['xp'])

    def award_xp(self, hero_id: str, amount: int, combat: bool = False) -> int:
        if amount < 0:
            raise ValueError('XP negativo')
        hero = self.heroes[hero_id]
        if combat:
            amount = min(amount, DATA['rules']['combat_xp_cap'] - hero['combat_xp'])
        gained = min(amount, DATA['rules']['xp_cap'] - hero['xp'])
        hero['xp'] += gained
        if combat:
            hero['combat_xp'] += gained
        return gained

    def start_project(self, kind: str) -> bool:
        if kind not in STRUCTURES or kind in self.projects or kind in self.structures:
            return False
        spec = STRUCTURES[kind]
        if self.free_terrain < spec['terrain'] or any(self.stock[r] < n for r,n in spec['cost'].items()):
            return False
        for resource, amount in spec['cost'].items():
            self.stock[resource] -= amount
        self.projects[kind] = 0
        return True

    def work_project(self, kind: str, units: int = 1, hero_id: str | None = None) -> bool:
        if kind not in self.projects or units <= 0:
            raise ValueError('Projeto/trabalho inválido')
        if hero_id is not None:
            if hero_id not in self.heroes or self.heroes[hero_id]['location'] != 'camp':
                raise ValueError('Herói fora do abrigo')
            units += self.skill_bonus(hero_id,'build')
        self.projects[kind] += units
        if self.projects[kind] >= STRUCTURES[kind]['work']:
            self.structures[kind] = {'health': STRUCTURES[kind]['max_health'],'age':0}
            del self.projects[kind]
            return True
        return False

    def damage_structure(self, kind: str, amount: int = 1) -> None:
        if kind not in self.structures or amount <= 0:
            raise ValueError('Estrutura/dano inválido')
        self.structures[kind]['health'] = max(0,self.structures[kind]['health']-amount)

    def repair_structure(self, kind: str) -> bool:
        if kind not in self.structures or self.stock['scrap'] < 1 or self.structures[kind]['health'] >= STRUCTURES[kind]['max_health']:
            return False
        self.stock['scrap'] -= 1
        self.structures[kind]['health'] += 1
        return True

    def establish_outpost(self, location_id: str, npc_id: str) -> bool:
        """Local esgotado representa a limpeza; responsável fica vinculado ao posto."""
        if (location_id not in LOCATIONS or location_id in self.outposts
                or self.searches[location_id] != 0 or npc_id not in self.npcs
                or any(p['keeper'] == npc_id for p in self.outposts.values())
                or self.stock['wood'] < 2 or self.stock['scrap'] < 2):
            return False
        self.stock['wood'] -= 2
        self.stock['scrap'] -= 2
        self.outposts[location_id] = {'health':3,'keeper':npc_id}
        return True

    def attack_outpost(self, location_id: str, damage: int) -> None:
        if location_id not in self.outposts or damage <= 0:
            raise ValueError('Ataque inválido')
        post = self.outposts[location_id]
        post['health'] = max(0,post['health']-damage)

    def repair_outpost(self, location_id: str) -> bool:
        if (location_id not in self.outposts or self.stock['scrap'] < 1
                or self.outposts[location_id]['health'] >= 3):
            return False
        self.stock['scrap'] -= 1
        self.outposts[location_id]['health'] += 1
        return True

    def npc_defense(self, threat: int, line_of_sight: bool) -> int:
        """Atirador/guarda só age com munição e linha de visão; 1 munição/alvo."""
        if threat < 0:
            raise ValueError('Ameaça inválida')
        if not line_of_sight or 'watch' not in self.structures or self.structures['watch']['health'] == 0:
            return threat
        guards = sum(state['level'] for npc_id,state in self.npcs.items()
                     if state['job'] == 'guard' and NPCS[npc_id]['output'] == 'defense')
        stopped = min(threat,guards,self.stock['ammo'])
        self.stock['ammo'] -= stopped
        return threat-stopped

    def search(self, expedition_id: str) -> dict[str,int]:
        if expedition_id not in self.expeditions:
            raise ValueError('Expedição inexistente')
        exp = self.expeditions[expedition_id]
        if exp.remaining != 0 or exp.returning:
            raise ValueError('Equipe não está explorando o local')
        location_id = exp.destination
        if self.searches[location_id] <= 0:
            return {}
        capacity = 6 * len(exp.heroes) - sum(exp.cargo.values())
        if capacity <= 0:
            return {}
        self.searches[location_id] -= 1
        loot = LOCATIONS[location_id]['loot']
        found = {}
        for resource,amount in loot.items():
            found[resource] = min(amount,capacity)
            exp.cargo[resource] = exp.cargo.get(resource,0) + found[resource]
            capacity -= found[resource]
        return found

    def open_expedition(self, expedition_id: str, hero_ids: list[str], location_id: str) -> None:
        if expedition_id in self.expeditions or not hero_ids or len(set(hero_ids)) != len(hero_ids) or location_id not in LOCATIONS:
            raise ValueError('Expedição inválida')
        if any(h not in self.heroes or self.heroes[h]['location'] != 'camp' for h in hero_ids):
            raise ValueError('Herói indisponível')
        distance = LOCATIONS[location_id]['distance']
        segments = DATA['rules']['travel_segments'][distance]
        self.expeditions[expedition_id] = Expedition(expedition_id,hero_ids,location_id,distance,segments)
        for h in hero_ids:
            self.heroes[h]['location'] = expedition_id

    def advance_expedition(self, expedition_id: str) -> str:
        exp = self.expeditions[expedition_id]
        exp.remaining -= 1
        if exp.remaining > 0:
            return 'travel'
        if not exp.returning:
            exp.remaining = 0
            return 'arrived'
        delivered = {resource:self.deposit(resource,amount) for resource,amount in exp.cargo.items()}
        left_behind = {resource:amount-delivered[resource] for resource,amount in exp.cargo.items()
                       if amount > delivered[resource]}
        self.log.append({'day':self.day,'expedition':expedition_id,'delivered':delivered,
                         'left_behind':left_behind})
        for h in exp.heroes:
            self.heroes[h]['location'] = 'camp'
        del self.expeditions[expedition_id]
        return 'returned'

    def begin_return(self, expedition_id: str) -> None:
        exp = self.expeditions[expedition_id]
        if exp.remaining != 0 or exp.returning:
            raise ValueError('Retorno indisponível')
        exp.returning = True
        exp.remaining = DATA['rules']['travel_segments'][exp.distance]

    def end_day(self) -> dict:
        self.day += 1
        produced = dict.fromkeys(RESOURCES,0)
        # Especialistas geram apenas suas tarefas previstas; saídas abstratas não criam recurso.
        for npc_id,state in self.npcs.items():
            if state['job'] is None:
                continue
            output = NPCS[npc_id]['output']
            if output in RESOURCES:
                produced[output] += self.deposit(output,state['level'])
            elif output == 'repair' and self.stock['scrap']:
                damaged = next((kind for kind,structure in self.structures.items()
                                if structure['health'] < STRUCTURES[kind]['max_health']),None)
                if damaged:
                    self.repair_structure(damaged)
            elif output == 'build' and self.projects:
                self.work_project(next(iter(self.projects)),state['level'])
            elif output == 'research':
                self.clues += state['level']
            elif output == 'rescue' and self.stock['medicine']:
                injured = next((hero for hero in self.heroes.values() if hero['health'] < 3),None)
                if injured:
                    self.stock['medicine'] -= 1
                    injured['health'] += 1
        if 'garden' in self.structures and self.structures['garden']['health'] > 0:
            garden = self.structures['garden']
            garden['age'] += 1
            if garden['age'] >= DATA['rules']['garden_growth_days']:
                produced['food'] += self.deposit('food',DATA['rules']['garden_food_per_harvest'])
        need = self.residents
        missing = {}
        for resource in ('food','water'):
            missing[resource] = max(0,need-self.stock[resource])
            self.stock[resource] = max(0,self.stock[resource]-need)
        for loc_id,loc in LOCATIONS.items():
            if loc['renewal'] == 'natural' and self.searches[loc_id] < loc['searches']:
                self.searches[loc_id] += 1
        for hero in self.heroes.values():
            hero['combat_xp'] = 0
        crisis = self._roll_crisis()
        result = {'day':self.day,'produced':produced,'missing':missing,'stock':dict(self.stock),'crisis':crisis}
        self.log.append(result)
        self.validate()
        return result

    def _roll_crisis(self) -> str | None:
        rng = random.Random()
        rng.setstate(_tuples(self.rng_state))
        trigger = rng.randrange(DATA['rules']['crisis_chance_denominator']) == 0
        eligible = [c for c in CRISES.values() if c['target'] in self.structures
                    and c['id'] not in self.active_crises
                    and self.day-self.crises_last_day.get(c['id'],-999) > c['cooldown_days']]
        chosen = rng.choice(eligible) if trigger and eligible else None
        self.rng_state = _lists(rng.getstate())
        if chosen:
            self.crises_last_day[chosen['id']] = self.day
            self.active_crises.append(chosen['id'])
            self.damage_structure(chosen['target'])
            return chosen['id']
        return None

    def resolve_crisis(self, crisis_id: str, resource: str = 'scrap') -> bool:
        if crisis_id not in self.active_crises or self.stock.get(resource,0) < 1:
            return False
        self.stock[resource] -= 1
        self.active_crises.remove(crisis_id)
        return True

    def save(self, path: Path) -> None:
        self.validate()
        payload = asdict(self)
        payload['schema'] = 1
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    @classmethod
    def load(cls, path: Path) -> 'World':
        payload = json.loads(path.read_text(encoding='utf-8'))
        if payload.pop('schema',None) != 1:
            raise ValueError('Esquema inválido')
        payload['expeditions'] = {k:Expedition(**v) for k,v in payload['expeditions'].items()}
        world = cls(**payload)
        world.validate()
        return world


def _lists(value):
    return [_lists(v) for v in value] if isinstance(value,tuple) else value


def _tuples(value):
    return tuple(_tuples(v) for v in value) if isinstance(value,list) else value
