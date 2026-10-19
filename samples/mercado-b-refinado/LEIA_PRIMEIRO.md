# Mercado B refinado — amostra isolada

A composição B foi mantida. Esta pasta não substitui nenhuma edição do jogo.

## O que imprimir

| Arquivo | Uso | Folhas | Configuração |
|---|---|---:|---|
| [MERCADO_4_A4.pdf](MERCADO_4_A4.pdf) | Mercado para avaliação na mesa | 4 | A4 paisagem, uma face, 100%, sem ajustar |
| [DETALHE_100MM_A4.pdf](DETALHE_100MM_A4.pdf) | Prova opcional antes do mapa | 1 | A4 retrato, uma face, 100% |

O mercado exige **4 folhas**, ou **5 incluindo a prova opcional**. Não imprimir os PDFs de fontes e de simulação como componentes adicionais.

Corte cada módulo em 277 × 190 mm pelas marcas. Una pelas bordas, sem sobreposição, com fita no verso:

```
M1 | M2
---+---
M3 | M4
```

Resultado: 554 × 380 mm. As margens são de 10 mm. Não há duplex nesta amostra.

Linhas tracejadas delimitam zonas; as interrupções de 14 mm são os conectores existentes. Barras marrons são portas; X vermelho indica o bloqueio inicial 7–8. E/S: entrada/saída; B: busca; O: objetivo; S: surgimento. Paredes contínuas são permanentes. Móveis são decorativos, sem novas regras de cobertura ou bloqueio.

## Arquivos digitais

- `MERCADO_ARTE_175PPI.png`: composição raster em 3817 × 2618 pixels.
- `MERCADO_SEM_INTERFACE.png`: prévia extraída do PDF com arquitetura, sem interface.
- `MERCADO_COM_GEOMETRIA.png`: prévia do PDF final remontado.
- `fontes/MERCADO_ARTE_VETOR.pdf`: composição integral sem interface, com paredes vetoriais.
- `fontes/MERCADO_FONTE.pdf`: composição integral com geometria vetorial.
- `COMPARACAO_B_ANTES_DEPOIS.jpg` e `provas/`: comparações e páginas renderizadas.
- `originais/`: imagens nativas efetivamente produzidas pelo image_gen integrado. Tentativas anteriores identificadas não entram na impressão.
- `ASSET_MANIFEST.json`: dimensões, recorte, tamanho físico, ppi e hash de cada imagem utilizada.

As prévias PNG do PDF foram renderizadas a 72 ppi para consulta; não substituem o PDF de impressão, cujo raster tem 175 ppi.

Leia [RELATORIO.md](RELATORIO.md) para verificações e limitações.
