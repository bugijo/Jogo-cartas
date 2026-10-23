"""Gera plantas funcionais experimentais; seis geometrias vêm do catálogo 0.2."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent.parent/'content/catalog.json'
MAPPING={
    'Mercado':('market_intro','EXP-LOC-02'),
    'Hospital':('hospital_02','EXP-LOC-04'),
    'Oficina':('workshop_02','EXP-LOC-03'),
    'Posto':('gas_station_02',None),
    'Condomínio':('condominium_02',None),
    'Estação':('station_02','EXP-LOC-05'),
}


def build_content() -> dict:
    catalog=json.loads(SOURCE.read_text(encoding='utf-8'))
    maps={}
    for source in catalog['maps']:
        map_id,location=MAPPING[source['name']]
        record={key:source[key] for key in
                ('zones','edges','entry','exit','spawn','search','objectives')}
        record['doors']=[{'edge':e,'resistance':3 if e in source['blocked'] else 2,
                          'blocked':e in source['blocked']} for e in source['doors']]
        record['source_id']=source['id']
        if location:record['location']=location
        else:record['reference_only']=True
        maps[map_id]=record
    maps['camp_final']={'zones':[1,2,3,4],'edges':[[1,2],[2,3],[3,4]],
                        'entry':1,'exit':1,'spawn':4,'search':[],
                        'objectives':[1],'doors':[]}
    edges=[]
    for zone in range(1,17):
        if zone%4:edges.append([zone,zone+1])
        if zone<=12:edges.append([zone,zone+4])
    maps['military_installation']={'zones':list(range(1,17)),'edges':edges,
        'entry':1,'exit':1,'spawn':16,'search':[],'objectives':[6],
        'doors':[{'edge':[2,6],'resistance':2,'blocked':False}],
        'location':'EXP-LOC-06'}
    return {'schema':1,'maps':maps,'enemies':{
        'slow':{'health':1,'attack':1,'move':1,'sight':2,'xp':1},
        'runner':{'health':1,'attack':1,'move':2,'sight':3,'xp':2},
        'brute':{'health':3,'attack':2,'move':1,'sight':2,'xp':3}},
        'hordes':{
            'common':{'units':['slow','slow'],'announced_delay':1},
            'special':{'units':['slow','runner','brute'],'announced_delay':1},
            'surprise':{'units':['runner'],'announced_delay':0}}}


if __name__=='__main__':
    (ROOT/'tactics.json').write_text(json.dumps(build_content(),ensure_ascii=False,indent=2)+'\n',
                                     encoding='utf-8')
