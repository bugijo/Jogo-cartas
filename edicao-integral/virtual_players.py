"""Jogadores virtuais: 18 personas fictícias jogando a Cisterna pelo motor.

As idades são traços de personas fictícias, não afirmações sobre faixas etárias
reais. Cada persona controla um fundador e tem traços próprios (0–1). A mesa
decide no amanhecer por voto ponderado pela assertividade; quem discorda gera
um conflito registrado. Toda ação passa pelo motor (`CampaignPlayer02`), que só
lê estado visível a qualquer jogador na mesa. Erros de regra são simulados como
propostas ilegais testadas numa cópia do jogo: o motor as recusa e nada muda.

Isto é teste automatizado, não playtest humano: mede onde as regras exigem
planejamento e onde a mesa depende de um líder, como hipótese a validar.
"""
from __future__ import annotations

import zlib
from copy import deepcopy
from dataclasses import dataclass, field
from random import Random

from campaign_player02 import CampaignPlayer02
from cistern02 import STAGES

TRAITS = ('risk', 'exploration', 'planning', 'cooperation', 'resources',
          'assertiveness', 'experience', 'resilience')


@dataclass(frozen=True)
class Persona:
    id: str
    group: str
    age: int
    profile: str
    communication: str
    goal: str
    under_pressure: str
    risk: float
    exploration: float
    planning: float
    cooperation: float
    resources: float
    assertiveness: float
    experience: float
    resilience: float

    @property
    def comprehension(self) -> float:
        """Chance de ler certo uma regra de planejamento (simulada)."""
        return round(0.35 + 0.35 * self.planning + 0.3 * self.experience, 3)

    def preferences(self, pressure: bool) -> dict:
        """Preferência individual de política; sob pressão, a reação muda o risco."""
        risk = self.risk
        if pressure:
            risk = min(1.0, risk + 0.25) if self.under_pressure == 'arrisca' else (
                max(0.0, risk - 0.25) if self.under_pressure == 'recua' else risk)
        return {
            'adaptive': self.planning >= 0.5,
            'far_first': self.exploration >= 0.6,
            'cautious': risk < 0.45,
            'retreat': risk < 0.6,
            'escort': self.cooperation >= 0.5,
            'support': self.cooperation >= 0.65,
            'collection': self.resources >= 0.5,
            'whole_team': risk >= 0.55 or self.cooperation >= 0.7,
        }


def _p(id_, group, age, profile, communication, goal, under_pressure, *values):
    return Persona(id_, group, age, profile, communication, goal, under_pressure,
                   *values)


#              id   grp age perfil                       comunicação  objetivo                    pressão     risk expl plan coop res  assert exp  resil
PERSONAS = (
    _p('A13', 'A', 13, 'iniciante curioso', 'pergunta muito', 'ver todos os lugares', 'segue', .50, .80, .25, .60, .30, .20, .10, .50),
    _p('A15', 'A', 15, 'impulsivo e competitivo', 'decide rápido', 'ser quem mais coleta', 'arrisca', .90, .60, .30, .30, .25, .80, .30, .40),
    _p('A16', 'A', 16, 'criativo e explorador', 'propõe ideias', 'achar rotas novas', 'arrisca', .65, .95, .45, .55, .35, .55, .35, .55),
    _p('A17', 'A', 17, 'social e cooperativo', 'media a mesa', 'ninguém fica para trás', 'recua', .40, .45, .50, .95, .55, .50, .35, .60),
    _p('A18', 'A', 18, 'estrategista', 'explica o plano', 'vencer com plano', 'segue', .45, .40, .85, .55, .70, .70, .50, .65),
    _p('A19', 'A', 19, 'prefere partidas rápidas', 'curto e direto', 'terminar logo', 'arrisca', .75, .35, .35, .45, .30, .60, .40, .45),
    _p('B21', 'B', 21, 'competitivo', 'decide rápido', 'maximizar coleta', 'arrisca', .85, .55, .55, .30, .45, .85, .55, .50),
    _p('B24', 'B', 24, 'casual', 'concorda fácil', 'se divertir', 'segue', .55, .55, .35, .65, .35, .25, .40, .55),
    _p('B27', 'B', 27, 'estrategista experiente', 'explica o plano', 'vencer com margem', 'recua', .35, .40, .95, .60, .80, .75, .90, .80),
    _p('B30', 'B', 30, 'cooperativo', 'media a mesa', 'proteger o grupo', 'recua', .35, .40, .60, .90, .60, .45, .60, .70),
    _p('B33', 'B', 33, 'fã de narrativa e RPG', 'conta histórias', 'acolher personagens', 'segue', .55, .75, .55, .70, .40, .55, .70, .60),
    _p('B35', 'B', 35, 'otimizador de recursos', 'faz contas', 'não desperdiçar nada', 'recua', .30, .30, .85, .50, .95, .65, .75, .70),
    _p('C36', 'C', 36, 'experiente', 'explica o plano', 'vencer bem jogado', 'segue', .45, .45, .80, .60, .70, .65, .90, .75),
    _p('C42', 'C', 42, 'casual e social', 'conversa', 'passar tempo junto', 'segue', .50, .50, .40, .80, .40, .35, .50, .60),
    _p('C48', 'C', 48, 'metódico', 'segue o manual', 'fazer certo', 'recua', .25, .30, .85, .55, .80, .55, .65, .75),
    _p('C55', 'C', 55, 'cooperativo', 'media a mesa', 'todos sobrevivem', 'recua', .30, .35, .60, .90, .65, .45, .60, .75),
    _p('C63', 'C', 63, 'interessado em narrativa', 'conta histórias', 'conhecer a história', 'segue', .40, .65, .55, .65, .50, .40, .55, .65),
    _p('C70', 'C', 70, 'iniciante atento às regras', 'pergunta muito', 'entender as regras', 'recua', .20, .30, .40, .60, .55, .30, .10, .55),
)
BY_ID = {persona.id: persona for persona in PERSONAS}


def table_policy(personas: list[Persona], pressure: bool = False) -> dict:
    """Voto ponderado por assertividade; o líder é a persona mais assertiva."""
    weights = [0.2 + p.assertiveness for p in personas]
    prefs = [p.preferences(pressure) for p in personas]
    leader = max(range(len(personas)), key=lambda i: (personas[i].assertiveness,
                                                       personas[i].planning, -i))
    policy, conflicts, leader_agree = {}, [], 0
    for key in prefs[0]:
        yes = sum(w for w, pref in zip(weights, prefs) if pref[key])
        policy[key] = yes * 2 >= sum(weights)
        leader_agree += prefs[leader][key] == policy[key]
        for persona, pref in zip(personas, prefs):
            # Só discorda abertamente quem não é muito cooperativo.
            if pref[key] != policy[key] and persona.cooperation < 0.7:
                conflicts.append({'persona': persona.id, 'topic': key,
                                  'wanted': pref[key]})
    return {'policy': policy, 'leader': personas[leader].id,
            'leader_agreement': leader_agree / len(prefs[0]), 'conflicts': conflicts}


@dataclass
class TablePlayer(CampaignPlayer02):
    """Controlador da Cisterna dirigido pela mesa de personas."""
    personas: list[Persona] = field(default_factory=list)
    table_log: list[dict] = field(default_factory=list)
    rule_log: list[dict] = field(default_factory=list)
    scripted: bool = False  # mesa sem planejador: segue o roteiro fixo

    def apply_policy(self, policy: dict) -> None:
        self.adaptive = policy['adaptive']
        self.adaptive_order = (('Estação', 'Oficina') if policy['far_first']
                               else ('Oficina', 'Estação'))
        self.emergency_collection = policy['collection']
        self.tactics = tuple(name for name, on in (
            ('escort', policy['escort']), ('late_retreat', policy['retreat']),
            ('cautious', policy['cautious']), ('support', policy['support'])) if on)
        self.team_caps = {} if policy['whole_team'] else {
            'Estação': max(2, len(self.personas) - 1)}

    def _pressure(self) -> bool:
        cistern = self.game.cistern
        short = self._shortfall()
        return bool(short['food'] or short['water']
                    or any(p['wounds'] >= 2 for p in cistern.people if p['kind'] == 'hero'))

    def _rng(self, persona: Persona, day: int) -> Random:
        return Random(zlib.crc32(f'{self.seed}:{persona.id}:{day}'.encode()))

    def _probe_rules(self, day: int) -> None:
        """Cada persona lê uma regra de planejamento; leitura errada vira proposta ilegal.

        A proposta roda numa cópia: o motor decide se é legal. Nada muda no jogo.
        """
        cistern = self.game.cistern
        heroes = {persona: hero for hero, persona in self.hero_of().items()}
        missing = [stage for stage in STAGES if stage not in cistern.reserved
                   and STAGES[stage]['part'] not in cistern.parts]
        for persona in self.personas:
            rng = self._rng(persona, day)
            misread = rng.random() > persona.comprehension
            if not misread:
                continue
            rule, attempt = (('worker_on_expedition',
                              lambda game: game.plan_filter_work(
                                  [heroes[persona.id]], [heroes[persona.id]]))
                             if not missing or rng.random() < 0.5 else
                             ('reserve_without_part',
                              lambda game: game.reserve_filter_stage(missing[0])))
            copy = deepcopy(self.game)
            try:
                attempt(copy)
                outcome = 'accepted'  # leitura errada que por acaso era legal
            except (ValueError, NotImplementedError):
                outcome = 'refused_by_engine'
            self.rule_log.append({'day': day, 'persona': persona.id, 'rule': rule,
                                  'outcome': outcome})

    def _adaptive_dawn(self, day, crew, destination, team, tasks, loadout):
        self._probe_rules(day)
        pressure = self._pressure()
        vote = table_policy(self.personas, pressure)
        self.apply_policy(vote['policy'])
        self.adaptive = True  # já está no ramo adaptativo do amanhecer
        self.table_log.append({'day': day, 'pressure': pressure, **vote})
        return super()._adaptive_dawn(day, crew, destination, team, tasks, loadout)

    @classmethod
    def for_table(cls, seed: int, personas: list[Persona]) -> 'TablePlayer':
        base = CampaignPlayer02.new_hn(seed, len(personas))
        player = cls(seed=seed, game=base.game, personas=list(personas))
        vote = table_policy(player.personas)
        player.apply_policy(vote['policy'])
        player.table_log.append({'day': 0, 'pressure': False, **vote})
        player.scripted = not player.adaptive
        return player

    def day_close(self, guards=None, guard_rolls=None, ammo=0):
        if self.scripted:
            # Roteiro fixo: sem voto no amanhecer, mas a mesa ainda lê as regras.
            self._probe_rules(self.game.cistern.day)
        return super().day_close(guards=guards, guard_rolls=guard_rolls, ammo=ammo)

    def hero_of(self) -> dict[str, str]:
        return dict(zip(self.game.founders, (p.id for p in self.personas)))
