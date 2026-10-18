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
