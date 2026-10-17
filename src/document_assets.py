from pathlib import Path
from PIL import Image
import json,hashlib
from asset_catalog import EQUIPMENT,BUILDINGS,ENCOUNTERS,ENEMIES,region
P=Path(__file__).resolve().parents[1];D=json.loads((P/'content/catalog.json').read_text());assets=[]
for f in sorted((P/'assets').glob('*.png')):
 im=Image.open(f);assets.append(dict(file=str(f.relative_to(P)),size=list(im.size),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),status='gerado pela ferramenta integrada; arquivo preservado'))
regions=[]
for h in D['heroes']:
 regions.append(dict(id=h['id'],kind='portrait',name=h['name'],region=h['art'],prompt=f"Retrato original adulto de {h['name']}, {h['profession']}, Santa Aurora brasileira fictícia. {h['story']} Graphic novel expressiva, petróleo, concreto, verde desbotado, ferrugem e âmbar; fundo claro; sem texto ou números; manter identidade da região de referência.",status='gerado e integrado à ficha e token'))
for sheet,labels,cols,rows in [('equipment',EQUIPMENT,3,3),('buildings',BUILDINGS,3,3),('enemies',ENEMIES,2,2),('encounters',ENCOUNTERS,2,4)]:
 for i,label in enumerate(labels):regions.append(dict(id=f'ZC-ART-{sheet.upper()}-{i+1:04}',kind=sheet,name=label,region=region(sheet,i,cols,rows),prompt=f'Ilustração original {label} em Santa Aurora, graphic novel em paleta petróleo/concreto/verde/ferrugem/âmbar, fundo claro, sem texto ou números. Usar região do manifesto como referência de identidade.',status='gerado e integrado à galeria; cartas/tokens quando correspondente'))
(P/'content/asset_manifest.json').write_text(json.dumps(dict(files=assets,illustrations=regions,cover='assets/cover.png',raster_illustrations=1+len(regions)),ensure_ascii=False,indent=2))
(P/'ASSET_MANIFEST.md').write_text('# Manifesto real de arte\n\n7 arquivos PNG de geração integrada; 55 ilustrações em regiões: capa 1, retratos 24, inimigos/rival 4, objetos 9, construções 9, encontros 8. Regiões, hashes, dimensões e prompts individuais em content/asset_manifest.json. As pranchas originais são preservadas; nenhuma regra usa texto gerado. As regiões são recortadas pela janela do PDF e não exigem edição dos PNG.\n\nIntegração: capa no PDF 00, retratos em fichas e tokens; objetos e construções em cartas correspondentes; encontros nas cartas; inimigos nos tokens. Galeria 11 é referência opcional.\n\nPendências reais: mapas têm planta vetorial funcional, mas não seis cenários ilustrados finais distintos. Faltam ilustrações específicas para Conexões, Bateria, Kit de instalação, Bancada, portão e depósito; os componentes estão presentes e legíveis por texto, sem impedir o protótipo. Não contar esses itens como arte raster produzida. Ícones e logotipo vetoriais são originais. Refinamento de consistência entre retratos e cenas de encontro depende de revisão artística humana.\n')
print(len(assets),'arquivos;',1+len(regions),'ilustrações por regiões')
