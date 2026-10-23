"""Mapa tático experimental. Geometria congelada do Mercado; regras novas isoladas."""
import json
from copy import deepcopy
from collections import deque
from pathlib import Path

from system import ITEMS, World

TACTICS=json.loads((Path(__file__).parent/'data/tactics.json').read_text(encoding='utf-8'))


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
        if any(other.destination==destination and other_id in world.encounters
               for other_id,other in world.expeditions.items()):
            raise ValueError('Local já em uso por outra equipe')
        state={
            'map':map_id,'heroes':{h:map_data['entry'] for h in world.expeditions[expedition_id].heroes},
            'search_zones':list(map_data['search']),
            'enemies':{},'next_enemy':1,
            'doors':{edge(*d['edge']):{'open':False,'resistance':d['resistance'],
                                      'blocked':d['blocked']} for d in map_data['doors']},
            'noise':[],'announced':[],'round':0}
        previous=world.site_states.get(destination)
        if previous:
            if previous['map']!=map_id:
                raise ValueError('Mapa incompatível com a revisita')
            for key in ('enemies','next_enemy','doors','announced','round'):
                state[key]=deepcopy(previous[key])
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
                                                     ('map','enemies','next_enemy','doors','announced','round')})
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
                    targets=list(self.state['heroes'].values())
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
