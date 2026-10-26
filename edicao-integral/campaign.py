"""Cartas tipadas e cenário de integração; o capítulo canônico permanece em CAMPAIGN.md."""
import hashlib
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

from system import DATA, HEROES, World
from tactics import TacticalGame

CATALOG=json.loads((Path(__file__).parent/'data/cycle_cards.json').read_text(encoding='utf-8'))
CARDS={card['id']:card for card in CATALOG['cards']}


def apply_event(world:World,expedition_id:str,card_id:str,choice_id:str,hero_id:str) -> dict:
    if card_id not in CARDS or CARDS[card_id]['family']!='event':
        raise ValueError('Evento inexistente')
    if expedition_id not in world.expeditions or world.expeditions[expedition_id].remaining!=0:
        raise ValueError('Equipe fora do local')
    if hero_id not in world.expeditions[expedition_id].heroes:
        raise ValueError('Herói fora da equipe')
    key=card_id
    if key in world.decisions:
        raise ValueError('Escolha já resolvida')
    choice=next((c for c in CARDS[card_id]['choices'] if c['id']==choice_id),None)
    if choice is None:
        raise ValueError('Escolha inválida')
    req=choice['requires']
    if req and HEROES[hero_id]['attributes'][req['attribute']]<req['minimum']:
        raise ValueError('Requisito não atendido')
    exp=world.expeditions[expedition_id]
    cargo={}
    for effect in choice['effects']:
        if effect['kind']=='cargo':
            maximum=6*len(exp.heroes) if not exp.vehicle_id else DATA['vehicles'][0]['cargo_capacity']
            if sum(exp.cargo.values())+effect['amount']>maximum:
                raise ValueError('Carga cheia')
            cargo[effect['resource']]=cargo.get(effect['resource'],0)+effect['amount']
        elif effect['kind']!='clues':
            raise ValueError('Efeito desconhecido')
    for resource,amount in cargo.items():
        exp.cargo[resource]=exp.cargo.get(resource,0)+amount
    for effect in choice['effects']:
        if effect['kind']=='clues':
            world.clues+=effect['amount']
    world.decisions[key]=choice_id
    world.log.append({'day':world.day,'card':card_id,'choice':choice_id,'hero':hero_id})
    return {'cargo':cargo,'clues':world.clues}


def _digest(world:World) -> str:
    data=json.dumps(asdict(world),ensure_ascii=False,sort_keys=True)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def play_market_day(seed:int,strategy:str='balanced',team_size:int=2) -> dict:
    if strategy not in ('conservative','explorer','builder','fighter','balanced'):
        raise ValueError('Estratégia desconhecida')
    if not 2<=team_size<=6:
        raise ValueError('Equipe fora do escopo')
    phases=['preparation']
    heroes=list(HEROES)[:team_size]
    world=World.new(seed,heroes,{'food':6,'water':6,'wood':2,'scrap':2,'ammo':1})
    world.give_item(heroes[1],'crowbar','EXP-EQU-002','hand')
    world.recruit('EXP-NPC-05')
    if 'EXP-NPC-05' in world.npcs:
        world.assign('EXP-NPC-05','farming')
    garden_built=False
    if strategy=='builder' and world.start_project('garden'):
        garden_built=world.work_project('garden',2)
    world.open_expedition('market',heroes,'EXP-LOC-02')
    phases.append('travel')
    world.advance_expedition('market')
    game=TacticalGame.start(world,'market','market_intro')
    phases.append('exploration')
    choice='inspect' if strategy in ('explorer','fighter','balanced') else 'ignore'
    event=apply_event(world,'market','EXP-EVT-001',choice,heroes[0])
    phases.append('event')
    enemy=game.spawn('slow',zone=1)
    killed=0
    initial_health=world.heroes[heroes[1]]['health']
    for _ in range(4):
        if enemy not in game.state['enemies'] or world.heroes[heroes[1]]['health']<1:
            break
        if strategy=='conservative' and world.heroes[heroes[1]]['health']<initial_health:
            break
        while (world.heroes[heroes[1]]['actions'] and enemy in game.state['enemies']
               and world.gear[heroes[1]]['crowbar']['durability']>0):
            result=game.attack(heroes[1],'crowbar',enemy)
            if result['enemy_health']==0:
                killed=1
        if enemy in game.state['enemies'] and world.gear[heroes[1]]['crowbar']['durability']>0:
            game.activate()
        elif enemy in game.state['enemies']:
            break
    phases.append('combat')
    loot={}
    searches_used=0
    if killed and world.gear[heroes[1]]['crowbar']['durability']>0:
        if world.heroes[heroes[1]]['actions']<1:
            game.activate()
        game.open_door(heroes[1],1,5)
        if world.heroes[heroes[1]]['actions']<1:
            game.activate()
        game.move(heroes[1],5)
        before_search=world.searches['EXP-LOC-02']
        if world.heroes[heroes[1]]['actions']<1:
            game.activate()
        loot=game.search(heroes[1])
        if strategy=='explorer':
            if world.heroes[heroes[1]]['actions']<1:
                game.activate()
            extra=game.search(heroes[1])
            for resource,amount in extra.items():
                loot[resource]=loot.get(resource,0)+amount
        searches_used=before_search-world.searches['EXP-LOC-02']
        if world.heroes[heroes[1]]['actions']<1:
            game.activate()
        game.move(heroes[1],1)
    game.finish(retreat=bool(game.state['enemies']) or not searches_used)
    phases.append('loot')
    world.begin_return('market')
    world.advance_expedition('market')
    phases.append('return')
    day=world.end_day()
    mission=CARDS['EXP-MIS-001']['requirements']
    complete=(killed>=mission['enemy_defeated_min']
              and searches_used>=mission['searches_min']
              and all(h['health']>0 for h in world.heroes.values())
              and not any(day['missing'].values()))
    if complete:
        world.camp_xp+=CARDS['EXP-MIS-001']['reward']['camp_xp']
    outcome='mission_complete' if complete else 'defeat' if any(h['health']==0 for h in world.heroes.values()) else 'retreated'
    phases.append('camp')
    before=_digest(world)
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'save.json';world.save(path)
        restored=World.load(path)
        after=_digest(restored)
    phases.append('save_restore')
    return {'seed':seed,'strategy':strategy,'team_size':team_size,
            'garden_built':garden_built,'phases':phases,'outcome':outcome,
            'day':world.day,'searches_used':searches_used,'enemies_defeated':killed,
            'event_choice':choice,'event_result':event,'loot':loot,
            'production':day['produced'],'missing':day['missing'],
            'stock':day['stock'],'camp_xp':world.camp_xp,
            'state_before_save':before,'state_after_load':after}
