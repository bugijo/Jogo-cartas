# Acabamento 0.5
Base verificada: 9db928d, árvore limpa, fetch sem trabalho posterior. Branch arte/pnp-acabamento-v0-5. Pedido do proprietário nesta sessão é a especificação e autoriza os cinco ciclos sem pausas de aprovação.

Escopo: mesmas 114 cartas, mesmos dados congelados, 58 folhas duplex e 72 manuais. Peões, abrigo e fichas compactas preservados. Painel opcional continua duas folhas por jogador e quatro cargas.

Direção: molduras originais de equipamento de campo, caixas claras de leitura; arte maior nos efeitos curtos e menor nos densos. Superfície de mochila/prancheta ilustrada em vetores, não simulação de mecanismo. Mapas em composição global: pisos, setores, mobiliário, iluminação e desgaste vetoriais, sem reutilizar fundos de 70 ppi. Fronteiras de zonas conectadas discretas; paredes em conexões proibidas. Centros e vãos de 14 mm, portas e bloqueios preservados. Isso muda o desenho da fronteira permitida, não a conectividade ou a regra de movimento. Objetos não criam cobertura/obstáculo.

Referência: zombecide.zip não disponível; somente os cinco PDFs já auditados na 0.4. Não os incorporar. Geração integrada de imagens usada para itens em pranchas 2×2; rostos canônicos não são regenerados. Nenhuma API paga.

Ciclos: 1 amostra; 2 cartas; 3 painel; 4 sete tabuleiros; 5 inspeção, pacotes, push sem merge. Fontes e arte 0.4 intactas. Cada ciclo: gerar, inspecionar, corrigir, validar, checkpoint e commit.

Ciclo 1: amostra real de nove cartas, painel e quatro módulos do mercado gerados sem estouro. Fontes mecânicas não alteradas. Inspeção encontrou objetos de peças atravessando a divisão da prancha; nova composição com margens solicitada antes de replicar. Mercado usa composição global e mobiliário vetorial que atravessa limites conectados sem criar bloqueios. Três contratos dos PDFs falharam antes da geração completa (mapas vetoriais, contagens, peões preservados).
