"""Campanha regional contínua de vários dias (seed 22), com Viagem ligada.

Uso: python edicao-integral/verify_regional_campaign.py --write
     python edicao-integral/verify_regional_campaign.py
Parte da vitória certificada da Cisterna, migra, liga `regional_travel_cards` e
deixa `RegionalCampaignPlayer` jogar até `MAX_DAYS` dias (ou até derrota
parcial/bloqueio de regra), salvando e recarregando a cada dia. Não altera os
replays registrados anteriores.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from regional_campaign_player import RegionalCampaignPlayer
from verify_campaign_player02 import execute as execute_cistern

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "regional_campaign_seed22.json"
MAX_DAYS = 10


def run(seed: int = 22) -> dict:
    cistern_player, _ = execute_cistern(seed)
    campaign = cistern_player.game
    migration = campaign.transition_to_last_transmission()
    if not campaign.world.continuous_campaign:
        raise AssertionError("Pré-requisito não veio da campanha legal da Cisterna")
    campaign.world.regional_travel_cards = True
    campaign.world.regional_filter_production = True
    player = RegionalCampaignPlayer()
    campaign = player.run(campaign, MAX_DAYS)
    world = campaign.world
    expeditions = [day for day in player.days if day.get("expedition")]
    ambushes = [row for row in world.log if row.get("action") == "regional_ambush_finish"]
    cards = [row["card_id"] for row in world.log
             if row.get("action") == "regional_travel_card" and row.get("card_id")]
    evidence = [row["evidence_id"] for row in world.log
                if row.get("action") == "collect_regional_evidence"]
    if world.clues + 2 * bool(world.flags.get("radio_code")) != len(evidence):
        raise AssertionError("Pistas não correspondem às cópias físicas coletadas")
    delivered = {}
    for day in expeditions:
        for resource, amount in (day["expedition"].get("delivered") or {}).items():
            delivered[resource] = delivered.get(resource, 0) + amount
    return {
        "seed": seed,
        "migration_day": migration["day"],
        "days_played": sum(1 for day in player.days if "plan" in day),
        "final_day": world.day,
        "outcome": ("partial_defeat" if world.partial_defeat else
                    "blocked_rule" if any(d.get("result") == "blocked_rule"
                                          for d in player.days) else "running"),
        "objectives": {
            "clue_evidence": evidence,
            "clues": world.clues,
            "radio_code": bool(world.flags.get("radio_code")),
            "access_card": bool(world.flags.get("access_card")),
            "military_access": bool(world.flags.get("military_access")),
        },
        "expeditions": len(expeditions),
        "travel_cards": cards,
        "ambushes": [{key: row[key] for key in ("rounds", "clock", "emergency")}
                     for row in ambushes],
        "delivered_total": delivered,
        "final_stock": dict(world.stock),
        "markets_searches_left": world.searches["EXP-LOC-02"],
        "archive": dict(world.regional_travel_archive),
        "days": player.days,
        "blockers": player.blockers,
        "scope_limit": ("Expedições a pé, uma por dia. Sem combustível/veículos, sem "
                        "carga levada regional, ordem de pistas provisória (Célia, Vicente)."),
    }


def execute(seed: int = 22) -> dict:
    first = run(seed)
    if run(seed) != first:
        raise AssertionError("Campanha regional não é determinística")
    return first


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
            raise SystemExit("Campanha regional diverge do artefato registrado")
    print(json.dumps({key: result[key] for key in ("days_played", "final_day", "outcome",
                                                   "objectives", "expeditions", "blockers")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
