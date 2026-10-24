"""Peças só são entregues por retirada e retorno no mapa canônico."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrated_campaign import IntegratedCampaign, STARTERS, LINK_IDS
from travel02 import CARDS as TRAVEL_CARDS, TravelContext


class IntegratedTacticalTests(unittest.TestCase):
    def test_campaign_default_trip_uses_and_saves_shared_travel_shoe(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(130, STARTERS[:2], LINK_IDS[:2])
        first_card = game.travel_shoe["deck"][0]
        trip = game.start_travel(
            "Mercado", [hero], "short",
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        self.assertTrue(game.travel_uses_shoe)
        self.assertEqual(trip.events[0]["card_id"], first_card)
        self.assertEqual(trip.deck, game.travel_shoe["deck"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertEqual(resumed.travel_shoe, game.travel_shoe)
        self.assertEqual(resumed.travel.snapshot(), trip.snapshot())
        self.assertTrue(resumed.travel_uses_shoe)

    def test_campaign_rejects_three_carried_weapons_before_reserving_stock(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(131, STARTERS[:2], LINK_IDS[:2])
        weapons = ['Pé de cabra', 'Faca', 'Machado']
        game.equipment_inventory[hero] = weapons.copy()
        food, water, material = (game.cistern.food.copy(),
                                 game.cistern.water.copy(),
                                 game.cistern.materials)
        with self.assertRaisesRegex(ValueError, 'duas armas'):
            game.start_travel(
                'Mercado', [hero], context=TravelContext(
                    food=0, water=0, materials=0, fatigue={hero: 0}),
                equipment={hero: weapons})
        self.assertEqual(game.cistern.food, food)
        self.assertEqual(game.cistern.water, water)
        self.assertEqual(game.cistern.materials, material)

    def test_campaign_shoe_commits_draw_after_legal_m1_emergency(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(132, STARTERS[:2], LINK_IDS[:2])
        game.travel_shoe["deck"] = ["ZC-VIA-0005"] + [card for card in
            game.travel_shoe["deck"] if card != "ZC-VIA-0005"]
        game.start_travel("Mercado", [hero], "short",
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.start_travel_ambush()
        game.emergency_return()
        self.assertEqual(game.travel_shoe["discard"], ["ZC-VIA-0005"])
        self.assertFalse(game.travel_uses_shoe)

    def test_campaign_shoe_commits_normal_outbound_and_return_only_once(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(133, STARTERS[:2], LINK_IDS[:2])
        first = ["ZC-VIA-0001", "ZC-VIA-0007"]
        game.travel_shoe["deck"] = first + [card for card in
            game.travel_shoe["deck"] if card not in set(first)]
        trip = game.start_travel(
            "Mercado", [hero], context=TravelContext(
                food=0, water=0, materials=0, fatigue={hero: 0}))
        game.resolve_travel_choice(trip.events[-1]["event_id"], None)
        tactical = game.enter_expedition()
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(game.travel_shoe["discard"], first)
        self.assertFalse(game.travel_uses_shoe)
        with self.assertRaises(ValueError):
            game.return_expedition()
        self.assertEqual(game.travel_shoe["discard"], first)

    def test_campaign_load_rejects_fake_travel_draw_and_segment_mismatch(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(134, STARTERS[:2], LINK_IDS[:2])
        game.start_travel("Mercado", [hero], deck=[
            "ZC-VIA-0001", "ZC-VIA-0007"], context=TravelContext(
                food=0, water=0, materials=0, fatigue={hero: 0}))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            trip = payload["travel"]
            first_id = trip["events"][0]["event_id"]
            card_id = "ZC-VIA-0007"
            card = TRAVEL_CARDS[card_id]
            trip["index"] = 2
            trip["events"].append({
                "event_id": "travel-outbound-002", "card_id": card_id,
                "name": card["name"], "text": card["text"],
                "direction": "outbound", "ambush": False,
                "minimum_rounds": card["minimum_rounds"]})
            trip["resolved"][first_id] = {"choice": None, "effect": {}}
            trip["pending_choices"] = []
            trip["pending_ambush"] = None
            trip["pending_resolution"] = None
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                IntegratedCampaign.load(path)

    def test_travel_entry_requires_resolution_before_entering_map(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(114, STARTERS[:2], LINK_IDS[:2])
        travel = game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0002"],
            context=TravelContext(food=0, water=1, materials=0,
                                  fatigue={hero: 0}))
        with self.assertRaises(ValueError):
            game.enter_expedition()
        event_id=game.travel.events[-1]['event_id']
        game.resolve_travel_choice(event_id, "water")
        self.assertEqual(game.enter_expedition().destination, "mercado")
        self.assertEqual(game.cistern.clock, 2)  # trecho + primeira rodada.

    def test_outbound_travel_fatigue_choice_persists_to_local_encounter(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(123, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0002"],
            context=TravelContext(food=0, water=1, materials=0,
                                  fatigue={hero: 0}))
        event = game.travel.events[-1]
        game.resolve_travel_choice(event["event_id"], "fatigue")
        tactical = game.enter_expedition()
        person = next(p for p in game.cistern.people if p["id"] == hero)
        self.assertEqual(tactical.fatigue[hero], 1)
        self.assertEqual(person["fatigue"], 1)

    def test_travel_cannot_claim_food_water_or_materials_missing_from_stock(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(125, STARTERS[:2], LINK_IDS[:2])
        game.cistern.food = []
        with self.assertRaisesRegex(ValueError, "estoque real"):
            game.start_travel(
                "Mercado", [hero], "short", deck=["ZC-VIA-0001"],
                context=TravelContext(food=1, water=0, materials=0,
                                      fatigue={hero: 0}))
        self.assertIsNone(game.travel)

    def test_pending_return_blocks_new_trip_and_day_advance(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(126, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0006"],
            context=TravelContext(food=1, water=1, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()
        with self.assertRaises(ValueError):
            game.start_travel("Oficina", [hero], context=TravelContext(
                food=0, water=0, materials=0, fatigue={hero: 0}))
        with self.assertRaises(ValueError):
            game.next_cistern_day()

    def test_travel_entry_runs_m1_and_does_not_charge_its_segment_twice(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(115, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        ambush = game.start_travel_ambush()
        ambush.begin_round()
        ambush.move(hero, 2)
        ambush.move(hero, 6)
        ambush.attack(hero, 1, "Pé de cabra", 6)
        ambush.end_round()
        ambush.positions[hero] = 1
        ambush.finish()
        game.finish_travel_ambush()
        game.enter_expedition()
        self.assertEqual(game.cistern.clock, 3)  # trecho + M1 + rodada local.

    def test_long_ambush_pays_each_started_outbound_segment_once(self):
        hero=STARTERS[0]
        game=IntegratedCampaign.new(117,STARTERS[:2],LINK_IDS[:2])
        game.start_travel("Mercado",[hero],"long",
            deck=["ZC-VIA-0001","ZC-VIA-0005"],
            context=TravelContext(food=0,water=0,materials=0,fatigue={hero:0}))
        event=game.travel.events[-1]
        game.travel.apply(event['event_id'],game.travel_context)
        ambush_event=game.reveal_travel()
        self.assertEqual(game.cistern.clock,0)
        self.assertTrue(ambush_event['ambush'])
        ambush=game.start_travel_ambush()
        self.assertEqual(game.cistern.clock,2)  # Os dois trechos foram iniciados.
        ambush.begin_round(); ambush.end_round()
        ambush.positions[hero]=1; ambush.enemies.clear(); ambush.finish()
        game.finish_travel_ambush(); game.enter_expedition()
        self.assertEqual(game.cistern.clock,4)  # Trechos + M1 + rodada local.

    def test_ambush_wounds_persist_to_the_founder_on_return(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(118, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        ambush = game.start_travel_ambush()
        ambush.enemies[0]["zone"] = 1
        ambush.begin_round()
        ambush.end_round()
        self.assertEqual(ambush.wounds[hero], 1)
        ambush.begin_round()
        ambush.attack(hero, 1, "Pé de cabra", 6)
        ambush.end_round()
        ambush.finish()
        game.finish_travel_ambush()
        person = next(p for p in game.cistern.people if p["id"] == hero)
        self.assertEqual(person["wounds"], 1)

    def test_m1_shares_persistent_horde_shoe_and_each_night_segment_adds_fatigue(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(119, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.cistern.clock = 7
        ambush = game.start_travel_ambush()
        self.assertEqual(game.cistern.clock, 8)
        ambush.begin_round()  # Segmento 9: uma fadiga e uma Horda noturna.
        self.assertEqual(ambush.fatigue[hero], 1)
        ambush.enemies.clear()
        ambush.local_pressure = 1  # Ao fim: Horda por pressão + Horda noturna.
        ambush.end_round()
        self.assertEqual(len(ambush.horde_deck["discard"]), 2)
        ambush.finish()
        game.finish_travel_ambush()
        person = next(p for p in game.cistern.people if p["id"] == hero)
        self.assertEqual(person["fatigue"], 1)
        tactical = game.enter_expedition()
        self.assertEqual(tactical.horde_deck, game.horde_deck)
        self.assertEqual(tactical.fatigue[hero], 2)  # Segmento 10, sem cobrar 9 outra vez.

    def test_m1_emergency_resolves_travel_failure_without_safe_return_receipt(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(120, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        ambush = game.start_travel_ambush()
        ambush.begin_round()
        game.emergency_return()
        person = next(p for p in game.cistern.people if p["id"] == hero)
        self.assertEqual(person["wounds"], 1)
        self.assertEqual(person["fatigue"], 3)
        self.assertEqual(game.expedition_days, [1])
        self.assertIsNone(game.travel)
        self.assertIsNone(game.ambush)

    def test_campaign_save_restores_horde_shoe_during_m1(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(121, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        ambush = game.start_travel_ambush()
        ambush.enemies.clear()
        ambush.local_pressure = 1
        ambush.begin_round(); ambush.end_round()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "m1-horde.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertEqual(resumed.ambush.horde_deck, ambush.horde_deck)
        self.assertEqual(resumed.ambush.log, ambush.log)

    def test_return_route_ambush_can_be_resumed_and_settled(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(122, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001", "ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        event = game.travel.events[-1]
        game.travel.apply(event["event_id"], game.travel_context)
        tactical = game.enter_expedition()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()  # Stops safely at the pending return ambush.
        self.assertTrue(tactical.finished)
        ambush = game.start_travel_ambush()
        ambush.begin_round(); ambush.end_round()
        ambush.finish()
        game.finish_travel_ambush()
        game.return_expedition()
        self.assertIsNone(game.return_travel)
        self.assertIsNone(game.tactical)

    def test_emergency_resolves_return_ambush_and_closes_route_state(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(130, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()
        game.start_travel_ambush()
        game.emergency_return()
        person = next(p for p in game.cistern.people if p["id"] == hero)
        self.assertEqual(person["wounds"], 1)
        self.assertEqual(person["fatigue"], 3)
        self.assertIsNone(game.ambush)
        self.assertIsNone(game.return_travel)
        self.assertIsNone(game.return_context)
        self.assertIsNone(game.tactical)

    def test_emergency_can_resolve_return_ambush_when_clock_has_no_round_left(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(131, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        tactical.chapter.clock = 9
        with self.assertRaises(ValueError):
            game.return_expedition()  # Route payment ends at 10; M1 cannot start.
        with self.assertRaises(ValueError):
            game.start_travel_ambush()
        game.emergency_return()  # Can still choose the canonical emergency.
        self.assertIsNone(game.return_travel)
        self.assertEqual(next(p for p in game.cistern.people if p["id"] == hero)["fatigue"], 3)

    def test_failed_return_settlement_does_not_partially_consume_stock_or_receipts(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(124, STARTERS[:2], LINK_IDS[:2])
        game.cistern.food = [1]
        game.cistern.water = [1]
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001", "ZC-VIA-0006"],
            context=TravelContext(food=1, water=1, materials=0,
                                  fatigue={hero: 0}))
        outbound = game.travel.events[-1]
        game.travel.apply(outbound["event_id"], game.travel_context)
        tactical = game.enter_expedition()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()
        event = game.return_travel.events[-1]
        game.resolve_travel_choice(event["event_id"], "help")
        game.return_context.food = -1  # Corrupt saldo no limite de persistência.
        before_food = list(game.cistern.food)
        before_delivered = list(game.delivered_objectives)
        with self.assertRaises(ValueError):
            game.return_expedition()
        self.assertEqual(game.cistern.food, before_food)
        self.assertEqual(game.delivered_objectives, before_delivered)
        self.assertIsNotNone(game.return_travel)
        self.assertIsNotNone(game.return_context)
        self.assertIs(game.tactical, tactical)

    def test_unspent_reserved_trip_supplies_return_once(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(127, STARTERS[:2], LINK_IDS[:2])
        food_before = sum(game.cistern.food)
        water_before = sum(game.cistern.water)
        second = STARTERS[1]
        game.start_travel(
            "Mercado", [hero, second], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0001"],
            context=TravelContext(food=2, water=1, materials=1,
                                  fatigue={hero: 0, second: 0}))
        self.assertEqual(sum(game.cistern.food), 0)  # Carta física de 4 porções reservada.
        self.assertEqual(sum(game.cistern.water), 0)
        self.assertEqual(game.cistern.materials, 2)
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(sum(game.cistern.food), food_before)
        self.assertEqual(sum(game.cistern.water), water_before)
        self.assertEqual(game.cistern.materials, 3)

    def test_route_dog_requires_eligible_team_family_and_arrives_once(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(128, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0009", "ZC-VIA-0001"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}, eligible_dog_adoption=True))
        event = game.travel.events[-1]
        game.resolve_travel_choice(event["event_id"], "accept")
        self.assertEqual(game.travel_context.dogs, 1)
        self.assertEqual(game.travel_context.dog_family, hero)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dog-trip.json"
            game.save(path)
            game = IntegratedCampaign.load(path)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(game.cistern.dogs, 1)
        self.assertTrue(any(p["kind"] == "dog" and p["family"] == hero
                            for p in game.cistern.people))

    def test_family_with_existing_dog_cannot_accept_road_dog(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(129, STARTERS[:2], [LINK_IDS[10], LINK_IDS[0]])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0009"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}, eligible_dog_adoption=True))
        event = game.travel.events[-1]
        with self.assertRaises(ValueError):
            game.resolve_travel_choice(event["event_id"], "accept")

    def test_second_community_dog_may_join_a_different_eligible_family(self):
        hero = STARTERS[1]
        game = IntegratedCampaign.new(134, STARTERS[:2], [LINK_IDS[10], LINK_IDS[0]])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0009", "ZC-VIA-0001"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        event = game.travel.events[-1]
        game.resolve_travel_choice(event["event_id"], "accept")
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(game.cistern.dogs, 2)
        self.assertEqual(sum(p["kind"] == "dog" and p["family"] == hero
                             for p in game.cistern.people), 1)

    def test_return_skip_event_completes_without_applying_twice(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(135, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0003", "ZC-VIA-0001"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertIsNone(game.return_travel)
        self.assertIsNone(game.return_context)

    def test_return_travel_fatigue_choice_persists_to_founder(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(138, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001", "ZC-VIA-0002"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()
        event = game.return_travel.events[-1]
        game.resolve_travel_choice(event["event_id"], "fatigue")
        game.return_expedition()
        self.assertEqual(next(p for p in game.cistern.people if p["id"] == hero)["fatigue"], 1)

    def test_return_ambush_starts_from_current_fatigue_and_persists_night_segments(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(139, STARTERS[:2], LINK_IDS[:2])
        game.cistern.clock = 6
        game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001", "ZC-VIA-0005"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]["event_id"], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()  # Finish reaches segment 9.
        self.assertEqual(tactical.fatigue[hero], 1)
        ambush = game.start_travel_ambush()
        self.assertEqual(ambush.fatigue[hero], 1)
        ambush.begin_round()  # Segment 10 adds the second point.
        self.assertEqual(ambush.fatigue[hero], 2)
        ambush.enemies.clear()
        ambush.positions[hero] = 1
        ambush.end_round()
        ambush.finish()
        game.finish_travel_ambush()
        game.return_expedition()
        self.assertEqual(next(p for p in game.cistern.people if p["id"] == hero)["fatigue"], 2)

    def test_trip_cargo_respects_party_capacity(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(136, STARTERS[:2], LINK_IDS[:2])
        game.cistern.food = [4, 4, 4]
        game.cistern.water = [4]
        with self.assertRaisesRegex(ValueError, "capacidade"):
            game.start_travel(
                "Mercado", [hero], "short", deck=["ZC-VIA-0001"],
                context=TravelContext(food=9, water=4, materials=1,
                                      fatigue={hero: 0}))
        self.assertIsNone(game.travel)

    def test_trip_cards_fit_four_loads_by_counting_portion_cards(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(137, STARTERS[:2], LINK_IDS[:2])
        trip = game.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001"],
            context=TravelContext(food=4, water=4, materials=1,
                                  fatigue={hero: 0}))
        self.assertIsNotNone(trip)
        self.assertEqual(sum(game.cistern.food), 0)
        self.assertEqual(sum(game.cistern.water), 0)
        self.assertEqual(game.cistern.materials, 2)

    def test_partially_used_cards_each_consume_one_physical_load(self):
        hero = STARTERS[0]
        rejected = IntegratedCampaign.new(140, STARTERS[:2], LINK_IDS[:2])
        rejected.cistern.food = [1, 1, 1, 1]
        with self.assertRaisesRegex(ValueError, "capacidade"):
            rejected.start_travel(
                "Mercado", [hero], "short", deck=["ZC-VIA-0001"],
                context=TravelContext(food=4, water=0, materials=0,
                                      fatigue={hero: 0}))
        self.assertEqual(rejected.cistern.food, [1, 1, 1, 1])

        accepted = IntegratedCampaign.new(141, STARTERS[:2], LINK_IDS[:2])
        accepted.cistern.food = [1, 1, 1]
        accepted.start_travel(
            "Mercado", [hero], "short", deck=["ZC-VIA-0001"],
            context=TravelContext(food=3, water=0, materials=0,
                                  fatigue={hero: 0}))
        self.assertEqual(accepted.travel_context.food_lots, [1, 1, 1])
        self.assertEqual(accepted.cistern.food, [])

    def test_equipment_pickup_is_delivered_and_persists_in_loadout(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(132, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero])
        tactical.positions[hero] = 7
        receipt = tactical.pickup_equipment(hero, "Faca", 1)
        self.assertEqual(receipt["id"], "mercado:Faca:1")
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        proof = game.return_expedition()
        self.assertTrue(any(x["event"] == "pickup_equipment" for x in proof))
        self.assertIn("Faca", game.equipment_inventory[hero])
        game.meal()
        game.next_cistern_day()
        again = game.start_expedition("Mercado", [hero])
        self.assertIn("Faca", again.equipment[hero])

    def test_equipment_lost_in_emergency_is_not_delivered_or_replenished(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(133, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero])
        tactical.positions[hero] = 7
        tactical.pickup_equipment(hero, "Faca", 1)
        game.emergency_return()
        self.assertNotIn("Faca", game.equipment_inventory[hero])
        self.assertIn("mercado:Faca:1", game.lost_objectives)

    def test_pending_travel_round_trips_through_campaign_save(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(116, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0002"],
            context=TravelContext(food=0, water=1, materials=0,
                                  fatigue={hero: 0}))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "travel.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertIsNotNone(resumed.travel)
        event_id=resumed.travel.events[-1]['event_id']
        resumed.resolve_travel_choice(event_id, "water")
        self.assertEqual(resumed.enter_expedition().destination, "mercado")

    def test_return_travel_applies_ferragens_to_stock_after_legal_return(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(119, STARTERS[:2], LINK_IDS[:2])
        initial = game.cistern.materials
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0010"],
            context=TravelContext(food=0, water=0, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]['event_id'], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(game.cistern.materials, initial + 1)

    def test_return_choice_blocks_stock_settlement_until_resolved(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(120, STARTERS[:2], LINK_IDS[:2])
        game.start_travel(
            "Mercado", [hero], "short",
            deck=["ZC-VIA-0001", "ZC-VIA-0006"],
            context=TravelContext(food=1, water=1, materials=0,
                                  fatigue={hero: 0}))
        game.resolve_travel_choice(game.travel.events[-1]['event_id'], None)
        game.enter_expedition()
        tactical = game.tactical
        tactical.positions[hero] = 1
        tactical.enemies.clear()
        tactical.end_round()
        with self.assertRaises(ValueError):
            game.return_expedition()
        event_id = game.return_travel.events[-1]['event_id']
        game.resolve_travel_choice(event_id, "help")
        game.return_expedition()
        self.assertEqual(game.cistern.morale, 5)
    def test_legal_trip_delivers_once_and_survives_save(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(103, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Oficina", [hero], "long")
        tactical.move(hero, 2); tactical.move(hero, 3)
        tactical.end_round(); tactical.begin_round()
        tactical.open_door(hero, 7, "Pé de cabra"); tactical.move(hero, 7)
        tactical.end_round(); tactical.begin_round()
        tactical.pickup_part(hero, "Conexões")
        self.assertEqual(game.cistern.parts, {})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "during.json"
            game.save(path)
            game = IntegratedCampaign.load(path)
        tactical = game.tactical
        tactical.pickup_part(hero, "Bateria")
        tactical.end_round(); tactical.begin_round()
        tactical.move(hero, 3); tactical.move(hero, 2); tactical.move(hero, 1)
        tactical.end_round()
        delivery = game.return_expedition()
        self.assertEqual([x["part"] for x in delivery], ["Conexões", "Bateria"])
        self.assertEqual(game.cistern.parts["Conexões"], 1)
        self.assertTrue(game.battery_available)
        with self.assertRaises(ValueError): game.return_expedition()
        with self.assertRaises(ValueError): game.start_expedition("Estação", [hero])

    def test_emergency_does_not_deliver_part(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(103, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Oficina", [hero], "long")
        tactical.move(hero, 2); tactical.move(hero, 3)
        tactical.end_round(); tactical.begin_round()
        tactical.open_door(hero, 7, "Pé de cabra"); tactical.move(hero, 7)
        tactical.end_round(); tactical.begin_round()
        tactical.pickup_part(hero, "Conexões")
        game.emergency_return()
        self.assertEqual(game.cistern.parts, {})

    def test_return_without_loot_is_legal(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(104, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero], "long")
        tactical.end_round()
        self.assertEqual(game.return_expedition(), [])
        self.assertIsNone(game.tactical)

    def test_cannot_depart_after_nightly_meal(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(104, STARTERS[:2], LINK_IDS[:2])
        game.meal()
        with self.assertRaises(ValueError):
            game.start_expedition("Mercado", [hero])

    def test_supply_requires_pickup_and_returns_as_four_portion_cards(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(105, STARTERS[:2], LINK_IDS[:2])
        initial_food = sum(game.cistern.food)
        tactical = game.start_expedition("Oficina", [hero], "long")
        tactical.move(hero, 2); tactical.move(hero, 3)
        tactical.end_round(); tactical.begin_round()
        tactical.open_door(hero, 7, "Pé de cabra"); tactical.move(hero, 7)
        tactical.end_round(); tactical.begin_round()
        tactical.pickup_supply(hero, "Conserva", 1)
        self.assertEqual(sum(game.cistern.food), initial_food)
        tactical.end_round(); tactical.begin_round()
        tactical.move(hero, 3); tactical.move(hero, 2); tactical.move(hero, 1)
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(sum(game.cistern.food), initial_food + 4)
        self.assertIn("oficina:Conserva:1", game.delivered_objectives)

    def test_supply_lost_in_emergency_does_not_respawn(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(106, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Oficina", [hero], "long")
        tactical.move(hero, 2); tactical.move(hero, 3)
        tactical.end_round(); tactical.begin_round()
        tactical.open_door(hero, 7, "Pé de cabra"); tactical.move(hero, 7)
        tactical.end_round(); tactical.begin_round()
        tactical.pickup_supply(hero, "Conserva", 1)
        game.emergency_return()
        self.assertIn("oficina:Conserva:1", game.lost_objectives)
        game.meal(); game.next_cistern_day()
        revisit = game.start_expedition("Oficina", [hero], "long")
        revisit.positions[hero] = 7  # Isola a persistência do lote perdido.
        with self.assertRaises(ValueError):
            revisit.pickup_supply(hero, "Conserva", 1)

    def test_battery_cannot_be_added_to_loadout_without_delivery(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(107, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(ValueError):
            game.start_expedition("Posto", [hero], equipment={hero: ["Pé de cabra", "Bateria"]})
        self.assertEqual(game.cistern.clock, 0)

    def test_spent_posto_fuel_cannot_reappear(self):
        # Bateria sintética isola a contabilidade da viagem, sem simular campanha.
        hero = STARTERS[0]
        game = IntegratedCampaign.new(108, STARTERS[:2], LINK_IDS[:2])
        game.battery_available = True
        tactical = game.start_expedition(
            "Posto", [hero], equipment={hero: ["Pé de cabra", "Bateria"]})
        tactical.positions[hero] = 7
        tactical.inspect_van(hero)
        tactical.pickup_supply(hero, "Combustível", 1)
        tactical.pickup_supply(hero, "Combustível", 2)
        tactical.end_round(); tactical.begin_round()
        tactical.repair_van(hero, 6)
        tactical.positions[hero] = 1
        tactical.end_round()
        game.return_expedition(by_van=True)
        self.assertEqual(game.van_state, "operational")
        self.assertFalse(game.battery_available)
        self.assertEqual(game.fuel_cards, [])
        self.assertIn("posto:Combustível:1", game.lost_objectives)
        self.assertIn("posto:Combustível:2", game.lost_objectives)

    def test_workshop_battery_then_posto_van_uses_legal_map_actions(self):
        h1, h2 = STARTERS[:2]
        game = IntegratedCampaign.new(109, STARTERS[:2], LINK_IDS[:2])
        workshop = game.start_expedition("Oficina", [h1], "long")
        workshop.move(h1, 2); workshop.move(h1, 3)
        workshop.end_round(); workshop.begin_round()
        workshop.open_door(h1, 7, "Pé de cabra"); workshop.move(h1, 7)
        workshop.end_round(); workshop.begin_round()
        workshop.pickup_part(h1, "Bateria")
        workshop.end_round(); workshop.begin_round()
        workshop.move(h1, 3); workshop.move(h1, 2); workshop.move(h1, 1)
        workshop.end_round(); game.return_expedition()
        self.assertTrue(game.battery_available)
        game.meal(); game.next_cistern_day()

        posto = game.start_expedition("Posto", [h1, h2], "long",
            equipment={h1: ["Pé de cabra", "Bateria"], h2: ["Pé de cabra"]})
        for hero in (h1, h2):
            posto.move(hero, 2); posto.move(hero, 3)
        posto.end_round(); posto.begin_round()
        posto.open_door(h1, 7); posto.move(h1, 7); posto.inspect_van(h1)
        posto.move(h2, 7); posto.pickup_supply(h2, "Combustível", 1)
        posto.end_round(); posto.begin_round()
        self.assertTrue(posto.repair_van(h1, 6))
        posto.pickup_supply(h1, "Combustível", 2)
        posto.pickup_supply(h2, "Combustível", 3)
        posto.pickup_supply(h2, "Combustível", 4)
        posto.end_round(); posto.begin_round()
        for hero in (h1, h2):
            posto.move(hero, 3); posto.move(hero, 2); posto.move(hero, 1)
        posto.end_round()
        game.return_expedition(by_van=True)
        self.assertEqual(game.van_state, "operational")
        self.assertEqual(game.cistern.clock, 8)
        self.assertFalse(game.battery_available)
        self.assertEqual(len(game.lost_objectives), 4)
        game.meal(); game.next_cistern_day()
        revisit = game.start_expedition("Posto", [h1], "long")
        self.assertEqual(revisit.van_state, "away")

    def test_revisit_keeps_open_door_and_does_not_repeat_initial_spawn(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(110, STARTERS[:2], LINK_IDS[:2])
        first = game.start_expedition("Mercado", [hero])
        first.open_door(hero, 5)
        first.end_round(); game.return_expedition()
        game.meal(); game.next_cistern_day()
        later = game.start_expedition("Mercado", [hero])
        self.assertIn([1, 5], later.doors_open)
        self.assertEqual(len(later.enemies), 1)

    def test_regional_search_reward_enters_shelter_only_after_return(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(111, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero], "long")
        tactical.open_door(hero, 5); tactical.move(hero, 5)
        found = tactical.search(hero)
        self.assertTrue(found['carried'])
        self.assertEqual(game.delivered_objectives, [])
        before = {'Conserva':sum(game.cistern.food), 'Água':sum(game.cistern.water),
                  'Carne':sum(game.cistern.meat), 'Material':game.cistern.materials,
                  'Munição':game.cistern.ammo, 'Medicamento':game.cistern.medicine}
        tactical.end_round(); tactical.begin_round()
        tactical.move(hero, 1); tactical.end_round()
        game.return_expedition()
        self.assertIn(found['id'], game.delivered_objectives)
        after = {'Conserva':sum(game.cistern.food), 'Água':sum(game.cistern.water),
                 'Carne':sum(game.cistern.meat), 'Material':game.cistern.materials,
                 'Munição':game.cistern.ammo, 'Medicamento':game.cistern.medicine}
        for kind in before:
            unit = 4 if kind in ('Conserva','Água','Carne') else 1
            self.assertEqual(after[kind]-before[kind], unit*found['reward'].get(kind,0))
        self.assertEqual(len(game.site_states['mercado']['search_deck']), 5)

    def test_rescue_is_bound_to_map_zone_and_enters_shelter_on_return(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(112, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero])
        tactical.positions[hero] = 7  # O1 canônico do Mercado.
        receipt = tactical.rescue(hero, "ZC-MOR-0001", "welcome")
        self.assertEqual(receipt["event"], "rescue")
        self.assertEqual(game.cistern.rescue_history, {})
        tactical.positions[hero] = 1
        tactical.end_round()
        game.return_expedition()
        self.assertEqual(game.cistern.rescue_history["ZC-MOR-0001"], "welcome")

    def test_rescue_rejects_wrong_map_or_zone(self):
        hero = STARTERS[0]
        game = IntegratedCampaign.new(113, STARTERS[:2], LINK_IDS[:2])
        tactical = game.start_expedition("Mercado", [hero])
        with self.assertRaises(ValueError):
            tactical.rescue(hero, "ZC-MOR-0001", "welcome")
        tactical.positions[hero] = 7
        with self.assertRaises(ValueError):
            tactical.rescue(hero, "ZC-MOR-0002", "welcome")


if __name__ == "__main__":
    unittest.main()
