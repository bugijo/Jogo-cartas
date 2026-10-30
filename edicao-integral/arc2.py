"""Portões e defesa final persistente de Última Transmissão (edição experimental)."""
import json
from collections import deque
from pathlib import Path

import camp as camp_rules
import community as community_rules
from system import DATA, ITEMS, LOCATIONS, TACTICS_DATA, VEHICLES, World

ARC_DATA=json.loads((Path(__file__).parent/'data/last_transmission.json').read_text(encoding='utf-8'))
ARC_CARDS={card['id']:card for card in ARC_DATA['cards']}


class Arc2:
    def __init__(self,world:World):
        self.world=world

    def decode_radio(self) -> None:
        card=ARC_CARDS['EXP-MIS-102']
        if (self.world.expeditions or self.world.encounters
                or not self.world.cistern_verified
                or self.world.clues<card['requires']['clues']
                or self.world.flags.get('radio_code')):
            raise ValueError('Decodificação exige retorno ao abrigo, Cisterna verificada e duas pistas')
        self.world.clues-=card['cost']['clues']
        self.world.flags['radio_code']=True
        self.world.log.append({'day':self.world.day,'mission':card['id'],
                               'result':'decoded',
                               'clues_spent':card['cost']['clues'],
                               'clues_remaining':self.world.clues})

    def recover_access_card(self,expedition_id:str) -> None:
        card=ARC_CARDS['EXP-MIS-103']
        exp=self.world.expeditions.get(expedition_id)
        location=card['location']
        floor=next((site for site,items in sorted(self.world.unique_items_at_sites.items())
                    if 'access_card' in items),None)
        if floor is not None:
            self._pick_dropped_card(expedition_id,floor)
            return
        if (not exp or exp.destination!=location or exp.remaining!=0 or exp.returning
                or not any(entry.get('expedition')==expedition_id
                           and entry.get('location')==location and entry.get('action')=='search'
                           for entry in self.world.log)
                or self.world.flags.get('access_card')):
            raise ValueError('Cartão inacessível')
        if any('access_card' in items
               for items in self.world.unique_items_at_sites.values()):
            raise ValueError('Cartão está no chão; regra de recuperação ainda não definida')
        continuous=bool((self.world.cistern_record or {}).get('migration',{}).get('receipt'))
        if continuous:
            encounter=self.world.encounters.get(expedition_id)
            searchers={entry.get('hero') for entry in self.world.log
                       if entry.get('expedition')==expedition_id
                       and entry.get('location')==location and entry.get('action')=='search'}
            carrier=next((hero_id for hero_id in sorted(searchers)
                          if encounter and hero_id in encounter['heroes']
                          and encounter['heroes'][hero_id] in encounter['search_zones']
                          and self.world.heroes[hero_id]['health']>0),None)
            capacity=(6*len(exp.heroes) if not exp.vehicle_id else
                      next(v['cargo_capacity'] for v in DATA['vehicles']
                           if v['id']==exp.vehicle_id))
            if (carrier is None or 'access_card' in self.world.special_stock
                    or any('access_card' in other.special_cargo
                           for other in self.world.expeditions.values())
                    or sum(exp.cargo.values())+len(exp.special_cargo)+1>capacity):
                raise ValueError('Cartão não está no alcance/sem carga')
            exp.special_cargo.append('access_card')
        self.world.flags['access_card']=True
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'card'})

    def _pick_dropped_card(self,expedition_id:str,site:str) -> None:
        """Cartão perdido numa expedição que falhou (decisão do diretor, D-19).

        Fica no chão do local onde caiu. Uma nova expedição a esse local o
        recolhe: herói vivo numa zona de busca gasta 1 PA; mesma regra de carga.
        Não exige nova busca (o local pode estar esgotado).
        """
        exp=self.world.expeditions.get(expedition_id)
        if (not exp or exp.destination!=site or exp.remaining!=0 or exp.returning
                or self.world.flags.get('access_card')):
            raise ValueError('Cartão inacessível')
        encounter=self.world.encounters.get(expedition_id)
        carrier=next((hero_id for hero_id in sorted(exp.heroes)
                      if self.world.heroes[hero_id]['health']>0
                      and self.world.heroes[hero_id]['actions']>=1
                      and (encounter is None or (hero_id in encounter['heroes']
                           and encounter['heroes'][hero_id] in encounter['search_zones']))),None)
        capacity=(6*len(exp.heroes) if not exp.vehicle_id else
                  next(v['cargo_capacity'] for v in DATA['vehicles']
                       if v['id']==exp.vehicle_id))
        if carrier is None or sum(exp.cargo.values())+len(exp.special_cargo)+1>capacity:
            raise ValueError('Cartão não está no alcance/sem carga')
        self.world.heroes[carrier]['actions']-=1
        self.world.unique_items_at_sites[site].remove('access_card')
        exp.special_cargo.append('access_card')
        self.world.flags['access_card']=True
        self.world.log.append({'day':self.world.day,'mission':'EXP-MIS-103','result':'card',
                               'recovered_from_floor':site,'hero':carrier})

    def authorize_installation(self,expedition_id:str,hero_ids:list[str],vehicle_id:str) -> None:
        card=ARC_CARDS['EXP-MIS-104']
        migration=(self.world.cistern_record or {}).get('migration', {})
        continuous=bool(migration.get('receipt'))
        if (not self.world.cistern_verified or not self.world.flags.get('radio_code')
                or not self.world.flags.get('access_card')
                or self.world.flags.get('military_access')):
            raise ValueError('Código/cartão/missão ausente')
        if continuous and vehicle_id != 'EXP-VEI-02':
            raise ValueError('Campanha contínua exige a van canônica recuperada no Posto')
        if continuous and 'access_card' not in self.world.special_stock:
            raise ValueError('Campanha contínua exige cartão de acesso transportado ao abrigo')
        if continuous and self.world.community is None:
            distance=LOCATIONS[card['location']]['distance']
            segments=DATA['rules']['travel_segments'][distance]
            expected=2*segments*VEHICLES[vehicle_id]['fuel_per_segment']
            if (card['cost'].get('fuel')!=expected
                    or card['requires'].get('fuel_round_trip')!=expected):
                raise ValueError('Custo da missão não corresponde a 2 Combustíveis por trecho')
        self.world.flags['military_access']=True
        try:
            self.world.open_expedition(
                expedition_id,hero_ids,card['location'],vehicle_id=vehicle_id,
                special_items=['access_card'] if continuous else None)
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
                or any('transmitter' in items
                       for items in self.world.unique_items_at_sites.values())
                or any('transmitter' in other.special_cargo
                       for other in self.world.expeditions.values())):
            raise ValueError('Transmissor inacessível')
        encounter=self.world.encounters.get(expedition_id)
        operator=next((hero_id for hero_id,zone in encounter['heroes'].items()
                       if zone==6 and self.world.heroes[hero_id]['health']>0
                       and self.world.heroes[hero_id]['actions']>0),None) if encounter else None
        if (not encounter or encounter['map']!='military_installation'
                or operator is None
                or any(enemy['zone']==6 for enemy in encounter['enemies'].values())):
            raise ValueError('Objetivo militar fora de alcance ou ocupado')
        capacity=(6*len(exp.heroes) if not exp.vehicle_id else
                  next(v['cargo_capacity'] for v in DATA['vehicles'] if v['id']==exp.vehicle_id))
        if sum(exp.cargo.values())+len(exp.special_cargo)+1>capacity:
            raise ValueError('Carga insuficiente')
        self.world.heroes[operator]['actions']-=1
        exp.special_cargo.append('transmitter')
        self.world.log.append({'day':self.world.day,'mission':card['id'],'result':'loaded'})

    def final_defense(self) -> dict:
        w=self.world
        if (w.final_defense is not None or w.expeditions or w.encounters
                or 'transmitter' not in w.special_stock
                or not w.cistern_verified
                or not all(w.flags.get(key) for key in
                           ('radio_code','access_card','military_access'))
                or not any(h['health']>0 for h in w.heroes.values())):
            raise ValueError('Defesa final indisponível')
        if community_rules.transmission_silent(w):
            raise ValueError('A frequência calou: prazo da transmissão encerrado')
        away=community_rules.away(w)  # quem está em viagem automática não defende
        w.final_defense={'status':'active','map':'camp_final','integrity':3,'wave':1,
                         'heroes':{h:1 for h,state in w.heroes.items()
                                   if state['health']>0 and h not in away},
                         'enemies':{},'next_enemy':1,'round':0}
        self._spawn_wave()
        if w.community is not None:
            w.begin_round()  # D-22: a defesa abre rodada nova, como a entrada num mapa
        w.log.append({'day':w.day,'mission':'EXP-MIS-106','result':'started'})
        return w.final_defense

    def _active_defense(self) -> dict:
        defense=self.world.final_defense
        if not defense or defense['status']!='active':
            raise ValueError('Defesa final não ativa')
        return defense

    def _spawn_wave(self) -> None:
        defense=self._active_defense()
        waves=(community_rules.defense_waves(self.world,len(defense['heroes']))
               or ARC_DATA['final_defense']['waves'])
        for kind in waves[defense['wave']-1]:
            eid=f"E{defense['next_enemy']:03d}"
            defense['next_enemy']+=1
            defense['enemies'][eid]={'kind':kind,'zone':4,
                                     'health':TACTICS_DATA['enemies'][kind]['health']}

    @staticmethod
    def _distance(start:int,end:int) -> int:
        edges=TACTICS_DATA['maps']['camp_final']['edges']
        todo=deque([(start,0)]);seen={start}
        while todo:
            zone,distance=todo.popleft()
            if zone==end:return distance
            for a,b in edges:
                nxt=b if a==zone else a if b==zone else None
                if nxt is not None and nxt not in seen:
                    seen.add(nxt);todo.append((nxt,distance+1))
        raise ValueError('Zona desconectada')

    def defense_move(self,hero_id:str,zone:int) -> None:
        defense=self._active_defense()
        if (hero_id not in defense['heroes'] or zone not in TACTICS_DATA['maps']['camp_final']['zones']
                or self._distance(defense['heroes'][hero_id],zone)!=1
                or self.world.heroes[hero_id]['health']<1
                or self.world.heroes[hero_id]['actions']<1):
            raise ValueError('Movimento de defesa indisponível')
        self.world.heroes[hero_id]['actions']-=1
        defense['heroes'][hero_id]=zone

    def defense_attack(self,hero_id:str,item_id:str,enemy_id:str) -> dict:
        defense=self._active_defense()
        if (hero_id not in defense['heroes'] or enemy_id not in defense['enemies']
                or item_id not in self.world.gear[hero_id]):
            raise ValueError('Ataque de defesa inválido')
        item=self.world.gear[hero_id][item_id]
        combat=ITEMS[item['template']]['combat']
        reach=combat.get('range',1) if combat else 0
        enemy=defense['enemies'][enemy_id]
        if self._distance(defense['heroes'][hero_id],enemy['zone'])>reach:
            raise ValueError('Inimigo fora de alcance')
        result=self.world.attack_with_item(hero_id,item_id)
        enemy['health']=max(0,enemy['health']-result['damage'])
        if enemy['health']==0:
            self.world.award_xp(hero_id,TACTICS_DATA['enemies'][enemy['kind']]['xp'],combat=True)
            del defense['enemies'][enemy_id]
        return dict(result,enemy_health=enemy['health'])

    def defense_activate(self) -> dict:
        defense=self._active_defense()
        waves=(community_rules.defense_waves(self.world,len(defense['heroes']))
               or ARC_DATA['final_defense']['waves'])
        if not defense['enemies']:
            if defense['wave']==len(waves):
                defense['status']='won'
                self.world.flags['free_survival']=True
                self.world.log.append({'day':self.world.day,'mission':'EXP-MIS-106','result':'won'})
                return {'status':'won','integrity':defense['integrity']}
            defense['wave']+=1
            self._spawn_wave()
        # D-23: Vigia e guardas do acampamento atiram no inimigo mais próximo.
        support=[]
        for shooter in camp_rules.defense_shooters(self.world):
            if not defense['enemies']:
                break
            eid=min(defense['enemies'],key=lambda e:(defense['enemies'][e]['zone'],e))
            target=defense['enemies'][eid]
            target['health']=max(0,target['health']-camp_rules.RULES['defense_support']['damage'])
            support.append([shooter,eid])
            if target['health']==0:
                del defense['enemies'][eid]
        if support:
            defense.setdefault('support',[]).append(support)
        for enemy in defense['enemies'].values():
            for _ in range(TACTICS_DATA['enemies'][enemy['kind']]['move']):
                if enemy['zone']>1:enemy['zone']-=1
            victims=[h for h,z in defense['heroes'].items()
                     if z==enemy['zone'] and self.world.heroes[h]['health']>0]
            if victims:
                hero_id=sorted(victims)[0]
                armor=next((iid for iid,item in self.world.gear[hero_id].items()
                            if item['slot'] in ('head','torso','legs')
                            and 'armor' in ITEMS[item['template']] and item['durability']>0),None)
                prior=self.world.heroes[hero_id]['health']
                self.world.receive_damage(hero_id,
                                          TACTICS_DATA['enemies'][enemy['kind']]['attack'],armor)
                if self.world.heroes[hero_id]['health']<prior:
                    self.world.roll_infection(hero_id)
            if enemy['zone']==1:
                defense['integrity']=max(0,defense['integrity']-1)
        defense['round']+=1
        self.world.begin_round()
        if defense['integrity']==0 or not any(self.world.heroes[h]['health']>0 for h in defense['heroes']):
            defense['status']='lost'
            self.world.log.append({'day':self.world.day,'mission':'EXP-MIS-106','result':'lost'})
        return {'status':defense['status'],'integrity':defense['integrity'],
                'wave':defense['wave'],'round':defense['round']}

    def defense_retreat(self) -> None:
        defense=self._active_defense()
        defense['status']='retreated'
        self.world.log.append({'day':self.world.day,'mission':'EXP-MIS-106','result':'retreated'})
