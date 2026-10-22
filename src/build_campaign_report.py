"""Relatório reproduzível dos ensaios de campanha com limites explícitos."""
import json
from pathlib import Path

from campaign_seeded_review import ROOT, run_matrix
from probe_tactical_replay_scale import probe


def main():
    matrix=run_matrix()
    tactical=[probe(h) for h in range(2,7)]
    root=ROOT/'kit-final-prova/auditoria'
    (root/'CAMPANHA_SEMENTES.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    (root/'ROTEIRO_TATICO_ESCALA.json').write_text(json.dumps(tactical,ensure_ascii=False,indent=2)+'\n')
    lines=['# Revisão reproduzível da campanha — cinco dias', '',
           'Regras e catálogo da edição 0.2 preservados. Quinze ensaios de **fases** (H=2–6, três sementes cada) '
           'registram preparação, carga prevista, provisões, confrontos amostrados, resgates, fila de cerco, '
           'trabalhos e filtro ao longo dos cinco dias. São ensaios determinísticos para achar lacunas, '
           '**não partidas táticas completas nem evidência de equilíbrio**. Perfil favorável recusa resgates '
           'opcionais e prioriza abastecimento; difícil acolhe Jana; limite seleciona vínculos de maior consumo '
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
    lines += ['', '**Partidas integrais certificadas: 0/5 tamanhos.** O roteiro de Lia/Ivo de `src/review_five_days.py` '
              'percorre uma trajetória específica de cinco dias em H=2, sem exercer resgates. '
              'Ao aplicar o número correto de inimigos iniciais `ceil(H/2)`, o roteiro fixo H=3–6 para no Mercado, '
              'rodada 4: Lia precisa de 1 PA depois de chegar a 0. **Isso comprova falha de cobertura do replay, '
              'não que a campanha seja impossível nesses grupos.** O próximo trabalho é escrever ações legais para '
              'heróis adicionais e verificar todas as zonas, dados, cartas de Viagem/Horda e consequências. '
              'Nenhuma dificuldade foi ajustada nesta rodada.', '',
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
              '- Os ensaios de fases simplificam posições, PA táticos, cansaço, ferimentos individuais ao longo '
              'de dias, efeitos completos de Viagem/Busca, intenções verificadas e transporte de resgatados. '
              'Por isso nenhuma linha da tabela certifica uma vitória.',
              '- Impressão física, duplex real, montagem e playtest humano não ocorreram.', '',
              '**Estado:** campanha não validada integralmente para H=2–6. O grupo H=2 tem um replay tático '
              'favorável parcial existente; H3–H6 ainda exigem replay tático novo. Os 15 ensaios de fases estão completos '
              'e servem para orientar esse trabalho.']
    (root/'CAMPANHA_REPLAY_RELATORIO.md').write_text('\n'.join(lines)+'\n')
    print(root/'CAMPANHA_REPLAY_RELATORIO.md')


if __name__=='__main__':main()
