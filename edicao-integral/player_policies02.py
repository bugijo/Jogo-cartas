"""Oito políticas programáticas para decisões públicas do núcleo parcial 0.2.

Elas não resolvem uma campanha: Viagem, Saque, resgate e transição ainda faltam.
Nenhuma política vê cartas futuras nem aceita recursos artificiais.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from collections import deque


PROFILES = (
    'Conservador', 'Explorador', 'Construtor', 'Combatente',
    'Líder', 'Iniciante', 'Oportunista', 'Adversarial',
)


def observe_campaign(game) -> dict:
    """Recorte público para decisões de campanha; não expõe baralhos futuros."""
    c = game.cistern
    remaining = {}
    for destination, state in game.site_states.items():
        remaining[destination] = len(state.get('search_deck', ()))
    from cistern_tactics02 import SEARCH_CARDS, REGIONS
    for destination, region in REGIONS.items():
        remaining.setdefault(destination, sum(1 for card in SEARCH_CARDS.values()
                                               if card['region'] == region))
    return {
        'phase': game.phase, 'day': c.day, 'founders': tuple(game.founders),
        'people': tuple({k:p[k] for k in ('id','kind','wounds','hungry','thirsty','fatigue')
                         if k in p} for p in c.people),
        'consumers': c.consumers, 'food': sum(c.food), 'water': sum(c.water),
        'materials': c.materials, 'parts': tuple(sorted(c.parts)),
        'delivered': tuple(game.delivered_objectives),
        'expedition_days': tuple(game.expedition_days),
        'search_remaining': remaining,
        'expedition_active': game.tactical is not None,
    }


def observe_tactical(tactical) -> dict:
    """Estado local visível: nunca expõe a ordem futura de Saque ou Horda."""
    return {
        'destination': tactical.destination, 'team': tuple(tactical.team),
        'positions': dict(tactical.positions), 'doors': tuple(tuple(e) for e in tactical.doors_open),
        'equipment': {hero:tuple(items) for hero,items in tactical.equipment.items()},
        'edges': tuple(tuple(e) for e in tactical.map['edges']),
        'door_edges': tuple(tuple(e) for e in tactical.map['doors']),
        'blocked_edges': tuple(tuple(e) for e in tactical.map['blocked']),
        'entry': tactical.map['entry'], 'search_zones': tuple(tactical.map['search']),
        'enemies': tuple({k:e[k] for k in ('id','kind','zone','hp')} for e in tactical.enemies),
        'ap': dict(tactical.ap), 'round_no': tactical.round_no,
        'completed_rounds': tactical.completed_rounds,
        'can_exit': tactical.can_exit(), 'finished': tactical.finished,
        'failed': tactical.failed,
    }


@dataclass(frozen=True)
class Decision:
    kind: str
    args: tuple
    reason: str


@dataclass
class ProgrammedPlayer:
    profile: str
    seed: int
    history: list[Decision] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.profile not in PROFILES:
            raise ValueError('Perfil desconhecido')

    def _record(self, kind: str, args: tuple, reason: str) -> Decision:
        decision = Decision(kind, args, reason)
        self.history.append(decision)
        return decision

    def choose_expedition(self, game) -> Decision:
        view = observe_campaign(game)
        if view['phase'] != 'cistern' or view['expedition_active']:
            raise ValueError('Expedição não disponível')
        if view['day'] in view['expedition_days']:
            raise ValueError('Já houve expedição hoje')
        people = {p['id']: p for p in view['people']}
        available = [h for h in view['founders']
                     if people[h]['wounds'] < 3 and people[h].get('fatigue',0) < 3]
        if not available:
            raise ValueError('Sem herói apto')
        food, water, consumers = view['food'], view['water'], view['consumers']
        delivered = set(view['delivered'])
        if self.profile == 'Conservador' and food < 2*consumers:
            destination, reason = 'Mercado', 'Comida abaixo de dois consumos'
        elif self.profile == 'Construtor' and 'Oficina:Conexões' not in delivered:
            destination, reason = 'Oficina', 'Buscar peça e material de construção'
        elif self.profile == 'Oportunista' and game.cistern.day >= 2:
            destination, reason = 'Posto', 'Avaliar recurso limitado de combustível'
        elif water < consumers and self.profile in ('Líder','Conservador'):
            destination, reason = 'Estação', 'Água ameaça a próxima refeição'
        else:
            preferred = {
                'Explorador': 'Estação', 'Combatente': 'Oficina',
                'Líder': 'Oficina', 'Iniciante': 'Mercado',
                'Adversarial': 'Condomínio', 'Construtor': 'Oficina',
                'Conservador': 'Mercado', 'Oportunista': 'Posto',
            }
            destination, reason = preferred[self.profile], 'Prioridade pública do perfil'
        if destination not in self.goals:
            self.goals.append(destination)
        team_count = min(len(available), 2 if self.profile in ('Conservador','Iniciante') else 3)
        if self.profile == 'Líder' and len(available) >= 4:
            team_count = 2  # Deixa trabalhadores e vigias no abrigo.
        team = available[:team_count]
        route = 'long' if self.profile in ('Conservador','Iniciante') else 'short'
        # Desempate reproduzível apenas entre opções já públicas.
        if self.profile == 'Explorador' and game.cistern.day > 1:
            route = Random(self.seed + game.cistern.day).choice(('short','long'))
        return self._record('expedition', (destination, team, route), reason)

    def choose_local(self, tactical) -> Decision:
        view = observe_tactical(tactical)
        if view['finished'] or view['failed']:
            raise ValueError('Expedição encerrada')
        if view['round_no'] == view['completed_rounds']:
            return self._record('begin_round', (), 'Prosseguir após a ativação inimiga')
        if view['can_exit'] and self.profile == 'Conservador':
            return self._record('return', (), 'Saída segura e estoque preservado')
        for hero in view['team']:
            if view['ap'].get(hero, 0) < 1:
                continue
            here = view['positions'][hero]
            target = 7 if view['destination'] != 'estação' else 14
            graph = {z:[] for edge in view['edges'] for z in edge}
            for a,b in view['edges']:
                graph[a].append(b); graph[b].append(a)
            q=deque([(here,[here])]); seen={here}; path=[]
            while q:
                zone, candidate=q.popleft()
                if zone==target:
                    path=candidate; break
                for nxt in sorted(graph.get(zone,[])):
                    if nxt not in seen:
                        seen.add(nxt); q.append((nxt,candidate+[nxt]))
            if len(path) < 2:
                continue
            nxt = path[1]
            doors = {tuple(sorted(e)) for e in view['door_edges']}
            opened = {tuple(sorted(e)) for e in view['doors']}
            if tuple(sorted((here,nxt))) in doors and tuple(sorted((here,nxt))) not in opened:
                blocked = tuple(sorted((here, nxt))) in {
                    tuple(sorted(e)) for e in view['blocked_edges']}
                if blocked and (view['ap'][hero] < 2
                                or not any(tool in view['equipment'][hero]
                                           for tool in ('Pé de cabra','Ferramentas'))):
                    continue
                return self._record('open_door', (hero, nxt,
                    'Pé de cabra' if blocked else None), 'Abrir rota até objetivo público')
            cost = 1 + int(any(e['zone'] == here for e in view['enemies']))
            if view['ap'][hero] >= cost:
                return self._record('move', (hero, nxt), 'Avançar por conector legal')
        if view['can_exit']:
            return self._record('return', (), 'Nenhuma ação útil restante; retorno legal')
        return self._record('end_round', (), 'Aguardar ativação e recompor PA')

    def invalid_probe(self, game) -> Decision:
        """Sondagem adversarial separada da política legal de partida."""
        if self.profile != 'Adversarial':
            raise ValueError('Sondagem exclusiva do perfil adversarial')
        return self._record('reject_probe', ('Conexões',),
                            'Confirmar que collect_part isolado é recusado')
