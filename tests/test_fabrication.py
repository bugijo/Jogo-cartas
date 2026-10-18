"""Contratos físicos: mudanças de pareamento ou tamanho devem quebrar estes testes."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
class FabricationTests(unittest.TestCase):
 def contract(self):
  self.assertTrue((Path(__file__).resolve().parents[1]/'src/production_geometry.py').exists(),'Falta contrato de fabricação')
  import production_geometry as p
  return p
 def test_manual_pairs_do_not_inherit_duplex_mirroring(self):
  p=self.contract()
  self.assertEqual(p.card_cell(0,'duplex_back'),(0,2))
  self.assertEqual(p.card_cell(0,'manual_back'),(0,0))
  self.assertEqual(p.card_cell(8,'manual_back'),(2,2))
 def test_58_sheet_compatibility_and_manual_alternative(self):
  p=self.contract();self.assertEqual(p.sheet_totals('duplex'),(25,33,58));self.assertEqual(p.sheet_totals('manual'),(33,39,72))
 def test_real_cards_fit_four_slots_without_overlap(self):
  p=self.contract();slots=p.panel_slots();self.assertEqual(len(slots),4)
  for x,y,w,h in slots:self.assertGreaterEqual(w,66);self.assertGreaterEqual(h,92);self.assertLessEqual(x+w,554);self.assertLessEqual(y+h,190)
  self.assertTrue(all(a[0]+a[2]<=b[0] for a,b in zip(slots,slots[1:])))
 def test_pawn_bases_fit_one_zone_without_reducing_enemy_cap(self):
  p=self.contract();self.assertEqual(p.MAX_ENEMIES,24);self.assertEqual(p.pawn_capacity(138.5,95),42);self.assertGreaterEqual(p.pawn_capacity(138.5,95),24+6)
 def test_only_one_enemy_variant_per_existing_id(self):
  p=self.contract();self.assertEqual(len(p.enemy_variants()),72);self.assertEqual(len({v['id'] for v in p.enemy_variants()}),24)
 def test_editable_archive_includes_proof_dependencies(self):
  import zipfile
  root=Path(__file__).resolve().parents[1]
  archive=root/'dist/ZZ_04_FONTES_EDITAVEIS.zip'
  if not archive.exists():self.skipTest('Verificação de distribuição: gerar pacotes primeiro')
  with zipfile.ZipFile(archive) as z:
   self.assertIn('output/edicao-ilustrada-v0.3/ilustrada/extras/mapa_mercado.pdf',z.namelist())
   build=z.read('src/build_fabrication.py').decode();self.assertIn('sample()',build[build.index('def full_build():'):])
 def test_manual_calibration_marks_can_align_back_to_back(self):
  import fitz
  root=Path(__file__).resolve().parents[1];f=root/'output/edicao-fabricacao-v0.4/ilustrada/03_CARTAS_RECORTAR_E_COLAR/CALIBRACAO_COLAGEM.pdf'
  if not f.exists():self.skipTest('Gerar PDFs de fabricação primeiro')
  d=fitz.open(f);center=(35+63/2)*72/25.4
  for page in d:
   spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] if s['text'] in ['A','B']]
   self.assertEqual(len(spans),2)
   for s in spans:self.assertAlmostEqual((s['bbox'][0]+s['bbox'][2])/2,center,delta=.5)
