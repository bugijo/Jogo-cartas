"""0.6: copia componentes preservados; gera somente mapas e suas montagens."""
from pathlib import Path
import json,hashlib,shutil,argparse,copy,io
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
import board_art06 as art
P=Path(__file__).resolve().parents[1];BASE=P/'output/edicao-acabamento-v0.5';O=P/'output/edicao-tabuleiros-v0.6'
MAPS=json.loads((P/'content/production/geometry_0.6.json').read_text());SCENES=json.loads((P/'content/production/scenes_0.6.json').read_text())
KEYS={'Mercado':'MERCADO','Hospital':'HOSPITAL','Oficina':'OFICINA','Posto':'POSTO','Condomínio':'CONDOMINIO','Estação':'ESTACAO','Comuns':'COMUNS'}
CHANGED=['06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf','06_TABULEIROS/MERCADO_MONTAGEM.pdf','06_TABULEIROS/DEMAIS_DESTINOS_MONTAGENS.pdf']+['08_EXTRAS_OPCIONAIS/'+KEYS[m['name']]+'_M01_M04_LADO_A.pdf' for m in MAPS]
GEOMETRY=[]
def text(c,s,x,y,size=9,bold=False,col='#294a43'):
 c.setFillColor(art.color(col));c.setFont('Bold' if bold else 'Body',size/mm);c.drawString(x,y,s)
def zone_box(z):
 row,col=divmod(z-1,4);return col*138.5,(3-row)*95,138.5,95
def segments(m):
 es={tuple(sorted(e)) for e in m['edges']};doors={tuple(sorted(e)) for e in m['doors']};blocked={tuple(sorted(e)) for e in m['blocked']}
 for z in m['zones']:
  row,col=divmod(z-1,4);x,y,w,h=zone_box(z)
  sides=[('R',z+1 if col<3 else None),('D',z+4 if row<3 else None)]
  if col==0:sides.append(('L',None))
  if row==0:sides.append(('U',None))
  for side,nb in sides:
   key=tuple(sorted([z,nb])) if nb else None;connected=key in es
   if side in ['L','R']:p1=(x if side=='L' else x+w,y);p2=(p1[0],y+h);center=(p1[0],y+h/2)
   else:p1=(x,y if side=='D' else y+h);p2=(x+w,p1[1]);center=(x+w/2,p1[1])
   yield dict(zone=z,neighbor=nb,side=side,key=list(key) if key else None,connected=connected,door=key in doors,blocked=key in blocked,gap_mm=14 if connected else 0,p1=p1,p2=p2,center=center)

def geometry(c,m,reference=False):
 for s in segments(m):
  x,y=s['p1'];X,Y=s['p2'];cx,cy=s['center'];vertical=s['side'] in ['L','R']
  if not s['connected']:
   # Parede opaca na mesma fronteira: alvenaria, reboco claro e sombra interior.
   art.line(c,x+.55,y-.55,X+.55,Y-.55,'#b3b09a',2.7)
   art.line(c,x,y,X,Y,'#466159',2.1);art.line(c,x,y,X,Y,'#c0bcaa',.85)
  else:
   c.setDash(1.6,2.1)
   if vertical:
    art.line(c,x,y,cx,cy-7,'#667e70',.3);art.line(c,cx,cy+7,X,Y,'#667e70',.3)
   else:
    art.line(c,x,y,cx-7,cy,'#667e70',.3);art.line(c,cx+7,cy,X,Y,'#667e70',.3)
   c.setDash()
   # Ombreiras integram soleiras ao piso; nada cobre o vão com um retângulo branco.
   for off in [-7,7]:
    if vertical:art.rect(c,cx-1,cy+off-.5,2,1,'#8a7959','#485f52',.2)
    else:art.rect(c,cx+off-.5,cy-1,1,2,'#8a7959','#485f52',.2)
   if s['door']:
    if vertical:
     art.line(c,cx,cy-6.5,cx,cy+6.5,'#8e6448',1.7);art.line(c,cx-.3,cy-6,cx-.3,cy+6,'#c1a476',.45)
    else:
     art.line(c,cx-6.5,cy,cx+6.5,cy,'#8e6448',1.7);art.line(c,cx-6,cy+.3,cx+6,cy+.3,'#c1a476',.45)
    if s['blocked']:
     for sign in [-1,1]:art.line(c,cx-3.2,cy-sign*3.2,cx+3.2,cy+sign*3.2,'#943e32',1.1)
     # Extra diagonal form, not color alone.
     art.oval(c,cx-1,cy-1,2,2,'#e4c991','#943e32')
  GEOMETRY.append(dict(destination=m['name'],reference=reference,**s))

def labels(c,m,theme):
 for z in m['zones']:
  x,y,w,h=zone_box(z)
  art.rect(c,x+4,y+h-11,17,7,'#f4efdf','#a6ae97',.6);text(c,f'Z{z:02}',x+5.7,y+h-9,10,True)
  label={m['entry']:'ENTRADA / SAÍDA',m['spawn']:'S / SURGIMENTO'}
  label.update({v:f'B{i+1} / BUSCA' for i,v in enumerate(m['search'])});label.update({v:f'O{i+1} / OBJETIVO' for i,v in enumerate(m['objectives'])})
  if z in label:
   art.rect(c,x+4,y+h-21,53,7,'#f4efdf','#a6ae97',.6);text(c,label[z],x+6,y+h-18.5,8.5,True,'#943e32' if z==m['spawn'] else '#294a43')
 # Identificações ficam dentro do corte, sem atravessar a junção vertical.
 for i,(x,y) in enumerate([(0,190),(277,190),(0,0),(277,0)],1):
  art.rect(c,x+3,y+2,94,4,'#f4efdf');text(c,f'M{i} / {theme.upper()} / A / TOPO ↑ / 0.6',x+4,y+3,5.8)

def signature(theme):
 h=hashlib.sha256()
 for path in [P/'src/build_boards06.py',P/'src/board_art06.py',P/'content/production/geometry_0.6.json',P/'content/production/crops_0.6.json']:
  h.update(path.read_bytes())
 h.update(json.dumps(SCENES[theme],sort_keys=True,ensure_ascii=False).encode())
 h.update((P/'assets/v0.6/pisos_materiais.png').read_bytes())
 for name in sorted({o['file'] for o in SCENES[theme]['objects'] if o['kind']=='asset'}):h.update((P/name).read_bytes())
 return h.hexdigest()

def full_board(theme,edition='ilustrada',reference=False):
 art.ECON=edition=='economica';m=copy.deepcopy(next((m for m in MAPS if m['name']==theme),MAPS[0]))
 if theme=='Comuns':m['name']='Comuns';m['blocked']=[]
 folder=O/('plantas_funcionais' if reference else 'fontes_tabuleiros')/edition;folder.mkdir(parents=True,exist_ok=True);path=folder/(KEYS[theme]+'.pdf')
 c=canvas.Canvas(str(path),pagesize=(554*mm,380*mm),invariant=1);c.setTitle(f'Zona Zero 0.6 / {theme} / '+('planta funcional' if reference else 'cena global'))
 c.setSubject(('GEOMETRIA_CONGELADA' if reference else 'ZZ06_SOURCE_SHA256='+signature(theme))+' / A pisos / B mobiliário / C ambientação / D geometria / E sinais')
 key='ZZ06_'+KEYS[theme]
 if not reference:
  c.beginForm(key,0,0,554*mm,380*mm);c.saveState();c.scale(mm,mm);art.scene(c,theme,SCENES[theme]);c.restoreState();c.endForm();c.doForm(key)
 else:
  c.saveState();c.scale(mm,mm);art.rect(c,0,0,554,380,'#ffffff');c.restoreState()
 c.saveState();c.scale(mm,mm);geometry(c,m,reference);labels(c,m,theme);c.restoreState();c.showPage();c.save();return path

def split_board(source,destination,theme):
 destination.parent.mkdir(parents=True,exist_ok=True)
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=landscape(A4),invariant=1)
 c.setTitle('Zona Zero 0.6 / '+theme+' / quatro módulos')
 for i in range(4):
  c.saveState();c.scale(mm,mm);text(c,f'M{i+1} / {theme} / LADO A / TOPO ↑ / corte 277×190 mm / união sem sobreposição / 0.6',10,203,6.8)
  for x,y,dx,dy in [(10,10,-2,0),(287,10,2,0),(10,200,-2,0),(287,200,2,0),(10,10,0,-2),(287,10,0,-2),(10,200,0,2),(287,200,0,2)]:art.line(c,x,y,x+dx,y+dy,'#67796b',.22)
  c.restoreState();c.showPage()
 c.save();doc=fitz.open(stream=buf.getvalue(),filetype='pdf');full=fitz.open(source)
 for i,page in enumerate(doc):
  x=(i%2)*277;y=(i//2)*190;page.show_pdf_page(fitz.Rect(10*mm,10*mm,287*mm,200*mm),full,0,clip=fitz.Rect(x*mm,y*mm,(x+277)*mm,(y+190)*mm))
 metadata=doc.metadata;metadata['subject']=full.metadata['subject'];doc.set_metadata(metadata);doc.save(destination,garbage=4,deflate=True);return destination

def miniature(theme,edition):
 # Miniatura de ambientação SEM textos/portas: somente A–C é rasterizado a 200 ppi.
 folder=O/'miniaturas'/edition;folder.mkdir(exist_ok=True,parents=True);path=folder/(KEYS[theme]+'.png')
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(554*mm,380*mm),invariant=1);start=len(art.USES)
 c.saveState();c.scale(mm,mm);art.scene(c,theme,SCENES[theme]);c.restoreState();c.save()
 del art.USES[start:]
 doc=fitz.open(stream=buf.getvalue(),filetype='pdf');scale=170/554*200/72;pix=doc[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);pix.save(path)
 art.USES.append(dict(theme=theme,file=str(path.relative_to(P)),role='miniatura derivada de A–C; D–E continuam vetoriais',original_pixels=[pix.width,pix.height],used_pixels=[pix.width,pix.height],crop_pixels=[0,0,pix.width,pix.height],print_mm=[170,380*170/554],effective_ppi=min(pix.width/(170/25.4),pix.height/(380*170/554/25.4)),edition=edition))
 return path

def diagrams(root,indices,name):
 dest=root/'06_TABULEIROS'/name;buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=landscape(A4),invariant=1);art.ECON=root.name=='economica'
 for idx in indices:
  m=MAPS[idx];image=miniature(m['name'],root.name);c.saveState();c.scale(mm,mm);text(c,m['name'].upper()+' / MONTAGEM 0.6',11,192,17,True)
  text(c,'M1 M2 em cima; M3 M4 embaixo. Topo ↑. Não girar. Corte e união sem sobreposição.',11,181,8.5)
  # O form contém a arte da miniatura; geometria, números e símbolos são texto/vetor.
  key='ZZ06_MINI_'+KEYS[m['name']];c.beginForm(key,0,0,170,380*170/554);c.drawImage(str(image),0,0,170,380*170/554);c.endForm()
  c.saveState();c.translate(11,54);c.doForm(key);c.saveState();c.scale(170/554,170/554);geometry(c,m);c.restoreState()
  scale=170/554
  for z in m['zones']:
   x,y,w,h=zone_box(z);X,Y=x*scale,y*scale
   art.rect(c,X+1.2,Y+h*scale-5,8,4.3,'#f4efdf');text(c,str(z),X+2,Y+h*scale-4,7.5,True)
   tag={1:'E/S',5:'B1',12:'B2',7:'O1',14:'O2',16:'S'}.get(z)
   if tag:art.rect(c,X+1.2,Y+1,11,4.5,'#f4efdf');text(c,tag,X+2,Y+2,7.2,True)
  c.restoreState()
  for label,x,y in [('M1',11,173),('M2',96,173),('M3',11,47),('M4',96,47)]:text(c,label,x,y,9,True)
  lines=['MESMA GEOMETRIA','Parede espessa: sem conexão.','Tracejado: fronteira aberta.','Vão central: passagem de 14 mm.','Barra: porta. X: bloqueada.','Móveis: sem obstáculo/cobertura.','','Entrada e saída: Z1.','B1: Z5. B2: Z12.','O1: Z7. O2: Z14. S: Z16.','','Portas: 1–5, 3–7, 7–8,','9–13 e 13–14.','Bloqueadas: '+(', '.join(f'{x}–{y}' for x,y in m['blocked']) or 'nenhuma')+'.','','Grupo inicial: ceil(H/2) Errantes','em S; rota longa reduz um.']
  if m['name']=='Estação':lines+=['Acrescente Bruto na Z14.']
  for j,word in enumerate(lines):text(c,word,191,170-j*7,9.3,j==0)
  text(c,'Use quatro módulos comuns OU quatro temáticos. Não imprimir ambos para a mesma montagem.',11,24,9.2,True)
  text(c,'Coloque os marcadores de portas e bloqueios conforme este diagrama. Achados e resgates seguem a campanha.',11,15,8.3)
  c.restoreState();c.showPage()
 c.setSubject('ZZ06_SOURCE_SHA256='+hashlib.sha256(''.join(signature(MAPS[i]['name']) for i in indices).encode()).hexdigest());c.save()
 doc=fitz.open(stream=buf.getvalue(),filetype='pdf');doc.save(dest,garbage=4,deflate=True)

def copy_preserved(root):
 for f in (BASE/root.name).rglob('*.pdf'):
  rel=f.relative_to(BASE/root.name)
  if str(rel) in CHANGED:continue
  target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)

def index(root):
 data=json.loads((BASE/root.name/'00_LEIA_PRIMEIRO/manifesto.json').read_text());data['version']='0.6';data['maps_replaced']=CHANGED;data['preserved_from']='0.5 / b99c470'
 for e in data['files']:
  path=root/e['file'];e['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();e['edition']=root.name
 folder=root/'00_LEIA_PRIMEIRO';folder.mkdir(exist_ok=True,parents=True);(folder/'manifesto.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 textmd='# Zona Zero 0.6 / '+root.name+'\n\nEscolha duplex (58 A4) OU recortar e colar (72 A4). Extras opcionais, não somar alternativas. Cartas, painel, peões, abrigo e regras são os PDFs preservados da 0.5.\n\nMapas: A4 paisagem, uma face, 100%, sem ajustar. Corte 277×190 mm; M1/M2 acima, M3/M4 abaixo, topo para cima, união sem sobreposição. As seis variantes substituem os quatro comuns, nunca são obrigatórias.\n\n'
 for method in ['duplex','manual']:
  textmd+='## '+method+'\n\n| PDF | Etapa | Folhas | Impressão |\n|---|---|---:|---|\n'
  for e in data['files']:
   if not e['optional'] and e['method'] in ['both',method]:textmd+=f'| [{e["file"]}](../{e["file"]}) | {e["stage"]} | {e["sheets"]} | '+('duplex retrato, borda longa' if e['duplex'] else 'uma face, '+e['orientation'])+' |\n'
 for method,expected in [('duplex',58),('manual',72)]:assert sum(e['sheets'] for e in data['files'] if not e['optional'] and e['method'] in ['both',method])==expected
 (folder/'IMPRIMA_ESTES.md').write_text(textmd)

def build(pilot=False,maps_only=False):
 O.mkdir(exist_ok=True,parents=True)
 for theme in ['Comuns']+[m['name'] for m in MAPS]:full_board(theme,reference=True)
 for ed in ['ilustrada','economica']:
  root=O/ed
  for d in ['06_TABULEIROS','08_EXTRAS_OPCIONAIS']:(root/d).mkdir(parents=True,exist_ok=True)
  if not pilot and not maps_only:copy_preserved(root)
  for theme in (['Mercado'] if pilot else ['Comuns']+[m['name'] for m in MAPS]):
   source=full_board(theme,ed);rel=('06_TABULEIROS/' if theme=='Comuns' else '08_EXTRAS_OPCIONAIS/')+KEYS[theme]+'_M01_M04_LADO_A.pdf';split_board(source,root/rel,theme)
  if not pilot:
   diagrams(root,[0],'MERCADO_MONTAGEM.pdf');diagrams(root,list(range(1,6)),'DEMAIS_DESTINOS_MONTAGENS.pdf')
   if not maps_only:index(root)
 (O/'geometry.json').write_text(json.dumps(GEOMETRY,ensure_ascii=False,indent=2));(O/'asset_usage.json').write_text(json.dumps(art.USES,ensure_ascii=False,indent=2))
 print('0.6 /', 'piloto' if pilot else 'todos os mapas','/ usos raster:',len(art.USES))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--maps-only',action='store_true');args=parser.parse_args();build(args.pilot,args.maps_only)
