"""A–C: cena global em milímetros. Não contém paredes ou regras de movimento."""
from pathlib import Path
from functools import lru_cache
import math, random, json
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
P=Path(__file__).resolve().parents[1]
ECON=False
USES=[]

def color(s):
 c=HexColor(s)
 if ECON:
  v=.299*c.red+.587*c.green+.114*c.blue
  return type(c)(v,v,v)
 return c
def rect(c,x,y,w,h,fill,stroke=None,r=0):
 c.setFillColor(color(fill));c.setStrokeColor(color(stroke or fill));c.setLineWidth(.35)
 if r:c.roundRect(x,y,w,h,r,fill=1,stroke=bool(stroke))
 else:c.rect(x,y,w,h,fill=1,stroke=bool(stroke))
def line(c,x,y,X,Y,col='#5b6960',width=.4):
 c.setStrokeColor(color(col));c.setLineWidth(width);c.line(x,y,X,Y)
def oval(c,x,y,w,h,fill,stroke=None):
 c.setFillColor(color(fill));c.setStrokeColor(color(stroke or fill));c.setLineWidth(.35);c.ellipse(x,y,x+w,y+h,fill=1,stroke=bool(stroke))
def poly(c,pts,fill,stroke=None):
 p=c.beginPath();p.moveTo(*pts[0])
 for pt in pts[1:]:p.lineTo(*pt)
 p.close();c.setFillColor(color(fill));c.setStrokeColor(color(stroke or fill));c.setLineWidth(.3);c.drawPath(p,fill=1,stroke=bool(stroke))
def shade(c,x,y,w,h):
 rect(c,x+1.2,y-1.2,w,h,'#e2e1d7' if ECON else '#bcb9a4',r=1)

@lru_cache(maxsize=128)
def crop(path,index):
 im=Image.open(P/path)
 if path.startswith('assets/v0.5/'):
  return json.loads((P/'content/production/crops_0.6.json').read_text())[path][index],im.size
 iw,ih=im.size;l=index%2*iw//2;t=index//2*ih//2;r=l+iw//2;b=t+ih//2
 if im.mode=='RGBA':
  alpha=im.getchannel('A').crop((l,t,r,b));native=alpha.size
  # Miniatura somente para analisar componentes de alfa; impressão usa os pixels originais.
  mask=alpha.resize((192,128),Image.Resampling.NEAREST);px=mask.load();seen=set();groups=[]
  for yy in range(128):
   for xx in range(192):
    if (xx,yy) in seen or px[xx,yy]<160:continue
    todo=[(xx,yy)];seen.add((xx,yy));n=0;L=R=xx;T=B=yy
    while todo:
     X,Y=todo.pop();n+=1;L=min(L,X);R=max(R,X);T=min(T,Y);B=max(B,Y)
     for u,v in [(X-1,Y),(X+1,Y),(X,Y-1),(X,Y+1)]:
      if 0<=u<192 and 0<=v<128 and (u,v) not in seen and px[u,v]>=160:seen.add((u,v));todo.append((u,v))
    groups.append((n,L,T,R+1,B+1))
  if groups:
   largest=max(g[0] for g in groups);keep=[g for g in groups if g[0]>=largest*.035]
   L=min(g[1] for g in keep);T=min(g[2] for g in keep);R=max(g[3] for g in keep);B=max(g[4] for g in keep)
   old_l,old_t=l,t;l=max(l,old_l+L*native[0]/192-2);t=max(t,old_t+T*native[1]/128-2);r=min(r,old_l+R*native[0]/192+2);b=min(b,old_t+B*native[1]/128+2)
 return [l,t,r,b],im.size

@lru_cache(maxsize=32)
def image_reader(path,econ):
 im=Image.open(P/path)
 if econ:
  from PIL import ImageOps
  alpha=im.getchannel('A') if im.mode=='RGBA' else None
  gray=ImageOps.grayscale(im)
  # Mantém o contraste dos objetos; clareia somente o piso vetorial.
  im=Image.merge('LA',(gray,alpha)) if alpha is not None else gray
 return ImageReader(im)

def asset(c,path,index,x,y,w,h,theme):
 box,size=crop(path,index);l,t,r,b=box;cw,ch=r-l,b-t
 scale=min(w/cw,h/ch,25.4/215)
 ww,hh=cw*scale,ch*scale;xx=x+(w-ww)/2;yy=y+(h-hh)/2
 c.saveState();clip=c.beginPath();clip.rect(xx,yy,ww,hh);c.clipPath(clip,stroke=0)
 c.drawImage(image_reader(path,ECON),xx-l*scale,yy-(size[1]-b)*scale,width=size[0]*scale,height=size[1]*scale,mask='auto');c.restoreState()
 USES.append(dict(theme=theme,file=path,index=index,original_pixels=list(size),crop_pixels=box,used_pixels=[cw,ch],print_mm=[ww,hh],bbox_mm=[xx,yy,ww,hh],effective_ppi=25.4/scale,edition='economica' if ECON else 'ilustrada'))

def material(c,x,y,w,h,kind):
 path='assets/v0.6/pisos_materiais.png'
 if ECON or not (P/path).exists():return False
 index={'concrete':0,'asphalt':1,'tile':2,'paver':3,'wood':4,'grass':5}.get(kind)
 if index is None:return False
 iw,ih=Image.open(P/path).size;cw,ch=iw/3,ih/2;tile=60;scale=min(tile/cw,tile/ch,25.4/215);tw,th=cw*scale,ch*scale;l=index%3*cw;t=index//3*ch;bot=t+ch
 c.saveState();bound=c.beginPath();bound.rect(x,y,w,h);c.clipPath(bound,stroke=0)
 for row in range(math.floor(y/th),math.ceil((y+h)/th)):
  for col in range(math.floor(x/tw),math.ceil((x+w)/tw)):
   c.saveState();c.translate(col*tw,row*th)
   # Espelhamento na composição, sem reamostrar pixels; bordas adjacentes coincidem.
   if col%2:c.translate(tw,0);c.scale(-1,1)
   if row%2:c.translate(0,th);c.scale(1,-1)
   cut=c.beginPath();cut.rect(0,0,tw,th);c.clipPath(cut,stroke=0)
   c.drawImage(image_reader(path,False),-l*scale,-(ih-bot)*scale,width=iw*scale,height=ih*scale);c.restoreState()
 c.restoreState()
 USES.append(dict(theme='material/'+kind,file=path,index=index,original_pixels=[iw,ih],crop_pixels=[l,t,l+cw,bot],used_pixels=[cw,ch],print_mm=[tw,th],bbox_mm=[x,y,w,h],effective_ppi=25.4/scale,edition='ilustrada',role='material nativo repetido; não mobiliário'))
 return True

def surface(c,x,y,w,h,kind,base):
 """Padrões globais, sem quadricular zonas; detalhes reduzidos na econômica."""
 rect(c,x,y,w,h,'#faf9f4' if ECON else base)
 textured=material(c,x,y,w,h,kind)
 c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0)
 grout='#e8e6df' if ECON else '#c7c5b6'
 if kind=='tile':
  for X in range(int(x//14)*14,int(x+w)+15,14):line(c,X,y,X,y+h,grout,.16)
  for Y in range(int(y//14)*14,int(y+h)+15,14):line(c,x,Y,x+w,Y,grout,.16)
  if not ECON and not textured:
   for X in range(int(x//28)*28,int(x+w),28):
    for Y in range(int(y//28)*28,int(y+h),28):rect(c,X+.5,Y+.5,13,13,'#dfddcf' if (X+Y)//28%2 else base)
 elif kind=='paver':
  for row,Y in enumerate(range(int(y//8)*8,int(y+h)+8,8)):
   line(c,x,Y,x+w,Y,grout,.23)
   for X in range(int(x//18)*18-18,int(x+w)+18,18):line(c,X+(9 if row%2 else 0),Y,X+(9 if row%2 else 0),Y+8,grout,.23)
 elif kind=='wood':
  for Y in range(int(y//7)*7,int(y+h)+7,7):
   line(c,x,Y,x+w,Y,grout,.25)
   for X in range(int(x//47)*47,int(x+w)+47,47):line(c,X+(15 if int(Y)%2 else 0),Y,X+(15 if int(Y)%2 else 0),Y+7,grout,.2)
 elif kind=='concrete':
  for X in range(int(x//72)*72,int(x+w)+72,72):line(c,X,y,X,y+h,grout,.24)
  for Y in range(int(y//55)*55,int(y+h)+55,55):line(c,x,Y,x+w,Y,grout,.24)
 elif kind=='asphalt' and not ECON:
  for X,Y in [(x+19,y+11),(x+w*.57,y+h*.3),(x+w*.8,y+h*.75)]:
   line(c,X,Y,X+6,Y+2,'#9fa69e',.4);line(c,X+6,Y+2,X+9,Y+8,'#9fa69e',.3)
 elif kind=='grass':
  for X in range(int(x)+4,int(x+w),11):
   for Y in range(int(y)+4,int(y+h),13):line(c,X,Y,X+2,Y+3,'#c8cdb7' if ECON else '#95a17c',.35)
 c.restoreState()

def product(c,x,y,kind,i):
 col=['#728967','#aa7556','#c4ad75','#7e9291','#bba56a'][i%5]
 if kind=='bottle':
  rect(c,x+.9,y+4,1.5,1.3,'#5f766b',r=.2);rect(c,x,y,3.3,4.3,col,'#647365',.5);rect(c,x+.4,y+1.3,2.5,1.5,'#e8dcb9');line(c,x+.8,y+.6,x+.8,y+3.5,'#e5ddc5',.3)
 elif kind=='can':
  oval(c,x,y,4.2,4.2,col,'#65756b');oval(c,x+.5,y+.5,3.2,3.2,'#c5c5a7');line(c,x+1,y+1.5,x+3,y+1.5,'#7e8d7b',.35)
 elif kind=='bag':
  poly(c,[(x,y),(x+5,y+.4),(x+4.5,y+5),(x+.5,y+5.5)],col,'#8a896e');rect(c,x+1,y+1.5,2.7,1.7,'#e6ddbd');line(c,x+.7,y+4.5,x+4,y+4.3,'#eee4c7',.35)
 elif kind=='box':
  rect(c,x,y,4,5,col,'#6e7869',.2);rect(c,x+.6,y+1,2.8,2,'#dfd9bc');line(c,x+.6,y+4,x+3.5,y+4,'#ede7d0',.3)
 else:oval(c,x,y,4.5,4,'#b6ac77' if i%3 else '#87976c','#78876b')

def gondola(c,x,y,w,h,kind='can'):
 shade(c,x,y,w,h);rect(c,x,y,w,h,'#7e8d80','#50695d',1.3);rect(c,x+1.1,y+1.2,w-2.2,h-2.4,'#c7b78e')
 for row in range(2):
  for i in range(int((w-5)/6)):
   product(c,x+2.5+i*6,y+2.4+row*(h/2),kind,i+row*3)
 line(c,x+1,y+h/2,x+w-1,y+h/2,'#61786b',1)
 for xx in [x+1,x+w-2.5]:rect(c,xx,y+1,1.5,h-2,'#a3af9c')
 rect(c,x+3,y-1,w-6,1.1,'#d7c899')

def crate(c,x,y,w=19,h=14,open_box=False):
 shade(c,x,y,w,h);rect(c,x,y,w,h,'#b39b71','#7b7a60',.5)
 for xx in [x+2,x+w-3]:line(c,xx,y+1,xx,y+h-1,'#8d7856',.7)
 rect(c,x+5,y+3,max(4,w-10),h-6,'#d5c39b')
 if open_box:
  poly(c,[(x,y+h),(x-3,y+h+4),(x+w+1,y+h+5),(x+w,y+h)],'#d1b987','#94815e')
  for i in range(2):product(c,x+3+i*6,y+4,'can',i)
 else:line(c,x+2,y+2,x+w-2,y+h-2,'#8f7855',.45)

def cart(c,x,y,loaded=False):
 shade(c,x,y,17,12);rect(c,x,y,17,12,'#adb9ad','#576e64',1)
 for X in [3,6,9,12,15]:line(c,x+X,y+1,x+X,y+11,'#708b7b',.35)
 for Y in [3,6,9]:line(c,x+1,y+Y,x+16,y+Y,'#708b7b',.35)
 line(c,x+19,y+1,x+19,y+11,'#526b5f',1)
 for X in [2,13]:oval(c,x+X,y-1.5,2,2,'#435b51')
 if loaded:product(c,x+2,y+2,'bag',0);product(c,x+9,y+5,'bottle',2)

def bench(c,x,y,w,h,kind='tools'):
 shade(c,x,y,w,h);rect(c,x,y,w,h,'#a79370','#617163',1)
 for yy in [3,h-3]:line(c,x+1,y+yy,x+w-1,y+yy,'#cfbd97',.4)
 for i in range(int(w/12)):
  xx=x+4+i*11
  if kind=='tools':
   line(c,xx,y+3,xx+3,y+h-4,'#45635b',1);oval(c,xx+1,y+h-6,4,3,'#9ba99c','#45635b');line(c,xx+5,y+3,xx+8,y+8,'#ac7453',1.2)
  else:product(c,xx,y+3,'box' if i%2 else 'bottle',i)
 rect(c,x+5,y+h/2,13,6,'#55776b','#3f5f55',.7)

def bed(c,x,y,w=20,h=35,blanket='#8fa595'):
 shade(c,x,y,w,h);rect(c,x,y,w,h,'#a2aca2','#60776c',1.5);rect(c,x+2,y+2,w-4,h-4,'#e9e3d3',r=1)
 rect(c,x+3,y+2,w-6,h*.55,blanket,r=.8);rect(c,x+4,y+h-9,w-8,6,'#f1ecde',r=1)
 for xx in [x-.6,x+w]:line(c,xx,y+3,xx,y+h-3,'#84968c',.65)
 line(c,x+4,y+6,x+w-4,y+7,'#bfccc0',.45)

def planter(c,x,y,w,h):
 shade(c,x,y,w,h);rect(c,x,y,w,h,'#ad9b77','#7b8469',1);rect(c,x+1,y+1,w-2,h-2,'#7d8863')
 for i in range(max(2,int(w/7))):
  for j in range(3):
   xx=x+4+i*6;yy=y+3+j*(h-6)/3
   for ang in [0,1.8,3.9]:oval(c,xx+math.cos(ang)*2-2,yy+math.sin(ang)*2-1,4.5,2.5,['#819363','#a3ad79','#597b5b'][j])

def story(c,x,y,kind):
 """Marcas concentradas nos acontecimentos; nunca ruído aleatório no piso."""
 if kind=='purchase':
  poly(c,[(x,y),(x+8,y-1),(x+10,y+7),(x+2,y+8)],'#baa278','#7d8267');line(c,x+3,y+8,x+4,y+11,'#6c7a62',.7);line(c,x+4,y+11,x+8,y+8,'#6c7a62',.7)
  for X,Y in [(12,1),(16,-1),(18,5)]:product(c,x+X,y+Y,'can' if X%2 else 'bottle',X)
 elif kind=='repair':
  oval(c,x,y,13,7,'#69776c','#465f54');oval(c,x+2,y+1,9,4,'#9d916e');line(c,x+17,y+1,x+22,y+8,'#6e8375',1.3);line(c,x+21,y+8,x+26,y+8,'#6e8375',1)
  for X,Y in [(3,11),(7,13),(11,10)]:oval(c,x+X,y+Y,1.5,1.5,'#9a9b7e','#536c61')
 elif kind=='papers':
  for X,Y in [(0,0),(6,3),(13,-1)]:
   poly(c,[(x+X,y+Y),(x+X+5,y+Y+1),(x+X+6,y+Y+7),(x+X+1,y+Y+6)],'#e9ddbb','#b9b091')
   for j in [2,3,4]:line(c,x+X+1.5,y+Y+j,x+X+4,y+Y+j+.4,'#b6ab8e',.22)
 elif kind=='garden':
  planter(c,x,y,24,12);rect(c,x+27,y+1,7,12,'#aa8964','#6b7b5e',1);line(c,x+37,y,x+40,y+17,'#7a7657',1);line(c,x+36,y+16,x+44,y+18,'#506d56',1.8)
 elif kind=='spill':
  oval(c,x,y,23,8,'#e9e7dc' if ECON else '#c7c5ad');oval(c,x+17,y+5,8,4,'#e9e7dc' if ECON else '#c7c5ad')
  line(c,x-3,y+1,x+24,y+3,'#b9b49a',.8)

def draw_object(c,o,theme):
 k=o['kind'];x,y,w,h=o['box'];v=o.get('variant','')
 if k=='asset':
  rotation=o.get('rotation',0)
  if rotation==90:
   c.saveState();c.translate(x+w/2,y+h/2);c.rotate(90);asset(c,o['file'],o['index'],-h/2,-w/2,h,w,theme);c.restoreState()
   use=USES[-1];ww,hh=use['print_mm'];use['bbox_mm']=[x+(w-hh)/2,y+(h-ww)/2,hh,ww];use['print_mm']=[hh,ww];use['rotation']=90
  else:asset(c,o['file'],o['index'],x,y,w,h,theme)
 elif k=='gondola':gondola(c,x,y,w,h,v or 'can')
 elif k=='bench':bench(c,x,y,w,h,v or 'tools')
 elif k=='crate':crate(c,x,y,w,h,v=='open')
 elif k=='cart':cart(c,x,y,bool(v))
 elif k=='bed':bed(c,x,y,w,h,v or '#8fa595')
 elif k=='planter':planter(c,x,y,w,h)
 elif k=='story':story(c,x,y,v)
 elif k=='drain':
  rect(c,x,y,w,h,'#a3aa99','#65776a',.4)
  for xx in range(int(x+1),int(x+w),3):line(c,xx,y+1,xx,y+h-1,'#596e63',.6)
 elif k=='rug':
  rect(c,x,y,w,h,'#d3c6a3' if not ECON else '#eeece4',r=1)
  for yy in [y+2,y+h-2]:line(c,x+2,yy,x+w-2,yy,'#aaa889',.5)
 elif k=='bay':
  for xx in [x,x+w]:line(c,xx,y,xx,y+h,'#c6ad70',.9)
  for yy in [y,y+h]:line(c,x,yy,x+w,yy,'#c6ad70',.9)
  for xx in range(int(x),int(x+w),9):line(c,xx,y,xx+3,y+4,'#b4a374',.7)
 elif k=='pipe':
  for off,width,col in [(1,3,'#b2b5a0'),(0,2.4,'#607e70'),(-.2,1,'#b7c4aa')]:line(c,x,y+off,x+w,y+h+off,col,width)
 elif k=='basin':
  shade(c,x,y,w,h);oval(c,x,y,w,h,'#9ba38e','#6b8070');oval(c,x+2,y+2,w-4,h-4,'#6a8c81','#486f64');oval(c,x+5,y+5,w-10,h-10,'#a3b9a2')
  line(c,x+3,y+h/2,x+w-3,y+h/2,'#cab990',1.5);oval(c,x+w/2-2,y+h/2-2,4,4,'#7c876c')
 elif k=='chairs':
  for i in range(max(1,int(w/13))):
   xx=x+i*13;shade(c,xx,y,10,h);rect(c,xx,y,10,h,'#7d9987','#527561',1.5);rect(c,xx+1,y+h-3,8,2,'#a3b39a',r=.5)
 elif k=='fridge':
  shade(c,x,y,w,h);rect(c,x,y,w,h,'#6d8981','#45665e',1)
  n=max(1,int(w/17))
  for i in range(n):
   xx=x+2+i*(w-3)/n;rect(c,xx,y+2,(w-5)/n,h-4,'#adc0ac','#66877b',.7)
   for j in range(3):product(c,xx+2+j*4,y+5,'box',i+j)
   line(c,xx+1,y+3,xx+1,y+h-3,'#dde0c9',.6)
 else:raise ValueError(k)

def scene(c,theme,config):
 # Layer A: floor surfaces in global coordinates.
 for s in config['surfaces']:surface(c,*s)
 # Deliberate paving/curbs and circulation paint, never architectural walls.
 for p in config.get('paint',[]):
  x,y,X,Y,col,width=p;line(c,x,y,X,Y,col,width)
 # Layer B: furniture; all quantities here are decorative, not resource awards.
 for o in config['objects']:draw_object(c,o,theme)
 # Layer C: local wear and interrupted activity.
 for o in config.get('stories',[]):draw_object(c,o,theme)
