"""Photo facade strips (Porin kaupunki photos): one bay wide, full height from street to eave.
v = z / eave in the game, u = metres / bay width (repeats)."""
import numpy as np
from PIL import Image
im=np.asarray(Image.open('img/Keskusta/Keskusta 03.jpg').convert('RGB'),float)
def seam(m,b=6):
    m=m.copy(); w=m.shape[1]
    for k in range(b): f=(k+1)/(b+1); m[:,w-b+k]=m[:,w-b+k]*(1-f)+m[:,0]*f
    return m
def shopfront(w,h,wall,glass=(44,52,60),frame=(205,205,200),fascia=None):
    g=np.zeros((h,w,3)); g[:]=wall
    fh=int(h*0.16); g[:fh]=fascia if fascia is not None else np.array(wall)*0.55      # sign band
    gl=np.array(glass,float)
    for y in range(fh+4,h-6):
        t=(y-fh)/(h-fh); g[y,6:w-6]=gl*(0.8+0.5*(1-t))+np.array([18,22,26])*(1-t)       # glass with sky reflection
    for x in np.linspace(6,w-7,4).astype(int): g[fh+4:h-6,max(0,x-2):x+2]=frame       # mullions
    g[h-6:]=np.array(wall)*0.7                                                           # plinth
    return g
def strip(stor,nf,fh_m,gf_m,eave_m,wall,name,top=None,fascia=None):
    ph=stor.shape[0]; pxm=ph/fh_m; w=stor.shape[1]
    gfp=int(round(gf_m*pxm)); total=int(round(eave_m*pxm))
    rest=total-gfp-nf*ph; parts=[]
    tp=np.zeros((max(rest,4),w,3)); tp[:]=wall
    if top is not None: tp=np.array(Image.fromarray(top.astype(np.uint8)).resize((w,max(rest,4))),float)
    parts=[tp]+[stor]*nf+[shopfront(w,gfp,wall,fascia=fascia)]
    S=np.concatenate(parts,0).clip(0,255).astype(np.uint8)
    Image.fromarray(S).save(f'/home/claude/pori/{name}.jpg',quality=90); print(name,S.shape,'bay m',round(w/pxm,2))
    return w/pxm
W=seam(im[738:838,848:1181]); Y=seam(im[740:830,1836:1970],4); B=seam(im[745:835,2120:2248],4)
wall_w=np.median(W[5:20].reshape(-1,3),0); wall_y=np.median(im[700:740,1840:1960].reshape(-1,3),0); wall_b=np.median(B[5:15].reshape(-1,3),0)
print('walls',wall_w,wall_y,wall_b)
r={}
r['603']=strip(W,6,3.05,4.5,22.8,wall_w,'ph_603',top=im[500:540,848:1181])
r['604y']=strip(Y,6,3.23,4.5,23.9,wall_y,'ph_604y',top=im[540:600,1836:1970])
r['604b']=strip(B,6,3.23,4.5,23.9,wall_b,'ph_604b',top=im[548:608,2120:2248])
print(r)
