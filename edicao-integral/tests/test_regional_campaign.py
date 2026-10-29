"""Campanha regional contínua de vários dias com o controlador."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from regional_campaign_player import RegionalCampaignPlayer
from verify_campaign_player02 import execute as execute_cistern
from verify_regional_campaign import ARTIFACT
from simulate_regional_campaign import run_one


def migrated():
    player, _ = execute_cistern(22)
    campaign = player.game
    campaign.transition_to_last_transmission()
    campaign.world.regional_travel_cards = True
    campaign.world.regional_filter_production = True
    return campaign


class RegionalCampaignTests(unittest.TestCase):
    def test_day_runs_expedition_and_closes_with_meals(self):
        campaign = migrated()
        world = campaign.world
        player = RegionalCampaignPlayer()
        record = player.play_day(world)
        self.assertEqual(record["plan"], "supply")
        self.assertEqual(record["expedition"]["status"], "returned")
        self.assertEqual(world.day, 1)
        self.assertEqual((world.regional_clock, world.daily_expeditions), (0, 0))
        meals = [row for row in world.log if "unfed" in row]
        self.assertEqual(meals[-1]["day"], 1)
        self.assertTrue(record["clock_reset"])

    def test_meal_priority_feeds_longest_deprivation_first(self):
        world = migrated().world
        world.meal_people()["R01"]["streak"] = 1  # fixture: residente já sem refeição
        plan = RegionalCampaignPlayer.meal_plan(world)
        self.assertEqual(plan["food_priority"][0], "R01")
        self.assertEqual(plan["food_priority"], plan["water_priority"])

    def test_wounded_team_rests_before_far_station(self):
        world = migrated().world
        world.stock["food"] = 6  # fixture: dois dias de comida, sem pressão
        hero = sorted(world.heroes)[0]
        world._set_hero_health(hero, 2)
        record = RegionalCampaignPlayer().play_day(world)
        self.assertEqual(record["plan"], "rest")
        self.assertIn("Estação", record["rest_reason"])
        self.assertNotIn("expedition", record)

    def test_radio_decoded_at_dawn_with_two_clues(self):
        world = migrated().world
        world.clues = 2  # fixture
        world.stock["food"] = 6
        record = RegionalCampaignPlayer().play_day(world)
        self.assertTrue(record["radio_decoded"])
        self.assertTrue(world.flags["radio_code"])
        self.assertEqual(world.clues, 0)

    def test_military_without_fuel_rule_is_recorded_blocker(self):
        world = migrated().world
        world.flags.update(radio_code=True, access_card=True)  # fixture
        world.stock["food"] = 6
        player = RegionalCampaignPlayer()
        record = player.play_day(world)
        self.assertEqual(record["plan"], "rest")
        self.assertEqual([row["code"] for row in player.blockers],
                         ["military_fuel_rule_pending"])
        self.assertEqual(world.stock["fuel"], 0)

    def test_run_reloads_world_each_day(self):
        campaign = migrated()
        player = RegionalCampaignPlayer()
        result = player.run(campaign, 2)
        self.assertIsNot(result, campaign)
        self.assertEqual(result.world.day, 2)
        self.assertEqual(len(player.days), 2)

    def test_artifact_records_multi_day_campaign(self):
        replay = json.loads(ARTIFACT.read_text(encoding="utf-8"))["replay"]
        self.assertGreaterEqual(replay["days_played"], 3)
        self.assertGreaterEqual(replay["expeditions"], 2)
        self.assertEqual(replay["objectives"]["clues"]
                         + 2 * replay["objectives"]["radio_code"],
                         len(replay["objectives"]["clue_evidence"]))
        self.assertFalse(replay["objectives"]["military_access"])
        self.assertEqual(replay["final_stock"]["fuel"], 0)


    def test_migration_discards_excess_over_storage_with_receipt(self):
        # Decisão aprovada 2026-10-29: H6 seed 2 vence com 46 de água; depósito 30.
        import tempfile
        from campaign_player02 import CampaignPlayer02
        from integrated_campaign import IntegratedCampaign
        from simulate_cistern_sweep import auto_settings
        player = CampaignPlayer02.new_hn(2, 6)
        for key, value in auto_settings(6).items():
            setattr(player, key, value)
        self.assertTrue(player.attempt_cistern()["verified_victory"])
        receipt = player.game.transition_to_last_transmission()
        world = player.game.world
        self.assertEqual(receipt["storage_discarded"],
                         {"capacity": 30, "resources": {"water": 26}})
        self.assertEqual(sum(world.stock.values()), world.storage)
        self.assertEqual(world.stock["food"], 8)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "c.json"
            player.game.save(path)
            self.assertEqual(IntegratedCampaign.load(path).world.stock, world.stock)
        row = run_one(6, 2)
        self.assertNotEqual(row["outcome"], "migration_refused")

    def test_migration_within_storage_has_no_discard_receipt(self):
        receipt = migrated().world.log[0]
        self.assertEqual(receipt["event"], "campaign_transition")
        self.assertNotIn("storage_discarded", receipt)

if __name__ == "__main__":
    unittest.main()
