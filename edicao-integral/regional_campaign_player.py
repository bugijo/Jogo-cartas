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

from arc2 import Arc2
from integrated_campaign import IntegratedCampaign
from regional_player import AdaptiveRegionalPlayer
from system import LOCATIONS, REGIONAL_CONTACTS

MARKET = 'EXP-LOC-02'
STATION = 'EXP-LOC-05'
CLUE_ORDER = ('EXP-NPC-02', 'EXP-NPC-14')  # Célia, depois Vicente (ordem provisória)


def _collected(world, npc_id):
    evidence = REGIONAL_CONTACTS['contacts'][npc_id]['evidence']['id']
    return any(row.get('action') == 'collect_regional_evidence'
               and row.get('evidence_id') == evidence for row in world.log)


class RegionalCampaignPlayer:
    """Política determinística de amanhecer sobre o estado observável."""

    def __init__(self, food_days=2, market_searches=2):
        self.food_days = food_days  # reserva-alvo de comida em dias de consumo
        self.market_searches = market_searches  # buscas máximas por ida ao Mercado
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

    def plan(self, world):
        """Escolhe o objetivo do dia. Retorna (tipo, destino, mapa, objetivos)."""
        consumers = len(world.meal_people())
        food_short = world.stock['food'] < self.food_days * consumers
        if food_short and world.searches[MARKET] > 0:
            searches = min(world.searches[MARKET], self.market_searches)
            objectives = [{'kind': 'search', 'zone': 5, 'searches': min(2, searches)}]
            if searches > 2:
                objectives.append({'kind': 'search', 'zone': 12,
                                   'searches': min(2, searches - 2)})
            return ('supply', MARKET, 'market_intro', objectives)
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
        if world.flags.get('radio_code') and world.flags.get('access_card'):
            self._block(world, 'military_fuel_rule_pending',
                        'Instalação militar exige veículo e combustível regional '
                        '(regra pendente de aprovação)')
        return ('rest', None, None, None)

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
        elif kind in ('clue', 'access_card') and not self.ready_for_far(world, team):
            # Estação é longe: só sai com a equipe inteira descansada e curada.
            kind = 'rest'
            record['rest_reason'] = 'recuperar ferimentos/fadiga antes da Estação'
        if (kind == 'rest' and world.stock['food'] < len(world.meal_people())
                and world.searches[MARKET] <= 0):
            self._block(world, 'no_mapped_food_source',
                        'Mercado esgotado; nenhum outro local com mapa tático dá comida')
        record['plan'] = kind
        if kind != 'rest':
            expedition_id = f'campaign-day{world.day}-{kind}'
            player = AdaptiveRegionalPlayer('explorer' if kind == 'supply' else 'stealth')
            try:
                result = player.run_expedition(world, expedition_id, destination, team,
                                               map_id, objectives, max_steps=80)
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
