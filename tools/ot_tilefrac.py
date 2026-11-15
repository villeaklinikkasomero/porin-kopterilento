import sys,numpy as np, os
from PIL import Image
from scipy import ndimage
def norm(a):
    m=a.reshape(-1,3).mean(0); s=a.reshape(-1,3).std(0)+1e-3; return (a-m)/s
for f in sorted(os.listdir('pori/ot')):
    k=f[3:-4]
    o=np.asarray(Image.open(f'pori/ot/{f}').convert('RGB').resize((512,512),Image.BILINEAR),np.float32)
    n=np.asarray(Image.open(f'work/ot_new/{f}').convert('RGB').resize((512,512),Image.BILINEAR),np.float32)
    a=ndimage.gaussian_filter(norm(o).mean(2),1);b=ndimage.gaussian_filter(norm(n).mean(2),1)
    B=8;h=64
    A=a.reshape(h,B,h,B).transpose(0,2,1,3).reshape(h,h,-1);Bb=b.reshape(h,B,h,B).transpose(0,2,1,3).reshape(h,h,-1)
    A=A-A.mean(-1,keepdims=True);Bb=Bb-Bb.mean(-1,keepdims=True)
    cor=(A*Bb).sum(-1)/(np.sqrt((A*A).sum(-1)*(Bb*Bb).sum(-1))+1e-6)
    tex=np.sqrt((A*A).mean(-1)); dm=np.abs(A.mean(-1)*0+a.reshape(h,B,h,B).mean((1,3))-b.reshape(h,B,h,B).mean((1,3)))
    ch=((cor<0.45)&(tex>0.2))|(dm>0.9); ch=ndimage.binary_opening(ch)
    print(k, round(float(ch.mean()),3), round(float(np.median(cor[tex>0.2])) if (tex>0.2).any() else 1,2))
