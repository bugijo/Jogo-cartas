"""Replay contínuo até o primeiro bloqueio logístico após a Cisterna.

O replay usa somente as ações públicas existentes e não declara campanha
completa: a seed 22 vence a Cisterna, pesquisa recursos, recruta Célia pela
operação atualmente definida no motor, obtém pistas pelo trabalho de pesquisa,
decifra o rádio, recupera o cartão e combustível regional, e para no Posto/van.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

from integrated_campaign import IntegratedCampaign
from tactics import TacticalGame
from verify_campaign_player02 import execute as execute_cistern

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "replays" / "cistern_to_transmission_seed22_blocked.json"


def _move_actor(tactical: TacticalGame, hero: str, destination: int) -> list[int]:
    """Choose a shortest currently-open path using public map state."""
    path = tactical.path_to(hero, destination)
    if not path:
        raise AssertionError(f"Sem caminho aberto para {hero}: {destination}")
    for zone in path[1:]:
        if tactical.world.heroes[hero]["actions"] < 1:
            tactical.activate()
        tactical.move(hero, zone)
    return path


def _search_at_map(tactical: TacticalGame, count: int) -> list[dict]:
    """Spend one actor PA per search in a printed search zone."""
    found = []
    for _ in range(count):
        candidates = sorted(tactical.snapshot()["heroes"])
        choices = []
        for hero in candidates:
            for zone in tactical.snapshot()["search_zones"]:
                path = tactical.path_to(hero, zone)
                if path:
                    choices.append((len(path), hero, zone))
        if not choices:
            raise AssertionError("Nenhum herói alcança área de busca")
        _, hero, zone = min(choices)
        _move_actor(tactical, hero, zone)
        if tactical.world.heroes[hero]["actions"] < 1:
            tactical.activate()
        found.append(tactical.search(hero))
    return found


def _clear_exit(tactical: TacticalGame) -> dict[str, list[int]]:
    paths = {}
    for hero in sorted(tactical.snapshot()["heroes"]):
        paths[hero] = _move_actor(tactical, hero, tactical.exit_zone)
    tactical.finish()
    return paths


def execute(seed: int = 22) -> dict:
    player, cistern_report = execute_cistern(seed)
    game = player.game
    migration = game.transition_to_last_transmission()
    if not game.world or game.phase != "last_transmission" or not game.world.cistern_verified:
        raise AssertionError("A migração não ativou o mundo regional")

    world = game.world
    team = list(world.heroes)
    actions = []

    # Collect enough food/water to recruit the available researcher and feed
    # the enlarged shelter through the two clue-producing daily phases.
    market = "continuous-seed22-market"
    world.open_expedition(market, team, "EXP-LOC-02")
    actions.append({"action": "open_expedition", "destination": "EXP-LOC-02"})
    market_arrival = world.advance_expedition(market)
    actions.append({"action": "advance_expedition", "result": market_arrival})
    market_map = TacticalGame.start(world, market, "market_intro")
    market_searches = _search_at_map(market_map, 4)
    market_exit = _clear_exit(market_map)
    world.begin_return(market)
    actions.append({"action": "begin_return", "expedition": market})
    market_return = [world.advance_expedition(market)]
    actions.extend({"action": "search", "destination": "EXP-LOC-02", "result": found}
                   for found in market_searches)
    actions.append({"action": "move_to_exit", "paths": market_exit})
    actions.extend({"action": "advance_expedition", "result": result}
                   for result in market_return)
    if market_arrival != "arrived" or market_return != ["returned"]:
        raise AssertionError("Viagem ao Mercado não completou ida e volta")

    recruited = world.recruit("EXP-NPC-02")
    if not recruited:
        raise AssertionError("Célia não pôde ser recrutada com espaço e sustento")
    world.assign("EXP-NPC-02", "teaching")
    actions.extend([{"action": "recruit", "npc": "EXP-NPC-02", "result": recruited},
                    {"action": "assign", "npc": "EXP-NPC-02", "job": "teaching"}])
    daily = []
    daily_clues = []
    for _ in range(2):
        before_clues = world.clues
        daily.append(world.end_day())
        daily_clues.append(world.clues - before_clues)
    actions.extend({"action": "advance_day", "result": result} for result in daily)
    if [result["missing"] for result in daily] != [
            {"food": 0, "water": 0}, {"food": 0, "water": 0}]:
        raise AssertionError("Rota de pistas não sustenta o abrigo nos dois dias")
    if world.clues != 2:
        raise AssertionError(f"Pesquisa não gerou duas pistas: {world.clues}")
    game.decode_radio()
    if not world.flags.get("radio_code") or world.clues != 0:
        raise AssertionError("Decodificação de rádio não consumiu as duas pistas")
    actions.append({"action": "decode_radio", "result": "radio_code", "clues_spent": 2})

    station = "continuous-seed22-station"
    world.open_expedition(station, team, "EXP-LOC-05")
    actions.append({"action": "open_expedition", "destination": "EXP-LOC-05"})
    station_travel = [world.advance_expedition(station) for _ in range(3)]
    actions.extend({"action": "advance_expedition", "result": result}
                   for result in station_travel)
    station_map = TacticalGame.start(world, station, "station_02")
    station_searches = _search_at_map(station_map, 1)
    station_search = station_searches[0]
    game.recover_access_card(station)
    station_exit = _clear_exit(station_map)
    world.begin_return(station)
    station_return = [world.advance_expedition(station) for _ in range(3)]
    actions.extend([
        {"action": "search", "destination": "EXP-LOC-05", "result": station_search},
        {"action": "recover_access_card", "result": "access_card"},
        {"action": "move_to_exit", "paths": station_exit},
        {"action": "begin_return", "expedition": station},
        *[{"action": "advance_expedition", "result": result}
          for result in station_return],
    ])
    if station_travel != ["travel", "travel", "arrived"] or station_return != [
            "travel", "travel", "returned"]:
        raise AssertionError("Expedição da Estação não completou ida e volta")

    workshop = "continuous-seed22-workshop"
    world.open_expedition(workshop, team, "EXP-LOC-03")
    actions.append({"action": "open_expedition", "destination": "EXP-LOC-03"})
    workshop_travel = [world.advance_expedition(workshop) for _ in range(2)]
    workshop_map = TacticalGame.start(world, workshop, "workshop_02")
    workshop_searches = _search_at_map(workshop_map, 3)
    workshop_exit = _clear_exit(workshop_map)
    world.begin_return(workshop)
    workshop_return = [world.advance_expedition(workshop) for _ in range(2)]
    actions.extend([
        *[{"action": "advance_expedition", "result": result}
          for result in workshop_travel],
        *[{"action": "search", "destination": "EXP-LOC-03", "result": found}
          for found in workshop_searches],
        {"action": "move_to_exit", "paths": workshop_exit},
        {"action": "begin_return", "expedition": workshop},
        *[{"action": "advance_expedition", "result": result}
          for result in workshop_return],
    ])
    if workshop_travel != ["travel", "arrived"] or workshop_return != [
            "travel", "returned"]:
        raise AssertionError("Expedição da Oficina não completou ida e volta")

    # The verified Cistern replay left the guaranteed battery at Workshop O1.
    # Recover it through the active tactical map and carry it back explicitly.
    battery_trip = "continuous-seed22-battery"
    world.open_expedition(battery_trip, team, "EXP-LOC-03")
    battery_travel = [world.advance_expedition(battery_trip) for _ in range(2)]
    workshop_map = TacticalGame.start(world, battery_trip, "workshop_02")
    hero = team[0]
    crowbar = next(iter(world.gear[hero]))
    workshop_map.move(hero, 2)
    workshop_map.move(hero, 3)
    workshop_map.breach(hero, 3, 7, crowbar)
    workshop_map.activate()
    workshop_map.breach(hero, 3, 7, crowbar)
    workshop_map.move(hero, 7)
    workshop_map.pickup_unique_item(hero, "battery")
    workshop_map.activate()
    workshop_map.move(hero, 3)
    workshop_map.move(hero, 2)
    workshop_map.activate()
    workshop_map.move(hero, 1)
    workshop_map.finish()
    world.begin_return(battery_trip)
    battery_return = [world.advance_expedition(battery_trip) for _ in range(2)]
    if (battery_travel != ["travel", "arrived"]
            or battery_return != ["travel", "returned"]
            or "battery" not in world.special_stock):
        raise AssertionError("A Bateria canônica não foi transportada da Oficina")
    actions.extend([
        {"action": "open_expedition", "destination": "EXP-LOC-03"},
        *[{"action": "advance_expedition", "result": result}
          for result in battery_travel],
        {"action": "move", "hero": hero, "path": [1, 2, 3]},
        {"action": "breach", "hero": hero, "edge": [3, 7], "uses": 2},
        {"action": "move", "hero": hero, "path": [3, 7]},
        {"action": "pickup_unique_item", "item": "battery", "zone": 7, "pa": 1},
        {"action": "move", "hero": hero, "path": [7, 3, 2, 1]},
        {"action": "return_expedition", "delivered": "battery",
         "travel": battery_return},
    ])

    # Open the canonical Posto destination and collect its eight physical fuel
    # cards, each by its own 1-PA O1 action. No fuel is injected into stock.
    posto = "continuous-seed22-posto"
    world.open_expedition(posto, team, "EXP-LOC-07", special_items=["battery"])
    posto_travel = [world.advance_expedition(posto) for _ in range(2)]
    posto_map = TacticalGame.start(world, posto, "gas_station_02")
    if posto_travel != ["travel", "arrived"]:
        raise AssertionError("Viagem ao Posto não completou")
    path_to_fuel = posto_map.path_to(hero, 7)
    if not path_to_fuel:
        raise AssertionError("O1 do Posto está desconectado")
    for zone in path_to_fuel[1:]:
        if world.heroes[hero]["actions"] < 1:
            posto_map.activate()
        posto_map.move(hero, zone)
    fuel_cards = []
    for lot in range(1, 9):
        if world.heroes[hero]["actions"] < 1:
            posto_map.activate()
        fuel_cards.append(posto_map.pickup_fuel_card(hero, lot))
    if posto_map.state["van_state"] == "abandoned":
        if world.heroes[hero]["actions"] < 1:
            posto_map.activate()
        posto_map.inspect_van(hero)
    repair_attempts = []
    for candidate in team:
        if posto_map.state["van_state"] == "operational":
            break
        candidate_path = posto_map.path_to(candidate, 7)
        if not candidate_path:
            raise AssertionError(f"Reparador {candidate} não alcança O1")
        for zone in candidate_path[1:]:
            if world.heroes[candidate]["actions"] < 1:
                posto_map.activate()
            posto_map.move(candidate, zone)
        if world.heroes[candidate]["actions"] < 2:
            posto_map.activate()
        repair_attempts.append(posto_map.repair_van(candidate))
    van_recovered = posto_map.state["van_state"] == "operational"
    exit_paths = {}
    for candidate in team:
        path_to_exit = posto_map.path_to(candidate, posto_map.exit_zone)
        if not path_to_exit:
            raise AssertionError(f"Saída do Posto não alcançável por {candidate}")
        exit_paths[candidate] = path_to_exit
        for zone in path_to_exit[1:]:
            if world.heroes[candidate]["actions"] < 1:
                posto_map.activate()
            posto_map.move(candidate, zone)
    posto_map.finish()
    world.begin_return(posto, vehicle_id="EXP-VEI-02" if van_recovered else None)
    posto_return = [world.advance_expedition(posto) for _ in range(2)]
    if posto_return != ["travel", "returned"]:
        raise AssertionError("Retorno do Posto não completou")
    actions.extend([
        {"action": "open_expedition", "destination": "EXP-LOC-07",
         "special_cargo": ["battery"]},
        *[{"action": "advance_expedition", "result": result}
          for result in posto_travel],
        {"action": "move", "hero": hero, "path": path_to_fuel},
        *[{"action": "pickup_fuel_card", **receipt} for receipt in fuel_cards],
        {"action": "inspect_van", "zone": 7, "pa": 1},
        *[{"action": "repair_van", **receipt} for receipt in repair_attempts],
        {"action": "move_to_exit", "paths": exit_paths},
        {"action": "return_by_van" if van_recovered else "return_on_foot",
         "fuel_spent_from_cargo": 4 if van_recovered else 0,
         "result": posto_return},
    ])

    vehicle_error = None
    before_military_gate = asdict(world)
    try:
        game.authorize_installation("continuous-seed22-military", team, "EXP-VEI-02")
    except ValueError as exc:
        vehicle_error = str(exc)
    if vehicle_error != "Combustível insuficiente para ida e volta" or world.flags.get("military_access"):
        raise AssertionError(f"O custo canônico do trecho não foi aplicado: {vehicle_error}")
    if asdict(world) != before_military_gate:
        raise AssertionError("Gate militar com combustível insuficiente deixou mutação parcial")
    actions.append({"action": "authorize_installation", "blocked": vehicle_error})
    if world.final_defense is not None or "transmitter" in world.special_stock:
        raise AssertionError("A defesa/transmissor apareceu sem cumprir os portões")

    snapshot = {
        "cistern": {
            "status": game.cistern.result,
            "days": game.cistern.day,
            "nights": len(cistern_report["days"]),
            "expeditions": sum(day["destination"] is not None
                                for day in cistern_report["days"]),
            "decisions": cistern_report["decision_count"],
            "objectives": list(game.delivered_objectives),
        },
        "migration": migration,
        "last_transmission": {
            "phase": game.phase,
            "heroes": team,
            "clues": world.clues,
            "access_card": world.flags.get("access_card", False),
            "radio_code": world.flags.get("radio_code", False),
            "recruited_researcher": "EXP-NPC-02" in world.npcs,
            "daily_clues": daily_clues,
            "daily_missing": [result["missing"] for result in daily],
            "market_searches": market_searches,
            "station_search": station_search,
            "workshop_searches": workshop_searches,
            "fuel": world.stock["fuel"],
            "vehicle": dict(world.vehicles),
            "battery_delivered_to_posto": "battery" not in world.special_stock,
            "fuel_cards_taken": len(fuel_cards),
            "van_recovered": van_recovered,
            "van_repair_attempts": repair_attempts,
            "posto_return": "van" if van_recovered else "foot",
            "military_fuel_required": 12,
            "fuel_shortfall": max(0, 12 - world.stock["fuel"]),
            "day": world.day,
            "campaign_actions": actions,
            "blocking_requirement": "combustível insuficiente para ida e volta à instalação militar",
            "post_location_error": None,
            "military_vehicle_error": vehicle_error,
        },
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "continuous.json"
        game.save(path)
        restored = IntegratedCampaign.load(path)
        if restored.world is None or restored.world.cistern_record != world.cistern_record:
            raise AssertionError("A proveniência de migração divergiu após save/load")
        if asdict(restored.world) != asdict(world):
            raise AssertionError("Estado regional divergiu após save/load")
        if restored.transition_to_last_transmission() != migration:
            raise AssertionError("A retomada duplicou a transição")
    return snapshot


def write_artifact(path: Path = ARTIFACT) -> None:
    result = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": 1, "status": "blocked_at_military_fuel",
                                "replay": result}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def verify_artifact(path: Path = ARTIFACT) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or payload.get("status") != "blocked_at_military_fuel":
        raise AssertionError("Artefato de campanha contínua inválido")
    actual = execute()
    if actual != payload["replay"]:
        raise AssertionError("Replay contínuo difere do artefato salvo")
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--path", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    if args.write:
        write_artifact(args.path)
    result = verify_artifact(args.path)
    print(json.dumps({"status": "blocked_at_military_fuel",
                      "cistern_days": result["cistern"]["days"],
                      "second_arc_trace_entries": len(result["last_transmission"]["campaign_actions"]),
                      "access_card": result["last_transmission"]["access_card"],
                      "clues": result["last_transmission"]["clues"],
                      "blocker": result["last_transmission"]["blocking_requirement"]},
                     ensure_ascii=False))
