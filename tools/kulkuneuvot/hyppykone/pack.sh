#!/bin/bash
# full build -> game modules (hyppykone.js / hyppykone_m.js)
set -e
cd /home/claude/hyppykone
python3 build3.py | tail -1
LITE=1 python3 build3.py | tail -1
python3 make_game_js.py out/hyppykone.glb game/hyppykone.js 2048 >/dev/null
python3 make_game_js.py out/lite/hyppykone.glb game/hyppykone_m.js 1024 >/dev/null
cd game
for f in hyppykone hyppykone_m; do gltf-transform quantize $f.glb $f.q.glb >/dev/null 2>&1; done
python3 - <<'PY'
import base64
HDR=open('/home/claude/hyppykone/header.txt',encoding='utf-8').read().strip()
for f,tag in (("hyppykone",""),("hyppykone_m"," Kevyt versio kosketuslaitteille.")):
    b=open(f+".q.glb","rb").read()
    open(f+".js","w",encoding="utf-8").write("// "+HDR+tag+"\nexport default \""+base64.b64encode(b).decode()+"\";\n")
    print(f, round(len(b)/1e6,2),'MB')
PY
