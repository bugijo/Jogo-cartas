"""Independent, reproducible audit of setup, phase-model samples and selected PDFs.

This does not turn the simplified phase model into a tactical playtest.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from math import ceil, sqrt
from pathlib import Path

import fitz

from campaign_seeded_review import LINKS, phase_replay
from final_kit_audit import ROOT, MAPS, run as print_audit
from scaled_tactical_replay import run as tactical_run

OUT = ROOT / 'kit-final-prova' / 'auditoria'


def setups():
    rows = []
    for h in range(2, 7):
        seen = Counter()
        for picks in combinations(range(len(LINKS)), h):
            chosen = [LINKS[i] for i in picks]
            people = h + sum(x[1] for x in chosen)
            dogs = sum(x[2] for x in chosen)
            consumers = people + dogs
            tents = max(4, h)
            full = ceil(2 * consumers / 4)
            lot = ceil(consumers / 4)
            assert people <= tents * 2
            assert 4 * full >= 2 * consumers
            assert 4 * full - 2 * consumers <= 3
            assert 4 * lot >= consumers
            assert 1 <= ceil(h / 2) <= 3
            assert h <= 6  # seis pes de cabra distintos na folha condicional
            seen[(people, dogs, consumers, full, lot)] += 1
        rows.append(dict(heroes=h, combinations=sum(seen.values()), tents=max(4, h),
                         capacity=2 * max(4, h), initial_food_and_water_cards_range=[min(x[3] for x in seen), max(x[3] for x in seen)],
                         lot_cards_range=[min(x[4] for x in seen), max(x[4] for x in seen)],
                         consumers_range=[min(x[2] for x in seen), max(x[2] for x in seen)],
                         distinct_resource_cases=len(seen)))
    assert sum(x['combinations'] for x in rows) == 2497
    return rows


def wilson(k, n):
    z = 1.96
    center = (k + z*z/2) / (n + z*z)
    radius = z * sqrt(k*(n-k)/n + z*z/4) / (n + z*z)
    return [round(max(0, center-radius), 3), round(min(1, center+radius), 3)]


def samples():
    summaries = []
    seed_rows = []
    for h in range(2, 7):
        results = []
        for profile, code in [('favoravel', 1), ('dificil', 2), ('limite', 3)]:
            for i in range(50):
                seed = h * 100000 + code * 10000 + i
                run = phase_replay(h, seed, profile)
                assert len(run['days']) == 5
                last = run['days'][-1]
                causes = []
                if not last['filter_active']: causes.append('filtro_inativo')
                if last['health'] < 1: causes.append('saude_zero')
                if last['morale'] < 1: causes.append('moral_zero')
                if any(last['shortage']): causes.append('falta_na_ultima_refeicao')
                if run['incapacitated']: causes.append('incapacitacao_amostrada')
                record = dict(heroes=h, profile=profile, seed=seed,
                              model_result=run['result'], causes=causes,
                              rescues=sum(bool(d['rescue_card']) for d in run['days']),
                              final_stock=last['stock_after'],
                              food_by_day=[d['stock_after']['food'] for d in run['days']],
                              water_by_day=[d['stock_after']['water'] for d in run['days']],
                              shortages=[d['shortage'] for d in run['days']],
                              component_exhaustion=run['component_exhaustion'])
                results.append(record)
                seed_rows.append(record)
        n = len(results)
        possible = sum(x['model_result'] == 'plano_de_fases_possivel' for x in results)
        summaries.append(dict(heroes=h, samples=n, seed_range=[min(x['seed'] for x in results), max(x['seed'] for x in results)],
                              possible=possible, blocked=n-possible, model_possible_rate=round(possible/n, 3),
                              wilson_95_model_only=wilson(possible, n),
                              causes=dict(Counter(c for x in results for c in x['causes'])),
                              rescues_total=sum(x['rescues'] for x in results),
                              exhaustions=dict(Counter(e['item'] for x in results for e in x['component_exhaustion'])),
                              mean_end_food_by_day=[round(sum(x['food_by_day'][d] for x in results)/n, 2) for d in range(5)],
                              mean_end_water_by_day=[round(sum(x['water_by_day'][d] for x in results)/n, 2) for d in range(5)]))
    return summaries, seed_rows


def pdf_index_check():
    audit = print_audit()
    selected = audit['files'] + audit['conditionals'] + audit['maps']
    for item in selected:
        assert item['a4'] and item['pages_ok'] and item['duplex_even']
        assert not item['text_outside_page'] and not item['fontless_text_pages']
    # Independent arithmetic against actual PDF pages, not only manifest sheet counts.
    totals = {}
    for method in ('duplex', 'manual'):
        relevant = [x for x in audit['files'] if x['method'] in ('both', method)]
        pages = sum(x['pages'] for x in relevant)
        sheets = sum(x['pages']//2 if x['method']=='duplex' else x['pages'] for x in relevant)
        assert sheets == (58 if method=='duplex' else 72), (method, sheets)
        totals[method] = dict(pdf_count=len(relevant), pages=pages, sheets=sheets)
    dense = {}
    font_failures=[]
    checked_pages=0
    for entry in audit['files']:
        if entry['kind'] != 'cartas': continue
        with fitz.open(ROOT / entry['path']) as doc:
            dense[Path(entry['path']).name] = dict(pages=len(doc), text_chars=sum(len(p.get_text()) for p in doc),
                                                       embedded_fonts=all(p.get_fonts() for p in doc if p.get_text().strip()))
    for entry in selected:
        with fitz.open(ROOT/entry['path']) as doc:
            font_bytes={}
            for page in doc:
                checked_pages+=1
                used={span['font'] for block in page.get_text('dict')['blocks'] if 'lines' in block
                      for line in block['lines'] for span in line['spans']}
                resources=[]
                for font in page.get_fonts(full=True):
                    xref,base=font[0],font[3].split('+')[-1]
                    if xref not in font_bytes:font_bytes[xref]=len(doc.extract_font(xref)[-1])
                    resources.append((base,font_bytes[xref]))
                for name in used:
                    matches=[size for base,size in resources if base==name or base.startswith(name) or name.startswith(base)]
                    if not matches or not any(matches):font_failures.append((entry['path'],page.number+1,name))
    assert not font_failures,font_failures[:10]
    return dict(totals=totals, cards=dense, maps={k:v for k,v in MAPS.items()},
                geometry={k:v['differences'] for k,v in audit['geometry'].items()},
                pages_with_used_fonts_checked=checked_pages,unembedded_used_fonts=font_failures)


def independent_route_ledgers():
    """Recalculate stocks from the recorded deliveries and meals, without Replay code."""
    routes=json.loads((OUT/'ROTEIROS_TATICOS_H2_H6.json').read_text())
    checks=[]
    for route in routes:
        c=route['consumers_initial']
        start=4*ceil(2*c/4)
        food=water=start
        for day in route['days']:
            day_no=day['day']
            delivery=route['tactical'][day_no-1]['delivered'] if day_no<=3 else {}
            # Each lot card is four portions; the night travel card removes one carried water portion.
            food += 4*delivery.get('Conserva',0)
            water += 4*delivery.get('Água',0)
            if day_no==3: water-=1
            if day_no==5: water+=2*c
            eat=day['people']+day['dogs']
            food-=eat;water-=eat
            assert (food,water)==(day['food'],day['water']), (route['heroes'],day_no,food,water,day['food'],day['water'])
            assert food>=0 and water>=0
        checks.append(dict(heroes=route['heroes'],end_food=food,end_water=water,days_checked=5))
    return checks


def alternate_decisions():
    """Replay the same route with the legal Bia choice reversed for each H."""
    rows=[]
    for h in range(2,7):
        choice=(h==6)  # inverse of the original five routes
        try:
            r=tactical_run(h,choice)
            rows.append(dict(heroes=h,accept_bia=choice,status='route_completed',
                             food=r['days'][-1]['food'],water=r['days'][-1]['water'],
                             route=r))
        except AssertionError as exc:
            rows.append(dict(heroes=h,accept_bia=choice,status='route_blocked',
                             evidence=repr(exc)))
    (OUT/'ROTEIROS_ALTERNATIVOS_BIA_H2_H6.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    return [{k:v for k,v in x.items() if k!='route'} for x in rows]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    setup = setups()
    summary, seeds = samples()
    pdfs = pdf_index_check()
    payload = dict(setups=setup, phase_summary=summary, seed_records=seeds, print_audit=pdfs,
                   independent_route_ledgers=independent_route_ledgers(),
                   alternative_decisions=alternate_decisions(),
                   warnings=['Phase model omits tactical PA/positions and many card effects; rates are conditional on its three fixed policies.',
                             'No human playtest or physical printing performed.'])
    (OUT/'REVISAO_DIGITAL_FINAL.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    print([(s['heroes'],s['possible'],s['samples']) for s in summary])
    print(pdfs['totals'])


if __name__ == '__main__': main()
