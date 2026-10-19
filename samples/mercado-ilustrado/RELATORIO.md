# Relatório da amostra do mercado

## Base, ferramentas e referências

Fetch confirmou `ec071e1` como ponta da branch informada. Árvore limpa, sem trabalho posterior observado. Criada `arte/mercado-amostra-ilustrada`. Apenas arquivos novos em `samples/mercado-ilustrado`; nenhuma edição anterior substituída.

Ferramenta realmente usada: **image_gen.imagegen integrada**, para duas propostas e duas edições. Não foi usada API externa, chave, CLI de geração ou serviço contratado. A ferramenta está disponível independentemente de uma skill com nome imagegen; essa skill não constava da lista de skills disponíveis. Seguidas as instruções da ferramenta, incluindo inspeção das imagens antes de editar. O limite de duas correções foi consumido; não houve alegação de bloqueio de quota do serviço.

Os cinco PDFs anexados desta tarefa foram abertos e suas páginas renderizadas: dois de personagens, dois de equipamentos e uma ficha com três painéis. Todos têm uma página. Observações: agrupamento por categoria; títulos e mecânica separados das imagens; pares de personagens adjacentes; áreas próprias de equipamento. Não há tiles nesses arquivos; não se deduz geometria nem regime de duplex deles. `zombecide.zip` e PDFs de tiles não estavam disponíveis. Nenhum arquivo ou recorte privado foi incorporado à entrega.

Mercados 0.4, 0.5 e 0.6 examinados na comparação extraída dos PDFs existentes: a 0.4 traz variedade local mas reinicia o ambiente por zona; a 0.5 tem circulação contínua e pouca composição; a 0.6 traz mais setores, ainda com objetos destacados sobre piso. Aproveitados da 0.6 apenas planta, dimensões e gramática funcional. A imagem desta amostra é nova, não uma montagem dos sprites anteriores.

## Propostas e seleção

| Aspecto | A, clara | B, atmosférica |
|---|---|---|
| Reconhecimento | Mercado com caixas, refrigeração e estoque | Mercado com corredores, departamentos e recebimento mais coesos |
| Arquitetura | Divisórias aproximadas; barreira de entrada inventada | Divisórias aproximadas, mas acesso mais aberto |
| Riqueza | Produtos legíveis; arranjo mais esquemático | Luz global, materiais e pequenas histórias mais integrados |
| Espaço | Corredores grandes; interferências pontuais | Boa circulação, porém cart/freezer/pallets precisavam mover |
| Fidelidade à planta | Não aprovada sem correção | Melhor ponto de partida, não aprovada sem correção |

**Escolhida B.** O ganho principal é uma cena global: estacionamento/recebimento, caixas junto ao acesso, corredores, padaria, hortifruti, refrigeração e depósito. A luz atravessa o ambiente inteiro. Móveis têm relações espaciais, sem uma ilustração independente por zona.

Correção 1: deslocou cart de compras, recolheu freezers e redistribuiu pallets para liberar conectores. Pediu alinhamento das divisórias e câmera vertical, parcialmente atendidos.

Correção 2: retirou as divisórias raster e sua vegetação, liberou passagem ao lado da padaria e manteve composição global. Recompostas somente as três divisórias reais em vetor, nas posições congeladas. Não foram aplicadas etiquetas grandes para cobrir arquitetura errada.

## Resolução real

Todos os quatro PNGs recebidos têm **1514 × 1039 pixels nativos**. O gerador não atendeu aos pedidos textuais de 3272 × 2244 ou 4363 × 2992. A interface disponível só expõe prompt/referências/transparência, sem parâmetro numérico de resolução.

Área utilizada: imagem inteira, sem recorte, impressa em 554 × 380 mm. Cálculo: `1514 ÷ (554/25,4) = 69,4144 ppi`; `1039 ÷ (380/25,4) = 69,4489 ppi`. **Meta de 150 ppi não atingida.** Na arte desta amostra, objetos pequenos e embalagens perdem definição no tamanho final. A proposta não substitui a resolução superior do mobiliário da 0.6.

Não houve interpolação dos originais, alteração de DPI, nitidez artificial nem exportação alegada como detalhe novo. Os PNGs de prévia são renderizações dos PDFs; sua quantidade de pixels não muda a resolução intrínseca da imagem incorporada. Arquitetura, números, símbolos, portas e corte são vetoriais; fontes DejaVu incorporadas.

## Verificação e avaliação final

- Planta congelada: 16 zonas, 21 conexões, cinco portas e bloqueio inicial 7–8; mesmas entradas, buscas, objetivos e surgimento. Comparação JSON exata com a 0.6.
- As três divisórias permanentes são 2–6, 6–10 e 10–14. Nenhum conector foi adicionado/removido para acomodar arte.
- Quatro páginas A4 exatas, paisagem; corte 277 × 190 mm; montagem 554 × 380 mm; uma face. Imagem nativa presente em cada página. Todas renderizadas e examinadas em contato, com detalhe de junção.
- Remontagem comparada com PDF fonte a 72 ppi: diferença média inferior a 1/255, registrada em `VERIFICACOES.json`. Uma imagem global contínua garante que os quatro recortes não têm estilos ou iluminação independentes.
- Simulação de seis marcadores atuais de 29 × 29 mm em Z6 preserva número e conectores. A decoração pode ficar sob as peças. Não foram redesenhados marcadores nem alterado o limite de inimigos. A limitação conhecida de aglomeração com muitos marcadores planos permanece.
- A passagem Z15–Z16 ainda fica visualmente atravessada por caixas/expositor de bebidas. O vetor preserva a conexão, mas a composição **falha na clareza visual desse ponto**. Veja `provas/PASSAGEM_15_16_PENDENTE.png`. Não deve ser tratada como obstáculo pelas regras.
- Há inclinação residual nos refrigeradores e móveis periféricos. A câmera é predominantemente superior, mas **não se aprovou ortografia rigorosa**.
- Número de objetos não foi usado como prova de qualidade. A avaliação artística é revisão do autor e permanece sujeita à avaliação do proprietário.

**Resultado:** amostra visual concreta, com composição global mais convincente; **não aprovada como arte final de produção**, por resolução baixa, perspectiva residual e interferência em Z15–Z16. Não houve impressão física, montagem física nem playtest humano.

## Retomada exata, somente após avaliação do proprietário

Parar nesta amostra. Se a direção B for escolhida, a próxima produção deve corrigir primeiro o conector Z15–Z16 (x=415,5 mm; y=332,5 mm medido do topo), removendo as caixas de uma área livre ao redor desse ponto, e a projeção dos refrigeradores. A imagem-base é `originais/CORRECAO_2_ESCOLHIDA.png`; a planta é `fontes/geometria.json`. O código recoloca as três paredes precisas. Depois será necessária geração nativa de maior resolução ou produção coordenada de seções com referência global; não ampliar esta imagem e declarar 150 ppi. Não aplicar aos outros destinos antes da decisão visual.
