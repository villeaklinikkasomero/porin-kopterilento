#!/bin/sh
# Kadut + Luvianpuistokadun käytävä alusta loppuun (21.11.2026). Aja repon juuresta; build_roads.py lukee /home/claude/pori/{city.js,styles.json,blender/osm_extract.json}
# (linkitä repon tiedostot sinne) ja kirjoittaa /home/claude/work/roads_geom.pkl, jota tie_luvianpuisto.py käyttää.
set -e
python3 tools/roads/build_roads.py tools/roads/osm_ways_tie.json /tmp/roads_ilman_rinteita.js -1790 -1495 900 995
python3 tools/roads/tie_luvianpuisto.py . /home/claude/work/roads_geom.pkl tools/roads/osm_ways_tie.json /tmp/tie_out
cp /tmp/tie_out/tie/tie_data.js tie/tie_data.js; cp /tmp/tie_out/tie_rinteet.json tools/roads/tie_rinteet.json
python3 tools/roads/build_roads.py tools/roads/osm_ways_tie.json roads.js -1790 -1495 900 995 --rinteet=tools/roads/tie_rinteet.json
