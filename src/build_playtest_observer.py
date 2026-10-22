"""Two printable A4 pages: objective observation during play and opinions after it."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'kit-final-prova/playtest'
W,H=210*mm,297*mm
pdfmetrics.registerFont(TTFont('Obs','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ObsBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))


def text(c,x,y,s,size=8.5,bold=False):
    c.setFont('ObsBold' if bold else 'Obs',size);c.drawString(x*mm,y*mm,s)


def ln(c,x,y,w):c.line(x*mm,y*mm,(x+w)*mm,y*mm)


def header(c,title,page):
    c.setFillColorRGB(.12,.27,.27);c.rect(0,H-21*mm,W,21*mm,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1);text(c,13,281,title,14,True)
    c.setFillColorRGB(.08,.15,.16)
    text(c,13,9,f'Zona Zero · observação de mesa · {page}/2 · A4 100%, sem ajustar',7)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/'OBSERVADOR_E_DEVOLUTIVA.pdf'
    c=canvas.Canvas(str(p),pagesize=(W,H))
    header(c,'Observador — fatos durante a partida',1)
    text(c,13,266,'Sessão: ______   Data: __________   Observador: ______________   Jogadores: __________',9)
    text(c,13,257,'Início: ______   Fim: ______   Pausas: ______ min   Duração ativa: ______ min',9)
    text(c,13,243,'Anote minutos reais por fase; escreva 0 se a fase não ocorreu.',9)
    cols=[13,27,53,91,126,156,194]
    heads=['Dia','Preparo','Viagem/mapa','Noite','Pausas','Total']
    for x,h in zip(cols,heads):text(c,x+1,232,h,8,True)
    for y in [228,217,206,195,184,173]:ln(c,13,y,181)
    for x in cols[1:]:c.line(x*mm,173*mm,x*mm,238*mm)
    for i,y in enumerate([220,209,198,187,176],1):text(c,16,y,str(i),9)
    text(c,13,161,'FATOS OBSERVADOS — descreva o que aconteceu, sem avaliar o jogador.',9,True)
    text(c,13,153,'Use o registro diário para detalhes; aqui guarde os três pontos mais importantes.',8)
    for top in [145,119,93]:
        text(c,13,top,'Dia/fase/hora: __________   Zona/ID/página: __________________________',8.5)
        text(c,13,top-9,'O que houve: ______________________________________________________',8.5)
        text(c,13,top-18,'Regra consultada? ___   Espera/min: ___   Decisão tomada: __________',8)
    text(c,13,57,'Marque o que deve ser detalhado no relatório:',8.5,True)
    text(c,13,48,'□ regra/dúvida   □ decisão discutida   □ símbolo/texto   □ recurso/estoque',8.5)
    text(c,13,39,'□ espera/confusão   □ carta/componente   □ corte/verso/montagem',8.5)
    text(c,13,25,'Não corrija a regra durante a partida. Anote a interpretação provisória usada.',8)
    c.showPage()
    header(c,'Depois da partida — opiniões separadas',2)
    text(c,13,265,'Resultado: vitória □  derrota parcial □  retirada □  interrompida □',9)
    text(c,13,256,'Parou em: dia ____ fase __________ motivo ___________________________',9)
    text(c,13,246,'Pergunte a cada pessoa separadamente. Resposta é opinião, não falha comprovada.',8.5)
    for label,base in [('Jogador 1',233),('Jogador 2',174)]:
        text(c,13,base,label,10,True)
        text(c,13,base-10,'Momento mais interessante: __________________________________________',8.5)
        text(c,13,base-20,'Momento frustrante ou lento: _________________________________________',8.5)
        text(c,13,base-30,'Decisão que pareceu importante: ______________________________________',8.5)
        text(c,13,base-40,'Regra/carta/símbolo difícil; o que entendeu: ___________________________',8.5)
        text(c,13,base-49,'Recurso fácil/difícil de acompanhar: _________________________________',8.5)
    text(c,13,113,'PARA DEVOLVER AO PROJETO',9,True)
    text(c,13,103,'Escolha uma categoria por relato; pode mudar depois da revisão:',8.5)
    text(c,13,93,'□ Falha de regra: duas instruções incompatíveis ou ação sem resolução.',8)
    text(c,13,84,'□ Clareza: regra existe, mas foi localizada ou entendida com dificuldade.',8)
    text(c,13,75,'□ Ritmo: espera, repetição ou duração observada; informe minutos.',8)
    text(c,13,66,'□ Preferência: gosto pessoal sem erro de funcionamento demonstrado.',8)
    text(c,13,51,'Evidência: dia ____ fase ____ ID/página ____ foto ____',8.5)
    text(c,13,39,'Interpretação provisória, se houve: __________________________________',8.5)
    text(c,13,27,'Mudança sugerida? Registre como hipótese; não altere o componente.',8.2)
    c.showPage();c.save()
    print(p)


if __name__=='__main__':main()
