"""Acabamento 0.5: altera apresentação; fontes mecânicas 0.4 intocadas."""
from pathlib import Path
import json,math,hashlib,shutil,html,argparse,random
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import build_fabrication as f
import art_finish_maps as art
P=f.P;O=P/'output/edicao-acabamento-v0.5';OLD=P/'output/edicao-fabricacao-v0.4';q=f.q;a=f.a;b=f.b;D=f.D;M=f.M
original_art=f.artwork;old_panel=f.player_panel
NEW_ART={**{n:('armas',i) for i,n in enumerate(['Faca','Machado','Pistola','Espingarda'])},**{n:('suprimentos',i) for i,n in enumerate(['Ferramentas','Conserva','Água','Combustível'])},**{n:('pecas_corrigidas',i) for i,n in enumerate(['Bomba','Membrana','Conexões','Bateria'])},**{n:('viagens',i) for i,n in enumerate(['Emboscada','Ruído distante','Barricada','Ponte avistada'])}}
RES=[]
def new_art(c,card,x,y,w,h):
 name=card['name'].split(': ')[-1]
 if name not in NEW_ART:return original_art(c,card,x,y,w,h)
 sheet,i=NEW_ART[name]
 if name=='Ferramentas':sheet,i='toolbox',0
 piece=dict(path=f'assets/v0.5/{sheet}.png',cols=1 if sheet=='toolbox' else 2,rows=1 if sheet=='toolbox' else 2,col=i%2,row=i//2)
 if sheet=='suprimentos':piece['crop']=[[100,0,755,448],[970,0,1420,445],[230,448,640,1024],[925,450,1430,1024]][i]
 if sheet=='pecas_corrigidas':piece['crop']=[[20,0,785,480],[800,25,1520,475],[10,530,800,1015],[810,490,1525,1015]][i]
 if sheet!='viagens':piece=f.tight_body(piece)
 else:
  from PIL import Image
  iw,ih=Image.open(P/piece['path']).size;piece['crop']=[(i%2)*iw/2+12,(i//2)*ih/2+12,(i%2+1)*iw/2-12,(i//2+1)*ih/2-12]
 from PIL import Image
 im=Image.open(P/piece['path']);l,t,r,bot=piece.get('crop',[0,0,*im.size]);ppi=max((r-l)/(w/25.4),(bot-t)/(h/25.4));RES.append(dict(file=piece['path'],component=card['id'],used_pixels=[round(r-l),round(bot-t)],print_box_mm=[w,h],effective_ppi=round(ppi,1),kind='raster nativo'))
 q.raster(c,piece,x,y,w,h)
def palette(fam):return '#9a604b' if fam in ['HOR','CER'] else '#b29351' if fam=='VIA' else '#5c7861' if fam in ['SAQ','PEC','VIN','MOR','INT'] else '#315e60'
def frame(c,x,y,w,h,accent):
 a.rect(c,x*mm,y*mm,w*mm,h*mm,'#ffffff' if a.ECON else '#dfd7c2',stroke=a.INK,r=1.8*mm)
 a.rect(c,(x+1.4)*mm,(y+1.4)*mm,(w-2.8)*mm,(h-2.8)*mm,'#fcfcf8' if a.ECON else '#f0eadb',stroke=accent,r=1.1*mm)
 for xx,yy in [(x+2.4,y+2.4),(x+w-2.4,y+2.4),(x+2.4,y+h-2.4),(x+w-2.4,y+h-2.4)]:
  c.setFillColor(a.color(accent));c.circle(xx*mm,yy*mm,.45*mm,fill=1,stroke=0)
 # Laminação angular de cantos; não interfere na zona de texto.
 for xx in [x+1.5,x+w-3]:a.line(c,xx*mm,(y+11)*mm,xx*mm,(y+h-11)*mm,accent,.5)
def card_front(c,card,x,y,initial):
 text=f.effect(card,initial);measure=Paragraph(html.escape(text),ParagraphStyle('m',fontName='Body',fontSize=10,leading=12.5)).wrap(55*mm,200*mm)[1]/mm
 dense=measure>30;short=measure<=20;accent=palette(card['family']);frame(c,x,y,63,88,accent)
 if dense:
  f.para(c,card['name'],x+4,y+61,35,22,11.5,True,card['id']+' nome');f.artwork(c,card,x+40,y+60,19,21);hh=47
 else:
  a.rect(c,(x+3)*mm,(y+72)*mm,57*mm,12*mm,'#e0d7be',stroke='#e0d7be',r=.5*mm)
  f.para(c,card['name'],x+4,y+72,55,12,11.5,True,card['id']+' nome')
  yy=35 if short else 46;f.artwork(c,card,x+4,y+yy,55,36 if short else 25);hh=20 if short else 30
  by=y+31 if short else y+41;a.rect(c,(x+4)*mm,by*mm,55*mm,4*mm,accent,stroke=accent)
  badge=''
  if card.get('load') is not None:badge=f'CARGA {card["load"]}'
  elif card.get('reward'):
   qty=sum(card['reward'].values());resource=next(iter(card['reward']));parts=next((r.get('portions') for r in D['cards'] if r.get('resource')==resource),None) if resource in ['Conserva','Água','Carne'] else None;badge=f'{qty} carta(s) / {qty*parts} porções' if parts else f'RESERVA: {qty} carta(s)'
  else:badge=b.FAMILIES[card['family']].upper()
  q.txt(c,badge,x+6,by+1,9.5,True,col='#ffffff')
 a.rect(c,(x+3.5)*mm,(y+9)*mm,56*mm,(hh+1)*mm,'#fcf9ee',stroke='#c9c1a9',r=.6*mm)
 f.para(c,text,x+4,y+10,55,hh,9.5 if dense else 10,label=card['id']+' efeito')
 b.family_icon(c,card['family'],(x+4)*mm,(y+4.5)*mm,3*mm);q.txt(c,b.FAMILIES[card['family']],x+8,y+4.7,6.4,True);q.txt(c,card['id'],x+33,y+4.4,6)
def card_back(c,fam,x,y):
 accent=palette(fam);frame(c,x,y,63,88,accent)
 a.rect(c,(x+4)*mm,(y+4)*mm,55*mm,80*mm,'#e4e6de' if a.ECON else '#36585a',stroke='#d9c89d',r=1*mm)
 for j in range(9):
  yy=y+8+j*8;a.line(c,(x+6)*mm,yy*mm,(x+57)*mm,(yy+5)*mm,'#43676a',.5)
 for yy in [y+10,y+78]:
  a.line(c,(x+8)*mm,yy*mm,(x+55)*mm,yy*mm,'#bdab7d',1)
 q.txt(c,'ZONA ZERO',x+8,y+64,15,True,col=a.INK if a.ECON else '#f3e8cc');q.txt(c,'COMUNIDADE',x+8,y+57,10,True,col=a.INK if a.ECON else '#f3e8cc')
 a.rect(c,(x+21)*mm,(y+31)*mm,21*mm,21*mm,'#e6d6ae',stroke='#a18b5d',r=1*mm);b.family_icon(c,fam,(x+25)*mm,(y+35)*mm,13*mm)
 a.rect(c,(x+6)*mm,(y+15)*mm,51*mm,12*mm,'#ecdfbf',stroke='#ecdfbf',r=.6*mm);f.para(c,b.FAMILIES[fam].upper(),x+8,y+16,47,10,10.5,True,label='verso '+fam)

def geometry(c,z,x,y,w,h,scale=1,doors=None,blocked=None):
 row,col=divmod(z-1,4);edges={tuple(sorted(e)) for e in D['maps'][0]['edges']};doors=doors or {tuple(e) for e in D['maps'][0]['doors']};blocked=blocked or set()
 for side,nb in [('L',z-1 if col else None),('R',z+1 if col<3 else None),('U',z-4 if row else None),('D',z+4 if row<3 else None)]:
  key=tuple(sorted((z,nb))) if nb else None;connected=key in edges;gap=14*scale if connected else 0
  c.setDash([2*scale*mm,1.1*scale*mm] if connected else [])
  color='#687d73' if connected else '#324f49';width=.65*scale if connected else 2.4*scale
  if side in ['L','R']:
   xx=x if side=='L' else x+w;mid=y+h/2
   for y1,y2 in [(y,mid-gap/2),(mid+gap/2,y+h)]:a.line(c,xx*mm,y1*mm,xx*mm,y2*mm,color,width)
   cx,cy=xx,mid
  else:
   yy=y if side=='D' else y+h;mid=x+w/2
   for x1,x2 in [(x,mid-gap/2),(mid+gap/2,x+w)]:a.line(c,x1*mm,yy*mm,x2*mm,yy*mm,color,width)
   cx,cy=mid,yy
  c.setDash()
  if connected:
   # Soleiras e ombreiras, sem remendos brancos no piso.
   if side in ['L','R']:
    for dy in [-7,7]:a.line(c,(cx-1.2*scale)*mm,(cy+dy*scale)*mm,(cx+1.2*scale)*mm,(cy+dy*scale)*mm,a.RUST,.9*scale)
   else:
    for dx in [-7,7]:a.line(c,(cx+dx*scale)*mm,(cy-1.2*scale)*mm,(cx+dx*scale)*mm,(cy+1.2*scale)*mm,a.RUST,.9*scale)
  if connected and key in doors and side in ['R','D']:
   if side=='R':a.line(c,cx*mm,(cy-gap/2)*mm,cx*mm,(cy+gap/2)*mm,a.RUST,1.7*scale)
   else:a.line(c,(cx-gap/2)*mm,cy*mm,(cx+gap/2)*mm,cy*mm,a.RUST,1.7*scale)
   if key in blocked:
    for sign in [-1,1]:a.line(c,(cx-3*scale)*mm,(cy-sign*3*scale)*mm,(cx+3*scale)*mm,(cy+sign*3*scale)*mm,'#9c493b',1.5*scale)
  q.GEOMETRY.append(dict(file=q.LABEL,page=q.PAGE,zone=z,side=side,neighbor=nb,connected=connected,gap_mm=gap/scale,x=x,y=y,w=w,h=h,scale=scale))

def assemblies(folder,indices,name):
 path=folder/name;q.LABEL=str(path);c=canvas.Canvas(str(path),pagesize=landscape(A4))
 for page,index in enumerate(indices,1):
  q.PAGE=page;m=D['maps'][index];q.heading(c,m['name'].upper()+' / SANTA AURORA','M1 M2 em cima; M3 M4 embaixo. Topo ↑, rotação 0°. Mesmas conexões da edição 0.2.')
  scale=150/554;zw=138.5*scale;zh=95*scale
  for z in m['zones']:
   r,col=divmod(z-1,4);q.zone(c,z,11+col*zw,46+(3-r)*zh,zw,zh,m['name'],scale,{tuple(sorted(e)) for e in m['doors']},{tuple(sorted(e)) for e in m['blocked']})
  scene_thumb(c,index,174,116,111,60);q.txt(c,'AMBIENTAÇÃO / ilustração, não tabuleiro',174,113,7)
  f.para(c,'SÍMBOLOS\nTracejado: limite de zona conectada.\nTraço espesso: parede sem conexão.\nSoleira: passagem de 14 mm.\nBarra ferrugem: porta. X: bloqueio.\nB: busca. O: objetivo. S: surgimento.\nEntrada e saída: Z1.',174,61,111,52,10)
  f.para(c,'Portas: '+', '.join(f'{x}–{y}' for x,y in m['doors'])+'.\nBloqueadas: '+(', '.join(f'{x}–{y}' for x,y in m['blocked']) or 'nenhuma')+'.\nInicial: ceil(H/2) Errantes em S; longa −1. Estação acrescenta Bruto em Z14.',174,19,111,37,9.5)
  f.para(c,'Use os quatro módulos comuns, mudando apenas os marcadores. Móveis são ambientação sem efeito: não bloqueiam, não dão cobertura e não acrescentam buscas. B1 em Z5; B2 em Z12. O1 em Z7; O2 em Z14; S em Z16. Consulte os achados na campanha.',11,13,150,28,9)
  c.showPage()
 c.save()

def scene_thumb(c,index,x,y,w,h):
 c.saveState();c.translate(x*mm,y*mm);c.scale(w/554,h/380);art.scene(c,D['maps'][index]['name']);c.restoreState()
def maps_pdf(folder,theme,name):
 path=folder/name;q.LABEL=str(path);c=canvas.Canvas(str(path),pagesize=landscape(A4))
 for mi,(r0,c0) in enumerate([(0,0),(0,2),(2,0),(2,2)],1):
  q.PAGE=mi;q.txt(c,f'M{mi} / {theme} / LADO A / TOPO ↑ / corte 277×190 mm / sem sobreposição / 100%',10,203,6.5)
  for lr in range(2):
   for lc in range(2):q.zone(c,(r0+lr)*4+c0+lc+1,10+lc*138.5,10+(1-lr)*95,138.5,95,theme)
  a.rect(c,12*mm,11*mm,59*mm,4*mm,a.PAPER,stroke=a.PAPER);q.txt(c,f'M{mi} / {theme} / A / TOPO ↑',13,12,6)
  c.showPage()
 c.save();return path

def panel(root):
 path=root/'05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf';q.LABEL=str(path);c=canvas.Canvas(str(path),pagesize=landscape(A4))
 for page in range(2):
  q.PAGE=page+1;q.txt(c,f'PJ{page+1} / corte 277×190 mm / unir sem sobrepor / A4 100%',10,203,7)
  c.saveState();clip=c.beginPath();clip.rect(10*mm,10*mm,277*mm,190*mm);c.clipPath(clip,stroke=0);c.translate((10-277*page)*mm,10*mm)
  a.rect(c,0,0,554*mm,190*mm,'#eeeeE8' if a.ECON else '#45635c',stroke='#24443f')
  # Tecido, costura, correias e fechos desenhados como superfície; sem trilhos falsos.
  for j in range(1,138):a.line(c,j*4*mm,0,j*4*mm,190*mm,'#506d62',.15)
  for yy in [3,187]:
   c.setDash(2,2);a.line(c,3*mm,yy*mm,551*mm,yy*mm,'#acb391',.6);c.setDash()
  for xx in [4,275,279,550]:a.line(c,xx*mm,4*mm,xx*mm,186*mm,'#273f38',2)
  for xx in [5,268,282,545]:
   a.rect(c,xx*mm,174*mm,8*mm,9*mm,'#a59570',stroke='#273f38',r=1*mm);a.rect(c,(xx+1.5)*mm,176*mm,5*mm,5*mm,'#52665c',stroke='#273f38')
  q.txt(c,'SANTA AURORA / CADERNO DE CAMPO',16,181,12,True,col=a.INK if a.ECON else '#f3e8c9')
  frame(c,8,22,214,152.5,'#9c8d69');a.rect(c,11*mm,25*mm,208*mm,146.5*mm,'#eee9d7',stroke='#d2c8ac')
  f.para(c,'SUA FICHA COMPACTA\nMesma pessoa, habilidades, inventário e evolução.\nColoque a ficha de 210 × 148,5 mm sobre esta área.',28,78,174,38,13,True)
  a.rect(c,226*mm,24*mm,46*mm,149*mm,'#eee8d6',stroke='#c6b995',r=1*mm)
  f.para(c,'FERIMENTOS\n0  1  2  3\nVida máxima 3\n\nFADIGA\n0  1  2  3\n\nFome □ Sede □\n\nXP total ___\nEscolhas\n3 ___\n6 ___\n9 ___',230,28,38,140,9.5)
  for i in range(10):
   xx=8+i*24;a.rect(c,xx*mm,6*mm,23*mm,11*mm,'#dbc798' if i in [3,6,9] else '#d7ddc6',stroke='#273f38',r=.8*mm);q.txt(c,str(i),xx+9,9,10,True)
  q.txt(c,'3 / 6 / 9: evolução da própria ficha',10,19,7,col=a.INK if a.ECON else '#f5edcf')
  q.txt(c,'MOCHILA / EQUIPAMENTOS / QUATRO CARGAS-BASE',285,181,11.5,True,col=a.INK if a.ECON else '#f5edcf')
  for i,(x,y,w,h) in enumerate(f.g.panel_slots()):
   frame(c,x-1,y-1,w+2,h+2,'#c6b58a');a.rect(c,x*mm,y*mm,w*mm,h*mm,'#d5ddc6',stroke='#8d9c84',r=1*mm)
   a.rect(c,(x+3)*mm,(y+h+2)*mm,(w-6)*mm,6*mm,'#d4bd87',stroke='#2d4a3f');q.txt(c,f'CARGA {i+1}',x+5,y+h+3.4,9,True)
   f.para(c,'63 × 88 mm\nSlot 66 × 92 mm',x+6,y+35,w-12,18,10,True)
  a.rect(c,283*mm,8*mm,264*mm,61*mm,'#eee9d7',stroke='#bea777',r=1*mm)
  f.para(c,'Armas: máximo duas transportadas, dentro destas cargas. Uma usada por ataque. Equipar na mochila é grátis no próprio turno.\nPeça com carga 2 ou 3: marque os demais espaços ocupados. As cargas da ficha e do painel são as mesmas; não somam.\nCapacidade atual ___ / bônus de habilidade ___ / itens além da base: ____________________\nUse lápis, marcador solto ou clipe. A arte não é mecanismo de pinos.',287,11,256,55,10)
  q.txt(c,f'PJ{page+1} / A / topo ↑',254+277*page,5,6,col=a.INK if a.ECON else '#f4e8c5');c.restoreState();c.showPage()
 c.save();f.record(root,path,'painel ampliado',optional=True,copies=2,replaces='organização compacta; mesmas quatro cargas')

# All old generation entrypoints retain their contract; only presentation callbacks change.
def setup():
 f.O=O;f.artwork=new_art;f.card_front=card_front;f.card_back=card_back;f.player_panel=panel;f.maps_pdf=maps_pdf;f.scenario_floor=art.floor_draw;q.geometry=geometry;q.scene=scene_thumb;q.assemblies=assemblies

def index(root):
 entries=[e for e in f.FILES if e.get('edition')==root.name];totals={}
 text='# Acabamento 0.5 / '+root.name+'\n\nEscolha duplex: **25 + 33 = 58 folhas**, OU colar: **33 + 39 = 72 folhas**. Mesmas 114 cartas. A4 100%, sem ajustar. Não imprimir ambos. Peões, ficha compacta e abrigo preservados.\n\n'
 for method in ['duplex','manual']:
  text+='## '+method.upper()+'\n\n| Arquivo | Etapa | Folhas | Impressão |\n|---|---|---:|---|\n';totals[method]={}
  for stage in ['initial','supplement']:
   es=[e for e in entries if not e['optional'] and e['method'] in ['both',method] and e['stage']==stage];totals[method][stage]=sum(e['sheets'] for e in es)
   for e in es:text+=f"| [{Path(e['file']).name}](../{e['file']}) | {stage} | {e['sheets']} | {e['orientation']} / "+('duplex, borda longa' if e['duplex'] else 'uma face')+' |\n'
  assert tuple(totals[method][s] for s in ['initial','supplement'])==f.g.sheet_totals(method)[:2]
 text+='\n## Extras opcionais\n\n| Arquivo | Folhas | Substitui |\n|---|---:|---|\n'
 for e in entries:
  if e['optional']:text+=f"| [{Path(e['file']).name}](../{e['file']}) | {e['sheets']} | {e['replaces'] or e['kind']} |\n"
 text+='\nPainel: duas folhas por jogador, quatro para dois; mesmas cargas. Peões: oito folhas, máximo 24 inimigos. Mapas: quatro por destino substituem comuns, sem lados B. Corte 277×190 mm; monte 554×380, sem sobrepor. Linha fina tracejada é limite de zona conectada; traço espesso é parede sem conexão. Soleira de 14 mm indica passagem; barra ferrugem indica porta; X é bloqueio. Arte não cria obstáculos ou cobertura. Portas, buscas, objetivos e surgimentos permanecem nas posições originais.\n\nMétodo colar: frente + miolo opaco + verso, topos iguais; remover códigos fora do corte. Teste opacidade. Calibração antes do lote. Leia guia e campanha, regras 0.2 preservadas. Nenhuma impressão física ou playtest humano.\n'
 folder=root/'00_LEIA_PRIMEIRO';(folder/'IMPRIMA_ESTES.md').write_text(text);(folder/'manifesto.json').write_text(json.dumps(dict(version='0.5',rules='0.2',edition=root.name,totals=totals,files=entries),ensure_ascii=False,indent=2))
 body='<h1>Zona Zero / 0.5</h1><p>Uma edição, um método: duplex 58 folhas OU colar 72. Não imprimir ambos.</p>'
 for method in ['duplex','manual']:
  body+='<h2>'+method+'</h2><ul>'
  for e in entries:
   if not e['optional'] and e['method'] in ['both',method]:body+='<li><a href="../'+e['file']+'">'+e['file']+'</a> / '+str(e['sheets'])+' folhas / '+e['orientation']+' / '+('duplex borda longa' if e['duplex'] else 'uma face')+'</li>'
  body+='</ul>'
 (folder/'ABRA_NO_NAVEGADOR.html').write_text('<!doctype html><meta charset="utf-8"><title>Zona Zero 0.5</title><style>body{font:18px sans-serif;margin:2em;max-width:1100px}li{margin:.6em}</style>'+body)

def build(step):
 setup()
 if step=='sample':
  f.sample();root=O/'amostras';f.init(root);a.ECON=False;panel(root);a.floor=art.floor_draw;maps_pdf(root,'Mercado','MERCADO_M01_M04_LADO_A.pdf');return
 for ed in ['ilustrada','economica']:
  root=O/ed;f.init(root);a.ECON=ed=='economica';start=len(f.FILES)
  f.copy_stable(root);f.starter_guide(root);f.all_cards(root)
  # Existing good pawn PDFs and compact sheets stay byte-identical to 0.4.
  for name in ['HEROIS_24_RECORTAR.pdf','INIMIGOS_VARIANTES_E01_E24_RECORTAR.pdf']:
   dest=root/'04_PERSONAGENS_E_INIMIGOS'/name;shutil.copyfile(OLD/ed/'04_PERSONAGENS_E_INIMIGOS'/name,dest);f.record(root,dest,'peões preservados',optional=True,replaces='marcadores planos, mesmos IDs')
  panel(root);f.all_maps(root);f.manual_calibration(root);f.assembly_guide(root);f.organization(root)
  if a.ECON:
   for file in root.rglob('*.pdf'):
    if '04_PERSONAGENS_E_INIMIGOS' not in file.parts:q.gray_pdf(file)
  from pdf_finish_export import compact
  for file in root.rglob('*.pdf'):
   if file.parent.name in ['02_CARTAS_DUPLEX','03_CARTAS_RECORTAR_E_COLAR','06_TABULEIROS'] or file.name.endswith('_M01_M04_LADO_A.pdf'):compact(file)
  for e in f.FILES[start:]:e['edition']=ed;e['sha256']=hashlib.sha256((root/e['file']).read_bytes()).hexdigest()
  index(root)
 (O/'geometry.json').write_text(json.dumps(f.MAP_GEOMETRY,indent=2));(O/'files.json').write_text(json.dumps(f.FILES,ensure_ascii=False,indent=2))
 # Pisos vetoriais e mobiliário raster nativo; medir o ppi efetivo no PDF final.
 RES.extend(dict(file=e['file'],component='mapa principal',kind='arquitetura vetorial + mobiliário raster nativo',effective_ppi=None,print_box_mm=[277,190],resolution_status='piso vetorial; imagens nativas limitadas a ≥170 ppi, verificar resolucao_pdfs.json') for e in f.FILES if e['kind'] in ['módulos comuns','variante temática'])
 (O/'resolucao.json').write_text(json.dumps(RES,ensure_ascii=False,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--step',default='sample');args=parser.parse_args();O.mkdir(parents=True,exist_ok=True);build(args.step);f.save_layout();print('Acabamento',args.step,'estouros',b.issues[:10])
