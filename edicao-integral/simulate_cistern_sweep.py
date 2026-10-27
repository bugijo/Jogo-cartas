"""Varredura reproduzível de A Cisterna em H2–H6 com o controlador heurístico.

Uso: python edicao-integral/simulate_cistern_sweep.py --write
     python edicao-integral/simulate_cistern_sweep.py

Cada tentativa usa apenas ações públicas de CampaignPlayer02; nada é injetado.
O resultado mede o controlador fixo (plano Mercado → Oficina → Estação), não o
equilíbrio do jogo: taxa baixa pode refletir limitação da heurística.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from campaign_player02 import CampaignPlayer02

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "cistern_sweep_h2_h6.json"
SIZES = range(2, 7)
SEEDS = range(1, 31)
# Sementes nunca usadas para escolher a política adaptativa por tamanho.
HELDOUT = range(31, 61)
# Validação cega: medida uma vez antes de qualquer ajuste (2026-10-27).
VALIDATION = range(61, 91)
CONTROLLERS = {
    "fixed": {},
    "adaptive_oficina_first": {"adaptive": True, "adaptive_order": ("Oficina", "Estação")},
    "adaptive_estacao_first": {"adaptive": True, "adaptive_order": ("Estação", "Oficina")},
}


def previous_settings(size: int) -> dict:
    """Adaptativo publicado antes das táticas da Estação (ordem por tamanho)."""
    order = ("Estação", "Oficina") if size >= 5 else ("Oficina", "Estação")
    return {"adaptive": True, "adaptive_order": order, "tactics": ()}


def auto_settings(size: int) -> dict:
    """Escolha registrada a partir das sementes 1–30, validada em 31–60.

    Com escolta, recuo por tempo, rota cautelosa e apoio, Oficina primeiro foi
    melhor ou próximo em todos os tamanhos nas sementes de ajuste.
    """
    return {"adaptive": True, "adaptive_order": ("Oficina", "Estação")}


REQUIRED_PARTS = ("Conexões", "Bomba", "Membrana")


def classify(report: dict) -> str:
    """Primeira causa observável, derivada do relatório da tentativa."""
    if report["verified_victory"]:
        return "verified_victory"
    for day in report["days"]:
        if day["destination"] and day["tactical_outcome"] != "returned":
            return f"expedition_{day['destination']}_{day['tactical_outcome']}"
    parts = report["final_state"]["parts"]
    missing = [part for part in REQUIRED_PARTS if part not in parts]
    if missing:
        return "missing_part_" + "+".join(missing)
    if report["result"] == "partial_defeat":
        people = report["final_state"]["people"]
        if any(person["hungry"] or person["thirsty"] for person in people):
            return "partial_defeat_hunger_or_thirst"
        return "partial_defeat_health_or_morale"
    blocked = report["blocked"] or {}
    if blocked.get("action"):
        return f"blocked_{blocked['action']}"
    return f"result_{report['result']}"


def run_one(size: int, seed: int, settings: dict | None = None) -> dict:
    player = CampaignPlayer02.new_hn(seed, size)
    for key, value in (settings or {}).items():
        setattr(player, key, value)
    report = player.attempt_cistern()
    final = report["final_state"]
    return {
        "size": size, "seed": seed, "result": report["result"],
        "verified_victory": report["verified_victory"],
        "cause": classify(report),
        "consumers": sum(1 for person in report["setup"]["people"]),
        "nights": report["nights_completed"],
        "decisions": report["decision_count"],
        "outcomes": [day["tactical_outcome"] for day in report["days"]],
        "parts": sorted(final["parts"]),
        "materials": final["materials"],
        "health": final["health"], "morale": final["morale"],
        "blocked": (report["blocked"] or {}).get("action"),
        "hungry_or_thirsty_end": sum(person["hungry"] or person["thirsty"]
                                     for person in final["people"]),
        "expeditions": [{key: stat[key] for key in
                         ("day", "destination", "team", "rounds", "incapacitated",
                          "escorts", "survived_map")}
                        for stat in report["expedition_stats"]],
    }


def _metrics(rows: list[dict]) -> dict:
    expeditions = [item for row in rows for item in row["expeditions"]]
    station = [item for item in expeditions if item["destination"] == "Estação"]
    return {
        "hungry_or_thirsty_end_mean": round(
            sum(row["hungry_or_thirsty_end"] for row in rows) / len(rows), 2),
        "expeditions": len(expeditions),
        "map_emergencies": sum(not item["survived_map"] for item in expeditions),
        "station_expeditions": len(station),
        "station_map_emergencies": sum(not item["survived_map"] for item in station),
        "incapacitations": sum(item["incapacitated"] for item in expeditions),
        "escorts": sum(item["escorts"] for item in expeditions),
        "mean_rounds": round(sum(item["rounds"] for item in expeditions)
                             / max(1, len(expeditions)), 2),
        "mean_station_rounds": round(sum(item["rounds"] for item in station)
                                     / max(1, len(station)), 2),
    }


def _summary(runs: list[dict]) -> dict:
    summary = {}
    for size in SIZES:
        rows = [row for row in runs if row["size"] == size]
        summary[f"H{size}"] = {
            "attempts": len(rows),
            "verified_victories": sum(row["verified_victory"] for row in rows),
            "victory_seeds": [row["seed"] for row in rows if row["verified_victory"]],
            "causes": dict(Counter(row["cause"] for row in rows).most_common()),
            **_metrics(rows),
        }
    return summary


def sweep() -> dict:
    groups = {}
    for name, settings in CONTROLLERS.items():
        runs = [{**run_one(size, seed, settings), "controller": name}
                for size in SIZES for seed in SEEDS]
        groups[name] = {"seeds": [SEEDS.start, SEEDS.stop - 1],
                        "summary": _summary(runs), "runs": runs}
    for seeds, suffix in ((HELDOUT, "heldout"), (VALIDATION, "validation")):
        for name, chooser in (("fixed", lambda size: {}),
                              ("adaptive_previous", previous_settings),
                              ("adaptive_auto", auto_settings)):
            label = f"{name}_{suffix}"
            runs = [{**run_one(size, seed, chooser(size)), "controller": label}
                    for size in SIZES for seed in seeds]
            groups[label] = {"seeds": [seeds.start, seeds.stop - 1],
                             "summary": _summary(runs), "runs": runs}
    return {"schema": 2, "controller": "CampaignPlayer02", "groups": groups}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = sweep()
    if args.write:
        ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    elif ARTIFACT.exists():
        stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("Varredura diverge do artefato registrado")
    table = {name: {size: data["verified_victories"]
                    for size, data in group["summary"].items()}
             for name, group in result["groups"].items()}
    print(json.dumps(table, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
