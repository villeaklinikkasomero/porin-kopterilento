"""Tavarajunien reitit Porin ratapihan läpi (21.11.2026): rata/rata_data.js + tools/rata/osm_rail.json -> rata/tavara_reitit.js
Ajo: python3 tools/rata/tavara_reitit.py
- Jokainen pelin raiteen piste saa OSM:n raidenumeron (railway:track_ref, < 3 m). Numerot ovat samat kuin Digitrafficin raideosuuksissa
  (PRI_838, PRI_803 ...), joten juna/tavara_aikataulu.js:n raiteet löytyvät suoraan. Raide 1 = OSM 801, raide 2 = 802.
- Reitit Dijkstralla vaihteiden kautta, ei yli 25 asteen kääntöjä (kuten build_data.py).
"""
import json, os, numpy as np, math, heapq
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,'..','..')
src=open(os.path.join(ROOT,'rata','rata_data.js'),encoding='utf-8').read()
d=json.loads(src[src.index('export default')+len('export default'):].strip().rstrip(';'))
O=json.load(open(os.path.join(HERE,'osm_rail.json'),encoding='utf-8'))
T=[np.array(t['p']).reshape(-1,3) for t in d['t']]
# OSM-raidenumero jokaiselle pisteelle (lähin OSM-väylä, jolla tr, < 3 m)
segs=[]
for t,g in O['W']:
    if t.get('tr') and t.get('r')=='rail':
        P=np.array(g).reshape(-1,2)
        for a,b in zip(P[:-1],P[1:]): segs.append((a,b,t['tr']))
A=np.array([s[0] for s in segs]); B=np.array([s[1] for s in segs]); R=[s[2] for s in segs]
def ref(p):
    ab=B-A; t=np.clip(((p-A)*ab).sum(1)/np.maximum((ab*ab).sum(1),1e-9),0,1); q=A+ab*t[:,None]; dd=np.linalg.norm(q-p,axis=1); i=int(np.argmin(dd))
    return R[i] if dd[i]<3.0 else None
LAB=[[ref(p[:2]) for p in P] for P in T]

# ---------------- graafi
N=sum(len(P) for P in T); off=np.cumsum([0]+[len(P) for P in T]); 
def nid(ti,j): return int(off[ti]+j)
XY=np.concatenate([P[:,:2] for P in T]); Z=np.concatenate([P[:,2] for P in T])
ADJ=[[] for _ in range(N)]
for ti,P in enumerate(T):
    for j in range(len(P)-1):
        a,b=nid(ti,j),nid(ti,j+1); w=float(np.linalg.norm(P[j+1,:2]-P[j,:2])); ADJ[a].append((b,w)); ADJ[b].append((a,w))
links=0
for to in d['to']:
    dt=to['d']; e=0 if to['e']==0 else len(T[dt])-1; th=to['th']
    p=T[dt][e,:2]; dd=np.linalg.norm(T[th][:,:2]-p,axis=1); j=int(np.argmin(dd))
    a,b=nid(dt,e),nid(th,j); ADJ[a].append((b,float(dd[j]))); ADJ[b].append((a,float(dd[j]))); links+=1
ends=[(ti,0) for ti in range(len(T))]+[(ti,len(T[ti])-1) for ti in range(len(T))]
for i,(ta,ja) in enumerate(ends):
    for tb,jb in ends[i+1:]:
        if ta!=tb and np.linalg.norm(T[ta][ja,:2]-T[tb][jb,:2])<0.5:
            a,b=nid(ta,ja),nid(tb,jb); ADJ[a].append((b,0.01)); ADJ[b].append((a,0.01)); links+=1
# lyhyet liitokset (vaihde, raiteen päät): korvataan reunoilla naapuripisteistä, jotta kulmatarkistus näkee oikean suunnan
tr_of=lambda n:int(np.searchsorted(off,n,side='right')-1)
def tnb(n):
    ti=tr_of(n); j=n-off[ti]; return [nid(ti,k) for k in (j-1,j+1) if 0<=k<len(T[ti])]
short=[(a,b) for a in range(N) for b,w in ADJ[a] if tr_of(a)!=tr_of(b) and a<b]
for a,b in short:
    ADJ[a]=[(m,w) for m,w in ADJ[a] if m!=b]; ADJ[b]=[(m,w) for m,w in ADJ[b] if m!=a]
    for u in tnb(a):
        w=float(np.linalg.norm(XY[u]-XY[b])); ADJ[u].append((b,w)); ADJ[b].append((u,w))
    for v in tnb(b):
        w=float(np.linalg.norm(XY[v]-XY[a])); ADJ[v].append((a,w)); ADJ[a].append((v,w))

def route(a,b,maxdeg=25,pr0=-1):
    dist={(a,pr0):0}; prev={}; pq=[(0,a,pr0)]
    while pq:
        dd,n,pr=heapq.heappop(pq)
        if n==b:
            path=[n]; s=(n,pr)
            while s in prev: s=prev[s]; path.append(s[0])
            return path[::-1]
        if dist.get((n,pr),1e18)<dd: continue
        for m,w in ADJ[n]:
            if m==pr: continue
            if pr>=0:
                v1=XY[n]-XY[pr]; v2=XY[m]-XY[n]
                if np.linalg.norm(v1)>0.05 and np.linalg.norm(v2)>0.05 and np.dot(v1,v2)/np.linalg.norm(v1)/np.linalg.norm(v2)<math.cos(math.radians(maxdeg)): continue
            nd=dd+w; s=(m,n)
            if nd<dist.get(s,1e18): dist[s]=nd; prev[s]=(n,pr); heapq.heappush(pq,(nd,m,n))
    return None

# kaakko (Tampere/Harjavalta) = päärata kartan eteläreunalla, luode (Mäntyluoto) = haararata kartan länsireunalla
def edge_end(kind, test):
    for ti,t in enumerate(d['t']):
        if t['k']!=kind: continue
        for j in (0,len(T[ti])-1):
            if test(T[ti][j]): return nid(ti,j)
SE=edge_end('m', lambda p: p[1]<-3501.6+1); NW=edge_end('b', lambda p: p[0]<-2504.1+1)
LABN=[l for L in LAB for l in L]
def mid(r):
    for ti,L in enumerate(LAB):
        idx=[j for j,l in enumerate(L) if l==r]
        if idx and d['t'][ti]['k']!='x': return nid(ti,idx[len(idx)//2])
def chain(pts):
    path=[pts[0]]; pr=-1
    for a,b in zip(pts[:-1],pts[1:]):
        p=route(a,b,pr0=pr)
        if p is None: return None
        path+=p[1:]; pr=path[-2]
    return path
def summ(path):
    seq=[]
    for n in path:
        l=LABN[n]
        if l and (not seq or seq[-1]!=l): seq.append(l)
    return seq
def far(r, frm, margin=10):
    # raiteen r piste, joka on kauimpana pisteestä frm (pääteraiteella juna ajaa raiteen perälle asti), 20 m ennen raiteen päätä
    for ti,L in enumerate(LAB):
        idx=[j for j,l in enumerate(L) if l==r]
        if idx and d['t'][ti]['k']!='x':
            a,b=idx[0],idx[-1]
            if np.linalg.norm(T[ti][a,:2]-XY[frm])>np.linalg.norm(T[ti][b,:2]-XY[frm]): return nid(ti,a+margin)
            return nid(ti,b-margin)
RT={'SE-2-NW':[SE,mid('802'),NW],'NW-803-SE':[NW,mid('803'),SE],'SE-804':[SE,far('804',SE)],'804-SE':[far('804',SE),SE],'804-NW':[far('804',NW),NW],'NW-804':[NW,far('804',NW)],
    'SE-808':[SE,far('808',SE)],'808-SE':[far('808',SE),SE],'808-NW':[far('808',NW),NW],'SE-810':[SE,far('810',SE)],'810-SE':[far('810',SE),SE]}
OUT={}
for k,w in RT.items():
    p=chain(w)
    if p is None: print(k,'EI REITTIÄ'); continue
    L=float(sum(np.linalg.norm(XY[a]-XY[b]) for a,b in zip(p[:-1],p[1:])))
    print(k,round(L),'m',' > '.join(summ(p))); OUT[k]=p


# ulos: reitti = kiskon yläpinta 2 m välein (x, y, z) + yhteenveto; raide = kaupallisen raiteen osuus reitillä (m reitin alusta)
res={}
for k,p in OUT.items():
    P=XY[p]; Zr=Z[p]+d['rail']
    keep=np.concatenate([[True],np.linalg.norm(np.diff(P,axis=0),axis=1)>0.05]); P=P[keep]; Zr=Zr[keep]; lab=[LABN[n] for n,kp in zip(p,keep) if kp]
    s=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))])
    want=k.split('-')[1] if k.count('-')==2 else [x for x in k.split('-') if x not in ('SE','NW')][0]
    want={'2':'802'}.get(want,want); ii=[i for i,l in enumerate(lab) if l==want]
    flat=[]
    for (x,y),z in zip(P,Zr): flat+=[round(float(x),2),round(float(y),2),round(float(z),2)]
    res[k]=dict(p=flat,L=round(float(s[-1]),1),raide=want,s=[round(float(s[ii[0]]),1),round(float(s[ii[-1]]),1)],kautta=summ(p))
hdr="""// Tavarajunien reitit Porin ratapihan läpi (tools/rata/tavara_reitit.py, älä muokkaa käsin).
// SE = kaakko (Tampere/Harjavalta, kartan etelareuna), NW = luode (Mäntyluoto, kartan länsireuna). 2 = raide 2 (OSM 802), 8xx = ratapihan raiteet.
// p = kiskon yläpinta (x, y, z) 2 m välein kuten RATA.r; s = raiteen osuus reitillä (m alusta); kautta = OSM:n raidenumerot = Digitrafficin raideosuudet (PRI_8xx).
export default """
open(os.path.join(ROOT,'rata','tavara_reitit.js'),'w',encoding='utf-8').write(hdr+json.dumps(res,separators=(',',':'))+';\n')
