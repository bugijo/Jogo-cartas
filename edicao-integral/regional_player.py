"""Jogador adaptativo de exploração regional usando somente APIs públicas.

O controlador executa ida, objetivo tático e retorno a pé. Não define conteúdo
de cartas de viagem/emboscadas regionais nem a regra de combustível militar.
"""
from collections import deque
from dataclasses import dataclass, field

from system import ITEMS, NPCS, REGIONAL_CONTACTS
from tactics import TACTICS, TacticalGame


@dataclass
class AdaptiveRegionalPlayer:
    """Política determinística baseada no estado observável da mesa.

    Os perfis alteram prioridades, não recebem dados ocultos nem acessam o RNG.
    Cada efeito é aplicado por TacticalGame/World; o agente não escreve estado.
    """

    profile: str = 'balanced'
    completed: set[tuple] = field(default_factory=set)
    history: list[dict] = field(default_factory=list)
    search_progress: dict[tuple,int] = field(default_factory=dict)

    PROFILES = {
        'cautious': {'combat_distance': 1},
        'explorer': {'combat_distance': 1},
        'builder': {'combat_distance': 1},
        'combatant': {'combat_distance': 3},
        'leader': {'combat_distance': 2},
        'novice': {'combat_distance': 1},
        'optimizer': {'combat_distance': 2},
        'adversarial': {'combat_distance': 1},
        'balanced': {'combat_distance': 1},
    }

    def __post_init__(self):
        if self.profile not in self.PROFILES:
            raise ValueError(f'Perfil regional desconhecido: {self.profile}')

    def snapshot(self):
        return {'schema':1,'profile':self.profile,
                'completed':[list(key) for key in sorted(self.completed)],
                'history':[dict(row) for row in self.history],
                'search_progress':[{'key':list(key),'remaining':remaining}
                                   for key,remaining in sorted(self.search_progress.items())]}

    @classmethod
    def from_snapshot(cls, payload):
        if (not isinstance(payload,dict) or payload.get('schema')!=1
                or payload.get('profile') not in cls.PROFILES
                or not isinstance(payload.get('completed'),list)
                or not isinstance(payload.get('history'),list)
                or not isinstance(payload.get('search_progress'),list)):
            raise ValueError('Save do jogador regional inválido')
        player=cls(payload['profile'])
        player.completed={tuple(key) for key in payload['completed']}
        player.history=[dict(row) for row in payload['history']]
        for row in payload['search_progress']:
            key=row.get('key');remaining=row.get('remaining')
            if (not isinstance(key,list) or len(key)!=6
                    or not isinstance(remaining,int) or remaining<0):
                raise ValueError('Progresso de busca do jogador regional inválido')
            player.search_progress[tuple(key)]=remaining
        return player

    @staticmethod
    def _key(tactical, objective):
        return (tactical.id, objective.get('kind'), objective.get('npc'),
                objective.get('zone'), objective.get('item'), objective.get('lot'))

    def _objective_done(self, tactical, objective):
        key=self._key(tactical,objective)
        kind=objective.get('kind')
        if kind=='contact':
            npc=objective['npc']
            exp=tactical.world.expeditions[tactical.id]
            physically_recruited=(npc in exp.crew and any(
                row.get('action')=='physical_contact_recruit'
                and row.get('expedition')==tactical.id
                and row.get('npc')==npc for row in tactical.world.log))
            if physically_recruited:
                self.completed.add(key)
                return True
            # A stale controller snapshot cannot replace an in-world receipt.
            self.completed.discard(key)
            return False
        if key in self.completed:
            return True
        if kind=='zone':
            if objective['zone'] in tactical.state['heroes'].values():
                self.completed.add(key)
                return True
        if kind=='search':
            remaining=self.search_progress.setdefault(
                key,objective.get('searches',1))
            if remaining<=0:
                self.completed.add(key)
                return True
        if kind=='battery' and 'battery' in tactical.world.expeditions[tactical.id].special_cargo:
            self.completed.add(key)
            return True
        if kind=='fuel' and objective['lot'] in [
                int(entry.rsplit(':',1)[-1])
                for entry in tactical.state.get('fuel_cards_taken',[])]:
            self.completed.add(key)
            return True
        if kind=='inspect_van' and tactical.state.get('van_state')!='abandoned':
            self.completed.add(key)
            return True
        if kind=='repair_van' and tactical.state.get('van_state')=='operational':
            self.completed.add(key)
            return True
        return False

    @staticmethod
    def _topological_path(tactical, start, goal):
        edges=tactical.map['edges']
        queue=deque([(start,[start])]);seen={start}
        while queue:
            current,path=queue.popleft()
            if current==goal:
                return path
            neighbors=sorted(b if a==current else a for a,b in edges
                             if current in (a,b))
            for nxt in neighbors:
                if nxt not in seen:
                    seen.add(nxt);queue.append((nxt,path+[nxt]))
        return None

    def _goal(self, tactical, objective):
        kind=objective.get('kind')
        if kind in ('zone','search','battery','fuel','inspect_van','repair_van'):
            if objective['zone'] not in tactical.map['zones']:
                return []
            destination=tactical.world.expeditions[tactical.id].destination
            if kind=='search' and (objective['zone'] not in tactical.state['search_zones']
                                   or tactical.world.searches[destination]<1):
                return []
            if kind=='battery' and 'battery' not in tactical.world.unique_items_at_sites.get(destination,[]):
                return []
            if kind=='fuel' and (destination!='EXP-LOC-07'
                                 or not 1<=objective.get('lot',0)<=8
                                 or tactical.world.searches[destination]<1
                                 or f'EXP-LOC-07:Combustível:{objective["lot"]}'
                                    in tactical.state.get('fuel_cards_taken',[])):
                return []
            if kind=='inspect_van' and (destination!='EXP-LOC-07'
                                        or tactical.state.get('van_state')!='abandoned'):
                return []
            if kind=='repair_van' and (destination!='EXP-LOC-07'
                                       or tactical.state.get('van_state')!='incomplete'
                                       or 'battery' not in tactical.world.expeditions[
                                           tactical.id].special_cargo):
                return []
            return [objective['zone']]
        if kind=='contact':
            npc=objective['npc']
            contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc)
            zone=tactical.state.get('npc_contacts',{}).get(npc)
            exp=tactical.world.expeditions[tactical.id]
            vehicle=(tactical.world.vehicles.get(exp.vehicle_id,{}) if exp.vehicle_id else None)
            seats=(vehicle['seats'] if vehicle else 6*len(exp.heroes))
            community=tactical.world
            npc_spec=NPCS.get(npc,{})
            existing=community.npcs.get(npc)
            contact_legal=(community.residents<community.beds
                           and community.stock['food']>=community.residents+1
                           and community.stock['water']>=community.residents+1
                           and len(exp.heroes)+len(exp.crew)+1<=seats
                           and npc_spec.get('source_hero_id') not in community.heroes
                           and (existing is None or existing['location']==exp.destination))
            if (contact and zone is not None and contact['map']==tactical.state['map']
                    and contact['location']==exp.destination and contact_legal):
                return [zone]
            return []
        if kind=='exit':
            return [tactical.exit_zone]
        raise ValueError(f'Objetivo regional desconhecido: {kind}')

    def _weapon_attacks(self, tactical, hero_id, enemy_id):
        hero_zone=tactical.state['heroes'][hero_id]
        enemy=tactical.state['enemies'][enemy_id]
        distance=abs((hero_zone-1)//4-(enemy['zone']-1)//4)+abs(
            (hero_zone-1)%4-(enemy['zone']-1)%4)
        options=[]
        for instance_id,item in tactical.world.gear[hero_id].items():
            spec=ITEMS[item['template']].get('combat')
            if (not spec or item['durability']<1
                    or distance>spec.get('range',1)
                    or not tactical.line_of_sight(hero_zone,enemy['zone'])):
                continue
            options.append((spec.get('damage',0),spec.get('dice',0),instance_id))
        return sorted(options,reverse=True)

    def _threat_action(self, tactical, objectives):
        limit=self.PROFILES[self.profile]['combat_distance']
        urgent_zones=set(objectives)
        urgent_zones.add(tactical.exit_zone)
        candidates=[]
        for hero_id,zone in sorted(tactical.state['heroes'].items()):
            hero=tactical.world.heroes[hero_id]
            if hero['health']<1 or hero['actions']<1:
                continue
            for enemy_id,enemy in sorted(tactical.state['enemies'].items()):
                dist=abs((zone-1)//4-(enemy['zone']-1)//4)+abs(
                    (zone-1)%4-(enemy['zone']-1)%4)
                if enemy['zone'] not in urgent_zones and dist>limit:
                    continue
                for _,_,instance_id in self._weapon_attacks(tactical,hero_id,enemy_id):
                    candidates.append((dist,hero_id,enemy_id,instance_id))
        if not candidates:
            return None
        _,hero_id,enemy_id,instance_id=min(candidates)
        receipt=tactical.attack(hero_id,instance_id,enemy_id)
        return {'action':'attack','hero':hero_id,'enemy':enemy_id,'item':instance_id,
                'result':receipt}

    def _act_on_goal(self, tactical, objective, hero_id):
        kind=objective['kind']
        if kind=='zone':
            self.completed.add(self._key(tactical,objective))
            return {'action':'reach_zone','hero':hero_id,'zone':objective['zone']}
        if kind=='search':
            result=tactical.search(hero_id)
            key=self._key(tactical,objective)
            self.search_progress.setdefault(key,objective.get('searches',1))
            self.search_progress[key]-=1
            if self.search_progress[key]<=0:
                self.completed.add(self._key(tactical,objective))
            return {'action':'search','hero':hero_id,'result':result}
        if kind=='contact':
            result=tactical.contact_npc(hero_id,objective['npc'])
            self.completed.add(self._key(tactical,objective))
            return {'action':'contact','hero':hero_id,'result':result}
        if kind=='battery':
            tactical.pickup_unique_item(hero_id,'battery')
            self.completed.add(self._key(tactical,objective))
            return {'action':'pickup_unique','hero':hero_id,'item':'battery'}
        if kind=='fuel':
            result=tactical.pickup_fuel_card(hero_id,objective['lot'])
            self.completed.add(self._key(tactical,objective))
            return {'action':'pickup_fuel','hero':hero_id,'result':result}
        if kind=='inspect_van':
            tactical.inspect_van(hero_id)
            self.completed.add(self._key(tactical,objective))
            return {'action':'inspect_van','hero':hero_id}
        if kind=='repair_van':
            result=tactical.repair_van(hero_id)
            if result['success']:
                self.completed.add(self._key(tactical,objective))
            return {'action':'repair_van','hero':hero_id,'result':result}
        raise ValueError(f'Objetivo regional sem ação: {kind}')

    @staticmethod
    def _action_cost(objective):
        return 2 if objective.get('kind')=='repair_van' else 1

    def step(self, tactical, objective):
        """Executa uma decisão e devolve a trilha observável dessa ação."""
        if tactical.id not in tactical.world.encounters:
            return {'action':'blocked','reason':'encontro já encerrado'}
        if tactical.state.get('round_closed'):
            return {'action':'blocked','reason':'relógio sem reserva de retorno'}
        if self._objective_done(tactical,objective):
            targets=[tactical.exit_zone]
        else:
            targets=self._goal(tactical,objective)
        if not targets:
            return {'action':'blocked','reason':'objetivo não está disponível neste local'}

        active=[hero for hero in sorted(tactical.state['heroes'])
                if tactical.world.heroes[hero]['health']>0]
        if not active:
            return {'action':'blocked','reason':'equipe incapacitada'}
        threat=self._threat_action(tactical,targets)
        if threat:
            decision=threat
            self.history.append(decision)
            return decision

        choices=[]
        for hero_id in active:
            zone=tactical.state['heroes'][hero_id]
            for goal in targets:
                if zone==goal:
                    if not self._objective_done(tactical,objective) and \
                            tactical.world.heroes[hero_id]['actions']>=self._action_cost(objective) \
                            and not (objective.get('kind')=='repair_van'
                                     and hero_id in tactical.state.get('van_attempts',[])):
                        choices.append((0,hero_id,goal,'interact'))
                    continue
                open_path=tactical.path_to(hero_id,goal)
                route=self._topological_path(tactical,zone,goal)
                closed_door=next(((a,b) for a,b in zip(route or [],(route or [])[1:])
                                  if f'{min(a,b)}-{max(a,b)}' in tactical.state['doors']
                                  and not tactical.state['doors'][
                                      f'{min(a,b)}-{max(a,b)}']['open']),None)
                door_actionable=False
                if closed_door:
                    door=tactical.state['doors'][
                        f'{min(closed_door[0],closed_door[1])}-'
                        f'{max(closed_door[0],closed_door[1])}']
                    door_actionable=not door['blocked'] or any(
                        item['slot']=='hand' and item['durability']>0
                        and ITEMS[item['template']].get('breach',0)>0
                        for item in tactical.world.gear[hero_id].values())
                # Prefer a short route through an openable printed door over
                # a very long detour around it. Door crossing still costs the
                # matching public action below.
                if closed_door and door_actionable and (open_path is None or
                                    len(route)<len(open_path)):
                    choices.append((len(route)-1,hero_id,goal,'door'))
                elif open_path:
                    choices.append((len(open_path)-1,hero_id,goal,'move'))
        choices.sort()
        if choices:
            _,hero_id,goal,kind=choices[0]
            if kind=='interact':
                decision=self._act_on_goal(tactical,objective,hero_id)
            elif kind=='door':
                zone=tactical.state['heroes'][hero_id]
                route=self._topological_path(tactical,zone,goal)
                closed=next(((a,b,tactical.state['doors'][
                    f'{min(a,b)}-{max(a,b)}']) for a,b in zip(route,route[1:])
                    if f'{min(a,b)}-{max(a,b)}' in tactical.state['doors']
                    and not tactical.state['doors'][f'{min(a,b)}-{max(a,b)}']['open']),None)
                if closed is None:
                    return {'action':'blocked','reason':'porta da rota mudou'}
                a,b,door=closed
                endpoints=[]
                for endpoint in (a,b):
                    path=tactical.path_to(hero_id,endpoint)
                    if path:
                        endpoints.append((len(path)-1,endpoint,path))
                if not endpoints:
                    return {'action':'blocked','reason':'não alcança a face da porta'}
                _,endpoint,path=min(endpoints)
                if len(path)>1:
                    nxt=path[1]
                    cost=1+int(any(enemy['zone']==zone
                                   for enemy in tactical.state['enemies'].values()))
                    if tactical.world.heroes[hero_id]['actions']<cost:
                        return self._activate(tactical)
                    tactical.move(hero_id,nxt)
                    decision={'action':'move','hero':hero_id,'from':zone,'to':nxt,
                              'target':goal,'cost':cost}
                elif not door['blocked']:
                    tactical.open_door(hero_id,a,b)
                    decision={'action':'open_door','hero':hero_id,'edge':[a,b]}
                else:
                    tools=[instance_id for instance_id,item in
                           tactical.world.gear[hero_id].items()
                           if item['slot']=='hand' and item['durability']>0
                           and ITEMS[item['template']].get('breach',0)>0]
                    if not tools:
                        return {'action':'blocked','reason':'porta bloqueada sem ferramenta'}
                    if tactical.world.heroes[hero_id]['actions']<2:
                        return self._activate(tactical)
                    opened=tactical.breach(hero_id,a,b,tools[0])
                    decision={'action':'breach','hero':hero_id,'edge':[a,b],
                              'opened':opened,'item':tools[0]}
            else:
                zone=tactical.state['heroes'][hero_id]
                path=tactical.path_to(hero_id,goal)
                if not path or len(path)<2:
                    return {'action':'blocked','reason':'rota aberta indisponível'}
                nxt=path[1]
                cost=1+int(any(enemy['zone']==zone
                               for enemy in tactical.state['enemies'].values()))
                if tactical.world.heroes[hero_id]['actions']<cost:
                    return self._activate(tactical)
                tactical.move(hero_id,nxt)
                decision={'action':'move','hero':hero_id,'from':zone,'to':nxt,
                          'target':goal,'cost':cost}
            self.history.append(decision)
            return decision

        # No hero has an available action. The phase transition is legal only
        # through the tactical engine, which also advances the shared clock.
        return self._activate(tactical)

    def _activate(self, tactical):
        try:
            result=tactical.activate()
        except ValueError as exc:
            return {'action':'blocked','reason':str(exc)}
        decision={'action':'activate','result':result}
        self.history.append(decision)
        return decision

    def run_objective(self, tactical, objective, max_steps=100):
        baseline=sum(row.get('action')=='search' and row.get('expedition')==tactical.id
                     for row in tactical.world.log)
        start_searches=objective.get('searches',1)
        for _ in range(max_steps):
            if tactical.id not in tactical.world.encounters:
                return {'status':'objective_completed_and_exited',
                        'searches':sum(row.get('action')=='search'
                                       and row.get('expedition')==tactical.id
                                       for row in tactical.world.log)-baseline}
            result=self.step(tactical,objective)
            if result['action']=='blocked':
                return {'status':'blocked','reason':result['reason'],
                        'decisions':len(self.history)}
            if (self._objective_done(tactical,objective)
                    and all(zone==tactical.exit_zone
                            for zone in tactical.state['heroes'].values())):
                try:
                    tactical.finish()
                except ValueError:
                    # An enemy may still occupy the exit; next policy step
                    # attacks it only if a legal weapon/action exists.
                    pass
                if tactical.id not in tactical.world.encounters:
                    break
        if tactical.id not in tactical.world.encounters:
            status=('objective_completed_and_exited' if
                    self._objective_done(tactical,objective) else 'objective_not_completed')
        else:
            status='step_limit'
        count=sum(row.get('action')=='search' and row.get('expedition')==tactical.id
                  for row in tactical.world.log)-baseline
        return {'status':status,'searches':count,'requested_searches':start_searches,
                'decisions':len(self.history)}

    def run_expedition(self, world, expedition_id, destination, team, map_id,
                       objective, max_steps=100, vehicle_id=None):
        """Joga uma expedição regional a pé, incluindo ida, mapa e retorno.

        Viagens por cartas e direção de veículos ficam fora deste executor
        enquanto suas regras regionais não forem aprovadas. A decisão nunca
        fornece combustível e usa somente as APIs públicas de World/TacticalGame.
        """
        if not world.continuous_campaign:
            raise ValueError('Controlador exige migração verificada da Cisterna')
        if vehicle_id is not None:
            raise ValueError('Controlador regional aguarda regra aprovada de combustível/veículos')
        map_data=TACTICS.get('maps',{}).get(map_id)
        if (map_data is None or map_data.get('reference_only')
                or (map_data.get('location') and map_data['location']!=destination)
                or (destination=='EXP-LOC-06' and map_id!='military_installation')):
            raise ValueError('Mapa incompatível com a expedição regional')
        world.open_expedition(expedition_id,team,destination)
        outbound=[]
        while world.expeditions[expedition_id].remaining>0:
            outbound.append(world.advance_expedition(expedition_id))
        tactical=TacticalGame.start(world,expedition_id,map_id)
        local=self.run_objective(tactical,objective,max_steps)
        if local['status']!='objective_completed_and_exited':
            if expedition_id in world.encounters:
                emergency=tactical.emergency_return(
                    f'Controlador interrompido: {local.get("reason",local["status"])}')
                return {'status':'local_defeat_emergency','outbound':outbound,
                        'local':local,'emergency':emergency,'return':[]}
            return {'status':'blocked_before_return','outbound':outbound,
                    'local':local,'return':[]}
        world.begin_return(expedition_id)
        returning=[]
        while expedition_id in world.expeditions:
            returning.append(world.advance_expedition(expedition_id))
        return {'status':'returned','outbound':outbound,'local':local,
                'return':returning,'decisions':list(self.history)}
