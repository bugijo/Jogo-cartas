# Checkpoint — 23/10/2026

Base preservada: `cebb76a` em `arte/kit-pos-apocaliptico-provas`. Nova branch: `evolucao/zona-zero-sistema-v1`. Branch padrão remota: `fisico/antes-que-a-agua-acabe`; nenhuma delas foi alterada por merge.

Estado: implementar e testar primeiro o núcleo determinístico independente. Fonte de dados em `data/core.json`, motor em `engine.py`, testes em `tests/`. A campanha, as habilidades individualizadas, os 15 NPCs completos, as 16 placas, os 12 interiores e a diagramação continuam pendentes. Não tratar as constantes desta pasta como regras aprovadas.

Próximo lote: revisar o design dos dez protagonistas e 15 NPCs com o proprietário após uma prova jogável; implementar cartas tipadas e validação de efeitos; conectar missões A Cisterna e Última Transmissão sem alterar a campanha 0.2. Só então construir a paginação A4.

## Unidade 2 — equipamento e espaço

Quatro instâncias-modelo de equipamento em `data/equipment.json`; bolsos, mãos, cabeça, tronco, pernas e grade de mochila testados. O motor impede sobreposição e uso sem mochila. O conteúdo continua experimental, sem cartas diagramadas ou distribuição de cópias. Oito testes próprios passaram; a suíte legada de 51 testes passou antes desta unidade (sem mudanças nos arquivos legados). Próximo passo: fechar regras de inventário e multiplicidade de cartas, antes da arte/impressão.

## Unidade 3 — catálogo e estado persistente

`data/system.json` é gerado de `data/build_system_data.py` e concentra 10 protagonistas com 70 habilidades tipadas, 15 NPCs nível 1–3, sete estruturas, cinco locais e cinco crises. `system.py` cobre capacidade de depósito e alojamento, recrutamento, projeto, trabalho, dano/reparo, busca com esgotamento, carga de expedição, viagens de equipes separadas, postos avançados, defesa com munição/visão, consumo/produção, crise com cooldown e salvamento com estado do PRNG. Dezoito testes novos passaram. Os textos de habilidade e custos ainda são hipótes de design da nova edição; nem cartas nem PDFs foram criados.

Lacunas da unidade: a maioria das tarefas de NPC sem saída de recurso ainda não possui efeito operacional; equipamentos de `engine.py` ainda não estão integrados ao estado de `system.py`; o gasto de PA/relógio tático, inimigos, eventos e campanha não estão implementados. A busca por localização é uma regra experimental que não modifica os seis mapas 0.2.
