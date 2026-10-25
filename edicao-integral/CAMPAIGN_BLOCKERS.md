# Bloqueios verificados da sequência completa

## Estado ativo — checkpoint após `fb48fda` e revisão de regras

- O replay `verify_continuous_campaign.py` continua a certificar A Cisterna H2
  seed 22 e fecha corretamente o dia após o Mercado. Ele começa Estação no dia
  seguinte, registra contato provisório com Célia, sofre uma derrota local por
  incapacitação e aplica a retirada de emergência canônica. O grupo retorna
  ferido e fatigado, perde a carga obtida e deixa Célia no destino; nenhum
  retorno normal ou recrutamento completo é forjado. `verified_victory` continua
  somente no arco da Cisterna.
- O relógio regional compartilhado e o máximo de uma expedição/dia estão
  ativos; viagem e rodada tática consomem segmento, e as posições 9–10 causam
  fadiga conforme `RULES.md` §5. Surgimento inicial, pressão e baralho Horda
  persistente estão conectados ao encontro tático. A frequência de hordas
  específicas do segundo arco e o baralho de Viagem regional não têm regra de
  conteúdo aprovada e permanecem sem implementação.
- A API de retirada de emergência regional está implementada e testada. O
  primeiro bloqueio atual é de campanha/estratégia: a adaptação de contato de
  Célia na Estação termina em derrota local e o replay não pode continuar como
  se o grupo tivesse regressado com ela.
- Revisão de `RULES.md` §25 encontrou recuperação noturna ausente: agora o motor
  reduz fadiga após refeição completa e cura um ferimento adicional apenas de
  heróis/NPCs no abrigo que não trabalharam nem saíram. Trabalho operacional e
  saída ficam no save e são apagados ao fechar o dia. Isso não substitui o
  registro integral de alocação de civis/crianças/cães, ainda ausente.
- `World.validate()` agora rejeita fadiga fora de 0–3 também em saves; o primeiro
  turno protegido do Mercado mantém Hordas anunciadas pendentes sem avançá-las.
  Ambas as correções têm regressões dedicadas.
- A automação médica só cura heróis presentes no abrigo; NPC que saiu não pode
  aplicar cuidado remoto ao encerrar o dia.
- O motor regional ainda não revela cartas de Viagem por trecho nem automatiza
  encontros/emboscadas regionais com cadência canônica. `far=3` continua sem
  correspondência aprovada a rota longa canônica de dois trechos por sentido.
- Se um cartão de acesso ou transmissor for perdido em emergência, ele permanece
  único no destino; a API de autorização/recuperação bloqueia uma segunda cópia.
  A ação para recolher esses dois itens do chão ainda não foi definida, então
  essa rota também falha fechada.
- O contato físico de Célia está codificado como adaptação em
  `data/regional_campaign.json`, não como regra canônica. O ponto Estação/O2
  exige atravessar uma zona com Bruto, e o replay demonstra incapacitação antes
  do retorno; o resgate não é considerado completo.
- Uma tentativa diagnóstica com apenas Lia na expedição à Estação também chegou
  a Célia no relógio 6/10, mas o Bruto a incapacitou na ativação seguinte, no
  segmento 7. Essa rota exploratória não foi salva como replay de campanha nem
  processada como conclusão; não prova que todas as estratégias de Estação falhem.
- O conflito de combustível continua sem decisão: §64 cobra 2 por trecho; a
  viagem militar experimental é `far=3` (12 ida/volta pela van), enquanto
  `EXP-MIS-104` fixa 6. Posto O1 traz 8 cartas finitas; O2 não explicita
  combustível. Nenhuma quantidade foi criada. Ver a matriz atualizada em
  `TACTICAL_FUEL_AUDIT.md`.

O texto restante abaixo é o registro histórico de bloqueios anterior ao replay
com relógio e às alterações deste lote. Use este estado ativo como referência.

Estado na branch experimental, após o porte parcial de `cistern02.py`. Nenhum bloqueio foi contornado por concessão de combustível, peças, armas ou flags no fluxo normal.

**Correção após o remoto `8700073`:** a primeira versão de
`integrated_campaign.py` criou um atalho: `collect_part()` entregava peças por
dois segmentos sem expedição e `complete_cistern()` aceitava uma vitória apenas
candidata, perdia estado e criava pistas. Ambos os métodos foram bloqueados
até haver recibos táticos e migração testada. Os testes anteriores daquela
integração não constituíam campanha legal. Ver `TACTICAL_FUEL_AUDIT.md`.

1. **A Cisterna ainda não certifica vitória.** A preparação, 2.497 vínculos, refeição individual, relógio de dez segmentos, filtro A/B/C, parte de acolhimento, intenções e cercos têm código e testes. `Tactical02` cobre entrada/saída, PA, portas, combate, peças, lotes e Saque regional finito, com carga/retorno e revisitas persistentes. Faltam Viagem/emboscadas, resgates ligados ao mapa, equipamentos achados, trabalhos civis, promessas, todos os eventos e a fila final. `receive_part()` e `rescue()` continuam entradas administrativas quando chamadas diretamente. `close_chapter()` retorna `candidate_victory`, que o segundo arco recusa. A flag `cistern_complete` isolada também é recusada.
2. **Combustível insuficiente no catálogo experimental.** Só a Oficina gera combustível: três buscas urbanas únicas, uma unidade cada. Recuperar o furgão na Oficina consome duas para voltar; restaria no máximo uma, enquanto a viagem militar longa exige seis para ida e volta. O teste `test_catalog_fuel_cannot_pay_recovery_and_military_trip` reproduz a sequência com todo o combustível da Oficina, certificado sintético apenas para isolar a economia e falha no acesso militar. O kit 0.2 prevê oito Combustíveis no Posto e recupera a van lá, mas o motor experimental não tem Posto regional e usa a Oficina. **Adaptação proposta, não aplicada:** portar Posto, combustível e recuperação conforme `CAMPAIGN.md`/`RULES.md`, preservando os IDs experimentais existentes até uma migração explícita de estado.

   Atualização: o núcleo tático 0.2 já permite retirar as oito cartas finitas
   do Posto e pagar o retorno da van com combustível carregado, sem gerar
   combustível no estoque. Isso **não** muda o bloqueio do motor regional de
   Última Transmissão: ainda não há migração de combustível/van nem teste da
   ida e volta militar com recursos legalmente obtidos.
3. **Os arcos têm modelos de personagens e estoque diferentes.** O kit 0.2 tem 12 fundadores possíveis — inclusive Téo e Célia —, civis, crianças, cães e cartas de quatro porções; `World` tem somente os dez protagonistas Lia–Yumi, 15 NPCs e contadores. Téo e Célia não têm ficha heroica equivalente no novo motor. Não existe transformação sem perda de identidade, ferimentos, vínculos e recursos. É necessário um esquema de estado comum ou uma migração testada antes de começar a Última Transmissão. A decisão sobre Téo/Célia não pode ser tomada silenciosamente: adicionar dois protagonistas à edição experimental ou restringir fundadores altera um dos escopos aprovados.
4. **A defesa final isolada não prova campanha.** O ensaio de 250 defesas usa certificado sintético, transmissor, portões e um pé de cabra por herói. Os resultados H2–H6 medem somente uma política naquele cenário. Ondas e mapa são experimentais; nenhuma revisão de equilíbrio foi aplicada. A edição física experimental tem zero PDFs novos.

Próxima unidade funcional: portar expedição 0.2 com a geometria já copiada do catálogo, relógio de dez segmentos e PA; registrar entregas de peças e lotes no estado `Cistern02` apenas depois de retorno legal. Em seguida, portar Posto/van/combustível e testar uma trajetória completa sem fixture sintética. Só então permitir emissão de `verified_victory` e transição automática.
