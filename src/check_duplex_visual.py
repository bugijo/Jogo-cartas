from pathlib import Path
import json
import fitz
from PIL import Image,ImageChops,ImageStat
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-ilustrada-v0.3';MM=72/25.4
m=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());d=json.loads((P/'content/catalog.json').read_text());cards={c['id']:c for c in d['cards']};records=[]
for edition in ['ilustrada','economica']:
 doc=fitz.open(O/edition/'01_inicial/02_cartas_duplex.pdf');reference=None;maxdiff=0;n=0
 for i,id in enumerate(m['initial_cards']):
  if cards[id]['family']!='INT':continue
  row,col=divmod(i%9,3);col=2-col;clip=fitz.Rect((8.5+col*65)*MM,(14.5+row*90)*MM,(71.5+col*65)*MM,(102.5+row*90)*MM)
  normalized=fitz.open();p=normalized.new_page(width=63*MM,height=88*MM);p.show_pdf_page(p.rect,doc,i//9*2+1,clip=clip)
  pix=p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  if reference is None:reference=im
  delta=sum(ImageStat.Stat(ImageChops.difference(reference,im)).mean)/3;maxdiff=max(maxdiff,delta);n+=1
 records.append(dict(edition=edition,intentions=n,maximum_mean_pixel_difference=maxdiff,identical_layout_and_content=maxdiff<.6,threshold=.6,reason='Subpixel rasterization can differ across original positions; maximum average difference in RGB 0..255.'))
 assert n==12 and maxdiff<.6,records[-1]
(O/'duplex_visual.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print(records)
