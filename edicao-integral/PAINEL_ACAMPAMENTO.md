# Painel e tabuleiro do acampamento — especificação funcional (D-30)

Sem arte definitiva: dimensões, trilhas, marcadores e textos de regra. A
identidade visual será escolhida depois (pacote de transição, D-32). Os
números vêm de `data/community.json` (`camp`); se mudarem, o gerador
`tools/build_boards_integral.py` reconstrói os PDFs.

## 1. Tabuleiro do acampamento (A4 retrato)

| Item | Especificação |
|---|---|
| Grade | 4×4 lotes de 45 mm (180 × 180 mm), margem de 15 mm |
| Borda | fogueira e estoque inicial impressos fora da grade (não ocupam lote) |
| Símbolos por lote | 1–2 categorias: barraca, horta, água, estoque, oficina, defesa |
| Níveis | 1 = 2×2 (linhas e colunas 1–2); 2 = 3×3; 3 = 4×4. As faixas fechadas ficam cobertas por 2 tiras de "mato" (L), retiradas na expansão |
| Peças | construção 40 × 40 mm; barraca pequena 40 × 19 mm (2 por lote); barraca familiar e alojamento 40 × 40 mm |
| Obra em andamento | a peça entra virada (verso "em obra") com cubos de trabalho por cima |
| Horta plantada | peça de horta virada até o amanhecer em que fica pronta (3 amanheceres) |

Mapa de símbolos (linha × coluna):

| | c1 | c2 | c3 | c4 |
|---|---|---|---|---|
| r1 | barraca/horta | barraca/horta | horta/água | defesa/oficina |
| r2 | barraca | barraca/horta | barraca/estoque | horta/oficina |
| r3 | horta/água | oficina/estoque | barraca/horta | barraca/defesa |
| r4 | defesa/água | horta | barraca/oficina | horta/água |

## 2. Painel de recursos e condição (A4 paisagem)

Cada trilha tem um marcador de quantidade e, quando há limite, uma ficha de
**limite** colocada no número atual do nível (ex.: comida 24 → 36 → 48).

| Trilha | Faixa | Limite | Muda quando |
|---|---|---|---|
| Comida (porções) | 0–48 | 24 / +12 Depósito / +12 Depósito nível 2 | refeição, horta, viagens, buscas, ração de obra |
| Água | 0–36 | 24 / +12 Reservatório | refeição, horta em dia seco, chuva no coletor, viagens |
| Madeira | 0–20 | 20 | obras, lenha, ferver água, cozinhar sem cozinha |
| Metal (sucata) | 0–20 | 20 | obras, viagens às ruínas, buscas |
| Carne crua | 0–6 | 6 | caça e armadilha; estraga em 2 noites (5 com defumador) |
| Moradores / camas | 0–30, dois marcadores | — | chegada, resgate, barraca, alojamento |
| Crise | 0–10 | 10 = colapso | toda noite |
| Dia | 1–25 | — | amanhecer |

Remédio, munição, combustível, peças e conhecimento ficam como cartas.

### Faixas da Crise (texto impresso ao lado da trilha)

| Crise | Faixa | Efeito |
|---|---|---|
| 0 | calma | nenhum |
| 1–3 | leve | nenhum (aviso) |
| 4–6 | moderada | obras pesadas param (expansão, Depósito, Oficina, Enfermaria, Vigia, Reservatório, Alojamento) |
| 7–9 | grave | ninguém recupera Vida à noite; amanhecer: D6 ≤ 2, perde 1 madeira ou metal (briga) |
| 10 | colapso | derrota parcial (Evacuação) |

Toda noite: alguém sem porção → +1 (até metade dos humanos) ou +2 (mais que
isso); todos servidos → −1, ou −2 se o estoque ainda cobre outra noite; mais de
2 moradores sem cama → +1; recusar sobreviventes → +1.

## 3. Rotina do amanhecer na mesa (contagem de marcadores)

| Passo | Marcadores mexidos (acampamento típico, 10 moradores) |
|---|---|
| D6 do tempo (chuva 4–6): coletor | água (0–1) |
| Retorno de viagens | comida/madeira/água/carne (0–2) |
| Armadilhas | carne (0–1) |
| Designar trabalhos (peões nos lotes) | peões, sem trilha |
| Fim do dia: horta, obras, cozinha | comida, água, cubos de obra (2–3) |
| Refeição | comida e água (2) |
| Crise | 1 |
| **Total** | **6–10 movimentos** |
