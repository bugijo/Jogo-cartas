"""Baralho persistente de Horda, baseado nas nove cartas canônicas da ed. 0.2."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from random import Random


_CATALOG = json.loads((Path(__file__).resolve().parent.parent / "content/catalog.json")
                     .read_text(encoding="utf-8"))
_CARDS = {card["id"]: card for card in _CATALOG["cards"]
          if card.get("family") == "HOR"}
CARD_IDS = tuple(sorted(_CARDS))


class HordeDeck02:
    """Shoe serializável: compra, descarte e reembaralhamento determinístico."""

    @staticmethod
    def new(seed: int) -> dict:
        cards = list(CARD_IDS)
        Random(seed).shuffle(cards)
        return {"seed": seed, "reshuffles": 0, "draw_pile": cards, "discard": []}

    @staticmethod
    def validate(snapshot: dict) -> dict:
        if not isinstance(snapshot, dict) or set(snapshot) != {
                "seed", "reshuffles", "draw_pile", "discard"}:
            raise ValueError("Estado do baralho Horda incompatível")
        pile, discard = snapshot["draw_pile"], snapshot["discard"]
        if (not isinstance(snapshot["seed"], int)
                or not isinstance(snapshot["reshuffles"], int)
                or snapshot["reshuffles"] < 0
                or not isinstance(pile, list) or not isinstance(discard, list)
                or len(pile) + len(discard) != len(CARD_IDS)
                or sorted(pile + discard) != list(CARD_IDS)):
            raise ValueError("Cartas duplicadas ou ausentes no baralho Horda")
        return deepcopy(snapshot)

    @classmethod
    def draw(cls, snapshot: dict) -> tuple[str, dict]:
        state = cls.validate(snapshot)
        if not state["draw_pile"]:
            state["draw_pile"] = state["discard"]
            state["discard"] = []
            state["reshuffles"] += 1
            Random(state["seed"] + 104729 * state["reshuffles"]).shuffle(
                state["draw_pile"])
        card_id = state["draw_pile"].pop(0)
        state["discard"].append(card_id)
        return card_id, state

    @staticmethod
    def card_type(card_id: str) -> str:
        try:
            return _CARDS[card_id]["name"]
        except KeyError as exc:
            raise ValueError("Carta Horda desconhecida") from exc


__all__ = ["HordeDeck02", "CARD_IDS"]
