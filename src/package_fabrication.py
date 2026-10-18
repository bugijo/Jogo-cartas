"""Pacotes reprodutíveis por edição e alternativa, sem referências privadas."""
from pathlib import Path
import json,zipfile,hashlib,sys
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-fabricacao-v0.4';DIST=P/'dist';DIST.mkdir(exist_ok=True);packages=[]
def zip_files(name,items,info):
 f=DIST/name
 with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for path,arc in items:z.write(path,arc)
  import html
  pdfs=[arc for path,arc in items if arc.endswith('.pdf')]
  links=''.join('<li><a href="../'+html.escape(a)+'">'+html.escape(a)+'</a></li>' for a in pdfs)
  z.writestr('00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html','<!doctype html><meta charset="utf-8"><title>Zona Zero</title><style>body{font:18px sans-serif;max-width:1000px;margin:2em auto}li{margin:.6em}</style><h1>Imprimir este pacote</h1><p>'+html.escape(info)+'</p><p>A4, 100%, sem ajustar. Siga o método escolhido; leia COMECE_AQUI e o guia de montagem. Nesta lista estão somente os PDFs realmente incluídos neste ZIP.</p><ul>'+links+'</ul>')
  z.writestr('00_LEIA_PRIMEIRO/ESTE_PACOTE.txt',info+'\n\nLeia o índice IMPRIMA_ESTES.md; arquivos de outras etapas podem estar no pacote complementar. Não imprima alternativas duplicadas. Todos em A4, escala 100%, sem ajustar. Extras têm contagens próprias e não integram as 58/72 folhas.\n')
 with zipfile.ZipFile(f) as z:assert z.testzip() is None
 packages.append(dict(file=name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),description=info))
for ed in ['ilustrada','economica']:
 root=O/ed;m=json.loads((root/'00_LEIA_PRIMEIRO/manifesto.json').read_text());common=[(f,str(f.relative_to(root))) for f in (root/'00_LEIA_PRIMEIRO').iterdir() if f.is_file()]
 for method in ['duplex','manual']:
  for stage in ['initial','supplement']:
   es=[e for e in m['files'] if not e['optional'] and e['method'] in ['both',method] and e['stage']==stage];sheets=sum(e['sheets'] for e in es)
   label='INICIAL' if stage=='initial' else 'COMPLEMENTO'
   zip_files(f'ZZ_04_{ed.upper()}_{method.upper()}_{label}.zip',common+[(root/e['file'],e['file']) for e in es],f'{ed} / {method} / {label}: {sheets} folhas A4. '+('Dia 1.' if stage=='initial' else 'Dias 2–5; use com o inicial da mesma edição/método.'))
  # Complete selected kit also generated locally; large file need not be pushed (>100MB).
  es=[e for e in m['files'] if not e['optional'] and e['method'] in ['both',method]]
  zip_files(f'ZZ_04_{ed.upper()}_{method.upper()}_COMPLETO.zip',common+[(root/e['file'],e['file']) for e in es],f'{ed} / {method} / kit completo: {sum(e["sheets"] for e in es)} folhas A4.')
 es=[e for e in m['files'] if e['optional']]
 zip_files(f'ZZ_04_{ed.upper()}_EXTRAS_OPCIONAIS.zip',common+[(root/e['file'],e['file']) for e in es],f'{ed}: extras opcionais. Peões 8 folhas; painel 2 por jogador; guia 3; variantes 4 por destino; todas as fichas 12. Não acrescente tudo ao kit básico automaticamente.')
# Editable source set; generated economic caches and abandoned art drafts excluded.
items=[];drafts={n+'.png' for n in ['comum','mercado','hospital','oficina','posto','condominio','estacao']}|{'condominio_ajustado.png','oficina_ajustado.png'}
for base in ['src','content','assets','tests']:
 for f in (P/base).rglob('*'):
  if not f.is_file() or '__pycache__' in f.parts or 'economica' in f.parts or 'impressao' in f.parts or f.suffix=='.pyc':continue
  if f.parent==P/'assets/v0.4' and f.name in drafts:continue
  items.append((f,str(f.relative_to(P))))
for f in P.glob('*.md'):items.append((f,f.name))
items.append((P/'docs/PRODUCAO_0.4.md','docs/PRODUCAO_0.4.md'))
# Old generators depend on these stable PDFs/manifests; include base outputs for deterministic copies.
for ed in ['ilustrada','economica']:
 for f in (P/'output/edicao-ilustrada-v0.3'/ed).rglob('*'):
  if f.is_file() and 'extras' not in f.parts:items.append((f,str(f.relative_to(P))))
 f=P/'output/edicao-ilustrada-v0.3'/ed/'extras/24_fichas.pdf';items.append((f,str(f.relative_to(P))))
 if ed=='ilustrada':
  f=P/'output/edicao-ilustrada-v0.3'/ed/'extras/mapa_mercado.pdf';items.append((f,str(f.relative_to(P))))
for base in ['output/comece-aqui-duas-pessoas','output/revisao-0.2']:
 for f in (P/base).rglob('*.json'):items.append((f,str(f.relative_to(P))))
source_items=items.copy()
zip_files('ZZ_04_FONTES_EDITAVEIS.zip',items,'Fontes editáveis e base preservada. Python 3; pip install reportlab Pillow pymupdf. Execute python src/build_fabrication.py --step all; python src/validate_fabrication.py; python src/proof_fabrication.py. O repositório GitHub contém o histórico e todas as edições anteriores.')
for label,prefixes in [('CODIGO',('src/','content/','docs/','tests/')),('ARTES',('assets/',)),('BASE_ILUSTRADA',('output/edicao-ilustrada-v0.3/ilustrada/',)),('BASE_ECONOMICA',('output/edicao-ilustrada-v0.3/economica/',)),('BASE_MANIFESTOS',('output/comece-aqui-duas-pessoas/','output/revisao-0.2/'))]:
 subset=[(p,a) for p,a in source_items if a.startswith(prefixes) or (label=='CODIGO' and '/' not in a)]
 zip_files('ZZ_04_FONTES_'+label+'.zip',subset,'Parte das fontes editáveis: '+label+'. Para reconstruir, extraia as cinco partes FONTES no mesmo diretório. Alternativa: clone a branch do repositório, que já contém todas elas.')
zip_files('ZZ_04_PROVAS_E_VERIFICACOES.zip',[(f,str(f.relative_to(O))) for base in ['evidencias','contatos'] for f in (O/base).rglob('*') if f.is_file()]+[(O/'verificacao.json','verificacao.json')],'Capturas e relatórios digitais; não imprimir como componentes.')
(O/'pacotes.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2))
print('\n'.join(f'{e["file"]}: {e["bytes"]/1e6:.1f} MB'+(' (dividido em inicial + complemento para GitHub)' if e['bytes']>99_000_000 else '') for e in packages))
