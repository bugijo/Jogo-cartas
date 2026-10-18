"""Cenas globais originais 0.5. Coordenadas em mm; tudo vetorial, sem imagem esticada."""
import math,random
from reportlab.lib.units import mm
import illustrated_art as a
W,H=554,380

THEMES={'Mercado':'mercado','Hospital':'hospital','Oficina':'oficina','Posto':'posto','Estação':'estacao','Condomínio':'condominio','Neutro':'oficina'}
from functools import lru_cache
@lru_cache(maxsize=64)
def arrangement_crop(path,index):
 """Analisa o alfa para enquadrar o grupo; desenha sempre os pixels nativos originais."""
 from PIL import Image
 image=Image.open(path);iw,ih=image.size;left=(index%2)*iw//2;top=(index//2)*ih//2;right=(index%2+1)*iw//2;bottom=(index//2+1)*ih//2
 mask=image.crop((left,top,right,bottom)).getchannel('A') if image.mode=='RGBA' else image.crop((left,top,right,bottom)).convert('L').point(lambda v:255 if v<240 else 0)
 native=mask.size;mask=mask.resize((192,128),Image.Resampling.NEAREST);pixels=mask.load();visited=set();groups=[]
 for yy in range(128):
  for xx in range(192):
   if (xx,yy) in visited or pixels[xx,yy]<160:continue
   todo=[(xx,yy)];visited.add((xx,yy));count=0;l=r=xx;t=b=yy
   while todo:
    x,y=todo.pop();count+=1;l=min(l,x);r=max(r,x);t=min(t,y);b=max(b,y)
    for X,Y in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if 0<=X<192 and 0<=Y<128 and (X,Y) not in visited and pixels[X,Y]>=160:visited.add((X,Y));todo.append((X,Y))
   groups.append((count,l,t,r+1,b+1))
 if not groups:return [left,top,right,bottom]
 largest=max(g[0] for g in groups);keep=[g for g in groups if g[0]>=largest*(.15 if path.name=='mapa_mercado.png' else .04)];l=min(g[1] for g in keep);t=min(g[2] for g in keep);r=max(g[3] for g in keep);b=max(g[4] for g in keep)
 return [max(left,left+l*native[0]/192-2),max(top,top+t*native[1]/128-2),min(right,left+r*native[0]/192+2),min(bottom,top+b*native[1]/128+2)]

def detailed(c,index,x,y,w,h,asset_theme=None):
 """Raster nativo pequeno sobre arquitetura global; piso não é uma imagem ampliada."""
 from pathlib import Path
 from PIL import Image
 import build_illustrated as q
 import build_fabrication as f
 theme=getattr(c,'_zz05_theme','Mercado');key=THEMES[asset_theme or theme];path=q.P/'assets/v0.5'/('mapa_'+key+'.png')
 if not path.exists():return False
 art=dict(path=str(path.relative_to(q.P)),cols=2,rows=2,col=index%2,row=index//2)
 art['crop']=arrangement_crop(path,index);l,t,r,b=art['crop'];cw,ch=r-l,b-t
 # Hard native-density guard: no resampling; target ≥170 ppi (reserve above 150).
 ww=min(w,cw*25.4/170);hh=min(h,ch*25.4/170)
 c.saveState();c.scale(1/mm,1/mm);q.raster(c,art,x+(w-ww)/2,y+(h-hh)/2,ww,hh);c.restoreState();return True

def rect(c,x,y,w,h,fill,stroke=None,r=0):
 
 if a.ECON and w*h>6000:fill='#f4f4f0' if fill!='#a5aaa4' and fill!='#9fa8a0' else '#e6e6e0'
 c.setFillColor(a.color(fill));c.setStrokeColor(a.color(stroke or fill));c.setLineWidth(.25)
 if r:c.roundRect(x,y,w,h,r,fill=1,stroke=bool(stroke))
 else:c.rect(x,y,w,h,fill=1,stroke=bool(stroke))
def line(c,x,y,X,Y,col='#526661',width=.35,dash=None):
 c.setStrokeColor(a.color(col));c.setLineWidth(width);c.setDash(dash or []);c.line(x,y,X,Y);c.setDash()
def ellipse(c,x,y,w,h,fill,stroke=None):
 c.setFillColor(a.color(fill));c.setStrokeColor(a.color(stroke or fill));c.setLineWidth(.35);c.ellipse(x,y,x+w,y+h,fill=1,stroke=bool(stroke))
def shadow(c,x,y,w,h):rect(c,x+1.6,y-1.5,w,h,'#b6b5a6',r=1)
def floor(c,theme):
 rect(c,0,0,W,H,'#e4dfcf')
 for x in range(0,555,12):line(c,x,0,x,380,'#d5cfbd',.17)
 for y in range(0,381,12):line(c,0,y,554,y,'#d5cfbd',.17)
 rng=random.Random(451)
 for i in range(1200):
  x=rng.uniform(0,554);y=rng.uniform(0,380);r=rng.uniform(.1,.55);ellipse(c,x,y,r*2,r,'#cbc6b8')
 if theme in ['Mercado','Oficina','Posto','Neutro']:
  rect(c,0,292,277 if theme=='Mercado' else 190,88,'#a5aaa4')
  for x in [8,94,180]:
   line(c,x,298,x,375,'#e0d0a0',.8);line(c,x,298,x+70,298,'#e0d0a0',.8)
  for x in range(5,274,19):rect(c,x,287,10,3,'#b4a06e')
 if theme=='Hospital':
  rect(c,0,292,145,88,'#adb5ae');rect(c,144,290,410,90,'#d2dbd0')
  rect(c,290,0,32,292,'#cedbd7')
  for y in range(8,285,22):rect(c,303,y,6,12,'#729a8b')
 if theme=='Condomínio':
  rect(c,277,0,277,285,'#d7d6c5')
  for x in range(282,555,18):line(c,x,0,x,285,'#bdc2ae',.2)
  for y in range(0,286,18):line(c,277,y,554,y,'#bdc2ae',.2)
 if theme=='Estação':
  rect(c,0,0,554,380,'#d7d8c9')
  for y in range(12,380,23):line(c,0,y,554,y,'#c0c7b8',.25)
  for x in range(12,554,30):line(c,x,0,x,380,'#c0c7b8',.2)

def shelf(c,x,y,w=110,h=16,kind='goods'):
 theme=getattr(c,'_zz05_theme','Mercado');idx=(1 if int(x+y)%3==0 else 0) if theme=='Mercado' else 2 if theme=='Hospital' else 1 if theme in ['Posto','Condomínio'] else 2 if theme=='Oficina' else 3
 if detailed(c,idx,x,y,w,max(h,28)):return
 shadow(c,x,y,w,h);rect(c,x,y,w,h,'#5b6962','#344942',1);rect(c,x+1,y+1,w-2,h-2,'#d0c5a6')
 rng=random.Random(int(x*3+y*7))
 n=max(4,int(w/5.5))
 for row in range(2):
  yy=y+1.5+row*(h/2)
  for i in range(n):
   xx=x+2+i*(w-4)/n;col=rng.choice(['#779178','#c49b61','#a9674f','#d4c8a2','#8a9b9b'])
   if kind=='goods':
    rect(c,xx,yy,3.2,h/2-2,col, r=.3);rect(c,xx+.3,yy+1,2.6,1.7,'#e9e1c9');line(c,xx+.4,yy+4,xx+2.5,yy+4,'#54675e',.22)
   elif kind=='tools':
    line(c,xx,yy,xx+2,yy+h/2-2,'#344b48',.7);ellipse(c,xx+.5,yy+h/2-3,2,2,'#879995','#344b48')
   else:rect(c,xx,yy,3,h/2-2,col)
 line(c,x+1,y+h/2,x+w-1,y+h/2,'#53685e',.8)
 for xx in [x+1,x+w-2]:rect(c,xx,y+1,1,h-2,'#849184')
 theme=getattr(c,'_zz05_theme','Mercado');idx=(1 if int(x+y)%3==0 else 0) if theme=='Mercado' else 2 if theme=='Hospital' else 1 if theme in ['Posto','Condomínio'] else 2 if theme=='Oficina' else 3
 detailed(c,idx,x,y,w,h)
def crate(c,x,y,w=19,h=15):
 shadow(c,x,y,w,h);rect(c,x,y,w,h,'#b29367','#665f48')
 for off in [1.2,3.3]:line(c,x+off,y+1,x+off,y+h-1,'#725e40',.6);line(c,x+w-off,y+1,x+w-off,y+h-1,'#725e40',.6)
 line(c,x+4,y+1,x+w-4,y+h-1,'#cbb08a',1);rect(c,x+w*.35,y+h*.35,w*.3,h*.25,'#e2d3b3')
def pallets(c,x,y,cols=3,rows=2):
 if detailed(c,3,x,y,cols*21-3,rows*18-4):return
 for r in range(rows):
  for col in range(cols):crate(c,x+col*21,y+r*18,18,14)
 detailed(c,3,x,y,cols*21-3,rows*18-4)
def vehicle(c,x,y,w=80,h=35,ambulance=False):
 if not ambulance and detailed(c,2 if getattr(c,'_zz05_theme','')=='Posto' else 1,x,y,w,h,'Posto' if getattr(c,'_zz05_theme','')=='Posto' else 'Oficina'):return
 shadow(c,x,y,w,h)
 for xx in [x+w*.17,x+w*.72]:
  for yy in [y-2,y+h-2]:rect(c,xx,yy,w*.13,4,'#3d4440',r=.8)
 rect(c,x,y,w,h,'#e0ded0' if ambulance else '#73857b','#384c48',5)
 rect(c,x+w*.26,y+3,w*.47,h-6,'#babdb0',r=4);rect(c,x+w*.24,y+4,w*.14,h-8,'#365953',r=1)
 rect(c,x+w*.67,y+5,w*.09,h-10,'#435e57',r=1)
 for yy in [y+2,y+h-4]:line(c,x+w*.41,yy,x+w*.62,yy,'#4c645b',.6)
 for yy in [y+3,y+h-8]:rect(c,x+1,yy,3,5,'#e1c575',r=.7)
 line(c,x+w*.13,y+3,x+w*.18,y+h-4,'#9d8264',.6)
 if ambulance:
  rect(c,x+w*.49,y+h*.25,4,h*.5,'#9e4d40');rect(c,x+w*.43,y+h*.42,w*.18,h*.15,'#9e4d40')
 
 if getattr(c,'_zz05_theme','') in ['Oficina','Neutro','Posto']:detailed(c,2 if getattr(c,'_zz05_theme','')=='Posto' else 1,x,y,w,h)
def cart(c,x,y):
 shadow(c,x,y,17,11);rect(c,x,y,17,11,'#b2bab1','#526761',1)
 for i in range(1,5):line(c,x+i*3,y+1,x+i*3,y+10,'#627c70',.35)
 for yy in [y+3,y+7]:line(c,x+1,yy,x+16,yy,'#627c70',.35)
 line(c,x+18,y+1,x+18,y+10,'#526a5d',1.2)
 for xx in [x+2,x+13]:ellipse(c,xx,y-2,2,2,'#334f47')
def checkout(c,x,y):
 if detailed(c,2 if getattr(c,'_zz05_theme','')=='Mercado' else 1,x,y,30,18):return
 shadow(c,x,y,30,18);rect(c,x,y,30,18,'#91a39a','#4b655d',2);rect(c,x+2,y+2,13,14,'#424e49');rect(c,x+17,y+9,8,7,'#c0bda5','#4b655d',1);rect(c,x+18,y+10,5,4,'#31544c');ellipse(c,x+21,y-6,7,7,'#687e70');detailed(c,2 if getattr(c,'_zz05_theme','')=='Mercado' else 1,x,y,30,18)
def tank(c,x,y,r=36):
 if detailed(c,0,x-r,y-r,2*r,2*r):return
 ellipse(c,x-r+2,y-r-2,2*r,2*r,'#b2bbaa');ellipse(c,x-r,y-r,2*r,2*r,'#6e8c7c','#3f6059');ellipse(c,x-r+3,y-r+3,2*r-6,2*r-6,'#b8c5aa','#475e52');ellipse(c,x-r+6,y-r+6,2*r-12,2*r-12,'#668b80')
 for rr in [.38,.68]:
  c.setStrokeColor(a.color('#a4b9a1'));c.setLineWidth(.3);c.circle(x,y,r*rr,fill=0,stroke=1)
 line(c,x-r,y,x+r,y,'#d1c6a2',2);ellipse(c,x-3,y-3,6,6,'#c4b38a','#56665a');line(c,x,y,x+r*.64,y+r*.55,'#b3ac8a',1.2);detailed(c,0,x-r,y-r,2*r,2*r)
def bed(c,x,y):
 if detailed(c,0,x,y,24,46):return
 shadow(c,x,y,24,46);rect(c,x,y,24,46,'#aeb6ac','#5f736c',2);rect(c,x+2,y+3,20,39,'#e4e5d5',r=2);rect(c,x+3,y+22,18,20,'#6f958b',r=1);rect(c,x+4,y+5,16,7,'#f1eadb',r=2)
 for xx in [x-1,x+24]:line(c,xx,y+5,xx,y+38,'#7a8d81',.9)
 for xx in [x+2,x+20]:ellipse(c,xx,y-2,2,2,'#526a60')
 detailed(c,0,x,y,24,46)
def plant(c,x,y,r=9):
 ellipse(c,x-r+2,y-r-2,r*2,r*2,'#adb19b');ellipse(c,x-r*.8,y-r*.8,r*1.6,r*1.6,'#b19673','#837e5f')
 for i in range(9):
  ang=i*math.pi*2/9;xx=x+math.cos(ang)*r*.45;yy=y+math.sin(ang)*r*.45;ellipse(c,xx-r*.45,yy-r*.2,r*.9,r*.4,['#6f8c6a','#839a6c','#4f7560'][i%3])
 ellipse(c,x-2,y-2,4,4,'#476854')
def bench(c,x,y,w=85):
 if detailed(c,0 if getattr(c,'_zz05_theme','') in ['Oficina','Neutro'] else 2,x,y,w,27):return
 shadow(c,x,y,w,22);rect(c,x,y,w,22,'#a88f6b','#5b6558',1)
 for yy in [y+3,y+10,y+17]:line(c,x+2,yy,x+w-2,yy,'#d3bc8f',.4)
 for i in range(8):
  xx=x+5+i*(w-10)/8;line(c,xx,y+4,xx+4,y+16,'#435b53',1);ellipse(c,xx+2,y+14,4,4,'#849b8d','#3e5e53')
 rect(c,x+3,y+5,18,11,'#52665e',r=1)
 detailed(c,0 if getattr(c,'_zz05_theme','') in ['Oficina','Neutro'] else 2,x,y,w,22)
def sofa(c,x,y,w=65):
 if detailed(c,0,x,y-20,w,47):return
 shadow(c,x,y,w,27);rect(c,x,y,w,27,'#6a8579','#405e52',3);rect(c,x+5,y+4,w-10,16,'#a0ad8e',r=2)
 for xx in [x+4,x+w-10]:rect(c,xx,y+2,6,22,'#80997f',r=2)
 line(c,x+w/2,y+5,x+w/2,y+20,'#5f796b',.45)
 ellipse(c,x+w*.45,y-20,19,13,'#ac936c','#69715d');ellipse(c,x+w*.5,y-17,7,6,'#cab58f');detailed(c,0,x,y-20,w,47)
def pipes(c,points):
 for (x,y),(X,Y) in zip(points,points[1:]):
  line(c,x+1,y-1,X+1,Y-1,'#a5b3a0',4);line(c,x,y,X,Y,'#516e63',3.5);line(c,x,y,X,Y,'#a2b19a',2)
  ellipse(c,x-2,y-2,4,4,'#a5b599','#536a5c')

def scene(c,theme):
 c._zz05_theme=theme;c.saveState();c.scale(mm,mm);floor(c,theme)
 if theme=='Mercado':
  vehicle(c,16,314,72,34);vehicle(c,163,319,80,36)
  for x in [16,35,54]:cart(c,x,302)
  # Setores contínuos; as gôndolas atravessam fronteiras de zona permitidas.
  for y in [202,105,18]:
   for x,w in [(18,110),(170,95),(310,90),(440,95)]:
    if y==18 and x==440:continue
    shelf(c,x,y,w,28)
  for x in [18,62,104]:checkout(c,x,258)
  # Parede fria com portas de vidro desenhadas em vetor, sem escalar um sprite horizontal.
  rect(c,520,105,18,150,'#829e93','#425f57')
  for yy in range(110,250,23):rect(c,522,yy,14,19,'#bbcabe','#476a60',1)
  for x,y,cols,rows in [(297,312,3,3),(440,310,4,3),(450,26,3,2)]:pallets(c,x,y,cols,rows)
  cart(c,309,236);cart(c,474,75);plant(c,8,275,6)
 elif theme=='Oficina':
  vehicle(c,16,314,92,38);bench(c,160,343,171);bench(c,378,343,151)
  for x,y,w,h in [(280,110,130,65),(20,110,105,65),(300,208,110,57)]:
   for off in range(0,int(w),12):line(c,x+off,y,x+off+7,y+8,'#c4aa61',1)
   rect(c,x,y,w,h,'#c9ccbe',r=2)
  vehicle(c,295,126,100,42);vehicle(c,25,123,85,36)
  bench(c,167,210,76);shelf(c,447,230,78,18,'tools');bench(c,323,35,190)
  for x,y in [(23,36),(182,44),(456,130)]:pallets(c,x,y,2,2)
  for x,y in [(480,307),(300,270),(100,224)]:ellipse(c,x,y,16,16,'#3f4b45');ellipse(c,x+3,y+3,10,10,'#9aa697');line(c,x,y,x+23,y+14,'#9d7754',1)
 elif theme=='Hospital':
  vehicle(c,18,314,100,43,True);checkout(c,183,329);checkout(c,215,329)
  for x in range(280,510,25):rect(c,x,344,20,14,'#6f8e7d','#4a655c',2)
  for x,y in [(20,219),(82,219),(345,223),(470,224),(20,115),(85,116),(346,116),(468,116),(25,24),(88,24),(345,25),(470,25)]:bed(c,x,y)
  for x,y,w in [(178,220,70),(180,120,68),(174,35,80),(430,312,88)]:shelf(c,x,y,w,14,'medical')
  plant(c,269,329,11);plant(c,532,275,9)
 elif theme=='Posto':
  rect(c,0,0,190,289,'#9fa8a0')
  for y in range(12,288,34):rect(c,31,y,3,16,'#e0d1a7')
  vehicle(c,68,312,96,38);vehicle(c,65,114,92,36)
  for x,y in [(264,227),(424,227),(264,116),(424,116)]:
   shadow(c,x-12,y-8,64,28);rect(c,x-12,y-8,64,28,'#c8c7b4','#8d977f',7)
   for xx in [x,x+26]:
    rect(c,xx,y,14,18,'#8f9e8b','#435e55',2);rect(c,xx+2,y+8,10,7,'#31564d');rect(c,xx+3,y+10,8,3,'#c4c8a0');line(c,xx+15,y+12,xx+21,y-3,'#485b50',1);line(c,xx+21,y-3,xx+17,y-3,'#485b50',1)
  shelf(c,280,334,120,17);shelf(c,431,333,102,17);checkout(c,450,302)
  pallets(c,441,25,4,2);bench(c,225,31,90)
 elif theme=='Estação':
  for x,y,r in [(80,337,34),(350,336,35),(481,145,34),(345,48,34)]:tank(c,x,y,r)
  pipes(c,[(15,289),(538,289),(538,20),(400,20)])
  for x,y in [(25,210),(173,210),(315,210),(35,115),(178,30)]:
   shadow(c,x,y,70,34);rect(c,x,y,70,34,'#9daa94','#526e60',2)
   for xx in [x+5,x+27,x+49]:rect(c,xx,y+5,14,24,'#527e73','#395a54',5);ellipse(c,xx+4,y+13,6,6,'#c7b78b')
  bench(c,430,335,94);shelf(c,429,222,95,17,'tools');pallets(c,25,28,3,2)
 elif theme=='Condomínio':
  vehicle(c,18,315,94,37);sofa(c,175,330,80);shelf(c,330,339,174,17)
  sofa(c,20,225,84);sofa(c,178,225,74);sofa(c,23,122,82);sofa(c,173,35,82)
  for x,y in [(340,238),(480,235),(353,140),(480,40)]:plant(c,x,y,17)
  for x,y in [(425,321),(428,122),(316,33)]:bench(c,x,y,88)
  for x in range(430,527,24):rect(c,x,253,20,24,'#b8c7b5','#738877',2);ellipse(c,x+4,258,12,12,'#55796b')
  shelf(c,20,33,102,18,'tools');pallets(c,440,181,3,1)
 else:
  vehicle(c,22,314,100,39);bench(c,171,342,174);shelf(c,397,341,133,16)
  for x,y,cols,rows in [(22,210,4,3),(320,213,4,3),(440,31,4,3),(23,32,4,3)]:pallets(c,x,y,cols,rows)
  for x,y,w in [(170,218,82),(21,115,105),(325,120,195),(181,30,70)]:bench(c,x,y,w)
  cart(c,294,259);cart(c,411,91);plant(c,533,272,12)
 # Wear remains global and does not suggest new walls or mechanical objects.
 rng=random.Random(114)
 for i in range(60):
  x=rng.uniform(8,540);y=rng.uniform(8,372);line(c,x,y,x+rng.uniform(1,5),y+rng.uniform(-2,2),'#b5b7a4',.17)
 c.restoreState()

def floor_draw(c,x,y,w,h,z,theme='Neutro'):
 key='ZZ05_'+str(['Neutro','Mercado','Hospital','Oficina','Posto','Condomínio','Estação'].index(theme));made=getattr(c,'_zz05_forms',set())
 if key not in made:
  c.beginForm(key,0,0,W*mm,H*mm);scene(c,theme);c.endForm();made.add(key);c._zz05_forms=made
 row,col=divmod(z-1,4);scale=w/(138.5*mm);c.saveState();path=c.beginPath();path.rect(x,y,w,h);c.clipPath(path,stroke=0);c.translate(x-col*138.5*mm*scale,y-(3-row)*95*mm*scale);c.scale(scale,scale);c.doForm(key);c.restoreState()
