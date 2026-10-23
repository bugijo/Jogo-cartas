"""Gera o catálogo estruturado da edição experimental; executar para atualizar system.json."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
base = json.loads((root / 'core.json').read_text(encoding='utf-8'))
attrs = [
    [1, 2, 2, 3, 3, 2], [3, 2, 2, 1, 2, 3], [1, 2, 2, 3, 2, 3],
    [2, 3, 3, 1, 2, 2], [2, 2, 3, 3, 1, 2], [3, 1, 2, 2, 2, 3],
    [1, 2, 3, 3, 2, 2], [2, 1, 2, 2, 3, 3], [3, 2, 2, 2, 1, 3],
    [1, 2, 3, 3, 2, 2],
]
# Efeitos são tipados: habilidade permanente soma bônus somente à operação indicada.
tracks = [
    ('medicine', 'water', 'medicine', 'rescue', 'medicine', 'rescue', 'medicine'),
    ('defense', 'attack', 'defense', 'noise', 'attack', 'defense', 'attack'),
    ('medicine', 'rescue', 'medicine', 'infection', 'rescue', 'medicine', 'infection'),
    ('travel', 'search', 'travel', 'noise', 'search', 'travel', 'search'),
    ('water', 'repair', 'water', 'search', 'water', 'repair', 'water'),
    ('build', 'repair', 'build', 'defense', 'repair', 'build', 'repair'),
    ('repair', 'craft', 'repair', 'search', 'craft', 'repair', 'craft'),
    ('food', 'storage', 'food', 'rescue', 'food', 'storage', 'food'),
    ('defense', 'rescue', 'defense', 'repair', 'rescue', 'defense', 'rescue'),
    ('infection', 'medicine', 'infection', 'search', 'medicine', 'infection', 'medicine'),
]
heroes = []
for index, hero in enumerate(base['heroes']):
    profile = dict(hero)
    profile['attributes'] = dict(zip(base['attributes'], attrs[index]))
    profile['health'] = 3
    profile['skills'] = [
        {'id': f"EXP-SKL-{index+1:02d}-{n:02d}", 'xp': xp, 'operation': op,
         'bonus': 1 if n < 4 else 2,
         'text': f"{op.capitalize()}: +{1 if n < 4 else 2} ao teste ou rendimento correspondente."}
        for n, (xp, op) in enumerate(zip(base['skill_unlock_xp'], tracks[index]))
    ]
    heroes.append(profile)

old = json.loads((root.parent.parent / 'content/catalog.json').read_text(encoding='utf-8'))
remaining = old['heroes'][10:]
npc_jobs = [
    ('plumbing','water'), ('teaching','research'), ('veterinary','medicine'),
    ('carpentry','build'), ('farming','food'), ('driving','travel'),
    ('medicine','medicine'), ('electricity','repair'), ('scouting','search'),
    ('guard','defense'), ('cooking','food'), ('rescue','rescue'),
    ('mechanics','repair'), ('radio','research')
]
npcs = []
for hero, (job, output) in zip(remaining, npc_jobs):
    npcs.append({'id': f"EXP-NPC-{len(npcs)+1:02d}", 'source_hero_id': hero['id'],
                 'name': hero['name'], 'profession': hero['profession'], 'job': job,
                 'output': output, 'level': 1, 'max_level': 3,
                 'task_per_day': 1, 'food_cost': 1, 'water_cost': 1})
npcs.append({'id':'EXP-NPC-15','source_hero_id': None,'name':'Lúcia',
             'profession':'zeladora de escola','job':'maintenance','output':'repair',
             'level':1,'max_level':3,'task_per_day':1,'food_cost':1,'water_cost':1})
structures = [
    ('garden','Horta',{'wood':2,'scrap':1},2,2,0,0),
    ('workshop','Oficina',{'wood':2,'scrap':3},3,2,0,0),
    ('infirmary','Enfermaria',{'wood':2,'scrap':2,'medicine':1},3,2,0,0),
    ('watch','Vigia',{'wood':2,'scrap':2},2,2,0,0),
    ('storage','Depósito',{'wood':3,'scrap':2},3,2,12,0),
    ('reservoir','Reservatório',{'wood':2,'scrap':3},3,2,0,0),
    ('lodging','Alojamento',{'wood':4,'scrap':2},3,2,0,4),
]
structures = [{'id': f'EXP-BLD-{i:02d}', 'kind': kind, 'name': name,
               'cost': cost, 'work': work, 'terrain': terrain,
               'storage_bonus': storage, 'beds_bonus': beds,
               'max_health': 3} for i,(kind,name,cost,work,terrain,storage,beds)
              in enumerate(structures,1)]
locations = [
    ('garden_edge','Horta abandonada','natural',3,{'food':2},'near'),
    ('market','Mercado','urban',4,{'food':2,'water':1},'near'),
    ('workshop','Oficina','urban',3,{'scrap':2,'fuel':1},'medium'),
    ('hospital','Hospital','urban',3,{'medicine':2,'water':1},'medium'),
    ('station','Estação','urban',2,{'water':2,'scrap':1},'far'),
]
locations = [{'id':f'EXP-LOC-{i:02d}','kind':kind,'name':name,'renewal':renewal,
              'searches':searches,'loot':loot,'distance':distance}
             for i,(kind,name,renewal,searches,loot,distance) in enumerate(locations,1)]
crises = [
    ('garden_damage','Horta danificada','garden',2),
    ('locusts','Gafanhotos','garden',3),
    ('termites','Cupins','storage',3),
    ('contaminated_water','Água contaminada','reservoir',3),
    ('structural_damage','Estrutura comprometida','lodging',2),
]
crises = [{'id':f'EXP-CRI-{i:02d}','kind':kind,'name':name,'target':target,
           'cooldown_days':cooldown} for i,(kind,name,target,cooldown) in enumerate(crises,1)]
data = {'edition':'experimental-1','attributes':base['attributes'],
        'rules': {'actions':3,'health':3,'xp_cap':100,'combat_xp_cap':8,
                  'skill_unlock_xp':base['skill_unlock_xp'],'storage_base':30,
                  'beds_base':8,'terrain_base':7,'garden_growth_days':4,
                  'garden_food_per_harvest':2,'daily_food_per_resident':1,
                  'daily_water_per_resident':1,'crisis_chance_denominator':12,
                  'travel_segments':{'near':1,'medium':2,'far':3}},
        'heroes':heroes,'npcs':npcs,'structures':structures,
        'locations':locations,'crises':crises}
(root / 'system.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
