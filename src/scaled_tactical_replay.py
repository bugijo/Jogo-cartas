"""Trajetória tática fixa H=3..6, com três expedicionários e cinco dias.

Não testa toda ordem de monte: usa rolagens/ordem favoráveis declaradas.
"""
import json
from collections import Counter
from math import ceil
from pathlib import Path

from review_five_days import Replay

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'content/catalog.json').read_text())
COMBAT_DIE=3
TRAVEL_DRAWS={
    'Mercado':['ZC-VIA-0001','ZC-VIA-0011'],
    'Oficina':['ZC-VIA-0008','ZC-VIA-0012'],
    'Estação':['ZC-VIA-0006','ZC-VIA-0009'],
}
EXTRA_NIGHT_TRAVEL='ZC-VIA-0002'  # perde 1 porção de água levada; sem fadiga adicional da carta
LINK_DECK=Counter({'Sozinho':4,'Parceiro':4,'Filho':2,'Cachorro':1,'Parceiro e cachorro':1})


def rounds_market(h):
    return [
      [('Lia',[('move',2),('move',3),('open',3,7)]),('Ivo',[('open',1,5),('move',5),('move',9)]),('Caio',[('move',5),('search',),('move',9)])],
      [('Lia',[('move',7),('take','Conserva',7,2,1),('take','Conserva',7,2,1)]),('Ivo',[('open',9,13),('move',13),('open',13,14)]),('Caio',[('move',10),('move',11),('move',12)])],
      [('Lia',[('move',11),('move',12),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)]),('Caio',[('attack',)] if h>=5 else [])],
      [('Caio',[('attack',)]),('Lia',[('attack',),('move',11),('move',7)]),('Ivo',[('move',11),('move',7),('floor',)])],
      [('Lia',[('move',3),('move',2),('move',1)]),('Ivo',[('move',3),('move',2),('move',1)]),('Caio',[('move',11),('move',7),('move',3)])],
      [('Caio',[('move',2),('move',1)])]]


def rounds_market_2():
    return [
      [('Lia',[('move',2),('move',3),('open',3,7)]),('Ivo',[('open',1,5),('move',5),('move',9)])],
      [('Lia',[('move',7),('take','Conserva',7,2,1),('take','Conserva',7,2,1)]),('Ivo',[('open',9,13),('move',13),('open',13,14)])],
      [('Lia',[('move',11),('move',12),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)])],
      [('Lia',[('attack',),('move',11),('move',7)]),('Ivo',[('move',11),('move',7),('floor',)])],
      [('Lia',[('move',3),('move',2),('move',1)]),('Ivo',[('move',3),('move',2),('move',1)])]]


def rounds_workshop(rescue):
    caio=[('move',7),('contact',),('move',3)] if rescue else [('move',7),('move',3),('move',2)]
    return [
      [('Lia',[('move',2),('move',3)]),('Ivo',[('open',1,5),('move',5),('move',9)]),('Caio',[('move',2),('move',3)])],
      [('Lia',[('open',3,7),('move',7)]),('Ivo',[('open',9,13),('move',13),('open',13,14)]),('Caio',[('move',7)])],
      [('Lia',[('open',7,8),('move',8),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)]),('Caio',[('move',8),('attack',)])],
      [('Caio',[('attack',)]),('Lia',[('move',7),('take','Conexões',7,1,1),('take','Bateria',7,1,1)]),('Ivo',[('attack',),('move',11),('move',7)])],
      [('Lia',[('take','Conserva',7,2,1),('move',3),('move',2)]),('Ivo',[('floor',),('move',3),('move',2)]),('Caio',caio)],
      [('Lia',[('move',1)]),('Ivo',[('move',1)]),('Caio',[('move',2),('move',1)] if rescue else [('move',1)])]]


def rounds_workshop_2():
    return [
      [('Lia',[('move',2),('move',3)]),('Ivo',[('open',1,5),('move',5),('move',9)])],
      [('Lia',[('open',3,7),('move',7)]),('Ivo',[('open',9,13),('move',13),('open',13,14)])],
      [('Lia',[('open',7,8),('move',8),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)])],
      [('Lia',[('move',7),('take','Conexões',7,1,1),('take','Bateria',7,1,1)]),('Ivo',[('attack',),('move',11),('move',7)])],
      [('Lia',[('take','Conserva',7,2,1),('contact',),('move',3)]),('Ivo',[('floor',),('move',3),('move',2)])],
      [('Lia',[('move',2),('move',1)]),('Ivo',[('move',1)])]]


def rounds_station():
    return [
      [('Lia',[('move',2),('move',3),('open',3,7)]),('Ivo',[('open',1,5),('move',5),('move',9)]),('Caio',[('move',2),('move',3)])],
      [('Lia',[('move',7),('pump',)]),('Ivo',[('move',10),('move',11),('move',15)]),('Caio',[('move',7),('open',7,8)])],
      [('Ivo',[('attack',),('attack',),('attack',)]),('Lia',[('move',11),('move',15),('move',14)]),('Caio',[('move',8),('attack',),('attack',)])],
      [('Caio',[('attack',),('move',7),('move',3)]),('Ivo',[('attack',),('move',14),('take','Membrana',14,1,1)]),('Lia',[('move',15),('move',11)])],
      [('Lia',[('move',7),('move',3),('move',2)]),('Ivo',[('take','Água',14,2,1),('move',15),('move',11)]),('Caio',[('move',2),('move',1)])],
      [('Lia',[('move',1)]),('Ivo',[('attack',),('move',7),('attack',)])],
      [('Ivo',[('move',3),('move',2),('move',1)])]]


def rounds_station_2():
    return [[(hero,actions) for hero,actions in row if hero!='Caio'] for row in rounds_station()]


class SizedReplay(Replay):
    def __init__(self,h):
        super().__init__()
        # Permutação válida das nove cartas HOR; lotes maiores aparecem ao fim
        # de uma visita. A ordem favorável é explícita e não estima probabilidade.
        self.horda=['Arrastar','Arrastar','Aglomerado','Arrastar','Arrastar','Aglomerado','Corrida','Corrida','Peso morto']
        assert Counter(self.horda)==Counter(c['name'] for c in CAT['cards'] if c['family']=='HOR')
        self.h=h
        if h>=3:self.health['Caio']=3
        self.rescues=[]
        self.searches=[]
    def start(self,name):
        super().start(name)
        if self.h>=3:
            self.pos['Caio']=1
            self.bags['Caio']=[('Pé de cabra',1)]
        for _ in range(ceil(self.h/2)-1):self.spawn('Errante',16)
    def act(self,name,action):
        if action[0]=='contact':
            assert self.m['name']=='Oficina' and self.pos[name]==7
            self.cost(name,1)
            self.rescues.append('Bia')
            return
        if action[0]=='search':
            assert self.m['name']=='Mercado' and self.pos[name]==5 and not self.searches
            self.cost(name,1)
            self.gain(name,[('Medicamento',1)])
            self.searches.append('ZC-SAQ-0005')
            return
        if action[0]=='attack' and name=='Caio':
            target=next((e for e in self.enemies if e['z']==self.pos[name]),None)
            assert target and target['kind']=='Errante'
            assert COMBAT_DIE+2>=5  # Caio: Corpo 2; rolagem registrada 3
        return super().act(name,action)
    def end(self):
        before=len(self.draws)
        super().end()
        if len(self.draws)>before and self.draws[-1]=='Aglomerado':
            for _ in range(ceil(self.h/2)-1):self.spawn('Errante',16)
            self.logs[-1]['enemies']=[e.copy() for e in self.enemies]


def play_day(r,name,rounds,expected):
    r.start(name)
    start_log=len(r.logs)
    for instructions in rounds:
        r.begin()
        for hero,actions in instructions:
            for action in actions:
                if action[0]=='attack' and not any(e['z']==r.pos[hero] for e in r.enemies):
                    # Ação condicional planejada: se não há alvo, não gasta PA.
                    continue
                r.act(hero,action)
        r.end()
    assert all(z==1 for z in r.pos.values()),(name,r.pos)
    assert all(e['z']!=1 for e in r.enemies),(name,r.enemies)
    r.clock+=1  # retorno curto
    assert r.clock<=10,(name,r.clock)
    night_segments=sum(segment in (9,10) for segment in range(1,r.clock+1))
    assert night_segments==(1 if name=='Estação' else 0)
    delivered=Counter(item for bag in r.bags.values() for item,_ in bag if item!='Pé de cabra')
    assert delivered==expected,(name,delivered,expected)
    assert all(0<value<=3 for value in r.health.values()),r.health
    peak=max((len(frame['enemies']) for frame in r.logs[start_log:]),default=0)
    assert peak<=24,(name,peak)
    return dict(destination=name,segments=r.clock,rounds=r.round,delivered=dict(delivered),
                health=dict(r.health),rescue=list(r.rescues),
                travel_cards=TRAVEL_DRAWS[name],
                extra_night_travel=EXTRA_NIGHT_TRAVEL if night_segments else None,
                night_fatigue_per_hero=night_segments,
                horde_draws=r.draws.copy(),peak_enemies=peak,round_log=r.logs[start_log:])


def run(h, accept_bia=None):
    assert h in (2,3,4,5,6)
    travel=[cid for leg in TRAVEL_DRAWS.values() for cid in leg]
    assert len(travel)==len(set(travel))==6
    assert set(travel)<={c['id'] for c in CAT['cards'] if c['family']=='VIA'}
    assert EXTRA_NIGHT_TRAVEL not in travel and EXTRA_NIGHT_TRAVEL in {c['id'] for c in CAT['cards'] if c['family']=='VIA'}
    # Fundadores Lia, Ivo, Caio; restantes ficam no abrigo nos dias de expedição.
    # Vínculos legais sem reposição: C=5 para H2–5 e C=8 para H6.
    links={2:['Parceiro','Parceiro e cachorro'],
           3:['Parceiro','Parceiro','Sozinho'],4:['Parceiro','Sozinho','Sozinho','Sozinho'],
           5:['Sozinho']*4+['Parceiro'],6:['Sozinho']*4+['Cachorro','Parceiro']}[h]
    assert all(count<=LINK_DECK[kind] for kind,count in Counter(links).items()),links
    consumers=h+sum(x in ('Parceiro','Parceiro e cachorro') for x in links)+sum(x in ('Cachorro','Parceiro e cachorro') for x in links)
    # Para H6 quatro Sozinho, um Cachorro e um Parceiro: C=8 e lote2.
    assert ceil(consumers/4)==2
    people=h+sum(x in ('Parceiro','Parceiro e cachorro') for x in links)
    dogs=sum(x in ('Cachorro','Parceiro e cachorro') for x in links)
    cap=2*max(4,h)
    assert people<=cap
    rescued=(h<6) if accept_bia is None else accept_bia
    r=SizedReplay(h)
    market=play_day(r,'Mercado',rounds_market_2() if h==2 else rounds_market(h),
                    Counter({'Conserva':4,'Água':2} if h==2 else {'Conserva':4,'Água':2,'Medicamento':1}))
    workshop_rounds=rounds_workshop_2() if h==2 else rounds_workshop(rescued)
    if h==2 and not rescued:
        workshop_rounds=[[(name,[a for a in actions if a[0]!='contact']) for name,actions in row] for row in workshop_rounds]
    workshop=play_day(r,'Oficina',workshop_rounds,Counter({'Conexões':1,'Bateria':1,'Conserva':2,'Água':2}))
    station=play_day(r,'Estação',rounds_station_2() if h==2 else rounds_station(),Counter({'Bomba':1,'Membrana':1,'Água':2}))
    assert (r.rescues==['Bia'])==rescued
    active=['Lia','Ivo']+(['Caio'] if h>=3 else [])
    xp={name:6 for name in active}  # 1 saída normal +1 objetivo principal por dia, três visitas
    progression={}
    for name in active:
        hero=next(x for x in CAT['heroes'] if x['name']==name)
        progression[name]={'3':hero['progression']['3'][0], '6':hero['progression']['6'][1]}
    # Dia 3: cerco fixo Força 4. Dia 5: pressão chega a 3; sorteio fixado em
    # ZC-CER-0001 (Força 4). Vigias são adultos que ficaram no abrigo.
    food=water=4*ceil(2*consumers/4)
    materials=3;ammo=2;medicine=2+len(r.searches);pressure=0;filter_work=0;days=[]
    health=morale=5
    for day in range(1,6):
        event_pressure=int(day in (2,4,5))
        pressure=min(3,pressure+event_pressure)
        siege=None
        if day==1:
            food+=16;water+=8
        elif day==2:
            food+=8;water+=8
            if rescued:people+=1
        elif day==3:
            water+=7  # 8 porções trazidas; Viagem noturna extra custou 1 da carga
        if day==3:
            home_adults=max(0,h-(2 if h==2 else 3))+sum(x in ('Parceiro','Parceiro e cachorro') for x in links)
            dice=[4,2,2][:min(3,home_adults)]
            defense=2+int(dogs>0)+sum(x>=4 for x in dice)
            bullets=max(0,4-defense)
            assert bullets<=ammo and bullets<=2
            ammo-=bullets;defense+=bullets
            siege=dict(kind='missão',force=4,defense=defense,dice=dice,bullets=bullets)
            assert defense>=4
        if day==5:
            assert pressure==3
            # Dois adultos trabalham no filtro; até três outros vigiam.
            eligible=people-2
            dice=[4,4,2][:min(3,eligible)]
            defense=2+int(dogs>0)+sum(x>=4 for x in dice)
            assert defense>=4
            siege=dict(kind='pressão ZC-CER-0001',force=4,defense=defense,dice=dice,bullets=0)
            pressure=1
        if day==4:
            assert materials>=3
            materials-=3;filter_work+=2
        if day==5:
            filter_work+=2
            assert filter_work==4
            water+=2*consumers
        c_today=people+dogs
        food-=c_today;water-=c_today
        assert food>=0 and water>=0,(h,day,food,water)
        days.append(dict(day=day,destination={1:'Mercado',2:'Oficina',3:'Estação'}.get(day),
                         people=people,dogs=dogs,food=food,water=water,materials=materials,
                         medicine=medicine,ammo=ammo,
                         bia_intention=('fora' if not rescued or day==1 else 'envelope lacrado — 1ª noite' if day==2
                                        else 'Solidário revelado após 2ª noite' if day==3 else 'apta após observação'),
                         expedition_night_fatigue=(1 if day==3 else 0),
                         fatigue_removed_next_dawn=(1 if day==4 else 0),
                         pressure=pressure,filter_work=filter_work,filter_active=filter_work==4,
                         siege=siege,health=health,morale=morale))
    assert rescued is False or people<=cap
    return dict(heroes=h,founders=(['Lia','Ivo'] if h==2 else ['Lia','Ivo','Caio']+['Mara','Nara','Bento'][:h-3]),
                links=links,consumers_initial=consumers,capacity=cap,decision_bia='acolher' if rescued else 'deixar no destino',
                rescue_intention='ZC-INT-0001 Solidário' if rescued else None,
                searches=list(r.searches),tactical=[market,workshop,station],days=days,result='vitória nesta trajetória fixa',
                hero_xp=xp,progression_choices=progression,final_wounds={name:3-hp for name,hp in r.health.items()},
                limitations=['Rolagens de combate 3 e cerco favorável pré-fixados; não mede probabilidade.',
                             'Viagem: seis cartas legalmente distintas e decisões de não aceitar trocas; outros arranjos não testados.',
                             'Busca: uma carta Mercado para H3–6; os demais resultados de Busca não foram testados.',
                             'Uma trajetória não valida equilíbrio nem todos os ramos da campanha.'])


if __name__=='__main__':
    results=[]
    for h in range(2,7):
        try:results.append(run(h))
        except Exception as exc:results.append(dict(heroes=h,result='BLOCKED',evidence=repr(exc)))
    path=ROOT/'kit-final-prova/auditoria/ROTEIROS_TATICOS_H2_H6.json'
    path.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print([(x['heroes'],x['result'],x.get('evidence')) for x in results])
