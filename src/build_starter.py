"""Seleção e diagramação do conteúdo existente para duas pessoas, sem novos baralhos."""
from pathlib import Path
import json,math,shutil,html
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
import build as b
P=b.P;D=b.D;ROOT=P/'output/comece-aqui-duas-pessoas';I=ROOT/'01_inicial';S=ROOT/'02_complemento';R=P/'output/revisao-0.2'
for p in [I,S,ROOT/'conferencia']:p.mkdir(parents=True,exist_ok=True)
manifest={'version':'0.2','base_commit':'db67f42','heroes':2,'evaluated_expressions':{'ceil(H/2)':1},'initial':[],'supplement':[],'initial_cards':[],'supplement_cards':[],'embedded_equipment':['ZC-EQU-0001','ZC-EQU-0002']}
def add(folder,name,duplex=False,kind=''):
 f=folder/name;pages=len(fitz.open(f));record=dict(file=str(f.relative_to(ROOT)),pages=pages,sheets=math.ceil(pages/2) if duplex else pages,duplex=duplex,orientation='paisagem' if fitz.open(f)[0].rect.width>fitz.open(f)[0].rect.height else 'retrato',kind=kind)
 manifest['initial' if folder==I else 'supplement'].append(record)
def extract(src,pages,out):
 a=fitz.open(src);z=fitz.open()
 if pages==list(range(pages[0],pages[-1]+1)):z.insert_pdf(a,from_page=pages[0],to_page=pages[-1])
 else:
  for n in pages:z.insert_pdf(a,from_page=n,to_page=n)
 z.save(out,garbage=4,deflate=True)
def guide():
 styles={k:ParagraphStyle(k,fontName='Bold' if k!='body' else 'Body',fontSize=s,leading=l,textColor=b.INK,spaceAfter=6,spaceBefore=5 if k=='h' else 0) for k,s,l in [('title',21,25),('sub',10,13),('h',12,16),('body',10.3,13.6)]}
 flow=[];pages=json.loads((P/'content/starter/01_guia.json').read_text())
 for i,page in enumerate(pages):
  if i:flow.append(PageBreak())
  flow.extend([Paragraph(html.escape(page['title']),styles['title']),Paragraph(html.escape(page['subtitle']),styles['sub']),Spacer(1,5*mm)])
  for title,text in page['sections']:flow.extend([Paragraph(html.escape(title),styles['h']),Paragraph(html.escape(text),styles['body'])])
 doc=SimpleDocTemplate(str(I/'01_comece_aqui.pdf'),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=15*mm,bottomMargin=17*mm)
 doc.build(flow,onFirstPage=b.foot,onLaterPages=b.foot);add(I,'01_comece_aqui.pdf',kind='guia')
def cards():
 initial=[];equipment_names={'Faca'};one=set()
 for c in D['cards']:
  take=c['family'] in ['VIN','INT','VIA','HOR','CER'] or c.get('region')=='MER' or (c['family']=='MOR' and c['name']=='Jana e criança')
  if c['family']=='EQU':
   if c['name']=='Faca':take=True
   if c['name'] in ['Ferramentas','Lanterna'] and c['name'] not in one:take=True;one.add(c['name'])
  if take:
   printed=c.copy();printed['text']=c['text'].replace('ceil(H/2)','1');initial.append(printed)
 assert len(initial)==62
 initial_ids={x['id'] for x in initial}
 extras=[]
 for c in D['cards']:
  if c['id'] in initial_ids:continue
  if c['family'] in ['SAQ','MOR','PEC','VEI'] or (c['family']=='EQU' and c['name']!='Pé de cabra'):extras.append(c)
 assert len(extras)==52
 for folder,cards,name in [(I,initial,'02_cartas_duplex.pdf'),(S,extras,'01_cartas_complemento_duplex.pdf')]:
  b.O=folder;b.cards(cards,name);add(folder,name,True,'cartas')
 manifest['initial_cards']=[c['id'] for c in initial];manifest['supplement_cards']=[c['id'] for c in extras]
def heroes():
 extract(R/'04_fichas_personagens.pdf',[0],I/'03_lia_ivo.pdf')
 f=I/'03_lia_ivo.pdf';doc=fitz.open(f)
 for i,h in enumerate(['Lia','Ivo']):
  x,y,w,hgt=55*mm,(94+148.5*i)*mm,145*mm,20*mm
  doc[0].draw_rect(fitz.Rect(x,y,x+w,y+hgt),color=(.1,.24,.26),width=.5)
  txt=f'ITEM ÚNICO ZC-EQU-000{i+1} | Pé de cabra | carga 1\nAtaque próximo: 1 PA, d6+Corpo contra Defesa, dano 1.\nLocal inicial: {h}. Local atual: __________. Transferir altera o local; nunca cria outra cópia.'
  doc[0].insert_textbox(fitz.Rect(x+2*mm,y+2*mm,x+w-2*mm,y+hgt-1*mm),txt,fontname='helv',fontsize=8.6,color=(.1,.24,.26))
 tmp=f.with_suffix('.tmp.pdf');doc.save(tmp,deflate=True);doc.close();tmp.replace(f);add(I,f.name,kind='fichas')
 extract(R/'04_fichas_personagens.pdf',list(range(6,12)),S/'02_herois_resgataveis.pdf');add(S,'02_herois_resgataveis.pdf',kind='fichas')
def ledger_page(c,title,rows=24):
 W,H=landscape(A4);b.title(c,title,W,H,'Um ID por item/lote • E estoque / L Lia / I Ivo / V van / P projeto / C destino+zona • vazio = reserva')
 b.para(c,'Conserva, Carne e Água: até 4 porções por lote; uma carga por lote, mesmo parcial. Outros bens: 1 unidade/carga, salvo peça marcada. Não duplique cartas físicas no registro. Carga por herói: 4; Van: 12. Ao mover, risque o lugar antigo. Reaproveite linha vazia com NOVO ID.',10*mm,160*mm,277*mm,22*mm,9.5)
 widths=[23,53,26,30,50,95];headers=['ID','Recurso / item','Porções','Carga','Local / dono','Origem / dia / observação']
 xs=[10]
 for w in widths:xs.append(xs[-1]+w)
 top=157
 for col,label in enumerate(headers):b.para(c,label,xs[col]*mm,(top-7)*mm,widths[col]*mm,6*mm,8.2,bold=True)
 for r in range(rows):
  for col in range(6):c.setStrokeColor(b.HexColor('#aeb6b1'));c.rect(xs[col]*mm,(top-7-(r+1)*5.7)*mm,widths[col]*mm,5.7*mm)
 c.showPage()
def panels():
 name='06_paineis_registros.pdf';W,H=landscape(A4);c=canvas.Canvas(str(I/name),pagesize=(W,H))
 b.title(c,'ABRIGO / DUAS PESSOAS',W,H,'Estado inicial já impresso; use lápis para projeto, dano e alterações. Cartas de Estrutura não são necessárias.')
 labels=['Barraca • 2 vagas','Barraca • 2 vagas','Barraca • 2 vagas','Barraca • 2 vagas','Cozinha ativa','Depósito ativo','Cisterna danificada','Livre','Livre','Livre','Livre','Livre']
 for n,text in enumerate(labels):
  r,col=divmod(n,4);x=(10+col*45)*mm;y=(127-r*40)*mm;c.setStrokeColor(b.INK);c.rect(x,y,43*mm,37*mm)
  b.para(c,f'T{n+1:02}\n{text}\nDano □ Projeto ____',x+2*mm,y+3*mm,39*mm,31*mm,8.8)
 b.para(c,'Portão ativo □ Defesa 2\nDia: 1 2 3 4 5\nMoral: 0 1 2 3 4 5\nSaúde: 0 1 2 3 4 5\nPressão: 0 1 2 3\nPonte conhecida □\nRelação −2 −1 0 +1 +2\nFila de cercos:\n________________\nC inicial ___ Vagas 8\nConsumidores hoje ___',196*mm,68*mm,91*mm,91*mm,10)
 b.para(c,'FILTRO / T7 — A: Material+Conexões+1 trabalho □  B: Material+Bomba+1 □  C: Material+Membrana+2 □□\nMáximo dois trabalhos/dia. Ao concluir: 2C água uma vez; depois C por amanhecer. Ativo □ Danificado □\nProjeto B: terreno ____ custos reservados ____ trabalho 0 1 2 3 4\nRelógio: 0 1 2 3 4 5 6 7 8 | 9 10   Pressão local 0 1   Rota curta 1+1 / longa 2+2',10*mm,10*mm,277*mm,32*mm,9.8)
 c.showPage();b.title(c,'MORADORES, TAREFAS E DESTINO',W,H,'Toda pessoa tem identidade, estado e função. Crianças não trabalham ou combatem. Registre cães como consumidores.')
 heads=['ID / nome / família','Adulto/criança/cão','Fer/fad/XP','Fome/Sede/noites','Chegada/obs/vaga','Função/investigação']
 for j,text in enumerate(heads):b.para(c,text,(10+46*j)*mm,164*mm,44*mm,15*mm,8.2,bold=True)
 for r in range(10):
  for col in range(6):c.setStrokeColor(b.HexColor('#aeb6b1'));c.rect((10+46*col)*mm,(153-r*10)*mm,46*mm,10*mm)
 b.para(c,'Tarefas antes de sair: pessoa → tarefa → alvo: ______________________________________________\nDestino/data ___ Portas abertas ___ B1 usos 3 2 1 0  B2 usos 3 2 1 0  Última visita ___\nMercado: comida O1 lote A □ B □ / água O2 lote A □ B □ / Facas 1 □ 2 □ / Jana+criança acolhidas □\nOutros destinos: lotes / peças / equipamentos / pessoas já retirados ____________________________\nItens no chão: ID / destino / zona ____________________ Promessas e prazos ____________________\nFim do dia: comida ___ água ___ Estado do veículo ___ Combustível ___ Passageiros ___ Carga ___',10*mm,10*mm,277*mm,46*mm,9.5)
 c.showPage();ledger_page(c,'RECURSOS E CARGA / REGISTRO 1');c.save();add(I,name,kind='painéis')
 c=canvas.Canvas(str(S/'07_registro_adicional.pdf'),pagesize=(W,H));ledger_page(c,'RECURSOS E CARGA / REGISTRO 2');ledger_page(c,'RECURSOS E CARGA / REGISTRO 3');c.save();add(S,'07_registro_adicional.pdf',kind='registro')
def tokens(folder,tokens,name):
 c=canvas.Canvas(str(folder/name),pagesize=A4);W,H=A4;heroes={h['id']:h for h in D['heroes']}
 for i,t in enumerate(tokens):
  row,col=divmod(i,6);x=(10+col*32)*mm;y=H-(15+(row+1)*32)*mm;c.setStrokeColor(b.INK);c.rect(x,y,29*mm,29*mm)
  if t['kind']=='hero':b.clip_portrait(c,heroes[t['hero_ref']],x+2*mm,y+8*mm,25*mm,19*mm)
  elif t['kind']=='enemy':b.para(c,t['name']+'\nTipo E/C/B ___\nVida ___',x+2*mm,y+6*mm,25*mm,20*mm,9,bold=True)
  else:b.para(c,t['name'],x+2*mm,y+7*mm,25*mm,18*mm,10,bold=True)
  c.setFont('Body',6.8);c.setFillColor(b.INK);c.drawCentredString(x+14.5*mm,y+3*mm,t['name'] if t['kind']=='hero' else t['id'])
 c.showPage();c.save();add(folder,name,kind='marcadores')
def markers():
 used=[]
 for h in ['ZC-HER-0001','ZC-HER-0002']:used+= [next(t for t in D['tokens'] if t['hero_ref']==h)]
 used += [t for t in D['tokens'] if t['kind']=='enemy']
 for name,n in [('Porta',5),('Bloqueio',1),('Busca',6),('Relógio',1),('Pressão',1),('Fome',2),('Sede',2),('Verificado',1)]:used += [t for t in D['tokens'] if t['name']==name][:n]
 assert len(used)==45
 tokens(I,used,'07_marcadores.pdf');manifest['initial_tokens']=[t['id'] for t in used]
 extra=[t for t in D['tokens'] if t['kind']=='hero' and int(t['hero_ref'][-4:])>=13];tokens(S,extra,'08_tokens_resgataveis.pdf');manifest['supplement_tokens']=[t['id'] for t in extra]
def dividers():
 name='08_divisorias.pdf';c=canvas.Canvas(str(I/name),pagesize=A4);W,H=A4
 labels=['VÍNCULOS','INTENÇÕES','VIAGEM','HORDA','CERCO','SAQUE MERCADO','SAQUE HOSPITAL','SAQUE OFICINA','SAQUE POSTO','SAQUE CONDOMÍNIO','SAQUE ESTAÇÃO','EQUIPAMENTOS / ENCONTROS']
 for i,text in enumerate(labels):
  r,col=divmod(i,2);x=(10+96*col)*mm;y=H-(14+(r+1)*44)*mm;c.setStrokeColor(b.INK);c.rect(x,y,90*mm,40*mm);b.para(c,text,x+4*mm,y+17*mm,82*mm,19*mm,11,bold=True);b.para(c,'RESERVA' if i==11 else 'MONTE (esquerda) | DESCARTE (direita)',x+4*mm,y+10*mm,82*mm,6*mm,7.8);c.setDash(3,2);c.line(x,y+8*mm,x+90*mm,y+8*mm);c.setDash()
 c.showPage();c.save();add(I,name,kind='organização')
def static():
 shutil.copyfile(R/'06_mapas_modulos.pdf',I/'04_modulos_locais.pdf');add(I,'04_modulos_locais.pdf',kind='mapas')
 extract(R/'07_montagens_destinos.pdf',[0],I/'05_montagem_mercado.pdf');add(I,'05_montagem_mercado.pdf',kind='montagem')
 shutil.copyfile(R/'10_calibracao_duplex.pdf',I/'09_calibracao_duplex.pdf');add(I,'09_calibracao_duplex.pdf',True,'calibração')
 extract(R/'07_montagens_destinos.pdf',list(range(1,6)),S/'03_montagens_restantes.pdf');add(S,'03_montagens_restantes.pdf',kind='montagens')
 for source,name in [('01_manual_iniciantes.pdf','04_manual_revisado.pdf'),('02_campanha.pdf','05_campanha_cinco_dias.pdf')]:shutil.copyfile(R/source,S/name);add(S,name,kind='regras')
 extract(R/'05_paineis_registros.pdf',[1],S/'06_mapa_geral.pdf');add(S,'06_mapa_geral.pdf',kind='mapa geral')
 extract(R/'05_paineis_registros.pdf',[2],S/'09_moradores_adicional.pdf');add(S,'09_moradores_adicional.pdf',kind='registro')
 # Visible project recipes already exist in the manual; no construction deck is needed.
 manifest['represented_on_references']=['EVE','PRO','STR','MIS','AJU','REC']
def write_index():
 for key in ['initial','supplement']:
  manifest[key].sort(key=lambda x:x['file'])
  manifest[key+'_sheets']=sum(x['sheets'] for x in manifest[key])
 manifest['total_sheets']=manifest['initial_sheets']+manifest['supplement_sheets'];(ROOT/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 text='# Comece Aqui — Duas Pessoas\n\nEdição 0.2. Lia e Ivo, famílias sorteadas, mesmos baralhos e mesmas regras da campanha revisada. Nenhuma missão, herói, carta ou ilustração nova.\n\n'
 text+=f"**Primeira impressão: {manifest['initial_sheets']} folhas A4 para o dia 1. Complemento: {manifest['supplement_sheets']} folhas antes do dia 2. Capítulo completo: {manifest['total_sheets']} folhas**, sem repetir componentes comuns. Inclui calibração; não inclui cópias extras opcionais de registros.\n\n"
 for key,title in [('initial','Imprima primeiro — Dia 1'),('supplement','Imprima antes do Dia 2 — segue até o Dia 5')]:
  text+='## '+title+'\n\n| PDF | Páginas | Folhas | Regime |\n|---|---:|---:|---|\n'
  for e in manifest[key]:text+=f"| [{Path(e['file']).name}]({e['file']}) | {e['pages']} | {e['sheets']} | {'Duplex borda longa' if e['duplex'] else 'Uma face'} / {e['orientation']} |\n"
  text+='\n'
 text+='## Ordem para começar\n\n1. Calibração a 100%, sem ajustar: meça 100 mm e confira frente/verso.\n2. Leia o guia, escolha quem controla Lia/Ivo, sorteie vínculos e registre porções.\n3. Separe montes e descartes nas divisórias. Intenções em envelopes/sleeves opacos; nunca abra antes do gatilho.\n4. Monte os quatro módulos usando o diagrama Mercado e jogue o primeiro dia.\n5. Guarde estado e descartes; imprima só o complemento para continuar.\n\nDados (três d6), lápis, borracha, tesoura, fita e envelopes opacos são materiais externos necessários. Não há aplicativo obrigatório.\n\n## Representações sem duplicação\n\nAs cartas de Horda/Viagem já trazem a quantidade calculada para dois heróis (metade arredondada para cima = um); não alteram a composição do monte. Os dois pés de cabra únicos estão nas fichas. Recursos têm registros numerados: no máximo quatro porções por lote de comida/água, uma carga por lote, mesmo parcial. Cada outro item mantém seu custo de carga. Cada item tem exatamente um lugar. As quatro barracas e estruturas iniciais estão no painel. Projetos e eventos são consultados no manual/campanha, não precisam de cartas adicionais. Guardem o espaço vazio nas folhas como sobra de papel; não é componente.\n\nO marcador E01–E24 recebe tipo E (Errante), C (Corredor) ou B (Bruto) e Vida por lápis; os valores estão no guia. Marque uso de Busca e portas no próprio mapa. Nas montagens posteriores reaproveite os marcadores existentes. As fichas resgatáveis e tokens extras estão no complemento.\n\nNão imprima a caixa 0.1 junto deste kit. As referências revisadas 0.2 prevalecem. Arquivos antigos foram preservados. Sem teste físico/humano nesta rodada.\n'
 (ROOT/'LEIA-ME.md').write_text(text)
 # Preserve obsolete drafts outside printable folders so selecting all PDFs is safe.
 archive=R/'rascunhos-gerados';archive.mkdir(exist_ok=True)
 for key,folder in [('initial',I),('supplement',S)]:
  expected={Path(x['file']).name for x in manifest[key]}
  for f in folder.glob('*.pdf'):
   if f.name not in expected:shutil.move(str(f),str(archive/f.name))
if __name__=='__main__':
 guide();cards();heroes();panels();markers();dividers();static();write_index()
 (ROOT/'conferencia/layout_boxes.json').write_text(json.dumps(b.boxes,ensure_ascii=False,indent=2));(ROOT/'conferencia/layout_issues.json').write_text(json.dumps(b.issues,ensure_ascii=False,indent=2))
 print('Inicial:',manifest['initial_sheets'],'Complemento:',manifest['supplement_sheets'],'Total:',manifest['total_sheets'],'Estouros:',b.issues)
