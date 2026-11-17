import math,sys
# pixel (800x450, fov 90 vertical) -> (s, z) on a vertical wall plane A->B
def mk(cx,cy,hd,pt,A,B,ch=2.5,W=800,H=450):
    f=(H/2)/math.tan(math.radians(45)); L=math.hypot(B[0]-A[0],B[1]-A[1]); t=((B[0]-A[0])/L,(B[1]-A[1])/L)
    h=math.radians(hd); p=math.radians(pt)
    fwd=(math.sin(h)*math.cos(p), math.cos(h)*math.cos(p), math.sin(p)); right=(math.cos(h), -math.sin(h), 0)
    up=(-math.sin(h)*math.sin(p), -math.cos(h)*math.sin(p), math.cos(p))
    def conv(px,py):
        u=(px-W/2)/f; v=(H/2-py)/f
        d=[fwd[i]+u*right[i]+v*up[i] for i in range(3)]
        det=d[0]*(-t[1])-d[1]*(-t[0]); rx,ry=A[0]-cx,A[1]-cy
        k=(rx*(-t[1])-ry*(-t[0]))/det; s=(d[0]*ry-d[1]*rx)/det
        return round(s,2), round(ch+k*d[2],2)
    return conv
