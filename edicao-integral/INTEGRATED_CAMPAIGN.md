# Campanha contínua experimental

`IntegratedCampaign` é a fronteira operacional entre a caixa 0.2 e o motor
experimental. Ela não altera `RULES.md`, `CAMPAIGN.md`, `content/catalog.json`
ou os PDFs existentes.

## Fluxo

1. `new(seed, founders, links)` usa a preparação canônica de `Cistern02`.
2. Cada peça (`Conexões`, `Bomba`, `Membrana`) só é obtida por
   `collect_part(..., choice="search")`; a escolha é persistida e não pode ser
   repetida.
3. O relógio, refeições, reservas e trabalho continuam sendo validados por
   `Cistern02`. O filtro só é considerado concluído quando A/B/C realmente
   terminam.
4. `complete_cistern()` cria o `World` com os mesmos protagonistas, conserva
   recursos disponíveis dentro do depósito do motor e registra a recompensa uma
   única vez. A flag usada por `Arc2` não pode ser injetada pela API pública.
5. A Última Transmissão segue os portões existentes: rádio, cartão, acesso
   militar, transporte do transmissor e defesa. Vitória, derrota, retirada e
   impossibilidade são estados terminais persistentes.

## Limites conhecidos

O adaptador não reescreve as regras 0.2 de cercos, privação individual,
resgates e vínculos; essas regras seguem nos arquivos canônicos e ainda exigem
portabilidade específica antes de uma edição física final. A defesa e seus
mapas continuam conteúdo experimental, devendo receber playtest humano antes
de qualquer afirmação de equilíbrio ou prontidão de impressão.

O estado completo é salvo em JSON com schema próprio, incluindo o `World`, a
Cisterna, decisões, recompensas e motivo terminal. `load()` valida o estado
antes de permitir retomada.
