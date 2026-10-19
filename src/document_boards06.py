"""Índices e inventário gerados dos PDFs efetivamente conferidos."""
from pathlib import Path
import json,csv,hashlib
from PIL import Image
import build_boards06 as b
P=b.P;O=b.O;qa=json.loads((O/'verificacao.json').read_text());assert not qa['failures'],qa['failures']
uses=json.loads((O/'asset_usage.json').read_text());assets=[]
for name in sorted({u['file'] for u in uses}):
 path=P/name;im=Image.open(path);records=[u for u in uses if u['file']==name]
 assets.append(dict(file=name,origin='render de A–C a 200 ppi para miniatura; não inclui geometria/textos' if name.startswith('output/') else 'original existente 0.5' if '/v0.5/' in name else 'geração integrada de imagem original, com revisão de projeção/recorte',pixels=list(im.size),destinations=sorted({u['theme'] for u in records}),integrated=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),minimum_used_ppi=round(min(u['effective_ppi'] for u in records),2)))
inventory=dict(version='0.6',main_map_minimum_ppi=qa['main_map_minimum_ppi'],main_geometry='vetorial, catálogo congelado',assets=assets,placements_file='asset_usage.json',exceptions='Miniaturas de ambientação dos diagramas: 200 ppi, texto e geometria vetoriais separados. Nenhuma exceção abaixo de 211,3 ppi nos mapas principais.',remaining_illustrations=[])
(O/'ASSET_MANIFEST.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
with (O/'USOS_ASSETS.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['arquivo','destino','edicao','originais_px','recorte_px','pixels_utilizados','tamanho_impresso_mm','ppi','papel'])
 for u in uses:w.writerow([u['file'],u['theme'],u['edition'],u['original_pixels'],u['crop_pixels'],u['used_pixels'],u['print_mm'],round(u['effective_ppi'],2),u.get('role','mobiliário nativo')])
raw='https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-tabuleiros-v0-6/'
blob='https://github.com/bugijo/Jogo-cartas/blob/arte/pnp-tabuleiros-v0-6/'
md='# Zona Zero 0.6 / baixar e imprimir\n\nSe já tem a 0.5, baixe SOMENTE MAPAS. Cartas, painel, peões, abrigo e regras continuam os mesmos arquivos.\n\n| Atualização sem cartas | ZIP |\n|---|---|\n'
for ed in ['ILUSTRADA','ECONOMICA']:md+=f'| {ed.title()} | [Somente mapas]({raw}dist/ZZ_06_{ed}_SOMENTE_MAPAS.zip) |\n'
md+='\nPara atualizar o tabuleiro, reimprima apenas **4 folhas**: comuns OU um destino temático. Os seis diagramas novos substituem os antigos e podem ser vistos na tela. Cada ZIP oferece 34 páginas: 4 comuns + 24 das seis variantes + 6 diagramas; **não imprimir tudo como obrigatório**. Não reimprima cartas ou outros componentes.\n\nMapas: A4 paisagem, uma face, escala 100%, sem ajustar. Corte 277×190 mm; M1/M2 acima e M3/M4 abaixo; todos com topo para cima, sem sobreposição. Tabuleiro unido: 554×380 mm. Variantes são peças separadas, sem lado B. Portas/bloqueios dos comuns são configurados pelos marcadores conforme o diagrama. Sinais impressos indicam a preparação inicial; após abertura prevalecem os marcadores e o registro persistente.\n\n## Kits completos / escolha uma alternativa\n\n| Edição | Duplex | Recortar e colar |\n|---|---|---|\n'
for ed in ['ILUSTRADA','ECONOMICA']:md+=f'| {ed.title()} | [58 folhas: 25 + 33]({raw}dist/ZZ_06_{ed}_DUPLEX_COMPLETO.zip) | [72 folhas: 33 + 39]({raw}dist/ZZ_06_{ed}_MANUAL_COMPLETO.zip) |\n'
md+='\nDuplex: somente cartas/calibração em retrato, borda longa. Mapas e demais painéis uma face. Método manual: tudo uma face; frente + miolo opaco + verso, topos iguais. Escolha apenas um método. Extraia e abra `00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html`; o índice interno lista só os PDFs daquele ZIP.\n\n'
for ed in ['ILUSTRADA','ECONOMICA']:md+=f'- {ed.title()}: [Inicial 25 folhas]({raw}dist/ZZ_06_{ed}_DUPLEX_INICIAL.zip) + [complemento 33]({raw}dist/ZZ_06_{ed}_DUPLEX_COMPLEMENTO.zip), em lugar do completo. [Extras opcionais]({raw}dist/ZZ_06_{ed}_EXTRAS_OPCIONAIS.zip).\n'
md+='\nZIP de extras preservados (28 folhas se imprimir todas as opções): painel 2 folhas/jogador; peões 8; fichas completas 12; guia 3; bases 1. Variantes atualizadas estão em SOMENTE_MAPAS, 4/destino substituem comuns. Nada disso aumenta o kit obrigatório de 58 folhas.\n\n## PDFs separados\n\n| Componente | Ilustrada | Econômica | Uso |\n|---|---|---|---|\n'
for rel in b.CHANGED:
 title=Path(rel).stem;usage='4 A4, substitui o tabuleiro anterior' if rel.endswith('_M01_M04_LADO_A.pdf') else '1 A4, referência' if 'MERCADO_MONTAGEM' in rel else '5 A4, referência'
 md+=f'| {title} | [PDF]({raw}output/edicao-tabuleiros-v0.6/ilustrada/{rel}) | [PDF]({raw}output/edicao-tabuleiros-v0.6/economica/{rel}) | {usage} |\n'
md+=f'\n[Índice completo ilustrado]({blob}output/edicao-tabuleiros-v0.6/ilustrada/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md) · [Índice econômico]({blob}output/edicao-tabuleiros-v0.6/economica/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md)\n\n## Fontes e verificação\n\n'
md+=f'- [Código, JSON, arte nativa e geometria SVGZ]({raw}dist/ZZ_06_FONTES_CODIGO_ARTE.zip). Para gerar só mapas: `python src/build_boards06.py --maps-only`.\n'
# Source bases are grouped by a fixed 85 MiB uncompressed budget, matching the packager.
for ed in ['ilustrada','economica']:
 files=sorted((b.BASE/ed).rglob('*.pdf'))+[b.BASE/ed/'00_LEIA_PRIMEIRO/manifesto.json']
 if ed=='ilustrada':files+=sorted((b.BASE/'amostras').rglob('*.pdf'))+[P/'output/edicao-fabricacao-v0.4/ilustrada/08_EXTRAS_OPCIONAIS/MERCADO_M01_M04_LADO_A.pdf']
 chunks=1;size=0
 for f in files:
  if size and size+f.stat().st_size>85*1024*1024:chunks+=1;size=0
  size+=f.stat().st_size
 for i in range(1,chunks+1):md+=f'- [Base PDF 0.5 {ed}, parte {i}]({raw}dist/ZZ_06_FONTES_BASE05_{ed.upper()}_{i:02}.zip). Para reconstrução completa/provas, extraia todas as partes junto ao código.\n'
md+=f'- [Capturas e comparações reais]({raw}dist/ZZ_06_PROVAS_VISUAIS.zip) · [Provas A4 e relatórios]({raw}dist/ZZ_06_PROVAS_ESCALA_RELATORIOS.zip). Provas não são folhas obrigatórias.\n'
md+=f'\nMobiliário principal: pelo menos **{qa["main_map_minimum_ppi"]} ppi efetivos**, medidos nas transformações do PDF; sem ampliação artificial. [Usos com recortes, pixels e tamanho físico]({raw}output/edicao-tabuleiros-v0.6/USOS_ASSETS.csv) · [Medição independente dos PDFs]({raw}output/edicao-tabuleiros-v0.6/RESOLUCAO_EFETIVA.csv). As miniaturas dos diagramas têm 200 ppi e geometria/textos vetoriais próprios.\n\nA simulação máxima usa bases de 22×12 mm, 24 inimigos + 6 heróis. Os marcadores planos de 29×29 mm são mostrados em cenário usual; 24 deles não cabem sem sobreposição numa única zona. Não houve redução de limite, bases ou zonas.\n\nPython 3 + requirements.txt + DejaVu Sans. Fluxo completo: `build_boards06.py` → `validate_boards06.py` → `proof_boards06.py` → `document_boards06.py` → `package_boards06.py`, todos em src/. Testes próprios: `python -m unittest discover -s tests -p test_boards06.py`.\n\n[Relatório visual](VISUAL_QA.md) · [Checkpoint](CHECKPOINT.md). Sem impressão física, montagem física ou playtest humano. Edições anteriores preservadas, sem merge na principal.\n'
(P/'DOWNLOADS_0.6.md').write_text(md)
def section(name,body):
 path=P/name;s=path.read_text() if path.exists() else '';marker='\n<!-- TABULEIROS06 -->\n';s=s.split(marker)[0].rstrip();path.write_text(s+marker+body+'\n')
section('ASSET_MANIFEST.md',f'''## Tabuleiros 0.6
Inventário em output/edicao-tabuleiros-v0.6/ASSET_MANIFEST.json. Usos por arquivo, recorte nativo, pixels, tamanho físico e ppi em USOS_ASSETS.csv; medição independente do PDF em RESOLUCAO_EFETIVA.csv. O mínimo principal medido é {qa['main_map_minimum_ppi']} ppi. Novas pranchas e materiais originais em assets/v0.6; artes 0.5 boas mantidas, sem reamostragem. Miniaturas dos diagramas são derivadas de A–C a 200 ppi; D–E permanecem vetoriais, com rótulos próprios legíveis. Geometria SVGZ é separada da arte, não se apresenta como mapa inteiro ilustrado. Cenas completas editáveis em Python/JSON e PNGs. Rascunhos rejeitados não entram nos pacotes. Nenhum prompt contado como imagem e nenhuma referência privada distribuída.''')
section('VISUAL_QA.md',f'''## Tabuleiros 0.6
Base b99c470, branch arte/pnp-tabuleiros-v0-6. {qa['passed']}/{qa['checks']} verificações finais sem falhas; {qa['changed_pages_rendered']} páginas alteradas renderizadas. {qa['preserved_pdf_entries']} entradas PDF preservadas byte a byte nas duas edições, sem regenerar cartas, painel, peões, abrigo ou regras. Mesmos 58/72 A4 e mesmas posições/conexões/portas/bloqueios. O parâmetro de bloqueio, omitido nos módulos grandes 0.5, agora é aplicado conforme o catálogo.

Inspeção direta: mercado 0.4→0.5→0.6, sete tabuleiros montados e econômica, emenda central, duas áreas de 100×100 mm em A4 real, ocupação máxima de bases e cenário com seis marcadores originais de 29 mm. Capturas vêm dos PDFs finais. Sete remontagens comparadas pixel a pixel com as fontes globais (encaixe.json); as diferenças de antialias são registradas. Cenas são compostas antes do corte. Soleiras de 18×18 mm ficam livres de mobiliário; vãos mecânicos continuam com 14 mm.

Correções: projeção e enquadramento de novas artes; fragmentos de atlas; duas sobreposições no mercado; carrinhos próximos de soleiras no posto/comuns; transparência vetorial em forms com recursos ausentes; miniaturas de preparação que carregavam resoluções desnecessárias e tinham números pequenos. Miniaturas agora usam somente ambiente A–C a 200 ppi, com D–E vetoriais e textos próprios. Mapas principais mantêm PNGs nativos sem exportação JPEG nem redução; mínimo físico {qa['main_map_minimum_ppi']} ppi. Textos do mapa são conferidos no recorte efetivo e na fonte global, sem atravessar emendas; texto invisível externo ao recorte de um form não é tratado como impresso.

Não se usa quantidade de testes como aprovação artística. A revisão é do autor. Sem impressão física, montagem física ou playtest humano. O ensaio de 30 bases usa 22×12 mm; não comprova 24 marcadores planos de 29×29 mm sem sobreposição. Esses marcadores e as bases não foram reduzidos. Não houve teste novo de equilíbrio/diversão.''')
section('PRINT_GUIDE.md','''## Atualização 0.6
Já tem a 0.5: baixe SOMENTE_MAPAS. Troque as quatro folhas comuns OU quatro folhas do destino escolhido. Diagramas novos são substitutos, podem ficar na tela. Cada mapa é A4 paisagem, uma face; 100%, sem ajustar; corte 277×190 mm e una sem sobreposição em 554×380 mm, M1/M2 acima, M3/M4 abaixo. Nenhuma face B. Cartas, calibração, peões, painel e abrigo da 0.5 continuam válidos. Kits completos conservam 58 duplex ou 72 manual; não misturar métodos. Miniaturas de guias não substituem os módulos na escala de jogo.''')
section('ART_DIRECTION.md','''## Tabuleiros 0.6
Composição global em A pisos/arquitetura, B mobiliário, C histórias de uso, D geometria congelada, E sinais e F corte. Pranchas originais revistas em projeção superior; gôndolas variadas, compra interrompida, manutenção e vida doméstica. Materiais de piso nativos e padrões contínuos globais, sem um quadro independente por zona. Estação é de tratamento de água. Comuns são acesso/salão/pátio de serviço genéricos, sem prometer seis arquiteturas detalhadas idênticas. Econômica omite material raster de fundo, mantém mobiliário e sinais em cinza. Não há promessa percentual de economia de cartucho.''')
section('CHANGELOG.md','''## 0.6 / tabuleiros
Sete cenas globais, duas edições, quatro módulos por mapa e seis diagramas. Arte nativa, circulação protegida, legendas vetoriais, miniaturas legíveis e pacote de atualização sem cartas. Corrigida aplicação dos bloqueios existentes aos módulos grandes. Demais componentes 0.5 copiados byte a byte; regras/campanha/dimensões/quantidades preservadas. Sem merge e sem apagar pacotes anteriores.''')
readme=P/'README.md';s=readme.read_text();intro='# Tabuleiros 0.6 / atualização sem reimprimir cartas\n\n[Downloads 0.6](DOWNLOADS_0.6.md): mapas avulsos para quem já tem a 0.5, kits completos de 58/72 folhas, duas edições, fontes e provas. Cartas, personagens, peões, painel e abrigo preservados. Imprima quatro módulos comuns OU quatro de um destino. [Relatório visual](VISUAL_QA.md).\n\n'
if not s.startswith('# Tabuleiros 0.6'):readme.write_text(intro+s)
print('Índices e inventário:',len(assets),'arquivos; mapas principais',qa['main_map_minimum_ppi'],'ppi.')
