# Entrega atual — Comece Aqui / Duas Pessoas, edição 0.2

[Abra o índice do kit](output/comece-aqui-duas-pessoas/LEIA-ME.md): 25 folhas para começar o dia 1; 33 de complemento; 58 no capítulo completo. [Guia inicial PDF](output/comece-aqui-duas-pessoas/01_inicial/01_comece_aqui.pdf). [Correções e revisão dos cinco dias](REVISAO_0.2.md). [Profissões consolidadas](PROFISSOES.md).

O estado de partida era db67f42, sem alterações posteriores. A base está na tag preservado/prototipo-0.1-db67f42. A revisão continua o mesmo projeto, com os mesmos IDs e arte; novos PDFs estão em subpastas próprias. Não misture versões.

---

## Registro preservado da entrega 0.1

Os links e números abaixo documentam o pacote anterior. Para imprimir agora, use o índice 0.2 acima.

# Sobreviventes — Zona Zero: Comunidade
## Antes que a água acabe • protótipo físico 0.1
Jogo cooperativo sem narrador para 1–6 participantes; solo controla dois heróis. Este pacote contém regras e componentes para testar os cinco dias. Não é uma caixa final validada: não houve impressão física nem playtest humano. Mapas usam planta funcional comum; ambientação final e algumas ilustrações de peças continuam pendentes.

## Comece aqui — sem programar
1. Leia [guia de impressão](PRINT_GUIDE.md) e imprima [calibração](output/10_calibracao_duplex.pdf) primeiro.
2. Abra [manual para iniciantes](output/01_manual_iniciantes.pdf) e [campanha](output/02_campanha.pdf). As regras desta edição são completas; não use o manual 1.0.
3. Escolha cartas completas OU alternativa econômica; imprima demais componentes e separe os baralhos. Providencie três dados d6, lápis, tesoura e envelopes/sleeves opacos.

## PDFs separados
| Arquivo | Páginas | Folhas / regime |
|---|---:|---|
| [Capa](output/00_capa.pdf) | 1 | 1, uma face, opcional |
| [Manual](output/01_manual_iniciantes.pdf) | 8 | 8, uma face |
| [Campanha](output/02_campanha.pdf) | 3 | 3, uma face |
| [324 cartas completas](output/03_cartas_duplex.pdf) | 72 | 36 duplex, borda longa |
| [168 cartas econômicas](output/03b_cartas_sem_recursos_duplex.pdf) | 38 | 19 duplex; substitui o anterior |
| [24 fichas](output/04_fichas_personagens.pdf) | 12 | 12, uma face |
| [Abrigo, mapa geral e registros](output/05_paineis_registros.pdf) | 5 | 5 paisagem, uma face |
| [Quatro módulos locais](output/06_mapas_modulos.pdf) | 4 | 4 paisagem, corte e união |
| [Seis montagens](output/07_montagens_destinos.pdf) | 6 | 6 paisagem, referência |
| [198 marcadores](output/08_marcadores.pdf) | 5 | 5, uma face |
| [Divisórias e bases](output/09_organizacao.pdf) | 5 | 5, uma face |
| [Calibração](output/10_calibracao_duplex.pdf) | 2 | 1 duplex, borda longa |
| [Galeria de arte](output/11_galeria_arte.pdf) | 4 | 4, opcional |

Total completo: 90 folhas incluindo capa, galeria e calibração, sem alternativa 03b. Econômico: 68, trocando 03 por 03b e omitindo capa/galeria. Fotocópias extras de registros não estão nessa conta. Manual/campanha podem ficar na tela para economizar mais 11 folhas.

## Conteúdo real e fontes
324 cartas, 24 fichas de heróis com retratos e tokens, 198 marcadores totais, quatro módulos reutilizáveis e seis diagramas, cinco painéis/registros e divisórias. [Catálogo](CONTENT_CATALOG.md) detalha quantidades. [JSON](content/catalog.json) traz IDs, custos, recursos, heróis, tokens e mapas. [Manifesto de arte](ASSET_MANIFEST.md) registra 55 ilustrações em sete arquivos PNG, regiões e hashes.

O PDF fonte principal foi lido integralmente e está em sources/. O ZIP antigo não foi fornecido e não foi misturado. Dez profissões não constam da fonte; propostas estão marcadas no catálogo e fichas. As outras 14 seguem o documento. Alterações e justificativas em GAME_DESIGN.md.

## Capturas e verificação
[Mapa montado](output/previews/mapa_montado.png), [ficha](output/previews/04_fichas_personagens_001.png), [folha com maior texto](output/previews/03_cartas_duplex_067.png), [versos mistos](output/previews/03_cartas_duplex_004.png), [visão geral](output/previews/contact_05.jpg). Todas as páginas foram renderizadas; contatos e capturas estão em output/previews/. Resultados automáticos em output/validation.json; relatório em VALIDATION_REPORT.md; plano de teste humano em PLAYTEST_PLAN.md.

## Regenerar — para manutenção
Python 3.12, dependências em requirements.txt; fontes DejaVu Sans e Bold nos caminhos definidos em src/build.py. Sem chaves, serviços pagos ou código do jogo digital.

    python src/make_content.py
    python src/document_assets.py
    python src/build.py
    python -m unittest discover -s tests -v
    python src/validate.py
    python src/render.py

Edite o conteúdo central em src/make_content.py para persistir após regeneração; content/catalog.json é a forma estruturada gerada. Regras e campanha são Markdown editável. Não edite PDF à mão. A arte já está incluída e não precisa ser gerada novamente. Mapas derivam do catálogo; map_layouts.json é uma exportação de consulta.

## Continuidade
Branch fisico/antes-que-a-agua-acabe. Commits locais, sem push. CHECKPOINT.md orienta retomada. O ZIP inclui um bundle Git para restaurar o histórico, além das fontes e arquivos finais. Nenhum trabalho continua em segundo plano após a entrega.
