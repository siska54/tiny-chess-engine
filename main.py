import os,json,urllib.request as R
def api(p,d={}):
 u=os.environ['MAKEFUN_ENV_URL']+p
 return json.loads(R.urlopen(R.Request(u,json.dumps(d).encode(),{'Content-Type':'application/json'})).read())
def fen2b(fen):
 s=fen.split();bd=[' ']*120;r=2;c=1
 for ch in s[0]:
  if ch=='/':r+=1;c=1
  elif ch.isdigit():
   for _ in range(int(ch)):bd[r*10+c]='.';c+=1
  else:bd[r*10+c]=ch;c+=1
 ep=-1
 if s[3]!='-':ep=(10-int(s[3][1]))*10+ord(s[3][0])-96
 return bd,s[1],ep
V={'P':100,'N':300,'B':310,'R':500,'Q':900,'K':0}
def ev(bd,t):
 s=sum((1 if p.isupper()else-1)*V.get(p.upper(),0)for i in range(20,100)if(p:=bd[i])not in(' ','.'))
 return s if t=='w'else-s
def gm(bd,t,ep):
 res=[];me=str.isupper if t=='w'else str.islower;opp=str.islower if t=='w'else str.isupper
 pd=-10 if t=='w'else 10;pr=set(range(21,29)if t=='w'else range(91,99));ps=set(range(81,89)if t=='w'else range(31,39))
 for i in range(20,100):
  p=bd[i]
  if p in(' ','.'): continue
  if not me(p): continue
  P=p.upper()
  if P=='P':
   f=i+pd
   if bd[f]=='.':
    for q in(('Q','R','B','N')if f in pr else['']):res.append((i,f,q))
    if f not in pr and i in ps and bd[i+2*pd]=='.':res.append((i,i+2*pd,''))
   for dc in(-1,1):
    f=i+pd+dc
    if bd[f]==' ':continue
    if opp(bd[f])or f==ep:
     for q in(('Q','R','B','N')if f in pr else['']):res.append((i,f,q or('ep'if f==ep else'')))
  elif P=='N':
   for d in(-21,-19,-12,-8,8,12,19,21):
    f=i+d
    if bd[f]!=' 'and not me(bd[f]):res.append((i,f,''))
  elif P=='K':
   for d in(-11,-10,-9,-1,1,9,10,11):
    f=i+d
    if bd[f]!=' 'and not me(bd[f]):res.append((i,f,''))
  else:
   for d in{'B':(-11,-9,9,11),'R':(-10,-1,1,10),'Q':(-11,-10,-9,-1,1,9,10,11)}[P]:
    f=i+d
    while bd[f]!=' ':
     if me(bd[f]):break
     res.append((i,f,''))
     if opp(bd[f]):break
     f+=d
 return res
def mk(bd,mv):
 bd=bd[:];f,t,fl=mv;p=bd[f];bd[f]='.'
 if fl and fl not in('','ep'):bd[t]=fl.upper()if p.isupper()else fl.lower()
 else:bd[t]=p
 if fl=='ep':bd[t+(10 if p.isupper()else-10)]='.'
 return bd
def atk(bd,sq,by):
 me=str.isupper if by=='w'else str.islower;pd=-10 if by=='w'else 10
 for i in range(20,100):
  p=bd[i]
  if not me(p):continue
  P=p.upper()
  if P=='P'and sq in(i+pd-1,i+pd+1):return True
  if P=='N'and sq-i in{-21,-19,-12,-8,8,12,19,21}:return True
  if P=='K'and sq-i in{-11,-10,-9,-1,1,9,10,11}:return True
  for sl,ds in[('BQ',(-11,-9,9,11)),('RQ',(-10,-1,1,10))]:
   if P not in sl:continue
   for d in ds:
    f=i+d
    while bd[f]!=' ':
     if f==sq:return True
     if bd[f]!='.':break
     f+=d
 return False
def ic(bd,t):
 k='K'if t=='w'else'k';ki=next((i for i in range(20,100)if bd[i]==k),-1)
 return ki<0 or atk(bd,ki,'b'if t=='w'else'w')
def ab(bd,d,a,b,t,ep):
 if d==0:return ev(bd,t),None
 bm=None;legal=False
 for mv in sorted(gm(bd,t,ep),key=lambda m:V.get(bd[m[1]].upper(),0),reverse=True):
  nb=mk(bd,mv)
  if ic(nb,t):continue
  legal=True
  nep=(mv[0]+mv[1])//2 if bd[mv[0]].upper()=='P'and abs(mv[1]-mv[0])==20 else-1
  s,_=ab(nb,d-1,-b,-a,'b'if t=='w'else'w',nep)
  s=-s
  if s>a:a=s;bm=mv
  if a>=b:break
 if not legal:return(-9999,None)if ic(bd,t)else(0,None)
 return a,bm
def sq2a(sq):return chr(96+sq%10)+str(10-sq//10)
ep=-1
while True:
 try:
  g=api('/game')
  if g.get('over')or g.get('status','')in('over','done','finished'):break
  if not(fen:=g.get('fen')):break
  bd,t,ep=fen2b(fen)
  _,mv=ab(bd,3,-9999,9999,t,ep)
  if mv is None:api('/resign');break
  api('/move',{'move':sq2a(mv[0])+sq2a(mv[1])+(mv[2].lower()if mv[2]not in('','ep')else'')})
 except:break
