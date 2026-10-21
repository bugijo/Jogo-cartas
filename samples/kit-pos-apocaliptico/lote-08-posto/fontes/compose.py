"""Composição física de reconstruções nativas, sem ampliar fontes."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
S=Path(__file__).resolve().parents[1];PPI=175;PX=PPI/25.4;W,H=round(554*PX),round(380*PX)
REG=json.loads((S/'fontes/secoes.json').read_text())
def seam(cost):
 h,w=cost.shape;dist=cost[0].copy();back=np.zeros((h,w),dtype=np.int8)
 for i in range(1,h):
  prev=np.stack([np.r_[np.inf,dist[:-1]],dist,np.r_[dist[1:],np.inf]])
  choose=np.argmin(prev,axis=0);back[i]=choose-1;dist=cost[i]+prev[choose,np.arange(w)]
 x=int(np.argmin(dist));path=np.zeros(h,dtype=int);path[-1]=x
 for i in range(h-1,0,-1):x+=int(back[i,x]);path[i-1]=x
 return path

def compose(pilot=False):
 canvas=np.full((H,W,3),235,dtype=np.float32);placed=[];usage=[]
 for a in REG:
  src=S/'originais'/f"{a['id']}.png"
  if pilot and not src.exists():continue
  im=Image.open(src).convert('RGB');b=a['print_box_mm'];x0,y0,x1,y1=[round(v*PX) for v in b];tw,th=x1-x0,y1-y0
  assert tw<=im.width and th<=im.height,(a['id'],im.size,(tw,th))
  pic=np.asarray(im.resize((tw,th),Image.Resampling.LANCZOS),dtype=np.float32);old=canvas[y0:y1,x0:x1];alpha=np.ones((th,tw),dtype=np.float32)
  if a['col']:
   prev=next(r for r in placed if r['row']==a['row'] and r['col']==a['col']-1);ow=round(prev['print_box_mm'][2]*PX)-x0
   cost=np.mean(abs(old[:,:ow]-pic[:,:ow]),axis=2);cost[:,:5]+=100;cost[:,-5:]+=100;path=seam(cost)
   alpha[:,:ow]=np.clip((np.arange(ow)[None,:]-path[:,None]+2)/4,0,1)
  if a['row']:
   prev=next(r for r in placed if r['row']==a['row']-1 and r['col']==a['col']);oh=round(prev['print_box_mm'][3]*PX)-y0
   cost=np.mean(abs(old[:oh]-pic[:oh]),axis=2).T;cost[:,:5]+=100;cost[:,-5:]+=100;path=seam(cost)
   alpha[:oh]=np.minimum(alpha[:oh],np.clip((np.arange(oh)[:,None]-path[None,:]+2)/4,0,1))
  canvas[y0:y1,x0:x1]=pic*alpha[:,:,None]+old*(1-alpha[:,:,None]);placed.append(a)
  usage.append(dict(id=a['id'],native_pixels=list(im.size),print_box_mm=b,ppi_xy=[im.width/(b[2]-b[0])*25.4,im.height/(b[3]-b[1])*25.4],upscaled=False))
 out=Image.fromarray(np.uint8(np.clip(canvas,0,255)))
 for a in json.loads((S/'fontes/reparos.json').read_text()):
  source=S/'originais'/f"{a['id']}.png"
  if not source.exists():continue
  im=Image.open(source).convert('RGB');box=a['print_box_mm'];x0,y0,x1,y1=[round(v*PX) for v in box];tw,th=x1-x0,y1-y0
  assert tw<=im.width and th<=im.height
  patch=im.resize((tw,th),Image.Resampling.LANCZOS);feather=round(a.get('feather_mm',4)*PX);xx=np.arange(tw)[None,:];yy=np.arange(th)[:,None];alpha=np.ones((th,tw))
  if x0:alpha=np.minimum(alpha,xx/feather)
  if y0:alpha=np.minimum(alpha,yy/feather)
  if x1<W:alpha=np.minimum(alpha,(tw-1-xx)/feather)
  if y1<H:alpha=np.minimum(alpha,(th-1-yy)/feather)
  if 'core_box_mm' in a:
   cx0,cy0,cx1,cy1=[round(v*PX) for v in a['core_box_mm']]
   # Limita a edição à falha indicada; preserva a composição já aprovada.
   alpha=np.minimum(alpha,np.clip((xx-(cx0-x0))/feather,0,1))
   alpha=np.minimum(alpha,np.clip(((cx1-x0)-xx)/feather,0,1))
   alpha=np.minimum(alpha,np.clip((yy-(cy0-y0))/feather,0,1))
   alpha=np.minimum(alpha,np.clip(((cy1-y0)-yy)/feather,0,1))
  out.paste(patch,(x0,y0),Image.fromarray(np.uint8(np.clip(alpha,0,1)*255)))
  usage.append(dict(id=a['id'],native_pixels=list(im.size),print_box_mm=box,ppi_xy=[im.width/(box[2]-box[0])*25.4,im.height/(box[3]-box[1])*25.4],upscaled=False))
 if pilot:
  crop=out.crop((0,0,round(379.457*PX),round(136.785*PX)));crop.thumbnail((1600,900));crop.save(S/'provas/PILOTO_DUAS_SECOES.png')
 else:
  out.save(S/'POSTO_ARTE_175PPI.png');preview=out.copy();preview.thumbnail((1800,1300));preview.save(S/'provas/ARTE_COMPLETA.jpg',quality=95)
 (S/'fontes/resolucao.json').write_text(json.dumps(dict(composite_pixels=[W,H],print_mm=[554,380],ppi_xy=[W/554*25.4,H/380*25.4],sources=usage,pilot=pilot),indent=2))
 return out
if __name__=='__main__':compose('--pilot' in sys.argv)
