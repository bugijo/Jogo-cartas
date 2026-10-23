"""Núcleo fiel de preparação, porções, relógio e filtro da edição 0.2.

Não substitui RULES.md/CAMPAIGN.md nem implementa exploração e cercos.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from math import ceil
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CATALOG=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf-8'))
STARTERS=tuple(hero['id'] for hero in CATALOG['heroes'] if hero['initial'])
LINK_IDS=tuple(card['id'] for card in CATALOG['cards'] if card['family']=='VIN')
LINK_PEOPLE={**{link:(0,0) for link in LINK_IDS[:4]},
             **{link:(1,0) for link in LINK_IDS[4:10]},
             LINK_IDS[10]:(0,1),LINK_IDS[11]:(1,1)}
STAGES={'A':{'materials':1,'part':'Conexões','work':1},
        'B':{'materials':1,'part':'Bomba','work':1},
        'C':{'materials':1,'part':'Membrana','work':2}}


@dataclass
class Cistern02:
    founders: list[str]
    links: list[str]
    initial_consumers: int
    humans: int
    dogs: int
    capacity: int
    food: list[int]
    water: list[int]
    people: list[dict] = field(default_factory=list)
    meat: list[int] = field(default_factory=list)
    materials: int = 3
    day: int = 1
    clock: int = 0
    parts: dict[str,int] = field(default_factory=dict)
    reserved: list[str] = field(default_factory=list)
    stage: str = 'A'
    stage_work: int = 0
    works_today: int = 0
    meal_day: int = 0
    filter_active: bool = False
    morale: int = 5
    health: int = 5
    pressure: int = 0
    ammo: int = 2
    structures: list[str] = field(default_factory=lambda:['Portão','Cozinha','Depósito'])
    pending_sieges: list[str] = field(default_factory=list)
    planned_guards: list[str] = field(default_factory=list)
    siege_day: int = 0

    @classmethod
    def new(cls,founders:list[str] | tuple[str,...],links:list[str] | tuple[str,...]) -> 'Cistern02':
        founders=list(founders);links=list(links)
        if (not 2<=len(founders)<=6 or len(links)!=len(founders)
                or len(set(founders))!=len(founders) or any(hero not in STARTERS for hero in founders)
                or any(link not in LINK_IDS for link in links)
                or any(count>1 for count in Counter(links).values())):
            raise ValueError('Preparação ou sorteio de vínculos inválido')
        humans=len(founders)+sum(LINK_PEOPLE[link][0] for link in links)
        dogs=sum(LINK_PEOPLE[link][1] for link in links)
        capacity=2*max(4,len(founders))
        if humans>capacity:raise ValueError('Barracas insuficientes')
        consumers=humans+dogs
        lots=[4]*ceil(2*consumers/4)
        people=[];resident_no=0;dog_no=0
        for hero,link in zip(founders,links):
            people.append(cls._person(hero,'hero',hero))
            if LINK_PEOPLE[link][0]:
                resident_no+=1
                kind='child' if link in LINK_IDS[8:10] else 'adult'
                people.append(cls._person(f'R{resident_no:02d}',kind,hero))
            if LINK_PEOPLE[link][1]:
                dog_no+=1
                people.append(cls._person(f'D{dog_no:02d}','dog',hero))
        return cls(founders,links,consumers,humans,dogs,capacity,lots.copy(),lots.copy(),people)

    @staticmethod
    def _person(identifier:str,kind:str,family:str) -> dict:
        return {'id':identifier,'kind':kind,'family':family,'hungry':False,
                'thirsty':False,'streak':0,'wounds':0,'alert':kind=='dog'}

    @property
    def consumers(self) -> int:
        return self.humans+self.dogs

    @property
    def night_segments(self) -> int:
        return max(0,self.clock-8)

    def spend_segments(self,amount:int) -> None:
        if amount<0 or self.clock+amount>10:
            raise ValueError('Relógio diário excedido')
        self.clock+=amount

    def raise_pressure(self,amount:int) -> None:
        if amount<0:raise ValueError('Pressão negativa')
        old=self.pressure
        self.pressure=min(3,self.pressure+amount)
        if old<3 and self.pressure==3:self.pending_sieges.append('Pressão')

    def queue_siege(self,trigger:str) -> None:
        if not trigger:raise ValueError('Gatilho vazio')
        self.pending_sieges.append(trigger)

    def plan_guards(self,heroes:list[str]) -> None:
        if (len(heroes)>3 or len(set(heroes))!=len(heroes)
                or any(hero not in self.founders for hero in heroes)):
            raise ValueError('Vigias inválidos')
        self.planned_guards=list(heroes)

    def resolve_siege(self,strength:int,guards:list[str],rolls:list[int],ammo:int,
                      damage_targets:list[str]) -> dict:
        if (not self.pending_sieges or self.siege_day==self.day or strength<0
                or guards!=self.planned_guards or len(rolls)!=len(guards)
                or any(not 1<=die<=6 for die in rolls)
                or not 0<=ammo<=min(2,self.ammo)):
            raise ValueError('Cerco não pode ser resolvido nesta noite')
        defense=(2 if 'Portão' in self.structures else 0)
        defense+=int('Torre' in self.structures)
        defense+=int(any(person['kind']=='dog' and person['alert'] for person in self.people))
        defense+=sum(die>=4 for die in rolls)+ammo
        gap=max(0,strength-defense)
        target_count=0 if gap==0 else 1 if gap<=2 else 2
        eligible=[name for name in self.structures if name not in ('Barraca','Casa simples')]
        if (len(damage_targets)!=min(target_count,len(eligible))
                or len(set(damage_targets))!=len(damage_targets)
                or any(name not in eligible for name in damage_targets)):
            raise ValueError('Escolha de estruturas danificadas inválida')
        self.ammo-=ammo
        for name in damage_targets:self.structures.remove(name)
        food_lost=0;water_lost=0
        if gap:
            food_lost=self._take(self.food,4)
            food_lost+=self._take(self.meat,4-food_lost)
            if gap>=3:
                water_lost=self._take(self.water,4)
                self.morale=max(0,self.morale-1)
            self.health=max(0,self.health-(target_count-len(damage_targets)))
        trigger=self.pending_sieges.pop(0)
        if trigger=='Pressão':self.pressure=1
        self.siege_day=self.day
        return {'trigger':trigger,'strength':strength,'defense':defense,'gap':gap,
                'food_lost':food_lost,'water_lost':water_lost,
                'damaged':damage_targets.copy(),'health':self.health,'morale':self.morale}

    @staticmethod
    def _take(lots:list[int],amount:int) -> int:
        taken=0
        while amount and lots:
            portion=min(lots[0],amount)
            lots[0]-=portion;amount-=portion;taken+=portion
            if lots[0]==0:lots.pop(0)
        return taken

    def meal(self,food_priority:list[str] | None=None,
             water_priority:list[str] | None=None) -> dict:
        """Resolve por pessoa; prioridades expressam a escolha do grupo na escassez."""
        if self.meal_day==self.day:
            raise ValueError('Refeição do dia já resolvida')
        ids=[person['id'] for person in self.people]
        food_priority=ids.copy() if food_priority is None else food_priority
        water_priority=ids.copy() if water_priority is None else water_priority
        if (len(set(ids))!=len(ids) or len(food_priority)!=len(ids)
                or len(water_priority)!=len(ids)
                or set(food_priority)!=set(ids) or set(water_priority)!=set(ids)
                or len(set(food_priority))!=len(ids) or len(set(water_priority))!=len(ids)):
            raise ValueError('Prioridade deve conter cada consumidor uma vez')
        fed=set();watered=set();meat_used=0;food_used=0;water_used=0
        for identifier in food_priority:
            meat_portion=self._take(self.meat,1)
            food_portion=0 if meat_portion else self._take(self.food,1)
            meat_used+=meat_portion;food_used+=food_portion
            if meat_portion or food_portion:fed.add(identifier)
        for identifier in water_priority:
            received=self._take(self.water,1)
            water_used+=received
            if received:watered.add(identifier)
        expired=sum(self.meat)
        self.meat.clear()
        for person in self.people:
            identifier=person['id']
            person['hungry']=identifier not in fed
            person['thirsty']=identifier not in watered
            deprived=person['hungry'] or person['thirsty']
            person['streak']=person['streak']+1 if deprived else 0
            if person['kind']=='dog':person['alert']=not deprived
            elif person['streak']>=2:
                person['wounds']=min(3,person['wounds']+1)
        if sum(person['kind']!='dog' and person['streak']>=3
               for person in self.people)>=ceil(self.humans/4):
            self.health=0
        self.meal_day=self.day
        return {'consumers':self.consumers,'meat_used':meat_used,'food_used':food_used,
                'water_used':water_used,'food_missing':self.consumers-len(fed),
                'water_missing':self.consumers-len(watered),'meat_expired':expired,
                'hungry':[p['id'] for p in self.people if p['hungry']],
                'thirsty':[p['id'] for p in self.people if p['thirsty']]}

    def receive_part(self,name:str) -> None:
        if name not in {stage['part'] for stage in STAGES.values()} or name in self.parts:
            raise ValueError('Peça desconhecida ou duplicada')
        self.parts[name]=self.day

    def reserve(self,stage:str) -> None:
        if (stage not in STAGES or stage in self.reserved or self.filter_active
                or STAGES[stage]['part'] not in self.parts
                or self.parts[STAGES[stage]['part']]>=self.day
                or self.materials<STAGES[stage]['materials']):
            raise ValueError('Etapa não pode ser reservada hoje')
        self.materials-=STAGES[stage]['materials']
        self.reserved.append(stage)

    def work(self,units:int) -> None:
        if units<1 or self.works_today+units>2:
            raise ValueError('Limite de dois trabalhos diários')
        expected=self.stage;progress=self.stage_work
        for _ in range(units):
            if expected not in self.reserved or expected=='done':
                raise ValueError('Próxima etapa não reservada')
            progress+=1
            if progress==STAGES[expected]['work']:
                progress=0
                expected={'A':'B','B':'C','C':'done'}[expected]
        for _ in range(units):
            self.stage_work+=1;self.works_today+=1
            if self.stage_work==STAGES[self.stage]['work']:
                self.stage_work=0
                if self.stage=='C':
                    self.filter_active=True
                    self.water.extend(self._lots(2*self.initial_consumers))
                else:self.stage='B' if self.stage=='A' else 'C'

    @staticmethod
    def _lots(amount:int) -> list[int]:
        return [4]*(amount//4)+([amount%4] if amount%4 else [])

    def next_day(self) -> None:
        if self.day>=5:raise ValueError('Prazo encerrado')
        if self.meal_day!=self.day:raise ValueError('Refeição diária pendente')
        self.day+=1;self.clock=0;self.works_today=0
        if self.filter_active:
            self.water.extend(self._lots(self.initial_consumers))

    def save(self,path:Path) -> None:
        path.write_text(json.dumps({'schema':1,'state':asdict(self)},ensure_ascii=False,indent=2)+'\n',
                        encoding='utf-8')

    @classmethod
    def load(cls,path:Path) -> 'Cistern02':
        payload=json.loads(path.read_text(encoding='utf-8'))
        if payload.get('schema')!=1:raise ValueError('Esquema inválido')
        return cls(**payload['state'])
