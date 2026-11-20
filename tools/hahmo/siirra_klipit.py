# -*- coding: utf-8 -*-
"""Siirtaa nimetyt animaatioklipit mallichatin GLB:sta pelin base64-moduuliin (hahmo.js / npc_*.js) koskematta muuhun
(verkko, tekstuurit ja pelin omat klipit Walk/Run/Idle/Sit/Chair sailyvat). Luut sovitetaan nimen mukaan.
Ajo: python tools/hahmo/siirra_klipit.py peli.js lahde.glb ulos.js Klippi1,Klippi2"""
import sys, json, struct, base64, re
def rd(p):
    b = open(p, 'rb').read(); pre = post = None
    if p.endswith('.js'):
        s = b.decode(); m = re.search(r'[A-Za-z0-9+/=]{1000,}', s); pre, post = s[:m.start()], s[m.end():]; b = base64.b64decode(m.group(0))
    jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + jl]); o = 20 + jl; bl = struct.unpack('<I', b[o:o + 4])[0]
    return j, bytearray(b[o + 8:o + 8 + bl]), pre, post
def raw(j, bn, i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; n = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
    assert a['componentType'] == 5126 and not bv.get('byteStride'); o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return bytes(bn[o:o + 4 * n * a['count']]), a
dst, src, out, names = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
J, B, pre, post = rd(dst); S, SB, _, _ = rd(src)
dn = {n.get('name'): i for i, n in enumerate(J['nodes'])}
worst = 0.0
for i, n in enumerate(S['nodes']):                                   # same skeleton? compare rest pose of every node
    m = J['nodes'][dn[n['name']]]
    for k in ('translation', 'rotation', 'scale'):
        a, b = n.get(k), m.get(k)
        if a and b: worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
        elif (a or b) and k == 'translation': worst = max(worst, max(abs(x) for x in (a or b)))
print('  rest pose max diff', round(worst, 6)); assert worst < 2e-3, 'luusto eroaa'
cache = {}
def put(i):
    if i in cache: return cache[i]
    data, a = raw(S, SB, i)
    while len(B) % 4: B.append(0)
    J['bufferViews'].append({'buffer': 0, 'byteOffset': len(B), 'byteLength': len(data)}); B.extend(data)
    na = {k: v for k, v in a.items() if k not in ('bufferView', 'byteOffset')}; na['bufferView'] = len(J['bufferViews']) - 1
    J['accessors'].append(na); cache[i] = len(J['accessors']) - 1; return cache[i]
for nm in names:
    A = next(a for a in S['animations'] if a['name'] == nm)
    N = {'name': nm, 'samplers': [dict(s, input=put(s['input']), output=put(s['output'])) for s in A['samplers']],
         'channels': [{'sampler': c['sampler'], 'target': {'node': dn[S['nodes'][c['target']['node']]['name']], 'path': c['target']['path']}} for c in A['channels']]}
    J['animations'] = [a for a in J['animations'] if a['name'] != nm] + [N]
J['buffers'][0]['byteLength'] = len(B)
js = json.dumps(J, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
while len(B) % 4: B.append(0)
g = b'glTF' + struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(B)) + struct.pack('<I', len(js)) + b'JSON' + js + struct.pack('<I', len(B)) + b'BIN\x00' + bytes(B)
open(out, 'w' if pre is not None else 'wb', **({'encoding': 'utf-8', 'newline': ''} if pre is not None else {})).write(pre + base64.b64encode(g).decode() + post if pre is not None else g)
print('  ->', out, len(g), [a['name'] for a in J['animations']])
