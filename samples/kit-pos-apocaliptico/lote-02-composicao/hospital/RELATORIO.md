# Hospital — composição contínua, lote 02

Base preservada: 46263b2. Referência de atmosfera: Mercado B pós-apocalíptico, 48f5794. Esta pasta é uma prova independente e não substitui a edição distribuída.

## Produção real

Arte nova pelo image_gen integrado: composição global, nove reconstruções nativas coordenadas e reparo integral do balcão da recepção. A imagem global de 1514 × 1039 serviu apenas como guia. A saída composta tem 3817 × 2618 pixels em 554 × 380 mm: 175,00 × 174,99 ppi. Fontes das seções: 183,33–195,16 ppi; reparo da recepção: aproximadamente 270 ppi. Todas foram reduzidas para composição, nunca ampliadas para alegar detalhe novo. Dimensões e áreas individuais em fontes/resolucao.json.

O cenário agora compartilha piso, iluminação e circulação. Cadeiras foram separadas do balcão. Duas macas decorativas foram removidas para liberar conectores. As três divisórias permanentes são vetoriais, nas posições canônicas, sem deixar o gerador definir regras.

## Arquivos

- HOSPITAL_4_A4.pdf: quatro folhas paisagem, uma face, 100%, corte 277 × 190 mm. M1/M2 acima; M3/M4 abaixo. Unir sem sobreposição.
- DETALHE_100MM_A4.pdf: detalhe em escala física.
- COMPARACAO_B_ANTES_DEPOIS.jpg: comparação extraída dos PDFs anterior e novo.
- HOSPITAL_COM_GEOMETRIA.png e HOSPITAL_SEM_INTERFACE.png: renders dos PDFs.
- provas/CONEXOES_21.jpg: inspeção dos 21 conectores.
- fontes/build.py e compose.py: geração reproduzível; executar compose.py e depois build.py.

## Verificação e limites

Geometria JSON igual ao hospital canônico: 16 zonas, 21 conexões, cinco portas, bloqueio 7–8, entradas, buscas e objetivos preservados. Quatro páginas A4 exatas, fontes incorporadas, mesma imagem e transformações físicas nos quatro recortes. Todas as páginas renderizadas. Revisão visual da montagem e dos 21 conectores: passagens livres; armários próximos de 4–8 e 11–12 exigem atenção na colocação das peças. Móveis continuam decorativos.

A arte tem faces laterais estilizadas residuais nos armários e pequenas diferenças de rejunte nas junções artísticas. Não é ortografia arquitetônica perfeita. A densidade de 175 ppi acompanha o Mercado aprovado, mas é inferior à densidade dos pequenos sprites da prova anterior (~215 ppi). O ganho é composição e detalhe ambiental contínuo, não aumento numérico de ppi em relação àqueles sprites.

Não houve impressão física nem playtest. Oficina, outros destinos, cartas, retratos restantes e peões ainda são lotes independentes; esta prova não encerra o kit.
