# Revisão posterior das provas

[Estado atual dos lotes 02–04](LOTES_02_04.md). A sobreposição de cadeiras da antiga prova hospitalar foi eliminada na nova composição contínua. Hospital e oficina agora têm nove seções nativas cada. Os defeitos descritos abaixo pertencem às provas históricas preservadas.

---

# Relatório visual e de impressão

## Resultado real

Quatro lotes iniciais materializados em PDFs, seguidos de um lote do hospital. Seis retratos receberam desgaste; duas artes de suprimentos aparecem na folha de nove cartas; oficina e hospital receberam edições localizadas de mobiliário. Os inimigos são uma prova de **arte preservada**, não geração nova. Não se alterou o kit distribuído.

**Direção artística:** remendos, recipientes usados, compartimentos saqueados, vidro trincado, papel rasgado e sangue seco pontual aproximam os materiais do Mercado B aprovado. Roupa característica, cabelo, pele e fisionomia dos seis personagens continuam reconhecíveis na comparação. Persistem pequenas variações de traço gerado; não se afirma identidade pixel a pixel. Não há mãos novas nos retratos.

**Limitação central:** oficina e hospital ainda usam composições anteriores com objetos isolados. A edição localizada melhora materiais, mas não alcança a continuidade arquitetônica do Mercado B. O hospital mantém cadeiras vetoriais sobre a ilustração da recepção e camas esquemáticas; defeitos preexistentes, visíveis na prova antes/depois. Não aprovar os cenários como acabamento final nem propagar esse resultado como padrão concluído.

## Correções realizadas

1. Removido fragmento de outro objeto no recorte de água com nova edição isolada; tampa e corpo inteiros na carta final.
2. Primeira edição do hospital rejeitada: alfa mínimo 218, fundo opaco. Segunda edição tem alfa zero fora dos objetos; incorporada após conferência.
3. Datas variáveis dos canvases controladas no gerador para reconstrução estável.
4. Recortes e posições físicas da oficina/hospital preservados; desgaste não ampliou os retângulos ocupados.

## Verificações executadas

- 39 testes existentes aprovados (`fontes/testes_existentes.log`); não significam aprovação artística.
- Regras, campanha, catálogo, guia inicial, cenas e geometria canônica comparados byte a byte com `48f5794`.
- Textos pesquisáveis de todas as seis fichas e nove cartas iguais aos anteriores, incluindo habilidades, valores e IDs.
- Página inteira dos versos idêntica na renderização; colunas continuam refletidas para borda longa. Nenhum ID individual acrescentado ao verso secreto.
- Geometria e textos extraídos dos dois mapas iguais aos PDFs de referência. Todas as 21 conexões de cada mapa renderizadas em folhas de inspeção; nenhum objeto novo sobre os conectores. Mercado/Z15–Z16 não editado.
- Cada mapa: quatro A4 paisagem, corte 277 × 190 mm, montagem 554 × 380 mm. Remontagem digital conferida a 72 ppi; diferença média por canal abaixo de 1/255, decorrente de rasterização nas transformações. A 36 ppi a oficina apresentou 1,35/255; não foi usado esse diagnóstico reduzido como prova de desalinhamento físico.
- Renderizadas todas as páginas novas e suas referências, sem erro do renderizador. Contato geral, mapas montados, conexões, fichas, cartas densas, versos, cinza e recortes de 100 mm inspecionados.
- Fontes DejaVu utilizadas nos textos incorporadas. Texto e símbolos permanecem vetoriais.

## Resolução efetiva dos PDFs

| PDF | Menor ppi raster medido |
|---|---:|
| Folha de seis retratos ampliados | 161,49 |
| Seis fichas compactas | 221,71 |
| Folha de inimigos ampliados | 170,71 |
| Nove cartas | 249,24 |
| Oficina | 216,75 |
| Hospital | 215,00 |
| Comparações físicas | 215,00 |

As folhas de exposição ampliam as figuras e têm menor densidade que os componentes. Não são retratos a 300 ppi. Os recortes novos de oficina atingem 310,44 ppi ou mais nos usos registrados; o mínimo do mapa vem de fontes preservadas. Água isolada tem densidade maior, mas isso não aumenta a resolução dos outros itens. Nenhuma interpolação foi apresentada como detalhe novo.

## Não verificado / pendências

Sem impressão física, corte real, montagem real, teste de alinhamento da impressora ou playtest humano. A nitidez final depende da impressão. Faltam os outros 18 retratos, desgaste dos peões, demais cenários e componentes ilustrados. A carta Solidário ainda usa abrigo claro; não foi modificada silenciosamente nem contada como arte nova. Os mapas precisam de trabalho de composição contínua além destas edições de material.

Próximo lote recomendado: corrigir a composição do hospital (primeiro a sobreposição decorativa da recepção) e preparar condomínio com áreas vazias de saque, tecidos gastos e vegetação sem manutenção; manter as fontes funcionais congeladas. Depois, os próximos seis retratos e peões correspondentes.
