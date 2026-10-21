# Estação de tratamento: lote adicional

Nove seções nativas, nove reparos e composto 3817 × 2618 px em 554 × 380 mm; resolução e origem por arquivo em [fontes/resolucao.json](samples/kit-pos-apocaliptico/lote-05-estacao/fontes/resolucao.json). Arte integrada ao [PDF de quatro A4](samples/kit-pos-apocaliptico/lote-05-estacao/ESTACAO_4_A4.pdf), sem substituir o mapa distribuído.

---

# Assets dos lotes pós-apocalípticos 02–04

[Inventário nativo](samples/kit-pos-apocaliptico/fontes/inventario_lotes_02_04.json) e [índice de integração](samples/kit-pos-apocaliptico/LOTES_02_04.md). Fontes anteriores preservadas. Resolução por uso nas pastas fontes de cada lote.

---

# Atualização — provas pós-apocalípticas

[Inventário, fontes nativas, integração e pendências](samples/kit-pos-apocaliptico/ASSET_MANIFEST.md). Cinco imagens aproveitadas e uma saída rejeitada; não representam revisão completa do kit. Catálogo e assets distribuídos preservados.

---

# Inventário de arte — edição 0.3

Fontes anteriores preservadas: sete pranchas, 55 regiões. Foram produzidas e integradas três pranchas novas, **23 regiões ilustradas reais** (6 ambientes, 16 grupos de objetos e abrigo), além de arte vetorial funcional. Não se contam prompts como imagens. Detalhes por arquivo e região em [JSON](content/asset_manifest_0.3.json); edição anterior em content/asset_manifest.json.

| Arquivo novo | Dimensões | Origem | Destino |
|---|---|---|---|
| assets/v0.3/environments.png | 1536 × 1024 px | geração integrada nesta sessão, sem API externa | Montagens dos seis destinos e mapa geral; arte de ambientação, não define geometria. |
| assets/v0.3/map_objects.png | 1536 × 1024 px | geração integrada nesta sessão, sem API externa | Camada A dos módulos comuns e temáticos; cartas/itens quando correspondente. |
| assets/v0.3/shelter.png | 1536 × 1024 px | geração integrada nesta sessão, sem API externa | Painel do abrigo, cena contínua com etiquetas vetoriais. |
| assets/v0.3/map_objects_alpha.png | 1536 × 1024 px | edição integrada do gerador: fundo transparente dos mesmos 16 objetos | Mapas e itens; substitui a prancha opaca na composição |

Os SVGs de componentes em assets/v0.3/vetores/ são exportações vetoriais dos PDFs, com textos convertidos em caminhos apenas nesses arquivos auxiliares. Nos PDFs de impressão, textos continuam pesquisáveis com fonte incorporada. Código Python e JSON são as fontes editáveis primárias.

A econômica deriva os mesmos arquivos para cinza e clareia a luminância em 25%, sem redesenhar personagens. O gerador reproduz essas derivações; não são novas ilustrações.

## Limitações reais

- Retratos originais mantidos: aproximadamente 165 ppi na ficha; não foram ampliados artificialmente para alegar detalhe adicional.
- Objetos raster pequenos em cartas: fonte 512×341 px, cerca de 300 ppi na área de 43×29 mm; mapas cerca de 170–210 ppi conforme escala de cada sprite.
- Abrigo 1536×1024 px em 180×120 mm: cerca de 217 ppi; cenas de montagem cerca de 176 ppi.
- Nem todas as 324 cartas da caixa antiga foram rediagramadas: a seleção física desta edição mantém exatamente as 114 cartas do kit 0.2. Catálogo completo e PDFs anteriores preservados.
- Não houve impressão física nem playtest humano.

As plantas táticas têm geometria vetorial exata; objetos não criam obstáculos ou cobertura. A arte das montagens é ilustração de ambientação separada do diagrama jogável. Não há imagem essencial faltando para jogar o kit. A capa anterior permanece disponível, mas não acrescenta folha obrigatória à seleção.


## Fabricação 0.4

Inventário por arquivo, dimensão, origem e integração em [assets_0.4.json](content/production/assets_0.4.json). Novos corpos completos usam os retratos originais como referência; retratos das fichas e encontros foram preservados. Quatro pranchas contêm 24 corpos; duas pranchas contêm 12 itens; sete cenas contínuas integradas. Rascunhos de cenas estão preservados localmente e identificados como não integrados. Econômica é derivada pelo gerador; não é arte independente. Não há prompts contados como imagens. Nenhum PDF ou desenho privado de referência foi incorporado. Mapas têm cerca de 70 ppi efetivos; não foram ampliados para alegar detalhe novo. Textos, medidas, paredes e símbolos funcionais são vetoriais.


## Acabamento 0.5

[Inventário estruturado](content/production/assets_0.5.json), [medições por imagem no PDF](output/edicao-acabamento-v0.5/resolucao_pdfs.json) e [CSV](output/edicao-acabamento-v0.5/RESOLUCAO_EFETIVA.csv). Cinco fontes de cartas integradas (armas, suprimentos, peças corrigidas, viagens e caixa de ferramentas individual); seis pranchas de mobiliário original; sete SVGZ extraídos dos tabuleiros finais. Prancha de peças inicial é rascunho não integrado. Retratos, peões, abrigo e fichas compactas 0.4 preservados. Não há prompts contabilizados como imagens.

Pisos e arquitetura vetoriais; imagens de mobiliário medem pelo menos 211,3 ppi nos módulos. O relatório identifica cada raster por PDF, página, xref, pixels e densidade efetiva. Artes antigas de cartas/rostos mantidas podem ficar abaixo de 300 ppi; não se declara que todas atingem essa meta. JPEG 95 preserva dimensões e máscara alfa, sem reamostragem; PNGs originais editáveis incluídos. A miniatura de alfa é usada somente na análise do enquadramento, nunca como imagem impressa.
<!-- TABULEIROS06 -->
## Tabuleiros 0.6
Inventário em output/edicao-tabuleiros-v0.6/ASSET_MANIFEST.json. Usos por arquivo, recorte nativo, pixels, tamanho físico e ppi em USOS_ASSETS.csv; medição independente do PDF em RESOLUCAO_EFETIVA.csv. O mínimo principal medido é 215.0 ppi. Novas pranchas e materiais originais em assets/v0.6; artes 0.5 boas mantidas, sem reamostragem. Miniaturas dos diagramas são derivadas de A–C a 200 ppi; D–E permanecem vetoriais, com rótulos próprios legíveis. Geometria SVGZ é separada da arte, não se apresenta como mapa inteiro ilustrado. Cenas completas editáveis em Python/JSON e PNGs. Rascunhos rejeitados não entram nos pacotes. Nenhum prompt contado como imagem e nenhuma referência privada distribuída.
