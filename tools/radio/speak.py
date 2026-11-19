"""Radio Porikopterin puhekanava: puhe.json -> radio/puhe_*.mp3 + radio.json-kanava "puhe".
usage: python3 tools/radio/speak.py tools/radio/voice/fi_FI-harri-medium.onnx radio/
Ääni: Piper (MIT), malli fi_FI-harri-medium (MIT, aineisto CC0). pip install "piper-tts>=1.5"; ffmpeg.
Mainoksiin kevyt taustamusiikki radio/pop_*.mp3:sta (oma sävellys), puheisiin ei taustaa."""
import json, os, subprocess, sys, wave
from piper import PiperVoice, SynthesisConfig

onnx, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(here, 'puhe.json')))
v = PiperVoice.load(onnx)
cfg = SynthesisConfig(length_scale=1.06, noise_scale=0.5, noise_w_scale=0.4)   # hieman rauhallisempi tahti kuin oletus
tmp = '/tmp/puhe'; os.makedirs(tmp, exist_ok=True)

def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

beds = ['pop_1.mp3', 'pop_2.mp3', 'pop_3.mp3']; nb = 0
for s in P['seg']:
    w = f"{tmp}/{s['id']}.wav"
    with wave.open(w, 'wb') as wf: v.synthesize_wav(s['s'], wf, syn_config=cfg)
    mp = os.path.join(out, f"puhe_{s['id']}.mp3")
    if s['k'] == 'm':                    # mainos: musiikkimatto alle, 0,8 s alku ja 1,2 s loppu
        d = dur(w) + 2.0; bed = os.path.join(out, beds[nb % 3]); nb += 1
        fc = (f"[1:a]atrim=20:{20 + d},asetpts=N/SR/TB,volume=0.16,afade=t=in:d=0.6,afade=t=out:st={d - 1.2}:d=1.2,aformat=channel_layouts=mono:sample_rates=44100[b];"
              f"[0:a]adelay=800,apad=pad_dur=1.2,aformat=channel_layouts=mono:sample_rates=44100[s];[s][b]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5[o]")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', w, '-i', bed, '-filter_complex', fc, '-map', '[o]', '-ac', '1', '-ar', '44100', '-b:a', '80k', mp], check=True)
    else:                                # puhe: 0,6 s hiljaisuus alkuun ja loppuun
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', w, '-af', 'adelay=600,apad=pad_dur=0.8,loudnorm=I=-16:TP=-1.5', '-ac', '1', '-ar', '44100', '-b:a', '64k', mp], check=True)
    s['d'] = round(dur(mp), 2); print(s['id'], s['d'])

L = []
for n, s in enumerate(P['seg']):
    L.append({'f': f"puhe_{s['id']}.mp3", 'd': s['d'], 't': s['t']})
    if n % 4 == 3: L.append({'f': 'jingle_1.mp3', 'd': 3.71, 't': 'Radio Porikopteri'})
rj = os.path.join(out, 'radio.json'); R = json.load(open(rj)); R['puhe'] = L
open(rj, 'w').write(json.dumps(R, ensure_ascii=False, indent=1)); print('yht', round(sum(x['d'] for x in L) / 60, 1), 'min')
