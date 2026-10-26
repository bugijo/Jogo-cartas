"""Reproduz o maior avanço atual do motor regional após a Cisterna.

O verificador certifica a Cisterna e executa ações táticas regionais que copiam
e extraem fisicamente uma pista da Estação. Não resolve ainda cartas de Viagem,
portanto NÃO comprova paridade da expedição com o manual 0.2 nem declara a
campanha integral: a segunda pista, contato/recrutamento de Célia, rádio, Posto,
van, instalação, transmissor e defesa final ainda não foram completados.
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
ARTIFACT = ROOT / "replays" / "cistern_to_transmission_seed22_clue_returned.json"


def _start(seed: int):
    player, cistern_report = execute_cistern(seed)
    game = player.game
    migration = game.transition_to_last_transmission()
    world = game.world
    if (not world or game.phase != "last_transmission"
            or not world.cistern_verified
            or migration.get("to") != "last_transmission"):
        raise AssertionError("Migração não veio da vitória certificada da Cisterna")
    return game, migration, world, cistern_report


def _clue_expedition(seed: int, profile: str):
    game, migration, world, cistern_report = _start(seed)
    expedition_id = f"continuous-seed{seed}-station-clue-{profile}"
    start_log = len(world.log)
    result = AdaptiveRegionalPlayer(profile).run_expedition(
        world, expedition_id, "EXP-LOC-05", list(world.heroes), "station_02",
        [
            {"kind": "investigate_contact", "npc": "EXP-NPC-02"},
            {"kind": "evidence", "npc": "EXP-NPC-02"},
        ], max_steps=120)
    regional_log = world.log[start_log:]
    local = result.get("local", {})
    evidence = [row for row in regional_log
                if row.get("action") == "collect_regional_evidence"]
    discovered = [row for row in regional_log
                  if row.get("action") == "investigate_physical_contact"]
    emergencies = [row for row in regional_log
                   if row.get("action") == "emergency_return"]
    returned = result.get("status") == "returned"
    if (len(discovered) != 1 or len(evidence) != 1
            or evidence[0].get("evidence_id") != "EXP-CLUE-001"
            or evidence[0].get("clues_awarded") != 1
            or world.clues != 1 or world.flags.get("radio_code")
            or "EXP-NPC-02" in world.npcs
            or (returned and emergencies)):
        raise AssertionError("A rota de pistas concedeu estado não comprovado")

    status = ("regional_evidence_returned_incomplete" if returned
              else "local_defeat_clock_blocked")
    blocker = ("Uma pista física foi copiada e retornou ao abrigo. O rádio ainda \
exige duas pistas; esta rota não contata/recruta Célia nem conclui o arco."
               if returned else
               "A rota deste perfil terminou em emergência após copiar uma pista; \
a falha de uma política não prova impossibilidade geral da equipe.")
    state = {
        "status": status,
        "scope": "ações táticas públicas do protótipo regional; baralho de Viagem não resolvido; não equivale a expedição canônica integral",
        "phase": game.phase,
        "seed": seed,
        "profile": profile,
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
            "status": result["status"],
            "outbound": result["outbound"],
            "local_status": local.get("status"),
            "decision_count": len(local.get("decisions", [])),
            "decisions": local.get("decisions", []),
            "clock": world.regional_clock,
            "clock_after_emergency": world.regional_clock if emergencies else None,
            "clues": world.clues,
            "clues_physically_returned": world.clues if returned else 0,
            "radio_code": world.flags.get("radio_code", False),
            "celia_recruited": "EXP-NPC-02" in world.npcs,
            "stock_after_return": dict(world.stock),
            "team_fatigue_after_return": {
                hero: world.heroes[hero].get("fatigue", 0)
                for hero in world.heroes
            },
            "emergency_receipts": emergencies,
            "emergency_receipt": emergencies[0] if emergencies else None,
            "log": regional_log,
            "blocker": blocker,
        },
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "continuous-campaign-save.json"
        game.save(path)
        restored = IntegratedCampaign.load(path)
        if asdict(restored.world) != asdict(world):
            raise AssertionError("Save/load divergiu após a expedição regional")
        if restored.transition_to_last_transmission() != migration:
            raise AssertionError("Retomar save duplicou a migração")
    return state


def execute(seed: int = 22) -> dict:
    """Best engine-level path: low-contact clue extraction; not full 0.2 legality."""
    result = _clue_expedition(seed, "stealth")
    if result["status"] != "regional_evidence_returned_incomplete":
        raise AssertionError("A política stealth não extraiu a pista física")
    return result


def execute_balanced_blocked(seed: int = 22) -> dict:
    """Comparison only: the balanced profile spends time on optional combat."""
    result = _clue_expedition(seed, "balanced")
    if result["status"] != "local_defeat_clock_blocked":
        raise AssertionError("A trajetória comparativa mudou; revise o relatório")
    return result


def write_artifact(path: Path = ARTIFACT) -> None:
    result = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": 4, "status": result["status"],
                                "replay": result}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def verify_artifact(path: Path = ARTIFACT) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (payload.get("schema") != 4
            or payload.get("status") != "regional_evidence_returned_incomplete"):
        raise AssertionError("Artefato de pista extraída incompatível")
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
        "profile": result["profile"],
        "regional_status": regional["status"],
        "regional_decisions": regional["decision_count"],
        "clues_returned": regional["clues_physically_returned"],
        "radio_code": regional["radio_code"],
        "celia_recruited": regional["celia_recruited"],
        "clock": regional["clock"],
        "blocker": regional["blocker"],
    }, ensure_ascii=False))
