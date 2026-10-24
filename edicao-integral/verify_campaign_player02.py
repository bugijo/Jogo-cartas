"""Executa/verifica o replay legal H2 da Cisterna com seed 22.

Uso: python edicao-integral/verify_campaign_player02.py --write
     python edicao-integral/verify_campaign_player02.py
O replay registra ações públicas e recibos reais; não injeta peças nem estados.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from campaign_player02 import CampaignPlayer02
from integrated_campaign import IntegratedCampaign

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "cisterna_h2_seed22.json"
EVENTS = [f"ZC-EVE-{number:04d}" for number in range(1, 6)]
OBJECTIVES = {"Oficina:Conexões", "Estação:Bomba", "Estação:Membrana"}


def execute(seed: int = 22) -> tuple[CampaignPlayer02, dict]:
    player = CampaignPlayer02.new_h2(seed)
    report = player.attempt_cistern()
    if report["result"] != "verified_victory" or not report["verified_victory"]:
        raise AssertionError(f"Campanha não certificada: {report['blocked']}")
    if len(report["days"]) != 5 or report["nights_completed"] != 5:
        raise AssertionError("Replay não contém cinco dias/noites completos")
    if report["events"] != EVENTS or not OBJECTIVES.issubset(
            set(report["delivered_objectives"])):
        raise AssertionError("Eventos ou objetivos legais divergentes")
    objective_receipts = {
        item["id"] for item in report["receipts"]
        if item.get("event") == "pickup_part"
    }
    if objective_receipts != OBJECTIVES:
        raise AssertionError(f"Recibos de coleta divergentes: {objective_receipts}")
    if len({item["id"] for item in report["receipts"]}) != len(report["receipts"]):
        raise AssertionError("ID de recibo duplicado")
    if len(report["sieges"]) != 2 or report["final_state"]["pending_sieges"]:
        raise AssertionError("Cercos obrigatórios pendentes ou ausentes")
    if player.game.cistern.result != "verified_victory":
        raise AssertionError("Estado da Cisterna não confirma o certificado")
    return player, report


def trace(report: dict) -> dict:
    keys = ("seed", "founders", "links", "setup", "days", "receipts", "events", "sieges",
            "nights_completed", "delivered_objectives", "final_state", "certificate",
            "decision_count", "decisions", "verified_victory", "rewards")
    return {key: report[key] for key in keys}


def write_artifact(path: Path = ARTIFACT) -> None:
    player, report = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        save_path = Path(directory) / "terminal-campaign.json"
        player.game.save(save_path)
        terminal_save = json.loads(save_path.read_text(encoding="utf-8"))
    payload = {
        "schema": 1,
        "description": "Replay determinístico de A Cisterna, H2, iniciado legitimamente.",
        "setup": {"seed": player.seed, "founders": report["founders"],
                  "links_drawn": report["links"], **report["setup"]},
        "trace": trace(report),
        "terminal_save": terminal_save,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def verify_artifact(path: Path = ARTIFACT) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != 1:
        raise AssertionError("Versão de replay desconhecida")
    _, replayed = execute(payload["setup"]["seed"])
    actual = trace(replayed)
    expected_setup = {"seed": replayed["seed"], "founders": replayed["founders"],
                      "links_drawn": replayed["links"], **replayed["setup"]}
    if expected_setup != payload["setup"]:
        raise AssertionError("A preparação salva difere da preparação reproduzida")
    if actual != payload["trace"]:
        raise AssertionError("A reprodução difere do log registrado")
    with tempfile.TemporaryDirectory() as directory:
        save_path = Path(directory) / "terminal-campaign.json"
        save_path.write_text(json.dumps(payload["terminal_save"], ensure_ascii=False),
                             encoding="utf-8")
        restored = IntegratedCampaign.load(save_path)
    restored.cistern.validate_snapshot()
    if (restored.cistern.result != "verified_victory"
            or "verified_victory" not in restored.rewards
            or restored.cistern.event_history != EVENTS):
        raise AssertionError("Save terminal não sobrevive a round-trip")
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="grava o replay verificado")
    parser.add_argument("--path", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    if args.write:
        write_artifact(args.path)
    result = verify_artifact(args.path)
    print(json.dumps({"status": "verified_victory", "days": len(result["days"]),
                      "nights": result["nights_completed"],
                      "expeditions": sum(day["destination"] is not None
                                         for day in result["days"]),
                      "decisions": result["decision_count"],
                      "certificate": result["certificate"]}, ensure_ascii=False))
