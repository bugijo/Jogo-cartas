"""Integra os 39 IDs VIN/VIA/HOR/CER nas 114 cartas da prova anterior."""
from pathlib import Path
import json, sys, math
import fitz
from PIL import Image, ImageDraw
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

S = Path(__file__).resolve().parents[1]
P = next(p for p in S.parents if (p/'content/catalog.json').exists())
sys.path.insert(0, str(P/'src'))
import build_finish as f

f.setup()
g = f.f
original = g.artwork
L03 = S.parent/'lote-03-personagens'
L04 = S.parent/'lote-04-cartas'
L06 = S.parent/'lote-06-itens'
L07 = S.parent/'lote-07-moradores'
H = f.D['heroes'][6:]
BOXES = {2:([20,500,975],[461,937,1417],[16,553],[515,1080]),
         3:([18,496,975],[460,940,1418],[15,558],[515,1074]),
         4:([16,495,975],[461,941,1419],[16,540],[503,1081])}
OLD = {**{n:('ARMAS_CENAS',i) for i,n in enumerate(['Faca','Machado','Pistola','Espingarda'])},
       **{n:('SUPRIMENTOS_CENAS',i) for i,n in enumerate(['Ferramentas','Conserva','Água','Combustível'])},
       **{n:('PECAS_CENAS',i) for i,n in enumerate(['Bomba','Membrana','Conexões','Bateria'])},
       **{n:('INTENCOES_CENAS',i) for i,n in enumerate(['Solidário','Assustado','Oportunista','Infiltrado'])}}
MORE = {**{n:('SAQUES_COMPLEMENTARES',i) for i,n in enumerate(['Material','Munição','Medicamento','Carne'])},
        **{n:('UTILITARIOS_VEICULO',i) for i,n in enumerate(['Lanterna','Kit de instalação médica','Bancada','Van de manutenção'])}}

def new_scene(card):
    fam = card['family']
    n = int(card['id'].split('-')[-1])
    if fam == 'VIN':
        slot = 0 if n <= 4 else 1 if n <= 8 else 2 if n <= 10 else 3
        return 'VIN_CENAS', slot
    if fam == 'VIA': return f'VIA_CENAS_{(n-1)//4+1:02}', (n-1)%4
    if fam == 'HOR': return 'HOR_CENAS', 0 if n <= 4 else 1 if n <= 6 else 2 if n <= 8 else 3
    if fam == 'CER': return ('CER_CENAS_01',n-1) if n <= 4 else ('CER_CENAS_02',n-5)
    return None

USED = []
def art(c,card,x,y,w,h):
    scene = new_scene(card)
    if scene:
        sheet, slot = scene
        path = S/'originais'/f'{sheet}.png'
        im = Image.open(path).convert('RGB')
        pw,ph = im.size
        # O gerador deixa um divisor claro. O recuo evita vazá-lo para a carta.
        col,row = slot%2,slot//2
        box = (round(col*pw/2+12),round(row*ph/2+12),
               round((col+1)*pw/2-12),round((row+1)*ph/2-12))
        crop=im.crop(box)
        scale=min(w/crop.width,h/crop.height)
        ww,hh=crop.width*scale,crop.height*scale
        c.drawImage(ImageReader(crop),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm)
        USED.append(dict(id=card['id'],source=str(path.relative_to(P)),crop_pixels=list(box),
                         print_box_mm=[round(ww,2),round(hh,2)],effective_ppi=round(25.4/scale,1)))
        return
    # Mesmo tratamento do lote 07 para os outros 75 IDs; nenhum retrato é regenerado.
    if card['family']=='MOR':
        heroes=[z for z in H if z['name'] in card['name']]
        assert heroes,card['name']
        for j,hero in enumerate(heroes):
            k=next(k for k,z in enumerate(H) if z['id']==hero['id']);batch=k//6+2;pos=k%6
            col,row=pos%3,pos//3;l,r,t,b=BOXES[batch];box=(l[col],t[row],r[col],b[row])
            im=Image.open(L03/'originais'/f'RETRATOS_{batch:02}.png').crop(box)
            xx=x+j*w/len(heroes);slot=w/len(heroes);scale=max(slot/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale
            c.saveState();cp=c.beginPath();cp.rect(xx*mm,y*mm,slot*mm,h*mm);c.clipPath(cp,stroke=0)
            c.drawImage(ImageReader(im),(xx+(slot-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm);c.restoreState()
        return
    name=card['name'].split(': ')[-1]
    if name in MORE:sheet,i=MORE[name];path=L06/'originais'/f'{sheet}.png'
    elif name in OLD:sheet,i=OLD[name];path=L04/'originais'/f'{sheet}.png'
    else:return original(c,card,x,y,w,h)
    im=Image.open(path);cw,ch=im.width/2,im.height/2
    box=(int(i%2*cw+7),int(i//2*ch+7),int((i%2+1)*cw-7),int((i//2+1)*ch-7))
    if sheet=='SUPRIMENTOS_CENAS':box=([7,7,754,462],[783,7,1529,462],[7,485,754,1017],[783,485,1529,1017])[i]
    crop=im.crop(box);scale=min(w/crop.width,h/crop.height);ww,hh=crop.width*scale,crop.height*scale
    c.drawImage(ImageReader(crop),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm)

def main():
    sel=f.M['initial_cards']+f.M['supplement_cards']
    assert len(sel)==114 and len(set(sel))==114
    target={x['id'] for x in f.D['cards'] if x['id'] in sel and new_scene(x)}
    assert len(target)==39
    root=S/'pdfs';g.init(root);g.artwork=art
    g.all_cards(root)
    g.cards_pdf(root,sorted(target),'PROVA_39_CARTAS_DUPLEX.pdf',True)
    g.artwork=original
    baseline=L07/'pdfs';checks=[]
    for path in sorted(root.rglob('*.pdf')):
        rel=path.relative_to(root);before=fitz.open(baseline/rel) if (baseline/rel).exists() else None;after=fitz.open(path)
        if before:
            assert len(before)==len(after),rel
            assert [p.get_text() for p in before]==[p.get_text() for p in after],rel
        for i,p in enumerate(after):
            assert abs(p.rect.width-210*mm)<.01 and abs(p.rect.height-297*mm)<.01,(rel,i,p.rect)
            if before and 'DUPLEX' in path.name and i%2:
                assert p.get_pixmap().samples==before[i].get_pixmap().samples,('verso diferente',rel,i)
            for font in p.get_fonts(full=True):
                if font[2]=='Type0':assert after.extract_font(font[0])[3]
            out=S/'provas'/rel.parent;out.mkdir(parents=True,exist_ok=True)
            p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(out/f'{path.stem}_{i+1:02}.png')
        checks.append(dict(file=str(rel),pages=len(after),a4=True,text_identical=bool(before),versos_identicos=bool(before)))
    # Prova do alvo e comparação extraídas do PDF efetivo.
    pairs=[]
    for family in ('VIN','VIA','HOR','CER'):
        found=None
        for filename in ('KIT_INICIAL_1_DUPLEX.pdf','KIT_COMPLEMENTO_2_DUPLEX.pdf'):
            old=fitz.open(baseline/'02_CARTAS_DUPLEX'/filename)
            new=fitz.open(root/'02_CARTAS_DUPLEX'/filename)
            for i in range(0,len(new),2):
                if f'ZC-{family}-' in new[i].get_text():
                    found=(old,new,i);break
            if found:break
        assert found,family
        pairs.append((family,*found))
    for family,before,after,i in pairs:
        board=Image.new('RGB',(1300,900),'#eee8d9');d=ImageDraw.Draw(board)
        for j,doc in enumerate((before,after)):
            p=doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
            im=Image.frombytes('RGB',(p.width,p.height),p.samples);im.thumbnail((625,850))
            board.paste(im,(j*650,25));d.text((j*650+15,5),('ANTES','DEPOIS')[j],fill='black')
        board.save(S/'provas'/f'COMPARACAO_{family}.jpg',quality=94)
    (S/'fontes/resolucao.json').write_text(json.dumps(USED,ensure_ascii=False,indent=2)+'\n')
    (S/'VERIFICACOES.json').write_text(json.dumps(dict(selected_ids=sel,changed_ids=sorted(set(x['id'] for x in USED)),
        changed_count=len(set(x['id'] for x in USED)),pdfs=checks,min_ppi=min(x['effective_ppi'] for x in USED),
        preserved_text=True,preserved_backs=True,physical_print=False),ensure_ascii=False,indent=2)+'\n')
    print('Cartas selecionadas',len(sel),'arte nova',len(set(x['id'] for x in USED)),'ppi minimo',min(x['effective_ppi'] for x in USED))

if __name__=='__main__':main()
