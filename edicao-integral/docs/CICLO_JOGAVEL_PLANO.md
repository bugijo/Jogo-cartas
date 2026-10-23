# Ciclo jogável experimental — plano de implementação

Objetivo: executar preparação, viagem, mapa, combate, busca, retorno, fase diária, salvamento/restauração, sem tocar no kit 0.2.

Decisão: congelar a geometria do Mercado antigo como cenário de teste; adicionar dados novos e tipados de inimigos, portas, encontros e objetivos nesta edição. O módulo tático opera sobre `World`, cuja serialização já inclui estado do PRNG. Os efeitos da campanha serão dados separados com condições verificáveis. Isto é um protótipo de regras, não conversão silenciosa do manual canônico.

- [x] Geometria, inimigos, portas e hordas em JSON; conferência contra catálogo original.
- [x] Encontro persistente: movimento, porta, alcance/visão, ataque, ruído, ativação e surgimento.
- [ ] Eventos e objetivos estruturados que liguem busca e combate ao retorno.
- [ ] Replay completo determinístico para equipes e estratégias, com salvamento no meio.
- [ ] Testes novos, suíte legada, relatório, checkpoint e commits progressivos.

Bloqueadores previstos: habilidades existentes têm tipos genéricos sem efeitos para todas as operações; nova campanha e impressão 20 × 20 cm não estão definidas. Não atribuir taxa de vitória às simulações até modelar todos os eventos e decisões.
