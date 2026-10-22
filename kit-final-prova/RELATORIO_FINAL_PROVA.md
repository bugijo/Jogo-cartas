# Fechamento digital da seleção pós-apocalíptica

Esta é uma **prova de seleção**, preservada ao lado da edição 0.6. As 39 cartas restantes (lote 10) completam 114/114 IDs selecionados com arte revista. Os quatro módulos comuns (lote 11) completam sete alternativas de mapa: seis destinos temáticos e uma montagem comum reutilizável. Nenhuma regra ou texto de carta foi alterado nesses lotes.

## Verificação executada

- `python src/final_kit_audit.py`: PDFs selecionados presentes, A4, páginas esperadas e páginas pares nos duplex. Sete fontes de geometria comparadas à geometria canônica; 16 zonas, 21 conexões e cinco portas por mapa. Os comuns não trazem o bloqueio inicial específico do Mercado. Tamanho da arte comum 3817 × 2618 px em 554 × 380 mm = 175 ppi efetivos. Os seis destinos revisados também declaram 3817 × 2618 px / 175 ppi nos respectivos `VERIFICACOES.json`. As novas artes das cartas têm mínimo documentado de 349,2 ppi no lote 10. Números, portas e texto são vetoriais.
- `python src/render_final_qa.py`: 136 páginas dos PDFs selecionados, mapas e condicionais renderizadas em nove folhas de contato. Inspeção visual de contato: frentes e versos alternados; nenhum corte grosseiro ou página em branco inesperada; contraste das cartas e mapas preservado. Esse contato não resolve detalhes de impressão física nem alinhamento de impressora.
- `python src/validate.py`: IDs, recursos, conexões, cortes e duplex da fonte geral passaram. `python -m unittest discover -s tests -q`: 39 testes passaram. `python src/review_five_days.py`: uma trajetória legal de cinco dias com Lia/Ivo chegou ao filtro. Não é simulação de probabilidade.
- Preparo: 66, 220, 495, 792 e 924 combinações de vínculos de H=2–6, respectivamente; todas cabem nas barracas previstas. Solo usa H=2. O cálculo inicial de consumidores, cartas de quatro porções e `ceil(H/2)` foi executado por configuração. Os limites econômicos favoráveis de cinco dias em `src/validate.py` cobrem H=2–6, mas presumem entregas bem-sucedidas, sem resgate ou perdas.

## Pendências reais

1. Agora há 15 ensaios reprodutíveis de **fases** de cinco dias para H=2–6, com sementes, estoque, carga, resgate, cerco e filtro, em [CAMPANHA_REPLAY_RELATORIO.md](auditoria/CAMPANHA_REPLAY_RELATORIO.md). Esses ensaios não resolvem todos os PA, posições e efeitos de cartas. O roteiro tático herdado passa para H=2, mas bloqueia no Mercado/rodada 4 para H=3–6 com o número correto de inimigos iniciais. O kit não está validado como caixa final.
2. Para H=3–6, use os peões recortáveis de 24 heróis; os marcadores planos base incluem Lia/Ivo e os 12 resgatáveis, mas não os outros dez fundadores iniciais. A folha de peões de 24 imprime algumas figuras que talvez não entrem nesta partida. No campo Local dos registros, escreva ID/nome de heróis além de Lia/Ivo.
3. Os PDFs condicionais recortar/colar foram extraídos das páginas duplex correspondentes. Conferência de frente/verso por posição é digital; uma colagem precisa de miolo opaco. A impressão física, calibração de frente/verso e corte continuam pendentes.
4. Recursos adicionais podem ser anotados no registro numerado quando a reserva física se esgotar, conforme manual. Isso é um procedimento previsto; precisa de playtest com população alta para medir a frequência.
5. Nenhum playtest humano, impressão física ou avaliação de diversão/equilíbrio foi realizado nesta rodada.

O [índice de impressão](INDICE_IMPRESSAO_CONSOLIDADO.md) separa as duas alternativas e lista as substituições. As nove folhas de contato estão em `auditoria/CONTATO_FINAIS_01.jpg` a `_09.jpg`. Os PDFs de comparação antes/depois e fontes dos lotes 10 e 11 permanecem nas pastas respectivas.
