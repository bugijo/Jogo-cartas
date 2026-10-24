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
        if len(self.deck) < count and self.discard:
            recycled = self.discard.copy()
            Random(self.seed + 1_000_003 * (self.reshuffles + 1)).shuffle(recycled)
            self.reshuffles += 1
            self.deck.extend(recycled)
            self.discard.clear()
        if len(self.deck) < count:
            raise ValueError("Sapato de Viagem não tem cartas suficientes")

    def prepare_trip(self, count: int) -> list[str]:
        self.ensure_available(count)
        return self.deck.copy()

    def finish_trip(self, trip: "Travel02") -> None:
        if trip.deck != self.deck:
            raise ValueError("A ordem da viagem não corresponde ao sapato ativo")
        if (trip.pending_resolution is not None or trip.pending_choices
                or trip.pending_ambush is not None):
            raise ValueError("Resolva a ocorrência antes de descartar o sapato")
        drawn = [event["card_id"] for event in trip.events
                 if event.get("card_id") is not None]
        if (trip.index != len(drawn) or trip.index > len(self.deck)
                or drawn != self.deck[:trip.index]):
            raise ValueError("A viagem não prova as cartas reveladas do sapato")
        self.discard.extend(drawn)
        self.deck = self.deck[trip.index:]
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
        if any(not isinstance(lot, int) or not 1 <= lot <= 4
               for lot in self.food_lots + self.water_lots):
            raise ValueError("Cursor de carta de porções inválido")
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

    def reveal(self, direction: str, context: TravelContext | None = None) -> dict:
        if direction not in ("outbound", "return"):
            raise ValueError("Direção inválida")
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
            context.fatigue[hero] += effect.get("fatigue", 0)
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

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "Travel02":
        required = {"route", "deck", "index", "outbound_segments",
                    "return_segments", "events", "resolved",
                    "pending_choices", "pending_ambush", "pending_resolution",
                    "skip_return_card"}
        if set(snapshot) != required:
            raise ValueError("Snapshot de Viagem incompatível")
        trip = cls(**deepcopy(snapshot))
        if trip.route not in ("short", "long") or any(x not in CARDS for x in trip.deck):
            raise ValueError("Snapshot de Viagem inválido")
        if trip.index < 0 or trip.index > len(trip.deck):
            raise ValueError("Índice de Viagem inválido")
        return trip


__all__ = ["CARDS", "Travel02", "TravelContext", "TravelShoe02"]
