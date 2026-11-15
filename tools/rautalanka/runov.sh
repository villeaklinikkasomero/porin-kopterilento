#!/bin/bash
# Rautalanka in one go: render the game at every pose of views.json, overlay the model edges on the matching Street View screenshots.
# usage: ZONE=kivi1 runov.sh views.json out.jpg KEY:/path/to/sv_KEY.jpg [KEY2:/path/sv2.jpg ...]
#   KEY = the "k" of a view in views.json; the SV screenshot (800x450 or 480x270) must be taken from exactly that pose.
# needs: a local http server in the game folder on port 8765 (started here), node + playwright, python3 + Pillow.
V=$(realpath "$1"); O=$2; shift 2
GAME=${GAME:-$(dirname "$0")/../..}; T=${TMPDIR:-/tmp}/rauta; mkdir -p $T
cd "$GAME"; pgrep -f "http.server 8765" >/dev/null || (nohup python3 -m http.server 8765 >/dev/null 2>&1 &); sleep 1
timeout 500 node tools/rautalanka/gshot_sv.mjs index.html $T/ "$V"
L=""
for p in "$@"; do k=${p%%:*}; f=${p#*:}; python3 tools/rautalanka/ov.py "$f" $T/$k.jpg $T/ov_$k.jpg; L="$L $T/ov_$k.jpg"; done
python3 -c "
import sys
from PIL import Image
ims=[Image.open(f) for f in sys.argv[2:]]; c=Image.new('RGB',(800*len(ims),900)); [c.paste(im,(i*800,0)) for i,im in enumerate(ims)]; c.save(sys.argv[1],quality=82)" "$O" $L
echo "$O"
