"""Provas obtidas dos PDFs finais, sem substituir a arte por mockups."""
from pathlib import Path
import json,hashlib
import fitz
from PIL import Image,ImageDraw,ImageFont
from reportlab.lib.units import mm
from build import joined,compare,S,segments
old=joined(S.parent/'mercado-b-refinado/MERCADO_4_A4.pdf');new=joined(S/'MERCADO_4_A4.pdf')
def crop(doc,box,scale=2):
 p=doc[0].get_pixmap(matrix=fitz.Matrix(scale,scale),clip=fitz.Rect(*[v*mm for v in box]),alpha=False)
 return Image.frombytes('RGB',(p.width,p.height),p.samples)
for name,box in [('Z15_Z16',[390,307,441,358]),('REFRIGERADORES',[0,225,115,380]),('JUNCAO_ARTISTICA',[350,285,402,375])]:
 compare([('B refinado / atual',crop(old,box)),('Pós-apocalíptico / PDF final',crop(new,box))],S/f'provas/{name}_ANTES_DEPOIS.jpg')
 crop(new,box).save(S/'provas/JUNCAO_ARTISTICA_FINAL.png')
# Centros das 21 passagens; quadros verdes são somente marcação de inspeção.
art=fitz.open(S/'fontes/MERCADO_ARTE_VETOR.pdf');out=Image.new('RGB',(1500,1050),'#eee7d5');d=ImageDraw.Draw(out);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for i,s in enumerate(v for v in segments() if v['connected']):
 x,y=s['center'];y=380-y;box=[x-18,y-18,x+18,y+18];im=crop(art,box);im=im.resize((190,190));dd=ImageDraw.Draw(im);dd.rectangle((58,58,132,132),outline='#00a968',width=2)
 X=(i%7)*214;Y=(i//7)*345;out.paste(im,(X,Y+30));d.text((X+5,Y+5),str(s['key']),font=f,fill='black')
out.save(S/'provas/CONEXOES_21.jpg',quality=95)
# Manifesto resolve todos os caminhos nativos e registra SHA-256.
r=json.loads((S/'fontes/resolucao.json').read_text())
for x in r['sources']:
 p=S/x['file'];x['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();x['origin']='image_gen integrado / reconstrução ou edição nativa'
(S/'ASSET_MANIFEST.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
assert json.loads((S/'fontes/geometria.json').read_text())==json.loads((S.parent/'mercado-b-refinado/fontes/geometria.json').read_text())
assert all(min(x['effective_ppi_xy'])>=150 and not x['upscaled'] for x in r['sources'])
print('Fontes nativas:',len(r['sources']),'ppi mínimo',min(min(x['effective_ppi_xy']) for x in r['sources']))

# Diagnóstico em cinza do PDF final, sem alterar a arte distribuída.
full=crop(new,[0,0,554,380],1)
full.convert('L').save(S/'provas/CONTRASTE_CINZA.png')
crop(new,[0,215,100,315],2).save(S/'provas/SANGUE_DESGASTE.png')
crop(new,[390,307,441,358],2).save(S/'provas/PASSAGEM_LIVRE.png')
crop(new,[150,40,220,100],2).save(S/'provas/JUNCAO_ACESSO.png')
