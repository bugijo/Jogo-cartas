"""Exportação JPEG 95 em pixels nativos; mantém máscaras alfa e texto vetorial."""
import io
from pathlib import Path
from PIL import Image
import fitz

def compact(path):
 path=Path(path);doc=fitz.open(path);refs={info[0] for p in doc for info in p.get_images(full=True)};changed=False
 for xref in refs:
  if doc.xref_get_key(xref,'Filter')[1]=='/DCTDecode':continue
  raw=doc.extract_image(xref)
  if raw['width']<128 or raw['height']<128:continue
  smask=doc.xref_get_key(xref,'SMask');im=Image.open(io.BytesIO(raw['image']));im=im.convert('L' if im.mode in ['L','1'] else 'RGB');stream=io.BytesIO();im.save(stream,format='JPEG',quality=95,subsampling=0)
  doc[0].replace_image(xref,stream=stream.getvalue())
  if smask[0]=='xref':doc.xref_set_key(xref,'SMask',smask[1])
  changed=True
 if changed:
  temp=path.with_suffix('.export.pdf');doc.save(temp,garbage=4,deflate=True);doc.close();temp.replace(path)
 else:doc.close()
