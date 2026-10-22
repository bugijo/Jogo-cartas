import sys
import unittest
from pathlib import Path

import fitz

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from audit_h6_bia_playtest import BASE, ledger
from build_first_playtest import files


class FirstPlaytestTest(unittest.TestCase):
    def test_h6_bia_collection_uses_existing_portions(self):
        original=ledger(False)
        self.assertEqual([(x['food_balance'],x['water_balance']) for x in original],
                         [(x['food'],x['water']) for x in BASE['days']])
        self.assertEqual(ledger(True)[-1]['food_shortage'],4)
        route=ledger(True,(4,5))
        self.assertEqual([x['collected_food'] for x in route],[0,0,0,2,2])
        self.assertEqual(route[-1]['food_balance'],0)
        self.assertEqual(route[-1]['water_balance'],11)

    def test_exact_duplex_selection_and_printable_forms(self):
        selected=files()
        self.assertEqual((len(selected),sum(x['sheets'] for x in selected)),(18,58))
        for name,pages in [('PRIMEIRA_PARTIDA_DUAS_PESSOAS.pdf',3),('OBSERVADOR_E_DEVOLUTIVA.pdf',2)]:
            with fitz.open(ROOT/'kit-final-prova/playtest'/name) as pdf:
                self.assertEqual(len(pdf),pages)
                for page in pdf:
                    self.assertEqual((round(page.rect.width*25.4/72),round(page.rect.height*25.4/72)),(210,297))
                    self.assertTrue(page.get_text().strip())
                    self.assertTrue(all(page.rect.contains(fitz.Rect(word[:4])) for word in page.get_text('words')))


if __name__=='__main__':unittest.main()
