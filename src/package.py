"""Empacota árvore pronta; não gera nem altera conteúdo do jogo."""
from pathlib import Path
import hashlib,zipfile,json,subprocess
P=Path(__file__).resolve().parents[1]
D=P/'dist';D.mkdir(exist_ok=True)
log=subprocess.check_output(['git','log','--oneline','--decorate'],cwd=P,text=True)
(P/'COMMIT_LOG.txt').write_text(log)
bundle=P/'history.bundle'
if bundle.exists():bundle.unlink()
subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=P,check=True)
def files():
 return sorted(f for f in P.rglob('*') if f.is_file() and not any(x in f.relative_to(P).parts for x in ['.git','dist','__pycache__']) and f.suffix!='.pyc' and f.name!='SHA256SUMS.txt')
selected=files();sums=[]
for f in selected:sums.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(P)))
(P/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n')
archive=D/'Zona-Zero-Comunidade-Prototipo-0.1.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in selected+[P/'SHA256SUMS.txt']:z.write(f,Path(P.name)/f.relative_to(P))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert P.name+'/README.md' in z.namelist()
 assert P.name+'/history.bundle' in z.namelist()
print(json.dumps(dict(zip=str(archive),bytes=archive.stat().st_size,files=len(selected)+1,sha256=hashlib.sha256(archive.read_bytes()).hexdigest()),indent=2))
