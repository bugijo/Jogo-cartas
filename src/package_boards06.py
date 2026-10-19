"""Distribuição 0.6: atualização só de mapas e alternativas completas exclusivas."""
from pathlib import Path
import json,zipfile,hashlib,html,sys
import build_boards06 as b
P=b.P;O=b.O;DIST=P/'dist';DIST.mkdir(exist_ok=True);ONLY_SOURCES='--sources-only' in sys.argv
PACKAGES=json.loads((O/'pacotes.json').read_text()) if ONLY_SOURCES and (O/'pacotes.json').exists() else []
def make(name,items,note,entries=None):
 if ONLY_SOURCES and not name.startswith('ZZ_06_FONTES_'):return
 path=DIST/name
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for file,arc in items:z.write(file,arc)
  z.writestr('00_LEIA_PRIMEIRO/LEIA_PRIMEIRO.txt',note+'\n\nA4 exato; 100%, sem ajustar. Não imprimir fontes ou provas como componentes. Extras e métodos são alternativas. Edição anterior preservada. Sem impressão física/playtest humano.\n')
  links=''.join('<li><a href="../'+html.escape(arc)+'">'+html.escape(arc)+'</a></li>' for file,arc in items if arc.endswith('.pdf'))
  z.writestr('00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html','<!doctype html><meta charset="utf-8"><title>Zona Zero 0.6</title><style>body{font:18px sans-serif;max-width:1150px;margin:2em auto}li{margin:.7em}</style><h1>Zona Zero / tabuleiros 0.6</h1><p>'+html.escape(note)+'</p><p>Escala 100%, sem ajustar. Use somente uma edição e um método. Os links abaixo apontam apenas para os PDFs deste ZIP.</p><ul>'+links+'</ul>')
  if entries is not None:
   z.writestr('00_LEIA_PRIMEIRO/MANIFESTO_DESTE_PACOTE.json',json.dumps(dict(version='0.6',note=note,files=entries),ensure_ascii=False,indent=2))
   md='# O que está neste ZIP\n\n'+note+'\n\n| Arquivo | Uso | Folhas | Cópias | Orientação | Impressão | Substitui |\n|---|---|---:|---:|---|---|---|\n'
   for e in entries:md+=f'| [{e["file"]}](../{e["file"]}) | '+('opcional' if e['optional'] else 'básico / consulta' if 'montage' in e['kind'] else 'básico')+f' | {e["sheets"]} | {e["copies"]} | {e["orientation"]} | '+('duplex, borda longa' if e['duplex'] else 'uma face')+' | '+str(e.get('replaces') or 'mesmo componente anterior')+' |\n'
   z.writestr('00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md',md)
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 assert path.stat().st_size<100*1024*1024,'Dividir pacote: '+str(path)
 PACKAGES[:]=[p for p in PACKAGES if p['file']!=name]
 PACKAGES.append(dict(file=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),note=note));print(name,round(path.stat().st_size/1e6,1),'MB',flush=True)

for ed in ['ilustrada','economica']:
 root=O/ed;m=json.loads((root/'00_LEIA_PRIMEIRO/manifesto.json').read_text());entries=m['files']
 changed=[e for e in entries if e['file'] in b.CHANGED]
 make('ZZ_06_'+ed.upper()+'_SOMENTE_MAPAS.zip',[(root/e['file'],e['file']) for e in changed],
      'ATUALIZAÇÃO PARA QUEM JÁ TEM A 0.5: nenhuma carta, painel, peão ou regra precisa ser baixada/reimpressa. Troque somente as quatro folhas do tabuleiro escolhido: COMUNS OU uma variante temática. Seis diagramas novos substituem os antigos; podem ser consultados na tela. Este ZIP oferece 34 páginas A4: 4 comuns + 24 de seis variantes + 6 diagramas. NÃO é uma ordem para imprimir 34 folhas. Portas e bloqueios impressos mostram a preparação inicial; depois prevalecem marcadores e registro. Tudo uma face, paisagem. Corte 277×190 mm; M1/M2 acima, M3/M4 abaixo, sem girar nem sobrepor.',changed)
 for method,total in [('duplex',58),('manual',72)]:
  es=[e for e in entries if not e['optional'] and e['method'] in ['both',method]];assert sum(e['sheets'] for e in es)==total
  note=f'KIT COMPLETO {ed} / {method}: {total} folhas A4. '+('25 iniciais + 33 complemento. Somente cartas/calibração duplex retrato, borda longa; restante uma face.' if method=='duplex' else '33 iniciais + 39 complemento. Tudo uma face. Cole frente + miolo opaco + verso com topos iguais; elimine códigos fora do corte.')+' Cartas e demais componentes preservados da 0.5; mapas atualizados. Escolha só este método, não imprima a outra alternativa.'
  make('ZZ_06_'+ed.upper()+'_'+method.upper()+'_COMPLETO.zip',[(root/e['file'],e['file']) for e in es],note,es)
  if method=='duplex':
   for stage,label in [('initial','INICIAL'),('supplement','COMPLEMENTO')]:
    chosen=[e for e in es if e['stage']==stage];n=sum(e['sheets'] for e in chosen)
    make('ZZ_06_'+ed.upper()+'_DUPLEX_'+label+'.zip',[(root/e['file'],e['file']) for e in chosen],f'{ed} / {label}: {n} folhas A4. Substitui essa etapa do completo; não imprimir ambos. Somente cartas/calibração duplex retrato, borda longa. Mapas uma face paisagem, 100%.',chosen)
 es=[e for e in entries if e['optional'] and e['file'] not in b.CHANGED]
 make('ZZ_06_'+ed.upper()+'_EXTRAS_OPCIONAIS.zip',[(root/e['file'],e['file']) for e in es],'EXTRAS PRESERVADOS: escolha somente o que usar. Variantes atualizadas estão no ZIP SOMENTE_MAPAS. Painel: 2 folhas por jogador. Peões: 8 folhas. Fichas completas: 12. Guia: 3. Bases: 1. Não imprimir tudo como se fosse obrigatório. Mesmos IDs e limite de 24 inimigos.',es)

source=[]
for f in (P/'src').glob('*.py'):source.append((f,str(f.relative_to(P))))
for f in [P/'requirements.txt',P/'tests/test_boards06.py',P/'content/catalog.json',P/'content/map_layouts.json']+[P/'content/production'/n for n in ['baseline_0.6.json','geometry_0.6.json','scenes_0.6.json','crops_0.6.json']]:source.append((f,str(f.relative_to(P))))
for f in list(P.glob('*.md'))+[P/'docs/TABULEIROS_0.6.md']:source.append((f,str(f.relative_to(P))))
assets={o['file'] for scene in b.SCENES.values() for o in scene['objects'] if o['kind']=='asset'}|{'assets/v0.6/pisos_materiais.png'}
for name in sorted(assets):source.append((P/name,name))
for f in (P/'assets/v0.6/vetores').glob('*.svgz'):source.append((f,str(f.relative_to(P))))
note='FONTES EDITÁVEIS 0.6. Python 3, requirements.txt e DejaVu Sans. Apenas mapas: python src/build_boards06.py --maps-only. Para reconstruir o kit completo/provas, extraia também todas as partes FONTES_BASE05 no mesmo diretório; execute build_boards06.py, validate_boards06.py, proof_boards06.py, document_boards06.py e package_boards06.py. Os componentes anteriores são copiados, nunca regenerados. Fontes das cartas/peões 0.5 continuam disponíveis no índice 0.5. Não imprimir estas partes.'
make('ZZ_06_FONTES_CODIGO_ARTE.zip',source,note)
SOURCE_PATHS={arc for file,arc in source}
for ed in ['ilustrada','economica']:
 files=sorted((b.BASE/ed).rglob('*.pdf'))+[b.BASE/ed/'00_LEIA_PRIMEIRO/manifesto.json']
 if ed=='ilustrada':files+=sorted(f for f in b.BASE.rglob('*.pdf') if f.relative_to(b.BASE).parts[0] not in ['ilustrada','economica'])+[P/'output/edicao-fabricacao-v0.4/ilustrada/08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf']
 SOURCE_PATHS.update(str(f.relative_to(P)) for f in files)
 chunks=[];chunk=[];size=0
 for f in files:
  if chunk and size+f.stat().st_size>85*1024*1024:chunks.append(chunk);chunk=[];size=0
  chunk.append(f);size+=f.stat().st_size
 if chunk:chunks.append(chunk)
 for i,chunk in enumerate(chunks,1):make('ZZ_06_FONTES_BASE05_'+ed.upper()+f'_{i:02}.zip',[(f,str(f.relative_to(P))) for f in chunk],note)
missing=set(json.loads((P/'content/production/baseline_0.6.json').read_text()))-SOURCE_PATHS
assert not missing,'Dependências congeladas ausentes das fontes: '+str(sorted(missing))
visual=[(f,str(f.relative_to(O))) for folder in ['evidencias','contatos'] for f in (O/folder).rglob('*') if f.is_file() and f.suffix!='.pdf']
make('ZZ_06_PROVAS_VISUAIS.zip',visual,'Capturas extraídas dos PDFs A4 finais: versões 0.4/0.5/0.6, sete montagens, econômica, emenda e ocupação. Capturas não são componentes de jogo.')
files=[f for f in (O/'evidencias').glob('*.pdf')]+[O/n for n in ['verificacao.json','resolucao_pdfs.json','asset_usage.json','RESOLUCAO_EFETIVA.csv','USOS_ASSETS.csv','encaixe.json','reconstrucao.json'] if (O/n).exists()]+[P/'VISUAL_QA.md',P/'ASSET_MANIFEST.md',P/'docs/TABULEIROS_0.6.md']
make('ZZ_06_PROVAS_ESCALA_RELATORIOS.zip',[(f,str(f.relative_to(O)) if f.is_relative_to(O) else f.name) for f in files],'Provas A4 de escala física e ocupação, relatórios de geometria, preservação, resolução e reconstrução. Uso opcional de conferência; não somar ao kit de 58/72 folhas. Não comprova impressão física.')
(O/'pacotes.json').write_text(json.dumps(PACKAGES,ensure_ascii=False,indent=2));print('Total:',len(PACKAGES),'ZIPs.')
