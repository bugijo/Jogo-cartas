"""Empacota impressão básica sem extras, extras opcionais e fontes. Verifica CRC e SHA."""
from pathlib import Path
import json,zipfile,hashlib,subprocess
P=Path(__file__).resolve().parents[1];O=P/'output/edicao-ilustrada-v0.3';DIST=P/'dist';DIST.mkdir(exist_ok=True)
records=[]
def make(name,files,prefix):
 f=DIST/name
 with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for path,rel in files:z.write(path,prefix+'/'+str(rel))
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None
  for path,rel in files:assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(z.read(prefix+'/'+str(rel))).digest()
 record=dict(file=name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),files=len(files));records.append(record);print(name,round(record['bytes']/1e6,1),'MB',len(files),'arquivos')
for edition in ['ilustrada','economica']:
 root=O/edition;m=json.loads((root/'manifesto.json').read_text());files=[]
 for key in ['initial','supplement']:
  for e in m[key]:files.append((root/e['file'],Path(e['file'])))
 for name in ['IMPRIMA-ESTES.md','manifesto.json']:files.append((root/name,Path(name)))
 make('Zona-Zero-0.3-'+edition+'-58-folhas.zip',files,'Zona-Zero-0.3-'+edition)
files=[(f,f.relative_to(O)) for edition in ['ilustrada','economica'] for f in sorted((O/edition/'extras').glob('*.pdf'))]
info=O/'EXTRAS-OPCIONAIS.md';info.write_text('# Extras opcionais — não necessários às 58 folhas\n\nEscolha uma edição. Por edição: seis mapas × quatro folhas = 24 folhas e fichas de 24 heróis = 12 folhas. Total opcional 36 folhas, incluindo fichas que repetem as do kit. Cada mapa substitui os quatro módulos comuns; não soma zonas. Não imprima ilustrada e econômica juntas. Não são novos personagens ou regras.\n')
files.append((info,Path(info.name)));make('Zona-Zero-0.3-extras-opcionais.zip',files,'Extras-Zona-Zero-0.3')
files=[]
for folder in ['src','content','assets','tests']:
 for f in sorted((P/folder).rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts and '/economica/' not in str(f):files.append((f,f.relative_to(P)))
for f in sorted(P.glob('*.md')):files.append((f,Path(f.name)))
files.append((P/'requirements.txt',Path('requirements.txt')));make('Zona-Zero-0.3-fontes-editaveis.zip',files,'Fontes-Zona-Zero-0.3')
files=[(f,Path('evidencias')/f.name) for f in sorted((O/'evidencias').iterdir()) if f.suffix in ['.jpg','.png','.json']]
for name in ['VISUAL_QA.md','ASSET_MANIFEST.md']:files.append((P/name,Path(name)))

for name in ['verificacao.json','duplex_visual.json','producao.json','geometry.json','duplex.json']:files.append((O/name,Path(name)))
make('Zona-Zero-0.3-conferencia-visual.zip',files,'Conferencia-Zona-Zero-0.3')
(O/'pacotes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
