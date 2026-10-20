from pathlib import Path
import sys,json
S=Path(__file__).resolve().parents[1];P=next(p for p in S.parents if (p/'content/catalog.json').exists());sys.path.insert(0,str(P/'src'))
import build_finish as f
import fitz
from PIL import Image,ImageDraw
f.setup();g=f.f;old=g.hero_body;res=[]
def body(i):
 path=S/'originais'/f'PEOES_{"ABCD"[i//6]}.png';im=Image.open(path);a=g.tight_body(dict(path=str(path.relative_to(P)),col=i%3,row=(i%6)//3,cols=3,rows=2));l,t,r,b=a['crop'];scale=min(20/(r-l),44/(b-t));res.append(dict(id=g.D['heroes'][i]['id'],file=str(path.relative_to(S)),native_pixels=list(im.size),crop=a['crop'],print_mm=[(r-l)*scale,(b-t)*scale],effective_ppi=25.4/scale));return a
for new in [False,True]:
 root=S/('pdfs' if new else 'antes');(root/'04_PERSONAGENS_E_INIMIGOS').mkdir(exist_ok=True);g.hero_body=body if new else old;g.standees(root)
g.hero_body=old
name='04_PERSONAGENS_E_INIMIGOS/HEROIS_24_RECORTAR.pdf';a=fitz.open(S/'antes'/name);b=fitz.open(S/'pdfs'/name)
assert len(a)==len(b)==2;assert [p.get_text() for p in a]==[p.get_text() for p in b]
for i in range(2):
 comp=Image.new('RGB',(1220,880),'#eee8d9');d=ImageDraw.Draw(comp)
 for j,(label,doc) in enumerate([('ANTES',a),('DEPOIS',b)]):
  p=doc[i];pix=p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);pix.save(S/'provas'/f'PEOES_{label}_{i+1}.png');im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((600,850));comp.paste(im,(j*610,25));d.text((j*610+10,5),label,fill='black')
 comp.save(S/'provas'/f'COMPARACAO_PEOES_{i+1}.jpg',quality=93)
(S/'fontes/resolucao_peoes.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print('24 peões / 2 A4 / nomes e linhas preservados')
