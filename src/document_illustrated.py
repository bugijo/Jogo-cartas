from pathlib import Path
import json,hashlib
from PIL import Image
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-ilustrada-v0.3'
from build_illustrated import REGIONS
old=json.loads((P/'content/asset_manifest.json').read_text());items=[]
for i in old['illustrations']:
 record=i.copy();record.pop('prompt',None);record['origin']='original existente (geração integrada 0.1)';record['integration_0.3']='Retrato canônico em ficha/token/encontro; demais objetos quando selecionados. Capa e cenas preservadas nas fontes.'
 if 'region' in record:
  record['dimensions_px']=list(Image.open(P/record['region']['path']).size)
  if Path(record['region']['path']).name in REGIONS:
   cols,rows=REGIONS[Path(record['region']['path']).name];l,r=cols[record['region']['col']];t,bot=rows[record['region']['row']];record['print_crop_0_3']=[l,t,r,bot]
 items.append(record)
for file,count,targets in [('environments.png',6,'Montagens dos seis destinos e mapa geral; arte de ambientação, não define geometria.'),('map_objects.png',16,'Camada A dos módulos comuns e temáticos; cartas/itens quando correspondente.'),('shelter.png',1,'Painel do abrigo, cena contínua com etiquetas vetoriais.')]:
 f=P/'assets/v0.3'/file;items.append(dict(file=str(f.relative_to(P)),id='ZC-ART-03-'+file.replace('.png',''),origin='geração integrada nesta sessão, sem API externa',dimensions_px=list(Image.open(f).size),regions=count,component=targets,status='integrado',sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
f=P/'assets/v0.3/map_objects_alpha.png';items.append(dict(file=str(f.relative_to(P)),origin='edição integrada do gerador: fundo transparente dos mesmos 16 objetos',dimensions_px=list(Image.open(f).size),component='Mapas e itens; substitui a prancha opaca na composição',status='integrado; não contado novamente como ilustração',sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
for file,target in [('src/illustrated_art.py','Pisos, texturas discretas, objetos suplementares e construções'),('src/build_illustrated.py','Molduras, textos, famílias, ícones funcionais, portas, campos, corte e calibração preservada')]:items.append(dict(file=file,origin='vetorial original por código',dimensions='milímetros / vetores escaláveis',component=target,status='integrado'))
manifest={'edition':'0.3','old_raster_regions':55,'new_raster_regions':23,'new_raster_files':3,'items':items,'limitations':['Retratos originais mantidos: aproximadamente 165 ppi na ficha; não foram ampliados artificialmente para alegar detalhe adicional.','Objetos raster pequenos em cartas: fonte 512×341 px, cerca de 300 ppi na área de 43×29 mm; mapas cerca de 170–210 ppi conforme escala de cada sprite.','Abrigo 1536×1024 px em 180×120 mm: cerca de 217 ppi; cenas de montagem cerca de 176 ppi.','Nem todas as 324 cartas da caixa antiga foram rediagramadas: a seleção física desta edição mantém exatamente as 114 cartas do kit 0.2. Catálogo completo e PDFs anteriores preservados.','Não houve impressão física nem playtest humano.']}
(P/'content/asset_manifest_0.3.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
text='# Inventário de arte — edição 0.3\n\nFontes anteriores preservadas: sete pranchas, 55 regiões. Foram produzidas e integradas três pranchas novas, **23 regiões ilustradas reais** (6 ambientes, 16 grupos de objetos e abrigo), além de arte vetorial funcional. Não se contam prompts como imagens. Detalhes por arquivo e região em [JSON](content/asset_manifest_0.3.json); edição anterior em content/asset_manifest.json.\n\n| Arquivo novo | Dimensões | Origem | Destino |\n|---|---|---|---|\n'
for it in items:
 if it.get('file','').startswith('assets/v0.3/') and '/economica/' not in it['file']:text+=f"| {it['file']} | {' × '.join(map(str,it['dimensions_px']))} px | {it['origin']} | {it['component']} |\n"
text+='\nOs SVGs de componentes em assets/v0.3/vetores/ são exportações vetoriais dos PDFs, com textos convertidos em caminhos apenas nesses arquivos auxiliares. Nos PDFs de impressão, textos continuam pesquisáveis com fonte incorporada. Código Python e JSON são as fontes editáveis primárias.\n\nA econômica deriva os mesmos arquivos para cinza e clareia a luminância em 25%, sem redesenhar personagens. O gerador reproduz essas derivações; não são novas ilustrações.\n\n## Limitações reais\n\n'+'\n'.join('- '+s for s in manifest['limitations'])+'\n\nAs plantas táticas têm geometria vetorial exata; objetos não criam obstáculos ou cobertura. A arte das montagens é ilustração de ambientação separada do diagrama jogável. Não há imagem essencial faltando para jogar o kit. A capa anterior permanece disponível, mas não acrescenta folha obrigatória à seleção.\n'
(P/'ASSET_MANIFEST.md').write_text(text)
print('Inventário gerado:',len(items),'registros; 23 novas regiões raster.')
