import json, base64, numpy as np
U='/mnt/user-data/uploads/porin-kopterilento/'
s=open(U+'terrain.js').read(); T=json.loads(s[s.index('{'):s.rindex('}')+1])
nx,ny,g,x0,y0=T['nx'],T['ny'],T['g'],T['x0'],T['y0']
hg=np.frombuffer(base64.b64decode(T['hg']),'<i2').reshape(ny,nx).astype(np.float32)/10
hs=np.frombuffer(base64.b64decode(T['hs']),'<i2').reshape(ny,nx).astype(np.float32)/10
K=305; ny2=ny+K; y02=round(y0-K*g,1)
xs=x0+np.arange(nx)*g; ys=y02+np.arange(K)*g
# runway / threshold elevations (AIP EFPO, ft -> m, minus the game's REF 4 m)
P=np.array([[-703.9,-2048.9,44.2],[845.6,-3166.3,36.1],[132.5,-2459.9,37.3],[216.5,-3245.0,32.0]]); P[:,2]=P[:,2]*0.3048-T['ref']
A=np.c_[P[:,0],P[:,1],np.ones(4)]; c,*_=np.linalg.lstsq(A,P[:,2],rcond=None); print('plane',c)
X,Y=np.meshgrid(xs,ys); B=c[0]*X+c[1]*Y+c[2]
edge=hg[0]; es=hs[0]
d=(y0-Y)                      # metres south of the old edge
w=np.exp(-d/220.0)
# smooth the edge profile along x so hills at the edge fade, not stripe
from scipy.ndimage import uniform_filter1d
eg=uniform_filter1d(edge,9); 
H=w*eg[None,:]+(1-w)*B
H[-1]=edge  # last new row joins exactly (row K-1 is 6 m south of the old row 0)
H[-1]=0.5*edge+0.5*H[-2]
hg2=np.vstack([H,hg]); hs2=np.vstack([H,hs])
enc=lambda a: base64.b64encode(np.round(a*10).astype('<i2').tobytes()).decode()
skip=np.unpackbits(np.frombuffer(base64.b64decode(T['skip']),np.uint8))[:nx*ny]
skip2=np.concatenate([np.zeros(K*nx,np.uint8),skip]); 
T2=dict(T); T2.update(y0=y02,ny=ny2,hg=enc(hg2),hs=enc(hs2),skip=base64.b64encode(np.packbits(skip2).tobytes()).decode())
out=s[:s.index('{')]+json.dumps(T2,separators=(',',':'))+s[s.rindex('}')+1:]
open('/mnt/user-data/outputs/terrain.js','w').write(out); print(y02,ny2,len(out), 'edge range',edge.min(),edge.max(),'airport B',B.min(),B.max())
