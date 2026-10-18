# Acabamento 0.5
Base verificada: 9db928d, árvore limpa, fetch sem trabalho posterior. Branch arte/pnp-acabamento-v0-5. Pedido do proprietário nesta sessão é a especificação e autoriza os cinco ciclos sem pausas de aprovação.

Escopo: mesmas 114 cartas, mesmos dados congelados, 58 folhas duplex e 72 manuais. Peões, abrigo e fichas compactas preservados. Painel opcional continua duas folhas por jogador e quatro cargas.

Direção: molduras originais de equipamento de campo, caixas claras de leitura; arte maior nos efeitos curtos e menor nos densos. Superfície de mochila/prancheta ilustrada em vetores, não simulação de mecanismo. Mapas em composição global: pisos, setores, mobiliário, iluminação e desgaste vetoriais, sem reutilizar fundos de 70 ppi. Fronteiras de zonas conectadas discretas; paredes em conexões proibidas. Centros e vãos de 14 mm, portas e bloqueios preservados. Isso muda o desenho da fronteira permitida, não a conectividade ou a regra de movimento. Objetos não criam cobertura/obstáculo.

Referência: zombecide.zip não disponível; somente os cinco PDFs já auditados na 0.4. Não os incorporar. Geração integrada de imagens usada para itens em pranchas 2×2; rostos canônicos não são regenerados. Nenhuma API paga.

Ciclos: 1 amostra; 2 cartas; 3 painel; 4 sete tabuleiros; 5 inspeção, pacotes, push sem merge. Fontes e arte 0.4 intactas. Cada ciclo: gerar, inspecionar, corrigir, validar, checkpoint e commit.

Ciclo 1: amostra real de nove cartas, painel e quatro módulos do mercado gerados sem estouro. Fontes mecânicas não alteradas. Inspeção encontrou objetos de peças atravessando a divisão da prancha; nova composição com margens solicitada antes de replicar. Mercado usa composição global e mobiliário vetorial que atravessa limites conectados sem criar bloqueios. Três contratos dos PDFs falharam antes da geração completa (mapas vetoriais, contagens, peões preservados).

Ciclo 2 concluído: 114 cartas, quatro PDFs manuais e dois duplex por edição. Arte de armas e peças em pranchas 2×2; recortes por objeto corrigidos, sem fragmentos vizinhos. Efeitos mantidos a 9,5–10 pt e texto pesquisável. Validação dos mesmos efeitos/IDs e versos passou em ambas as edições; mesmos 58/72 A4.

Ciclo 3 concluído: duas A4 por painel, mesmos quatro slots 66×92 mm, área da ficha 214×152,5 mm. Superfície de tecido, costuras, fechos, molduras de papel e fichas de XP em vetores; espaços essenciais claros. Prova com ficha e quatro cartas de 63×88 mm não cobre títulos/estados. Econômica usa fundo claro e texto escuro no lugar de tecido escuro. Ficha compacta e retratos preservados. Contagem opcional: quatro folhas para duas pessoas.

Ciclo 4: a amostra inteiramente vetorial ainda era esquemática. A composição global foi mantida e recebeu seis pranchas originais de mobiliário, recortadas em objetos e aplicadas em coordenadas físicas, nunca um cenário pequeno ampliado. Pisos, arquitetura e fronteiras permanecem vetoriais. Limite de desenho usa pixels nativos e reserva ≥170 ppi; conferência no PDF exige ≥150. Partes de gôndolas, veículos, tanques, leitos e bancadas substituem os pictogramas, sem um quadro independente por zona. Não há remendos brancos nas passagens. Legendagem de fronteira, parede, soleira, porta e bloqueio atualizada nos diagramas, mantendo os mesmos dados. Falha real de renderização com nomes de forms acentuados foi reproduzida por teste e corrigida com IDs ASCII.

Revisão de corte: faixa de objeto vizinho no expositor foi reproduzida com o recorte antigo e removida pela seleção de grupos de alfa significativos; os pixels desenhados continuam sendo os nativos originais. Inspeção dos valores estruturados levou a aumentar sua fonte para 9,5 pt; a etiqueta de reserva foi abreviada para RESERVA: N carta(s) para caber na margem, mantendo o efeito completo e as mesmas quantidades no texto principal. Não são novos atributos nem resumo de regra.

Ciclo 4 concluído: sete composições globais montadas e revisadas. Geometria, centros, vãos, portas e bloqueios coincidem com o catálogo; pisos/arquitetura são vetoriais e raster nativo foi medido no PDF final acima de 150 ppi. Identificações M1–M4 também ficam dentro do corte. Cores e medidas não dependem da imagem gerada.

Ciclo 5: a inspeção das provas detectou PDFs antigos de mapas apesar da fonte atual. O teste de presença da planta global falhou com esses arquivos e passou após o build completo. Todas as 300 páginas e as 30 evidências foram regeneradas; 4.798 verificações e 29 testes aprovados. Menor densidade medida no mobiliário dos módulos: 211,3 ppi. A revisão independente ficou indisponível por limite de uso; não há parecer independente da 0.5. Revisão direta e reconstrução limpa documentadas nos relatórios.
