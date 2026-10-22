# H6 e Bia — pergunta dirigida de playtest

Esta análise compara **a mesma trajetória fixa** de Mercado → Oficina → Estação, com os mesmos dados, entregas, carta de Viagem noturna, cerco e intenção Solidário já registrados em [ROTEIROS_TATICOS_H2_H6.json](../auditoria/ROTEIROS_TATICOS_H2_H6.json). H6 começa com seis fundadores, um adulto parceiro e um cão: oito consumidores, 12 vagas humanas, quatro cartas cheias iniciais de Conserva e quatro de Água. Bia chega no dia 2, passa duas noites em observação e aumenta o consumo para nove a partir da refeição desse dia. Não foi criada carta ou recurso novo.

| Escolha e pressuposto | D1 | D2 | D3 | D4 | D5 | Consequência nessa trajetória |
|---|---:|---:|---:|---:|---:|---|
| Não acolher Bia; sem coleta | 24 | 24 | 16 | 8 | 0 | Quinta refeição completa; zero sobra depois. |
| Acolher Bia; sem coleta | 24 | 23 | 14 | 5 | **−4** | Faltam quatro porções na quinta refeição. O número negativo representa déficit, não estoque físico negativo. |
| Acolher Bia; coletar 2 comida no dia 4 e 2 no dia 5 | 24 | 23 | 14 | 7 | **0** | Quinta refeição completa, com margem zero. Água após a quinta refeição: 11 porções. |

A terceira opção é permitida por **RULES.md §4**: cada adulto alocado à Coleta de emergência gera uma porção escolhida, limite comunitário de duas por dia. São quatro **porções**, não quatro cartas. Em ambos os dias o grupo fica no abrigo, como na trajetória fixa. No planejamento dos dias 4 e 5, Mara e Nara fazem os dois trabalhos do filtro; Bento e o adulto parceiro coletam uma comida cada. No dia 5, Lia, Ivo e Caio são os três vigias do cerco de Pressão. São sete adultos distintos, todos fundadores ou parceiro confiável; Bia não precisa trabalhar. O filtro mantém os quatro trabalhos A/B/C e as peças/material já pagos. A ação de vigiar usa trabalho, conforme §4; nenhum adulto recebe dois.

O cálculo independente em [H6_BIA_SALDOS.json](H6_BIA_SALDOS.json) aplica entregas, refeições, coleta e enchimento do filtro por dia; [fonte reproduzível](../../src/audit_h6_bia_playtest.py). O saldo de água no caminho com Bia e coleta de comida é 16 / 15 / 13 / 4 / 11. Isso comprova **uma solução de estoque e trabalho sob as condições favoráveis do roteiro**, não a chance de conseguir a mesma trajetória com outros dados, cartas, danos ou decisões. O déficit sem coleta não prova que toda partida H6 com Bia perde.

Perguntas à mesa: os jogadores perceberam a possibilidade de coleta? O custo de dois trabalhadores nos dias 4 e 5 pareceu uma decisão interessante ou uma obrigação escondida? Conseguiram acompanhar que porções coletadas não são cartas cheias? Registrar antes de considerar qualquer ajuste de equilíbrio. **Nenhuma mudança mecânica foi aplicada.**
