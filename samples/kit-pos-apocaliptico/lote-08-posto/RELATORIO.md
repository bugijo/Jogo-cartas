# Lote 08 — posto de combustível, prova artística

O posto da campanha (dia 4: van e combustível) foi recomposto como um pátio contínuo com bombas, quiosque, tanque, van e áreas de circulação. A arte anterior e o pacote distribuído continuam intactos. Esta pasta é uma **prova opcional de substituição das quatro folhas do posto**, não um novo kit completo.

- [Mapa para imprimir: quatro A4 paisagem](POSTO_4_A4.pdf), 100%, corte de 277 × 190 mm cada, junção de 554 × 380 mm. A ordem M1–M4 e o topo estão fora do corte.
- [Mapa remontado com geometria](POSTO_COM_GEOMETRIA.png) · [arte sem interface](POSTO_SEM_INTERFACE.png) · [comparação anterior → prova](COMPARACAO_B_ANTES_DEPOIS.jpg).
- [Prova de 100 mm em A4](DETALHE_100MM_A4.pdf) · [comparação do mesmo recorte em 100 mm](COMPARACAO_100MM_A4.pdf).
- [Contato das 21 conexões](provas/CONEXOES_21.jpg) · [quatro páginas](provas/CONTATO_4_A4.jpg) · [escala de cinza](provas/POSTO_CINZA.png) · [ocupação digital](provas/OCUPACAO_A4.pdf).

A geometria foi copiada da fonte `content/production/geometry_0.6.json`, ID ZC-MAP-0004: 16 zonas, 21 conexões, cinco portas, nenhum bloqueio inicial, entrada Z1, buscas Z5/Z12, objetivos Z7/Z14 e surgimento Z16. Limites e símbolos são vetoriais. As correções localizadas limparam entulho de Z7–Z11 e abriram os encontros da ilha ajardinada em Z9–Z13 e Z15–Z16. Não foram criadas barreiras ou regras.

Nove reconstruções artísticas nativas compõem 3817 × 2618 px a 554 × 380 mm: 175,0 × 175,0 ppi efetivos. Cada seção nativa usa ao menos 181,3 ppi em sua área impressa; três reparos nativos usam ao menos 271,3 ppi. A composição global pequena serviu somente de guia e não foi ampliada para impressão. Medidas individuais estão em `fontes/resolucao.json`.

As quatro páginas foram renderizadas e o contato, conexões, junção, cinza e recorte físico digital foram inspecionados. `VERIFICACOES.json` registra dimensões, geometria e fontes. A arte ainda tem discretas faces laterais estilizadas no quiosque e nos veículos; a luz é mais quente que no Mercado B. Também é possível notar pequena variação de textura nos trechos retocados em observação ampliada. Impressão física e playtest humano não ocorreram. Portanto, a prova ainda depende de avaliação e impressão antes de substituir a edição distribuída.

Para reconstruir: `python fontes/compose.py && python fontes/build.py && python fontes/diagnostics.py`, a partir da raiz desta pasta. Dependências já usadas pelo projeto: Pillow, NumPy, ReportLab e PyMuPDF. Fontes e imagens nativas estão em `fontes/` e `originais/`.
