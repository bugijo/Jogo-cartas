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
