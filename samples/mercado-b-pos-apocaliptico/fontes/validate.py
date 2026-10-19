"""Verifica os arquivos finais: dimensões físicas, fontes, arte e camada funcional."""
from pathlib import Path
import ast,json,hashlib
import fitz
from PIL import Image
S=Path(__file__).resolve().parents[1];OLD=S.parent/'mercado-b-refinado';mm=72/25.4
assert (S/'fontes/geometria.json').read_bytes()==(OLD/'fontes/geometria.json').read_bytes()
def funcs(p):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)}
a=funcs(S/'fontes/build.py');b=funcs(OLD/'fontes/build.py')
for n in ['segments','architecture','functional','labels']:assert a[n]==b[n],n
pdf=fitz.open(S/'MERCADO_4_A4.pdf');assert len(pdf)==4
original=Image.open(S/'MERCADO_ARTE_175PPI.png').convert('RGB');digest=hashlib.md5(original.tobytes()).digest()
for p in pdf:
 assert abs(p.rect.width/mm-297)<.001 and abs(p.rect.height/mm-210)<.001
 assert any(i['digest']==digest for i in p.get_image_info(hashes=True))
 for f in p.get_fonts(full=True):assert pdf.extract_font(f[0])[3]
proof=fitz.open(S/'PROVA_COMPARATIVA_100MM_A4.pdf');p=proof[0]
assert len(proof)==1 and abs(p.rect.width/mm-210)<.001 and abs(p.rect.height/mm-297)<.001
boxes=[fitz.Rect(x[3]) for x in p.get_xobjects() if x[2]==0]
assert len(boxes)==2
for r in boxes:assert abs(r.width/mm-100)<.001 and abs(r.height/mm-100)<.001
for f in p.get_fonts(full=True):assert proof.extract_font(f[0])[3]
ruler=p.get_drawings()[0]['rect'];assert abs(ruler.width/mm-100)<.001
assert 'Imprimir em 100%, sem ajustar' in p.get_text()
m=json.loads((S/'ASSET_MANIFEST.json').read_text())
for x in m['sources']:
 assert not x['upscaled'] and min(x['effective_ppi_xy'])>=175
 assert hashlib.sha256((S/x['file']).read_bytes()).hexdigest()==x['sha256']
result={'geometry_bytes_identical':True,'functional_vector_functions_identical':True,'new_raster_verified_by_decoded_pixel_hash':True,'a4_landscape_pages':4,'comparison_a4_portrait_pages':1,'comparison_boxes_measured_mm':[[r.width/mm,r.height/mm] for r in boxes],'ruler_measured_mm':ruler.width/mm,'fonts_embedded':True,'minimum_native_ppi':min(min(x['effective_ppi_xy']) for x in m['sources']),'physical_printing':False}
(S/'VERIFICACAO_FINAL.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
