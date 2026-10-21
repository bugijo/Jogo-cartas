# Lote 10 — 39 cartas restantes

Ilustrações originais foram integradas às cartas VIN (12), VIA (12), HOR (9) e CER (6) da seleção de 114 cartas. A arte segue os materiais gastos, iluminação e cores do Mercado B e do condomínio. Personagens, textos, IDs, atributos e verso ficaram como no lote 07. A edição distribuída anterior foi preservada.

- [Prova das 39 cartas, duplex](pdfs/PROVA_39_CARTAS_DUPLEX.pdf): cinco folhas A4, frente e verso em borda longa, apenas para avaliação; não acrescentar ao kit de 114 cartas.
- PDFs de distribuição atualizados: [kit inicial](pdfs/02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf) e [complemento](pdfs/02_CARTAS_DUPLEX/KIT_COMPLEMENTO_2_DUPLEX.pdf). Alternativa de recortar e colar na pasta `pdfs/03_CARTAS_RECORTAR_E_COLAR/`.
- Comparações extraídas dos PDFs finais: [vínculos](provas/COMPARACAO_VIN.jpg), [viagens](provas/COMPARACAO_VIA.jpg), [hordas](provas/COMPARACAO_HOR.jpg), [cercos](provas/COMPARACAO_CER.jpg). [Contato de todas as frentes](provas/CONTATO_FRENTES.jpg).

O gerador parte dos componentes artísticos já aprovados nos lotes anteriores e altera somente a ilustração dos 39 IDs. `VERIFICACOES.json` confirma 114 IDs únicos selecionados, 39 IDs alterados neste lote, texto pesquisável idêntico ao lote 07 em todos os PDFs equivalentes, versos duplex pixel a pixel iguais, A4 e fontes incorporadas. `fontes/resolucao.json` registra cada corte, área impressa e ppi efetivo; mínimo **349,2 ppi** para as novas ilustrações. Não houve ampliação artificial.

As 13 páginas de frente dos dois PDFs duplex foram renderizadas e inspecionadas como contato. As cartas densas mantêm menos área de arte para conservar o texto em 9,5 pt. Os versos secretos não receberam diferenciação individual. A prova de 39 cartas é um artefato de revisão e duplica os mesmos IDs; não deve ser impressa junto aos PDFs de distribuição.

Limites: pequenas cenas de perigo ficam reduzidas nas cartas de cercos mais densas; uma prova em impressora doméstica ainda precisa confirmar leitura e alinhamento real. O teste digital de duplex não substitui a impressão física. Nenhum playtest humano foi realizado.

Reconstrução: `python samples/kit-pos-apocaliptico/lote-10-cartas-restantes/fontes/build.py` a partir da raiz do repositório.
