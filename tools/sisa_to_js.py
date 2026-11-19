"""Kirkon sisätila pelin moduuliksi: python3 tools/sisa_to_js.py [DIR=/home/claude/out_sisa] -> kirkko_sisa.js
(DIR: blender/kirkko_sisa.py:n tulos kirkko_sisa.glb + kirkko_sisa_lm.jpg + kirkko_sisa.json)."""
import sys, json, base64
d = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out_sisa'
b64 = lambda f: base64.b64encode(open(f'{d}/{f}', 'rb').read()).decode()
m = json.load(open(f'{d}/kirkko_sisa.json'))
r3 = lambda v: [r3(x) for x in v] if isinstance(v, list) else round(v, 3) if isinstance(v, float) else v
m = {k: (dict((a, r3(b)) for a, b in v.items()) if isinstance(v, dict) else r3(v)) for k, v in m.items()}
open('kirkko_sisa.js', 'w').write('// Keski-Porin kirkon sisätila (blender/kirkko_sisa.py): meta = törmäykset ja mitat, lm = leivottu valokartta (UV1), default = GLB\n'
    'export const meta = %s;\nexport const lm = "data:image/jpeg;base64,%s";\nexport default "%s";\n' % (json.dumps(m, separators=(',', ':')), b64('kirkko_sisa_lm.jpg'), b64('kirkko_sisa.glb')))
print('kirkko_sisa.js')
