"""Regressão do baralho e dos recibos de Viagem da Cisterna 0.2."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from travel02 import Travel02


class Travel02Tests(unittest.TestCase):
    def test_same_seed_reveals_same_cards_and_route_has_exact_legs(self):
        deck = ["ZC-VIA-0001", "ZC-VIA-0008", "ZC-VIA-0012", "ZC-VIA-0011"]
        left = Travel02.from_deck(deck, "long")
        right = Travel02.from_deck(deck, "long")
        self.assertEqual(left.reveal("outbound"), right.reveal("outbound"))
        self.assertEqual(left.reveal("outbound"), right.reveal("outbound"))
        self.assertEqual(left.segments, 2)
        self.assertEqual(left.remaining("return"), 2)

    def test_choice_card_stays_pending_until_explicit_resolution(self):
        trip = Travel02.from_deck(["ZC-VIA-0002"], "short")
        event = trip.reveal("outbound")
        self.assertEqual(event["name"], "Chuva ácida de fuligem")
        self.assertEqual(trip.pending_choices, [event["event_id"]])
        self.assertEqual(trip.resolve(event["event_id"], "water"),
                         {"water_loss": 1})
        self.assertEqual(trip.pending_choices, [])
        with self.assertRaises(ValueError):
            trip.resolve(event["event_id"], "fatigue")

    def test_ambush_is_a_pending_event_and_cannot_be_resolved_twice(self):
        trip = Travel02.from_deck(["ZC-VIA-0005"], "short")
        event = trip.reveal("outbound")
        self.assertTrue(event["ambush"])
        self.assertEqual(trip.pending_ambush, event["event_id"])
        self.assertEqual(trip.resolve_ambush(event["event_id"]),
                         {"map": "ZC-MOD-0001", "rounds_required": 1})
        self.assertIsNone(trip.pending_ambush)
        with self.assertRaises(ValueError):
            trip.resolve_ambush(event["event_id"])

    def test_snapshot_preserves_draws_pending_events_and_idempotence(self):
        trip = Travel02.from_deck(["ZC-VIA-0004", "ZC-VIA-0001"], "long")
        first = trip.reveal("outbound")
        saved = trip.snapshot()
        resumed = Travel02.from_snapshot(saved)
        self.assertEqual(resumed.snapshot(), saved)
        self.assertEqual(resumed.resolve(first["event_id"], "pressure"),
                         {"pressure": 1})
        with self.assertRaises(ValueError):
            resumed.resolve(first["event_id"], "pressure")
        resumed.reveal("outbound")
        with self.assertRaises(ValueError):
            resumed.reveal("outbound")

    def test_return_cannot_start_before_outbound_is_complete(self):
        trip = Travel02.from_deck(["ZC-VIA-0001", "ZC-VIA-0001"], "long")
        trip.reveal("outbound")
        with self.assertRaises(ValueError):
            trip.reveal("return")


if __name__ == "__main__":
    unittest.main()
