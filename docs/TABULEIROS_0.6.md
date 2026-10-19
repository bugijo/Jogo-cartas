# Tabuleiros 0.6

Base real b99c470, limpa; fetch sem alterações posteriores. Branch arte/pnp-tabuleiros-v0-6. Escopo autorizado: arte e fabricação dos sete tabuleiros e seis diagramas. Nenhuma alteração em cartas, retratos, peões, painel, abrigo, regras ou campanha.

Fonte funcional: catálogo e map_layouts conferidos iguais, exportados em content/production/geometry_0.6.json. Hashes de regras, catálogo, geradores 0.5 e PDFs anteriores em baseline_0.6.json. Cada destino mantém 16 zonas, 21 conexões e cinco portas, com seus próprios bloqueios. Estação é de tratamento de água (fonte principal e missão Bomba/Membrana), não ferroviária.

Composição escolhida: cena global de 554×380 mm antes do corte; pisos e arquitetura, mobiliário, histórias de uso, geometria, sinais e corte separados. Setores seguem a circulação e não viram quadros por zona. Objetos principais nativos a pelo menos 215 ppi de desenho; vetores elaborados completam gôndolas, equipamentos e pisos, sem esticar imagens. Sem sujeira aleatória ou novas coberturas. Áreas de passagem têm proteção independente da ilustração.

Mercado piloto: acesso/estacionamento no alto à esquerda, recebimento no acesso de serviço, caixas junto à entrada, corredores de mercearia, padaria, hortifruti, frios e estoque. A composição é adaptada às portas reais. Móveis não são obstáculos; os marcadores funcionais indicam os únicos achados e objetivos.

Diagnóstico concreto de impressão: na 0.5 os diagramas passavam bloqueios do destino ao desenho; os módulos grandes não passavam esse parâmetro. A 0.6 deve imprimir nos módulos os bloqueios já previstos nas regras/catálogo, sem mudar nenhum estado ou custo. O mapa comum continua genérico: portas e bloqueios do destino são indicados no diagrama e pelos marcadores existentes.

Ciclos: 1 diagnóstico/planta/mercado; 2 demais mapas; 3 impressão/econômica/índices; 4 QA/reconstrução/pacotes/push sem merge. Preservados devem ser copiados byte a byte, nunca regenerados.

## Ciclo 1 — revisão direta do mercado

Comparação real em evidencias/MERCADO_04_05_06.jpg, extraída das quatro A4 de cada versão. Cinco aspectos revistos: (1) estacionamento, caixas, padaria, hortifruti, frios e recebimento são reconhecíveis; (2) produtos e histórias de uso substituem emblemas e gôndolas genéricas, sem entulhar circulação; (3) paredes, fronteiras, soleiras e X de bloqueio são distintos; (4) áreas livres têm função de circulação e colocação, sem acrescentar obstáculos; (5) pisos e alguns conjuntos comerciais atravessam zonas e junções. Esta é revisão do autor, não aprovação estética do proprietário nem teste físico.

Correções do piloto: gôndola e caixa se sobrepunham; hortifruti e expositor também. Foram separados sem mover pontos funcionais. Dois recortes continham fragmentos de outro quadrante, eliminados pelo enquadramento por componentes de alfa (análise em miniatura; pixels impressos continuam nativos). Cinco pranchas e a do mercado receberam correção da projeção; gôndolas novas têm conteúdos distintos. Sombras vetoriais com transparência em forms produziam avisos de recurso em leitores: substituídas por tons sólidos claros; alfa nativo das imagens mantido. Materiais de piso são atlas nativo, repetido em coordenadas globais com bordas espelhadas; a econômica omite essas texturas. Não se alega detalhe novo por ampliação.

Piloto gerado em duas edições, quatro folhas cada, assinatura de fontes atual conferida e renderização sem avisos. As sete plantas funcionais foram geradas antes da arte. Regras, dados e 0.5 continuam intactos. Os testes do conjunto completo ainda aguardam os demais mapas, conforme a etapa seguinte.

## Ciclo 2 — sete ambientes
Os seis destinos e os comuns foram montados digitalmente em duas edições. Revisão direta removeu fragmentos de atlas no controle da estação e corrigiu recortes da oficina que atravessavam a divisão nominal da prancha. Uma bancada individual em vista superior substitui o agrupamento insuficiente; não foi acrescentado componente de jogo. Comuns receberam recepção, trabalho e pátio mais reconhecíveis, sem afirmar serem a planta detalhada de todos os destinos. Dois carrinhos foram afastados das soleiras. Mesmas 16 zonas, 21 conexões, cinco portas e bloqueios do catálogo. Nenhum móvel cria cobertura ou recurso.

Conferência final: 7.536 verificações, 68 páginas alteradas e 52 entradas PDF preservadas byte a byte. Nove testes próprios aprovados após as correções; a suíte completa de 38 passou durante a produção, sem modificar as fontes dos testes anteriores. Sete remontagens comparadas às cenas globais com diferença média inferior a 0,5/255 (antialias), registrada em encaixe.json. Raster principal mínimo 215 ppi, medido no PDF. Sem exceções abaixo da meta nos módulos.

## Ciclo 3 — fabricação
Mesmo corte 277×190 mm, quatro A4 por tabuleiro, união sem sobreposição e códigos dentro do corte. Diagramas usam miniatura de A–C a 200 ppi e geometria/rótulos vetoriais próprios: a redução é somente da referência de montagem, não dos tabuleiros. Econômica omite materiais raster do piso e preserva os objetos/sinais em cinza. Mesmas 58 folhas duplex e 72 manuais.

O primeiro ZIP ilustrado de mapas excedeu 100 MiB. A incorporação agora usa apenas o recorte nativo utilizado de cada PNG, sem reamostragem, JPEG ou alteração do original. O teste de extração RGB da bancada no PDF confirma pixels idênticos ao recorte fonte. Os dez testes próprios passam; o mínimo físico continua 215 ppi. A comparação digital de montagem usa decodificação limpa do renderizador para não comparar imagens em estágios distintos do cache de redução; o limiar de aprovação não foi aumentado. Diferenças medidas e resolução de análise constam de encaixe.json. Isto não modifica a arte nem comprova impressão física.

Atualização sem cartas: ZIP de mapas contém 34 páginas oferecidas, mas reimprimir quatro comuns OU quatro de um destino basta para trocar o tabuleiro. Seis diagramas novos são substitutos consultáveis na tela. Variantes não estão duplicadas nos ZIPs de extras preservados. Fontes e provas têm pacotes separados; nada temporário ou privado é distribuído.

## Ciclo 4 — reconstrução e distribuição
O primeiro ensaio de fontes encontrou dois PDFs de provas 0.5 fora das pastas de edição, exigidos pelo congelamento. Foram incluídos nas fontes-base; o gerador de pacotes agora exige cobertura de todas as 81 dependências. Novo ensaio iniciado em outra pasta vazia: build, validação, provas e inventário concluídos; dez testes próprios aprovados, 68 capturas idênticas e 24 entradas de geração idênticas por SHA-256. Relatório em reconstrucao.json. Os arquivos de impressão são separados das fontes e das provas, sem caches ou referência privada. A distribuição será pela branch própria, sem merge.
