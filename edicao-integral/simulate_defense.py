"""Ensaio isolado da defesa final. NÃO simula a campanha ou aquisição de equipamento."""
import argparse
import json
from collections import Counter
from pathlib import Path

from arc2 import Arc2
from system import HEROES, World


def replay(seed: int, team_size: int) -> dict:
    heroes=list(HEROES)[:team_size]
    world=World.new(seed,heroes,{'food':team_size*2,'water':team_size*2})
    # Pré-condições injetadas: este ensaio NÃO demonstra que foram obtidas legalmente.
    world.flags.update(cistern_complete=True,radio_code=True,
                       access_card=True,military_access=True)
    world.special_stock.append('transmitter')
    for index,hero in enumerate(heroes):
        world.give_item(hero,f'crowbar{index}','EXP-EQU-002','hand')
    arc=Arc2(world);arc.final_defense()
    for _ in range(15):
        if world.final_defense['status']!='active':break
        for index,hero in enumerate(heroes):
            item_id=f'crowbar{index}'
            while (world.heroes[hero]['actions']>0 and world.heroes[hero]['health']>0
                   and world.gear[hero][item_id]['durability']>0
                   and world.final_defense['enemies']):
                enemy_id=min(world.final_defense['enemies'],
                             key=lambda eid:world.final_defense['enemies'][eid]['zone'])
                target=world.final_defense['enemies'][enemy_id]['zone']
                zone=world.final_defense['heroes'][hero]
                if abs(target-zone)<=1:
                    arc.defense_attack(hero,item_id,enemy_id)
                else:
                    arc.defense_move(hero,zone+(1 if target>zone else -1))
        arc.defense_activate()
    return {'seed':seed,'heroes':team_size,'status':world.final_defense['status'],
            'rounds':world.final_defense['round'],'integrity':world.final_defense['integrity'],
            'incapacitated':sum(h['health']==0 for h in world.heroes.values()),
            'wave':world.final_defense['wave']}


def aggregate(seeds: int = 50, base_seed: int = 20261023) -> dict:
    if seeds<1:raise ValueError('Quantidade de sementes inválida')
    runs=[replay(base_seed+i,team) for team in range(2,7) for i in range(seeds)]
    return {'scope':'defesa isolada; quatro flags, transmissor e um pé de cabra por herói injetados',
            'seed_start':base_seed,'seeds_per_team':seeds,'runs':runs,
            'counts':{str(team):dict(Counter(r['status'] for r in runs if r['heroes']==team))
                      for team in range(2,7)}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seeds',type=int,default=50)
    parser.add_argument('--seed',type=int,default=20261023)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=aggregate(args.seeds,args.seed)
    output=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.write_text(output,encoding='utf-8')
    else:print(output)
