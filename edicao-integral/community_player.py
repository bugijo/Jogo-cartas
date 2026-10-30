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

import camp
import community
from regional_campaign_player import CampRegionalPlayer
from system import STRUCTURES

FOOD_ACTIVITY = {'cacador': 'caca', 'coletor': 'coleta',
                 'agricultor': 'coleta'}


class CommunityRegionalPlayer(CampRegionalPlayer):
    BUILD_ORDER = ('garden', 'storage', 'lodging', 'watch', 'infirmary', 'workshop',
                   'reservoir')

    def __init__(self, *args, options=('priority', 'build'), trips=True,
                 community_builds=('canteiro', 'coletor', 'canteiro', 'cozinha'),
                 max_days=3, risk='covered',
                 per_day_choice=False, dogs=True, accept='beds', growth=True,
                 edge='short', horta_target=6, horta_per_adult=2, tents_first=False,
                 no_market=False, water_days=1.0, **kwargs):
        super().__init__(*args, options=options, risk=risk, **kwargs)
        self.accept = accept
        self.horta_target = horta_target
        self.horta_per_adult = horta_per_adult
        self.tents_first = tents_first  # situação A: barracas antes da produção
        self.no_market = no_market      # situação G: sem Mercado nem Horta abandonada
        self.water_days = water_days    # viagem de água abaixo de N noites de água
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
        if self.no_market:
            return None
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
    def _wanted(self, world):
        if camp.on(world):
            return self._camp_wishes(world)
        state = world.community
        wanted = list(self.community_builds)
        for done_kind in state['built']:
            if done_kind in wanted:
                wanted.remove(done_kind)
        if self.growth:
            wanted = self._growth_builds(world, wanted)
        return wanted

    def _camp_wishes(self, world):
        """Acampamento em lotes: cama para quem chega, horta para quem trabalha,
        expansão quando falta lote; o resto (coletor, cozinha) depois."""
        state = world.community
        lots = state['camp']
        wishes = []
        humans = world.residents + len((state['arrival'] or {}).get('people', []))
        if humans > world.beds:
            wishes.append('barraca')
        adults = [p for p in community.workers(world) if p not in world.npcs]
        horta = camp.built(world, 'horta') + ('horta' in state['projects'])
        target = min(self.horta_target, self.horta_per_adult * max(1, len(adults)))
        if self.tents_first and world.day < 6:
            wishes.insert(0, 'barraca')  # situação A: abrigar antes de produzir
            target = 0
        if horta < target:
            wishes.append('horta')
        if horta >= 1 and 'coletor' not in state['built']:
            wishes.append('coletor')
        if 'cozinha' not in state['built'] and 'cozinha' in self.community_builds:
            wishes.append('cozinha')
        for kind in ('composteira', 'filtro', 'defumador', 'bancada', 'ambulatorio'):
            spec = community.STRUCTURES[kind]
            required = spec.get('requires')
            if (spec['knowledge'] in lots['knowledge'] and kind not in state['built']
                    and (not required or required in world.structures)):
                wishes.append(kind)
        blocked = [k for k in wishes if not camp.can_claim(world, k)]
        nxt = f"expansao{lots['level'] + 1}"
        if blocked and nxt in community.STRUCTURES:
            spec = community.STRUCTURES[nxt]
            if spec.get('requires_any') and not any(k in world.structures
                                                    for k in spec['requires_any']):
                wishes = [k for k in wishes if k not in blocked]
            else:
                wishes = [nxt] + [k for k in wishes if k not in blocked]
        else:
            wishes = [k for k in wishes if k not in blocked]
        return [k for k in wishes if k not in state['projects']]

    CAMP_BUILD_ORDER = ('storage', 'watch', 'workshop', 'infirmary', 'reservoir', 'lodging')

    def _build(self, world, team):
        """Em lotes: obra EXP-BLD só quando a Comunidade não espera madeira;
        Depósito e Vigia primeiro (estoque e defesa final)."""
        if world.community is not None and camp.on(world):
            urgent = [k for k in self._camp_wishes(world)
                      if k in ('barraca', 'horta') or k.startswith('expansao')]
            if not world.projects and (world.community['projects'] or urgent):
                return {}
            order, self.BUILD_ORDER = self.BUILD_ORDER, self.CAMP_BUILD_ORDER
            try:
                return super()._build(world, team)
            finally:
                self.BUILD_ORDER = order
        return super()._build(world, team)

    def _wood_target(self, world):
        state = world.community
        if not world.projects and not camp.on(world):
            kind = next((k for k in self.BUILD_ORDER if k not in world.structures), None)
            if kind:
                return STRUCTURES[kind]['cost'].get('wood', 0)
        wanted = self._wanted(world)
        if camp.on(world) and not wanted and not world.projects:
            kind = next((k for k in self.BUILD_ORDER if k not in world.structures
                         and k != 'garden'), None)
            if kind:
                return STRUCTURES[kind]['cost'].get('wood', 0)
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
            beds = world.beds
            tent = state['arrival'].get('tent')
            if camp.on(world) and tent and camp.free_lot(world, 'barraca', tent):
                beds += camp.RULES['beds'][tent]  # a família monta a própria barraca
            accept = community.arrival_fits(world) and (
                self.accept == 'fits'
                or (self.accept == 'beds' and world.residents + arriving <= beds)
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
            # Um herói pode estar nas duas listas (livres e heróis): só uma função por dia.
            people[:] = [p for p in people if p not in state['jobs']]
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
        wanted = self._wanted(world)
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
        # Em lotes, obra leve (horta, barraca) vale o investimento com meia noite coberta.
        half = world.stock['food'] >= consumers // 2
        if targets and (covered or (camp.on(world) and half)):
            for target in targets:
                spec = community.STRUCTURES.get(target, {}) if target in state['projects'] else {}
                if camp.work_allowed(world, target, spec):
                    continue
                # Em lotes: a expansão é um mutirão (até o trabalho que falta, 3 pessoas).
                crew = 1
                if camp.on(world) and spec.get('expansion'):
                    crew = min(3, spec['work'] - state['projects'][target])
                for _ in range(crew):
                    worker = take(free, 'obra') or take(heroes, 'obra')
                    if not worker:
                        break
                    community.assign_job(world, worker, 'obra', target)
                    done.setdefault('community', []).append((worker, 'obra', target))
        # 2a. horta por lotes: agricultor primeiro, até cobrir os lotes prontos
        if camp.on(world):
            # Dia seco: rega só com a água que sobra acima da bebida desta noite.
            spare = world.stock['water'] - consumers
            lots_left = len(camp.ready_horta(world))
            while free and lots_left > 0:
                if not state['camp']['rain'] and spare < 1:
                    break
                farmer = any(community.specialist(world, p, 'horta') for p in free)
                if lots_left < camp.HORTA['lots_per_worker'] and not farmer:
                    break  # 1 lote rende menos que uma viagem: fica sem cuidado hoje
                worker = take(free, 'horta')
                try:
                    community.assign_job(world, worker, 'horta')
                except ValueError:
                    free.insert(0, worker)
                    break
                cap = (camp.HORTA['specialist_lots'] if community.specialist(world, worker, 'horta')
                       else camp.HORTA['lots_per_worker'])
                tended = min(cap, lots_left)
                lots_left -= tended
                if not state['camp']['rain']:
                    spare -= -(-tended // camp.HORTA['lots_per_water'])
                done.setdefault('community', []).append((worker, 'horta'))
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
                free_boil = ('reservoir' in world.structures or camp.has(world, 'filtro')
                             or (world.continuity_filter or {}).get('active'))
                water_trip = any(t['activity'] == 'agua' for t in state['trips'])
                if (activity is None and camp.on(world) and free_boil and not water_trip
                        and world.stock['water'] < self.water_days * consumers):
                    activity, days = 'agua', min(2, self.max_days)  # rio, sem ferver
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
        # 3b. remédio no Ambulatório quando o estoque de remédio acaba
        if (free and camp.has(world, 'ambulatorio') and world.stock['medicine'] < 2
                and world.stock['food'] > consumers + camp.EFFECTS['remedio_food']):
            person = take(free, 'cuidar')
            community.assign_job(world, person, 'remedio')
            done.setdefault('community', []).append((person, 'remedio'))
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
