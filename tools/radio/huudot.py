"""Kävelijöiden huudahdukset: tools/radio/huudot.json -> radio/huuto_{m,n,l}_NN.mp3 + radio/huudot.json (pelin lukema kopio).
usage: python3 tools/radio/huudot.py radio/voice/fi_FI-harri-medium.onnx radio/
Piperissä on suomeksi vain miesääni (harri): m = sellaisenaan, n = naisääni samasta nostamalla sävelkorkeutta 1,22x, l = lapsi 1,45x
(asetrate + atempo, kesto säilyy). Jos oikea naisääni saadaan, vaihda tähän."""
import json, os, subprocess, sys, wave
from piper import PiperVoice, SynthesisConfig
onnx, out = sys.argv[1], sys.argv[2]; here = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(here, 'huudot.json'))); v = PiperVoice.load(onnx); cfg = SynthesisConfig(length_scale=0.98, noise_scale=0.6, noise_w_scale=0.5)
tmp = '/tmp/huuto'; os.makedirs(tmp, exist_ok=True)
def make(text, name, k):
    w = f'{tmp}/{name}.wav'
    with wave.open(w, 'wb') as wf: v.synthesize_wav(text, wf, syn_config=cfg)
    sr = wave.open(w).getframerate(); f = f'asetrate={sr}*{k},aresample=44100,atempo={1 / k:.4f},' if k != 1 else ''
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', w, '-af', f + 'loudnorm=I=-15:TP=-1.5', '-ac', '1', '-ar', '44100', '-b:a', '64k', os.path.join(out, name + '.mp3')], check=True)
for i, t in enumerate(P['a']): make(t, f'huuto_m_{i + 1:02d}', 1); make(t, f'huuto_n_{i + 1:02d}', 1.22)
for i, t in enumerate(P.get('n', [])): make(t, f"huuto_n_{len(P['a']) + i + 1:02d}", 1.22)      # naisten omat, numerointi jatkuu yhteisistä
for i, t in enumerate(P['l']): make(t, f'huuto_l_{i + 1:02d}', 1.45)
json.dump({'a': P['a'], 'n': P.get('n', []), 'l': P['l']}, open(os.path.join(out, 'huudot.json'), 'w'), ensure_ascii=False); print(len(P['a']) * 2 + len(P.get('n', [])) + len(P['l']), 'tiedostoa')
