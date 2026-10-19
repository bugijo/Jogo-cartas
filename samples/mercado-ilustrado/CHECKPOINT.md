# Checkpoint — amostra do mercado

Base conferida: `ec071e1`, limpa, sem commits posteriores encontrados no fetch.
Branch: `arte/mercado-amostra-ilustrada`. Alterações restritas a esta pasta.

Concluído nesta exploração: inspeção dos cinco PDFs acessíveis; comparação 0.4/0.5/0.6; congelamento da planta; duas propostas nativas; seleção B; duas rodadas de edição; composição vetorial independente; PDF em quatro A4; detalhe físico; contato, comparação, ocupação com peças atuais e relatório. Nada aplicado a outros mapas. Nenhum arquivo privado incorporado.

Parada deliberada no limite solicitado de duas propostas e duas correções. Não houve limite de quota informado pela ferramenta. Amostra entregue para avaliação, **não aprovada para substituir o mapa atual**.

Pendências artísticas concretas:
1. Liberar visualmente a conexão Z15–Z16 das caixas de bebidas.
2. Corrigir a inclinação residual dos refrigeradores e móveis periféricos.
3. Produzir resolução nativa suficiente: atual 1514×1039, 69,4 ppi; meta >=150 ppi não alcançada.

Não iniciar aplicação aos outros destinos sem avaliação do proprietário. Se retomada autorizada, usar `originais/CORRECAO_2_ESCOLHIDA.png` e `fontes/geometria.json`, seguindo a seção de retomada do relatório. Não alterar as regras nem reduzir a escala do tabuleiro para mascarar a resolução.

Reprodução: `python samples/mercado-ilustrado/fontes/build.py`. O script só escreve nesta pasta. Verificação automática valida dimensões, fontes, planta, presença da imagem e junção; não aprova a estética. Não houve impressão física nem playtest humano.
