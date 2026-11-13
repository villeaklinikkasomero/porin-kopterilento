"""Apply the LoD2 corner cuts (chamfer.py) to the game's lod2.js roofs, for buildings that are drawn by a Blender block.
Run from the repo root: python3 blender/chamfer_lod2.py  (rewrites lod2.js; re-running is harmless: a cut corner is not cut again)"""
import json, pickle, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chamfer
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
RAW = pickle.load(open('/home/claude/mmlproc/raw.pkl', 'rb'))
s = open(os.path.join(ROOT, 'city.js')).read(); B = json.loads(s[s.index('{'):s.rindex('}') + 1])['b']
LOOK = json.load(open(os.path.join(ROOT, 'styles.json')))
blocks = set(i for v in json.load(open(os.path.join(ROOT, 'city_zones.json')))['zones'].values() for i in v['ids'])
import re
k = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kivi.py')).read()
m = re.search(r"ZONESK = \{(.*?)\n\}", k, re.S)
blocks |= set(int(x) for x in re.findall(r"\b\d{1,5}\b", m.group(1)))
done = {i: v for i, v in chamfer.apply(RAW, B, LOOK).items() if i in blocks}
t = open(os.path.join(ROOT, 'lod2.js')).read(); pre = 'export default '
L2 = json.loads(t[len(pre):t.rindex('}') + 1])
chamfer.clip_lod2(L2, done)
open(os.path.join(ROOT, 'lod2.js'), 'w').write(pre + json.dumps(L2, separators=(',', ':')) + ';\n')
print('cut', sorted(done))
