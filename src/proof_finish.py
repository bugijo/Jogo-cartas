"""Evidências digitais. Os PDFs de prova não são componentes para imprimir."""
from pathlib import Path
import fitz,sys,math,json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-acabamento-v0.5';R=O/'ilustrada';E=O/'evidencias';E.mkdir(exist_ok=True);MM=72/25.4
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def render(d,path,scale=1):
 p=d[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);p.save(str(path))
def join_maps(source,out):
 d=fitz.open(source);v=fitz.open();p=v.new_page(width=554*MM,height=380*MM)
 for i in range(4):
  x=(i%2)*277;y=(i//2)*190;p.show_pdf_page(fitz.Rect(x*MM,y*MM,(x+277)*MM,(y+190)*MM),d,i,clip=fitz.Rect(10*MM,10*MM,287*MM,200*MM))
 render(v,out,.8);return v
maps={}
for file in [R/'06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf',*sorted((R/'08_EXTRAS_OPCIONAIS').glob('*_M01_M04_LADO_A.pdf'))]:
 maps[file.stem]=join_maps(file,E/(file.stem+'_MONTADO.png'))
# Two exact panel parts placed alongside one another, original compact sheet and actual vector cards.
src=fitz.open(R/'05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf');v=fitz.open();p=v.new_page(width=554*MM,height=190*MM)
for i in range(2):p.show_pdf_page(fitz.Rect(i*277*MM,0,(i+1)*277*MM,190*MM),src,i,clip=fitz.Rect(10*MM,10*MM,287*MM,200*MM))
p.draw_rect(fitz.Rect(10*MM,17.5*MM,220*MM,166*MM),color=None,fill=(1,1,1));f=fitz.open(R/'05_PAINEIS/FICHAS_LIA_IVO.pdf');p.show_pdf_page(fitz.Rect(10*MM,17.5*MM,220*MM,166*MM),f,0,clip=fitz.Rect(0,0,210*MM,148.5*MM))
cards=fitz.open(R/'02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf')
for i,card_index in enumerate([24,25,26,27]):
 sn,k=divmod(card_index,9);x=277+5+68*i;y=26;col=k%3;row=k//3;p.show_pdf_page(fitz.Rect(x*MM,y*MM,(x+63)*MM,(y+88)*MM),cards,2*sn,clip=fitz.Rect((8.5+65*col)*MM,(14.5+90*row)*MM,(71.5+65*col)*MM,(102.5+90*row)*MM))
p.insert_text((284*MM,162*MM),'Ensaio de medidas; nao representa uma preparacao de partida.',fontsize=9,color=(.15,.25,.2))
render(v,E/'PAINEL_COM_CARTAS_REAIS.png',1)
# Duplex evidence: original fronts above backs, physical orientation explained by labels.
import json
catalog=json.loads((P/'content/catalog.json').read_text());selection=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());cards_by_name={}
for card in catalog['cards']:
 if card['id'] in selection['initial_cards']+selection['supplement_cards']:cards_by_name.setdefault(card['name'],card['id'])
def selected_page(id,root=R,back=False):
 key='initial_cards' if id in selection['initial_cards'] else 'supplement_cards';stem='KIT_INICIAL_1' if key=='initial_cards' else 'KIT_COMPLEMENTO_2';i=selection[key].index(id);sn,k=divmod(i,9);row,col=divmod(k,3);col=2-col if back else col
 doc=fitz.open(root/'02_CARTAS_DUPLEX'/(stem+'_DUPLEX.pdf'));clip=fitz.Rect((8.5+65*col)*MM,(14.5+90*row)*MM,(71.5+65*col)*MM,(102.5+90*row)*MM);return doc,2*sn+int(back),clip
names=['Faca','Bomba','Mercado: Conserva','Jana e criança','Emboscada','Solidário','Arrastar','Bateria','Van de manutenção'];dup=fitz.open()
for back in [False,True]:
 page=dup.new_page(width=210*MM,height=297*MM)
 for k,name in enumerate(names):
  doc,num,clip=selected_page(cards_by_name[name],back=back);row,col=divmod(k,3);col=2-col if back else col;target=fitz.Rect((8.5+65*col)*MM,(14.5+90*row)*MM,(71.5+65*col)*MM,(102.5+90*row)*MM);page.show_pdf_page(target,doc,num,clip=clip)
dup.save(E/'AMOSTRA_EXTRAIDA_PDFS_FINAIS.pdf');render(dup,E/'CARTAS_FRENTES.png',1.2)
v=fitz.open();v.insert_pdf(dup,from_page=1,to_page=1);render(v,E/'CARTAS_VERSOS.png',1.2)
# One-sheet fronts and reverses overlaid using long-edge column reflection to check registration.
pf=dup[0].get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False);pb=dup[1].get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False)
a=Image.frombytes('RGB',(pf.width,pf.height),pf.samples);b=Image.frombytes('RGB',(pb.width,pb.height),pb.samples).transpose(Image.Transpose.FLIP_LEFT_RIGHT);Image.blend(a,b,.5).save(E/'DUPLEX_SOBREPOSTO.png')
# Standees simulated upright using actual front image regions from print nets.
d=fitz.open(R/'04_PERSONAGENS_E_INIMIGOS/HEROIS_24_RECORTAR.pdf');scene=Image.new('RGB',(1200,650),'#ebe9df');draw=ImageDraw.Draw(scene)
for i in range(6):
 x=19+29*i;y=161;clip=fitz.Rect(x*MM,(297-y-58)*MM,(x+22)*MM,(297-y-6)*MM);pix=d[0].get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((140,420));xx=40+i*190;yy=110
 draw.polygon([(xx-12,yy+im.height),(xx+55,yy+im.height+24),(xx+im.width+15,yy+im.height),(xx+55,yy+im.height-16)],fill='#a6ac99',outline='#41534c');scene.paste(im,(xx,yy))
draw.text((25,20),'Simulação digital — base aberta; não é montagem física.',font=font,fill='#243b34');scene.save(E/'PEOES_SIMULADOS.png')
# Proof that 24 enemies + six heroes can be identified in one unchanged zone (no miniature occupancy rules).
scene=Image.new('RGB',(1050,740),'#eee9dc');draw=ImageDraw.Draw(scene);sx=7;draw.rectangle((25,45,25+138.5*sx,45+95*sx),outline='#203d35',width=3)
for i in range(30):
 row,col=divmod(i,6);x=27+col*22*sx;y=48+row*12*sx;draw.rectangle((x,y,x+22*sx-2,y+12*sx-2),outline='#59665a',width=2);draw.text((x+8,y+25),f'E{i+1:02}' if i<24 else f'H{i-23}',font=font,fill='black')
scene.save(E/'BASES_EM_ZONA.png')
# Preserved illustrated shelter.
d=fitz.open(R/'05_PAINEIS/ABRIGO_MORADORES_ESTOQUE.pdf');render(d,E/'ABRIGO.png',1.3)
# Before / after comparison from actual PDFs, not mockups.
pairs=[('MAPA',P/'output/edicao-fabricacao-v0.4/ilustrada/08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf',E/'MERCADO_M01_M04_LADO_A_MONTADO.png'),('ABRIGO',P/'output/edicao-fabricacao-v0.4/ilustrada/05_PAINEIS/ABRIGO_MORADORES_ESTOQUE.pdf',E/'ABRIGO.png')]
for label,old,after in pairs:
 d=fitz.open(old)
 if label=='MAPA':v=join_maps(old,E/'MAPA_ANTES.png');before=Image.open(E/'MAPA_ANTES.png').convert('RGB')
 else:
  pix=d[0].get_pixmap(alpha=False);before=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 after=Image.open(after).convert('RGB');out=Image.new('RGB',(1600,1050),'white');dr=ImageDraw.Draw(out);dr.text((20,10),'ANTES / 0.4',font=font,fill='black');dr.text((820,10),'DEPOIS / 0.5'+(' (preservado)' if label=='ABRIGO' else ''),font=font,fill='black')
 for i,im in enumerate([before,after]):im.thumbnail((775,990));out.paste(im,(i*800+10,50))
 out.save(E/(label+'_ANTES_DEPOIS.jpg'),quality=90)
# Real components montage for final message.
files=['MERCADO_M01_M04_LADO_A_MONTADO.png','CARTAS_FRENTES.png','PEOES_SIMULADOS.png','PAINEL_COM_CARTAS_REAIS.png','ABRIGO.png'];out=Image.new('RGB',(1600,1800),'#eceadd');draw=ImageDraw.Draw(out)
for i,name in enumerate(files):
 im=Image.open(E/name).convert('RGB');im.thumbnail((770,560));x=10+(i%2)*800;y=40+(i//2)*590;out.paste(im,(x,y));draw.text((x,y-27),['Mercado montado','Cartas 63 × 88 mm','Peões (simulação)','Painel com cartas reais','Abrigo preservado'][i],font=font,fill='black')
out.save(E/'COMPONENTES_0.5.jpg',quality=90)
# Global contacts and every assembled map are reproducible from current renders.
for ed in ['ilustrada','economica']:
 files=sorted((O/'renders'/ed).rglob('*.jpg'));out=Image.new('RGB',(1600,240*((len(files)+9)//10)),'#ccc');draw=ImageDraw.Draw(out)
 for i,file in enumerate(files):
  im=Image.open(file);im.thumbnail((152,215));x=i%10*160;y=i//10*240;out.paste(im,(x,y));draw.text((x,y+216),file.stem+' '+file.parent.name[:16],fill='black')
 out.save(E/('CONTATO_GERAL_'+ed+'.jpg'),quality=85)
files=sorted(E.glob('*_MONTADO.png'));out=Image.new('RGB',(2100,500*((len(files)+2)//3)),'#ddd');draw=ImageDraw.Draw(out)
for i,file in enumerate(files):
 im=Image.open(file).convert('RGB');im.thumbnail((690,465));x=i%3*700;y=i//3*500;out.paste(im,(x,y+25));draw.text((x,y+3),file.stem,fill='black')
out.save(E/'TODOS_MAPAS_MONTADOS.jpg',quality=90)
for name,label in [('Faca','ARMA'),('Jana e criança','CARTA_DENSA')]:
 out=Image.new('RGB',(1050,800),'#e7e1d0');draw=ImageDraw.Draw(out)
 for i,root in enumerate([P/'output/edicao-fabricacao-v0.4/ilustrada',R]):
  doc,num,clip=selected_page(cards_by_name[name],root=root);pix=doc[num].get_pixmap(matrix=fitz.Matrix(2.4,2.4),clip=clip,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((500,740));out.paste(im,(i*525+12,50));draw.text((i*525+12,10),'0.4' if i==0 else '0.5',font=font,fill='black')
 out.save(E/(label+'_04_05.jpg'),quality=92)
# Actual A4 card-sheet comparison: same IDs on both sides of the comparison.
old=fitz.open(P/'output/edicao-fabricacao-v0.4/ilustrada/02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf');new=fitz.open(R/'02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf');out=Image.new('RGB',(1500,1100),'white');draw=ImageDraw.Draw(out)
for i,doc in enumerate([old,new]):
 pix=doc[4].get_pixmap(alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((730,1040));out.paste(im,(i*750+10,45));draw.text((i*750+10,10),'0.4' if i==0 else '0.5',font=font,fill='black')
out.save(E/'FOLHA_A4_04_05.jpg',quality=92)
# Two stitched panels and workshop boards, both from real output PDFs.
for label,path,after in [('PAINEL','05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf','PAINEL_COM_CARTAS_REAIS.png'),('OFICINA','08_EXTRAS_OPCIONAIS/OFICINA_M01_M04_LADO_A.pdf','OFICINA_M01_M04_LADO_A_MONTADO.png')]:
 oldpath=P/'output/edicao-fabricacao-v0.4/ilustrada'/path
 if label=='OFICINA':join_maps(oldpath,E/'OFICINA_ANTES.png');before=Image.open(E/'OFICINA_ANTES.png')
 else:before=Image.open(P/'output/edicao-fabricacao-v0.4/evidencias/PAINEL_COM_CARTAS_REAIS.png')
 out=Image.new('RGB',(1600,1000),'white');draw=ImageDraw.Draw(out)
 for i,img in enumerate([before,Image.open(E/after)]):
  img=img.copy().convert('RGB');img.thumbnail((780,940));out.paste(img,(i*800+10,40));draw.text((i*800+10,8),'0.4' if i==0 else '0.5',font=font,fill='black')
 out.save(E/(label+'_04_05.jpg'),quality=92)
# A4 comparison, both square details physically 100×100mm (no enlarged source).
out=fitz.open();page=out.new_page(width=210*MM,height=297*MM)
for i,root in enumerate([P/'output/edicao-fabricacao-v0.4/ilustrada',R]):
 doc=fitz.open(root/'08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf');y=25+i*130;page.show_pdf_page(fitz.Rect(55*MM,y*MM,155*MM,(y+100)*MM),doc,2,clip=fitz.Rect(20*MM,40*MM,120*MM,140*MM));page.insert_text((55*MM,(y-5)*MM),'0.4 / 100 x 100 mm' if i==0 else '0.5 / 100 x 100 mm / vetores',fontsize=11)
page.insert_text((30*MM,285*MM),'100% / sem ajustar. Prova digital; nao comprova impressao fisica.',fontsize=9);out.save(E/'DETALHE_MAPA_ESCALA_REAL_A4.pdf');render(out,E/'DETALHE_MAPA_ESCALA_REAL_A4.png',1.3)
# SVGs keep map drawings editable; no raster background in these files.
svg=P/'assets/v0.5/vetores';svg.mkdir(exist_ok=True)
import gzip
for stem,doc in maps.items():(svg/(stem+'.svgz')).write_bytes(gzip.compress(doc[0].get_svg_image(text_as_path=False).encode(),compresslevel=9))
print('Evidências geradas:',len(list(E.iterdir())))
