"""Edição artística 0.3. Lê a seleção 0.2, nunca modifica conteúdo ou geradores anteriores.
Uso: python src/build_illustrated.py [--cycle 1..5]
"""
from pathlib import Path
import json,math,shutil,copy,argparse,hashlib
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import white,HexColor
import build as b
import illustrated_art as a
P=b.P;BASE=P/'output/comece-aqui-duas-pessoas';OUT=P/'output/edicao-ilustrada-v0.3'
D=b.D;M=json.loads((BASE/'manifesto.json').read_text());CARDS={x['id']:x for x in D['cards']};HEROES={x['id']:x for x in D['heroes']};TOKENS={x['id']:x for x in D['tokens']}
GEOMETRY=[]; DUPLEX=[];ASSETS=[]

def txt(c,t,x,y,size=9,bold=False,col=a.INK):
 c.setFillColor(a.color(col));c.setFont('Bold' if bold else 'Body',size);c.drawString(x*mm,y*mm,t)
def paragraph(c,t,x,y,w,h,size=10,bold=False,label=''):
 b.para(c,t,x*mm,y*mm,w*mm,h*mm,size,bold,file=LABEL,page=PAGE,label=label)
def heading(c,title,sub,W=297,H=210):
 a.rect(c,10*mm,(H-23)*mm,(W-20)*mm,13*mm,a.PAPER,stroke=a.PAPER)
 txt(c,title,13,H-19,17,True);txt(c,sub,11,H-30,8)

REGIONS={
 'equipment.png':([[6,504],[518,1017],[1031,1530]],[[3,296],[306,612],[622,1017]]),
 'buildings.png':([[11,500],[520,1015],[1036,1526]],[[8,332],[348,673],[689,1015]]),
 'portraits_01.png':([[11,331],[352,673],[693,1016]],[[9,374],[390,759],[772,1139],[1153,1524]]),
 'portraits_02.png':([[8,335],[349,676],[690,1017]],[[6,374],[385,761],[772,1134],[1144,1527]]),
 'encounters.png':([[0,506],[520,1024]],[[0,346],[357,707],[718,1092],[1102,1536]]),
 'enemies.png':([[22,600],[623,1201]],[[0,600],[619,1267]])}
DERIVED=set()
def art_for_print(art):
 art=art.copy();name=Path(art['path']).name
 if 'crop' not in art and name in REGIONS:
  cols,rows=REGIONS[name];l,r=cols[art.get('col',0)];t,bot=rows[art.get('row',0)];art['crop']=[l,t,r,bot]
 if not a.ECON:return art
 path=P/art['path'];out=P/'assets/v0.3/economica'/path.name
 if out not in DERIVED:
  from PIL import Image,ImageOps
  out.parent.mkdir(parents=True,exist_ok=True)
  original=Image.open(path);im=ImageOps.grayscale(original);im=im.point(lambda v:min(255,int(v*.75+63.75)))
  if original.mode=='RGBA':im=Image.merge('LA',(im,original.getchannel('A')))
  im.save(out);DERIVED.add(out)
 result=art.copy();result['path']=str(out.relative_to(P));return result

def raster(c,art,x,y,w,h):
 art=art_for_print(art)
 if 'crop' not in art:b.sheet_art(c,art,x*mm,y*mm,w*mm,h*mm);return
 from PIL import Image
 iw,ih=Image.open(P/art['path']).size;l,t,r,bot=art['crop'];cw,ch=r-l,bot-t;scale=(max if art.get('fill') else min)(w*mm/cw,h*mm/ch);ax=x*mm+(w*mm-cw*scale)/2;ay=y*mm+(h*mm-ch*scale)/2
 c.saveState();path=c.beginPath();path.rect(x*mm,y*mm,w*mm,h*mm) if art.get('fill') else path.rect(ax,ay,cw*scale,ch*scale);c.clipPath(path,stroke=0)
 c.drawImage(str(P/art['path']),ax-l*scale,ay-(ih-bot)*scale,width=iw*scale,height=ih*scale,mask='auto');c.restoreState()
def portrait(c,hero,x,y,w,h):
 art=hero['art'].copy();art['fill']=True;raster(c,art,x/mm,y/mm,w/mm,h/mm)
def sprite(c,index,x,y,w,h):
 art=dict(path='assets/v0.3/map_objects_alpha.png',col=index%4,row=index//4,cols=4,rows=4)
 if (P/art['path']).exists():b.sheet_art(c,art_for_print(art),x,y,w,h)
a.SPRITE_DRAW=sprite
def scene(c,index,x,y,w,h):
 f=P/'assets/v0.3/environments.png'
 if f.exists():
  top,bottom=[(0,315),(326,633),(645,1024)][index//2];left=768*(index%2)
  raster(c,dict(path=str(f.relative_to(P)),crop=[left,top,left+768,bottom]),x,y,w,h)

def geometry(c,z,x,y,w,h,scale=1,doors=None,blocked=None):
 """B: geometria exata, independente da arte A. Abertura proporcional 14 mm."""
 r,col=divmod(z-1,4);edges={tuple(sorted(e)) for e in D['maps'][0]['edges']}
 for side,nb in [('L',z-1 if col else None),('R',z+1 if col<3 else None),('U',z-4 if r else None),('D',z+4 if r<3 else None)]:
  key=tuple(sorted((z,nb))) if nb else None;connected=key in edges;gap=14*scale if connected else 0
  if side in ['L','R']:
   xx=x if side=='L' else x+w;mid=y+h/2
   a.line(c,xx*mm,y*mm,xx*mm,(mid-gap/2)*mm,width=2.4*scale)
   a.line(c,xx*mm,(mid+gap/2)*mm,xx*mm,(y+h)*mm,width=2.4*scale)
   center=(xx,mid)
  else:
   yy=y if side=='D' else y+h;mid=x+w/2
   a.line(c,x*mm,yy*mm,(mid-gap/2)*mm,yy*mm,width=2.4*scale)
   a.line(c,(mid+gap/2)*mm,yy*mm,(x+w)*mm,yy*mm,width=2.4*scale)
   center=(mid,yy)
  if connected and side in ['R','D'] and doors is not None and key in doors:
   xx,yy=center;s=max(2,4*scale)
   a.rect(c,(xx-s/2)*mm,(yy-s/2)*mm,s*mm,s*mm,a.PAPER)
   if key in blocked:
    a.line(c,(xx-s/2)*mm,(yy-s/2)*mm,(xx+s/2)*mm,(yy+s/2)*mm,a.RUST,1)
    a.line(c,(xx-s/2)*mm,(yy+s/2)*mm,(xx+s/2)*mm,(yy-s/2)*mm,a.RUST,1)
  GEOMETRY.append(dict(file=LABEL,page=PAGE,zone=z,side=side,neighbor=nb,connected=connected,gap_mm=gap/scale,x=x,y=y,w=w,h=h,scale=scale))

def zone(c,z,x,y,w,h,theme='Neutro',scale=1,doors=None,blocked=None):
 a.floor(c,x*mm,y*mm,w*mm,h*mm,z,theme)
 geometry(c,z,x,y,w,h,scale,doors,blocked)
 # C: labels on opaque plaques, never textures beneath rules.
 if scale<1:
  txt(c,str(z),x+1.5,y+h-4,8,True)
  mini={1:'ENTRADA',5:'B1',12:'B2',7:'O1',14:'O2',16:'S'}
  if z in mini:
   a.rect(c,(x+1)*mm,(y+2)*mm,(w-2)*mm,5*mm,a.PAPER,stroke=a.PAPER)
   txt(c,mini[z],x+2,y+3,7.5,True)
  return
 a.rect(c,(x+4*scale)*mm,(y+h-13*scale)*mm,26*scale*mm,9*scale*mm,a.PAPER,stroke=a.PAPER)
 txt(c,f'Z{z:02}',x+6*scale,y+h-11*scale,16*scale,True)
 tags={1:('↔ ENTRADA / SAÍDA','ESTACIONAMENTO'),5:('B1 / BUSCA','3 usos por campanha'),12:('B2 / BUSCA','3 usos por campanha'),7:('O1 / OBJETIVO',''),14:('O2 / OBJETIVO',''),16:('S / SURGIMENTO','')}
 if z in tags:
  t,sub=tags[z];py=y+h*.69
  a.rect(c,(x+4*scale)*mm,py*mm,(w*.46)*mm,13*scale*mm,a.PAPER,stroke=a.PAPER)
  txt(c,t,x+6*scale,py+7*scale,10*scale,True,col=a.RUST if z==16 else a.INK)
  if sub:txt(c,sub,x+6*scale,py+2*scale,7.5*scale)

def maps(folder,theme='Neutro',name='04_modulos_locais.pdf'):
 global LABEL,PAGE
 LABEL=str(folder/name);c=canvas.Canvas(LABEL,pagesize=landscape(A4))
 for PAGE,(r0,c0) in enumerate([(0,0),(0,2),(2,0),(2,2)],1):
  txt(c,f'M{PAGE}  ↑ TOPO  |  {theme}  |  277 × 190 mm  |  100%  |  corte e união sem sobreposição',10,204,7.2)
  for lr in range(2):
   for lc in range(2):zone(c,(r0+lr)*4+c0+lc+1,10+lc*138.5,10+(1-lr)*95,138.5,95,theme)
  c.showPage()
 c.save()

def assemblies(folder,indices,name):
 global LABEL,PAGE
 LABEL=str(folder/name);c=canvas.Canvas(LABEL,pagesize=landscape(A4))
 for PAGE,idx in enumerate(indices,1):
  m=D['maps'][idx];heading(c,m['name'].upper()+' / SANTA AURORA','M1 M2 em cima; M3 M4 embaixo. Topo ↑, rotação 0°. Conexões e zonas idênticas à edição 0.2.')
  scale=150/554;zw=138.5*scale;zh=95*scale
  for z in m['zones']:
   r,col=divmod(z-1,4);zone(c,z,11+col*zw,46+(3-r)*zh,zw,zh,m['name'],scale,{tuple(sorted(e)) for e in m['doors']},{tuple(sorted(e)) for e in m['blocked']})
  scene(c,idx,174,116,111,60)
  txt(c,'AMBIENTAÇÃO / ilustração, não tabuleiro',174,113,7)
  paragraph(c,'SÍMBOLOS\nTraço espesso: parede permanente.\nAbertura: conexão livre. □: porta.\nQuadrado com X: porta bloqueada.\nB: busca. O: objetivo. S: surgimento.\nEntrada e saída: Z1.',174,61,111,52,10)
  paragraph(c,'Portas: '+', '.join(f'{x}–{y}' for x,y in m['doors'])+'.\nBloqueadas: '+(', '.join(f'{x}–{y}' for x,y in m['blocked']) or 'nenhuma')+'.\nInicial: ceil(H/2) Errantes em S; longa −1. Estação acrescenta Bruto em Z14.',174,19,111,37,9.5)
  paragraph(c,'Use os quatro módulos comuns, mudando apenas os marcadores. Móveis são ambientação sem efeito: não bloqueiam, não dão cobertura e não acrescentam buscas. B1 em Z5; B2 em Z12. O1 em Z7; O2 em Z14; S em Z16. Consulte os achados na campanha.',11,13,150,28,9)
  c.showPage()
 c.save()

def shelter(c):
 heading(c,'COMUNIDADE / SANTA AURORA','Planta ilustrativa: terrenos conservam as regras atuais; a distância desenhada não cria efeito mecânico.')
 # A: cena contínua do abrigo, sem geografia com efeito mecânico.
 raster(c,dict(path='assets/v0.3/shelter.png',col=0,row=0,cols=1,rows=1),10,58,180,120)
 sites=[(1,18,139,34,'Barraca • 2 vagas'),(2,53,139,34,'Barraca • 2 vagas'),(3,18,91,34,'Barraca • 2 vagas'),(4,53,91,34,'Barraca • 2 vagas'),(5,90,143,41,'Cozinha ativa'),(6,90,83,42,'Depósito ativo'),(7,120,116,48,'Cisterna danificada')]
 for n,x,y,w,label in sites:
  a.rect(c,x*mm,y*mm,w*mm,10*mm,'#ffffff',stroke=a.OLIVE,r=1*mm)
  txt(c,f'T{n:02} / '+label,x+1,y+6.4,6.8,True)
  txt(c,'Dano □ Projeto ____',x+1,y+2,7)
 for j in range(5):
  x=11+j*35.7;a.rect(c,x*mm,44*mm,34*mm,11*mm,'#ffffff',stroke=a.OLIVE,r=1*mm)
  txt(c,f'T{j+8:02} / LIVRE',x+1,51,7.3,True);txt(c,'Dano □ Projeto ____',x+1,46.5,7)
 txt(c,'PORTÃO / PERÍMETRO',76,60,7.5,True)
 paragraph(c,'Portão ativo □ Defesa 2\nDia: 1 2 3 4 5\nMoral: 0 1 2 3 4 5\nSaúde: 0 1 2 3 4 5\nPressão: 0 1 2 3\nPonte conhecida □\nRelação −2 −1 0 +1 +2\nFila de cercos:\n________________\nC inicial ___ Vagas 8\nConsumidores hoje ___',198,73,88,97,10,label='shelter indicators')
 # A regra existente de garagem usa adjacência: conservar a grade administrativa original.
 txt(c,'Adjacência original dos terrenos / garagem',198,117,7.8,True)
 for n in range(12):
  row,col=divmod(n,4);xx=198+col*21;yy=105-row*9
  a.rect(c,xx*mm,yy*mm,21*mm,9*mm,'#ffffff',stroke=a.OLIVE)
  txt(c,f'T{n+1:02}',xx+6,yy+3,8,True)
 paragraph(c,'População humana ___ / capacidade ___\nComida ___ porções  Água ___ porções\nDanos e reparos: anote no terreno.\nConstruções novas: escreva nos livres.',198,44,88,26,8.8)
 a.rect(c,10*mm,9*mm,277*mm,30*mm,a.PAPER,stroke=a.OLIVE,r=2*mm)
 paragraph(c,'FILTRO / T7 — A: Material+Conexões+1 trabalho □  B: Material+Bomba+1 □  C: Material+Membrana+2 □□\nMáximo dois trabalhos/dia. Ao concluir: 2C água uma vez; depois C por amanhecer. Ativo □ Danificado □\nProjeto B: terreno ____ custos reservados ____ trabalho 0 1 2 3 4\nRelógio: 0 1 2 3 4 5 6 7 8 | 9 10   Pressão local 0 1   Rota curta 1+1 / longa 2+2',12,11,273,26,9.4,label='filter')

def shelter_pdf(folder):
 global LABEL,PAGE
 LABEL=str(folder/'06_paineis_registros.pdf');PAGE=1
 c=canvas.Canvas(LABEL,pagesize=landscape(A4));shelter(c);c.save()
 original=fitz.open(BASE/'01_inicial/06_paineis_registros.pdf');d=fitz.open(LABEL);d.insert_pdf(original,from_page=1,to_page=2);tmp=Path(LABEL).with_suffix('.tmp.pdf');d.save(tmp,garbage=4,deflate=True);d.close();tmp.replace(LABEL)

def travel_art(c,name,x,y,w,h):
 if name=='Cão perdido':raster(c,b.lookup('Aline e cão','MOR'),x,y,w,h);return
 if name=='Ferragens':a.prop(c,'pipes',x*mm,y*mm,w*mm,h*mm);return
 if name=='Barricada':a.prop(c,'pallet',x*mm,y*mm,w*mm,h*mm);return
 if name=='Vizinho na janela':
  art=next(z for z in D['heroes'] if z['name']=='Otávio')['art'];raster(c,art,x+3,y,w-6,h)
  a.rect(c,(x+2)*mm,y*mm,2*mm,h*mm,a.RUST);a.rect(c,(x+w-4)*mm,y*mm,2*mm,h*mm,a.RUST)
  a.line(c,(x+2)*mm,(y+h*.5)*mm,(x+w-2)*mm,(y+h*.5)*mm,a.RUST,2);return
 if name=='Ruído distante':raster(c,b.lookup('Errante'),x,y,w,h);return
 if name=='Ponte avistada':
  a.rect(c,x*mm,(y+h*.25)*mm,w*mm,h*.4*mm,a.CONCRETE,stroke=a.CONCRETE)
  for j in range(8):a.line(c,(x+j*w/8)*mm,(y+h*.25)*mm,(x+j*w/8)*mm,(y+h*.65)*mm,a.PAPER,2)
  for yy in [.21,.69]:a.line(c,x*mm,(y+h*yy)*mm,(x+w)*mm,(y+h*yy)*mm,a.RUST,2)
  return
 a.rect(c,x*mm,(y+h*.18)*mm,w*mm,h*.63*mm,a.CONCRETE,stroke=a.CONCRETE)
 for j in range(4):a.line(c,(x+j*w/4)*mm,(y+h*.48)*mm,(x+(j+.5)*w/4)*mm,(y+h*.48)*mm,a.PAPER,1)
 if name=='Chuva ácida de fuligem':
  for j in range(9):a.line(c,(x+j*w/9)*mm,(y+h*.9)*mm,(x+(j+.4)*w/9)*mm,(y+h*.1)*mm,a.INK,.6)
 elif name in ['Sinal de passagem','Desvio sinalizado']:
  a.line(c,(x+w*.3)*mm,(y+h*.45)*mm,(x+w*.7)*mm,(y+h*.45)*mm,a.YELLOW,4)
  a.poly(c,[((x+w*.7)*mm,(y+h*.7)*mm),((x+w*.7)*mm,(y+h*.2)*mm),((x+w*.95)*mm,(y+h*.45)*mm)],a.YELLOW)
 elif name=='Emboscada':raster(c,b.lookup('Corredor'),x,y,w,h)
 else:a.prop(c,'van',(x+w*.25)*mm,(y+h*.3)*mm,w*.5*mm,h*.35*mm)

def card_art(c,card,x,y,large=False):
 ax,ay,aw,ah=(x+10,y+31,43,31) if large else (x+40,y+56,19,20)
 name=card['name'];fam=card['family'];art=b.lookup(name,fam)
 if fam=='MOR':
  # Character portraits are the canonical identity in all playable components.
  names={'Jana e criança':['Jana'],'Bia':['Bia'],'Vicente e Sol':['Vicente','Sol'],'Raul e Otávio':['Raul','Otávio'],'Denise, Miguel e civil':['Denise','Miguel'],'Samuel, Bruna e criança':['Samuel','Bruna'],'Aline e cão':['Aline'],'Hugo':['Hugo']}[name]
  for i,n in enumerate(names):
   hero=next(h for h in D['heroes'] if h['name']==n);portrait(c,hero,(ax+i*aw/len(names))*mm,ay*mm,(aw/len(names))*mm,ah*mm)
 elif art:raster(c,art,ax,ay,aw,ah)
 else:
  kind={'Conexões':'pipes','Bateria':'battery','Kit de instalação médica':'medicine','Bancada':'bench','Van de manutenção':'van'}
  if fam in ['SAQ','REC']:
   resource=name.split(': ')[-1];kind2={'Conserva':'can','Água':'water','Carne':'meat','Material':'crate','Medicamento':'medicine','Munição':'ammo','Combustível':'fuel','Madeira':'pallet','Lona':'tent','Sementes':'tree'}[resource]
  elif fam=='HOR':
   art=b.lookup('Corredor' if name=='Corrida' else 'Bruto' if name=='Peso morto' else 'Errante');raster(c,art,ax,ay,aw,ah);return
  elif fam=='CER':raster(c,b.lookup('Rival' if 'Ponte' in name or 'Caravana' in name else 'Bruto'),ax,ay,aw,ah);return
  elif fam=='VIA':travel_art(c,name,ax,ay,aw,ah);return
  elif fam=='VIN':
   arts={'Sozinho':b.lookup('Bia','MOR'),'Parceiro ou parceira':b.lookup('Vicente e Sol','MOR'),'Filho ou filha':b.lookup('Jana e criança','MOR'),'Cachorro':b.lookup('Aline e cão','MOR'),'Parceiro e cachorro':b.lookup('Aline e cão','MOR')}
   raster(c,arts[name],ax,ay,aw,ah);return
  elif fam=='INT':
   if name=='Solidário':raster(c,b.lookup('Cozinha','STR'),ax,ay,aw,ah)
   elif name=='Assustado':raster(c,b.lookup('Lanterna','EQU'),ax,ay,aw,ah)
   elif name=='Oportunista':
    a.prop(c,'can',ax*mm,ay*mm,aw*.65*mm,ah*mm);a.line(c,(ax+aw*.55)*mm,(ay+ah*.4)*mm,(ax+aw*.95)*mm,(ay+ah*.4)*mm,a.RUST,2)
   else:
    for j in range(6):a.line(c,(ax+j*aw/6)*mm,ay*mm,(ax+j*aw/6)*mm,(ay+ah)*mm,a.OLIVE,2)
    a.line(c,ax*mm,(ay+ah*.5)*mm,(ax+aw)*mm,(ay+ah*.5)*mm,a.RUST,2)
   return
  else:kind2=kind.get(name,'bench')
  a.prop(c,kind2,ax*mm,ay*mm,aw*mm,ah*mm)

def cards(folder,ids,name,initial=False):
 global LABEL,PAGE
 LABEL=str(folder/name);c=canvas.Canvas(LABEL,pagesize=A4)
 for sn in range(math.ceil(len(ids)/9)):
  batch=ids[sn*9:sn*9+9]
  for back in [False,True]:
   PAGE=sn*2+1+int(back);txt(c,f'Folha {sn+1:02} | '+('VERSO • borda longa' if back else 'FRENTE')+' | 100% | edição artística 0.3',8.5,7,7)
   for i,id in enumerate(batch):
    card=CARDS[id];r,col=divmod(i,3);col=2-col if back else col;x=8.5+col*65;y=297-14.5-(r+1)*88-r*2;fam=card['family']
    a.rect(c,x*mm,y*mm,63*mm,88*mm,'#ffffff',stroke='#a0aaa5')
    if not back:
     a.rect(c,(x+3)*mm,(y+76)*mm,57*mm,8*mm,a.INK,stroke=a.INK)
     a.poly(c,[((x+3)*mm,(y+76)*mm),((x+8)*mm,(y+76)*mm),((x+10)*mm,(y+84)*mm),((x+3)*mm,(y+84)*mm)],a.YELLOW)
     b.family_icon(c,fam,(x+4)*mm,(y+78)*mm,4*mm)
     txt(c,b.FAMILIES[fam].upper(),x+12,y+79,8,True,col='#ffffff')
     text=card['text'].replace('ceil(H/2)','1') if initial else card['text']
     large=len(text)<118
     card_art(c,card,x,y,large)
     paragraph(c,card['name'],x+4,y+(64 if large else 57),55 if large else 35,11 if large else 18,11 if large else 10.5,True,label=id+' title')
     paragraph(c,text,x+4,y+12,55,18 if large else 44,9.5,label=id)
     txt(c,id+' • arte 0.3 / regras 0.2',x+4,y+5,6.3)
    else:
     # Every back of one family uses precisely the same marks and colours.
     a.rect(c,(x+4)*mm,(y+4)*mm,55*mm,80*mm,a.PAPER,stroke=a.INK,r=2*mm)
     for j in range(5):a.line(c,(x+7+j*10)*mm,(y+7)*mm,(x+7+j*10)*mm,(y+81)*mm,'#d1d8ca',.4)
     a.rect(c,(x+8)*mm,(y+23)*mm,47*mm,44*mm,'#ffffff',stroke=a.INK)
     txt(c,'ZONA ZERO',x+10,y+57,16,True);txt(c,'COMUNIDADE',x+10,y+50,10,True)
     b.family_icon(c,fam,(x+26)*mm,(y+35)*mm,10*mm)
     paragraph(c,b.FAMILIES[fam].upper(),x+10,y+24,43,9,10,True,label='back '+fam)
     DUPLEX.append(dict(file=LABEL,page=PAGE,id=id,family=fam,row=r,front_col=i%3,back_col=col))
   c.showPage()
 c.save()

def heroes(folder,ids,name,embedded=False):
 global LABEL,PAGE
 LABEL=str(folder/name);c=canvas.Canvas(LABEL,pagesize=A4)
 for i,id in enumerate(ids):
  PAGE=i//2+1;off=148.5 if i%2==0 else 0;h=HEROES[id]
  c.saveState();c.translate(0,off*mm)
  a.rect(c,8*mm,130*mm,194*mm,13*mm,a.PAPER,stroke=a.PAPER)
  txt(c,h['name'].upper(),10,135,19,True);txt(c,h['profession'],57,135,10,True)
  portrait(c,h,9*mm,68*mm,40*mm,59*mm)
  for j,(attr,val) in enumerate(h['attributes'].items()):
   xx=55+j*48;a.rect(c,xx*mm,115*mm,44*mm,12*mm,a.PAPER,stroke=a.OLIVE,r=2*mm);txt(c,f'{attr.upper()} {val}',xx+2,119,10,True)
  body=h['story']+'\nInicial: '+h['ability']+'\n3 XP — escolha: '+' OU '.join(h['progression']['3'])+'\n6 XP — escolha: '+' OU '.join(h['progression']['6'])+'\n9 XP — escolha: '+' OU '.join(h['progression']['9'])
  paragraph(c,body,55,52,145,60,9.5,label=id+' rules')
  txt(c,'Vida 3 • PA 3',10,62,9,True);txt(c,'Mochila 4 cargas',10,57,8.5,True)
  paragraph(c,h['unlock']+' • Manual §§3,13 • '+id,10,46,190,8,7.5,label=id+' unlock')
  txt(c,'XP ___  Escolhas 3/6/9: __________  Ferimentos ___  Fadiga ___  Fome □ Sede □  Vínculo ____',10,41,8.3)
  for j in range(4):
   xx=10+j*47.5;a.rect(c,xx*mm,27*mm,45*mm,10*mm,'#ffffff',stroke='#a2b09f');txt(c,f'Carga {j+1}: __________',xx+2,31,8)
  if embedded:
   txt(c,f'ITEM ÚNICO ZC-EQU-000{i+1} | Pé de cabra | carga 1',10,22,8,True)
   txt(c,'Ataque próximo: 1 PA, d6+Corpo contra Defesa, dano 1.',10,17,8.3)
   txt(c,f'Local inicial: {h["name"]}. Local atual: __________. Transferir altera o local; nunca cria outra cópia.',10,12,8)
  else:
   txt(c,'Equipamentos / armas (máximo duas transportadas): __________________________________',10,21,8.4)
   txt(c,'Local dos itens e alterações de capacidade: ___________________________________________',10,14,8.4)
  a.line(c,8*mm,5*mm,202*mm,5*mm,'#8b9c91',.5);c.restoreState()
  if i%2:c.showPage()
 if len(ids)%2:c.showPage()
 c.save()

def markers(folder,ids,name):
 global LABEL,PAGE
 LABEL=str(folder/name);PAGE=1;c=canvas.Canvas(LABEL,pagesize=A4)
 for i,id in enumerate(ids):
  t=TOKENS[id];row,col=divmod(i,6);x=10+col*32;y=297-(15+(row+1)*32)
  a.rect(c,x*mm,y*mm,29*mm,29*mm,'#ffffff',stroke=a.INK,r=1*mm)
  if t['kind']=='hero':portrait(c,HEROES[t['hero_ref']],(x+2)*mm,(y+8)*mm,25*mm,19*mm)
  elif t['kind']=='enemy':
   # Generic numbered tokens remain assignable to all types; three canonical silhouettes.
   for j,n in enumerate(['Errante','Corredor','Bruto']):raster(c,b.lookup(n),x+2+j*8,y+15,8,12)
   txt(c,t['name']+'  E/C/B ___',x+2,y+11,7.3,True);txt(c,'Vida ___',x+2,y+6,7.4)
  else:
   n=t['name'];txt(c,n,x+2,y+23,8.2,True)
   cx,cy=(x+14)*mm,(y+13)*mm
   if n in ['Porta','Bloqueio']:
    a.rect(c,cx-5*mm,cy-5*mm,10*mm,10*mm,a.PAPER)
    if n=='Bloqueio':
     a.line(c,cx-4*mm,cy-4*mm,cx+4*mm,cy+4*mm,a.RUST,2);a.line(c,cx-4*mm,cy+4*mm,cx+4*mm,cy-4*mm,a.RUST,2)
    else:a.line(c,cx-4*mm,cy-4*mm,cx+4*mm,cy+4*mm,a.OLIVE,2)
   elif n in ['Busca','Relógio']:
    c.setStrokeColor(a.color(a.INK));c.circle(cx,cy,4*mm,fill=0)
    if n=='Busca':a.line(c,cx+3*mm,cy-3*mm,cx+7*mm,cy-7*mm,a.INK,2)
    else:a.line(c,cx,cy,cx,cy+3*mm,a.INK,1.5);a.line(c,cx,cy,cx+3*mm,cy,a.INK,1.5)
   elif n=='Pressão':
    a.poly(c,[(cx-6*mm,cy-5*mm),(cx+6*mm,cy-5*mm),(cx,cy+6*mm)],a.YELLOW)
    a.line(c,cx,cy-1*mm,cx,cy+3*mm,a.INK,2)
   elif n=='Verificado':
    a.line(c,cx-5*mm,cy,cx-1*mm,cy-4*mm,a.OLIVE,2);a.line(c,cx-1*mm,cy-4*mm,cx+6*mm,cy+5*mm,a.OLIVE,2)
   else:a.prop(c,'water' if n=='Sede' else 'can',(x+8)*mm,(y+6)*mm,13*mm,15*mm)
  txt(c,t['name'] if t['kind']=='hero' else id,x+2,y+3,6.2)
 c.showPage();c.save()

def dividers(folder):
 global LABEL,PAGE
 LABEL=str(folder/'08_divisorias.pdf');PAGE=1;c=canvas.Canvas(LABEL,pagesize=A4)
 labels=['VÍNCULOS','INTENÇÕES','VIAGEM','HORDA','CERCO','SAQUE MERCADO','SAQUE HOSPITAL','SAQUE OFICINA','SAQUE POSTO','SAQUE CONDOMÍNIO','SAQUE ESTAÇÃO','EQUIPAMENTOS / ENCONTROS']
 fams=['VIN','INT','VIA','HOR','CER']+['SAQ']*6+['EQU']
 for i,label in enumerate(labels):
  r,col=divmod(i,2);x=10+96*col;y=297-(14+(r+1)*44)
  a.rect(c,x*mm,y*mm,90*mm,40*mm,'#ffffff',stroke=a.INK)
  a.rect(c,(x+2)*mm,(y+27)*mm,86*mm,11*mm,a.PAPER,stroke=a.PAPER)
  b.family_icon(c,fams[i],(x+4)*mm,(y+29)*mm,6*mm)
  paragraph(c,label,x+13,y+28,73,9,9.5,True,label='divider '+label)
  txt(c,'RESERVA' if i==11 else 'MONTE (esquerda) | DESCARTE (direita)',x+4,y+15,7.8)
  txt(c,'DOBRE A ABA • ajuste à sua caixa e sleeves',x+4,y+3,7)
  c.setDash(3,2);a.line(c,x*mm,(y+8)*mm,(x+90)*mm,(y+8)*mm,a.OLIVE,.5);c.setDash()
 c.showPage();c.save()

def world(folder):
 global LABEL,PAGE
 LABEL=str(folder/'06_mapa_geral.pdf');PAGE=1;c=canvas.Canvas(LABEL,pagesize=landscape(A4))
 heading(c,'SANTA AURORA / ROTAS','Todas saem do abrigo. Curta: 1 trecho/sentido • longa: 2. Mesmo relógio a pé e van.')
 for x in range(14,288,12):a.line(c,x*mm,19*mm,(x-4)*mm,173*mm,'#e0e4d9',2)
 for y in [34,68,110,149]:a.line(c,10*mm,y*mm,287*mm,(y+3)*mm,'#e0e4d9',3)
 positions=[(51,143),(148,143),(245,143),(51,58),(148,58),(245,58)]
 for i,(m,(x,y)) in enumerate(zip(D['maps'],positions)):
  a.line(c,148*mm,102*mm,x*mm,y*mm,a.OLIVE,2)
  a.rect(c,(x-40)*mm,(y-30)*mm,80*mm,62*mm,'#ffffff',stroke=a.OLIVE,r=2*mm)
  scene(c,i,x-37,y-9,74,37);txt(c,m['name'].upper(),x-36,y-17,10.5,True)
  txt(c,'Curta: risco normal | Longa: −1 inicial',x-36,y-23,6.8);txt(c,'Estado NV / C / P / E',x-36,y-28,7)
 a.rect(c,125*mm,92*mm,47*mm,17*mm,a.PAPER,r=2*mm);txt(c,'ABRIGO',130,98,13,True)
 c.save()

def decorate_existing(root):
 # Existing manuals, calibration and writable registers retain every text and position.
 # A thin botanical/industrial divider in the free margin reinforces identity.
 for f in root.rglob('*.pdf'):
  if f.name not in ['01_comece_aqui.pdf','04_manual_revisado.pdf','05_campanha_cinco_dias.pdf','07_registro_adicional.pdf','09_moradores_adicional.pdf']:continue
  doc=fitz.open(f)
  for page in doc:
   page.draw_line((10*mm,8*mm),(page.rect.width-10*mm,8*mm),color=(.32,.43,.37),width=.8)
  tmp=f.with_suffix('.tmp.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(f)

def gray_pdf(f):
 import re
 doc=fitz.open(f)
 pattern=re.compile(rb'(?<![\d.])([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(rg|RG)\b')
 def sub(m):
  r,g,b2=map(float,m.group(1,2,3));v=.299*r+.587*g+.114*b2
  return f'{v:.6f} '.encode()+(b'g' if m[4]==b'rg' else b'G')
 for xref in range(1,doc.xref_length()):
  if doc.xref_is_stream(xref) and doc.xref_get_key(xref,'Subtype')[1]!='/Image':
   stream=doc.xref_stream(xref);new=pattern.sub(sub,stream)
   if new!=stream:doc.update_stream(xref,new)
 tmp=f.with_suffix('.tmp.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(f)

def init(root):
 for key in ['initial','supplement']:
  for entry in M[key]:
   f=root/entry['file'];f.parent.mkdir(parents=True,exist_ok=True)
   if not f.exists():shutil.copyfile(BASE/entry['file'],f)

def index(root,edition):
 manifest=copy.deepcopy(M);manifest.update(version='0.3',rules_version='0.2',edition=edition,base_commit='9c38aa5',optional_extras={'mapas_tematicos':'6 destinos × 4 folhas = 24 folhas opcionais; cada destino substitui as 4 comuns. Imprimir todos acrescenta 24 folhas se mantiver o kit básico; não obrigatório.','24_fichas':'12 folhas opcionais; não necessárias ao kit de duas pessoas.'})
 for key in ['initial','supplement']:
  for e in manifest[key]:
   doc=fitz.open(root/e['file']);assert len(doc)==e['pages'],(e['file'],len(doc),e['pages']);e['sha256']=hashlib.sha256((root/e['file']).read_bytes()).hexdigest()
 (root/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 text=f'# Comece Aqui — Duas Pessoas / {edition} 0.3\n\nRegras 0.2 preservadas. Imprima **25 folhas iniciais + 33 de complemento = 58 A4**. Escolha somente UMA edição; não misture com PDFs 0.1/0.2.\n\n'
 for key,title in [('initial','Dia 1 — 25 folhas'),('supplement','Antes do dia 2 — 33 folhas')]:
  text+='## '+title+'\n\n| PDF | Páginas | Folhas | Impressão |\n|---|---:|---:|---|\n'
  for e in manifest[key]:text+=f"| [{Path(e['file']).name}]({e['file']}) | {e['pages']} | {e['sheets']} | {'Duplex borda longa' if e['duplex'] else 'Uma face'}, {e['orientation']} |\n"
 text+='\n100%, tamanho real, sem ajustar. Somente cartas e calibração são duplex, retrato, borda longa. Versos refletem colunas e mantêm linhas. Meça a régua de 100 mm antes de imprimir tudo. Mapas: recorte 277 × 190 mm; M1/M2 em cima, M3/M4 embaixo; união sem sobreposição, 554 × 380 mm. Use o diagrama de destino para portas e bloqueios.\n\nMóveis, marcas de piso e paisagismo são ambientação sem efeito de obstáculo ou cobertura. Somente paredes e conectores governam movimento. Os módulos comuns servem a todos os destinos: não reimprima para continuar.\n\nExtras NÃO obrigatórios em extras/: variantes temáticas, quatro folhas por destino (24 ao imprimir os seis), e 24 fichas, 12 folhas. Cada variante substitui os quatro módulos comuns, com portas por marcadores; não some variantes para obter conexões novas. As montagens ilustradas já estão incluídas nas 58 folhas.\n\nTrês dados d6, lápis, borracha, tesoura, fita e envelopes/sleeves opacos são externos. Intenções: versos idênticos; teste opacidade real. Sem impressão física ou playtest humano. Edição econômica mantém todos os componentes, sem reduzir o baralho ou as regras.\n'
 (root/'IMPRIMA-ESTES.md').write_text(text)

LABEL='';PAGE=1
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--cycle',type=int,default=5);args=parser.parse_args()
 for edition in ['ilustrada','economica']:
  root=OUT/edition;root.mkdir(parents=True,exist_ok=True);a.ECON=edition=='economica';init(root);I=root/'01_inicial';S=root/'02_complemento'
  if args.cycle==1:
   samples=OUT/'amostras'/edition;samples.mkdir(parents=True,exist_ok=True);maps(samples);shelter_pdf(samples);cards(samples,M['initial_cards'][-9:],'amostra_cartas.pdf',True)
  if args.cycle>=2:
   maps(I);assemblies(I,[0],'05_montagem_mercado.pdf');assemblies(S,range(1,6),'03_montagens_restantes.pdf')
   extras=root/'extras';extras.mkdir(exist_ok=True)
   for m in D['maps']:maps(extras,m['name'],'mapa_'+m['name'].lower()+'.pdf')
  if args.cycle>=3:
   shelter_pdf(I);world(S);heroes(I,['ZC-HER-0001','ZC-HER-0002'],'03_lia_ivo.pdf',True)
   heroes(S,[h['id'] for h in D['heroes'][12:]],'02_herois_resgataveis.pdf');heroes(root/'extras',[h['id'] for h in D['heroes']],'24_fichas.pdf')
  if args.cycle>=4:
   cards(I,M['initial_cards'],'02_cartas_duplex.pdf',True);cards(S,M['supplement_cards'],'01_cartas_complemento_duplex.pdf')
   markers(I,M['initial_tokens'],'07_marcadores.pdf');markers(S,M['supplement_tokens'],'08_tokens_resgataveis.pdf');dividers(I)
  if args.cycle>=5:
   decorate_existing(root)
   if a.ECON:
    for file in root.rglob('*.pdf'):gray_pdf(file)
   index(root,edition)
 (OUT/'layout_issues.json').write_text(json.dumps(b.issues,ensure_ascii=False,indent=2));(OUT/'layout_boxes.json').write_text(json.dumps(b.boxes,ensure_ascii=False,indent=2));(OUT/'geometry.json').write_text(json.dumps(GEOMETRY,indent=2));(OUT/'duplex.json').write_text(json.dumps(DUPLEX,indent=2))
 print('Ciclo',args.cycle,'estouros:',len(b.issues));print(b.issues[:8])
