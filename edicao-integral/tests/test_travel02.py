"""Regressão do baralho e dos recibos de Viagem da Cisterna 0.2."""
import sys
import unittest
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from travel02 import CARDS, Travel02, TravelContext, TravelShoe02


class Travel02Tests(unittest.TestCase):
    @staticmethod
    def _resolve_event(trip, event):
        context = TravelContext(food=10, water=10, materials=10,
                                fatigue={"h": 0}, eligible_dog_adoption=True)
        if event["ambush"]:
            trip.complete_ambush(event["event_id"], SimpleNamespace(
                returned=True, failed=False, round_no=1, completed_rounds=1,
                positions={"h": 1}, enemies=[]))
        elif trip.pending_choices:
            choices = {"ZC-VIA-0002": "fatigue",
                       "ZC-VIA-0004": "pressure",
                       "ZC-VIA-0006": "decline",
                       "ZC-VIA-0009": "decline"}
            trip.apply(event["event_id"], context,
                       choices.get(event["card_id"], "decline"))
        else:
            trip.apply(event["event_id"], context)

    @staticmethod
    def _finish_first_card(shoe):
        trip = Travel02.from_deck(shoe.prepare_trip(1), "short")
        event = trip.reveal("outbound")
        Travel02Tests._resolve_event(trip, event)
        shoe.finish_trip(trip)
        return event["card_id"], trip

    def test_campaign_shoe_discards_only_revealed_cards_and_rejects_double_commit(self):
        shoe = TravelShoe02.new(77)
        card_id, trip = self._finish_first_card(shoe)
        self.assertEqual(len(shoe.deck), len(CARDS) - 1)
        self.assertEqual(shoe.discard, [card_id])
        with self.assertRaises(ValueError):
            shoe.finish_trip(trip)

    def test_via_0003_skip_pays_return_segment_without_drawing_shoe_card(self):
        shoe = TravelShoe02.new(79)
        shoe.deck = ["ZC-VIA-0003"] + [card for card in shoe.deck
                                       if card != "ZC-VIA-0003"]
        trip = Travel02.from_deck(shoe.prepare_trip(2), "short")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h": 0})
        outbound = trip.reveal("outbound")
        trip.apply(outbound["event_id"], context)
        skipped = trip.reveal("return", context)
        self.assertTrue(skipped["skipped"])
        self.assertEqual(trip.index, 1)
        shoe.finish_trip(trip)
        self.assertEqual(shoe.discard, ["ZC-VIA-0003"])

    def test_campaign_shoe_reshuffles_discard_reproducibly_and_round_trips(self):
        left = TravelShoe02.new(78)
        right = TravelShoe02.from_snapshot(left.snapshot())
        # Consume the whole shoe in one-card trips, keeping the same explicit
        # card sequence used by each shoe.
        while left.deck:
            for shoe in (left, right):
                self._finish_first_card(shoe)
        left_plan = left.prepare_trip(1)
        right_plan = right.prepare_trip(1)
        self.assertEqual(left_plan, right_plan)
        self.assertEqual(len(left_plan), len(CARDS))
        self.assertEqual(left.deck, [])
        resumed = TravelShoe02.from_snapshot(left.snapshot())
        self.assertEqual(resumed.snapshot(), left.snapshot())

    def test_long_trip_does_not_shuffle_discard_before_draw_pile_is_empty(self):
        shoe = TravelShoe02.new(80)
        remaining = ["ZC-VIA-0001", "ZC-VIA-0007"]
        shoe.deck = remaining.copy()
        shoe.discard = [card for card in CARDS if card not in set(remaining)]
        before = shoe.snapshot()
        planned = shoe.prepare_trip(4)
        self.assertEqual(planned[:2], remaining)
        self.assertEqual(shoe.snapshot(), before)
        trip = Travel02.from_deck(planned, "long")
        for _ in range(2):
            event = trip.reveal("outbound")
            self._resolve_event(trip, event)
        shoe.finish_trip(trip)
        self.assertEqual(shoe.deck, [])
        self.assertEqual(shoe.reshuffles, 0)
        self.assertEqual(shoe.discard[:2], before["discard"][:2])

    def test_long_trip_reshuffles_discard_only_when_it_draws_past_empty_shoe(self):
        shoe = TravelShoe02.new(81)
        remaining = ["ZC-VIA-0001", "ZC-VIA-0007"]
        shoe.deck = remaining.copy()
        shoe.discard = [card for card in CARDS if card not in set(remaining)]
        trip = Travel02.from_deck(shoe.prepare_trip(4), "long")
        events = []
        for direction in ("outbound", "outbound", "return"):
            event = trip.reveal(direction)
            events.append(event["card_id"])
            self._resolve_event(trip, event)
        shoe.finish_trip(trip)
        self.assertEqual(shoe.reshuffles, 1)
        self.assertEqual(shoe.discard, events)
        self.assertEqual(len(shoe.deck), len(CARDS) - 3)
        restored = TravelShoe02.from_snapshot(shoe.snapshot())
        self.assertEqual(restored.snapshot(), shoe.snapshot())

    def test_same_seed_reveals_same_cards_and_route_has_exact_legs(self):
        deck = ["ZC-VIA-0001", "ZC-VIA-0008", "ZC-VIA-0012", "ZC-VIA-0011"]
        left = Travel02.from_deck(deck, "long")
        right = Travel02.from_deck(deck, "long")
        context=TravelContext(food=0,water=0,materials=0,fatigue={"h":0})
        for _ in range(2):
            a=left.reveal("outbound"); b=right.reveal("outbound")
            self.assertEqual(a,b)
            left.apply(a['event_id'],context); right.apply(b['event_id'],context)
        self.assertEqual(left.segments, 2)
        self.assertEqual(left.remaining("return"), 2)

    def test_choice_card_stays_pending_until_explicit_resolution(self):
        trip = Travel02.from_deck(["ZC-VIA-0002"], "short")
        event = trip.reveal("outbound")
        self.assertEqual(event["name"], "Chuva ácida de fuligem")
        self.assertEqual(trip.pending_choices, [event["event_id"]])
        context = TravelContext(food=0, water=1, materials=0,
                                fatigue={"h1": 0})
        self.assertEqual(trip.resolve(event["event_id"], "water", context),
                         {"water_loss": 1})
        self.assertEqual(context.water, 0)
        self.assertEqual(trip.pending_choices, [])
        with self.assertRaises(ValueError):
            trip.resolve(event["event_id"], "fatigue", context)

    def test_ambush_is_a_pending_event_and_cannot_be_resolved_twice(self):
        trip = Travel02.from_deck(["ZC-VIA-0005"], "short")
        event = trip.reveal("outbound")
        self.assertTrue(event["ambush"])
        self.assertEqual(trip.pending_ambush, event["event_id"])
        self.assertEqual(trip.resolve_ambush(event["event_id"]),
                         {"map": "ZC-MOD-0001", "rounds_required": 1})
        with self.assertRaises(ValueError):
            trip.reveal("outbound")

    def test_snapshot_preserves_draws_pending_events_and_idempotence(self):
        trip = Travel02.from_deck(["ZC-VIA-0004", "ZC-VIA-0001"], "long")
        first = trip.reveal("outbound")
        saved = trip.snapshot()
        resumed = Travel02.from_snapshot(saved)
        self.assertEqual(resumed.snapshot(), saved)
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h1": 0})
        self.assertEqual(resumed.resolve(first["event_id"], "pressure",context),
                         {"pressure": 1})
        with self.assertRaises(ValueError):
            resumed.resolve(first["event_id"], "pressure",context)
        resumed.reveal("outbound")
        with self.assertRaises(ValueError):
            resumed.reveal("outbound")

    def test_snapshot_rejects_impossible_ambush_duration(self):
        trip = Travel02.from_deck(["ZC-VIA-0005"], "short")
        event = trip.reveal("outbound")
        snapshot = trip.snapshot()
        snapshot["pending_resolution"] = None
        snapshot["pending_ambush"] = None
        snapshot["pending_choices"] = []
        snapshot["resolved"][event["event_id"]] = {"ambush": {
            "map": "ZC-MOD-0001", "rounds": 11, "returned": True}}
        with self.assertRaisesRegex(ValueError, "Saída segura da Emboscada"):
            Travel02.from_snapshot(snapshot)

    def test_return_cannot_start_before_outbound_is_complete(self):
        trip = Travel02.from_deck(["ZC-VIA-0001", "ZC-VIA-0001"], "long")
        trip.reveal("outbound")
        with self.assertRaises(ValueError):
            trip.reveal("return")

    def test_every_revealed_card_must_be_applied_before_next_segment(self):
        trip=Travel02.from_deck(["ZC-VIA-0007","ZC-VIA-0001"],"long")
        event=trip.reveal("outbound")
        with self.assertRaises(ValueError): trip.reveal("outbound")
        context=TravelContext(food=0,water=0,materials=0,fatigue={"h1":0})
        self.assertEqual(trip.apply(event["event_id"],context),{"pressure":1})
        next_event=trip.reveal("outbound")
        self.assertEqual(next_event["card_id"],"ZC-VIA-0001")

    def test_directional_effects_are_explicit_and_applied_once(self):
        trip = Travel02.from_deck(["ZC-VIA-0003", "ZC-VIA-0010",
                                   "ZC-VIA-0011"], "long")
        context = TravelContext(food=2, water=2, materials=1,
                                fatigue={"h1": 0})
        first = trip.reveal("outbound")
        self.assertEqual(trip.apply(first["event_id"], context),
                         {"skip_return_card": 1})
        second = trip.reveal("outbound")
        self.assertEqual(trip.apply(second["event_id"], context),
                         {"material_drop": 1})
        with self.assertRaises(ValueError):
            trip.apply(second["event_id"], context)

    def test_effect_refuses_missing_carried_resource_without_partial_change(self):
        trip = Travel02.from_deck(["ZC-VIA-0004"], "short")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h1": 0})
        event = trip.reveal("outbound")
        before = context.snapshot()
        with self.assertRaises(ValueError):
            trip.apply(event["event_id"], context, "material")
        self.assertEqual(context.snapshot(), before)

    def test_ferragens_outbound_requires_and_drops_carried_material(self):
        trip = Travel02.from_deck(["ZC-VIA-0010"], "short")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h1": 0})
        event = trip.reveal("outbound")
        before = context.snapshot()
        with self.assertRaises(ValueError):
            trip.apply(event["event_id"], context)
        self.assertEqual(context.snapshot(), before)
        context.materials = 1
        self.assertEqual(trip.apply(event["event_id"], context),
                         {"material_drop": 1})
        self.assertEqual(context.materials, 0)

    def test_road_signal_skips_one_return_card_but_still_uses_the_segment(self):
        trip = Travel02.from_deck(["ZC-VIA-0003", "ZC-VIA-0001",
                                   "ZC-VIA-0012"], "long")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h1": 0})
        for _ in range(2):
            event = trip.reveal("outbound")
            trip.apply(event["event_id"], context)
        first_return = trip.reveal("return", context)
        self.assertTrue(first_return["skipped"])
        self.assertEqual(trip.index, 2)
        self.assertEqual(trip.return_segments, 1)
        self.assertEqual(context.skip_return_card, 0)

    def test_lost_dog_requires_eligible_family_and_adds_one_dog(self):
        trip = Travel02.from_deck(["ZC-VIA-0009"], "short")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h1": 0})
        event = trip.reveal("outbound")
        with self.assertRaises(ValueError):
            trip.apply(event["event_id"], context, "accept")
        self.assertEqual(context.dogs, 0)
        context.eligible_dog_adoption = True
        self.assertEqual(trip.apply(event["event_id"], context, "accept"),
                         {"dog": 1})
        self.assertEqual(context.dogs, 1)


    def test_night_extra_is_a_second_occurrence_for_same_paid_segment(self):
        trip = Travel02.from_deck([
            "ZC-VIA-0001", "ZC-VIA-0008", "ZC-VIA-0001"], "short")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h": 0})
        normal = trip.reveal("outbound")
        trip.apply(normal["event_id"], context)
        extra = trip.reveal_night_extra("outbound")
        self.assertEqual(extra["card_id"], "ZC-VIA-0008")
        self.assertEqual(extra["segment_event_id"], normal["event_id"])
        self.assertTrue(extra["extra"])
        self.assertEqual(trip.outbound_segments, 1)
        self.assertEqual(trip.index, 2)
        trip.apply(extra["event_id"], context)
        self.assertTrue(context.route_known)
        with self.assertRaisesRegex(ValueError, "extra noturna já revelada"):
            trip.reveal_night_extra("outbound")
        restored = Travel02.from_snapshot(trip.snapshot())
        self.assertEqual(restored.snapshot(), trip.snapshot())

    def test_night_extra_pending_occurrence_survives_save_and_blocks_next_segment(self):
        trip = Travel02.from_deck([
            "ZC-VIA-0001", "ZC-VIA-0002", "ZC-VIA-0001"], "long")
        context = TravelContext(food=0, water=1, materials=0,
                                fatigue={"h": 0})
        normal = trip.reveal("outbound")
        trip.apply(normal["event_id"], context)
        extra = trip.reveal_night_extra("outbound")
        saved = Travel02.from_snapshot(trip.snapshot())
        with self.assertRaises(ValueError):
            saved.reveal("outbound")
        self.assertEqual(saved.resolve(extra["event_id"], "water", context),
                         {"water_loss": 1})
        next_segment = saved.reveal("outbound")
        self.assertEqual(next_segment["event_id"], "travel-outbound-002")

    def test_fatigue_choice_cannot_raise_beyond_canonical_three(self):
        trip = Travel02.from_deck(["ZC-VIA-0002"], "short")
        event = trip.reveal("outbound")
        context = TravelContext(food=0, water=0, materials=0,
                                fatigue={"h": 3})
        before = context.snapshot()
        effect = trip.apply(event["event_id"], context, "fatigue")
        self.assertEqual(effect, {"fatigue": 1})
        self.assertEqual(context.fatigue["h"], 3)
        self.assertEqual(context.snapshot(), before)
        self.assertIn(event["event_id"], trip.resolved)


if __name__ == "__main__":
    unittest.main()
