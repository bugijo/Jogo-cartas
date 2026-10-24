"""Baralho persistente de Viagem da campanha A Cisterna 0.2."""
from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random


_CATALOG = json.loads((Path(__file__).resolve().parent.parent / "content/catalog.json")
                      .read_text(encoding="utf-8"))
CARD_IDS = tuple(card["id"] for card in _CATALOG["cards"]
                 if card["family"] == "VIA")


@dataclass
class TravelDeck02:
    """Sapato de campanha com descarte e embaralhamento reproduzível."""

    seed: int
    deck: list[str]
    discard: list[str]
    reshuffles: int = 0

    @classmethod
    def new(cls, seed: int) -> "TravelDeck02":
        cards = list(CARD_IDS)
        Random(seed).shuffle(cards)
        return cls(seed, cards, [])

    def draw(self) -> str:
        self.validate()
        if not self.deck:
            cards = self.discard.copy()
            Random(self.seed + 2_000_033 * (self.reshuffles + 1)).shuffle(cards)
            self.deck, self.discard = cards, []
            self.reshuffles += 1
        card_id = self.deck.pop(0)
        self.discard.append(card_id)
        self.validate()
        return card_id

    def validate(self) -> None:
        if (not isinstance(self.seed, int) or isinstance(self.seed, bool)
                or not isinstance(self.reshuffles, int)
                or isinstance(self.reshuffles, bool) or self.reshuffles < 0
                or not isinstance(self.deck, list)
                or not isinstance(self.discard, list)):
            raise ValueError("Estado do baralho de Viagem inválido")
        cards = self.deck + self.discard
        if (any(not isinstance(card, str) or card not in CARD_IDS for card in cards)
                or Counter(cards) != Counter(CARD_IDS)):
            raise ValueError("Estado do baralho de Viagem inválido")

    def snapshot(self) -> dict:
        self.validate()
        return deepcopy(asdict(self))

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "TravelDeck02":
        if not isinstance(snapshot, dict) or set(snapshot) != {
                "seed", "deck", "discard", "reshuffles"}:
            raise ValueError("Snapshot do baralho de Viagem incompatível")
        result = cls(**deepcopy(snapshot))
        result.validate()
        return result
