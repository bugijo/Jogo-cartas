"""Contratos da edição 0.5, verificados nos componentes reais gerados."""
import unittest,json
from pathlib import Path
import fitz
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-acabamento-v0.5'
class FinishTests(unittest.TestCase):
 def test_main_maps_have_no_low_resolution_raster(self):
  f=O/'ilustrada/06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf';self.assertTrue(f.exists(),'Gerar mapa completo 0.5')
  d=fitz.open(f);self.assertEqual(len(d),4)
  for page in d:self.assertEqual(page.get_images(full=True),[],'O mapa principal deve ser vetorial; nenhum fundo de 70 ppi')
 def test_selected_114_cards_preserved(self):
  m=json.loads((O/'ilustrada/00_LEIA_PRIMEIRO/manifesto.json').read_text());self.assertEqual(m['totals']['duplex'],{'initial':25,'supplement':33});self.assertEqual(m['totals']['manual'],{'initial':33,'supplement':39})
  src=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());self.assertEqual(len(set(src['initial_cards']+src['supplement_cards'])),114)
 def test_good_pawns_and_faces_preserved_byte_for_byte(self):
  for ed in ['ilustrada','economica']:
   for f in ['HEROIS_24_RECORTAR.pdf','INIMIGOS_VARIANTES_E01_E24_RECORTAR.pdf']:
    p=Path(ed)/'04_PERSONAGENS_E_INIMIGOS'/f;self.assertEqual((O/p).read_bytes(),(P/'output/edicao-fabricacao-v0.4'/p).read_bytes())
