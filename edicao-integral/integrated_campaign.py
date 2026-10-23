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
from system import Expedition, World


PART_MISSIONS = {
    "Conexões": {"id": "CIS-MIS-A", "location": "EXP-LOC-01", "cost": 2},
    "Bomba": {"id": "CIS-MIS-B", "location": "EXP-LOC-03", "cost": 2},
    "Membrana": {"id": "CIS-MIS-C", "location": "EXP-LOC-04", "cost": 2},
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
        """Resolve uma missão de obtenção de peça sem aceitar injeção de peça.

        A peça só entra pelo local/decisão desta camada; ``receive_part`` do
        modelo 0.2 permanece disponível para compatibilidade de testes e não é
        usado pela transição automática.
        """
        self._require_running()
        if self.world is not None:
            raise ValueError("Peças só podem ser coletadas no arco da Cisterna")
        if part not in PART_MISSIONS or part in self.cistern.parts:
            raise ValueError("Missão de peça indisponível")
        if choice != "search":
            raise ValueError("Escolha não obtém a peça")
        mission = PART_MISSIONS[part]
        if self.cistern.clock + mission["cost"] > 10:
            raise ValueError("Relógio insuficiente para a missão")
        self.cistern.spend_segments(mission["cost"])
        self.cistern.receive_part(part)
        self.decisions[mission["id"]] = choice
        return {"mission": mission["id"], "part": part,
                "location": mission["location"], "day": self.cistern.day}

    def meal(self) -> dict:
        self._require_running()
        if self.world is not None:
            raise ValueError("Use advance_day no arco da Última Transmissão")
        return self.cistern.meal()

    def next_cistern_day(self) -> None:
        self._require_running()
        if self.world is not None:
            raise ValueError("A Cisterna já foi concluída")
        self.cistern.next_day()

    def complete_cistern(self) -> None:
        """Transfere apenas um filtro realmente concluído para o motor novo."""
        self._require_running()
        if self.world is not None or not self.cistern.filter_completed:
            raise ValueError("Filtro da Cisterna ainda não está concluído")
        if self.cistern.close_chapter() != "candidate_victory":
            raise ValueError("Vitória canônica da Cisterna não certificada")
        food = sum(self.cistern.food)
        water = sum(self.cistern.water)
        # O modelo novo conserva identidade dos protagonistas; porções
        # excedentes ficam limitadas ao depósito experimental, não são criadas.
        self.world = World.new(self.seed, self.founders,
                               {"food": min(food, 30), "water": min(water, 30)})
        self.world.flags["cistern_complete"] = True
        self.world.clues = 2
        self.world.log.append({"day": self.world.day, "campaign": self.campaign_id,
                               "result": "cistern_complete"})
        self.rewards.append("cistern_complete")

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
        if payload.get("world") is not None:
            payload["world"] = _world_from_payload(payload["world"])
        campaign = cls(schema=1, **payload)
        if campaign.status not in cls.STATUSES:
            raise ValueError("Status de campanha desconhecido")
        return campaign


__all__ = ["IntegratedCampaign", "PART_MISSIONS", "LINK_IDS", "STARTERS"]
