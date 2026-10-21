"""Recortes de revisão derivados somente dos PDFs finais."""
from pathlib import Path
import fitz,importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];mm=72/25.4
for name in ['condominio']:
 S=P;stem=name.upper();sp=importlib.util.spec_from_file_location(name,S/'fontes/build.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
 doc=fitz.open(S/f'fontes/{stem}_REMONTADO.pdf');Image.open(S/f'{stem}_COM_GEOMETRIA.png').convert('L').save(S/f'provas/{stem}_CINZA.png')
 contact=Image.new('RGB',(1400,690),'#eee8da');d=ImageDraw.Draw(contact)
 for i,s in enumerate(v for v in b.segments() if v['connected']):
  x,y=s['center'];y=380-y;pix=doc[0].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect((x-20)*mm,(y-20)*mm,(x+20)*mm,(y+20)*mm),alpha=False);tile=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);tile.thumbnail((185,200));X=(i%7)*200;Y=(i//7)*230;contact.paste(tile,(X,Y+22));d.text((X+4,Y+4),str(s['key']),fill='black')
 contact.save(S/'provas/CONEXOES_21.jpg')
 # same 100mm square, before/after, true physical proof
 old=fitz.open(b.P/'output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/CONDOMINIO_M01_M04_LADO_A.pdf');before=b.joined(b.P/'output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/CONDOMINIO_M01_M04_LADO_A.pdf');proof=b.sheet_template(f'{stem} / COMPARAÇÃO EM ESCALA REAL',['Dois recortes iguais de 100 × 100 mm. Imprimir em 100%, sem ajustar.'],True)
 clip=fitz.Rect(95*mm,0,195*mm,100*mm)
 for i,source in enumerate([before,doc]):
  top=45+i*120;proof[0].show_pdf_page(fitz.Rect(55*mm,top*mm,155*mm,(top+100)*mm),source,0,clip=clip)
  proof[0].insert_font(fontname='ZZ',fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');proof[0].insert_text((55*mm,(top-3)*mm),['ANTERIOR','CONTÍNUO'][i],fontname='ZZ',fontsize=10)
 proof.save(S/'COMPARACAO_100MM_A4.pdf',garbage=4,deflate=True);b.render(proof,S/'provas/COMPARACAO_100MM.png')
