"""Fabricação 0.4: fontes novas, catálogo/regras e geradores anteriores preservados."""
from pathlib import Path
import json,math,copy,hashlib,shutil,argparse
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
import build_illustrated as q
import production_geometry as g
P=q.P;O=P/'output/edicao-fabricacao-v0.4';BASE=P/'output/edicao-ilustrada-v0.3';M=q.M;D=q.D;a=q.a;b=q.b
PAIRS=[];LAYOUT=[];FILES=[];MAP_GEOMETRY=[]
DIRS=['00_LEIA_PRIMEIRO','01_GUIA_E_REGRAS','02_CARTAS_DUPLEX','03_CARTAS_RECORTAR_E_COLAR','04_PERSONAGENS_E_INIMIGOS','05_PAINEIS','06_TABULEIROS','07_MARCADORES_E_DIVISORIAS','08_EXTRAS_OPCIONAIS','09_FONTES_EDITAVEIS','10_VERIFICACOES']

def art_for_print(art):
 art=art.copy();name=Path(art['path']).name
 if 'crop' not in art and name in q.REGIONS:
  cols,rows=q.REGIONS[name];l,r=cols[art.get('col',0)];t,bot=rows[art.get('row',0)];art['crop']=[l,t,r,bot]
 if not a.ECON:return art
 from PIL import Image,ImageOps
 path=P/art['path'];out=P/'assets/v0.4/economica'/path.name
 if out not in q.DERIVED:
  out.parent.mkdir(parents=True,exist_ok=True);src=Image.open(path);im=ImageOps.grayscale(src).point(lambda v:min(255,int(v*.78+56.1)))
  if src.mode=='RGBA':im=Image.merge('LA',(im,src.getchannel('A')))
  im.save(out);q.DERIVED.add(out)
 art['path']=str(out.relative_to(P));return art
q.art_for_print=art_for_print

def init(root):
 for d in DIRS:(root/d).mkdir(parents=True,exist_ok=True)

def para(c,text,x,y,w,h,size=10,bold=False,label=''):
 q.paragraph(c,text,x,y,w,h,size,bold,label)
 LAYOUT.append(dict(file=q.LABEL,page=q.PAGE,label=label,x=x,y=y,w=w,h=h,size=size,text=text))

def title(c,t,sub='',W=210,H=297):q.heading(c,t,sub,W,H)
def txt(*args,**kwargs):q.txt(*args,**kwargs)

def record(root,f,kind,stage='initial',duplex=False,optional=False,replaces=None,method='both',copies=1):
 d=fitz.open(f);FILES.append(dict(file=str(f.relative_to(root)),kind=kind,stage=stage,duplex=duplex,method=method,optional=optional,replaces=replaces,copies=copies,pages=len(d),sheets=math.ceil(len(d)/2)*copies if duplex else len(d)*copies,orientation='paisagem' if d[0].rect.width>d[0].rect.height else 'retrato',size='A4 210×297 mm',turn='borda longa' if duplex else None,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))

def effect(card,initial=False):return card['text'].replace('ceil(H/2)','1') if initial else card['text']

def artwork(c,card,x,y,w,h):
 # Same canonical original artwork, mapped uniformly to the requested area.
 if card['family']=='MOR':
  heroes=[hero for hero in D['heroes'] if hero['name'] in card['name']]
  for i,hero in enumerate(heroes):q.raster(c,hero['art'],x+i*w/len(heroes),y,w/len(heroes),h)
  return
 c.saveState();scale=min(w/43,h/31);c.translate((x+(w-43*scale)/2-10*scale)*mm,(y+(h-31*scale)/2-31*scale)*mm);c.scale(scale,scale);q.card_art(c,card,0,0,True);c.restoreState()

def card_front(c,card,x,y,initial):
 text=effect(card,initial);dense=len(text)>165;short=len(text)<=85
 a.rect(c,x*mm,y*mm,63*mm,88*mm,'#ffffff',stroke='#8b9b95',r=1*mm)
 a.line(c,(x+4)*mm,(y+85)*mm,(x+59)*mm,(y+85)*mm,a.OLIVE,1.2)
 para(c,card['name'],x+4,y+(58 if dense else 72),35 if dense else 55,25 if dense else 12,11.5 if dense else 12.5,True,card['id']+' nome')
 if dense:artwork(c,card,x+40,y+57,19,22)
 else:artwork(c,card,x+5,y+(35 if short else 46),53,35 if short else 24)
 if card.get('load') is not None and not dense:
  yy=y+(29 if short else 40);a.rect(c,(x+4)*mm,yy*mm,55*mm,5*mm,a.PAPER,stroke=a.PAPER);txt(c,f'CARGA {card["load"]}',x+6,yy+1.3,8.3,True)
 elif card.get('reward') and not dense:
  qty=sum(card['reward'].values());yy=y+40;a.rect(c,(x+4)*mm,yy*mm,55*mm,5*mm,a.PAPER,stroke=a.PAPER);resource=next(iter(card['reward']));parts=next((r.get('portions') for r in D['cards'] if r.get('resource')==resource),None)
  badge=f'{qty} carta(s) / {qty*parts} porções' if parts else f'ACHADO: {qty} carta(s) da reserva'
  txt(c,badge,x+6,yy+1.3,8,True)
 h=44 if dense else (16 if short else 27)
 para(c,text,x+4,y+12,55,h,9.5 if dense else 10,label=card['id']+' efeito')
 b.family_icon(c,card['family'],(x+4)*mm,(y+6)*mm,3*mm)
 txt(c,b.FAMILIES[card['family']],x+8,y+6.2,6.8,True);txt(c,card['id'],x+33,y+4.5,6.2)

def card_back(c,fam,x,y):
 a.rect(c,x*mm,y*mm,63*mm,88*mm,'#ffffff',stroke='#8b9b95',r=1*mm)
 a.rect(c,(x+4)*mm,(y+4)*mm,55*mm,80*mm,a.PAPER,stroke=a.INK,r=1*mm)
 a.line(c,(x+8)*mm,(y+72)*mm,(x+55)*mm,(y+72)*mm,a.OLIVE,1)
 txt(c,'ZONA ZERO',x+8,y+62,16,True);txt(c,'COMUNIDADE',x+8,y+55,10,True)
 b.family_icon(c,fam,(x+24)*mm,(y+35)*mm,13*mm)
 para(c,b.FAMILIES[fam].upper(),x+8,y+19,47,10,11,True,label='verso '+fam)
 a.line(c,(x+8)*mm,(y+13)*mm,(x+55)*mm,(y+13)*mm,a.OLIVE,1)

def cards_pdf(folder,ids,name,initial=False):
 f=folder/name;q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=A4)
 for n in range(math.ceil(len(ids)/9)):
  batch=ids[n*9:n*9+9]
  for back in [False,True]:
   q.PAGE=n*2+1+back;txt(c,f'{name} | folha {n+1:02} | '+('VERSO • borda longa' if back else 'FRENTE')+' | 100%',8.5,7,6.4)
   for k,id in enumerate(batch):
    row,col=g.card_cell(k,'duplex_back' if back else 'front');x=8.5+col*65;y=297-14.5-row*90-88
    if back:card_back(c,q.CARDS[id]['family'],x,y)
    else:card_front(c,q.CARDS[id],x,y,initial)
   c.showPage()
 c.save();return f

def sample():
 root=O/'amostras';root.mkdir(parents=True,exist_ok=True)
 ids=[next(c['id'] for c in D['cards'] if c['name']==name and c['id'] in M['initial_cards']+M['supplement_cards']) for name in ['Faca','Bomba','Mercado: Conserva','Jana e criança','Emboscada','Solidário','Arrastar','Bateria','Van de manutenção']]
 cards_pdf(root,ids,'AMOSTRA_CARTAS_DUPLEX.pdf',True)

def manual_cards(root,source,ids,stem,stage):
 d=fitz.open(source);folder=root/'03_CARTAS_RECORTAR_E_COLAR'
 for back in [False,True]:
  f=folder/(stem+('_VERSOS.pdf' if back else '_FRENTES.pdf'));c=canvas.Canvas(str(f),pagesize=A4)
  for sn in range(math.ceil(len(ids)/9)):
   txt(c,f'COLAR / {stem} / '+('VERSOS' if back else 'FRENTES')+f' / folha {sn+1:02} / UMA FACE / 100%',8.5,7,6.7)
   c.showPage()
  c.save();out=fitz.open(f)
  for i,id in enumerate(ids):
   sn,k=divmod(i,9);x,top,w,h=g.card_rect(k,'duplex_back' if back else 'front');clip=fitz.Rect(x*mm,top*mm,(x+w)*mm,(top+h)*mm)
   xx,yy,_,_=g.card_rect(k,'manual_back' if back else 'front');target=fitz.Rect(xx*mm,yy*mm,(xx+w)*mm,(yy+h)*mm)
   out[sn].show_pdf_page(target,d,sn*2+int(back),clip=clip)
   code=f'{stem[-1]}-{sn+1:02}-{k+1}'
   out[sn].insert_font(fontname='ZZBody',fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
   out[sn].insert_text((xx*mm,(yy+h+1.6)*mm),code,fontname='ZZBody',fontsize=4.2,color=(.15,.25,.25))
   PAIRS.append(dict(file=str(f.relative_to(root)),id=id,code=code,page=sn+1,slot=k,side='back' if back else 'front',box=[xx,yy,w,h],label_outside=True))
  tmp=f.with_suffix('.tmp.pdf');out.save(tmp,garbage=4,deflate=True);out.close();tmp.replace(f)
  record(root,f,'cartas',stage,method='manual')

def all_cards(root):
 for ids,stem,stage,initial in [(M['initial_cards'],'KIT_INICIAL_1','initial',True),(M['supplement_cards'],'KIT_COMPLEMENTO_2','supplement',False)]:
  f=cards_pdf(root/'02_CARTAS_DUPLEX',ids,stem+'_DUPLEX.pdf',initial);record(root,f,'cartas',stage,True,method='duplex');manual_cards(root,f,ids,stem,stage)

def save_layout():
 (O/'layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2));(O/'layout_issues.json').write_text(json.dumps(b.issues,ensure_ascii=False,indent=2));(O/'pares_manuais.json').write_text(json.dumps(PAIRS,ensure_ascii=False,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--step',default='sample');args=p.parse_args()
 if args.step=='sample':sample()
 else:
  for ed in ['ilustrada','economica']:
   root=O/ed;init(root);a.ECON=ed=='economica'
   if args.step=='cards':all_cards(root)
 save_layout();print('Etapa',args.step,'estouros',b.issues[:8])
