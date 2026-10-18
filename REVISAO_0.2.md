# Revisão focada 0.2 — Duas Pessoas
18/10/2026
## Estado conferido antes da alteração
HEAD era db67f42, sem alterações rastreadas ou arquivos novos fora dos artefatos ignorados conhecidos. Não havia commit posterior. A tag preservado/prototipo-0.1-db67f42 fixa a base. PDFs e ZIP 0.1 permaneceram intactos; a nova geração fica em output/revisao-0.2 e o kit em output/comece-aqui-duas-pessoas. Não houve reinício nem alteração do jogo digital.

## Escopo desta rodada
Revisar cinco dias, fixar dez profissões e selecionar material existente para duas pessoas. Nenhum herói, missão, equipamento, baralho, ilustração ou destino foi acrescentado. Os 324 IDs de cartas e 24 IDs de heróis foram mantidos. O kit usa Lia/Ivo e famílias sorteadas, sem alterar as proporções dos montes. Referências e registros substituem componentes redundantes de consulta, não regras.

## Correções
1. Mercado: o bloqueio Z6–Z7 não pertencia às portas impressas e caía na emenda. Transferido a Z7–Z8, porta existente dentro de módulo; diagrama e catálogo atualizados.
2. Emboscada: a carta mandava usar Z4, que não faz parte de M1. Agora define área Z1/2/5/6, grupo Z1, inimigos/surgimento Z6, porta 1–5 comum fechada, pressão local 0 e uma rodada completa obrigatória. Usa o mesmo relógio; trecho já pago não é pago outra vez.
3. Inimigos: definido caminho por conectores incluindo portas, desempate e gasto da ativação para romper porta, sem atravessar instantaneamente. Sem trajeto possível, ficam parados.
4. Saída: conferida depois da ativação de inimigos/surgimentos; a rodada iniciada custa tempo. Busca limitada a uma por ponto/visita foi explicitada, sem renovar os três usos totais.
5. Lotes: regra padrão comida O1/água O2 quando o destino não especificar posição. Recompensas específicas de hospital/posto/condomínio continuam em O2 conforme texto. Proteção da primeira rodada do mercado só vale na primeira visita; marca pressão local 1.
6. Retirada: peças únicas Conexões, Bateria, Bomba e Membrana ficam registradas no chão da origem para recuperação, em vez de desaparecerem e travarem o filtro. Saque comum perdido não é reposto; não se duplica componente.
7. XP de objetivo: só na primeira conclusão de cada objetivo principal, não em visitas repetidas. Retorno normal continua dando um XP, máximo dois por dia.
8. Final do dia 5: filtro precisa estar ativo depois dos cercos pendentes. Segurança final mantém vigias do dia 5, sem novos trabalhos, refeição ou produção. Sem reparo extra fora do prazo.
9. Viagem Ferragens: distingue ida (chão Z1, coleta 1 PA) de volta (estoque ao chegar), uma unidade por ocorrência. Cão perdido paga seu consumo na refeição, sem custo de estrada implícito. Oportunista explicitamente rouba conserva, conforme manual.
10. Van: recuperação no posto usa Bateria e 2 PA+teste; não exige ponto civil adicional. Reparo posterior continua distinto.
11. Profissões: nove propostas mantidas e fixadas; Duda passa de estudante a técnica em eletrônica. As dez são decisões editoriais 0.2, com origem registrada. Não se atribui informação ausente ao PDF.

## Revisão dos cinco dias
Há replay executável em src/review_five_days.py e registro em output/revisao-0.2/replay_cinco_dias.json. Usa C=5 (Lia, Ivo, dois parceiros adultos e um cão), sem resgates, civis em recuperação, testes com rolagens 3 e ordem legal conhecida de Horda/Viagem. Não altera os montes do kit: os jogadores os embaralham normalmente.

| Dia | Procedimento verificado | Tempo/obra | Comida/água após refeição |
|---|---|---|---|
| 1 | Mercado: dois lotes comida, um água, excesso carregado em duas mochilas via chão | 5 rodadas + 2 viagem = 7 | 23 / 15 |
| 2 | Oficina: Conexões, Bateria, um lote de cada | 6 rodadas + 2 viagem = 8 | 26 / 18 |
| 3 | Estação: Bomba, Membrana, um lote água; teste passa; cerco 4 com cão e uma munição | 7 rodadas + 2 viagem = 9; fadiga 1, Viagem extra | 21 / 21 |
| 4 | Heróis ficam; reservam A+B, gastam dois Materiais e dois trabalhos. Descanso remove fadiga noturna | duas etapas, teto 2/dia | 16 / 16 |
| 5 | Reservam C, gastam Material+Membrana e dois trabalhos; enchem 10 água. Cerco de pressão Força4 com última munição | filtro 4/4 e ativo | 11 / 21 |

Horda utilizada: quatro Arrastar, dois Aglomerado e dois Corrida, sem exceder a composição original; Peso morto fica no monte. Ferragens no retorno do dia 3 acrescenta um Material, portanto sobra um Material após pagar três pelo filtro. Portão, Saúde e Moral seguem ativos/positivos. O roteiro respeita quatro cargas por herói, portas, PA, rodadas, dano, surgimento e janela de retorno. Aos 3 XP podem escolher Lia/Rede e Ivo/Alerta, sem alterar as ações dessa trajetória. Aos 6 XP as escolhas ficam registradas, sem novo combate nesse exemplo.

Também foi preservada a preparação por sorteio: 66 pares físicos de Vínculo para dois fundadores, C de 2 a 5. O replay não demonstra vitória para todos os sorteios. Emboscadas, falhas, cercos mais fortes ou resgates podem exigir mudar a rota ou causar derrota; o kit inclui os procedimentos e componentes para resolver esses casos.

## Conferência de impressão
Quantidade definitiva por arquivo no manifesto do kit. Cartas mantêm 63×88 mm, 9 por A4, 2 mm entre elas e verso com colunas refletidas. Intenções têm verso comum e exigem envelopes/sleeves opacos. Os dois pés de cabra são representados nas fichas com seus IDs originais e local atual; não há carta duplicada deles no kit. As 62 cartas iniciais incluem o monte completo de cada família aleatória necessária. Os PDFs 0.1 não devem ser misturados.

Verificações automáticas, contagens, renderização de páginas e capturas acompanham o kit. Não houve impressão física ou playtest humano nesta rodada. Revisão lógica e trajetória determinística não comprovam equilíbrio ou diversão.

## Resultado desta rodada
Kit inicial: 25 folhas, 62 cartas, duas fichas e 45 marcadores; guia de seis páginas com sequência do primeiro dia. Complemento: 33 folhas, 52 cartas restantes selecionadas, 12 fichas resgatáveis, demais montagens e referências; total 58 folhas sem repetir os montes comuns. O kit tem 72 páginas PDF em 18 arquivos, além de registros de conferência não destinados à impressão.

Quatorze testes de regressão passaram, além de 46 verificações específicas do kit. As 72 páginas foram renderizadas e conferidas por contatos e amostras ampliadas. O ZIP 0.1 preservou seu SHA-256 original. A inspeção corrigiu uma folha órfã do guia, a sobreposição do filtro com a grade de terrenos, caracteres de separação no registro dos pés de cabra e etiquetas para os seis descartes regionais. Não foram produzidos heróis, cartas, missões ou artes novos.

Na seleção para duas pessoas, a expressão metade do grupo arredondada para cima foi calculada como um nas cartas de Horda/Viagem, mantendo os mesmos IDs, quantidades e efeitos. Isso elimina notação de programação da leitura inicial.
