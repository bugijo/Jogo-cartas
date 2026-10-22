"""Cartas substitutas para a fórmula canônica ceil(H/2) com H=3..6."""
from pathlib import Path
import sys
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P/'src'))
import build_finish as b

OUT = P/'kit-final-prova/componentes-condicionais'
OUT.mkdir(parents=True, exist_ok=True)
b.setup()
ids = ['ZC-VIA-0005', 'ZC-HOR-0007', 'ZC-HOR-0008']
cards = [next(c for c in b.D['cards'] if c['id']==cid) for cid in ids]
assert all('ceil(H/2)' in c['text'] for c in cards)
original = b.f.effect
try:
    for n,lo,hi in [(2,3,4),(3,5,6)]:
        b.f.effect = lambda card, initial=False, n=n: card['text'].replace('ceil(H/2)', str(n))
        path = OUT/f'REPOSICAO_H{lo}_H{hi}_DUPLEX.pdf'
        pdf = canvas.Canvas(str(path),pagesize=A4)
        for back in (False,True):
            for i,card in enumerate(cards):
                col=i if not back else 2-i
                x=8.5+65*col;y=297-14.5-88
                (b.card_back(pdf,card['family'],x,y) if back else b.card_front(pdf,card,x,y,False))
            pdf.setFont('Body',8)
            pdf.drawString(8.5*mm,288*mm,f'ZONA ZERO / H{lo}–H{hi} / '+('VERSOS / borda longa' if back else 'FRENTES')+' / 100%')
            pdf.showPage()
        pdf.save()
        doc=fitz.open(path)
        assert len(doc)==2 and all(abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01 for p in doc)
        front=' '.join(doc[0].get_text().split())
        assert all(c['id'] in front for c in cards)
        assert all(' '.join(c['text'].replace('ceil(H/2)',str(n)).split()) in front for c in cards)
        assert 'ceil(H/2)' not in front
        doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(OUT/f'REPOSICAO_H{lo}_H{hi}_FRENTES.png')
        print(path, '3 substituições, 1 folha duplex')
finally:
    b.f.effect=original
