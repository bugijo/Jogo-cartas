# Prova adicional: posto de combustível

[PDF, comparação e contato das conexões](samples/kit-pos-apocaliptico/lote-08-posto/RELATORIO.md). Nove seções nativas e três reparos; composição a 175 ppi. Restam discretas faces laterais estilizadas, temperatura de luz mais quente que Mercado B e possível transição de textura vista ampliada. Impressão física pendente.

---

# Lote 07 — moradores nas cartas

[Comparação das cartas de moradores](samples/kit-pos-apocaliptico/lote-07-moradores/provas/COMPARACAO_MORADORES_1.jpg): oito rostos/grupos reconhecíveis, mais desgaste e no mínimo 589,04 ppi nos retratos; crianças e cão permanecem informação textual como antes.

---

# Lote 06 — itens e cartas

[Oito itens adicionais](samples/kit-pos-apocaliptico/lote-06-itens/RELATORIO.md): 29 IDs com cenas novas em duas pranchas nativas, 351,37 ppi mínimos; textos e versos iguais aos da versão anterior.

---

# Prova adicional: estação de tratamento

[Relatório e PDF](samples/kit-pos-apocaliptico/lote-05-estacao/RELATORIO.md). Ambiente contínuo, 175 ppi, quatro A4, planta canônica preservada; seis interferências de arte localizadas e corrigidas antes da prova. Ainda requer impressão física e avaliação artística.

---

# Atualização — provas pós-apocalípticas, lotes 02–04

[Resultados e pendências reais](samples/kit-pos-apocaliptico/LOTES_02_04.md). As antigas provas de hospital/oficina não são o acabamento novo: composições contínuas estão em lote-02-composicao. A aprovação artística do kit inteiro continua pendente.

---

# Atualização — provas pós-apocalípticas

[Relatório atual](samples/kit-pos-apocaliptico/VISUAL_QA.md): quatro lotes iniciais + hospital, comparações reais de PDFs, resolução efetiva, 39 testes existentes aprovados e verificações direcionadas. Cenários ainda não aprovados como composição final. Sem impressão física ou playtest.

---

# Conferência visual e de produção — edição 0.3

Escopo: acabamento do kit Comece Aqui / Duas Pessoas, regras 0.2. Base real 9c38aa5, que acrescentara ZIPs ao b407e84. Branch própria arte/pnp-edicao-ilustrada-v0-3; edição anterior preservada, sem merge. Os quatro ciclos artísticos estão registrados no histórico; ciclo final reúne provas, arquivos e publicação.

## Conteúdo e papel

Cada edição: 18 PDFs, 72 páginas, 25 folhas iniciais + 33 de complemento = 58 A4. Mesmos 114 IDs de cartas, 14 fichas selecionadas, 45+12 marcadores e 12 divisórias. Os dois pés de cabra únicos continuam nas fichas. Catálogo de 324 cartas e 24 heróis, regras, campanha, guia e seleção 0.2 permanecem byte a byte iguais; não houve reequilíbrio. PDFs anteriores não foram substituídos. Versão econômica conserva toda a seleção.

Cada kit básico não inclui extras. Estes são separados: seis variantes de mapa × quatro folhas = 24 opcionais por edição, mais 12 folhas com os 24 heróis já existentes. Variantes substituem os módulos comuns, não acrescentam zonas ou conexões. Nenhuma variante é obrigatória.

## Verificação executável

`python src/validate_illustrated.py` grava contagem, resultados e detalhes em output/edicao-ilustrada-v0.3/verificacao.json. Confere hashes da base, seleção/IDs, efeitos e nomes impressos de cada carta, atributos/habilidades/progressões das fichas, quatro cargas, dimensões, A4, fontes utilizadas incorporadas, texto dentro do papel, símbolos e família dos versos, manuais e guia preservados, conectividade e largura de aberturas. Os 14 testes existentes passaram; mudanças artísticas posteriores não modificaram lógica.

Mapas mantêm exatamente os 21 conectores por destino, cinco portas e bloqueios próprios: mercado/hospital 7–8, oficina 3–7, posto nenhum, condomínio 9–13, estação 7–8 e 13–14. Entrada/saída Z1, buscas Z5/Z12, objetivos Z7/Z14, surgimento Z16. Corte 277 × 190 mm por módulo, união sem sobreposição em 554 × 380 mm. Paredes são espessas e aberturas centrais têm 14 mm. Objetos decorativos ficam fora dos eixos de passagem e não têm cobertura/obstáculo. Montagens têm diagrama jogável separado da cena de ambiente.

Cartas 63 × 88 mm, nove por A4, intervalo 2 mm, grade 193 × 268 mm; margens 8,5 / 14,5 mm. Conteúdo essencial a 4 mm do corte. Frente/verso alternados; colunas refletidas, linhas preservadas. Somente retrato de cartas e calibração usa duplex na borda longa. Demais documentos são de uma face. Intenções têm verso comum sem IDs ou variação por conteúdo.

## Revisão visual

Todas as páginas obrigatórias e extras são renderizadas em output/edicao-ilustrada-v0.3/renders/, com contatos em evidencias/. Ali ficam os mapas montados, junções, sobreposição de folha com versos de famílias diferentes, intenção ampliada, calibração, divisórias, ficha, painel e comparações antes/depois. Inspeção das amostras corrigiu: abrigo em grade substituído por cena contínua; etiquetas estreitas; números minúsculos das montagens; texto Verificado quebrado; símbolos de função trocados por caixas decorativas; repetição desnecessária da van em viagens; Intenções passaram a usar objetos/ambientes para não sugerir que um herói nomeado é sempre infiltrado; recorte das cenas; manchas decorativas e fundos brancos dos objetos no mapa.

Econômica: imagens em cinza clareadas, pisos quase brancos e vetores convertidos para cinza. Todos os mesmos textos e componentes. Não se promete percentual real de economia de cartucho: depende da impressora. Fontes de regras em cartas 9,5 pt, fichas 9,5 pt; IDs/legendas podem ser menores. Títulos e arte maiores nas cartas curtas; cartas densas mantêm espaço integral de leitura.

## Referência externa e ponto de regra preservado

O proprietário indicou a pasta Drive 1htPUeVNxuYl5sHdkgdIePV0hOGblYO5N. Com a skill Google Drive, foi possível listar o atalho ZOMBICIDE; a leitura desse atalho retornou HTTP 403. Não se afirma ter visto as cartas da pasta. Preferências descritas pelo proprietário orientaram hierarquia de título/arte/efeito; nenhum material dessa pasta foi copiado, integrado ou redistribuído.

A garagem usa dois terrenos adjacentes no manual, apesar de o abrigo também funcionar como painel administrativo. Para não reinterpretar a regra, a grade original T1–T12 foi preservada em miniatura no novo painel; a cena não define novas adjacências. Nenhuma contradição foi resolvida por mudança de custo, probabilidade ou efeito.

## Limitações reais

Não houve impressão física, teste de opacidade com papel real, montagem física ou playtest humano. A simulação de duplex não garante o alinhamento da impressora do proprietário. Nenhuma revisão visual ou teste automático comprova diversão ou equilíbrio. A contagem de folhas foi verificada em PDF, não em uma impressora.

Retratos originais foram mantidos; resolução na ficha é aproximadamente 165 ppi. Objetos pequenos atingem cerca de 300 ppi nas cartas, mapas usam cerca de 170–210 ppi e abrigo cerca de 217 ppi. Não houve ampliação vendida como detalhe novo. As imagens mantêm leitura na inspeção digital no tamanho de componente, mas uma prova impressa é recomendada antes de toda tiragem. Nenhum asset necessário para jogar a seleção de 58 folhas está ausente; as outras 210 cartas da caixa antiga continuam preservadas na edição anterior, não fazem parte deste kit.

## Resultado final registrado

1.423 verificações digitais passaram sem falhas; 14 testes de regras existentes passaram. Foram renderizadas 216 páginas (144 obrigatórias nas duas edições e 72 de extras). As 108 páginas da econômica foram verificadas canal a canal como cinza. Todos os dez contatos, sete mapas montados de cada edição e amostras ampliadas foram inspecionados. Comparação normalizada dos 12 versos de Intenção por edição: diferença média máxima menor que 0,00003 numa escala RGB de 0 a 255, atribuível à rasterização em posições distintas. Evidência em duplex_visual.json. Mapas e abrigo econômicos têm menor cobertura escura na renderização; isso não mede cartucho.


## Fabricação 0.4 — verificação final

Base ccff9c8, nova branch arte/pnp-fabricacao-v0-4. Foram conferidos hashes das fontes mecânicas, todos os efeitos de 114 cartas nos dois métodos/edições, IDs únicos, contagens reais dos PDFs, A4, fontes incorporadas, texto dentro da página, geometria do catálogo e aberturas de 14 mm. Resultado registrado em output/edicao-fabricacao-v0.4/verificacao.json: 1.922 verificações, sem falhas, 300 páginas renderizadas, econômica sem páginas coloridas. Efeitos a 9,5–10 pt. Cartas 63 × 88, grade 193 × 268, margens 8,5/14,5 mm e intervalo 2 mm.

Inspeção visual: contatos de todas as páginas em ambas as edições; amostra de nove cartas diferentes; Espingarda e Jana, densas; frente/verso sobreposto; peões de 24 heróis e três tipos inimigos; rede e simulação digital; painel com ficha e cartas reais; abrigo preservado; sete mapas montados e junções. Corrigidos: medição real da altura dos efeitos, enquadramento dos peões, guia com pasta antiga, móveis cruzando limites (tanque, jardim central e carro da oficina), dependências de prova nas fontes e alvos de calibração manual. Na prova do painel, o papel é tratado como opaco para não deixar o texto-guia transparecer.

Revisão independente verificou invariantes, 19 testes iniciais, manifestações/hash, dimensões e amostras dos métodos. Encontrou dependência de fontes ausente e calibração manual impossível de alinhar pelos alvos; ambos receberam testes que falharam antes da correção. A revisão não julgou semelhança facial exaustiva, montagem física, registro/opacidade da impressora e extração ainda em empacotamento. Fontes e extração final são conferidas separadamente pelo autor.

As cenas opacas são exportadas em JPEG qualidade 95, sem reamostragem e nas dimensões originais; PNGs originais editáveis são preservados. Isso reduz arquivos sem rasterizar regras ou geometria. Mapas têm cerca de 70 ppi efetivos; não se alega 300 ppi nem detalhe acrescentado por ampliação.

Limites reais: não houve impressão física, recorte/colagem ou playtest humano, nem nova validação de equilíbrio. A simulação digital não garante registro duplex nem opacidade da impressora do proprietário. zombecide.zip não foi recebido; somente cinco PDFs/seis páginas, integralmente renderizados e inspecionados, sem tiles/tokens/spawn/folhas de peões. Nenhum componente privado foi incorporado. Não foram encontradas novas contradições mecânicas; regras 0.2 e campanha permanecem congeladas.

Nem todas as artes pequenas atingem 300 ppi efetivos: a resolução depende da prancha e do recorte original. A revisão digital mostrou os objetos reconhecíveis, mas isso permanece uma limitação de acabamento para impressão exigente; não foi ocultada por ampliação artificial. Todas as ilustrações necessárias desta seleção existem e estão integradas.

Reconstrução final do autor: extraídas as cinco partes de fontes em pasta limpa, executados build, validação e provas na ordem documentada. 1.922/1.922 verificações, 300 páginas e capturas produzidas; suíte 21/21. As correções de revisão não deixaram achados menores pendentes. Evidência em reconstrucao.json.


## Acabamento 0.5

Base 9db928d, branch arte/pnp-acabamento-v0-5. 4.798 verificações aprovadas, 29 testes e 300 páginas renderizadas. Na conferência final, uma saída de mapas antiga foi detectada; o build completo, as 300 renderizações e todas as provas foram refeitos. Um teste novo exige a planta global nos PDFs distribuídos. Conteúdo e IDs dos mesmos 114 componentes conferidos; hashes canônicos de regras/campanha/catálogo preservados; peões bons copiados byte a byte. Frente/verso e ambos os métodos mantêm 58/72 A4.

Resolução medida na transformação física de cada imagem do PDF. Mobiliário dos sete tabuleiros: mínimo 211,3 ppi; piso e arquitetura vetoriais. Não foi reutilizado o fundo de 70 ppi nem aplicada ampliação artificial. PNGs nativos e SVGZ disponíveis. Exceções de 300 ppi em artes antigas de cartas/rostos estão no CSV por arquivo/página/xref.

Inspeção: contatos das 300 páginas, armas e carta densa ampliadas, folha A4 com mesmos IDs nas duas versões, frente/verso, painel com cartas reais e ficha, sete mapas montados e junções, econômica em cinza e detalhe de mapa 100×100 mm em A4 real. Comparações ARMA_04_05, CARTA_DENSA_04_05, FOLHA_A4_04_05, PAINEL_04_05, MAPA_ANTES_DEPOIS e OFICINA_04_05 vêm dos PDFs finais. Não são mockups de componentes inexistentes.

Corrigidos: cortes de pranchas e fragmentos vizinhos; forms com acentos que desapareciam em leitores PDF; fonte dos valores estruturados; etiqueta que tratava materiais/munição/medicamento como porções. Esta última era erro de apresentação herdado: agora apenas comida/água exibem rendimento em porções. Efeitos integrais, recursos, custos e quantidades continuam os mesmos. Testes reproduziram a falha de forms, o fragmento e a etiqueta de unidade antes da correção.

Limites: sem impressão física, montagem física ou playtest humano; simulação digital não garante registro/opacity da impressora doméstica. Não há nova validação de equilíbrio ou diversão. Revisão direta do autor realizada. A tentativa de revisão independente não produziu parecer: o agente revisor ficou indisponível por limite de uso da ferramenta. A reconstrução limpa é registrada em reconstrucao.json.

Reconstrução limpa: oito partes de fontes extraídas juntas, build, validação e provas executados. 4.792 verificações aprovadas e 300 imagens renderizadas idênticas às da entrega. A diferença de seis verificações decorre dos arquivos de relatório já existentes no checkout completo. Na pasta limpa: 27 testes aprovados e dois testes históricos de distribuição 0.4 omitidos por não haver seu pacote/PDF não utilizado; no checkout completo, 29/29 passaram. Registro em output/edicao-acabamento-v0.5/reconstrucao.json.
<!-- TABULEIROS06 -->
## Tabuleiros 0.6
Base b99c470, branch arte/pnp-tabuleiros-v0-6. 7536/7536 verificações finais sem falhas; 68 páginas alteradas renderizadas. 52 entradas PDF preservadas byte a byte nas duas edições, sem regenerar cartas, painel, peões, abrigo ou regras. Mesmos 58/72 A4 e mesmas posições/conexões/portas/bloqueios. O parâmetro de bloqueio, omitido nos módulos grandes 0.5, agora é aplicado conforme o catálogo.

Inspeção direta: mercado 0.4→0.5→0.6, sete tabuleiros montados e econômica, emenda central, duas áreas de 100×100 mm em A4 real, ocupação máxima de bases e cenário com seis marcadores originais de 29 mm. Capturas vêm dos PDFs finais. Sete remontagens comparadas pixel a pixel com as fontes globais (encaixe.json); as diferenças de antialias são registradas. Cenas são compostas antes do corte. Soleiras de 18×18 mm ficam livres de mobiliário; vãos mecânicos continuam com 14 mm.

Correções: projeção e enquadramento de novas artes; fragmentos de atlas; duas sobreposições no mercado; carrinhos próximos de soleiras no posto/comuns; transparência vetorial em forms com recursos ausentes; miniaturas de preparação que carregavam resoluções desnecessárias e tinham números pequenos. Miniaturas agora usam somente ambiente A–C a 200 ppi, com D–E vetoriais e textos próprios. Mapas principais mantêm PNGs nativos sem exportação JPEG nem redução; mínimo físico 215.0 ppi. Textos do mapa são conferidos no recorte efetivo e na fonte global, sem atravessar emendas; texto invisível externo ao recorte de um form não é tratado como impresso.

Não se usa quantidade de testes como aprovação artística. A revisão é do autor. Sem impressão física, montagem física ou playtest humano. O ensaio de 30 bases usa 22×12 mm; não comprova 24 marcadores planos de 29×29 mm sem sobreposição. Esses marcadores e as bases não foram reduzidos. Não houve teste novo de equilíbrio/diversão.

Reconstrução final 0.6: cinco partes de fontes extraídas em uma nova pasta vazia; build, validação, provas, dez testes próprios e inventário executados na ordem documentada. Resultado 7.536/7.536, 68 capturas JPEG idênticas às da entrega e 24 entradas de geração comparadas por SHA-256. O primeiro ensaio encontrou duas provas antigas 0.5 ausentes: os pacotes foram corrigidos e a cobertura das 81 dependências congeladas agora é exigida automaticamente. Registro detalhado em output/edicao-tabuleiros-v0.6/reconstrucao.json. Isto valida a reprodução digital, não o registro da impressora ou a montagem física.
# Seleção pós-apocalíptica: auditoria digital atual

As 136 páginas selecionadas de componentes, sete mapas e cartas condicionais foram renderizadas em `kit-final-prova/auditoria/CONTATO_FINAIS_01.jpg` a `_09.jpg`. As dimensões, fontes de geometria e contagens constam do `FINAL_KIT_AUDIT.json`. As artes raster principais dos mapas têm 175 ppi efetivos; as artes novas das cartas do lote 10, mínimo 349,2 ppi. As correções de conexões localizadas do lote 11 estão documentadas em seu relatório. Verificação física de duplex, corte, contraste no papel e playtest continuam pendentes.

