"""Replay regional com cartas de Viagem e Emboscada ligadas (seed 22).

Uso: python edicao-integral/verify_regional_travel.py --write
     python edicao-integral/verify_regional_travel.py
Parte da vitória certificada da Cisterna, migra, liga `regional_travel_cards`
e joga uma expedição ao Mercado só por APIs públicas. Não altera os replays
regionais já registrados (que seguem com a opção desligada).
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from integrated_campaign import IntegratedCampaign
from regional_player import AdaptiveRegionalPlayer
from travel_deck02 import TravelDeck02
from verify_campaign_player02 import execute as execute_cistern

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "regional_travel_seed22.json"
TRAVEL_ACTIONS = ("regional_travel_card", "regional_travel_choice", "regional_ambush_start",
                  "regional_ambush_attack", "regional_ambush_finish", "road_emergency")


def execute(seed: int = 22) -> dict:
    cistern_player, _ = execute_cistern(seed)
    campaign = cistern_player.game
    campaign.transition_to_last_transmission()
    world = campaign.world
    if not world.continuous_campaign:
        raise AssertionError("Pré-requisito não veio da campanha legal da Cisterna")
    world.regional_travel_cards = True
    stock_before = dict(world.stock)
    player = AdaptiveRegionalPlayer("explorer")
    result = player.run_expedition(world, "regional-travel-seed22-market", "EXP-LOC-02",
                                   sorted(world.heroes), "market_intro",
                                   {"kind": "search", "zone": 5}, max_steps=40)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "campaign.json"
        campaign.save(path)
        reloaded = IntegratedCampaign.load(path).world
    if (reloaded.regional_travel_deck != world.regional_travel_deck
            or reloaded.regional_travel_archive != world.regional_travel_archive
            or reloaded.log != world.log):
        raise AssertionError("Save/load não preservou baralho, arquivo ou recibos de Viagem")
    travel_log = [{key: value for key, value in row.items() if key != "day"}
                  for row in world.log if row.get("action") in TRAVEL_ACTIONS]
    cards = [row["card_id"] for row in travel_log if row["action"] == "regional_travel_card"]
    if cards != TravelDeck02.from_snapshot(world.regional_travel_deck).discard[-len(cards):]:
        raise AssertionError("Cartas reveladas não correspondem ao descarte do baralho")
    if "ZC-VIA-0005" in cards and not any(row["action"] == "regional_ambush_finish"
                                          for row in travel_log):
        raise AssertionError("Emboscada revelada sem resolução")
    delivered = next((row["delivered"] for row in reversed(world.log)
                      if row.get("expedition") == "regional-travel-seed22-market"
                      and "delivered" in row), {})
    return {
        "seed": seed,
        "status": result["status"],
        "outbound": result["outbound"],
        "return": result["return"],
        "local_status": result.get("local", {}).get("status"),
        "travel_log": travel_log,
        "regional_clock": world.regional_clock,
        "archive": dict(world.regional_travel_archive),
        "heroes": {hero: {key: state[key] for key in ("wounds", "fatigue", "location")}
                   for hero, state in sorted(world.heroes.items())},
        "stock_before": stock_before,
        "stock_after": dict(world.stock),
        "delivered": delivered,
        "controller_history": [row for row in player.history
                               if row.get("action") in ("regional_ambush", "travel_choice")],
        "scope_limit": ("Uma expedição a pé ao Mercado. Não cobre carga levada regional, "
                        "veículos, combustível, Célia, transmissor ou defesa final."),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.write:
        ARTIFACT.write_text(json.dumps({"schema": 1, "replay": result}, ensure_ascii=False,
                                       indent=2) + "\n", encoding="utf-8")
    else:
        stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if stored.get("schema") != 1 or stored["replay"] != result:
            raise SystemExit("Replay de Viagem regional diverge do artefato registrado")
    print(json.dumps({key: result[key] for key in ("status", "outbound", "return",
                                                   "regional_clock", "delivered")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
