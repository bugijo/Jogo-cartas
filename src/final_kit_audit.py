"""Auditoria reproduzível dos PDFs selecionados, geometria e preparação."""
import json
from collections import Counter
from math import ceil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'kit-final-prova' / 'auditoria'
MAN = json.loads((ROOT / 'output/edicao-tabuleiros-v0.6/ilustrada/00_LEIA_PRIMEIRO/manifesto.json').read_text())
GEOM = json.loads((ROOT / 'content/production/geometry_0.6.json').read_text())
MAPS = {
    'Mercado': 'samples/mercado-b-pos-apocaliptico/MERCADO_4_A4.pdf',
    'Hospital': 'samples/kit-pos-apocaliptico/lote-02-composicao/hospital/HOSPITAL_4_A4.pdf',
    'Oficina': 'samples/kit-pos-apocaliptico/lote-02-composicao/oficina/OFICINA_4_A4.pdf',
    'Posto': 'samples/kit-pos-apocaliptico/lote-08-posto/POSTO_4_A4.pdf',
    'Condomínio': 'samples/kit-pos-apocaliptico/lote-09-condominio/CONDOMINIO_4_A4.pdf',
    'Estação': 'samples/kit-pos-apocaliptico/lote-05-estacao/ESTACAO_4_A4.pdf',
    'Comuns': 'samples/kit-pos-apocaliptico/lote-11-modulos-comuns/COMUNS_4_A4.pdf',
}
GEOMS = {
    'Mercado': 'samples/mercado-b-pos-apocaliptico/fontes/geometria.json',
    'Hospital': 'samples/kit-pos-apocaliptico/lote-02-composicao/hospital/fontes/geometria.json',
    'Oficina': 'samples/kit-pos-apocaliptico/lote-02-composicao/oficina/fontes/geometria.json',
    'Posto': 'samples/kit-pos-apocaliptico/lote-08-posto/fontes/geometria.json',
    'Condomínio': 'samples/kit-pos-apocaliptico/lote-09-condominio/fontes/geometria.json',
    'Estação': 'samples/kit-pos-apocaliptico/lote-05-estacao/fontes/geometria.json',
    'Comuns': 'samples/kit-pos-apocaliptico/lote-11-modulos-comuns/fontes/geometria.json',
}
FIELDS = ('zones', 'edges', 'doors', 'blocked', 'entry', 'exit', 'spawn', 'search', 'objectives')


def pdf_check(path, pages=None, duplex=False):
    doc = fitz.open(ROOT / path)
    sizes = [(round(p.rect.width * 25.4 / 72, 2), round(p.rect.height * 25.4 / 72, 2)) for p in doc]
    a4 = all(sorted(s) == [210.0, 297.0] for s in sizes)
    text_outside_page = []
    fontless_text_pages = []
    for page in doc:
        for word in page.get_text('words'):
            if word[0] < -0.5 or word[1] < -0.5 or word[2] > page.rect.width+0.5 or word[3] > page.rect.height+0.5:
                text_outside_page.append(page.number+1)
        if page.get_text().strip() and not page.get_fonts():
            fontless_text_pages.append(page.number+1)
    return dict(path=path, pages=len(doc), expected_pages=pages, pages_ok=pages is None or len(doc) == pages,
                a4=a4, duplex_even=(not duplex or len(doc) % 2 == 0), sizes_mm=sorted(set(sizes)),
                text_outside_page=text_outside_page, fontless_text_pages=fontless_text_pages)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    canonical = {m['name']: m for m in GEOM}
    geometry = {}
    for name, path in GEOMS.items():
        source = json.loads((ROOT / path).read_text())
        if isinstance(source, list): source = source[0]
        target = canonical.get(name, canonical['Mercado'])
        differences = [k for k in FIELDS if source.get(k) != ([] if name == 'Comuns' and k == 'blocked' else target.get(k))]
        geometry[name] = dict(source=path, differences=differences,
                              zones=len(source['zones']), edges=len(source['edges']), doors=len(source['doors']),
                              blocked=len(source['blocked']))
    files = []
    for item in MAN['files']:
        if item['optional']: continue
        path = 'output/edicao-tabuleiros-v0.6/ilustrada/' + item['file']
        if item['kind'] == 'cartas':
            path = 'samples/kit-pos-apocaliptico/lote-10-cartas-restantes/pdfs/' + item['file']
        elif item['file'].endswith('COMUNS_M01_M04_LADO_A.pdf'):
            path = MAPS['Comuns']
        files.append(dict(stage=item['stage'], method=item['method'], sheets=item['sheets'],
                          kind=item['kind'], **pdf_check(path, item['pages'], item['duplex'])))
    base = {m: {s: sum(x['sheets'] for x in files if x['stage'] == s and x['method'] in ('both', m))
                for s in ('initial', 'supplement')} for m in ('duplex', 'manual')}
    # Supplemental H>2 route uses all 24 hero sheets in place of Lia/Ivo (1) and resgatáveis (6).
    # Flat markers remain for enemies; 24 cutout heroes supply founder tokens 3-12.
    extra = {'duplex': 12 - 7 + 2 + 2, 'manual': 12 - 7 + 4 + 2}  # fichas, cartas condicionais, peões
    setups = []
    links = {'Sozinho': (0, 0), 'Parceiro': (1, 0), 'Filho': (1, 0),
             'Cachorro': (0, 1), 'Parceiro e cachorro': (1, 1)}
    deck = ['Sozinho'] * 4 + ['Parceiro'] * 4 + ['Filho'] * 2 + ['Cachorro', 'Parceiro e cachorro']
    from itertools import combinations
    for participants in range(1, 7):
        h = max(2, participants)
        results = []
        for chosen in combinations(range(12), h):
            humans = h + sum(links[deck[i]][0] for i in chosen)
            dogs = sum(links[deck[i]][1] for i in chosen)
            cap = 2 * max(4, h)
            c = humans + dogs
            cards = ceil(2 * c / 4)
            results.append((humans, dogs, cap, cards, humans <= cap))
        setups.append(dict(participants=participants, heroes=h, barracks=max(4, h),
                           family_combinations=len(results), all_fit=all(r[4] for r in results),
                           humans_range=[min(r[0] for r in results), max(r[0] for r in results)],
                           consumers_range=[min(r[0]+r[1] for r in results), max(r[0]+r[1] for r in results)],
                           initial_food_water_cards_range=[min(r[3] for r in results), max(r[3] for r in results)],
                           starting_errantes=ceil(h/2),
                           duplex_sheets=base['duplex']['initial']+base['duplex']['supplement']+(0 if h==2 else extra['duplex']),
                           manual_sheets=base['manual']['initial']+base['manual']['supplement']+(0 if h==2 else extra['manual'])))
    map_pdfs = [pdf_check(p, 4) for p in MAPS.values()]
    conditionals = [pdf_check('kit-final-prova/componentes-condicionais/'+p, 2, True) for p in
                    ('PES_DE_CABRA_SEIS_FUNDADORES_DUPLEX.pdf','REPOSICAO_H3_H4_DUPLEX.pdf','REPOSICAO_H5_H6_DUPLEX.pdf')]
    for stem in ('PES_DE_CABRA_SEIS_FUNDADORES', 'REPOSICAO_H3_H4', 'REPOSICAO_H5_H6'):
        for side in ('FRENTES', 'VERSOS'):
            conditionals.append(pdf_check(f'kit-final-prova/componentes-condicionais/manual/{stem}_{side}.pdf', 1))
    result = dict(base_sheets=base, files=files, maps=map_pdfs, geometry=geometry,
                  conditionals=conditionals, setup_simulations=setups,
                  limitations=['Modelo combinatório de preparo, não simulação estocástica dos cinco dias.',
                               'H3–6 usa peões recortáveis para fundadores; marcadores planos existentes só trazem Lia/Ivo e resgatáveis.',
                               'Compatibilidade gráfica digital não valida alinhamento da impressora nem playtest.'])
    (OUT/'FINAL_KIT_AUDIT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    assert all(not g['differences'] for g in geometry.values()), geometry
    assert all(x['a4'] and x['pages_ok'] and x['duplex_even'] for x in files + map_pdfs + conditionals)
    assert all(not x['text_outside_page'] and not x['fontless_text_pages'] for x in files + map_pdfs + conditionals)
    assert all(x['all_fit'] for x in setups)
    return result


if __name__ == '__main__':
    data = run()
    print('base', data['base_sheets'])
    print('setups', [(x['participants'],x['heroes'],x['duplex_sheets'],x['manual_sheets']) for x in data['setup_simulations']])
