"""Migração da vitória legal da Cisterna para o mundo regional."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrated_campaign import IntegratedCampaign
from system import HEROES, World
from verify_campaign_player02 import execute
from verify_continuous_campaign import execute as execute_continuous


class CampaignTransitionTests(unittest.TestCase):
    @staticmethod
    def completed_seed22():
        player, _ = execute(22)
        return player.game

    def test_migration_requires_real_cistern_certificate(self):
        game = IntegratedCampaign.new(22, ("ZC-HER-0001", "ZC-HER-0003"),
                                      ("ZC-VIN-0005", "ZC-VIN-0002"))
        with self.assertRaisesRegex(ValueError, "verified_victory"):
            game.transition_to_last_transmission()
        self.assertIsNone(game.world)

    def test_legal_seed22_migrates_people_resources_and_provenance(self):
        game = self.completed_seed22()
        before_cistern = game.cistern.__dict__.copy()
        expected_source_people = [dict(person) for person in game.cistern.people]
        receipt = game.transition_to_last_transmission()

        self.assertEqual(game.phase, "last_transmission")
        self.assertTrue(game.world.cistern_verified)
        self.assertEqual(set(game.world.heroes), set(game.founders))
        self.assertEqual(game.world.residents, 3)
        self.assertEqual(game.world.consumers, 3)
        self.assertEqual(game.world.continuity_people, [
            person for person in expected_source_people if person["kind"] != "hero"])
        self.assertEqual(game.world.stock["food"], sum(before_cistern["food"]))
        self.assertEqual(game.world.stock["water"], sum(before_cistern["water"]))
        self.assertEqual(game.world.stock["medicine"], before_cistern["medicine"])
        self.assertEqual(game.world.stock["ammo"], before_cistern["ammo"])
        self.assertEqual(game.world.stock["fuel"], 0)
        self.assertEqual(receipt["source_digest"],
                         game.world.cistern_record["migration"]["source_digest"])
        archive = game.world.cistern_record["migration"]["source_archive"]
        self.assertEqual(archive["founders"], game.founders)
        self.assertEqual(archive["links"], game.links)
        self.assertEqual(archive["cistern"]["people"], expected_source_people)
        self.assertEqual(archive["cistern"]["structures"], before_cistern["structures"])
        self.assertEqual(len(archive["mission_receipts"]), 3)
        self.assertEqual({receipt["destination"] for receipt in archive["mission_receipts"]},
                         {"mercado", "oficina", "estação"})
        game.world.validate()

    def test_migration_preserves_nonzero_fatigue_in_test_only_state_fixture(self):
        game=self.completed_seed22()
        hero=game.founders[0]
        source=next(person for person in game.cistern.people
                    if person['id']==hero)
        # Unit fixture for state mapping only; this does not claim a new legal
        # campaign trajectory or replace the certified seed-22 replay.
        source['fatigue']=2
        game.transition_to_last_transmission()
        self.assertEqual(game.world.heroes[hero]['fatigue'],2)
        self.assertEqual(game.world.heroes[hero]['continuity_state']['fatigue'],2)

    def test_transition_is_idempotent_and_does_not_duplicate_stock(self):
        game = self.completed_seed22()
        first = game.transition_to_last_transmission()
        stock = dict(game.world.stock)
        second = game.transition_to_last_transmission()
        self.assertEqual(first, second)
        self.assertEqual(game.world.stock, stock)
        self.assertEqual(len(game.world.log), 1)

    def test_migration_survives_save_load_and_preserves_second_arc_phase(self):
        game = self.completed_seed22()
        receipt = game.transition_to_last_transmission()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "continuous-campaign.json"
            game.save(path)
            restored = IntegratedCampaign.load(path)
        self.assertEqual(restored.phase, "last_transmission")
        self.assertEqual(restored.world.cistern_record, game.world.cistern_record)
        self.assertEqual(restored.world.stock, game.world.stock)
        self.assertEqual(restored.transition_to_last_transmission(), receipt)

    def test_replay_stops_at_regional_emergency_without_forging_return(self):
        replay = execute_continuous(22)
        last = replay["last_transmission"]
        self.assertEqual(last["status"], "local_expedition_defeat")
        self.assertEqual(last["phase"], "last_transmission")
        self.assertEqual(last["clock_at_emergency"], 7)
        self.assertEqual(last["clock_after_night"], 0)
        self.assertEqual(last["blocked_action"], "continue_second_arc")
        self.assertIn("incapacitado", last["error"])
        self.assertEqual(last["contact_receipt"]["npc"], "EXP-NPC-02")
        self.assertEqual(last["emergency_receipt"]["status"], "failed")
        self.assertEqual(last["emergency_receipt"]["stranded_npcs"], ["EXP-NPC-02"])
        self.assertEqual(last["heroes"]["ZC-HER-0001"]["health"], 0)
        self.assertIn("derrota local", last["blocking_requirement"])

    def test_all_twelve_cistern_founders_have_world_identity_profiles(self):
        for founder_id in (f"ZC-HER-{number:04d}" for number in range(1, 13)):
            with self.subTest(founder=founder_id):
                self.assertIn(founder_id, HEROES)
                world = World.new(4, [founder_id])
                self.assertEqual(list(world.heroes), [founder_id])
                self.assertEqual(world.residents, 1)
        self.assertNotIn("ZC-HER-0013", HEROES)

    def test_continuity_people_and_dogs_remain_in_daily_consumption(self):
        world = World.new(9, ["ZC-HER-0001"], {"food": 4, "water": 4})
        world.continuity_people = [
            {"id": "R01", "kind": "adult"},
            {"id": "C01", "kind": "child"},
            {"id": "D01", "kind": "dog"},
        ]
        world.validate()
        result = world.end_day()
        self.assertEqual(world.residents, 3)
        self.assertEqual(world.consumers, 4)
        self.assertEqual(result["missing"], {"food": 0, "water": 0})
        self.assertEqual(world.stock["food"], 0)
        self.assertEqual(world.stock["water"], 0)

    def test_selected_teo_cannot_be_recruited_again_as_npc(self):
        world = World.new(10, ["ZC-HER-0011"], {"food": 8, "water": 8})
        self.assertFalse(world.recruit("EXP-NPC-01"))
        world.validate()


if __name__ == "__main__":
    unittest.main()
