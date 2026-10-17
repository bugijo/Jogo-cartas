from pathlib import Path
import fitz,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];O=P/'output';V=O/'previews';V.mkdir(exist_ok=True)
files=[]
for f in sorted(O.glob('*.pdf')):
 doc=fitz.open(f)
 for p in doc:
  out=V/f'{f.stem}_{p.number+1:03}.png';p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(out);files.append(out)
# contact sheets are verification artifacts, not edits of generated art.
for n in range(0,len(files),36):
 subset=files[n:n+36];im=Image.new('RGB',(1200,1500),'#d1d4d2');draw=ImageDraw.Draw(im)
 for j,f in enumerate(subset):
  tile=Image.open(f);tile.thumbnail((185,220));x=(j%6)*200+7;y=(j//6)*250+8;im.paste(tile,(x,y));draw.text((x,y+222),f.name[:28],fill='black')
 im.save(V/f'contact_{n//36+1:02}.jpg',quality=85)
(O/'render_manifest.json').write_text(json.dumps([str(f.relative_to(P)) for f in files],indent=2));print('Renderizadas',len(files),'páginas')
