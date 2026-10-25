"""Replay contínuo até o primeiro bloqueio real após a Cisterna.

Esse artefato não declara a campanha completa: confirma a vitória legal H2,
faz a migração idempotente, executa a rota regional que o motor atual permite
até obter o cartão de acesso e registra a barreira de rádio por falta de pistas.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from integrated_campaign import IntegratedCampaign
from verify_campaign_player02 import execute as execute_cistern

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "cistern_to_transmission_seed22_blocked.json"


def execute(seed: int = 22) -> dict:
    player, cistern_report = execute_cistern(seed)
    game = player.game
    migration = game.transition_to_last_transmission()
    if not game.world or game.phase != "last_transmission" or not game.world.cistern_verified:
        raise AssertionError("A migração não ativou o mundo regional")

    world = game.world
    team = list(world.heroes)
    expedition_id = "continuous-seed22-station"
    world.open_expedition(expedition_id, team, "EXP-LOC-05")
    travel = [world.advance_expedition(expedition_id) for _ in range(3)]
    if travel != ["travel", "travel", "arrived"]:
        raise AssertionError(f"Chegada regional divergente: {travel}")
    found = world.search(expedition_id)
    game.recover_access_card(expedition_id)
    world.begin_return(expedition_id)
    returning = [world.advance_expedition(expedition_id) for _ in range(3)]
    if returning != ["travel", "travel", "returned"]:
        raise AssertionError(f"Retorno regional divergente: {returning}")

    radio_error = None
    try:
        game.decode_radio()
    except ValueError as exc:
        radio_error = str(exc)
    if radio_error != "Frequência indisponível":
        raise AssertionError(f"O portão de rádio não bloqueou como esperado: {radio_error}")
    if world.flags.get("radio_code") or world.clues != 0:
        raise AssertionError("A tentativa bloqueada alterou pistas/código")
    if world.final_defense is not None or "transmitter" in world.special_stock:
        raise AssertionError("A defesa/transmissor apareceu sem cumprir os portões")

    snapshot = {
        "cistern": {
            "status": game.cistern.result,
            "days": game.cistern.day,
            "nights": len(cistern_report["days"]),
            "expeditions": sum(day["destination"] is not None
                                for day in cistern_report["days"]),
            "decisions": cistern_report["decision_count"],
            "objectives": list(game.delivered_objectives),
        },
        "migration": migration,
        "last_transmission": {
            "phase": game.phase,
            "heroes": team,
            "clues": world.clues,
            "access_card": world.flags.get("access_card", False),
            "radio_code": world.flags.get("radio_code", False),
            "station_search": found,
            "fuel": world.stock["fuel"],
            "vehicle": dict(world.vehicles),
            "day": world.day,
            "campaign_actions": [
                {"action": "open_expedition", "destination": "EXP-LOC-05"},
                *[{"action": "advance_expedition", "result": result} for result in travel],
                {"action": "search", "result": found},
                {"action": "recover_access_card", "result": "access_card"},
                {"action": "begin_return"},
                *[{"action": "advance_expedition", "result": result} for result in returning],
                {"action": "decode_radio", "blocked": radio_error},
            ],
            "blocking_requirement": "duas pistas para decifrar o rádio",
        },
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "continuous.json"
        game.save(path)
        restored = IntegratedCampaign.load(path)
        if restored.world is None or restored.world.cistern_record != world.cistern_record:
            raise AssertionError("A proveniência de migração divergiu após save/load")
        if restored.world.stock != world.stock or restored.world.log != world.log:
            raise AssertionError("Estado regional divergiu após save/load")
        if restored.transition_to_last_transmission() != migration:
            raise AssertionError("A retomada duplicou a transição")
    return snapshot


def write_artifact(path: Path = ARTIFACT) -> None:
    result = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": 1, "status": "blocked_before_radio",
                                "replay": result}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def verify_artifact(path: Path = ARTIFACT) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or payload.get("status") != "blocked_before_radio":
        raise AssertionError("Artefato de campanha contínua inválido")
    actual = execute()
    if actual != payload["replay"]:
        raise AssertionError("Replay contínuo difere do artefato salvo")
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--path", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    if args.write:
        write_artifact(args.path)
    result = verify_artifact(args.path)
    print(json.dumps({"status": "blocked_before_radio",
                      "cistern_days": result["cistern"]["days"],
                      "second_arc_actions": len(result["last_transmission"]["campaign_actions"]),
                      "access_card": result["last_transmission"]["access_card"],
                      "clues": result["last_transmission"]["clues"],
                      "blocker": result["last_transmission"]["blocking_requirement"]},
                     ensure_ascii=False))
