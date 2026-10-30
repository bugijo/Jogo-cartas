"""Controlador da comunidade: decisões de amanhecer que uma mesa humana tomaria.

Herda o controlador do acampamento (expedição tática dos heróis, Horta, obras
EXP-BLD) e acrescenta só ações públicas de `community.py`:

1. cozinhar carne que vai estragar (cozinheiro primeiro);
2. obra comunitária ou EXP-BLD em andamento, se a comida de hoje está coberta;
3. viagens automáticas: comida quando há menos de `food_days` dias de estoque,
   madeira quando a próxima obra precisa; 2 dias (3 quando o estoque cobre),
   ração só do que sobra acima da refeição desta noite;
4. armadilha com madeira sobrando; cuidados se há ferido e gente livre.

Nada aqui olha o futuro (dados, cartas, reservas escondidas): só estoque,
pessoas, profissões e reservas visíveis do entorno.
"""
from __future__ import annotations

import community
from regional_campaign_player import CampRegionalPlayer
from system import STRUCTURES

FOOD_ACTIVITY = {'cacador': 'caca', 'pescador': 'pesca', 'coletor': 'coleta',
                 'agricultor': 'coleta'}


class CommunityRegionalPlayer(CampRegionalPlayer):
    BUILD_ORDER = ('garden', 'storage', 'lodging', 'watch', 'infirmary', 'workshop',
                   'reservoir')

    def __init__(self, *args, options=('priority', 'build'), trips=True,
                 community_builds=('canteiro', 'coletor', 'canteiro', 'cozinha'),
                 max_days=3, risk='covered',
                 per_day_choice=False, dogs=True, accept='beds', growth=True,
                 edge='short', **kwargs):
        super().__init__(*args, options=options, risk=risk, **kwargs)
        self.accept = accept
        self.growth = growth
        self.edge = edge  # Horta abandonada: 'always', 'short' (noite descoberta), 'never'
        self.trips = trips
        self.community_builds = tuple(community_builds)
        self.max_days = max_days
        self.per_day_choice = per_day_choice
        self.dogs = dogs

    @staticmethod
    def garden_worker(world, kind):
        """Horta: adulto apto em casa primeiro (agricultor antes); herói em descanso."""
        garden = world.continuity_garden
        if world.community is None:
            return CampRegionalPlayer.garden_worker(world, kind)
        if garden is None or not garden['active'] or garden['worker'] is not None:
            return None
        adults = [p for p in community.workers(world)
                  if p not in world.npcs and community.able(world, p)]
        adults.sort(key=lambda p: not community.specialist(world, p, 'horta'))
        if adults:
            return adults[0]
        if kind != 'rest':
            return None
        return next((h for h in sorted(world.heroes)
                     if community.able(world, h) and world.heroes[h]['health'] > 0), None)

    def food_site(self, world):
        site = super().food_site(world)
        if site != 'EXP-LOC-01' or self.edge == 'always':
            return site
        if self.edge == 'short' and world.stock['food'] < len(world.meal_people()):
            return site
        return None

    @staticmethod
    def far_team(world):
        away = community.away(world) if world.community is not None else set()
        return [h for h in CampRegionalPlayer.far_team(world) if h not in away]

    def team(self, world):
        away = community.away(world) if world.community is not None else set()
        return [h for h in super().team(world) if h not in away]

    # --- alvos visíveis ----------------------------------------------------------
    def _wood_target(self, world):
        state = world.community
        if not world.projects:
            kind = next((k for k in self.BUILD_ORDER if k not in world.structures), None)
            if kind:
                return STRUCTURES[kind]['cost'].get('wood', 0)
        wanted = list(self.community_builds)
        for done_kind in state['built']:
            if done_kind in wanted:
                wanted.remove(done_kind)
        if self.growth:
            wanted = self._growth_builds(world, wanted)
        for kind in wanted:
            if kind not in state['projects']:
                return community.STRUCTURES[kind]['cost'].get('wood', 0)
        return 0

    def _expected_food(self, world, person, activity, days, planned):
        """Comida esperada (média do D6 = 3,5), pela reserva visível do entorno."""
        spec = community.ACTIVITIES[activity]
        bonus = community.TRIPS['specialist_bonus'] if community.specialist(
            world, person, activity) else 0
        units = int((3.5 + bonus) * days // spec['points_per_unit'])
        units = min(units, community.TRIPS['capacity'],
                    world.community['pools'][spec['pool']] - planned.get(spec['pool'], 0))
        if units <= 0:
            return 0
        if spec['output'] == 'meat':
            cook = world.stock['wood'] >= 1 or 'cozinha' in world.community['built']
            return units * community.RULES['meat'][
                'portions_cooked' if cook else 'portions_improvised']
        return units

    def _food_activity(self, world, person, days, planned):
        """(atividade, dias) com mais comida esperada por dia fora.

        Caça só rende carne com 2+ dias (4 pontos por carne), então entra com
        no mínimo 2 dias mesmo quando a noite de hoje não está coberta.
        """
        options = [(a, days) for a in ('pesca', 'coleta')]
        options.append(('caca', max(days, 2) if self.per_day_choice else days))
        options = [(a, min(d, self.max_days)) for a, d in options]

        def score(option):
            food = self._expected_food(world, person, option[0], option[1], planned)
            return (food / option[1] if self.per_day_choice else food, option[0])
        best = max(options, key=score)
        return best if score(best)[0] > 0 else (None, days)

    def _growth_builds(self, world, wanted):
        """Obras de crescimento quando o espaço visível aperta (D-20)."""
        state = world.community
        needs = []
        beds_short = (world.residents >= world.beds
                      or (state['arrival'] and not community.arrival_fits(world)))
        if beds_short and 'lodging' in world.structures and 'alojamento2' not in state['built']:
            needs.append('alojamento2')
        if 'storage' in world.structures and world.free_space('food') <= 4:
            needs.append('deposito2')
        upcoming = [k for k in wanted if k not in state['projects']][:1]
        need_terrain = max([community.STRUCTURES[k].get('terrain', 0) for k in upcoming]
                           + [STRUCTURES[k]['terrain'] for k in self.BUILD_ORDER
                              if k not in world.structures][:1] or [0])
        if (need_terrain > world.free_terrain
                and state['built'].count('cerca') < community.STRUCTURES['cerca']['max']):
            needs.append('cerca')
        return [k for k in needs if k not in state['built']] + wanted

    # --- amanhecer -----------------------------------------------------------------
    def camp_work(self, world, kind, team):
        done = super().camp_work(world, kind, team) or {}
        if world.community is None:
            return done or None
        state = world.community
        # 0. chegada de sobreviventes: acolher se houver cama (mais braços e bocas)
        if state['arrival']:
            arriving = len(state['arrival']['people'])
            accept = community.arrival_fits(world) and (
                self.accept == 'fits'
                or (self.accept == 'beds' and world.residents + arriving <= world.beds)
                or (self.accept == 'stock'
                    and world.stock['food'] >= len(world.meal_people()) + arriving))
            receipt = community.receive(world, accept)
            done.setdefault('community', []).append(('chegada', receipt['accepted'],
                                                     len(receipt['people'])))
        consumers = len(world.meal_people())
        covered = world.stock['food'] >= consumers
        free = [p for p in community.workers(world) if community.able(world, p)]
        if community.TRIPS.get('heroes_allowed'):
            # Variante para decisão do criador: heróis fora da expedição tática
            # de hoje também podem viajar (floresta/rio sem mapa tático).
            free += [h for h in sorted(world.heroes) if h not in team
                     and community.able(world, h, 1)]
        heroes = [h for h in sorted(world.heroes) if h not in team
                  and community.able(world, h)]

        def take(people, prefer=None):
            if prefer:
                for person in people:
                    if community.specialist(world, person, prefer):
                        people.remove(person)
                        return person
            return people.pop(0) if people else None

        # 1. carne crua: cozinhar hoje
        if state['meat']:
            cook = take(free, 'cozinhar') or take(heroes, 'cozinhar')
            if cook:
                community.assign_job(world, cook, 'cozinhar')
                done.setdefault('community', []).append((cook, 'cozinhar'))
        # 2. obras comunitárias
        wanted = list(self.community_builds)
        for done_kind in state['built']:
            if done_kind in wanted:
                wanted.remove(done_kind)
        if self.growth:
            wanted = self._growth_builds(world, wanted)
        for build in wanted:
            if build in state['projects']:
                break
            try:
                community.start_build(world, build)
                done.setdefault('community', []).append(('start', build))
            except ValueError:
                pass
            break
        targets = list(state['projects']) + list(world.projects)
        if targets and covered:
            for target in targets:
                worker = take(free, 'obra') or take(heroes, 'obra')
                if worker:
                    community.assign_job(world, worker, 'obra', target)
                    done.setdefault('community', []).append((worker, 'obra', target))
        # 2b. canteiros: um trabalhador por canteiro pronto (comida sem esgotar o entorno)
        for _ in range(state['built'].count('canteiro')):
            worker = take(free, 'horta')
            if not worker:
                break
            community.assign_job(world, worker, 'canteiro')
            done.setdefault('community', []).append((worker, 'canteiro'))
        # 3. viagens automáticas
        if self.trips:
            planned = {}
            for person in list(free):
                if not community.able(world, person, community.TRIPS['depart_max_wounds']):
                    continue
                stock_days = world.stock['food'] / max(1, consumers)
                need_wood = world.stock['wood'] < self._wood_target(world)
                activity = None
                wood_trip = any(t['activity'] == 'lenha' for t in state['trips'])
                if (world.stock['wood'] < 2 and not wood_trip and len(free) >= 2
                        and stock_days >= 1 and state['pools']['madeira'] >= 2):
                    activity = 'lenha'  # lenha para cozinhar a caça
                # Estoque não cobre a noite: volta amanhã; coberto: viagem longa.
                days = (1 if stock_days < 1 else 2 if stock_days < self.food_days
                        else self.max_days)
                days = min(days, self.max_days)
                if activity is None and stock_days < self.food_days:
                    activity, days = self._food_activity(world, person, days, planned)
                if activity is None and need_wood and state['pools']['madeira'] >= 2:
                    activity = 'lenha'
                if activity is None:
                    continue
                spec = community.ACTIVITIES[activity]
                if spec['pool']:
                    planned[spec['pool']] = planned.get(spec['pool'], 0) + int(
                        3.5 * days // spec['points_per_unit'])
                # A ração é a refeição de quem viaja (não come no abrigo): leva o
                # que houver, até um dia de ração por dia de viagem.
                dog = None
                if self.dogs and activity in ('caca', 'coleta', 'pesca'):
                    dog = next((p['id'] for p in world.continuity_people
                                if p['kind'] == 'dog' and p['id'] not in community.away(world)
                                and not p.get('hungry') and not p.get('thirsty')), None)
                try:
                    community.send_trip(world, person, activity, days, dog=dog)
                except ValueError:
                    continue      # o abrigo não pode ficar vazio
                free.remove(person)
                done.setdefault('community', []).append((person, 'viagem', activity, days))
        # 4. armadilha e cuidados
        if (free and world.stock['wood'] > self._wood_target(world)
                and len(state['traps']) < community.RULES['traps']['max']
                and state['pools']['caca'] > 0):
            person = take(free)
            community.assign_job(world, person, 'armadilha')
            done.setdefault('community', []).append((person, 'armadilha'))
        people = world.meal_people()
        if free and any(community._wounds(world, pid) > 0 for pid in people
                        if people[pid].get('kind') != 'dog'):
            person = take(free, 'cuidar')
            community.assign_job(world, person, 'cuidar')
            done.setdefault('community', []).append((person, 'cuidar'))
        return done or None
