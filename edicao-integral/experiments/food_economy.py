"""Experimento isolado da economia de comida regional (Fase 6).

Uso: python edicao-integral/experiments/food_economy.py [--seeds 1-30] [--grid]
     [--food 1.5] [--garden-output 6] [--jobs 4] [--controller strategic]
     [--market-renewal] [--forage] [--regional-garden] [--delivery-discard]
     [--bridge]

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


def apply_market_renewal() -> None:
    """Referência experimental: Mercado repõe 1 busca por noite (renovação natural)."""
    system.LOCATIONS[rcp.MARKET]["renewal"] = "natural"


def apply_forage(per_worker: int = 1) -> None:
    """Fonte C2: coleta no entorno ligada a trabalhadores, proporcional e limitada.

    Antes da refeição, cada adulto civil apto e cada herói no abrigo que não saiu
    nem trabalhou coleta `per_worker` comida, no máximo ceil(consumidores / 2) no
    total, pelo depósito. Quem coleta conta como trabalho (sem recuperação §25).
    """
    end = system.World.__dict__.get("_base_end_day") or system.World._end_day
    system.World._base_end_day = end

    def end_day(self, meal_plan):
        cap = -(-len(self.meal_people()) // 2)
        workers = [p["id"] for p in self.continuity_people if p["kind"] == "adult"
                   and p.get("wounds", 0) < 3 and p.get("fatigue", 0) < 3
                   and not p.get("hungry") and not p.get("thirsty")
                   and p["id"] not in self.worked_today]
        workers += [h for h, s in sorted(self.heroes.items()) if s["location"] == "camp"
                    and s["health"] > 0 and s.get("fatigue", 0) < 3
                    and not s.get("hungry") and not s.get("thirsty")
                    and h not in self.worked_today and h not in self.departed_today]
        workers = workers[:cap // per_worker if per_worker else 0]
        if (self.continuity_garden or {}).get("worker") in workers:
            workers.remove(self.continuity_garden["worker"])
        self.deposit("food", per_worker * len(workers))
        self.worked_today.extend(workers)
        FORAGE.append(per_worker * len(workers))
        return end(self, meal_plan)
    system.World._end_day = end_day


FORAGE: list[int] = []


def apply_regional_garden(ready_after: int = 3) -> None:
    """Frente D, teto otimista: Sementes guardadas na Cisterna viram Horta §61 regional.

    Só quando a Cisterna termina com Sementes e sem Horta (acolhimento legal de
    ZC-MOR-0006). A Horta fica ativa `ready_after` dias depois da migração, sem
    cobrar a ida à Oficina (sucata no lugar de Materiais) nem os 2 trabalhos:
    mede o máximo que essa rota poderia dar, não a regra.
    """
    import integrated_campaign
    cls = integrated_campaign.IntegratedCampaign
    migrate = cls.__dict__.get("_base_migrate") or cls.transition_to_last_transmission
    cls._base_migrate = migrate

    def transition(self, *args, **kwargs):
        result = migrate(self, *args, **kwargs)
        world = self.world
        if self.cistern.seeds and world.continuity_garden is None:
            world.continuity_garden = {"source": "cistern02", "active": False,
                                       "output": 4, "worker": None}
            PENDING_GARDEN[id(world)] = world.day + ready_after
        return result
    cls.transition_to_last_transmission = transition
    end = system.World.__dict__.get("_base_end_day_d") or system.World._end_day
    system.World._base_end_day_d = end

    def end_day(self, meal_plan):
        result = end(self, meal_plan)
        ready = PENDING_GARDEN.get(id(self))
        if ready is not None and self.day >= ready and self.continuity_garden:
            self.continuity_garden["active"] = True
            PENDING_GARDEN.pop(id(self))
        return result
    system.World._end_day = end_day


PENDING_GARDEN: dict[int, int] = {}


def apply_delivery_discard() -> None:
    """Hipótese F: descarte voluntário de água também quando chega comida.

    Mesmo princípio aprovado para a colheita: só o espaço que falta e só a água
    acima do consumo previsto da noite. Vale para carga entregue e coleta.
    """
    deposit = system.World.__dict__.get("_base_deposit") or system.World.deposit
    system.World._base_deposit = deposit

    def variant(self, resource, amount):
        if resource == "food" and amount > 0:
            free = self.storage - sum(self.stock.values())
            spare = max(0, self.stock["water"] - len(self.meal_people()))
            self.stock["water"] -= min(spare, max(0, amount - free))
        return deposit(self, resource, amount)
    system.World.deposit = variant


def apply_bridge_ration() -> None:
    """Hipótese G: ração-ponte única na chegada (leitura de CAMPAIGN l.32).

    O texto da Evacuação dá uma vez 1 porção de comida e água por consumidor.
    Aqui aplicado à migração, pelo depósito com o descarte da hipótese F.
    """
    import integrated_campaign
    cls = integrated_campaign.IntegratedCampaign
    migrate = cls.__dict__.get("_base_migrate_g") or cls.transition_to_last_transmission
    cls._base_migrate_g = migrate

    def transition(self, *args, **kwargs):
        result = migrate(self, *args, **kwargs)
        self.world.deposit("food", len(self.world.meal_people()))
        return result
    cls.transition_to_last_transmission = transition


def measure(food: float, garden_output: int, seeds: range, controller: str = "base",
            renewal: bool = False, forage: bool = False,
            regional_garden: bool = False, delivery_discard: bool = False,
            bridge: bool = False) -> dict:
    apply_variant(food, garden_output)
    if delivery_discard or bridge:
        apply_delivery_discard()
    if bridge:
        apply_bridge_ration()
    if regional_garden:
        apply_regional_garden()
    if renewal:
        apply_market_renewal()
    if forage:
        apply_forage()
    player_cls = rcp.RegionalCampaignPlayer
    if controller.startswith("strategic"):
        risk = "short" if controller == "strategic-short" else "covered"

        class player_cls(rcp.StrategicRegionalPlayer):  # noqa: N801
            def __init__(self, *args, **kwargs):
                super().__init__(*args, risk=risk, **kwargs)
    last = []
    base_run = player_cls.run

    def run(self, *args, **kwargs):
        last[:] = [self]
        return base_run(self, *args, **kwargs)
    player_cls.run = run
    rows = []
    for size in regional.SIZES:
        for seed in seeds:
            last.clear()
            FORAGE.clear()
            row = regional.run_one(size, seed, garden=True, player_cls=player_cls)
            if row is None:
                continue
            if last:
                nights = [day["night"] for day in last[0].days if day.get("night")]
                row["missing_food"] = sum(n["missing"]["food"] for n in nights)
                row["short_nights"] = sum(n["missing"]["food"] > 0 for n in nights)
            row["forage_food"] = sum(FORAGE)
            rows.append(row)
    player_cls.run = base_run
    result = summarize(food, garden_output, seeds, rows)
    result.update(controller=controller, renewal=renewal, forage=forage,
                  regional_garden=regional_garden, delivery_discard=delivery_discard,
                  bridge=bridge)
    return result


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
            "day_plans": dict(sum((Counter(r.get("plans", {})) for r in migrated), Counter())),
            "clue_evidence": sum(r["clue_evidence"] for r in migrated),
            "radio_all": sum(r["radio_code"] for r in migrated),
            "forage_food": sum(r.get("forage_food", 0) for r in migrated),
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
    parser.add_argument("--controller", choices=("base", "strategic", "strategic-short"), default="base")
    parser.add_argument("--market-renewal", action="store_true")
    parser.add_argument("--forage", action="store_true")
    parser.add_argument("--regional-garden", action="store_true")
    parser.add_argument("--delivery-discard", action="store_true")
    parser.add_argument("--bridge", action="store_true")
    args = parser.parse_args()
    start, stop = map(int, args.seeds.split("-"))
    seeds = range(start, stop + 1)
    if start <= 120 and stop >= 91:
        raise SystemExit("Sementes 91–120 reservadas para a validação cega final")
    extra = (args.controller, args.market_renewal, args.forage, args.regional_garden,
             args.delivery_discard, args.bridge)
    configs = ([(f, g, seeds, *extra) for f in FOOD_STEPS for g in GARDEN_STEPS] if args.grid
               else [(args.food, args.garden_output, seeds, *extra)])
    with Pool(min(args.jobs, len(configs))) as pool:
        for result in pool.imap(_job, configs):
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
