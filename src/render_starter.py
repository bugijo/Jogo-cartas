from pathlib import Path
import json
import fitz
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];R=P/'output/comece-aqui-duas-pessoas';V=R/'conferencia';M=json.loads((R/'manifesto.json').read_text());files=[]
for entry in M['initial']+M['supplement']:
 doc=fitz.open(R/entry['file']);prefix=Path(entry['file']).parts[0]+'_'+Path(entry['file']).stem
 for page in doc:
  path=V/f'{prefix}_{page.number+1:02}.png';page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(path);files.append(path)
for offset in range(0,len(files),24):
 sheet=Image.new('RGB',(1200,1500),'#d9dcd9');draw=ImageDraw.Draw(sheet)
 for k,path in enumerate(files[offset:offset+24]):
  im=Image.open(path);im.thumbnail((280,220));x=(k%4)*300+7;y=(k//4)*250+8;sheet.paste(im,(x,y));draw.text((x,y+225),path.stem[-37:],fill='black')
 sheet.save(V/f'contato_{1+offset//24:02}.jpg',quality=86)
(V/'paginas_renderizadas.json').write_text(json.dumps([str(f.relative_to(R)) for f in files],indent=2));print('Renderizadas',len(files),'páginas do kit')
