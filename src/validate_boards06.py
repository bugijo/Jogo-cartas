"""Verifica somente as saídas alteradas e os hashes dos componentes preservados."""
from pathlib import Path
import json,hashlib,math,csv,sys
import fitz
from PIL import Image,ImageDraw,ImageChops,ImageStat
import build_boards06 as b
P=b.P;O=b.O;MM=72/25.4;checks=[];issues=[];res=[];pages=0
def ck(name,ok,detail=None):
 checks.append(dict(check=name,passed=bool(ok),detail=detail))
 if not ok:issues.append(name)
def overlap(a,d):
 x,y,w,h=a;X,Y,W,H=d;return min(x+w,X+W)-max(x,X)>0.3 and min(y+h,Y+H)-max(y,Y)>0.3
for path,h in json.loads((P/'content/production/baseline_0.6.json').read_text()).items():ck('0.5/fonte preservada '+path,hashlib.sha256((P/path).read_bytes()).hexdigest()==h)
catalog=json.loads((P/'content/catalog.json').read_text());ck('Seis plantas idênticas ao catálogo',b.MAPS==catalog['maps'])
for m in b.MAPS:
 seen={m['entry']}
 while True:
  nxt=seen|{j for a,d in m['edges'] for i,j in [(a,d),(d,a)] if i in seen}
  if nxt==seen:break
  seen=nxt
 ck('Objetivos e buscas alcançáveis '+m['name'],set(m['zones'])==seen and all(z in seen for z in m['search']+m['objectives']+[m['exit'],m['spawn']]))
 for s in b.segments(m):ck(m['name']+' vão '+str(s['key']),s['gap_mm']==(14 if s['connected'] else 0))
preserved=0
for ed in ['ilustrada','economica']:
 root=O/ed;manifest=json.loads((root/'00_LEIA_PRIMEIRO/manifesto.json').read_text())
 for e in manifest['files']:
  path=root/e['file'];ck('Existe '+ed+'/'+e['file'],path.exists());ck('Manifesto/hash '+ed+'/'+e['file'],hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256'])
  if e['file'] not in b.CHANGED:
   ck('Componente byte a byte '+ed+'/'+e['file'],path.read_bytes()==(b.BASE/ed/e['file']).read_bytes());preserved+=1
 for method,expected in [('duplex',58),('manual',72)]:ck(ed+' '+method+' folhas',sum(e['sheets'] for e in manifest['files'] if not e['optional'] and e['method'] in ['both',method])==expected)
 for rel in b.CHANGED:
  path=root/rel;doc=fitz.open(path);is_map=rel.endswith('_M01_M04_LADO_A.pdf');theme=next((k for k,v in b.KEYS.items() if path.name.startswith(v+'_M01')),None)
  ck('PDF não reparado '+ed+'/'+rel,not doc.is_repaired)
  if is_map:
   ck('Quatro módulos '+ed+'/'+rel,len(doc)==4);ck('Arte atual/assinatura '+ed+'/'+rel,('ZZ06_SOURCE_SHA256='+b.signature(theme)) in doc.metadata['subject'])
  thumbs=[]
  for page in doc:
   pages+=1;label=ed+'/'+rel+' p'+str(page.number+1)
   ck('A4 paisagem '+label,abs(page.rect.width-297*MM)<.02 and abs(page.rect.height-210*MM)<.02)
   ck('Cena nova ZZ06 '+label,any('ZZ06_' in x[1] for x in page.get_xobjects()))
   fitz.TOOLS.mupdf_warnings(reset=True);pix=page.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False);ck('Render sem erros '+label,not fitz.TOOLS.mupdf_warnings())
   im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
   if ed=='economica':
    channels=im.split();ck('Econômica cinza '+label,ImageChops.difference(channels[0],channels[1]).getbbox() is None and ImageChops.difference(channels[1],channels[2]).getbbox() is None)
   out=O/'renders'/ed/Path(rel).with_suffix('');out.mkdir(parents=True,exist_ok=True);im.save(out/f'{page.number+1:03}.jpg',quality=90)
   im.thumbnail((285,202));thumbs.append(im)
   spans=[s for block in page.get_text('dict')['blocks'] for line in block.get('lines',[]) for s in line['spans']]
   used={s['font'].replace(' ','').replace('-','') for s in spans}
   for s in spans:
    x,y,X,Y=s['bbox'];ck('Texto dentro A4 '+label,x>=-.2 and y>=-.2 and X<=page.rect.width+.2 and Y<=page.rect.height+.2,s['text'])
   for font in page.get_fonts(full=True):
    name=font[3].split('+')[-1].replace(' ','').replace('-','')
    if name in used:ck('Fonte incorporada '+label+' '+name,bool(doc.extract_font(font[0])[3]))
   for v in page.get_image_info(xrefs=True):
    a,bb,c,d,*_=v['transform'];wx=(a*a+bb*bb)**.5/72;hy=(c*c+d*d)**.5/72;ppi=min(v['width']/wx,v['height']/hy)
    if is_map:ck('Raster ≥211,3 ppi '+label,ppi>=211.25,round(ppi,2))
    res.append(dict(pdf=ed+'/'+rel,page=page.number+1,xref=v['xref'],pixels=[v['width'],v['height']],printed_mm=[round(wx*25.4,3),round(hy*25.4,3)],effective_ppi=round(ppi,2),main_map=is_map))
  sheet=Image.new('RGB',(600,235*math.ceil(len(thumbs)/2)),'#d6d2c6');d=ImageDraw.Draw(sheet)
  for i,im in enumerate(thumbs):x=i%2*300;y=i//2*235;sheet.paste(im,(x,y));d.text((x+4,y+207),f'p{i+1} / {path.stem}',fill='black')
  out=O/'contatos'/ed;out.mkdir(parents=True,exist_ok=True);sheet.save(out/(path.stem+'.jpg'),quality=90)
# Footprints are checked in the global drawing before any cuts. No image sets geometry.
usages=json.loads((O/'asset_usage.json').read_text());collisions=[]
for theme,scene in b.SCENES.items():
 m=next((m for m in b.MAPS if m['name']==theme),b.MAPS[0]);corridors=[]
 for s in b.segments(m):
  if not s['connected']:continue
  x,y=s['center'];corridors.append((x-9,y-9,18,18))
 for o in scene['objects']:
  if o['kind'] in ['bay','rug','pipe','drain']:continue
  boxes=[u['bbox_mm'] for u in usages if u['theme']==theme and u['edition']=='ilustrada' and o['kind']=='asset' and u['file']==o['file'] and u['index']==o['index'] and overlap(u['bbox_mm'],o['box'])] if o['kind']=='asset' else [o['box']]
  # Rotated assets already have physical footprints recorded in asset_usage.json.
  if any(overlap(box,c) for box in boxes for c in corridors):collisions.append(dict(theme=theme,object=o))
ck('Mobiliário fora das soleiras de 18×18 mm',not collisions,collisions)
minimum=min(v['effective_ppi'] for v in res if v['main_map']);report=dict(version='0.6',checks=len(checks),passed=len(checks)-len(issues),failures=issues,changed_pages_rendered=pages,preserved_pdf_entries=preserved,main_map_minimum_ppi=minimum,doorway_collisions=collisions,limitations=['Revisão digital; sem impressão física, montagem física ou playtest humano.','Quantidade de testes não comprova qualidade artística ou equilíbrio.'],details=checks)
(O/'resolucao_pdfs.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));(O/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (O/'RESOLUCAO_EFETIVA.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['PDF','pagina','xref','pixels_x','pixels_y','largura_impressa_mm','altura_impressa_mm','ppi_efetivo'])
 for v in res:w.writerow([v['pdf'],v['page'],v['xref'],*v['pixels'],*v['printed_mm'],v['effective_ppi']])
print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False,indent=2));sys.exit(bool(issues))
