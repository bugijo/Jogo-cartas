"""Confere cobertura documental/física das seleções H=2..6."""
import json
from pathlib import Path

import fitz

from campaign_seeded_review import ROOT, HEROES, run_matrix
from final_kit_audit import run as print_audit


def text(path):
    return '\n'.join(p.get_text() for p in fitz.open(ROOT/path))


def run():
    qa=print_audit()
    matrix=run_matrix()
    chosen=json.loads((ROOT/'samples/kit-pos-apocaliptico/lote-10-cartas-restantes/VERIFICACOES.json').read_text())
    assert len(chosen['selected_ids'])==len(set(chosen['selected_ids']))==114
    sheet=text('output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/FICHAS_24_HEROIS.pdf')
    pawns=text('output/edicao-tabuleiros-v0.6/ilustrada/04_PERSONAGENS_E_INIMIGOS/HEROIS_24_RECORTAR.pdf')
    missing_hero=[h['name'] for h in HEROES if h['name'].upper() not in sheet.upper() or h['name'] not in pawns]
    assert not missing_hero,missing_hero
    equip=text('kit-final-prova/componentes-condicionais/PES_DE_CABRA_SEIS_FUNDADORES_DUPLEX.pdf')
    missing_equip=[f'ZC-EQU-{i:04}' for i in range(1,7) if f'ZC-EQU-{i:04}' not in equip]
    assert not missing_equip,missing_equip
    marker=text('output/edicao-tabuleiros-v0.6/ilustrada/07_MARCADORES_E_DIVISORIAS/MARCADORES_INICIAIS.pdf')
    enemy_count=sum(f'ZC-TOK-{i:04}' in marker for i in range(25,49))
    assert enemy_count==24
    conditionals={}
    for h in range(2,7):
        if h==2:continue
        fname='REPOSICAO_H3_H4_DUPLEX.pdf' if h<=4 else 'REPOSICAO_H5_H6_DUPLEX.pdf'
        content=text('kit-final-prova/componentes-condicionais/'+fname)
        expected=(h+1)//2
        assert f'{expected} Errantes' in content
        conditionals[h]=dict(file=fname,initial_crowbars=h,formula_errantes=expected)
    by_h={x['heroes']:x for x in qa['setup_simulations']}
    assert all(x['all_fit'] for x in qa['setup_simulations'])
    assert all(x['duplex_sheets']==(58 if x['heroes']==2 else 67) for x in qa['setup_simulations'])
    records=[]
    for h in range(2,7):
        runs=[x for x in matrix['runs'] if x['heroes']==h]
        assert len(runs)==3 and all(len(x['days'])==5 for x in runs)
        records.append(dict(heroes=h,founder_cards=h,hero_sheets='1 Lia/Ivo + 6 resgatáveis' if h==2 else '12 folhas de 24 heróis',
                            hero_pawns='marcadores planos Lia/Ivo' if h==2 else '2 folhas de 24 peões',
                            crowbar_ids='0001–0002 nas fichas' if h==2 else '0001–0006, use somente 0001..000H',
                            enemy_markers=enemy_count,conditional=conditionals.get(h),
                            duplex_sheets=by_h[h]['duplex_sheets'],manual_sheets=by_h[h]['manual_sheets'],
                            modeled_exhaustions=[z for r in runs for z in r['component_exhaustion']]))
    result=dict(cards=114,hero_sheets_complete=True,hero_pawns_complete=True,enemies_printed=enemy_count,
                group_components=records,
                documented_fallbacks=['Recursos em lotes/parciais: registro numerado de saldos; cartas vazias voltam à reserva.',
                                      'Inimigo 25 simultâneo: expedição perdida e retirada de emergência (RULES.md §6).',
                                      'Se reserva de inimigos acabar antes do limite, usar tokens numerados e registrar excedentes.',
                                      'Se lotes excederem cartas físicas disponíveis, ficha numerada anotada do mesmo valor (RULES.md §7).'],
                actual_exhaustion_in_phase_runs=any(r['component_exhaustion'] for r in matrix['runs']),
                limitations=['Contagem de suporte não comprova todas as interações táticas.',
                             'O registro impresso nomeia L/I; para fundadores adicionais escreva ID/nome na coluna Local.',
                             'Três dados d6, lápis, tesoura e envelopes opacos são externos ao papel.'])
    target=ROOT/'kit-final-prova/auditoria/COMPONENTES_POR_GRUPO.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    x=run();print([(r['heroes'],r['duplex_sheets'],r['manual_sheets']) for r in x['group_components']])
