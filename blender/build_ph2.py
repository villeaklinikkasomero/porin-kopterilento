import cv2, numpy as np
from PIL import Image
import importlib.util, sys
spec=importlib.util.spec_from_file_location('b1','/home/claude/photos/build_ph.py')
# reuse helpers without rerunning: copy minimal versions
def seam(m,b=6):
    m=m.copy(); w=m.shape[1]
    for k in range(b): f=(k+1)/(b+1); m[:,w-b+k]=m[:,w-b+k]*(1-f)+m[:,0]*f
    return m
def shopfront(w,h,wall,glass=(44,52,60),frame=(205,205,200)):
    g=np.zeros((h,w,3)); g[:]=wall; fh=int(h*0.16); g[:fh]=np.array(wall)*0.55
    gl=np.array(glass,float)
    for y in range(fh+4,h-6): t=(y-fh)/(h-fh); g[y,6:w-6]=gl*(0.8+0.5*(1-t))+np.array([18,22,26])*(1-t)
    n=max(2,int(round(w/45)))
    for x in np.linspace(6,w-7,n+1).astype(int): g[fh+4:h-6,max(0,x-2):x+2]=frame
    g[h-6:]=np.array(wall)*0.7; return g
def strip(stor,nf,fh_m,gf_m,eave_m,wall,name,top=None):
    ph=stor.shape[0]; pxm=ph/fh_m; w=stor.shape[1]
    gfp=int(round(gf_m*pxm)); total=int(round(eave_m*pxm)); rest=total-gfp-nf*ph
    tp=np.zeros((max(rest,4),w,3)); tp[:]=wall
    if top is not None and rest>4: tp=np.array(Image.fromarray(top.astype(np.uint8)).resize((w,rest)),float)
    S=np.concatenate([tp]+[stor]*nf+[shopfront(w,gfp,wall)],0).clip(0,255).astype(np.uint8)
    Image.fromarray(S).save(f'/home/claude/pori/{name}.jpg',quality=90); print(name,S.shape,'bay m',round(w/pxm,2)); return w/pxm
rgb=lambda p: np.asarray(Image.open(p).convert('RGB'),float)
res={}
# ---- 1726 north side: homography-rectified Keskusta 02
im=cv2.imread('img/Keskusta/Keskusta 02.jpg'); ox,oy=1400,350
src=np.float32([[140,370],[985,236],[990,650],[140,675]])+np.float32([ox,oy]); dst=np.float32([[0,0],[600,0],[600,500],[0,500]])
H=np.float32([[1,0,60],[0,1,140],[0,0,1]])@cv2.getPerspectiveTransform(src,dst)
R=cv2.cvtColor(cv2.warpPerspective(im,H,(800,900)),cv2.COLOR_BGR2RGB).astype(float)
st=seam(R[190:290,288:538]); wall=np.median(R[150:180,300:420].reshape(-1,3),0)
res['1726']=strip(st,6,3.25,4.5,24.2,wall,'ph_1726')
# ---- 1599 east side: sheared Gröndahl 23
S=rgb('g23_sheared.png'); A=S[20:142,1335:1840].copy(); B=S[142:264,1335:1840].copy()
blk=A.sum(2)<60; A[blk]=B[blk]
wall=np.median(A[95:115,200:400].reshape(-1,3),0)
nf=round((27.9-4.5)/3.0); res['1599']=strip(seam(A),nf,(27.9-4.5)/nf,4.5,27.9,wall,'ph_1599')
# ---- 602 south-east: Gröndahl 20 (frontal), median over window columns and rows
G=rgb('img/Keskusta/Kesäinen keskusta 2026 Veera Gröndahl (20).jpg'); gy=G.mean(2)
prof=gy[165:255,1380:1980].mean(1); y0=165+int(np.argmax(prof))
cp=gy[y0:y0+270,1380:1442].mean(0); x0=1380+int(np.argmax(cp))
cr=[G[y0+j*90:y0+j*90+90, x0+i*62:x0+i*62+62] for i in range(8) for j in range(3)]
st=np.median(np.stack(cr),0); wall=np.median(st[5:15,25:40].reshape(-1,3),0)
print('602 y0 x0',y0,x0,'wall',wall)
res['602']=strip(seam(st,3),5,3.06,4.5,19.8,wall,'ph_602')
print(res)
