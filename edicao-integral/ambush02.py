"""Resolução tática isolada da Emboscada de Viagem da Cisterna 0.2."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from collections import deque
from math import ceil

from cistern_tactics02 import ENEMIES, HEROES, WEAPONS
from horde_deck02 import HordeDeck02


EDGES = {tuple(sorted(edge)) for edge in ((1, 2), (1, 5), (2, 6), (5, 6))}
DOOR = (1, 5)


@dataclass
class Ambush02:
    team: list[str]
    clock: int
    positions: dict[str, int]
    enemies: list[dict]
    ap: dict[str, int] = field(default_factory=dict)
    round_no: int = 0
    completed_rounds: int = 0
    door_open: bool = False
    wounds: dict[str, int] = field(default_factory=dict)
    returned: bool = False
    log: list[dict] = field(default_factory=list)
    equipment: dict[str, list[str]] = field(default_factory=dict)
    ammo: int = 0
    shots: int = 0
    local_pressure: int = 0
    horde_deck: dict = field(default_factory=dict)
    fatigue: dict[str, int] = field(default_factory=dict)
    next_enemy: int = 1
    failed: bool = False
    knife_used: list[str] = field(default_factory=list)
    shotgun_used: list[str] = field(default_factory=list)
    ap_penalty: dict[str, int] = field(default_factory=dict)

    @classmethod
    def start(cls, team: list[str], clock: int,
              equipment: dict[str, list[str]] | None = None,
              ammo: int = 2, horde_deck: dict | None = None,
              fatigue: dict[str, int] | None = None,
              ap_penalty: dict[str, int] | None = None,
              allow_emergency_at_limit: bool = False) -> "Ambush02":
        if not team or len(set(team)) != len(team) or any(hero not in HEROES for hero in team):
            raise ValueError("Equipe de Emboscada inválida")
        if (not (0 <= clock <= 9 or (allow_emergency_at_limit and clock == 10))
                or not isinstance(ammo, int) or ammo < 0):
            raise ValueError("Relógio inválido para Emboscada")
        loadout = equipment if equipment is not None else {
            hero: ["Pé de cabra"] for hero in team}
        if (set(loadout) != set(team)
                or any(len(items) > 4 or any(item not in WEAPONS and item != "Bateria"
                                             for item in items)
                       for items in loadout.values())):
            raise ValueError("Equipamento de Emboscada inválido")
        fatigue = fatigue if fatigue is not None else {hero: 0 for hero in team}
        if (set(fatigue) != set(team)
                or any(not isinstance(value, int) or not 0 <= value <= 3
                       for value in fatigue.values())):
            raise ValueError("Fadiga de Emboscada inválida")
        ap_penalty = ap_penalty if ap_penalty is not None else {hero: 0 for hero in team}
        if (set(ap_penalty) != set(team)
                or any(not isinstance(value, int) or not 0 <= value <= 2
                       for value in ap_penalty.values())):
            raise ValueError("Penalidade de PA da Emboscada inválida")
        enemies = [{"id": i + 1, "kind": "Errante", "zone": 6, "hp": 1}
                   for i in range(ceil(len(team) / 2))]
        return cls(list(team), clock, {hero: 1 for hero in team}, enemies,
                   wounds={hero: 0 for hero in team},
                   equipment=deepcopy(loadout), ammo=ammo,
                   horde_deck=(HordeDeck02.from_snapshot(horde_deck).snapshot()
                               if horde_deck is not None
                               else HordeDeck02.new(clock).snapshot()),
                   fatigue=deepcopy(fatigue), next_enemy=len(enemies) + 1,
                   ap_penalty=deepcopy(ap_penalty))

    def _pay(self, hero: str, amount: int) -> None:
        if (self.returned or self.failed or self.round_no == self.completed_rounds
                or hero not in self.ap or self.ap[hero] < amount
                or self.wounds.get(hero, 0) >= 3):
            raise ValueError("PA indisponíveis na Emboscada")
        self.ap[hero] -= amount

    def begin_round(self) -> None:
        if self.returned or self.failed or self.round_no != self.completed_rounds:
            raise ValueError("Rodada de Emboscada indisponível")
        if self.clock >= 10:
            raise ValueError("Relógio excedido na Emboscada")
        self.clock += 1
        self.round_no += 1
        self.shots = 0
        self.knife_used = []
        self.shotgun_used = []
        if self.clock >= 9:
            for hero in self.team:
                self.fatigue[hero] = min(3, self.fatigue[hero] + 1)
        self.ap = {hero: max(1, 3 - self.ap_penalty[hero]
                             - int(self.fatigue[hero] >= 2))
                   for hero in self.team}
        self.log.append({"event": "round", "number": self.round_no,
                         "clock": self.clock, "fatigue": self.fatigue.copy()})

    def move(self, hero: str, zone: int) -> None:
        if hero not in self.positions or zone not in (1, 2, 5, 6):
            raise ValueError("Zona de Emboscada inválida")
        current = self.positions[hero]
        pair = tuple(sorted((current, zone)))
        if pair not in EDGES or (pair == DOOR and not self.door_open):
            raise ValueError("Passagem fechada na Emboscada")
        self._pay(hero, 1)
        self.positions[hero] = zone
        self.log.append({"event": "move", "hero": hero, "from": current, "to": zone})

    def open_door(self, hero: str) -> None:
        if hero not in self.positions or self.positions[hero] != 1 or self.door_open:
            raise ValueError("Porta da Emboscada indisponível")
        self._pay(hero, 1)
        self.door_open = True
        self.log.append({"event": "door", "hero": hero})

    def attack(self, hero: str, enemy_id: int, weapon: str, die: int) -> bool:
        if hero not in self.positions or weapon not in WEAPONS or not 1 <= die <= 6:
            raise ValueError("Ataque de Emboscada inválido")
        target = next((enemy for enemy in self.enemies if enemy["id"] == enemy_id), None)
        if target is None or weapon not in self.equipment[hero]:
            raise ValueError("Inimigo ou arma indisponível")
        damage, cost, ranged = WEAPONS[weapon]
        here, there = self.positions[hero], target["zone"]
        pair = tuple(sorted((here, there)))
        if ranged:
            if here != there and (pair not in EDGES or (pair == DOOR and not self.door_open)):
                raise ValueError("Alvo fora de alcance ou sem linha de visão")
            if self.ammo < 1:
                raise ValueError("Munição insuficiente")
        elif there != here:
            raise ValueError("Inimigo fora de alcance")
        if weapon == "Espingarda" and hero in self.shotgun_used:
            raise ValueError("Espingarda já usada nesta rodada")
        self._pay(hero, cost)
        if ranged:
            self.ammo -= 1
            self.shots += 1
        if weapon == "Espingarda":
            self.shotgun_used.append(hero)
        bonus = int(weapon == "Faca" and hero not in self.knife_used)
        if weapon == "Faca":
            self.knife_used.append(hero)
        attribute = HEROES[hero]["attributes"]["Agilidade" if ranged else "Corpo"]
        defense = ENEMIES[target["kind"]][1]
        hit = die == 6 or (die != 1 and die + attribute + bonus >= defense)
        if hit:
            target["hp"] -= damage
            if target["hp"] <= 0:
                self.enemies.remove(target)
        self.log.append({"event": "attack", "hero": hero, "enemy": enemy_id,
                         "weapon": weapon, "die": die, "hit": hit,
                         "ammo": self.ammo, "shots": self.shots})
        return hit

    def _spawn(self, kind: str, zone: int) -> None:
        if len(self.enemies) >= 24:
            self.failed = True
            self.log.append({"event": "overrun", "zone": zone})
            return
        self.enemies.append({"id": self.next_enemy, "kind": kind, "zone": zone,
                             "hp": ENEMIES[kind][0], "door_target": None,
                             "door_hits": 0})
        self.next_enemy += 1

    def _activate(self) -> None:
        for enemy in list(self.enemies):
            targets = sorted((len(path) - 1, zone, hero, path)
                             for hero, zone in self.positions.items()
                             if (path := self._path(enemy["zone"], zone)))
            if not targets:
                continue
            _, _, hero, path = targets[0]
            if len(path) == 1:
                self.wounds[hero] = min(3, self.wounds[hero] + ENEMIES[enemy["kind"]][2])
                self.log.append({"event": "wound", "hero": hero,
                                 "enemy": enemy["id"], "amount": ENEMIES[enemy["kind"]][2]})
                continue
            for _ in range(ENEMIES[enemy["kind"]][3]):
                path = self._path(enemy["zone"], self.positions[hero])
                if len(path) < 2:
                    break
                nxt = path[1]
                pair = tuple(sorted((enemy["zone"], nxt)))
                if pair == DOOR and not self.door_open:
                    self.door_open = True
                    self.log.append({"event": "enemy_open_door", "enemy": enemy["id"],
                                     "edge": list(pair)})
                    break
                old = enemy["zone"]
                enemy["zone"] = nxt
                self.log.append({"event": "enemy_move", "enemy": enemy["id"],
                                 "from": old, "to": nxt})
                if nxt == self.positions[hero]:
                    break

    def _horde(self) -> None:
        deck = HordeDeck02.from_snapshot(self.horde_deck)
        card = deck.draw()
        self.horde_deck = deck.snapshot()
        kind, count = {"Arrastar": ("Errante", 1), "Corrida": ("Corredor", 1),
                       "Aglomerado": ("Errante", ceil(len(self.team) / 2)),
                       "Peso morto": ("Bruto", 1)}[card]
        spawned = 0
        for _ in range(count):
            before = len(self.enemies)
            self._spawn(kind, 6)
            spawned += len(self.enemies) - before
            if self.failed:
                break
        self.log.append({"event": "horde", "card": card,
                         "zone": 6, "spawned": spawned})

    @staticmethod
    def _path(start: int, target: int) -> list[int]:
        """Shortest route on M1; zone labels have no distance semantics."""
        graph = {zone: [] for zone in (1, 2, 5, 6)}
        for a, b in EDGES:
            graph[a].append(b)
            graph[b].append(a)
        queue = deque([(start, [start])])
        seen = {start}
        while queue:
            zone, path = queue.popleft()
            if zone == target:
                return path
            for neighbor in sorted(graph[zone]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def end_round(self) -> None:
        if self.returned or self.failed or self.completed_rounds == self.round_no:
            raise ValueError("Rodada de Emboscada já encerrada")
        self._activate()
        for _ in range(self.shots // 2):
            self._spawn("Errante", 6)
            if self.failed:
                break
        self.local_pressure += 1
        if not self.failed and self.local_pressure >= 2:
            self.local_pressure = 0
            self._horde()
        if not self.failed and self.clock >= 9:
            self._horde()
        self.completed_rounds += 1
        self.log.append({"event": "end_round", "number": self.round_no,
                         "enemies": len(self.enemies), "clock": self.clock,
                         "pressure": self.local_pressure, "failed": self.failed})

    def finish(self) -> None:
        if (self.returned or self.failed or self.completed_rounds != self.round_no
                or self.round_no < 1 or any(zone != 1 for zone in self.positions.values())
                or any(enemy["zone"] == 1 for enemy in self.enemies)):
            raise ValueError("Retorno da Emboscada não liberado")
        self.returned = True
        self.log.append({"event": "return", "clock": self.clock})

    def emergency_return(self) -> None:
        """Retirada automática: falha a missão e aplica ferimento/fadiga canônicos."""
        if self.returned:
            raise ValueError("Emboscada já retornou")
        for hero in self.team:
            self.wounds[hero] = min(3, self.wounds[hero] + 1)
            self.fatigue[hero] = 3
        self.failed = True
        self.returned = True
        self.log.append({"event": "emergency", "clock": self.clock,
                         "wounds": self.wounds.copy(), "fatigue": self.fatigue.copy()})

    def snapshot(self) -> dict:
        return deepcopy({"team": self.team, "clock": self.clock,
                         "positions": self.positions, "enemies": self.enemies,
                         "ap": self.ap, "round_no": self.round_no,
                         "completed_rounds": self.completed_rounds,
                         "door_open": self.door_open, "wounds": self.wounds,
                         "returned": self.returned, "log": self.log,
                         "equipment": self.equipment, "ammo": self.ammo,
                         "shots": self.shots, "local_pressure": self.local_pressure,
                         "horde_deck": self.horde_deck, "fatigue": self.fatigue,
                         "next_enemy": self.next_enemy, "failed": self.failed,
                         "knife_used": self.knife_used,
                         "shotgun_used": self.shotgun_used,
                         "ap_penalty": self.ap_penalty})

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "Ambush02":
        required = {"team", "clock", "positions", "enemies", "ap", "round_no",
                    "completed_rounds", "door_open", "wounds", "returned", "log"}
        extended = {"equipment", "ammo", "shots", "local_pressure", "horde_deck",
                    "fatigue", "next_enemy", "failed", "knife_used",
                    "shotgun_used", "ap_penalty"}
        if set(snapshot) not in (required, required | extended):
            raise ValueError("Snapshot de Emboscada incompatível")
        payload = deepcopy(snapshot)
        if set(snapshot) == required:
            payload.update({
                "equipment": {hero: ["Pé de cabra"] for hero in snapshot["team"]},
                "ammo": 2, "shots": 0, "local_pressure": 0,
                "horde_deck": HordeDeck02.new(snapshot["clock"]).snapshot(),
                "fatigue": {hero: 0 for hero in snapshot["team"]},
                "next_enemy": max((enemy["id"] for enemy in snapshot["enemies"]),
                                  default=0) + 1,
                "failed": False, "knife_used": [], "shotgun_used": [],
                "ap_penalty": {hero: 0 for hero in snapshot["team"]},
            })
        obj = cls(**payload)
        if any(hero not in HEROES for hero in obj.team):
            raise ValueError("Snapshot de Emboscada inválido")
        obj.horde_deck = HordeDeck02.from_snapshot(obj.horde_deck).snapshot()
        return obj


__all__ = ["Ambush02"]
