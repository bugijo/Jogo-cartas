"""Arte vetorial original, em coordenadas locais; nenhum objeto modifica a geometria."""
from reportlab.lib.colors import HexColor, white
INK='#24484b'; PAPER='#f3efe4'; OLIVE='#879581'; RUST='#af7554'; YELLOW='#d2af60'; CONCRETE='#d6d9d2'
ECON=False

def color(h):
 if not ECON:return HexColor(h)
 c=HexColor(h);v=.299*c.red+.587*c.green+.114*c.blue
 return type(c)(v,v,v)
def rect(c,x,y,w,h,fill=PAPER,stroke=INK,r=0):
 c.setFillColor(color(fill));c.setStrokeColor(color(stroke));c.setLineWidth(.65)
 if r:c.roundRect(x,y,w,h,r,fill=1,stroke=1)
 else:c.rect(x,y,w,h,fill=1,stroke=1)
def line(c,x1,y1,x2,y2,col=INK,width=.8):
 c.setStrokeColor(color(col));c.setLineWidth(width);c.line(x1,y1,x2,y2)
def poly(c,pts,fill=OLIVE):
 p=c.beginPath();p.moveTo(*pts[0])
 for xy in pts[1:]:p.lineTo(*xy)
 p.close();c.setFillColor(color(fill));c.setStrokeColor(color(INK));c.drawPath(p,fill=1,stroke=1)
def oval(c,x,y,w,h,fill=CONCRETE):
 c.setFillColor(color(fill));c.setStrokeColor(color(INK));c.ellipse(x,y,x+w,y+h,fill=1,stroke=1)
def prop(c,kind,x,y,w,h,variant=0):
 """Objetos de ambientação detalhados, ortográficos. Sem paredes ou aberturas."""
 c.saveState();c.translate(x,y);c.scale(w/100,h/70)
 if kind in ('shelf','crate','bench'):
  rect(c,3,6,94,58,CONCRETE if kind=='shelf' else RUST,r=2)
  for row in range(3):
   line(c,6,12+row*17,94,12+row*17)
   for col in range(7):
    xx=8+col*12;yy=13+row*17
    rect(c,xx,yy,8,11,[OLIVE,YELLOW,PAPER,RUST][(col+row+variant)%4],r=1)
  if kind=='bench':
   rect(c,14,15,28,15,INK);line(c,56,17,78,44,YELLOW,3);oval(c,70,42,11,11,PAPER)
 elif kind=='cart':
  poly(c,[(14,18),(73,18),(84,59),(7,59)],CONCRETE)
  for j in range(5):line(c,19+j*12,20,15+j*15,57)
  for j in range(3):line(c,12,29+j*10,77,29+j*10)
  line(c,74,59,91,64,INK,3);oval(c,16,4,12,12,INK);oval(c,65,4,12,12,INK)
 elif kind in ('car','van'):
  rect(c,8,6,84,58,OLIVE,r=9);rect(c,27,11,47,48,PAPER,r=5)
  rect(c,29,15,15,39,INK,r=2);rect(c,61,15,10,39,INK,r=2)
  for xx in [16,78]:
   for yy in [0,61]:rect(c,xx,yy,13,8,INK)
  line(c,49,12,49,57,RUST);rect(c,12,14,6,12,YELLOW);rect(c,12,44,6,12,YELLOW)
 elif kind in ('tank','cistern'):
  oval(c,12,1,76,68,CONCRETE);oval(c,20,8,60,54,OLIVE);oval(c,28,15,44,40,PAPER)
  line(c,2,33,29,33,INK,5);line(c,73,33,98,33,INK,5);line(c,50,14,50,57,RUST,3)
  for j in range(5):line(c,34,20+j*7,64,20+j*7,OLIVE)
  if kind=='cistern':line(c,54,63,48,49,RUST,2);line(c,48,49,57,37,RUST,2)
 elif kind in ('bed','sofa'):
  rect(c,8,6,84,58,CONCRETE,r=4);rect(c,13,11,74,48,PAPER,r=4);rect(c,16,16,19,38,OLIVE,r=3)
  for xx in [8,82]:
   for yy in [0,61]:oval(c,xx,yy,10,8,INK)
  line(c,42,12,42,58,RUST)
 elif kind=='pump':
  rect(c,30,4,40,63,RUST,r=3);rect(c,36,36,28,22,INK);rect(c,38,15,24,10,PAPER)
  line(c,70,50,87,52,INK,3);line(c,87,52,88,15,INK,3);line(c,88,15,77,15,INK,3)
 elif kind=='tent':
  poly(c,[(3,9),(49,66),(97,9)],OLIVE);poly(c,[(49,66),(58,9),(97,9)],PAPER)
  poly(c,[(49,48),(30,9),(58,9)],INK);line(c,49,66,49,69,RUST,2)
  for xx in [1,96]:line(c,xx,4,xx+3,12,RUST,2)
 elif kind in ('roof','depot','kitchen'):
  rect(c,5,4,90,62,RUST,r=2)
  for j in range(8):line(c,10+j*11,6,10+j*11,64,PAPER)
  rect(c,32,17,36,35,OLIVE,r=2)
  if kind=='kitchen':oval(c,36,22,28,25,INK);oval(c,40,26,20,17,CONCRETE);line(c,50,48,50,60,INK,3)
  if kind=='depot':rect(c,12,15,20,20,PAPER);line(c,12,15,32,35)
 elif kind=='tree':
  for xx,yy in [(20,20),(45,39),(62,20),(39,10)]:oval(c,xx,yy,34,29,OLIVE)
  line(c,49,8,49,41,RUST,4)
 elif kind=='pipes':
  for yy in [17,42]:line(c,6,yy,76,yy,OLIVE,8);line(c,6,yy+3,76,yy+3,PAPER,1)
  line(c,76,17,76,61,OLIVE,8);oval(c,34,25,25,25,RUST);line(c,46,29,46,46,PAPER,2);line(c,38,38,54,38,PAPER,2)
 elif kind=='pallet':
  rect(c,3,9,94,52,RUST)
  for j in range(6):rect(c,6+j*15,12,10,45,PAPER)
 elif kind=='checkout':
  rect(c,6,7,88,56,OLIVE,r=5);rect(c,10,13,49,43,INK,r=2)
  for j in range(8):line(c,13+j*5,16,13+j*5,52,CONCRETE)
  rect(c,69,32,20,24,CONCRETE);rect(c,72,36,14,16,INK);rect(c,68,13,21,14,YELLOW)
 elif kind=='laundry':
  line(c,2,63,98,63,INK,2)
  for xx in [10,38,66]:poly(c,[(xx,58),(xx+8,62),(xx+16,58),(xx+24,43),(xx+18,39),(xx+17,14),(xx+5,14),(xx+4,39),(xx-2,43)],[PAPER,OLIVE,YELLOW][xx//28])
 elif kind=='battery':
  rect(c,10,8,80,48,INK,r=3);rect(c,16,14,68,32,OLIVE);rect(c,22,56,13,9,RUST);rect(c,65,56,13,9,YELLOW);line(c,64,28,77,28,PAPER,2);line(c,71,21,71,35,PAPER,2)
 elif kind=='can':
  rect(c,20,10,60,47,OLIVE,r=2);oval(c,20,49,60,16,CONCRETE);oval(c,20,4,60,15,CONCRETE)
  rect(c,21,20,58,22,PAPER);oval(c,43,24,16,14,RUST);line(c,50,57,62,57,INK,2)
 elif kind=='water':
  rect(c,29,8,42,45,OLIVE,r=8);rect(c,39,53,22,10,CONCRETE);rect(c,38,62,24,6,INK)
  for yy in [17,25,33]:line(c,32,yy,68,yy,PAPER,2)
 elif kind=='medicine':
  rect(c,10,11,80,49,PAPER,r=4);rect(c,40,18,19,35,OLIVE);rect(c,30,27,40,16,OLIVE)
 elif kind=='fuel':
  rect(c,19,8,62,52,RUST,r=5);rect(c,34,51,32,12,INK,r=2);rect(c,39,54,22,6,PAPER)
  line(c,30,17,70,47,PAPER,2);line(c,70,17,30,47,PAPER,2)
 elif kind=='ammo':
  rect(c,6,5,88,27,OLIVE)
  for xx in [15,34,53,72]:rect(c,xx,19,10,35,YELLOW,r=2);poly(c,[(xx,54),(xx+5,65),(xx+10,54)],RUST)
 elif kind=='meat':
  oval(c,12,8,77,53,RUST);oval(c,32,21,25,25,PAPER);oval(c,39,28,12,11,CONCRETE)
 else:
  rect(c,7,9,86,52,CONCRETE,r=3);line(c,9,12,91,59,RUST,3);line(c,9,59,91,12,RUST,3)
 c.restoreState()

THEMES={
 'Neutro':['pallet','crate','pipes','bench','tree','crate','pallet','pipes','bench','crate','pipes','pallet','tree','bench','crate','pipes'],
 'Mercado':['car','cart','checkout','checkout','shelf','shelf','crate','shelf','shelf','cart','shelf','crate','pallet','water','crate','van'],
 'Hospital':['car','bench','bed','bed','medicine','bed','medicine','bed','bed','bed','bench','medicine','pallet','bed','bed','van'],
 'Oficina':['car','car','bench','car','bench','pallet','battery','bench','car','pipes','bench','crate','pallet','car','crate','van'],
 'Posto':['car','pump','pump','car','shelf','bench','van','fuel','pump','car','shelf','crate','pallet','bench','fuel','van'],
 'Condomínio':['car','tree','tree','laundry','sofa','bench','pallet','sofa','laundry','tree','sofa','crate','tree','laundry','bench','van'],
 'Estação':['car','pipes','tank','tank','bench','pipes','pipes','tank','tank','pipes','bench','crate','tank','pipes','pallet','van']}

def floor(c,x,y,w,h,z,theme='Neutro'):
 rect(c,x,y,w,h,'#faf9f3' if ECON else ['#ecebdf','#e4e8e0','#efe9dc'][z%3],stroke='#d3d8cf')
 c.saveState();p=c.beginPath();p.rect(x+2,y+2,w-4,h-4);c.clipPath(p,stroke=0)
 # Fine paving, cracked edges and plant growth; no false walls.
 for j in range(1,7):line(c,x+j*w/7,y,x+j*w/7,y+h,'#e4e4dc',.25)
 for j in range(1,5):line(c,x,y+j*h/5,x+w,y+j*h/5,'#e4e4dc',.25)
 prop(c,THEMES[theme][z-1],x+w*.58,y+h*.60,w*.34,h*.25,z)
 prop(c,'crate' if z%3 else 'pallet',x+w*.06,y+h*.13,w*.23,h*.20,z)
 for j in range(3):
  xx=x+w*(.78+j*.045);yy=y+h*.12
  line(c,xx,yy,xx+w*.02,yy+h*.06,OLIVE,.6)
 # Printed footprint traces emphasize the traversable centre.
 if not ECON:
  for j in [0,1]:oval(c,x+w*(.42+j*.06),y+h*(.42+j*.07),w*.025,h*.05,'#d3d8cf')
 c.restoreState()
