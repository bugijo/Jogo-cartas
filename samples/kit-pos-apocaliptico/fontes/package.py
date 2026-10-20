"""Empacota provas locais, sem publicar nem incluir caches/dependências."""
from pathlib import Path
import zipfile,subprocess,json,hashlib
P=Path(__file__).resolve().parents[3];S=P/'samples/kit-pos-apocaliptico';O=P.parent/'entregas-zona-zero/provas-pos-apocalipticas';O.mkdir(parents=True,exist_ok=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
sets={
 'ZONA_ZERO_PROVAS_PDFS.zip':list((S/'pdfs').glob('*.pdf'))+list(S.glob('*.md')),
 'ZONA_ZERO_FONTES_ARTE.zip':list((S/'originais').glob('*.png'))+list((S/'fontes').glob('*.py'))+list((S/'fontes').glob('*.json'))+list((S/'fontes').glob('*.log'))+list(S.glob('*.md')),
 'ZONA_ZERO_COMPARACOES.zip':list((S/'provas').glob('COMPARACAO*.jpg'))+list((S/'provas').glob('COMPARACAO_100MM*.png'))+list((S/'provas').glob('*DEPOIS_MONTADA.png'))+list((S/'provas').glob('*21_CONEXOES.jpg'))+[S/'provas/CONTATO_TODAS_PAGINAS.jpg',S/'VISUAL_QA.md']
}
result=[]
for name,files in sets.items():
 with zipfile.ZipFile(O/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.writestr('COMMIT.txt',commit+'\nBranch: arte/kit-pos-apocaliptico-provas\nBase: 48f5794\nPacotes locais; sem publicação.\n')
  for path in sorted(set(files)):z.write(path,str(path.relative_to(S)))
 with zipfile.ZipFile(O/name) as z:assert z.testzip() is None
 result.append(dict(file=name,bytes=(O/name).stat().st_size,sha256=hashlib.sha256((O/name).read_bytes()).hexdigest()))
(O/'manifesto-downloads.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
