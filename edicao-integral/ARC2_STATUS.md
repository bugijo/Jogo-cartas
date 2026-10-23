# Última Transmissão — estado experimental

O capítulo oficial “Antes que a água acabe” permanece em `CAMPAIGN.md` e não foi convertido nem alterado. A evolução experimental ainda registra sua conclusão por `world.flags['cistern_complete']`; não há ponte verificada com o capítulo antigo.

As cinco cartas em `data/last_transmission.json` alimentam os portões de código de rádio, cartão, instalação e transporte, além da defesa final. A viagem militar exige furgão e combustível de ida e volta. O transmissor é peça única e persiste no transporte e no estoque do abrigo.

A defesa final experimental usa `camp_final`, mapa funcional linear de quatro zonas independente da geometria do kit 0.2. Ela exige os quatro portões narrativos e o transmissor no abrigo. Três ondas constam do catálogo. Heróis podem se mover e atacar com equipamentos existentes; inimigos avançam, ferem heróis na zona do objetivo e reduzem sua integridade. Eliminar a terceira onda marca vitória e desbloqueia a flag de sobrevivência livre; integridade zero ou equipe incapacitada marca derrota; retirada marca encerramento parcial. Estado, posições, ferimentos, equipamento e RNG são salvos por `World.save`.

**Limites:** o mapa militar local ainda não existe. A defesa não modela munição à distância nem obstáculos/linha de visão complexa, pois os equipamentos estruturados disponíveis são de combate corpo a corpo. A Cisterna 0.2 ainda não foi integrada. A vitória automatizada não foi demonstrada numa partida tática legal; os testes de progressão isolam o encerramento das ondas. Não há PDF, impressão ou playtest deste arco. Custos e ondas são hipóteses da edição experimental, sem efeito retroativo no kit 0.2.
