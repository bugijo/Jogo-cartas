"""Replay legal curto do controlador regional após vitória real da Cisterna.

Isso verifica o agente e a interface tática regional, não a campanha completa
Última Transmissão nem as regras de viagem ainda pendentes.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

from regional_player import AdaptiveRegionalPlayer
from tactics import TacticalGame
from verify_campaign_player02 import execute as execute_cistern
from integrated_campaign import IntegratedCampaign

ROOT=Path(__file__).resolve().parent
ARTIFACT=ROOT/'replays'/'regional_player_seed22.json'


def run_once(seed=22):
    cistern_player,cistern_report=execute_cistern(seed)
    campaign=cistern_player.game
    migration=campaign.transition_to_last_transmission()
    world=campaign.world
    if not world or not world.cistern_verified or campaign.phase!='last_transmission':
        raise AssertionError('Pré-requisito não veio da campanha legal da Cisterna')

    expedition='regional-player-seed22-market'
    team=sorted(world.heroes)
    before_stock=dict(world.stock)
    world.open_expedition(expedition,team,'EXP-LOC-02')
    outbound=world.advance_expedition(expedition)
    tactical=TacticalGame.start(world,expedition,'market_intro')
    player=AdaptiveRegionalPlayer('explorer')
    objective={'kind':'search','zone':5}

    first=player.step(tactical,objective)
    if first['action']!='open_door':
        raise AssertionError(f'A primeira ação adaptativa divergiu: {first}')
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'regional.json'
        campaign.save(path)
        campaign=IntegratedCampaign.load(path)
    world=campaign.world
    tactical=TacticalGame(world,expedition)
    player=AdaptiveRegionalPlayer.from_snapshot(player.snapshot())

    local=player.run_objective(tactical,objective,max_steps=40)
    if local['status']!='objective_completed_and_exited' or local['searches']!=1:
        raise AssertionError(f'Objetivo tático não foi concluído e extraído: {local}')
    world.begin_return(expedition)
    returned=world.advance_expedition(expedition)
    if returned!='returned':
        raise AssertionError(f'Expedição não retornou: {returned}')
    delivered=next(row['delivered'] for row in reversed(world.log)
                   if row.get('expedition')==expedition and 'delivered' in row)
    search_result=next(row['result'] for row in player.history
                       if row.get('action')=='search')
    if delivered!=search_result:
        raise AssertionError('Carga entregue diverge do saque resolvido pela ação')
    stock_after_delivery=deepcopy(world.stock)
    for resource,amount in delivered.items():
        if stock_after_delivery[resource]!=before_stock[resource]+amount:
            raise AssertionError(f'Recurso entregue sem conservação: {resource}')
    if stock_after_delivery['fuel']!=before_stock['fuel']:
        raise AssertionError('A expedição regional criou combustível')
    meal_order=sorted(world.meal_people())
    day=world.end_day(meal_plan={'food_priority':meal_order,
                                'water_priority':meal_order})
    consumers=world.consumers
    expected_after_day=dict(stock_after_delivery)
    for resource in expected_after_day:
        expected_after_day[resource]+=day['produced'][resource]
        if resource in ('food','water'):
            expected_after_day[resource]=max(0,expected_after_day[resource]-consumers)
    if world.stock!=expected_after_day or any(day['missing'].values()):
        raise AssertionError('Saldo diário diverge da produção, consumo ou déficit')

    relevant=[row for row in world.log if row.get('expedition')==expedition]
    search_receipt=next(row for row in relevant if row.get('action')=='search')
    arrival=next(row for row in world.log if row.get('expedition')==expedition
                 and 'delivered' in row)
    report={
        'status':'regional_agent_round_trip_verified',
        'seed':seed,
        'cistern':{'status':campaign.cistern.result,
                   'days':len(cistern_report['days']),
                   'decisions':cistern_report['decision_count']},
        'migration':migration,
        'regional':{
            'profile':'explorer','expedition':expedition,
            'destination':'EXP-LOC-02','team':team,
            'outbound':outbound,'objective':local,
            'decisions':player.history,
            'search_receipt':search_receipt,
            'delivery':arrival['delivered'],
            'stock_before':before_stock,'stock_after_delivery':stock_after_delivery,
            'stock_after_day':dict(world.stock),'consumers':consumers,
            'day_close':day,'day_after_close':world.day,
            'regional_clock_after_close':world.regional_clock,
        },
        'scope_limit':('Não cobre Célia, O2, viagens regionais por cartas, '
                       'combustível militar, transmissor ou defesa final.'),
    }
    return report


def execute(seed=22):
    first=run_once(seed)
    second=run_once(seed)
    if first!=second:
        raise AssertionError('Controlador regional não reproduz o mesmo estado e decisões')
    return first


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=22)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    report=execute(args.seed)
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if args.write:
        ARTIFACT.write_text(rendered,encoding='utf-8')
    print(rendered,end='')


if __name__=='__main__':
    main()
