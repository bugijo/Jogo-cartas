# Itens adicionais — prova pós-apocalíptica

[Prova de oito itens em duplex](pdfs/PROVA_8_ITENS_DUPLEX.pdf) e [comparação da frente, extraída dos PDFs](provas/COMPARACAO_ITENS_1.jpg). As duas [pranchas nativas](originais/) e o [gerador editável](fontes/build.py) estão nesta pasta. A arte foi criada com o gerador de imagens integrado; títulos, números, efeitos e molduras foram compostos pelo gerador de PDF.

Quatro cenas representam Material, Munição, Medicamento e Carne. A segunda prancha representa Lanterna, Kit de instalação médica, Bancada e Van de manutenção. Estas cenas substituem a arte de **29 IDs** das 114 cartas selecionadas. Os 38 IDs do lote 04 continuam com suas cenas novas: total acumulado de **67/114 IDs** com mudança artística. Os outros 47 conservam a arte existente; isso não implica que estejam aprovados visualmente. Não foram criadas cartas ou regras. O combustível aparece apenas como arte na prancha antiga, sem carta nova.

## Imprimir

- [Duplex inicial](pdfs/02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf): 7 folhas A4 retrato, virada longa.
- [Duplex complemento](pdfs/02_CARTAS_DUPLEX/KIT_COMPLEMENTO_2_DUPLEX.pdf): 6 folhas A4 retrato, virada longa.
- Alternativa [recortar e colar](pdfs/03_CARTAS_RECORTAR_E_COLAR/): frentes e versos separados, 26 folhas A4 de uma face, substitui os 13 duplex. Não imprimir os dois métodos juntos.
- A prova de oito itens é opcional, uma folha duplex adicional apenas se quiser avaliar antes de imprimir o kit.

As cartas mantêm 63 × 88 mm. O gerador preserva exatamente os 114 IDs, textos e quantidade por PDF; verificou as páginas A4 e os versos duplex contra o lote 04. As novas imagens ocupam áreas de impressão com pelo menos **351,37 ppi efetivos**, calculados com pixels usados e milímetros impressos em `fontes/resolucao.json`. Todos os PDFs foram renderizados; [contato de todas as páginas duplex](provas/CONTATO_DUPLEX.jpg). A imagem da van permanece pequena por causa da regra densa na própria carta. As imagens têm fundo contextual, então não se trata de recorte transparente do objeto; essa apresentação foi inspecionada na folha final.

`fontes/build.py` cria temporariamente `antes/` para verificar textos e versos, usando a arte publicada no lote 04. `antes/` é uma saída reproduzível e não integra esta entrega. Comparações feitas com esses PDFs foram conservadas. Não houve impressão física, medição de frente/verso em impressora, nem playtest.
