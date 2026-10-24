"""Baralho de Viagem auditável da campanha A Cisterna 0.2.

Este módulo só resolve a camada de estrada: revela uma carta por trecho,
preserva escolhas pendentes e emite recibos idempotentes. Combate de
Emboscada e aplicação dos efeitos no abrigo continuam sendo responsabilidade
do integrador, para não transformar uma revelação em recompensa implícita.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from random import Random

from cistern02 import CATALOG


CARDS = {
    card["id"]: {
        "id": card["id"], "name": card["name"],
        "text": card["text"], "minimum_rounds": card.get("minimum_rounds", 0),
        "map_module": card.get("map_module"),
    }
    for card in CATALOG["cards"] if card["family"] == "VIA"
}
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

    def reveal(self, direction: str) -> dict:
        if direction not in ("outbound", "return"):
            raise ValueError("Direção inválida")
        if direction == "return" and self.outbound_segments != self.leg_size:
            raise ValueError("Retorno exige completar a ida")
        if self.remaining(direction) <= 0:
            raise ValueError("Trechos da direção já revelados")
        if self.pending_choices or self.pending_ambush is not None:
            raise ValueError("Resolva o evento de Viagem pendente")
        if self.index >= len(self.deck):
            raise ValueError("Baralho de Viagem esgotado")
        card_id = self.deck[self.index]
        self.index += 1
        event_id = f"travel-{self.index:03d}"
        card = CARDS[card_id]
        event = {
            "event_id": event_id, "card_id": card_id, "name": card["name"],
            "text": card["text"], "direction": direction,
            "ambush": card_id == "ZC-VIA-0005",
            "minimum_rounds": card["minimum_rounds"],
        }
        self.events.append(event)
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

    def resolve(self, event_id: str, choice: str) -> dict:
        event, card_id = self._event(event_id)
        if event_id not in self.pending_choices or choice not in CHOICES[card_id]:
            raise ValueError("Escolha de Viagem inválida")
        effect = deepcopy(CHOICES[card_id][choice])
        self.pending_choices.remove(event_id)
        self.resolved[event_id] = {"choice": choice, "effect": effect}
        return effect

    def resolve_ambush(self, event_id: str) -> dict:
        event, _ = self._event(event_id)
        if self.pending_ambush != event_id or not event["ambush"]:
            raise ValueError("Emboscada não está pendente")
        result = {"map": "ZC-MOD-0001", "rounds_required": event["minimum_rounds"]}
        self.pending_ambush = None
        self.resolved[event_id] = {"ambush": result}
        return deepcopy(result)

    def snapshot(self) -> dict:
        return deepcopy({
            "route": self.route, "deck": self.deck, "index": self.index,
            "outbound_segments": self.outbound_segments,
            "return_segments": self.return_segments, "events": self.events,
            "resolved": self.resolved, "pending_choices": self.pending_choices,
            "pending_ambush": self.pending_ambush,
        })

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "Travel02":
        required = {"route", "deck", "index", "outbound_segments",
                    "return_segments", "events", "resolved",
                    "pending_choices", "pending_ambush"}
        if set(snapshot) != required:
            raise ValueError("Snapshot de Viagem incompatível")
        trip = cls(**deepcopy(snapshot))
        if trip.route not in ("short", "long") or any(x not in CARDS for x in trip.deck):
            raise ValueError("Snapshot de Viagem inválido")
        if trip.index < 0 or trip.index > len(trip.deck):
            raise ValueError("Índice de Viagem inválido")
        return trip


__all__ = ["CARDS", "Travel02"]
