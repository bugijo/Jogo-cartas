"""Evidências digitais. Os PDFs de prova não são componentes para imprimir."""
from pathlib import Path
import fitz,sys,math,json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-fabricacao-v0.4';R=O/'ilustrada';E=O/'evidencias';E.mkdir(exist_ok=True);MM=72/25.4
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
for i,card_index in enumerate([24,26,27,28]):
 sn,k=divmod(card_index,9);x=277+5+68*i;y=26;col=k%3;row=k//3;p.show_pdf_page(fitz.Rect(x*MM,y*MM,(x+63)*MM,(y+88)*MM),cards,2*sn,clip=fitz.Rect((8.5+65*col)*MM,(14.5+90*row)*MM,(71.5+65*col)*MM,(102.5+90*row)*MM))
render(v,E/'PAINEL_COM_CARTAS_REAIS.png',1)
# Duplex evidence: original fronts above backs, physical orientation explained by labels.
dup=fitz.open(O/'amostras/AMOSTRA_CARTAS_DUPLEX.pdf');render(dup,E/'CARTAS_FRENTES.png',1.2)
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
pairs=[('MAPA',P/'output/edicao-ilustrada-v0.3/ilustrada/extras/mapa_mercado.pdf',E/'MERCADO_M01_M04_LADO_A_MONTADO.png'),('CARTAS',P/'output/edicao-ilustrada-v0.3/ilustrada/01_inicial/02_cartas_duplex.pdf',E/'CARTAS_FRENTES.png'),('ABRIGO',P/'output/edicao-ilustrada-v0.3/ilustrada/01_inicial/06_paineis_registros.pdf',E/'ABRIGO.png'),('FICHA',P/'output/edicao-ilustrada-v0.3/ilustrada/01_inicial/03_lia_ivo.pdf',E/'PAINEL_COM_CARTAS_REAIS.png')]
for label,old,after in pairs:
 d=fitz.open(old)
 if label=='MAPA':v=join_maps(old,E/'MAPA_ANTES.png');before=Image.open(E/'MAPA_ANTES.png').convert('RGB')
 else:
  pix=d[0].get_pixmap(alpha=False);before=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 after=Image.open(after).convert('RGB');out=Image.new('RGB',(1600,1050),'white');dr=ImageDraw.Draw(out);dr.text((20,10),'ANTES / 0.3',font=font,fill='black');dr.text((820,10),'DEPOIS / 0.4'+(' (preservado)' if label=='ABRIGO' else ''),font=font,fill='black')
 for i,im in enumerate([before,after]):im.thumbnail((775,990));out.paste(im,(i*800+10,50))
 out.save(E/(label+'_ANTES_DEPOIS.jpg'),quality=90)
# Real components montage for final message.
files=['MERCADO_M01_M04_LADO_A_MONTADO.png','CARTAS_FRENTES.png','PEOES_SIMULADOS.png','PAINEL_COM_CARTAS_REAIS.png','ABRIGO.png'];out=Image.new('RGB',(1600,1800),'#eceadd');draw=ImageDraw.Draw(out)
for i,name in enumerate(files):
 im=Image.open(E/name).convert('RGB');im.thumbnail((770,560));x=10+(i%2)*800;y=40+(i//2)*590;out.paste(im,(x,y));draw.text((x,y-27),['Mercado montado','Cartas 63 × 88 mm','Peões (simulação)','Painel com cartas reais','Abrigo preservado'][i],font=font,fill='black')
out.save(E/'COMPONENTES_0.4.jpg',quality=90)
print('Evidências geradas:',len(list(E.iterdir())))
