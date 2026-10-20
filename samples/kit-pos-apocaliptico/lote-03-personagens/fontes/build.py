"""Provas dos 18 retratos restantes; nenhuma fonte mecânica alterada."""
from pathlib import Path
import sys,json
S=Path(__file__).resolve().parents[1];P=next(p for p in S.parents if (p/'content/catalog.json').exists());sys.path.insert(0,str(P/'src'))
import build_finish as f
import fitz
from PIL import Image,ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
f.setup();q=f.q;H=json.loads((P/'content/catalog.json').read_text())['heroes'][6:];RES=[]
# Measured native gutters; no uniform crop assumption.
BOXES={2:([20,500,975],[461,937,1417],[16,553],[515,1080]),3:([18,496,975],[460,940,1418],[15,558],[515,1074]),4:([16,495,975],[461,941,1419],[16,540],[503,1081])}
for d in ['pdfs','antes','provas']:(S/d).mkdir(exist_ok=True)
def draw(c,h,x,y,w,hh):
 i=next(i for i,v in enumerate(H) if v['id']==h['id']);batch=i//6+2;k=i%6;col=k%3;row=k//3;l,r,t,b=BOXES[batch];box=(l[col],t[row],r[col],b[row]);path=S/'originais'/f'RETRATOS_{batch:02}.png';im=Image.open(path);crop=im.crop(box)
 scale=max(w/crop.width,hh/crop.height);ww,he=crop.width*scale,crop.height*scale
 c.saveState();clip=c.beginPath();clip.rect(x,y,w,hh);c.clipPath(clip,stroke=0);c.drawImage(ImageReader(crop),x+(w-ww)/2,y+(hh-he)/2,ww,he);c.restoreState()
 RES.append(dict(id=h['id'],file=str(path.relative_to(S)),native_pixels=list(im.size),crop_pixels=box,printed_mm=[ww/mm,he/mm],effective_ppi=72/scale))
old=q.portrait
for new in [False,True]:
 out=S/('pdfs' if new else 'antes');q.portrait=draw if new else old
 q.heroes(out,[h['id'] for h in H],'FICHAS_18_HEROIS.pdf')
 c=canvas.Canvas(str(out/'RETRATOS_18_PROVA.pdf'),pagesize=A4,invariant=1)
 for batch in range(3):
  q.txt(c,'ZONA ZERO / RETRATOS / '+str(batch+2),12,281,13,True)
  for k,h in enumerate(H[batch*6:batch*6+6]):
   x=13+k%3*64;y=173-k//3*108;q.portrait(c,h,x*mm,y*mm,55*mm,81*mm);q.txt(c,h['name'],x,y-7,12,True);q.txt(c,h['profession'],x,y-13,7)
  q.txt(c,'Prova de arte; fichas jogáveis em arquivo separado. Escala 100%.',12,13,8);c.showPage()
 c.save()
q.portrait=old
for name in ['FICHAS_18_HEROIS.pdf','RETRATOS_18_PROVA.pdf']:
 a=fitz.open(S/'antes'/name);b=fitz.open(S/'pdfs'/name);assert len(a)==len(b)
 assert [p.get_text() for p in a]==[p.get_text() for p in b]
 for i in range(len(b)):
  thumbs=[]
  for label,doc in [('ANTES',a),('DEPOIS',b)]:
   p=doc[i];assert abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01
   for font in p.get_fonts(full=True):
    if font[2]=='Type0':assert doc.extract_font(font[0])[3]
   pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False);pix.save(S/'provas'/f'{name[:-4]}_{label}_{i+1:02}.png');im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((600,850));thumbs.append(im)
  comp=Image.new('RGB',(1220,880),'#e9e4d9');d=ImageDraw.Draw(comp)
  for j,im in enumerate(thumbs):comp.paste(im,(j*610,25));d.text((j*610+10,5),['ANTES','DEPOIS'][j],fill='black')
  comp.save(S/'provas'/f'COMPARACAO_{name[:-4]}_{i+1:02}.jpg',quality=92)
(S/'fontes/resolucao.json').write_text(json.dumps(RES,ensure_ascii=False,indent=2))
(S/'VERIFICACOES.json').write_text(json.dumps(dict(heroes=18,hero_ids=[h['id'] for h in H],sheet_pages=9,contact_pages=3,text_identical=True,a4=True,all_pages_rendered=True,physical_print=False,human_playtest=False),indent=2))
print('18 retratos integrados, 9 fichas A4 + 3 contatos; texto preservado.')
