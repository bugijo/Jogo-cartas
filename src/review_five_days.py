"""Replay determinístico de três expedições e duas noites de obra.
Dados e montes escolhidos legalmente; não é simulação de probabilidade nem playtest.
"""
from pathlib import Path
import json
from collections import deque,Counter
P=Path(__file__).resolve().parents[1]
D=json.loads((P/'content/catalog.json').read_text())
class Replay:
 def __init__(self):
  self.logs=[];self.horda=['Arrastar','Arrastar','Arrastar','Aglomerado','Arrastar','Aglomerado','Corrida','Corrida','Peso morto'];self.draws=[];self.health={'Lia':3,'Ivo':3};self.serial=0
 def start(self,name):
  self.m=next(x for x in D['maps'] if x['name']==name);self.pos={'Lia':1,'Ivo':1};self.bags={h:[('Pé de cabra',1)] for h in self.pos};self.floor={};self.pa={};self.round=0;self.clock=1;self.open=set();self.doorhits={};self.enemies=[];self.parts=set();self.goods=[]
  self.graph={z:[] for z in self.m['zones']}
  for a,b in self.m['edges']:self.graph[a].append(b);self.graph[b].append(a)
  self.doors={tuple(e) for e in self.m['doors']};self.blocked={tuple(e) for e in self.m['blocked']}
  self.spawn('Errante',16)
  if name=='Estação':self.spawn('Bruto',14)
 def spawn(self,kind,z):self.serial+=1;self.enemies.append(dict(id=self.serial,kind=kind,z=z,hp=3 if kind=='Bruto' else 1))
 def begin(self):self.round+=1;self.clock+=1;self.pa={h:3 for h in self.pos}
 def cost(self,h,n):
  assert self.health[h]>0,(h,'incapacitado')
  assert self.pa[h]>=n,(self.m['name'],self.round,h,'PA',self.pa[h],n)
  self.pa[h]-=n
 def load(self,h):return sum(v for _,v in self.bags[h])
 def gain(self,h,items):
  for item in items:
   if self.load(h)+item[1]<=4:self.bags[h].append(item)
   else:self.floor.setdefault(self.pos[h],[]).append(item)
 def act(self,h,a):
  op,*args=a
  if op=='move':
   z=args[0];assert z in self.graph[self.pos[h]]
   edge=tuple(sorted((self.pos[h],z)));assert edge not in self.doors or edge in self.open,(h,'porta',edge)
   self.cost(h,1+int(any(e['z']==self.pos[h] for e in self.enemies)));self.pos[h]=z
  elif op=='open':
   edge=tuple(sorted(args));assert self.pos[h] in edge and edge in self.doors and edge not in self.open
   self.cost(h,2 if edge in self.blocked else 1);self.open.add(edge)
  elif op=='take':
   item,z,n,load=args;assert self.pos[h]==z
   self.cost(h,1);self.gain(h,[(item,load)]*n)
  elif op=='floor':
   self.cost(h,1);item=self.floor[self.pos[h]].pop(0);assert self.load(h)+item[1]<=4;self.bags[h].append(item)
  elif op=='attack':
   target=next((e for e in self.enemies if e['z']==self.pos[h]),None);assert target,(self.m['name'],self.round,h,self.pos,self.enemies);self.cost(h,1)
   total=3+(2 if h=='Lia' else 3);assert total>=(6 if target['kind']=='Bruto' else 5)
   target['hp']-=1
   if not target['hp']:self.enemies.remove(target)
  elif op=='pump':
   assert self.pos[h]==7;self.cost(h,2);assert 3+D['heroes'][0]['attributes']['Técnica']>=6;self.gain(h,[('Bomba',2)])
  else:raise AssertionError(op)
  assert self.load(h)<=4
 def distance(self,start,target):
  q=deque([(start,0)]);seen={start}
  while q:
   z,d=q.popleft()
   if z==target:return d
   for n in self.graph[z]:
    if n not in seen:seen.add(n);q.append((n,d+1))
  return 999
 def ai(self):
  for e in list(self.enemies):
   targets=[h for h,z in self.pos.items() if z==e['z']]
   if targets:
    h='Ivo' if 'Ivo' in targets else targets[0];self.health[h]-=2 if e['kind']=='Bruto' else 1;assert self.health[h]>0,(self.m['name'],self.round,h,'incapacitado');continue
   target=min(self.pos.values(),key=lambda z:(self.distance(e['z'],z),z))
   for _ in range(2 if e['kind']=='Corredor' else 1):
    if e['z']==target:break
    z=min(self.graph[e['z']],key=lambda n:(self.distance(n,target),n));edge=tuple(sorted((e['z'],z)))
    if edge in self.doors and edge not in self.open:
     self.doorhits[edge]=self.doorhits.get(edge,0)+1
     if self.doorhits[edge]>=(2 if edge in self.blocked else 1):self.open.add(edge)
     break
    e['z']=z
 def end(self):
  tutorial=self.m['name']=='Mercado' and self.round==1
  if not tutorial:self.ai()
  if self.round%2==0:
   name=self.horda.pop(0);self.draws.append(name);self.spawn('Corredor' if name=='Corrida' else 'Bruto' if name=='Peso morto' else 'Errante',16)
  self.logs.append(dict(destination=self.m['name'],round=self.round,clock=self.clock,positions=self.pos.copy(),pa_remaining=self.pa.copy(),health=self.health.copy(),loads={h:self.load(h) for h in self.pos},enemies=[e.copy() for e in self.enemies]))
 def play(self,name,rounds):
  self.start(name)
  for instructions in rounds:
   self.begin()
   for h,actions in instructions:
    for a in actions:self.act(h,a)
   self.end()
  assert all(z==1 for z in self.pos.values());assert all(e['z']!=1 for e in self.enemies)
  self.clock+=1;assert self.clock<=10
  delivery=Counter(item for bag in self.bags.values() for item,_ in bag if item!='Pé de cabra')
  return dict(destination=name,segments=self.clock,rounds=self.round,delivery=dict(delivery),health=self.health.copy())
def run():
 r=Replay()
 m=r.play('Mercado',[
 [('Lia',[('move',2),('move',3),('open',3,7)]),('Ivo',[('open',1,5),('move',5),('move',9)])],
 [('Lia',[('move',7),('take','Conserva',7,2,1),('take','Conserva',7,2,1)]),('Ivo',[('open',9,13),('move',13),('open',13,14)])],
 [('Lia',[('move',11),('move',12),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)])],
 [('Lia',[('attack',),('move',11),('move',7)]),('Ivo',[('move',11),('move',7),('floor',)])],
 [('Lia',[('move',3),('move',2),('move',1)]),('Ivo',[('move',3),('move',2),('move',1)])]])
 o=r.play('Oficina',[
 [('Lia',[('move',2),('move',3)]),('Ivo',[('open',1,5),('move',5),('move',9)])],
 [('Lia',[('open',3,7),('move',7)]),('Ivo',[('open',9,13),('move',13),('open',13,14)])],
 [('Lia',[('open',7,8),('move',8),('attack',)]),('Ivo',[('move',14),('take','Água',14,2,1),('move',15)])],
 [('Lia',[('move',7),('take','Conexões',7,1,1),('take','Bateria',7,1,1)]),('Ivo',[('attack',),('move',11),('move',7)])],
 [('Lia',[('take','Conserva',7,2,1),('move',3),('move',2)]),('Ivo',[('floor',),('move',3),('move',2)])],
 [('Lia',[('move',1)]),('Ivo',[('move',1)])]])
 s=r.play('Estação',[
 [('Lia',[('move',2),('move',3),('open',3,7)]),('Ivo',[('open',1,5),('move',5),('move',9)])],
 [('Lia',[('move',7),('pump',)]),('Ivo',[('move',10),('move',11),('move',15)])],
 [('Ivo',[('attack',),('attack',),('attack',)]),('Lia',[('move',11),('move',15),('move',14)])],
 [('Ivo',[('attack',),('move',14),('take','Membrana',14,1,1)]),('Lia',[('move',15),('move',11)])],
 [('Lia',[('move',7),('move',3),('move',2)]),('Ivo',[('take','Água',14,2,1),('move',15),('move',11)])],
 [('Lia',[('move',1)]),('Ivo',[('attack',),('move',7),('attack',)])],
 [('Ivo',[('move',3),('move',2),('move',1)])]])
 assert m['delivery']=={'Conserva':4,'Água':2};assert o['delivery']=={'Conexões':1,'Bateria':1,'Conserva':2,'Água':2};assert s['delivery']=={'Bomba':1,'Membrana':1,'Água':2}
 counts=Counter(r.draws);assert counts=={'Arrastar':4,'Aglomerado':2,'Corrida':2}
 # C=5: dois parceiros adultos e um cão; vínculos Parceiro e Parceiro+cão.
 food=water=12;materials=3;ammo=2;work=0;days=[];pressure=0
 for day in range(1,6):
  if day==1:food+=16;water+=8
  if day==2:food+=8;water+=8;pressure+=1
  if day==3:water+=8;materials+=1;ammo-=1 # Defesa portão 2+cão1+munição1 = força4
  if day==4:pressure+=1;materials-=2;work+=2
  if day==5:pressure+=1;materials-=1;work+=2;water+=10;ammo-=1 # Cerco pressão Força4
  food-=5;water-=5;assert food>=0 and water>=0 and materials>=0
  days.append(dict(day=day,food=food,water=water,materials=materials,filter_work=work,fatigue=1 if day==3 else 0,pressure=1 if day==5 else pressure,ammo=ammo))
 assert work==4 and materials==1 and days[-1]['food']==11
 return dict(status='PASS',scope='Uma trajetória legal C=5, sem resgates, rolagens 3 e ordem válida de Horda; não mede chance de vitória.',travel=['Rua vazia','Desvio sinalizado','Caminho limpo','Ponte avistada','Vizinho na janela (sem ajuda)','Ferragens (retorno: +1 Material, fora dos custos do filtro)','Sinal de passagem (extra do segmento 9, sem efeito retroativo)'],expeditions=[m,o,s],days=days,horde_draws=r.draws,round_log=r.logs)
if __name__=='__main__':
 out=run();target=P/'output/revisao-0.2';target.mkdir(exist_ok=True,parents=True);(target/'replay_cinco_dias.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({k:out[k] for k in ['status','expeditions','days']},ensure_ascii=False,indent=2))
