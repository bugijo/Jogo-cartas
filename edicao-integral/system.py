"""Motor determinístico experimental para recursos, campanha e expedições.

Todas as constantes de conteúdo vêm de data/system.json. Não substitui RULES.md.
"""
from __future__ import annotations

import json
import random
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from horde_deck02 import HordeDeck02
from travel_deck02 import CARD_IDS as TRAVEL_CARD_IDS, TravelDeck02
from travel02 import AUTO_EFFECTS, CHOICES
from ambush02 import Ambush02
from cistern_tactics02 import WEAPONS as WEAPONS02
from horde_deck02 import HordeDeck02 as _HordeDeck02
import community as community_rules

DATA = json.loads((Path(__file__).parent / 'data/system.json').read_text(encoding='utf-8'))
EQUIPMENT = json.loads((Path(__file__).parent / 'data/equipment.json').read_text(encoding='utf-8'))
TACTICS_DATA = json.loads((Path(__file__).parent / 'data/tactics.json').read_text(encoding='utf-8'))
REGIONAL_CONTACTS = json.loads((Path(__file__).parent / 'data/regional_campaign.json')
                               .read_text(encoding='utf-8'))
ITEMS = {item['id']:item for item in EQUIPMENT['items']}
HEROES = {h['id']: h for h in DATA['heroes']}
# A Cisterna 0.2 has twelve selectable founders. The regional prototype only
# models ten, while Téo and Célia were represented as NPCs. Keep their exact
# source identity/attributes as bridge profiles; legacy abilities remain in
# the continuity archive until they are explicitly ported.
_LEGACY_CATALOG = json.loads((Path(__file__).resolve().parents[1] / 'content/catalog.json')
                             .read_text(encoding='utf-8'))
for _hero in _LEGACY_CATALOG['heroes']:
    if _hero.get('initial') and _hero['id'] not in HEROES:
        HEROES[_hero['id']] = {
            'id': _hero['id'], 'name': _hero['name'],
            'profession': _hero['profession'], 'attributes': dict(_hero['attributes']),
            'skills': [], 'continuity_only': True,
        }
NPCS = {n['id']: n for n in DATA['npcs']}
STRUCTURES = {s['kind']: s for s in DATA['structures']}
LOCATIONS = {l['id']: l for l in DATA['locations']}
CRISES = {c['id']: c for c in DATA['crises']}
VEHICLES = {v['id']: v for v in DATA['vehicles']}
RESOURCES = ('food', 'water', 'wood', 'scrap', 'medicine', 'fuel', 'ammo')
# D (protótipo): Horta §61 regional; sucata no lugar dos Materiais da Cisterna.
GARDEN_BUILD = {'seeds': 1, 'scrap': 2, 'work': 2}


@dataclass
class Expedition:
    id: str
    heroes: list[str]
    destination: str
    distance: str
    remaining: int
    returning: bool = False
    cargo: dict[str, int] = field(default_factory=dict)
    vehicle_id: str | None = None
    crew: list[str] = field(default_factory=list)
    segment_cost: int = 0
    special_cargo: list[str] = field(default_factory=list)
    # Cartas de Viagem regionais (opcional; ver World.regional_travel_cards).
    travel_events: list[dict] = field(default_factory=list)
    pending_travel: dict | None = None
    leg_paid: bool = False
    night_extra_due: bool = False
    skip_return_card: int = 0
    route_known: bool = False
    bridge_known: bool = False


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
    vehicles: dict[str, dict] = field(default_factory=dict)
    gear: dict[str, dict] = field(default_factory=dict)
    continuity_people: list[dict] = field(default_factory=list)
    continuity_beds: int = 0
    shelter_health: int = 5
    shelter_morale: int = 5
    partial_defeat: bool = False
    unique_items_at_sites: dict[str, list[str]] = field(default_factory=dict)
    camp_xp: int = 0
    clues: int = 0
    used_structure_actions: dict[str, int] = field(default_factory=dict)
    encounters: dict[str, dict] = field(default_factory=dict)
    decisions: dict[str, str] = field(default_factory=dict)
    site_states: dict[str, dict] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)
    special_stock: list[str] = field(default_factory=list)
    final_defense: dict | None = None
    cistern_record: dict | None = None
    regional_clock: int = 0
    daily_expeditions: int = 0
    worked_today: list[str] = field(default_factory=list)
    departed_today: list[str] = field(default_factory=list)
    regional_horde_deck: dict | None = None
    regional_travel_deck: dict | None = None
    # Opcional: revela uma carta de Viagem por trecho pago (§29). Desligado
    # preserva os replays regionais registrados antes desta ponte.
    regional_travel_cards: bool = False
    # Efeitos de Viagem sem equivalente regional (mesma política da migração:
    # arquivados para auditoria, não gastáveis).
    regional_travel_archive: dict[str, int] = field(
        default_factory=lambda: {'materials': 0, 'pressure': 0})
    # Filtro da Cisterna consertado no mesmo abrigo (decisão aprovada em
    # 2026-10-29): produz `output` água a cada amanhecer regional, pelo depósito.
    # A produção é ligada por `regional_filter_production`, desligada por padrão
    # para preservar os replays regionais certificados (como a ponte de Viagem).
    continuity_filter: dict | None = None
    regional_filter_production: bool = False
    # Horta §61 concluída na Cisterna (H1, aprovada em 2026-10-29): produz
    # `output` comida no dia em que um herói ou adulto é designado no amanhecer.
    continuity_garden: dict | None = None
    # Acampamento regional (2026-10-30). F (aprovada): prioridade de comida no
    # depósito. G, C2 e D: protótipos ligados só por `enable_regional_prototypes`.
    # None preserva os saves e replays regionais anteriores.
    regional_camp: dict | None = None
    # Regras Comunidade (Missão Mestre, aprovadas em 2026-10-30): trabalhadores,
    # profissões, viagens automáticas, recursos naturais (`community.py`).
    # None preserva saves e replays certificados.
    community: dict | None = None
    garden_worker: str | None = None
    guarding: dict[str, int] = field(default_factory=dict)
    rng_state: object = None
    log: list[dict] = field(default_factory=list)

    @classmethod
    def new(cls, seed: int, hero_ids: list[str], stock: dict[str, int] | None = None) -> 'World':
        if not hero_ids or len(set(hero_ids)) != len(hero_ids) or any(h not in HEROES for h in hero_ids):
            raise ValueError('Heróis iniciais inválidos')
        world = cls(seed=seed)
        world.heroes = {h:{'xp':0,'health':3,'wounds':0,'hungry':False,
                          'thirsty':False,'streak':0,'combat_xp':0,
                          'location':'camp','infected':False,'fatigue':0}
                        for h in hero_ids}
        for hero in world.heroes.values():
            hero['actions']=DATA['rules']['actions']
        world.gear = {h:{} for h in hero_ids}
        world.searches = {key:loc['searches'] for key,loc in LOCATIONS.items()}
        world.stock.update(stock or {})
        world.rng_state = _lists(random.Random(seed).getstate())
        world.regional_travel_deck = TravelDeck02.new(seed + 8103).snapshot()
        world.validate()
        return world

    @property
    def beds(self) -> int:
        return (DATA['rules']['beds_base'] + self.continuity_beds
                + sum(STRUCTURES[k]['beds_bonus'] for k in self.structures))

    @property
    def storage(self) -> int:
        skill=max((self.skill_bonus(hero_id,'storage') for hero_id in self.heroes),default=0)
        return DATA['rules']['storage_base'] + sum(STRUCTURES[k]['storage_bonus'] for k in self.structures)+skill

    @property
    def water_capacity(self) -> int | None:
        """Comunidade: água em tanques próprios, fora do depósito seco."""
        if self.community is None:
            return None
        tanks = community_rules.RULES['water_tanks']
        return tanks['base'] + tanks['per_reservoir'] * ('reservoir' in self.structures)

    def free_space(self, resource: str) -> int:
        if self.community is not None:
            if resource == 'water':
                return self.water_capacity - self.stock['water']
            return self.storage - sum(v for k, v in self.stock.items() if k != 'water')
        return self.storage - sum(self.stock.values())

    @property
    def residents(self) -> int:
        civilians = sum(person['kind'] in ('adult', 'child')
                        for person in self.continuity_people)
        shelter_npcs=sum(state['location'] not in LOCATIONS
                         for state in self.npcs.values())
        return len(self.heroes) + shelter_npcs + civilians

    @property
    def consumers(self) -> int:
        """People and dogs carried across from the 0.2 shelter ledger."""
        dogs = sum(person['kind'] == 'dog' for person in self.continuity_people)
        # Quem está em viagem automática come da própria ração, não no abrigo.
        return self.residents + dogs - len(community_rules.away(self))

    def meal_people(self) -> dict[str, dict]:
        """Return this night's actual consumers keyed by their persistent identity."""
        people = dict(self.heroes)
        people.update({identifier: person for identifier, person in self.npcs.items()
                       if person.get('location') not in LOCATIONS})
        people.update({person['id']: person for person in self.continuity_people})
        for identifier in community_rules.away(self):
            people.pop(identifier, None)
        if len(people) != self.consumers:
            raise ValueError('Identidades de consumidores não correspondem ao censo')
        return people

    @property
    def cistern_verified(self) -> bool:
        return bool(self.cistern_record
                    and self.cistern_record.get('status')=='verified_victory'
                    and self.cistern_record.get('source')=='cistern02')

    @property
    def continuous_campaign(self) -> bool:
        return bool(self.cistern_verified
                    and (self.cistern_record or {}).get('migration',{}).get('receipt'))

    def regional_contact_identity_available(self, npc_id: str,
                                            destination: str) -> bool:
        """Avoid recreating a founder or a named Cisterna rescue as a copy."""
        contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc_id)
        if not contact or contact.get('location')!=destination:
            return False
        if NPCS[npc_id].get('source_hero_id') in self.heroes:
            return False
        existing=self.npcs.get(npc_id)
        if existing is not None and existing.get('location')!=destination:
            return False
        group_id=contact.get('source_group_id')
        migration=(self.cistern_record or {}).get('migration',{})
        source_archive=migration.get('source_archive',{})
        cistern=source_archive.get('cistern',{}) if isinstance(source_archive,dict) else {}
        if (group_id and cistern.get('rescue_history',{}).get(group_id)=='welcome'):
            return False
        return True

    @property
    def free_terrain(self) -> int:
        return DATA['rules']['terrain_base'] - sum(STRUCTURES[k]['terrain'] for k in self.structures) - sum(STRUCTURES[k]['terrain'] for k in self.projects)

    def validate(self) -> None:
        archive=self.regional_travel_archive
        if (not isinstance(archive,dict) or set(archive)!={'materials','pressure'}
                or any(not isinstance(value,int) or isinstance(value,bool) or value<0
                       for value in archive.values())):
            raise ValueError('Arquivo de efeitos de Viagem regional inválido')
        for exp in self.expeditions.values():
            pending=exp.pending_travel
            if pending is not None and (not self.regional_travel_cards
                                        or pending.get('card_id') not in TRAVEL_CARD_IDS):
                raise ValueError('Carta de Viagem pendente inválida no save')
        if (not isinstance(self.regional_clock,int) or isinstance(self.regional_clock,bool)
                or not 0<=self.regional_clock<=10):
            raise ValueError('Relógio regional deve permanecer entre zero e dez segmentos')
        if (not isinstance(self.daily_expeditions,int) or isinstance(self.daily_expeditions,bool)
                or not 0<=self.daily_expeditions<=1):
            raise ValueError('Contador diário de expedições inválido')
        if (len(self.worked_today) != len(set(self.worked_today))
                or any(person not in {*self.heroes, *self.npcs}
                       for person in self.worked_today)
                or len(self.departed_today) != len(set(self.departed_today))
                or any(person not in {*self.heroes, *self.npcs}
                       for person in self.departed_today)):
            raise ValueError('Registro diário de trabalho/saída inválido')
        if self.regional_horde_deck is not None:
            HordeDeck02.from_snapshot(self.regional_horde_deck)
        if self.regional_travel_deck is not None:
            TravelDeck02.from_snapshot(self.regional_travel_deck)
        if any(v < 0 or not isinstance(v,int) for v in self.stock.values()):
            raise ValueError('Estoque inválido')
        if not isinstance(self.clues,int) or isinstance(self.clues,bool) or self.clues<0:
            raise ValueError('Contador de pistas inválido')
        if self.continuity_filter is not None and (
                not isinstance(self.continuity_filter, dict)
                or set(self.continuity_filter) != {'source', 'output', 'active'}
                or self.continuity_filter['source'] != 'cistern02'
                or not isinstance(self.continuity_filter['output'], int)
                or isinstance(self.continuity_filter['output'], bool)
                or self.continuity_filter['output'] < 1
                or not isinstance(self.continuity_filter['active'], bool)
                or not self.cistern_verified):
            raise ValueError('Filtro de continuidade inválido')
        if not isinstance(self.regional_filter_production, bool):
            raise ValueError('Opção de produção do filtro inválida')
        garden = self.continuity_garden
        if garden is not None and (
                not isinstance(garden, dict)
                or set(garden) - {'discard_water'} != {'source', 'output', 'active', 'worker'}
                or 'discard_water' in garden and (garden['discard_water'] is not True
                                                  or garden['worker'] is None)
                or garden['source'] not in ('cistern02', 'regional_build')
                or garden['output'] != 4
                or not isinstance(garden['active'], bool)
                or garden['worker'] is not None
                and garden['worker'] not in self.worked_today
                and garden['worker'] not in {item['id'] for item in self.continuity_people}
                or not self.cistern_verified):
            raise ValueError('Horta de continuidade inválida')
        self._validate_regional_camp()
        community_rules.validate(self)
        if (any(k not in RESOURCES for k in self.stock)
                or any(self.free_space(k) < 0 for k in ('food', 'water'))):
            raise ValueError('Depósito excedido')
        if (self.residents > self.beds + community_rules.bed_allowance(self)
                or self.free_terrain < 0):
            raise ValueError('Capacidade excedida')
        continuity_ids = [person.get('id') for person in self.continuity_people]
        if (len(continuity_ids) != len(set(continuity_ids))
                or any(not person.get('id') or person.get('kind') not in
                       ('adult', 'child', 'dog') for person in self.continuity_people)
                or set(continuity_ids) & (set(self.heroes) | set(self.npcs))
                or not isinstance(self.continuity_beds, int)):
            raise ValueError('Pessoas/capacidade de continuidade inválidas')
        if any(v < 0 for v in self.searches.values()):
            raise ValueError('Contador de busca negativo')
        if any(location not in LOCATIONS
               or any(item not in ('battery','access_card','transmitter') for item in items)
               for location, items in self.unique_items_at_sites.items()):
            raise ValueError('Item único em local inválido')
        if any(h not in HEROES or state['xp'] > 100
               or not isinstance(state['health'], int)
               or isinstance(state['health'], bool)
               or not 0 <= state['health'] <= 3
               or ('wounds' in state and state['wounds'] != 3-state['health'])
               or not isinstance(state.get('fatigue', 0), int)
               or isinstance(state.get('fatigue', 0), bool)
               or not 0 <= state.get('fatigue', 0) <= 3
               or not 0 <= state['actions'] <= DATA['rules']['actions']
               for h,state in self.heroes.items()):
            raise ValueError('Herói inválido; Fadiga deve ficar entre zero e três')
        if (not isinstance(self.shelter_health, int) or isinstance(self.shelter_health, bool)
                or not 0 <= self.shelter_health <= 5
                or not isinstance(self.shelter_morale, int)
                or isinstance(self.shelter_morale, bool)
                or not 0 <= self.shelter_morale <= 5
                or not isinstance(self.partial_defeat, bool)):
            raise ValueError('Estado de Saúde/Moral do abrigo inválido')
        for identifier, person in [*self.heroes.items(), *self.npcs.items(),
                                   *((item.get('id'), item)
                                     for item in self.continuity_people)]:
            if (not isinstance(person.get('streak', 0), int)
                    or isinstance(person.get('streak', 0), bool)
                    or person.get('streak', 0) < 0
                    or not isinstance(person.get('wounds', 0), int)
                    or isinstance(person.get('wounds', 0), bool)
                    or not 0 <= person.get('wounds', 0) <= 3
                    or not isinstance(person.get('hungry', False), bool)
                    or not isinstance(person.get('thirsty', False), bool)):
                raise ValueError('Estado individual de privação inválido')
        for person in [*self.heroes.values(), *self.npcs.values()]:
            if ('health' in person and (
                    not isinstance(person['health'], int)
                    or isinstance(person['health'], bool)
                    or not 0 <= person['health'] <= 3
                    or ('wounds' in person
                        and person['wounds'] != 3-person['health']))):
                raise ValueError('Estado de Saúde/Ferimentos individual inconsistente')
        if self.garden_worker is not None and self.garden_worker not in self.heroes:
            raise ValueError('Trabalhador de horta inválido')
        if any(hero not in self.heroes or points<0 for hero,points in self.guarding.items()):
            raise ValueError('Guarda inválida')
        if any(n not in NPCS or not 1 <= state['level'] <= 3
               or ('fatigue' in state and
                   (not isinstance(state['fatigue'], int)
                    or isinstance(state['fatigue'], bool)
                    or not 0 <= state['fatigue'] <= 3))
               for n,state in self.npcs.items()):
            raise ValueError('NPC inválido')
        if any(NPCS[n].get('source_hero_id') in self.heroes for n in self.npcs):
            raise ValueError('Fundador duplicado como NPC')
        active_heroes = set()
        for key, exp in self.expeditions.items():
            if (key != exp.id or exp.destination not in LOCATIONS or exp.remaining < 0
                    or len(set(exp.heroes)) != len(exp.heroes)
                    or len(set(exp.crew)) != len(exp.crew)
                    or active_heroes.intersection(exp.heroes)
                    or any(h not in self.heroes or self.heroes[h]['location'] != key
                           for h in exp.heroes)
                    or any(n not in self.npcs or self.npcs[n]['location'] != key
                           for n in exp.crew)
                    or any(r not in RESOURCES or n < 0 for r,n in exp.cargo.items())
                    or any(item not in ('transmitter', 'battery', 'access_card')
                           for item in exp.special_cargo)
                    or (exp.vehicle_id is None and sum(exp.cargo.values())+len(exp.special_cargo) > 6 * len(exp.heroes))):
                raise ValueError('Expedição/carga inválida')
            if exp.vehicle_id is not None:
                if (exp.vehicle_id not in self.vehicles
                        or self.vehicles[exp.vehicle_id]['location'] != key
                        or len(exp.heroes)+len(exp.crew) > VEHICLES[exp.vehicle_id]['seats']
                        or sum(exp.cargo.values())+len(exp.special_cargo) > VEHICLES[exp.vehicle_id]['cargo_capacity']):
                    raise ValueError('Veículo/carga inválidos')
            active_heroes.update(exp.heroes)
        if any(h['location'] != 'camp' for hero_id,h in self.heroes.items()
               if hero_id not in active_heroes):
            raise ValueError('Herói fora de expedição')
        active_npcs={n for exp in self.expeditions.values() for n in exp.crew}
        if any(n['location'] != 'camp' and n['location'] not in LOCATIONS
               for npc_id,n in self.npcs.items() if npc_id not in active_npcs):
            raise ValueError('NPC fora de expedição')
        if any(vid not in VEHICLES or state['location'] not in
               ('camp', *LOCATIONS.keys(), *(self.expeditions.keys()))
               or not 0 <= state['health'] <= VEHICLES[vid]['health']
               for vid,state in self.vehicles.items()):
            raise ValueError('Veículo inválido')
        canonical_van=self.vehicles.get('EXP-VEI-02')
        if (canonical_van and canonical_van['location']=='EXP-LOC-07'
                and canonical_van['health']>0):
            repaired=(self.site_states.get('EXP-LOC-07',{}).get('van_state')=='operational'
                      or any(expedition_id in self.encounters
                             and self.encounters[expedition_id].get('map')=='gas_station_02'
                             and self.encounters[expedition_id].get('van_state')=='operational'
                             for expedition_id,expedition in self.expeditions.items()
                             if expedition.destination=='EXP-LOC-07'))
            if not repaired:
                raise ValueError('Van canônica sem recibo de reparo no Posto')
        if any(item not in ('transmitter', 'battery', 'access_card') for item in self.special_stock):
            raise ValueError('Peça de missão desconhecida')
        for unique_item in ('transmitter', 'battery', 'access_card'):
            copies = (self.special_stock.count(unique_item)
                      + sum(exp.special_cargo.count(unique_item)
                            for exp in self.expeditions.values())
                      + sum(items.count(unique_item)
                            for items in self.unique_items_at_sites.values()))
            if copies > 1:
                raise ValueError('Peça única duplicada')
        if self.final_defense is not None:
            defense=self.final_defense
            defense_zones=set(TACTICS_DATA['maps']['camp_final']['zones'])
            if (defense.get('status') not in ('active','won','lost','retreated')
                    or not 0<=defense.get('integrity',-1)<=3
                    or not 1<=defense.get('wave',-1)<=3
                    or defense.get('map')!='camp_final'
                    or any(h not in self.heroes or zone not in defense_zones
                           for h,zone in defense.get('heroes',{}).items())
                    or any(enemy.get('kind') not in TACTICS_DATA['enemies']
                           or enemy.get('zone') not in defense_zones
                           or not 0<enemy.get('health',0)<=TACTICS_DATA['enemies'][enemy['kind']]['health']
                           for enemy in defense.get('enemies',{}).values())):
                raise ValueError('Defesa final inválida')
        for expedition_id, encounter in self.encounters.items():
            if expedition_id not in self.expeditions or encounter.get('map') not in TACTICS_DATA['maps']:
                raise ValueError('Encontro sem expedição/mapa')
            map_data=TACTICS_DATA['maps'][encounter['map']]
            zones=set(map_data['zones'])
            exp=self.expeditions[expedition_id]
            if (exp.remaining!=0 or exp.returning
                    or set(encounter['heroes'])!=set(exp.heroes)
                    or any(zone not in zones for zone in encounter['heroes'].values())
                    or encounter.get('search_zones')!=map_data['search']
                    or len(encounter.get('enemies',{}))>24
                    or not 0<=encounter.get('pressure',0)<=3):
                raise ValueError('Posições do encontro inválidas')
            if ('fuel_cache_collected' in encounter
                    and not isinstance(encounter['fuel_cache_collected'], bool)):
                raise ValueError('Estado da reserva experimental inválido')
            discovered=encounter.get('discovered_npcs', [])
            if (not isinstance(discovered, list) or len(discovered)!=len(set(discovered))
                    or any(npc_id not in REGIONAL_CONTACTS.get('contacts', {})
                           or REGIONAL_CONTACTS['contacts'][npc_id]['map']!=encounter['map']
                           for npc_id in discovered)):
                raise ValueError('Registro de investigação de sobreviventes inválido')
            for npc_id, zone in encounter.get('npc_contacts', {}).items():
                contact=REGIONAL_CONTACTS.get('contacts', {}).get(npc_id)
                stranded=self.npcs.get(npc_id)
                if (not contact or (stranded is not None
                                    and stranded['location']!=contact['location'])
                        or contact['map']!=encounter['map']
                        or zone!=contact['zone'] or zone not in zones
                        or not self.regional_contact_identity_available(
                            npc_id,contact['location'])):
                    raise ValueError('Contato de sobrevivente inválido')
            for npc_id, hero_id in encounter.get('npc_followers', {}).items():
                if (npc_id not in exp.crew or npc_id not in self.npcs
                        or self.npcs[npc_id]['location']!=expedition_id
                        or hero_id not in encounter['heroes']):
                    raise ValueError('Acompanhante do encontro inválido')
            for enemy in encounter['enemies'].values():
                kind=enemy.get('kind')
                if (kind not in TACTICS_DATA['enemies'] or enemy.get('zone') not in zones
                        or not 0<enemy.get('health',0)<=TACTICS_DATA['enemies'][kind]['health']):
                    raise ValueError('Inimigo inválido')
        if any(loc not in LOCATIONS or state['health'] < 0 or state['health'] > 3
               for loc,state in self.outposts.items()):
            raise ValueError('Posto avançado inválido')
        evidence_rows=[row for row in self.log
                       if row.get('action')=='collect_regional_evidence']
        permitted_evidence={contact['evidence']['id']:(npc_id,contact)
                            for npc_id,contact in REGIONAL_CONTACTS.get(
                                'contacts',{}).items() if contact.get('evidence')}
        evidence_ids=[row.get('evidence_id') for row in evidence_rows]
        if len(evidence_ids)!=len(set(evidence_ids)):
            raise ValueError('Recibos de evidência regional duplicados/inválidos')
        for log_index,row in enumerate(self.log):
            if row.get('action')!='collect_regional_evidence':
                continue
            identity=permitted_evidence.get(row.get('evidence_id'))
            if identity is None:
                raise ValueError('Recibo de evidência regional inválido')
            npc_id,contact=identity
            evidence=contact['evidence']
            if (row.get('npc')!=npc_id or row.get('location')!=contact['location']
                    or row.get('zone')!=contact['zone']
                    or row.get('clues_awarded')!=evidence['clues']
                    or row.get('action_cost')!=evidence['action_cost']
                    or row.get('hero') not in self.heroes
                    or not isinstance(row.get('expedition'),str)
                    or not row['expedition']
                    or not isinstance(row.get('total_clues'),int)
                    or isinstance(row.get('total_clues'),bool)
                    or row.get('total_clues',0)<evidence['clues']):
                raise ValueError('recibo de evidência regional diverge do catálogo')
            prior=self.log[:log_index]
            expedition_id=row['expedition']
            has_trip=any(entry.get('action')=='open_expedition'
                         and entry.get('expedition')==expedition_id
                         and entry.get('destination')==contact['location']
                         for entry in prior)
            has_investigation=any(entry.get('action')=='investigate_physical_contact'
                                  and entry.get('npc')==npc_id
                                  and entry.get('location')==contact['location']
                                  for entry in prior)
            if not has_trip or not has_investigation:
                raise ValueError('recibo de evidência sem investigação anterior na expedição')
        if any('fuel_cache_collected' in site
               and not isinstance(site['fuel_cache_collected'], bool)
               for site in self.site_states.values()):
            raise ValueError('Estado salvo da reserva experimental inválido')
        for location,site in self.site_states.items():
            discovered=site.get('discovered_npcs', [])
            if (not isinstance(discovered, list) or len(discovered)!=len(set(discovered))
                    or any(npc_id not in REGIONAL_CONTACTS.get('contacts', {})
                           or REGIONAL_CONTACTS['contacts'][npc_id]['location']!=location
                           for npc_id in discovered)):
                raise ValueError('Investigação salva de sobreviventes inválida')
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
                if not 0 <= item['durability'] <= spec['durability']:
                    raise ValueError('Durabilidade inválida')
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
                  index: int = 0, x: int = 0, y: int = 0, in_combat: bool = False) -> None:
        if in_combat and self.heroes[hero_id]['actions'] < 1:
            raise ValueError('Sem ações para troca')
        item=self.gear[hero_id][instance_id]
        old=dict(item)
        item.update(slot=slot,index=index,x=x,y=y)
        try:
            self.validate()
        except ValueError:
            item.clear();item.update(old)
            raise
        if in_combat:
            self.heroes[hero_id]['actions']-=1

    def begin_round(self) -> None:
        if self.continuous_campaign and (self.expeditions or self.encounters):
            raise ValueError('Use TacticalGame.activate para renovar PA e avançar o relógio')
        self._refresh_actions()

    def _refresh_actions(self) -> None:
        for hero in self.heroes.values():
            penalty=(int(hero.get('fatigue',0)>=2)
                     + int(hero.get('hungry',False))
                     + int(hero.get('thirsty',False)))
            hero['actions']=max(1,DATA['rules']['actions']-penalty)
        self.guarding.clear()

    def advance_regional_segment(self, expedition_id: str, kind: str) -> dict | None:
        """Charge one canonical travel/map segment only after Cisterna migration."""
        if not self.continuous_campaign:
            return None
        if (expedition_id not in self.expeditions or kind not in ('travel','map_round')
                or self.regional_clock>=10):
            raise ValueError('Relógio de dez segmentos esgotado ou segmento inválido')
        self.regional_clock+=1
        night=self.regional_clock>=9
        affected=[]
        if night:
            exp=self.expeditions[expedition_id]
            for person_id in [*exp.heroes,*exp.crew]:
                person=(self.heroes.get(person_id) if person_id in self.heroes
                        else self.npcs.get(person_id))
                if person is None:
                    continue
                person['fatigue']=min(3,person.get('fatigue',0)+1)
                affected.append(person_id)
        receipt={'segment':self.regional_clock,'kind':kind,'night':night,
                 'fatigue':affected}
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'regional_clock_segment',**receipt})
        return receipt

    def guard(self,hero_id:str) -> int:
        hero=self.heroes[hero_id]
        if hero['health']<1 or hero['actions']<1:
            raise ValueError('Guarda indisponível')
        hero['actions']-=1
        points=1+self.skill_bonus(hero_id,'defense')
        self.guarding[hero_id]=self.guarding.get(hero_id,0)+points
        return points

    def rescue_hero(self,rescuer_id:str,target_id:str) -> int:
        rescuer=self.heroes[rescuer_id];target=self.heroes[target_id]
        if (rescuer['health']<1 or rescuer['actions']<1 or self.stock['medicine']<1
                or rescuer['location']!=target['location'] or target['health']>=3):
            raise ValueError('Resgate indisponível')
        self.stock['medicine']-=1
        rescuer['actions']-=1
        self._set_hero_health(target_id, min(3,target['health']+1
                                            +self.skill_bonus(rescuer_id,'rescue')))
        return target['health']

    def _set_hero_health(self, hero_id: str, health: int) -> None:
        """Keep wounds as a projection of the authoritative remaining health."""
        hero = self.heroes[hero_id]
        hero['health'] = max(0, min(3, int(health)))
        hero['wounds'] = 3-hero['health']
        source = hero.get('continuity_state')
        if isinstance(source, dict):
            source['health'] = hero['health']
            source['wounds'] = hero['wounds']

    def roll_infection(self,hero_id:str) -> dict:
        roll=self._d6()[0]
        adjusted=min(6,roll+self.skill_bonus(hero_id,'infection'))
        infected=adjusted<=2
        self.heroes[hero_id]['infected']=self.heroes[hero_id]['infected'] or infected
        return {'roll':roll,'adjusted':adjusted,'infected':infected}

    def assign_garden(self,hero_id:str) -> None:
        if ('garden' not in self.structures or self.structures['garden']['health']<=0):
            raise ValueError('Horta ativa ausente')
        self._require_working_hero(hero_id)
        self.garden_worker=hero_id
        self.worked_today.append(hero_id)

    def assign_continuity_garden(self, person_id: str, discard_water: bool = False) -> None:
        """Amanhecer: um herói ou adulto apto trabalha na Horta da Cisterna.

        `discard_water`: o abrigo aceita descartar, na colheita, só a água
        excedente necessária para a comida caber no depósito.
        """
        garden = self.continuity_garden
        if garden is None or not garden['active'] or garden['worker'] is not None:
            raise ValueError('Horta de continuidade indisponível hoje')
        if self.partial_defeat or self.continuous_campaign and (
                self.expeditions or self.daily_expeditions):
            raise ValueError('Trabalho da Horta se planeja antes da expedição')
        if self.community is not None and (person_id in community_rules.away(self)
                                           or person_id in self.community['jobs']):
            raise ValueError('Trabalhador da Horta indisponível')
        if person_id in self.heroes:
            self._require_working_hero(person_id)
        else:
            person = next((item for item in self.continuity_people
                           if item['id'] == person_id), None)
            if (person is None or person['kind'] != 'adult'
                    or person.get('wounds', 0) >= 3 or person.get('fatigue', 0) >= 3
                    or person.get('hungry') or person.get('thirsty')):
                raise ValueError('Trabalhador da Horta indisponível')
        garden['worker'] = person_id
        if discard_water:
            garden['discard_water'] = True
        if person_id in self.heroes:
            self.worked_today.append(person_id)

    def _continuity_garden_harvest(self) -> dict | None:
        """Fase de trabalhos: o trabalhador designado colhe antes da refeição."""
        garden = self.continuity_garden
        if garden is None or garden['worker'] is None:
            return None
        worker = garden['worker']
        garden['worker'] = None
        discard = garden.pop('discard_water', False)
        if worker not in self.worked_today:
            # Civil migrado: conta como trabalho até o fim do dia (sem recuperação).
            self.worked_today.append(worker)
        if not garden['active']:
            return {'worker': worker, 'produced': 0, 'not_stored': 0, 'reason': 'inactive'}
        receipt = {'worker': worker}
        output = garden['output'] + community_rules.garden_bonus(self, worker)
        if discard and self.community is None:  # Comunidade: água tem tanque próprio
            # Descarte voluntário: só o que falta de espaço e só a água acima do
            # consumo previsto da refeição desta noite.
            free = self.free_space('food')
            spare = max(0, self.stock['water'] - len(self.meal_people()))
            receipt['water_discarded'] = min(spare, max(0, output - free))
            self.stock['water'] -= receipt['water_discarded']
        produced = self.deposit('food', output)
        receipt.update(produced=produced, not_stored=output - produced)
        return receipt

    # --- acampamento regional: F aprovada; G, C2 e D em protótipo ---------------
    CAMP_PROTOTYPES = ('bridge', 'forage', 'garden_build')

    def _camp(self) -> dict:
        if self.regional_camp is None:
            self.regional_camp = {}
        return self.regional_camp

    def _validate_regional_camp(self) -> None:
        camp = self.regional_camp
        if camp is None:
            return
        allowed = {'food_priority', 'prototypes', 'bridge_claimed', 'forage',
                   'garden_build', 'seeds_spent'}
        ok = isinstance(camp, dict) and set(camp) <= allowed and all(
            isinstance(camp.get(key, False), bool)
            for key in ('food_priority', 'bridge_claimed', 'seeds_spent'))
        protos = camp.get('prototypes', []) if ok else None
        ok = ok and isinstance(protos, list) and len(protos) == len(set(protos)) \
            and set(protos) <= set(self.CAMP_PROTOTYPES)
        forage = camp.get('forage') if ok else None
        if ok and forage is not None:
            ok = ('forage' in protos and isinstance(forage, dict)
                  and set(forage) == {'pool', 'max', 'regrow', 'workers'}
                  and all(isinstance(forage[k], int) and not isinstance(forage[k], bool)
                          for k in ('pool', 'max', 'regrow'))
                  and 0 <= forage['pool'] <= forage['max'] and forage['regrow'] >= 0
                  and isinstance(forage['workers'], list)
                  and len(forage['workers']) == len(set(forage['workers'])))
        build = camp.get('garden_build') if ok else None
        if ok and build is not None:
            ok = ('garden_build' in protos and camp.get('seeds_spent') is True
                  and isinstance(build, dict)
                  and set(build) == {'work', 'workers', 'done'}
                  and isinstance(build['work'], int) and not isinstance(build['work'], bool)
                  and 0 <= build['work'] <= GARDEN_BUILD['work']
                  and isinstance(build['workers'], list) and len(build['workers']) <= 2
                  and build['done'] == (build['work'] >= GARDEN_BUILD['work']))
        if not ok:
            raise ValueError('Estado do acampamento regional inválido')

    def enable_regional_prototypes(self, *names: str, forage_max: int | None = None,
                                   forage_regrow: int | None = None) -> None:
        """Liga protótipos aprovados para teste (G, C2, D). Não é regra definitiva."""
        if not self.continuous_campaign or not self.cistern_verified:
            raise ValueError('Protótipos só na campanha regional após a Cisterna')
        if not names or set(names) - set(self.CAMP_PROTOTYPES):
            raise ValueError('Protótipo desconhecido')
        camp = self._camp()
        protos = camp.setdefault('prototypes', [])
        for name in names:
            if name not in protos:
                protos.append(name)
        if 'forage' in names and 'forage' not in camp:
            consumers = len(self.meal_people())
            top = forage_max if forage_max is not None else 2 * consumers
            camp['forage'] = {'pool': top, 'max': top, 'workers': [],
                              'regrow': forage_regrow if forage_regrow is not None
                              else -(-consumers // 4)}
        self.validate()

    def set_storage_priority(self, food_first: bool) -> None:
        """F (aprovada em 2026-10-30): o abrigo prioriza comida no depósito.

        Com a prioridade ligada, toda comida que chega descarta só a água que
        falta de espaço e só a acima do consumo previsto da noite. Capacidade
        do depósito inalterada; cada descarte entra no histórico.
        """
        if not isinstance(food_first, bool):
            raise ValueError('Prioridade de depósito inválida')
        self._camp()['food_priority'] = food_first
        self.log.append({'day': self.day, 'action': 'storage_priority',
                         'food_first': food_first})

    def _make_room_for_food(self, amount: int, reason: str) -> int:
        if self.community is not None:
            return 0  # Comunidade: água em tanques próprios não ocupa o depósito
        free = self.free_space('food')
        spare = max(0, self.stock['water'] - len(self.meal_people()))
        discarded = min(spare, max(0, amount - free))
        if discarded:
            self.stock['water'] -= discarded
            self.log.append({'day': self.day, 'action': 'storage_discard',
                             'resource': 'water', 'amount': discarded,
                             'for': 'food', 'reason': reason})
        return discarded

    def _require_camp_prototype(self, name: str) -> dict:
        camp = self.regional_camp or {}
        if name not in camp.get('prototypes', []):
            raise ValueError('Protótipo desligado nesta campanha')
        return camp

    def _require_dawn_camp_worker(self, person_id: str) -> None:
        """Trabalho do acampamento: amanhecer, um trabalho por pessoa por dia."""
        if self.partial_defeat or self.continuous_campaign and (
                self.expeditions or self.daily_expeditions):
            raise ValueError('Trabalho do acampamento se planeja antes da expedição')
        camp = self.regional_camp or {}
        busy = set(self.worked_today) | set(self.departed_today)
        busy |= set((camp.get('forage') or {}).get('workers', []))
        busy |= set((camp.get('garden_build') or {}).get('workers', []))
        if (self.continuity_garden or {}).get('worker'):
            busy.add(self.continuity_garden['worker'])
        if self.community is not None:
            busy |= community_rules.away(self) | set(self.community['jobs'])
        if person_id in busy:
            raise ValueError('Trabalhador já ocupado hoje')
        if person_id in self.heroes:
            self._require_working_hero(person_id)
            return
        person = next((item for item in self.continuity_people
                       if item['id'] == person_id), None)
        if (person is None or person['kind'] != 'adult'
                or person.get('wounds', 0) >= 3 or person.get('fatigue', 0) >= 3
                or person.get('hungry') or person.get('thirsty')):
            raise ValueError('Trabalhador do acampamento indisponível')

    def claim_bridge_ration(self) -> dict:
        """G (protótipo): ração-ponte única na chegada, 1 comida por consumidor.

        Origem: a Ponte acolhe o grupo evacuado (CAMPAIGN, Evacuação) e entrega
        uma vez a ração de viagem. Só no dia da migração; nunca de novo.
        """
        camp = self._require_camp_prototype('bridge')
        if camp.get('bridge_claimed'):
            raise ValueError('Ração-ponte já recebida')
        arrived = any(row.get('event') == 'campaign_transition' for row in self.log)
        if not arrived or any('missing' in row for row in self.log):
            raise ValueError('Ração-ponte só no dia da chegada')
        amount = len(self.meal_people())
        stored = self.deposit('food', amount)
        camp['bridge_claimed'] = True
        receipt = {'day': self.day, 'action': 'bridge_ration', 'food': amount,
                   'stored': stored}
        self.log.append(receipt)
        self.validate()
        return dict(receipt)

    def assign_forage(self, person_id: str) -> None:
        """C2 (protótipo): coleta no entorno, 1 comida por trabalhador.

        Limites: no máximo ceil(consumidores/2) coletores por dia e o entorno
        tem reserva própria (`pool`) que só se recompõe `regrow` por amanhecer.
        Coletar é o trabalho do dia (sem recuperação §25, sem outra tarefa).
        """
        forage = self._require_camp_prototype('forage')['forage']
        self._require_dawn_camp_worker(person_id)
        if len(forage['workers']) >= -(-len(self.meal_people()) // 2):
            raise ValueError('Limite diário de coletores atingido')
        if len(forage['workers']) >= forage['pool']:
            raise ValueError('Entorno esgotado por hoje')
        forage['workers'].append(person_id)
        if person_id in self.heroes:
            self.worked_today.append(person_id)

    def _forage_harvest(self) -> dict | None:
        forage = (self.regional_camp or {}).get('forage')
        if forage is None:
            return None
        workers = forage['workers']
        forage['workers'] = []
        gathered = min(len(workers), forage['pool'])
        forage['pool'] -= gathered
        for worker in workers:
            if worker not in self.worked_today:
                self.worked_today.append(worker)
        stored = self.deposit('food', gathered) if gathered else 0
        return {'workers': list(workers), 'gathered': gathered, 'stored': stored,
                'pool': forage['pool']}

    def _forage_regrow(self) -> None:
        forage = (self.regional_camp or {}).get('forage')
        if forage is not None:
            forage['pool'] = min(forage['max'], forage['pool'] + forage['regrow'])

    def regional_seeds_available(self) -> int:
        """Sementes não gastas na Cisterna, arquivadas na migração."""
        if (self.regional_camp or {}).get('seeds_spent'):
            return 0
        archived = (((self.cistern_record or {}).get('migration') or {})
                    .get('projection') or {}).get('garden_archived') or {}
        return int(archived.get('seeds_unspent') or 0)

    def start_regional_garden(self) -> dict:
        """D (protótipo): Horta §61 no abrigo regional com Sementes transportadas.

        Custo: 1 Sementes + 2 sucata (no lugar dos 2 Materiais, sem equivalente
        regional) + 2 trabalhos (máximo 2 por dia). Produz 4 comida por dia com
        um trabalhador designado, a partir do amanhecer seguinte à conclusão.
        """
        camp = self._require_camp_prototype('garden_build')
        if self.continuity_garden is not None or camp.get('garden_build') is not None:
            raise ValueError('O abrigo já tem Horta ou obra de Horta')
        if self.regional_seeds_available() < GARDEN_BUILD['seeds']:
            raise ValueError('Sem Sementes transportadas')
        if self.stock['scrap'] < GARDEN_BUILD['scrap']:
            raise ValueError('Sucata insuficiente para a Horta')
        if self.partial_defeat or self.expeditions:
            raise ValueError('Obra da Horta se inicia no abrigo')
        self.stock['scrap'] -= GARDEN_BUILD['scrap']
        camp['seeds_spent'] = True
        camp['garden_build'] = {'work': 0, 'workers': [], 'done': False}
        self.log.append({'day': self.day, 'action': 'start_regional_garden',
                         'paid': {'scrap': GARDEN_BUILD['scrap'],
                                  'seeds': GARDEN_BUILD['seeds']}})
        self.validate()
        return dict(camp['garden_build'])

    def work_regional_garden(self, person_id: str) -> None:
        build = self._require_camp_prototype('garden_build').get('garden_build')
        if build is None or build['done']:
            raise ValueError('Sem obra de Horta em andamento')
        if (len(build['workers']) >= 2
                or build['work'] + len(build['workers']) >= GARDEN_BUILD['work']):
            raise ValueError('Obra da Horta não aceita mais trabalho hoje')
        self._require_dawn_camp_worker(person_id)
        build['workers'].append(person_id)
        if person_id in self.heroes:
            self.worked_today.append(person_id)

    def _garden_build_work(self) -> dict | None:
        build = (self.regional_camp or {}).get('garden_build')
        if build is None or not build['workers']:
            return None
        workers = build['workers']
        build['workers'] = []
        for worker in workers:
            if worker not in self.worked_today:
                self.worked_today.append(worker)
        build['work'] += len(workers)
        build['done'] = build['work'] >= GARDEN_BUILD['work']
        if build['done']:
            # Concluída nos trabalhos: produz a partir do próximo amanhecer.
            self.continuity_garden = {'source': 'regional_build', 'active': False,
                                      'output': 4, 'worker': None}
            self.log.append({'day': self.day, 'action': 'regional_garden_done'})
        return {'workers': list(workers), 'work': build['work'], 'done': build['done']}

    def _d6(self, count: int = 1) -> list[int]:
        rng=random.Random();rng.setstate(_tuples(self.rng_state))
        rolls=[rng.randint(1,6) for _ in range(count)]
        self.rng_state=_lists(rng.getstate())
        return rolls

    def attack_with_item(self, hero_id: str, instance_id: str) -> dict:
        hero=self.heroes[hero_id]
        item=self.gear[hero_id][instance_id]
        spec=ITEMS[item['template']]
        combat=spec.get('combat')
        if (hero['actions']<1 or item['slot']!='hand' or item['durability']<1
                or not combat):
            raise ValueError('Ataque indisponível')
        rolls=self._d6(combat['dice'])
        hits=sum(roll>=combat['hit_on'] for roll in rolls)
        damage=hits*combat['damage']
        if hits:
            damage+=self.skill_bonus(hero_id,'attack')
        hero['actions']-=1
        item['durability']-=1
        return {'rolls':rolls,'hits':hits,'damage':damage,'noise':combat['noise'],
                'durability':item['durability']}

    def receive_damage(self, hero_id: str, damage: int, armor_instance: str | None = None) -> dict:
        if damage<0:
            raise ValueError('Dano negativo')
        guard_absorbed=min(damage,self.guarding.get(hero_id,0))
        self.guarding[hero_id]=self.guarding.get(hero_id,0)-guard_absorbed
        damage-=guard_absorbed
        absorbed=guard_absorbed
        if armor_instance is not None:
            item=self.gear[hero_id][armor_instance]
            spec=ITEMS[item['template']]
            if item['slot'] not in ('head','torso','legs') or item['durability']<1 or 'armor' not in spec:
                raise ValueError('Armadura indisponível')
            armor_absorbed=min(damage,spec['armor'])
            if armor_absorbed:
                item['durability']-=1
                absorbed+=armor_absorbed
                damage-=armor_absorbed
        hero=self.heroes[hero_id]
        self._set_hero_health(hero_id, hero['health']-damage)
        return {'absorbed':absorbed,'health':hero['health']}

    def deposit(self, resource: str, amount: int) -> int:
        if resource not in RESOURCES or amount < 0:
            raise ValueError('Recurso inválido')
        if resource == 'food' and amount and (self.regional_camp or {}).get('food_priority'):
            self._make_room_for_food(amount, 'storage_priority')
        accepted = min(amount, self.free_space(resource))
        self.stock[resource] += accepted
        return accepted

    def recruit(self, npc_id: str) -> bool:
        if (self.cistern_record or {}).get('migration', {}).get('receipt'):
            raise ValueError('contato físico tático obrigatório para recrutar na campanha contínua')
        if (npc_id not in NPCS or npc_id in self.npcs or self.residents >= self.beds
                or NPCS[npc_id].get('source_hero_id') in self.heroes
                or self.stock['food'] < self.residents + 1
                or self.stock['water'] < self.residents + 1):
            return False
        self.npcs[npc_id] = {'level':1,'job':None,'health':3,'wounds':0,
                             'hungry':False,'thirsty':False,'streak':0,
                             'location':'camp'}
        return True

    def assign(self, npc_id: str, job: str) -> None:
        if (npc_id not in self.npcs or self.npcs[npc_id]['location']!='camp'
                or job != NPCS[npc_id]['job'] or npc_id in self.departed_today):
            raise ValueError('Trabalho incompatível')
        person = self.npcs[npc_id]
        if (person.get('hungry') or person.get('thirsty')
                or person.get('fatigue', 0) >= 3 or person.get('health', 3) <= 0):
            raise ValueError('Morador sem condição física para trabalhar')
        self.npcs[npc_id]['job'] = job

    def level_npc(self, npc_id: str) -> bool:
        if (npc_id not in self.npcs or self.npcs[npc_id]['location']!='camp'
                or self.npcs[npc_id]['level'] >= 3):
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
            self._require_working_hero(hero_id)
            units += self.skill_bonus(hero_id,'build')
            self.worked_today.append(hero_id)
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

    def repair_structure(self, kind: str, hero_id: str | None = None) -> bool:
        if hero_id is not None:
            self._require_working_hero(hero_id)
        if kind not in self.structures or self.stock['scrap'] < 1 or self.structures[kind]['health'] >= STRUCTURES[kind]['max_health']:
            return False
        self.stock['scrap'] -= 1
        bonus=self.skill_bonus(hero_id,'repair') if hero_id is not None else 0
        self.structures[kind]['health']=min(STRUCTURES[kind]['max_health'],
                                           self.structures[kind]['health']+1+bonus)
        if hero_id is not None:
            self.worked_today.append(hero_id)
        return True

    def _require_working_hero(self, hero_id: str) -> None:
        if hero_id not in self.heroes or self.heroes[hero_id]['location']!='camp':
            raise ValueError('Herói fora do abrigo')
        if self.heroes[hero_id]['health']<=0 or self.heroes[hero_id].get('fatigue',0)>=3:
            raise ValueError('Herói incapacitado/fadigado não pode trabalhar')
        if self.heroes[hero_id].get('hungry') or self.heroes[hero_id].get('thirsty'):
            raise ValueError('Herói com Fome ou Sede não pode trabalhar')
        if hero_id in self.departed_today:
            raise ValueError('Expedição no mesmo dia impede trabalho')
        if hero_id in self.worked_today:
            raise ValueError('Herói já realizou trabalho no mesmo dia')

    def use_structure(self, kind: str, hero_id: str | None = None) -> bool:
        if kind not in self.structures or self.structures[kind]['health'] == 0:
            return False
        spec=STRUCTURES[kind].get('action')
        if not spec or self.used_structure_actions.get(kind) == self.day:
            return False
        if any(self.stock[r] < n for r,n in spec['cost'].items()):
            return False
        if hero_id is not None:
            self._require_working_hero(hero_id)
        if spec['kind']=='heal':
            if hero_id not in self.heroes or self.heroes[hero_id]['health'] >= 3:
                return False
            self._set_hero_health(hero_id, min(3,self.heroes[hero_id]['health']
                                               +spec['health']
                                               +self.skill_bonus(hero_id,'medicine')))
        else:
            output=dict(spec['output'])
            if hero_id is not None:
                operation={'pump':'water','craft':'craft'}[spec['kind']]
                first=next(iter(output))
                output[first]+=self.skill_bonus(hero_id,operation)
            if sum(self.stock.values())-sum(spec['cost'].values())+sum(output.values())>self.storage:
                return False
            for resource,amount in output.items():
                self.stock[resource]+=amount
        for resource,amount in spec['cost'].items():
            self.stock[resource]-=amount
        self.used_structure_actions[kind]=self.day
        if hero_id is not None:
            self.worked_today.append(hero_id)
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
                     if state['job'] == 'guard' and state['location']=='camp'
                     and NPCS[npc_id]['output'] == 'defense')
        stopped = min(threat,guards,self.stock['ammo'])
        self.stock['ammo'] -= stopped
        return threat-stopped

    def search(self, expedition_id: str, hero_id: str | None = None) -> dict[str,int]:
        if expedition_id not in self.expeditions:
            raise ValueError('Expedição inexistente')
        exp = self.expeditions[expedition_id]
        if hero_id is not None and hero_id not in exp.heroes:
            raise ValueError('Herói fora da expedição')
        continuous=self.continuous_campaign
        if continuous and (hero_id is None or expedition_id not in self.encounters):
            raise ValueError('Campanha contínua exige encontro tático para a busca')
        if exp.remaining != 0 or exp.returning:
            raise ValueError('Equipe não está explorando o local')
        encounter=self.encounters.get(expedition_id)
        if hero_id is not None:
            actor=self.heroes[hero_id]
            if actor['health']<1 or actor['actions']<1:
                raise ValueError('Herói sem ação disponível para buscar')
            if encounter and encounter['heroes'].get(hero_id) not in encounter['search_zones']:
                raise ValueError('Herói fora da área de busca')
        elif encounter:
            raise ValueError('Busca tática exige identificar o herói')
        elif not continuous:
            # The pre-tactical one-day simulator keeps this abstract call for
            # regression compatibility; campaign replays use the action API.
            pass
        location_id = exp.destination
        if location_id == 'EXP-LOC-07':
            raise ValueError('Posto exige retirada tática por PA')
        if self.searches[location_id] <= 0:
            return {}
        maximum = VEHICLES[exp.vehicle_id]['cargo_capacity'] if exp.vehicle_id else 6 * len(exp.heroes)
        used_capacity = sum(exp.cargo.values()) + len(exp.special_cargo)
        if used_capacity > maximum:
            raise ValueError('Carga excede capacidade')
        capacity = maximum - used_capacity
        if capacity <= 0:
            return {}
        self.searches[location_id] -= 1
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'location':location_id,'action':'search','hero':hero_id})
        loot = LOCATIONS[location_id]['loot']
        found = {}
        scouts=sum(self.npcs[n]['level'] for n in exp.crew
                   if self.npcs[n]['job']=='scouting')
        scouts+=self.skill_bonus(hero_id,'search') if hero_id else 0
        for resource,amount in loot.items():
            amount += scouts
            found[resource] = min(amount,capacity)
            exp.cargo[resource] = exp.cargo.get(resource,0) + found[resource]
            capacity -= found[resource]
            scouts=0
        if hero_id is not None:
            self.heroes[hero_id]['actions']-=1
        return found

    def recover_vehicle(self, vehicle_id: str, expedition_id: str) -> bool:
        if vehicle_id not in VEHICLES or vehicle_id in self.vehicles or expedition_id not in self.expeditions:
            return False
        # EXP-VEI-02 is the canonical maintenance van. It is recovered only by
        # inspection, a carried Workshop battery, and the Posto repair action.
        if vehicle_id == 'EXP-VEI-02':
            return False
        exp=self.expeditions[expedition_id]
        spec=VEHICLES[vehicle_id]
        fuel=DATA['rules']['travel_segments'][exp.distance]*spec['fuel_per_segment']
        if (exp.destination != 'EXP-LOC-03' or exp.remaining != 0 or exp.returning
                or len(exp.heroes)+len(exp.crew)>spec['seats']
                or sum(exp.cargo.values())>spec['cargo_capacity']
                or self.stock['fuel']<fuel):
            return False
        self.stock['fuel']-=fuel
        self.vehicles[vehicle_id]={'location':expedition_id,'health':spec['health']}
        exp.vehicle_id=vehicle_id
        return True

    def open_expedition(self, expedition_id: str, hero_ids: list[str], location_id: str,
                        vehicle_id: str | None = None, npc_ids: list[str] | None = None,
                        special_items: list[str] | None = None) -> None:
        npc_ids = npc_ids or []
        special_items = special_items or []
        if self.continuous_campaign and self.daily_expeditions>=1:
            raise ValueError('A regra canônica permite uma expedição por dia')
        if location_id=='EXP-LOC-06' and (not self.cistern_verified or not vehicle_id or not all(
                self.flags.get(key) for key in ('radio_code','access_card','military_access'))):
            raise ValueError('Instalação exige código, cartão, missão e veículo')
        if (expedition_id in self.expeditions or not hero_ids
                or len(set(hero_ids)) != len(hero_ids) or location_id not in LOCATIONS
                or len(set(special_items)) != len(special_items)
                or any(item not in ('battery', 'access_card') or item not in self.special_stock
                       for item in special_items)
                or len(special_items) > 6 * len(hero_ids)):
            raise ValueError('Expedição inválida')
        if any(h not in self.heroes or self.heroes[h]['location'] != 'camp' for h in hero_ids):
            raise ValueError('Herói indisponível')
        if set(hero_ids) & community_rules.away(self):
            raise ValueError('Herói em viagem automática não entra na expedição')
        if any(h in self.worked_today for h in hero_ids):
            raise ValueError('Herói que trabalhou não pode sair em expedição no mesmo dia')
        if any(self.heroes[h].get('fatigue',0)>=3 for h in hero_ids):
            raise ValueError('Fadiga 3 impede expedição neste amanhecer')
        if len(set(npc_ids))!=len(npc_ids) or any(n not in self.npcs or self.npcs[n]['location']!='camp' for n in npc_ids):
            raise ValueError('NPC indisponível')
        distance = LOCATIONS[location_id]['distance']
        segments = DATA['rules']['travel_segments'][distance]
        segments=max(1,segments-max(self.skill_bonus(h,'travel') for h in hero_ids))
        fuel=0
        if vehicle_id is not None:
            driver=any(self.npcs[n]['job']=='driving' for n in npc_ids)
            if driver:
                segments=max(1,segments-1)
            if (vehicle_id not in self.vehicles or self.vehicles[vehicle_id]['location'] != 'camp'
                    or self.vehicles[vehicle_id]['health'] == 0
                    or len(hero_ids)+len(npc_ids) > VEHICLES[vehicle_id]['seats']):
                raise ValueError('Veículo indisponível')
            fuel = 2 * segments * VEHICLES[vehicle_id]['fuel_per_segment']
            if self.stock['fuel'] < fuel:
                raise ValueError('Combustível insuficiente para ida e volta')
        # Compute the shared-clock reserve from the final segment count,
        # including legal travel-skill and driver reductions, before any spend.
        if (self.continuous_campaign
                and self.regional_clock + segments + 1 + segments > 10):
            raise ValueError('Relógio regional sem reserva para ida, 1 rodada local e retorno')
        if vehicle_id is not None:
            self.stock['fuel'] -= fuel
            self.vehicles[vehicle_id]['location'] = expedition_id
        self.expeditions[expedition_id] = Expedition(expedition_id,hero_ids,location_id,distance,segments,
                                                    vehicle_id=vehicle_id,crew=npc_ids,
                                                    segment_cost=segments,
                                                    special_cargo=list(special_items))
        for item in special_items:
            self.special_stock.remove(item)
        for h in hero_ids:
            self.heroes[h]['location'] = expedition_id
            if h not in self.departed_today:
                self.departed_today.append(h)
        for n in npc_ids:
            self.npcs[n]['location'] = expedition_id
            if n not in self.departed_today:
                self.departed_today.append(n)
        if self.continuous_campaign:
            self.daily_expeditions+=1
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'open_expedition','destination':location_id,
                         'distance':distance,'segments':segments,'vehicle':vehicle_id,
                         'special_items':list(special_items)})

    def advance_expedition(self, expedition_id: str) -> str:
        exp = self.expeditions[expedition_id]
        if self.regional_travel_cards:
            if exp.pending_travel is not None:
                raise ValueError('Resolva a carta de Viagem pendente antes de seguir')
            if not exp.leg_paid:
                self.advance_regional_segment(expedition_id,'travel')
                exp.leg_paid=True
                exp.night_extra_due=self.continuous_campaign and self.regional_clock>=9
                self._reveal_regional_travel(exp, extra=False)
                if exp.pending_travel is not None:
                    return 'travel_pending'
            if exp.night_extra_due:
                exp.night_extra_due=False
                self._reveal_regional_travel(exp, extra=True)
                if exp.pending_travel is not None:
                    return 'travel_pending'
            exp.leg_paid=False
        else:
            self.advance_regional_segment(expedition_id,'travel')
        exp.remaining -= 1
        if exp.remaining > 0:
            return 'travel'
        if not exp.returning:
            exp.remaining = 0
            return 'arrived'
        delivered = {resource:self.deposit(resource,amount) for resource,amount in exp.cargo.items()}
        self.special_stock.extend(exp.special_cargo)
        left_behind = {resource:amount-delivered[resource] for resource,amount in exp.cargo.items()
                       if amount > delivered[resource]}
        self.log.append({'day':self.day,'expedition':expedition_id,'delivered':delivered,
                         'left_behind':left_behind})
        for h in exp.heroes:
            self.heroes[h]['location'] = 'camp'
            self.heroes[h]['combat_xp'] = 0
        for n in exp.crew:
            self.npcs[n]['location'] = 'camp'
        if exp.vehicle_id:
            self.vehicles[exp.vehicle_id]['location']='camp'
        del self.expeditions[expedition_id]
        return 'returned'

    # Escolhas disponíveis sem provisões levadas: o motor regional ainda não
    # tem ação de levar comida/água/Material na viagem.
    REGIONAL_TRAVEL_CHOICES = {'ZC-VIA-0002': ('fatigue',), 'ZC-VIA-0004': ('pressure',),
                               'ZC-VIA-0006': ('decline',), 'ZC-VIA-0009': ('decline',)}

    def _reveal_regional_travel(self, exp: Expedition, extra: bool) -> None:
        """Revela a carta do trecho pago (ou a extra noturna, sem segmento)."""
        direction='return' if exp.returning else 'outbound'
        if direction=='return' and not extra and exp.skip_return_card>0:
            exp.skip_return_card-=1
            exp.travel_events.append({'direction':direction,'card_id':None,
                                      'skipped':True,'segment':self.regional_clock})
            return
        deck=TravelDeck02.from_snapshot(self.regional_travel_deck)
        card_id=deck.draw()
        self.regional_travel_deck=deck.snapshot()
        event={'direction':direction,'card_id':card_id,'extra':extra,
               'segment':self.regional_clock}
        exp.travel_events.append(event)
        if card_id=='ZC-VIA-0005':
            event['ambush']=True
            exp.pending_travel=event
        elif card_id in CHOICES:
            exp.pending_travel=event
        else:
            event['effect']=self._apply_regional_travel(exp,card_id,direction,None)
        self.log.append({'day':self.day,'expedition':exp.id,'action':'regional_travel_card',
                         **deepcopy(event)})

    def _apply_regional_travel(self, exp: Expedition, card_id: str, direction: str,
                               choice: str | None) -> dict:
        effect=deepcopy(CHOICES[card_id][choice] if choice is not None
                        else AUTO_EFFECTS.get(card_id, {}))
        if card_id=='ZC-VIA-0010':
            # Ida: nada levado, nada perdido (decisão aprovada). Volta: Material
            # sem equivalente regional fica arquivado.
            effect=({'material_gain':1} if direction=='return'
                    else {'material_drop':0,'no_material_carried':1})
        applied={}
        if effect.get('fatigue'):
            for person_id in [*exp.heroes,*exp.crew]:
                person=self.heroes.get(person_id) or self.npcs.get(person_id)
                person['fatigue']=min(3,person.get('fatigue',0)+effect['fatigue'])
            applied['fatigue']=list([*exp.heroes,*exp.crew])
        if effect.get('pressure'):
            self.regional_travel_archive['pressure']+=effect['pressure']
            applied['pressure_archived']=effect['pressure']
        if effect.get('material_gain'):
            self.regional_travel_archive['materials']+=effect['material_gain']
            applied['materials_archived']=effect['material_gain']
        if effect.get('skip_return_card'):
            exp.skip_return_card+=effect['skip_return_card']
            applied['skip_return_card']=effect['skip_return_card']
        if effect.get('route_known'):
            exp.route_known=True;applied['route_known']=True
        if effect.get('bridge_known'):
            exp.bridge_known=True;applied['bridge_known']=True
        if effect.get('no_material_carried'):
            applied['no_material_carried']=True
        return applied

    def start_regional_ambush(self, expedition_id: str) -> Ambush02:
        """Abre a Emboscada pendente no M1 da regra 0.2 (§30) para o mundo regional.

        Só armas do gabarito regional cujo nome é arma 0.2 entram; nenhuma
        Munição é levada (o motor regional não leva carga na viagem). Ferimentos,
        fadiga, Fome/Sede, relógio e Horda vêm do estado regional.
        """
        exp=self.expeditions[expedition_id]
        event=exp.pending_travel
        if (event is None or not event.get('ambush') or 'ambush_state' in event
                or self.regional_horde_deck is None):
            raise ValueError('Nenhuma Emboscada regional para abrir')
        team=list(exp.heroes)
        equipment={hero:[ITEMS[item['template']]['name']
                         for item in getattr(self,'gear',{}).get(hero,{}).values()
                         if ITEMS.get(item['template'],{}).get('name') in WEAPONS02][:4]
                   for hero in team}
        ambush=Ambush02.start(
            team,self.regional_clock,equipment=equipment,ammo=0,
            horde_deck=self.regional_horde_deck,
            fatigue={hero:self.heroes[hero].get('fatigue',0) for hero in team},
            ap_penalty={hero:min(2,int(self.heroes[hero].get('hungry',False))
                                 +int(self.heroes[hero].get('thirsty',False)))
                        for hero in team},
            allow_emergency_at_limit=True)
        ambush.wounds={hero:self.heroes[hero].get('wounds',0) for hero in team}
        event['ambush_state']=ambush.snapshot()
        event['ambush_start_clock']=self.regional_clock
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'regional_ambush_start','clock':self.regional_clock,
                         'equipment':deepcopy(equipment)})
        return ambush

    def regional_ambush(self, expedition_id: str) -> Ambush02:
        """Retoma a Emboscada salva (por exemplo, após load)."""
        event=self.expeditions[expedition_id].pending_travel or {}
        if 'ambush_state' not in event:
            raise ValueError('Emboscada regional não iniciada')
        return Ambush02.from_snapshot(event['ambush_state'])

    def store_regional_ambush(self, expedition_id: str, ambush: Ambush02) -> None:
        event=self.expeditions[expedition_id].pending_travel or {}
        if 'ambush_state' not in event or ambush.team!=event['ambush_state']['team']:
            raise ValueError('Emboscada regional divergente')
        event['ambush_state']=ambush.snapshot()

    def regional_ambush_attack(self, expedition_id: str, ambush: Ambush02, hero: str,
                               enemy_id: int, weapon: str) -> bool:
        """Ataque na Emboscada com d6 do RNG persistido do mundo (não do jogador)."""
        event=self.expeditions[expedition_id].pending_travel or {}
        if 'ambush_state' not in event or ambush.team!=event['ambush_state']['team']:
            raise ValueError('Emboscada regional divergente')
        rng=random.Random();rng.setstate(_tuples(self.rng_state))
        die=rng.randint(1,6)
        self.rng_state=_lists(rng.getstate())
        hit=ambush.attack(hero,enemy_id,weapon,die)
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'regional_ambush_attack','hero':hero,
                         'enemy':enemy_id,'weapon':weapon,'die':die,'hit':hit})
        return hit

    def finish_regional_ambush(self, expedition_id: str, ambush: Ambush02) -> str:
        """Sincroniza o resultado: relógio real, ferimentos, fadiga e Horda.

        Retorna 'continue' (viagem segue no mesmo trecho) ou 'emergency'
        (retorno automático de estrada pela §34).
        """
        exp=self.expeditions[expedition_id]
        event=exp.pending_travel or {}
        start_clock=event.get('ambush_start_clock')
        if ('ambush_state' not in event or not ambush.returned
                or ambush.team!=event['ambush_state']['team']
                or not start_clock<=ambush.clock<=10
                or (not ambush.failed and ambush.round_no<1)):
            raise ValueError('Emboscada regional não concluída legalmente')
        _HordeDeck02.from_snapshot(ambush.horde_deck)
        if ambush.failed and (exp.special_cargo or exp.vehicle_id):
            raise NotImplementedError(
                'Emergência de estrada com carga única ou veículo ainda não modelada')
        self.regional_clock=ambush.clock
        self.regional_horde_deck=deepcopy(ambush.horde_deck)
        for hero in ambush.team:
            state=self.heroes[hero]
            state['wounds']=ambush.wounds[hero]
            state['health']=3-ambush.wounds[hero]
            state['fatigue']=ambush.fatigue[hero]
        night_rounds=sum(1 for clock in range(start_clock+1,ambush.clock+1) if clock>=9)
        for npc_id in exp.crew:
            npc=self.npcs[npc_id]
            npc['fatigue']=min(3,npc.get('fatigue',0)+night_rounds)
        event.pop('ambush_state')
        event['ambush_result']={'rounds':ambush.round_no,'clock':ambush.clock,
                                'emergency':ambush.failed,
                                'wounds':deepcopy(ambush.wounds)}
        exp.pending_travel=None
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'regional_ambush_finish',**deepcopy(event['ambush_result'])})
        if not ambush.failed:
            return 'continue'
        self._road_emergency(exp)
        return 'emergency'

    def _road_emergency(self, exp: Expedition) -> None:
        """§34 na estrada: perde a carga obtida e todos voltam ao abrigo."""
        for npc_id in exp.crew:
            npc=self.npcs[npc_id]
            npc['wounds']=min(3,npc.get('wounds',0)+1)
            if 'health' in npc:
                npc['health']=max(0,3-npc['wounds'])
            npc['fatigue']=3
            npc['location']='camp'
        for hero in exp.heroes:
            self.heroes[hero]['location']='camp'
            self.heroes[hero]['combat_xp']=0
        lost=deepcopy(exp.cargo)
        self.log.append({'day':self.day,'expedition':exp.id,'action':'road_emergency',
                         'lost_cargo':lost})
        del self.expeditions[exp.id]

    def resolve_regional_travel(self, expedition_id: str, choice: str) -> dict:
        """Resolve a carta pendente por decisão pública registrada."""
        exp=self.expeditions[expedition_id]
        event=exp.pending_travel
        if event is None:
            raise ValueError('Nenhuma carta de Viagem pendente')
        if event.get('ambush'):
            raise ValueError('Emboscada se resolve com start/finish_regional_ambush')
        allowed=self.REGIONAL_TRAVEL_CHOICES[event['card_id']]
        if choice not in allowed:
            raise ValueError(f'Escolha indisponível sem provisões levadas: {allowed}')
        event['choice']=choice
        event['effect']=self._apply_regional_travel(exp,event['card_id'],
                                                    event['direction'],choice)
        exp.pending_travel=None
        self.log.append({'day':self.day,'expedition':expedition_id,
                         'action':'regional_travel_choice',**deepcopy(event)})
        return deepcopy(event)

    def begin_return(self, expedition_id: str, vehicle_id: str | None = None) -> None:
        exp = self.expeditions[expedition_id]
        if exp.remaining != 0 or exp.returning or expedition_id in self.encounters:
            raise ValueError('Retorno indisponível')
        if (self.continuous_campaign
                and self.regional_clock + exp.segment_cost > 10):
            raise ValueError('Retorno regional excede o relógio; emergência ainda não integrada')
        if vehicle_id is not None:
            if vehicle_id not in VEHICLES or vehicle_id not in self.vehicles:
                raise ValueError('Veículo indisponível')
            vehicle = self.vehicles[vehicle_id]
            if (exp.destination != 'EXP-LOC-07' or vehicle_id != 'EXP-VEI-02'
                    or vehicle['location'] != exp.destination or vehicle['health'] < 1
                    or self.site_states.get(exp.destination, {}).get('van_state') != 'operational'
                    or len(exp.heroes) + len(exp.crew) > VEHICLES[vehicle_id]['seats']):
                raise ValueError('Van operacional indisponível no Posto')
            fuel_cost = exp.segment_cost * VEHICLES[vehicle_id]['fuel_per_segment']
            if exp.cargo.get('fuel', 0) < fuel_cost:
                raise ValueError('Combustível físico insuficiente para retorno da van')
            exp.cargo['fuel'] -= fuel_cost
            if exp.cargo['fuel'] == 0:
                del exp.cargo['fuel']
            exp.vehicle_id = vehicle_id
            vehicle['location'] = expedition_id
        exp.returning = True
        exp.remaining = exp.segment_cost

    def emergency_return(self, expedition_id: str, reason: str) -> dict:
        """Resolve the canonical failed/abandoned expedition without free loot."""
        if (not self.continuous_campaign or expedition_id not in self.expeditions
                or expedition_id not in self.encounters or not reason.strip()):
            raise ValueError('Retirada de emergência indisponível')
        exp=self.expeditions[expedition_id]
        encounter=self.encounters[expedition_id]
        destination=exp.destination
        # Preserve the map, objective state and persistent enemies for a later visit.
        site=deepcopy({key:encounter[key] for key in
                       ('map','enemies','next_enemy','doors','announced','round',
                        'pressure','initial_spawned','van_state','fuel_cards_taken',
                        'fuel_cache_collected','discovered_npcs')
                       if key in encounter})
        stranded=sorted(encounter.get('npc_followers',{}))
        if stranded:
            site['stranded_npcs']=sorted(set(site.get('stranded_npcs',[]))|set(stranded))
        self.site_states[destination]=site

        opening=next((entry for entry in reversed(self.log)
                      if entry.get('expedition')==expedition_id
                      and entry.get('action')=='open_expedition'),{})
        carried=list(opening.get('special_items',[]))
        retained=[]
        lost_special=[]
        remaining=list(exp.special_cargo)
        for item in carried:
            if item in remaining:
                remaining.remove(item)
                retained.append(item)
        self.special_stock.extend(retained)
        lost_special.extend(remaining)
        if lost_special:
            site['lost_special_items']=sorted(set(site.get('lost_special_items',[]))
                                               |set(lost_special))
            for item in lost_special:
                items=self.unique_items_at_sites.setdefault(destination,[])
                if item not in items:
                    items.append(item)
                if item=='access_card':
                    self.flags['access_card']=False
                    self.special_stock=[stored for stored in self.special_stock
                                        if stored!='access_card']
                if item=='transmitter':
                    self.flags['transmitter']=False
        if destination=='EXP-LOC-06':
            self.flags['military_access']=False

        lost_cargo=dict(exp.cargo)
        followers=set(stranded)
        for hero_id in exp.heroes:
            state=self.heroes[hero_id]
            self._set_hero_health(hero_id, state['health']-1)
            state['fatigue']=3
            state['location']='camp'
        for npc_id in exp.crew:
            state=self.npcs[npc_id]
            state['location']=destination if npc_id in followers else 'camp'
        if exp.vehicle_id:
            vehicle=self.vehicles[exp.vehicle_id]
            vehicle['location']=destination
            vehicle['health']=0
            site['van_state']='damaged'

        del self.encounters[expedition_id]
        del self.expeditions[expedition_id]
        receipt={'day':self.day,'expedition':expedition_id,
                 'action':'emergency_return','destination':destination,
                 'reason':reason,'status':'failed','lost_cargo':lost_cargo,
                 'lost_special_items':lost_special,'retained_special_items':retained,
                 'stranded_npcs':sorted(followers),'returned_heroes':list(exp.heroes),
                 'vehicle_damaged':exp.vehicle_id}
        self.log.append(receipt)
        self.validate()
        return deepcopy(receipt)

    def end_day(self, meal_plan: dict | None = None) -> dict:
        """Close the day, requiring explicit allocation when food/water is scarce.

        The choice is intentionally not automated: this is a player decision in
        RULES.md. A rejected allocation restores the complete pre-call state.
        """
        before = deepcopy(self.__dict__)
        try:
            return self._end_day(meal_plan)
        except Exception:
            self.__dict__.clear()
            self.__dict__.update(before)
            raise

    def _end_day(self, meal_plan: dict | None = None) -> dict:
        if self.partial_defeat:
            raise ValueError('Derrota parcial: resolva a Evacuação antes de retomar a campanha')
        if self.continuous_campaign and (self.expeditions or self.encounters):
            raise ValueError('Não encerre o dia com expedição regional em andamento')
        if self.final_defense is not None and self.final_defense['status']=='active':
            raise ValueError('Resolva a defesa final antes do próximo dia')
        if (self.garden_worker in self.heroes and 'garden' in self.structures
                and self.structures['garden']['health'] > 0
                and self.heroes[self.garden_worker]['location']=='camp'
                and not self.heroes[self.garden_worker].get('hungry')
                and not self.heroes[self.garden_worker].get('thirsty')
                and self.heroes[self.garden_worker].get('fatigue', 0)<3
                and self.garden_worker not in self.worked_today):
            self.worked_today.append(self.garden_worker)
        for npc_id,person in self.npcs.items():
            if (person.get('job') is not None and person.get('location')=='camp'
                    and not person.get('hungry') and not person.get('thirsty')
                    and person.get('fatigue', 0)<3 and person.get('health', 3)>0
                    and npc_id not in self.departed_today
                    and npc_id not in self.worked_today):
                self.worked_today.append(npc_id)
        self.day += 1
        if self.continuous_campaign:
            self.regional_clock=0
            self.daily_expeditions=0
        produced = dict.fromkeys(RESOURCES,0)
        # Especialistas geram apenas suas tarefas previstas; saídas abstratas não criam recurso.
        for npc_id,state in self.npcs.items():
            if (state['job'] is None or state['location']!='camp'
                    or state.get('hungry') or state.get('thirsty')
                    or state.get('fatigue', 0)>=3 or state.get('health', 3)<=0
                    or npc_id in self.departed_today):
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
                injured = next((hero for hero in self.heroes.values()
                                if hero['location']=='camp' and hero['health'] < 3),None)
                if injured:
                    self.stock['medicine'] -= 1
                    hero_id = next(identifier for identifier, state in self.heroes.items()
                                   if state is injured)
                    self._set_hero_health(hero_id, injured['health']+1)
        if 'garden' in self.structures and self.structures['garden']['health'] > 0:
            garden = self.structures['garden']
            garden['age'] += 1
            if garden['age'] >= DATA['rules']['garden_growth_days']:
                bonus=(self.skill_bonus(self.garden_worker,'food') if self.garden_worker
                       and self.heroes[self.garden_worker]['location']=='camp'
                       and not self.heroes[self.garden_worker].get('hungry')
                       and not self.heroes[self.garden_worker].get('thirsty')
                       and self.heroes[self.garden_worker].get('fatigue', 0)<3 else 0)
                harvest = (community_rules.RULES['garden_food_per_harvest']
                           if self.community is not None
                           else DATA['rules']['garden_food_per_harvest'])
                produced['food'] += self.deposit('food',harvest+bonus)
        garden_food = self._continuity_garden_harvest()
        forage = self._forage_harvest()
        garden_build = self._garden_build_work()
        community_work = community_rules.day_work(self)
        people = self.meal_people()
        identifiers = set(people)
        need = len(people)
        shortages = {resource: max(0, need-self.stock[resource])
                     for resource in ('food','water')}
        if meal_plan is None:
            if any(shortages.values()):
                raise ValueError('Escassez exige distribuição explícita de comida e água')
            priorities = {resource: sorted(identifiers) for resource in ('food','water')}
        else:
            if not isinstance(meal_plan, dict) or set(meal_plan) != {
                    'food_priority','water_priority'}:
                raise ValueError('Plano de refeição deve indicar prioridades de comida e água')
            priorities = {}
            for resource in ('food','water'):
                selected = meal_plan[f'{resource}_priority']
                if (not isinstance(selected, (list, tuple))
                        or len(selected) != len(set(selected))
                        or set(selected) != identifiers):
                    raise ValueError(f'Prioridade inválida de {resource}: indique cada consumidor uma vez')
                priorities[resource] = list(selected)
        allocations = {
            resource: set(priorities[resource][:min(need, self.stock[resource])])
            for resource in ('food','water')
        }
        missing = {}
        for resource in ('food','water'):
            missing[resource] = need-len(allocations[resource])
            self.stock[resource] -= len(allocations[resource])
        for identifier, person in people.items():
            kind = person.get('kind', 'hero' if identifier in self.heroes else 'adult')
            person['hungry'] = identifier not in allocations['food']
            person['thirsty'] = identifier not in allocations['water']
            deprived = person['hungry'] or person['thirsty']
            person['streak'] = person.get('streak', 0)+1 if deprived else 0
            if kind == 'dog':
                person['alert'] = not deprived
            elif person['streak'] >= 2:
                if identifier in self.heroes:
                    self._set_hero_health(identifier, person['health']-1)
                elif 'health' in person:
                    person['health'] = max(0, person['health']-1)
                    person['wounds'] = 3-person['health']
                else:
                    person['wounds'] = min(3, person.get('wounds', 0)+1)
            if identifier in self.heroes and isinstance(person.get('continuity_state'), dict):
                source = person['continuity_state']
                for key in ('hungry','thirsty','streak','wounds','fatigue'):
                    if key in person:
                        source[key] = person[key]
                source['health'] = person['health']
        community_care = community_rules.after_meal(self, people)
        human_consumers = [person for identifier,person in people.items()
                           if person.get('kind', 'hero' if identifier in self.heroes else 'adult') != 'dog']
        collapse_threshold = (len(human_consumers)+3)//4
        deprived_humans = sum(person.get('streak',0)>=3 for person in human_consumers)
        if deprived_humans >= collapse_threshold:
            self.shelter_health = 0
            self.partial_defeat = True
        if self.shelter_health == 0 or self.shelter_morale == 0:
            self.partial_defeat = True
        for loc_id,loc in LOCATIONS.items():
            if loc['renewal'] == 'natural' and self.searches[loc_id] < loc['searches']:
                self.searches[loc_id] += 1
        for hero in self.heroes.values():
            if hero['location']=='camp':
                hero['combat_xp'] = 0
        # Recovery is individual: a community-wide shortage does not penalize
        # someone who personally received both portions, nor does it deny that
        # person's printed overnight recovery.
        # Comunidade: abrigo lotado (mais moradores que camas) não recupera Vida.
        crowded = community_rules.crowded(self)
        for identifier, person in people.items():
            fully_supplied = not person['hungry'] and not person['thirsty']
            if not fully_supplied or person.get('location', 'camp') != 'camp':
                continue
            if 'fatigue' in person:
                person['fatigue'] = max(0, person['fatigue']-1)
            if crowded:
                pass
            elif (identifier not in self.worked_today
                    and identifier not in self.departed_today
                    and 'health' in person):
                person['health'] = min(3, person['health']+1)
                person['wounds'] = 3-person['health']
                if identifier in self.heroes:
                    self._set_hero_health(identifier, person['health'])
            elif (identifier not in self.worked_today
                  and identifier not in self.departed_today
                  and 'wounds' in person):
                # Migrated civilians retain the 0.2 injury track without an
                # experimental HP field; §25 still gives them normal recovery.
                person['wounds'] = max(0, person['wounds']-1)
            if identifier in self.heroes and isinstance(person.get('continuity_state'), dict):
                source = person['continuity_state']
                for key in ('health','wounds','fatigue'):
                    if key in person:
                        source[key] = person[key]
        self.worked_today=[]
        self.departed_today=[]
        filter_water = self._continuity_filter_dawn()
        self._forage_regrow()
        if (self.continuity_garden or {}).get('source') == 'regional_build':
            self.continuity_garden['active'] = True
        guard = community_rules.guard_roll(self)
        crisis = self._roll_crisis(blocked=bool(guard and guard['prevents']))
        community_dawn = community_rules.dawn(self)
        result = {'day':self.day,'produced':produced,'missing':missing,
                  'unfed': {resource: sorted(identifiers-allocations[resource])
                            for resource in ('food','water')},
                  'shelter_health':self.shelter_health,
                  'shelter_morale':self.shelter_morale,
                  'partial_defeat':self.partial_defeat,
                  'stock':dict(self.stock),'crisis':crisis}
        if filter_water is not None:
            result['filter_water'] = filter_water
        if garden_food is not None:
            result['garden_food'] = garden_food
        if forage is not None:
            result['forage'] = forage
        if garden_build is not None:
            result['garden_build'] = garden_build
        if self.community is not None:
            result['community'] = {key: value for key, value in (
                ('work', community_work), ('care', community_care), ('guard', guard),
                ('dawn', community_dawn), ('crowded', crowded)) if value}
        self.log.append(result)
        self.validate()
        return result

    def _continuity_filter_dawn(self) -> dict | None:
        """Amanhecer: o filtro funcional do mesmo abrigo produz sua água.

        Depois da refeição (não alimenta a noite que terminou). Respeita o
        depósito: o que não cabe não é criado. Sem produção após Colapso, pois
        o abrigo deixa de ser o mesmo até a Evacuação.
        """
        source = self.continuity_filter
        if (not self.regional_filter_production or not self.continuous_campaign
                or source is None or not source['active']):
            return None
        if self.partial_defeat:
            return {'produced': 0, 'not_stored': 0, 'reason': 'partial_defeat'}
        produced = self.deposit('water', source['output'])
        return {'produced': produced, 'not_stored': source['output'] - produced}

    def _roll_crisis(self, blocked: bool = False) -> str | None:
        rng = random.Random()
        rng.setstate(_tuples(self.rng_state))
        trigger = rng.randrange(DATA['rules']['crisis_chance_denominator']) == 0
        eligible = [c for c in CRISES.values() if c['target'] in self.structures
                    and c['id'] not in self.active_crises
                    and self.day-self.crises_last_day.get(c['id'],-999) > c['cooldown_days']]
        chosen = rng.choice(eligible) if trigger and eligible else None
        self.rng_state = _lists(rng.getstate())
        if chosen and blocked:
            # Comunidade: a vigia percebeu a ameaça a tempo.
            self.log.append({'day': self.day, 'action': 'crisis_prevented',
                             'crisis': chosen['id']})
            return None
        if chosen:
            self.crises_last_day[chosen['id']] = self.day
            self.active_crises.append(chosen['id'])
            effect=chosen['effect']
            self.damage_structure(chosen['target'],effect['damage'])
            for resource,amount in effect['loss'].items():
                self.stock[resource]=max(0,self.stock[resource]-amount)
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
        payload['schema'] = 2
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    @classmethod
    def load(cls, path: Path) -> 'World':
        payload = json.loads(path.read_text(encoding='utf-8'))
        schema = payload.pop('schema',None)
        if schema not in (1, 2):
            raise ValueError('Esquema inválido')
        # Additive schema-1 migration for saves created before health/wounds
        # were mirrored explicitly in the regional state.
        if schema == 1:
            for state in payload.get('heroes', {}).values():
                state.setdefault('wounds', max(0, min(3, 3-state.get('health', 3))))
                state.setdefault('hungry', False)
                state.setdefault('thirsty', False)
                state.setdefault('streak', 0)
            for person in [*payload.get('npcs', {}).values(),
                           *payload.get('continuity_people', [])]:
                if 'health' in person:
                    person.setdefault('wounds', max(0, min(3, 3-person.get('health', 3))))
                person.setdefault('hungry', False)
                person.setdefault('thirsty', False)
                person.setdefault('streak', 0)
        payload['expeditions'] = {k:Expedition(**v) for k,v in payload['expeditions'].items()}
        world = cls(**payload)
        world.validate()
        return world


def _lists(value):
    return [_lists(v) for v in value] if isinstance(value,tuple) else value


def _tuples(value):
    return tuple(_tuples(v) for v in value) if isinstance(value,list) else value
