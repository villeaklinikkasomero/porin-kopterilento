import sys, time
sys.path.insert(0, '/home/claude')
from zones import *
name = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else sys.argv[1]
t = time.time()
Z = Zone(name, ZONES[name])
for i in Z.ids: build_building(Z, i, SPEC.get(i) or auto(i))
context(Z); pack(Z)
print('hi', len(Z.hi), 'lo', len(Z.lo), 'exp', len(Z.exp), 's3rep', len(Z.s3rep), 's3copy', len(Z.s3copy))
bake_zone(Z, '/home/claude/out', samples=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 24)
print('time', round(time.time() - t))
