"""Reproduz a descoberta física pré-rádio de Célia após a Cisterna seed 22.

Prova apenas a sequência local de investigação/cópia e o retorno no relógio
regional atual. A viagem regional por cartas ainda não está integrada, portanto
este artefato não certifica uma expedição completa nem a campanha do segundo arco.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from arc2 import Arc2
from regional_player import AdaptiveRegionalPlayer
from tactics import TacticalGame
from verify_campaign_player02 import execute as execute_cistern

ROOT=Path(__file__).resolve().parent
ARTIFACT=ROOT/'replays'/'pre_radio_celia_seed22.json'


def run(seed: int=22) -> dict:
    cistern_player, cistern=execute_cistern(seed)
    campaign=cistern_player.game
    migration=campaign.transition_to_last_transmission()
    world=campaign.world
    if not world or not world.cistern_verified:
        raise AssertionError('A migração exige vitória certificada da Cisterna')
    if not world.regional_contact_identity_available('EXP-NPC-02','EXP-LOC-05'):
        raise AssertionError('Célia não está disponível como fonte regional neste estado')

    expedition='pre-radio-celia-seed22'
    team=sorted(world.heroes)
    world.open_expedition(expedition,team,'EXP-LOC-05')
    paid_travel_segments=[]
    while world.expeditions[expedition].remaining:
        paid_travel_segments.append(world.advance_expedition(expedition))
    tactical=TacticalGame.start(world,expedition,'station_02')
    player=AdaptiveRegionalPlayer('stealth')
    local=player.run_objectives(tactical,[
        {'kind':'investigate_contact','npc':'EXP-NPC-02'},
        {'kind':'evidence','npc':'EXP-NPC-02'},
    ],max_steps=60)
    if local['status']!='objective_completed_and_exited':
        raise AssertionError(f'Rota tática a Célia não concluiu: {local}')
    evidence=[row for row in world.log
              if row.get('expedition')==expedition
              and row.get('action')=='collect_regional_evidence']
    if len(evidence)!=1 or evidence[0].get('clues_awarded')!=1:
        raise AssertionError('A pista precisa vir de uma cópia física única')
    if world.flags.get('radio_code') or world.clues!=1:
        raise AssertionError('Descobrir Célia não pode ativar o rádio nem gerar pistas extras')

    world.begin_return(expedition)
    paid_return_segments=[]
    while expedition in world.expeditions:
        paid_return_segments.append(world.advance_expedition(expedition))
    if world.regional_clock!=10:
        raise AssertionError('Relógio regional não preservou os segmentos pagos')
    radio_error=None
    try:
        Arc2(world).decode_radio()
    except ValueError as exc:
        radio_error=str(exc)
    else:
        raise AssertionError('Rádio foi ativado com apenas uma pista')

    return {
        'status':'regional_tactical_clue_extracted_incomplete',
        'seed':seed,
        'cistern':{'status':campaign.cistern.result,
                   'days':len(cistern['days']),
                   'nights':sum(bool(day.get('night')) for day in cistern['days']),
                   'decisions':cistern['decision_count']},
        'migration':migration,
        'regional':{
            'profile':player.profile,'destination':'EXP-LOC-05','map':'station_02',
            'team':team,'outbound_segments':len(paid_travel_segments),
            'outbound_travel_cards':'not_resolved',
            'decisions':player.history,'local_status':local['status'],
            'evidence_receipts':evidence,'clues_after_return':world.clues,
            'radio_code':world.flags.get('radio_code',False),
            'celia_recruited':any(row.get('action')=='physical_contact_recruit'
                                   and row.get('npc')=='EXP-NPC-02'
                                   for row in world.log),
            'return_segments':len(paid_return_segments),
            'regional_clock':world.regional_clock,
            'radio_rejection':radio_error,
        },
        'limit':'O motor local provou investigação/cópia e movimento, mas não revelou cartas de Viagem, não recrutou Célia e não concluiu a campanha regional.',
    }


def execute(seed: int=22) -> dict:
    first=run(seed)
    second=run(seed)
    if first!=second:
        raise AssertionError('Rota regional de evidência não é determinística')
    return first


def main() -> None:
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
