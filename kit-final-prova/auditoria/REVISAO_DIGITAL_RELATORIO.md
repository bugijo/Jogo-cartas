# Revisão digital final — evidência e limites

Base conferida: branch `arte/kit-pos-apocaliptico-provas`, commit inicial `f02de295e0704fb6b68458002fff2c118baef288`, igual ao remoto no começo desta revisão. Regras e campanha canônicas: [RULES.md](../../RULES.md) e [CAMPAIGN.md](../../CAMPAIGN.md). Nenhuma mecânica ou PDF artístico aprovado foi alterado.

## Preparação e trajetórias

Um cálculo independente percorreu todas as **2.497** combinações sem reposição dos 12 Vínculos para H=2–6 (66, 220, 495, 792, 924). Solo repete H2. Em cada combinação conferiu humanos contra 8/10/12 vagas, cães fora das vagas, consumidores C, cartas iniciais `ceil(2C/4)` de cada provisão, sobra máxima de três porções, lote `ceil(C/4)`, barracas e Errantes iniciais. Todas couberam e a folha condicional comporta até seis Pés de cabra. Os casos e intervalos estão em [REVISAO_DIGITAL_FINAL.json](REVISAO_DIGITAL_FINAL.json).

As cinco trajetórias táticas fixas de `f02de29` foram preservadas. Recalculei os saldos de comida e água dos cinco dias diretamente das entregas e refeições registradas, sem chamar o código `Replay`: H2 7/16, H3 7/16, H4 7/16, H5 2/13, H6 0/15. H6 tem **zero comida depois de alimentar todos**. Uma segunda escolha legal foi executada em cada tamanho de grupo: deixar Bia no destino em H2–5 mantém quatro porções adicionais ao fim, e os quatro roteiros terminam; acolhê-la em H6, mantendo a mesma rota e sem coleta de emergência, bloqueia a quinta refeição com déficit de quatro porções. Isso demonstra consequência da escolha, não inevitabilidade da derrota. Ver [roteiros alternativos](ROTEIROS_ALTERNATIVOS_BIA_H2_H6.json).

O replay espacial exercita PA, portas, movimento, ataque próximo, IA e surgimentos, carga, busca escolhida, resgate de Bia, viagem noturna, dois cercos e obras A/B/C. **Não exercita todos os valores de dados, armas de tiro/ruído, cada carta de Viagem/Busca/Encontro/Cerco, todos os resgates, ferimentos persistentes em outros heróis, veículos ou retirada de emergência.** Logo não é uma partida automatizada geral.

## Ensaios com sementes: 150 por H, 750 no total

Foram repetidos os três perfis anteriores com 50 sementes cada: favorável, difícil e limite. O perfil define decisões, incluindo resgates, e a semente define vínculos, intenções, cercos e dados amostrados. As sementes completas, recursos por noite, resgates, esgotamentos e sinalizadores estão no JSON. Intervalos de Wilson 95% abaixo expressam apenas variação de sementes **dentro deste modelo e desta mistura arbitrária de perfis**; não estimam a taxa real de vitória do jogo.

| H | Modelo: plano possível / 150 | Intervalo do modelo | Falta na 5ª refeição | Incapacitação amostrada | Comida média ao fim dos dias 1–5 |
|---:|---:|---:|---:|---:|---|
| 2 | 38 | 0,190–0,328 | 111 | 9 | 15,36 / 15,13 / 8,81 / 3,11 / 0,65 |
| 3 | 46 | 0,238–0,385 | 95 | 18 | 21,26 / 21,01 / 13,42 / 5,87 / 2,24 |
| 4 | 83 | 0,473–0,631 | 49 | 27 | 26,39 / 26,81 / 17,97 / 8,99 / 1,77 |
| 5 | 52 | 0,275–0,426 | 83 | 32 | 30,95 / 30,73 / 20,09 / 9,31 / 1,71 |
| 6 | 88 | 0,507–0,662 | 48 | 23 | 37,87 / 38,29 / 25,89 / 13,33 / 2,10 |

O modelo de fases não resolve posições, PA, cargas efetivamente recolhidas nem todos os efeitos das cartas. Há ainda duas divergências que impedem interpretar seus rótulos de “derrota” como regra literal: ele reduz Saúde da comunidade por escassez em dias posteriores, enquanto RULES §8 aplica ferimento a pessoas após noites consecutivas e colapso só no limiar descrito; e trata incapacitação em um confronto amostrado como bloqueio geral, enquanto a regra permite transporte/retirada com consequências. Esses resultados são **triagem de risco**, principalmente da margem de comida, e não prova de equilíbrio. Não foi feita mudança mecânica para favorecer vitórias. Proposta para decisão futura: testar em mesa se a quinta refeição aperta excessivamente grupos H2/H5; nenhum custo, porção ou probabilidade foi alterado.

## Impressão e componentes

O auditor percorreu os PDFs selecionados, condicionais e sete mapas: A4 exato, número de páginas, texto dentro da página, fontes realmente usadas incorporadas, páginas pares de duplex e geometria JSON sem diferença nas zonas/conexões/portas/bloqueios. Uma falha foi corrigida: os cabeçalhos das folhas condicionais usavam Helvetica sem incorporação; agora usam a fonte DejaVu incorporada. Os textos extraídos antes/depois são idênticos, e os PDFs manuais foram reconstruídos exatamente das páginas duplex corrigidas. Um recurso Helvetica não usado ainda consta internamente nos PDFs de ReportLab, mas nenhuma palavra depende dele. A soma independente das páginas selecionadas é **58 folhas duplex** ou **72 de recortar/colar** para solo/dupla; substituições e condicionais somam **67/83** para H3–6. Os 114 IDs e os versos preservados foram conferidos no lote 10; as verificações já publicadas medem arte nova das cartas com mínimo 349,2 ppi e mapas principais com 175 ppi. Isso não significa 300 ppi em toda arte anterior. Os PDFs incluem instrução de virada longa no retrato; mapas são A4 paisagem de uma face. O encaixe lógico e as fontes de geometria foram conferidos; deslocamento da impressora ainda é desconhecido.

As **136 páginas selecionadas** foram renderizadas nas nove [folhas de contato](CONTATO_FINAIS_01.jpg). A [carta mais densa da seleção](CARTA_DENSA_100_PCT_2X.png) foi conferida ampliada; a [página 1 do mercado em cinza](MERCADO_CINZA_PAGINA_1.png) manteve labels e passagens discerníveis na imagem digital. Contato geral não certifica leitura em papel; a prova física segue necessária. A nova [calibração](../playtest/CALIBRACAO_FRENTE_VERSO_A4.pdf) tem régua vetorial de 100 mm e alvos assimétricos frente/verso, opcional e fora das 58/72 folhas. A folha não mede sozinha o desvio real da impressora.

O índice manda imprimir componentes condicionais de H3–6 como **substituições**, não duplicações. As alternativas temáticas dos mapas substituem as quatro folhas comuns por sessão. Dados, tesoura, lápis e envelopes/sleeves opacos são externos. Nenhum esgotamento de componente foi registrado nos 750 ensaios de fases; esses ensaios não representam picos simultâneos de inimigos. RULES §6 determina token numerado antes do limite de 24 e expedição perdida no 25º; §7 manda registrar ficha numerada de mesmo valor se faltar carta física, sem criar recursos.

## Estado

O kit está **preparado para um playtest humano exploratório**, com [roteiro e registro diário](../playtest/ROTEIRO_E_REGISTRO_PLAYTEST.pdf). A [matriz de cobertura](COVERAGE_MATRIX.csv) mantém 5 linhas CAMPANHA_H* como PARTIAL e 206 tokens/painéis antigos como NEEDS_REVIEW visual; os 114 IDs de cartas e sete mapas selecionados estão presentes. A revisão digital permanece **parcial** quanto a todas as cartas/decisões e probabilidades táticas. Impressão, alinhamento duplex, corte, montagem e playtest humano não ocorreram. O relatório anterior `CAMPANHA_REPLAY_RELATORIO.md` mantém as 15 sementes e o roteiro herdado por histórico; este documento e o JSON novo descrevem a cobertura atual.
