# Zona Zero / acabamento 0.5 — baixar e imprimir

Escolha UMA edição e UM método. As mesmas 114 cartas, regras 0.2, personagens e campanha permanecem. A4 exato, 100%, sem ajustar. Extraia e abra `00_LEIA_PRIMEIRO/ABRA_ESTE_PACOTE.html`.

| Pacote completo | Folhas | ZIP |
|---|---:|---|
| Ilustrada / duplex | 25 + 33 = 58 | [Baixar](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ILUSTRADA_DUPLEX_COMPLETO.zip) |
| Ilustrada / manual | 33 + 39 = 72 | [Baixar](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ILUSTRADA_MANUAL_COMPLETO.zip) |
| Economica / duplex | 25 + 33 = 58 | [Baixar](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ECONOMICA_DUPLEX_COMPLETO.zip) |
| Economica / manual | 33 + 39 = 72 | [Baixar](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ECONOMICA_MANUAL_COMPLETO.zip) |

Duplex: somente cartas/calibração em retrato, borda longa; versos já espelhados. Outros PDFs uma face. Manual: tudo uma face, frente + miolo opaco + verso, topos iguais; remover códigos fora do corte. Não imprimir alternativas juntas.

Para imprimir só o dia 1, escolha INICIAL e depois o COMPLEMENTO correspondente, em lugar do completo:

- Ilustrada: [Inicial, 25 folhas](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ILUSTRADA_DUPLEX_INICIAL.zip) e [complemento, 33](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ILUSTRADA_DUPLEX_COMPLEMENTO.zip).
- Economica: [Inicial, 25 folhas](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ECONOMICA_DUPLEX_INICIAL.zip) e [complemento, 33](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ECONOMICA_DUPLEX_COMPLEMENTO.zip).

Extras opcionais: painel de duas folhas por jogador (4 para duas pessoas), peões 8 folhas, guia 3, bases 1, variantes 4 por destino substituindo as quatro comuns, todas as fichas 12. Nenhuma capacidade/ID foi acrescentada; máximo 24 inimigos.

- [Extras ilustrada](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ILUSTRADA_EXTRAS_OPCIONAIS.zip)
- [Extras economica](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_ECONOMICA_EXTRAS_OPCIONAIS.zip)

[PDFs e índice ilustrado](https://github.com/bugijo/Jogo-cartas/blob/arte/pnp-acabamento-v0-5/output/edicao-acabamento-v0.5/ilustrada/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md) • [PDFs econômicos](https://github.com/bugijo/Jogo-cartas/blob/arte/pnp-acabamento-v0-5/output/edicao-acabamento-v0.5/economica/00_LEIA_PRIMEIRO/IMPRIMA_ESTES.md) • [Comparações reais e resolução](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_PROVAS_E_RESOLUCAO.zip)

Mapas: arquitetura e pisos vetoriais, com mobiliário bitmap original medido em **pelo menos 211.3 ppi efetivos** nos módulos finais. Não é ampliação dos mapas 0.4. [CSV de todas as imagens](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/output/edicao-acabamento-v0.5/RESOLUCAO_EFETIVA.csv). Artes antigas de cartas/rostos podem ficar abaixo de 300 ppi; exceções identificadas por PDF, página e imagem.

Fontes completas: clone a branch ou extraia TODAS as oito partes abaixo no mesmo diretório. PNGs nativos, SVGZ, código, catálogo e PDFs-base estão incluídos. Não imprimir estas partes.

- [Fontes / CODIGO](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_CODIGO.zip)
- [Fontes / ARTES_NOVAS](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_ARTES_NOVAS.zip)
- [Fontes / VETORES](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_VETORES.zip)
- [Fontes / ARTES_BASE04](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_ARTES_BASE04.zip)
- [Fontes / PDF_BASE03_ILUSTRADA](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_PDF_BASE03_ILUSTRADA.zip)
- [Fontes / PDF_BASE03_ECONOMICA](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_PDF_BASE03_ECONOMICA.zip)
- [Fontes / MANIFESTOS_BASE](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_MANIFESTOS_BASE.zip)
- [Fontes / PDF_BASE04](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/pnp-acabamento-v0-5/dist/ZZ_05_FONTES_PDF_BASE04.zip)

Python 3 + requirements.txt + DejaVu Sans. Execute `python src/build_finish.py --step all`, `python src/validate_finish.py`, `python src/proof_finish.py`, `python src/document_finish.py` e `python src/package_finish.py`. [Relatório visual](VISUAL_QA.md) e [checkpoint](CHECKPOINT.md). Sem impressão física ou playtest humano. Edições anteriores preservadas.
