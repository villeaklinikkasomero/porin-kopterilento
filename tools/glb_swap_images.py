"""Vaihtaa GLB:n upotettuja kuvia nimen mukaan koskematta geometriaan (valokartan UV:t säilyvät, uutta leivontaa ei tarvita).
usage: python3 tools/glb_swap_images.py in.glb out.glb nimi=kuva.png [nimi2=kuva2.png ...]   (kuvat tallennetaan JPEG 88)"""
import sys, json, struct, io
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]; swaps = dict(a.split('=', 1) for a in sys.argv[3:])
d = open(src, 'rb').read(); jl = struct.unpack('<I', d[12:16])[0]; j = json.loads(d[20:20 + jl]); b0 = 20 + jl + 8; binb = d[b0:b0 + struct.unpack('<I', d[20 + jl:24 + jl])[0]]
new = {}
for im in j['images']:
    if im.get('name') in swaps:
        bio = io.BytesIO(); Image.open(swaps[im['name']]).convert('RGB').save(bio, 'JPEG', quality=88); new[im['bufferView']] = bio.getvalue(); im['mimeType'] = 'image/jpeg'; print('vaihdettu', im['name'], len(bio.getvalue()))
out = bytearray()
for i, bv in sorted(enumerate(j['bufferViews']), key=lambda t: t[1].get('byteOffset', 0)):
    data = new.get(i, binb[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']])
    while len(out) % 4: out.append(0)
    bv['byteOffset'] = len(out); bv['byteLength'] = len(data); out += data
while len(out) % 4: out.append(0)
j['buffers'][0]['byteLength'] = len(out); js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
open(dst, 'wb').write(b'glTF' + struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack('<I', len(js)) + b'JSON' + js + struct.pack('<I', len(out)) + b'BIN\x00' + bytes(out))
