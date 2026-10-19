# Mercado B refinado — relatório

Base verificada: branch `arte/mercado-amostra-ilustrada`, commit `9d08b2f`. Não havia alterações posteriores na base consultada. Toda a entrega está em pasta nova. O mercado anterior, outros destinos, cartas, personagens, peões, painel, abrigo e regras não foram alterados.

## Direção artística

Preservados a composição B, estacionamento superior, caixas à esquerda, corredores centrais, hortifruti à direita, refrigeração inferior/esquerda e estoque/bebidas no canto inferior direito. A luz quente diagonal e a paleta original continuam. A reconstrução tornou embalagens mais definidas e algumas cores mais vivas; isso é alteração artística visível, não apenas aumento de resolução.

Foi utilizado **image_gen integrado**, sem chave externa, API paga adicional ou instalação de serviço. A skill imagegen não estava disponível no catálogo; foram seguidas as instruções da ferramenta integrada. A arte anterior serviu como referência de composição, não como raster ampliado da entrega.

Foram produzidas nove reconstruções coordenadas em malha 3 × 3, uma correção de junção e oito reparos locais integrados: 18 fontes nativas. O teste inicial usou duas seções vizinhas; a quebra de piso identificada foi corrigida antes de completar a malha. Reparos posteriores trataram móveis inteiros nas emendas, hortifruti, veículo de carga e expositores de bebidas. Tentativas rejeitadas foram preservadas.

Os cinco PDFs avulsos disponíveis foram abertos e renderizados: dois de personagens, dois de equipamentos e um painel. Não havia tiles frente/verso nem ZIP acessível nesta tarefa. Nenhum material privado de referência foi incluído nesta pasta.

## Fidelidade à planta

JSON idêntico ao da candidata anterior e à geometria de produção: 16 zonas, 21 conexões, cinco portas, bloqueio 7–8 e três divisórias internas permanentes (2–6, 6–10, 10–14). Entradas, buscas, objetivos e surgimento preservados.

Z15–Z16 está em x=415,5 mm, y=332,5 mm, origem superior esquerda. A pilha que atravessava o ponto foi redistribuída; o piso está livre na própria imagem, sem etiqueta cobrindo caixas. Foram revistos os outros vinte conectores. O hortifruti também foi encurtado para liberar 4–8 e 8–12.

`provas/CONEXOES_21.jpg` mostra a inspeção da arte sem interface. Os quadrados verdes são instrumentos de revisão, não novos espaços ou regras. Carrinho junto a 5–9 e gôndola junto a 10–11 ficam próximos da passagem, mas não cruzam sua linha funcional. Componentes podem cobrir decoração; a simulação com seis marcadores atuais de 29 mm em Z6 mantém números e conectores visíveis. Não é uma afirmação sobre lotação máxima de todas as zonas.

## Resolução

Antes: 1514 × 1039 pixels em 554 × 380 mm, aproximadamente 69,4 ppi.
Agora: **3817 × 2618 pixels**, **175,003 × 174,993 ppi** no mesmo tamanho físico. Meta mínima de 150 ppi atingida; a meta desejável de 200 ppi não foi atingida em toda a composição.

A menor densidade nativa utilizada é **178,0168 ppi** (R2C2, eixo vertical). O manifesto registra separadamente os dois eixos de todas as fontes, inclusive recortes e sobreposições. As imagens foram reduzidas à composição de 175 ppi, nunca ampliadas. O compositor verifica isso automaticamente. A exportação PDF preserva a imagem de 3817 × 2618, sem recompressão JPEG. Paredes, geometria, sinais e textos permanecem vetoriais.

## Verificações e inspeção

- Quatro páginas A4 paisagem exatas; corte 277 × 190 mm; montagem 554 × 380 mm.
- Todas as quatro páginas finais renderizadas e inspecionadas por contato; mapa montado e detalhes revistos.
- Fontes incorporadas e textos pesquisáveis; imagem nova presente nas quatro páginas.
- Mesmos bytes de imagem nos quatro módulos; matrizes de remontagem diferem menos de 0,001 ponto da fonte integral.
- A diferença média entre renders integral/remontado em 72 ppi foi 2,85/255: a reamostragem do renderizador varia nos recortes aninhados. A inspeção do mapa de diferenças e das matrizes não apontou deslocamento físico de módulos; isso não é uma garantia de alinhamento de impressora.
- Prova de 100 × 100 mm fornecida em A4, sem redução.
- Comparações Z15–Z16, refrigeradores, junção e mapa inteiro vêm dos PDFs finais.
- A montagem artística usa sobreposição e junção de menor diferença; reparos locais usam transição de 4 mm no piso. Não foram usados quadros espessos para esconder emendas.

## Prontidão e pendências

**Direção artística:** B preservada e refinada, sujeita à avaliação visual do proprietário.

**Planta:** preservada; passagem principal corrigida na ilustração.

**Resolução:** mínimo de 150 ppi resolvido; saída real de 175 ppi.

**Impressão:** PDF disponível para prova doméstica em quatro folhas. Não houve impressão física, montagem física ou playtest humano.

A projeção dos refrigeradores e móveis principais foi corrigida para vista superior. Ainda há pequenas faces laterais estilizadas em volumes periféricos, especialmente caixas/vasos do estoque. Portanto, não declaro ortografia absolutamente perfeita nem aprovação artística final. Há pequenas variações locais na malha do piso em áreas de composição; as junções A4 usam a mesma imagem global e não introduzem mudanças adicionais. Nenhuma delas foi convertida em parede ou regra.

A próxima avaliação deve usar a prova física de 100 mm e os detalhes de projeção. Nenhum outro destino recebeu esta arte.
