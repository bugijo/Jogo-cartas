# Última Transmissão — estado experimental

O capítulo oficial “Antes que a água acabe” permanece em `CAMPAIGN.md` e não foi convertido nem alterado. A evolução experimental registra a conclusão dele apenas por `world.flags['cistern_complete']`; **não existe importação automática ou validação do capítulo antigo**.

Cinco cartas de missão estão em `data/last_transmission.json`. Quatro portões são executáveis em `arc2.py`:

1. Decifrar a frequência no abrigo exige capítulo anterior registrado e duas pistas, que são consumidas.
2. Obter o cartão exige chegar à Estação e usar ao menos uma busca.
3. Autorizar acesso à instalação exige código, cartão, furgão e combustível de ida e volta (seis unidades para distância longa); abre a expedição.
4. Levar o transmissor exige chegada à instalação e uma vaga de carga; a peça única acompanha a equipe e entra no registro do abrigo ao retornar. Salvamento e restauração mantêm flags, carga e estoque especial.

A quinta carta, defesa da última transmissão, **não é executável**. Falta planta funcional do perímetro, surgimento, alcance/linha de visão, condição de defesa final e ligação segura ao modo sobrevivência livre. `Arc2.final_defense()` falha explicitamente. A instalação militar é um destino regional abstrato, sem mapa local ou PDF. Por isso o arco não é campanha jogável completa.

As escolhas e custos são hipóteses novas da edição experimental, não regras retroativas do kit 0.2. O teste de duas equipes impede duplicação do transmissor. Não há impressão ou playtest deste arco.
