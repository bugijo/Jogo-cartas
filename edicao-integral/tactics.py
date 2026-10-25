"""Mapa tático experimental. Geometria congelada do Mercado; regras novas isoladas."""
import json
from copy import deepcopy
from collections import deque
from pathlib import Path

from system import ITEMS, VEHICLES, World

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
        state={
            'map':map_id,'heroes':{h:map_data['entry'] for h in world.expeditions[expedition_id].heroes},
            'search_zones':list(map_data['search']),
            'enemies':{},'next_enemy':1,
            'doors':{edge(*d['edge']):{'open':False,'resistance':d['resistance'],
                                      'blocked':d['blocked']} for d in map_data['doors']},
            'noise':[],'announced':[],'round':0,
            'van_state':'abandoned','van_attempts':[],
            'fuel_cards_taken':[]}
        previous=world.site_states.get(destination)
        if previous:
            if previous['map']!=map_id:
                raise ValueError('Mapa incompatível com a revisita')
            for key in ('enemies','next_enemy','doors','announced','round',
                        'van_state','fuel_cards_taken'):
                if key in previous:
                    state[key]=deepcopy(previous[key])
        state['van_attempts']=[]  # Regra canônica: uma tentativa por herói/visita.
        world.begin_round()
        world.encounters[expedition_id]=state
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
        if (not self._passable(origin,destination) or self.world.heroes[hero_id]['actions']<1
                or self.world.heroes[hero_id]['health']<1):
            raise ValueError('Movimento indisponível')
        self.world.heroes[hero_id]['actions']-=1
        self.state['heroes'][hero_id]=destination
        return destination

    def breach(self,hero_id,a,b,instance_id):
        if hero_id not in self.state['heroes'] or self.state['heroes'][hero_id]!=a or not self._adjacent(a,b):
            raise ValueError('Porta fora de alcance')
        door=self.state['doors'].get(edge(a,b))
        if (not door or door['open'] or self.world.heroes[hero_id]['actions']<1
                or self.world.heroes[hero_id]['health']<1):
            raise ValueError('Porta indisponível')
        item=self.world.gear[hero_id][instance_id]
        spec=ITEMS[item['template']]
        if item['slot']!='hand' or item['durability']<1 or spec['breach']<1:
            raise ValueError('Ferramenta indisponível')
        item['durability']-=1
        self.world.heroes[hero_id]['actions']-=1
        door['resistance']-=spec['breach']
        opened=door['resistance']<=0
        if opened:
            door['open']=True
        self.noise(a,2)
        return opened

    def search(self, hero_id: str) -> dict[str, int]:
        """Busca de uma carta/unidade custa 1 PA no setor impresso no mapa."""
        return self.world.search(self.id, hero_id)

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
        if self.state['enemies'] and not retreat:
            raise ValueError('Ameaças ainda presentes')
        self.world.log.append({'day':self.world.day,'encounter':self.id,
                               'retreat':bool(retreat),'enemies_remaining':len(self.state['enemies'])})
        destination=self.world.expeditions[self.id].destination
        self.world.site_states[destination]=deepcopy({key:self.state[key] for key in
                                                     ('map','enemies','next_enemy','doors','announced','round',
                                                      'van_state','fuel_cards_taken')})
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

    def activate(self):
        spawned=[]
        later=[]
        for horde in self.state['announced']:
            if horde['delay']>0:
                horde['delay']-=1;later.append(horde)
            else:
                spawned.extend(self.spawn(kind) for kind in TACTICS['hordes'][horde['kind']]['units'])
        self.state['announced']=later
        attacks=[]
        for eid,enemy in list(self.state['enemies'].items()):
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
        self.state['round']+=1
        self.world.begin_round()
        return {'spawned':spawned,'attacks':attacks,'round':self.state['round']}
