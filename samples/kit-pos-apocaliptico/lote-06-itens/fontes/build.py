"""Integra oito novas cenas preservando exatamente os 114 componentes do lote 04."""
from pathlib import Path
import sys,json,math
S=Path(__file__).resolve().parents[1];P=next(p for p in S.parents if (p/'content/catalog.json').exists());sys.path.insert(0,str(P/'src'))
import build_finish as f
import fitz
from PIL import Image,ImageDraw
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
f.setup();g=f.f;original=g.artwork;RES=[];L04=S.parent/'lote-04-cartas'
OLD={**{n:('ARMAS_CENAS',i) for i,n in enumerate(['Faca','Machado','Pistola','Espingarda'])},**{n:('SUPRIMENTOS_CENAS',i) for i,n in enumerate(['Ferramentas','Conserva','Água','Combustível'])},**{n:('PECAS_CENAS',i) for i,n in enumerate(['Bomba','Membrana','Conexões','Bateria'])},**{n:('INTENCOES_CENAS',i) for i,n in enumerate(['Solidário','Assustado','Oportunista','Infiltrado'])}}
NEW={**{n:('SAQUES_COMPLEMENTARES',i) for i,n in enumerate(['Material','Munição','Medicamento','Carne'])},**{n:('UTILITARIOS_VEICULO',i) for i,n in enumerate(['Lanterna','Kit de instalação médica','Bancada','Van de manutenção'])}}
def art(c,card,x,y,w,h,include_new):
 name=card['name'].split(': ')[-1]
 if include_new and name in NEW:sheet,i=NEW[name];path=S/'originais'/f'{sheet}.png'
 elif name in OLD:sheet,i=OLD[name];path=L04/'originais'/f'{sheet}.png'
 else:return original(c,card,x,y,w,h)
 im=Image.open(path);cw,ch=im.width/2,im.height/2
 box=(int(i%2*cw+7),int(i//2*ch+7),int((i%2+1)*cw-7),int((i//2+1)*ch-7))
 if sheet=='SUPRIMENTOS_CENAS':box=([7,7,754,462],[783,7,1529,462],[7,485,754,1017],[783,485,1529,1017])[i]
 crop=im.crop(box);scale=min(w/crop.width,h/crop.height);ww,hh=crop.width*scale,crop.height*scale
 c.drawImage(ImageReader(crop),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm)
 if include_new:RES.append(dict(id=card['id'],source=str(path.relative_to(P)),crop_pixels=box,printed_mm=[ww,hh],effective_ppi=25.4/scale,new_scene=sheet in ['SAQUES_COMPLEMENTARES','UTILITARIOS_VEICULO']))
sel=f.M['initial_cards']+f.M['supplement_cards'];assert len(sel)==114 and len(set(sel))==114
sample=[next(c['id'] for c in f.D['cards'] if c['id'] in sel and (c['name']==n or c['name'].endswith(': '+n))) for n in NEW]
for new in [False,True]:
 root=S/('pdfs' if new else 'antes');g.init(root);g.artwork=lambda c,card,x,y,w,h:art(c,card,x,y,w,h,new)
 g.all_cards(root);g.cards_pdf(root,sample,'PROVA_8_ITENS_DUPLEX.pdf',True)
g.artwork=original
checks=[]
for path in sorted((S/'pdfs').rglob('*.pdf')):
 rel=path.relative_to(S/'pdfs');a=fitz.open(S/'antes'/rel);b=fitz.open(path)
 assert [p.get_text() for p in a]==[p.get_text() for p in b],rel
 for i,p in enumerate(b):
  assert abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01
  if 'DUPLEX' in path.name and i%2:assert p.get_pixmap().samples==a[i].get_pixmap().samples,('Verso mudou',rel,i)
  for font in p.get_fonts(full=True):
   if font[2]=='Type0':assert b.extract_font(font[0])[3]
  out=S/'provas'/rel.parent;out.mkdir(parents=True,exist_ok=True);p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(out/f'{path.stem}_{i+1:02}.png')
 checks.append(dict(file=str(rel),pages=len(b),text_identical=True,a4=True))
 if path.name!='PROVA_8_ITENS_DUPLEX.pdf':continue
 for i in range(0,len(b),2):
  comp=Image.new('RGB',(1220,880),'#eee8d9');d=ImageDraw.Draw(comp)
  for j,doc in enumerate([a,b]):
   pix=doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((600,850));comp.paste(im,(j*610,25));d.text((j*610+10,5),['ANTES','DEPOIS'][j],fill='black')
  comp.save(S/'provas'/f'COMPARACAO_ITENS_{i//2+1}.jpg',quality=94)
(S/'fontes/resolucao.json').write_text(json.dumps(RES,ensure_ascii=False,indent=2))
(S/'VERIFICACOES.json').write_text(json.dumps(dict(selected_ids=sel,changed_ids=sorted(set(x['id'] for x in RES if x['new_scene'])),pdfs=checks,unchanged_backs=True,min_new_ppi=min(x['effective_ppi'] for x in RES if x['new_scene']),physical_print=False),ensure_ascii=False,indent=2))
print('114 cartas, textos e versos preservados;',len(set(x['id'] for x in RES if x['new_scene'])),'IDs com novas cenas.')
files=sorted((S/'provas/02_CARTAS_DUPLEX').glob('*.png'));out=Image.new('RGB',(1800,math.ceil(len(files)/6)*425),'#eee8d9');d=ImageDraw.Draw(out)
for i,p in enumerate(files):
 im=Image.open(p);im.thumbnail((295,410));out.paste(im,(i%6*300,i//6*425+12));d.text((i%6*300,i//6*425),p.stem[-15:],fill='black')
out.save(S/'provas/CONTATO_DUPLEX.jpg')
