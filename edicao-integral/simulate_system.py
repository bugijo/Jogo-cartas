"""Ensaio integrado reproduzível do subconjunto implementado.

Não modela combate tático, cartas/eventos, missão ou vitória. Não é playtest.
"""
import argparse
import json
from collections import Counter
from system import World, HEROES


def replay(seed: int, hero_count: int, rescue: bool) -> dict:
    heroes=list(HEROES)[:hero_count]
    initial={'food':min(12,hero_count*2),'water':min(12,hero_count*2),
             'wood':2,'scrap':2,'ammo':1}
    # O estoque inicial é cenário de ensaio, não preparação canônica.
    world=World.new(seed,heroes,initial)
    if rescue and world.residents<world.beds:
        world.recruit('EXP-NPC-05')
        world.assign('EXP-NPC-05','farming')
    if world.start_project('garden'):
        world.work_project('garden',2)
    exp_heroes=heroes[:min(2,hero_count)]
    world.open_expedition('mercado',exp_heroes,'EXP-LOC-02')
    outcomes=[]
    for day in range(5):
        if 'mercado' in world.expeditions:
            status=world.advance_expedition('mercado')
            if status=='arrived':
                world.search('mercado')
                world.begin_return('mercado')
        outcomes.append(world.end_day())
    world.validate()
    return {'seed':seed,'heroes':hero_count,'rescue':rescue,
            'missing_food':sum(d['missing']['food'] for d in outcomes),
            'missing_water':sum(d['missing']['water'] for d in outcomes),
            'crises':[d['crisis'] for d in outcomes if d['crisis']],
            'end_stock':dict(world.stock),'day5':world.day,
            'expeditions_unreturned':list(world.expeditions)}


def aggregate(start_seed: int, seeds: int) -> dict:
    results=[]
    for heroes in range(2,7):
        for offset in range(seeds):
            results.append(replay(start_seed+offset,heroes,rescue=bool(offset%2)))
    by_size={}
    for size in range(2,7):
        subset=[r for r in results if r['heroes']==size]
        by_size[str(size)]={'runs':len(subset),
                           'food_shortage_runs':sum(r['missing_food']>0 for r in subset),
                           'water_shortage_runs':sum(r['missing_water']>0 for r in subset),
                           'food_shortage_total':sum(r['missing_food'] for r in subset),
                           'water_shortage_total':sum(r['missing_water'] for r in subset),
                           'crises':dict(Counter(c for r in subset for c in r['crises']))}
    return {'start_seed':start_seed,'seeds_per_group':seeds,'total_replays':len(results),
            'scope':'cinco dias de economia e uma busca; sem campanha, combate tático, vitória ou duração de mesa',
            'by_hero_count':by_size}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=20261023)
    parser.add_argument('--seeds',type=int,default=100)
    args=parser.parse_args()
    print(json.dumps(aggregate(args.seed,args.seeds),ensure_ascii=False,indent=2))
