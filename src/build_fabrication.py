"""Fabricação 0.4: fontes novas, catálogo/regras e geradores anteriores preservados."""
from pathlib import Path
import json,math,copy,hashlib,shutil,argparse
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
import build_illustrated as q
import production_geometry as g
P=q.P;O=P/'output/edicao-fabricacao-v0.4';BASE=P/'output/edicao-ilustrada-v0.3';M=q.M;D=q.D;a=q.a;b=q.b
PAIRS=[];LAYOUT=[];FILES=[];MAP_GEOMETRY=[]
DIRS=['00_LEIA_PRIMEIRO','01_GUIA_E_REGRAS','02_CARTAS_DUPLEX','03_CARTAS_RECORTAR_E_COLAR','04_PERSONAGENS_E_INIMIGOS','05_PAINEIS','06_TABULEIROS','07_MARCADORES_E_DIVISORIAS','08_EXTRAS_OPCIONAIS','09_FONTES_EDITAVEIS','10_VERIFICACOES']

def art_for_print(art):
 art=art.copy();name=Path(art['path']).name
 if 'crop' not in art and name in q.REGIONS:
  cols,rows=q.REGIONS[name];l,r=cols[art.get('col',0)];t,bot=rows[art.get('row',0)];art['crop']=[l,t,r,bot]
 if not a.ECON:return art
 from PIL import Image,ImageOps
 path=P/art['path'];out=P/'assets/v0.4/economica'/path.name
 if out not in q.DERIVED:
  out.parent.mkdir(parents=True,exist_ok=True);src=Image.open(path);im=ImageOps.grayscale(src).point(lambda v:min(255,int(v*.78+56.1)))
  if src.mode=='RGBA':im=Image.merge('LA',(im,src.getchannel('A')))
  im.save(out);q.DERIVED.add(out)
 art['path']=str(out.relative_to(P));return art
q.art_for_print=art_for_print

def init(root):
 for d in DIRS:(root/d).mkdir(parents=True,exist_ok=True)

def para(c,text,x,y,w,h,size=10,bold=False,label=''):
 q.paragraph(c,text,x,y,w,h,size,bold,label)
 LAYOUT.append(dict(file=q.LABEL,page=q.PAGE,label=label,x=x,y=y,w=w,h=h,size=size,text=text))

def title(c,t,sub='',W=210,H=297):q.heading(c,t,sub,W,H)
def txt(*args,**kwargs):q.txt(*args,**kwargs)

def record(root,f,kind,stage='initial',duplex=False,optional=False,replaces=None,method='both',copies=1):
 d=fitz.open(f);FILES.append(dict(file=str(f.relative_to(root)),kind=kind,stage=stage,duplex=duplex,method=method,optional=optional,replaces=replaces,copies=copies,pages=len(d),sheets=math.ceil(len(d)/2)*copies if duplex else len(d)*copies,orientation='paisagem' if d[0].rect.width>d[0].rect.height else 'retrato',size='A4 210×297 mm',turn='borda longa' if duplex else None,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))

def effect(card,initial=False):return card['text'].replace('ceil(H/2)','1') if initial else card['text']

ITEM_ART={'Conserva':('a',0),'Água':('a',1),'Carne':('a',2),'Medicamento':('a',3),'Munição':('a',4),'Material':('a',5),'Bateria':('b',0),'Conexões':('b',1),'Kit de instalação médica':('b',2),'Bancada':('b',3),'Combustível':('b',4),'Madeira':('b',5)}
def artwork(c,card,x,y,w,h):
 # Same canonical original artwork, mapped uniformly to the requested area.
 name=card['name'].split(': ')[-1]
 if name in ITEM_ART:
  sheet,i=ITEM_ART[name];art=dict(path='assets/v0.4/itens_'+sheet+'.png',col=i%3,row=i//3,cols=3,rows=2);q.raster(c,tight_body(art),x,y,w,h);return
 if card['family']=='MOR':
  heroes=[hero for hero in D['heroes'] if hero['name'] in card['name']]
  for i,hero in enumerate(heroes):q.raster(c,hero['art'],x+i*w/len(heroes),y,w/len(heroes),h)
  return
 c.saveState();scale=min(w/43,h/31);c.translate((x+(w-43*scale)/2-10*scale)*mm,(y+(h-31*scale)/2-31*scale)*mm);c.scale(scale,scale);q.card_art(c,card,0,0,True);c.restoreState()

def card_front(c,card,x,y,initial):
 text=effect(card,initial)
 from reportlab.platypus import Paragraph
 from reportlab.lib.styles import ParagraphStyle
 import html
 measured=Paragraph(html.escape(text),ParagraphStyle('fit',fontName='Body',fontSize=10,leading=12.5)).wrap(55*mm,200*mm)[1]
 dense=measured>27*mm;short=measured<=16*mm
 a.rect(c,x*mm,y*mm,63*mm,88*mm,'#ffffff',stroke='#8b9b95',r=1*mm)
 a.line(c,(x+4)*mm,(y+85)*mm,(x+59)*mm,(y+85)*mm,a.OLIVE,1.2)
 para(c,card['name'],x+4,y+(58 if dense else 72),35 if dense else 55,25 if dense else 12,11.5 if dense else 12.5,True,card['id']+' nome')
 if dense:artwork(c,card,x+40,y+57,19,22)
 else:artwork(c,card,x+5,y+(35 if short else 46),53,35 if short else 24)
 if card.get('load') is not None and not dense:
  yy=y+(29 if short else 40);a.rect(c,(x+4)*mm,yy*mm,55*mm,5*mm,a.PAPER,stroke=a.PAPER);txt(c,f'CARGA {card["load"]}',x+6,yy+1.3,8.3,True)
 elif card.get('reward') and not dense:
  qty=sum(card['reward'].values());yy=y+40;a.rect(c,(x+4)*mm,yy*mm,55*mm,5*mm,a.PAPER,stroke=a.PAPER);resource=next(iter(card['reward']));parts=next((r.get('portions') for r in D['cards'] if r.get('resource')==resource),None)
  badge=f'{qty} carta(s) / {qty*parts} porções' if parts else f'ACHADO: {qty} carta(s) da reserva'
  txt(c,badge,x+6,yy+1.3,8,True)
 h=44 if dense else (16 if short else 27)
 para(c,text,x+4,y+12,55,h,9.5 if dense else 10,label=card['id']+' efeito')
 b.family_icon(c,card['family'],(x+4)*mm,(y+6)*mm,3*mm)
 txt(c,b.FAMILIES[card['family']],x+8,y+6.2,6.8,True);txt(c,card['id'],x+33,y+4.5,6.2)

def card_back(c,fam,x,y):
 a.rect(c,x*mm,y*mm,63*mm,88*mm,'#ffffff',stroke='#8b9b95',r=1*mm)
 a.rect(c,(x+4)*mm,(y+4)*mm,55*mm,80*mm,a.PAPER,stroke=a.INK,r=1*mm)
 a.line(c,(x+8)*mm,(y+72)*mm,(x+55)*mm,(y+72)*mm,a.OLIVE,1)
 txt(c,'ZONA ZERO',x+8,y+62,16,True);txt(c,'COMUNIDADE',x+8,y+55,10,True)
 b.family_icon(c,fam,(x+24)*mm,(y+35)*mm,13*mm)
 para(c,b.FAMILIES[fam].upper(),x+8,y+19,47,10,11,True,label='verso '+fam)
 a.line(c,(x+8)*mm,(y+13)*mm,(x+55)*mm,(y+13)*mm,a.OLIVE,1)

def cards_pdf(folder,ids,name,initial=False):
 f=folder/name;q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=A4)
 for n in range(math.ceil(len(ids)/9)):
  batch=ids[n*9:n*9+9]
  for back in [False,True]:
   q.PAGE=n*2+1+back;txt(c,f'{name} | folha {n+1:02} | '+('VERSO • borda longa' if back else 'FRENTE')+' | 100%',8.5,7,6.4)
   for k,id in enumerate(batch):
    row,col=g.card_cell(k,'duplex_back' if back else 'front');x=8.5+col*65;y=297-14.5-row*90-88
    if back:card_back(c,q.CARDS[id]['family'],x,y)
    else:card_front(c,q.CARDS[id],x,y,initial)
   c.showPage()
 c.save();return f

def sample():
 root=O/'amostras';root.mkdir(parents=True,exist_ok=True)
 ids=[next(c['id'] for c in D['cards'] if c['name']==name and c['id'] in M['initial_cards']+M['supplement_cards']) for name in ['Faca','Bomba','Mercado: Conserva','Jana e criança','Emboscada','Solidário','Arrastar','Bateria','Van de manutenção']]
 cards_pdf(root,ids,'AMOSTRA_CARTAS_DUPLEX.pdf',True)

def manual_cards(root,source,ids,stem,stage):
 d=fitz.open(source);folder=root/'03_CARTAS_RECORTAR_E_COLAR'
 for back in [False,True]:
  f=folder/(stem+('_VERSOS.pdf' if back else '_FRENTES.pdf'));c=canvas.Canvas(str(f),pagesize=A4)
  for sn in range(math.ceil(len(ids)/9)):
   txt(c,f'COLAR / {stem} / '+('VERSOS' if back else 'FRENTES')+f' / folha {sn+1:02} / UMA FACE / 100%',8.5,7,6.7)
   c.showPage()
  c.save();out=fitz.open(f)
  for i,id in enumerate(ids):
   sn,k=divmod(i,9);x,top,w,h=g.card_rect(k,'duplex_back' if back else 'front');clip=fitz.Rect(x*mm,top*mm,(x+w)*mm,(top+h)*mm)
   xx,yy,_,_=g.card_rect(k,'manual_back' if back else 'front');target=fitz.Rect(xx*mm,yy*mm,(xx+w)*mm,(yy+h)*mm)
   out[sn].show_pdf_page(target,d,sn*2+int(back),clip=clip)
   code=f'{stem[-1]}-{sn+1:02}-{k+1}'
   out[sn].insert_font(fontname='ZZBody',fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
   out[sn].insert_text((xx*mm,(yy+h+1.6)*mm),code,fontname='ZZBody',fontsize=4.2,color=(.15,.25,.25))
   PAIRS.append(dict(file=str(f.relative_to(root)),id=id,code=code,page=sn+1,slot=k,side='back' if back else 'front',box=[xx,yy,w,h],label_outside=True))
  tmp=f.with_suffix('.tmp.pdf');out.save(tmp,garbage=4,deflate=True);out.close();tmp.replace(f)
  record(root,f,'cartas',stage,method='manual')

def all_cards(root):
 for ids,stem,stage,initial in [(M['initial_cards'],'KIT_INICIAL_1','initial',True),(M['supplement_cards'],'KIT_COMPLEMENTO_2','supplement',False)]:
  f=cards_pdf(root/'02_CARTAS_DUPLEX',ids,stem+'_DUPLEX.pdf',initial);record(root,f,'cartas',stage,True,method='duplex');manual_cards(root,f,ids,stem,stage)

def hero_body(index):
 art=dict(path='assets/v0.4/herois_'+['a','b','c','d'][index//6]+'.png',col=index%3,row=(index%6)//3,cols=3,rows=2)
 return tight_body(art)

def tight_body(art):
 from PIL import Image,ImageOps
 art=art.copy();im=Image.open(P/art['path']);iw,ih=im.size
 if 'crop' in art:l,t,r,bot=art['crop']
 elif Path(art['path']).name in q.REGIONS:
  cols,rows=q.REGIONS[Path(art['path']).name];l,r=cols[art['col']];t,bot=rows[art['row']]
 else:
  cw,ch=iw/art.get('cols',3),ih/art.get('rows',2);l,t=int(art['col']*cw),int(art['row']*ch);r,bot=int(l+cw),int(t+ch)
 crop=im.crop((l,t,r,bot));mask=crop.getchannel('A').point(lambda v:255 if v>160 else 0) if crop.mode=='RGBA' else ImageOps.grayscale(crop).point(lambda v:255 if v<205 else 0)
 bounds=mask.getbbox()
 if bounds:
  x0,y0,x1,y1=bounds;art['crop']=[max(l,l+x0-2),max(t,t+y0-2),min(r,l+x1+2),min(bot,t+y1+2)]
 return art

def standee_face(c,label,art,x,y,reverse=False):
 if reverse:
  c.saveState();c.translate((x+22)*mm,y*mm);c.scale(-1,1);q.raster(c,art,1,12,20,44);c.restoreState()
 else:q.raster(c,art,x+1,y+12,20,44)
 txt(c,label,x+1,y+7.8,6.1,True)

def standees(root,enemy=False):
 folder=root/'04_PERSONAGENS_E_INIMIGOS'
 if enemy:items=[dict(label=v['id']+' / '+v['type'],art=tight_body(b.lookup(v['type'])),id=v['id'],type=v['type']) for v in g.enemy_variants()];name='INIMIGOS_VARIANTES_E01_E24_RECORTAR.pdf'
 else:items=[dict(label=h['name'],art=hero_body(i),id=h['id']) for i,h in enumerate(D['heroes'])];name='HEROIS_24_RECORTAR.pdf'
 f=folder/name;q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=A4)
 for i,item in enumerate(items):
  slot=i%12;row,col=divmod(slot,6);x=19+col*29;y=161-row*124;q.PAGE=i//12+1
  if slot==0:txt(c,('VARIANTES DOS MESMOS 24 IDs • nunca use duas do mesmo E' if enemy else '24 HERÓIS EXISTENTES • frente e verso ilustrado espelhado'),10,289,7.5,True)
  a.rect(c,x*mm,y*mm,22*mm,116*mm,'#ffffff',stroke=a.INK)
  standee_face(c,item['label'],item['art'],x,y)
  c.saveState();c.translate((x+22)*mm,(y+116)*mm);c.rotate(180);standee_face(c,item['label'],item['art'],0,0,True);c.restoreState()
  c.setDash(2,1)
  for yy in [y+6,y+58,y+110]:a.line(c,x*mm,yy*mm,(x+22)*mm,yy*mm,a.OLIVE,.6)
  c.setDash();txt(c,'BASE / NÃO COLAR',x+.6,y+2,4.5);c.saveState();c.translate((x+22)*mm,(y+116)*mm);c.rotate(180);txt(c,'BASE / NÃO COLAR',.6,2,4.5);c.restoreState()
  if slot==11:c.showPage()
 if len(items)%12:c.showPage()
 c.save();record(root,f,'peões',optional=True,replaces='marcadores planos de personagem/inimigo; mesmos IDs')
 return f

def player_panel(root):
 f=root/'05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf';q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=landscape(A4))
 for page in range(2):
  q.PAGE=page+1;txt(c,f'PJ{page+1} / LADO ÚNICO / TOPO ↑ / corte 277×190 mm / juntar PJ1–PJ2 sem sobreposição',10,204,7)
  c.saveState();path=c.beginPath();path.rect(10*mm,10*mm,277*mm,190*mm);c.clipPath(path,stroke=0);c.translate((10-277*page)*mm,10*mm)
  txt(c,'MEU SOBREVIVENTE',8,181,14,True)
  a.rect(c,8*mm,22*mm,214*mm,152.5*mm,'#ffffff',stroke=a.OLIVE)
  para(c,'COLOQUE A FICHA COMPACTA AQUI\n210 × 148,5 mm • mesma pessoa, mesmas habilidades e estados',17,77,195,38,13,True)
  para(c,'FERIMENTOS\n0  1  2  3\nVida máxima 3\n\nFADIGA\n0  1  2  3\n\nFome □ Sede □\n\nXP total ___\nEscolhas\n3 ___\n6 ___\n9 ___',230,28,40,141,9.5)
  for n in range(10):
   xx=8+n*24;a.rect(c,xx*mm,6*mm,24*mm,11*mm,a.PAPER,stroke=a.OLIVE);txt(c,str(n),xx+9,9,10,True)
  txt(c,'3 / 6 / 9: escolha somente a evolução da própria ficha',8,19,7)
  txt(c,'EQUIPAMENTOS E INVENTÁRIO / MESMAS QUATRO CARGAS',284,181,11.5,True)
  for i,(x,y,w,h) in enumerate(g.panel_slots()):
   a.rect(c,x*mm,y*mm,w*mm,h*mm,'#ffffff',stroke=a.OLIVE,r=1*mm);txt(c,f'CARGA {i+1}',x+4,y+h+3,9.5,True)
   para(c,'Carta 63 × 88 mm\nFolga: 66 × 92 mm',x+5,y+32,w-10,24,10)
  para(c,'Armas: máximo duas transportadas, dentro destas cargas. Uma usada por ataque. Equipar na mochila é grátis no próprio turno.\nPeça com carga 2 ou 3: marque os demais espaços ocupados, sem duplicar o item. As cargas da ficha e do painel são as mesmas; não somam.\nCapacidade atual ___ / bônus de habilidade ___ / itens além da base: ____________________\nUse lápis, marcador solto ou clipe. Não há trilho ou pino funcional impresso.',284,10,263,59,10)
  c.restoreState();c.showPage()
 c.save();record(root,f,'painel ampliado',optional=True,copies=2,replaces='organização compacta na mesa; coloque a ficha existente, não elimina regras')
 return f

MAP_ASSETS={'Neutro':'comum','Mercado':'mercado','Hospital':'hospital','Oficina':'oficina','Posto':'posto','Condomínio':'condominio','Estação':'estacao'}

def scenario_floor(c,x,y,w,h,z,theme='Neutro'):
 from PIL import Image
 key=MAP_ASSETS[theme];file=P/'assets/v0.4'/f'{key}.png';iw,ih=Image.open(file).size
 uw=min(iw,ih*554/380);uh=uw*380/554;left=(iw-uw)/2;top=(ih-uh)/2;row,col=divmod(z-1,4)
 art=dict(path=str(file.relative_to(P)),crop=[left+col*uw/4,top+row*uh/4,left+(col+1)*uw/4,top+(row+1)*uh/4])
 q.raster(c,art,x/mm,y/mm,w/mm,h/mm)
 # Borda de parede opaca e corredores livres derivados exclusivamente dos conectores.
 band=2.3*mm*min(w/(138.5*mm),h/(95*mm));floor='#e8e5d9' if not a.ECON else '#f5f5f5'
 for xx,yy,ww,hh in [(x,y,band,h),(x+w-band,y,band,h),(x,y,w,band),(x,y+h-band,w,band)]:a.rect(c,xx,yy,ww,hh,floor,stroke=floor)
 edges={tuple(sorted(e)) for e in D['maps'][0]['edges']};scale=w/(138.5*mm);gap=14*mm*scale;depth=12*mm*scale
 for side,nb in [('L',z-1 if col else None),('R',z+1 if col<3 else None),('U',z-4 if row else None),('D',z+4 if row<3 else None)]:
  if nb is None or tuple(sorted((z,nb))) not in edges:continue
  if side=='L':xx,yy,ww,hh=x,y+h/2-gap/2,depth,gap
  elif side=='R':xx,yy,ww,hh=x+w-depth,y+h/2-gap/2,depth,gap
  elif side=='U':xx,yy,ww,hh=x+w/2-gap/2,y+h-depth,gap,depth
  else:xx,yy,ww,hh=x+w/2-gap/2,y,gap,depth
  a.rect(c,xx,yy,ww,hh,floor,stroke=floor)

def maps_pdf(folder,theme,name):
 f=folder/name;q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=landscape(A4))
 for mi,(r0,c0) in enumerate([(0,0),(0,2),(2,0),(2,2)],1):
  q.PAGE=mi;txt(c,f'M{mi} / {theme} / LADO A / TOPO ↑ / corte 277×190 mm / união sem sobreposição / 100%',10,204,6.7)
  for lr in range(2):
   for lc in range(2):q.zone(c,(r0+lr)*4+c0+lc+1,10+lc*138.5,10+(1-lr)*95,138.5,95,theme)
  c.showPage()
 c.save();return f

def all_maps(root):
 a.floor=scenario_floor
 f=maps_pdf(root/'06_TABULEIROS','Neutro','COMUNS_M01_M04_LADO_A.pdf');record(root,f,'módulos comuns')
 q.assemblies(root/'06_TABULEIROS',[0],'MERCADO_MONTAGEM.pdf');record(root,root/'06_TABULEIROS/MERCADO_MONTAGEM.pdf','montagem')
 q.assemblies(root/'06_TABULEIROS',range(1,6),'DEMAIS_DESTINOS_MONTAGENS.pdf');record(root,root/'06_TABULEIROS/DEMAIS_DESTINOS_MONTAGENS.pdf','montagens','supplement')
 for m in D['maps']:
  key=MAP_ASSETS[m['name']];f=maps_pdf(root/'08_EXTRAS_OPCIONAIS',m['name'],key.upper()+'_M01_M04_LADO_A.pdf');record(root,f,'variante temática',optional=True,replaces='COMUNS_M01_M04_LADO_A.pdf (quatro folhas)')
 # Nenhuma face B: todos os destinos têm seu conjunto separado e nunca exigem virar peça em uso.
 MAP_GEOMETRY.extend(q.GEOMETRY);q.GEOMETRY.clear()

def save_layout():
 (O/'layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2));(O/'layout_issues.json').write_text(json.dumps(b.issues,ensure_ascii=False,indent=2));(O/'pares_manuais.json').write_text(json.dumps(PAIRS,ensure_ascii=False,indent=2))

def copy_stable(root):
 mappings=[
 ('01_inicial/01_comece_aqui.pdf','01_GUIA_E_REGRAS/COMECE_AQUI.pdf','guia','initial',False),
 ('01_inicial/03_lia_ivo.pdf','05_PAINEIS/FICHAS_LIA_IVO.pdf','fichas compactas','initial',False),
 ('01_inicial/06_paineis_registros.pdf','05_PAINEIS/ABRIGO_MORADORES_ESTOQUE.pdf','abrigo e registros','initial',False),
 ('01_inicial/07_marcadores.pdf','07_MARCADORES_E_DIVISORIAS/MARCADORES_INICIAIS.pdf','marcadores planos','initial',False),
 ('01_inicial/08_divisorias.pdf','07_MARCADORES_E_DIVISORIAS/DIVISORIAS.pdf','divisórias','initial',False),
 ('01_inicial/09_calibracao_duplex.pdf','02_CARTAS_DUPLEX/CALIBRACAO_DUPLEX.pdf','calibração','initial',True),
 ('02_complemento/02_herois_resgataveis.pdf','05_PAINEIS/FICHAS_RESGATAVEIS.pdf','fichas compactas','supplement',False),
 ('02_complemento/04_manual_revisado.pdf','01_GUIA_E_REGRAS/MANUAL.pdf','manual','supplement',False),
 ('02_complemento/05_campanha_cinco_dias.pdf','01_GUIA_E_REGRAS/CAMPANHA.pdf','campanha','supplement',False),
 ('02_complemento/06_mapa_geral.pdf','06_TABULEIROS/SANTA_AURORA_ROTAS.pdf','rotas','supplement',False),
 ('02_complemento/07_registro_adicional.pdf','05_PAINEIS/REGISTRO_ADICIONAL.pdf','registro','supplement',False),
 ('02_complemento/08_tokens_resgataveis.pdf','07_MARCADORES_E_DIVISORIAS/MARCADORES_RESGATAVEIS.pdf','marcadores planos','supplement',False),
 ('02_complemento/09_moradores_adicional.pdf','05_PAINEIS/MORADORES_ADICIONAL.pdf','moradores','supplement',False)]
 for old,new,kind,stage,dup in mappings:
  f=root/new;shutil.copyfile(BASE/root.name/old,f);record(root,f,kind,stage,dup,method='duplex' if dup else 'both')
 f=root/'08_EXTRAS_OPCIONAIS/FICHAS_24_HEROIS.pdf';shutil.copyfile(BASE/root.name/'extras/24_fichas.pdf',f);record(root,f,'24 fichas',optional=True,replaces='fichas compactas selecionadas, se desejado')

def manual_calibration(root):
 f=root/'03_CARTAS_RECORTAR_E_COLAR/CALIBRACAO_COLAGEM.pdf';q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=A4)
 for side in ['FRENTE','VERSO']:
  title(c,'CALIBRAÇÃO / COLAR',side+' / uma face / não imprimir duplex / 100%')
  a.line(c,20*mm,240*mm,120*mm,240*mm,a.INK,1)
  for n in range(11):a.line(c,(20+10*n)*mm,237*mm,(20+10*n)*mm,243*mm,a.INK,1)
  txt(c,'100 mm entre as pontas',20,230,11,True)
  a.rect(c,35*mm,105*mm,63*mm,88*mm,'#ffffff',stroke=a.INK)
  txt(c,'TOPO ↑',40,182,12,True);txt(c,'A',40,167,18,True);txt(c,'B',82,118,18,True)
  para(c,'Recorte as duas peças de 63 × 88 mm. Una os topos A com A e B com B, costas para dentro. Aplique miolo opaco. Confira escala, corte e orientação antes do lote. Este ensaio não mede o registro automático da impressora.',20,33,170,56,12)
  c.showPage()
 c.save();record(root,f,'calibração manual',method='manual')

def assembly_guide(root):
 f=root/'08_EXTRAS_OPCIONAIS/GUIA_ILUSTRADO_MONTAGEM.pdf';q.LABEL=str(f);c=canvas.Canvas(str(f),pagesize=A4)
 title(c,'1 / ESCOLHA UMA IMPRESSÃO','Leia na tela; imprimir este guia é opcional: três folhas.')
 para(c,'A — DUPLEX: 25 folhas iniciais + 33 de complemento = 58 A4. Somente cartas e calibração: retrato, borda longa. O verso já reflete as colunas. Restante: uma face.\n\nB — RECORTAR E COLAR: 33 iniciais + 39 de complemento = 72 A4. Tudo uma face. Use as frentes e os versos separados; não imprima também o duplex. As posições de colagem são iguais em ambas as folhas.\n\nEscolha também uma única edição: ilustrada OU econômica. Escala 100%, tamanho real, sem ajustar. Meça primeiro a régua de 100 mm. Os dois métodos têm as mesmas 114 cartas e os mesmos componentes jogáveis.',15,130,180,115,12)
 for i,label in enumerate(['FRENTE','MIOLO OPACO','VERSO']):
  x=15+i*65;a.rect(c,x*mm,48*mm,54*mm,76*mm,a.PAPER,stroke=a.INK);txt(c,label,x+3,108,9,True)
 para(c,'Colagem: separe pares pelo código fora do corte. Mantenha TOPO com TOPO. Cole com miolo opaco, deixe secar plano e recorte. Remova completamente os códigos. Intenções têm versos iguais: nenhuma marca individual pode permanecer. Confira opacidade sob luz antes de jogar.',15,15,180,29,10)
 c.showPage();title(c,'2 / PEÕES E PAINÉIS','Extras de fabricação; marcadores planos e fichas compactas continuam válidos.')
 para(c,'Peões: 24 heróis em duas folhas. Inimigos: seis folhas com três variantes de E01–E24. São alternativas visuais dos mesmos IDs, não 72 inimigos: máximo 24 simultâneos; nunca use duas variantes do mesmo ID. Recorte o contorno retangular; vinque nas linhas tracejadas. Dobre no centro, una somente os corpos e abra as duas abas de 6 mm para lados opostos. Base 22 × 12 mm. O verso é a mesma figura espelhada, não uma vista das costas.',15,155,180,86,11)
 # Esquema de rede e montagem, vetorial e em escala declaradamente reduzida.
 x=22;y=65;scale=.65
 a.rect(c,x*mm,y*mm,22*scale*mm,116*scale*mm,'#ffffff',stroke=a.INK)
 for dy in [6,58,110]:
  c.setDash(2,2);a.line(c,x*mm,(y+dy*scale)*mm,(x+22*scale)*mm,(y+dy*scale)*mm,a.OLIVE,.6);c.setDash()
 txt(c,'REDE (reduzida)',15,56,8,True)
 a.poly(c,[(86*mm,71*mm),(102*mm,65*mm),(118*mm,71*mm),(102*mm,77*mm)],a.PAPER)
 a.rect(c,99*mm,71*mm,6*mm,62*mm,a.PAPER,stroke=a.INK);txt(c,'BASE ABERTA',78,56,9,True)
 para(c,'Painel opcional: duas A4 paisagem por jogador; quatro folhas para duas pessoas. Recorte 277 × 190 mm e una PJ1–PJ2 sem sobrepor. Coloque a ficha compacta sobre PJ1 e cartas reais sobre PJ2. Quatro slots de 66 × 92 mm recebem cartas de 63 × 88 mm. São as mesmas quatro cargas das regras; armas contam nelas. Itens com carga 2/3 ocupam mais slots. Use lápis ou marcadores soltos; não há mecanismo de pinos.',15,15,180,36,10)
 c.showPage();title(c,'3 / TABULEIROS E MESA','Módulos comuns reutilizados nos seis destinos; variantes são opcionais.')
 for i in range(4):
  xx=20+(i%2)*75;yy=130-(i//2)*51;a.rect(c,xx*mm,yy*mm,75*mm,51*mm,a.PAPER,stroke=a.INK);txt(c,f'M{i+1} / TOPO ↑',xx+5,yy+24,11,True)
 para(c,'Recorte cada módulo em 277 × 190 mm. M1/M2 em cima, M3/M4 embaixo, todos com o topo para cima. Una borda com borda, sem abas dentro do jogo e sem sobreposição. Tabuleiro montado: 554 × 380 mm. Use fita no verso. Todos são LADO A: não há pareamento duplex de mapas.\n\nO diagrama do destino indica portas e bloqueios por marcadores. A arte não cria obstáculos, cobertura ou conexões. Nunca atravesse parede porque um móvel sugere passagem. As variantes temáticas substituem as quatro folhas comuns; não são exigidas para continuar a campanha.',15,15,180,104,11)
 c.showPage();c.save();record(root,f,'guia de montagem',optional=True)

def make_index(root):
 entries=[e for e in FILES if (root/e['file']).exists() and e.get('edition')==root.name]
 text='# Zona Zero / fabricação 0.4 — '+root.name+'\n\n**Escolha A duplex (58 folhas) OU B recortar e colar (72 folhas). Não imprima os dois.**\n\nRegras 0.2 e seleção original preservadas. Leia COMECE_AQUI antes da primeira partida; MANUAL e CAMPANHA completam os cinco dias. 100%, sem ajustar. Materiais externos: três d6, lápis, borracha, tesoura, fita/cola e miolo ou envelopes opacos.\n\n'
 totals={}
 for method,label in [('duplex','A / DUPLEX'),('manual','B / RECORTAR E COLAR')]:
  text+='## '+label+'\n\n| Arquivo | Uso | Etapa | Páginas | Folhas | Impressão |\n|---|---|---|---:|---:|---|\n';totals[method]={}
  for stage in ['initial','supplement']:
   use=[e for e in entries if not e['optional'] and e['method'] in ['both',method] and e['stage']==stage];totals[method][stage]=sum(e['sheets'] for e in use)
   for e in use:text+=f"| [{Path(e['file']).name}](../{e['file']}) | {e['kind']} | {'Inicial' if stage=='initial' else 'Complemento'} | {e['pages']} | {e['sheets']} | {e['orientation']}, "+('duplex borda longa' if e['duplex'] else 'uma face')+' |\n'
  expected=g.sheet_totals(method);assert (totals[method]['initial'],totals[method]['supplement'])==expected[:2],totals
  text+=f"\n**{totals[method]['initial']} + {totals[method]['supplement']} = {expected[2]} folhas.**\n\n"
 text+='## Extras opcionais — não somar automaticamente\n\n| PDF | Folhas | Cópias consideradas | Substitui / finalidade |\n|---|---:|---:|---|\n'
 for e in entries:
  if e['optional']:text+=f"| [{Path(e['file']).name}](../{e['file']}) | {e['sheets']} | {e['copies']} | {e['replaces'] or e['kind']} |\n"
 text+='\nPeões: oito folhas (2 heróis + 6 variantes inimigas); preservam limite de 24 inimigos. Painel: duas folhas por jogador; quatro para duas pessoas. Guia de montagem: três opcionais. Seis variantes de destino: 24 folhas; cada conjunto de quatro substitui os quatro módulos comuns. Fichas de todos os heróis: 12 opcionais. Não são expansões de conteúdo.\n\nPDFs de referência privados não fazem parte desta entrega. Não houve montagem física nem playtest humano.\n'
 (root/'00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md').write_text(text)
 (root/'00_LEIA_PRIMEIRO/manifesto.json').write_text(json.dumps(dict(version='0.4',rules='0.2',edition=root.name,totals=totals,files=entries),ensure_ascii=False,indent=2))

def full_build():
 for ed in ['ilustrada','economica']:
  root=O/ed;init(root);a.ECON=ed=='economica';start=len(FILES)
  copy_stable(root);all_cards(root);standees(root);standees(root,True);player_panel(root);all_maps(root);manual_calibration(root);assembly_guide(root)
  if a.ECON:
   for f in root.rglob('*.pdf'):q.gray_pdf(f)
  for e in FILES[start:]:
   e['edition']=ed;e['sha256']=hashlib.sha256((root/e['file']).read_bytes()).hexdigest()
  make_index(root)
 (O/'geometry.json').write_text(json.dumps(MAP_GEOMETRY,ensure_ascii=False,indent=2))
 (O/'files.json').write_text(json.dumps(FILES,ensure_ascii=False,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--step',default='sample');args=p.parse_args()
 if args.step=='sample':sample()
 elif args.step=='all':full_build()
 else:
  for ed in ['ilustrada','economica']:
   root=O/ed;init(root);a.ECON=ed=='economica'
   if args.step=='cards':all_cards(root)
   if args.step=='pawns':standees(root);standees(root,True);player_panel(root)
   if args.step=='maps':all_maps(root)
 save_layout();print('Etapa',args.step,'estouros',b.issues[:8])
