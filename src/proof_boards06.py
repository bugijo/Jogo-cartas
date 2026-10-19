"""Provas derivadas dos PDFs A4 distribuídos, sem substituir o componente por mockup."""
from pathlib import Path
import json,io,gzip,argparse
import fitz
from PIL import Image,ImageDraw,ImageFont
import build_boards06 as b
P=b.P;O=b.O;E=O/'evidencias';MM=72/25.4;E.mkdir(parents=True,exist_ok=True)
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def joined(path):
 src=fitz.open(path);doc=fitz.open();page=doc.new_page(width=554*MM,height=380*MM)
 for i in range(4):
  x=i%2*277;y=i//2*190;page.show_pdf_page(fitz.Rect(x*MM,y*MM,(x+277)*MM,(y+190)*MM),src,i,clip=fitz.Rect(10*MM,10*MM,287*MM,200*MM))
 return doc
def raster(doc,path,scale=.9):
 pix=doc[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);pix.save(path)
 return Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
def compare(items,out,cell=(800,575)):
 im=Image.new('RGB',(cell[0]*len(items),cell[1]),'#e7e3d5');draw=ImageDraw.Draw(im)
 for i,(label,img) in enumerate(items):
  img=img.copy();img.thumbnail((cell[0]-20,cell[1]-50));im.paste(img,(i*cell[0]+10,42));draw.text((i*cell[0]+12,8),label,font=FONT,fill='#29483d')
 im.save(out,quality=93)
def a4_template(title,lines=(),landscape=True):
 from reportlab.pdfgen import canvas
 from reportlab.lib.pagesizes import A4,landscape as orient
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=orient(A4) if landscape else A4,invariant=1);h=210 if landscape else 297
 c.saveState();c.scale(MM,MM);b.art.ECON=False;b.text(c,title,10,h-13,14,True)
 for i,s in enumerate(lines):b.text(c,s,10,h-22-i*6,8.5)
 c.restoreState();c.save();return fitz.open(stream=buf.getvalue(),filetype='pdf')

def make(pilot=False):
 roots=[P/'output/edicao-fabricacao-v0.4/ilustrada',b.BASE/'ilustrada',O/'ilustrada'];theme_images={};docs={}
 for theme in (['Mercado'] if pilot else ['Comuns']+[m['name'] for m in b.MAPS]):
  rel=('06_TABULEIROS/' if theme=='Comuns' else '08_EXTRAS_OPCIONAIS/')+b.KEYS[theme]+'_M01_M04_LADO_A.pdf'
  doc=joined(O/'ilustrada'/rel);docs[theme]=doc;theme_images[theme]=raster(doc,E/(b.KEYS[theme]+'_MONTADO.png'))
  if not pilot:
   gray=joined(O/'economica'/rel);raster(gray,E/(b.KEYS[theme]+'_ECONOMICO_MONTADO.png'))
 market=[]
 for root,label in zip(roots,['0.4 / cenas quadradas','0.5 / planta contínua','0.6 / setores e ambiente']):
  if not (root/'08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf').exists():continue
  doc=joined(root/'08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf');pix=doc[0].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False);market.append((label,Image.frombytes('RGB',(pix.width,pix.height),pix.samples)))
 compare(market,E/'MERCADO_04_05_06.jpg',(750,545))
 if pilot:return
 # Todos os mapas, exatamente como montados a partir de quatro folhas finais.
 out=Image.new('RGB',(2100,3*515),'#e7e3d5');d=ImageDraw.Draw(out)
 for i,(theme,img) in enumerate(theme_images.items()):
  im=img.copy();im.thumbnail((680,470));x=i%3*700;y=i//3*515;out.paste(im,(x+10,y+35));d.text((x+10,y+4),theme,font=FONT,fill='#29483d')
 out.save(E/'TODOS_MAPAS_MONTADOS.jpg',quality=93)
 rel='08_EXTRAS_OPCIONAIS/OFICINA_M01_M04_LADO_A.pdf';old=joined(b.BASE/'ilustrada'/rel);pix=old[0].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
 compare([('Oficina / 0.5',Image.frombytes('RGB',(pix.width,pix.height),pix.samples)),('Oficina / 0.6',theme_images['Oficina'])],E/'OFICINA_05_06.jpg')
 # Zoom da emenda real entre as quatro folhas, extraído do tabuleiro remontado.
 market=docs['Mercado'];clip=fitz.Rect(207*MM,135*MM,347*MM,245*MM);pix=market[0].get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False);pix.save(E/'JUNCAO_CENTRAL.png')
 proof=a4_template('DETALHES REAIS / A4 / ESCALA 100%', ['Duas áreas de 100×100 mm extraídas dos PDFs finais. Não ajustar à página.'],False)
 for target,clip in [(fitz.Rect(55*MM,37*MM,155*MM,137*MM),fitz.Rect(20*MM,205*MM,120*MM,305*MM)),(fitz.Rect(55*MM,165*MM,155*MM,265*MM),fitz.Rect(227*MM,140*MM,327*MM,240*MM))]:proof[0].show_pdf_page(target,market,0,clip=clip)
 proof.save(E/'DETALHE_ESCALA_FISICA_A4.pdf',garbage=4,deflate=True);raster(proof,E/'DETALHE_ESCALA_FISICA_A4.png',1)
 # Encaixe digital: comparar a remontagem dos quatro PDFs com a cena fonte.
 seams=[]
 from PIL import ImageChops,ImageStat
 for theme,doc in docs.items():
  full=fitz.open(O/'fontes_tabuleiros/ilustrada'/(b.KEYS[theme]+'.pdf'));a=doc[0].get_pixmap(matrix=fitz.Matrix(.4,.4),alpha=False);z=full[0].get_pixmap(matrix=fitz.Matrix(.4,.4),alpha=False)
  im1=Image.frombytes('RGB',(a.width,a.height),a.samples);im2=Image.frombytes('RGB',(z.width,z.height),z.samples)
  diff=sum(ImageStat.Stat(ImageChops.difference(im1,im2)).mean)/3;seams.append(dict(theme=theme,mean_difference_0_255=diff,passed=diff<1.0))
 (O/'encaixe.json').write_text(json.dumps(seams,ensure_ascii=False,indent=2));assert all(v['passed'] for v in seams),seams
 # Simulação superior de ocupação máxima: bases existentes de 22×12 mm, não peças novas.
 from reportlab.pdfgen import canvas
 from reportlab.lib.pagesizes import A4,landscape
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=landscape(A4),invariant=1);c.saveState();c.scale(MM,MM)
 b.text(c,'OCUPAÇÃO MÁXIMA / VISTA SUPERIOR DAS BASES',10,197,14,True)
 b.text(c,'24 inimigos + 6 heróis. Bases reais de 22×12 mm; sem diminuir o limite ou aumentar a zona.',10,187,8.5)
 for i in range(30):
  col,row=i%6,i//6;x=13.25+22*col;y=67+12*row;b.art.rect(c,x,y,22,12,'#f4efde' if i>=24 else '#d6d0b9','#526b5b',.5);b.text(c,f'E{i+1:02}' if i<24 else ['Lia','Ivo','Mara','Caio','Nara','Bento'][i-24],x+2,y+4,7,True)
 for i,s in enumerate(['Z7 em escala real: 138,5×95 mm.','As figuras ficam verticais; aqui vemos as bases.','A decoração pode ficar sob os peões: não é obstáculo.','Na faixa superior, números e objetivo ficam visíveis.','','À direita: frente original de um peão (22×58 mm).','Abaixo: marcador plano original (29×29 mm).','São alternativas de representação, não IDs extras.','','Simulação digital; não comprova montagem física.']):b.text(c,s,160,160-i*7,8)
 c.restoreState();c.save();proof=fitz.open(stream=buf.getvalue(),filetype='pdf')
 # Zone goes behind the base schematic: overlay=False.
 proof[0].show_pdf_page(fitz.Rect(10*MM,54*MM,148.5*MM,149*MM),market,0,clip=fitz.Rect(277*MM,95*MM,415.5*MM,190*MM),overlay=False)
 hero=fitz.open(O/'ilustrada/04_PERSONAGENS_E_INIMIGOS/HEROIS_24_RECORTAR.pdf');proof[0].show_pdf_page(fitz.Rect(242*MM,44*MM,264*MM,102*MM),hero,0,clip=fitz.Rect(19*MM,78*MM,41*MM,136*MM))
 markers=fitz.open(O/'ilustrada/07_MARCADORES_E_DIVISORIAS/MARCADORES_INICIAIS.pdf');proof[0].show_pdf_page(fitz.Rect(242*MM,125*MM,271*MM,154*MM),markers,0,clip=fitz.Rect(74*MM,18*MM,103*MM,47*MM))
 proof.save(E/'ZONA_OCUPADA_A4.pdf',garbage=4,deflate=True);raster(proof,E/'ZONA_OCUPADA.png',1.4)
 # Geometria editável separada. A cena completa é reproduzida pelo código/JSON e PNGs nativos.
 folder=P/'assets/v0.6/vetores';folder.mkdir(exist_ok=True)
 for theme in docs:
  ref=fitz.open(O/'plantas_funcionais/ilustrada'/(b.KEYS[theme]+'.pdf'));(folder/(b.KEYS[theme]+'_GEOMETRIA.svgz')).write_bytes(gzip.compress(ref[0].get_svg_image(text_as_path=False).encode()))
 html='<!doctype html><meta charset="utf-8"><title>Zona Zero 0.6 / provas</title><style>body{font:18px sans-serif;max-width:1400px;margin:2em auto}img{max-width:100%}</style><h1>Provas dos PDFs finais</h1><p>Revisão digital, sem impressão física. Capturas não são componentes obrigatórios.</p>'
 for f in sorted(E.glob('*.jpg')):html+='<h2>'+f.stem+'</h2><a href="'+f.name+'"><img src="'+f.name+'"></a>'
 for f in sorted(E.glob('*.png')):html+='<p><a href="'+f.name+'">'+f.stem+'</a></p>'
 (E/'ABRA_AS_PROVAS.html').write_text(html)
 print('Provas:',len(list(E.iterdir())),'/ sete encaixes conferidos.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');make(p.parse_args().pilot)
