from pathlib import Path
import json, math, re, html, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from asset_catalog import lookup
P=Path(__file__).resolve().parents[1]; O=P/'output'; O.mkdir(exist_ok=True)
D=json.loads((P/'content/catalog.json').read_text())
pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
FAMILIES={'AJU':'Ajudas','CER':'Cercos','EQU':'Equipamentos','EVE':'Eventos','HOR':'Hordas','INT':'Intenção','MIS':'Missões','MOR':'Moradores','PEC':'Peças','PRO':'Projetos','REC':'Recursos','SAQ':'Saque','STR':'Estruturas','VEI':'Veículos','VIA':'Viagem','VIN':'Vínculos'}
INK=HexColor('#173c43'); RUST=HexColor('#995b3e'); GRAY=HexColor('#e7e9e6')
boxes=[]; issues=[]; pagination={}; duplex=[]
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=10,leading=14,spaceAfter=7,textColor=INK),
 'h1':ParagraphStyle('h1',fontName='Bold',fontSize=24,leading=29,spaceAfter=16,textColor=INK),
 'h2':ParagraphStyle('h2',fontName='Bold',fontSize=15,leading=20,spaceBefore=12,spaceAfter=9,textColor=INK)}
def foot(c,doc):
 c.setFont('Body',8);c.setFillColor(INK); c.drawString(17*mm,10*mm,'ZONA ZERO / COMUNIDADE • protótipo 0.1'); c.drawRightString(doc.pagesize[0]-17*mm,10*mm,str(doc.page))
def md_pdf(src,name):
 flow=[]
 for line in (P/src).read_text().splitlines():
  if not line.strip():continue
  style='h1' if line.startswith('# ') else 'h2' if line.startswith('## ') else 'body'
  txt=html.escape(re.sub(r'^#{1,3} ','',line))
  if line.startswith('- '):txt='• '+txt[2:]
  flow.append(Paragraph(txt,styles[style]))
 doc=SimpleDocTemplate(str(O/name),pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=16*mm,bottomMargin=19*mm)
 doc.build(flow,onFirstPage=foot,onLaterPages=foot)
def para(c,text,x,y,w,h,size=10,bold=False,file='',page=0,label=''):
 # x/y bottom; no silent shrinking below size.
 sty=ParagraphStyle('cell',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.25,textColor=INK)
 p=Paragraph(html.escape(text).replace('\n','<br/>'),sty); pw,ph=p.wrap(w,h)
 if ph>h+0.1:issues.append(dict(file=file,page=page,label=label,height=ph,available=h))
 p.drawOn(c,x,y+h-ph)
 boxes.append(dict(file=file,page=page,label=label,x=x,y=y,w=w,h=h,text_h=ph))
def title(c,t,w,h,sub=''):
 c.setFillColor(INK);c.setFont('Bold',18);c.drawString(10*mm,h-14*mm,t)
 c.setFont('Body',9);c.drawString(10*mm,h-21*mm,sub)
def sheet_art(c,art,x,y,w,h,fill=False):
 from PIL import Image as PI
 path=P/art['path']
 if not path.exists():return
 iw,ih=PI.open(path).size; cols,rows=art.get('cols',3),art.get('rows',4);cw,ch=iw/cols,ih/rows
 scale=max(w/cw,h/ch) if fill else min(w/cw,h/ch)
 aw,ah=(w,h) if fill else (cw*scale,ch*scale)
 ax,ay=x+(w-aw)/2,y+(h-ah)/2
 center_x=(art['col']+.5)*cw;center_y=ih-(art['row']+.5)*ch
 c.saveState();p=c.beginPath();p.rect(ax,ay,aw,ah);c.clipPath(p,stroke=0)
 c.drawImage(str(path),x+w/2-center_x*scale,y+h/2-center_y*scale,width=iw*scale,height=ih*scale,mask='auto');c.restoreState()
def clip_portrait(c,hero,x,y,w,h):
 if hero.get('art'):sheet_art(c,hero['art'],x,y,w,h,True)
 else:
  c.setStrokeColor(RUST);c.rect(x,y,w,h);para(c,'RETRATO PENDENTE',x+2*mm,y+2*mm,w-4*mm,h-4*mm,10)
FAMILY_COLOR={'VIN':'#98535e','INT':'#777d7d','REC':'#8d896d','SAQ':'#667f5d','VIA':'#ac873d','HOR':'#a0523c','CER':'#7d4750','PRO':'#173c43','STR':'#876b54','MIS':'#786077','MOR':'#ad874a','EQU':'#36616b','EVE':'#a77f39','PEC':'#546b67','VEI':'#536879','AJU':'#637a7b'}
def family_icon(c,f,x,y,s):
 c.saveState();c.setStrokeColor(HexColor(FAMILY_COLOR[f]));c.setLineWidth(.7)
 if f=='INT':
  c.rect(x,y,s,s*.7);c.line(x,y+s*.7,x+s/2,y+s*.3);c.line(x+s,y+s*.7,x+s/2,y+s*.3)
 elif f=='STR':
  p=c.beginPath();p.moveTo(x,y);p.lineTo(x,y+s*.6);p.lineTo(x+s/2,y+s);p.lineTo(x+s,y+s*.6);p.lineTo(x+s,y);p.close();c.drawPath(p)
 elif f=='VIN':
  c.ellipse(x,y,x+s*.65,y+s*.5);c.ellipse(x+s*.35,y,x+s,y+s*.5)
 elif f=='VIA':
  c.line(x,y,x+s*.3,y+s);c.line(x+s,y,x+s*.7,y+s);c.line(x+s/2,y,x+s/2,y+s*.4)
 elif f=='CER':
  c.rect(x,y,s,s);c.line(x+s*.33,y,x+s*.33,y+s);c.line(x+s*.66,y,x+s*.66,y+s)
 elif f=='MIS':
  c.line(x,y,x,y+s);c.rect(x,y+s*.55,s*.8,s*.45)
 elif f=='MOR':
  c.circle(x+s*.3,y+s*.7,s*.16);c.circle(x+s*.75,y+s*.7,s*.16);c.line(x+s*.1,y,x+s*.3,y+s*.5);c.line(x+s*.55,y,x+s*.75,y+s*.5)
 elif f in ['PRO','EQU','PEC']:
  c.line(x,y,x+s,y+s);c.line(x,y+s,x+s,y);c.circle(x+s,y+s,s*.15)
 elif f=='HOR':
  c.ellipse(x,y,x+s*.35,y+s*.6);c.ellipse(x+s*.6,y+s*.4,x+s,y+s)
 else:
  c.rect(x,y,s,s*.8);c.line(x,y+s*.8,x+s/2,y+s*.4);c.line(x+s,y+s*.8,x+s/2,y+s*.4)
 c.restoreState()
def cards(card_list=None,name='03_cartas_duplex.pdf'):
 card_list=D['cards'] if card_list is None else card_list
 c=canvas.Canvas(str(O/name),pagesize=A4)
 W,H=A4; cw,ch=63*mm,88*mm; gap=2*mm
 batches=[card_list[i:i+9] for i in range(0,len(card_list),9)]
 for sheet,batch in enumerate(batches,1):
  for side in ['front','back']:
   page=(sheet-1)*2+(1 if side=='front' else 2)
   c.setFont('Body',7);c.setFillColor(INK);c.drawString(8.5*mm,7*mm,f'Folha {sheet:02} • '+('FRENTE' if side=='front' else 'VERSO • borda longa')+' • 100%')
   for n,card in enumerate(batch):
    r,col=divmod(n,3); pcol=col if side=='front' else 2-col
    x=8.5*mm+pcol*(cw+gap);y=H-14.5*mm-(r+1)*ch-r*gap
    c.setStrokeColor(Color(.6,.6,.6));c.setLineWidth(.35);c.rect(x,y,cw,ch)
    if side=='front':
     family_icon(c,card['family'],x+4*mm,y+ch-10*mm,5*mm)
     para(c,FAMILIES[card['family']],x+12*mm,y+ch-11*mm,cw-16*mm,6*mm,8,bold=True,file=name,page=page,label=card['id']+' family')
     art=lookup(card['name'],card['family'])
     hasart=art and (P/art['path']).exists()
     if hasart:sheet_art(c,art,x+cw-23*mm,y+ch-31*mm,19*mm,19*mm)
     para(c,card['name'],x+4*mm,y+ch-30*mm,cw-(29 if hasart else 8)*mm,17*mm,11 if hasart else 12,bold=True,file=name,page=page,label=card['id']+' title')
     para(c,card['text'],x+4*mm,y+12*mm,cw-8*mm,ch-44*mm,9.5,file=name,page=page,label=card['id'])
     para(c,card['id']+' • 0.1',x+4*mm,y+4*mm,cw-8*mm,5*mm,6.8,file=name,page=page,label=card['id']+' id')
    else:
     # INT back carries no unique ID or secret identity.
     fam=card['family']; para(c,'ZONA ZERO\nCOMUNIDADE',x+5*mm,y+44*mm,cw-10*mm,20*mm,14,bold=True,file=name,page=page,label='back')
     para(c,'INTENÇÃO' if fam=='INT' else FAMILIES[fam].upper(),x+5*mm,y+27*mm,cw-10*mm,10*mm,12,bold=True)
     c.setStrokeColor(INK); c.rect(x+8*mm,y+10*mm,cw-16*mm,ch-20*mm)
     if name=='03_cartas_duplex.pdf':duplex.append(dict(sheet=sheet,row=r,front_col=col,back_col=pcol,id=card['id'],family=fam,back_key=fam))
   c.showPage()
 c.save()
def hero_sheets():
 name='04_fichas_personagens.pdf'; c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4
 for i,h in enumerate(D['heroes']):
  k=i%2;y=H-(k+1)*H/2
  c.setStrokeColor(INK);c.line(8*mm,y+H/2-2*mm,W-8*mm,y+H/2-2*mm)
  para(c,h['name']+' / '+h['profession'],9*mm,y+H/2-20*mm,W-18*mm,13*mm,16,bold=True,file=name,page=i//2+1,label=h['id'])
  clip_portrait(c,h,9*mm,y+37*mm,39*mm,78*mm)
  txt=h['story']+'\n'+' • '.join(f'{a} {v}' for a,v in h['attributes'].items())+'\nVida 3 | mochila 4 | PA 3\nInicial: '+h['ability']+'\n3 XP — escolha: '+ ' OU '.join(h['progression']['3'])+'\n6 XP — escolha: '+ ' OU '.join(h['progression']['6'])+'\n9 XP — escolha: '+ ' OU '.join(h['progression']['9'])
  para(c,txt,52*mm,y+30*mm,W-61*mm,94*mm,10.5,file=name,page=i//2+1,label=h['id']+' body')
  para(c,h['unlock']+' • '+h['profession_status']+' • Manual §§3,13\nXP ___   Ferimentos ___   Fadiga ___   Fome □ Sede □   Vínculo ___\nEscolhas 3/6/9: __________   ID '+h['id'],9*mm,y+5*mm,W-18*mm,23*mm,8.5,file=name,page=i//2+1,label='record')
  if k==1:c.showPage()
 c.save()
def maps():
 name='06_mapas_modulos.pdf'; W,H=landscape(A4);c=canvas.Canvas(str(O/name),pagesize=(W,H))
 M=D['maps'][0];edges={tuple(sorted(e)) for e in M['edges']}
 for mi,(r0,c0) in enumerate([(0,0),(0,2),(2,0),(2,2)],1):
  x0,y0=10*mm,10*mm;mw,mh=277*mm,190*mm;zw,zh=mw/2,mh/2
  c.setFont('Body',7);c.drawString(10*mm,H-6*mm,f'M{mi} • topo ↑ • corte na moldura 277 × 190 mm • união sem sobreposição')
  for lr in range(2):
   for lc in range(2):
    gr,gc=r0+lr,c0+lc;z=gr*4+gc+1;x=x0+lc*zw;y=y0+(1-lr)*zh
    c.setFillColor(white);c.rect(x,y,zw,zh,fill=1,stroke=0)
    c.setStrokeColor(INK);c.setLineWidth(1.4)
    # Every boundary is a wall except a declared open connector.
    for direction,nb in [('L',z-1 if gc else None),('R',z+1 if gc<3 else None),('U',z-4 if gr else None),('D',z+4 if gr<3 else None)]:
     connected=nb is not None and tuple(sorted((z,nb))) in edges
     opening=14*mm if connected else 0
     if direction in ['L','R']:
      xx=x if direction=='L' else x+zw;mid=y+zh/2
      c.line(xx,y,xx,mid-opening/2);c.line(xx,mid+opening/2,xx,y+zh)
     else:
      yy=y if direction=='D' else y+zh;mid=x+zw/2
      c.line(x,yy,mid-opening/2,yy);c.line(mid+opening/2,yy,x+zw,yy)
    c.setFont('Bold',19);c.setFillColor(INK);c.drawString(x+7*mm,y+zh-12*mm,f'Z{z:02}')
    labels=[]
    if z==1:labels=['ENTRADA / SAÍDA','ESTACIONAMENTO']
    if z==16:labels=['S • SURGIMENTO']
    if z in [5,12]:labels=[f'B{1 if z==5 else 2} • BUSCA','3 usos por campanha']
    if z in [7,14]:labels=[f'O{1 if z==7 else 2} • OBJETIVO']
    para(c,'\n'.join(labels),x+7*mm,y+12*mm,zw-14*mm,30*mm,12,file=name,page=mi,label=f'zone{z}')
    # original restrained vector floor hatch; no decorative obstacles.
    c.setStrokeColor(Color(.85,.87,.85));c.setLineWidth(.3)
    for j in range(3):c.line(x+zw-30*mm,y+(15+j*8)*mm,x+zw-8*mm,y+(15+j*8)*mm)
  c.showPage()
 c.save()
 name='07_montagens_destinos.pdf';c=canvas.Canvas(str(O/name),pagesize=landscape(A4))
 for pi,M in enumerate(D['maps'],1):
  title(c,M['name'].upper()+' / montagem',W,H,'M1 M2 na linha superior; M3 M4 inferior. Todos topo ↑, rotação 0°. Não espelhar módulos.')
  x0,y0=14*mm,23*mm;sw,sh=154*mm,147*mm;zw,zh=sw/4,sh/4;edges={tuple(sorted(e)) for e in M['edges']}; doors={tuple(sorted(e)) for e in M['doors']}; blocked={tuple(sorted(e)) for e in M['blocked']}
  for z in M['zones']:
   r,col=divmod(z-1,4);x=x0+col*zw;y=y0+(3-r)*zh
   c.setFillColor(Color(.97,.97,.95));c.setStrokeColor(Color(.75,.78,.75));c.setLineWidth(.3);c.rect(x,y,zw,zh,fill=1,stroke=1)
   c.setFont('Bold',11);c.setFillColor(INK);c.drawString(x+3*mm,y+sh/4-6*mm,str(z))
   labels={1:'ENTRADA',5:'B1',12:'B2',7:'O1',14:'O2',16:'S'}
   if z in labels:c.drawString(x+4*mm,y+8*mm,labels[z])
   for nb in [z+1 if col<3 else None,z+4 if r<3 else None]:
    if nb is None:continue
    key=tuple(sorted((z,nb))); c.setStrokeColor(INK);c.setLineWidth(1)
    vertical=nb==z+1
    if vertical:xx,yy=x+zw,y+zh/2
    else:xx,yy=x+zw/2,y
    if key in edges:
     c.setStrokeColor(RUST if key in blocked else INK);c.setLineWidth(2)
     if vertical:c.line(xx-5*mm,yy,xx+5*mm,yy)
     else:c.line(xx,yy-5*mm,xx,yy+5*mm)
     if key in doors:
      c.setFillColor(white);c.rect(xx-2*mm,yy-2*mm,4*mm,4*mm,fill=1)
      if key in blocked:c.line(xx-2*mm,yy-2*mm,xx+2*mm,yy+2*mm)
  c.setStrokeColor(INK);c.setLineWidth(1);c.rect(x0,y0,sw,sh)
  for cx,cy,lab in [(0,1,'M1'),(1,1,'M2'),(0,0,'M3'),(1,0,'M4')]:
   c.setFont('Body',8);c.drawString(x0+cx*sw/2+2*mm,y0+cy*sh/2+2*mm,lab)
  text='Linhas ligam zonas; onde não há linha, há parede. Quadrado = porta comum; risco diagonal ferrugem = bloqueada.\n\nColoque marcadores de porta indicados aqui nos conectores correspondentes dos módulos. Abra por 1 PA, bloqueada com ferramenta por 2 PA.\n\nEntrada/saída Z1. S em Z16. B1 Z5 e B2 Z12: três usos cada. Objetivos O1 Z7 e O2 Z14.\n\nInicial: ceil(H/2) Errantes em S; longa −1. Estação acrescenta Bruto em Z14.\n\nOs quatro módulos formam 554 × 380 mm. Corte e encoste sem sobreposição. Textos ficam longe das emendas.'
  para(c,text,181*mm,23*mm,101*mm,147*mm,10,file=name,page=pi,label=M['id'])
  c.showPage()
 c.save()
def panels():
 name='05_paineis_registros.pdf';W,H=landscape(A4);c=canvas.Canvas(str(O/name),pagesize=(W,H))
 title(c,'ABRIGO / SANTA AURORA',W,H,'12 terrenos • barracas 1–4 • cozinha 5 • depósito 6 • cisterna 7 • extras fundadores 8/9')
 for n in range(12):
  r,col=divmod(n,4);x=10*mm+col*48*mm;y=H-66*mm-r*45*mm;c.setStrokeColor(INK);c.rect(x,y,46*mm,42*mm);para(c,f'T{n+1:02}\nEstrutura: ______\nProjeto: ______\nDano: □',x+3*mm,y+3*mm,40*mm,36*mm,10)
 para(c,'PERÍMETRO\nPortão 2 □ ativo\nTorre +1 □ ativa\nCães +1 coletivo\n\nDia 1 2 3 4 5\nMoral 0 1 2 3 4 5\nSaúde 0 1 2 3 4 5\nPressão 0 1 2 3\nFila de cercos:\n____________\n\nProjetos A / B\nMax 2 simultâneos\nMax 2 trabalho/dia\npor projeto',210*mm,28*mm,77*mm,148*mm,11,file=name,page=1,label='shelter')
 c.showPage();title(c,'MAPA GERAL / ROTAS',W,H,'Todas saem do abrigo; curta 1 trecho/sentido • longa 2 • mesmo relógio a pé e van')
 positions=[(55,145),(145,145),(235,145),(55,65),(145,65),(235,65)]
 c.setFont('Bold',13);c.drawCentredString(145*mm,105*mm,'ABRIGO')
 for M,(xx,yy) in zip(D['maps'],positions):
  c.setStrokeColor(INK);c.line(145*mm,101*mm,xx*mm,(yy-5)*mm);c.setFillColor(white);c.rect((xx-38)*mm,(yy-18)*mm,76*mm,33*mm,fill=1)
  para(c,M['name']+'\nCurta: risco normal\nLonga: −1 inimigo inicial\nEstado NV / C / P / E',(xx-35)*mm,(yy-16)*mm,70*mm,30*mm,9)
 c.showPage(); title(c,'REGISTRO / MORADORES E CAMPANHA',W,H,'Fotocopie esta página conforme necessário. IDs individuais; nunca apague histórico de saída.')
 headers=['ID / nome / família','Adulto/criança/cão','Fer / fad / XP','Fome/sede / noites','Chegada / obs / vaga','Função / intenção']
 for col,txt in enumerate(headers):para(c,txt,(10+col*46)*mm,168*mm,44*mm,15*mm,8,bold=True)
 for r in range(9):
  for col in range(6):c.setStrokeColor(Color(.5,.5,.5));c.rect((10+col*46)*mm,(150-r*14)*mm,46*mm,14*mm)
 para(c,'Dia ___ C inicial ___ Consumidores hoje ___ Vagas ___ Excesso ___\nEstoque comida ___ Água ___ Reserva/estoque separados. Lotes retirados por destino: __________________\nRelógio 0 1 2 3 4 5 6 7 8 | 9 10 • Pressão local 0 1 • Van estado ___ combustível ___\nPlanejamento: pessoa → tarefa → alvo → custo reservado ______________________________\nProjetos: etapa/custos/trabalho __________________________________________________\nDestino/portas/buscas/chão/resgates/XP _____________________________________________\nFila cercos ___ Promessas ___ Relação Ponte ___ Saldo / continuação ____________________',10*mm,12*mm,277*mm,57*mm,9)
 c.showPage(); title(c,'EXPANSÃO / CONTROLE LOGÍSTICO',W,H,'Adicionar só após limpar área, pagar 4 Materiais + 2 Madeiras + 2 trabalhos; máximo uma.')
 for n in range(6):
  r,col=divmod(n,3);x=(10+col*64)*mm;y=(107-r*67)*mm;c.rect(x,y,61*mm,62*mm);para(c,f'T{13+n}\nEstrutura ______\nProjeto ______\nDano □',x+4*mm,y+4*mm,53*mm,54*mm,12)
 para(c,'PROJETO A\nNome / terreno ____\nMateriais reservados\n________________\nTrabalho: 0 1 2 3 4\n\nPROJETO B\nNome / terreno ____\nMateriais reservados\n________________\nTrabalho: 0 1 2 3 4\n\nVAN: passageiros ___\nCarga 0–12 ___\nCombustível ___',210*mm,35*mm,75*mm,135*mm,11)
 c.showPage();title(c,'RECURSOS / ALTERNATIVA ECONÔMICA',W,H,'Substitui 156 cartas de reserva por registros numerados; não altera porções, carga nem disponibilidade.')
 para(c,'Use cada linha para um lote físico: ID único, tipo, quantidade/porções, local e origem.\nComida/água: máximo quatro porções por lote; uma carga por lote, mesmo parcial. Material, combustível, munição e outros: uma unidade/carga.\nMarque local E=estoque, M=mochila com herói, V=van, C=chão com destino/zona, P=projeto. Nunca use saldo em dois locais.\nZerado volta à reserva, não gera estoque nem devolve saque. Registre origem para auditar cada achado. Fotocopie quando acabar.',10*mm,139*mm,277*mm,44*mm,10)
 for r in range(8):
  for col,lab in enumerate(['ID / tipo','Qtd / porções','Local / pessoa','Origem / dia']):
   x=(10+col*69)*mm;y=(116-r*12)*mm;c.rect(x,y,69*mm,12*mm)
   if r==0:para(c,lab,x+2*mm,y+2*mm,65*mm,8*mm,9,bold=True)
 c.showPage();c.save()
def markers():
 name='08_marcadores.pdf';c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4
 # hero token portraits circularly clipped, same actual artwork; no raster editing.
 hero_by_id={h['id']:h for h in D['heroes']}
 items=[(t['kind'],t['name'],hero_by_id.get(t['hero_ref'])) for t in D['tokens']]
 for i,(typ,txt,h) in enumerate(items):
  slot=i%48;r,col=divmod(slot,6);x=(10+col*32)*mm;y=H-(15+(r+1)*32)*mm;c.setStrokeColor(INK);c.rect(x,y,29*mm,29*mm)
  if typ=='hero':clip_portrait(c,h,x+2*mm,y+8*mm,25*mm,19*mm)
  else:
   art=lookup(txt)
   if art:sheet_art(c,art,x+2*mm,y+7*mm,25*mm,20*mm)
   else:
    c.setFont('Bold',13);c.setFillColor(INK);c.drawCentredString(x+14.5*mm,y+15*mm,txt)
  c.setFont('Body',7);c.drawCentredString(x+14.5*mm,y+3*mm,txt if typ=='hero' or lookup(txt) else 'ZC • marcador')
  if slot==47:c.showPage()
 if len(items)%48:c.showPage()
 c.save()
def organizer():
 name='09_organizacao.pdf';c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4
 fams=sorted({c['family'] for c in D['cards']})
 for i,f in enumerate(fams):
  slot=i%8;r,col=divmod(slot,2);x=(10+col*96)*mm;y=H-(15+(r+1)*65)*mm
  c.setStrokeColor(INK);c.rect(x,y,90*mm,60*mm);para(c,'ZONA ZERO / '+FAMILIES[f],x+4*mm,y+42*mm,82*mm,12*mm,13,bold=True)
  qty=sum(a['family']==f for a in D['cards']);para(c,f'{qty} cartas na edição completa • {f}\nMonte □ Descarte □\nReserva separada do estoque',x+4*mm,y+9*mm,82*mm,29*mm,10)
  c.setDash(3,2);c.line(x,y+8*mm,x+90*mm,y+8*mm);c.setDash()
  if slot==7:c.showPage()
 if len(fams)%8:c.showPage()
 for group in [('EXPLORAÇÃO','COMUNIDADE','RECURSOS','REFERÊNCIAS'),('MONTE','DESCARTE','RESERVA','ESTOQUE'),('INVENTÁRIO','CARGA DA VAN','CHÃO POR DESTINO','PROJETOS A / B')]:
  for n,t in enumerate(group):
   r,col=divmod(n,2);x=(10+col*96)*mm;y=(155-r*100)*mm;c.rect(x,y,90*mm,85*mm);para(c,t,x+5*mm,y+55*mm,80*mm,20*mm,14,bold=True)
   para(c,'Base de mesa; mantenha bens físicos aqui. Divisórias: dobre aba tracejada. Ajuste separação à espessura real.',x+5*mm,y+10*mm,80*mm,40*mm,10)
  c.showPage()
 c.save()
def calibration():
 name='10_calibracao_duplex.pdf';c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4
 for side in ['FRENTE','VERSO']:
  title(c,'CALIBRAÇÃO / '+side,W,H,'A4 retrato • 100% • virada borda longa • linhas mantidas, colunas refletidas')
  c.setStrokeColor(INK);x=20*mm;y=H-50*mm;c.line(x,y,x+100*mm,y)
  for n in range(101):c.line(x+n*mm,y,x+n*mm,y+(5 if n%10==0 else 2)*mm)
  c.setFont('Body',10);c.drawString(x,y-8*mm,'Esta régua deve medir exatamente 100 mm.')
  for r in range(3):
   for col in range(3):
    x=(8.5+col*65)*mm;y=H-(108+r*58)*mm;c.rect(x,y,63*mm,48*mm)
    frontcol=col if side=='FRENTE' else 2-col;label=f'{r+1}{chr(65+frontcol)}'
    c.setFont('Bold',18);c.drawString(x+8*mm,y+25*mm,label)
    # asymmetric arrow and matching target centers
    c.line(x+31.5*mm,y+10*mm,x+31.5*mm,y+20*mm);c.line(x+31.5*mm,y+20*mm,x+27.5*mm,y+16*mm)
    c.circle(x+31.5*mm,y+10*mm,2*mm);c.setFont('Body',8);c.drawString(x+5*mm,y+3*mm,'↑ topo da folha')
  para(c,'Contra a luz, A deve coincidir com A, B com B e C com C. Verifique as três linhas. Compense deslocamento na impressora; não redimensione. Teste também opacidade do envelope: nenhuma intenção deve ser identificável.',12*mm,12*mm,186*mm,30*mm,10)
  c.showPage()
 c.save()
def gallery():
 name='11_galeria_arte.pdf';c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4
 from asset_catalog import EQUIPMENT,BUILDINGS,ENCOUNTERS,ENEMIES,region
 for sheet,labels,cols,rows in [('enemies',ENEMIES,2,2),('equipment',EQUIPMENT,3,3),('buildings',BUILDINGS,3,3),('encounters',ENCOUNTERS,2,4)]:
  if not (P/f'assets/{sheet}.png').exists():continue
  title(c,'SANTA AURORA / '+sheet.upper(),W,H,'Prancha de referência artística opcional; textos e regras são diagramados separadamente.')
  sw,sh=190*mm/cols,250*mm/rows
  for i,label in enumerate(labels):
   r,col=divmod(i,cols);x=10*mm+col*sw;y=H-29*mm-(r+1)*sh
   sheet_art(c,region(sheet,i,cols,rows),x+2*mm,y+10*mm,sw-4*mm,sh-13*mm)
   para(c,label,x+2*mm,y,sw-4*mm,9*mm,9,bold=True)
  c.showPage()
 c.save()
def cover():
 name='00_capa.pdf';c=canvas.Canvas(str(O/name),pagesize=A4);W,H=A4;art=P/'assets/cover.png'
 if art.exists():c.drawImage(str(art),0,0,width=W,height=H,mask='auto')
 c.setFillColor(INK);c.setFont('Bold',13);c.drawString(15*mm,H-22*mm,'SOBREVIVENTES')
 c.setFont('Bold',37);c.drawString(15*mm,H-39*mm,'ZONA ZERO')
 c.setFont('Bold',18);c.drawString(15*mm,H-51*mm,'COMUNIDADE')
 c.setFont('Body',11);c.drawString(15*mm,H-63*mm,'ANTES QUE A ÁGUA ACABE • protótipo 0.1')
 c.save()
if __name__=='__main__':
 for src,name in [('RULES.md','01_manual_iniciantes.pdf'),('CAMPAIGN.md','02_campanha.pdf')]:md_pdf(src,name)
 cards();cards([a for a in D['cards'] if a['family']!='REC'],'03b_cartas_sem_recursos_duplex.pdf');hero_sheets();maps();panels();markers();organizer();calibration();cover();gallery()
 (O/'layout_boxes.json').write_text(json.dumps(boxes,ensure_ascii=False,indent=2));(O/'duplex_manifest.json').write_text(json.dumps(duplex,indent=2))
 (O/'layout_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2))
 print('PDFs gerados. Caixas de texto excedidas:',len(issues)); print(json.dumps(issues[:10],ensure_ascii=False))
