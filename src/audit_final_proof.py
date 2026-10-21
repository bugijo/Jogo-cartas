"""Inventário reproduzível da prova pós-apocalíptica; não aprova arte automaticamente."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1]
S = P / 'samples/kit-pos-apocaliptico'
OUT = P / 'kit-final-prova/auditoria'
CAT = json.loads((P / 'content/catalog.json').read_text())
MAN = json.loads((P / 'output/comece-aqui-duas-pessoas/manifesto.json').read_text())
SEL = MAN['initial_cards'] + MAN['supplement_cards']
assert len(SEL) == len(set(SEL)) == 114
CHANGED = set()
for lot in ['lote-04-cartas', 'lote-06-itens', 'lote-07-moradores']:
    CHANGED.update(json.loads((S / lot / 'VERIFICACOES.json').read_text())['changed_ids'])
assert CHANGED <= set(SEL)
CARDS = {c['id']: c for c in CAT['cards']}
ROWS: list[dict[str, str]] = []


def add(component, expected, found, status, source, output, qa, notes=''):
    assert status in {'READY', 'PARTIAL', 'MISSING', 'BROKEN', 'NEEDS_REVIEW', 'NOT_APPLICABLE'}
    ROWS.append(dict(COMPONENT=component, EXPECTED=str(expected), FOUND=str(found),
                     STATUS=status, SOURCE=str(source), OUTPUT=str(output), QA=qa, NOTES=notes))


card_pdf = S / 'lote-07-moradores/pdfs/02_CARTAS_DUPLEX/KIT_INICIAL_1_DUPLEX.pdf'
for cid in SEL:
    card = CARDS[cid]
    art = cid in CHANGED
    add(cid, 'carta selecionada; arte revisada', 'carta e PDF; ' + ('arte nova' if art else 'arte anterior'),
        'READY' if art and card_pdf.exists() else 'PARTIAL', 'content/catalog.json',
        card_pdf.relative_to(P) if card_pdf.exists() else '', 'texto/verso conferido no lote 07' if art else 'revisão artística pendente',
        f"{card['family']} / {card['name']}")

map_proofs = {
    'Mercado': P / 'samples/mercado-b-pos-apocaliptico/MERCADO_4_A4.pdf',
    'Hospital': S / 'lote-02-composicao/hospital/HOSPITAL_4_A4.pdf',
    'Oficina': S / 'lote-02-composicao/oficina/OFICINA_4_A4.pdf',
    'Posto': S / 'lote-08-posto/POSTO_4_A4.pdf',
    'Condomínio': S / 'lote-09-condominio/CONDOMINIO_4_A4.pdf',
    'Estação': S / 'lote-05-estacao/ESTACAO_4_A4.pdf',
}
for m in CAT['maps']:
    path = map_proofs[m['name']]
    exists = bool(path and path.exists())
    slug = {'Condomínio': 'CONDOMINIO', 'Estação': 'ESTACAO'}.get(m['name'], m['name'].upper())
    old = P / f"output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/{slug}_M01_M04_LADO_A.pdf"
    add(m['id'], 'prova pós-apocalíptica em 4 A4', 'prova nova' if exists else 'mapa 0.6 apenas',
        'READY' if exists else 'PARTIAL', 'content/production/geometry_0.6.json',
        path.relative_to(P) if exists else old.relative_to(P),
        'PDF e geometria inspecionados; impressão física pendente' if exists else 'recompor ambiente e verificar conexões',m['name'])

for h in CAT['heroes']:
    new = S / 'lote-03-personagens/pdfs/FICHAS_18_HEROIS.pdf'
    old = P / 'output/edicao-tabuleiros-v0.6/ilustrada/05_PAINEIS/FICHAS_LIA_IVO.pdf'
    add(h['id'], 'personagem reconhecível', 'ficha ilustrada existente', 'READY',
        'content/catalog.json', new.relative_to(P) if h not in CAT['heroes'][:2] else old.relative_to(P),
        'revisão visual global pendente', h['name'])

token_pdf = P / 'output/edicao-tabuleiros-v0.6/ilustrada/07_MARCADORES_E_DIVISORIAS/MARCADORES_RESGATAVEIS.pdf'
for t in CAT['tokens']:
    add(t['id'], 'token compatível com regras', 'token existente', 'NEEDS_REVIEW',
        'content/catalog.json', token_pdf.relative_to(P), 'auditoria visual global pendente',t['kind'])

common = P / 'output/edicao-tabuleiros-v0.6/ilustrada/06_TABULEIROS/COMUNS_M01_M04_LADO_A.pdf'
for mod in CAT['modules']:
    add(mod['id'], 'módulo comum com arte da edição final', 'módulo 0.6', 'PARTIAL',
        'content/catalog.json', common.relative_to(P), 'arte pós-apocalíptica e junções pendentes',mod['name'])

for label, relative in {
    'REGRAS': 'output/edicao-tabuleiros-v0.6/ilustrada/01_GUIA_E_REGRAS/MANUAL.pdf',
    'CAMPANHA': 'output/edicao-tabuleiros-v0.6/ilustrada/01_GUIA_E_REGRAS/CAMPANHA.pdf',
    'ABRIGO': 'output/edicao-tabuleiros-v0.6/ilustrada/05_PAINEIS/ABRIGO_MORADORES_ESTOQUE.pdf',
    'DIVISORIAS': 'output/edicao-tabuleiros-v0.6/ilustrada/07_MARCADORES_E_DIVISORIAS/DIVISORIAS.pdf',
    'PAINEL': 'output/edicao-tabuleiros-v0.6/ilustrada/05_PAINEIS/PAINEL_JOGADOR_2_A4.pdf',
    'REGISTRO_RECURSOS': 'output/edicao-tabuleiros-v0.6/ilustrada/05_PAINEIS/REGISTRO_ADICIONAL.pdf',
    'MORADORES_ADICIONAL': 'output/edicao-tabuleiros-v0.6/ilustrada/05_PAINEIS/MORADORES_ADICIONAL.pdf',
    'COMECE_AQUI': 'output/edicao-tabuleiros-v0.6/ilustrada/01_GUIA_E_REGRAS/COMECE_AQUI.pdf',
}.items():
    path = P / relative
    add(label, 'PDF imprimível e consistente', 'PDF 0.6' if path.exists() else 'ausente',
        'NEEDS_REVIEW' if path.exists() else 'MISSING', 'output/edicao-tabuleiros-v0.6',
        relative, 'auditoria global de texto, legibilidade e folhas pendente')

founders = P / 'output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/FICHAS_24_HEROIS.pdf'
add('FICHAS_FUNDADORES_3_A_6', 'fichas imprimíveis para fundador além de Lia/Ivo',
    'PDF opcional 0.6 existente' if founders.exists() else 'ausente',
    'NEEDS_REVIEW' if founders.exists() else 'MISSING', 'RULES.md / setup H=2..6',
    founders.relative_to(P), 'deve ser obrigatório no índice quando H>2; cópias exatas conforme seleção')
for label, relative, note in [
    ('PES_DE_CABRA_SEIS_FUNDADORES', 'kit-final-prova/componentes-condicionais/PES_DE_CABRA_SEIS_FUNDADORES_DUPLEX.pdf', 'seis IDs únicos 0001–0006; alternativa universal para H3–H6'),
    ('PES_DE_CABRA_H3_A_H6', 'kit-final-prova/componentes-condicionais/PES_DE_CABRA_H3_A_H6_DUPLEX.pdf', 'quatro IDs únicos 0003–0006; imprimir conforme H'),
    ('CARTAS_FORMULA_H3_A_H4', 'kit-final-prova/componentes-condicionais/REPOSICAO_H3_H4_DUPLEX.pdf', 'substituir VIA-0005, HOR-0007/0008, sem duplicar IDs'),
    ('CARTAS_FORMULA_H5_A_H6', 'kit-final-prova/componentes-condicionais/REPOSICAO_H5_H6_DUPLEX.pdf', 'substituir VIA-0005, HOR-0007/0008, sem duplicar IDs'),
]:
    path=P/relative
    add(label, 'suplemento condicional sem alterar a regra', 'PDF gerado' if path.exists() else 'ausente',
        'NEEDS_REVIEW' if path.exists() else 'MISSING', 'content/catalog.json / RULES.md',
        relative, 'dimensão e texto conferidos; indexação no pacote ainda pendente', note)

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / 'COVERAGE_MATRIX.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, ROWS[0].keys(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(ROWS)
stats = Counter(r['STATUS'] for r in ROWS)
summary = dict(selected_cards=len(SEL), art_changed_cards=len(CHANGED), cards_pending_art=len(SEL)-len(CHANGED),
               maps_with_new_proofs=sum(bool(p and p.exists()) for p in map_proofs.values()),
               maps_expected=len(CAT['maps']), common_modules=len(CAT['modules']),
               heroes=len(CAT['heroes']), tokens=len(CAT['tokens']), matrix_rows=len(ROWS), statuses=dict(stats))
(OUT / 'COVERAGE_SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False, indent=2))
