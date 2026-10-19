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
