from pathlib import Path
from collections import deque,Counter
import json,itertools,math,sys
import fitz
P=Path(__file__).resolve().parents[1];O=P/'output';D=json.loads((P/'content/catalog.json').read_text());checks=[]
def check(name,condition,detail=''):
 checks.append(dict(name=name,passed=bool(condition),detail=detail));print(('OK ' if condition else 'FALHA ')+name+(' • '+str(detail) if detail else ''))
ids=[x['id'] for x in D['cards']+D['heroes']+D['maps']]
check('IDs únicos',len(ids)==len(set(ids)),len(ids))
check('24 heróis / 12 iniciais',len(D['heroes'])==24 and sum(h['initial'] for h in D['heroes'])==12)
rescue={i for c in D['cards'] if c['family']=='MOR' for i in c['hero_refs']}
check('Todos os 12 desbloqueáveis têm encontro',rescue==set(range(13,25)),sorted(rescue))
check('12 vínculos / 12 intenções',Counter(c['family'] for c in D['cards'])['VIN']==12 and Counter(c['family'] for c in D['cards'])['INT']==12)
check('Proporção das intenções',Counter(c['name'] for c in D['cards'] if c['family']=='INT')==Counter({'Solidário':7,'Assustado':3,'Oportunista':1,'Infiltrado':1}))
resources={c['name'] for c in D['cards'] if c['family']=='REC'}
check('Saque só concede recursos existentes',all(set(c['reward'])<=resources for c in D['cards'] if c['family']=='SAQ'))
check('Seis buscas e seis cartas por destino',all(sum(c.get('region')==f for c in D['cards'])==6 for f in ['MER','HOS','OFI','POS','CON','EST']))
check('Referências de arquivos existem',all((P/r.split(' §')[0]).exists() for c in D['cards'] for r in c['refs']))
for M in D['maps']:
 def distances(locked):
  g={z:[] for z in M['zones']}
  for a,b in M['edges']:
   if locked and [a,b] in M['blocked']:continue
   g[a].append(b);g[b].append(a)
  dist={M['entry']:0};q=deque(dist)
  while q:
   z=q.popleft()
   for n in g[z]:
    if n not in dist:dist[n]=dist[z]+1;q.append(n)
  return dist
 dist=distances(False); alternative=distances(True)
 check(M['name']+' conectividade',len(dist)==16 and all(z in dist for z in M['objectives']+[M['spawn'],M['exit']]),{str(z):dist.get(z) for z in M['objectives']})
 check(M['name']+' rota alternativa sem bloqueios',all(z in alternative for z in M['objectives']))
 def module(z):r,c=divmod(z-1,4);return r//2,c//2
 check(M['name']+' portas fora das emendas',all(module(a)==module(b) for a,b in M['doors']))
available={c['name'] for c in D['cards'] if c['family'] in ['REC','PEC','EQU']}
check('Custos estruturados têm componentes e valores válidos',all(set(c['cost'])<=available and all(v>0 for v in c['cost'].values()) and c['work']>0 for c in D['cards'] if c['family']=='PRO'))
check('24 retratos produzidos e referenciados',all(h.get('art') and (P/h['art']['path']).exists() for h in D['heroes']))
manifest=json.loads((O/'duplex_manifest.json').read_text())
check('324 posições frente/verso',len(manifest)==len(D['cards']))
check('Duplex reflete só colunas',all(m['back_col']==2-m['front_col'] and 0<=m['row']<=2 for m in manifest))
check('Verso de intenção único',{m['back_key'] for m in manifest if m['family']=='INT'}=={'INT'})
doc_cards=fitz.open(O/'03_cartas_duplex.pdf');actual_positions=[]
for i,c in enumerate(D['cards']):
 sheet,slot=divmod(i,9);r,col=divmod(slot,3);x=(8.5+col*65)*72/25.4;y=(14.5+r*90)*72/25.4
 rect=fitz.Rect(x,y,x+63*72/25.4,y+88*72/25.4)
 text=doc_cards[sheet*2].get_textbox(rect)
 bx=(8.5+(2-col)*65)*72/25.4;brect=fitz.Rect(bx,y,bx+63*72/25.4,y+88*72/25.4)
 back=doc_cards[sheet*2+1].get_textbox(brect)
 actual_positions.append(c['id'] in text and 'ZONA ZERO' in back and (c['family']!='INT' or ('INTENÇÃO' in back and 'ZC-' not in back)))
check('Correspondência lida nos 324 recortes PDF',all(actual_positions),sum(actual_positions))
check('Grade física',3*63+2*2==193 and 3*88+2*2==268 and 193+2*8.5==210 and 268+2*14.5==297)
check('Nenhum estouro de parágrafo',json.loads((O/'layout_issues.json').read_text())==[])
pagecounts={};pdf_problems=[]
for path in sorted(O.glob('*.pdf')):
 doc=fitz.open(path);pagecounts[path.name]=len(doc)
 for page in doc:
  w,h=page.rect.width,page.rect.height;dims=sorted([w,h]);a4=sorted([210*72/25.4,297*72/25.4])
  if any(abs(a-b)>1 for a,b in zip(dims,a4)):pdf_problems.append(f'{path.name} página {page.number+1}: dimensão')
  for word in page.get_text('words'):
   if word[0]<-.2 or word[1]<-.2 or word[2]>w+.2 or word[3]>h+.2:pdf_problems.append(f'{path.name} página {page.number+1}: texto fora')
check('Dimensões A4 e texto dentro da página',not pdf_problems,pdf_problems[:5])
check('Cartas 72 páginas duplex',pagecounts.get('03_cartas_duplex.pdf')==72)
# Deterministic economic bounds, NOT a full game simulation.
economy=[]
from rules_engine import family_setup
links=[(0,0)]*4+[(1,0)]*6+[(0,1),(1,1)]
for h in range(2,7):
 vals=[family_setup(h,x)['consumers'] for x in itertools.combinations(links,h)]
 for C in [min(vals),max(vals)]:
  lot=4*math.ceil(C/4);start=4*math.ceil(2*C/4)
  # A possible five-day supply schedule, presuming all deliveries succeed and no added population/cercos.
  # market d1 (2 lots each); workshop d2 (1 each); station d3 (2 water); d4/d5 work.
  f,w=start,start;rows=[]
  for day in range(1,6):
   if day==1:f+=2*lot;w+=2*lot
   if day==2:f+=lot;w+=lot
   if day==3:w+=2*lot
   # No expedition d4/d5: all founders may build two work/day.
   if day==5:w+=2*C # completion fill (assuming four work applied by then)
   f-=C;w-=C;rows.append({'day':day,'food':f,'water':w})
  economy.append(dict(heroes=h,consumers=C,days=rows,assumptions='Todos lotes entregues; sem perda/carga/combate/resgate. Limite econômico, não partida.'))
check('Limite de oferta em cinco dias sem escassez inevitável',all(min(r['food'],r['water'])>=0 for s in economy for r in s['days']))
(O/'economy_scenarios.json').write_text(json.dumps(economy,ensure_ascii=False,indent=2))
(O/'validation.json').write_text(json.dumps(dict(checks=checks,pagecounts=pagecounts,pdf_problems=pdf_problems),ensure_ascii=False,indent=2))
print('Páginas:',sum(pagecounts.values()),pagecounts)
sys.exit(0 if all(c['passed'] for c in checks) else 1)
