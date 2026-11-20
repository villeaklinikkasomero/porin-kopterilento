import numpy as np, rasterio
from rasterio.enums import Resampling
from pyproj import Transformer
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
U='/mnt/user-data/uploads/porin-kopterilento/'
OX0,OX1,OY1=-2504.1,2450.8,1894.4; OYold=-1671.6; OYnew=-3501.6
T=Transformer.from_crs(4326,3067,always_xy=True)
ds={k:rasterio.open(U+'mml_orto/M3412%s.jp2'%k) for k in 'CDEF'}
SC=2  # read at 1 m/px (overview)
cache={}
def arr(k):
    if k not in cache:
        d=ds[k]; cache[k]=d.read(out_shape=(3,d.height//SC,d.width//SC),resampling=Resampling.average)
    return cache[k]
def render(ya,yb,W,H):
    xs=OX0+(np.arange(W)+0.5)/W*(OX1-OX0); ys=yb-(np.arange(H)+0.5)/H*(yb-ya)
    X,Y=np.meshgrid(xs,ys); E,N=T.transform(X/53278+21.796,Y/111437+61.486)
    img=np.zeros((H,W,3),np.float32)
    for k,d in ds.items():
        b=d.bounds; m=(E>=b.left)&(E<b.right)&(N>b.bottom)&(N<=b.top)
        if not m.any(): continue
        a=arr(k); col=((E[m]-b.left)/(0.5*SC)-0.5).clip(0,a.shape[2]-1.001); row=((b.top-N[m])/(0.5*SC)-0.5).clip(0,a.shape[1]-1.001)
        c0=col.astype(int); r0=row.astype(int); fc=col-c0; fr=row-r0
        for ch in range(3):
            A=a[ch].astype(np.float32); img[...,ch][m]=A[r0,c0]*(1-fc)*(1-fr)+A[r0,c0+1]*fc*(1-fr)+A[r0+1,c0]*(1-fc)*fr+A[r0+1,c0+1]*fc*fr
    return img
def extend(old, name, outH):
    W,Hold=old.size; mpp=(OY1-OYold)/Hold
    Hs=int(round((OYold-OYnew)/mpp))
    strip=render(OYnew,OYold,W,Hs)
    band=int(150/mpp); ref=np.asarray(old,np.float32)[-band:]; mine=render(OYold,OYold+band*mpp,W,band)
    for ch in range(3):
        mu_r,sd_r=ref[...,ch].mean(),ref[...,ch].std(); mu_m,sd_m=mine[...,ch].mean(),mine[...,ch].std()
        strip[...,ch]=(strip[...,ch]-mu_m)/sd_m*sd_r+mu_r
        print(name,ch,round(mu_r,1),round(sd_r,1),round(mu_m,1),round(sd_m,1))
    full=np.vstack([np.asarray(old,np.float32),strip]).clip(0,255).astype(np.uint8)
    im=Image.fromarray(full).resize((W,outH),Image.LANCZOS); return im
old=Image.open(U+'outer.jpg').convert('RGB')
extend(old,'outer',4096).save('/mnt/user-data/outputs/outer.jpg',quality=88)
mini=Image.open(U+'mini.jpg').convert('RGB')
extend(mini,'mini',int(round(922*(OY1-OYnew)/(OY1-OYold)))).save('/mnt/user-data/outputs/mini.jpg',quality=88)
