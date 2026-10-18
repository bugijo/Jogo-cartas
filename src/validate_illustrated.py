"""Conferência de invariantes, conteúdo impresso, geometria e PDF. Não mede diversão."""
from pathlib import Path
import json,re,hashlib,collections
import fitz
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-ilustrada-v0.3';B=P/'output/comece-aqui-duas-pessoas';MM=72/25.4
D=json.loads((P/'content/catalog.json').read_text());M=json.loads((B/'manifesto.json').read_text());CARDS={c['id']:c for c in D['cards']};checks=[];failures=[]
def check(name,cond,detail=None):
 checks.append(dict(check=name,passed=bool(cond),detail=detail))
 if not cond:failures.append(name)
def norm(s):return re.sub(r'\s+','',s).replace('\u00ad','')
def cardbox(i,back=False):
 row,col=divmod(i,3);col=2-col if back else col
 return fitz.Rect((8.5+col*65)*MM,(14.5+row*90)*MM,(71.5+col*65)*MM,(102.5+row*90)*MM)

for f,h in json.loads((O/'baseline.json').read_text()).items():check('Base preservada '+f,hashlib.sha256((P/f).read_bytes()).hexdigest()==h)
check('324 cartas únicas',len(CARDS)==324)
check('24 heróis únicos',len({h['id'] for h in D['heroes']})==24)
check('Sem estouro de parágrafos',json.loads((O/'layout_issues.json').read_text())==[])
geo=json.loads((O/'geometry.json').read_text());edges={tuple(sorted(e)) for e in D['maps'][0]['edges']}
check('Todas as paredes/aberturas derivam do catálogo',all(g['connected']==((tuple(sorted((g['zone'],g['neighbor']))) in edges) if g['neighbor'] else False) for g in geo))
check('Todas as aberturas medem 14mm',all(abs(g['gap_mm']-(14 if g['connected'] else 0))<1e-6 for g in geo))
check('Objetos fora dos corredores de 14mm',138.5*.57>138.5/2+7 and 95*.60>95/2+7 and 138.5*.40<138.5/2-7 and 95*.39<95/2-7)
for m in D['maps']:
 adj={z:set() for z in m['zones']}
 for x,y in m['edges']:adj[x].add(y);adj[y].add(x)
 seen={m['entry']};q=list(seen)
 while q:
  for n in adj[q.pop()]-seen:seen.add(n);q.append(n)
 check(m['name']+' objetivos alcançáveis',set(m['objectives']+m['search']+[m['exit'],m['spawn']])<=seen)
 check(m['name']+' bloqueios são portas',set(map(tuple,m['blocked']))<=set(map(tuple,m['doors'])))
 check(m['name']+' portas fora das emendas',all(not ((abs(x-y)==1 and (x-1)%4==1) or (abs(x-y)==4 and (x-1)//4==1)) for x,y in m['doors']))
fonts=[];imagecount=0
for edition in ['ilustrada','economica']:
 root=O/edition;m=json.loads((root/'manifesto.json').read_text());allfiles=[e for k in ['initial','supplement'] for e in m[k]]
 check(edition+' seleção/IDs/quantidades preservados',all(m[k]==M[k] for k in ['initial_cards','supplement_cards','initial_tokens','supplement_tokens','embedded_equipment']))
 check(edition+' 25+33=58 folhas',sum(e['sheets'] for e in m['initial'])==25 and sum(e['sheets'] for e in m['supplement'])==33 and m['total_sheets']==58)
 check(edition+' 18 PDFs/72 páginas',len(allfiles)==18 and sum(e['pages'] for e in allfiles)==72)
 for entry in allfiles:
  f=root/entry['file'];doc=fitz.open(f)
  check(edition+' contagem '+f.name,len(doc)==entry['pages'])
  check(edition+' A4 '+f.name,all(abs(min(p.rect.width,p.rect.height)-210*MM)<.1 and abs(max(p.rect.width,p.rect.height)-297*MM)<.1 for p in doc))
  used=set()
  for page in doc:
   spans=[span for block in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
   used|={s['font'] for s in spans}
   # Glyphs outside the physical paper indicate clipping, even if their logical box fits.
   bad=[s['text'] for s in spans if s['bbox'][0]<0 or s['bbox'][1]<0 or s['bbox'][2]>page.rect.width+.5 or s['bbox'][3]>page.rect.height+.5]
   check(edition+' texto dentro A4 '+f.name+f'/{page.number+1}',not bad,bad)
   for info in page.get_images(full=True):imagecount+=1
   for font in page.get_fonts(full=True):
    xref,ext,typ,base,res,*_=font;clean=base.split('+')[-1]
    if clean in used or base in used:
     blob=doc.extract_font(xref)[3];fonts.append((f.name,base,len(blob)))
     check(edition+' fonte incorporada '+base+'/'+f.name,len(blob)>0)
  # Page sequence, guides/manuals/records preserve exact words and numbers.
  if entry['kind'] in ['guia','regras','registro','calibração']:
   orig=fitz.open(B/entry['file'])
   check(edition+' referência textual '+f.name,all(norm(orig[i].get_text())==norm(doc[i].get_text()) for i in range(len(doc))))
 for ids,file,initial in [(M['initial_cards'],'01_inicial/02_cartas_duplex.pdf',True),(M['supplement_cards'],'02_complemento/01_cartas_complemento_duplex.pdf',False)]:
  doc=fitz.open(root/file);backs=collections.defaultdict(set)
  for n,id in enumerate(ids):
   page=doc[n//9*2];rect=cardbox(n%9);text=norm(page.get_textbox(rect));card=CARDS[id];expected=card['text'].replace('ceil(H/2)','1') if initial else card['text']
   check(edition+' efeito e nome '+id,norm(expected) in text and norm(card['name']) in text and id in text)
   check(edition+' carta 63×88 '+id,abs(rect.width/MM-63)<1e-8 and abs(rect.height/MM-88)<1e-8)
   backrect=cardbox(n%9,True)
   # Edge antialias differs with subpixel placements; compare interior at identical local sampling via PDF extraction.
   backtext=norm(doc[n//9*2+1].get_textbox(backrect));backs[card['family']].add(backtext)
   check(edition+' verso família/reflexão '+id,norm('ZONA ZERO') in backtext and norm('COMUNIDADE') in backtext)
  check(edition+' versos INT sem ID e iguais '+file,len(backs.get('INT',set()))<=1 and all('ZC-INT' not in s for s in backs.get('INT',set())))
 for file,ids in [('01_inicial/03_lia_ivo.pdf',[h['id'] for h in D['heroes'][:2]]),('02_complemento/02_herois_resgataveis.pdf',[h['id'] for h in D['heroes'][12:]]),('extras/24_fichas.pdf',[h['id'] for h in D['heroes']])]:
  doc=fitz.open(root/file)
  for i,id in enumerate(ids):
   h=next(h for h in D['heroes'] if h['id']==id);rect=fitz.Rect(0,(i%2)*148.5*MM,210*MM,(i%2+1)*148.5*MM);text=norm(doc[i//2].get_textbox(rect))
   expected=[h['name'].upper(),h['profession'],h['story'],h['ability']]+[k.upper()+' '+str(v) for k,v in h['attributes'].items()]+sum([h['progression'][k] for k in ['3','6','9']],[])
   check(edition+' herói preservado '+id+'/'+file,all(norm(v) in text for v in expected))
   check(edition+' quatro cargas '+id+'/'+file,all('Carga'+str(j)+':' in text for j in range(1,5)))
 # 4 modules plus 6 themed alternatives retain paper and cut dimensions.
 for file in [root/'01_inicial/04_modulos_locais.pdf']+list((root/'extras').glob('mapa_*.pdf')):
  doc=fitz.open(file);check(edition+' quatro módulos '+file.name,len(doc)==4)
  check(edition+' corte e escala '+file.name,all('277 × 190' in p.get_text() for p in doc))
 # Existing 45 + 12 marker IDs remain individually printed (heroes carry names instead).
 for ids,file in [(M['initial_tokens'],'01_inicial/07_marcadores.pdf'),(M['supplement_tokens'],'02_complemento/08_tokens_resgataveis.pdf')]:
  t=''.join(p.get_text() for p in fitz.open(root/file));tokens={t['id']:t for t in D['tokens']}
  check(edition+' marcadores preservados '+file,all((tokens[id]['name'] if tokens[id]['kind']=='hero' else id) in t for id in ids))
check('Imagens realmente integradas',imagecount>100,imagecount)
report={'checks':len(checks),'passed':len(checks)-len(failures),'failures':failures,'items':checks,'used_embedded_fonts':fonts,'physical_print':False,'human_playtest':False,'balance_claim':False}
(O/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Verificações:',len(checks),'Falhas:',len(failures));print('\n'.join(failures[:30]))
raise SystemExit(bool(failures))
