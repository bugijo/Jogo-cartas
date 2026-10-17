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
# Preview assembled from actual cut areas, no overlap. Not proof of physical printing.
doc=fitz.open(O/'06_mapas_modulos.pdf');unit=72/25.4
pieces=[]
for page in doc:
 pix=page.get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(10*unit,10*unit,287*unit,200*unit),alpha=False)
 pieces.append(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
tw,th=pieces[0].size;assembled=Image.new('RGB',(2*tw,2*th),'white')
for i,piece in enumerate(pieces):assembled.paste(piece,((i%2)*tw,(i//2)*th))
assembled.save(V/'mapa_montado.png')
