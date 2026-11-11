import sys, time, json
sys.path.insert(0, '/home/claude')
from zones2 import *
name = sys.argv[1]; ids = json.loads(sys.argv[2]); samples = int(sys.argv[3]) if len(sys.argv) > 3 else 16
t = time.time()
for i in ids: B[i]['h'] = eave_of(i)        # facade rows sized to the measured eave height
Z = Zone(name, ids); Z.roofflag = False
for i in ids: build_lod2(Z, i, spec_for(i))
context2(Z); pack(Z)
print('hi', len(Z.hi), 'lo', len(Z.lo), 'exp', len(Z.exp))
bake_zone(Z, '/home/claude/out', samples=samples)
print('time', round(time.time() - t))
