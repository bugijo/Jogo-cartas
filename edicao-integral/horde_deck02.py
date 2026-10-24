"""Sapato de Horda persistente da campanha A Cisterna 0.2."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
from random import Random


CARD_TYPES = ("Arrastar",) * 4 + ("Corrida",) * 2 + ("Aglomerado",) * 2 + ("Peso morto",)


@dataclass
class HordeDeck02:
    seed: int
    deck: list[str]
    discard: list[str]
    reshuffles: int = 0

    @classmethod
    def new(cls, seed: int) -> "HordeDeck02":
        cards = list(CARD_TYPES)
        Random(seed).shuffle(cards)
        return cls(seed, cards, [])

    def draw(self) -> str:
        self.validate()
        if not self.deck:
            if not self.discard:
                raise ValueError("Baralho de Horda vazio")
            cards = self.discard.copy()
            Random(self.seed + 1_000_003 * (self.reshuffles + 1)).shuffle(cards)
            self.deck, self.discard = cards, []
            self.reshuffles += 1
        card = self.deck.pop(0)
        self.discard.append(card)
        self.validate()
        return card

    def validate(self) -> None:
        if (not isinstance(self.seed, int) or isinstance(self.seed, bool)
                or not isinstance(self.reshuffles, int) or isinstance(self.reshuffles, bool)
                or self.reshuffles < 0 or not isinstance(self.deck, list)
                or not isinstance(self.discard, list)):
            raise ValueError("Estado do baralho de Horda inválido")
        cards = self.deck + self.discard
        if (any(not isinstance(card, str) or card not in CARD_TYPES for card in cards)
                or Counter(cards) != Counter(CARD_TYPES)):
            raise ValueError("Estado do baralho de Horda inválido")

    def snapshot(self) -> dict:
        self.validate()
        return deepcopy(asdict(self))

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "HordeDeck02":
        if not isinstance(snapshot, dict) or set(snapshot) != {
                "seed", "deck", "discard", "reshuffles"}:
            raise ValueError("Snapshot do baralho de Horda incompatível")
        deck = cls(**deepcopy(snapshot))
        deck.validate()
        return deck
