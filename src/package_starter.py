from pathlib import Path
import json,hashlib,zipfile,subprocess
P=Path(__file__).resolve().parents[1];R=P/'output/comece-aqui-duas-pessoas';M=json.loads((R/'manifesto.json').read_text());OUT=P/'dist';OUT.mkdir(exist_ok=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
(R/'COMMIT_0.2.txt').write_text('Commit: '+commit+'\nBranch: '+subprocess.check_output(['git','branch','--show-current'],cwd=P,text=True)+'Base preservada: db67f42\n')
# Include only current manifest PDFs: no drafts or unrelated old releases.
common=[(R/'LEIA-ME.md',Path('LEIA-ME.md')),(R/'manifesto.json',Path('manifesto.json')),(R/'COMMIT_0.2.txt',Path('COMMIT_0.2.txt')),(P/'REVISAO_0.2.md',Path('referencias/REVISAO_0.2.md')),(P/'PROFISSOES.md',Path('referencias/PROFISSOES.md'))]
result=[]
for key,label in [('initial','Inicial-25-folhas'),('supplement','Complemento-33-folhas'),('all','Completo-58-folhas')]:
 entries=M['initial']+M['supplement'] if key=='all' else M[key]
 files=[(R/e['file'],Path(e['file'])) for e in entries]+common
 if key=='all':
  for f in (R/'conferencia').iterdir():
   if f.is_file():files.append((f,Path('conferencia')/f.name))
  files +=[(P/'content/starter/01_guia.json',Path('fontes/01_guia.json')),(P/'src/build_starter.py',Path('fontes/build_starter.py')),(P/'output/revisao-0.2/replay_cinco_dias.json',Path('conferencia/replay_cinco_dias.json'))]
 zip_path=OUT/f'Comece-Aqui-Duas-Pessoas-0.2-{label}.zip'
 checksum='\n'.join(hashlib.sha256(src.read_bytes()).hexdigest()+'  '+str(dst) for src,dst in files)+'\n'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for src,dst in files:z.write(src,Path('Comece-Aqui-Duas-Pessoas-0.2')/dst)
  z.writestr('Comece-Aqui-Duas-Pessoas-0.2/SHA256SUMS.txt',checksum)
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None
  for src,dst in files:assert hashlib.sha256(z.read(str(Path('Comece-Aqui-Duas-Pessoas-0.2')/dst))).digest()==hashlib.sha256(src.read_bytes()).digest()
 result.append(dict(file=str(zip_path),bytes=zip_path.stat().st_size,sha256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),commit=commit))
print(json.dumps(result,ensure_ascii=False,indent=2))
