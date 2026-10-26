"""Reproduz o primeiro bloqueio regional após a vitória legal da Cisterna.

Este verificador NÃO declara campanha integral. Ele preserva o replay H2 seed
22, migra o estado e tenta investigar/copiar evidência de Célia por ações
públicas. O controlador registra a pista obtida, mas não consegue concluir a
extração dentro do relógio regional. O artefato prova a derrota local, não um
resultado de Última Transmissão.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

from regional_player import AdaptiveRegionalPlayer
from verify_campaign_player02 import execute as execute_cistern
from integrated_campaign import IntegratedCampaign

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "cistern_to_transmission_seed22_blocked.json"


def execute(seed: int = 22) -> dict:
    player, cistern_report = execute_cistern(seed)
    game = player.game
    migration = game.transition_to_last_transmission()
    world = game.world
    if (not world or game.phase != "last_transmission"
            or not world.cistern_verified
            or migration.get("to") != "last_transmission"):
        raise AssertionError("Migração não veio da vitória certificada da Cisterna")

    team = list(world.heroes)
    expedition_id = "continuous-seed22-station-clue"
    policy = AdaptiveRegionalPlayer("balanced")
    start_log = len(world.log)
    result = policy.run_expedition(
        world, expedition_id, "EXP-LOC-05", team, "station_02",
        [
            {"kind": "investigate_contact", "npc": "EXP-NPC-02"},
            {"kind": "evidence", "npc": "EXP-NPC-02"},
        ], max_steps=120)
    regional_log = world.log[start_log:]
    local = result.get("local", {})

    if result.get("status") != "local_defeat_emergency":
        raise AssertionError(f"O bloqueio esperado mudou: {result.get('status')}")
    evidence = [row for row in regional_log
                if row.get("action") == "collect_regional_evidence"]
    discovered = [row for row in regional_log
                  if row.get("action") == "investigate_physical_contact"]
    emergency = next((row for row in regional_log
                      if row.get("action") == "emergency_return"), None)
    if (len(discovered) != 1 or len(evidence) != 1
            or evidence[0].get("evidence_id") != "EXP-CLUE-001"
            or evidence[0].get("clues_awarded") != 1
            or world.clues != 1 or world.flags.get("radio_code")
            or "EXP-NPC-02" in world.npcs
            or emergency is None):
        raise AssertionError("A tentativa regional concedeu estado não comprovado")

    # The experiment reaches physical contact/evidence, then records the
    # controller's actual failure. No recruit, radio flag, fuel or mission item
    # is synthesized.
    state = {
        "status": "local_defeat_clock_blocked",
        "phase": game.phase,
        "seed": seed,
        "cistern": {
            "status": game.cistern.result,
            "days": len(cistern_report["days"]),
            "nights": cistern_report["nights_completed"],
            "expeditions": sum(day["destination"] is not None
                                for day in cistern_report["days"]),
            "decisions": cistern_report["decision_count"],
        },
        "migration": migration,
        "regional_expedition": {
            "destination": "EXP-LOC-05",
            "map": "station_02",
            "outbound": result["outbound"],
            "local_status": local.get("status"),
            "local_reason": local.get("reason"),
            "decision_count": len(local.get("decisions", [])),
            "decisions": local.get("decisions", []),
            "clock_after_emergency": world.regional_clock,
            "clues": world.clues,
            "radio_code": world.flags.get("radio_code", False),
            "celia_recruited": "EXP-NPC-02" in world.npcs,
            "access_card": world.flags.get("access_card", False),
            "fuel_stock": world.stock["fuel"],
            "regional_log": regional_log,
            "emergency_receipt": emergency,
            "blocker": "no station_02, caminho mais curto à zona 14 custa 7 PA (4 movimentos + portas), investigação e evidência somam 2 PA, e o retorno mais curto custa 4 movimentos: mínimo 13 PA individuais. A rota far=3 deixa 3 ativações locais, máximo de 9 PA por herói; a saída não cabe no relógio atual.",
        },
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "continuous-campaign-save.json"
        game.save(path)
        restored = IntegratedCampaign.load(path)
        if asdict(restored.world) != asdict(world):
            raise AssertionError("Save/load divergiu após a retirada regional")
        if restored.transition_to_last_transmission() != migration:
            raise AssertionError("Retomar save duplicou a migração")
    return state


def write_artifact(path: Path = ARTIFACT) -> None:
    result = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": 3, "status": result["status"],
                                "replay": result}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def verify_artifact(path: Path = ARTIFACT) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != 3 or payload.get("status") != "local_defeat_clock_blocked":
        raise AssertionError("Artefato de bloqueio regional incompatível")
    actual = execute(payload["replay"]["seed"])
    if actual != payload["replay"]:
        raise AssertionError("Replay regional divergiu do artefato salvo")
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--path", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    if args.write:
        write_artifact(args.path)
    result = verify_artifact(args.path)
    regional = result["regional_expedition"]
    print(json.dumps({
        "status": result["status"],
        "cistern": result["cistern"],
        "regional_decisions": regional["decision_count"],
        "clues_physically_copied": regional["clues"],
        "radio_code": regional["radio_code"],
        "celia_recruited": regional["celia_recruited"],
        "clock_after_emergency": regional["clock_after_emergency"],
        "blocker": regional["blocker"],
    }, ensure_ascii=False))
