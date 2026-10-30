"""Experimento isolado da economia de comida regional (Fase 6).

Uso: python edicao-integral/experiments/food_economy.py [--seeds 1-30] [--grid]
     [--food 1.5] [--garden-output 6] [--jobs 4]

Nada aqui muda o motor nem os artefatos: as variantes são aplicadas só na
memória deste processo. Comida por busca = arredondamento para cima de metade
(2 × 1,25 = 2,5 → 3; 2 × 1,5 = 3; 2 × 2 = 4). A produção da Horta troca só a
colheita regional (4 → 6 ou 8). A regra de fome não muda. Métricas comparadas
com `ECONOMY_TARGETS.md`.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import system  # noqa: E402
import regional_campaign_player as rcp  # noqa: E402
import simulate_regional_campaign as regional  # noqa: E402

FOOD_STEPS = (1.0, 1.25, 1.5, 2.0)
GARDEN_STEPS = (4, 6, 8)


def scaled(amount: int, factor: float) -> int:
    return math.floor(amount * factor + 0.5)


def apply_variant(food: float, garden_output: int) -> None:
    for location in system.LOCATIONS.values():
        if location["loot"].get("food"):
            base = location.setdefault("_base_food", location["loot"]["food"])
            location["loot"]["food"] = scaled(base, food)
    harvest = system.World.__dict__.get("_base_harvest") or system.World._continuity_garden_harvest
    system.World._base_harvest = harvest

    def variant_harvest(self):
        garden = self.continuity_garden
        if garden is None:
            return harvest(self)
        garden["output"] = garden_output
        try:
            return harvest(self)
        finally:
            garden["output"] = 4  # a validação do motor só conhece a §61
    system.World._continuity_garden_harvest = variant_harvest


def measure(food: float, garden_output: int, seeds: range) -> dict:
    apply_variant(food, garden_output)
    last = []
    base_run = rcp.RegionalCampaignPlayer.run

    def run(self, *args, **kwargs):
        last[:] = [self]
        return base_run(self, *args, **kwargs)
    rcp.RegionalCampaignPlayer.run = run
    rows = []
    for size in regional.SIZES:
        for seed in seeds:
            last.clear()
            row = regional.run_one(size, seed, garden=True)
            if row is None:
                continue
            if last:
                nights = [day["night"] for day in last[0].days if day.get("night")]
                row["missing_food"] = sum(n["missing"]["food"] for n in nights)
                row["short_nights"] = sum(n["missing"]["food"] > 0 for n in nights)
            rows.append(row)
    rcp.RegionalCampaignPlayer.run = base_run
    return summarize(food, garden_output, seeds, rows)


def summarize(food, garden_output, seeds, rows) -> dict:
    migrated = [r for r in rows if r["outcome"] != "migration_refused"]
    survived = [r for r in migrated if r.get("survived")]
    consumer_nights = sum(r["consumers"] * r["days_played"] for r in survived if r["consumers"])
    shortage = (sum(r["missing_food"] for r in survived) / consumer_nights
                if consumer_nights else None)
    by_size = {f"H{s}": [sum(r["size"] == s for r in survived),
                         sum(r["size"] == s for r in migrated)] for s in regional.SIZES}
    t1 = len(survived) / len(migrated) if migrated else 0
    targets = {
        "T1": 0.40 <= t1 <= 0.85,
        "T2": bool(survived) and sum(r["short_nights"] > 0 for r in survived) >= len(survived) / 2,
        "T3": shortage is not None and shortage <= 0.10,
        "T4": all(v[0] > 0 for v in by_size.values()),
        "T5": bool(survived) and sum(r["radio_code"] for r in survived) >= 0.3 * len(survived),
    }
    return {"food": food, "garden_output": garden_output,
            "seeds": [seeds.start, seeds.stop - 1], "victories": len(rows),
            "migrated": len(migrated), "survived": len(survived),
            "survival_rate": round(t1, 3),
            "mean_days": round(sum(r["days_played"] for r in migrated) / len(migrated), 2)
                         if migrated else None,
            "shortage_share": round(shortage, 3) if shortage is not None else None,
            "radio": sum(r["radio_code"] for r in survived),
            "access_card": sum(r["access_card"] for r in survived),
            "garden_migrated": sum(r.get("garden_migrated", False) for r in rows),
            "by_size_survived_of_migrated": by_size,
            "blockers": dict(Counter(c for r in rows for c in r["blockers"])),
            "targets": targets}


def _job(args):
    return measure(*args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="1-30")
    parser.add_argument("--food", type=float, default=1.0)
    parser.add_argument("--garden-output", type=int, default=4)
    parser.add_argument("--grid", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    start, stop = map(int, args.seeds.split("-"))
    seeds = range(start, stop + 1)
    if start <= 120 and stop >= 91:
        raise SystemExit("Sementes 91–120 reservadas para a validação cega final")
    configs = ([(f, g, seeds) for f in FOOD_STEPS for g in GARDEN_STEPS] if args.grid
               else [(args.food, args.garden_output, seeds)])
    with Pool(min(args.jobs, len(configs))) as pool:
        for result in pool.imap(_job, configs):
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
