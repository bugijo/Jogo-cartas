"""Stable sheet regions. Raster source sheets are preserved in full."""
EQUIPMENT=['Pé de cabra','Faca','Machado','Pistola','Espingarda','Ferramentas','Lanterna','Bomba','Membrana']
BUILDINGS=['Barraca','Casa simples','Enfermaria','Oficina','Garagem','Torre','Horta','Filtro','Cozinha']
ENCOUNTERS=['Jana e criança','Bia','Vicente e Sol','Raul e Otávio','Denise, Miguel e civil','Samuel, Bruna e criança','Aline e cão','Hugo']
ENEMIES=['Errante','Corredor','Bruto','Rival']
def region(sheet,index,cols,rows):return dict(path='assets/'+sheet+'.png',col=index%cols,row=index//cols,cols=cols,rows=rows)
def lookup(name,family=''):
 if name in EQUIPMENT and family in ['EQU','PEC']:return region('equipment',EQUIPMENT.index(name),3,3)
 if name=='Cisterna / filtro':name='Filtro'
 if name in BUILDINGS and family in ['PRO','STR']:return region('buildings',BUILDINGS.index(name),3,3)
 if name in ENCOUNTERS and family=='MOR':return region('encounters',ENCOUNTERS.index(name),2,4)
 if name in ENEMIES:return region('enemies',ENEMIES.index(name),2,2)
