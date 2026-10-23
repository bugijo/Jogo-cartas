"""Peças só são entregues por retirada e retorno no mapa canônico."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrated_campaign import IntegratedCampaign, STARTERS, LINK_IDS


class IntegratedTacticalTests(unittest.TestCase):
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
        tactical.end_round(); tactical.begin_round()
        tactical.move(hero, 3); tactical.move(hero, 2); tactical.move(hero, 1)
        tactical.end_round()
        delivery = game.return_expedition()
        self.assertEqual([x["part"] for x in delivery], ["Conexões"])
        self.assertEqual(game.cistern.parts["Conexões"], 1)
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


if __name__ == "__main__":
    unittest.main()
