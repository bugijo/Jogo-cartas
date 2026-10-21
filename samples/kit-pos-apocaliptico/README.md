> Continuação: [lotes 02–04, PDFs e comparações](LOTES_02_04.md). O relato abaixo documenta as primeiras provas e permanece como histórico.

# Zona Zero — provas pós-apocalípticas

**Provas isoladas de arte, não uma nova edição completa.** Base conferida localmente e no remoto: `48f5794`. Branch `arte/kit-pos-apocaliptico-provas`. Nenhuma publicação ou substituição do kit de 58 folhas.

## O que abrir

| PDF | Conteúdo | Páginas / folhas | Impressão |
|---|---|---:|---|
| [PERSONAGENS_PROVA_A4.pdf](pdfs/PERSONAGENS_PROVA_A4.pdf) | Lia, Ivo, Mara, Caio, Nara, Bento | 1 / 1 | Retrato, uma face |
| [INIMIGOS_PROVA_A4.pdf](pdfs/INIMIGOS_PROVA_A4.pdf) | Errante, Corredor, Bruto; arte preservada | 1 / 1 | Retrato, uma face |
| [CARTAS_PROVA_DUPLEX.pdf](pdfs/CARTAS_PROVA_DUPLEX.pdf) | Nove cartas existentes, frente e verso | 2 / 1 | Retrato, duplex, borda longa |
| [OFICINA_4_A4.pdf](pdfs/OFICINA_4_A4.pdf) | Oficina com atlas revisado | 4 / 4 | Paisagem, uma face |
| [FICHAS_SEIS_HEROIS.pdf](pdfs/FICHAS_SEIS_HEROIS.pdf) | Seis fichas com as mesmas regras | 3 / 3 | Retrato, uma face |
| [HOSPITAL_4_A4.pdf](pdfs/HOSPITAL_4_A4.pdf) | Segundo cenário: mobiliário revisado | 4 / 4 | Paisagem, uma face |
| [COMPARACOES_100MM_A4.pdf](pdfs/COMPARACOES_100MM_A4.pdf) | Antes/depois no mesmo recorte físico | 2 / 2 | Retrato, uma face |

Os quatro primeiros arquivos permitem avaliar os quatro lotes iniciais: **7 folhas**. Todos os PDFs acima: **17 páginas em 16 folhas**. São provas opcionais; não somar às 58 folhas obrigatórias nem imprimir como pacote completo de jogo.

A4 exato, 100%, sem ajustar. Cartas 63 × 88 mm, grade existente com intervalos de 2 mm. Mapas: cortar cada folha em 277 × 190 mm; M1/M2 em cima, M3/M4 embaixo, topo para cima; unir sem sobreposição. Montagem 554 × 380 mm. As montagens grandes em `fontes/` são fontes, não páginas domésticas a imprimir reduzidas.

## Evidências

- [Antes/depois dos retratos](provas/COMPARACAO_PERSONAGENS.jpg)
- [Antes/depois das cartas](provas/COMPARACAO_CARTAS.jpg)
- [Oficina montada](provas/OFICINA_DEPOIS_MONTADA.png)
- [Hospital montado](provas/HOSPITAL_DEPOIS_MONTADA.png)
- [Todas as páginas de componentes](provas/CONTATO_TODAS_PAGINAS.jpg)
- [Conectores da oficina](provas/OFICINA_21_CONEXOES.jpg) e [do hospital](provas/HOSPITAL_21_CONEXOES.jpg)
- [Relatório e limitações](VISUAL_QA.md)

## Reproduzir

No repositório existente, com a base `48f5794` e esta branch:

```sh
python samples/kit-pos-apocaliptico/fontes/build.py
python samples/kit-pos-apocaliptico/fontes/validate.py
```

Pillow, PyMuPDF, ReportLab e NumPy; fontes DejaVu instaladas. A reconstrução dos PDFs usa imagens nativas salvas e não chama geradores nem APIs. O ZIP de provas não é um clone autônomo do repositório: `src/`, `content/`, assets preservados e o manifesto original são dependências explicitamente mantidas na base.

As artes nativas foram editadas com `image_gen` integrado. Nenhuma API paga externa ou chave. Inimigos e armas adequados foram reaproveitados. Imagens de referência privadas não foram incluídas; o Mercado de comparação é arte do próprio projeto.

Pacotes locais separados (gerar com `python samples/kit-pos-apocaliptico/fontes/package.py`): `ZONA_ZERO_PROVAS_PDFS.zip` contém os sete PDFs e guias; `ZONA_ZERO_FONTES_ARTE.zip` contém imagens nativas, código e dados; `ZONA_ZERO_COMPARACOES.zip` contém evidências visuais. Os links de comparação deste índice apontam ao pacote de comparações; extraia os pacotes na mesma pasta para navegar entre eles. Nenhum é uma publicação no GitHub.
