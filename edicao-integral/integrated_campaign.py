"""Campanha contínua para A Cisterna 0.2 -> Última Transmissão.

Este módulo é uma camada de integração. Os arquivos canônicos da edição 0.2
continuam somente leitura; ``Cistern02`` permanece o modelo de preparação,
porções, relógio e filtro, enquanto ``World`` executa o segundo arco.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from arc2 import Arc2
from cistern02 import Cistern02, LINK_IDS, STARTERS
from cistern_tactics02 import Tactical02
from system import Expedition, World


PART_MISSIONS = {
    "Conexões": {"id": "CIS-MIS-A", "location": "EXP-LOC-03", "cost": 1},
    "Bomba": {"id": "CIS-MIS-B", "location": "EXP-LOC-05", "cost": 2},
    "Membrana": {"id": "CIS-MIS-C", "location": "EXP-LOC-05", "cost": 1},
}


def _world_payload(world: World) -> dict:
    return asdict(world)


def _world_from_payload(payload: dict) -> World:
    payload = dict(payload)
    payload.pop("schema", None)
    payload["expeditions"] = {
        key: Expedition(**value) for key, value in payload["expeditions"].items()
    }
    world = World(**payload)
    world.validate()
    return world


@dataclass
class IntegratedCampaign:
    """Estado único, serializável e retomável dos dois arcos."""

    schema: int
    campaign_id: str
    seed: int
    status: str
    cistern: Cistern02
    founders: list[str]
    links: list[str]
    decisions: dict[str, str] = field(default_factory=dict)
    rewards: list[str] = field(default_factory=list)
    world: World | None = None
    terminal_reason: str | None = None
    tactical: Tactical02 | None = None
    expedition_days: list[int] = field(default_factory=list)
    visited_destinations: list[str] = field(default_factory=list)
    delivered_objectives: list[str] = field(default_factory=list)
    lost_objectives: list[str] = field(default_factory=list)
    fuel_cards: list[str] = field(default_factory=list)
    battery_available: bool = False
    van_state: str = "abandoned"
    site_states: dict[str, dict] = field(default_factory=dict)

    STATUSES = {"RUNNING", "VICTORY", "DEFEAT", "IMPOSSIBLE", "PAUSED"}

    @classmethod
    def new(
        cls,
        seed: int,
        founders: list[str] | tuple[str, ...],
        links: list[str] | tuple[str, ...],
    ) -> "IntegratedCampaign":
        cistern = Cistern02.new(founders, links, seed=seed)
        return cls(1, f"zona-zero-{seed}", seed, "RUNNING", cistern,
                    list(founders), list(links))

    @property
    def phase(self) -> str:
        if self.status != "RUNNING":
            return "finished"
        return "cistern" if self.world is None else "last_transmission"

    def _require_running(self) -> None:
        if self.status != "RUNNING":
            raise ValueError("Campanha encerrada")

    def decide(self, decision_id: str, choice: str) -> None:
        self._require_running()
        if decision_id in self.decisions:
            raise ValueError("Decisão já resolvida")
        if not decision_id or not choice:
            raise ValueError("Decisão inválida")
        self.decisions[decision_id] = choice

    def collect_part(self, part: str, choice: str = "search") -> dict:
        """Indisponível até haver recibo verificável de coleta e retorno tático."""
        self._require_running()
        if self.world is not None:
            raise ValueError("Peças só podem ser coletadas no arco da Cisterna")
        if part not in PART_MISSIONS:
            raise ValueError("Missão de peça indisponível")
        raise NotImplementedError(
            "Coleta exige expedição 0.2, PA, carga e retorno; integração pendente")

    def start_expedition(self, destination: str, team: list[str],
                         route: str = "short",
                         equipment: dict[str, list[str]] | None = None) -> Tactical02:
        self._require_running()
        if self.world is not None or self.tactical is not None:
            raise ValueError("Expedição indisponível nesta fase")
        if self.cistern.meal_day == self.cistern.day:
            raise ValueError("Expedição ocorre antes da refeição noturna")
        if self.cistern.day in self.expedition_days:
            raise ValueError("Limite de uma expedição por dia")
        loadout = equipment if equipment is not None else {hero: ["Pé de cabra"] for hero in team}
        if (set(loadout) != set(team)
                or any(items.count("Pé de cabra") > 1 or items.count("Bateria") > 1
                       or any(item not in ("Pé de cabra", "Bateria") for item in items)
                       for items in loadout.values())
                or sum(items.count("Bateria") for items in loadout.values())
                   > int(self.battery_available)):
            raise ValueError("Equipamento não disponível no estoque")
        tactical = Tactical02.start(
            self.cistern, destination, team, route,
            taken_before=self.delivered_objectives + self.lost_objectives,
            first_visit=destination.lower() not in self.visited_destinations,
            equipment=loadout,
            prior_state=self.site_states.get(destination.lower()))
        self.tactical = tactical
        self.expedition_days.append(self.cistern.day)
        self.visited_destinations.append(destination.lower())
        return tactical

    def return_expedition(self, by_van: bool = False) -> list[dict]:
        self._require_running()
        if self.tactical is None:
            raise ValueError("Nenhuma expedição ativa")
        tactical = self.tactical
        if not tactical.finished:
            tactical.finish(by_van=by_van)
        proof = tactical.delivery_proof()
        keys = [
            (receipt["group_id"] if receipt["event"] == "rescue" else
             receipt.get("id", f"{receipt.get('destination')}:{receipt.get('part')}"))
            for receipt in proof if receipt["event"] != "deliver_van"
        ]
        if len(keys) != len(set(keys)) or any(key in self.delivered_objectives for key in keys):
            raise ValueError("Objetivo já entregue")
        for receipt in proof:
            if receipt["event"] == "rescue":
                self.cistern.rescue(receipt["group_id"], receipt["decision"])
                self.delivered_objectives.append(receipt["group_id"])
            elif receipt["event"] in ("pickup_part", "recover_part"):
                part = receipt["part"]
                if part in PART_MISSIONS:
                    self.cistern.receive_part(part)
                elif part == "Bateria":
                    self.battery_available = True
                self.delivered_objectives.append(f"{receipt['destination']}:{part}")
            elif receipt["event"] == "pickup_supply":
                if receipt["kind"] == "Conserva":
                    self.cistern.food.extend([4] * receipt["cards"])
                elif receipt["kind"] == "Água":
                    self.cistern.water.extend([4] * receipt["cards"])
                elif receipt["kind"] == "Combustível":
                    self.fuel_cards.append(receipt["id"])
                self.delivered_objectives.append(receipt["id"])
            elif receipt["event"] == "deliver_van":
                self.van_state = "operational"
            elif receipt["event"] == "search_reward":
                for kind, count in receipt["reward"].items():
                    if kind == "Conserva":
                        self.cistern.food.extend([4] * count)
                    elif kind == "Água":
                        self.cistern.water.extend([4] * count)
                    elif kind == "Carne":
                        self.cistern.meat.extend([4] * count)
                    elif kind == "Material":
                        self.cistern.materials += count
                    elif kind == "Munição":
                        self.cistern.ammo += count
                    elif kind == "Medicamento":
                        self.cistern.medicine += count
                    else:
                        raise ValueError("Recompensa regional desconhecida")
                self.delivered_objectives.append(receipt["id"])
        if any(receipt["event"] == "repair_van" and receipt["success"]
               for receipt in tactical.log):
            self.battery_available = False
            if not tactical.van_returned:
                self.van_state = "operational_at_posto"
        self.lost_objectives.extend(
            receipt["id"] for receipt in tactical.log
            if receipt["event"] == "fuel_spent")
        self.site_states[tactical.destination] = tactical.site_snapshot()
        self.tactical = None
        return proof

    def emergency_return(self) -> None:
        self._require_running()
        if self.tactical is None:
            raise ValueError("Nenhuma expedição ativa")
        for receipt in self.tactical.log:
            if receipt["event"] == "pickup_supply":
                self.lost_objectives.append(receipt["id"])
            elif receipt["event"] == "pickup_part":
                self.lost_objectives.append(receipt["id"])
        self.tactical.emergency()
        self.site_states[self.tactical.destination] = self.tactical.site_snapshot()
        self.tactical = None

    def meal(self) -> dict:
        self._require_running()
        if self.world is not None:
            raise ValueError("Use advance_day no arco da Última Transmissão")
        if self.tactical is not None:
            raise ValueError("Resolva a expedição antes da refeição")
        return self.cistern.meal()

    def next_cistern_day(self) -> None:
        self._require_running()
        if self.world is not None:
            raise ValueError("A Cisterna já foi concluída")
        if self.tactical is not None:
            raise ValueError("Expedição ainda não retornou")
        self.cistern.next_day()

    def complete_cistern(self) -> None:
        """Bloqueia transição enquanto não há vitória e migração verificadas."""
        self._require_running()
        if self.world is not None or not self.cistern.filter_completed:
            raise ValueError("Filtro da Cisterna ainda não está concluído")
        raise NotImplementedError(
            "Vitória candidata não certifica expedições; migração integral pendente")

    def _arc(self) -> Arc2:
        self._require_running()
        if self.world is None:
            raise ValueError("Conclua A Cisterna antes da Última Transmissão")
        return Arc2(self.world)

    def advance_day(self) -> dict:
        self._require_running()
        if self.world is None:
            raise ValueError("Use meal/next_cistern_day na Cisterna")
        result = self.world.end_day()
        if all(hero["health"] == 0 for hero in self.world.heroes.values()):
            self.finish("DEFEAT", "todos_os_protagonistas_incapacitados")
        return result

    def final_defense(self) -> dict:
        return self._arc().final_defense()

    def defense_move(self, hero_id: str, zone: int) -> None:
        self._arc().defense_move(hero_id, zone)

    def defense_attack(self, hero_id: str, item_id: str, enemy_id: str) -> dict:
        return self._arc().defense_attack(hero_id, item_id, enemy_id)

    def defense_activate(self) -> dict:
        result = self._arc().defense_activate()
        if result["status"] == "won":
            self.finish("VICTORY", "defesa_final_concluida")
        elif result["status"] == "lost":
            self.finish("DEFEAT", "defesa_final_perdida")
        return result

    def defense_retreat(self) -> None:
        self._arc().defense_retreat()
        self.finish("DEFEAT", "retirada_da_defesa_final")

    def mark_impossible(self, reason: str) -> None:
        self.finish("IMPOSSIBLE", reason)

    def finish(self, status: str, reason: str) -> None:
        if status not in self.STATUSES - {"RUNNING", "PAUSED"}:
            raise ValueError("Status terminal inválido")
        if self.status != "RUNNING":
            return
        self.status = status
        self.terminal_reason = reason

    def save(self, path: Path) -> None:
        if self.schema != 1 or self.status not in self.STATUSES:
            raise ValueError("Estado de campanha inválido")
        payload = asdict(self)
        payload["cistern"] = asdict(self.cistern)
        payload["tactical"] = self.tactical.snapshot() if self.tactical else None
        payload["world"] = _world_payload(self.world) if self.world is not None else None
        payload["world"] = {"schema": 1, **payload["world"]} if payload["world"] else None
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "IntegratedCampaign":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.pop("schema", None) != 1:
            raise ValueError("Esquema de campanha desconhecido")
        payload["cistern"] = Cistern02(**payload["cistern"])
        if payload.get("tactical") is not None:
            payload["tactical"] = Tactical02.from_snapshot(payload["cistern"],
                                                           payload["tactical"])
        if payload.get("world") is not None:
            payload["world"] = _world_from_payload(payload["world"])
        campaign = cls(schema=1, **payload)
        if campaign.status not in cls.STATUSES:
            raise ValueError("Status de campanha desconhecido")
        return campaign


__all__ = ["IntegratedCampaign", "PART_MISSIONS", "LINK_IDS", "STARTERS"]
