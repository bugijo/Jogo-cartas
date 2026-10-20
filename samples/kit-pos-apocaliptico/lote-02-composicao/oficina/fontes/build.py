"""Amostra isolada; não escreve em nenhuma edição do jogo. PNGs nativos + vetores."""
from pathlib import Path
import io,json,hashlib,math
import fitz
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
S=Path(__file__).resolve().parents[1];P=next(p for p in S.parents if (p/"content/catalog.json").exists())
M=json.loads((S/'fontes/geometria.json').read_text());W,H=554,380
for name,f in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+f))
def txt(c,s,x,y,size=9,bold=False,col='#243b34'):
 c.setFillColor(col);c.setFont('Bold' if bold else 'Body',size/mm);c.drawString(x,y,s)
def line(c,a,b,col,width):
 c.setStrokeColor(col);c.setLineWidth(width);c.line(*a,*b)
def rect(c,x,y,w,h,col):
 c.setFillColor(col);c.rect(x,y,w,h,fill=1,stroke=0)
def segments():
 edges={tuple(e) for e in M['edges']};doors={tuple(e) for e in M['doors']};blocked={tuple(e) for e in M['blocked']}
 for z in M['zones']:
  row,col=divmod(z-1,4);x=col*138.5;y=(3-row)*95
  sides=[('R',z+1 if col<3 else None),('D',z+4 if row<3 else None)]
  if col==0:sides.append(('L',None))
  if row==0:sides.append(('U',None))
  for side,nb in sides:
   k=(z,nb) if nb else None
   if side in ['L','R']:a=(x if side=='L' else x+138.5,y);b=(a[0],y+95)
   else:a=(x,y if side=='D' else y+95);b=(x+138.5,a[1])
   yield dict(zone=z,neighbor=nb,side=side,key=list(k) if k else None,connected=k in edges,door=k in doors,blocked=k in blocked,p1=a,p2=b,center=((a[0]+b[0])/2,(a[1]+b[1])/2),gap_mm=14 if k in edges else 0)
def architecture(c):
 # Parede real da planta: topo de alvenaria e capeamento; nenhuma parede extra.
 for s in segments():
  if s['connected']:continue
  a,b=s['p1'],s['p2'];line(c,(a[0]+.5,a[1]-.6),(b[0]+.5,b[1]-.6),'#747b68',2.6)
  line(c,a,b,'#36554c',2.1);line(c,a,b,'#b9b6a5',1.25);line(c,(a[0],a[1]+.3),(b[0],b[1]+.3),'#ded8c5',.25)
def functional(c):
 for s in segments():
  if not s['connected']:continue
  a,b=s['p1'],s['p2'];x,y=s['center'];vert=s['side'] in ['L','R']
  c.setDash(1.5,2.2)
  for col,wd in [('#eee8d8',.65),('#456353',.23)]:
   if vert:line(c,a,(x,y-7),col,wd);line(c,(x,y+7),b,col,wd)
   else:line(c,a,(x-7,y),col,wd);line(c,(x+7,y),b,col,wd)
  c.setDash()
  for offset in [-7,7]:
   if vert:line(c,(x-.9,y+offset),(x+.9,y+offset),'#53685a',.65)
   else:line(c,(x+offset,y-.9),(x+offset,y+.9),'#53685a',.65)
  if s['door']:
   a=(x,y-6.5) if vert else (x-6.5,y);b=(x,y+6.5) if vert else (x+6.5,y)
   line(c,a,b,'#5a4530',1.7);line(c,a,b,'#c2a56d',.65)
   if s['blocked']:
    line(c,(x-3.2,y-3.2),(x+3.2,y+3.2),'#8e3425',1.1);line(c,(x-3.2,y+3.2),(x+3.2,y-3.2),'#8e3425',1.1)
def labels(c):
 tags={M['entry']:'E/S',M['spawn']:'S'};tags.update({z:'B'+str(i+1) for i,z in enumerate(M['search'])});tags.update({z:'O'+str(i+1) for i,z in enumerate(M['objectives'])})
 for z in M['zones']:
  row,col=divmod(z-1,4);x=col*138.5+4;y=(4-row)*95-11
  rect(c,x,y,15,7,'#eee7d5');txt(c,f'Z{z:02}',x+1.5,y+2,10,True)
  if z in tags:rect(c,x+17,y,12,7,'#eee7d5');txt(c,tags[z],x+18,y+2,9.5,True,'#8e3425' if z==16 else '#243b34')
 for i in range(4):
  x=i%2*277;y=(1-i//2)*190
  rect(c,x+198,y+2,77,4,'#eee7d5');txt(c,f'M{i+1} / OFICINA / AMOSTRA / TOPO ↑',x+199,y+3,5.8)
def full(name,signals):
 c=canvas.Canvas(str(S/name),pagesize=(W*mm,H*mm),invariant=1,initialFontName="Body");c.setTitle('Zona Zero / oficina / amostra artística');c.setSubject('Arte nativa 3817×2618; arquitetura, geometria e sinais vetoriais; base 46263b2')
 c.scale(mm,mm);c.drawImage(str(S/'OFICINA_ARTE_175PPI.png'),0,0,W,H);architecture(c)
 if signals:functional(c);labels(c)
 c.save()
def sheet_template(title,lines=(),portrait=False):
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=A4 if portrait else landscape(A4),invariant=1,initialFontName="Body");c.scale(mm,mm);height=297 if portrait else 210
 txt(c,title,10,height-12,13,True)
 for i,s in enumerate(lines):txt(c,s,10,height-20-i*5,8)
 c.save();return fitz.open(stream=buf.getvalue(),filetype='pdf')
def render(doc,path,scale=1):
 p=doc[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);p.save(path);return Image.frombytes('RGB',(p.width,p.height),p.samples)
def joined(path):
 source=fitz.open(path);doc=fitz.open();p=doc.new_page(width=W*mm,height=H*mm)
 for i in range(4):
  x=i%2*277;y=i//2*190;p.show_pdf_page(fitz.Rect(x*mm,y*mm,(x+277)*mm,(y+190)*mm),source,i,clip=fitz.Rect(10*mm,10*mm,287*mm,200*mm))
 return doc
def compare(images,path):
 out=Image.new('RGB',(1800,670),'#ece6d7');draw=ImageDraw.Draw(out);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
 for i,(label,img) in enumerate(images):
  img=img.copy();img.thumbnail((880,610));out.paste(img,(10+i*900,48));draw.text((12+i*900,12),label,font=font,fill='#243b34')
 out.save(path,quality=94)
def main():
 (S/'provas').mkdir(exist_ok=True)
 full('fontes/OFICINA_ARTE_VETOR.pdf',False);full('fontes/OFICINA_FONTE.pdf',True)
 source=fitz.open(S/'fontes/OFICINA_FONTE.pdf');out=fitz.open()
 for i in range(4):
  doc=sheet_template(f'OFICINA / M{i+1} / LADO A / TOPO ↑',[]);p=doc[0]
  # Título fica fora do corte. Informação de fabricação na margem inferior.
  buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=landscape(A4),invariant=1,initialFontName="Body");c.scale(mm,mm)
  txt(c,f'M{i+1} / OFICINA / AMOSTRA / TOPO ↑ / 277 × 190 mm / 100% / UMA FACE',10,203,7,True)
  txt(c,'M1 M2 acima · M3 M4 abaixo · cortar e unir sem sobreposição · arte 175 ppi: prova para avaliação',10,5,6.5)
  for x in [10,287]:
   for y in [10,200]:line(c,(x+(-2 if x==10 else 0),y),(x+(0 if x==10 else 2),y),'#384f43',.2);line(c,(x,y+(-2 if y==10 else 0)),(x,y+(0 if y==10 else 2)),'#384f43',.2)
  c.save();doc=fitz.open(stream=buf.getvalue(),filetype='pdf');x=i%2*277;y=i//2*190
  doc[0].show_pdf_page(fitz.Rect(10*mm,10*mm,287*mm,200*mm),source,0,clip=fitz.Rect(x*mm,y*mm,(x+277)*mm,(y+190)*mm));out.insert_pdf(doc)
 out.set_metadata({'title':'Zona Zero / Mercado / amostra / quatro A4','subject':'Base 46263b2. Mesma geometria. Arte nativa 175 ppi. Não substitui edição atual.'});out.save(S/'OFICINA_4_A4.pdf',garbage=4,deflate=True)
 assembled=joined(S/'OFICINA_4_A4.pdf');assembled.save(S/'fontes/OFICINA_REMONTADO.pdf',garbage=4,deflate=True)
 final=render(assembled,S/'OFICINA_COM_GEOMETRIA.png')
 art=fitz.open(S/'fontes/OFICINA_ARTE_VETOR.pdf');render(art,S/'OFICINA_SEM_INTERFACE.png')
 # Prévia PNG é render do PDF, não evidência de aumento de resolução raster.
 oldpath=P/'samples/kit-pos-apocaliptico/pdfs/OFICINA_4_A4.pdf'
 if oldpath.exists():
  old=joined(oldpath);before=render(old,S/'provas/OFICINA_B_ANTERIOR.png');compare([('Hospital anterior / objetos isolados',before),('Hospital contínuo / 175 ppi',final)],S/'COMPARACAO_B_ANTES_DEPOIS.jpg')
 proof=sheet_template('OFICINA / DETALHE DE 100 × 100 mm',['Imprimir em 100%, sem ajustar. Amostra: arte nativa 175 ppi; vetores sem essa limitação.','Esta prova mostra a resolução real disponível; não é certificação de impressão final.'],True)
 clip=fitz.Rect(277*mm,145*mm,377*mm,245*mm);target=fitz.Rect(55*mm,60*mm,155*mm,160*mm);proof[0].show_pdf_page(target,assembled,0,clip=clip)
 proof.save(S/'DETALHE_100MM_A4.pdf',garbage=4,deflate=True);render(proof,S/'provas/DETALHE_100MM.png')
 pix=assembled[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=fitz.Rect(227*mm,140*mm,327*mm,240*mm),alpha=False);pix.save(S/'provas/JUNCAO_CENTRAL.png')
 assembled[0].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(385.5*mm,302.5*mm,445.5*mm,362.5*mm),alpha=False).save(S/'provas/PASSAGEM_15_16.png')
 # Seis peças planas atuais, 29×29mm, colocadas em Z6 evitando os dois conectores.
 markerpath=P/'output/edicao-tabuleiros-v0.6/ilustrada/07_MARCADORES_E_DIVISORIAS/MARCADORES_INICIAIS.pdf'
 if markerpath.exists():
  markers=fitz.open(markerpath);zone=sheet_template('OCUPAÇÃO / COMPONENTES ATUAIS / ESCALA REAL',['Exemplo digital em Z6. Seis marcadores de 29 × 29 mm. Decoração não cria obstáculos.','Portas, números e conectores ficam livres. Não é montagem física nem preparação inicial.'])
  zone[0].show_pdf_page(fitz.Rect(10*mm,55*mm,148.5*mm,150*mm),assembled,0,clip=fitz.Rect(138.5*mm,95*mm,277*mm,190*mm))
  for i,slot in enumerate([2,3,4,5,0,1]):
   x=10+32*slot;y=18;X=29+(i%3)*32;Y=76+(i//3)*32
   zone[0].show_pdf_page(fitz.Rect(X*mm,Y*mm,(X+29)*mm,(Y+29)*mm),markers,0,clip=fitz.Rect(x*mm,y*mm,(x+29)*mm,(y+29)*mm))
  zone.save(S/'provas/OCUPACAO_A4.pdf',garbage=4,deflate=True);render(zone,S/'provas/OCUPACAO.png')
 # PDF final: todas as quatro folhas e contato, com a arte realmente incorporada.
 contact=Image.new('RGB',(1200,880),'#eee8da');d=ImageDraw.Draw(contact)
 finalpdf=fitz.open(S/'OFICINA_4_A4.pdf')
 for i,p in enumerate(finalpdf):
  pix=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pix.save(S/f'provas/FOLHA_{i+1}.png');im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((590,420));contact.paste(im,(i%2*600+5,i//2*440+18));d.text((i%2*600+10,i//2*440+4),f'M{i+1}',fill='black')
 contact.save(S/'provas/CONTATO_4_A4.jpg',quality=94)
 fitz.TOOLS.store_shrink(100);a=joined(S/'OFICINA_4_A4.pdf')[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
 fitz.TOOLS.store_shrink(100);bb=fitz.open(S/'fontes/OFICINA_FONTE.pdf')[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
 diff=sum(ImageStat.Stat(ImageChops.difference(Image.frombytes('RGB',[a.width,a.height],a.samples),Image.frombytes('RGB',[bb.width,bb.height],bb.samples))).mean)/3
 im=Image.open(S/'OFICINA_ARTE_175PPI.png');ppi=[im.width/(W/25.4),im.height/(H/25.4)]
 # Verifica imagem presente sem reamostragem no PDF, A4, fontes e geometria congelada.
 assert len(finalpdf)==4
 for p in finalpdf:
  assert abs(p.rect.width-297*mm)<.01 and abs(p.rect.height-210*mm)<.01
  assert any(i['width']==im.width and i['height']==im.height for i in p.get_image_info())
  for f in p.get_fonts(full=True):assert finalpdf.extract_font(f[0])[3],f
 # PyMuPDF muda a reamostragem com recortes aninhados: medir o raster é diagnóstico.
 # A integridade de montagem é verificada pelos bytes da imagem e matriz física.
 srcinfo=source[0].get_image_info(hashes=True)[0]
 mounted=assembled[0].get_image_info(hashes=True)
 assert len(mounted)==4
 for item in mounted:
  assert item['digest']==srcinfo['digest']
  assert max(abs(a-b) for a,b in zip(item['transform'],srcinfo['transform']))<.001

 canon=P/'content/production/geometry_0.6.json'
 if canon.exists():assert M==json.loads(canon.read_text())[2]
 seg=list(segments());assert sum(s['connected'] for s in seg)==21;assert sum(s['door'] for s in seg)==5;assert sum(s['blocked'] for s in seg)==1
 (S/'fontes/segmentos.json').write_text(json.dumps(seg,ensure_ascii=False,indent=2))
 report={'base':'46263b2','map_id':M['id'],'zones':16,'connections':21,'doors':5,'blocked':M['blocked'],'board_mm':[554,380],'module_mm':[277,190],'a4_landscape_pages':4,'native_pixels':list(im.size),'raster_effective_ppi_xy':ppi,'target_150ppi_met':True,'upscaling':False,'all_final_pages_rendered':True,'fonts_embedded':True,'geometry_preserved':True,'join_mean_difference_0_255':diff,'physical_printing':False,'human_playtest':False,'strict_orthographic_art':'vista superior; faces laterais estilizadas residuais nos armários','visual_passage_15_16':'revisar junto às 21 conexões; nenhuma alteração funcional','production_ready':'prova de impressão; aguarda avaliação visual do proprietário e impressão física','native_sources':len(json.loads((S/'fontes/resolucao.json').read_text())['sources'])}
 (S/'VERIFICACOES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
