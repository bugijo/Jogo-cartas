"""Congela a planta funcional do Mercado 0.2 para um cenário de teste separado."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
catalog=json.loads((root.parent.parent/'content/catalog.json').read_text(encoding='utf-8'))
market=next(m for m in catalog['maps'] if m['name']=='Mercado')
map_data={k:market[k] for k in ('zones','edges','entry','exit','spawn','search','objectives')}
map_data['doors']=[{'edge':edge,'resistance':3 if edge==[7,8] else 2,
                    'blocked':edge==[7,8]} for edge in market['doors']]
content={'schema':1,'maps':{'market_intro':map_data},
         'enemies':{
             'slow':{'health':1,'attack':1,'move':1,'sight':2,'xp':1},
             'runner':{'health':1,'attack':1,'move':2,'sight':3,'xp':2},
             'brute':{'health':3,'attack':2,'move':1,'sight':2,'xp':3}},
         'hordes':{
             'common':{'units':['slow','slow'],'announced_delay':1},
             'special':{'units':['slow','runner','brute'],'announced_delay':1},
             'surprise':{'units':['runner'],'announced_delay':0}}}
(root/'tactics.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
