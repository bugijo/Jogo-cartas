# Auditoria de base e separação de edições

Repositório conferido em `cebb76a` antes de abrir esta branch; árvore limpa e remoto da branch iguais. A branch padrão remota é `fisico/antes-que-a-agua-acabe`. A edição 0.2 possui 24 heróis, 324 registros de cartas, seis destinos e quatro módulos de 277 × 190 mm, conforme `content/catalog.json`; o índice seleciona 58 folhas duplex para a primeira partida. O capítulo canônico é “Antes que a água acabe”. Os testes e PDFs existentes permanecem preservados.

O pedido desta evolução especifica dez protagonistas, quinze NPCs, seis atributos, placas 200 × 200 mm e dois arcos. Isso diverge materialmente do kit 0.2 (24 heróis, três atributos e outra escala de mapas). Portanto a evolução fica em pasta própria e não altera `RULES.md`, `CAMPAIGN.md`, `content/catalog.json` nem PDFs distribuídos. O novo catálogo é um protótipo de dados, não uma conversão automática das 324 cartas.

Inventário de produção: **10 perfis-base de protagonistas** (IDs, nomes e profissões preservados; atributos e árvores ainda ausentes), **0 fichas completas de NPC**, **0 cartas novas**, **0 placas 200 × 200 mm**, **0 interiores**, **0 missões novas**, **0 PDFs novos**. Os 14 outros heróis e os seis destinos da edição 0.2 continuam disponíveis em seus arquivos originais, mas não contam como componentes produzidos da edição integral. A meta de ~415 cartas não é uma contagem atingida.

O motor atual cobre somente combate probabilístico elementar, rolagem de infecção, XP, capacidade de alojamento, produção/consumo ilustrativos e salvamento JSON. Não cobre três ações no mapa, horda, ruído, portas, durabilidade, inventário espacial, viagem, combustível, busca, eventos, crise, fabricação, postos avançados ou os dois arcos. As mil iterações de `simulate.py` são ensaios desse subconjunto, não partidas completas.

Hipóteses a confirmar antes de uso como regra: rendimento diário da horta após a primeira colheita; custo de dois materiais da horta; definição de dano da armadura por acerto; consequências de déficit alimentar; atributos e árvores individuais; estrutura da campanha “Última Transmissão”. Esses valores não devem migrar silenciosamente ao manual.
