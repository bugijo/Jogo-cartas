import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
class RevisionTests(unittest.TestCase):
 def test_blocked_doors_are_printed_doors(self):
  d=json.loads((P/'content/catalog.json').read_text())
  for m in d['maps']:
   self.assertTrue({tuple(e) for e in m['blocked']} <= {tuple(e) for e in m['doors']},m['name'])
 def test_ten_professions_are_consolidated_with_provenance(self):
  d=json.loads((P/'content/catalog.json').read_text())
  for h in d['heroes'][:10]:
   self.assertIn('consolidada',h['profession_status'])
   self.assertEqual(h['profession_origin'],'decisão editorial; fonte 2.0 não especifica')
if __name__=='__main__':unittest.main()

class StarterContentTests(unittest.TestCase):
 def test_ambush_uses_actual_entry_module_zones(self):
  d=json.loads((P/'content/catalog.json').read_text());a=next(c for c in d['cards'] if c['name']=='Emboscada')
  self.assertEqual(set(a['encounter_zones']),{1,2,5,6});self.assertIn(a['spawn'],a['encounter_zones']);self.assertIn(a['entry'],a['encounter_zones']);self.assertEqual(a['closed_door'],[1,5])
 def test_unique_filter_parts_can_be_recovered(self):
  d=json.loads((P/'content/catalog.json').read_text());parts=[c for c in d['cards'] if c.get('unique_campaign')]
  self.assertEqual({c['name'] for c in parts},{'Conexões','Bateria','Bomba','Membrana'})
  self.assertTrue(all(c['on_emergency']=='origin_floor' for c in parts))
 def test_five_days_replay_respects_cargo_clock_and_work(self):
  import sys
  sys.path.insert(0,str(P/'src'))
  from review_five_days import run
  r=run();self.assertEqual([e['segments'] for e in r['expeditions']],[7,8,9]);self.assertEqual(r['days'][-1]['filter_work'],4);self.assertEqual(r['days'][-1]['materials'],1)
  self.assertTrue(all(max(x['loads'].values())<=4 for x in r['round_log']))
  self.assertEqual(r['days'][2]['fatigue'],1);self.assertEqual(r['days'][3]['fatigue'],0)
