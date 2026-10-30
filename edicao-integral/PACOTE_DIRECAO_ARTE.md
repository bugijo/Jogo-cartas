# Pacote de transição para direção artística — Sobreviventes: Zona Zero

Para o proprietário e o ChatGPT compararem quatro propostas de arte
conceitual. Nada aqui é arte final: são mecânicas estáveis, quantidades e
restrições. Números e ids vêm de `data/` e de `data/print_inventory.json`
(gerado pelo `tools/card_inventory.py`); se um número divergir, vale o arquivo.

## 1. Identidade temática e ambientação

- Jogo físico cooperativo de sobrevivência zumbi, 2–6 heróis, campanha longa.
- Tom: sobrevivência comunitária, cotidiano de acampamento, escassez com
  esperança; violência existe mas não é o centro.
- Lugar: interior do Sudeste brasileiro, meses depois do colapso. Mata
  Atlântica degradada, rio, plantações abandonadas, cidade pequena com mercado,
  oficina, hospital, estação, posto e uma instalação militar. Clima com chuva
  frequente (o D6 do tempo chove em metade dos dias).
- Fauna e flora coerentes (para ilustrar caça, pesca e coleta): capivara,
  tatu, cutia, paca, jacu; lambari, traíra, tilápia de açude; goiaba, banana,
  manga, jabuticaba, mandioca, milho, abóbora e feijão nas hortas.
- Referências de experiência (não de imagem): Dead of Winter, This War of
  Mine, Last Day on Earth, Project Zomboid, Zombicide. A identidade deve ser
  original.

## 2. História e campanhas

1. **A Cisterna** (kit 0.2, certificado): o grupo defende um abrigo urbano
   até consertar a cisterna e o filtro; termina na evacuação.
2. **Última Transmissão** (edição integral): a comunidade chega a uma
   clareira fora da cidade, monta o acampamento em lotes, produz comida,
   acolhe famílias e segue pistas de uma transmissão de rádio. Rádio →
   cartão de acesso → bateria da Oficina → van do Posto → combustível →
   Instalação militar (transmissor) → defesa final do acampamento.
   Prazo: depois do dia 25 a frequência cala.

## 3. Personagens

| Grupo | Quantidade | Onde está | O que ilustrar |
|---|---|---|---|
| Heróis jogáveis | 24 no catálogo da Cisterna (12 iniciais, 12 desbloqueáveis); 10 deles no motor regional (Lia, Ivo, Mara, Caio, Nara, Bento, Duda, Rosa, Joel, Yumi) | `content/catalog.json#heroes`, `data/system.json#heroes` | retrato, ficha com Vida 3, ações, perícias |
| Especialistas nomeados | 15 (Téo, Célia, Aline, Samuel, Bruna, Raul, Denise, Hugo, Sol, Otávio, Jana, Miguel, Bia, Vicente, Lúcia) | `data/system.json#npcs` | retrato e ofício |
| Sobreviventes comuns | adultos, crianças, cães (sem nome fixo) | migração e chegadas | 6–8 silhuetas genéricas reutilizáveis |
| Profissões | 9 (caçador, agricultor, coletor, cozinheiro, carpinteiro, mecânico, enfermeiro, guarda, comum) em 12 cartas | `data/community.json#profession_deck` | ícone + ferramenta do ofício |

## 4. Inimigos

| Id | Tipo | Ilustrar |
|---|---|---|
| slow | lento (o comum) | 3–4 variações de figura |
| runner | corredor | 1–2 variações |
| brute | brutamontes | 1 figura |
| hordas | cartas de Horda da Cisterna (9) e ondas da defesa final | cena de grupo |

## 5. Locais e ambientes

| Id | Local | Mapa tático |
|---|---|---|
| EXP-LOC-01 | Horta abandonada | `garden_edge_01` (4×4 zonas) |
| EXP-LOC-02 | Mercado | `market_intro` |
| EXP-LOC-03 | Oficina | `workshop_02` |
| EXP-LOC-04 | Hospital | `hospital_02` |
| EXP-LOC-05 | Estação | `station_02` |
| EXP-LOC-06 | Instalação militar | `military_installation` |
| EXP-LOC-07 | Posto | `gas_station_02` |
| — | Condomínio, acampamento final | `condominium_02`, `camp_final` |
| — | Entorno (floresta, rio, ruínas) | `print/tabuleiro_entorno.pdf` |

## 6. Estruturas e construções (peças de lote)

Barraca (2 lugares), barraca familiar, Alojamento (e nível 2), lote de horta,
coletor de chuva, Reservatório, Depósito (e nível 2), Oficina, Enfermaria,
Ambulatório, Vigia, Cozinha (na fogueira), composteira, defumador, bancada,
filtro de areia; tiras de mato que cobrem os lotes ainda fechados. Cada peça
precisa de frente "pronta" e verso "em obra".

## 7. Componentes e quantidades (técnico)

| Família | Quantidade | Fonte |
|---|---|---|
| Cartas da Cisterna 0.2 | 324 | `content/catalog.json` (certificado, reaproveitar ids) |
| Acontecimentos de viagem | 12 | `event_deck` |
| Profissões | 12 | `profession_deck` |
| Estruturas regionais (cartas de referência de obra) | 22 | estruturas do sistema + Comunidade |
| Locais regionais | 7 | `locations` |
| Crises regionais | 5 | `crises` |
| Última Transmissão (cartas de enredo) | 5 | `last_transmission.json` |
| Referência da comunidade | 8 | bagagem, viagem, comida e água, tempo, chegadas, horta, Crise, obras |
| Conhecimento | 5 (K-AGR, K-CON, K-FER, K-SAU, K-AGU) | `camp.knowledge` |
| Peças de lote | ver `tokens_new` no inventário (barraca 16, horta 12, familiar 4, demais 1) | `print_inventory.json` |
| Tabuleiros | painel do acampamento (2 folhas A4), tabuleiro de lotes (A4 retrato), entorno, 9 mapas táticos | `print/` |
| Marcadores | trilhas (8), limite (2), Crise (1), cubos de obra (6), peões (12), viajantes (6), armadilhas (2) | inventário |

Lista por identificador: `INVENTARIO_DIRECAO_ARTE.md` (heróis, sobreviventes,
inimigos, cartas por família e nome, peças e mapas; gerado por
`tools/art_inventory.py`) e `data/print_inventory.json`.

## 8. Elementos visuais a representar

- Ícones de categoria de lote: barraca, horta, água, estoque, oficina, defesa.
- Recursos: porção de comida, água, madeira, metal, carne crua, remédio,
  munição, combustível, peça (bateria, cartão, transmissor).
- Estados: ferido (Vida), faminto, sedento, fadiga, sem cama.
- Tempo: chuva / seco (D6), dia 1–25.
- Faixas da Crise: calma, leve, moderada, grave, colapso.

## 9. Formatos físicos

- Cartas 63 × 88 mm, 9 por A4 retrato, vãos de 2 mm, frente e verso com
  virada pela borda longa (`PRINT_PREP.md`).
- Tabuleiro de lotes: 4×4 lotes de 45 mm (A4 retrato).
- Painel: 2 folhas A4 paisagem.
- Peças de lote 40 × 40 mm; barraca pequena 40 × 19 mm.
- Mapas táticos: metades de 100 × 200 mm por A4 quando a placa não cabe.

## 10. Restrições práticas de impressão

- Impressora doméstica: margem segura ≥ 8 mm, nada essencial a menos de 3 mm
  do corte; legível em preto e branco (cor como reforço, não como única pista).
- Textos de regra em ≥ 6,5 pt; números de trilha ≥ 5,5 pt.
- Fundo claro nas peças que recebem marcador por cima.

## 11. Decisões visuais em aberto

1. Estilo de ilustração (realista, gravura, quadrinho, pintura).
2. Paleta e como diferenciar recursos sem depender de cor.
3. Iconografia das categorias de lote.
4. Nome comercial definitivo das cartas (ids ficam).
5. Arte da caixa e logotipo.
6. Quanto mostrar de violência.
7. Retratos únicos para os 15 especialistas ou silhuetas.

## 12. O que já está validado e o que não está

- Validado por testes automatizados e simulação: regras do motor, economia,
  acampamento em lotes, Crise, tamanhos 2–6 (ver `COMUNIDADE_BALANCEAMENTO.md`):
  sobrevivência de 15 dias 72–78%, vitória em 25 dias 37%, nenhum tamanho
  abaixo de 25% de vitória (1–30) nem de 60% de sobrevivência (31–90).
- Não validado: playtest com pessoas (D-13), legibilidade das peças na mesa,
  tempo real de partida.
