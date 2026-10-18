"""Inventário e notas 0.5 gerados das medições efetivas dos PDFs."""
from pathlib import Path
import json,csv,hashlib
from PIL import Image
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-acabamento-v0.5'
qa=json.loads((O/'verificacao.json').read_text());usage=json.loads((O/'resolucao_pdfs.json').read_text());maps=[r for r in usage if r['file'].endswith('_M01_M04_LADO_A.pdf')];minimum=min(r['effective_ppi'] for r in maps)
assets=[]
for f in sorted((P/'assets/v0.5').glob('*.png')):
 im=Image.open(f);assets.append(dict(file=str(f.relative_to(P)),origin='geração integrada de imagem original',pixels=list(im.size),integrated=f.name!='pecas.png',destination='rascunho substituído' if f.name=='pecas.png' else 'mobiliário de mapa' if f.name.startswith('mapa_') else 'cartas',sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
for f in sorted((P/'assets/v0.5/vetores').glob('*.svgz')):assets.append(dict(file=str(f.relative_to(P)),origin='vetores originais + imagens nativas exportados do PDF final',integrated=True,destination='fonte editável do mapa',pixels=None))
summary=dict(version='0.5',assets=assets,map_minimum_ppi=minimum,architecture='vetorial original em escala física',native_resize=False,ppi_method='pixels nativos divididos pelo tamanho impresso em polegadas, usando a transformação real do XObject no PDF; alfa altera enquadramento, não densidade',missing_assets=[],remaining_limitations='Artes antigas de cartas/rostos preservados podem ficar abaixo de 300 ppi. Todas as ocorrências estão na planilha por PDF/página/xref. Sem impressão física/playtest humano.')
(P/'content/production/assets_0.5.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(O/'resolucao.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
with (O/'RESOLUCAO_EFETIVA.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['PDF','pagina','xref','pixels_x','pixels_y','ppi_efetivo','situacao'])
 for r in usage:w.writerow([r['file'],r['page'],r['xref'],*r['pixels'],r['effective_ppi'],r['status']])
base='https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/'
blob='https://github.com/bugijo/Jogo-cartas/blob/arte/pnp-acabamento-v0-5/'
text='# Zona Zero / acabamento 0.5 — baixar e imprimir\n\nEscolha UMA edição e UM método. As mesmas 114 cartas, regras 0.2, personagens e campanha permanecem. A4 exato, 100%, sem ajustar. Extraia e abra `00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html`.\n\n| Pacote completo | Folhas | ZIP |\n|---|---:|---|\n'
for ed in ['ILUSTRADA','ECONOMICA']:
 for method,count in [('DUPLEX','25 + 33 = 58'),('MANUAL','33 + 39 = 72')]:text+=f'| {ed.title()} / {method.lower()} | {count} | [Baixar]({base}dist/ZZ_05_{ed}_{method}_COMPLETO.zip) |\n'
text+='\nDuplex: somente cartas/calibração em retrato, borda longa; versos já espelhados. Outros PDFs uma face. Manual: tudo uma face, frente + miolo opaco + verso, topos iguais; remover códigos fora do corte. Não imprimir alternativas juntas.\n\nPara imprimir só o dia 1, escolha INICIAL e depois o COMPLEMENTO correspondente, em lugar do completo:\n\n'
for ed in ['ILUSTRADA','ECONOMICA']:text+=f'- {ed.title()}: [Inicial, 25 folhas]({base}dist/ZZ_05_{ed}_DUPLEX_INICIAL.zip) e [complemento, 33]({base}dist/ZZ_05_{ed}_DUPLEX_COMPLEMENTO.zip).\n'
text+='\nExtras opcionais: painel de duas folhas por jogador (4 para duas pessoas), peões 8 folhas, guia 3, bases 1, variantes 4 por destino substituindo as quatro comuns, todas as fichas 12. Nenhuma capacidade/ID foi acrescentada; máximo 24 inimigos.\n\n'
for ed in ['ILUSTRADA','ECONOMICA']:text+=f'- [Extras {ed.lower()}]({base}dist/ZZ_05_{ed}_EXTRAS_OPCIONAIS.zip)\n'
text+='\n[PDFs e índice ilustrado]('+blob+'output/edicao-acabamento-v0.5/ilustrada/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md) • [PDFs econômicos]('+blob+'output/edicao-acabamento-v0.5/economica/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md) • [Comparações reais e resolução]('+base+'dist/ZZ_05_PROVAS_E_RESOLUCAO.zip)\n\n'
text+=f'Mapas: arquitetura e pisos vetoriais, com mobiliário bitmap original medido em **pelo menos {minimum} ppi efetivos** nos módulos finais. Não é ampliação dos mapas 0.4. [CSV de todas as imagens]({base}output/edicao-acabamento-v0.5/RESOLUCAO_EFETIVA.csv). Artes antigas de cartas/rostos podem ficar abaixo de 300 ppi; exceções identificadas por PDF, página e imagem.\n\nFontes completas: clone a branch ou extraia TODAS as oito partes abaixo no mesmo diretório. PNGs nativos, SVGZ, código, catálogo e PDFs-base estão incluídos. Não imprimir estas partes.\n\n'
for part in ['CODIGO','ARTES_NOVAS','VETORES','ARTES_BASE04','PDF_BASE03_ILUSTRADA','PDF_BASE03_ECONOMICA','MANIFESTOS_BASE','PDF_BASE04']:text+=f'- [Fontes / {part}]({base}dist/ZZ_05_FONTES_{part}.zip)\n'
text+='\nPython 3 + requirements.txt + DejaVu Sans. Execute `python src/build_finish.py --step all`, `python src/validate_finish.py`, `python src/proof_finish.py`, `python src/document_finish.py` e `python src/package_finish.py`. [Relatório visual](VISUAL_QA.md) e [checkpoint](CHECKPOINT.md). Sem impressão física ou playtest humano. Edições anteriores preservadas.\n'
(P/'DOWNLOADS_0.5.md').write_text(text)
for ed in ['ilustrada','economica']:
 folder=O/ed/'10_VERIFICACOES';folder.mkdir(exist_ok=True)
 for name in ['verificacao.json','resolucao_pdfs.json','RESOLUCAO_EFETIVA.csv']:(folder/name).write_bytes((O/name).read_bytes())
print('Inventário:',len(assets),'assets; mínimo nos mapas:',minimum,'ppi;',qa['passed'],'verificações.')
