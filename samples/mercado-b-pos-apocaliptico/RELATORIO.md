# Relatório — variante pós-apocalíptica do mercado B

Base conferida e atualizada por fetch: `arte/mercado-amostra-ilustrada`, `c2e66fd`, sem trabalho posterior nem alterações locais no início. Entrega em pasta nova. Nenhum arquivo da versão anterior, outro destino ou componente do jogo foi alterado.

## Alterações artísticas

O mercado mantém estacionamento/acesso, caixas, padaria, corredores, hortifruti, refrigeração e estoque. A variante mostra caixa interrompido, monitores apagados, bandejas abertas nos balcões, prateleiras parcialmente saqueadas, produtos desalinhados, papel rasgado, metal gasto, caixas abertas, vidro trincado e pequenas marcas de umidade. As frutas remanescentes perderam a aparência fresca. A luz diagonal permanece, com tons mais neutros e saturação menor.

Há uma pequena mancha de sangue seco e rastro junto ao refrigerador esquerdo. Não há corpos, mutilações, pessoas ou zumbis desenhados. O sangue não foi espalhado por todos os setores. A tentativa de proteção não foi representada por barricadas, para não sugerir bloqueio novo.

Ferramenta efetivamente usada: **image_gen integrado em edição**, sem chave externa, API paga adicional ou serviço contratado. Não havia skill imagegen disponível. Foram inspecionadas as referências locais antes do uso. Pillow/NumPy fazem recorte, composição e medição; ReportLab e PyMuPDF produzem vetores, PDFs e capturas. Não foi aplicado um filtro genérico para simular a produção artística.

O piloto R2C1 incluiu caixa, prateleira, refrigerador e circulação. Sua aparência orientou as outras oito seções. A primeira montagem revelou móveis cortados nas sobreposições; seis reparos passaram a abranger móveis inteiros. O reparo dos caixas foi expandido para eliminar fragmentos no seu limite superior. Dois reparos pequenos regularizaram a continuidade do piso no acesso. São **17 imagens nativas integradas**, mais uma tentativa substituída preservada. Não são propostas alternativas de arquitetura.

## Preservação e legibilidade

A geometria é idêntica em bytes à base: 16 zonas, **21 conexões**, cinco portas, bloqueio 7–8, três divisórias internas permanentes. Mesmas entradas, buscas, objetivos e surgimento. As funções vetoriais de paredes, portas e símbolos foram preservadas.

As 21 passagens foram inspecionadas na arte sem interface em `provas/CONEXOES_21.jpg`. Z15–Z16 continua livre em **415,5 × 332,5 mm**, origem superior esquerda. Não há entulho cruzando conectores. Expositores próximos a 4–8 e 10–11 e o carrinho junto a 5–9 continuam próximos da circulação, sem cruzar a linha funcional da passagem. Os quadrados verdes da prova são marcações de revisão, não novos espaços de jogo.

Números e sinais continuam sobre fundos claros, aplicados após a arte. O diagnóstico em cinza preserva sua leitura. O desgaste não se tornou uma zona de dano ou uma busca adicional. A simulação com marcadores de 29 mm é digital e não altera componentes.

## Resolução e fabricação

Composição final: **3817 × 2618 pixels** em **554 × 380 mm**, equivalentes a **175,003 × 174,993 ppi**, a mesma densidade da base. Menor densidade de fonte utilizada: **183,2045 ppi**. Todos os originais foram reduzidos para compor, nunca ampliados; o código verifica essa condição. Ppi calculado pela área física efetiva, não por metadados. `ASSET_MANIFEST.json` registra dimensões nativas, área utilizada, tamanho impresso, ppi em cada eixo e SHA-256.

Quatro A4 paisagem exatos, cortes 277 × 190 mm, mesma ordem e orientação. Os quatro módulos contêm o mesmo raster incorporado, com recortes vetoriais da composição global. As matrizes da remontagem correspondem à fonte com erro menor que 0,001 ponto. A comparação raster em 72 ppi varia por reamostragem do renderizador (valor registrado no JSON); não representa diferença física entre os módulos.

A prova comparativa usa o recorte **x=0, y=190, largura=100, altura=100 mm** nas duas versões, sem redução. Destinos na A4: x=55 mm, y=30 e y=155 mm, ambos com 100 × 100 mm; régua de 100 mm. As identificações ficam fora dos recortes.

## Revisão e limites

Renderizados e inspecionados: quatro folhas, mapa montado, imagem sem interface, 21 conectores, detalhe de sangue/vidro, passagem Z15–Z16, junções e diagnóstico em cinza. Verificadas A4, fontes incorporadas, imagem nova, geometria, escala da prova e integridade dos pacotes.

A direção e os setores foram mantidos, mas a edição generativa produz pequenas variações de textura, sombras, contornos decorativos e rejunte. Não se alega identidade pixel a pixel dos móveis com a base. Alguns objetos periféricos conservam faces laterais estilizadas. Em ampliação podem ser percebidas variações locais de piso nas áreas recompostas; os quatro cortes A4 não introduzem novas emendas de imagem. A leitura de conexão depende da geometria vetorial preservada, não de cada rejunte decorativo.

Não houve impressão física, montagem física ou playtest humano. A aprovação da atmosfera é visual e cabe ao proprietário; os testes objetivos não a substituem. A prova foi preparada para impressão futura. Nenhum outro mapa recebeu este tratamento.
