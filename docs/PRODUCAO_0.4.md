# Produção 0.4 — referência privada, jogo preservado

Base: ccff9c8, árvore limpa, nenhuma candidata 0.4 local/remota após fetch. Branch arte/pnp-fabricacao-v0-4. Não tocar no jogo digital nem substituir edições anteriores. Escopo vinculante: pedido do proprietário nesta sessão; todos os dados e regras 0.2 ficam congelados.

## Plano de execução
1. Inspecionar anexos e registrar observações objetivas.
2. Template real 63×88 mm: nome, arte, efeito integral (mínimo 9,5 pt), restrições e ID; sem números novos.
3. Aplicar às mesmas 114 cartas e conferir sigilo/versos; opção por categoria para reposição separada.
4. Peões dos mesmos 24 heróis, corpos completos coerentes com retratos; inimigos existentes e painel opcional que recebe fichas e cartas reais.
5. Cenas táticas contínuas, ortográficas, com geometria vetorial preservada; abrigo e adjacência administrativa mantidos.
6. Pacotes A duplex e B recortar/colar, cada um com edição ilustrada e econômica. Compatível A: 58 folhas; B: calcular diferenças por PDF. Extras nunca obrigatórios.
7. Renderizar tudo, provas de peões/painel, validar, ZIPs sem referência, commit e push sem merge.

## Interfaces e decisões
- Cartas e painéis compartilham 63×88 mm; slots opcionais 66×92 mm. Quatro cargas-base, armas contam dentro delas, jamais seis cargas por separar equipamentos.
- Mapas e peões compartilham zona 138,5×95 mm; base de papel 22×12 mm. Verificar ocupação e manter limite de 24 inimigos.
- Dado que 24 inimigos podem ser de qualquer tipo, oferecer 3 variantes visuais de E01–E24, não 72 IDs simultâneos. Nunca usar duas variantes do mesmo ID. Tipos não mudam regras.
- Cartas por categoria podem desperdiçar mais espaços de folha: ficam como reposição opcional, substituem os PDFs consolidados, nunca somam cartas ao jogo.
- Referência recebida: cinco PDFs, seis páginas. Falta zombecide.zip; não recebidos tiles, tokens, spawn e folhas de sobreviventes/zumbis. Não inferir seus métodos de montagem.
- Não incorporar material de referência. Renders e extrações privados ficam somente em /tmp/zz-referencia-privada, fora do repositório e de qualquer ZIP.

## Ciclo 1 — observado
PDFs de personagens: três pares frente/verso lado a lado por página, arte grande, habilidades em blocos no rodapé. Um arquivo declara Frente e Verso; o outro mantém a mesma organização. Isso NÃO é demonstração de duplex automático.
Equipamentos: dezesseis frentes por página (4×4), título superior, objeto central, faixa de condição/efeito e símbolos/valores no rodapé. Não há versos nas duas páginas recebidas.
Ficha: guia de duas páginas mostra ficha apoiada em material macio, marcadores perfurantes e fendas para cartas em pé. A funcionalidade depende de material real. Nosso painel usará lápis, clipes opcionais e slots planos com folga; não simular mecanismo plástico.
Dimensões observadas variam: 209,55–210,06 mm × 296,76–297,04 mm. São amostras próximas de A4, não base dimensional. Nossa saída será A4 exato e cartas 63×88 mm. Não copiar atributos, trilhas, personagens ou emblemas.

## Progresso
Ciclo 1 concluído: seis páginas integralmente renderizadas e inspecionadas, textos extraídos quando presentes. Categorias ausentes registradas. Nenhum asset privado copiado ao produto.

Ciclo 2 concluído: amostra real de nove tipos de carta, nove por A4, 63×88 mm. Efeitos a 10 pt quando curtos/médios e 9,5 pt quando densos, sem suprimir texto. Nomes primeiro, arte central, valores apenas de metadados existentes. Inspeção corrigiu enquadramento de retratos dos encontros; não recortar o rosto em miniatura horizontal. Cinco novos testes físicos falharam antes da implementação e passaram depois; suíte total 19/19.

Ciclo 3: seleção aplicada aos 114 IDs, dois métodos. 456 comparações de efeitos impressos passaram nas duas edições; correção de uma carta curta com palavras longas: altura medida no tamanho real substitui limite por número de caracteres. Sem reduzir fonte. Recursos e componentes ganharam ilustrações originais específicas; a atualização final integrará essas pranchas já produzidas. Pareamento manual é colocado fora do corte; miolo opaco necessário. Versos secretos permanecem comuns.

Ciclo 4 concluído: 24 corpos completos produzidos com os retratos originais como referência. Redes retangulares 22 × 116 mm, dobra central e duas abas de 6 mm: base 22 × 12 mm. Verso ilustrado espelhado, sem fingir anatomia posterior. Dois A4 de heróis e seis de variantes inimigas, sempre 24 IDs máximos. Painel opcional em duas A4 por jogador, com quatro slots 66 × 92 mm e área para a ficha 210 × 148,5 mm. Corrigido enquadramento das figuras: recorte por alfa antes de dimensionar, evitando corpos minúsculos dentro de células quadradas. Testes físicos 19/19; geração sem estouros.

Ciclo 5: sete cenários contínuos novos produzidos, com revisão por planta vetorial exata. Veículos e tanques foram reduzidos/recompostos para não atravessar limites. Conectores são limpos por máscara vetorial de 14 mm e a geometria vem exclusivamente do catálogo. Comuns: quatro folhas; seis variantes opcionais de quatro folhas. Nenhum lado B foi imposto: todos os módulos continuam disponíveis simultaneamente. Abrigo 0.3 preservado por já conter comunidade ilustrada e grade administrativa de adjacências. Revisão de composição corrigiu o jardim central do condomínio que atravessava quatro zonas; arranjos separados substituíram essa única composição. Piso e móveis seguem ilustrativos, geometria funcional é vetorial.

Ciclo 6 concluído: alternativas separadas duplex e colagem, calibração própria, guia ilustrado de três folhas e bases de organização opcionais. Índices gerados dos PDFs, com tamanho/orientação/método/cópias/substituições. Contagem confirmada: A 25+33=58; B 33+39=72. Guia inicial herdado continha pasta antiga inexistente: corrigida apenas a seção de impressão para os dois métodos. Referências mecânicas e demais páginas preservadas.

Revisão independente final: nenhum crítico. Importante: pacote de fontes omitia mapa antigo usado na prova e não gerava amostra; teste do ZIP real falhou antes da correção. Menor reclassificado importante: alvos A/B da calibração manual não poderiam coincidir fisicamente por ficarem fora do eixo central; isso impediria seguir a instrução de montagem. Teste de coordenadas do PDF falhou antes da centralização dos alvos. Correções em uma passagem: gerar amostra em --step all, incluir PDF antigo nas fontes e centralizar A/B nos dois lados. Nenhum efeito ou probabilidade alterado. Revisão não julgou impressão física, registro/opacidade da impressora, semelhança facial exaustiva nem extração de arquivos ainda em empacotamento. Esses limites serão mantidos; dependências e extração serão conferidas pelo autor.

Correções finais verificadas: dois testes novos falharam (dependência real do ZIP e alinhamento dos alvos impressos) e passaram após correção; suíte 21/21. Nenhum achado menor ficou adiado. Falta somente finalizar ensaio de reconstrução limpa e push. Cenas opacas exportadas em JPEG 95 na resolução nativa; originais PNG permanecem editáveis. Sem alteração de texto vetorial, regras ou geometria.

Ciclo 7 concluído: cinco ZIPs de fontes extraídos em pasta limpa, build --step all, validação e provas executados na sequência documentada. Resultado: 1.922/1.922, 300 páginas e 23 evidências; suíte 21/21 no projeto. Índices de navegador por pacote, ZIPs testados sem erro, sem referência privada/cache Python. Reconstrução registrada em output/edicao-fabricacao-v0.4/reconstrucao.json. Entrega por DOWNLOADS_0.4.md; todas as opções completas de jogo cabem no GitHub. Não houve impressão física, montagem física ou playtest humano. Próxima ação após commit: push -u origin arte/pnp-fabricacao-v0-4 e conferir links remotos, sem merge.
