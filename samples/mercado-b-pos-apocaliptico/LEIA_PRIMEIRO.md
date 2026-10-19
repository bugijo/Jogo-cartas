# Mercado B — variante pós-apocalíptica

Variante isolada da composição B de `c2e66fd`. Não substitui o mercado atual nem a edição distribuída.

| Arquivo | Finalidade | Folhas | Impressão |
|---|---|---:|---|
| [PROVA_COMPARATIVA_100MM_A4.pdf](PROVA_COMPARATIVA_100MM_A4.pdf) | Comparar as duas atmosferas quando puder imprimir | **1** | A4 retrato; uma face; 100%, sem ajustar |
| [MERCADO_4_A4.pdf](MERCADO_4_A4.pdf) | Montar o mercado completo | **4** | A4 paisagem; uma face; 100%, sem ajustar |

A prova comparativa basta para avaliar papel, cor, sombra, sangue e nitidez: contém dois recortes do **mesmo local**, cada um com **100 × 100 mm**, dispostos verticalmente, e régua de 100 mm. Não é necessário imprimir o mapa para fazer essa avaliação.

Se imprimir ambos, são **5 folhas**. Os PDFs dentro de `fontes/` e a simulação de ocupação não são folhas adicionais obrigatórias.

Para o mapa, corte nas marcas em 277 × 190 mm e una pelas bordas, sem sobreposição, com fita no verso:

```
M1 | M2
---+---
M3 | M4
```

Resultado: **554 × 380 mm**. Margens externas de 10 mm. Não há duplex. Nunca usar “ajustar à página”.

Os sinais são os mesmos: E/S entrada/saída, B busca, O objetivo, S surgimento; linhas tracejadas delimitam zonas; interrupções são os conectores; barras marrons são portas; X vermelho é o bloqueio inicial 7–8. Sangue, lixo, móveis e desgaste são somente decoração: não criam obstáculos, cobertura, dano ou recursos.

## Consulta digital e fontes

- `MERCADO_ARTE_175PPI.png`: composição raster original desta variante, 3817 × 2618 pixels.
- `MERCADO_SEM_INTERFACE.png`: captura do PDF com arquitetura vetorial, sem sinais.
- `MERCADO_COM_GEOMETRIA.png`: captura do PDF final remontado.
- `COMPARACAO_ATUAL_VARIANTE.jpg`: comparação dos PDFs montados.
- `provas/PROVA_COMPARATIVA.png`: captura da folha comparativa.
- `provas/SANGUE_DESGASTE.png`, `PASSAGEM_LIVRE.png`, `CONTRASTE_CINZA.png`: detalhes e diagnóstico do PDF final.
- `originais/`: saídas nativas do image_gen; `referencias/`: recortes do nosso mercado usados na edição.
- `fontes/`: composição, gerador, geometria e recortes editáveis; `ASSET_MANIFEST.json`: densidades e hashes.

As capturas de consulta usam 72 ppi; detalhes usam 144 ppi. Os PDFs de impressão mantêm a arte a 175 ppi e geometria/textos vetoriais.
