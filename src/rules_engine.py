"""Oráculo limitado de verificação lógica; não joga expedições nem mede diversão."""
from math import ceil
def family_setup(h,links):
 humans=h+sum(x[0] for x in links);dogs=sum(x[1] for x in links);c=humans+dogs
 return dict(humans=humans,dogs=dogs,consumers=c,capacity=2*max(4,h),food=4*ceil(2*c/4))
def consume(conserved,meat,consumers):
 eaten=min(meat,consumers);remaining=consumers-eaten;used=min(conserved,remaining)
 return conserved-used,remaining-used,meat-eaten
# tuple: conserved remaining, unmet food, expired meat
def intake(occupied,capacity,new,arrival,night):
 if occupied+new<=capacity:return 'permanente'
 if occupied+new>capacity+2:return 'sem_capacidade'
 return 'temporario' if night<arrival+2 else 'superlotacao'
def intent(kind,verified,food,pressure):
 if kind=='Oportunista':return max(0,food-(0 if verified else 4)),pressure,'parte'
 if kind=='Infiltrado':return food,min(3,pressure+(0 if verified else 1)),'parte'
 return food,pressure,'fica'
def reserve_project(stock,cost):
 if any(stock.get(k,0)<v for k,v in cost.items()):raise ValueError('Estoque insuficiente')
 left=stock.copy()
 for k,v in cost.items():left[k]-=v
 return left,cost.copy()
def advance(clock,segments):
 end=clock+segments;night=sum(8<s<=10 for s in range(clock+1,end+1))
 return end,night,end>10
def pending_pressure(current,added,queue):
 new=min(3,current+added);q=list(queue)
 if current<3 and new==3:q.append('pressao')
 return new,q
def apply_deprivation(streak,fed,watered):
 n=0 if fed and watered else streak+1
 return n,int(n>=2)
