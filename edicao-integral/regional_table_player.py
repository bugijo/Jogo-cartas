"""Mesa de personas na campanha regional (Última Transmissão).

Estende o laboratório de jogadores virtuais além da Cisterna: a cada amanhecer
regional a mesa vota (peso por assertividade, como `table_policy`) e o voto
ajusta o controlador experimental `CampRegionalPlayer`. Só estado observável e
ações públicas do motor; nenhuma avaliação subjetiva de diversão.
"""
from __future__ import annotations

from regional_campaign_player import CampRegionalPlayer
from virtual_players import Persona


def regional_preferences(persona: Persona, pressure: bool) -> dict:
    """Preferência individual no regional; sob pressão a reação muda o risco."""
    risk = persona.risk
    if pressure:
        risk = min(1.0, risk + 0.25) if persona.under_pressure == 'arrisca' else (
            max(0.0, risk - 0.25) if persona.under_pressure == 'recua' else risk)
    return {
        'risk_short': risk >= 0.5,              # aceita uma noite curta pela pista
        'progress_first': persona.exploration >= 0.6,
        'reserve_3_days': risk < 0.35,          # quer 3 dias de comida antes de sair
        'forage': persona.resources >= 0.5 or persona.cooperation >= 0.65,
        'invest': persona.planning >= 0.5,      # obras e Horta antes do curto prazo
        'storage_priority': persona.resources >= 0.4 or persona.planning >= 0.6,
    }


def regional_policy(personas: list[Persona], pressure: bool = False) -> dict:
    weights = [0.2 + p.assertiveness for p in personas]
    prefs = [regional_preferences(p, pressure) for p in personas]
    leader = max(range(len(personas)), key=lambda i: (personas[i].assertiveness,
                                                       personas[i].planning, -i))
    policy, conflicts, agree = {}, [], 0
    for key in prefs[0]:
        yes = sum(w for w, pref in zip(weights, prefs) if pref[key])
        policy[key] = yes * 2 >= sum(weights)
        agree += prefs[leader][key] == policy[key]
        for persona, pref in zip(personas, prefs):
            if pref[key] != policy[key] and persona.cooperation < 0.7:
                conflicts.append({'persona': persona.id, 'topic': key,
                                  'wanted': pref[key]})
    return {'policy': policy, 'leader': personas[leader].id,
            'leader_agreement': agree / len(prefs[0]), 'conflicts': conflicts}


class RegionalTablePlayer(CampRegionalPlayer):
    """Controlador regional cujo amanhecer é decidido pelo voto da mesa."""

    def __init__(self, personas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personas = list(personas)
        self.table_log: list[dict] = []

    @staticmethod
    def pressure(world) -> bool:
        people = world.meal_people()
        return (world.stock['food'] < len(people)
                or any(p.get('streak', 0) for p in people.values())
                or any(h['health'] <= 1 for h in world.heroes.values()))

    def apply_policy(self, policy: dict) -> None:
        self.risk = 'short' if policy['risk_short'] or policy['progress_first'] else 'covered'
        self.food_days = 3 if policy['reserve_3_days'] else 2
        options = {'bridge'}
        if policy['storage_priority']:
            options.add('priority')
        if policy['forage']:
            options.add('forage')
        if policy['invest']:
            options |= {'garden', 'build'}
        self.options = options

    def plan(self, world):
        pressure = self.pressure(world)
        vote = regional_policy(self.personas, pressure)
        self.apply_policy(vote['policy'])
        self.table_log.append({'day': world.day, 'pressure': pressure, **vote})
        return super().plan(world)
