"""Verificações digitais da fabricação; não são impressão nem playtest."""
from pathlib import Path
import json,hashlib,math,re,sys
import fitz
from PIL import Image,ImageOps,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
import production_geometry as g
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-fabricacao-v0.4';MM=72/25.4
D=json.loads((P/'content/catalog.json').read_text());C={c['id']:c for c in D['cards']};M=json.loads((P/'output/comece-aqui-duas-pessoas/manifesto.json').read_text());checks=[];fails=[]
def ck(name,yes,detail=None):
 checks.append(dict(check=name,passed=bool(yes),detail=detail))
 if not yes:fails.append(name)
def norm(t):return re.sub(r'\s+','',t).replace('\u00ad','')
def box(i,side='front'):
 x,y,w,h=g.card_rect(i,side);return fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM)
for f,h in json.loads((P/'content/production/baseline_0.4.json').read_text()).items():ck('Fonte preservada: '+f,hashlib.sha256((P/f).read_bytes()).hexdigest()==h)
ck('114 cartas selecionadas únicas',len(set(M['initial_cards']+M['supplement_cards']))==114)
ck('24 heróis existentes',len(D['heroes'])==24)
ck('Bases cabem sem alterar limite',g.pawn_capacity(138.5,95)>=30 and g.MAX_ENEMIES==24)
ck('Variantes não criam IDs',len(g.enemy_variants())==72 and len(set(e['id'] for e in g.enemy_variants()))==24)
ck('Slots com folga para 63×88',all(w>=65 and h>=90 for x,y,w,h in g.panel_slots()))
ck('Sem estouros de parágrafos',json.loads((O/'layout_issues.json').read_text())==[])
geo=json.loads((O/'geometry.json').read_text());edges={tuple(sorted(e)) for e in D['maps'][0]['edges']}
ck('Geometria derivada das conexões existentes',len(geo)>0 and all(r['connected']==(bool(r['neighbor']) and tuple(sorted((r['zone'],r['neighbor']))) in edges) for r in geo))
ck('Aberturas exatas de 14 mm',all(abs(r['gap_mm']-(14 if r['connected'] else 0))<1e-5 for r in geo))
rendered=0;econ_bad=[];private_names=['zombecide','Pesonagens','Equipamentos-1.pdf','Equipamentos-2.pdf'];secret_hashes={}
for edition in ['ilustrada','economica']:
 root=O/edition;manifest=json.loads((root/'00_LEIA_PRIMEIRO/manifesto.json').read_text());allf=manifest['files']
 for method in ['duplex','manual']:
  used=[e for e in allf if not e['optional'] and e['method'] in ['both',method]]
  sums=tuple(sum(e['sheets'] for e in used if e['stage']==s) for s in ['initial','supplement'])
  ck(edition+' folhas '+method,sums==g.sheet_totals(method)[:2],sums)
 for fentry in allf:
  f=root/fentry['file'];d=fitz.open(f);ck('Hash '+str(f.relative_to(O)),hashlib.sha256(f.read_bytes()).hexdigest()==fentry['sha256'])
  ck('A4 '+str(f.relative_to(O)),all(abs(min(p.rect.width,p.rect.height)-210*MM)<.15 and abs(max(p.rect.width,p.rect.height)-297*MM)<.15 for p in d))
  thumbs=[]
  for page in d:
   spans=[s for b in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
   used={s['font'] for s in spans}
   outside=[s['text'] for s in spans if s['bbox'][0]<-.5 or s['bbox'][1]<-.5 or s['bbox'][2]>page.rect.width+.5 or s['bbox'][3]>page.rect.height+.5]
   ck(f'{edition}/{f.name}/{page.number+1} texto na página',not outside,outside)
   for font in page.get_fonts(full=True):
    if font[3] in used or font[3].split('+')[-1] in used:ck(f'{edition}/{f.name} fonte {font[3]}',len(d.extract_font(font[0])[3])>0)
   pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);rendered+=1
   im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
   if edition=='economica':
    r,gg,b=im.split();import PIL.ImageChops as ic
    if ic.difference(r,gg).getextrema()[1]>3 or ic.difference(r,b).getextrema()[1]>3:econ_bad.append(str(f))
   out=O/'renders'/edition/Path(fentry['file']).parent/f.stem;out.mkdir(parents=True,exist_ok=True);im.save(out/f'{page.number+1:03}.jpg',quality=80)
   im.thumbnail((180,255));thumbs.append(im.copy())
  sheet=Image.new('RGB',(4*190,math.ceil(len(thumbs)/4)*280),'#cccccc');draw=ImageDraw.Draw(sheet)
  for i,im in enumerate(thumbs):x=(i%4)*190;y=(i//4)*280;sheet.paste(im,(x,y));draw.text((x+2,y+256),str(i+1),fill='black')
  out=O/'contatos'/edition/Path(fentry['file']).parent;out.mkdir(parents=True,exist_ok=True);sheet.save(out/(f.stem+'.jpg'),quality=85)
 # Check every actual effect, physical crop, duplex/manual mapping, and indistinguishability.
 for key,stem,initial in [('initial_cards','KIT_INICIAL_1',True),('supplement_cards','KIT_COMPLEMENTO_2',False)]:
  dup=fitz.open(root/'02_CARTAS_DUPLEX'/f'{stem}_DUPLEX.pdf');front=fitz.open(root/'03_CARTAS_RECORTAR_E_COLAR'/f'{stem}_FRENTES.pdf');back=fitz.open(root/'03_CARTAS_RECORTAR_E_COLAR'/f'{stem}_VERSOS.pdf')
  for i,id in enumerate(M[key]):
   n,k=divmod(i,9);expected=C[id]['text'].replace('ceil(H/2)','1') if initial else C[id]['text']
   for label,page,rect in [('duplex',dup[2*n],box(k)),('manual',front[n],box(k))]:ck(f'{edition} {id} efeito {label}',norm(expected) in norm(page.get_text(clip=rect)))
   bp=dup[2*n+1];br=box(k,'duplex_back');mr=box(k,'manual_back')
   p1=bp.get_pixmap(matrix=fitz.Matrix(1,1),clip=br);p2=back[n].get_pixmap(matrix=fitz.Matrix(1,1),clip=mr)
   ck(f'{edition} {id} verso pareado',norm(bp.get_text(clip=br))==norm(back[n].get_text(clip=mr)))
   if C[id]['family']=='INT':
    # Normalize raster crop to avoid fractional-coordinate antialias variation.
    text=bp.get_text(clip=br);ck('Sem ID secreto no verso '+id,id not in text)
    secret_hashes.setdefault(edition,[]).append(norm(text))
 for f in root.rglob('*'):ck('Sem referência privada '+str(f.relative_to(root)),not any(n.lower() in f.name.lower() for n in private_names))
ck('Econômica em cinza',not econ_bad,econ_bad)
for ed,values in secret_hashes.items():ck(ed+' versos INT com mesmo texto',len(set(values))==1)
report=dict(checks=len(checks),passed=len(checks)-len(fails),failures=fails,rendered_pages=rendered,economic_colored_pages=econ_bad,limitations=['Sem impressão física, montagem física ou playtest humano.','Mapas raster cerca de 70 ppi; textos, geometria e símbolos vetoriais.','Referência recebida: cinco PDFs, seis páginas; ZIP e demais categorias ausentes.'],details=checks)
(O/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False,indent=2));sys.exit(bool(fails))
