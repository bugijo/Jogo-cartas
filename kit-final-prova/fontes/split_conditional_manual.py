"""Create one-face card alternatives from the exact corrected duplex pages."""
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'kit-final-prova/componentes-condicionais'
OUT=BASE/'manual'
OUT.mkdir(parents=True,exist_ok=True)
for stem in ('PES_DE_CABRA_SEIS_FUNDADORES','REPOSICAO_H3_H4','REPOSICAO_H5_H6'):
    source=fitz.open(BASE/f'{stem}_DUPLEX.pdf')
    assert len(source)==2
    for page,label in ((0,'FRENTES'),(1,'VERSOS')):
        output=fitz.open()
        output.insert_pdf(source,from_page=page,to_page=page)
        path=OUT/f'{stem}_{label}.pdf'
        output.save(path,garbage=4,deflate=True)
        output.close()
        assert len(fitz.open(path))==1
    source.close()
