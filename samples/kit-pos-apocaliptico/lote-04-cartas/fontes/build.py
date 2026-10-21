from pathlib import Path
import sys,json,math
S=Path(__file__).resolve().parents[1];P=next(p for p in S.parents if (p/'content/catalog.json').exists());sys.path.insert(0,str(P/'src'))
import build_finish as f
import fitz
from PIL import Image,ImageDraw
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
f.setup();g=f.f;old=g.artwork;res=[]
MAP={**{n:('ARMAS_CENAS',i) for i,n in enumerate(['Faca','Machado','Pistola','Espingarda'])},**{n:('SUPRIMENTOS_CENAS',i) for i,n in enumerate(['Ferramentas','Conserva','Água','Combustível'])},**{n:('PECAS_CENAS',i) for i,n in enumerate(['Bomba','Membrana','Conexões','Bateria'])}}
MAP.update({n:('INTENCOES_CENAS',i) for i,n in enumerate(['Solidário','Assustado','Oportunista','Infiltrado'])})
def art(c,card,x,y,w,h):
 n=card['name'].split(': ')[-1]
 if n not in MAP:return old(c,card,x,y,w,h)
 sheet,i=MAP[n];path=S/'originais'/f'{sheet}.png';im=Image.open(path);cw,ch=im.width/2,im.height/2;box=(int(i%2*cw+7),int(i//2*ch+7),int((i%2+1)*cw-7),int((i//2+1)*ch-7));
 if sheet=='SUPRIMENTOS_CENAS':box=([7,7,754,462],[783,7,1529,462],[7,485,754,1017],[783,485,1529,1017])[i]
 im=im.crop(box)
 # Contain: never cut ends of objects for an art-area ratio.
 scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale
 c.drawImage(ImageReader(im),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm)
 res.append(dict(id=card['id'],file=str(path.relative_to(S)),crop_pixels=box,print_mm=[ww,hh],effective_ppi=25.4/scale))
sel=f.M['initial_cards']+f.M['supplement_cards'];assert len(sel)==114 and len(set(sel))==114
sample=[]
for name in ['Faca','Machado','Ferramentas','Mercado: Conserva','Água','Bateria','Bomba','Membrana','Conexões']:
 sample.append(next(c['id'] for c in f.D['cards'] if c['id'] in sel and (c['name']==name or c['name'].endswith(': '+name))))
for new in [False,True]:
 root=S/('pdfs' if new else 'antes');g.init(root);g.artwork=art if new else old;g.all_cards(root);g.cards_pdf(root,sample,'PROVA_9_CARTAS_DUPLEX.pdf',True);g.cards_pdf(root,[next(c['id'] for c in f.D['cards'] if c['id'] in sel and c['name']==n) for n in ['Solidário','Assustado','Oportunista','Infiltrado']],'PROVA_INTENCOES_DUPLEX.pdf',True)
g.artwork=old
checks=[]
for path in sorted((S/'pdfs').rglob('*.pdf')):
 rel=path.relative_to(S/'pdfs');a=fitz.open(S/'antes'/rel);b=fitz.open(path);assert [p.get_text() for p in a]==[p.get_text() for p in b]
 for i,p in enumerate(b):
  assert abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01
  if 'DUPLEX' in path.name and i%2:
   assert p.get_pixmap().samples==a[i].get_pixmap().samples,'Verso mudou'
  for font in p.get_fonts(full=True):
   if font[2]=='Type0':assert b.extract_font(font[0])[3]
  out=S/'provas'/rel.parent;out.mkdir(parents=True,exist_ok=True);pix=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pix.save(out/f'{path.stem}_{i+1:02}.png')
 checks.append(dict(file=str(rel),pages=len(b),text_identical=True,a4=True))
 for i in range(0,len(b),2 if 'DUPLEX' in path.name else 1):
  if not path.name.startswith('PROVA_'):continue
  comp=Image.new('RGB',(1220,880),'#eee8d9');d=ImageDraw.Draw(comp)
  for j,doc in enumerate([a,b]):
   pix=doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((600,850));comp.paste(im,(j*610,25));d.text((j*610+10,5),['ANTES','DEPOIS'][j],fill='black')
  comp.save(S/'provas'/('COMPARACAO_CARTAS.jpg' if path.name=='PROVA_9_CARTAS_DUPLEX.pdf' else 'COMPARACAO_INTENCOES.jpg'),quality=94)
(S/'fontes/resolucao.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));(S/'VERIFICACOES.json').write_text(json.dumps(dict(selected_ids=sel,changed_ids=sorted(set(x['id'] for x in res)),pdfs=checks,unchanged_backs=True,physical_print=False),ensure_ascii=False,indent=2));print('114 cartas preservadas; arquivos duplex e manual; versos idênticos.')
# Contact must always be regenerated from the current final PDFs, never reused.
files=sorted((S/'provas/02_CARTAS_DUPLEX').glob('*.png'));out=Image.new('RGB',(1800,math.ceil(len(files)/6)*425),'#eee8d9');d=ImageDraw.Draw(out)
for i,p in enumerate(files):
 im=Image.open(p);im.thumbnail((295,410));out.paste(im,(i%6*300,i//6*425+12));d.text((i%6*300,i//6*425),p.stem[-15:],fill='black')
out.save(S/'provas/CONTATO_DUPLEX.jpg')
