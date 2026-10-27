"""Coleta de emergência (RULES §26) no motor da Cisterna."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cistern02 import LINK_IDS, STARTERS
from integrated_campaign import IntegratedCampaign

# LINK_IDS[4] = Parceiro: o primeiro fundador traz o adulto R01.
LINKS = [LINK_IDS[4], LINK_IDS[0]]


def campaign() -> IntegratedCampaign:
    return IntegratedCampaign.new(5, [STARTERS[0], STARTERS[2]], LINKS)


class EmergencyCollectionTests(unittest.TestCase):
    def test_each_allocated_adult_adds_one_chosen_portion(self):
        game = campaign()
        food, water = sum(game.cistern.food), sum(game.cistern.water)
        game.plan_emergency_collection([{"worker": "R01", "kind": "Conserva"},
                                        {"worker": STARTERS[0], "kind": "Água"}])
        result = game.resolve_filter_work()
        self.assertEqual(sum(game.cistern.food), food + 1)
        self.assertEqual(sum(game.cistern.water), water + 1)
        # Porção avulsa, nunca uma carta de quatro.
        self.assertEqual(game.cistern.food[-1], 1)
        self.assertEqual(result["emergency_collection"]["task"], "emergency_collection")

    def test_community_limit_is_two_portions_per_day(self):
        game = campaign()
        with self.assertRaisesRegex(ValueError, "inválida"):
            game.plan_emergency_collection([
                {"worker": "R01", "kind": "Conserva"},
                {"worker": STARTERS[0], "kind": "Conserva"},
                {"worker": STARTERS[2], "kind": "Conserva"}])
        game.plan_emergency_collection([{"worker": "R01", "kind": "Conserva"}])
        with self.assertRaisesRegex(ValueError, "inválida"):
            game.plan_emergency_collection([{"worker": STARTERS[0], "kind": "Água"}])

    def test_only_rested_trusted_adults_can_collect(self):
        game = campaign()
        people = {person["id"]: person for person in game.cistern.people}
        people["R01"]["hungry"] = True
        with self.assertRaisesRegex(ValueError, "Coletor indisponível"):
            game.plan_emergency_collection([{"worker": "R01", "kind": "Água"}])
        people["R01"]["hungry"] = False
        people[STARTERS[0]]["fatigue"] = 3
        with self.assertRaisesRegex(ValueError, "Coletor indisponível"):
            game.plan_emergency_collection([{"worker": STARTERS[0], "kind": "Água"}])
        with self.assertRaisesRegex(ValueError, "inválida"):
            game.plan_emergency_collection([{"worker": "R01", "kind": "Material"}])

    def test_children_and_dogs_never_collect(self):
        game = IntegratedCampaign.new(5, [STARTERS[0], STARTERS[2]],
                                      [LINK_IDS[8], LINK_IDS[10]])
        kinds = {person["id"]: person["kind"] for person in game.cistern.people}
        child = next(pid for pid, kind in kinds.items() if kind == "child")
        dog = next(pid for pid, kind in kinds.items() if kind == "dog")
        for worker in (child, dog):
            with self.assertRaisesRegex(ValueError, "Coletor indisponível"):
                game.plan_emergency_collection([{"worker": worker, "kind": "Água"}])

    def test_one_job_per_person(self):
        game = campaign()
        game.plan_guards(["R01"])
        with self.assertRaisesRegex(ValueError, "já alocado"):
            game.plan_emergency_collection([{"worker": "R01", "kind": "Água"}])
        game = campaign()
        game.plan_emergency_collection([{"worker": "R01", "kind": "Água"}])
        with self.assertRaisesRegex(ValueError, "Vigias inválidos"):
            game.plan_guards(["R01"])

    def test_collector_cannot_join_the_expedition(self):
        game = campaign()
        with self.assertRaisesRegex(ValueError, "já alocado"):
            game.plan_emergency_collection([{"worker": STARTERS[0], "kind": "Água"}],
                                           expedition_team=[STARTERS[0]])
        game.plan_emergency_collection([{"worker": STARTERS[0], "kind": "Água"}])
        with self.assertRaisesRegex(ValueError, "Coletor não pode sair"):
            game.cistern.lock_work_plan([STARTERS[0]])

    def test_plan_survives_save_load_and_resolves_once(self):
        game = campaign()
        game.plan_emergency_collection([{"worker": "R01", "kind": "Conserva"}])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            game.save(path)
            loaded = IntegratedCampaign.load(path)
        self.assertEqual(loaded.cistern.collection_plan,
                         [{"worker": "R01", "kind": "Conserva"}])
        food = sum(loaded.cistern.food)
        loaded.resolve_filter_work()
        self.assertEqual(sum(loaded.cistern.food), food + 1)
        self.assertEqual(loaded.cistern.collection_plan, [])
        with self.assertRaisesRegex(ValueError, "já foi resolvida"):
            loaded.resolve_filter_work()
        self.assertEqual(sum(loaded.cistern.food), food + 1)

    def test_plan_is_cleared_and_available_again_next_day(self):
        game = campaign()
        game.plan_emergency_collection([{"worker": "R01", "kind": "Água"}])
        game.resolve_filter_work()
        game.meal()
        game.resolve_intentions()
        game.next_cistern_day()
        self.assertEqual(game.cistern.day, 2)
        self.assertEqual(game.cistern.collection_plan, [])
        game.plan_emergency_collection([{"worker": "R01", "kind": "Conserva"}])
        self.assertEqual(len(game.cistern.collection_plan), 1)

    def test_collection_waits_for_pending_siege(self):
        game = campaign()
        game.plan_emergency_collection([{"worker": "R01", "kind": "Água"}])
        game.cistern.pending_sieges.append("Barulho no vale")
        with self.assertRaisesRegex(ValueError, "Cerco precede"):
            game.resolve_filter_work()

if __name__ == "__main__":
    unittest.main()
