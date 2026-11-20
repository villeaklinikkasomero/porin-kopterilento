import json, base64, numpy as np
s=open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..', 'terrain.js')).read(); T=json.loads(s[s.index('{'):s.rindex('}')+1])
HG=np.frombuffer(base64.b64decode(T['hg']),dtype=np.int16).reshape(T['ny'],T['nx'])
HS=np.frombuffer(base64.b64decode(T['hs']),dtype=np.int16).reshape(T['ny'],T['nx'])
def bil(A,x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    fx=np.clip((x-T['x0'])/T['g'],0,T['nx']-1.001); fy=np.clip((y-T['y0'])/T['g'],0,T['ny']-1.001)
    i=np.floor(fx).astype(int); j=np.floor(fy).astype(int); u=fx-i; v=fy-j
    return ((A[j,i]*(1-u)+A[j,i+1]*u)*(1-v)+(A[j+1,i]*(1-u)+A[j+1,i+1]*u)*v)/10
TZg=lambda x,y: bil(HG,x,y)
TZs=lambda x,y: bil(HS,x,y)
