#!/bin/bash
# Fast rautalanka: as runov.sh, but renders with fshot.mjs (only the baked blocks, ~2 s a view). Use for the working loop; check the
# result once with runov.sh (the real game) before calling a building done.
# usage: runov_fast.sh views.json out.jpg KEY:/path/to/sv_KEY.jpg [...]
V=$(realpath "$1"); O=$2; shift 2
GAME=${GAME:-$(dirname "$0")/../..}; T=${TMPDIR:-/tmp}/rautaf; mkdir -p $T
cd "$GAME"; pgrep -f "http.server 8765" >/dev/null || (nohup python3 -m http.server 8765 >/dev/null 2>&1 &); sleep 1
timeout 300 node tools/rautalanka/fshot.mjs $T/ "$V" >/dev/null
L=""
for p in "$@"; do k=${p%%:*}; f=${p#*:}; python3 tools/rautalanka/ov.py "$f" $T/$k.jpg $T/ov_$k.jpg; L="$L $T/ov_$k.jpg"; done
python3 -c "
import sys
from PIL import Image
ims=[Image.open(f) for f in sys.argv[2:]]; c=Image.new('RGB',(800*len(ims),900)); [c.paste(im,(i*800,0)) for i,im in enumerate(ims)]; c.save(sys.argv[1],quality=82)" "$O" $L
echo "$O"
