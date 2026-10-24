"""Oito políticas programáticas para decisões públicas do núcleo parcial 0.2.

Elas não resolvem uma campanha: Viagem, Saque, resgate e transição ainda faltam.
Nenhuma política vê cartas futuras nem aceita recursos artificiais.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


PROFILES = (
    'Conservador', 'Explorador', 'Construtor', 'Combatente',
    'Líder', 'Iniciante', 'Oportunista', 'Adversarial',
)


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
        if game.phase != 'cistern' or game.tactical is not None:
            raise ValueError('Expedição não disponível')
        if game.cistern.day in game.expedition_days:
            raise ValueError('Já houve expedição hoje')
        people = {p['id']: p for p in game.cistern.people}
        available = [h for h in game.founders if people[h]['wounds'] < 3]
        if not available:
            raise ValueError('Sem herói apto')
        food = sum(game.cistern.food)
        water = sum(game.cistern.water)
        consumers = game.cistern.consumers
        delivered = set(game.delivered_objectives)
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
        if tactical.finished or tactical.failed:
            raise ValueError('Expedição encerrada')
        if tactical.round_no == tactical.completed_rounds:
            return self._record('begin_round', (), 'Prosseguir após a ativação inimiga')
        if tactical.can_exit() and self.profile == 'Conservador':
            return self._record('return', (), 'Saída segura e estoque preservado')
        for hero in tactical.team:
            if tactical.ap.get(hero, 0) < 1:
                continue
            here = tactical.positions[hero]
            target = 7 if tactical.destination != 'estação' else 14
            path = tactical._path(here, target)
            if len(path) < 2:
                continue
            nxt = path[1]
            if not tactical._open(here, nxt):
                blocked = tuple(sorted((here, nxt))) in {
                    tuple(sorted(e)) for e in tactical.map['blocked']}
                if blocked and (tactical.ap[hero] < 2 or
                                'Pé de cabra' not in tactical.equipment[hero]):
                    continue
                return self._record('open_door', (hero, nxt,
                    'Pé de cabra' if blocked else None), 'Abrir rota até objetivo público')
            cost = 1 + int(any(e['zone'] == here for e in tactical.enemies))
            if tactical.ap[hero] >= cost:
                return self._record('move', (hero, nxt), 'Avançar por conector legal')
        if tactical.can_exit():
            return self._record('return', (), 'Nenhuma ação útil restante; retorno legal')
        return self._record('end_round', (), 'Aguardar ativação e recompor PA')

    def invalid_probe(self, game) -> Decision:
        """Sondagem adversarial separada da política legal de partida."""
        if self.profile != 'Adversarial':
            raise ValueError('Sondagem exclusiva do perfil adversarial')
        return self._record('reject_probe', ('Conexões',),
                            'Confirmar que collect_part isolado é recusado')
