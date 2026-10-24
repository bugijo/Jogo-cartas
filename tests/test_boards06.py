"""Contratos físicos e de preservação, não julgamento artístico."""
import unittest,json,hashlib,sys
from pathlib import Path
import fitz
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-tabuleiros-v0.6';sys.path.insert(0,str(P/'src'))
class Boards06(unittest.TestCase):
 def test_frozen_sources_and_previous_edition_untouched(self):
  for name,h in json.loads((P/'content/production/baseline_0.6.json').read_text()).items():self.assertEqual(hashlib.sha256((P/name).read_bytes()).hexdigest(),h,name)
 def test_functional_reference_exactly_matches_catalog(self):
  data=json.loads((P/'content/production/geometry_0.6.json').read_text());catalog=json.loads((P/'content/catalog.json').read_text())['maps'];self.assertEqual(data,catalog)
  for m in data:self.assertEqual((len(m['zones']),len(m['edges']),len(m['doors'])),(16,21,5))
 def test_maps_are_new_four_a4_pages_without_renderer_errors(self):
  import build_boards06 as b
  for ed in ['ilustrada','economica']:
   for name in b.CHANGED:
    doc=fitz.open(O/ed/name);self.assertEqual(len(doc),5 if name.endswith('DEMAIS_DESTINOS_MONTAGENS.pdf') else 1 if name.endswith('MERCADO_MONTAGEM.pdf') else 4)
    for page in doc:
     self.assertAlmostEqual(page.rect.width,297*72/25.4,places=2);self.assertAlmostEqual(page.rect.height,210*72/25.4,places=2)
     self.assertTrue(any('ZZ06_' in x[1] for x in page.get_xobjects()),name+' contém a cena nova')
     fitz.TOOLS.mupdf_warnings(reset=True);page.get_pixmap(matrix=fitz.Matrix(.15,.15));self.assertEqual(fitz.TOOLS.mupdf_warnings(),'')
 def test_preserved_components_are_byte_identical(self):
  import build_boards06 as b
  for ed in ['ilustrada','economica']:
   for path in (b.BASE/ed).rglob('*.pdf'):
    rel=str(path.relative_to(b.BASE/ed))
    if rel not in b.CHANGED:self.assertEqual(path.read_bytes(),(O/ed/rel).read_bytes(),rel)
 def test_actual_map_raster_density_not_worse_than_05(self):
  for ed in ['ilustrada','economica']:
   files=list((O/ed/'08_EXTRAS_OPCIONAIS').glob('*_M01_M04_LADO_A.pdf'))+[O/ed/'06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf']
   self.assertEqual(len(files),7)
   for path in files:
    for page in fitz.open(path):
     for im in page.get_image_info():
      a,b,c,d,*_=im['transform'];ppi=min(im['width']/(a*a+b*b)**.5*72,im['height']/(c*c+d*d)**.5*72);self.assertGreaterEqual(ppi,211.25,str(path))
 def test_fifty_eight_and_seventy_two_sheets_still_hold(self):
  for ed in ['ilustrada','economica']:
   m=json.loads((O/ed/'00_LEIA_PRIMEIRO/manifesto.json').read_text())
   for method,n in [('duplex',58),('manual',72)]:self.assertEqual(sum(e['sheets'] for e in m['files'] if not e['optional'] and e['method'] in ['both',method]),n)
 def test_the_actual_pdf_shows_every_canonical_blocked_door(self):
  import build_boards06 as b
  mm=72/25.4
  for ed in ['ilustrada','economica']:
   for m in b.MAPS:
    doc=fitz.open(O/'fontes_tabuleiros'/ed/(b.KEYS[m['name']]+'.pdf'))
    lines=[it for d in doc[0].get_drawings() for it in d['items'] if it[0]=='l']
    for s in b.segments(m):
     if not s['blocked']:continue
     cx,cy=s['center'];x,y=cx*mm,(380-cy)*mm
     diagonals=[v for v in lines if abs((v[1].x+v[2].x)/2-x)<.1 and abs((v[1].y+v[2].y)/2-y)<.1 and abs(abs(v[1].x-v[2].x)-6.4*mm)<.1 and abs(abs(v[1].y-v[2].y)-6.4*mm)<.1]
     self.assertEqual(len(diagonals),2,m['name']+str(s['key']))

 def test_receiving_crop_does_not_include_neighbor_fragment(self):
  import board_art06 as art
  box,size=art.crop('assets/v0.6/mercado_topo.png',3)
  self.assertGreater(box[1],520,'O fragmento de outro quadrante não pertence ao recebimento')
 def test_real_component_footprints_fit_without_changing_the_zone(self):
  import production_geometry as g
  self.assertEqual((g.BASE_WIDTH,g.BASE_DEPTH,g.MAX_ENEMIES),(22,12,24))
  self.assertLessEqual(6*g.BASE_WIDTH,138.5);self.assertLessEqual(5*g.BASE_DEPTH,95-21)
  self.assertLessEqual(3*29,138.5);self.assertLessEqual(2*29,95-21)
 def test_pdf_embeds_native_cropped_pixels_losslessly(self):
  from PIL import Image
  import board_art06 as art
  name='assets/v0.6/bancada_topo.png';box,size=art.crop(name,0)
  with Image.open(P/name) as src:original=src.crop(box).convert('RGB')
  matches=[]
  with fitz.open(O/'ilustrada/06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf') as doc:
   for info in doc[0].get_images(full=True):
    if tuple(info[2:4])==original.size:
     pix=fitz.Pixmap(doc,info[0]);matches.append(pix.samples==original.tobytes())
  self.assertTrue(matches,'A bancada deve estar incorporada no PDF distribuído')
  self.assertTrue(all(matches),'Recorte mantém os pixels RGB nativos; não é JPEG nem reamostragem')
