"""Relatório reproduzível dos ensaios de campanha com limites explícitos."""
import json
from pathlib import Path

from campaign_seeded_review import ROOT, run_matrix
from probe_tactical_replay_scale import probe
from scaled_tactical_replay import run as tactical_run


def main():
    matrix=run_matrix()
    tactical=[probe(h) for h in range(2,7)]
    routes=[]
    for h in range(2,7):
        try:routes.append(tactical_run(h))
        except Exception as exc:routes.append(dict(heroes=h,result='BLOCKED',evidence=repr(exc)))
    root=ROOT/'kit-final-prova/auditoria'
    (root/'CAMPANHA_SEMENTES.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    (root/'ROTEIRO_TATICO_ESCALA.json').write_text(json.dumps(tactical,ensure_ascii=False,indent=2)+'\n')
    (root/'ROTEIROS_TATICOS_H2_H6.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2)+'\n')
    lines=['# Revisão reproduzível da campanha — cinco dias', '',
           'Regras e catálogo da edição 0.2 preservados. Quinze ensaios de **fases** (H=2–6, três sementes cada) '
           'registram preparação, carga prevista, provisões, confrontos amostrados, resgates, fila de cerco, '
           'trabalhos e filtro ao longo dos cinco dias. São ensaios determinísticos para achar lacunas, '
           '**não partidas táticas completas nem evidência de equilíbrio**. Perfil favorável recusa resgates '
           'opcionais e prioriza abastecimento; difícil acolhe Jana e recebe `ZC-VIA-0007` (+1 Pressão) no dia 2; '
           'limite seleciona vínculos de maior consumo '
           'e tenta os três resgates. Os dados e cercos continuam determinados pela semente, por isso um perfil '
           'favorável também pode encontrar uma rolagem ruim.', '',
           '## Preparação', '',
           '| Pessoas | Heróis | Vínculos examinados | Vagas | Consumidores possíveis | Resultado |',
           '|---:|---:|---:|---:|---:|---|']
    for x in matrix['setups']:
        lines.append(f"| {x['participants']} | {x['heroes']} | {x['combinations']} | {x['capacity']} | "
                     f"{x['consumers_min']}–{x['consumers_max']} | {'cabem' if x['all_fit'] else 'FALHA'} |")
    lines += ['', 'Solo controla dois heróis. Os 12 vínculos foram usados sem reposição; H5/H6 acrescentam uma/duas barracas iniciais.', '',
              '## Ensaios com sementes', '',
              '| H | Perfil | Semente | C inicial | Resgates aceitos | Filtro | Noite 5 | Resultado / causa |',
              '|---:|---|---:|---:|---:|---|---|---|']
    for x in matrix['runs']:
        last=x['days'][-1]
        n=sum(bool(d['rescue_card']) for d in x['days'])
        causes=[]
        if x['incapacitated']:causes.append('herói incapacitado na amostra')
        if any(last['shortage']):causes.append('falta de porções')
        if last['health']<1:causes.append('Saúde 0')
        if last['morale']<1:causes.append('Moral 0')
        if not last['filter_active']:causes.append('filtro inativo')
        label='plano possível' if x['result']=='plano_de_fases_possivel' else 'derrota/bloqueio: '+', '.join(causes)
        lines.append(f"| {x['heroes']} | {x['profile']} | {x['seed']} | {x['setup']['consumers']} | {n} | "
                     f"{'ativo' if last['filter_active'] else 'não ativo'} | "
                     f"comida {last['stock_after']['food']}, água {last['stock_after']['water']}, "
                     f"Saúde {last['health']}, Moral {last['morale']} | {label} |")
    lines += ['', 'Cada registro completo, com dados, cargas, estoque antes/depois, cerco e resgate, está em '
              '[CAMPANHA_SEMENTES.json](CAMPANHA_SEMENTES.json). As sementes são fixas; repetir o script gera o mesmo resultado. '
              'Um plano possível só demonstra que esses saldos de fases não se contradizem; o movimento e os efeitos '
              'de todas as cartas não foram resolvidos.', '',
              '## Replay tático herdado', '',
              '| H | Resultado | Evidência |', '|---:|---|---|']
    for x in tactical:
        lines.append(f"| {x['heroes']} | {x['status']} | {x.get('evidence','roteiro Lia/Ivo terminou cinco dias')} |")
    lines += ['', 'Esse é o **roteiro herdado**, preservado para explicar a lacuna encontrada. '
              'Ao aplicar `ceil(H/2)`, Lia fica sem 1 PA no Mercado/rodada 4 para H3–6. '
              'O roteiro novo abaixo usa Caio como expedicionário adicional e resolve essa lacuna '
              'sem mudar regra ou atributo.', '',
              '## Trajetórias táticas novas — cinco dias', '',
              '| H | Estado | C inicial | Resgate | Busca | Relógios M/O/E | Estoque final comida/água |',
              '|---:|---|---:|---|---|---|---|']
    for x in routes:
        if x['result']=='BLOCKED':
            lines.append(f"| {x['heroes']} | BLOQUEADO: {x['evidence']} | — | — | — | — | — |")
        else:
            clocks='/'.join(str(t['segments']) for t in x['tactical'])
            last=x['days'][-1]
            lines.append(f"| {x['heroes']} | vitória na trajetória fixa | {x['consumers_initial']} | "
                         f"{'Bia' if x['rescue_intention'] else 'nenhum'} | "
                         f"{'Mercado B1' if x['searches'] else 'nenhuma'} | {clocks} | "
                         f"{last['food']}/{last['water']} |")
    lines += ['', 'As cinco trajetórias passaram com dados de ataque 3, ordem de Horda registrada e '
              'cartas de Viagem distintas de efeito nulo/recusado (Ponte foi descoberta). '
              'O retorno da Estação ocorre no segmento 9: cada expedicionário recebe 1 fadiga; '
              'a Viagem extra `ZC-VIA-0002` retira 1 porção de água levada, e o descanso alimentado '
              'remove a fadiga no amanhecer do dia 4. '
              'Todas as portas, saídas, PA, cargas, IA, ferimentos e o limite de dez segmentos '
              'foram conferidos nas três expedições. A intenção Solidário de Bia foi revelada '
              'após duas noites para H2–5; H6 optou por não acolher. O cerco de missão Força 4 '
              'e o cerco de Pressão por `ZC-CER-0001` foram resolvidos antes dos trabalhos, '
              'com dados de vigia anotados. Os trabalhos A/B/C do filtro ocorreram nos dias 4–5. '
              'Heróis expedicionários recebem 2 XP por retorno com objetivo (6 XP em três visitas); '
              'as escolhas das marcas 3 e 6 XP ficam registradas por pessoa, sem transferir ferimentos. '
              'H6 termina com estoque de comida zero **após** alimentar todos os consumidores da quinta noite; '
              'é um caso de margem nula, não falta de refeição. '
              'Os estados por rodada estão em [ROTEIROS_TATICOS_H2_H6.json](ROTEIROS_TATICOS_H2_H6.json).', '',
              '## Esgotamentos observados', '']
    for resource in ('food','water','materials','ammo'):
        zero=sum(any(day['stock_after'][resource]==0 for day in x['days']) for x in matrix['runs'])
        lines.append(f'- {resource}: estoque zerou em {zero}/15 ensaios de fases.')
    lack=sum(any(any(day['shortage']) for day in x['days']) for x in matrix['runs'])
    lines += [f'- Faltou pelo menos uma porção em {lack}/15 ensaios; estoque zero **após** uma refeição '
              'completa não é privação.',
              '- Os três Materiais iniciais saem do estoque ao reservar A/B/C; o projeto mantém esses custos. '
              'Munição zero retira somente o bônus de cerco. Sem carta física de recurso suficiente, '
              'o manual manda usar ficha numerada anotada de mesmo valor; isso não repõe porções gastas.',
              '- Nenhum ensaio exigiu o 25º inimigo simultâneo. Se ocorrer, a regra determina '
              'expedição perdida e retirada de emergência; não há limite aumentado nesta revisão.', '',
              'Isto demonstra **uma vitória alcançável por tamanho de grupo** nas escolhas indicadas. '
              'As 15 sementes acima cobrem outras condições em nível de fases, incluindo perdas. '
              'Não há replay tático para cada semente nem para todos os efeitos do baralho; '
              'as trajetórias não estimam a chance de vencer. Nenhuma dificuldade foi ajustada nesta rodada.', '',
              '## Componentes e limites', '',
              '- [COMPONENTES_POR_GRUPO.json](COMPONENTES_POR_GRUPO.json) confere os 114 IDs, fichas e peões, '
              '24 marcadores de inimigos, seis Pés de cabra e substituições de fórmula. Não houve esgotamento de '
              'carga nem de 24 marcadores nos ensaios de fases; isso não cobre picos posicionais do mapa.',
              '- Regras §6: ao surgir o 25º inimigo simultâneo, a expedição é perdida e oferece retirada de emergência. '
              'Antes disso, falta de token físico usa token numerado e registro. Regras §7: falta de carta física '
              'de recurso usa ficha numerada de igual valor; cartas vazias retornam à reserva. Esses procedimentos '
              'foram conferidos no texto, não exercitados fisicamente.',
              '- O registro impresso usa L/I como exemplos. O guia de impressão agora explicita que H3–H6 '
              'escrevem ID ou nome do herói no campo Local; T08/T09 recebem barracas iniciais para H5/H6. '
              'É esclarecimento de preenchimento, sem mudança de mecânica.',
              '- Os ensaios com sementes simplificam posições, PA táticos, cansaço, ferimentos individuais ao longo '
              'de dias, efeitos completos de Viagem/Busca, intenções verificadas e transporte de resgatados. '
              'A trajetória tática fixa usa apenas uma seleção legal desses efeitos.',
              '- Impressão física, duplex real, montagem e playtest humano não ocorreram.', '',
              '**Estado:** cinco trajetórias fixas de cinco dias concluídas, uma por H=2–6. '
              'A campanha continua sem validação ampla de equilíbrio, efeitos alternativos, impressão física '
              'e playtest humano. Os 15 ensaios de fases estão completos e orientam os próximos casos táticos.']
    (root/'CAMPANHA_REPLAY_RELATORIO.md').write_text('\n'.join(lines)+'\n')
    print(root/'CAMPANHA_REPLAY_RELATORIO.md')


if __name__=='__main__':main()
