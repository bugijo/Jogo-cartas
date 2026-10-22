"""Generate the two-person quick guide from the selected PDF manifest."""
from __future__ import annotations

from math import ceil
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from final_kit_audit import ROOT, run

OUT=ROOT/'kit-final-prova/playtest'
pdfmetrics.registerFont(TTFont('ZBody','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ZBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=210*mm,297*mm


def files():
    selected=[x for x in run()['files'] if x['method'] in ('both','duplex')]
    assert len(selected)==18
    assert sum(x['sheets'] for x in selected)==58
    assert sum(x['pages'] for x in selected)==72
    return selected


def digital(rows):
    lines=['# Primeira partida — duas pessoas', '',
           'Escolha **duplex** para esta primeira sessão. Imprima os 18 PDFs abaixo, todas as páginas, '
           '**uma cópia de cada**, em A4 e 100% sem ajustar. São **58 folhas físicas**: 25 do kit inicial '
           'e 33 do complemento. As cartas e a calibração duplex usam A4 retrato, frente/verso na '
           '**borda longa**; painéis e mapas são de uma face. O método recortar e colar é uma alternativa '
           'completa de **72 folhas** no [índice consolidado](../INDICE_IMPRESSAO_CONSOLIDADO.md); não misture os conjuntos.', '',
           '| Etapa | PDF — imprimir todas as páginas | Páginas do PDF | Folhas A4 |',
           '|---|---|---:|---:|']
    for x in rows:
        p=Path(x['path'])
        lines.append(f"| {'Inicial' if x['stage']=='initial' else 'Complemento'} | [{p.name}](../../{x['path']}) | {x['pages']} | {x['sheets']} |")
    lines += ['', 'As 58 folhas **já incluem** `CALIBRACAO_DUPLEX.pdf`. A [prova de calibração adicional](CALIBRACAO_FRENTE_VERSO_A4.pdf) '
              'usa mais uma folha, se você quiser medir sua impressora antes da tiragem. Este guia (3 folhas) e '
              'as fichas de observação são extras opcionais.', '',
              '## Prepare a mesa', '',
              '1. Leia `COMECE_AQUI.pdf` páginas 1–2 e deixe `MANUAL.pdf` e `CAMPANHA.pdf` ao lado. '
              'As fontes oficiais são [RULES.md](../../RULES.md) §2 e [CAMPAIGN.md](../../CAMPAIGN.md) “Preparação dos destinos”.',
              '2. Monte os quatro módulos comuns: M1/M2 em cima, M3/M4 embaixo, corte 277 × 190 mm e una '
              'sem sobreposição. Use `MERCADO_MONTAGEM.pdf` para o primeiro destino. Marque entrada Z1 e surgimento S=Z16.',
              '3. No abrigo coloque quatro barracas T01–T04 (oito vagas), cozinha T05, depósito T06, '
              'cisterna danificada T07 e portão. Separe Lia e Ivo, suas fichas e peões; os Pés de cabra '
              'ZC-EQU-0001/0002 constam das fichas, sem folha adicional para H2.',
              '4. Embaralhe os 12 Vínculos e dê um a cada fundador, sem reposição. Nomeie acompanhantes '
              'humanos, anote família/estado; cão consome, mas não ocupa barraca. Conte C=humanos+cães.',
              '5. Ponha no estoque cartas cheias de Conserva e de Água: o menor inteiro de cartas que '
              'forneça pelo menos 2C porções de cada. Cada carta vale quatro porções. Para C=2: 1 de cada; '
              'C=3 ou 4: 2 de cada; C=5: 3 de cada. Acrescente 3 Materiais, 1 Lona, 2 Medicamentos, '
              '2 Munições, 1 Lanterna e 1 Ferramentas. Confira um Pé de cabra por herói nas fichas.',
              '6. Moral e Saúde começam 5; Pressão 0; relógio 0; sem veículo. Prepare lotes locais a partir '
              'do **C inicial** e nunca os recalcule após resgate. Cada lote contém `ceil(C/4)` cartas de '
              'quatro porções; veja a campanha para cada destino.',
              '7. Separe Viagem, Horda, Cerco, Saque de cada região e descarte correspondente. Ordene '
              'Eventos por dia. Intenções ficam face para baixo; só coloquem carta em envelope opaco e '
              'idêntico quando um grupo for acolhido. Separe reserva de componentes, estoque e inventários.',
              '8. Coloque `ceil(2/2)=1` Errante em S no Mercado, pressão local 0, portas conforme o diagrama. '
              'Cada ponto B tem três usos totais, não por herói.', '',
              '## Ensine jogando o primeiro dia', '',
              'Leia `COMECE_AQUI.pdf` páginas 3–5 junto à mesa e `CAMPANHA.pdf` no roteiro do Dia 1. '
              'No amanhecer leiam o Evento 1, escolham os heróis, equipamentos e trabalhos antes da saída. '
              'A rota curta até o Mercado gasta um segmento e revela Viagem. Cada rodada local gasta outro '
              'segmento; cada herói começa com 3 PA antes de condições. Na **primeira rodada da primeira '
              'visita ao Mercado**, o tutorial suspende ativação e surgimento de inimigos, mas ainda consome '
              'tempo e marca pressão local 1. Da segunda rodada em diante, apliquem combate, IA e Horda '
              'pelas regras oficiais (§§5–6). Abrir porta, mover e buscar têm custos distintos (§5).', '',
              'Após o retorno: resolvam, nessa ordem, até um cerco pendente, trabalhos, refeição, intenções '
              'e vencimento. Marquem porções abertas e saldos; recém-chegados também consomem. Consultem '
              'RULES §§7–12 sempre que surgirem carga, resgate, falta de comida, construção ou cerco.', '',
              '## Dias 2–5 e encerramento', '',
              'Usem `CAMPANHA.pdf` para os Eventos 2–5, objetivos e destinos. Há apenas uma expedição por dia; '
              'também é permitido permanecer no abrigo. Reservem peças do filtro no amanhecer **depois** '
              'da entrega e registrem quatro trabalhos A/B/C. Ao fim do dia 5, consultem as condições de '
              'vitória, derrota parcial e Noite de segurança em CAMPAIGN e RULES §12. Não há duração '
              'medida: cronometrem as fases no playtest.', '',
              '## Se algo falhar na fabricação', '',
              'Se uma folha sair fora de escala ou com verso desalinhado, reimprima a mesma folha após a '
              'calibração; não use cartas secretas identificáveis. Se optar pela montagem manual, imprima '
              '**todo** o conjunto correspondente do índice, com miolo opaco. Para token inimigo e carta '
              'de recurso faltantes, siga somente os registros numerados permitidos por RULES §§6–7, '
              'sem acrescentar porções. Para qualquer outro componente ausente, pause e reimprima; anote '
              'o ocorrido na ficha de observação.', '',
              'Extras recomendados: imprima este guia (3 folhas), a [página 2 do registro diário](ROTEIRO_E_REGISTRO_PLAYTEST.pdf) '
              '**cinco vezes** e a [ficha do observador](OBSERVADOR_E_DEVOLUTIVA.pdf) (2 folhas): 10 folhas extras. '
              'A página 1 do roteiro antigo repete a preparação deste guia e pode ficar no arquivo digital. '
              'Sem terceiro observador, um jogador anota ao fim de cada fase. Uma sessão pode ser pausada; '
              'anote ponto de parada e tempo real.']
    (OUT/'PRIMEIRA_PARTIDA_DUAS_PESSOAS.md').write_text('\n'.join(lines)+'\n')


def txt(c,x,y,value,size=8.5,bold=False):
    c.setFont('ZBold' if bold else 'ZBody',size)
    c.drawString(x*mm,y*mm,value)


def header(c,title,num):
    c.setFillColorRGB(.12,.27,.27);c.rect(0,H-21*mm,W,21*mm,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1);txt(c,12,281,title,14,True)
    c.setFillColorRGB(.08,.15,.16);txt(c,12,9,f'Zona Zero · primeira partida · {num}/3 · A4 100%, sem ajustar',7)


def paragraph(c,y,content,max_width=184,size=9,leading=5.4):
    words=content.split();line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if pdfmetrics.stringWidth(candidate,'ZBody',size)>max_width*mm and line:
            txt(c,13,y,line,size);y-=leading;line=word
        else:line=candidate
    if line:txt(c,13,y,line,size);y-=leading
    return y-3


def pdf(rows):
    p=OUT/'PRIMEIRA_PARTIDA_DUAS_PESSOAS.pdf'
    c=canvas.Canvas(str(p),pagesize=(W,H))
    header(c,'Imprima para duas pessoas',1)
    y=267
    y=paragraph(c,y,'Escolha duplex: 18 PDFs, todas as páginas, uma cópia de cada. 58 folhas A4 (25 iniciais + 33 complemento). Cartas e calibração: retrato, borda longa. Demais PDFs: uma face.',size=9)
    txt(c,13,y,'ETAPA   FOLHAS / PÁGINAS   ARQUIVO',8,True);y-=8
    for item in rows:
        stage='I' if item['stage']=='initial' else 'C'
        txt(c,13,y,f"{stage}   {item['sheets']:2} / {item['pages']:2}   {Path(item['path']).name}",8.3)
        y-=9.2
    y-=2
    y=paragraph(c,y,'I = inicial, C = complemento. Use os links e caminhos completos na versão digital deste guia. A calibração incluída é CALIBRACAO_DUPLEX.pdf. O outro PDF de calibração é opcional (+1 folha).',size=8)
    y=paragraph(c,y,'Alternativa recortar e colar: 72 folhas, conjunto inteiro no índice consolidado. Não misture os métodos.',size=8)
    c.showPage()
    header(c,'Prepare a mesa',2)
    y=265
    steps=[
      '1. Deixe COMECE_AQUI páginas 1–2, MANUAL e CAMPANHA ao lado. Regras oficiais: RULES §2; preparação dos destinos: CAMPAIGN.',
      '2. Una M1/M2 em cima e M3/M4 embaixo, 277 × 190 mm por módulo, sem sobreposição. MERCADO_MONTAGEM mostra a entrada Z1 e o surgimento S=Z16.',
      '3. Abrigo: barracas T01–T04 (8 vagas), cozinha T05, depósito T06, cisterna danificada T07 e portão. Separe Lia/Ivo, fichas e peões; os Pés de cabra 0001/0002 constam das fichas.',
      '4. Embaralhe 12 Vínculos; dê um a cada herói, sem reposição. Nomeie acompanhantes. Conte C=humanos+cães; cão consome, mas não ocupa vaga.',
      '5. Separe cartas cheias de Conserva e Água para pelo menos 2C porções de cada. C2: 1 carta; C3–4: 2; C5: 3. Cada carta tem 4 porções.',
      '6. Acrescente 3 Materiais, 1 Lona, 2 Medicamentos, 2 Munições, 1 Lanterna e 1 Ferramentas. Moral/Saúde 5, Pressão 0, relógio 0, sem veículo.',
      '7. Prepare os lotes de cada destino pelo C inicial (CAMPAIGN). Separe os baralhos Viagem, Horda, Cerco, Saque regional, Eventos por dia e Intenções secretas.',
      '8. Separe monte, descarte, reserva, estoque e inventários. Envelopes de intenção iguais; lacre apenas ao acolher. Mercado: 1 Errante em S, pressão local 0.',
    ]
    for s in steps:y=paragraph(c,y,s,size=9,leading=5.6)
    y-=2;txt(c,13,y,'Antes de começar, confira todos os humanos, cães, vagas e porções.',9,True)
    c.showPage()
    header(c,'Jogue, observe e registre',3)
    y=265
    sections=[
      ('Dia 1 — ensine em jogo','Leia COMECE_AQUI páginas 3–5 e CAMPAIGN, Dia 1. Amanhecer: Evento 1, escolha da equipe, equipamentos e trabalhos. Rota curta ao Mercado: 1 segmento e 1 Viagem. Cada rodada local gasta 1 segmento; heróis normalmente têm 3 PA.'),
      ('Exceção do tutorial','Somente na primeira rodada da primeira visita ao Mercado, suspenda ativação e surgimento de inimigos; a rodada ainda gasta tempo e marca pressão local 1. Depois aplique RULES §§5–6 literalmente.'),
      ('Noite e dias seguintes','Após retorno: um cerco pendente, trabalhos, refeição, intenções e vencimento. Consulte RULES §§7–12 para carga, consumo, resgate, obras e cercos. Nos dias 2–5 use os Eventos e objetivos de CAMPAIGN; só uma expedição por dia.'),
      ('Fim do quinto dia','Confira filtro, Saúde, Moral, última refeição e cercos pendentes em CAMPAIGN “Vitória e retirada” e RULES §12. Registre resultado e ponto de parada. O tempo da campanha será medido pelos jogadores.'),
      ('Quando faltar ou desalinha','Calibre e reimprima a mesma folha. Para montagem manual, use o conjunto inteiro do índice e miolo opaco. Tokens de inimigo e cartas físicas de recurso têm substituição numerada apenas como RULES §§6–7 permitem: sem criar porções. Outro componente ausente exige pausa e reimpressão.'),
    ]
    for title,body in sections:
        txt(c,13,y,title,10,True);y-=7
        y=paragraph(c,y,body,size=9,leading=5.7)-3
    txt(c,13,y,'Imprima: registro diário p. 2 × 5; ficha do observador 2 páginas.',9,True)
    c.showPage();c.save()


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    rows=files();digital(rows);pdf(rows)
    print(OUT/'PRIMEIRA_PARTIDA_DUAS_PESSOAS.md')
    print(OUT/'PRIMEIRA_PARTIDA_DUAS_PESSOAS.pdf')
