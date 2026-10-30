# Crescimento do acampamento regional — economia de materiais (2026-10-30)

Fase 7. Estado do motor e propostas para decisão. Nada aqui é regra aprovada.

## O que o acampamento pode construir (dados atuais, `data/system.json`)

| Estrutura | Custo | Trabalho | Efeito |
|---|---|---|---|
| EXP-BLD-01 Horta | 2 madeira + 1 sucata | 2 | 2 comida/dia a partir de 4 dias, sem trabalhador |
| EXP-BLD-02 Oficina | 2 madeira + 3 sucata | 3 | reparos |
| EXP-BLD-03 Enfermaria | 2 madeira + 2 sucata + 1 remédio | 3 | cura |
| EXP-BLD-04 Vigia | 2 madeira + 2 sucata | 2 | defesa |
| EXP-BLD-05 Depósito | 3 madeira + 2 sucata | 3 | +12 de depósito |
| EXP-BLD-06 Reservatório | 2 madeira + 3 sucata | 3 | água |
| EXP-BLD-07 Alojamento | 4 madeira + 2 sucata | 3 | +4 camas |

Tudo junto: 17 madeira e 15 sucata. Só heróis trabalham obras (`work_project`).
Uma estrutura de cada tipo; terreno base 7 (cada uma ocupa 2).

## Fontes atuais

| Recurso | Fonte com mapa tático | Total por campanha |
|---|---|---|
| Madeira | nenhuma | 0 |
| Sucata | Oficina (3 buscas × 2), Estação (2 × 1) | 8 |
| Sementes | acolhimento no Condomínio (Cisterna) | 1, se a migração não for recusada |

Resultado medido: 0 construções em todas as variantes sem madeira.

## Propostas de madeira (para decisão)

| Id | Fonte | Custo e risco | Limite | Observação |
|---|---|---|---|---|
| W1 | Posto (EXP-LOC-07, médio, mapa `gas_station_02`): paletes e caixotes, 1 madeira por busca | viagem média (cartas de Viagem, Emboscada), Horda do mapa | 8 buscas urbanas, sem reposição | hoje o Posto só tem retirada tática de combustível por PA; precisa de regra para a busca de madeira |
| W2 | Desmonte no entorno: 1 trabalho do amanhecer → 1 madeira | o trabalho do dia (sem recuperação §25, sem coleta) | reserva finita de 12 por abrigo | **medido** (só em memória): habilita Horta e Depósito |
| W3 | Materiais da Cisterna (hoje arquivados na migração) viram 1 madeira ou 1 sucata cada | nenhum novo; limite da carga da Evacuação | o que o grupo trouxe | usa recurso real que hoje some |
| W4 | Horta abandonada (EXP-LOC-01, perto, renovação natural) ganha mapa: cercas (madeira) e comida | viagem curta, encontro do mapa | buscas do local | exige conteúdo novo (mapa tático) |
| W5 | Custo alternativo: 2 sucata no lugar de 1 madeira | sucata é finita (8) | 4 madeira equivalentes por campanha | não cria recurso, só troca |

Recomendação para testar primeiro: W3 + W2 (crescimento gradual com o que o
grupo carregou e com trabalho, sem fonte infinita), depois W1 quando houver
regra de busca no Posto.

## Medido com W2 (ciclos 12–13, `ECONOMY_EXPERIMENTS.md`)

- 1–30: 22 Hortas EXP-BLD-01 e 2 Depósitos em 37 campanhas; 5/37 sobrevivem
  (ALL sem obras: 3/37). Primeiras sobrevivências de H3 e H4 em 1–30.
- 31–90: 42 Hortas e 1 Depósito em 107; 12/107 sobrevivem (ALL sem obras: 18/107).
- O investimento custa a comida de agora: as obras entram nos dias em que os
  heróis coletariam e a Horta só produz 4 dias depois. Sem folga na chegada, a
  obra chega tarde.

## Caminho de crescimento gradual (proposta de projeto)

1. Dias 1–3: estabilizar (F, G, coleta), Oficina para sucata.
2. Dias 3–6: Horta EXP-BLD-01 e Horta §61 (D) com Sementes.
3. Dias 6–10: Depósito (+12) e Vigia; Enfermaria se houver remédio.
4. Dias 10–15: Alojamento (+4 camas) para acolher contatos; Oficina e
   Reservatório.

Para isso funcionar, falta decidir: fonte de madeira (W1–W5), a recusa de
camas na migração (`HORTA_CONTINUITY.md`) e a folga da chegada (G hoje cobre
uma noite).
