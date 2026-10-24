"""Resolução tática isolada da Emboscada de Viagem da Cisterna 0.2."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from collections import deque
from math import ceil

from cistern_tactics02 import HEROES


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

    @classmethod
    def start(cls, team: list[str], clock: int) -> "Ambush02":
        if not team or len(set(team)) != len(team) or any(hero not in HEROES for hero in team):
            raise ValueError("Equipe de Emboscada inválida")
        if not 0 <= clock <= 9:
            raise ValueError("Relógio inválido para Emboscada")
        enemies = [{"id": i + 1, "kind": "Errante", "zone": 6, "hp": 1}
                   for i in range(ceil(len(team) / 2))]
        return cls(list(team), clock, {hero: 1 for hero in team}, enemies,
                   wounds={hero: 0 for hero in team})

    def _pay(self, hero: str, amount: int) -> None:
        if (self.returned or self.round_no == self.completed_rounds
                or hero not in self.ap or self.ap[hero] < amount):
            raise ValueError("PA indisponíveis na Emboscada")
        self.ap[hero] -= amount

    def begin_round(self) -> None:
        if self.returned or self.round_no != self.completed_rounds:
            raise ValueError("Rodada de Emboscada indisponível")
        if self.clock >= 10:
            raise ValueError("Relógio excedido na Emboscada")
        self.clock += 1
        self.round_no += 1
        self.ap = {hero: 3 for hero in self.team}
        self.log.append({"event": "round", "number": self.round_no,
                         "clock": self.clock})

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

    def attack(self, hero: str, enemy_id: int, die: int) -> bool:
        if hero not in self.positions or not 1 <= die <= 6:
            raise ValueError("Ataque de Emboscada inválido")
        target = next((enemy for enemy in self.enemies if enemy["id"] == enemy_id), None)
        if target is None or target["zone"] != self.positions[hero]:
            raise ValueError("Inimigo fora de alcance")
        self._pay(hero, 1)
        attribute = HEROES[hero]["attributes"]["Corpo"]
        hit = die == 6 or (die != 1 and die + attribute >= 5)
        if hit:
            target["hp"] -= 1
            if target["hp"] <= 0:
                self.enemies.remove(target)
        self.log.append({"event": "attack", "hero": hero, "enemy": enemy_id,
                         "die": die, "hit": hit})
        return hit

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
        if self.returned or self.completed_rounds == self.round_no:
            raise ValueError("Rodada de Emboscada já encerrada")
        for enemy in self.enemies:
            targets = sorted((len(path) - 1, zone, hero, path)
                             for hero, zone in self.positions.items()
                             if (path := self._path(enemy["zone"], zone)))
            if not targets:
                continue
            _, _, hero, path = targets[0]
            if len(path) == 1:
                self.wounds[hero] += 1
                self.log.append({"event": "wound", "hero": hero,
                                 "enemy": enemy["id"]})
                continue
            next_zone = path[1]
            pair = tuple(sorted((enemy["zone"], next_zone)))
            if pair == DOOR and not self.door_open:
                # The M1 door is a common door: the first enemy activation
                # against it opens it, matching the canonical tactical rule.
                self.door_open = True
                self.log.append({"event": "enemy_open_door", "enemy": enemy["id"],
                                 "edge": list(pair)})
            else:
                enemy["zone"] = next_zone
                self.log.append({"event": "enemy_move", "enemy": enemy["id"],
                                 "from": path[0], "to": next_zone})
        self.completed_rounds += 1
        self.log.append({"event": "end_round", "number": self.round_no,
                         "enemies": len(self.enemies)})

    def finish(self) -> None:
        if (self.returned or self.completed_rounds != self.round_no
                or self.round_no < 1 or any(zone != 1 for zone in self.positions.values())
                or any(enemy["zone"] == 1 for enemy in self.enemies)):
            raise ValueError("Retorno da Emboscada não liberado")
        self.returned = True
        self.log.append({"event": "return", "clock": self.clock})

    def snapshot(self) -> dict:
        return deepcopy({"team": self.team, "clock": self.clock,
                         "positions": self.positions, "enemies": self.enemies,
                         "ap": self.ap, "round_no": self.round_no,
                         "completed_rounds": self.completed_rounds,
                         "door_open": self.door_open, "wounds": self.wounds,
                         "returned": self.returned, "log": self.log})

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "Ambush02":
        required = {"team", "clock", "positions", "enemies", "ap", "round_no",
                    "completed_rounds", "door_open", "wounds", "returned", "log"}
        if set(snapshot) != required:
            raise ValueError("Snapshot de Emboscada incompatível")
        obj = cls(**deepcopy(snapshot))
        if any(hero not in HEROES for hero in obj.team):
            raise ValueError("Snapshot de Emboscada inválido")
        return obj


__all__ = ["Ambush02"]
