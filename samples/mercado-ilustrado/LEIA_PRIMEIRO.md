# Mercado — amostra artística para avaliação

**Candidata isolada, ainda não aprovada para substituir o mercado 0.6.** Foram produzidas duas propostas e duas correções da B. A composição melhorou, mas a resolução raster, a projeção de alguns móveis e o conector Z15–Z16 ainda precisam de trabalho. O limite desta exploração foi respeitado.

[Baixar somente esta amostra, com fontes e originais](https://raw.githubusercontent.com/bugijo/Jogo-cartas/arte/mercado-amostra-ilustrada/samples/mercado-ilustrado/AMOSTRA_MERCADO.zip)

## Abrir e avaliar

- [Duas propostas A/B](PROPOSTAS_A_B.jpg)
- [Mercado escolhido com arquitetura, sem interface](MERCADO_SEM_INTERFACE.png)
- [Mercado com geometria e símbolos — captura do PDF remontado](MERCADO_COM_GEOMETRIA.png)
- [Comparação real 0.6 → candidata](COMPARACAO_06_CANDIDATA.jpg)
- [Quatro folhas A4 do mercado](MERCADO_4_A4.pdf)
- [Prova de detalhe 100 × 100 mm em A4](DETALHE_100MM_A4.pdf)
- [Contato das quatro folhas](provas/CONTATO_4_A4.jpg)
- [Junção central](provas/JUNCAO_CENTRAL.png)
- [Componentes atuais em escala](provas/OCUPACAO_A4.pdf)
- [Relatório visual e de resolução](RELATORIO.md)
- [Verificações estruturadas](VERIFICACOES.json)

## Impressão desta amostra

O mercado usa **4 folhas A4 paisagem, uma face, escala 100%, sem ajustar**. Corte cada módulo em **277 × 190 mm**, usando as marcas; junte M1/M2 acima e M3/M4 abaixo, sem sobreposição. Resultado: **554 × 380 mm**. Margens de 10 mm. Não há duplex nesta amostra.

A prova de detalhe é **1 folha A4 retrato opcional**. A prova de ocupação é **1 A4 paisagem opcional**. Portanto, são quatro folhas para o mapa; cinco com detalhe; seis com as duas provas. Não imprima as imagens PNG nem os PDFs de `fontes/` como folhas do jogo: esses PDFs são pranchas de tamanho integral e plantas de referência.

E/S = entrada e saída; B1/B2 = busca; O1/O2 = objetivo; S = surgimento. Parede contínua = sem conexão; tracejado = fronteira funcional; abertura central = conector de 14 mm; barra = porta; X = bloqueio inicial. Estado persistente das portas continua registrado pelos componentes atuais. Móveis são decoração, sem nova cobertura ou obstáculo.

A resolução da arte é **69,4 ppi**, inferior à meta de 150–200 ppi. A prova serve para decidir a direção artística e observar essa limitação no tamanho físico. Não se recomenda reimprimir o jogo completo para avaliá-la.

## Fontes e preservação

`originais/` guarda os quatro PNGs nativos recebidos do gerador integrado, sem ampliação ou retoque externo. `fontes/geometria.json` congela o Mercado da 0.6. `fontes/build.py` compõe arquitetura, geometria, textos, corte, provas e relatório. Pillow foi usado apenas para contatos, medição e comparação; PyMuPDF para PDF/renderização; ReportLab para composição vetorial.

No repositório, execute:

```bash
python samples/mercado-ilustrado/fontes/build.py
```

Dependências: as de `requirements.txt` do projeto e fontes DejaVu em `/usr/share/fonts/truetype/dejavu/`. O PDF de impressão pode ser reconstruído com esta pasta isolada e essas dependências; as provas comparativas e de peças reais usam também os PDFs 0.6 preservados no repositório. As imagens-guia usadas na geração estão congeladas em `fontes/`, sem referências privadas anexadas.

Nenhuma mudança nas cartas, personagens, peões, painéis, abrigo, regras, campanha ou demais mapas. Não há edição econômica nem pacote completo novo. O arquivo ZIP desta entrega contém somente esta amostra.

Branch: `arte/mercado-amostra-ilustrada`, derivada de `ec071e1`, sem merge.
