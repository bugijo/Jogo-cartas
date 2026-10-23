"""Ensaios do núcleo de combate/economia, sem eventos ou campanha."""
import argparse
import json
import random
from engine import Camp, attack, infection


def run(seed: int, runs: int) -> dict:
    rng = random.Random(seed)
    defeats = 0
    infections = 0
    shortages = 0
    for _ in range(runs):
        camp = Camp(residents=2, beds=8, food=10, water=10, materials=2)
        camp.build_garden()
        for _day in range(5):
            result = attack(rng, 2, 4, 1, 2)
            defeats += result["target_health"] == 0
            infections += infection(rng)[1]
            meal = camp.end_day()
            shortages += bool(meal["missing_food"] or meal["missing_water"])
    return {"seed": seed, "runs": runs, "attack_defeats": defeats,
            "infection_rolls_positive": infections, "shortage_days": shortages,
            "scope": "5 ataques e 5 refeições por ensaio; não é partida nem taxa de vitória"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--runs", type=int, default=1000)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.runs), ensure_ascii=False, indent=2))
