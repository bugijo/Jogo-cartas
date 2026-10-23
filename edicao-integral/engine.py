"""Núcleo experimental determinístico; não substitui as regras 0.2."""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data/core.json").read_text(encoding="utf-8"))


@dataclass
class Hero:
    id: str
    health: int = 3
    xp: int = 0
    combat_xp_this_expedition: int = 0
    actions: int = 3

    def award_xp(self, amount: int, combat: bool = False) -> int:
        if amount < 0:
            raise ValueError("XP negativo")
        if combat:
            amount = min(amount, DATA["combat_xp_cap_per_expedition"] - self.combat_xp_this_expedition)
        gained = min(amount, DATA["xp_cap"] - self.xp)
        self.xp += gained
        if combat:
            self.combat_xp_this_expedition += gained
        return gained

    @property
    def unlocks(self) -> list[int]:
        return [n for n in DATA["skill_unlock_xp"] if self.xp >= n]


@dataclass
class Camp:
    residents: int
    beds: int
    food: int
    water: int
    materials: int = 0
    garden_age: int | None = None
    camp_xp: int = 0
    day: int = 0

    def __post_init__(self):
        if min(self.residents, self.beds, self.food, self.water, self.materials, self.camp_xp, self.day) < 0:
            raise ValueError("Contador negativo")
        if self.residents > self.beds:
            raise ValueError("Moradores excedem alojamento")

    def recruit(self, count: int = 1) -> bool:
        if count <= 0:
            raise ValueError("Quantidade inválida")
        if self.residents + count > self.beds:
            return False
        self.residents += count
        return True

    def build_garden(self, material_cost: int = 2) -> bool:
        if self.garden_age is not None or self.materials < material_cost:
            return False
        self.materials -= material_cost
        self.garden_age = 0
        return True

    def end_day(self) -> dict:
        """Produção antes de consumo, com carência de quatro dias para a horta.

        Colheita de 1 é hipótese de motor, ainda não regra oficial.
        Déficits são registrados; recursos não ficam negativos.
        """
        self.day += 1
        produced = 0
        if self.garden_age is not None:
            self.garden_age += 1
            if self.garden_age >= DATA["garden_first_harvest_days"]:
                produced = 1
                self.food += produced
        need = self.residents
        missing_food = max(0, need - self.food)
        missing_water = max(0, need - self.water)
        self.food = max(0, self.food - need)
        self.water = max(0, self.water - need)
        return {"day": self.day, "produced_food": produced,
                "missing_food": missing_food, "missing_water": missing_water,
                "food": self.food, "water": self.water}


def attack(rng: random.Random, dice: int, hit_on: int, damage: int,
           target_health: int, armor: int = 0) -> dict:
    if not 1 <= hit_on <= 6 or min(dice, damage, target_health, armor) < 0:
        raise ValueError("Parâmetro de combate inválido")
    rolls = [rng.randint(1, 6) for _ in range(dice)]
    hits = sum(n >= hit_on for n in rolls)
    raw = hits * damage
    absorbed = min(raw, armor)
    return {"rolls": rolls, "hits": hits, "damage": raw - absorbed,
            "armor_lost": absorbed, "target_health": max(0, target_health - raw + absorbed)}


def infection(rng: random.Random) -> tuple[int, bool]:
    roll = rng.randint(1, DATA["infection_die_sides"])
    return roll, roll in DATA["infection_results"]


def save(path: Path, heroes: list[Hero], camp: Camp, seed: int) -> None:
    payload = {"schema": 1, "seed": seed, "heroes": [asdict(h) for h in heroes], "camp": asdict(camp)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> tuple[list[Hero], Camp, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["schema"] != 1:
        raise ValueError("Esquema de salvamento desconhecido")
    allowed = {h["id"] for h in DATA["heroes"]}
    heroes = [Hero(**h) for h in data["heroes"]]
    if len({h.id for h in heroes}) != len(heroes) or any(h.id not in allowed for h in heroes):
        raise ValueError("Heróis inválidos ou duplicados")
    camp = Camp(**data["camp"])
    return heroes, camp, data["seed"]
