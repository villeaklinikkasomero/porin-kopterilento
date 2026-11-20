# -*- coding: utf-8 -*-
"""Kappaleiden iskut tanssia varten: python3 tools/radio/tahti.py radio/  ->  radio/tahti.json
Lukee radio.jsonista musiikkikappaleet (pop_*, rock_*, electric_*), etsii iskut (librosa.beat.beat_track) ja kirjoittaa ne muodossa
{"pop_1.mp3": [ensimmainen isku ms, vali ms, vali ms, ...]}. Peli (index.html, DANCE) lukee tiedoston ja tahdistaa Dance-klipit iskuihin;
kappale, jota tiedostossa ei ole, tanssitaan 120 BPM:lla. Aja uudestaan aina kun kappaleita vaihdetaan.  pip install librosa soundfile"""
import sys, os, json, warnings
import numpy as np, librosa
warnings.filterwarnings('ignore')
R = sys.argv[1] if len(sys.argv) > 1 else 'radio'
J = json.load(open(os.path.join(R, 'radio.json'), encoding='utf-8'))
files = sorted({e['f'] for v in J.values() for e in v if e['f'].split('_')[0] in ('pop', 'rock', 'electric')})
out = {}
for f in files:
    y, sr = librosa.load(os.path.join(R, f), sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    b = [int(round(float(t) * 1000)) for t in beats]
    out[f] = [b[0]] + [b[i] - b[i - 1] for i in range(1, len(b))]
    print('%s: %d iskua, %.1f BPM' % (f, len(b), 60000.0 * (len(b) - 1) / (b[-1] - b[0])))
json.dump(out, open(os.path.join(R, 'tahti.json'), 'w'), separators=(',', ':'))
