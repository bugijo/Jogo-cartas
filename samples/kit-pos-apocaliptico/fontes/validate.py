from pathlib import Path
import json,sys,subprocess,hashlib,io
import fitz
from PIL import Image,ImageDraw,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
P=Path(__file__).resolve().parents[3];S=P/'samples/kit-pos-apocaliptico'
sys.path.insert(0,str(P/'src'));import build_boards06 as b
# Immutable game sources, even if working-tree changes have not yet been committed.
locked=['RULES.md','CAMPAIGN.md','content/catalog.json','content/production/geometry_0.6.json','content/production/scenes_0.6.json','content/starter/01_guia.json']
for name in locked:assert (P/name).read_bytes()==subprocess.check_output(['git','show','48f5794:'+name],cwd=P),name
# All tracked changes stay in the isolated sample directory.
changed=subprocess.check_output(['git','diff','48f5794','--name-only'],cwd=P,text=True).splitlines()
assert all(n.startswith('samples/kit-pos-apocaliptico/') or n in ['README.md','CHECKPOINT.md','ASSET_MANIFEST.md','VISUAL_QA.md'] for n in changed)
# PDF evidence: exact text and vector geometry; art bytes differ.
for name in ['OFICINA','HOSPITAL']:
 old=fitz.open(S/f'antes/fontes_tabuleiros/ilustrada/{name}.pdf');new=fitz.open(S/f'fontes/fontes_tabuleiros/ilustrada/{name}.pdf')
 assert old[0].get_text()==new[0].get_text()
 assert str(old[0].get_drawings())==str(new[0].get_drawings())
 assert old[0].get_pixmap().samples!=new[0].get_pixmap().samples
 split=fitz.open(S/f'pdfs/{name}_4_A4.pdf');assert len(split)==4
 # Reassemble using exact physical crop; pixel identity verifies all four junctions.
 assembled=fitz.open();pg=assembled.new_page(width=554*mm,height=380*mm)
 for i in range(4):
  x=(i%2)*277;y=(i//2)*190
  pg.show_pdf_page(fitz.Rect(x*mm,y*mm,(x+277)*mm,(y+190)*mm),split,i,clip=fitz.Rect(10*mm,10*mm,287*mm,200*mm))
 # Vector transforms can cause subpixel antialiasing differences; measure and report, don't promise exact raster equality.
 import numpy as np
 A=np.frombuffer(new[0].get_pixmap(matrix=fitz.Matrix(1,1)).samples,dtype=np.uint8).astype(float)
 B=np.frombuffer(pg.get_pixmap(matrix=fitz.Matrix(1,1)).samples,dtype=np.uint8).astype(float)
 assert A.shape==B.shape
 difference=float(np.mean(abs(A-B)));assert difference<1,(name,difference)
 assembled.save(S/f'fontes/{name}_REMONTADO.pdf')
 # Contact sheet includes every connection at readable size, cropped from FINAL PDF.
 m=next(m for m in b.MAPS if m['name'].upper()==name);edges=[e for e in b.segments(m) if e['connected']]
 sheet=Image.new('RGB',(1000,7*145),'white');dr=ImageDraw.Draw(sheet)
 for i,e in enumerate(edges):
  x,y=e['center'];clip=fitz.Rect((x-22)*mm,(380-y-13)*mm,(x+22)*mm,(380-y+13)*mm)
  pix=new[0].get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=clip);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((320,115))
  X=(i%3)*333;Y=(i//3)*145;sheet.paste(im,(X,Y+23));dr.text((X+4,Y+4),str(e['key'])+(' porta' if e['door'] else ' passagem'),fill='black')
 sheet.save(S/f'provas/{name}_21_CONEXOES.jpg',quality=94)
 ImageOps.grayscale(Image.open(S/f'provas/{name}_DEPOIS_MONTADA.png')).save(S/f'provas/{name}_CINZA.png')
# The entire duplex back page is pixel-identical to the previous template.
a=fitz.open(S/'antes/CARTAS_PROVA_DUPLEX.pdf');d=fitz.open(S/'pdfs/CARTAS_PROVA_DUPLEX.pdf')
assert a[1].get_pixmap().samples==d[1].get_pixmap().samples
# Two 100x100mm crops on each A4; same coordinates before/after.
output=fitz.open()
for name,coord in [('OFICINA',(430,20)),('HOSPITAL',(150,20))]:
 buff=io.BytesIO();c=canvas.Canvas(buff,pagesize=A4,invariant=1);c.setFont('Body',10)
 for yy,t in [(280,f'{name} / COMPARAÇÃO EM ESCALA REAL'),(266,'Anterior'),(142,'Prova pós-apocalíptica'),(17,'Imprimir em 100%, sem ajustar. Cada imagem: 100 × 100 mm.')]:c.drawString(15*mm,yy*mm,t)
 c.line(15*mm,9*mm,115*mm,9*mm);c.setFont('Body',7);c.drawString(120*mm,8*mm,'100 mm');c.save()
 leaf=fitz.open(stream=buff.getvalue(),filetype='pdf');page=leaf[0]
 for folder,top in [('antes',35),('fontes',159)]:
  doc=fitz.open(S/f'{folder}/fontes_tabuleiros/ilustrada/{name}.pdf');x,y=coord
  page.show_pdf_page(fitz.Rect(15*mm,top*mm,115*mm,(top+100)*mm),doc,0,clip=fitz.Rect(x*mm,y*mm,(x+100)*mm,(y+100)*mm))
 output.insert_pdf(leaf)
output.save(S/'pdfs/COMPARACOES_100MM_A4.pdf')
for i,page in enumerate(output):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(S/f'provas/COMPARACAO_100MM_{i+1}.png')
# Measured density from PDF transformations, including clips; no metadata-DPI claims.
results=[]
for path in sorted((S/'pdfs').glob('*.pdf')):
 doc=fitz.open(path);ppi=[]
 for page in doc:
  assert sorted(round(v/mm,2) for v in [page.rect.width,page.rect.height])==[210,297]
  for info in page.get_image_info():
   a,b0,c,d0,*_=info['transform'];ppi.append(min(info['width']/(a*a+b0*b0)**.5*72,info['height']/(c*c+d0*d0)**.5*72))
  for font in page.get_fonts(full=True):
   if 'DejaVu' in font[3]:assert doc.extract_font(font[0])[3]
 results.append(dict(file=path.name,pages=len(doc),sheets=len(doc)//2 if 'DUPLEX' in path.name else len(doc),min_effective_ppi=round(min(ppi),2) if ppi else None,duplex='DUPLEX' in path.name))
(S/'fontes/qa_final.json').write_text(json.dumps(dict(files=results,legacy_sources_unchanged=locked,duplex_back_identical=True,geometry_and_text_identical=True,assembly_mean_channel_difference_below_1=True),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
