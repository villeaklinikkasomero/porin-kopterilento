"""Tapausten äänet (Outojen asioiden toimitus): tools/radio/tapausN.json -> radio/tapausN_*.mp3 + radio/tapausN.json (pelin lukema kopio kestoineen).
usage: python3 tools/radio/tapaukset.py radio/voice/fi_FI-harri-medium.onnx radio/ 1
Äänet: j = juontaja (harri sellaisenaan), s = soittaja (naisääni 1,22x + puhelinsuodin 300-3400 Hz), neuvot m/n/l kuten huudot.py (1 / 1,22 / 1,45)."""
import json, os, subprocess, sys, wave
from piper import PiperVoice, SynthesisConfig
onnx, out, n = sys.argv[1], sys.argv[2], sys.argv[3]; here = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(here, f'tapaus{n}.json'), encoding='utf8')); v = PiperVoice.load(onnx); cfg = SynthesisConfig(length_scale=1.0, noise_scale=0.6, noise_w_scale=0.5)
tmp = '/tmp/tapaus'; os.makedirs(tmp, exist_ok=True)
def make(text, name, k=1, phone=False):
    w = f'{tmp}/{name}.wav'
    with wave.open(w, 'wb') as wf: v.synthesize_wav(text, wf, syn_config=cfg)
    sr = wave.open(w).getframerate(); f = f'asetrate={sr}*{k},aresample=44100,atempo={1 / k:.4f},' if k != 1 else ''
    if phone: f += 'highpass=f=300,lowpass=f=3400,'
    o = os.path.join(out, name + '.mp3'); subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', w, '-af', f + 'loudnorm=I=-15:TP=-1.5', '-ac', '1', '-ar', '44100', '-b:a', '64k', o], check=True)
    return round(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', o], capture_output=True, text=True).stdout), 1)
K = {'m': 1, 'n': 1.22, 'l': 1.45}
for i, s in enumerate(P['soitto']): s['f'] = f'tapaus{n}_soitto_{i + 1}.mp3'; s['d'] = make(s['t'], s['f'][:-4], 1.22 if s['v'] == 's' else 1, s['v'] == 's')
for g, L in P['neuvot'].items():
    for i, t in enumerate(L): make(t, f'tapaus{n}_neuvo_{g}_{i + 1}', K[g])
for o in P['otsikot']: o['f'] = f"tapaus{n}_juttu_{o['k']}.mp3"; o['d'] = make(o['t'], o['f'][:-4])
json.dump(P, open(os.path.join(out, f'tapaus{n}.json'), 'w', encoding='utf8'), ensure_ascii=False); print('valmis', sorted(f for f in os.listdir(out) if f.startswith(f'tapaus{n}')))
