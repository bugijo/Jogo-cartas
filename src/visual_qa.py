"""Renderiza todos os PDFs 0.3, contatos e mapas montados. Sem afirmar teste físico."""
from pathlib import Path
import json
import fitz
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-ilustrada-v0.3';E=O/'evidencias';E.mkdir(exist_ok=True)
MM=72/25.4

def render_samples():
 for edition in ['ilustrada','economica']:
  root=O/edition
  for n,file,pg in [('mapa','01_inicial/04_modulos_locais.pdf',0),('mercado','01_inicial/05_montagem_mercado.pdf',0),('abrigo','01_inicial/06_paineis_registros.pdf',0),('fichas','01_inicial/03_lia_ivo.pdf',0),('cartas','01_inicial/02_cartas_duplex.pdf',8),('versos','01_inicial/02_cartas_duplex.pdf',1),('marcadores','01_inicial/07_marcadores.pdf',0),('divisorias','01_inicial/08_divisorias.pdf',0),('calibracao','01_inicial/09_calibracao_duplex.pdf',0),('mapa_geral','02_complemento/06_mapa_geral.pdf',0)]:
   if (root/file).exists():
    d=fitz.open(root/file);d[pg].get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(E/f'{edition}_{n}.png')
  for f in [root/'01_inicial/04_modulos_locais.pdf']+sorted((root/'extras').glob('mapa_*.pdf')):
   if not f.exists():continue
   d=fitz.open(f);ims=[]
   for page in d:
    pix=page.get_pixmap(matrix=fitz.Matrix(1.15,1.15),clip=fitz.Rect(10*MM,10*MM,287*MM,200*MM),alpha=False)
    ims.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
   w,h=ims[0].size;im=Image.new('RGB',(w*2,h*2),'white')
   for i,img in enumerate(ims):im.paste(img,(i%2*w,i//2*h))
   im.save(E/f'{edition}_{f.stem}_montado.jpg',quality=91)
   # Junction enlarged at true crop; no scaling masquerading as detail.
   im.crop((w-100,h-100,w+100,h+100)).save(E/f'{edition}_{f.stem}_juncao.png')
 for name in ['mapa','abrigo','fichas','cartas']:
  before=Image.open(E/f'antes_{name}.png');after=Image.open(E/f'ilustrada_{name}.png')
  if name=='mapa':after=Image.open(E/'ilustrada_mapa_mercado_montado.jpg')
  canvas=Image.new('RGB',(1800,760),'white');draw=ImageDraw.Draw(canvas)
  for x,img,label in [(0,before,'ANTES / 0.2'),(900,after,'DEPOIS / 0.3')]:
   img.thumbnail((880,710));canvas.paste(img,(x+(900-img.width)//2,40));draw.text((x+18,12),label,fill='black')
  canvas.save(E/f'comparacao_{name}.jpg',quality=91)

def contacts():
 report=[]
 for edition in ['ilustrada','economica']:
  root=O/edition;manifest=json.loads((root/'manifesto.json').read_text());files=[root/e['file'] for key in ['initial','supplement'] for e in manifest[key]]+sorted((root/'extras').glob('*.pdf'))
  thumbs=[]
  for f in files:
   d=fitz.open(f)
   for p in d:
    pix=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((230,270));thumbs.append((f.name,p.number+1,im))
   report.append(dict(edition=edition,file=str(f.relative_to(root)),pages=len(d)))
  for start in range(0,len(thumbs),24):
   sheet=Image.new('RGB',(1500,4*320),'#deded6');draw=ImageDraw.Draw(sheet)
   for i,(name,pg,img) in enumerate(thumbs[start:start+24]):
    x=i%6*250;y=i//6*320;sheet.paste(img,(x+(250-img.width)//2,y+23));draw.text((x+5,y+3),f'{name[:27]} / {pg}',fill='black')
   sheet.save(E/f'contato_{edition}_{start//24+1:02}.jpg',quality=90)
 (E/'render_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import sys
 render_samples()
 if '--samples' not in sys.argv:contacts()
 print('Renderização concluída.')
