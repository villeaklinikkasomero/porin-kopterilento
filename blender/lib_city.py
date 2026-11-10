import json,math
s=open('/home/claude/pori/city.js').read(); C=json.loads(s[s.index('{'):s.rindex('}')+1])
B=C['b']
def poly(i):
    p=B[i]['p']; pts=[(p[k]/10,p[k+1]/10) for k in range(0,len(p),2)]
    a=sum(pts[k][0]*pts[(k+1)%len(pts)][1]-pts[(k+1)%len(pts)][0]*pts[k][1] for k in range(len(pts)))/2
    if a<0: pts.reverse()
    return pts,abs(a)
def cen(pts): return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
