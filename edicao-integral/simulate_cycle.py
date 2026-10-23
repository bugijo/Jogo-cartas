"""Replays de um dia do cenário de integração, não simulação da campanha inteira."""
import argparse
import json
from collections import Counter

from campaign import play_market_day

STRATEGIES=('conservative','explorer','builder','fighter','balanced')


def aggregate(start_seed:int,seeds_per_group:int) -> dict:
    if seeds_per_group<1:
        raise ValueError('Número de sementes inválido')
    groups={}
    for size in range(2,7):
        for strategy in STRATEGIES:
            runs=[play_market_day(start_seed+i,strategy,size) for i in range(seeds_per_group)]
            groups[f'H{size}:{strategy}']={
                'runs':len(runs),
                'outcomes':dict(sorted(Counter(r['outcome'] for r in runs).items())),
                'searches_total':sum(r['searches_used'] for r in runs),
                'food_shortage_runs':sum(r['missing']['food']>0 for r in runs),
                'water_shortage_runs':sum(r['missing']['water']>0 for r in runs),
                'restore_mismatch':sum(r['state_before_save']!=r['state_after_load'] for r in runs)}
    return {'start_seed':start_seed,'seeds_per_group':seeds_per_group,
            'total_replays':seeds_per_group*len(groups),'groups':groups,
            'scope':'cenário experimental de um dia; não é campanha completa, equilíbrio nem playtest'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=20261023)
    parser.add_argument('--seeds',type=int,default=50)
    args=parser.parse_args()
    print(json.dumps(aggregate(args.seed,args.seeds),ensure_ascii=False,indent=2))
