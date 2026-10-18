"""Exportações auxiliares editáveis; PDFs mantêm texto real, SVG usa contornos."""
from pathlib import Path
import fitz
P=Path(__file__).resolve().parents[1];S=P/'output/edicao-ilustrada-v0.3/ilustrada/01_inicial';O=P/'assets/v0.3/vetores';O.mkdir(exist_ok=True)
for file,name in [('04_modulos_locais.pdf','modulo_M1.svg'),('06_paineis_registros.pdf','abrigo.svg'),('08_divisorias.pdf','divisorias.svg')]:
 d=fitz.open(S/file);(O/name).write_text(d[0].get_svg_image(text_as_path=True))
print('3 SVGs exportados; texto real permanece nos PDFs.')
