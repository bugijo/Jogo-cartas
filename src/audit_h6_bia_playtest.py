"""Independent food/work ledger for the fixed H6 route and one legal alternative.

No new resource: emergency collection is RULES §4, at most two portions per day.
"""
from __future__ import annotations

import json
from math import ceil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'kit-final-prova/playtest/H6_BIA_SALDOS.json'
ROUTES=json.loads((ROOT/'kit-final-prova/auditoria/ROTEIROS_TATICOS_H2_H6.json').read_text())
BASE=next(x for x in ROUTES if x['heroes']==6)
assert BASE['consumers_initial']==8 and BASE['founders']==['Lia','Ivo','Caio','Mara','Nara','Bento']
assert all(wounds<3 for wounds in BASE['final_wounds'].values())
assert BASE['days'][3]['fatigue_removed_next_dawn']==1


def ledger(accept_bia:bool,collection_days=()):
    initial_c=BASE['consumers_initial']
    food=water=4*ceil(2*initial_c/4)
    rows=[]
    for day in range(1,6):
        delivery=BASE['tactical'][day-1]['delivered'] if day<=3 else {}
        food+=4*delivery.get('Conserva',0)
        water+=4*delivery.get('Água',0)
        if day==3:water-=1  # ZC-VIA-0002 da trajetória fixa
        gathered=2 if day in collection_days else 0
        assert gathered<=2
        food+=gathered
        if day==5:water+=2*initial_c  # enchimento único do filtro
        eat=initial_c+int(accept_bia and day>=2)
        food-=eat;water-=eat
        rows.append(dict(day=day,humans=7+int(accept_bia and day>=2),dogs=1,
                         collected_food=gathered,meal_due=eat,
                         food_balance=food,food_shortage=max(0,-food),
                         water_balance=water,water_shortage=max(0,-water)))
    return rows


def main():
    declined=ledger(False)
    accepted=ledger(True)
    collected=ledger(True,(4,5))
    assert [(x['food_balance'],x['water_balance']) for x in declined]==[(x['food'],x['water']) for x in BASE['days']]
    assert [x['food_balance'] for x in accepted]==[24,23,14,5,-4]
    assert [x['food_balance'] for x in collected]==[24,23,14,7,0]
    assert [x['water_balance'] for x in collected]==[16,15,13,4,11]
    assert all(x['food_shortage']==x['water_shortage']==0 for x in collected)
    # Days 4/5 have no expedition. Six founders + one initial adult partner
    # are trusted and home. Bia need not work. Rule §4: at most one job/adult.
    workers={'day_4':dict(filter=['Mara','Nara'],collection=['Bento','adulto parceiro'],vigils=[]),
             'day_5':dict(filter=['Mara','Nara'],collection=['Bento','adulto parceiro'],vigils=['Lia','Ivo','Caio'])}
    for day in workers.values():
        assigned=sum(day.values(),[])
        assert len(assigned)==len(set(assigned)) and len(assigned)<=7
        assert len(day['collection'])<=2 and len(day['vigils'])<=3
    result=dict(source='RULES.md §§2,4,8,12; CAMPAIGN.md Construção principal e Vitória',
                initial_consumers=BASE['consumers_initial'],accepted_consumer_from_day=2,
                routes={'sem_bia':declined,'bia_sem_coleta':accepted,'bia_com_coleta_dias_4_5':collected},
                workers=workers,
                assumptions=['Mesmas entregas, rolagens, cercos e intenção Solidário da rota fixa H6.',
                             'Os sete adultos fundadores/confiáveis permanecem no abrigo nos dias 4 e 5.',
                             'Coleta gera porções, não cartas; nenhuma provisão é renovada.',
                             'A rota ainda depende das rolagens e escolhas favoráveis fixadas; não estima probabilidade.'])
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print([(k,[r['food_balance'] for r in v]) for k,v in result['routes'].items()])


if __name__=='__main__':main()
