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
        return cls(founders,links,consumers,humans,dogs,capacity,lots.copy(),lots.copy())

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

    @staticmethod
    def _take(lots:list[int],amount:int) -> int:
        taken=0
        while amount and lots:
            portion=min(lots[0],amount)
            lots[0]-=portion;amount-=portion;taken+=portion
            if lots[0]==0:lots.pop(0)
        return taken

    def meal(self) -> dict:
        """Consumo agregado; destinatários da escassez ainda requerem portabilidade."""
        if self.meal_day==self.day:
            raise ValueError('Refeição do dia já resolvida')
        need=self.consumers
        meat_used=self._take(self.meat,need)
        food_used=self._take(self.food,need-meat_used)
        water_used=self._take(self.water,need)
        expired=sum(self.meat)
        self.meat.clear()
        self.meal_day=self.day
        return {'consumers':need,'meat_used':meat_used,'food_used':food_used,
                'water_used':water_used,'food_missing':need-meat_used-food_used,
                'water_missing':need-water_used,'meat_expired':expired}

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
