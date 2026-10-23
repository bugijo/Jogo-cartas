import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'data'))
from build_tactics_data import build_content


class TacticalCatalogTests(unittest.TestCase):
    def test_generator_is_reproducible_and_preserves_six_legacy_plants(self):
        generated=build_content()
        checked_in=json.loads((ROOT/'data/tactics.json').read_text(encoding='utf-8'))
        self.assertEqual(generated,checked_in)
        legacy=json.loads((ROOT.parent/'content/catalog.json').read_text(encoding='utf-8'))
        by_name={m['name']:m for m in legacy['maps']}
        mapping={'Mercado':'market_intro','Hospital':'hospital_02',
                 'Oficina':'workshop_02','Posto':'gas_station_02',
                 'Condomínio':'condominium_02','Estação':'station_02'}
        for name,identifier in mapping.items():
            source=by_name[name];target=generated['maps'][identifier]
            for key in ('zones','edges','entry','exit','spawn','search','objectives'):
                self.assertEqual(target[key],source[key])
            self.assertEqual([d['edge'] for d in target['doors']],source['doors'])
            self.assertEqual([d['edge'] for d in target['doors'] if d['blocked']],source['blocked'])


if __name__=='__main__':unittest.main()
