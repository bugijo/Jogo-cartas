"""Dimensões físicas; não contém regras novas ou conteúdo de jogo."""
MAX_ENEMIES=24
BASE_WIDTH,BASE_DEPTH=22,12

def card_cell(index,side='front'):
 row,col=divmod(index%9,3)
 return row,2-col if side=='duplex_back' else col

def card_rect(index,side='front'):
 row,col=card_cell(index,side)
 return 8.5+65*col,14.5+90*row,63,88

def sheet_totals(method):
 if method=='duplex':return 25,33,58
 if method=='manual':return 33,39,72
 raise ValueError(method)

def panel_slots():return [(277+3.5+68*i,76,66,92) for i in range(4)]
def pawn_capacity(w,h):return int(w//BASE_WIDTH)*int(h//BASE_DEPTH)
def enemy_variants():return [dict(id=f'E{i:02}',type=t) for t in ['Errante','Corredor','Bruto'] for i in range(1,25)]
