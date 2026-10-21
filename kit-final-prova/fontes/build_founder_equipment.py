"""Quatro Pés de cabra condicionais para H=3..6; IDs e texto do catálogo."""
from pathlib import Path
import sys
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P / 'src'))
import build_finish as b

OUT = P / 'kit-final-prova/componentes-condicionais'
OUT.mkdir(parents=True, exist_ok=True)
b.setup()
cards = [c for c in b.D['cards'] if c['id'] in {f'ZC-EQU-{i:04}' for i in range(3, 7)}]
assert len(cards) == 4 and all(c['name'] == 'Pé de cabra' for c in cards)
path = OUT / 'PES_DE_CABRA_H3_A_H6_DUPLEX.pdf'
c = canvas.Canvas(str(path), pagesize=A4)
for back in [False, True]:
    for i, card in enumerate(cards):
        row, col = divmod(i, 3)
        if back:
            col = 2-col  # borda longa em A4 retrato
        x = 8.5 + 65*col
        y = 297 - 14.5 - 88 - 90*row
        (b.card_back(c, 'EQU', x, y) if back else b.card_front(c, card, x, y, False))
    c.setFont('Helvetica', 8)
    c.drawString(8.5*mm, 288*mm, 'ZONA ZERO / H3–H6 / ' + ('VERSOS / borda longa' if back else 'FRENTES') + ' / 100%')
    c.showPage()
c.save()
doc = fitz.open(path)
assert len(doc) == 2 and all(abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01 for p in doc)
front_text = doc[0].get_text()
assert all(card['id'] in front_text for card in cards)
assert all(' '.join(card['text'].split()) in ' '.join(front_text.split()) for card in cards)
for i,p in enumerate(doc):
    p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(OUT/f'PES_DE_CABRA_{i+1}.png')
print(path, '2 páginas / 1 folha duplex / quatro IDs adicionais')
