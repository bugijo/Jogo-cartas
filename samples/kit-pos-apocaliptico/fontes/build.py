"""Provas locais: não substitui fontes, regras nem saídas distribuídas."""
from pathlib import Path
import sys,json,hashlib,copy,math
P=Path(__file__).resolve().parents[3];S=P/'samples/kit-pos-apocaliptico'
sys.path.insert(0,str(P/'src'))
import fitz
from PIL import Image,ImageOps,ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
import build_finish as f
import build_boards06 as boards
q=f.q; art=boards.art
f.setup()
for d in ['pdfs','antes','provas','fontes']: (S/d).mkdir(exist_ok=True)
DATA=json.loads((P/'content/catalog.json').read_text());H=DATA['heroes'][:6]
RES=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def text(c,s,x,y,size=10):
 c.setFont('Body',size);c.setFillColorRGB(.15,.22,.2);c.drawString(x*mm,y*mm,s)
def draw(c,path,box,x,y,w,h,fill=False,component=''):
 im=Image.open(path);l,t,r,b=box;cw,ch=r-l,b-t
 scale=(max if fill else min)(w/cw,h/ch);ww,hh=cw*scale,ch*scale
 from reportlab.lib.utils import ImageReader
 c.saveState();clip=c.beginPath();clip.rect(x*mm,y*mm,w*mm,h*mm);c.clipPath(clip,stroke=0)
 c.drawImage(ImageReader(im.crop(box)),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm,mask='auto');c.restoreState()
 RES.append(dict(file=str(path.relative_to(P)),component=component,original_pixels=list(im.size),crop_pixels=box,used_pixels=[cw,ch],printed_image_mm=[ww,hh],visible_box_mm=[w,h],effective_ppi=round(25.4/scale,2)))

def portrait_box(i,new):
 if new:
  # Native generated sheet: gutters measured by inspection, no stretching.
  col=i%3;row=i//3
  return [ [16,499,981][col], [13,551][row], [467,950,1432][col],[528,1070][row]]
 a=q.art_for_print(H[i]['art']);return a['crop']
def portraits(new):
 folder=S/('pdfs' if new else 'antes');p=folder/'PERSONAGENS_PROVA_A4.pdf';c=canvas.Canvas(str(p),pagesize=A4,invariant=1)
 text(c,'ZONA ZERO / PERSONAGENS / PROVA DE ARTE',12,281,13)
 text(c,'Rostos preservados; desgaste localizado. Não substitui as fichas.',12,273,8)
 for i,h in enumerate(H):
  x=13+i%3*64;y=173-i//3*108
  path=S/'originais/RETRATOS_01.png' if new else P/h['art']['path']
  draw(c,path,portrait_box(i,new),x,y,55,81,True,h['id'])
  text(c,h['name'],x,y-7,12)
  for j,line in enumerate(h['profession'].split(' de ')):text(c,line if j==0 else 'de '+line,x,y-13-j*4,7.7)
 text(c,'Comparar com Mercado B pós-apocalíptico / 100%, sem ajustar',12,13,8);c.save()
 old=q.portrait
 if new:
  def replacement(c,hero,x,y,w,h):
   i=next(i for i,v in enumerate(H) if v['id']==hero['id'])
   draw(c,S/'originais/RETRATOS_01.png',portrait_box(i,True),x/mm,y/mm,w/mm,h/mm,True,hero['id'])
  q.portrait=replacement
 q.heroes(folder,[h['id'] for h in H],'FICHAS_SEIS_HEROIS.pdf')
 q.portrait=old

for new in [False,True]:portraits(new)
# Enemy illustration is already consistent: no gratuitous regeneration or extra category.
p=S/'pdfs/INIMIGOS_PROVA_A4.pdf';c=canvas.Canvas(str(p),pagesize=A4,invariant=1)
text(c,'ZONA ZERO / INIMIGOS / ARTE PRESERVADA',12,281,13)
text(c,'Revisão: silhuetas, roupas rasgadas, tons terrosos e leitura.',12,272,8)
for i,name in enumerate(['Errante','Corredor','Bruto']):
 box=q.art_for_print(dict(path='assets/enemies.png',col=i%2,row=i//2))['crop'];x=12+(i%2)*96;y=157 if i<2 else 42
 draw(c,P/'assets/enemies.png',box,x,y,86,98,False,name);text(c,name,x,y-7,12)
text(c,'Nenhuma categoria nova. Quarto quadrante do atlas excluído: figura humana.',12,16,8);c.save()
# Same selected IDs, effects, dimensions, families and duplex positions.
sel=f.M['initial_cards']+f.M['supplement_cards']; names=['Faca','Mercado: Conserva','Água','Machado','Ferramentas','Bomba','Emboscada','Solidário','Arrastar']
ids=[]
for name in names:
 candidates=[v for v in DATA['cards'] if v['id'] in sel and (v['name']==name or v['name'].endswith(': '+name))]
 if not candidates:raise ValueError(name)
 ids.append(candidates[0]['id'])
old_art=f.f.artwork
f.f.cards_pdf(S/'antes',ids,'CARTAS_PROVA_DUPLEX.pdf',True)
def card_art(c,card,x,y,w,h):
 name=card['name'].split(': ')[-1]
 if name not in ['Conserva','Água','Combustível']:return old_art(c,card,x,y,w,h)
 if name=='Água':
  path=S/'originais/AGUA_ISOLADA.png';box=list(Image.open(path).getbbox());draw(c,path,box,x,y,w,h,False,card['id']);return
 i=['Ferramentas','Conserva','Água','Combustível'].index(name)
 box=[[100,0,755,448],[970,0,1420,445],[230,448,640,1024],[925,450,1430,1024]][i]
 draw(c,S/'originais/SUPRIMENTOS.png',box,x,y,w,h,False,card['id'])
f.f.artwork=card_art
f.f.cards_pdf(S/'pdfs',ids,'CARTAS_PROVA_DUPLEX.pdf',True)
f.f.artwork=old_art
# Complete workshop; same physical footprints, crops and native pixel count.
boards.O=S/'antes';before=boards.full_board('Oficina');boards.split_board(before,S/'antes/OFICINA_4_A4.pdf','Oficina')
source='assets/v0.5/mapa_oficina.png';target=str((S/'originais/OFICINA.png').relative_to(P))
assert Image.open(P/source).size==Image.open(P/target).size
old_reader=art.image_reader
art.image_reader=lambda path,econ,box=None:old_reader(target if path==source else path,econ,box)
boards.O=S/'fontes';art.USES.clear();after=boards.full_board('Oficina')
boards.split_board(after,S/'pdfs/OFICINA_4_A4.pdf','Oficina')
for u in art.USES:
 if u['file']==source:u['file']=target
RES.extend(art.USES);art.image_reader=old_reader
# Canonical geometry snapshot and effective emitted vectors/text must be identical.
m=next(m for m in boards.MAPS if m['name']=='Oficina');dump(S/'fontes/geometria_oficina.json',m)
a=fitz.open(before);b=fitz.open(after)
assert a[0].get_text()==b[0].get_text()
assert str(a[0].get_drawings())==str(b[0].get_drawings()),'Geometria vetorial mudou'
# Before/after PDFs have same card and hero mechanical text, including titles.
for name in ['CARTAS_PROVA_DUPLEX.pdf','FICHAS_SEIS_HEROIS.pdf']:
 a=fitz.open(S/'antes'/name);b=fitz.open(S/'pdfs'/name)
 assert [p.get_text() for p in a]==[p.get_text() for p in b],name
# Raster evidence from generated PDFs. Preview resizing is NOT artwork resolution.
checks=[];thumbs=[]
for folder in [S/'pdfs',S/'antes']:
 for path in sorted(folder.glob('*.pdf')):
  doc=fitz.open(path)
  for i,page in enumerate(doc):
   assert sorted(round(x/mm,2) for x in (page.rect.width,page.rect.height))==[210,297],str(path)
   fitz.TOOLS.mupdf_warnings(reset=True)
   pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4));out=S/'provas'/f'{folder.name}_{path.stem}_{i+1:02}.png';pix.save(out)
   assert not fitz.TOOLS.mupdf_warnings()
   for font in page.get_fonts(full=True):
    if font[2]=='Type0' or 'DejaVu' in font[3]:assert doc.extract_font(font[0])[3],font
   thumbs.append((out,f'{folder.name} / {path.stem} / {i+1}'))
  checks.append(dict(file=str(path.relative_to(S)),pages=len(doc),a4=True))
for label,path in [('ANTES',before),('DEPOIS',after)]:
 doc=fitz.open(path);doc[0].get_pixmap(matrix=fitz.Matrix(.75,.75)).save(S/'provas'/f'OFICINA_{label}_MONTADA.png')
 # 100 x 100 mm proof, actual crop at print scale; only upper repair sector.
 clip=fitz.Rect(5*mm,15*mm,105*mm,115*mm)
 doc[0].get_pixmap(matrix=fitz.Matrix(200/72,200/72),clip=clip).save(S/'provas'/f'OFICINA_{label}_DETALHE.png')
# Comparisons themselves use only final/baseline PDF renderings.
for title,left,right in [
 ('PERSONAGENS','antes_PERSONAGENS_PROVA_A4_01.png','pdfs_PERSONAGENS_PROVA_A4_01.png'),
 ('CARTAS','antes_CARTAS_PROVA_DUPLEX_01.png','pdfs_CARTAS_PROVA_DUPLEX_01.png'),
 ('OFICINA','OFICINA_ANTES_MONTADA.png','OFICINA_DEPOIS_MONTADA.png')]:
 im1=Image.open(S/'provas'/left).convert('RGB');im2=Image.open(S/'provas'/right).convert('RGB')
 comp=Image.new('RGB',(im1.width+im2.width,max(im1.height,im2.height)+32),'white');comp.paste(im1,(0,32));comp.paste(im2,(im1.width,32));d=ImageDraw.Draw(comp);d.text((12,10),'ANTES',fill='black');d.text((im1.width+12,10),'PROVA ATUAL',fill='black');comp.save(S/'provas'/f'COMPARACAO_{title}.jpg',quality=92)
# Grayscale diagnostic only, not a new economic kit.
ImageOps.grayscale(Image.open(S/'provas/OFICINA_DEPOIS_MONTADA.png')).save(S/'provas/OFICINA_CINZA.png')
w=900;cw=225;ch=190;contact=Image.new('RGB',(w,math.ceil(len(thumbs)/4)*ch),'#dddddd');d=ImageDraw.Draw(contact)
for i,(path,label) in enumerate(thumbs):
 im=Image.open(path).convert('RGB');im.thumbnail((cw-12,ch-30));x=i%4*cw;y=i//4*ch;contact.paste(im,(x,y+22));d.text((x+2,y+2),label[:33],fill='black')
contact.save(S/'provas/CONTATO_TODAS_PAGINAS.jpg',quality=90)
dump(S/'fontes/resolucao.json',RES);dump(S/'fontes/verificacoes.json',dict(pdfs=checks,card_ids=ids,geometry_equal=True,card_and_hero_text_equal=True))
# Full factual inventory, without automatically claiming all old assets reviewed.
assets=[]
for path in sorted((P/'assets').rglob('*')):
 if path.suffix.lower() not in ['.png','.jpg','.jpeg','.svg']:continue
 item=dict(file=str(path.relative_to(P)),status='existente; revisão individual pendente')
 if path.suffix!='.svg':
  with Image.open(path) as im:item.update(pixels=list(im.size),mode=im.mode)
 assets.append(item)
for path in sorted((S/'originais').glob('*.png')):
 with Image.open(path) as im:assets.append(dict(file=str(path.relative_to(P)),pixels=list(im.size),origin='image_gen integrado / edição de arte existente',status='integrado apenas nas provas'))
dump(S/'fontes/inventario_assets.json',assets)
dump(S/'fontes/inventario_componentes.json',dict(catalog={k:len(DATA[k]) for k in ['heroes','cards','maps','tokens','modules']},selected_cards=len(sel),destinations=[m['name'] for m in DATA['maps']],pdfs_existing=[str(p.relative_to(P)) for p in sorted((P/'output').rglob('*.pdf'))]))
print('Provas geradas em',S)
