"""Standalone A4 calibration and human-playtest forms; no game components changed."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'kit-final-prova'/'playtest'
W,H = 210*mm,297*mm
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))


def label(c, x, y, s, size=9):
    c.setFont('DejaVu',size)
    c.drawString(x*mm, y*mm, s)


def line(c,x1,y1,x2,y2):
    c.line(x1*mm,y1*mm,x2*mm,y2*mm)


def base(c,title):
    c.setFillColorRGB(.13,.27,.27)
    c.rect(0,H-22*mm,W,22*mm,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1)
    label(c,13,280,title,15)
    c.setFillColorRGB(0,0,0)
    label(c,13,10,'Zona Zero · prova para playtest · A4 · imprimir a 100%, sem ajustar',7)


def calibration():
    path=OUT/'CALIBRACAO_FRENTE_VERSO_A4.pdf'
    c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=0)
    for side in ('FRENTE','VERSO'):
        base(c,'Calibração — '+side)
        label(c,13,264,'Imprima esta folha duplex: retrato, virada na borda longa.',9)
        label(c,13,257,'Compare as marcas à luz; depois meça a régua com régua física.',9)
        x0,y0=35,233
        c.setLineWidth(.35)
        line(c,x0,y0,x0+100,y0)
        for i in range(0,101,5):
            x=x0+i
            line(c,x,y0,x,y0+(7 if i%10==0 else 3))
            if i%20==0: label(c,x-2,y0+10,str(i),7)
        label(c,140,y0-1,'100 mm',8)
        # targets are asymmetric; reverse their columns on the back for long-edge flip.
        targets=[(25,180,'A',12),(160,180,'B',8),(25,70,'C',8),(160,70,'D',12)]
        for x,y,name,r in targets:
            if side=='VERSO': x=210-x
            c.setStrokeColorRGB(.15,.34,.31) if side=='FRENTE' else c.setStrokeColorRGB(.62,.24,.18)
            c.circle(x*mm,y*mm,r*mm,stroke=1,fill=0)
            line(c,x-4,y,x+4,y);line(c,x,y-4,x,y+4)
            c.setFillColorRGB(0,0,0)
            label(c,x-2,y+r+3,name,9)
        label(c,32,40,'Frente: A/B em cima, C/D embaixo. Verso: colunas refletidas.',8)
        label(c,32,34,'Desvio visível: ajuste a impressora antes das cartas.',8)
        c.showPage()
    c.save()
    return path


def bullet(c,y,s):
    label(c,15,y,'□ '+s,9)
    return y-10


def playtest():
    path=OUT/'ROTEIRO_E_REGISTRO_PLAYTEST.pdf'
    c=canvas.Canvas(str(path),pagesize=(W,H))
    base(c,'Comece aqui — playtest de duas pessoas')
    label(c,14,264,'Imprima o kit completo conforme o índice: 58 folhas duplex OU 72 para colar.',9)
    label(c,14,257,'Este roteiro é extra: imprima esta página e 5 cópias da folha diária.',9)
    y=243
    for s in ['Separem Manual, Campanha, mapa geral, quatro módulos, abrigo e registros.',
              'Separem Lia e Ivo, fichas, peões, pés de cabra, 3d6, lápis e envelopes opacos.',
              'Montem os baralhos e separadores; não olhem as intenções.',
              'Sorteiem dois vínculos distintos e registrem pessoas, cães e barracas.',
              'Contem C consumidores; separem cartas cheias para pelo menos 2C porções de cada.',
              'Separem 3 Materiais, 1 Lona, 2 Medicamentos, 2 Munições, Lanterna e Ferramentas.',
              'Preparem os lotes dos destinos e coloquem 1 Errante na zona S.',
              'Leiam a preparação e o Dia 1; usem o Mercado, rota curta, se quiserem aprender.',
              'Depois de cada fase, anotem tempo, dúvida e recursos na folha diária.']:
        y=bullet(c,y,s)
    label(c,14,137,'Sem alterar peças: fotografem a folha inteira, a área problemática e o registro do dia.',9)
    label(c,14,130,'Anotem dia, fase, zona, ID da carta e o que vocês esperavam que acontecesse.',9)
    label(c,14,115,'Materiais externos: papel opaco/sleeves para intenções, tesoura e fita, se necessário.',9)
    label(c,14,98,'Se uma regra travar a partida, marquem a dúvida e usem a interpretação provisória',9)
    label(c,14,91,'mais literal; não reescrevam cartas nem mudem custos no componente.',9)
    c.showPage()
    base(c,'Registro diário — copiar 5 vezes')
    label(c,14,263,'Grupo: __________   Dia: ____   Destino/rota: __________________   Data: ________',9)
    y=247
    for phase in ['Amanhecer e evento','Viagem / exploração','Combate / resgate','Retorno e cerco','Trabalho / construção','Refeição / intenções']:
        label(c,14,y,phase,9);label(c,96,y,'Tempo: ______ min',9);label(c,145,y,'Dúvida? _____',9)
        line(c,14,y-3,194,y-3);y-=18
    for prompt in ['C/consumidores: ____   Comida: ____   Água: ____   Materiais: ____',
                   'Saúde: ____   Moral: ____   Pressão: ____   Filtro/etapa: __________',
                   'Heróis: ferimentos / fadiga / XP: __________________________________',
                   'Cartas ou peças esgotadas, e solução do manual: ______________________',
                   'Decisão difícil, momento divertido ou surpresa: ______________________',
                   'Frustração, regra esquecida ou informação difícil de achar: _____________']:
        label(c,14,y,prompt,8.5);line(c,14,y-5,194,y-5);y-=18
    label(c,14,20,'Foto: registre código do mapa/posição, ID da carta, dia e fase. Não marque a arte.',8)
    c.showPage()
    base(c,'Adaptação para 3–6 pessoas')
    label(c,14,264,'Substituições e acréscimos em relação ao kit de duas pessoas:',10)
    y=247
    for s in ['Troque FICHAS_LIA_IVO (1) + FICHAS_RESGATAVEIS (6) por FICHAS_24_HEROIS (12).',
              'Acrescente HEROIS_24_RECORTAR (2) para os fundadores adicionais.',
              'Acrescente 1 folha de seis pés de cabra e 1 reposição H3_H4 ou H5_H6.',
              'No método recortar/colar, esses dois conjuntos de cartas exigem 4 folhas.',
              'Total do kit: 67 duplex OU 83 recortar/colar; extras de playtest à parte.',
              'H5: cinco barracas (T08). H6: seis barracas (T08 e T09).',
              'Cada jogador registra o herói por nome/ID; L/I são só exemplos.']:
        y=bullet(c,y,s)
    label(c,14,158,'Os mesmos cinco registros diários servem a qualquer grupo.',9)
    label(c,14,146,'Solo: uma pessoa controla Lia e Ivo; usa a seleção de duas pessoas.',9)
    label(c,14,123,'Pós-partida — discussão do grupo:',10)
    y=113
    for s in ['Qual fase levou mais tempo? Qual instrução foi esquecida?',
              'Que decisão pareceu interessante? Que escolha pareceu sem saída?',
              'Em que momento recursos ou peões acabaram? O manual resolveu?',
              'Conseguiram terminar? Se não, onde e por quê?']:
        y-=13;label(c,17,y,s,8.5)
    c.showPage();c.save()
    return path


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    print(calibration())
    print(playtest())
