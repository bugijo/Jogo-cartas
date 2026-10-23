"""Portões persistentes de Última Transmissão; defesa final ainda não implementada."""
import json
from pathlib import Path

from system import DATA, World

ARC_DATA=json.loads((Path(__file__).parent/'data/last_transmission.json').read_text(encoding='utf-8'))
ARC_CARDS={card['id']:card for card in ARC_DATA['cards']}


class Arc2:
    def __init__(self,world:World):
        self.world=world

    def decode_radio(self) -> None:
        card=ARC_CARDS['EXP-MIS-102']
        if (not self.world.flags.get('cistern_complete')
                or self.world.clues<card['requires']['clues']
                or self.world.flags.get('radio_code')):
            raise ValueError('Frequência indisponível')
        self.world.clues-=card['cost']['clues']
        self.world.flags['radio_code']=True
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'decoded'})

    def recover_access_card(self,expedition_id:str) -> None:
        card=ARC_CARDS['EXP-MIS-103']
        exp=self.world.expeditions.get(expedition_id)
        location=card['location']
        maximum=next(loc['searches'] for loc in DATA['locations'] if loc['id']==location)
        if (not exp or exp.destination!=location or exp.remaining!=0 or exp.returning
                or self.world.searches[location]>=maximum or self.world.flags.get('access_card')):
            raise ValueError('Cartão inacessível')
        self.world.flags['access_card']=True
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'card'})

    def authorize_installation(self,expedition_id:str,hero_ids:list[str],vehicle_id:str) -> None:
        card=ARC_CARDS['EXP-MIS-104']
        if (not self.world.flags.get('radio_code') or not self.world.flags.get('access_card')
                or self.world.flags.get('military_access')):
            raise ValueError('Código/cartão/missão ausente')
        self.world.flags['military_access']=True
        try:
            self.world.open_expedition(expedition_id,hero_ids,card['location'],vehicle_id=vehicle_id)
        except ValueError:
            del self.world.flags['military_access']
            raise
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'authorized'})

    def load_transmitter(self,expedition_id:str) -> None:
        card=ARC_CARDS['EXP-MIS-105']
        exp=self.world.expeditions.get(expedition_id)
        if (not exp or exp.destination!=card['location'] or exp.remaining!=0 or exp.returning
                or not self.world.flags.get('military_access')
                or 'transmitter' in self.world.special_stock
                or any('transmitter' in other.special_cargo
                       for other in self.world.expeditions.values())):
            raise ValueError('Transmissor inacessível')
        capacity=(6*len(exp.heroes) if not exp.vehicle_id else
                  next(v['cargo_capacity'] for v in DATA['vehicles'] if v['id']==exp.vehicle_id))
        if sum(exp.cargo.values())+len(exp.special_cargo)+1>capacity:
            raise ValueError('Carga insuficiente')
        exp.special_cargo.append('transmitter')
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'loaded'})

    def final_defense(self) -> None:
        raise NotImplementedError('Mapa do perímetro, horda final e condição de vitória pendentes')
