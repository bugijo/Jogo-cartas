"""Regressão do baralho e dos recibos de Viagem da Cisterna 0.2."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from travel02 import Travel02, TravelContext


class Travel02Tests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
