"""Contratos da edição 0.5, verificados nos componentes reais gerados."""
import unittest,json,sys
from pathlib import Path
import fitz
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'src'));O=P/'output/edicao-acabamento-v0.5'
class FinishTests(unittest.TestCase):
 def test_main_maps_have_no_low_resolution_raster(self):
  f=O/'ilustrada/06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf';self.assertTrue(f.exists(),'Gerar mapa completo 0.5')
  d=fitz.open(f);self.assertEqual(len(d),4)
  for page in d:
   for info in page.get_image_info():
    aa,bb,cc,dd,*_=info['transform'];ppi=min(info['width']/((aa*aa+bb*bb)**.5/72),info['height']/((cc*cc+dd*dd)**.5/72));self.assertGreaterEqual(ppi,149.9,'Nenhum fundo de 70 ppi ou detalhe ampliado')
 def test_selected_114_cards_preserved(self):
  m=json.loads((O/'ilustrada/00_LEIA_PRIMEIRO/manifesto.json').read_text());self.assertEqual(m['totals']['duplex'],{'initial':25,'supplement':33});self.assertEqual(m['totals']['manual'],{'initial':33,'supplement':39})
  src=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());self.assertEqual(len(set(src['initial_cards']+src['supplement_cards'])),114)
 def test_good_pawns_and_faces_preserved_byte_for_byte(self):
  for ed in ['ilustrada','economica']:
   for f in ['HEROIS_24_RECORTAR.pdf','INIMIGOS_VARIANTES_E01_E24_RECORTAR.pdf']:
    p=Path(ed)/'04_PERSONAGENS_E_INIMIGOS'/f;self.assertEqual((O/p).read_bytes(),(P/'output/edicao-fabricacao-v0.4'/p).read_bytes())
 def test_every_map_form_renders_including_accented_destinations(self):
  root=O/'ilustrada/08_EXTRAS_OPCIONAIS'
  for f in root.glob('*_M01_M04_LADO_A.pdf'):
   d=fitz.open(f);fitz.TOOLS.mupdf_warnings(reset=True)
   for page in d:page.get_pixmap(matrix=fitz.Matrix(.2,.2))
   self.assertNotIn('cannot find XObject',fitz.TOOLS.mupdf_warnings(),f.name)
 def test_delivered_maps_use_the_current_continuous_scene(self):
  for ed in ['ilustrada','economica']:
   root=O/ed
   paths=list((root/'08_EXTRAS_OPCIONAIS').glob('*_M01_M04_LADO_A.pdf'))+[root/'06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf']
   for path in paths:
    doc=fitz.open(path)
    for page in doc:
     self.assertTrue(any('ZZ05_' in item[1] for item in page.get_xobjects()),str(path)+' deve usar a planta global atual, não a antiga composição por zona')
 def test_atlas_crop_excludes_neighbor_fragments(self):
  from art_finish_maps import arrangement_crop
  crop=arrangement_crop(P/'assets/v0.5/mapa_mercado.png',1)
  self.assertGreater(crop[0],780,'A faixa da gôndola vizinha não pertence ao expositor de frutas')
 def test_structured_values_fit_the_card_safe_width(self):
  from reportlab.pdfbase import pdfmetrics
  import build_finish
  text='ACHADO: 1 carta(s) da reserva'
  # Actual delivered badge spans, not the paragraph-box estimate.
  for pdf in (O/'ilustrada/02_CARTAS_DUPLEX').glob('KIT_*_DUPLEX.pdf'):
   for page in list(fitz.open(pdf))[::2]:
    for block in page.get_text('dict')['blocks']:
     for line in block.get('lines',[]):
      for span in line['spans']:
       if span['text'].startswith(('ACHADO:','RESERVA:')):self.assertLessEqual(span['bbox'][2]-span['bbox'][0],53*72/25.4+.1)
 def test_only_food_and_water_are_labelled_as_portions(self):
  data=json.loads((P/'content/catalog.json').read_text());catalog={c['id']:c for c in data['cards']};m=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());mm=72/25.4
  for key,stem in [('initial_cards','KIT_INICIAL_1'),('supplement_cards','KIT_COMPLEMENTO_2')]:
   doc=fitz.open(O/'ilustrada/02_CARTAS_DUPLEX'/(stem+'_DUPLEX.pdf'))
   for i,id in enumerate(m[key]):
    card=catalog[id]
    if not card.get('reward') or next(iter(card['reward'])) in ['Conserva','Água','Carne']:continue
    n,k=divmod(i,9);r,col=divmod(k,3);box=fitz.Rect((8.5+65*col)*mm,(14.5+90*r)*mm,(71.5+65*col)*mm,(102.5+90*r)*mm)
    self.assertNotIn('porções',doc[2*n].get_text(clip=box),id+' não é alimento/água')
