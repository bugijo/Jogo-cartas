"""Campanha regional contínua de vários dias (Última Transmissão).

Cada dia: decide no amanhecer pelo estado visível, joga no máximo uma expedição
com `AdaptiveRegionalPlayer` (cartas de Viagem e Emboscadas incluídas), encerra
o dia com prioridade explícita de comida e água e salva/carrega a campanha.
Só usa ações públicas de World/TacticalGame/Arc2; nunca escreve estado, nunca
fornece combustível nem decide regras pendentes — registra o bloqueio e segue.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import community
from arc2 import Arc2
from integrated_campaign import IntegratedCampaign
from regional_player import AdaptiveRegionalPlayer
from system import ITEMS, LOCATIONS, REGIONAL_CONTACTS, VEHICLES

MARKET = 'EXP-LOC-02'
STATION = 'EXP-LOC-05'
GARDEN_EDGE = 'EXP-LOC-01'
POSTO = 'EXP-LOC-07'
MILITARY = 'EXP-LOC-06'
VAN = 'EXP-VEI-02'
# Local de comida → (mapa tático, zonas de busca). A Horta abandonada só existe
# na edição integral (regras Comunidade); os replays certificados não a veem.
FOOD_SITES = {MARKET: ('market_intro', (5, 12)), GARDEN_EDGE: ('garden_edge_01', (6, 11))}
CLUE_ORDER = ('EXP-NPC-02', 'EXP-NPC-14')  # Célia, depois Vicente (ordem provisória)


def _collected(world, npc_id):
    evidence = REGIONAL_CONTACTS['contacts'][npc_id]['evidence']['id']
    return any(row.get('action') == 'collect_regional_evidence'
               and row.get('evidence_id') == evidence for row in world.log)


class RegionalCampaignPlayer:
    """Política determinística de amanhecer sobre o estado observável."""

    def __init__(self, food_days=2, market_searches=2, discard_water=False):
        self.food_days = food_days  # reserva-alvo de comida em dias de consumo
        self.market_searches = market_searches  # buscas máximas por ida ao Mercado
        self.discard_water = discard_water  # descarte voluntário para a colheita caber
        self.days: list[dict] = []
        self.blockers: list[dict] = []

    # --- decisões de amanhecer -------------------------------------------------
    @staticmethod
    def team(world):
        return [hero for hero, state in sorted(world.heroes.items())
                if state['location'] == 'camp' and state['health'] > 0
                and state.get('fatigue', 0) < 3 and hero not in world.worked_today]

    @staticmethod
    def ready_for_far(world, team):
        able = [hero for hero in sorted(world.heroes) if world.heroes[hero]['health'] > 0]
        return (team == able and len(team) >= 2
                and all(world.heroes[hero]['health'] >= 3
                        and world.heroes[hero].get('fatigue', 0) <= 1 for hero in team))

    def next_clue(self, world):
        if world.flags.get('radio_code'):
            return None
        for npc in CLUE_ORDER:
            if _collected(world, npc):
                continue
            if world.regional_contact_identity_available(npc, STATION):
                return npc
        return None

    def food_site(self, world):
        """Local de comida com mapa e buscas: Mercado; depois a Horta abandonada."""
        if world.searches[MARKET] > 0:
            return MARKET
        if world.community is not None and world.searches[GARDEN_EDGE] > 0:
            return GARDEN_EDGE
        return None

    def plan(self, world):
        """Escolhe o objetivo do dia. Retorna (tipo, destino, mapa, objetivos)."""
        consumers = len(world.meal_people())
        food_short = world.stock['food'] < self.food_days * consumers
        site = self.food_site(world)
        if food_short and site:
            map_id, (first, second) = FOOD_SITES[site]
            searches = min(world.searches[site], self.market_searches)
            objectives = [{'kind': 'search', 'zone': first, 'searches': min(2, searches)}]
            if searches > 2:
                objectives.append({'kind': 'search', 'zone': second,
                                   'searches': min(2, searches - 2)})
            return ('supply', site, map_id, objectives)
        npc = self.next_clue(world)
        if npc:
            return ('clue', STATION, 'station_02',
                    [{'kind': 'investigate_contact', 'npc': npc},
                     {'kind': 'evidence', 'npc': npc}])
        if world.flags.get('radio_code') and not world.flags.get('access_card'):
            if world.searches[STATION] > 0:
                return ('access_card', STATION, 'station_02',
                        [{'kind': 'search', 'zone': 5}, {'kind': 'access_card'}])
            self._block(world, 'access_card_no_search_left',
                        'Cartão exige busca na Estação e as buscas acabaram')
        if (world.flags.get('radio_code') and world.flags.get('access_card')
                and 'access_card' in world.special_stock):
            ending = self.endgame(world)
            if ending:
                return ending
        if world.flags.get('radio_code') and world.flags.get('access_card'):
            if world.final_defense is not None:
                return ('rest', None, None, None)
            if world.community is not None:
                self._block(world, 'endgame_stalled',
                            'Fim de campanha sem passo legal (bateria perdida, '
                            'combustível esgotado ou cartão fora do abrigo)')
                return ('rest', None, None, None)
            self._block(world, 'military_fuel_rule_pending',
                        'Instalação militar exige veículo e combustível regional '
                        '(regra pendente de aprovação)')
        return ('rest', None, None, None)

    def endgame(self, world):
        """Edição integral (D-22): bateria → van no Posto → Instalação → defesa."""
        if world.community is None or world.final_defense is not None:
            return None  # a defesa final acontece uma vez (vencida ou perdida)
        if 'transmitter' in world.special_stock:
            alive = [s for s in world.heroes.values() if s['health'] > 0]
            ready = all(s['location'] == 'camp' and s['health'] >= 2
                        and s.get('fatigue', 0) == 0 and not s.get('hungry') for s in alive)
            self.maintain_weapons(world)
            if not ready:  # a defesa é uma só: esperar a equipe descansada
                self._kind = None
                return ('rest', None, None, None)
            self._kind = 'defense'
            return ('defense', None, None, None)
        van = world.vehicles.get(VAN)
        posto = world.site_states.get(POSTO, {})
        taken = {int(card.rsplit(':', 1)[-1]) for card in posto.get('fuel_cards_taken', [])}
        fuel = [{'kind': 'fuel', 'zone': 7, 'lot': lot} for lot in range(1, 9)
                if lot not in taken][:world.searches[POSTO]]
        if not world.flags.get('truck_tank_drained'):
            fuel.append({'kind': 'truck_tank', 'zone': 14})
        # Visitas curtas ao Posto (o relógio e a horda crescem a cada rodada):
        # com o conserto, só 2 cartas (o bastante para voltar dirigindo); a
        # pé, até 3 itens, tanque primeiro (rende 4).
        cards = [o for o in fuel if o['kind'] == 'fuel']
        tank = [o for o in fuel if o['kind'] == 'truck_tank']
        short = (tank + cards)[:3]
        if not (van and van['location'] == 'camp' and van['health'] > 0):
            if (van and van['location'] == POSTO and van['health'] > 0
                    and posto.get('van_state') == 'operational'):
                if not short:
                    return None
                self._kind = 'van'  # consertada antes: buscar combustível e voltar dirigindo
                return ('van', POSTO, 'gas_station_02', short)
            if 'battery' not in world.special_stock:
                if 'battery' in world.unique_items_at_sites.get('EXP-LOC-03', []):
                    self._kind = 'battery'
                    return ('battery', 'EXP-LOC-03', 'workshop_02',
                            [{'kind': 'battery', 'zone': 7}])
                return None
            self._kind = 'van'
            return ('van', POSTO, 'gas_station_02',
                    [{'kind': 'inspect_van', 'zone': 7}, {'kind': 'repair_van', 'zone': 7}]
                    + cards[:2])
        need = (2 * community.vehicle_trechos(world, LOCATIONS[MILITARY]['distance'])
                * VEHICLES[VAN]['fuel_per_segment'])
        if world.stock['fuel'] < need:
            if not fuel:
                return None
            self._kind = 'fuel'
            return ('fuel', POSTO, 'gas_station_02', short)
        self._kind = 'military'
        return ('military', MILITARY, 'military_installation',
                [{'kind': 'transmitter', 'zone': 6}])

    @staticmethod
    def maintain_weapons(world):
        """Véspera da defesa: 1 sucata por arma gasta, a mais gasta primeiro."""
        worn = sorted((item['durability'], hero, iid)
                      for hero, gear in sorted(world.gear.items())
                      if world.heroes[hero]['health'] > 0
                      for iid, item in sorted(gear.items())
                      if item['slot'] == 'hand' and ITEMS[item['template']].get('combat')
                      and item['durability'] < ITEMS[item['template']]['durability'])
        done = set()
        for _, hero, iid in worn:
            if hero in done or world.stock['scrap'] < 1:
                continue
            try:
                community.maintain_weapon(world, hero, iid)
                done.add(hero)
            except ValueError:
                continue

    def run_defense(self, world):
        """Defesa final no abrigo: atacar o mais próximo ao alcance, senão segurar Z1."""
        arc = Arc2(world)
        arc.final_defense()
        for _ in range(40):
            defense = world.final_defense
            if defense['status'] != 'active':
                break
            for hero in sorted(defense['heroes']):
                state = world.heroes[hero]
                weapons = [iid for iid, item in sorted(world.gear[hero].items())
                           if item['slot'] == 'hand' and item['durability'] > 0
                           and ITEMS[item['template']].get('combat')]
                while state['health'] > 0 and state['actions'] > 0 and defense['enemies']:
                    zone = defense['heroes'][hero]
                    target = None
                    for iid in weapons:
                        if world.gear[hero][iid]['durability'] < 1:
                            continue
                        reach = ITEMS[world.gear[hero][iid]['template']]['combat'].get('range', 1)
                        near = [(arc._distance(zone, e['zone']), eid)
                                for eid, e in sorted(defense['enemies'].items())]
                        near = [pair for pair in near if pair[0] <= reach]
                        if near:
                            target = (iid, min(near)[1])
                            break
                    if target:
                        arc.defense_attack(hero, *target)
                    elif zone < 4 and weapons:
                        arc.defense_move(hero, zone + 1)
                    else:
                        break
            arc.defense_activate()
        return dict(world.final_defense)

    def _block(self, world, code, reason):
        if not any(row['code'] == code for row in self.blockers):
            self.blockers.append({'day': world.day, 'code': code, 'reason': reason})

    @staticmethod
    def meal_plan(world):
        """Prioridade: maior sequência de privação primeiro, heróis antes, id."""
        people = world.meal_people()
        order = sorted(people, key=lambda key: (-people[key].get('streak', 0),
                                                 key not in world.heroes, key))
        return {'food_priority': order, 'water_priority': list(order)}

    @staticmethod
    def garden_worker(world, kind):
        """Horta da Cisterna: adulto apto primeiro; herói só em dia de descanso."""
        garden = world.continuity_garden
        if garden is None or not garden['active'] or garden['worker'] is not None:
            return None
        for person in world.continuity_people:
            if (person['kind'] == 'adult' and person.get('wounds', 0) < 3
                    and person.get('fatigue', 0) < 3 and not person.get('hungry')
                    and not person.get('thirsty')
                    and person['id'] not in world.worked_today):
                return person['id']
        if kind != 'rest':
            return None
        return next((hero for hero, state in sorted(world.heroes.items())
                     if state['location'] == 'camp' and state['health'] > 0
                     and state.get('fatigue', 0) < 3 and not state.get('hungry')
                     and not state.get('thirsty') and hero not in world.worked_today
                     and hero not in world.departed_today), None)

    def camp_work(self, world, kind, team):
        """Gancho de amanhecer para trabalhos do acampamento (base: nenhum)."""
        return None

    # --- um dia ------------------------------------------------------------------
    def play_day(self, world):
        dawn = {'day': world.day, 'stock': dict(world.stock), 'clues': world.clues,
                'heroes': {hero: {key: state.get(key) for key in
                                  ('health', 'fatigue', 'hungry', 'thirsty')}
                           for hero, state in sorted(world.heroes.items())}}
        record = {'day': world.day, 'dawn': dawn}
        if world.partial_defeat:
            record['result'] = 'partial_defeat'
            return record
        if not world.flags.get('radio_code') and world.clues >= 2:
            Arc2(world).decode_radio()
            record['radio_decoded'] = True
        kind, destination, map_id, objectives = self.plan(world)
        team = self.team(world)
        if kind != 'rest' and not team:
            kind = 'rest'
            record['rest_reason'] = 'sem herói apto (fadiga 3 ou ferido)'
        elif (kind in ('clue', 'access_card', 'military', 'battery', 'van', 'fuel')
              and not self.ready_for_far(world, team)):
            # Estação é longe: só sai com a equipe inteira descansada e curada.
            kind = 'rest'
            record['rest_reason'] = 'recuperar ferimentos/fadiga antes da Estação'
        if (kind == 'rest' and world.stock['food'] < len(world.meal_people())
                and self.food_site(world) is None):
            self._block(world, 'no_mapped_food_source',
                        'Mercado esgotado; nenhum outro local com mapa tático dá comida'
                        if world.community is None else
                        'Mercado esgotado e Horta abandonada sem busca')
        worker = self.garden_worker(world, kind)
        if worker:
            world.assign_continuity_garden(worker, self.discard_water)
            record['garden_worker'] = worker
        camp = self.camp_work(world, kind, team if kind != 'rest' else [])
        if camp:
            record['camp'] = camp
        record['plan'] = kind
        if kind == 'defense':
            record['defense'] = self.run_defense(world)
        elif kind != 'rest':
            expedition_id = f'campaign-day{world.day}-{kind}'
            player = AdaptiveRegionalPlayer('explorer' if kind == 'supply' else 'stealth')
            extra = {}
            if kind == 'van':
                extra = {'special_items': [i for i in ('battery',) if i in world.special_stock],
                         'return_vehicle_id': VAN}
            try:
                if kind == 'military':
                    Arc2(world).authorize_installation(expedition_id, team, VAN)
                    extra = {'opened': True}
                result = player.run_expedition(world, expedition_id, destination, team,
                                               map_id, objectives, max_steps=80, **extra)
            except NotImplementedError as exc:
                self._block(world, 'road_emergency_with_unique_cargo', str(exc))
                record['result'] = 'blocked_rule'
                record['reason'] = str(exc)
                return record
            except ValueError as exc:
                if expedition_id in world.expeditions:
                    raise  # recusa após abrir é defeito, não decisão legal
                record['result'] = 'expedition_refused'
                record['reason'] = str(exc)
            else:
                record['expedition'] = {
                    'id': expedition_id, 'destination': destination, 'team': team,
                    'status': result['status'],
                    'local': (result.get('local') or {}).get('status'),
                    'travel': [row for row in player.history
                               if row['action'] in ('regional_ambush', 'travel_choice')],
                }
                delivered = next((row['delivered'] for row in reversed(world.log)
                                  if row.get('expedition') == expedition_id
                                  and 'delivered' in row), None)
                record['expedition']['delivered'] = delivered
        night = world.end_day(self.meal_plan(world))
        record['night'] = {key: night[key] for key in
                           ('missing', 'unfed', 'crisis', 'partial_defeat')}
        record['clock_reset'] = world.regional_clock == 0
        if 'garden_food' in night:
            record['night']['garden_food'] = night['garden_food']
        record['clues'] = world.clues
        record['radio_code'] = bool(world.flags.get('radio_code'))
        record['access_card'] = bool(world.flags.get('access_card'))
        return record

    # --- campanha ----------------------------------------------------------------
    def run(self, campaign, days, save_dir=None):
        """Joga `days` dias, salvando e recarregando a campanha a cada amanhecer.

        O dia seguinte continua do mundo recarregado; divergência entre o estado
        salvo e o recarregado interrompe a campanha.
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(save_dir or directory) / 'regional_campaign.json'
            for _ in range(days):
                record = self.play_day(campaign.world)
                self.days.append(record)
                campaign.save(path)
                reloaded = IntegratedCampaign.load(path)
                if reloaded.world.__dict__ != campaign.world.__dict__:
                    raise AssertionError('Save/load divergiu no fim do dia')
                campaign = reloaded
                if record.get('result') in ('partial_defeat', 'blocked_rule'):
                    break
                if campaign.world.partial_defeat:
                    self.days.append({'day': campaign.world.day,
                                      'result': 'partial_defeat'})
                    break
        return campaign

    @staticmethod
    def location_food():
        """Locais com comida no loot (para relatório de bloqueio)."""
        return sorted(key for key, loc in LOCATIONS.items() if loc['loot'].get('food'))


class StrategicRegionalPlayer(RegionalCampaignPlayer):
    """Controlador experimental de médio prazo (não muda regras).

    O controlador base vai ao Mercado sempre que a comida está abaixo de dois
    dias de consumo; com oferta menor que o consumo isso nunca termina e a
    Estação não é tentada. Este equilibra, só com estado observável:
    - pista quando a noite de hoje está coberta; com `risk='short'`, também
      quando ninguém está com privação em sequência (uma noite curta não leva
      a Colapso);
    - equipe de longe = heróis com Vida >= 2 e fadiga <= 1 (os demais ficam);
    - Mercado com buscas proporcionais ao déficit de dois dias;
    - descanso quando menos de dois heróis estão aptos para ir longe.
    """

    def __init__(self, *args, risk='covered', **kwargs):
        super().__init__(*args, **kwargs)
        self.risk = risk  # 'covered': pista só com a noite coberta; 'short': aceita uma noite curta
        self._kind = None

    @staticmethod
    def far_team(world):
        return [hero for hero, state in sorted(world.heroes.items())
                if state['location'] == 'camp' and state['health'] >= 2
                and state.get('fatigue', 0) <= 1 and not state.get('hungry')
                and hero not in world.worked_today]

    def team(self, world):
        if self._kind in ('clue', 'access_card', 'military', 'battery', 'van', 'fuel'):
            return self.far_team(world)
        if self._kind == 'defense':
            return [h for h, s in sorted(world.heroes.items())
                    if s['location'] == 'camp' and s['health'] > 0]
        return RegionalCampaignPlayer.team(world)

    def ready_for_far(self, world, team):
        return len(team) >= 2

    def _supply(self, world, consumers):
        site = self.food_site(world)
        map_id, (first, second) = FOOD_SITES[site]
        food_per_search = max(1, LOCATIONS[site]['loot'].get('food', 1))
        deficit = max(1, self.food_days * consumers - world.stock['food'])
        searches = min(world.searches[site], 4, -(-deficit // food_per_search))
        objectives = [{'kind': 'search', 'zone': first, 'searches': min(2, searches)}]
        if searches > 2:
            objectives.append({'kind': 'search', 'zone': second, 'searches': searches - 2})
        return ('supply', site, map_id, objectives)

    def plan(self, world):
        consumers = len(world.meal_people())
        people = world.meal_people()
        covered = world.stock['food'] >= consumers
        safe_short = max((p.get('streak', 0) for p in people.values()), default=0) == 0
        far = len(self.far_team(world)) >= 2
        npc = self.next_clue(world)
        progress = None
        if npc:
            progress = ('clue', STATION, 'station_02',
                        [{'kind': 'investigate_contact', 'npc': npc},
                         {'kind': 'evidence', 'npc': npc}])
        elif (world.flags.get('radio_code') and not world.flags.get('access_card')
              and world.searches[STATION] > 0):
            progress = ('access_card', STATION, 'station_02',
                        [{'kind': 'search', 'zone': 5}, {'kind': 'access_card'}])
        if progress and far and (covered or self.risk == 'short' and safe_short):
            self._kind = progress[0]
            return progress
        if world.stock['food'] < self.food_days * consumers and self.food_site(world):
            self._kind = 'supply'
            return self._supply(world, consumers)
        self._kind = None
        if progress:  # pista possível, mas sem equipe apta: recuperar
            return ('rest', None, None, None)
        return super().plan(world)


WORKSHOP = 'EXP-LOC-03'


class CampRegionalPlayer(StrategicRegionalPlayer):
    """Controlador experimental com as opções de acampamento (F, G, C2, D).

    Só usa ações públicas do World. `options` escolhe o que o grupo usa:
    'priority' (F), 'bridge' (G), 'forage' (C2), 'garden' (D). Os protótipos
    precisam estar ligados no World; o controlador não liga regra nenhuma.
    Ordem dos trabalhos no amanhecer, com quem não sai em expedição: obra da
    Horta (até 2), depois coleta (até o limite), adultos antes de heróis.
    """

    def __init__(self, *args, options=('priority', 'bridge', 'forage', 'garden'),
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.options = set(options)

    def _scrap_target(self, world):
        """Sucata que falta para a próxima obra (Horta D primeiro)."""
        if self._build_pending(world):
            return 2
        if 'build' in self.options and not world.projects:
            kind = next((k for k in self.BUILD_ORDER if k not in world.structures), None)
            from system import STRUCTURES
            # Sem madeira no estoque a obra não começa: não buscar sucata à toa.
            if kind and world.stock['wood'] >= STRUCTURES[kind]['cost'].get('wood', 0):
                return STRUCTURES[kind]['cost'].get('scrap', 0)
        return 0

    def _build_pending(self, world):
        return ('garden' in self.options and world.continuity_garden is None
                and (world.regional_camp or {}).get('garden_build') is None
                and world.regional_seeds_available() > 0)

    def _setup(self, world):
        """Decisões de chegada, antes do plano: prioridade F e ração-ponte G."""
        done = {}
        camp = world.regional_camp or {}
        if 'priority' in self.options and not camp.get('food_priority'):
            world.set_storage_priority(True)
            done['priority'] = True
        if ('bridge' in self.options and 'bridge' in camp.get('prototypes', [])
                and not camp.get('bridge_claimed')):
            done['bridge'] = world.claim_bridge_ration()['stored']
        self._arrival = done

    def plan(self, world):
        self._setup(world)
        consumers = len(world.meal_people())
        people = world.meal_people()
        safe_short = max((p.get('streak', 0) for p in people.values()), default=0) == 0
        if (world.stock['scrap'] < self._scrap_target(world)
                and world.searches[WORKSHOP] > 0
                and (world.stock['food'] >= consumers
                     or self.risk == 'short' and safe_short)):
            self._kind = 'scrap'
            searches = min(world.searches[WORKSHOP], 2)
            return ('scrap', WORKSHOP, 'workshop_02',
                    [{'kind': 'search', 'zone': 5, 'searches': searches}])
        return super().plan(world)

    def team(self, world):
        if self._kind == 'scrap':
            return RegionalCampaignPlayer.team(world)
        return super().team(world)

    def _free_people(self, world, team):
        adults = [p['id'] for p in world.continuity_people if p['kind'] == 'adult'
                  and p.get('wounds', 0) < 3 and p.get('fatigue', 0) < 3
                  and not p.get('hungry') and not p.get('thirsty')]
        # Medido no ciclo 11: poupar o herói ferido corta a coleta pela metade
        # e encurta a campanha (fome impede a recuperação §25 de qualquer modo).
        heroes = [h for h, s in sorted(world.heroes.items())
                  if s['location'] == 'camp' and s['health'] > 0
                  and s.get('fatigue', 0) < 3 and not s.get('hungry')
                  and not s.get('thirsty') and h not in team]
        return adults + heroes

    def camp_work(self, world, kind, team):
        done = dict(getattr(self, '_arrival', {}))
        self._arrival = {}
        camp = world.regional_camp or {}
        if (self._build_pending(world) and world.stock['scrap'] >= 2
                and 'garden_build' in camp.get('prototypes', [])):
            world.start_regional_garden()
            done['garden_started'] = True
        build = (world.regional_camp or {}).get('garden_build')
        for person in self._free_people(world, team):
            if build is None or build['done']:
                break
            try:
                world.work_regional_garden(person)
            except ValueError:
                continue
            done.setdefault('garden_build', []).append(person)
        if 'build' in self.options:
            built = self._build(world, team)
            if built:
                done['build'] = built
        if 'forage' in self.options and camp.get('forage') is not None:
            for person in self._free_people(world, team):
                try:
                    world.assign_forage(person)
                except ValueError as exc:
                    if 'Limite' in str(exc) or 'esgotado' in str(exc):
                        break
                    continue
                done.setdefault('forage', []).append(person)
        return done or None

    # Ordem de crescimento: comida passiva, depois espaço, defesa e o resto.
    BUILD_ORDER = ('garden', 'storage', 'watch', 'infirmary', 'workshop',
                   'lodging', 'reservoir')

    def _build(self, world, team):
        """Obras do acampamento (estruturas EXP-BLD) pela API pública do World.

        Começa a primeira estrutura da ordem que o estoque paga e põe heróis
        sem expedição nem trabalho hoje na obra (só heróis trabalham obras).
        """
        done = {}
        if not world.projects:
            for kind in self.BUILD_ORDER:
                if kind not in world.structures and world.start_project(kind):
                    done['started'] = kind
                    break
        for kind in list(world.projects):
            for hero in self._free_people(world, team):
                if hero not in world.heroes or kind not in world.projects:
                    continue
                try:
                    finished = world.work_project(kind, 1, hero)
                except ValueError:
                    continue
                done.setdefault('workers', []).append(hero)
                if finished:
                    done['finished'] = kind
        return done
