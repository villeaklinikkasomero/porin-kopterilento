import sys, json, math; sys.path.insert(0,'/home/claude')
import kivi, numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
ZZ={}; name=sys.argv[1]
kivi.bake_zone = lambda Z, out, samples=8: ZZ.setdefault('Z', Z)
Zs=json.load(open('/home/claude/pori/city_zones.json'))['zones']
if name in kivi.ZONESK: kivi.build_and_bake(name, kivi.ZONESK[name], 4)
else: kivi.build_and_bake(name, Zs[name]['ids'], 4, spec=kivi.spec_for)
Z=ZZ['Z']; A=np.asarray(Image.open(f'/home/claude/out/{name}_bake.png').convert('RGB')).astype(float); S=A.shape[0]
s=open('/home/claude/pori/city.js').read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); B=C['b']
allp=[Polygon([(b['p'][k]/10,b['p'][k+1]/10) for k in range(0,len(b['p']),2)]).buffer(0) for b in B]; T=STRtree(allp)
from collections import Counter
vis=[]
for f in Z.lo:
    pts,r=f[0],f[1]; x,y,w,h=Z.px[r]; m=A[S-(y+h):S-y, x:x+w].mean()
    P=np.array(pts); c=P.mean(0)+np.array([Z.cx,Z.cy,0]); n=np.cross(P[1]-P[0],P[2]-P[0])
    if abs(n[2])>0.5*np.linalg.norm(n) or m>=25: continue
    n=n/np.linalg.norm(n); q=Point(c[0]+n[0]*1.5,c[1]+n[1]*1.5)
    if any(allp[j].contains(q) for j in T.query(q)): continue
    bid=min(Z.ids,key=lambda i: allp[i].distance(Point(c[0],c[1])))
    vis.append((bid,round(c[0]),round(c[1]),round(c[2],1),round(math.degrees(math.atan2(n[0],n[1])))))
print('VISIBLE BLACK', len(vis), Counter(v[0] for v in vis)); print(vis[:12])
