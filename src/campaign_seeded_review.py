"""Replay de fases com sementes; não substitui um replay tático zona a zona.

Usa exclusivamente valores das regras 0.2 e do catálogo. Toda abstração espacial é
marcada no resultado, portanto não emite certificado de campanha validada.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from itertools import combinations
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT/'content/catalog.json').read_text())
HEROES = [h for h in CAT['heroes'] if h['initial']]
INTENTIONS = [c for c in CAT['cards'] if c['family'] == 'INT']
CERCO = [c for c in CAT['cards'] if c['family'] == 'CER']
HORDA = [c for c in CAT['cards'] if c['family'] == 'HOR']
LINKS = [('Sozinho', 0, 0)]*4 + [('Parceiro', 1, 0)]*4 + [('Filho', 1, 0)]*2 + [('Cachorro', 0, 1), ('Parceiro e cachorro', 1, 1)]


def set_up(participants: int, seed: int, *, extreme: str | None = None):
    h = max(2, participants)
    rng = random.Random(seed)
    links = LINKS.copy()
    rng.shuffle(links)
    if extreme == 'max_consumption':
        links = sorted(LINKS, key=lambda row: row[1]+row[2], reverse=True)
    elif extreme == 'min_consumption':
        links = sorted(LINKS, key=lambda row: row[1]+row[2])
    chosen = links[:h]
    humans = h+sum(x[1] for x in chosen)
    dogs = sum(x[2] for x in chosen)
    capacity = 2*max(4,h)
    c = humans+dogs
    assert humans <= capacity
    return dict(participants=participants, heroes=h, founders=[x['name'] for x in HEROES[:h]],
                links=[x[0] for x in chosen], humans=humans, dogs=dogs, consumers=c,
                tents=max(4,h), capacity=capacity, lot_cards=ceil(c/4),
                initial_full_cards=ceil(2*c/4), initial_errantes=ceil(h/2))


def check_all_setups():
    table=[]
    for participants in range(1,7):
        h=max(2,participants)
        rows=[]
        for select in combinations(range(12),h):
            chosen=[LINKS[i] for i in select]
            humans=h+sum(x[1] for x in chosen)
            dogs=sum(x[2] for x in chosen)
            rows.append((humans,dogs,humans+dogs))
        table.append(dict(participants=participants, heroes=h, combinations=len(rows),
                          capacity=2*max(4,h), all_fit=all(x[0] <= 2*max(4,h) for x in rows),
                          consumers_min=min(x[2] for x in rows),consumers_max=max(x[2] for x in rows)))
    return table


def phase_replay(h: int, seed: int, profile: str):
    """Executes all five phases with cargo/stock/work/security/rescue ledgers.

    Spatial movement and every action's PA are not modeled; `tactical_verified` stays False.
    """
    assert profile in ('favoravel','dificil','limite')
    rng=random.Random(seed)
    setup=set_up(h,seed,extreme='max_consumption' if profile=='limite' else None)
    c=setup['consumers']; lot=setup['lot_cards']; cap=setup['capacity']
    stock={'food':4*setup['initial_full_cards'],'water':4*setup['initial_full_cards'],
           'materials':3,'ammo':2}
    state={'people':setup['humans'],'dogs':setup['dogs'],'capacity':cap,'health':5,'morale':5,
           'pressure':0,'portao':True,'filter_work':0,'filter_active':False,'filter_reserved':False,'parts':set(),
           'pending':[],'groups':[],'wounds':Counter(), 'stock':stock,
           'structures':{'Portão','Cozinha','Depósito'},'incapacitated':False}
    intentions=INTENTIONS.copy();rng.shuffle(intentions)
    sieges=CERCO.copy();rng.shuffle(sieges)
    siege_i=0;intent_i=0;logs=[];exhaustion=[]

    def take_intent(day,size,name):
        nonlocal intent_i
        card=intentions[intent_i];intent_i+=1
        state['people']+=size
        state['groups'].append(dict(name=name,size=size,day=day,intention=card['name'],
                                    id=card['id'],revealed=False,verified=False))
        return card['id']

    def guard(force,kind,day):
        adults_home=max(0,setup['humans']- (team if day<=3 else 0))
        # Acompanhantes iniciais são adultos, exceto os vínculos Filho.
        children=sum(1 for link in setup['links'] if link=='Filho')
        eligible=max(0,adults_home-children)
        vigils=min(3,eligible if day<=3 else max(0,eligible-2))
        rolls=[rng.randint(1,6) for _ in range(vigils)]
        ammo=min(stock['ammo'],2,max(0,force-(2 if state['portao'] else 0)-int(bool(state['dogs']))-sum(r>=4 for r in rolls)))
        stock['ammo']-=ammo
        defense=(2 if state['portao'] else 0)+int(bool(state['dogs']))+sum(r>=4 for r in rolls)+ammo
        gap=max(0,force-defense)
        damaged=[]
        if gap:
            # O grupo escolhe perdas elegíveis, protegendo o filtro se houver alternativa.
            for name in ('Portão','Depósito','Cozinha','Filtro'):
                if name in state['structures'] and len(damaged)<(2 if gap>=3 else 1):
                    damaged.append(name);state['structures'].remove(name)
            if 'Portão' in damaged:state['portao']=False
            if 'Filtro' in damaged:state['filter_active']=False
            stock['food']=max(0,stock['food']-4)
            if gap>=3:
                stock['water']=max(0,stock['water']-4)
                state['morale']-=1
                state['health']-=max(0,2-len(damaged))
        return dict(kind=kind,force=force,defense=defense,vigils=vigils,rolls=rolls,ammo=ammo,gap=gap,damaged=damaged)

    for day in range(1,6):
        before=dict(stock)
        event_pressure=1 if day in (2,4,5) else 0
        old=state['pressure'];state['pressure']=min(3,old+event_pressure)
        if old<3 and state['pressure']==3:state['pending'].append('Pressão')
        if day==3:state['pending'].append('Missão dia 3')
        dest={1:'Mercado',2:'Oficina',3:'Estação'}.get(day)
        team=0;loads=0;combat=[];rescue=None;clock=0;hordes=[]
        if dest:
            loads={1:3*lot,2:2*lot+2,3:lot+3}[day]
            team=max(2,ceil(loads/3))  # cada Pé de cabra ocupa 1 de 4 cargas
            if team>h:
                exhaustion.append(dict(day=day,item='carga de heróis',needed=loads,available=3*h))
                team=h
            clock={1:7,2:8,3:9}[day]
            # Amostra de confronto com os inimigos iniciais, sem fingir posições no mapa.
            enemies=ceil(h/2)+(1 if day==3 else 0)
            for i in range(enemies):
                die=rng.randint(1,6)
                body=HEROES[i%team]['attributes']['Corpo']
                target=6 if day==3 and i==enemies-1 else 5
                success=(die==6 or (die!=1 and die+body>=target))
                if not success:state['wounds'][HEROES[i%team]['name']]+=1
                combat.append(dict(enemy='Bruto' if target==6 else 'Errante',die=die,body=body,hit=success))
                if state['wounds'][HEROES[i%team]['name']]>=3:
                    state['incapacitated']=True
            # Hordas são auditadas como demanda física; a atuação espacial fica pendente.
            for _ in range(ceil((clock-2)/2)):
                card=rng.choice(HORDA)
                amount=ceil(h/2) if card['name']=='Aglomerado' else 1
                hordes.append(dict(id=card['id'],name=card['name'],tokens=amount))
            needed=enemies+sum(x['tokens'] for x in hordes)
            if needed>24:exhaustion.append(dict(day=day,item='inimigos',needed=needed,available=24))
            if day==1:
                stock['food']+=8*lot;stock['water']+=4*lot
                if profile!='favoravel' and state['people']+2<=cap+2:
                    rescue=take_intent(day,2,'Jana e criança')
            elif day==2:
                state['parts'].update(('Conexões','Bateria'))
                stock['food']+=4*lot;stock['water']+=4*lot
                if profile=='limite' and state['people']+1<=cap+2:
                    rescue=take_intent(day,1,'Bia')
            else:
                state['parts'].update(('Bomba','Membrana'))
                stock['water']+=4*lot
                if profile=='limite' and state['people']+2<=cap+2:
                    rescue=take_intent(day,2,'Vicente e Sol')
        # Uma ameaça por noite, antes dos trabalhos; excedentes ficam pendentes.
        siege=None
        if state['pending']:
            kind=state['pending'].pop(0)
            if kind=='Missão dia 3':force=4
            else:
                card=sieges[siege_i%len(sieges)];siege_i+=1
                force=card['force']
            siege=guard(force,kind,day)
            if kind=='Pressão':state['pressure']=1
        # Peças entregues hoje só são reserváveis amanhã.
        if day==4 and {'Conexões','Bomba','Membrana'}<=state['parts'] and stock['materials']>=3:
            stock['materials']-=3
            state['filter_reserved']=True
        if day in (4,5) and state['filter_reserved']:
            state['filter_work']+=2
            if state['filter_work']==4:
                state['filter_active']=True
                state['structures'].add('Filtro')
                stock['water']+=2*c
        shortage=max(0,state['people']+state['dogs']-stock['food']),max(0,state['people']+state['dogs']-stock['water'])
        stock['food']=max(0,stock['food']-state['people']-state['dogs'])
        stock['water']=max(0,stock['water']-state['people']-state['dogs'])
        if any(shortage):state['health']=max(0,state['health']-1) if day>=2 else state['health']
        for group in state['groups']:
            if not group['revealed'] and day>=group['day']+1:
                group['revealed']=True
                if group['intention'] in ('Oportunista','Infiltrado'):
                    state['people']-=group['size']
                    if group['intention']=='Oportunista':stock['food']=max(0,stock['food']-4)
                    else:
                        old=state['pressure'];state['pressure']=min(3,old+1)
                        if old<3 and state['pressure']==3:state['pending'].append('Pressão')
        if state['people']>cap and any(day>=g['day']+2 and g['revealed'] and g['intention'] not in ('Oportunista','Infiltrado') for g in state['groups']):
            state['health']-=1;state['morale']-=1
        logs.append(dict(day=day,event_pressure=event_pressure,destination=dest,expedition_heroes=team,
                         clock=clock,cargo_needed=loads,cargo_capacity=3*team,initial_enemies=ceil(h/2) if dest else 0,
                         sampled_combat=combat,hordes=hordes,rescue_card=rescue,siege=siege,
                         stock_before=before,stock_after=dict(stock),people=state['people'],dogs=state['dogs'],
                         capacity=cap,shortage=shortage,filter_work=state['filter_work'],
                         filter_active=state['filter_active'],pressure=state['pressure'],pending=list(state['pending']),
                         health=state['health'],morale=state['morale']))
    # Fila de segurança após dia 5. Não há novo trabalho/produção/refeição.
    security=[]
    while state['pending']:
        kind=state['pending'].pop(0)
        card=sieges[siege_i%len(sieges)];siege_i+=1
        security.append(guard(card['force'],kind,5))
    result='plano_de_fases_possivel' if (state['filter_active'] and state['health']>=1 and state['morale']>=1
                 and not any(logs[-1]['shortage']) and not state['incapacitated']) else 'derrota_ou_bloqueio_na_amostra'
    return dict(heroes=h,seed=seed,profile=profile,setup=setup,days=logs,security=security,
                result=result,groups=state['groups'],wounds=dict(state['wounds']),component_exhaustion=exhaustion,
                incapacitated=state['incapacitated'],
                tactical_verified=False,limitations=['Combate é amostra de dados/valores; falta movimento, PA e IA zona a zona.',
                                                   'Viagem, busca, cerco e resgate têm efeitos de cartas não completamente executados.',
                                                   'Resultado é cenário de fases, não partida integral certificada.'])


def run_matrix():
    rows=[]
    for h in range(2,7):
        for profile,offset in (('favoravel',101),('dificil',202),('limite',303)):
            rows.append(phase_replay(h,h*1000+offset,profile))
    return dict(setups=check_all_setups(),runs=rows,summary=Counter(x['result'] for x in rows),
                full_tactical_replays=0,campaign_validated=False)


if __name__=='__main__':
    out=run_matrix();target=ROOT/'kit-final-prova/auditoria/CAMPANHA_SEMENTES.json'
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print([(x['heroes'],x['profile'],x['result']) for x in out['runs']])
