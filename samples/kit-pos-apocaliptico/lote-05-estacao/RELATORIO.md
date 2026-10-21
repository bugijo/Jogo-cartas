# Estação de tratamento — prova pós-apocalíptica

A estação do capítulo é a instalação de abastecimento, com bomba, membrana e filtros. A arte representa manutenção interrompida, tubulações, bombas e estoque usado; compara-se ao Mercado B pós-apocalíptico aprovado. Este lote é uma prova isolada e não substitui a edição distribuída.

## Imprimir e avaliar

- [ESTACAO_4_A4.pdf](ESTACAO_4_A4.pdf): quatro A4 paisagem, uma face, 100%, sem ajustar. Corte 277 × 190 mm por folha; M1 M2 acima de M3 M4; montagem 554 × 380 mm.
- [DETALHE_100MM_A4.pdf](DETALHE_100MM_A4.pdf): recorte real de 100 × 100 mm. [Comparação na mesma escala](COMPARACAO_100MM_A4.pdf) com a edição anterior.
- [Mapa montado com regras](ESTACAO_COM_GEOMETRIA.png), [arte sem interface](ESTACAO_SEM_INTERFACE.png), [comparação 0.6 → prova](COMPARACAO_B_ANTES_DEPOIS.jpg).

As imagens de apresentação são renderizações dos PDFs finais. Textos, símbolos, zonas e paredes são vetores; as seções nativas estão em `originais/`, o recorte e a reconstrução em `fontes/compose.py`, o PDF em `fontes/build.py`, e os pontos revisados em `fontes/diagnostics.py`.

## Intervenções e fidelidade

Foram geradas nove seções nativas sobre uma composição global. Duas bombas e a bancada superior receberam reconstruções locais para evitar duplicação nas emendas. A bancada de Z6–Z7, quatro filtros sobre Z12–Z16 e um palete sobre Z9–Z13 foram removidos da ilustração; a estante foi deslocada para baixo da divisória permanente; a caixa de Z3–Z4 foi removida. O conjunto restante identifica uma estação de tratamento. Os códigos dos módulos ficam na margem da folha, fora da área jogável. Duas junções da parede inferior receberam reparos locais.

`fontes/geometria.json` é idêntico à estação canônica `content/production/geometry_0.6.json[5]`: 16 zonas, 21 conexões, cinco portas e dois bloqueios iniciais (7–8 e 13–14). Entrada/saída, busca, objetivos e surgimento permanecem nos mesmos números. Todos os 21 conectores foram recortados do PDF final em [provas/CONEXOES_21.jpg](provas/CONEXOES_21.jpg) e revistos visualmente.

## Resolução e limites

O composto usa 3817 × 2618 pixels em 554 × 380 mm, resultando em 175,0 ppi efetivos. Cada uma das nove seções cobre sua área com 183,1–195,2 ppi nativos antes da redução ao composto; os nove reparos têm 271,8 ppi ou mais. Nenhum arquivo foi ampliado para atingir esses números. Medidas individuais constam em `fontes/resolucao.json` e as verificações em `VERIFICACOES.json`.

A estação mantém diagonais de luz mais quentes que o Mercado B, faces laterais estilizadas em armários, pequenas diferenças de rejunte e transição de piso nos reparos. A geometria vetorial continua clara. A prova em cinza e o contato de quatro folhas foram inspecionados. A montagem digital apresenta diferenças de antialiasing entre PDF fonte e recortes (média 5,46/255); hashes e transformações físicas das quatro imagens foram conferidos. Ainda faltam impressão física, alinhamento manual, teste em mesa e avaliação artística do proprietário. Não tratar como kit inteiro concluído.
