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


if __name__ == "__main__":
    unittest.main()
