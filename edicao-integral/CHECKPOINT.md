# Checkpoint — 23/10/2026

Base preservada: `cebb76a` em `arte/kit-pos-apocaliptico-provas`. Nova branch: `evolucao/zona-zero-sistema-v1`. Branch padrão remota: `fisico/antes-que-a-agua-acabe`; nenhuma delas foi alterada por merge.

Estado: implementar e testar primeiro o núcleo determinístico independente. Fonte de dados em `data/core.json`, motor em `engine.py`, testes em `tests/`. A campanha, as habilidades individualizadas, os 15 NPCs completos, as 16 placas, os 12 interiores e a diagramação continuam pendentes. Não tratar as constantes desta pasta como regras aprovadas.

Próximo lote: revisar o design dos dez protagonistas e 15 NPCs com o proprietário após uma prova jogável; implementar cartas tipadas e validação de efeitos; conectar missões A Cisterna e Última Transmissão sem alterar a campanha 0.2. Só então construir a paginação A4.

## Unidade 2 — equipamento e espaço

Quatro instâncias-modelo de equipamento em `data/equipment.json`; bolsos, mãos, cabeça, tronco, pernas e grade de mochila testados. O motor impede sobreposição e uso sem mochila. O conteúdo continua experimental, sem cartas diagramadas ou distribuição de cópias. Oito testes próprios passaram; a suíte legada de 51 testes passou antes desta unidade (sem mudanças nos arquivos legados). Próximo passo: fechar regras de inventário e multiplicidade de cartas, antes da arte/impressão.

## Unidade 3 — catálogo e estado persistente

`data/system.json` é gerado de `data/build_system_data.py` e concentra 10 protagonistas com 70 habilidades tipadas, 15 NPCs nível 1–3, sete estruturas, cinco locais e cinco crises. `system.py` cobre capacidade de depósito e alojamento, recrutamento, projeto, trabalho, dano/reparo, busca com esgotamento, carga de expedição, viagens de equipes separadas, postos avançados, defesa com munição/visão, consumo/produção, crise com cooldown e salvamento com estado do PRNG. Dezoito testes novos passaram. Os textos de habilidade e custos ainda são hipótes de design da nova edição; nem cartas nem PDFs foram criados.

Lacunas da unidade: a maioria das tarefas de NPC sem saída de recurso ainda não possui efeito operacional; equipamentos de `engine.py` ainda não estão integrados ao estado de `system.py`; o gasto de PA/relógio tático, inimigos, eventos e campanha não estão implementados. A busca por localização é uma regra experimental que não modifica os seis mapas 0.2.

## Unidade 4 — integração e ensaio

Instâncias múltiplas de equipamento agora entram no `World` e no salvamento; mochila, slots e colisões são validados ao carregar. Recrutamento exige vaga e porções para a próxima refeição. Busca depende da expedição presente, carga tem limite de seis unidades por herói e só chega ao estoque no retorno. Postos avançados precisam de local esgotado, recursos e responsável. O ensaio `simulate_system.py` roda cinco dias para 2–6 heróis e grava resultado reproduzível em `ENSAIO_SISTEMA_20261023.json`; tabela e limites em `VALIDATION.md`. A preparação inicial H6 do ensaio excedia 30 unidades de armazenamento por uma unidade; reduzi materiais do **cenário de ensaio**, sem alterar capacidade/regra. Vinte e três testes próprios e 51 testes legados passaram. O bônus inicial de construção de Bento foi ligado a projetos; os demais bônus tipados ainda exigem integração.

Retomar por `python -m unittest discover -s edicao-integral/tests -q` e `python edicao-integral/simulate_system.py --seed 20261023 --seeds 100`. Não chamar esta evolução de edição jogável: faltam ações táticas, cartas/eventos, veículos, segundo arco, arte e impressão.
