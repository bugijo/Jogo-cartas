"""Campanha contínua para A Cisterna 0.2 -> Última Transmissão.

Este módulo é uma camada de integração. Os arquivos canônicos da edição 0.2
continuam somente leitura; ``Cistern02`` permanece o modelo de preparação,
porções, relógio e filtro, enquanto ``World`` executa o segundo arco.
"""
from __future__ import annotations

import json
import hashlib
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path

from arc2 import Arc2
from cistern02 import CATALOG, Cistern02, LINK_IDS, STARTERS, GARDEN
from ambush02 import Ambush02
from cistern_tactics02 import Tactical02, WEAPONS
from horde_deck02 import HordeDeck02
from travel02 import Travel02, TravelContext
from travel_deck02 import TravelDeck02
from system import Expedition, HEROES, World
import community as community_rules


PART_MISSIONS = {
    "Conexões": {"id": "CIS-MIS-A", "location": "EXP-LOC-03", "cost": 1},
    "Bomba": {"id": "CIS-MIS-B", "location": "EXP-LOC-05", "cost": 2},
    "Membrana": {"id": "CIS-MIS-C", "location": "EXP-LOC-05", "cost": 1},
}


STORAGE_DISCARD_ORDER = ("water", "food", "medicine", "ammo", "fuel")


def _migrate_horde_snapshot(snapshot: dict | None) -> dict | None:
    """Converte o antigo snapshot por IDs para o sapato atual por tipo."""
    if snapshot is None:
        return None
    if set(snapshot) == {"seed", "deck", "discard", "reshuffles"}:
        return HordeDeck02.from_snapshot(snapshot).snapshot()
    if set(snapshot) != {"seed", "draw_pile", "discard", "reshuffles"}:
        raise ValueError("Snapshot legado de Horda incompatível")
    names = {card["id"]: card["name"] for card in CATALOG["cards"]
             if card.get("family") == "HOR"}
    try:
        converted = {
            "seed": snapshot["seed"],
            "deck": [names[card] for card in snapshot["draw_pile"]],
            "discard": [names[card] for card in snapshot["discard"]],
            "reshuffles": snapshot["reshuffles"],
        }
    except (KeyError, TypeError) as exc:
        raise ValueError("Snapshot legado de Horda inválido") from exc
    return HordeDeck02.from_snapshot(converted).snapshot()


def _world_payload(world: World) -> dict:
    return asdict(world)


def _world_from_payload(payload: dict) -> World:
    payload = dict(payload)
    schema = payload.pop("schema", None)
    if schema not in (1, 2):
        raise ValueError("Esquema regional incompatível")
    if schema == 1:
        for state in payload.get("heroes", {}).values():
            state.setdefault("wounds", max(0, min(3, 3-state.get("health", 3))))
            state.setdefault("hungry", False)
            state.setdefault("thirsty", False)
            state.setdefault("streak", 0)
        for person in [*payload.get("npcs", {}).values(),
                       *payload.get("continuity_people", [])]:
            if "health" in person:
                person.setdefault("wounds", max(0, min(3, 3-person.get("health", 3))))
            person.setdefault("hungry", False)
            person.setdefault("thirsty", False)
            person.setdefault("streak", 0)
    payload["expeditions"] = {
        key: Expedition(**value) for key, value in payload["expeditions"].items()
    }
    world = World(**payload)
    world.validate()
    return world


@dataclass
class IntegratedCampaign:
    """Estado único, serializável e retomável dos dois arcos."""

    schema: int
    campaign_id: str
    seed: int
    status: str
    cistern: Cistern02
    founders: list[str]
    links: list[str]
    decisions: dict[str, str] = field(default_factory=dict)
    rewards: list[str] = field(default_factory=list)
    world: World | None = None
    terminal_reason: str | None = None
    tactical: Tactical02 | None = None
    expedition_days: list[int] = field(default_factory=list)
    visited_destinations: list[str] = field(default_factory=list)
    delivered_objectives: list[str] = field(default_factory=list)
    lost_objectives: list[str] = field(default_factory=list)
    fuel_cards: list[str] = field(default_factory=list)
    battery_available: bool = False
    van_state: str = "abandoned"
    site_states: dict[str, dict] = field(default_factory=dict)
    travel: Travel02 | None = None
    travel_context: TravelContext | None = None
    travel_request: dict | None = None
    ambush: Ambush02 | None = None
    travel_segments_paid: int = 0
    return_travel: Travel02 | None = None
    return_context: TravelContext | None = None
    return_context_initial: dict | None = None
    return_settlement_delta: dict | None = None
    route_known: bool = False
    bridge_known: bool = False
    equipment_inventory: dict[str, list[str]] = field(default_factory=dict)
    travel_uses_shoe: bool = False
    road_aid_settled: bool = False
    work_phase_resolved: bool = False
    mission_receipts: list[dict] = field(default_factory=list)

    STATUSES = {"RUNNING", "VICTORY", "DEFEAT", "IMPOSSIBLE", "PAUSED"}

    @classmethod
    def new(
        cls,
        seed: int,
        founders: list[str] | tuple[str, ...],
        links: list[str] | tuple[str, ...],
    ) -> "IntegratedCampaign":
        cistern = Cistern02.new(founders, links, seed=seed)
        game = cls(1, f"zona-zero-{seed}", seed, "RUNNING", cistern,
                   list(founders), list(links))
        game.equipment_inventory = {hero: ["Pé de cabra"] for hero in founders}
        return game

    @property
    def phase(self) -> str:
        if self.status != "RUNNING":
            return "finished"
        return "cistern" if self.world is None else "last_transmission"

    def _require_running(self) -> None:
        if self.status != "RUNNING":
            raise ValueError("Campanha encerrada")

    def _validate_loadout(self, team: list[str], loadout: dict[str, list[str]]) -> None:
        allowed = set(WEAPONS) | {"Bateria", "Lanterna", "Ferramentas"}
        if set(loadout) != set(team):
            raise ValueError("Equipamento deve ser declarado para cada herói")
        for hero, items in loadout.items():
            if len(items) > 4 or any(item not in allowed for item in items):
                raise ValueError("Equipamento inválido ou excede quatro cargas")
            if sum(item in WEAPONS for item in items) > 2:
                raise ValueError("Cada herói transporta no máximo duas armas")
            requested = Counter(items)
            owned = Counter(self.equipment_inventory.get(hero, []))
            for item, count in requested.items():
                if item == "Bateria":
                    if count > int(self.battery_available):
                        raise ValueError("Bateria não está no estoque")
                elif count > owned[item]:
                    raise ValueError(f"{item} não pertence ao inventário de {hero}")

    def decide(self, decision_id: str, choice: str) -> None:
        self._require_running()
        if decision_id in self.decisions:
            raise ValueError("Decisão já resolvida")
        if not decision_id or not choice:
            raise ValueError("Decisão inválida")
        self.decisions[decision_id] = choice

    def collect_part(self, part: str, choice: str = "search") -> dict:
        """Indisponível até haver recibo verificável de coleta e retorno tático."""
        self._require_running()
        if self.world is not None:
            raise ValueError("Peças só podem ser coletadas no arco da Cisterna")
        if part not in PART_MISSIONS:
            raise ValueError("Missão de peça indisponível")
        raise NotImplementedError(
            "Coleta exige expedição 0.2, PA, carga e retorno; integração pendente")

    def start_expedition(self, destination: str, team: list[str],
                         route: str = "short",
                         equipment: dict[str, list[str]] | None = None,
                         travel_segments_paid: int = 0,
                         starting_fatigue: dict[str, int] | None = None,
                         _prepared_travel: bool = False) -> Tactical02:
        """A abertura pública do mapa sempre exige a sequência de Viagem."""
        raise ValueError("Use start_travel → resolva as ocorrências → enter_expedition")

    def _start_tactical_fixture(self, destination: str, team: list[str],
                         route: str = "short",
                         equipment: dict[str, list[str]] | None = None,
                         travel_segments_paid: int = 0,
                         starting_fatigue: dict[str, int] | None = None,
                         _prepared_travel: bool = False) -> Tactical02:
        """Abertura interna do mapa; chamadas de teste não provam uma Viagem legal."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or (self.travel is not None and not _prepared_travel)
                or self.return_travel is not None or self.ambush is not None):
            raise ValueError("Expedição indisponível nesta fase")
        if self.cistern.meal_day == self.cistern.day:
            raise ValueError("Expedição ocorre antes da refeição noturna")
        if self.cistern.day in self.expedition_days:
            raise ValueError("Limite de uma expedição por dia")
        loadout = (deepcopy(equipment) if equipment is not None else
                   {hero: self.equipment_inventory.get(hero, []).copy() for hero in team})
        self._validate_loadout(team, loadout)
        tactical = Tactical02.start(
            self.cistern, destination, team, route,
            taken_before=self.delivered_objectives + self.lost_objectives,
            first_visit=destination.lower() not in self.visited_destinations,
            equipment=loadout,
            prior_state=self.site_states.get(destination.lower()),
            travel_segments_paid=travel_segments_paid,
            horde_deck=self.cistern.horde_deck,
            starting_fatigue=starting_fatigue)
        self.tactical = tactical
        self.expedition_days.append(self.cistern.day)
        self.visited_destinations.append(destination.lower())
        return tactical

    def start_travel(self, destination: str, team: list[str], route: str = "short",
                     deck: list[str] | None = None,
                     context: TravelContext | None = None,
                     equipment: dict[str, list[str]] | None = None) -> Travel02:
        """Prepara a estrada antes de pagar o trecho no mapa tático."""
        self._require_running()
        if (self.world is not None or self.tactical is not None or self.travel is not None
                or self.return_travel is not None or self.ambush is not None):
            raise ValueError("Viagem indisponível nesta fase")
        if self.cistern.meal_day == self.cistern.day or self.cistern.day in self.expedition_days:
            raise ValueError("Expedição indisponível após refeição ou já usada no dia")
        if self.work_phase_resolved:
            raise ValueError("Planejamento diário já foi resolvido")
        if (not team or len(set(team)) != len(team)
                or any(hero not in self.cistern.founders for hero in team)):
            raise ValueError("Equipe de viagem inválida")
        route_segments = 1 if route == "short" else 2 if route == "long" else 0
        if (not route_segments
                or self.cistern.clock + route_segments + 1 > 10):
            raise ValueError("Sem tempo para ida e entrada no destino")
        if context is None or set(context.fatigue) != set(team):
            raise ValueError("Contexto de carga da viagem é obrigatório")
        people = {person["id"]: person for person in self.cistern.people}
        dog_families = {person["family"] for person in self.cistern.people
                        if person["kind"] == "dog"}
        team_families = list(dict.fromkeys(people[hero]["family"] for hero in team))
        eligible_families = [family for family in team_families
                             if family not in dog_families]
        context.dogs = 0
        context.eligible_dog_adoption = bool(eligible_families)
        context.dog_family = eligible_families[0] if eligible_families else None
        context.pressure = self.cistern.pressure
        context.moral = self.cistern.morale
        context.route_known = self.route_known
        context.bridge_known = self.bridge_known
        if (any(not isinstance(value, int) or value < 0
                for value in (context.food, context.water, context.materials))
                or context.food > sum(self.cistern.food)
                or context.water > sum(self.cistern.water)
                or context.materials > self.cistern.materials):
            raise ValueError("Carga declarada excede o estoque real do abrigo")
        food_indices, food_lots = self._select_physical_lots(
            self.cistern.food, context.food)
        water_indices, water_lots = self._select_physical_lots(
            self.cistern.water, context.water)
        if food_indices is None or water_indices is None:
            raise ValueError("As porções escolhidas não correspondem a cartas físicas")
        context.fatigue = {hero: people[hero]["fatigue"] for hero in team}
        loadout = (deepcopy(equipment) if equipment is not None else
                   {hero: self.equipment_inventory.get(hero, []).copy() for hero in team})
        self._validate_loadout(team, loadout)
        free_load = sum(4 - len(loadout[hero]) for hero in team)
        if len(food_lots) + len(water_lots) + context.materials > free_load:
            raise ValueError("Carga de viagem excede a capacidade dos heróis")
        HordeDeck02.from_snapshot(self.cistern.horde_deck)
        if any(people[hero]["wounds"] >= 3 or people[hero]["fatigue"] >= 3
               for hero in team):
            raise ValueError("Herói incapacitado ou exausto não viaja")
        if deck is None:
            shoe = TravelDeck02.from_snapshot(self.cistern.travel_deck)
            trip = Travel02.from_deck(
                shoe.prepare_trip(2 * (1 if route == "short" else 2) + 2), route)
            self.travel_uses_shoe = True
        else:
            trip = Travel02.from_deck(deck, route)
            self.travel_uses_shoe = False
        if self.cistern.clock >= 10:
            raise ValueError("Sem segmento para iniciar a Viagem")
        self.cistern.lock_work_plan(team)
        # O contexto representa carga física da equipe. Reserve-a agora para
        # que a estrada não possa gastar o mesmo estoque duas vezes.
        self.cistern.food = [lot for i, lot in enumerate(self.cistern.food)
                             if i not in set(food_indices)]
        self.cistern.water = [lot for i, lot in enumerate(self.cistern.water)
                              if i not in set(water_indices)]
        context.food_lots = food_lots
        context.water_lots = water_lots
        context.food = sum(food_lots)
        context.water = sum(water_lots)
        self.cistern.materials -= context.materials
        self.travel = trip
        self.travel_context = context
        self.return_context_initial = context.snapshot()
        self.travel_request = {"destination": destination, "team": list(team),
                               "route": route,
                               "equipment": deepcopy(loadout)}
        self.travel_segments_paid = 0
        self._advance_road_segment("outbound")
        return trip

    def reveal_travel(self) -> dict:
        if self.travel is None:
            raise ValueError("Nenhuma viagem preparada")
        return self._advance_road_segment("outbound")

    def _advance_road_segment(self, direction: str) -> dict:
        """Paga exatamente um trecho, aplica fadiga e revela sua ocorrência.

        Se o trecho cruza para o relógio 9 ou 10, a próxima chamada revela a
        ocorrência extra sem cobrar outro segmento.
        """
        trip = self.travel if direction == "outbound" else self.return_travel
        context = self.travel_context if direction == "outbound" else self.return_context
        if trip is None or context is None:
            raise ValueError("Viagem ou carga de estrada ausente")
        if trip.pending_resolution is not None or trip.pending_choices or trip.pending_ambush:
            raise ValueError("Resolva a ocorrência de estrada pendente")
        if trip.requires_night_extra(direction):
            return trip.reveal_night_extra(direction)
        if trip.remaining(direction) <= 0:
            raise ValueError("Não há outro trecho nesta direção")
        if self.cistern.clock >= 10:
            raise ValueError("Relógio sem segmento para continuar a Viagem")
        self.cistern.spend_segments(1)
        if self.cistern.clock >= 9:
            for hero in context.fatigue:
                context.fatigue[hero] = min(3, context.fatigue[hero] + 1)
                people = {person["id"]: person for person in self.cistern.people}
                if hero in people:
                    people[hero]["fatigue"] = context.fatigue[hero]
                if direction == "return" and self.tactical is not None:
                    self.tactical.fatigue[hero] = context.fatigue[hero]
        if direction == "outbound":
            self.travel_segments_paid += 1
        event = trip.reveal(direction, context,
                            clock_segment=self.cistern.clock)
        return event

    @staticmethod
    def _select_physical_lots(stock: list[int], requested: int) -> tuple[list[int] | None, list[int]]:
        """Escolhe cartas físicas cuja carga cubra o saldo solicitado.

        A solução minimiza primeiro a quantidade de cartas e depois o excesso
        de porções. Empates seguem a ordem estável do estoque.
        """
        if requested == 0:
            return [], []
        states: dict[int, tuple[int, ...]] = {0: ()}
        for index, value in enumerate(stock):
            if not isinstance(value, int) or not 1 <= value <= 4:
                raise ValueError("Cursor de porções no estoque inválido")
            for total, chosen in list(states.items()):
                candidate_total = total + value
                candidate = chosen + (index,)
                old = states.get(candidate_total)
                if old is None or (len(candidate), candidate) < (len(old), old):
                    states[candidate_total] = candidate
        options = [(len(indices), total - requested, indices, total)
                   for total, indices in states.items() if total >= requested]
        if not options:
            return None, []
        _, _, indices, _ = min(options)
        return list(indices), [stock[index] for index in indices]

    def resolve_travel_choice(self, event_id: str, choice: str) -> dict:
        trip = self.travel if self.travel is not None else self.return_travel
        context = self.travel_context if self.travel is not None else self.return_context
        if trip is None or context is None:
            raise ValueError("Nenhuma viagem preparada")
        return trip.apply(event_id, context, choice)

    def start_travel_ambush(self) -> Ambush02:
        returning = self.travel is None and self.return_travel is not None
        trip = self.return_travel if returning else self.travel
        context = self.return_context if returning else self.travel_context
        if (trip is None or trip.pending_ambush is None or context is None
                or self.ambush is not None
                or (not returning and self.travel_request is None)
                or (returning and self.tactical is None)):
            raise ValueError("Nenhuma Emboscada pendente")
        event = next((entry for entry in trip.events
                      if entry.get("event_id") == trip.pending_ambush), None)
        if not event or not isinstance(event.get("clock_segment"), int):
            raise ValueError("Emboscada sem trecho de estrada pago")
        if self.cistern.clock < event["clock_segment"]:
            raise ValueError("Emboscada antecede o trecho de estrada")
        if returning:
            team = self.tactical.team
            equipment = self.tactical.equipment
        else:
            team = self.travel_request["team"]
            equipment = self.travel_request["equipment"]
        people = {person["id"]: person for person in self.cistern.people}
        self.ambush = Ambush02.start(
            team, self.cistern.clock,
            equipment=equipment, ammo=self.cistern.ammo,
            horde_deck=self.cistern.horde_deck,
            fatigue=context.fatigue,
            ap_penalty={hero: int(people[hero]["hungry"])
                        + int(people[hero]["thirsty"])
                        for hero in team},
            allow_emergency_at_limit=self.cistern.clock == 10)
        return self.ambush

    def finish_travel_ambush(self) -> None:
        trip = self.travel if self.travel is not None else self.return_travel
        if trip is None or self.ambush is None or not self.ambush.returned:
            raise ValueError("Emboscada ainda não retornou")
        event_id = trip.pending_ambush
        if event_id is None:
            raise ValueError("Emboscada já resolvida")
        if self.ambush.clock < self.cistern.clock:
            raise ValueError("Relógio da Emboscada retrocedeu")
        people = {person["id"]: person for person in self.cistern.people}
        if (set(self.ambush.wounds) != set(self.ambush.team)
                or any(hero not in people for hero in self.ambush.team)
                or any(not isinstance(count, int) or count < 0
                       for count in self.ambush.wounds.values())):
            raise ValueError("Ferimentos da Emboscada incompatíveis com os fundadores")
        context = self.travel_context if self.travel is not None else self.return_context
        trip.resolve_ambush(event_id)
        trip.complete_ambush(event_id, self.ambush)
        for hero, wounds in self.ambush.wounds.items():
            people[hero]["wounds"] = min(3, people[hero]["wounds"] + wounds)
            people[hero]["fatigue"] = self.ambush.fatigue[hero]
            if context is not None:
                context.fatigue[hero] = self.ambush.fatigue[hero]
        self.cistern.ammo = self.ambush.ammo
        self.cistern.horde_deck = deepcopy(self.ambush.horde_deck)
        self.cistern.clock = self.ambush.clock
        self.ambush = None

    def enter_expedition(self) -> Tactical02:
        if self.travel is None or self.travel_request is None:
            raise ValueError("Prepare a viagem antes de entrar no mapa")
        if (self.travel.remaining("outbound")
                or self.travel_segments_paid != self.travel.leg_size
                or self.travel.requires_night_extra("outbound")
                or self.travel.pending_choices
                or self.travel.pending_resolution is not None
                or self.travel.pending_ambush is not None or self.ambush is not None):
            raise ValueError("Viagem ainda não foi resolvida")
        request = self.travel_request
        tactical = self._start_tactical_fixture(
            request["destination"], request["team"], request["route"],
            request["equipment"], self.travel_segments_paid,
            starting_fatigue=self.travel_context.fatigue,
            _prepared_travel=True)
        return_trip = self.travel
        return_context = self.travel_context
        tactical.load_road_cargo(return_context.food_lots,
                                 return_context.water_lots,
                                 return_context.materials)
        self.travel = None
        self.travel_context = None
        self.travel_request = None
        self.travel_segments_paid = 0
        self.return_travel = return_trip
        self.return_context = return_context
        self.road_aid_settled = False
        if self.return_context_initial is None and return_context:
            self.return_context_initial = return_context.snapshot()
        return tactical

    def _settle_return_travel(self) -> None:
        """Revela e liquida a volta antes de entregar qualquer recibo."""
        if self.return_travel is None or self.return_context is None:
            return
        trip = self.return_travel
        context = self.return_context
        if trip.pending_resolution is not None or trip.pending_ambush is not None:
            raise ValueError("Resolva a carta de retorno pendente")
        while trip.remaining("return") or trip.requires_night_extra("return"):
            event = self._advance_road_segment("return")
            if event.get("skipped"):
                continue
            if event.get("ambush"):
                raise ValueError("Emboscada de retorno exige M1 antes da entrega")
            if trip.pending_choices:
                raise ValueError("Escolha da carta de retorno pendente")
            trip.apply(event["event_id"], context)
        if any(not isinstance(value, int) or value < 0
               for value in (context.food, context.water, context.materials)):
            raise ValueError("Saldo físico de carga inválido na estrada")
        self.return_settlement_delta = self._travel_arrival_delta(context)

    def _settle_road_aid_costs(self) -> None:
        """Deduct aid consumed at the destination before return-road effects."""
        if self.road_aid_settled or self.tactical is None or self.return_context is None:
            return
        aid_receipts=[receipt for receipt in self.tactical.log
                      if receipt.get('event')=='rescue'
                      and receipt.get('decision')=='aid']
        if not aid_receipts:
            return
        for receipt in aid_receipts:
            paid=receipt.get('aid_from_road',{})
            for kind in ('food','water'):
                amount=paid.get(kind,0)
                if not isinstance(amount,int) or amount<0:
                    raise ValueError('Recibo de ajuda rodoviária inválido')
                if amount:
                    self.return_context.consume(kind,amount)
        self.road_aid_settled=True

    def _settle_travel_shoe(self, trip: Travel02) -> None:
        """Consome uma única vez as cartas efetivamente reveladas na viagem."""
        if not self.travel_uses_shoe:
            return
        if not self.cistern.travel_deck:
            raise ValueError("Baralho persistente de Viagem ausente")
        shoe = TravelDeck02.from_snapshot(self.cistern.travel_deck)
        shoe.finish_trip(trip)
        self.cistern.travel_deck = shoe.snapshot()
        self.travel_uses_shoe = False

    def return_expedition(self, by_van: bool = False) -> list[dict]:
        """Liquida o retorno em cópia e publica apenas um resultado completo.

        Cartas de estrada, recibos táticos e estoque são uma única operação:
        uma falta de recurso não pode deixar metade dos efeitos aplicados nem
        apagar o estado necessário para corrigir o estoque e tentar novamente.
        """
        if self.tactical is not None and not self.tactical.finished:
            # O mapa local terminou; isso persiste mesmo enquanto a estrada
            # de retorno exige uma escolha ou uma Emboscada adicional.
            paid = (self.return_travel.leg_size
                    if self.return_travel is not None else 0)
            self.tactical.finish(by_van=by_van, travel_segments_paid=paid)
        self._settle_road_aid_costs()
        if (self.tactical is not None and self.return_context is not None
                and self.return_travel is not None
                and self.return_travel.return_segments == 0):
            for hero in self.tactical.team:
                self.return_context.fatigue[hero] = self.tactical.fatigue[hero]
        # Revelações e escolhas válidas são marcos persistentes, inclusive
        # quando precisam de uma ação posterior (por exemplo, resolver M1).
        self._settle_return_travel()
        candidate = deepcopy(self)
        proof = candidate._return_expedition_mutating(by_van=by_van)
        # Preserve identities de objetos expostos por start_expedition e
        # start_travel; código de mesa/teste pode manter essas referências.
        for name in self.__dataclass_fields__:
            current, updated = getattr(self, name), getattr(candidate, name)
            if (current is not None and updated is not None
                    and type(current) is type(updated)
                    and hasattr(current, "__dataclass_fields__")):
                for attr in current.__dataclass_fields__:
                    setattr(current, attr, deepcopy(getattr(updated, attr)))
            else:
                setattr(self, name, updated)
        if self.tactical is not None and hasattr(self.tactical, "chapter"):
            self.tactical.chapter = self.cistern
        return proof

    def _return_expedition_mutating(self, by_van: bool = False) -> list[dict]:
        self._require_running()
        if self.tactical is None:
            raise ValueError("Nenhuma expedição ativa")
        tactical = self.tactical
        if not tactical.finished:
            paid = (self.return_travel.return_segments
                    if self.return_travel is not None else 0)
            tactical.finish(by_van=by_van, travel_segments_paid=paid)
        proof = tactical.delivery_proof()
        keys = [
            (receipt["group_id"] if receipt["event"] == "rescue" else
             receipt.get("id", f"{receipt.get('destination')}:{receipt.get('part')}"))
            for receipt in proof if receipt["event"] != "deliver_van"
        ]
        if len(keys) != len(set(keys)) or any(key in self.delivered_objectives for key in keys):
            raise ValueError("Objetivo já entregue")
        for receipt in proof:
            if receipt["event"] == "rescue":
                decision = receipt["decision"]
                if decision == "aid":
                    if self.return_context is None:
                        raise ValueError("Ajuda sem carga de retorno")
                    paid = receipt.get("aid_paid")
                    if paid != {"food": receipt["humans"],
                                "water": receipt["humans"]}:
                        raise ValueError("Recibo de ajuda tática inválido")
                    # A carga da estrada já foi debitada antes de resolver a
                    # volta, para que eventos de retorno vejam o saldo real.
                    # Não debite o mesmo recibo novamente nesta liquidação.
                    road = receipt.get("aid_from_road", {})
                    if (not self.road_aid_settled
                            and any(road.get(kind, 0) for kind in ("food", "water"))):
                        raise ValueError("Custo de ajuda rodoviária ainda não liquidado")
                self.cistern.rescue(receipt["group_id"], decision,
                                    aid_paid=receipt.get("aid_paid"))
                if decision != "decline":
                    self.delivered_objectives.append(receipt["group_id"])
            elif receipt["event"] in ("pickup_part", "recover_part"):
                part = receipt["part"]
                if part in PART_MISSIONS:
                    self.cistern.receive_part(part)
                elif part == "Bateria":
                    self.battery_available = True
                self.delivered_objectives.append(f"{receipt['destination']}:{part}")
            elif receipt["event"] == "pickup_supply":
                if receipt["kind"] == "Conserva":
                    self.cistern.food.extend([4] * receipt["cards"])
                elif receipt["kind"] == "Água":
                    self.cistern.water.extend([4] * receipt["cards"])
                elif receipt["kind"] == "Combustível":
                    self.fuel_cards.append(receipt["id"])
                elif receipt["kind"] == "Sementes":
                    self.cistern.receive_seeds()
                self.delivered_objectives.append(receipt["id"])
            elif receipt["event"] == "pickup_equipment":
                item = receipt["item"]
                if item == "Bateria":
                    self.battery_available = True
                else:
                    self.equipment_inventory[receipt["hero"]].append(item)
                self.delivered_objectives.append(receipt["id"])
            elif receipt["event"] == "deliver_van":
                self.van_state = "operational"
            elif receipt["event"] == "search_reward":
                for kind, count in receipt["reward"].items():
                    if kind == "Conserva":
                        self.cistern.food.extend([4] * count)
                    elif kind == "Água":
                        self.cistern.water.extend([4] * count)
                    elif kind == "Carne":
                        self.cistern.meat.extend([4] * count)
                    elif kind == "Material":
                        self.cistern.materials += count
                    elif kind == "Munição":
                        self.cistern.ammo += count
                    elif kind == "Medicamento":
                        self.cistern.medicine += count
                    else:
                        raise ValueError("Recompensa regional desconhecida")
                self.delivered_objectives.append(receipt["id"])
        delta = self.return_settlement_delta or {}
        self._apply_travel_arrival(delta)
        if self.return_travel is not None:
            self._settle_travel_shoe(self.return_travel)
        self.return_settlement_delta = None
        self.return_travel = None
        self.return_context = None
        self.return_context_initial = None
        if any(receipt["event"] == "repair_van" and receipt["success"]
               for receipt in tactical.log):
            self.battery_available = False
            if not tactical.van_returned:
                self.van_state = "operational_at_posto"
        self.lost_objectives.extend(
            receipt["id"] for receipt in tactical.log
            if receipt["event"] == "fuel_spent")
        self.cistern.horde_deck = deepcopy(tactical.horde_deck)
        self.site_states[tactical.destination] = tactical.site_snapshot()
        self.mission_receipts.append({
            "day": self.cistern.day,
            "destination": tactical.destination,
            "team": list(tactical.team),
            "route": tactical.route,
            "receipts": deepcopy(proof),
            "tactical_log": deepcopy(tactical.log),
        })
        self.tactical = None
        return proof

    def _arrive_dogs(self, count: int, family: str | None) -> None:
        if count == 0:
            return
        if count != 1 or not family:
            raise ValueError("Adoção de cão excede limite ou não tem família")
        if family not in {person["id"] for person in self.cistern.people
                          if person["kind"] == "hero"}:
            raise ValueError("Família guardiã do cão não existe")
        if any(person["kind"] == "dog" and person["family"] == family
               for person in self.cistern.people):
            raise ValueError("Família já possui cão")
        number = 1 + max((int(person["id"][1:]) for person in self.cistern.people
                          if person["kind"] == "dog" and person["id"].startswith("D")),
                         default=0)
        self.cistern.people.append(Cistern02._person(f"D{number:02d}", "dog", family))
        self.cistern.dogs += 1

    def _apply_travel_arrival(self, delta: dict) -> None:
        """Aplica carga restante e efeitos de estrada uma única vez."""
        for stock, lots_key, amount_key in (
                (self.cistern.food, "food_lots", "food"),
                (self.cistern.water, "water_lots", "water")):
            lots = delta.get(lots_key)
            if lots is None:
                lots = TravelContext._pack(delta.get(amount_key, 0))
            if any(not isinstance(value, int) or not 1 <= value <= 4 for value in lots):
                raise ValueError("Carta de porções inválida na chegada")
            stock.extend(lots)
        materials = delta.get("materials", 0)
        if not isinstance(materials, int) or materials < 0:
            raise ValueError("Saldo de materiais inválido na chegada")
        self.cistern.materials += materials
        pressure = delta.get("pressure", 0)
        if pressure:
            self.cistern.raise_pressure(pressure)
        self.cistern.morale = max(0, min(5, self.cistern.morale + delta.get("moral", 0)))
        self._arrive_dogs(delta.get("dogs", 0), delta.get("dog_family"))
        self.route_known |= bool(delta.get("route_known", False))
        self.bridge_known |= bool(delta.get("bridge_known", False))
        people = {person["id"]: person for person in self.cistern.people}
        for hero, fatigue in delta.get("fatigue", {}).items():
            if hero not in people or not isinstance(fatigue, int) or not 0 <= fatigue <= 3:
                raise ValueError("Fadiga de chegada inválida")
            people[hero]["fatigue"] = fatigue

    def _travel_arrival_delta(self, context: TravelContext) -> dict:
        initial = self.return_context_initial or {}
        return {
            "food": context.food,
            "water": context.water,
            "food_lots": context.food_lots.copy(),
            "water_lots": context.water_lots.copy(),
            "materials": context.materials,
            "pressure": context.pressure - initial.get("pressure", 0),
            "moral": context.moral - initial.get("moral", context.moral),
            "dogs": context.dogs - initial.get("dogs", 0),
            "dog_family": context.dog_family,
            "route_known": context.route_known,
            "bridge_known": context.bridge_known,
            "fatigue": context.fatigue.copy(),
        }

    @staticmethod
    def _store_portions(lots: list[int], amount: int) -> None:
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("Saldo de porções inválido na liquidação")
        while amount:
            lot = min(4, amount)
            lots.append(lot)
            amount -= lot

    def emergency_return(self) -> None:
        self._settle_road_aid_costs()
        candidate = deepcopy(self)
        candidate._emergency_return_mutating()
        for name in self.__dataclass_fields__:
            current, updated = getattr(self, name), getattr(candidate, name)
            if (current is not None and updated is not None
                    and type(current) is type(updated)
                    and hasattr(current, "__dataclass_fields__")):
                for attr in current.__dataclass_fields__:
                    setattr(current, attr, deepcopy(getattr(updated, attr)))
            else:
                setattr(self, name, updated)
        if self.tactical is not None and hasattr(self.tactical, "chapter"):
            self.tactical.chapter = self.cistern

    def _emergency_return_mutating(self) -> None:
        self._require_running()
        trip = self.travel if self.travel is not None else self.return_travel
        context = self.travel_context if self.travel is not None else self.return_context
        if trip is not None and trip.pending_ambush is not None:
            returning = self.travel is None
            if context is None:
                raise ValueError("Estado de Emboscada/Viagem incompatível")
            team = (self.tactical.team if returning and self.tactical is not None
                    else self.travel_request["team"] if self.travel_request else [])
            equipment = (self.tactical.equipment if returning and self.tactical is not None
                         else self.travel_request["equipment"] if self.travel_request else {})
            if not team:
                raise ValueError("Equipe da Emboscada não registrada")
            people = {person["id"]: person for person in self.cistern.people}
            if self.ambush is None:
                self.ambush = Ambush02.start(
                    team, self.cistern.clock, equipment=equipment,
                    ammo=self.cistern.ammo,
                    horde_deck=self.cistern.horde_deck,
                    fatigue=context.fatigue,
                    ap_penalty={hero: int(people[hero]["hungry"])
                                + int(people[hero]["thirsty"]) for hero in team},
                    allow_emergency_at_limit=True)
            encounter = self.ambush
            encounter.emergency_return()
            trip.complete_emergency_ambush(trip.pending_ambush, encounter)
            self._settle_travel_shoe(trip)
            people = {person["id"]: person for person in self.cistern.people}
            for hero in encounter.team:
                people[hero]["wounds"] = min(
                    3, people[hero]["wounds"] + encounter.wounds[hero])
                people[hero]["fatigue"] = 3
                context.fatigue[hero] = 3
            self.cistern.ammo = encounter.ammo
            self.cistern.clock = encounter.clock
            self.cistern.horde_deck = deepcopy(encounter.horde_deck)
            self._apply_travel_arrival(self._travel_arrival_delta(context))
            if returning:
                if self.tactical is None:
                    raise ValueError("M1 de retorno sem expedição local")
                self._record_lost_tactical_cargo(self.tactical)
                self.tactical.lose_cargo_after_return_ambush()
                self.site_states[self.tactical.destination] = self.tactical.site_snapshot()
                self.tactical = None
            if self.cistern.day not in self.expedition_days:
                self.expedition_days.append(self.cistern.day)
            self.ambush = None
            self.travel = None
            self.travel_context = None
            self.travel_request = None
            self.travel_segments_paid = 0
            self.return_travel = None
            self.return_context = None
            self.return_context_initial = None
            self.return_settlement_delta = None
            return
        if self.travel is not None and self.tactical is None:
            trip = self.travel
            context = self.travel_context
            request = self.travel_request
            if (context is None or request is None or self.ambush is not None
                    or self.cistern.clock < 10
                    or trip.remaining("outbound")
                    or self.travel_segments_paid != trip.leg_size
                    or trip.requires_night_extra("outbound")
                    or trip.pending_resolution is not None
                    or trip.pending_choices or trip.pending_ambush
                    or not any(event.get("card_id") == "ZC-VIA-0005"
                               and event.get("event_id") in trip.resolved
                               for event in trip.events)
                    or self.cistern.clock + 1 <= 10):
                raise ValueError("Retirada rodoviária sem M1 concluída ou sem bloqueio de relógio")
            self._settle_travel_shoe(trip)
            people = {person["id"]: person for person in self.cistern.people}
            for hero in request["team"]:
                people[hero]["wounds"] = min(3, people[hero]["wounds"] + 1)
                people[hero]["fatigue"] = 3
                context.fatigue[hero] = 3
            self._apply_travel_arrival(self._travel_arrival_delta(context))
            if self.cistern.day not in self.expedition_days:
                self.expedition_days.append(self.cistern.day)
            self.travel = None
            self.travel_context = None
            self.travel_request = None
            self.travel_segments_paid = 0
            self.return_context_initial = None
            return
        if self.tactical is None:
            raise ValueError("Nenhuma expedição ativa")
        if self.tactical.finished:
            trip = self.return_travel
            if (trip is None or self.cistern.clock < 10
                    or not (trip.remaining("return")
                            or trip.requires_night_extra("return"))
                    or trip.pending_resolution is not None
                    or trip.pending_choices or trip.pending_ambush):
                raise ValueError("Retirada rodoviária indisponível neste estado")
            self._record_lost_tactical_cargo(self.tactical)
            self.tactical.emergency_after_return()
            self._settle_travel_shoe(trip)
            self.cistern.horde_deck = deepcopy(self.tactical.horde_deck)
            self.site_states[self.tactical.destination] = self.tactical.site_snapshot()
            if self.return_context is not None:
                for hero in self.tactical.team:
                    self.return_context.fatigue[hero] = self.tactical.fatigue[hero]
                self._apply_travel_arrival(
                    self._travel_arrival_delta(self.return_context))
            self.return_travel = None
            self.return_context = None
            self.return_context_initial = None
            self.return_settlement_delta = None
            self.tactical = None
            return
        self._record_lost_tactical_cargo(self.tactical)
        self.tactical.emergency()
        if self.return_travel is not None:
            self._settle_travel_shoe(self.return_travel)
        self.cistern.horde_deck = deepcopy(self.tactical.horde_deck)
        self.site_states[self.tactical.destination] = self.tactical.site_snapshot()
        if self.return_context is not None:
            for hero in self.tactical.team:
                self.return_context.fatigue[hero] = self.tactical.fatigue[hero]
            self._apply_travel_arrival(
                self._travel_arrival_delta(self.return_context))
        self.return_travel = None
        self.return_context = None
        self.return_context_initial = None
        self.return_settlement_delta = None
        self.tactical = None

    def _record_lost_tactical_cargo(self, tactical: Tactical02) -> None:
        for receipt in tactical.log:
            if receipt["event"] in ("pickup_supply", "pickup_equipment", "pickup_part", "recover_part",
                                    "search_reward", "fuel_spent"):
                identifier = receipt.get("id")
                if receipt["event"] in ("pickup_part", "recover_part"):
                    identifier = f"{receipt['destination']}:{receipt['part']}"
                if identifier and identifier not in self.lost_objectives:
                    self.lost_objectives.append(identifier)

    def meal(self) -> dict:
        self._require_running()
        if self.world is not None:
            raise ValueError("Use advance_day no arco da Última Transmissão")
        if self.tactical is not None:
            raise ValueError("Resolva a expedição antes da refeição")
        if self.travel is not None or self.return_travel is not None or self.ambush is not None:
            raise ValueError("Resolva ou encerre a viagem antes da refeição")
        if self.cistern.pending_sieges and self.cistern.siege_day!=self.cistern.day:
            raise ValueError("Resolva o cerco antes da refeição")
        if not self.work_phase_resolved:
            if self.cistern.filter_workers_plan or self.cistern.garden_workers_plan:
                raise ValueError("Resolva os trabalhos planejados antes da refeição")
            self.resolve_filter_work()
        return self.cistern.meal()

    def plan_filter_work(self,workers:list[str],
                         expedition_team:list[str]|None=None) -> None:
        """Ação pública para alocar trabalho nominal antes de sair."""
        self._require_running()
        if self.world is not None or self.cistern.meal_day==self.cistern.day:
            raise ValueError("Planejamento de trabalho indisponível nesta fase")
        self.cistern.plan_filter_work(workers,expedition_team)

    def plan_emergency_collection(self,assignments:list[dict],
                                  expedition_team:list[str]|None=None) -> None:
        """§26: aloca coleta de emergência no amanhecer, antes de sair."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.work_phase_resolved):
            raise ValueError("Coleta de emergência indisponível nesta fase")
        self.cistern.plan_emergency_collection(assignments,expedition_team)

    def reserve_filter_stage(self,stage:str) -> None:
        """Reserva materiais e peça no amanhecer, antes de qualquer expedição."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.cistern.meal_day==self.cistern.day):
            raise ValueError("Reserva do filtro indisponível nesta fase")
        self.cistern.reserve(stage)

    def reserve_garden(self) -> None:
        """RULES §61: reserva a Horta no amanhecer, antes de qualquer expedição."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.cistern.meal_day==self.cistern.day):
            raise ValueError("Reserva da Horta indisponível nesta fase")
        self.cistern.reserve_garden()

    def plan_garden_work(self,workers:list[str],
                         expedition_team:list[str]|None=None) -> None:
        """Aloca obra ou produção da Horta antes de sair."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.work_phase_resolved):
            raise ValueError("Trabalho da Horta indisponível nesta fase")
        self.cistern.plan_garden_work(workers,expedition_team)

    def plan_guards(self,heroes:list[str]) -> None:
        """Registra vigias antes da saída, pela interface da campanha."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.cistern.meal_day==self.cistern.day):
            raise ValueError("Planejamento de vigias indisponível nesta fase")
        self.cistern.plan_guards(heroes)

    def reveal_siege(self) -> dict:
        """Revela apenas o próximo cerco que já entrou na fila canônica."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None):
            raise ValueError("Cerco indisponível enquanto há expedição ativa")
        return self.cistern.reveal_siege()

    def resolve_siege(self,rolls:list[int],damage_targets:list[str],
                      ammo:int=0) -> dict:
        """Resolve o cerco revelado; Força e gatilho vêm do estado persistente."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or not self.cistern.pending_sieges
                or (self.cistern.active_siege is None
                    and self.cistern.pending_sieges[0] != "Barulho no vale")):
            raise ValueError("Cerco ainda não foi revelado ou há expedição ativa")
        encounter=(self.cistern.active_siege or self.cistern.reveal_siege())
        return self.cistern.resolve_siege(
            encounter["force"], self.cistern.planned_guards.copy(),
            rolls, ammo, damage_targets,
            security=self.cistern.day==5 and self.cistern.meal_day==self.cistern.day)

    def resolve_intentions(self) -> list[dict]:
        """Resolve gatilhos de intenção após a refeição, sem expor cartas antes."""
        self._require_running()
        if (self.world is not None or self.tactical is not None
                or self.travel is not None or self.return_travel is not None
                or self.ambush is not None):
            raise ValueError("Intenções só podem ser resolvidas no abrigo")
        return self.cistern.night_intentions()

    def resolve_filter_work(self) -> dict:
        """Resolve a alocação no abrigo, somente depois do retorno da equipe."""
        self._require_running()
        if (self.world is not None or self.tactical is not None or self.travel is not None
                or self.return_travel is not None or self.ambush is not None):
            raise ValueError("Trabalho só pode ser resolvido após o retorno")
        if self.work_phase_resolved:
            raise ValueError("Fase de trabalhos já foi resolvida")
        if not self.cistern.work_plan_locked:
            self.cistern.lock_work_plan([])
        units=len(self.cistern.filter_workers_plan)
        if units==0:
            result={"workers":[],"units":0,"day":self.cistern.day}
        else:
            receipt_start=len(self.cistern.work_receipts)
            self.cistern.work(units)
            result=deepcopy(self.cistern.work_receipts[receipt_start])
        garden=self.cistern.work_garden()
        if garden is not None:
            result["garden"]=garden
        collection=self.cistern.collect_emergency()
        if collection is not None:
            result["emergency_collection"]=collection
        self.work_phase_resolved=True
        return result

    def next_cistern_day(self) -> None:
        self._require_running()
        if self.world is not None:
            raise ValueError("A Cisterna já foi concluída")
        if self.tactical is not None:
            raise ValueError("Expedição ainda não retornou")
        if self.travel is not None or self.return_travel is not None or self.ambush is not None:
            raise ValueError("Resolva ou encerre a viagem antes de avançar o dia")
        if not self.work_phase_resolved:
            raise ValueError("Fase de trabalhos diária pendente")
        self.cistern.next_day()
        self.work_phase_resolved=False

    def complete_cistern(self) -> dict:
        """Certifica a Cisterna; a migração para o segundo arco é posterior."""
        self._require_running()
        if self.world is not None or not self.cistern.filter_completed:
            raise ValueError("Filtro da Cisterna ainda não está concluído")
        if self.cistern.result is None:
            self.cistern.close_chapter()
        required={"Oficina:Conexões","Estação:Bomba","Estação:Membrana"}
        if not required.issubset(set(self.delivered_objectives)):
            raise NotImplementedError("Vitória candidata sem recibos legais de peças")
        certificate = self.cistern.certify_victory(self.delivered_objectives)
        if "verified_victory" not in self.rewards:
            self.rewards.append("verified_victory")
        return certificate

    def _continuity_source(self) -> dict:
        """Serializable source ledger for an atomic cross-arc transition."""
        payload = asdict(self)
        payload.pop("world", None)
        # Campos da Horta só entram no digest quando usados: migrações sem
        # Horta mantêm o mesmo recibo dos replays certificados.
        for key, empty in (("seeds", 0), ("seeds_day", 0), ("garden", None),
                           ("garden_workers_plan", [])):
            if payload["cistern"].get(key) == empty:
                payload["cistern"].pop(key, None)
        payload["founder_roster"] = list(STARTERS)
        return payload

    @staticmethod
    def _digest_payload(payload: dict) -> str:
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def transition_to_last_transmission(self, community: bool = False) -> dict:
        """Project a certified Cisterna save into the regional engine exactly once.

        ``community`` liga as regras Comunidade (``community.py``) na chegada:
        profissões dos adultos, viagens automáticas e abrigo lotado (até +2
        moradores sem cama). Desligado, a migração é a certificada.

        Values without a rules-equivalent representation stay in an archival,
        non-spendable continuity manifest. The conversion is built and validated
        off to the side before ``self.world`` is assigned, so a failed capacity
        check cannot partially consume or duplicate the source state.
        """
        if self.world is not None:
            migration = (self.world.cistern_record or {}).get("migration", {})
            archive = migration.get("source_archive")
            digest = migration.get("source_digest")
            receipt = migration.get("receipt")
            if (archive is None or not digest or self._digest_payload(archive) != digest
                    or not receipt or receipt.get("source_digest") != digest
                    or not self.world.cistern_verified):
                raise ValueError("Transição existente não possui proveniência íntegra")
            self.world.validate()
            return deepcopy(receipt)

        self._require_running()
        if (self.status != "RUNNING" or self.cistern.result != "verified_victory"
                or "verified_victory" not in self.rewards
                or self.cistern.chapter_receipt is None
                or self.cistern.chapter_receipt.get("result") != "verified_victory"):
            raise ValueError("Transição exige certificado verified_victory")
        if (self.tactical is not None or self.travel is not None or self.return_travel is not None
                or self.ambush is not None or self.travel_request is not None
                or self.cistern.pending_sieges or self.cistern.event_queue
                or self.cistern.meal_day != self.cistern.day):
            raise ValueError("Há resolução obrigatória pendente na Cisterna")
        self.cistern.validate_snapshot()
        required = {"Oficina:Conexões", "Estação:Bomba", "Estação:Membrana"}
        if not required.issubset(set(self.delivered_objectives)):
            raise ValueError("Objetivos legais da Cisterna incompletos")
        receipt_parts = [f"{receipt['destination']}:{receipt['part']}"
                         for expedition in self.mission_receipts
                         for receipt in expedition.get("receipts", [])
                         if receipt.get("event") in ("pickup_part", "recover_part")]
        if (len(receipt_parts) != len(set(receipt_parts))
                or not required.issubset(set(receipt_parts))):
            raise ValueError("Recibos de expedição não comprovam as três peças")
        people = {person["id"]: person for person in self.cistern.people}
        if len(people) != len(self.cistern.people):
            raise ValueError("Identidades duplicadas no abrigo de origem")
        if set(self.founders) - set(people) or any(
                people[founder]["kind"] != "hero" for founder in self.founders):
            raise ValueError("Fundadores ativos não correspondem às identidades da Cisterna")
        if any(founder not in HEROES for founder in self.founders):
            raise ValueError("Fundador sem identidade no motor regional")

        source = self._continuity_source()
        source_digest = self._digest_payload(source)
        stock = {
            "food": sum(self.cistern.food),
            "water": sum(self.cistern.water),
            "medicine": self.cistern.medicine,
            "ammo": self.cistern.ammo,
            # Each physical fuel card represents one regional fuel unit.
            "fuel": len(self.fuel_cards),
        }
        # Decisão aprovada (2026-10-29): o que passar do depósito regional é
        # descartado na migração e registrado no recibo. Ordem: água primeiro
        # (único recurso que a Cisterna consertada acumula acima do limite).
        capacity = World.new(self.seed, list(self.founders)).storage
        discarded = {}
        for resource in STORAGE_DISCARD_ORDER:
            excess = sum(stock.values()) - capacity
            if excess <= 0:
                break
            cut = min(excess, stock[resource])
            if cut:
                stock[resource] -= cut
                discarded[resource] = cut
        projected = World.new(self.seed, list(self.founders), stock)
        projected.regional_horde_deck = deepcopy(self.cistern.horde_deck)
        # Travel is a campaign-wide finite deck. Continue the 0.2 shoe at its
        # exact post-Cisterna state; do not start a fresh copy in Arc 2.
        projected.regional_travel_deck = deepcopy(self.cistern.travel_deck)
        battery_delivered = self.battery_available
        battery_lost = any(
            objective in self.lost_objectives
            for objective in ("Oficina:Bateria", "oficina:Bateria:1")
        )
        battery_receipted = any(
            receipt.get("part") == "Bateria"
            or receipt.get("item") == "Bateria"
            for expedition in self.mission_receipts
            for receipt in expedition.get("receipts", [])
        )
        if battery_delivered and battery_lost:
            raise ValueError("Bateria marcada simultaneamente entregue e perdida")
        if battery_delivered:
            projected.special_stock.append("battery")
        elif battery_lost:
            # The canonical lost-objective ledger is retained in the source
            # archive; never respawn a unique part after an emergency loss.
            pass
        elif not battery_receipted:
            # The seed-22 victory left the unique guaranteed Oficina battery
            # untouched. It remains at its canonical map objective, not in the
            # shelter inventory.
            projected.unique_items_at_sites["EXP-LOC-03"] = ["battery"]
        source_people = [deepcopy(person) for person in self.cistern.people]
        for hero_id in self.founders:
            person = people[hero_id]
            state = projected.heroes[hero_id]
            wounds = int(person.get("wounds", 0))
            if not 0 <= wounds <= 3:
                raise ValueError(f"Ferimentos de {hero_id} não podem ser migrados")
            state["health"] = max(0, 3 - wounds)
            fatigue = person.get("fatigue", 0)
            if (not isinstance(fatigue, int) or isinstance(fatigue, bool)
                    or not 0 <= fatigue <= 3):
                raise ValueError(f"Fadiga de {hero_id} não pode ser migrada")
            state["fatigue"] = fatigue
            state["wounds"] = wounds
            state["hungry"] = bool(person.get("hungry", False))
            state["thirsty"] = bool(person.get("thirsty", False))
            state["streak"] = int(person.get("streak", 0))
            state["continuity_state"] = deepcopy(person)

        projected.continuity_people = [person for person in source_people
                                       if person["kind"] != "hero"]
        projected.shelter_health = int(self.cistern.health)
        projected.shelter_morale = int(self.cistern.morale)
        projected.continuity_beds = self.cistern.capacity - projected.beds
        for person in projected.continuity_people:
            if person["kind"] not in ("adult", "child", "dog"):
                raise ValueError(f"Tipo de morador sem modelo regional: {person['kind']}")
        if community:
            # Antes das demais validações: abrigo lotado (+2) só vale com Comunidade.
            projected.community = community_rules.new_state(projected)

        # Only the identical crowbar has a matching active equipment model.
        # Other 0.2 items remain present in the immutable source archive until
        # their combat/stat model is ported; they are never silently converted.
        equipment_projection = []
        equipment_archived = []
        for hero_id in self.founders:
            counts = Counter(self.equipment_inventory.get(hero_id, []))
            crowbars = counts.pop("Pé de cabra", 0)
            for index in range(min(crowbars, 2)):
                instance_id = f"CIS-{hero_id}-CROWBAR-{index + 1:02d}"
                projected.give_item(hero_id, instance_id, "EXP-EQU-002", "hand", index)
                equipment_projection.append({"hero": hero_id, "source_item": "Pé de cabra",
                                             "instance": instance_id,
                                             "target_item": "EXP-EQU-002"})
            if crowbars > 2:
                equipment_archived.extend([{"hero": hero_id, "item": "Pé de cabra",
                                            "reason": "limite de duas mãos regionais"}
                                           for _ in range(crowbars - 2)])
            for item, amount in counts.items():
                equipment_archived.extend([{"hero": hero_id, "item": item,
                                            "reason": "sem modelo regional equivalente"}
                                           for _ in range(amount)])

        migration_id = f"cistern02:{source_digest[:16]}"
        receipt = {"id": migration_id, "source_digest": source_digest,
                   "from": "cistern02", "to": "last_transmission",
                   "heroes": list(self.founders), "people": len(source_people),
                   "consumers": self.cistern.consumers, "day": self.cistern.day}
        if discarded:
            receipt["storage_discarded"] = {"capacity": capacity, "resources": discarded}
        ledger = {
            "schema": 1,
            "source_digest": source_digest,
            "source_archive": source,
            "archive_policy": "auditoria/continuidade; não é inventário gastável",
            "projection": {
                "resource_units": stock,
                "food_lots": list(self.cistern.food),
                "water_lots": list(self.cistern.water),
                "meat_lots_archived": list(self.cistern.meat),
                "materials_archived": self.cistern.materials,
                "structures_archived": list(self.cistern.structures),
                "morale_health_pressure_archived": {
                    "morale": self.cistern.morale, "health": self.cistern.health,
                    "pressure": self.cistern.pressure,
                },
                "relationships_and_promises_archived": {
                    "links": list(self.links), "rescue_history": deepcopy(self.cistern.rescue_history),
                    "groups": deepcopy(self.cistern.groups),
                },
                "equipment_projected": equipment_projection,
                "equipment_archived": equipment_archived,
                "battery_archived": self.battery_available,
                "battery_projection": ("camp_stock" if battery_delivered else
                                       "lost_unavailable" if battery_lost else
                                       "workshop_objective" if not battery_receipted else
                                       "source_receipt_requires_review"),
                "vehicle_archived": self.van_state,
                "unspent_clues": 0,
            },
            "receipt": receipt,
        }
        projected.decisions = deepcopy(self.decisions)
        projected.cistern_record = {
            "status": "verified_victory", "source": "cistern02",
            "objectives": sorted(required), "certificate": deepcopy(self.cistern.chapter_receipt),
            "migration": ledger,
        }
        if self.cistern.filter_active:
            # Mesmo abrigo, filtro funcional: segue produzindo C inicial/amanhecer
            # (exige o certificado acima; a primeira produção é no próximo amanhecer).
            projected.continuity_filter = {"source": "cistern02", "active": True,
                                           "output": int(self.cistern.initial_consumers)}
        garden = self.cistern.garden
        if garden is not None and garden["active"]:
            # RULES §61: a Horta pronta segue no mesmo abrigo; produz só com um
            # trabalhador designado no regional (4 comida/dia, sem bônus).
            projected.continuity_garden = {"source": "cistern02", "active": True,
                                           "output": GARDEN["output"], "worker": None}
        if self.cistern.seeds or garden is not None:
            ledger["projection"]["garden_archived"] = {
                "seeds_unspent": self.cistern.seeds, "garden": deepcopy(garden)}
        projected.log.append({"day": 0, "event": "campaign_transition", **receipt})
        if community:
            projected.log.append({"day": 0, "event": "community_rules_on",
                                  "professions": dict(projected.community["professions"]),
                                  "hero_kits": community_rules.arrival_kits(projected),
                                  "evacuation_supply":
                                      community_rules.evacuation_supply(projected)})
        projected.validate()
        self.world = projected
        return deepcopy(receipt)

    def _arc(self) -> Arc2:
        self._require_running()
        if self.world is None:
            raise ValueError("Conclua A Cisterna antes da Última Transmissão")
        return Arc2(self.world)

    def advance_day(self, meal_plan: dict | None = None) -> dict:
        self._require_running()
        if self.world is None:
            raise ValueError("Use meal/next_cistern_day na Cisterna")
        result = self.world.end_day(meal_plan=meal_plan)
        if self.world.partial_defeat:
            self.finish("DEFEAT", "derrota_parcial; evacuação da campanha pendente")
        elif all(hero["health"] == 0 for hero in self.world.heroes.values()):
            self.finish("DEFEAT", "todos_os_protagonistas_incapacitados")
        return result

    def decode_radio(self) -> None:
        return self._arc().decode_radio()

    def recover_access_card(self, expedition_id: str) -> None:
        return self._arc().recover_access_card(expedition_id)

    def authorize_installation(self, expedition_id: str, hero_ids: list[str],
                                vehicle_id: str) -> None:
        return self._arc().authorize_installation(expedition_id, hero_ids, vehicle_id)

    def load_transmitter(self, expedition_id: str) -> None:
        return self._arc().load_transmitter(expedition_id)

    def final_defense(self) -> dict:
        return self._arc().final_defense()

    def defense_move(self, hero_id: str, zone: int) -> None:
        self._arc().defense_move(hero_id, zone)

    def defense_attack(self, hero_id: str, item_id: str, enemy_id: str) -> dict:
        return self._arc().defense_attack(hero_id, item_id, enemy_id)

    def defense_activate(self) -> dict:
        result = self._arc().defense_activate()
        if result["status"] == "won":
            self.finish("VICTORY", "defesa_final_concluida")
        elif result["status"] == "lost":
            self.finish("DEFEAT", "defesa_final_perdida")
        return result

    def defense_retreat(self) -> None:
        self._arc().defense_retreat()
        self.finish("DEFEAT", "retirada_da_defesa_final")

    def mark_impossible(self, reason: str) -> None:
        self.finish("IMPOSSIBLE", reason)

    def finish(self, status: str, reason: str) -> None:
        if status not in self.STATUSES - {"RUNNING", "PAUSED"}:
            raise ValueError("Status terminal inválido")
        if self.status != "RUNNING":
            return
        self.status = status
        self.terminal_reason = reason

    def save(self, path: Path) -> None:
        if self.schema != 1 or self.status not in self.STATUSES:
            raise ValueError("Estado de campanha inválido")
        payload = asdict(self)
        payload["cistern"] = asdict(self.cistern)
        payload["tactical"] = self.tactical.snapshot() if self.tactical else None
        payload["travel"] = self.travel.snapshot() if self.travel else None
        payload["travel_context"] = (self.travel_context.snapshot()
                                      if self.travel_context else None)
        payload["ambush"] = self.ambush.snapshot() if self.ambush else None
        payload["return_travel"] = (self.return_travel.snapshot()
                                     if self.return_travel else None)
        payload["return_context"] = (self.return_context.snapshot()
                                      if self.return_context else None)
        payload["return_context_initial"] = self.return_context_initial
        payload["world"] = _world_payload(self.world) if self.world is not None else None
        payload["world"] = {"schema": 2, **payload["world"]} if payload["world"] else None
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "IntegratedCampaign":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.pop("schema", None) != 1:
            raise ValueError("Esquema de campanha desconhecido")
        cistern_state = payload["cistern"]
        had_horde = "horde_deck" in cistern_state
        had_travel = "travel_deck" in cistern_state
        old_campaign_horde = _migrate_horde_snapshot(payload.pop("horde_deck", None))
        old_travel_shoe = payload.pop("travel_shoe", None)
        tactical_state = payload.get("tactical")
        if tactical_state is not None and tactical_state.get("horde_deck") is not None:
            tactical_state["horde_deck"] = _migrate_horde_snapshot(
                tactical_state["horde_deck"])
        ambush_state = payload.get("ambush")
        if ambush_state is not None and ambush_state.get("horde_deck") is not None:
            ambush_state["horde_deck"] = _migrate_horde_snapshot(
                ambush_state["horde_deck"])
        if not had_horde:
            migrated_horde = old_campaign_horde
            if tactical_state and tactical_state.get("horde_deck") is not None:
                tactical_horde = tactical_state["horde_deck"]
                if migrated_horde is not None and migrated_horde != tactical_horde:
                    raise ValueError("Sapatos legados de Horda divergem no save")
                migrated_horde = tactical_horde
            if ambush_state and ambush_state.get("horde_deck") is not None:
                ambush_horde = ambush_state["horde_deck"]
                if migrated_horde is not None and migrated_horde != ambush_horde:
                    raise ValueError("Sapatos legados de Horda divergem no save")
                migrated_horde = ambush_horde
            if migrated_horde is not None:
                cistern_state["horde_deck"] = migrated_horde
        if not had_travel and old_travel_shoe is not None:
            cistern_state["travel_deck"] = TravelDeck02.from_snapshot(
                old_travel_shoe).snapshot()
        cistern_state, migrated_events = Cistern02.upgrade_legacy_event_state(
            cistern_state)
        payload["cistern"] = Cistern02(**cistern_state)
        if migrated_events:
            payload["cistern"].apply_daily_event()
        if payload.get("tactical") is not None:
            payload["tactical"] = Tactical02.from_snapshot(payload["cistern"],
                                                           payload["tactical"])
        if payload.get("travel") is not None:
            payload["travel"] = Travel02.from_snapshot(payload["travel"])
        if payload.get("travel_context") is not None:
            payload["travel_context"] = TravelContext(**payload["travel_context"])
        if payload.get("ambush") is not None:
            payload["ambush"] = Ambush02.from_snapshot(payload["ambush"])
            payload["cistern"].horde_deck = deepcopy(payload["ambush"].horde_deck)
        if payload.get("return_travel") is not None:
            payload["return_travel"] = Travel02.from_snapshot(payload["return_travel"])
        if payload.get("return_context") is not None:
            payload["return_context"] = TravelContext(**payload["return_context"])
        if payload.get("world") is not None:
            payload["world"] = _world_from_payload(payload["world"])
        # Campos de chegada de estrada adicionados na mesma versão do save.
        payload.setdefault("route_known", False)
        payload.setdefault("bridge_known", False)
        payload.setdefault("travel_uses_shoe", False)
        payload.setdefault("road_aid_settled", False)
        payload.setdefault("work_phase_resolved", False)
        payload.setdefault("mission_receipts", [])
        if not isinstance(payload["travel_uses_shoe"], bool):
            raise ValueError("Marcador de sapato de Viagem inválido")
        if (not isinstance(payload["road_aid_settled"], bool)
                or not isinstance(payload["work_phase_resolved"], bool)):
            raise ValueError("Marcador de fase de campanha inválido")
        shoe = TravelDeck02.from_snapshot(payload["cistern"].travel_deck)
        active_trip = payload.get("travel") or payload.get("return_travel")
        if payload["travel_uses_shoe"] and (
                active_trip is None or not shoe.matches_trip(active_trip)):
            raise ValueError("Sapato persistente não corresponde à viagem ativa")
        payload.setdefault("equipment_inventory", {
            hero: ["Pé de cabra"] for hero in payload.get("founders", [])})
        campaign = cls(schema=1, **payload)
        if campaign.status not in cls.STATUSES:
            raise ValueError("Status de campanha desconhecido")
        campaign.cistern.validate_snapshot()
        return campaign


__all__ = ["IntegratedCampaign", "PART_MISSIONS", "LINK_IDS", "STARTERS"]
