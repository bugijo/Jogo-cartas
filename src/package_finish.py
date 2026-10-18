"""Pacotes 0.5: alternativas exclusivas, fontes completas em partes, sem referência privada."""
from pathlib import Path
import json,zipfile,hashlib,html,shutil
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-acabamento-v0.5';DIST=P/'dist';DIST.mkdir(exist_ok=True);packages=[]
def write_zip(name,items,note):
 path=DIST/name
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for file,arc in items:z.write(file,arc)
  z.writestr('00_LEIA_PRIMEIRO/ESTE_PACOTE.txt',note+'\n\nA4, 100%, sem ajustar. Escolha somente uma edição e um método. Extras são opcionais. Sem impressão física ou playtest humano.\n')
  links=''.join('<li><a href="../'+html.escape(a)+'">'+html.escape(a)+'</a></li>' for f,a in items if a.endswith('.pdf'))
  z.writestr('00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html','<!doctype html><meta charset="utf-8"><title>Zona Zero 0.5</title><style>body{font:18px sans-serif;max-width:1100px;margin:2em auto}li{margin:.6em}</style><h1>Zona Zero / acabamento 0.5</h1><p>'+html.escape(note)+'</p><p>Abra COMECE_AQUI; calibre primeiro, escala 100%. Os PDFs abaixo são somente os deste ZIP. Não imprimir alternativas duplicadas.</p><ul>'+links+'</ul>')
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 register(path,note)
def register(path,note):packages.append(dict(file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),description=note))
for edition in ['ilustrada','economica']:
 root=O/edition;manifest=json.loads((root/'00_LEIA_PRIMEIRO/manifesto.json').read_text());common=[(f,str(f.relative_to(root))) for f in (root/'00_LEIA_PRIMEIRO').iterdir() if f.is_file()]
 for method in ['duplex','manual']:
  es=[e for e in manifest['files'] if not e['optional'] and e['method'] in ['both',method]];sheets=sum(e['sheets'] for e in es)
  write_zip(f'ZZ_05_{edition.upper()}_{method.upper()}_COMPLETO.zip',common+[(root/e['file'],e['file']) for e in es],f'{edition} / {method}: {sheets} A4. '+('25 iniciais + 33 complemento.' if method=='duplex' else '33 iniciais + 39 complemento.')+' Cartas 63×88 mm. '+('Somente cartas/calibração duplex retrato, borda longa. Restante uma face.' if method=='duplex' else 'Tudo uma face. Frente + miolo opaco + verso; topos iguais. Remova códigos fora do corte.'))
  if method=='duplex':
   for stage,label in [('initial','INICIAL'),('supplement','COMPLEMENTO')]:
    chosen=[e for e in es if e['stage']==stage];n=sum(e['sheets'] for e in chosen);write_zip(f'ZZ_05_{edition.upper()}_DUPLEX_{label}.zip',common+[(root/e['file'],e['file']) for e in chosen],f'{edition} / duplex / {label}: {n} A4. Substitui a etapa correspondente no ZIP completo; não imprimir ambos.')
 es=[e for e in manifest['files'] if e['optional']]
 write_zip(f'ZZ_05_{edition.upper()}_EXTRAS_OPCIONAIS.zip',common+[(root/e['file'],e['file']) for e in es],f'{edition}: extras. Painel 2 folhas por jogador; peões 8; guia 3; bases 1; variantes 4 por destino substituem comuns; fichas 24 heróis 12. Máximo 24 inimigos, não duplicar ID.')
# Complete editable reconstruction: extract all source parts together.
code=[]
for base in ['src','content','tests']:
 for f in (P/base).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':code.append((f,str(f.relative_to(P))))
for f in P.glob('*.md'):code.append((f,f.name))
for f in [P/'requirements.txt',P/'docs/ACABAMENTO_0.5.md']:code.append((f,str(f.relative_to(P))))
note='FONTES: extraia TODAS as oito partes FONTES_05 no mesmo diretório, preservando caminhos. Python 3 + requirements.txt + DejaVu Sans. Execute python src/build_finish.py --step all; python src/validate_finish.py; python src/proof_finish.py. Alternativa: clone arte/pnp-acabamento-v0-5. Não imprimir fontes.'
write_zip('ZZ_05_FONTES_CODIGO.zip',code,note)
write_zip('ZZ_05_FONTES_ARTES_NOVAS.zip',[(f,str(f.relative_to(P))) for f in (P/'assets/v0.5').glob('*.png') if f.name!='pecas.png'],note)
write_zip('ZZ_05_FONTES_VETORES.zip',[(f,str(f.relative_to(P))) for f in (P/'assets/v0.5/vetores').glob('*.svgz')],note)
for old,new in [('ARTES','ARTES_BASE04'),('BASE_ILUSTRADA','PDF_BASE03_ILUSTRADA'),('BASE_ECONOMICA','PDF_BASE03_ECONOMICA'),('BASE_MANIFESTOS','MANIFESTOS_BASE')]:
 path=DIST/('ZZ_05_FONTES_'+new+'.zip');original=DIST/('ZZ_04_FONTES_'+old+'.zip')
 if original.exists():shutil.copyfile(original,path);register(path,note)
 else:
  if old=='ARTES':
   drafts={n+'.png' for n in ['comum','mercado','hospital','oficina','posto','condominio','estacao']}|{'condominio_ajustado.png','oficina_ajustado.png'}
   files=[f for f in (P/'assets').rglob('*') if f.is_file() and 'v0.5' not in f.parts and 'economica' not in f.parts and 'impressao' not in f.parts and not (f.parent==P/'assets/v0.4' and f.name in drafts)]
  elif old=='BASE_MANIFESTOS':files=[f for base in ['output/comece-aqui-duas-pessoas','output/revisao-0.2'] for f in (P/base).rglob('*.json')]
  else:
   ed='ilustrada' if old=='BASE_ILUSTRADA' else 'economica';files=[f for f in (P/'output/edicao-ilustrada-v0.3'/ed).rglob('*') if f.is_file() and ('extras' not in f.parts or f.name=='24_fichas.pdf' or (ed=='ilustrada' and f.name=='mapa_mercado.pdf'))]
  write_zip(path.name,[(f,str(f.relative_to(P))) for f in files],note)
# Only 0.4 originals actually used by preservation or before/after proof.
items=[];base=P/'output/edicao-fabricacao-v0.4'
for ed in ['ilustrada','economica']:
 for f in (base/ed/'04_PERSONAGENS_E_INIMIGOS').glob('*.pdf'):items.append((f,str(f.relative_to(P))))
for name in ['02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf','02_CARTAS_DUPLEX/KIT_COMPLEMENTO_2_DUPLEX.pdf','05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf','05_PAINEIS/ABRIGO_MORADORES_ESTOQUE.pdf','08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf','08_EXTRAS_OPCIONAIS/OFICINA_M01_M04_LADO_A.pdf']:
 f=base/'ilustrada'/name;items.append((f,str(f.relative_to(P))))
f=base/'evidencias/PAINEL_COM_CARTAS_REAIS.png';items.append((f,str(f.relative_to(P))))
write_zip('ZZ_05_FONTES_PDF_BASE04.zip',items,note)
items=[(f,str(f.relative_to(O))) for base in ['evidencias','contatos'] for f in (O/base).rglob('*') if f.is_file()]
for name in ['verificacao.json','resolucao_pdfs.json','resolucao.json','reconstrucao.json']:
 f=O/name
 if f.exists():items.append((f,name))
write_zip('ZZ_05_PROVAS_E_RESOLUCAO.zip',items,'Comparações reais 0.4→0.5 extraídas dos PDFs finais. Detalhe A4 100×100 mm em escala 100%. Capturas não são componentes obrigatórios. Resolução por imagem e relatório de verificação incluídos.')
(O/'pacotes.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2))
for e in packages:
 print(e['file'],round(e['bytes']/1e6,1),'MB')
 assert e['bytes']<100*1024*1024,'Dividir pacote acima do limite GitHub: '+e['file']
