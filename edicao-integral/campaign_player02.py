"""Controlador heurístico reproduzível para tentativas legais de A Cisterna.

O controlador consulta apenas estado observável e executa ações por métodos
públicos de IntegratedCampaign, Tactical02, Ambush02 e Travel02. O dado do
controlador é rolado somente no instante em que uma ação exigir um D6.
Uma tentativa pode perder; nenhuma recompensa é concedida fora dos recibos.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import ceil
from random import Random

from cistern02 import LINK_IDS, STAGES, STARTERS
from integrated_campaign import IntegratedCampaign
from travel02 import CHOICES, TravelContext
from cistern_tactics02 import WEAPONS


@dataclass
class CampaignPlayer02:
    seed: int
    game: IntegratedCampaign
    rng: Random = field(init=False)
    decisions: list[dict] = field(default_factory=list)
    blocked: dict | None = None
    last_expedition_outcome: str = "not_started"
    last_tactical_state: dict | None = None
    current_trip_events: list[dict] = field(default_factory=list)
    # Máximo de heróis por destino; ausente = todos os fundadores aptos.
    team_caps: dict[str, int] = field(default_factory=dict)
    # Modo adaptativo: busca comida nos dias 4–5 e escala vigias em cercos.
    # Desligado, preserva o plano fixo do replay certificado da seed 22.
    adaptive: bool = False
    adaptive_order: tuple[str, ...] = ("Oficina", "Estação")
    # §26 no modo adaptativo; desligável para comparar com a medição anterior.
    emergency_collection: bool = True
    # Táticas do modo adaptativo, ligáveis uma a uma para medição.
    tactics: tuple[str, ...] = ("escort", "late_retreat", "cautious", "support")

    def __post_init__(self) -> None:
        self.rng = Random(self.seed ^ 0xC15A)

    @classmethod
    def new_h2(cls, seed: int) -> "CampaignPlayer02":
        """Sorteia vínculos de um baralho embaralhado e inicia dois fundadores."""
        return cls.new_hn(seed, 2)

    @classmethod
    def new_hn(cls, seed: int, size: int) -> "CampaignPlayer02":
        """Inicia H2–H6 com o mesmo sorteio de vínculos, um por fundador.

        Os dois primeiros fundadores são os mesmos de H2; os demais seguem a
        ordem do catálogo. O plano de expedições continua o heurístico de H2.
        """
        links = list(LINK_IDS)
        Random(seed).shuffle(links)
        # A escolha tática usa protagonistas disponíveis com Técnica alta;
        # vínculos seguem o sorteio legal do baralho.
        founders = [STARTERS[0], STARTERS[2]]
        founders += [hero for hero in STARTERS if hero not in founders]
        game = IntegratedCampaign.new(seed, founders[:size], links[:size])
        return cls(seed, game)

    @staticmethod
    def _path(map_data: dict, start: int, target: int, opened=(), enemies=(),
              can_force: bool = True, cautious: bool = False) -> list[int]:
        graph = {zone: [] for zone in map_data["zones"]}
        for a, b in map_data["edges"]:
            graph[a].append(b)
            graph[b].append(a)
        doors = {tuple(sorted(edge)) for edge in map_data["doors"]}
        blocked = {tuple(sorted(edge)) for edge in map_data["blocked"]}
        opened = {tuple(sorted(edge)) for edge in opened}
        occupied = {enemy["zone"] for enemy in enemies}
        costs = {start: 0}
        previous = {}
        queue = [(0, start)]
        while queue:
            cost, zone = heappop(queue)
            if cost != costs[zone]:
                continue
            if zone == target:
                break
            for nxt in sorted(graph[zone]):
                pair = tuple(sorted((zone, nxt)))
                step = 1 + int(zone in occupied)
                if cautious and nxt != target:
                    # Evita atravessar inimigos e a vizinhança do surgimento.
                    spawn = map_data["spawn"]
                    near_spawn = nxt == spawn or tuple(sorted((nxt, spawn))) in {
                        tuple(sorted(edge)) for edge in map_data["edges"]}
                    step += 2 * int(nxt in occupied) + int(near_spawn)
                if pair in doors and pair not in opened:
                    if pair in blocked and not can_force:
                        continue
                    step += 2 if pair in blocked else 1
                candidate = cost + step
                if candidate < costs.get(nxt, 10**9):
                    costs[nxt] = candidate
                    previous[nxt] = zone
                    heappush(queue, (candidate, nxt))
        if target not in costs:
            return []
        path = [target]
        while path[-1] != start:
            path.append(previous[path[-1]])
        return list(reversed(path))

    @staticmethod
    def _load(tactical, hero: str) -> int:
        part_place = "Oficina" if tactical.destination == "oficina" else "Estação"
        part_sizes = {
            "Conexões": 1, "Bateria": 1, "Bomba": 2, "Membrana": 1}
        return (len(tactical.equipment[hero])
                + 2 * (hero in getattr(tactical, "escorts", {}))
                + sum(part_sizes[part] for part in tactical.carried[hero])
                + sum(item["cards"] for item in tactical.supply_cargo[hero])
                + sum(item["cards"] for item in tactical.search_cargo[hero]))

    def _choice(self, trip, event_id: str, context) -> str | None:
        event = next(item for item in trip.events
                     if item["event_id"] == event_id)
        card = event["card_id"]
        if card not in CHOICES:
            return None
        options = CHOICES[card]
        if card == "ZC-VIA-0002":
            return "water" if context.water else "fatigue"
        if card == "ZC-VIA-0004":
            # Só entrega material se o abrigo ainda cobrir as etapas do filtro.
            cistern = self.game.cistern
            needed = sum(STAGES[stage]["materials"] for stage in STAGES
                         if stage not in cistern.reserved and not cistern.filter_active)
            spare = cistern.materials + context.materials - 1 >= needed
            return "material" if context.materials >= 1 and spare else "pressure"
        if card == "ZC-VIA-0006":
            return ("help" if context.food >= 1 and context.water >= 1
                    and context.moral < 5 else "decline")
        if card == "ZC-VIA-0009":
            return "accept" if context.eligible_dog_adoption and context.dogs == 0 else "decline"
        return next(iter(options))

    def _resolve_ambush(self, returning: bool = False) -> None:
        encounter = self.game.start_travel_ambush()
        trip = self.game.return_travel if returning else self.game.travel
        event_id = trip.pending_ambush
        event = next(item for item in trip.events if item["event_id"] == event_id)
        required = event["minimum_rounds"]
        while not encounter.returned and not encounter.failed:
            if encounter.round_no == encounter.completed_rounds:
                if encounter.clock >= 10:
                    self.game.emergency_return()
                    return
                encounter.begin_round()
            for hero in encounter.team:
                while encounter.ap.get(hero, 0) > 0:
                    colocated = next((enemy for enemy in encounter.enemies
                                      if enemy["zone"] == encounter.positions[hero]), None)
                    if colocated:
                        weapon = next((item for item in encounter.equipment[hero]
                                       if item in WEAPONS), None)
                        if weapon:
                            encounter.attack(hero, colocated["id"], weapon,
                                             self.rng.randint(1, 6))
                            self.decisions.append({"action": "ambush_attack",
                                "hero": hero, "enemy": colocated["id"],
                                "round": encounter.round_no})
                            continue
                    if encounter.positions[hero] != 1:
                        graph = {zone: [] for zone in (1, 2, 5, 6)}
                        for a, b in ((1, 2), (1, 5), (2, 6), (5, 6)):
                            graph[a].append(b)
                            graph[b].append(a)
                        queue = deque([(encounter.positions[hero],
                                        [encounter.positions[hero]])])
                        seen = {encounter.positions[hero]}
                        path = []
                        while queue:
                            zone, route = queue.popleft()
                            if zone == 1:
                                path = route
                                break
                            for nxt in sorted(graph[zone]):
                                if nxt not in seen:
                                    seen.add(nxt)
                                    queue.append((nxt, route + [nxt]))
                        if len(path) > 1:
                            nxt = path[1]
                            if tuple(sorted((encounter.positions[hero], nxt))) == (1, 5) \
                                    and not encounter.door_open:
                                encounter.open_door(hero)
                            else:
                                encounter.move(hero, nxt)
                            continue
                    # Hold the exit and spend no unneeded AP. M1 resolves by activation.
                    break
            encounter.end_round()
            if (encounter.round_no >= required and encounter.completed_rounds == encounter.round_no
                    and all(zone == 1 for zone in encounter.positions.values())
                    and not any(enemy["zone"] == 1 for enemy in encounter.enemies)):
                encounter.finish()
                self.game.finish_travel_ambush()
            elif encounter.clock >= 10 and not encounter.returned:
                self.game.emergency_return()
                return
        if encounter.failed and not encounter.returned:
            self.game.emergency_return()

    def _resolve_outbound(self) -> None:
        while self.game.travel is not None:
            trip = self.game.travel
            if trip.pending_ambush:
                self._resolve_ambush()
                if self.game.travel is None:
                    return
                continue
            if trip.pending_resolution:
                event_id = trip.pending_resolution
                choice = self._choice(trip, event_id, self.game.travel_context)
                self.game.resolve_travel_choice(event_id, choice)
                self.decisions.append({"action": "travel_choice", "event": event_id,
                                       "choice": choice})
                continue
            if trip.remaining("outbound") or trip.requires_night_extra("outbound"):
                self.game.reveal_travel()
                continue
            return

    def _resolve_return(self) -> list[dict]:
        self.blocked = None
        for _ in range(32):
            observed_trip = self.game.return_travel
            try:
                receipts = self.game.return_expedition()
                if observed_trip is not None:
                    self.current_trip_events.extend(
                        self._trip_event_rows(observed_trip, "return"))
                return receipts
            except ValueError as exc:
                trip = self.game.return_travel
                if trip is None:
                    self.blocked = {"action": "return_expedition", "error": str(exc),
                                    "day": self.game.cistern.day,
                                    "clock": self.game.cistern.clock}
                    return []
                if trip.pending_ambush:
                    self._resolve_ambush(returning=True)
                    continue
                if trip.pending_resolution:
                    event_id = trip.pending_resolution
                    choice = self._choice(trip, event_id, self.game.return_context)
                    self.game.resolve_travel_choice(event_id, choice)
                    self.decisions.append({"action": "return_choice", "event": event_id,
                                           "choice": choice})
                    continue
                self.blocked = {"action": "return_expedition", "error": str(exc),
                                "day": self.game.cistern.day,
                                "clock": self.game.cistern.clock}
                return []
        self.blocked = {"action": "return_expedition", "error": "limite de resolução",
                        "day": self.game.cistern.day, "clock": self.game.cistern.clock}
        return []

    @staticmethod
    def _trip_event_rows(trip, leg: str) -> list[dict]:
        rows = []
        for event in trip.events:
            if event.get("direction") != leg:
                continue
            event_id = event.get("event_id")
            if event_id not in trip.resolved:
                continue
            rows.append({"leg": leg, "event_id": event_id,
                         "card_id": event.get("card_id"),
                         "resolution": deepcopy(trip.resolved[event_id])})
        return rows

    def _next_task(self, tasks: list[dict], assignments: dict[str, list[dict]],
                   hero: str) -> dict | None:
        # A Bomba permite uma tentativa por herói: todos permanecem no O1
        # até a primeira tentativa resultar, para que outro herói presente
        # possa tentar legalmente no mesmo local/visita.
        pump = next((task for task in tasks if not task.get("done")
                     and task.get("part") == "Bomba"
                     and task.get("assigned") == hero), None)
        if pump is not None:
            return pump
        for task in tasks:
            if task.get("assigned") != hero:
                continue
            if not task.get("done"):
                return task
        return None

    def _support_target(self, tactical, tasks: list[dict], hero: str) -> str | None:
        """Colega com tarefa pendente mais distante da saída, para acompanhar."""
        people = {p["id"]: p for p in tactical.chapter.people}
        exit_zone = tactical.map["exit"]
        busy = [task for task in tasks if not task.get("done")
                and task.get("assigned") not in (None, hero)
                and people[task["assigned"]]["wounds"] < 3]
        if not busy:
            return None
        task = max(busy, key=lambda item: (
            self._path_cost(tactical, exit_zone, item["zone"]), -tasks.index(item)))
        return task["assigned"]

    def _rescue_target(self, tactical, tasks: list[dict], hero: str) -> str | None:
        """Incapacitado sem escolta que cabe a este herói buscar, se houver.

        O resgatador é o apto com menos tarefas pendentes e carga que comporte
        as duas cargas do incapacitado; desempate pela ordem da equipe.
        """
        people = {p["id"]: p for p in tactical.chapter.people}
        escorts = getattr(tactical, "escorts", {})
        linked = {target for escort, target in escorts.items()
                  if people[escort]["wounds"] < 3}
        victims = [member for member in tactical.team
                   if people[member]["wounds"] >= 3 and member not in linked
                   and member in tactical.positions]
        if not victims:
            return None
        candidates = [member for member in tactical.team
                      if people[member]["wounds"] < 3 and member not in escorts
                      and self._load(tactical, member) + 2 <= 4]
        if not candidates:
            return None
        pending = {member: sum(1 for task in tasks if not task.get("done")
                               and task.get("assigned") == member)
                   for member in candidates}
        rescuers = sorted(candidates, key=lambda member: (
            pending[member], self._load(tactical, member), tactical.team.index(member)))
        for rescuer, victim in zip(rescuers, victims):
            if rescuer == hero:
                return victim
        return None

    def _act_tactical(self, tactical, tasks: list[dict],
                      assignments: dict[str, list[dict]]) -> None:
        for hero in tactical.team:
            while tactical.ap.get(hero, 0) > 0 and not tactical.failed:
                person = next(item for item in tactical.chapter.people
                              if item["id"] == hero)
                if person["wounds"] >= 3:
                    break
                task = self._next_task(tasks, assignments, hero)
                target = task["zone"] if task else tactical.map["exit"]
                here = tactical.positions[hero]
                if (self.adaptive and "wounded_retreat" in self.tactics
                        and person["wounds"] >= 2 and task is not None) \
                        and not task.get("done"):
                    # Ferido grave larga as tarefas e recua com a carga.
                    for pending in tasks:
                        if pending.get("assigned") == hero and not pending.get("done"):
                            pending["done"] = True
                            pending["abandoned"] = True
                    self.decisions.append({"action": "wounded_retreat", "hero": hero,
                                           "round": tactical.round_no})
                    task, target = None, tactical.map["exit"]
                if (self.adaptive and "escort" in self.tactics
                        and hero in getattr(tactical, "escorts", {})):
                    # Quem escolta só leva o colega para a saída.
                    task, target = None, tactical.map["exit"]
                victim = self._rescue_target(tactical, tasks, hero) \
                    if self.adaptive and "escort" in self.tactics else None
                if victim is not None:
                    if tactical.positions[victim] == here:
                        if tactical.ap[hero] < 1:
                            break
                        tactical.escort(hero, victim)
                        self.decisions.append({"action": "escort", "hero": hero,
                            "escorted": victim, "round": tactical.round_no})
                        continue
                    # Vai buscar o colega; a tarefa espera.
                    task, target = None, tactical.positions[victim]
                elif (task is None and self.adaptive and "support" in self.tactics
                        and hero not in getattr(tactical, "escorts", {})):
                    protege = self._support_target(tactical, tasks, hero)
                    if protege is not None:
                        foe = next((item for item in tactical.enemies
                                    if item["zone"] == here), None)
                        arm = next((item for item in tactical.equipment[hero]
                                    if item in WEAPONS), None)
                        if foe and arm:
                            if tactical.ap[hero] < WEAPONS[arm][1]:
                                break
                            tactical.attack(hero, foe["id"], arm, self.rng.randint(1, 6))
                            self.decisions.append({"action": "support_attack",
                                "hero": hero, "enemy": foe["id"],
                                "round": tactical.round_no})
                            continue
                        if tactical.positions[protege] == here:
                            break
                        target = tactical.positions[protege]
                enemy = next((item for item in tactical.enemies
                              if item["zone"] == here), None)
                weapon = next((item for item in tactical.equipment[hero]
                               if item in WEAPONS), None)
                assigned_here = (task is not None and task.get("assigned") == hero
                                 and target == here)
                if enemy and not assigned_here and target == here:
                    target = tactical.map["exit"]
                if enemy and weapon:
                    task_here = assigned_here
                    clear_exit = (task is None and here == target
                                  and target == tactical.map["exit"])
                    needs_escape = target != here and tactical.ap[hero] >= 2
                    if not task_here and not needs_escape or clear_exit:
                        if tactical.ap[hero] < WEAPONS[weapon][1]:
                            break
                        tactical.attack(hero, enemy["id"], weapon,
                                        self.rng.randint(1, 6))
                        self.decisions.append({"action": "attack", "hero": hero,
                            "enemy": enemy["id"], "round": tactical.round_no,
                            "observed_target": target,
                            "observed_task": deepcopy(task)})
                        continue
                if tactical.positions[hero] != target:
                    tools = ("Pé de cabra", "Ferramentas")
                    team_tool = any(item in tools for member in tactical.team
                                    if member in tactical.positions
                                    for item in tactical.equipment[member])
                    path = self._path(tactical.map, tactical.positions[hero], target,
                                      tactical.opened, tactical.enemies, team_tool,
                                      cautious=self.adaptive and "cautious" in self.tactics)
                    if len(path) < 2:
                        break
                    here, nxt = path[0], path[1]
                    pair = sorted((here, nxt))
                    if pair in [sorted(edge) for edge in tactical.map["doors"]] \
                            and tuple(pair) not in tactical.opened:
                        blocked = pair in [sorted(edge) for edge in tactical.map["blocked"]]
                        tool = next((item for item in tactical.equipment[hero]
                                     if item in ("Pé de cabra", "Ferramentas")), None)
                        cost = 2 if blocked else 1
                        if tactical.ap[hero] < cost or (blocked and tool is None):
                            # Sem ferramenta, espera quem a leva abrir a porta.
                            break
                        tactical.open_door(hero, nxt, tool)
                        self.decisions.append({"action": "open_door", "hero": hero,
                                               "edge": pair, "round": tactical.round_no})
                    else:
                        cost = 1 + int(any(item["zone"] == here for item in tactical.enemies))
                        if tactical.ap[hero] < cost:
                            break
                        if any(item["zone"] == nxt for item in tactical.enemies) and weapon \
                                and not WEAPONS[weapon][2] \
                                and tactical.ap[hero] < cost + WEAPONS[weapon][1]:
                            break
                        tactical.move(hero, nxt)
                        self.decisions.append({"action": "move", "hero": hero,
                            "zone": nxt, "round": tactical.round_no})
                    continue
                if task is not None and task.get("assigned") == hero:
                    cost = task.get("ap", 1)
                    if tactical.ap[hero] < cost:
                        break
                    action = task["action"]
                    if action in ("pickup_supply", "pickup_equipment") and \
                            self._load(tactical, hero) + task["load"] > 4:
                        # Carga de estrada ocupou espaço previsto; repassa a
                        # tarefa a quem tenha espaço ou desiste do lote.
                        replacement = next((candidate for candidate in tactical.team
                            if candidate != hero and candidate in tactical.positions
                            and self._load(tactical, candidate) + task["load"] <= 4),
                            None)
                        if replacement:
                            task["assigned"] = replacement
                        else:
                            task["done"] = True
                            task["dropped"] = True
                        self.decisions.append({"action": "reassign_supply_for_load",
                            "hero": hero, "replacement": replacement,
                            "task": task.copy(), "round": tactical.round_no})
                        continue
                    if action == "pickup_supply":
                        tactical.pickup_supply(hero, task["kind"], task["lot"])
                        task["done"] = True
                        result = True
                    elif action == "pickup_equipment":
                        tactical.pickup_equipment(hero, task["item"], task["lot"])
                        task["done"] = True
                        result = True
                    elif action == "pickup_part":
                        die = self.rng.randint(1, 6) if task["part"] == "Bomba" else None
                        result = tactical.pickup_part(hero, task["part"], die=die)
                        if result:
                            task["done"] = True
                        else:
                            task.setdefault("failed_by", []).append(hero)
                            replacement = next((candidate for candidate in tactical.team
                                if candidate != hero and candidate not in task["failed_by"]
                                and self._load(tactical, candidate) + task["load"] <= 4
                                and not any(not pending.get("done")
                                    and pending is not task
                                    and pending.get("assigned") == candidate
                                    for pending in tasks)), None)
                            if replacement:
                                task["assigned"] = replacement
                            else:
                                task["done"] = True
                    else:
                        raise ValueError(f"Tarefa desconhecida: {action}")
                    self.decisions.append({"action": action, "hero": hero,
                        "task": task.copy(), "result": result,
                        "round": tactical.round_no})
                    continue
                break

    def _assign(self, team: list[str], loadout: dict[str, list[str]],
                tasks: list[dict], base: dict[str, int] | None = None
                ) -> dict[str, list[dict]]:
        assigned = {hero: [] for hero in team}
        used = base.copy() if base else {hero: len(loadout[hero]) for hero in team}
        # Agrupa tarefas de mesma zona no mesmo herói quando couber.
        for task in tasks:
            choices = [hero for hero in team if used[hero] + task["load"] <= 4]
            if not choices:
                raise ValueError("A estratégia excede a carga legal da equipe")
            hero = min(choices, key=lambda candidate: (
                0 if any(item["zone"] == task["zone"] for item in assigned[candidate]) else 1,
                used[candidate], team.index(candidate)))
            task["assigned"] = hero
            assigned[hero].append(task)
            used[hero] += task["load"]
        return assigned

    def _assign_or_trim(self, team: list[str], loadout: dict[str, list[str]],
                        tasks: list[dict], base: dict[str, int] | None = None
                        ) -> dict[str, list[dict]]:
        """Distribui a carga; se não couber, abandona mantimentos do fim da lista.

        Peças e equipamento nunca são descartados. Lotes maiores (C inicial
        acima de 4) podem não caber na equipe; a decisão fica registrada.
        """
        while True:
            for task in tasks:
                task.pop("assigned", None)
            try:
                return self._assign(team, loadout, tasks, base)
            except ValueError:
                supplies = [task for task in tasks if task["action"] == "pickup_supply"]
                if not supplies:
                    raise
                dropped = supplies[-1]
                tasks.remove(dropped)
                self.decisions.append({"action": "drop_task_for_load",
                    "task": {key: dropped[key] for key in ("kind", "lot", "zone", "load")},
                    "day": self.game.cistern.day})

    def _path_cost(self, tactical, start: int, target: int) -> int:
        """PA estimados de start até target, com portas a abrir."""
        path = self._path(tactical.map, start, target, tactical.opened, tactical.enemies)
        if not path:
            return 99
        doors = {tuple(sorted(edge)) for edge in tactical.map["doors"]}
        blocked = {tuple(sorted(edge)) for edge in tactical.map["blocked"]}
        opened = {tuple(sorted(edge)) for edge in tactical.opened}
        cost = 0
        for a, b in zip(path, path[1:]):
            pair = tuple(sorted((a, b)))
            cost += 1
            if pair in doors and pair not in opened:
                cost += 2 if pair in blocked else 1
        return cost

    def _retreat_if_late(self, tactical, tasks: list[dict]) -> None:
        """Abandona tarefas pendentes quando só resta tempo para voltar.

        Sair com parte da carga evita a emergência, que perde tudo, fere e
        deixa fadiga 3. Estimativa: 3 PA por rodada, mais uma rodada de folga
        para limpar a saída, mais os trechos de volta.
        """
        if all(task.get("done") for task in tasks):
            return
        people = {p["id"]: p for p in tactical.chapter.people}
        exit_zone = tactical.map["exit"]
        able = [hero for hero in tactical.team if people[hero]["wounds"] < 3]
        if not able:
            return
        costs = [self._path_cost(tactical, tactical.positions[hero], exit_zone)
                 for hero in able]
        for victim in tactical.team:
            if people[victim]["wounds"] >= 3 and victim not in tactical.escorts.values():
                reach = min(self._path_cost(tactical, tactical.positions[hero],
                                            tactical.positions[victim]) for hero in able)
                costs.append(reach + 1 + self._path_cost(
                    tactical, tactical.positions[victim], exit_zone))
        rounds = max(1, ceil(max(costs) / 3)) + 1
        if self.game.cistern.clock + rounds + tactical.travel_cost > 10:
            for task in tasks:
                if not task.get("done"):
                    task["done"] = True
                    task["abandoned"] = True
            self.decisions.append({"action": "retreat_late",
                "clock": self.game.cistern.clock, "round": tactical.round_no,
                "estimated_rounds": rounds})

    def _run_tactical(self, tactical, tasks: list[dict],
                      assignments: dict[str, list[dict]]) -> bool:
        for _ in range(12):
            if tactical.failed:
                return False
            if self.adaptive and "late_retreat" in self.tactics:
                self._retreat_if_late(tactical, tasks)
            self._act_tactical(tactical, tasks, assignments)
            if all(task["done"] for task in tasks) and tactical.can_exit():
                return True
            tactical.end_round()
            self.decisions.append({"action": "end_round", "round": tactical.round_no,
                                   "clock": self.game.cistern.clock,
                                   "enemies": len(tactical.enemies)})
            if tactical.can_exit():
                return True
            if self.game.cistern.clock >= 10 or tactical.failed:
                return False
            tactical.begin_round()
        return False

    def expedition(self, destination: str, team: list[str], tasks: list[dict],
                   equipment: dict[str, list[str]] | None = None,
                   route: str = "short") -> list[dict]:
        self.blocked = None
        self.current_trip_events = []
        for task in tasks:
            task.setdefault("done", False)
            if task.get("action") == "pickup_supply":
                task["load"] = (1 if task["kind"] == "Combustível" else
                                ceil(self.game.cistern.initial_consumers / 4))
        loadout = equipment or {hero: self.game.equipment_inventory.get(hero, []).copy()
                                for hero in team}
        try:
            assignments = self._assign_or_trim(team, loadout, tasks)
        except ValueError as exc:
            self.blocked = {"action": "plan_cargo", "destination": destination,
                            "error": str(exc), "loadout": deepcopy(loadout),
                            "task_loads": [task.get("load") for task in tasks]}
            self.last_expedition_outcome = "strategy_load_blocked"
            return []
        free_load = sum(4 - len(loadout[hero]) for hero in team)
        travel_material = min(1, self.game.cistern.materials, free_load)
        trip = self.game.start_travel(destination, team, route,
            context=TravelContext(food=0, water=0, materials=travel_material,
                                  fatigue={hero: 0 for hero in team}),
            equipment=loadout)
        self.decisions.append({"action": "start_travel", "destination": destination,
                               "team": team.copy(), "day": self.game.cistern.day,
                               "route": route, "materials_carried": travel_material})
        self._resolve_outbound()
        self.current_trip_events.extend(
            self._trip_event_rows(trip, "outbound"))
        if self.game.travel is None:
            self.last_expedition_outcome = "emergency_on_outbound"
            return []
        tactical = self.game.enter_expedition()
        loads = {hero: self._load(tactical, hero) for hero in team}
        planned = {hero: sum(task["load"] for task in assignments[hero]) for hero in team}
        if any(loads[hero] + planned[hero] > 4 for hero in team):
            # A carga de estrada caiu sobre um herói com tarefas previstas;
            # refaz a distribuição uma vez com a carga real.
            try:
                assignments = self._assign_or_trim(team, loadout, tasks, loads)
            except ValueError:
                # Só peças restam e não cabem: mantém o plano e deixa a
                # checagem de carga em tempo real decidir.
                pass
            self.decisions.append({"action": "replan_cargo_on_entry",
                "loads": loads, "assigned": {hero: len(items)
                for hero, items in assignments.items()}})
        survived = self._run_tactical(tactical, tasks, assignments)
        if not survived:
            self.last_tactical_state = tactical.snapshot()
            self.game.emergency_return()
            self.last_expedition_outcome = "emergency_from_map"
            self.decisions.append({"action": "emergency_return", "destination": destination,
                                   "clock": self.game.cistern.clock})
            return []
        receipts = self._resolve_return()
        if self.blocked and self.game.tactical is not None \
                and self.game.cistern.clock >= 10:
            self.game.emergency_return()
            self.last_expedition_outcome = "emergency_after_clock"
            self.blocked = None
        else:
            self.last_expedition_outcome = ("returned" if self.blocked is None
                                            else "blocked_return")
        self.decisions.append({"action": "return", "destination": destination,
                               "receipts": deepcopy(receipts),
                               "clock": self.game.cistern.clock})
        return receipts

    def _filter_workers(self, crew: list[str]) -> list[str]:
        """Até dois heróis aptos ao trabalho do filtro, na ordem da equipe."""
        people = {person["id"]: person for person in self.game.cistern.people}
        able = [hero for hero in crew
                if people[hero]["wounds"] < 3 and people[hero].get("fatigue", 0) < 3
                and not people[hero]["hungry"] and not people[hero]["thirsty"]]
        return able[:2] or crew[:2]

    def _shortfall(self) -> dict[str, int]:
        """Porções que faltam para alimentar todos até a noite 5."""
        cistern = self.game.cistern
        nights = 5 - cistern.day + 1
        need = cistern.consumers * nights
        food = sum(cistern.food) + sum(getattr(cistern, "meat", []))
        return {"food": max(0, need - food),
                "water": max(0, need - sum(cistern.water))}

    def _filter_work_left(self) -> int:
        """Trabalho ainda devido nas etapas A–C a partir da etapa atual."""
        cistern = self.game.cistern
        order = list(STAGES)
        if cistern.filter_active or cistern.stage == "done":
            return 0
        start = order.index(cistern.stage) if cistern.stage in order else 0
        total = 0
        for stage in order[start:]:
            if stage not in cistern.reserved:
                break
            total += STAGES[stage]["work"]
        return max(0, total - cistern.stage_work)

    def _able(self, person: dict) -> bool:
        return (person["kind"] in ("hero", "adult") and person["wounds"] < 3
                and person.get("fatigue", 0) < 3
                and not person["hungry"] and not person["thirsty"])

    def _adaptive_dawn(self, day: int, crew: list[str], destination, team,
                       tasks, loadout):
        """Planejamento do amanhecer: filtro, destino, vigias.

        Usa só estado observável. Reserva cada etapa assim que sua peça chegou
        em dia anterior; prioriza peças faltantes (Estação/Oficina, com nova
        tentativa), depois mantimentos ainda não retirados. Trabalhadores do
        filtro priorizam adultos civis; vigias saem de quem fica no abrigo.
        """
        cistern = self.game.cistern
        people = {person["id"]: person for person in cistern.people}
        for stage in STAGES:
            part = STAGES[stage]["part"]
            if (stage not in cistern.reserved and not cistern.filter_active
                    and part in cistern.parts and cistern.parts[part] < day
                    and cistern.materials >= STAGES[stage]["materials"]):
                self.game.reserve_filter_stage(stage)
                self.decisions.append({"action": "adaptive_reserve", "day": day,
                                       "stage": stage})
        taken = set(self.game.delivered_objectives) | set(self.game.lost_objectives)
        fit = [hero for hero in crew
               if people[hero]["wounds"] < 3 and people[hero]["fatigue"] < 3]
        adults = [person["id"] for person in cistern.people
                  if person["kind"] == "adult" and self._able(person)
                  and person["family"] in cistern.founders]
        heroes = [hero for hero in crew if self._able(people[hero])]
        remaining = self._filter_work_left() if cistern.reserved else 0
        days_left = 5 - day + 1
        # Trabalho mínimo hoje para ainda caber no prazo (2 por dia).
        must_work = max(0, remaining - 2 * (days_left - 1))
        plan = self._adaptive_destination(day, taken)
        if plan is None:
            workers = (adults + heroes)[:min(2, remaining)]
            destination, team, tasks, loadout = None, [], [], None
        else:
            destination, tasks = plan
            workers = adults[:min(2, remaining)]
            if len(workers) < must_work:
                workers += [hero for hero in heroes
                            if hero not in workers][:must_work - len(workers)]
            team = [hero for hero in fit if hero not in workers]
            loadout = None
            if not team:
                destination, tasks = None, []
            elif destination == "Oficina":
                loadout = {hero: self.game.equipment_inventory[hero].copy()
                           for hero in team}
            self.decisions.append({"action": "adaptive_plan", "day": day,
                "destination": destination, "team": team.copy(),
                "workers": workers.copy(), "shortfall": self._shortfall(),
                "tasks": [task.get("part") or task.get("item") or task.get("kind")
                          for task in tasks]})
        if workers and remaining:
            self.game.plan_filter_work(workers, team if destination else None)
        if cistern.pending_sieges:
            away = set(team) if destination else set()
            guards = [person["id"] for person in cistern.people
                      if self._able(person) and person["id"] not in workers
                      and person["id"] not in away
                      and (person["kind"] == "hero" or person["family"] in cistern.founders)
                      ][:3]
            if guards:
                self.game.plan_guards(guards)
                self.decisions.append({"action": "adaptive_guards", "day": day,
                                       "guards": guards.copy()})
        shortfall = self._shortfall()
        if self.emergency_collection and (shortfall["food"] or shortfall["water"]):
            busy = set(workers) | set(cistern.planned_guards) | (
                set(team) if destination else set())
            collectors = [person["id"] for person in cistern.people
                          if self._able(person) and person["id"] not in busy
                          and (person["kind"] == "hero"
                               or person["family"] in cistern.founders)][:2]
            plan = []
            for worker in collectors:
                kind = "Conserva" if shortfall["food"] >= shortfall["water"] else "Água"
                shortfall["food" if kind == "Conserva" else "water"] -= 1
                plan.append({"worker": worker, "kind": kind})
            if plan:
                self.game.plan_emergency_collection(plan, team if destination else None)
                self.decisions.append({"action": "adaptive_collection", "day": day,
                                       "plan": deepcopy(plan)})
        return destination, team, tasks, loadout

    def _grounded(self, site: str, part: str) -> bool:
        """Peça única perdida em emergência e registrada no chão (§34)."""
        state = self.game.site_states.get(site) or {}
        return any(item["part"] == part for item in state.get("part_ground", []))

    def _adaptive_destination(self, day: int, taken: set[str]):
        """Destino e tarefas do dia, ou None para ficar no abrigo."""
        parts = self.game.cistern.parts
        order = self.adaptive_order
        for site in order:
            if site == "Estação":
                missing = [task for task in station_day_tasks()
                           if task["action"] == "pickup_part"
                           and task["part"] not in parts
                           and (f"Estação:{task['part']}" not in taken
                                or self._grounded("estação", task["part"]))]
                # Peça precisa chegar até o dia 4 para reservar no dia 5.
                if missing and day <= 4:
                    water = [task for task in station_day_tasks()
                             if task["action"] == "pickup_supply"
                             and f"estação:Água:{task['lot']}" not in taken]
                    return "Estação", missing + water
            if (site == "Oficina" and "Conexões" not in parts and day <= 4
                    and ("Oficina:Conexões" not in taken
                         or self._grounded("oficina", "Conexões"))):
                extra = [task for task in workshop_day_tasks()
                         if task["action"] != "pickup_part"
                         and (f"oficina:{task.get('kind')}:{task['lot']}" not in taken
                              if task["action"] == "pickup_supply"
                              else f"oficina:Machado:{task['lot']}" not in taken
                              and not any("Machado" in items for items
                                          in self.game.equipment_inventory.values()))]
                return "Oficina", [task for task in workshop_day_tasks()
                                   if task["action"] == "pickup_part"] + extra
        shortfall = self._shortfall()
        if not (shortfall["food"] or shortfall["water"]) or self.game.cistern.clock + 3 > 10:
            return None
        for site, food_zone in (("Mercado", 7), ("Hospital", 7),
                                ("Condomínio", 7), ("Posto", 14)):
            lots = 2 if site == "Mercado" else 1
            tasks = []
            for kind, zone, short in (("Conserva", food_zone, shortfall["food"]),
                                      ("Água", 14, shortfall["water"])):
                tasks += [{"action": "pickup_supply", "kind": kind, "lot": lot,
                           "zone": zone, "load": 1, "ap": 1}
                          for lot in range(1, lots + 1)
                          if short and f"{site.lower()}:{kind}:{lot}" not in taken]
            if tasks:
                return site, tasks
        return None

    def day_close(self, guards: list[str] | None = None,
                  guard_rolls: list[int] | None = None, ammo: int = 0) -> dict:
        guards = guards or []
        # Sem dados fornecidos, os vigias planejados rolam no cerco.
        if guards and not self.game.cistern.work_plan_locked:
            self.game.plan_guards(guards)
        siege_result = None
        if self.game.cistern.pending_sieges:
            siege_result = self._resolve_one_siege(ammo, guard_rolls)
        work = self.game.resolve_filter_work()
        meal = self.game.meal()
        intentions = self.game.resolve_intentions()
        return {"siege": siege_result, "work": work, "meal": meal,
                "intentions": intentions}

    def _resolve_one_siege(self, ammo:int=0,
                           guard_rolls:list[int]|None=None) -> dict:
        encounter = self.game.reveal_siege()
        guards = self.game.cistern.planned_guards.copy()
        rolls = guard_rolls if guard_rolls is not None else [
            self.rng.randint(1, 6) for _ in guards]
        defense = (2 if "Portão" in self.game.cistern.structures else 0)
        defense += int("Torre" in self.game.cistern.structures)
        defense += int(any(person["kind"] == "dog" and person["alert"]
                           for person in self.game.cistern.people))
        defense += sum(die >= 4 for die in rolls) + ammo
        gap = max(0, encounter["force"] - defense)
        target_count = 0 if gap == 0 else 1 if gap <= 2 else 2
        eligible = [name for name in self.game.cistern.structures
                    if name not in ("Barraca", "Casa simples")]
        targets = [name for name in eligible if name != "Filtro"][:target_count]
        targets += [name for name in eligible
                    if name == "Filtro" and len(targets) < target_count]
        result = self.game.resolve_siege(rolls, targets, ammo)
        return {**result, "rolls": rolls, "targets": targets}

    def attempt_cistern(self) -> dict:
        """Primeira rota heurística completa, sem injetar resultados ou itens."""
        h1, h2 = self.game.founders[:2]
        # Em H3–H6 os fundadores extras acompanham as expedições com o
        # inventário inicial e entram no trabalho do filtro nos dias 4–5.
        crew = self.game.founders.copy()
        extras = {hero: self.game.equipment_inventory[hero].copy() for hero in crew[2:]}
        report = {"seed": self.seed, "founders": self.game.founders.copy(),
                  "links": self.game.links.copy(), "days": [], "receipts": [],
                  "result": None, "certificate": None, "blocked": None,
                  "optional_rescues": [], "promises": "nenhuma assumida; regra sem carta/gatilho definido"}
        report["setup"] = {
            "people": deepcopy(self.game.cistern.people),
            "food_lots": self.game.cistern.food.copy(),
            "water_lots": self.game.cistern.water.copy(),
            "materials": self.game.cistern.materials,
            "ammo": self.game.cistern.ammo,
            "event_queue": self.game.cistern.event_queue.copy(),
            "starting_equipment": deepcopy(self.game.equipment_inventory),
        }
        plans = [
            ("Mercado", crew, market_day1_tasks(), None),
            # A Oficina tem pressão crescente após a primeira visita ao Mercado.
            # Levar os dois fundadores distribui ações de coleta e mantém um
            # combatente com Machado; o pé de cabra continua com quem abre a
            # porta bloqueada da rota. O Machado só pode ser usado depois de
            # ser retirado legalmente na Oficina, portanto a primeira viagem
            # mantém o inventário inicial de ambos.
            ("Oficina", crew, workshop_day_tasks(),
             {h1: ["Pé de cabra"], h2: ["Pé de cabra"], **extras}),
            ("Estação", crew, station_day_tasks(),
             {h1: ["Pé de cabra"], h2: ["Machado"], **extras}),
            (None, [], [], None),
            (None, [], [], None),
        ]
        for day, (destination, team, tasks, loadout) in enumerate(plans, start=1):
            self.current_trip_events = []
            if self.game.cistern.day != day:
                report["blocked"] = {"day": day, "action": "day_sequence",
                                     "observed_day": self.game.cistern.day}
                break
            if day == 3 and not self.adaptive:
                try:
                    self.game.reserve_filter_stage("A")
                except (ValueError, NotImplementedError) as exc:
                    report["blocked"] = {"day": day, "action": "plan_filter_A",
                        "error": str(exc), "parts": deepcopy(self.game.cistern.parts),
                        "materials": self.game.cistern.materials}
                    break
            if self.adaptive:
                try:
                    destination, team, tasks, loadout = self._adaptive_dawn(
                        day, crew, destination, team, tasks, loadout)
                except (ValueError, NotImplementedError) as exc:
                    report["blocked"] = {"day": day, "action": "adaptive_dawn",
                        "error": str(exc), "parts": deepcopy(self.game.cistern.parts),
                        "materials": self.game.cistern.materials}
                    break
            if destination == "Estação":
                holder = next((hero for hero in crew if "Machado"
                               in self.game.equipment_inventory.get(hero, [])), None)
                inventory = self.game.equipment_inventory
                if holder is not None and self.adaptive and holder in team and not any(
                        "Pé de cabra" in inventory.get(hero, [])
                        for hero in team if hero != holder):
                    # Ninguém mais leva ferramenta: o portador do Machado leva
                    # também o Pé de cabra para a porta bloqueada.
                    loadout = {hero: inventory.get(hero, []).copy() for hero in crew}
                elif holder is not None:
                    loadout = {hero: (["Machado"] if hero == holder else
                                      ["Pé de cabra"] if "Pé de cabra"
                                      in self.game.equipment_inventory.get(hero, [])
                                      else []) for hero in crew}
                else:
                    # Machado não foi retirado: cada herói leva o que possui.
                    loadout = None
            if destination is not None:
                people = {person["id"]: person for person in self.game.cistern.people}
                fit = [hero for hero in team if people[hero]["wounds"] < 3
                       and people[hero]["fatigue"] < 3]
                fit = fit[:self.team_caps.get(destination, len(fit))]
                if fit != team:
                    self.decisions.append({"action": "leave_home",
                        "day": day, "heroes": [hero for hero in team if hero not in fit]})
                    team = fit
                if loadout is not None:
                    loadout = {hero: loadout[hero] for hero in team}
                if not team:
                    destination = None
            if destination is None:
                receipts = []
                self.last_expedition_outcome = "no_expedition"
            else:
                try:
                    receipts = self.expedition(destination, team, tasks, loadout)
                except ValueError as exc:
                    # Ferragens (ZC-VIA-0010) na ida sem Material levado: a
                    # carta não define o caso e o motor recusa. Outros erros
                    # são defeitos e devem propagar.
                    if "Material levado insuficiente" not in str(exc):
                        raise
                    report["blocked"] = {"day": day, "action": "expedition_rule_gap",
                                         "destination": destination, "error": str(exc)}
                    break
            report["receipts"].extend(deepcopy(receipts))
            report["days"].append({"day": day, "destination": destination,
                "clock": self.game.cistern.clock,
                "travel_events": deepcopy(self.current_trip_events),
                "tactical_outcome": self.last_expedition_outcome,
                "delivered": [item.get("id", item.get("part")) for item in receipts]})
            if self.last_expedition_outcome == "strategy_load_blocked":
                report["blocked"] = {"day": day, **(self.blocked or {})}
                break
            if self.game.status != "RUNNING":
                report["result"] = self.game.status
                break
            try:
                guards = []
                ammo = 2 if day == 3 else 0
                if day == 4 and not self.adaptive:
                    self.game.reserve_filter_stage("B")
                    self.game.reserve_filter_stage("C")
                    self.game.plan_filter_work(self._filter_workers(crew))
                if day == 5 and not self.adaptive:
                    self.game.plan_filter_work(self._filter_workers(crew))
                close = self.day_close(guards=guards,
                                       guard_rolls=None, ammo=ammo)
                report["days"][-1]["night"] = deepcopy(close)
                if day == 5:
                    while self.game.cistern.pending_sieges:
                        encounter = self._resolve_one_siege(0)
                        report["days"][-1].setdefault("security_sieges", []).append(
                            deepcopy(encounter))
                    try:
                        report["certificate"] = self.game.complete_cistern()
                        report["result"] = self.game.cistern.result
                    except (ValueError, NotImplementedError) as exc:
                        report["result"] = self.game.cistern.result or "unresolved"
                        report["blocked"] = {"day": day, "action": "complete_cistern",
                                              "error": str(exc),
                                              "parts": deepcopy(self.game.cistern.parts),
                                              "filter_active": self.game.cistern.filter_active,
                                              "delivered_objectives": self.game.delivered_objectives.copy()}
                else:
                    self.game.next_cistern_day()
            except (ValueError, NotImplementedError) as exc:
                report["blocked"] = {"day": day, "action": "night_or_progression",
                    "error": str(exc), "clock": self.game.cistern.clock,
                    "pending_sieges": self.game.cistern.pending_sieges.copy(),
                    "parts": deepcopy(self.game.cistern.parts),
                    "stage": self.game.cistern.stage,
                    "stage_work": self.game.cistern.stage_work}
                break
        report["result"] = report["result"] or self.game.cistern.result or self.game.status
        report["clock"] = self.game.cistern.clock
        report["campaign_status"] = self.game.status
        report["verified_victory"] = "verified_victory" in self.game.rewards
        report["rewards"] = self.game.rewards.copy()
        report["events"] = deepcopy(self.game.cistern.event_history)
        report["sieges"] = deepcopy(self.game.cistern.siege_receipts)
        report["nights_completed"] = self.game.cistern.meal_day
        report["delivered_objectives"] = self.game.delivered_objectives.copy()
        report["final_state"] = {
            "day": self.game.cistern.day,
            "meal_day": self.game.cistern.meal_day,
            "filter_active": self.game.cistern.filter_active,
            "health": self.game.cistern.health,
            "morale": self.game.cistern.morale,
            "food_lots": self.game.cistern.food.copy(),
            "water_lots": self.game.cistern.water.copy(),
            "materials": self.game.cistern.materials,
            "ammo": self.game.cistern.ammo,
            "parts": deepcopy(self.game.cistern.parts),
            "people": deepcopy(self.game.cistern.people),
            "pending_sieges": self.game.cistern.pending_sieges.copy(),
            "groups": deepcopy(self.game.cistern.groups),
            "rescue_history": deepcopy(self.game.cistern.rescue_history),
        }
        report["decision_count"] = len(self.decisions)
        report["decisions"] = deepcopy(self.decisions)
        return report


def market_day1_tasks() -> list[dict]:
    return ([{"action":"pickup_supply","kind":"Conserva","lot":lot,
              "zone":7,"load":1,"ap":1} for lot in (1,2)]
            + [{"action":"pickup_supply","kind":"Água","lot":lot,
                "zone":14,"load":1,"ap":1} for lot in (1,2)])


def workshop_day_tasks() -> list[dict]:
    return [
        {"action":"pickup_part","part":"Conexões","zone":7,"load":1,"ap":1},
        {"action":"pickup_supply","kind":"Conserva","lot":1,"zone":7,"load":1,"ap":1},
        {"action":"pickup_equipment","item":"Machado","lot":1,
         "zone":14,"load":1,"ap":1},
    ]


def station_day_tasks() -> list[dict]:
    return [
        {"action":"pickup_part","part":"Bomba","zone":7,"load":2,"ap":2},
        {"action":"pickup_part","part":"Membrana","zone":14,"load":1,"ap":1},
        {"action":"pickup_supply","kind":"Água","lot":1,"zone":14,"load":1,"ap":1},
    ]
