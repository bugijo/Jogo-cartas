import unittest,itertools,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rules_engine import consume, family_setup, intake, intent, reserve_project, advance, pending_pressure, apply_deprivation
class RulesTests(unittest.TestCase):
 def test_all_initial_link_combinations_fit(self):
  links=[(0,0)]*4+[(1,0)]*4+[(1,0)]*2+[(0,1),(1,1)]
  for h in range(2,7):
   for combo in itertools.combinations(links,h):
    s=family_setup(h,combo)
    self.assertLessEqual(s['humans'],s['capacity']);self.assertGreaterEqual(s['food'],2*s['consumers'])
 def test_portions_and_expiry(self):
  self.assertEqual(consume(16,4,9),(11,0,0))
  self.assertEqual(consume(16,4,1),(16,0,3))
  self.assertEqual(consume(0,4,9),(0,5,0))
 def test_intake_and_deadline(self):
  self.assertEqual(intake(8,8,2,1,2),'temporario')
  self.assertEqual(intake(8,8,3,1,1),'sem_capacidade')
  self.assertEqual(intake(8,8,2,1,3),'superlotacao')
  self.assertEqual(intake(8,10,2,1,4),'permanente')
 def test_intent_protection_current_night(self):
  self.assertEqual(intent('Oportunista',False,11,0),(7,0,'parte'))
  self.assertEqual(intent('Oportunista',True,11,0),(11,0,'parte'))
  self.assertEqual(intent('Infiltrado',False,11,2),(11,3,'parte'))
  self.assertEqual(intent('Solidário',False,11,0),(11,0,'fica'))
 def test_project_stock_conservation(self):
  stock={'Material':3,'Lona':1};left,paid=reserve_project(stock,{'Material':2,'Lona':1})
  self.assertEqual(stock,{'Material':3,'Lona':1});self.assertEqual(left,{'Material':1,'Lona':0})
  self.assertEqual(sum(left.values())+sum(paid.values()),sum(stock.values()))
  with self.assertRaises(ValueError):reserve_project(stock,{'Material':4})
 def test_night_return_and_overrun(self):
  self.assertEqual(advance(8,2),(10,2,False));self.assertEqual(advance(9,2),(11,1,True))
  self.assertEqual(advance(6,2),(8,0,False))
 def test_pressure_queue_no_duplicate_at_three(self):
  self.assertEqual(pending_pressure(2,1,[]),(3,['pressao']))
  self.assertEqual(pending_pressure(3,1,['pressao']),(3,['pressao']))
 def test_deprivation_reset_and_collapse_threshold(self):
  self.assertEqual(apply_deprivation(1,False,True),(2,1))
  self.assertEqual(apply_deprivation(2,True,True),(0,0))
if __name__=='__main__':unittest.main()

class CampaignRegressionTests(unittest.TestCase):
 def test_ambush_cannot_be_skipped_from_entry(self):
  import json
  p=Path(__file__).resolve().parents[1]
  data=json.loads((p/'content/catalog.json').read_text())
  ambush=next(c for c in data['cards'] if c['name']=='Emboscada')
  minimum=ambush.get('minimum_rounds',0)
  self.assertFalse(0>=minimum,'Sair na chegada não pode evitar a rodada de emboscada')
  self.assertTrue(1>=minimum,'Após uma rodada a saída pode abrir se estiver livre')
