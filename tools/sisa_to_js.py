"""Sisätila pelin moduuliksi: python3 tools/sisa_to_js.py [DIR=/home/claude/out_sisa] [NIMI=kirkko_sisa] -> NIMI.js
(DIR: blender/NIMI.py:n tulos NIMI.glb + NIMI_lm.jpg + NIMI.json)."""
import sys, json, base64
d = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out_sisa'
N = sys.argv[2] if len(sys.argv) > 2 else 'kirkko_sisa'
b64 = lambda f: base64.b64encode(open(f'{d}/{f}', 'rb').read()).decode()
m = json.load(open(f'{d}/{N}.json'))
r3 = lambda v: [r3(x) for x in v] if isinstance(v, list) else round(v, 3) if isinstance(v, float) else v
m = {k: (dict((a, r3(b)) for a, b in v.items()) if isinstance(v, dict) else r3(v)) for k, v in m.items()}
open(N + '.js', 'w').write('// Sisätila ' + N + ' (blender/' + N + '.py): meta = törmäykset ja mitat, lm = leivottu valokartta (UV1), default = GLB\n'
    'export const meta = %s;\nexport const lm = "data:image/jpeg;base64,%s";\nexport default "%s";\n' % (json.dumps(m, separators=(',', ':')), b64(N + '_lm.jpg'), b64(N + '.glb')))
print(N + '.js')
