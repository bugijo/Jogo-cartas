"""Ciclo de balanceamento do acampamento regional (F, G, C2, D).

Uso: python edicao-integral/experiments/camp_economy.py [--seeds 1-30] [--jobs 6]
     [--configs B,BF,...] [--forage-regrow 4] [--market-renewal]

F (prioridade de comida no depósito) é regra aprovada; G (ração-ponte), C2
(coleta) e D (Horta regional com Sementes e sucata) são protótipos do motor,
ligados aqui por `World.enable_regional_prototypes` logo após a migração.
O controlador é o estratégico com risco 'short' (B do ciclo anterior) mais as
opções do acampamento. A regra de fome não muda. Metas em `ECONOMY_TARGETS.md`.
Nenhum artefato é gravado; 91–120 continuam reservadas.
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

import regional_campaign_player as rcp  # noqa: E402
import simulate_regional_campaign as regional  # noqa: E402
from experiments import food_economy  # noqa: E402

# Opções do controlador por configuração; os protótipos do motor seguem delas.
CONFIGS = {
    "B": (),
    "BF": ("priority",),
    "BG": ("bridge",),
    "BC2": ("forage",),
    "BD": ("garden",),
    "BFG": ("priority", "bridge"),
    "BFC2": ("priority", "forage"),
    "BFD": ("priority", "garden"),
    "BFGC2": ("priority", "bridge", "forage"),
    "BFGD": ("priority", "bridge", "garden"),
    "BFC2D": ("priority", "forage", "garden"),
    "ALL": ("priority", "bridge", "forage", "garden"),
    "ALL+BUILD": ("priority", "bridge", "forage", "garden", "build"),
}
SALVAGE_KEY = "EXP-SALVAGE"  # estado experimental em site_states (sobrevive ao save)


def apply_salvage(pool: int) -> None:
    """Fonte experimental W2: desmonte no entorno (madeira), só em memória.

    Um trabalho do amanhecer (herói ou adulto apto, sem outra tarefa) rende
    1 madeira de uma reserva finita de `pool` por abrigo, sem reposição. Só
    quando a próxima obra precisa de madeira. Não é regra: mede o efeito de
    existir alguma madeira legal.
    """
    import system

    def assign(world, person):
        site = world.site_states.setdefault(SALVAGE_KEY, {"pool": pool, "workers": []})
        if len(site["workers"]) >= site["pool"]:
            raise ValueError("entorno sem madeira")
        world._require_dawn_camp_worker(person)
        site["workers"].append(person)
        if person in world.heroes:
            world.worked_today.append(person)
    system.World.experimental_salvage = assign
    require = (system.World.__dict__.get("_base_require_w")
               or system.World._require_dawn_camp_worker)
    system.World._base_require_w = require

    def require_free(world, person):
        if person in world.site_states.get(SALVAGE_KEY, {}).get("workers", []):
            raise ValueError("Trabalhador já ocupado hoje")
        return require(world, person)
    system.World._require_dawn_camp_worker = require_free
    end = system.World.__dict__.get("_base_end_day_w") or system.World._end_day
    system.World._base_end_day_w = end

    def end_day(self, meal_plan):
        site = self.site_states.get(SALVAGE_KEY)
        if site and site["workers"]:
            got = self.deposit("wood", len(site["workers"]))
            site["pool"] -= len(site["workers"])
            for worker in site["workers"]:
                if worker not in self.worked_today:
                    self.worked_today.append(worker)
            site["workers"] = []
            self.log.append({"day": self.day, "action": "experimental_salvage", "wood": got})
        return end(self, meal_plan)
    system.World._end_day = end_day
PROTOTYPE = {"bridge": "bridge", "forage": "forage", "garden": "garden_build"}


def _player(options, forage_max, forage_regrow, forage_frac=None):
    class Player(rcp.CampRegionalPlayer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, risk="short", options=options, **kwargs)

        def camp_work(self, world, kind, team):
            # Desmonte antes da coleta: investir na obra contra a comida de hoje.
            done = {}
            if SALVAGE_POOL and "build" in self.options:
                from system import STRUCTURES
                target = next((k for k in self.BUILD_ORDER if k not in world.structures
                               and k not in world.projects), None)
                need = (STRUCTURES[target]["cost"].get("wood", 0) - world.stock["wood"]
                        if target and not world.projects else 0)
                for person in self._free_people(world, team):
                    if need <= 0:
                        break
                    try:
                        world.experimental_salvage(person)
                    except ValueError:
                        continue
                    need -= 1
                    done.setdefault("salvage", []).append(person)
            done.update(super().camp_work(world, kind, team) or {})
            return done or None

        def run(self, campaign, days, save_dir=None):
            protos = [PROTOTYPE[o] for o in self.options if o in PROTOTYPE]
            if forage_frac is not None:
                consumers = len(campaign.world.meal_people())
                regrow = math.ceil(consumers * forage_frac)
            else:
                regrow = forage_regrow
            if protos and campaign.world.regional_camp is None:
                campaign.world.enable_regional_prototypes(
                    *protos, forage_max=forage_max, forage_regrow=regrow)
            LAST[:] = [self]
            result = super().run(campaign, days, save_dir)
            WORLD[:] = [result.world]
            return result
    return Player


SALVAGE_POOL = 0
LAST: list = []
WORLD: list = []


def _one(job):
    name, size, seed, forage_max, forage_regrow, renewal, forage_frac, salvage = job
    global SALVAGE_POOL
    SALVAGE_POOL = salvage
    if salvage:
        apply_salvage(salvage)
    if renewal:
        food_economy.apply_market_renewal()
    LAST.clear()
    WORLD.clear()
    row = regional.run_one(size, seed, garden=True,
                           player_cls=_player(CONFIGS[name], forage_max, forage_regrow,
                                              forage_frac))
    if row is None:
        return None
    if LAST:
        days = LAST[0].days
        nights = [d["night"] for d in days if d.get("night")]
        row["missing_food"] = sum(n["missing"]["food"] for n in nights)
        row["short_nights"] = sum(n["missing"]["food"] > 0 for n in nights)
        row["food_only_days"] = sum(d.get("plan") == "supply" for d in days)
    log = WORLD[0].log if WORLD else []
    row["forage_food"] = sum(r["forage"]["stored"] for r in log if "forage" in r)
    row["discarded_water"] = sum(r["amount"] for r in log
                                 if r.get("action") == "storage_discard")
    row["not_stored_food"] = sum(r["left_behind"].get("food", 0) for r in log
                                 if "left_behind" in r)
    row["bridge_food"] = sum(r["stored"] for r in log if r.get("action") == "bridge_ration")
    row["garden_built"] = any(r.get("action") == "regional_garden_done" for r in log)
    row["garden_built_day"] = next((r["day"] for r in log
                                    if r.get("action") == "regional_garden_done"), None)
    row["structures"] = sorted(WORLD[0].structures) if WORLD else []
    row["scrap_trips"] = row.get("plans", {}).get("scrap", 0)
    return row


def measure(name, seeds, jobs, forage_max=None, forage_regrow=None, renewal=False,
            forage_frac=None, salvage=0):
    work = [(name, size, seed, forage_max, forage_regrow, renewal, forage_frac, salvage)
            for size in regional.SIZES for seed in seeds]
    with Pool(jobs) as pool:
        rows = [r for r in pool.map(_one, work, chunksize=2) if r is not None]
    result = food_economy.summarize(1.0, 4, seeds, rows)
    migrated = [r for r in rows if r["outcome"] != "migration_refused"]
    result.update(
        config=name, forage_max=forage_max, forage_regrow=forage_regrow,
        forage_frac=forage_frac, salvage=salvage,
        structures=dict(sum((Counter(r["structures"]) for r in migrated), Counter())),
        structures_per_campaign=round(sum(len(r["structures"]) for r in migrated)
                                      / max(1, len(migrated)), 2),
        renewal=renewal,
        forage_food=sum(r["forage_food"] for r in migrated),
        bridge_food=sum(r["bridge_food"] for r in migrated),
        discarded_water=sum(r["discarded_water"] for r in migrated),
        food_left_behind=sum(r["not_stored_food"] for r in migrated),
        gardens_built=sum(r["garden_built"] for r in migrated),
        garden_built_days=sorted(r["garden_built_day"] for r in migrated
                                 if r["garden_built_day"] is not None),
        seeds_carried=sum(r["scrap_trips"] > 0 or r["garden_built"]
                          for r in migrated),
        food_only_day_share=round(
            sum(r["food_only_days"] for r in migrated)
            / max(1, sum(r["days_played"] for r in migrated)), 3),
        defeats=dict(Counter(r["outcome"] for r in migrated)))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="1-30")
    parser.add_argument("--configs", default=",".join(CONFIGS))
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--forage-max", type=int)
    parser.add_argument("--forage-regrow", type=int)
    parser.add_argument("--forage-frac", type=float,
                        help="reposição do entorno = ceil(consumidores × fração)")
    parser.add_argument("--salvage", type=int, default=0,
                        help="W2 experimental: reserva de madeira do entorno")
    parser.add_argument("--market-renewal", action="store_true")
    args = parser.parse_args()
    start, stop = map(int, args.seeds.split("-"))
    if start <= 120 and stop >= 91:
        raise SystemExit("Sementes 91–120 reservadas para a validação cega final")
    for name in args.configs.split(","):
        result = measure(name, range(start, stop + 1), args.jobs,
                         args.forage_max, args.forage_regrow, args.market_renewal,
                         args.forage_frac, args.salvage)
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
