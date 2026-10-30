"""Mapa tático experimental. Geometria congelada do Mercado; regras novas isoladas."""
import json
from copy import deepcopy
from collections import deque
from math import ceil
from pathlib import Path

from system import ITEMS, NPCS, REGIONAL_CONTACTS, VEHICLES, World
import community as community_rules
from horde_deck02 import HordeDeck02

TACTICS=json.loads((Path(__file__).parent/'data/tactics.json').read_text(encoding='utf-8'))
LEGACY_HEROES={hero['id']:hero for hero in json.loads(
    (Path(__file__).resolve().parents[1]/'content/catalog.json').read_text(encoding='utf-8')
)['heroes']}


def edge(a,b):
    return '-'.join(map(str,sorted((a,b))))


class TacticalGame:
    def __init__(self,world:World,expedition_id:str):
        if expedition_id not in world.encounters:
            raise ValueError('Encontro ausente')
        self.world=world
        self.id=expedition_id

    @classmethod
    def start(cls,world:World,expedition_id:str,map_id:str):
        if (map_id not in TACTICS['maps'] or expedition_id not in world.expeditions
                or world.expeditions[expedition_id].remaining!=0
                or expedition_id in world.encounters):
            raise ValueError('Não pode iniciar encontro')
        map_data=TACTICS['maps'][map_id]
        destination=world.expeditions[expedition_id].destination
        if map_data.get('reference_only'):
            raise ValueError('Planta de referência ainda sem destino no motor')
        if map_data.get('location') and map_data['location']!=destination:
            raise ValueError('Mapa incompatível com o destino')
        if destination=='EXP-LOC-06' and map_id!='military_installation':
            raise ValueError('Instalação exige mapa militar')
        if any(other.destination==destination and other_id in world.encounters
               for other_id,other in world.expeditions.items()):
            raise ValueError('Local já em uso por outra equipe')
        contacts={}
        state={
            'map':map_id,'heroes':{h:map_data['entry'] for h in world.expeditions[expedition_id].heroes},
            'search_zones':list(map_data['search']),
            'enemies':{},'next_enemy':1,
            'doors':{edge(*d['edge']):{'open':False,'resistance':d['resistance'],
                                      'blocked':d['blocked']} for d in map_data['doors']},
            'noise':[],'announced':[],'round':0,'pressure':0,'initial_spawned':False,
            'van_state':'abandoned','van_attempts':[],
            'fuel_cards_taken':[],'fuel_cache_collected':False,
            'discovered_npcs':[],'npc_contacts':contacts,'npc_followers':{}}
        previous=world.site_states.get(destination)
        if previous:
            if previous['map']!=map_id:
                raise ValueError('Mapa incompatível com a revisita')
            for key in ('enemies','next_enemy','doors','announced','round','pressure',
                        'initial_spawned','van_state','fuel_cards_taken',
                        'fuel_cache_collected','discovered_npcs'):
                if key in previous:
                    state[key]=deepcopy(previous[key])
            stranded=set(previous.get('stranded_npcs',[]))
            discovered=set(state.get('discovered_npcs',[])) | stranded
            if world.cistern_verified and world.continuous_campaign:
                for npc_id,contact in REGIONAL_CONTACTS.get('contacts',{}).items():
                    if (npc_id in discovered and contact['location']==destination
                            and contact['map']==map_id
                            and world.regional_contact_identity_available(npc_id,destination)):
                        state['npc_contacts'][npc_id]=contact['zone']
        elif world.cistern_verified and world.continuous_campaign:
            # Contacts become visible only after a legal investigation action.
            # They are not placed automatically at expedition start.
            pass
        state['van_attempts']=[]  # Regra canônica: uma tentativa por herói/visita.
        state['first_market_visit']=(world.continuous_campaign
                                     and destination=='EXP-LOC-02' and previous is None)
        if world.continuous_campaign:
            if world.regional_horde_deck is None:
                world.regional_horde_deck=HordeDeck02.new(world.seed+8102).snapshot()
            if not state.get('initial_spawned',False):
                for _ in range(ceil(len(world.expeditions[expedition_id].heroes)/2)):
                    eid=f"E{state['next_enemy']:03d}"
                    state['next_enemy']+=1
                    state['enemies'][eid]={'kind':'slow','zone':map_data['spawn'],
                                           'health':TACTICS['enemies']['slow']['health']}
                if destination=='EXP-LOC-05':
                    eid=f"E{state['next_enemy']:03d}"
                    state['next_enemy']+=1
                    # The station's extra threat uses the printed spawn point,
                    # never the survivor contact/search objective zone.
                    state['enemies'][eid]={'kind':'brute','zone':map_data['spawn'],
                                           'health':TACTICS['enemies']['brute']['health']}
                state['initial_spawned']=True
        if (world.continuous_campaign
                and world.regional_clock+1+world.expeditions[expedition_id].segment_cost>10):
            raise ValueError('Sem reserva no relógio regional para iniciar uma rodada e retornar')
        world.advance_regional_segment(expedition_id,'map_round')
        state['round_clock']=world.regional_clock
        world._refresh_actions()
        world.encounters[expedition_id]=state
        world.validate()
        return cls(world,expedition_id)

    @property
    def state(self):
        return self.world.encounters[self.id]

    @property
    def map(self):
        return TACTICS['maps'][self.state['map']]

    def snapshot(self):
        return self.state

    @property
    def exit_zone(self) -> int:
        """Public exit location for route planning by campaign controllers."""
        return self.map['exit']

    def path_to(self, hero_id: str, destination: int) -> list[int] | None:
        """Return the current shortest open route without mutating game state."""
        if hero_id not in self.state['heroes'] or destination not in self.map['zones']:
            raise ValueError('Herói/zona inválida')
        return self._path(self.state['heroes'][hero_id], destination)

    def _adjacent(self,a,b):
        return [a,b] in self.map['edges'] or [b,a] in self.map['edges']

    def _passable(self,a,b):
        if not self._adjacent(a,b):
            return False
        door=self.state['doors'].get(edge(a,b))
        return door is None or door['open']

    def move(self,hero_id,destination):
        if hero_id not in self.state['heroes'] or destination not in self.map['zones']:
            raise ValueError('Herói/zona inválida')
        origin=self.state['heroes'][hero_id]
        cost=1+int(any(enemy['zone']==origin for enemy in self.state['enemies'].values()))
        if not self._passable(origin,destination):
            raise ValueError('Movimento indisponível')
        if self.world.heroes[hero_id]['health']<1:
            raise ValueError('Herói incapacitado não pode mover')
        if self.world.heroes[hero_id]['actions']<cost:
            raise ValueError(f'Movimento exige {cost} PA')
        self.world.heroes[hero_id]['actions']-=cost
        self.state['heroes'][hero_id]=destination
        return destination

    def open_door(self,hero_id,a,b):
        """Abre uma porta comum adjacente por 1 PA; porta bloqueada requer ferramenta."""
        if hero_id not in self.state['heroes'] or not self._adjacent(a,b):
            raise ValueError('Porta fora de alcance')
        door=self.state['doors'].get(edge(a,b))
        if (not door or door['open'] or door['blocked']
                or self.state['heroes'][hero_id] not in (a,b)
                or self.world.heroes[hero_id]['actions']<1
                or self.world.heroes[hero_id]['health']<1):
            raise ValueError('Porta comum indisponível ou bloqueada')
        self.world.heroes[hero_id]['actions']-=1
        door['open']=True
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'open_common_door','hero':hero_id,
                               'edge':edge(a,b),'action_cost':1})
        return True

    def breach(self,hero_id,a,b,instance_id):
        if (hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id] not in (a,b)
                or not self._adjacent(a,b)):
            raise ValueError('Porta fora de alcance')
        door=self.state['doors'].get(edge(a,b))
        if not door or door['open']:
            raise ValueError('Porta indisponível')
        if not door['blocked']:
            raise ValueError('Porta não bloqueada; use open_door')
        if self.world.heroes[hero_id]['health']<1:
            raise ValueError('Herói incapacitado não pode arrombar')
        if self.world.heroes[hero_id]['actions']<2:
            raise ValueError('Porta bloqueada exige 2 PA')
        item=self.world.gear[hero_id][instance_id]
        spec=ITEMS[item['template']]
        if item['slot']!='hand' or item['durability']<1 or spec['breach']<1:
            raise ValueError('Ferramenta indisponível')
        self.world.heroes[hero_id]['actions']-=2
        # RULES §5: a blocked door takes a fixed two PA with a crowbar/tool,
        # no test. Experimental resistance values are not another mechanic.
        door['open']=True
        return True

    def search(self, hero_id: str) -> dict[str, int]:
        """Busca de uma carta/unidade custa 1 PA no setor impresso no mapa."""
        return self.world.search(self.id, hero_id)

    def investigate_contact(self, hero_id: str, npc_id: str) -> dict:
        """Revela um sobrevivente por investigação física, sem conceder pistas.

        Esta disponibilidade regional é experimental e só vale após a vitória
        certificada da Cisterna, antes do código de rádio. Encontrar alguém e
        recrutá-lo são ações separadas; a zona precisa estar livre de inimigos.
        """
        exp=self.world.expeditions[self.id]
        contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc_id)
        if (not self.world.continuous_campaign or not contact
                or contact.get('moment') not in (
                    'post_cistern_pre_radio',
                    'post_cistern_pre_radio_if_not_in_community')
                or self.world.flags.get('radio_code')
                or contact['location']!=exp.destination
                or contact['map']!=self.state['map']
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=contact['zone']):
            raise ValueError('Investigação de contato indisponível neste local/momento')
        if (not self.world.regional_contact_identity_available(npc_id,exp.destination)
                or npc_id in self.state['npc_contacts']):
            raise ValueError('Identidade já presente ou contato já investigado')
        hero=self.world.heroes[hero_id]
        discovery=contact.get('discovery',{})
        cost=discovery.get('action_cost',1)
        if hero['health']<1 or hero['actions']<cost:
            raise ValueError('Investigar exige herói ativo e 1 PA')
        if any(enemy['zone']==contact['zone']
               for enemy in self.state['enemies'].values()):
            raise ValueError('Não é seguro investigar contato com ameaça na zona')
        hero['actions']-=cost
        self.state['npc_contacts'][npc_id]=contact['zone']
        if npc_id not in self.state['discovered_npcs']:
            self.state['discovered_npcs'].append(npc_id)
        receipt={'npc':npc_id,'hero':hero_id,'zone':contact['zone'],
                 'location':exp.destination,'action_cost':cost,'clues_awarded':0}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'investigate_physical_contact',**receipt})
        self.world.validate()
        return receipt

    def collect_contact_evidence(self, hero_id: str, npc_id: str) -> dict:
        """Registra uma pista somente após uma ação física de leitura/cópia."""
        exp=self.world.expeditions[self.id]
        contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc_id)
        evidence=contact.get('evidence') if contact else None
        if (not self.world.continuous_campaign or not evidence
                or self.world.flags.get('radio_code')
                or contact.get('moment') not in (
                    'post_cistern_pre_radio',
                    'post_cistern_pre_radio_if_not_in_community')
                or npc_id not in self.state.get('discovered_npcs', [])
                or contact['location']!=exp.destination
                or contact['map']!=self.state['map']
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=contact['zone']):
            raise ValueError('Evidência indisponível sem investigação física no local')
        if not any(row.get('action')=='investigate_physical_contact'
                   and row.get('npc')==npc_id
                   and row.get('location')==contact['location']
                   for row in self.world.log):
            raise ValueError('Evidência indisponível sem recibo de investigação física')
        evidence_id=evidence['id']
        if any(row.get('action')=='collect_regional_evidence'
               and row.get('evidence_id')==evidence_id for row in self.world.log):
            raise ValueError('Evidência única já coletada')
        hero=self.world.heroes[hero_id]
        if hero['health']<1 or hero['actions']<evidence['action_cost']:
            raise ValueError('Copiar evidência exige herói ativo e 1 PA')
        if any(enemy['zone']==contact['zone']
               for enemy in self.state['enemies'].values()):
            raise ValueError('Não é seguro copiar evidência com ameaça na zona')
        hero['actions']-=evidence['action_cost']
        self.world.clues+=evidence['clues']
        receipt={'evidence_id':evidence_id,'name':evidence['name'],
                 'npc':npc_id,'hero':hero_id,'zone':contact['zone'],
                 'location':contact['location'],
                 'action_cost':evidence['action_cost'],
                 'clues_awarded':evidence['clues'],'total_clues':self.world.clues}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'collect_regional_evidence',**receipt})
        self.world.validate()
        return receipt

    def contact_npc(self, hero_id: str, npc_id: str) -> dict:
        """Recruit a regional survivor only through physical contact on the map."""
        exp=self.world.expeditions[self.id]
        contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc_id)
        zone=self.state.get('npc_contacts',{}).get(npc_id)
        if not contact:
            raise ValueError('Sobrevivente desconhecido')
        existing=self.world.npcs.get(npc_id)
        if not self.world.regional_contact_identity_available(npc_id,exp.destination):
            raise ValueError('Sobrevivente não disponível: identidade já está na comunidade')
        if (zone is None or contact['location']!=exp.destination
                or contact['map']!=self.state['map'] or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=zone
                or not self.world.continuous_campaign
                or self.world.flags.get('radio_code')
                or contact.get('moment') not in (
                    'post_cistern_pre_radio',
                    'post_cistern_pre_radio_if_not_in_community')
                or npc_id not in self.state.get('discovered_npcs', [])
                or not any(row.get('action')=='investigate_physical_contact'
                           and row.get('npc')==npc_id
                           and row.get('location')==exp.destination
                           for row in self.world.log)):
            raise ValueError('Sobrevivente exige investigação prévia e contato físico na zona de contato')
        if self.world.heroes[hero_id]['health']<1 or self.world.heroes[hero_id]['actions']<1:
            raise ValueError('Contato indisponível sem herói ativo e 1 PA')
        if any(enemy['zone']==zone for enemy in self.state['enemies'].values()):
            raise ValueError('Não é seguro contatar sobrevivente com ameaça na zona')
        if (self.world.residents>=self.world.beds+community_rules.bed_allowance(self.world)
                or self.world.stock['food']<self.world.residents+1
                or self.world.stock['water']<self.world.residents+1):
            raise ValueError('A comunidade não tem vaga e sustento para acolher Célia')
        capacity=(VEHICLES[exp.vehicle_id]['seats'] if exp.vehicle_id
                  else 6*len(exp.heroes))
        if len(exp.heroes)+len(exp.crew)+1>capacity:
            raise ValueError('Sem capacidade de transporte para Célia')
        self.world.heroes[hero_id]['actions']-=1
        if existing is None:
            self.world.npcs[npc_id]={'level':1,'job':None,'health':3,'location':self.id}
        else:
            existing['location']=self.id
            site_state=self.world.site_states.get(exp.destination,{})
            site_state['stranded_npcs']=[person for person in
                                         site_state.get('stranded_npcs',[])
                                         if person!=npc_id]
            self.world.site_states[exp.destination]=site_state
        exp.crew.append(npc_id)
        if self.world.community is not None and existing is None:
            community_rules.join(self.world, npc_id)
        del self.state['npc_contacts'][npc_id]
        self.state['npc_followers'][npc_id]=hero_id
        receipt={'npc':npc_id,'hero':hero_id,'zone':zone,'location':exp.destination,
                 'action_cost':1}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'physical_contact_recruit',**receipt})
        self.world.validate()
        return receipt

    def salvage_fuel_cache(self, hero_id: str) -> dict:
        """Recupera a reserva experimental única da Oficina como carga física.

        A ação custa 2 PA e gera ruído alto. O combustível não entra no estoque
        até a expedição retornar normalmente; emergência perde a carga sem
        restaurar a reserva.
        """
        source=REGIONAL_CONTACTS.get('experimental_fuel',{})
        exp=self.world.expeditions[self.id]
        zone=source.get('zone')
        if (not self.world.continuous_campaign
                or not source.get('status','').startswith('experimental')
                or exp.destination!=source.get('location')
                or self.state['map']!=source.get('map')
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=zone
                or self.state.get('fuel_cache_collected')):
            raise ValueError('Reserva experimental indisponível neste local')
        hero=self.world.heroes[hero_id]
        cost=source['action_cost']
        capacity=(VEHICLES[exp.vehicle_id]['cargo_capacity'] if exp.vehicle_id
                  else 6*len(exp.heroes))
        amount=source['units']
        if hero['health']<1 or hero['actions']<cost:
            raise ValueError('Recuperar a reserva exige herói ativo e 2 PA')
        if any(enemy['zone']==zone for enemy in self.state['enemies'].values()):
            raise ValueError('Não é seguro desmontar a reserva com ameaça na zona')
        if sum(exp.cargo.values())+len(exp.special_cargo)+amount>capacity:
            raise ValueError('Reserva excede a capacidade de carga')
        hero['actions']-=cost
        self.state['fuel_cache_collected']=True
        exp.cargo['fuel']=exp.cargo.get('fuel',0)+amount
        self.noise(zone,source['noise'])
        receipt={'id':source['id'],'hero':hero_id,'zone':zone,'fuel':amount,
                 'action_cost':cost,'noise':source['noise'],
                 'cargo_fuel':exp.cargo['fuel'],'stock_added':0}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'salvage_fuel_cache',**receipt})
        self.world.validate()
        return receipt

    def emergency_return(self, reason: str) -> dict:
        """Apply the campaign's explicit failed-expedition return procedure."""
        return self.world.emergency_return(self.id,reason)

    def pickup_unique_item(self, hero_id: str, item: str) -> None:
        """Retira uma peça única no objetivo canônico e a transporta na expedição."""
        exp=self.world.expeditions[self.id]
        required={'battery':('EXP-LOC-03',7)}.get(item)
        if (required is None or (exp.destination, self.state['heroes'].get(hero_id))!=required
                or hero_id not in self.state['heroes']
                or item not in self.world.unique_items_at_sites.get(exp.destination, [])
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<1
                or sum(exp.cargo.values())+len(exp.special_cargo)
                   >= 6*len(exp.heroes)):
            raise ValueError('Peça única indisponível ou fora do objetivo')
        self.world.heroes[hero_id]['actions']-=1
        self.world.unique_items_at_sites[exp.destination].remove(item)
        exp.special_cargo.append(item)
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'pickup_unique','item':item,
                               'hero':hero_id,'zone':required[1]})

    def pickup_fuel_card(self, hero_id: str, lot: int) -> dict:
        """Retira uma das oito cartas únicas de combustível do O1 por 1 PA."""
        exp=self.world.expeditions[self.id]
        identifier=f'EXP-LOC-07:Combustível:{lot}'
        if (exp.destination!='EXP-LOC-07' or self.state['map']!='gas_station_02'
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=7
                or not isinstance(lot,int) or not 1<=lot<=8
                or identifier in self.state['fuel_cards_taken']
                or self.world.searches['EXP-LOC-07']<1
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<1):
            raise ValueError('Carta de combustível indisponível ou fora da zona O1')
        capacity=(VEHICLES[exp.vehicle_id]['cargo_capacity'] if exp.vehicle_id
                  else 6*len(exp.heroes))
        if sum(exp.cargo.values())+len(exp.special_cargo)+1>capacity:
            raise ValueError('Carga sem espaço para combustível')
        self.world.heroes[hero_id]['actions']-=1
        self.world.searches['EXP-LOC-07']-=1
        self.state['fuel_cards_taken'].append(identifier)
        exp.cargo['fuel']=exp.cargo.get('fuel',0)+1
        receipt={'id':identifier,'hero':hero_id,'zone':7,'cargo_fuel':exp.cargo['fuel']}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'pickup_fuel_card',**receipt})
        return receipt

    def drain_truck_tank(self, hero_id: str) -> dict:
        """O2 do Posto na edição integral (D-21): tanque do caminhão, uma vez.

        1 PA na zona do O2; o combustível vira carga física da expedição.
        """
        exp=self.world.expeditions[self.id]
        if self.world.community is None:
            raise ValueError('Tanque do caminhão só existe na edição integral')
        tank=community_rules.RULES['vehicles']['truck_tank']
        if (exp.destination!=tank['location'] or self.state['map']!='gas_station_02'
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=tank['zone']
                or self.world.flags.get('truck_tank_drained')
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<tank['actions']):
            raise ValueError('Tanque do caminhão indisponível ou fora do O2')
        amount=self.world.site_states.get(tank['location'],{}).get('truck_tank_fuel',
                                                                   tank['fuel'])
        capacity=(VEHICLES[exp.vehicle_id]['cargo_capacity'] if exp.vehicle_id
                  else 6*len(exp.heroes))
        if sum(exp.cargo.values())+len(exp.special_cargo)+amount>capacity:
            raise ValueError('Carga sem espaço para o combustível do tanque')
        self.world.heroes[hero_id]['actions']-=tank['actions']
        self.world.flags['truck_tank_drained']=True
        exp.cargo['fuel']=exp.cargo.get('fuel',0)+amount
        receipt={'hero':hero_id,'zone':tank['zone'],'fuel':amount,
                 'cargo_fuel':exp.cargo['fuel']}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'drain_truck_tank',**receipt})
        return receipt

    def inspect_van(self, hero_id: str) -> None:
        exp=self.world.expeditions[self.id]
        if (exp.destination!='EXP-LOC-07' or self.state['map']!='gas_station_02'
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=7
                or self.state['van_state']!='abandoned'
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<1):
            raise ValueError('Van indisponível para inspeção no O1')
        self.world.heroes[hero_id]['actions']-=1
        self.state['van_state']='incomplete'
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'inspect_van','hero':hero_id,'zone':7})

    def repair_van(self, hero_id: str) -> dict:
        exp=self.world.expeditions[self.id]
        if (exp.destination!='EXP-LOC-07' or self.state['map']!='gas_station_02'
                or hero_id not in self.state['heroes']
                or self.state['heroes'][hero_id]!=7
                or self.state['van_state']!='incomplete'
                or hero_id in self.state['van_attempts']
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<2
                or 'battery' not in exp.special_cargo):
            raise ValueError('Reparo da van exige inspeção, Bateria, O1 e 2 PA')
        self.world.heroes[hero_id]['actions']-=2
        self.state['van_attempts'].append(hero_id)
        roll=self.world._d6()[0]
        technique=LEGACY_HEROES[hero_id]['attributes']['Técnica']
        success=roll==6 or (roll!=1 and roll+technique>=6)
        if success:
            exp.special_cargo.remove('battery')
            self.state['van_state']='operational'
            self.world.vehicles['EXP-VEI-02']={
                'location':exp.destination,'health':VEHICLES['EXP-VEI-02']['health']}
        receipt={'hero':hero_id,'roll':roll,'technique':technique,
                 'success':success,'battery_consumed':success}
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'repair_van',**receipt})
        self.world.validate()
        return receipt

    def _neighbors(self,zone):
        return [b if a==zone else a for a,b in self.map['edges']
                if (a==zone or b==zone) and self._passable(a,b)]

    def _path(self,start,goal):
        todo=deque([(start,[start])]);seen={start}
        while todo:
            current,path=todo.popleft()
            if current==goal:return path
            for nxt in sorted(self._neighbors(current)):
                if nxt not in seen:
                    seen.add(nxt);todo.append((nxt,path+[nxt]))
        return None

    def line_of_sight(self,a,b):
        if a==b:return True
        ar,ac=divmod(a-1,4);br,bc=divmod(b-1,4)
        if ar!=br and ac!=bc:return False
        step=1 if ar==br and b>a else -1 if ar==br else 4 if b>a else -4
        return all(self._passable(z,z+step) for z in range(a,b,step))

    def spawn(self,kind,zone=None):
        if kind not in TACTICS['enemies']:
            raise ValueError('Inimigo desconhecido')
        if len(self.state['enemies'])>=24:
            raise ValueError('Limite canônico de 24 inimigos; resolução de excedente pendente')
        zone=self.map['spawn'] if zone is None else zone
        if zone not in self.map['zones']:
            raise ValueError('Zona inválida')
        eid=f"E{self.state['next_enemy']:03d}"
        self.state['next_enemy']+=1
        self.state['enemies'][eid]={'kind':kind,'zone':zone,
                                    'health':TACTICS['enemies'][kind]['health']}
        return eid

    def attack(self,hero_id,instance_id,enemy_id):
        if hero_id not in self.state['heroes'] or enemy_id not in self.state['enemies']:
            raise ValueError('Atacante/alvo indisponível')
        if self.world.heroes[hero_id]['health']<1:
            raise ValueError('Herói incapacitado')
        start=self.state['heroes'][hero_id]
        enemy=self.state['enemies'][enemy_id]
        item=self.world.gear[hero_id][instance_id]
        spec=ITEMS[item['template']]['combat']
        reach=spec.get('range',1) if spec else 0
        end=enemy['zone']
        distance=abs((start-1)//4-(end-1)//4)+abs((start-1)%4-(end-1)%4)
        if distance>reach or not self.line_of_sight(start,end):
            raise ValueError('Alvo fora de alcance/visão')
        result=self.world.attack_with_item(hero_id,instance_id)
        enemy['health']=max(0,enemy['health']-result['damage'])
        if enemy['health']==0:
            self.world.award_xp(hero_id,TACTICS['enemies'][enemy['kind']]['xp'],combat=True)
            del self.state['enemies'][enemy_id]
        intensity={'baixo':1,'médio':2,'alto':3}[result['noise']]
        intensity=max(0,intensity-self.world.skill_bonus(hero_id,'noise'))
        if intensity:
            self.noise(start,intensity)
        return dict(result,enemy_health=enemy['health'])

    def finish(self,retreat=False):
        if any(zone!=self.map['exit'] for zone in self.state['heroes'].values()):
            raise ValueError('Equipe fora da saída')
        for npc_id,hero_id in self.state.get('npc_followers',{}).items():
            if (self.world.npcs[npc_id]['location']!=self.id
                    or self.state['heroes'].get(hero_id)!=self.map['exit']):
                raise ValueError('Resgatado precisa acompanhar seu herói até a saída')
        if any(enemy['zone']==self.map['exit'] for enemy in self.state['enemies'].values()):
            raise ValueError('Ameaça ainda presente na zona de saída')
        self.world.log.append({'day':self.world.day,'encounter':self.id,
                               'retreat':bool(retreat),'enemies_remaining':len(self.state['enemies'])})
        destination=self.world.expeditions[self.id].destination
        prior_site=self.world.site_states.get(destination,{})
        saved=deepcopy({key:self.state[key] for key in
                        ('map','enemies','next_enemy','doors','announced','round','pressure',
                         'initial_spawned','van_state','fuel_cards_taken',
                         'fuel_cache_collected','discovered_npcs')})
        for key in ('stranded_npcs','lost_special_items'):
            if prior_site.get(key):
                saved[key]=deepcopy(prior_site[key])
        if self.state.get('npc_followers'):
            saved['stranded_npcs']=[person for person in saved.get('stranded_npcs',[])
                                    if person not in self.state['npc_followers']]
        self.world.site_states[destination]=saved
        del self.world.encounters[self.id]

    def noise(self,zone,intensity):
        if zone not in self.map['zones'] or intensity not in (1,2,3):
            raise ValueError('Ruído inválido')
        self.state['noise'].append({'zone':zone,'intensity':intensity})

    def announce_horde(self,kind,delay=None):
        if kind not in TACTICS['hordes']:
            raise ValueError('Horda desconhecida')
        delay=TACTICS['hordes'][kind]['announced_delay'] if delay is None else delay
        if delay<0:raise ValueError('Atraso inválido')
        self.state['announced'].append({'kind':kind,'delay':delay})

    def _draw_regional_horde(self):
        deck=HordeDeck02.from_snapshot(self.world.regional_horde_deck)
        card=deck.draw()
        self.world.regional_horde_deck=deck.snapshot()
        kind,count={
            'Arrastar':('slow',1),
            'Corrida':('runner',1),
            'Aglomerado':('slow',ceil(len(self.world.expeditions[self.id].heroes)/2)),
            'Peso morto':('brute',1),
        }[card]
        spawned=[self.spawn(kind) for _ in range(count)]
        self.world.log.append({'day':self.world.day,'expedition':self.id,
                               'action':'regional_horde','card':card,
                               'enemies':list(spawned)})
        return spawned

    def activate(self):
        if self.state.get('round_closed'):
            raise ValueError('Expedição tática encerrada pelo relógio regional')
        spawned=[]
        attacks=[]
        protected_market=(self.state.get('first_market_visit') and self.state['round']==0)
        for eid,enemy in ([] if protected_market else list(self.state['enemies'].items())):
            spec=TACTICS['enemies'][enemy['kind']]
            for _ in range(spec['move']):
                victims=[h for h,z in self.state['heroes'].items() if z==enemy['zone']
                         and self.world.heroes[h]['health']>0]
                if victims:break
                targets=[n['zone'] for n in self.state['noise'] if n['intensity']>=2]
                if not targets:
                    targets=[zone for hero_id,zone in self.state['heroes'].items()
                             if self.world.heroes[hero_id]['health']>0
                             and self.line_of_sight(enemy['zone'],zone)
                             and abs((enemy['zone']-1)//4-(zone-1)//4)
                                 +abs((enemy['zone']-1)%4-(zone-1)%4)<=spec['sight']]
                paths=[self._path(enemy['zone'],z) for z in targets]
                paths=[p for p in paths if p]
                if not paths:break
                path=min(paths,key=lambda p:(len(p),p[-1]))
                if len(path)>1:enemy['zone']=path[1]
            victims=[h for h,z in self.state['heroes'].items() if z==enemy['zone']
                     and self.world.heroes[h]['health']>0]
            if victims:
                hero_id=sorted(victims)[0]
                armor=next((iid for iid,item in self.world.gear[hero_id].items()
                            if item['slot'] in ('head','torso','legs')
                            and 'armor' in ITEMS[item['template']] and item['durability']>0),None)
                prior=self.world.heroes[hero_id]['health']
                harm=self.world.receive_damage(hero_id,spec['attack'],armor)
                infection=self.world.roll_infection(hero_id) if harm['health']<prior else None
                attacks.append({'enemy':eid,'hero':hero_id,**harm,'infection':infection})
        self.state['noise']=[]
        later=[]
        for horde in self.state['announced']:
            if protected_market:
                # The introductory round suspends all enemy activation and
                # spawning; its pending announcements therefore do not tick.
                later.append(horde)
            elif horde['delay']>0:
                horde['delay']-=1
                later.append(horde)
            else:
                spawned.extend(self.spawn(kind)
                               for kind in TACTICS['hordes'][horde['kind']]['units'])
        self.state['announced']=later
        if self.world.continuous_campaign:
            if protected_market:
                # The campaign's first market round suppresses activation/spawn;
                # the printed rule still advances local pressure to one.
                self.state['pressure']=1
            else:
                self.state['pressure']+=1
                if self.state['pressure']>=2:
                    self.state['pressure']=0
                    spawned.extend(self._draw_regional_horde())
                if self.state.get('round_clock',0)>=9:
                    spawned.extend(self._draw_regional_horde())
        self.state['round']+=1
        if self.world.continuous_campaign:
            exp=self.world.expeditions[self.id]
            if (self.world.regional_clock>=10
                    or self.world.regional_clock+1+exp.segment_cost>10):
                self.state['round_closed']=True
                return {'spawned':spawned,'attacks':attacks,'round':self.state['round'],
                        'clock':self.world.regional_clock,'return_reserve':False,
                        'round_closed':True}
            clock=self.world.advance_regional_segment(self.id,'map_round')
            self.state['round_clock']=self.world.regional_clock
            self.world._refresh_actions()
            return {'spawned':spawned,'attacks':attacks,'round':self.state['round'],
                    'clock':self.world.regional_clock,'fatigue':clock['fatigue'],
                    'return_reserve':True,'round_closed':False}
        self.world.begin_round()
        return {'spawned':spawned,'attacks':attacks,'round':self.state['round']}
