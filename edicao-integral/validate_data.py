"""Verificação estática do catálogo experimental e das referências entre componentes."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'data/system.json').read_text(encoding='utf-8'))
GEAR=json.loads((ROOT/'data/equipment.json').read_text(encoding='utf-8'))
TACTICS=json.loads((ROOT/'data/tactics.json').read_text(encoding='utf-8'))
CARDS=(json.loads((ROOT/'data/cycle_cards.json').read_text(encoding='utf-8'))['cards']
       +json.loads((ROOT/'data/last_transmission.json').read_text(encoding='utf-8'))['cards'])
RESOURCES={'food','water','wood','scrap','medicine','fuel','ammo'}
OPERATIONS={'medicine','water','rescue','defense','attack','noise','infection',
            'travel','search','repair','build','craft','food','storage','research'}


def validate() -> dict:
    ids=[]
    for family in ('heroes','npcs','structures','locations','crises','vehicles'):
        ids += [item['id'] for item in DATA[family]]
    ids += [skill['id'] for hero in DATA['heroes'] for skill in hero['skills']]
    ids += [item['id'] for item in GEAR['items']]
    ids += [card['id'] for card in CARDS]
    if len(ids)!=len(set(ids)):
        raise ValueError('IDs duplicados')
    if len(DATA['heroes'])!=10 or len(DATA['npcs'])!=15:
        raise ValueError('Elenco incompleto')
    for hero in DATA['heroes']:
        if set(hero['attributes'])!=set(DATA['attributes']) or any(not 1<=v<=3 for v in hero['attributes'].values()):
            raise ValueError('Atributos inválidos')
        if [s['xp'] for s in hero['skills']]!=DATA['rules']['skill_unlock_xp']:
            raise ValueError('Progressão inválida')
        if any(s['operation'] not in OPERATIONS or s['bonus']<=0 for s in hero['skills']):
            raise ValueError('Efeito de habilidade inválido')
    for npc in DATA['npcs']:
        if not 1<=npc['level']<=npc['max_level']<=3 or npc['output'] not in OPERATIONS|RESOURCES:
            raise ValueError('NPC inválido')
    for building in DATA['structures']:
        if building['work']<=0 or building['terrain']<=0 or building['max_health']<=0:
            raise ValueError('Construção inválida')
        if any(r not in RESOURCES or n<0 for r,n in building['cost'].items()):
            raise ValueError('Custo inválido')
        action=building.get('action')
        if action:
            if any(r not in RESOURCES or n<=0 for r,n in action['cost'].items()):
                raise ValueError('Receita inválida')
            if any(r not in RESOURCES or n<=0 for r,n in action.get('output',{}).items()):
                raise ValueError('Saída inválida')
    loc_kinds={loc['id'] for loc in DATA['locations']}
    building_kinds={b['kind'] for b in DATA['structures']}
    if any(c['target'] not in building_kinds or c['effect']['damage']<=0 or c['cooldown_days']<1
           for c in DATA['crises']):
        raise ValueError('Crise sem alvo ou proteção')
    if any(v['seats']<=0 or v['cargo_capacity']<=0 or v['fuel_per_segment']<=0
           for v in DATA['vehicles']):
        raise ValueError('Veículo inválido')
    if not loc_kinds:
        raise ValueError('Locais ausentes')
    for item in GEAR['items']:
        if item['size'][0]<=0 or item['size'][1]<=0 or item['durability']<=0 or not item['slots']:
            raise ValueError('Equipamento inválido')
        combat=item['combat']
        if combat and (not 1<=combat['hit_on']<=6 or combat['dice']<=0
                       or combat['noise'] not in ('baixo','médio','alto')):
            raise ValueError('Combate inválido')
    for map_data in TACTICS['maps'].values():
        zones=set(map_data['zones'])
        if (map_data.get('location') is not None and map_data['location'] not in loc_kinds
                or len(zones)!=len(map_data['zones']) or map_data['entry'] not in zones
                or map_data['exit'] not in zones or map_data['spawn'] not in zones
                or any(a not in zones or b not in zones or a==b for a,b in map_data['edges'])
                or any(door['edge'] not in map_data['edges'] for door in map_data['doors'])
                or any(z not in zones for z in map_data['search']+map_data['objectives'])):
            raise ValueError('Geometria tática inválida')
        reached={map_data['entry']}
        while True:
            more={b for a,b in map_data['edges'] if a in reached}|{a for a,b in map_data['edges'] if b in reached}
            if more <= reached:break
            reached|=more
        if reached!=zones:
            raise ValueError('Mapa desconectado')
    for horde in TACTICS['hordes'].values():
        if not horde['units'] or any(kind not in TACTICS['enemies'] for kind in horde['units']):
            raise ValueError('Horda sem inimigos válidos')
    for card in CARDS:
        if card['family']=='event':
            if not card['choices'] or len({c['id'] for c in card['choices']})!=len(card['choices']):
                raise ValueError('Escolhas inválidas')
            for choice in card['choices']:
                if any(effect['kind'] not in ('cargo','clues') for effect in choice['effects']):
                    raise ValueError('Efeito de carta desconhecido')
        elif card['family']=='mission':
            target=card.get('requirements',{}).get('destination',card.get('location'))
            if target not in loc_kinds|{'camp'}:
                raise ValueError('Missão sem destino')
        else:
            raise ValueError('Família de carta desconhecida')
    return {'unique_ids':len(ids),'heroes':len(DATA['heroes']),'skills':sum(len(h['skills']) for h in DATA['heroes']),
            'npcs':len(DATA['npcs']),'structures':len(DATA['structures']),
            'locations':len(DATA['locations']),'crises':len(DATA['crises']),
            'vehicles':len(DATA['vehicles']),'equipment_templates':len(GEAR['items']),
            'cards':len(CARDS),'tactical_maps':len(TACTICS['maps']),
            'enemy_types':len(TACTICS['enemies']),'horde_types':len(TACTICS['hordes'])}


if __name__=='__main__':
    print(json.dumps(validate(),ensure_ascii=False,indent=2))
