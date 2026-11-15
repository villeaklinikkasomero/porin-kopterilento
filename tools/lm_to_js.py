"""Wrap a landmark baked by blender/lm.py (out/bl_KEY.glb + bl_KEY.json) into the game's bl_KEY.js.
usage: python3 tools/lm_to_js.py KEY [outdir]   (local bake: python3 blender/lm.py KEY; 'still' renders a preview only)"""
import sys, json, base64
k = sys.argv[1]; o = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/blender/out'
m = json.load(open(f'{o}/bl_{k}.json')); b = base64.b64encode(open(f'{o}/bl_{k}.glb', 'rb').read()).decode()
open(f'bl_{k}.js', 'w').write('export const x = %s, y = %s, roof = %s;\nexport default "%s";\n' % (m['x'], m['y'], 'true' if m['roof'] else 'false', b))
print('bl_%s.js' % k)
