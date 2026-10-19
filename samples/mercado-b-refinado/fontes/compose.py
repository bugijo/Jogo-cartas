"""Reconstruções nativas coordenadas: montagem física, recorte e junção de sobreposições.
Não amplia a arte antiga. A referência antiga só forneceu composição e posições.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
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

def compose():
 canvas=np.zeros((H,W,3),dtype=np.float32);placed=[];usage=[]
 for a in REG:
  key=a['id'];im=Image.open(S/'originais'/f'{key}.png').convert('RGB');b=a['print_box_mm'];x0,y0,x1,y1=[round(v*PX) for v in b];tw,th=x1-x0,y1-y0
  assert tw<=im.width and th<=im.height, 'Não ampliar saída nativa'
  ppi=[im.width/(b[2]-b[0])*25.4,im.height/(b[3]-b[1])*25.4]
  pic=np.asarray(im.resize((tw,th),Image.Resampling.LANCZOS),dtype=np.float32);old=canvas[y0:y1,x0:x1];alpha=np.ones((th,tw),dtype=np.float32)
  if a['col']:
   prev=next(r for r in placed if r['row']==a['row'] and r['col']==a['col']-1);ow=round(prev['print_box_mm'][2]*PX)-x0
   cost=np.mean(abs(old[:,:ow]-pic[:,:ow]),axis=2)
   # Evita selecionar o limite externo da sobreposição.
   cost[:,:5]+=100;cost[:,-5:]+=100;path=seam(cost)
   alpha[:,:ow]=np.clip((np.arange(ow)[None,:]-path[:,None]+2)/4,0,1)
  if a['row']:
   prev=next(r for r in placed if r['row']==a['row']-1 and r['col']==a['col']);oh=round(prev['print_box_mm'][3]*PX)-y0
   cost=np.mean(abs(old[:oh]-pic[:oh]),axis=2).T;cost[:,:5]+=100;cost[:,-5:]+=100;path=seam(cost)
   top=np.clip((np.arange(oh)[:,None]-path[None,:]+2)/4,0,1);alpha[:oh]=np.minimum(alpha[:oh],top)
  canvas[y0:y1,x0:x1]=pic*alpha[:,:,None]+old*(1-alpha[:,:,None]);placed.append(a)
  usage.append({'id':key,'file':f'originais/{key}.png','native_pixels':list(im.size),'used_pixels':[0,0,im.width,im.height],'print_box_mm':b,'effective_ppi_xy':ppi,'composition_pixels':[tw,th],'upscaled':False})
 out=Image.fromarray(np.uint8(np.clip(canvas,0,255)))
 # Correção gerada da junção piloto: área de piso, não uma moldura de ocultação.
 patch=Image.open(S/'originais/JUNCAO_R3C2_R3C3.png').convert('RGB');native=patch.size;patch=patch.crop((9,0,patch.width-8,patch.height))
 boxref=[477+1270/2.7,665,477+1600/2.7,1039];boxmm=[boxref[0]/1514*554,boxref[1]/1039*380,boxref[2]/1514*554,380];x0,y0,x1,y1=[round(v*PX) for v in boxmm];tw,th=x1-x0,y1-y0
 assert tw<=patch.width and th<=patch.height
 ppi=[patch.width/(boxmm[2]-boxmm[0])*25.4,patch.height/(boxmm[3]-boxmm[1])*25.4]
 patch=patch.resize((tw,th),Image.Resampling.LANCZOS);mask=Image.new('L',(tw,th));d=ImageDraw.Draw(mask)
 for x in range(tw):d.line((x,0,x,th),fill=round(255*max(0,min(1,x/(tw/6),(tw-1-x)/(tw/6)))))
 out.paste(patch,(x0,y0),mask)
 usage.append({'id':'reparo_juncao_piloto','file':'originais/JUNCAO_R3C2_R3C3.png','native_pixels':list(native),'used_pixels':[9,0,native[0]-8,native[1]],'print_box_mm':boxmm,'effective_ppi_xy':ppi,'upscaled':False})
 # Reparos locais gerados incluem móveis inteiros; junções ficam no piso livre.
 for a in json.loads((S/'fontes/reparos.json').read_text()):
  patch=Image.open(S/'originais'/f"{a['id']}.png").convert('RGB');native=patch.size;b=a['print_box_mm'];x0,y0,x1,y1=[round(v*PX) for v in b];tw,th=x1-x0,y1-y0
  assert tw<=patch.width and th<=patch.height
  ppi=[patch.width/(b[2]-b[0])*25.4,patch.height/(b[3]-b[1])*25.4];patch=patch.resize((tw,th),Image.Resampling.LANCZOS)
  feather=round(4*PX);xx=np.arange(tw)[None,:];yy=np.arange(th)[:,None];alpha=np.ones((th,tw),dtype=np.float32)
  if x0>0:alpha=np.minimum(alpha,xx/feather)
  if x1<W:alpha=np.minimum(alpha,(tw-1-xx)/feather)
  if y0>0:alpha=np.minimum(alpha,yy/feather)
  if y1<H:alpha=np.minimum(alpha,(th-1-yy)/feather)
  out.paste(patch,(x0,y0),Image.fromarray(np.uint8(np.clip(alpha,0,1)*255)))
  usage.append({'id':a['id'],'file':f"originais/{a['id']}.png",'native_pixels':list(native),'used_pixels':[0,0,*native],'print_box_mm':b,'effective_ppi_xy':ppi,'upscaled':False})
 out.save(S/'MERCADO_ARTE_175PPI.png',dpi=(175,175));(S/'fontes/resolucao.json').write_text(json.dumps({'print_mm':[554,380],'composite_pixels':[W,H],'composite_ppi_xy':[W/554*25.4,H/380*25.4],'method':'9 reconstruções nativas; recorte por menor diferença nas sobreposições, transição de 4 pixels; reparo nativo de junção; apenas redução para composição','sources':usage},indent=2,ensure_ascii=False))
 preview=out.copy();preview.thumbnail((1800,1300));preview.save(S/'provas/MONTAGEM_SEM_INTERFACE.jpg',quality=95)
 print('Composto',out.size,'mínimo fonte',min(min(x['effective_ppi_xy']) for x in usage))
 return out
if __name__=='__main__':compose()
