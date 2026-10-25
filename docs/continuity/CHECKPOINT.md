# Checkpoint — campanha contínua Cisterna → Última Transmissão

Branch: `evolucao/zona-zero-sistema-v1`
HEAD remoto antes deste lote: `5d83b3760edbf36b44ba821e14e50af8af9c896d`
Commits funcionais publicados neste lote: `359ec46`, `cdc5b27`.
Main e kit físico 0.2 intactos.

## Evidência mais recente

- A Cisterna H2 seed 22 continua como regressão: 5 dias/noites, 3 expedições, 98 decisões e `verified_victory`.
- Migração atômica/idempotente por `transition_to_last_transmission()` preserva o arquivo integral, digest e quantidades com equivalência. Saves JSON são editáveis; o digest não é autenticação.
- Seed 22 migra Lia e Mara, o adulto R01, recursos e os recibos. A Bateria não foi retirada na Cisterna: segue como objetivo único na Oficina O1, não como recurso gratuito.
- O Posto está ativo em `EXP-LOC-07` ligado a `gas_station_02`. Cada uma das 8 cartas de combustível é retirada individualmente por 1 PA no O1. A van canônica tem 6 lugares/12 cargas, exige inspeção, Bateria e teste Técnica 6 por 2 PA. A falha não consome Bateria; sucesso consome. `EXP-VEI-01` não substitui a van na campanha migrada.
- O replay contínuo parcial `verify_continuous_campaign.py` realiza 62 registros resumidos após a Cisterna: rota de rádio e cartão, recuperação da Bateria por movimento/porta/PA, oito cartas do Posto, inspeção e reparo determinístico, retorno com a van e gate militar. Isso não equivale a 62 ações atômicas. O controlador renova PA por `TacticalGame.activate()`, nunca por `World.begin_round()`.
- Resultado seed 22: Lia falha no teste com 1; Mara passa com 5 + Técnica 3. Retorno médio com a van consome 4 das 8 cartas do Posto. Ficam 7 unidades no abrigo (3 Oficina + 4 Posto). O gate da instalação militar exige 12 na especificação canônica regional (`far=3`, dois sentidos, 2/segmento), rejeita sem mutação, e registra déficit 5.
- Busca regional em campanha migrada agora exige encontro tático, presença em zona de busca e 1 PA; cartão de acesso é carga única e precisa voltar ao abrigo. O replay salva/restaura o estado regional integral.

## Limite e bloqueio

Não há campanha integral Cisterna → defesa final. O catálogo regional atualmente modelado fornece no máximo 11 combustíveis (3 Oficina + 8 Posto) antes de retorno, abaixo das 12 unidades do modelo canônico; a seed deixa 7 depois de voltar do Posto. `data/last_transmission.json` ainda codifica custo 6, divergente de `RULES.md` §64. `CAMPAIGN.md` não define se o “lote de cada provisão” do Posto O2 inclui combustível nem a quantidade; por isso, 11 é teto do modelo, mas não prova o soft-lock canônico enquanto essa frase estiver ambígua. Nenhum custo foi reduzido e nenhum combustível foi criado.

Outras limitações de paridade: recrutamento do pesquisador ainda não tem contato narrativo; a pesquisa/estação e algumas operações regionais continuam protótipos, sem ligar todo o relógio de dez segmentos, eventos/emboscadas/hordas da regra 0.2. A cena regional não é simulada como combate completo em todos destinos. Portanto, o replay de 62 registros demonstra a ponte de estado e ações implementadas, não campanha física integral legal.

Nenhum `verified_victory` foi emitido para Última Transmissão. Transmissor e defesa final não foram alcançados. Não ocorreu impressão física nem playtest humano.

## Próxima decisão técnica

Antes de buscar a defesa final, resolver explicitamente a equivalência de combustível entre regional `far=3`, o custo experimental de seis e `RULES.md` §64 (2 por trecho), sem mudar números silenciosamente. Alternativas a avaliar na fila: formalizar uma unidade regional diferente com regra escrita e impacto; ou identificar uma fonte/mecânica de combustível já autorizada pelo conteúdo atual. A oferta atual demonstra déficit, não prova isolada de equilíbrio global.

## Verificação local desta unidade

- Regressão completa: 253 testes passaram, incluindo as duas regressões independentes.
- `validate_data.py`: passou (127 IDs únicos; 10 heróis; 70 habilidades; 15 NPCs; 7 locais; 8 mapas táticos).
- `verify_campaign_player02.py`: `verified_victory`, 5 dias/noites, 3 expedições, 98 decisões.
- `verify_continuous_campaign.py`: replay reproduzível chega ao gate militar e para sem mutação por falta de combustível; 62 registros resumidos após a Cisterna.
- `compileall` e `git diff --check`: passaram após as alterações de código e documentação.
- Auditoria adversarial encontrou e os testes confirmaram correção de dois erros: save/load de cartão de acesso em expedição militar e contagem de carga especial durante busca.
- Revisões independentes somente leitura nesta sessão: unidade/fontes de combustível e revisão de ponte/persistência. Confirmaram a divergência de custo, a ambiguidade do Posto O2 e que não se deve afirmar legalidade física completa.

Retomada:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python edicao-integral/verify_campaign_player02.py
python edicao-integral/verify_continuous_campaign.py
python -m unittest discover -s edicao-integral/tests -q
```
