import sys, time
sys.path.insert(0, '/home/claude')
from zones import *
name = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else sys.argv[1]
t = time.time()
if name not in ZONES:                                    # Kivi-Pori and Karhu blocks (kivi.py), so that 'bake kivi5' works the same way
    import kivi
    if name in kivi.ZONESK:
        kivi.build_and_bake(name, kivi.ZONESK[name], int(sys.argv[-1]) if sys.argv[-1].isdigit() else 24); sys.exit(0)
Z = Zone(name, ZONES[name]); Z.roofflag = name not in NOROOF
lod = False
for i in Z.ids:
    sp = SPEC.get(i) or auto(i)
    if sp.get('lod2'):                                   # facades on the measured LoD2 shell, roofs baked (BePOP)
        import zones2; zones2.ROOFBAKE = True; lod = True
        B[i]['h'] = zones2.eave_of(i); zones2.build_lod2(Z, i, sp)
        for ex in sp.get('extra', []): ex(Z, None, None, sp['P'])
    else: build_building(Z, i, sp)
if lod: zones2.context2(Z)
else: context(Z)
pack(Z)
print('hi', len(Z.hi), 'lo', len(Z.lo), 'exp', len(Z.exp), 's3rep', len(Z.s3rep), 's3copy', len(Z.s3copy))
bake_zone(Z, '/home/claude/out', samples=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 24)
print('time', round(time.time() - t))
