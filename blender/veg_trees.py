"""Trees from the aerial photo -> trees_extra.js.
Crown cover is found in outer.jpg (green, darker than lawns and rough: leaf clumps and their own shadows); buildings, roads, railways and the
river are masked out; OpenStreetMap woods / forest / scrub lower the threshold.  Trees go on a 7 m jittered grid and skip spots within 4.5 m of an
OSM tree.  Species from the crown colour: dark blue-green = spruce, otherwise birch or linden.  Input osm.json: OSM map extract
(veg polygons, railways) fetched with the OSM API.  python3 veg_trees.py (run from a folder holding osm.json)"""
import json,numpy as np,math,base64
from PIL import Image, ImageDraw
from scipy import ndimage
U='/mnt/user-data/uploads/porin-kopterilento/'
s=open(U+'city.js').read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); B=C['b']
OX0,OX1,OY0,OY1=C['ox0'],C['ox1'],C['oy0'],C['oy1']
im=Image.open(U+'outer.jpg').convert('RGB'); W,H=im.size; A=np.asarray(im).astype(np.float32)/255
sx=W/(OX1-OX0); sy=H/(OY1-OY0)                      # px per metre
def PX(x,y): return ((x-OX0)*sx, (OY1-y)*sy)
r,g,b=A[...,0],A[...,1],A[...,2]; v=A.max(axis=2); mn=A.min(axis=2); sat=(v-mn)/np.maximum(v,1e-3)
exg=2*g-r-b
lum=0.3*r+0.59*g+0.11*b
sd=np.sqrt(np.maximum(0,ndimage.uniform_filter(lum**2,5)-ndimage.uniform_filter(lum,5)**2))
green=(g>r*1.04)&(g>b*1.08)&(exg>0.045)
canopy=green&(lum<0.42)&(sd>0.022)                   # tree crowns: darker than lawns and rough (leaf clumps, own shadows)
canopy=ndimage.binary_opening(canopy,iterations=1); canopy=ndimage.binary_closing(canopy,iterations=2)
# masks: buildings, roads, river
mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
for bb in B:
    p=bb['p']; d.polygon([PX(p[k]/10,p[k+1]/10) for k in range(0,len(p),2)],fill=255)
for rd in C['r']:
    p=rd['p']; d.line([PX(p[k],p[k+1]) for k in range(0,len(p),2)],fill=255,width=max(2,int((9 if rd['k']>=2 else 6)*sx)))
O=json.load(open('osm.json')); XY=lambda q:((q[0]-21.796)*53278,(q[1]-61.486)*111437)
for rl in O['rail']:
    if rl['k']=='rail': d.line([PX(*XY(q)) for q in rl['g']],fill=255,width=int(6*sx))
bad=ndimage.binary_dilation(np.asarray(mask)>0,iterations=2)
s2=open(U+'river.js').read(); RIV=json.loads(s2[s2.index('{'):s2.rindex('}')+1]); M=RIV['mask']; ra=np.unpackbits(np.frombuffer(base64.b64decode(M['b']),dtype=np.uint8))[:M['nx']*M['ny']].reshape(M['ny'],M['nx'])
def inriver(x,y):
    i=int((x-OX0)/M['g']); j=int((y-OY0)/M['g']); return 0<=i<M['nx'] and 0<=j<M['ny'] and ra[j,i]
# OSM woodland polygons lower the threshold
wood=Image.new('L',(W,H),0); dw=ImageDraw.Draw(wood)
for vg in O['veg']:
    if vg['v'] in ('na:wood','lu:forest','na:scrub') and len(vg['g'])>=3: dw.polygon([PX(*XY(q)) for q in vg['g']],fill=255)
wood=np.asarray(wood)>0
frac=ndimage.uniform_filter(canopy.astype(np.float32),int(round(6*sx))|1)
ok=((frac>0.55)|(wood&(frac>0.25)))&~bad
t=C['t']; ex=np.array(t).reshape(-1,2)
from scipy.spatial import cKDTree
kd=cKDTree(ex); rng=np.random.default_rng(7); new=[]; SP=7.0
ys=np.arange(OY0+10,OY1-10,SP*0.87); 
for j,y in enumerate(ys):
    for x in np.arange(OX0+10+(SP/2 if j%2 else 0),OX1-10,SP):
        xx=x+rng.uniform(-2.2,2.2); yy=y+rng.uniform(-2.2,2.2); px,py=PX(xx,yy); px=int(px); py=int(py)
        if not (0<=px<W and 0<=py<H) or not ok[py,px] or inriver(xx,yy): continue
        new.append((round(xx,1),round(yy,1)))
new=np.array(new); dist,_=kd.query(new); new=new[dist>4.5]
print('existing',len(ex),'new',len(new),'canopy share %.1f%%'%(canopy.mean()*100))

# species from the photo colour around each tree: dark blue-green crowns are spruce / pine, the rest deciduous (birch / linden)
cols=[]
for x,y in new:
    px,py=PX(x,y); px=int(px); py=int(py); a=A[max(0,py-2):py+3,max(0,px-2):px+3].reshape(-1,3).mean(axis=0); cols.append(a)
cols=np.array(cols); L=cols.mean(axis=1); gb=cols[:,1]-cols[:,0]; con=(L<0.2)&(cols[:,2]>cols[:,0]*0.95)
kind=np.where(con,2,np.where(rng.random(len(new))<0.62,1,0))     # 2 spruce, 1 birch, 0 linden
print('conifer %.0f%%'%(con.mean()*100), 'birch', (kind==1).sum(), 'linden', (kind==0).sum())
P=np.round(new*10).astype('<i2'); K=kind.astype(np.uint8)
js='// trees found in the aerial photo (crown cover with no tree in OpenStreetMap), see osm/veg.py: x*10, y*10 as int16, species 0 linden 1 birch 2 spruce\nexport default { p: "%s", k: "%s" };\n'%(base64.b64encode(P.tobytes()).decode(), base64.b64encode(K.tobytes()).decode())
open('/home/claude/pori/trees_extra.js','w').write(js); print('trees_extra.js', len(js))
