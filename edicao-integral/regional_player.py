"""Jogador adaptativo de exploração regional usando somente APIs públicas."""
from collections import deque
from dataclasses import dataclass, field

from ambush02 import WEAPONS as AMBUSH_WEAPONS
from system import ITEMS, REGIONAL_CONTACTS
from tactics import TACTICS, TacticalGame
from arc2 import Arc2


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
        # A distinct low-contact policy avoids optional fights unless a threat
        # occupies an objective/exit zone; it is useful for long clue routes.
        'stealth': {'combat_distance': 0},
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
        if kind=='investigate_contact':
            npc=objective['npc']
            discovered=(npc in tactical.state.get('npc_contacts',{}) and any(
                row.get('action')=='investigate_physical_contact'
                and row.get('location')==tactical.world.expeditions[
                    tactical.id].destination
                and row.get('npc')==npc for row in tactical.world.log))
            if discovered:
                self.completed.add(key)
                return True
            self.completed.discard(key)
            return False
        if kind=='evidence':
            contact=REGIONAL_CONTACTS.get('contacts',{}).get(objective.get('npc'))
            evidence=contact.get('evidence') if contact else None
            collected=bool(evidence and any(
                row.get('action')=='collect_regional_evidence'
                and row.get('npc')==objective.get('npc')
                and row.get('evidence_id')==evidence['id']
                for row in tactical.world.log))
            if collected:
                self.completed.add(key)
                return True
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
        if kind=='fuel_cache' and tactical.state.get('fuel_cache_collected'):
            self.completed.add(key)
            return True
        if kind=='access_card' and tactical.world.flags.get('access_card'):
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
        if kind in ('zone','search','battery','fuel','fuel_cache','inspect_van','repair_van'):
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
            if kind=='fuel_cache':
                source=REGIONAL_CONTACTS.get('experimental_fuel',{})
                if (destination!=source.get('location')
                        or tactical.state['map']!=source.get('map')
                        or tactical.state.get('fuel_cache_collected')
                        or objective['zone']!=source.get('zone')):
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
        if kind=='access_card':
            if tactical.world.flags.get('access_card'):
                return []
            destination=tactical.world.expeditions[tactical.id].destination
            if 'access_card' in tactical.world.unique_items_at_sites.get(destination,[]):
                return list(tactical.state['search_zones'])  # cartão caído: recolher
            if not any(row.get('action')=='search'
                       and row.get('expedition')==tactical.id
                       and row.get('location')==tactical.world.expeditions[
                           tactical.id].destination for row in tactical.world.log):
                return []
            return list(tactical.state['search_zones'])
        if kind in ('contact','investigate_contact','evidence'):
            npc=objective['npc']
            contact=REGIONAL_CONTACTS.get('contacts',{}).get(npc)
            zone=tactical.state.get('npc_contacts',{}).get(npc)
            exp=tactical.world.expeditions[tactical.id]
            vehicle=(tactical.world.vehicles.get(exp.vehicle_id,{}) if exp.vehicle_id else None)
            seats=(vehicle['seats'] if vehicle else 6*len(exp.heroes))
            community=tactical.world
            if kind=='evidence':
                contact_legal=bool(not community.flags.get('radio_code')
                                    and npc in tactical.state.get('discovered_npcs',[]))
            elif kind=='investigate_contact':
                contact_legal=community.regional_contact_identity_available(
                    npc,exp.destination)
            else:
                contact_legal=(community.residents<community.beds
                               and community.stock['food']>=community.residents+1
                               and community.stock['water']>=community.residents+1
                               and len(exp.heroes)+len(exp.crew)+1<=seats
                               and community.regional_contact_identity_available(
                                   npc,exp.destination))
            if kind=='contact':
                available=zone is not None
            elif kind=='investigate_contact':
                available=(community.continuous_campaign and zone is None
                           and not community.flags.get('radio_code')
                           and contact is not None and contact.get('moment') in (
                               'post_cistern_pre_radio',
                               'post_cistern_pre_radio_if_not_in_community'))
            else:
                evidence=contact.get('evidence') if contact else None
                available=bool(evidence and npc in tactical.state.get('discovered_npcs', [])
                               and not self._objective_done(tactical,objective))
            if (contact and available and contact['map']==tactical.state['map']
                    and contact['location']==exp.destination and contact_legal):
                return [contact['zone'] if kind=='investigate_contact' else zone]
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
        if kind=='investigate_contact':
            result=tactical.investigate_contact(hero_id,objective['npc'])
            self.completed.add(self._key(tactical,objective))
            return {'action':'investigate_contact','hero':hero_id,'result':result}
        if kind=='evidence':
            result=tactical.collect_contact_evidence(hero_id,objective['npc'])
            self.completed.add(self._key(tactical,objective))
            return {'action':'collect_evidence','hero':hero_id,'result':result}
        if kind=='battery':
            tactical.pickup_unique_item(hero_id,'battery')
            self.completed.add(self._key(tactical,objective))
            return {'action':'pickup_unique','hero':hero_id,'item':'battery'}
        if kind=='fuel':
            result=tactical.pickup_fuel_card(hero_id,objective['lot'])
            self.completed.add(self._key(tactical,objective))
            return {'action':'pickup_fuel','hero':hero_id,'result':result}
        if kind=='fuel_cache':
            result=tactical.salvage_fuel_cache(hero_id)
            self.completed.add(self._key(tactical,objective))
            return {'action':'salvage_fuel_cache','hero':hero_id,'result':result}
        if kind=='access_card':
            Arc2(tactical.world).recover_access_card(tactical.id)
            self.completed.add(self._key(tactical,objective))
            return {'action':'recover_access_card','hero':hero_id,
                    'result':'access_card'}
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
        return 2 if objective.get('kind') in ('repair_van','fuel_cache') else 1

    def step(self, tactical, objective):
        """Executa uma decisão e devolve a trilha observável dessa ação."""
        kind=objective.get('kind')
        if tactical.id not in tactical.world.encounters:
            return {'action':'blocked','reason':'encontro já encerrado'}
        if tactical.state.get('round_closed'):
            return {'action':'blocked','reason':'relógio sem reserva de retorno'}
        if (objective.get('kind')=='exit'
                and all(zone==tactical.exit_zone
                        for zone in tactical.state['heroes'].values())
                and not any(enemy['zone']==tactical.exit_zone
                            for enemy in tactical.state['enemies'].values())):
            tactical.finish()
            decision={'action':'finish_encounter','returned_to_exit':True}
            self.history.append(decision)
            return decision
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
            available_actions=tactical.world.heroes[hero_id]['actions']
            for goal in targets:
                if zone==goal:
                    if kind!='exit' and not self._objective_done(tactical,objective) and \
                            available_actions>=self._action_cost(objective) \
                            and not (objective.get('kind')=='repair_van'
                                     and hero_id in tactical.state.get('van_attempts',[])) \
                            and not (kind in ('investigate_contact','evidence')
                                     and any(enemy['zone']==zone for enemy in
                                             tactical.state['enemies'].values())):
                        # Investigar/copiar exige zona sem ameaça (sem arma, espera ou sai).
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
                    door_cost=2 if door['blocked'] else 1
                    door_actionable=(available_actions>=door_cost and
                        (not door['blocked'] or any(
                            item['slot']=='hand' and item['durability']>0
                            and ITEMS[item['template']].get('breach',0)>0
                            for item in tactical.world.gear[hero_id].values())))
                # Prefer a short route through an openable printed door over
                # a very long detour around it. Door crossing still costs the
                # matching public action below.
                if closed_door and door_actionable and (open_path is None or
                                    len(route)<len(open_path)):
                    choices.append((len(route)-1,hero_id,goal,'door'))
                elif open_path:
                    move_cost=1+int(any(enemy['zone']==zone
                                        for enemy in tactical.state['enemies'].values()))
                    if available_actions>=move_cost:
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
                    if tactical.world.heroes[hero_id]['actions']<1:
                        return self._activate(tactical)
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

    def run_objectives(self, tactical, objectives, max_steps=120):
        """Resolve several legal objectives in one visit, then extract once."""
        if not isinstance(objectives,(list,tuple)) or not objectives:
            raise ValueError('A expedição exige ao menos um objetivo')
        start=len(self.history)
        incomplete_objective=False
        for objective in objectives:
            for _ in range(max_steps):
                if self._objective_done(tactical,objective):
                    break
                if (objective.get('kind')=='repair_van'
                        and tactical.state.get('van_state')=='incomplete'):
                    eligible={hero for hero in tactical.state['heroes']
                              if tactical.world.heroes[hero]['health']>0}
                    if eligible and eligible.issubset(
                            set(tactical.state.get('van_attempts',[]))):
                        # Each active hero gets at most one attempt per visit.
                        # Once all have failed, abandon this objective for now
                        # and use any remaining legal actions to extract.
                        incomplete_objective=True
                        break
                result=self.step(tactical,objective)
                if result['action']=='blocked':
                    if (objective.get('kind')=='repair_van'
                            and tactical.state.get('round_closed')):
                        incomplete_objective=True
                        break
                    return {'status':'blocked','reason':result['reason'],
                            'completed':[goal for goal in objectives
                                         if self._objective_done(tactical,goal)],
                            'decisions':self.history[start:]}
                if tactical.id not in tactical.world.encounters:
                    return {'status':'encounter_ended_before_all_objectives',
                            'completed':[goal for goal in objectives
                                         if self._objective_done(tactical,goal)],
                            'decisions':self.history[start:]}
            else:
                return {'status':'step_limit','completed':[goal for goal in objectives
                                    if self._objective_done(tactical,goal)],
                        'decisions':self.history[start:]}
            if incomplete_objective:
                break
        completed=[goal for goal in objectives
                   if self._objective_done(tactical,goal)]
        for _ in range(max_steps):
            if tactical.id not in tactical.world.encounters:
                break
            result=self.step(tactical,{'kind':'exit'})
            if result['action']=='blocked':
                return {'status':'blocked_during_extraction','reason':result['reason'],
                        'decisions':self.history[start:]}
        fully_completed=len(completed)==len(objectives)
        if tactical.id in tactical.world.encounters:
            status='step_limit'
        elif fully_completed:
            status='objective_completed_and_exited'
        else:
            status='objectives_incomplete_and_exited'
        return {'status':status,'completed':completed,
                'decisions':self.history[start:]}

    def run_objective(self, tactical, objective, max_steps=100):
        baseline=sum(row.get('action')=='search' and row.get('expedition')==tactical.id
                     for row in tactical.world.log)
        start_searches=objective.get('searches',1)
        key=self._key(tactical,objective)
        for _ in range(max_steps):
            if tactical.id not in tactical.world.encounters:
                completed=key in self.completed
                return {'status':('objective_completed_and_exited' if completed
                                  else 'objectives_incomplete_and_exited'),
                        'searches':sum(row.get('action')=='search'
                                       and row.get('expedition')==tactical.id
                                       for row in tactical.world.log)-baseline,
                        'objective_completed':completed}
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
                    key in self.completed else 'objective_not_completed')
        else:
            status='step_limit'
        count=sum(row.get('action')=='search' and row.get('expedition')==tactical.id
                  for row in tactical.world.log)-baseline
        return {'status':status,'searches':count,'requested_searches':start_searches,
                'decisions':len(self.history)}

    def _fight_ambush(self, world, expedition_id):
        """Emboscada no M1: segura a entrada Z1, ataca quem chega e sai limpo.

        Os dados vêm de World.regional_ambush_attack; o jogador só escolhe
        alvo e arma visíveis. Sem tempo, aceita a emergência de estrada.
        """
        ambush=world.start_regional_ambush(expedition_id)
        # Trechos ainda a pagar depois do atual (já pago ou extra sem segmento).
        legs_after=world.expeditions[expedition_id].remaining-1
        while True:
            if ambush.clock>=10 or ambush.clock+1+legs_after>10:
                # Outra rodada deixaria a equipe sem relógio para terminar a viagem.
                ambush.emergency_return()
                break
            ambush.begin_round()
            for hero in ambush.team:
                while ambush.ap.get(hero,0)>0 and ambush.wounds[hero]<3:
                    here=ambush.positions[hero]
                    foe=next((enemy for enemy in ambush.enemies
                              if enemy['zone']==here),None)
                    weapon=next((item for item in ambush.equipment[hero]
                                 if item in AMBUSH_WEAPONS),None)
                    if foe is None or weapon is None:
                        break
                    world.regional_ambush_attack(expedition_id,ambush,hero,
                                                 foe['id'],weapon)
            ambush.end_round()
            world.store_regional_ambush(expedition_id,ambush)
            if ambush.failed:
                if not ambush.returned:
                    ambush.emergency_return()
                break
            if (all(zone==1 for zone in ambush.positions.values())
                    and not any(enemy['zone']==1 for enemy in ambush.enemies)):
                ambush.finish()
                break
        result=world.finish_regional_ambush(expedition_id,ambush)
        self.history.append({'action':'regional_ambush','expedition':expedition_id,
                             'result':result,'rounds':ambush.round_no})
        return result

    def _advance(self, world, expedition_id):
        """Avança um trecho resolvendo cartas de Viagem pendentes (§29)."""
        while True:
            result=world.advance_expedition(expedition_id)
            if result!='travel_pending':
                return result
            event=world.expeditions[expedition_id].pending_travel
            if event.get('ambush'):
                if self._fight_ambush(world,expedition_id)=='emergency':
                    return 'road_emergency'
                continue
            choice=world.REGIONAL_TRAVEL_CHOICES[event['card_id']][0]
            world.resolve_regional_travel(expedition_id,choice)
            self.history.append({'action':'travel_choice','expedition':expedition_id,
                                 'card':event['card_id'],'choice':choice})

    def run_expedition(self, world, expedition_id, destination, team, map_id,
                       objective, max_steps=100, vehicle_id=None,
                       special_items=None, return_vehicle_id=None):
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
        world.open_expedition(expedition_id,team,destination,
                              special_items=special_items or [])
        outbound=[]
        while world.expeditions[expedition_id].remaining>0:
            outbound.append(self._advance(world,expedition_id))
            if outbound[-1]=='road_emergency':
                return {'status':'road_emergency_outbound','outbound':outbound,
                        'return':[],'decisions':list(self.history)}
        tactical=TacticalGame.start(world,expedition_id,map_id)
        local=(self.run_objectives(tactical,objective,max_steps)
               if isinstance(objective,(list,tuple)) else
               self.run_objective(tactical,objective,max_steps))
        if local['status'] not in ('objective_completed_and_exited',
                                   'objectives_incomplete_and_exited'):
            if expedition_id in world.encounters:
                emergency=tactical.emergency_return(
                    f'Controlador interrompido: {local.get("reason",local["status"])}')
                return {'status':'local_defeat_emergency','outbound':outbound,
                        'local':local,'emergency':emergency,'return':[]}
            return {'status':'blocked_before_return','outbound':outbound,
                    'local':local,'return':[]}
        return_vehicle=None
        if return_vehicle_id is not None:
            candidate=world.vehicles.get(return_vehicle_id)
            site=world.site_states.get(destination,{})
            if (candidate and candidate.get('location')==destination
                    and candidate.get('health',0)>0
                    and site.get('van_state')=='operational'):
                return_vehicle=return_vehicle_id
        world.begin_return(expedition_id,vehicle_id=return_vehicle)
        returning=[]
        while expedition_id in world.expeditions:
            returning.append(self._advance(world,expedition_id))
            if returning[-1]=='road_emergency':
                return {'status':'road_emergency_return','outbound':outbound,
                        'local':local,'return':returning,
                        'decisions':list(self.history)}
        status=('returned' if local['status']=='objective_completed_and_exited'
                else 'returned_with_objective_incomplete')
        return {'status':status,'outbound':outbound,'local':local,
                'return':returning,'return_vehicle':return_vehicle,
                'decisions':list(self.history)}
