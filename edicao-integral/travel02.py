"""Baralho de Viagem auditável da campanha A Cisterna 0.2.

Este módulo só resolve a camada de estrada: revela uma carta por trecho,
preserva escolhas pendentes e emite recibos idempotentes. Combate de
Emboscada e aplicação dos efeitos no abrigo continuam sendo responsabilidade
do integrador, para não transformar uma revelação em recompensa implícita.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from random import Random
from collections import Counter

from cistern02 import CATALOG


CARDS = {
    card["id"]: {
        "id": card["id"], "name": card["name"],
        "text": card["text"], "minimum_rounds": card.get("minimum_rounds", 0),
        "map_module": card.get("map_module"),
    }
    for card in CATALOG["cards"] if card["family"] == "VIA"
}


@dataclass
class TravelShoe02:
    """Baralho persistente de Viagem da campanha, com descarte próprio.

    Um mapa de estrada recebe uma cópia ordenada do sapato atual. Ao encerrar
    a ida/volta (ou uma retirada), somente as cartas realmente reveladas vão
    ao descarte. A cópia permite salvar o estado do encontro sem avançar o
    sapato duas vezes.
    """

    seed: int
    deck: list[str]
    discard: list[str] = field(default_factory=list)
    reshuffles: int = 0

    @classmethod
    def new(cls, seed: int) -> "TravelShoe02":
        deck = list(CARDS)
        Random(seed).shuffle(deck)
        return cls(seed=seed, deck=deck)

    def ensure_available(self, count: int) -> None:
        if not isinstance(count, int) or count < 1:
            raise ValueError("Quantidade de cartas necessária inválida")
        if len(self.deck) < count and not self.discard:
            raise ValueError("Sapato de Viagem não tem cartas suficientes")

    def prepare_trip(self, count: int) -> list[str]:
        self.ensure_available(count)
        planned = self.deck.copy()
        if len(planned) < count:
            recycled = self.discard.copy()
            Random(self.seed + 1_000_003 * (self.reshuffles + 1)).shuffle(recycled)
            planned.extend(recycled)
        return planned

    def matches_trip(self, trip: "Travel02") -> bool:
        if trip.deck[:len(self.deck)] != self.deck:
            return False
        if len(trip.deck) == len(self.deck):
            return True
        if not self.discard:
            return False
        recycled = self.discard.copy()
        Random(self.seed + 1_000_003 * (self.reshuffles + 1)).shuffle(recycled)
        return trip.deck[len(self.deck):] == recycled

    def finish_trip(self, trip: "Travel02") -> None:
        if not self.matches_trip(trip):
            raise ValueError("A ordem da viagem não corresponde ao sapato ativo")
        if (trip.pending_resolution is not None or trip.pending_choices
                or trip.pending_ambush is not None):
            raise ValueError("Resolva a ocorrência antes de descartar o sapato")
        drawn = [event["card_id"] for event in trip.events
                 if event.get("card_id") is not None]
        if (trip.index != len(drawn) or trip.index > len(trip.deck)
                or drawn != trip.deck[:trip.index]):
            raise ValueError("A viagem não prova as cartas reveladas do sapato")
        draw_pile_size = len(self.deck)
        if trip.index <= draw_pile_size:
            self.discard.extend(drawn)
            self.deck = self.deck[trip.index:]
        else:
            consumed_from_discard = trip.index - draw_pile_size
            recycled = trip.deck[draw_pile_size:]
            self.deck = recycled[consumed_from_discard:]
            self.discard = drawn
            self.reshuffles += 1
        self.validate()

    def validate(self) -> None:
        if (not isinstance(self.seed, int) or not isinstance(self.reshuffles, int)
                or self.reshuffles < 0
                or any(card not in CARDS for card in self.deck + self.discard)
                or Counter(self.deck + self.discard) != Counter(CARDS.keys())):
            raise ValueError("Estado do sapato de Viagem inválido")

    def snapshot(self) -> dict:
        return deepcopy(asdict(self))

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "TravelShoe02":
        if set(snapshot) != {"seed", "deck", "discard", "reshuffles"}:
            raise ValueError("Snapshot do sapato de Viagem incompatível")
        shoe = cls(**deepcopy(snapshot))
        shoe.validate()
        return shoe
CHOICES = {
    "ZC-VIA-0002": {"water": {"water_loss": 1},
                    "fatigue": {"fatigue": 1}},
    "ZC-VIA-0004": {"material": {"material_loss": 1},
                    "pressure": {"pressure": 1}},
    "ZC-VIA-0006": {"help": {"food_loss": 1, "water_loss": 1,
                                "moral": 1},
                    "decline": {}},
    "ZC-VIA-0009": {"accept": {"dog": 1}, "decline": {}},
}
AUTO_EFFECTS = {
    "ZC-VIA-0001": {},
    "ZC-VIA-0003": {"skip_return_card": 1},
    "ZC-VIA-0007": {"pressure": 1},
    "ZC-VIA-0008": {"route_known": 1},
    "ZC-VIA-0010": {"material_drop": 1},
    "ZC-VIA-0011": {"bridge_known": 1},
    "ZC-VIA-0012": {},
}


@dataclass
class TravelContext:
    """Recursos levados e marcadores alterados na estrada."""

    food: int
    water: int
    materials: int
    fatigue: dict[str, int]
    pressure: int = 0
    moral: int = 5
    route_known: bool = False
    bridge_known: bool = False
    skip_return_card: int = 0
    dogs: int = 0
    eligible_dog_adoption: bool = False
    dog_family: str | None = None
    food_lots: list[int] = field(default_factory=list)
    water_lots: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if (not isinstance(self.food, int) or self.food < 0
                or not isinstance(self.water, int) or self.water < 0
                or not isinstance(self.materials, int) or self.materials < 0):
            raise ValueError("Carga de viagem inválida")
        # Migra saves/contextos legados: saldos agregados viram cursors
        # parciais sem inventar porções, mantendo cada carta como uma carga.
        if not self.food_lots and self.food:
            self.food_lots = self._pack(self.food)
        if not self.water_lots and self.water:
            self.water_lots = self._pack(self.water)
        if (self.food != sum(self.food_lots)
                or self.water != sum(self.water_lots)):
            raise ValueError("Saldo de porções diverge das cartas carregadas")
        if any(not isinstance(lot, int) or not 1 <= lot <= 4
               for lot in self.food_lots + self.water_lots):
            raise ValueError("Cursor de carta de porções inválido")
        if (not isinstance(self.fatigue, dict)
                or any(not isinstance(value, int) or isinstance(value, bool)
                       or not 0 <= value <= 3 for value in self.fatigue.values())):
            raise ValueError("Fadiga na carga de Viagem inválida")
        self.food = sum(self.food_lots)
        self.water = sum(self.water_lots)

    @staticmethod
    def _pack(amount: int) -> list[int]:
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("Saldo de porções inválido")
        lots=[]
        while amount:
            cursor=min(4,amount)
            lots.append(cursor)
            amount-=cursor
        return lots

    def consume(self, kind: str, amount: int) -> None:
        if kind not in ("food", "water") or amount < 0:
            raise ValueError("Consumo de carga inválido")
        lots = self.food_lots if kind == "food" else self.water_lots
        remaining = amount
        while remaining and lots:
            used = min(remaining, lots[0])
            lots[0] -= used
            remaining -= used
            if lots[0] == 0:
                lots.pop(0)
        if remaining:
            raise ValueError("Porções insuficientes na carga da viagem")
        setattr(self, kind, sum(lots))

    def snapshot(self) -> dict:
        return deepcopy(asdict(self))


@dataclass
class Travel02:
    """Estado serializável da viagem de uma expedição.

    ``segments`` conta apenas trechos revelados. O relógio da campanha é
    consumido pelo motor tático; manter as duas contagens separadas evita
    pagar tempo duas vezes quando a integração for conectada.
    """

    route: str
    deck: list[str]
    index: int = 0
    outbound_segments: int = 0
    return_segments: int = 0
    events: list[dict] = field(default_factory=list)
    resolved: dict[str, dict] = field(default_factory=dict)
    pending_choices: list[str] = field(default_factory=list)
    pending_ambush: str | None = None
    pending_resolution: str | None = None
    skip_return_card: int = 0

    @classmethod
    def new(cls, seed: int, route: str = "short") -> "Travel02":
        if route not in ("short", "long"):
            raise ValueError("Rota inválida")
        deck = list(CARDS)
        Random(seed).shuffle(deck)
        return cls(route=route, deck=deck)

    @classmethod
    def from_deck(cls, deck: list[str], route: str = "short") -> "Travel02":
        if route not in ("short", "long") or not deck:
            raise ValueError("Baralho ou rota inválidos")
        if any(card_id not in CARDS for card_id in deck):
            raise ValueError("Carta de Viagem inválida")
        return cls(route=route, deck=list(deck))

    @property
    def leg_size(self) -> int:
        return 1 if self.route == "short" else 2

    @property
    def segments(self) -> int:
        return self.outbound_segments + self.return_segments

    def remaining(self, direction: str) -> int:
        if direction not in ("outbound", "return"):
            raise ValueError("Direção inválida")
        used = self.outbound_segments if direction == "outbound" else self.return_segments
        return self.leg_size - used

    def reveal(self, direction: str, context: TravelContext | None = None,
               clock_segment: int | None = None) -> dict:
        if direction not in ("outbound", "return"):
            raise ValueError("Direção inválida")
        if self.requires_night_extra(direction):
            raise ValueError("Resolva a extra noturna antes do próximo trecho")
        if (clock_segment is not None and
                (not isinstance(clock_segment, int) or isinstance(clock_segment, bool)
                 or not 1 <= clock_segment <= 10)):
            raise ValueError("Segmento do relógio inválido")
        if direction == "return" and self.outbound_segments != self.leg_size:
            raise ValueError("Retorno exige completar a ida")
        if self.remaining(direction) <= 0:
            raise ValueError("Trechos da direção já revelados")
        if (self.pending_resolution is not None or self.pending_choices
                or self.pending_ambush is not None):
            raise ValueError("Resolva o evento de Viagem pendente")
        if direction == "return" and self.skip_return_card:
            if self.skip_return_card < 1:
                raise ValueError("Contador de carta de retorno inválido")
            self.skip_return_card -= 1
            if context is not None and context.skip_return_card:
                context.skip_return_card -= 1
            self.return_segments += 1
            event_id = f"travel-return-{self.return_segments:03d}"
            skipped = {"event_id":event_id, "card_id":None, "direction":direction,
                       "skipped":True, "text":"Ignore a próxima Viagem normal; pague o trecho."}
            if clock_segment is not None:
                skipped["clock_segment"] = clock_segment
            self.events.append(skipped)
            self.resolved[event_id] = {"skipped":True}
            return deepcopy(skipped)
        if self.index >= len(self.deck):
            raise ValueError("Baralho de Viagem esgotado")
        card_id = self.deck[self.index]
        self.index += 1
        segment_no = (self.outbound_segments if direction == "outbound"
                      else self.return_segments) + 1
        event_id = f"travel-{direction}-{segment_no:03d}"
        card = CARDS[card_id]
        event = {
            "event_id": event_id, "card_id": card_id, "name": card["name"],
            "text": card["text"], "direction": direction,
            "ambush": card_id == "ZC-VIA-0005",
            "minimum_rounds": card["minimum_rounds"],
        }
        if clock_segment is not None:
            event["clock_segment"] = clock_segment
        self.events.append(event)
        self.pending_resolution = event_id
        if direction == "outbound":
            self.outbound_segments += 1
        else:
            self.return_segments += 1
        if card_id in CHOICES:
            self.pending_choices.append(event_id)
        if event["ambush"]:
            self.pending_ambush = event_id
        return deepcopy(event)

    def requires_night_extra(self, direction: str) -> bool:
        """True quando o último trecho pago cruzou o relógio em 9 ou 10."""
        segment_no = (self.outbound_segments if direction == "outbound"
                      else self.return_segments if direction == "return" else 0)
        if not segment_no:
            return False
        segment_id = f"travel-{direction}-{segment_no:03d}"
        normal = next((event for event in self.events
                       if event.get("event_id") == segment_id), None)
        if not normal or normal.get("clock_segment", 0) < 9:
            return False
        return not any(event.get("extra") is True
                       and event.get("segment_event_id") == segment_id
                       for event in self.events)

    def reveal_night_extra(self, direction: str,
                           clock_segment: int | None = None) -> dict:
        """Revela a carta adicional de um trecho já pago nos segmentos 9–10.

        Esta ocorrência não incrementa o contador de trechos. O integrador é
        responsável por cobrar o segmento e aplicar a fadiga uma única vez.
        """
        if direction not in ("outbound", "return"):
            raise ValueError("Direção inválida")
        if direction == "return" and self.outbound_segments != self.leg_size:
            raise ValueError("Retorno exige completar a ida")
        if (self.pending_resolution is not None or self.pending_choices
                or self.pending_ambush is not None):
            raise ValueError("Resolva o evento de Viagem pendente")
        segment_no = (self.outbound_segments if direction == "outbound"
                      else self.return_segments)
        if segment_no < 1:
            raise ValueError("Carta extra exige trecho noturno já pago")
        segment_event_id = f"travel-{direction}-{segment_no:03d}"
        normal = next((event for event in self.events
                       if event.get("event_id") == segment_event_id), None)
        if normal is None:
            raise ValueError("Carta extra exige trecho normal revelado")
        segment_clock = (normal.get("clock_segment") if clock_segment is None
                         else clock_segment)
        if (not isinstance(segment_clock, int) or isinstance(segment_clock, bool)
                or not 9 <= segment_clock <= 10
                or (normal.get("clock_segment") is not None
                    and segment_clock != normal["clock_segment"])):
            raise ValueError("Carta extra exige segmento noturno 9 ou 10")
        event_id = f"{segment_event_id}-extra"
        if any(event.get("event_id") == event_id for event in self.events):
            raise ValueError("extra noturna já revelada para este trecho")
        if self.index >= len(self.deck):
            raise ValueError("Baralho de Viagem esgotado")
        card_id = self.deck[self.index]
        self.index += 1
        card = CARDS[card_id]
        event = {
            "event_id": event_id, "card_id": card_id, "name": card["name"],
            "text": card["text"], "direction": direction,
            "ambush": card_id == "ZC-VIA-0005",
            "minimum_rounds": card["minimum_rounds"], "extra": True,
            "segment_event_id": segment_event_id,
            "clock_segment": segment_clock,
        }
        self.events.append(event)
        self.pending_resolution = event_id
        if card_id in CHOICES:
            self.pending_choices.append(event_id)
        if event["ambush"]:
            self.pending_ambush = event_id
        return deepcopy(event)

    def _event(self, event_id: str) -> tuple[dict, str]:
        event = next((item for item in self.events if item["event_id"] == event_id), None)
        if event is None:
            raise ValueError("Evento de Viagem inexistente")
        if event_id in self.resolved:
            raise ValueError("Evento de Viagem já resolvido")
        return event, event["card_id"]

    def resolve(self, event_id: str, choice: str,
                context: TravelContext) -> dict:
        """Resolve escolha e aplica o custo/efeito atomicamente ao contexto."""
        return self.apply(event_id, context, choice)

    def resolve_ambush(self, event_id: str) -> dict:
        """Retorna a especificação M1 sem liberar a viagem.

        A pendência só pode ser encerrada após o motor tático registrar a rodada
        obrigatória e a saída segura. Como M1 ainda não está ligado ao motor,
        este método falha fechado e mantém o evento pendente.
        """
        event, _ = self._event(event_id)
        if (self.pending_ambush != event_id or self.pending_resolution != event_id
                or not event["ambush"]):
            raise ValueError("Emboscada não está pendente")
        result = {"map": "ZC-MOD-0001", "rounds_required": event["minimum_rounds"]}
        return deepcopy(result)

    def complete_ambush(self, event_id: str, encounter) -> dict:
        """Finaliza só com recibo do motor após rodada e retorno seguros."""
        event, _ = self._event(event_id)
        required = event["minimum_rounds"]
        if (self.pending_ambush != event_id or self.pending_resolution != event_id
                or not event["ambush"] or not getattr(encounter,"returned",False)
                or getattr(encounter,"failed",False)
                or getattr(encounter,"round_no",0) < required
                or getattr(encounter,"completed_rounds",0) != getattr(encounter,"round_no",-1)
                or any(zone != 1 for zone in getattr(encounter,"positions",{}).values())
                or any(enemy.get("zone") == 1 for enemy in getattr(encounter,"enemies",[]))):
            raise ValueError("Recibo da Emboscada não prova a rodada e saída seguras")
        result={"map":"ZC-MOD-0001","rounds":encounter.completed_rounds,
                "returned":True}
        self.pending_ambush=None
        self.pending_resolution=None
        self.resolved[event_id]={"ambush":deepcopy(result)}
        return result

    def complete_emergency_ambush(self, event_id: str, encounter) -> dict:
        """Registra retirada e falha local sem falsificar saída segura."""
        event, _ = self._event(event_id)
        if (self.pending_ambush != event_id or self.pending_resolution != event_id
                or not event["ambush"] or not getattr(encounter, "returned", False)
                or not getattr(encounter, "failed", False)
                or not any(entry.get("event") == "emergency"
                           for entry in getattr(encounter, "log", []))):
            raise ValueError("Recibo não prova retirada de emergência")
        result = {"map": "ZC-MOD-0001", "failed": True,
                  "rounds": getattr(encounter, "completed_rounds", 0)}
        self.pending_ambush = None
        self.pending_resolution = None
        self.resolved[event_id] = {"ambush": deepcopy(result)}
        return result

    def apply(self, event_id: str, context: TravelContext,
              choice: str | None = None) -> dict:
        """Aplica um efeito depois de validar todos os custos.

        O recibo é gravado apenas depois da validação, para que falta de
        recurso não deixe metade de um efeito aplicada.
        """
        event, card_id = self._event(event_id)
        if self.pending_resolution != event_id:
            raise ValueError("Resolva a ocorrência atual antes de outra")
        if event["ambush"]:
            raise ValueError("Resolva a Emboscada no mapa tático")
        if card_id in CHOICES:
            if event_id not in self.pending_choices or choice not in CHOICES[card_id]:
                raise ValueError("Escolha de Viagem inválida")
            effect = deepcopy(CHOICES[card_id][choice])
        else:
            if event_id in self.pending_choices or choice is not None:
                raise ValueError("Carta de Viagem não aceita escolha")
            effect = deepcopy(AUTO_EFFECTS.get(card_id, {}))
            if card_id == "ZC-VIA-0010" and event["direction"] == "return":
                effect = {"material_gain": 1}
        water_loss = effect.get("water_loss", 0)
        food_loss = effect.get("food_loss", 0)
        material_loss = effect.get("material_loss", effect.get("material_drop", 0))
        if (card_id == "ZC-VIA-0009" and choice == "accept"
                and not context.eligible_dog_adoption):
            raise ValueError("Nenhuma família elegível para acolher o cão")
        if context.water < water_loss or context.food < food_loss:
            raise ValueError("Recurso levado insuficiente para Viagem")
        if context.materials < material_loss:
            raise ValueError("Material levado insuficiente para Viagem")
        context.consume("water", water_loss)
        context.consume("food", food_loss)
        context.materials -= material_loss
        context.materials += effect.get("material_gain", 0)
        context.dogs += effect.get("dog", 0)
        context.pressure += effect.get("pressure", 0)
        context.moral = min(5, context.moral + effect.get("moral", 0))
        for hero in context.fatigue:
            context.fatigue[hero] = min(
                3, context.fatigue[hero] + effect.get("fatigue", 0))
        context.route_known |= bool(effect.get("route_known"))
        context.bridge_known |= bool(effect.get("bridge_known"))
        context.skip_return_card += effect.get("skip_return_card", 0)
        self.skip_return_card += effect.get("skip_return_card", 0)
        self.pending_choices = [item for item in self.pending_choices
                                if item != event_id]
        self.pending_resolution = None
        self.resolved[event_id] = {"choice": choice, "effect": deepcopy(effect)}
        return effect

    def snapshot(self) -> dict:
        return deepcopy({
            "route": self.route, "deck": self.deck, "index": self.index,
            "outbound_segments": self.outbound_segments,
            "return_segments": self.return_segments, "events": self.events,
            "resolved": self.resolved, "pending_choices": self.pending_choices,
            "pending_ambush": self.pending_ambush,
            "pending_resolution": self.pending_resolution,
            "skip_return_card": self.skip_return_card,
        })

    def validate_snapshot_state(self) -> None:
        if (self.route not in ("short", "long")
                or not isinstance(self.deck, list)
                or any(card not in CARDS for card in self.deck)
                or not isinstance(self.index, int) or isinstance(self.index, bool)
                or not 0 <= self.index <= len(self.deck)
                or not isinstance(self.outbound_segments, int)
                or isinstance(self.outbound_segments, bool)
                or not isinstance(self.return_segments, int)
                or isinstance(self.return_segments, bool)
                or not isinstance(self.events, list)
                or not isinstance(self.resolved, dict)
                or not isinstance(self.pending_choices, list)
                or not isinstance(self.skip_return_card, int)
                or isinstance(self.skip_return_card, bool)
                or self.skip_return_card < 0):
            raise ValueError("Snapshot de Viagem inválido")
        leg_size = self.leg_size
        if (not 0 <= self.outbound_segments <= leg_size
                or not 0 <= self.return_segments <= leg_size):
            raise ValueError("Contadores de trechos no snapshot inválidos")

        segment_counts = {"outbound": 0, "return": 0}
        drawn: list[str] = []
        seen_return = False
        event_ids: list[str] = []
        by_id: dict[str, dict] = {}
        segment_event_ids: dict[str, dict] = {}
        extra_segments: set[str] = set()
        for event in self.events:
            if not isinstance(event, dict) or event.get("direction") not in segment_counts:
                raise ValueError("Evento de Viagem inválido no snapshot")
            direction = event["direction"]
            if direction == "return":
                seen_return = True
            elif seen_return:
                raise ValueError("Snapshot mistura a ordem das pernas de Viagem")
            event_id = event.get("event_id")
            is_extra = event.get("extra") is True
            if is_extra:
                segment_event_id = event.get("segment_event_id")
                segment_event = segment_event_ids.get(segment_event_id)
                if (segment_event is None or segment_event["direction"] != direction
                        or segment_event.get("skipped")
                        or event_id != f"{segment_event_id}-extra"
                        or segment_event_id in extra_segments):
                    raise ValueError("ID de extra noturna fora de sequência")
                extra_segments.add(segment_event_id)
                segment_no = segment_counts[direction]
            else:
                if "extra" in event or "segment_event_id" in event:
                    raise ValueError("Evento normal marcado como extra")
                segment_counts[direction] += 1
                segment_no = segment_counts[direction]
                if event_id != f"travel-{direction}-{segment_no:03d}":
                    raise ValueError("ID de trecho de Viagem fora de sequência")
            if event_id in by_id:
                raise ValueError("Evento de Viagem duplicado")
            by_id[event_id] = event
            segment_event_ids[event_id] = event
            event_ids.append(event_id)
            if event.get("skipped") is True:
                expected = {"event_id": event_id, "card_id": None,
                            "direction": "return", "skipped": True,
                            "text": "Ignore a próxima Viagem normal; pague o trecho."}
                if "clock_segment" in event:
                    expected["clock_segment"] = event["clock_segment"]
                    if (not isinstance(event["clock_segment"], int)
                            or isinstance(event["clock_segment"], bool)
                            or not 1 <= event["clock_segment"] <= 10):
                        raise ValueError("Segmento do relógio inválido no evento")
                if event != expected:
                    raise ValueError("Trecho ignorado adulterado")
            else:
                card_id = event.get("card_id")
                if card_id not in CARDS:
                    raise ValueError("Carta de Viagem inválida no evento")
                card = CARDS[card_id]
                expected = {"event_id": event_id, "card_id": card_id,
                            "name": card["name"], "text": card["text"],
                            "direction": direction,
                            "ambush": card_id == "ZC-VIA-0005",
                            "minimum_rounds": card["minimum_rounds"]}
                if event.get("extra") is True:
                    expected.update({"extra": True,
                                     "segment_event_id": event_id.removesuffix("-extra")})
                    expected["clock_segment"] = event.get("clock_segment")
                    segment_event = segment_event_ids.get(expected["segment_event_id"])
                    if (segment_event is None
                            or segment_event.get("clock_segment") != expected["clock_segment"]
                            or not isinstance(expected["clock_segment"], int)
                            or isinstance(expected["clock_segment"], bool)
                            or not 9 <= expected["clock_segment"] <= 10):
                        raise ValueError("Carta extra não corresponde ao segmento noturno")
                elif "clock_segment" in event:
                    expected["clock_segment"] = event["clock_segment"]
                    if (not isinstance(event["clock_segment"], int)
                            or isinstance(event["clock_segment"], bool)
                            or not 1 <= event["clock_segment"] <= 10):
                        raise ValueError("Segmento do relógio inválido no evento")
                if event != expected:
                    raise ValueError("Conteúdo do evento de Viagem adulterado")
                drawn.append(card_id)
        if (self.index != len(drawn) or drawn != self.deck[:self.index]
                or segment_counts != {"outbound": self.outbound_segments,
                                      "return": self.return_segments}
                or (self.return_segments and self.outbound_segments != leg_size)
                or self.pending_choices != list(dict.fromkeys(self.pending_choices))):
            raise ValueError("Eventos, índices e segmentos de Viagem divergem")

        if (self.pending_resolution is not None
                and (self.pending_resolution not in by_id
                     or not event_ids
                     or self.pending_resolution != event_ids[-1])):
            raise ValueError("Ocorrência pendente de Viagem inválida")
        expected_resolved = set(event_ids)
        if self.pending_resolution is not None:
            expected_resolved.remove(self.pending_resolution)
        if set(self.resolved) != expected_resolved:
            raise ValueError("Recibos de Viagem não correspondem aos eventos")

        pending_event = (by_id[self.pending_resolution]
                         if self.pending_resolution is not None else None)
        pending_card = pending_event.get("card_id") if pending_event else None
        expected_choices = ([self.pending_resolution]
                            if pending_card in CHOICES else [])
        expected_ambush = (self.pending_resolution
                           if pending_card == "ZC-VIA-0005" else None)
        if (self.pending_choices != expected_choices
                or self.pending_ambush != expected_ambush):
            raise ValueError("Escolhas/Emboscada pendentes não correspondem à carta")

        remaining_skips = 0
        for event_id, receipt in self.resolved.items():
            event = by_id[event_id]
            if not isinstance(receipt, dict):
                raise ValueError("Recibo de Viagem inválido")
            if event.get("skipped"):
                if receipt != {"skipped": True}:
                    raise ValueError("Recibo de trecho ignorado inválido")
                continue
            card_id = event["card_id"]
            if card_id == "ZC-VIA-0005":
                if set(receipt) != {"ambush"} or not isinstance(receipt["ambush"], dict):
                    raise ValueError("Recibo de Emboscada inválido")
                proof = receipt["ambush"]
                if proof.get("map") != "ZC-MOD-0001":
                    raise ValueError("Mapa de Emboscada divergente")
                if proof.get("failed") is True:
                    if (set(proof) != {"map", "failed", "rounds"}
                            or not isinstance(proof["rounds"], int)
                            or not 0 <= proof["rounds"] <= 10):
                        raise ValueError("Retirada da Emboscada inválida")
                elif (set(proof) != {"map", "rounds", "returned"}
                      or proof.get("returned") is not True
                      or not isinstance(proof.get("rounds"), int)
                      or not event["minimum_rounds"] <= proof["rounds"] <= 10):
                    raise ValueError("Saída segura da Emboscada inválida")
                continue
            if not isinstance(receipt, dict) or set(receipt) != {"choice", "effect"}:
                raise ValueError("Recibo de Viagem inválido")
            choice = receipt["choice"]
            effect = receipt["effect"]
            if card_id in CHOICES:
                if choice not in CHOICES[card_id] or effect != CHOICES[card_id][choice]:
                    raise ValueError("Efeito de escolha de Viagem adulterado")
            else:
                expected_effect = deepcopy(AUTO_EFFECTS.get(card_id, {}))
                if card_id == "ZC-VIA-0010" and event["direction"] == "return":
                    expected_effect = {"material_gain": 1}
                if choice is not None or effect != expected_effect:
                    raise ValueError("Efeito automático de Viagem adulterado")
            remaining_skips += effect.get("skip_return_card", 0)
        remaining_skips -= sum(bool(event.get("skipped"))
                               for event in self.events)
        if remaining_skips != self.skip_return_card:
            raise ValueError("Contador de cartas ignoradas diverge dos recibos")

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "Travel02":
        required = {"route", "deck", "index", "outbound_segments",
                    "return_segments", "events", "resolved",
                    "pending_choices", "pending_ambush", "pending_resolution",
                    "skip_return_card"}
        if set(snapshot) != required:
            raise ValueError("Snapshot de Viagem incompatível")
        trip = cls(**deepcopy(snapshot))
        trip.validate_snapshot_state()
        return trip


__all__ = ["CARDS", "Travel02", "TravelContext", "TravelShoe02"]
