"""python3 audit/street.py 'Antinkatu' [maxdist]  -> /tmp/street_<name>.json and a printed status table"""
import json, re, csv, io, subprocess, sys, pickle
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
NAME = sys.argv[1]; MAXD = float(sys.argv[2]) if len(sys.argv) > 2 else 14
s=open('/home/claude/pori/city.js').read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); B=C['b']
yl=unary_union([LineString([(e['p'][k], e['p'][k+1]) for k in range(0,len(e['p']),2)]) for e in C['r'] if e.get('n')==NAME])
html=open('/home/claude/pori/index.html').read()
ZB={int(k):int(v) for k,v in re.findall(r'(\d+):(\d+)', re.search(r'ZB = \{([^}]*)\}', html).group(1))}
KN=[x.strip().strip("'") for x in re.search(r"const KN = \[([^\]]*)\]",html).group(1).split(',') if "'" in x]
LMAT={k:(float(a),float(b)) for k,a,b in re.findall(r"(\w+): \[(-?[\d.]+), (-?[\d.]+)\]", re.search(r'const LMAT = \{([^}]*)\}', html).group(1))}
PHS=set(int(k) for k in re.findall(r'(\d+): \[\{ t:', re.search(r'let PHS = \{(.*?)\};', html).group(1)))|{int(k) for k in json.load(open('/home/claude/pori/phs.json'))}
L=json.load(open('/home/claude/pori/styles.json'))['b']
Z=json.load(open('/home/claude/pori/city_zones.json'))['zones']; zof={i:z for z,v in Z.items() for i in v['ids']}
L2=json.loads(open('/home/claude/pori/lod2.js').read()[len('export default '):-2]); HIDE=set(L2['hide'])
RAW=pickle.load(open('/home/claude/mmlproc/raw.pkl','rb'))
shells=[(i,Polygon([(p[0],p[1]) for p in r]).buffer(0)) for i,parts in RAW.items() for k,r,_ in parts if k=='G' and len(r)>=3]
src=open('/home/claude/zones.py').read()
ZONES=eval(re.search(r"ZONES = (\{.*?\n\})", src, re.S).group(1).replace('BEPOP','588').replace('UIMA','-1').replace('ISOK','580').replace('PROME','270'))
zn={i:k for k,v in ZONES.items() for i in v}
sys.path.insert(0,'/home/claude'); 
KS=open('/home/claude/kivi.py').read(); ZK=eval(re.search(r"ZONESK = (\{.*?\n\})", KS, re.S).group(1))
zk={i:k for k,v in ZK.items() for i in v}
t=subprocess.check_output(['git','-C','/tmp/pk','show','origin/main:ypakki_keskusta.csv']).decode('utf-8-sig')
YP={r['i']:r for r in csv.DictReader(io.StringIO(t)) if r['i']}
def how(i, pg):
    lm=[k for k,(x,y) in LMAT.items() if pg.contains(Point(x,y))]
    if lm: return 'maamerkki '+lm[0]
    if i in PHS: return 'valokuvajulkisivu'
    if i in zn: return 'käsilohko '+zn[i]
    if i in zk: return 'kivi '+zk[i]
    if i in ZB and ZB[i]<len(KN): return 'ZB '+KN[ZB[i]]
    if i in zof: return 'lohko '+zof[i]
    if i in HIDE:
        c=pg.representative_point(); cov=[j for j,sh in shells if j!=i and sh.contains(c)]
        if cov: j=cov[0]; return f'kuoressa {j} ({how(j, Polygon([(B[j]["p"][k]/10,B[j]["p"][k+1]/10) for k in range(0,len(B[j]["p"]),2)]).buffer(0))})'
        return 'PIILOSSA ilman kuorta'
    return 'pelin oma'
out=[]
for i,b in enumerate(B):
    pts=[(b['p'][k]/10,b['p'][k+1]/10) for k in range(0,len(b['p']),2)]
    pg=Polygon(pts).buffer(0)
    if pg.area<25: continue
    d=pg.distance(yl)
    if d>MAXD: continue
    c=pg.centroid; e=L.get(str(i),{}); y=YP.get(str(i),{}); l2=L2['b'].get(str(i))
    out.append(dict(i=i,x=round(c.x),y=round(c.y),d=round(d,1),area=round(pg.area),h=b['h'],l2=l2 and l2['h'],f=e.get('f'),ypf=y.get('kerrokset'),w=e.get('w'),m=e.get('m'),k=e.get('k'),
        how=how(i,pg),name=(y.get('osoite') or e.get('note','')).replace('Y-pakki: ',''),ypc=y.get('seinäväri'),ypm=y.get('materiaali'),yv=y.get('vuosi') or e.get('y'),url=y.get('url'),house=b.get('k')))
out.sort(key=lambda r:-(r['x']*-0.225+r['y']*-0.974)*-1)
json.dump(out,open(f'/tmp/street_{NAME}.json','w'),ensure_ascii=False)
for r in out: print(r['i'],(r['x'],r['y']),r['area'],'h',r['h'],'l2',r['l2'],'f',r['f'],'yf',r['ypf'],r['w'],'m' if r['m'] else '',r['k'] or '','|',r['how'],'|',r['name'][:42],r['ypc'] or '',r['ypm'] or '',r['yv'] or '')
print(len(out))
