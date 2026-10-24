import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from horde_deck02 import CARD_IDS, HordeDeck02


class HordeDeck02Tests(unittest.TestCase):
    def test_draw_discard_and_reshuffle_are_seeded_and_persistent(self):
        left = HordeDeck02.new(712)
        right = HordeDeck02.new(712)
        self.assertEqual(left, right)
        drawn = []
        for _ in range(len(CARD_IDS)):
            card, left = HordeDeck02.draw(left)
            drawn.append(card)
        self.assertEqual(set(drawn), set(CARD_IDS))
        self.assertEqual(left["draw_pile"], [])
        saved = HordeDeck02.validate(left)
        card, after = HordeDeck02.draw(saved)
        expected, right = HordeDeck02.draw(right)
        for _ in range(len(CARD_IDS) - 1):
            expected, right = HordeDeck02.draw(right)
        expected, right = HordeDeck02.draw(right)
        self.assertEqual(card, expected)
        self.assertEqual(after, right)
        self.assertEqual(after["reshuffles"], 1)

    def test_duplicate_or_missing_card_in_snapshot_is_rejected(self):
        state = HordeDeck02.new(5)
        state["draw_pile"][0] = state["draw_pile"][1]
        with self.assertRaises(ValueError):
            HordeDeck02.validate(state)


if __name__ == "__main__":
    unittest.main()
