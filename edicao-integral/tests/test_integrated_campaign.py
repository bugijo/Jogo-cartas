"""A camada integrada permanece fechada até portar a expedição 0.2."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integrated_campaign import IntegratedCampaign, LINK_IDS, STARTERS, PART_MISSIONS


class IntegratedCampaignTests(unittest.TestCase):
    def test_mission_references_match_canonical_locations(self):
        self.assertEqual(PART_MISSIONS["Conexões"]["location"], "EXP-LOC-03")
        self.assertEqual(PART_MISSIONS["Bomba"]["location"], "EXP-LOC-05")
        self.assertEqual(PART_MISSIONS["Membrana"]["location"], "EXP-LOC-05")

    def test_part_requires_tactical_receipt(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(NotImplementedError):
            game.collect_part("Conexões")
        self.assertEqual(game.cistern.parts, {})
        self.assertEqual(game.cistern.clock, 0)
        self.assertEqual(game.decisions, {})

    def test_public_expedition_entry_cannot_skip_travel(self):
        game=IntegratedCampaign.new(40,STARTERS[:2],LINK_IDS[:2])
        before=(game.cistern.clock,game.tactical,game.travel,game.travel_request.copy()
                if game.travel_request else None)
        with self.assertRaisesRegex(ValueError,'start_travel'):
            game.start_expedition('Mercado',[STARTERS[0]])
        self.assertEqual((game.cistern.clock,game.tactical,game.travel,game.travel_request),before)

    def test_candidate_cannot_drop_state_during_transition(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        game.cistern.filter_completed = True
        game.cistern.filter_active = True
        game.cistern.day = game.cistern.meal_day = 5
        with self.assertRaises((ValueError,NotImplementedError)):
            game.complete_cistern()
        self.assertIsNone(game.world)
        self.assertEqual(game.rewards, [])

    def test_complete_cistern_requires_legal_piece_receipts(self):
        game = IntegratedCampaign.new(42, STARTERS[:2], LINK_IDS[:2])
        game.cistern.result = 'candidate_victory'
        game.cistern.filter_active = True
        game.cistern.health = game.cistern.morale = 1
        with self.assertRaises((ValueError, NotImplementedError)):
            game.complete_cistern()
        self.assertEqual(game.cistern.result, 'candidate_victory')

    def test_candidate_flags_in_a_day_one_save_cannot_certify_cistern(self):
        game=IntegratedCampaign.new(991,STARTERS[:2],LINK_IDS[:2])
        game.cistern.result='candidate_victory'
        game.cistern.filter_completed=True
        game.cistern.filter_active=True
        game.cistern.parts={'Conexões':1,'Bomba':1,'Membrana':1}
        game.delivered_objectives=['Oficina:Conexões','Estação:Bomba','Estação:Membrana']
        with self.assertRaises(ValueError):
            game.complete_cistern()
        self.assertEqual(game.cistern.result,'candidate_victory')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'forged.json';game.save(path)
            with self.assertRaises(ValueError):IntegratedCampaign.load(path)

    def test_save_resume_preserves_partial_campaign(self):
        game = IntegratedCampaign.new(41, STARTERS[:2], LINK_IDS[:2])
        game.decide("rota_dia_1", "mercado")
        game.cistern.meal()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            game.save(path)
            resumed = IntegratedCampaign.load(path)
        self.assertEqual(resumed.decisions, game.decisions)
        self.assertEqual(resumed.cistern.food, game.cistern.food)
        self.assertEqual(resumed.cistern.water, game.cistern.water)
        self.assertIsNone(resumed.world)

    def test_legacy_campaign_save_records_event_gap_and_blocks_chapter_certification(self):
        import json
        game=IntegratedCampaign.new(992,STARTERS[:2],LINK_IDS[:2])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'legacy-campaign.json'
            game.save(path)
            payload=json.loads(path.read_text(encoding='utf-8'))
            state=payload['cistern']
            for key in ('event_queue','event_history','legacy_skipped_events',
                        'legacy_event_gap'):
                state.pop(key,None)
            state['day']=3;state['meal_day']=2;state['pressure']=0
            path.write_text(json.dumps(payload),encoding='utf-8')
            resumed=IntegratedCampaign.load(path)
        self.assertTrue(resumed.cistern.legacy_event_gap)
        self.assertEqual(resumed.cistern.legacy_skipped_events,
                         ['ZC-EVE-0001','ZC-EVE-0002'])
        self.assertEqual(resumed.cistern.pending_sieges,['Barulho no vale'])

    def test_fixture_emergency_drops_unique_part_and_next_map_delivers_same_piece(self):
        game=IntegratedCampaign.new(41,STARTERS[:2],LINK_IDS[:2])
        first=game._start_tactical_fixture('Oficina',[STARTERS[0]])
        first.positions[STARTERS[0]]=7
        first.pickup_part(STARTERS[0],'Conexões')
        game.emergency_return()
        key='Oficina:Conexões'
        self.assertIn(key,game.lost_objectives)
        self.assertEqual(game.site_states['oficina']['part_ground'],[
            {'part':'Conexões','destination':'oficina','zone':7,'load':1}])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'campaign.json'
            game.save(path)
            game=IntegratedCampaign.load(path)
        self.assertIn(key,game.lost_objectives)
        game.meal(); game.next_cistern_day()
        second=game._start_tactical_fixture('Oficina',[STARTERS[1]])
        second.positions[STARTERS[1]]=7
        second.pickup_part(STARTERS[1],'Conexões')
        with self.assertRaises(ValueError): second.pickup_part(STARTERS[1],'Conexões')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'campaign-after-recovery.json'
            game.save(path)
            game=IntegratedCampaign.load(path)
        second=game.tactical
        self.assertEqual(second.carried[STARTERS[1]],['Conexões'])
        with self.assertRaises(ValueError): second.pickup_part(STARTERS[1],'Conexões')
        second.positions[STARTERS[1]]=second.map['exit']
        second.enemies.clear(); second.end_round(); second.finish()
        receipts=game.return_expedition()
        self.assertEqual([r['event'] for r in receipts],['recover_part'])
        self.assertEqual(game.cistern.parts,{'Conexões':2})  # dia da entrega
        self.assertEqual(game.delivered_objectives.count(key),1)

    def test_terminal_states_persist(self):
        game = IntegratedCampaign.new(2, STARTERS[:2], LINK_IDS[:2])
        with self.assertRaises(ValueError):
            game.final_defense()
        game.mark_impossible("sem_rota_de_progresso")
        self.assertEqual(game.status, "IMPOSSIBLE")
        with self.assertRaises(ValueError):
            game.advance_day()


if __name__ == "__main__":
    unittest.main()
