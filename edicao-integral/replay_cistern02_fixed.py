"""Compara o abrigo portado com cinco trajetórias táticas fixas já auditadas.

Não certifica campanha livre: os dados e decisões táticas vêm de
src/scaled_tactical_replay.py, com rolagens favoráveis declaradas.
"""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from scaled_tactical_replay import run  # noqa: E402
from cistern02 import Cistern02, LINK_IDS, STARTERS  # noqa: E402

CATALOG=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf-8'))
NAME_TO_ID={hero['name']:hero['id'] for hero in CATALOG['heroes']}
LINK_NAMES={
    'Sozinho':LINK_IDS[:4],
    'Parceiro':LINK_IDS[4:8],
    'Filho':LINK_IDS[8:10],
    'Cachorro':LINK_IDS[10:11],
    'Parceiro e cachorro':LINK_IDS[11:12],
}


def _draw(names:list[str]) -> list[str]:
    used={key:0 for key in LINK_NAMES};result=[]
    for name in names:
        index=used[name];result.append(LINK_NAMES[name][index]);used[name]+=1
    return result


def replay(team_size:int) -> dict:
    oracle=run(team_size,accept_bia=False)
    founders=[NAME_TO_ID[name] for name in oracle['founders'][:team_size]]
    game=Cistern02.new(founders,_draw(oracle['links']))
    days=[]
    for day in range(1,6):
        if day>1:game.next_day()
        if day<=3:
            tactical=oracle['tactical'][day-1]
            game.spend_segments(tactical['segments'])
            found=tactical['delivered']
            game.food.extend([4]*found.get('Conserva',0))
            game.water.extend([4]*found.get('Água',0))
            if day==3:game._take(game.water,1)  # VIA-0002: uma porção de água levada
            if day==2:game.receive_part('Conexões')
            if day==3:
                game.receive_part('Bomba');game.receive_part('Membrana')
                game.reveal_siege()
                guards=[p['id'] for p in game.people if p['kind']=='adult'][:3]
                game.plan_guards(guards)
                base=2+int(game.dogs>0)+len(guards)
                ammo=max(0,4-base)
                game.resolve_siege(4,guards,[4]*len(guards),ammo,[])
        if day==4:
            for stage in ('A','B','C'):game.reserve(stage)
            game.work(2)
        if day==5:
            guards=[p['id'] for p in game.people if p['kind']=='adult']
            guards=(guards+[h for h in founders if h not in founders[:2]])[:3]
            game.plan_guards(guards)
            if game.pending_sieges:
                encounter=game.reveal_siege()
                game.resolve_siege(encounter['force'],guards,[4]*len(guards),
                                   max(0,encounter['force']-(2+int(game.dogs>0)+len(guards))),[])
            game.work(2)
        meal=game.meal()
        expected=oracle['days'][day-1]
        snapshot={'day':day,'food':sum(game.food),'water':sum(game.water),
                  'materials':game.materials,'pressure':game.pressure,
                  'filter_active':game.filter_active,'food_missing':meal['food_missing'],
                  'water_missing':meal['water_missing']}
        for key in ('food','water','materials','pressure','filter_active'):
            if snapshot[key]!=expected[key]:
                raise AssertionError((team_size,day,key,snapshot[key],expected[key]))
        days.append(snapshot)
    result=game.close_chapter()
    return {'heroes':team_size,'oracle_result':oracle['result'],
            'ported_result':result,'days':days}


if __name__=='__main__':
    print(json.dumps([replay(n) for n in range(2,7)],ensure_ascii=False,indent=2))
