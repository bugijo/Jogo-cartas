"""Cartas de Viagem regionais: uma por trecho pago (RULES §29), opcional."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from system import World
from travel_deck02 import CARD_IDS, TravelDeck02
from verify_campaign_player02 import execute as execute_cistern

HEROES = ["ZC-HER-0001", "ZC-HER-0003"]
NEAR = "EXP-LOC-01"


def stacked(world: World, first: list[str]) -> None:
    """Põe cartas conhecidas no topo, mantendo o baralho completo e válido."""
    rest = [card for card in CARD_IDS if card not in first]
    world.regional_travel_deck = TravelDeck02(world.seed, first + rest, []).snapshot()


def world_with(first: list[str]) -> World:
    world = World.new(7, HEROES)
    world.regional_travel_cards = True
    stacked(world, first)
    return world


class RegionalTravelCardTests(unittest.TestCase):
    def test_disabled_flag_draws_nothing(self):
        world = World.new(7, HEROES)
        before = dict(world.regional_travel_deck)
        world.open_expedition("e1", HEROES, NEAR)
        self.assertEqual(world.advance_expedition("e1"), "arrived")
        self.assertEqual(world.regional_travel_deck, before)
        self.assertEqual(world.expeditions["e1"].travel_events, [])

    def test_one_card_per_paid_leg_both_directions(self):
        world = world_with(["ZC-VIA-0001", "ZC-VIA-0012"])
        world.open_expedition("e1", HEROES, NEAR)
        self.assertEqual(world.advance_expedition("e1"), "arrived")
        world.begin_return("e1")
        exp = world.expeditions["e1"]
        self.assertEqual(world.advance_expedition("e1"), "returned")
        self.assertEqual(TravelDeck02.from_snapshot(world.regional_travel_deck).discard,
                         ["ZC-VIA-0001", "ZC-VIA-0012"])
        self.assertEqual([event["direction"] for event in exp.travel_events],
                         ["outbound", "return"])

    def test_choice_card_blocks_until_public_decision(self):
        world = world_with(["ZC-VIA-0002"])
        world.open_expedition("e1", HEROES, NEAR)
        self.assertEqual(world.advance_expedition("e1"), "travel_pending")
        with self.assertRaisesRegex(ValueError, "pendente"):
            world.advance_expedition("e1")
        with self.assertRaisesRegex(ValueError, "sem provisões"):
            world.resolve_regional_travel("e1", "water")
        world.resolve_regional_travel("e1", "fatigue")
        self.assertTrue(all(world.heroes[hero]["fatigue"] == 1 for hero in HEROES))
        deck_after_choice = dict(world.regional_travel_deck)
        self.assertEqual(world.advance_expedition("e1"), "arrived")
        # Mesmo trecho: nem nova carta nem novo segmento.
        self.assertEqual(world.regional_travel_deck, deck_after_choice)

    def test_ferragens_outbound_loses_nothing_and_return_is_archived(self):
        world = world_with(["ZC-VIA-0010", "ZC-VIA-0012", "ZC-VIA-0001"])
        stock = dict(world.stock)
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        exp = world.expeditions["e1"]
        self.assertEqual(exp.travel_events[0]["effect"], {"no_material_carried": True})
        self.assertEqual(world.stock, stock)
        # Ferragens na volta: Material sem equivalente regional fica arquivado.
        world2 = world_with(["ZC-VIA-0001", "ZC-VIA-0010"])
        world2.open_expedition("e1", HEROES, NEAR)
        world2.advance_expedition("e1")
        world2.begin_return("e1")
        stock2 = dict(world2.stock)
        world2.advance_expedition("e1")
        self.assertEqual(world2.regional_travel_archive["materials"], 1)
        self.assertEqual(world2.stock, stock2)

    def test_pressure_choice_is_archived_not_spent(self):
        world = world_with(["ZC-VIA-0004"])
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        with self.assertRaises(ValueError):
            world.resolve_regional_travel("e1", "material")
        world.resolve_regional_travel("e1", "pressure")
        self.assertEqual(world.regional_travel_archive["pressure"], 1)

    def test_road_sign_skips_next_return_card(self):
        world = world_with(["ZC-VIA-0003", "ZC-VIA-0012"])
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        world.begin_return("e1")
        exp = world.expeditions["e1"]
        world.advance_expedition("e1")
        self.assertEqual(exp.travel_events[-1]["skipped"], True)
        self.assertEqual(TravelDeck02.from_snapshot(world.regional_travel_deck).discard,
                         ["ZC-VIA-0003"])

    def test_ambush_is_never_ignored(self):
        world = world_with(["ZC-VIA-0005"])
        world.open_expedition("e1", HEROES, NEAR)
        self.assertEqual(world.advance_expedition("e1"), "travel_pending")
        self.assertTrue(world.expeditions["e1"].pending_travel["ambush"])
        with self.assertRaisesRegex(ValueError, "start/finish"):
            world.resolve_regional_travel("e1", "decline")
        with self.assertRaisesRegex(ValueError, "pendente"):
            world.advance_expedition("e1")

    @staticmethod
    def _ambush_world():
        world = world_with(["ZC-VIA-0005", "ZC-VIA-0012"])
        world.gear = {hero: {f"{hero}-CROWBAR": {"template": "EXP-EQU-002", "slot": "hand",
                                                  "index": 0, "x": 0, "y": 0,
                                                  "durability": 5}}
                      for hero in HEROES}
        world.regional_horde_deck = __import__("horde_deck02").HordeDeck02.new(3).snapshot()
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        return world

    def test_ambush_uses_regional_state_without_inventing_gear_or_ammo(self):
        world = self._ambush_world()
        world.heroes[HEROES[0]]["wounds"] = 1
        world.heroes[HEROES[0]]["health"] = 2
        world.heroes[HEROES[1]]["hungry"] = True
        ambush = world.start_regional_ambush("e1")
        self.assertEqual(ambush.equipment, {hero: ["Pé de cabra"] for hero in HEROES})
        self.assertEqual(ambush.ammo, 0)
        self.assertEqual(ambush.wounds[HEROES[0]], 1)
        self.assertEqual(ambush.ap_penalty[HEROES[1]], 1)
        world2 = self._ambush_world()
        world2.gear[HEROES[1]] = {}
        self.assertEqual(world2.start_regional_ambush("e1").equipment[HEROES[1]], [])
        with self.assertRaisesRegex(ValueError, "Nenhuma"):
            world.start_regional_ambush("e1")

    def test_ambush_rounds_spend_real_segments_and_trip_continues(self):
        world = self._ambush_world()
        clock = world.regional_clock
        ambush = world.start_regional_ambush("e1")
        ambush.enemies.clear()  # fixture: rodada sem inimigos para testar a ponte
        ambush.begin_round()
        ambush.end_round()
        ambush.finish()
        self.assertEqual(world.finish_regional_ambush("e1", ambush), "continue")
        self.assertEqual((ambush.clock, world.regional_clock), (clock + 1, clock + 1))
        self.assertIsNone(world.expeditions["e1"].pending_travel)
        self.assertEqual(world.expeditions["e1"].travel_events[0]["ambush_result"]["rounds"], 1)
        self.assertEqual(world.advance_expedition("e1"), "arrived")

    def test_ambush_emergency_returns_home_with_wound_and_fatigue(self):
        world = self._ambush_world()
        ambush = world.start_regional_ambush("e1")
        ambush.emergency_return()
        self.assertEqual(world.finish_regional_ambush("e1", ambush), "emergency")
        self.assertNotIn("e1", world.expeditions)
        for hero in HEROES:
            self.assertEqual(world.heroes[hero]["location"], "camp")
            self.assertEqual(world.heroes[hero]["wounds"], 1)
            self.assertEqual(world.heroes[hero]["fatigue"], 3)

    def test_unfinished_ambush_cannot_be_settled_and_survives_save(self):
        world = self._ambush_world()
        ambush = world.start_regional_ambush("e1")
        ambush.begin_round()
        with self.assertRaisesRegex(ValueError, "não concluída"):
            world.finish_regional_ambush("e1", ambush)
        world.store_regional_ambush("e1", ambush)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "world.json"
            world.save(path)
            loaded = World.load(path)
        resumed = loaded.regional_ambush("e1")
        self.assertEqual(resumed.round_no, 1)
        self.assertEqual(resumed.team, HEROES)

    def test_pending_card_survives_save_load_without_redraw(self):
        world = world_with(["ZC-VIA-0006"])
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "world.json"
            world.save(path)
            loaded = World.load(path)
        self.assertEqual(loaded.regional_travel_deck, world.regional_travel_deck)
        self.assertEqual(loaded.expeditions["e1"].pending_travel["card_id"], "ZC-VIA-0006")
        loaded.resolve_regional_travel("e1", "decline")
        self.assertEqual(loaded.advance_expedition("e1"), "arrived")
        self.assertEqual(len(loaded.expeditions["e1"].travel_events), 1)

    def test_forged_pending_card_or_archive_is_rejected(self):
        world = world_with(["ZC-VIA-0006"])
        world.open_expedition("e1", HEROES, NEAR)
        world.advance_expedition("e1")
        world.expeditions["e1"].pending_travel["card_id"] = "ZC-VIA-9999"
        with self.assertRaisesRegex(ValueError, "pendente inválida"):
            world.validate()
        world.expeditions["e1"].pending_travel["card_id"] = "ZC-VIA-0006"
        world.regional_travel_archive["materials"] = -1
        with self.assertRaisesRegex(ValueError, "Arquivo"):
            world.validate()

    def test_night_leg_reveals_extra_card_without_extra_segment(self):
        player, _ = execute_cistern(22)
        player.game.transition_to_last_transmission()
        world = player.game.world
        self.assertTrue(world.continuous_campaign)
        world.regional_travel_cards = True
        stacked(world, ["ZC-VIA-0001", "ZC-VIA-0012", "ZC-VIA-0008"])
        heroes = [hero for hero in world.heroes
                  if world.heroes[hero]["location"] == "camp"][:1]
        world.regional_clock = 6
        world.open_expedition("e1", heroes, NEAR)
        world.advance_expedition("e1")
        world.regional_clock = 8
        world.expeditions["e1"].remaining = 0
        world.begin_return("e1")
        exp = world.expeditions["e1"]
        self.assertEqual(world.advance_expedition("e1"), "returned")
        self.assertEqual(world.regional_clock, 9)
        self.assertEqual([(event["card_id"], event.get("extra"))
                          for event in exp.travel_events[-2:]],
                         [("ZC-VIA-0012", False), ("ZC-VIA-0008", True)])


if __name__ == "__main__":
    unittest.main()
