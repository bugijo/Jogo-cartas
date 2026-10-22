"""Renderiza contato dos PDFs finais selecionados para revisão visual."""
from pathlib import Path
import fitz
from PIL import Image, ImageOps, ImageDraw
from final_kit_audit import ROOT, run

OUT = ROOT/'kit-final-prova/auditoria'
OUT.mkdir(parents=True, exist_ok=True)
audit = run()
paths = list(dict.fromkeys(x['path'] for category in ('files','maps','conditionals') for x in audit[category]))
tiles=[]
for path in paths:
 doc=fitz.open(ROOT/path)
 for i,page in enumerate(doc):
  pix=page.get_pixmap(matrix=fitz.Matrix(0.75,0.75),alpha=False)
  im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  im.thumbnail((410,320))
  tile=Image.new('RGB',(450,355),'white')
  tile.paste(im,((450-im.width)//2,25))
  ImageDraw.Draw(tile).text((8,6),f'{Path(path).stem[:35]} • {i+1}/{len(doc)}',fill='#142b2c')
  tiles.append(tile)
for start in range(0,len(tiles),16):
 sheet=Image.new('RGB',(1800,1420),'#e8e5de')
 for j,tile in enumerate(tiles[start:start+16]):sheet.paste(tile,((j%4)*450,(j//4)*355))
 sheet.save(OUT/f'CONTATO_FINAIS_{start//16+1:02}.jpg',quality=86)
print(f'{len(tiles)} páginas renderizadas; {((len(tiles)+15)//16)} folhas de contato')
