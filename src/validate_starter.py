from pathlib import Path
import json,math,hashlib,zipfile
from collections import Counter
import fitz
P=Path(__file__).resolve().parents[1];R=P/'output/comece-aqui-duas-pessoas';M=json.loads((R/'manifesto.json').read_text());D=json.loads((P/'content/catalog.json').read_text());byid={c['id']:c for c in D['cards']};checks=[]
def check(name,passed,detail=''):
 checks.append(dict(name=name,passed=bool(passed),detail=detail));print(('OK ' if passed else 'FALHA ')+name+': '+str(detail))
check('25 folhas iniciais',M['initial_sheets']==25,M['initial_sheets']);check('33 folhas complemento',M['supplement_sheets']==33,M['supplement_sheets']);check('58 folhas capítulo',M['total_sheets']==58,M['total_sheets'])
a,b=M['initial_cards'],M['supplement_cards'];check('62+52 cartas únicas existentes',len(a)==62 and len(b)==52 and len(set(a+b))==114 and set(a+b)<=set(byid))
for family in ['VIN','INT','VIA','HOR','CER']:
 check('Monte '+family+' completo no inicial',{c['id'] for c in D['cards'] if c['family']==family}=={i for i in a if byid[i]['family']==family})
check('Saque regional preservado',all(sum(byid[i].get('region')==reg for i in a+b)==6 for reg in ['MER','HOS','OFI','POS','CON','EST']))
check('Pés de cabra sem carta duplicada',not(set(M['embedded_equipment'])&set(a+b)) and set(M['embedded_equipment'])<=set(byid))
check('Marcadores de ambos heróis no inicial',{'ZC-TOK-0001','ZC-TOK-0002'}<=set(M['initial_tokens']))
check('Sem PDFs extras nas pastas de impressão',all({str(p.relative_to(R)) for p in (R/folder).glob('*.pdf')}=={e['file'] for e in M[key]} for key,folder in [('initial','01_inicial'),('supplement','02_complemento')]))
problems=[]
for e in M['initial']+M['supplement']:
 doc=fitz.open(R/e['file']);check('Folhas '+Path(e['file']).name,len(doc)==e['pages'] and e['sheets']==(math.ceil(len(doc)/2) if e['duplex'] else len(doc)))
 if e['duplex']:check('Duplex em pares '+Path(e['file']).name,len(doc)%2==0)
 for page in doc:
  dims=sorted([page.rect.width,page.rect.height]);target=sorted([210*72/25.4,297*72/25.4])
  if any(abs(x-y)>1 for x,y in zip(dims,target)):problems.append(e['file']+' A4')
  for w in page.get_text('words'):
   if w[0]<0 or w[1]<0 or w[2]>page.rect.width+.1 or w[3]>page.rect.height+.1:problems.append(e['file']+' texto fora')
check('A4 e texto dentro de página',not problems,problems)
check('Parágrafos cabem nas caixas',not json.loads((R/'conferencia/layout_issues.json').read_text()))
for ids,key in [(a,'initial'),(b,'supplement')]:
 entry=next(e for e in M[key] if e['kind']=='cartas');doc=fitz.open(R/entry['file']);ok=[];safe=[];secret=[]
 for i,cid in enumerate(ids):
  sheet,slot=divmod(i,9);row,col=divmod(slot,3);x=(8.5+65*col)*72/25.4;y=(14.5+90*row)*72/25.4
  front=fitz.Rect(x,y,x+63*72/25.4,y+88*72/25.4);bx=(8.5+65*(2-col))*72/25.4;back=fitz.Rect(bx,y,bx+63*72/25.4,y+88*72/25.4)
  ft=doc[2*sheet].get_textbox(front);bt=doc[2*sheet+1].get_textbox(back)
  ok.append(cid in ft and 'ZONA ZERO' in bt)
  if byid[cid]['family']=='INT':secret.append('INTENÇÃO' in bt and 'ZC-' not in bt)
  for w in doc[2*sheet].get_text('words',clip=front):
   safe.append(w[0]>=front.x0+3.8*72/25.4 and w[2]<=front.x1-3.8*72/25.4 and w[1]>=front.y0+3.8*72/25.4 and w[3]<=front.y1-3.8*72/25.4)
 check('IDs e colunas duplex '+key,all(ok),len(ok));check('Texto seguro no corte '+key,all(safe));check('Versos secretos neutros '+key,all(secret))
cards_text=' '.join(p.get_text() for p in fitz.open(R/'01_inicial/02_cartas_duplex.pdf'));check('Quantidade da Horda resolvida para duas pessoas','ceil(' not in cards_text)
guide=fitz.open(R/'01_inicial/01_comece_aqui.pdf');titles=json.loads((P/'content/starter/01_guia.json').read_text());check('Guia em seis páginas sem seções deslocadas',len(guide)==6 and all(p['title'].split(' — ')[0] in guide[i].get_text().replace('\n',' ') for i,p in enumerate(titles)))
from review_five_days import run
replay=run();check('Replay cinco dias passa',replay['status']=='PASS')
# Verify old release bundle exactly, preserving the delivered artifact.
old=P/'dist/Zona-Zero-Comunidade-Prototipo-0.1.zip';check('ZIP 0.1 preservado',hashlib.sha256(old.read_bytes()).hexdigest()=='e6dd37d963da8798989e51b7cbcc4a159fff57b160f6f69747107ad4067089f8')
(R/'conferencia/verificacao.json').write_text(json.dumps(dict(checks=checks,passed=sum(x['passed'] for x in checks),total=len(checks),pages=sum(e['pages'] for e in M['initial']+M['supplement'])),ensure_ascii=False,indent=2))
assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]
print('TOTAL',len(checks),'verificações aprovadas')
