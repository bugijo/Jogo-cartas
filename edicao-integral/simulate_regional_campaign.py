"""Mede a campanha regional multi-dia a partir de vitórias legais da Cisterna.

Uso: python edicao-integral/simulate_regional_campaign.py [--garden] [--write]
Para cada tamanho H2–H6 e semente 1–30, joga a Cisterna com o adaptativo
publicado (`auto_settings`); só as `verified_victory` migram. Depois liga as
cartas regionais e deixa `RegionalCampaignPlayer` jogar até `MAX_DAYS` dias.
Nada é ajustado aqui: a política regional foi escrita olhando só a seed 22 H2.
Com `--garden`, a Cisterna usa o modo Horta (H1) do controlador e o artefato é
`regional_campaign_garden_sweep.json`; a medição sem Horta não muda. No regional,
a Horta usa o descarte voluntário de água (`--no-discard` mede sem ele).
`--seeds A-B` mede outro intervalo sem gravar artefato (só validação).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from campaign_player02 import CampaignPlayer02
from regional_campaign_player import RegionalCampaignPlayer
from simulate_cistern_sweep import auto_settings

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "regional_campaign_sweep.json"
GARDEN_ARTIFACT = ROOT / "replays" / "regional_campaign_garden_sweep.json"
MAX_DAYS = 15
SIZES = (2, 3, 4, 5, 6)
SEEDS = range(1, 31)


def run_one(size: int, seed: int, garden: bool = False,
            discard_water: bool = True,
            player_cls=RegionalCampaignPlayer) -> dict | None:
    player = CampaignPlayer02.new_hn(seed, size)
    for key, value in auto_settings(size).items():
        setattr(player, key, value)
    player.garden = garden
    if not player.attempt_cistern()["verified_victory"]:
        return None
    campaign = player.game
    try:
        campaign.transition_to_last_transmission()
    except ValueError as exc:  # recusa da migração: registrar, não contornar
        return {"size": size, "seed": seed, "outcome": "migration_refused",
                "reason": str(exc), "days_played": 0, "clue_evidence": 0,
                "radio_code": False, "access_card": False, "blockers": []}
    campaign.world.regional_travel_cards = True
    campaign.world.regional_filter_production = True
    regional = player_cls(discard_water=garden and discard_water)
    campaign = regional.run(campaign, MAX_DAYS)
    world = campaign.world
    plans = Counter(day.get("plan") for day in regional.days if "plan" in day)
    statuses = Counter(day["expedition"]["status"] for day in regional.days
                       if day.get("expedition"))
    row = {
        "size": size, "seed": seed,
        "consumers": len(world.meal_people()) if not world.partial_defeat else None,
        "days_played": sum(1 for day in regional.days if "plan" in day),
        "outcome": "partial_defeat" if world.partial_defeat else
                   ("blocked_rule" if any(d.get("result") == "blocked_rule"
                                          for d in regional.days) else "running"),
        "clue_evidence": sum(row.get("action") == "collect_regional_evidence"
                             for row in world.log),
        "radio_code": bool(world.flags.get("radio_code")),
        "access_card": bool(world.flags.get("access_card")),
        "plans": dict(plans), "expedition_status": dict(statuses),
        "blockers": [row["code"] for row in regional.blockers],
    }
    if garden:
        row["garden_migrated"] = world.continuity_garden is not None
        row["garden_food"] = sum(day["night"]["garden_food"]["produced"]
                                 for day in regional.days
                                 if "garden_food" in day.get("night", {}))
        row["water_discarded"] = sum(day["night"]["garden_food"].get("water_discarded", 0)
                                     for day in regional.days
                                     if "garden_food" in day.get("night", {}))
        row["survived"] = (not world.partial_defeat
                           and row["days_played"] == MAX_DAYS)
    return row


def sweep(garden: bool = False, seeds=SEEDS, discard_water: bool = True) -> dict:
    rows = [row for size in SIZES for seed in seeds
            if (row := run_one(size, seed, garden, discard_water)) is not None]
    summary = {}
    for size in SIZES:
        group = [row for row in rows if row["size"] == size]
        migrated = [row for row in group if row["outcome"] != "migration_refused"]
        summary[f"H{size}"] = {
            "cistern_victories": len(group),
            "radio_code": sum(row["radio_code"] for row in group),
            "access_card": sum(row["access_card"] for row in group),
            "clues_ge1": sum(row["clue_evidence"] >= 1 for row in group),
            "partial_defeat": sum(row["outcome"] == "partial_defeat" for row in group),
            "blocked_rule": sum(row["outcome"] == "blocked_rule" for row in group),
            "migration_refused": sum(row["outcome"] == "migration_refused" for row in group),
            "mean_days": (round(sum(row["days_played"] for row in migrated)
                                / len(migrated), 1) if migrated else None),
            "blockers": dict(Counter(code for row in group for code in row["blockers"])),
        }
        if garden:
            summary[f"H{size}"].update(
                garden_migrated=sum(row.get("garden_migrated", False) for row in group),
                survived=sum(row.get("survived", False) for row in group),
                survived_with_garden=sum(row.get("survived", False)
                                         and row.get("garden_migrated", False)
                                         for row in group))
    return {"schema": 1, "max_days": MAX_DAYS, "seeds": [seeds.start, seeds.stop - 1],
            "summary": summary, "runs": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--garden", action="store_true")
    parser.add_argument("--no-discard", action="store_true")
    parser.add_argument("--seeds", help="A-B: validação fora do artefato")
    args = parser.parse_args()
    seeds = SEEDS
    if args.seeds:
        start, stop = map(int, args.seeds.split("-"))
        seeds = range(start, stop + 1)
    result = sweep(args.garden, seeds, not args.no_discard)
    if args.seeds or args.no_discard:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return
    artifact = GARDEN_ARTIFACT if args.garden else ARTIFACT
    if args.write:
        artifact.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
    elif json.loads(artifact.read_text(encoding="utf-8")) != result:
        raise SystemExit("Medição da campanha regional diverge do artefato registrado")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
