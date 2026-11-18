"""Radio Porikopteri (18.11.2026): original songs for the car radio, written as MIDI by rules and rendered with FluidSynth
(FluidR3_GM soundfont, MIT licence) - no outside music, so the game may play them freely.

usage: python3 tools/radio/compose.py outdir
  writes outdir/<channel>_<n>.mid / .wav and, after mastering, .mp3 for the channels pop, electric, rock (+ jingles).
"""
import sys, os, random, math, subprocess
import numpy as np
import mido

OUT = sys.argv[1] if len(sys.argv) > 1 else 'radio'
os.makedirs(OUT, exist_ok=True)
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
TPB = 480                                  # ticks per beat
MAJ, MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]

class Song:
    def __init__(self, bpm):
        self.bpm = bpm; self.ev = {}             # channel -> list of (tick, msg)
        self.progs = {}
    def prog(self, ch, p, vol=100, pan=64, rev=40, cho=0):
        self.progs[ch] = (p, vol, pan, rev, cho)
    def note(self, ch, t, dur, n, v):
        if n < 0 or n > 127: return
        v = max(1, min(127, int(v)))
        t = max(0, t)
        self.ev.setdefault(ch, []).append((int(t), mido.Message('note_on', channel=ch, note=int(n), velocity=v)))
        self.ev.setdefault(ch, []).append((int(t + max(10, dur)), mido.Message('note_off', channel=ch, note=int(n), velocity=0)))
    def cc(self, ch, t, c, val):
        self.ev.setdefault(ch, []).append((int(t), mido.Message('control_change', channel=ch, control=c, value=int(max(0, min(127, val))))))
    def save(self, path):
        mf = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm), time=0))
        allev = []
        for ch, (p, vol, pan, rev, cho) in self.progs.items():
            if ch != 9: allev.append((0, 0, mido.Message('program_change', channel=ch, program=p)))
            for c, v in ((7, vol), (10, pan), (91, rev), (93, cho)): allev.append((0, 1, mido.Message('control_change', channel=ch, control=c, value=v)))
        for ch, L in self.ev.items():
            for t, m in L: allev.append((t, 2 if m.type == 'note_on' else 1, m))
        allev.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for t, _, m in allev: tr.append(m.copy(time=t - last)); last = t
        tr.append(mido.MetaMessage('end_of_track', time=TPB * 4))
        mf.save(path)

def chord(key, scale, deg, kind=3):
    """notes (pitch classes above the key root, as MIDI offsets) of the diatonic chord on degree deg (0-based)"""
    return [scale[(deg + 2 * i) % 7] + 12 * ((deg + 2 * i) // 7) for i in range(kind)]

# ---------------------------------------------------------------- drums (GM channel 10)
K, SN, CH, OH, CR, RD, T1, T2, T3, CLP = 36, 38, 42, 46, 49, 51, 50, 47, 43, 39
def drum_bar(s, t0, style, rnd, fill=False, crash=False, intensity=1.0):
    S16 = TPB // 4
    hum = lambda: rnd.randint(-6, 6)
    if crash: s.note(9, t0, TPB, CR, 110)
    if style == 'pop':
        for i in range(16):
            t = t0 + i * S16 + hum()
            if i in (0, 8, 10) or (i == 6 and rnd.random() < 0.3): s.note(9, t, S16, K, 108 * intensity)
            if i in (4, 12): s.note(9, t, S16, SN, 104 * intensity); s.note(9, t, S16, CLP, 60)
            if i % 2 == 0: s.note(9, t, S16, CH, (82 if i % 4 == 0 else 62) * intensity)
    elif style == 'electric':
        for i in range(16):
            t = t0 + i * S16 + hum() // 2
            if i % 4 == 0: s.note(9, t, S16, K, 118 * intensity)
            if i in (4, 12): s.note(9, t, S16, CLP, 98 * intensity)
            if i % 4 == 2: s.note(9, t, S16, OH, 78 * intensity)
            elif rnd.random() < 0.55: s.note(9, t, S16, CH, 50 + 20 * (i % 2 == 0))
    else:   # rock
        for i in range(16):
            t = t0 + i * S16 + hum()
            if i in (0, 7, 8) or (i == 10 and rnd.random() < 0.5): s.note(9, t, S16, K, 115 * intensity)
            if i in (4, 12): s.note(9, t, S16, SN, 118 * intensity)
            if i % 2 == 0: s.note(9, t, S16, RD if intensity > 1.05 else CH, (90 if i % 4 == 0 else 70) * intensity)
    if fill:
        toms = [SN, SN, T1, T1, T2, T2, T3, T3] if style != 'electric' else [SN] * 8
        for j in range(8):
            s.note(9, t0 + (8 + j) * S16 + hum(), S16, toms[j], 80 + j * 5)

# ---------------------------------------------------------------- melody: motif-based, chord tones on the strong beats
RHY = [[0, 2, 4, 6, 8, 12], [0, 3, 6, 8, 10, 12, 14], [0, 2, 3, 4, 8, 10, 12], [2, 4, 6, 8, 11, 14], [0, 4, 6, 8, 12], [0, 2, 4, 7, 8, 10, 12, 15]]
def make_phrase(rnd, chords_bars, key, scale, lo, hi, motif=None):
    """2 bars of melody over two chords -> list of (step16, len16, midi)"""
    if motif is None: motif = [rnd.choice(RHY), rnd.choice(RHY)]
    notes = []; prev = None
    pcs = [((key + scale[i % 7]) % 12) for i in range(7)]
    for b in range(2):
        ch = [(key + c) % 12 for c in chords_bars[b]]
        steps = motif[b]
        for k, st in enumerate(steps):
            nxt = steps[k + 1] if k + 1 < len(steps) else 16
            strong = st % 4 == 0
            cands = [n for n in range(lo, hi + 1) if (n % 12) in (ch if strong else pcs)]
            if prev is None: n = rnd.choice([c for c in cands if (lo + hi) // 2 - 5 <= c <= (lo + hi) // 2 + 5] or cands)
            else:
                w = [math.exp(-abs(c - prev) / (2.5 if strong else 1.6)) * (1.4 if (c % 12) in ch else 1.0) for c in cands]
                n = rnd.choices(cands, w)[0]
            notes.append((b * 16 + st, max(1, nxt - st), n)); prev = n
    return notes, motif

# ---------------------------------------------------------------- one song
PROGS = {'maj': [[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 4], [3, 4, 0, 5], [0, 4, 5, 2]],
         'min': [[0, 5, 2, 6], [0, 3, 6, 5], [0, 6, 5, 6], [5, 6, 0, 0], [0, 3, 4, 0]]}
def song(style, seed):
    rnd = random.Random(seed)
    if style == 'pop': bpm, mode = rnd.choice([104, 108, 112, 116]), rnd.choice(['maj', 'maj', 'min'])
    elif style == 'electric': bpm, mode = rnd.choice([122, 124, 126, 128]), rnd.choice(['min', 'min', 'maj'])
    else: bpm, mode = rnd.choice([132, 138, 144, 150]), rnd.choice(['min', 'maj'])
    key = rnd.randint(0, 11); sc = MAJ if mode == 'maj' else MIN; root = 48 + key
    s = Song(bpm)
    # instruments: ch0 chords, ch1 bass, ch2 lead, ch3 pad, ch4 extra (arp / second guitar), ch5 lead 2
    if style == 'pop':
        s.prog(0, rnd.choice([0, 4, 5]), 92, 50, 45, 20); s.prog(1, rnd.choice([33, 34, 38]), 108, 64, 10); s.prog(2, rnd.choice([80, 73, 11, 54]), 96, 70, 55, 30)
        s.prog(3, rnd.choice([48, 49, 89]), 70, 64, 70, 40); s.prog(4, rnd.choice([27, 25, 26]), 78, 84, 40, 30)
    elif style == 'electric':
        s.prog(0, rnd.choice([90, 81, 87]), 82, 54, 50, 50); s.prog(1, rnd.choice([38, 39]), 112, 64, 15); s.prog(2, rnd.choice([81, 80, 84]), 92, 72, 60, 40)
        s.prog(3, rnd.choice([89, 91, 95]), 78, 64, 80, 60); s.prog(4, rnd.choice([80, 81, 98]), 70, 40, 60, 30)
    else:
        s.prog(0, 30, 100, 40, 30, 10); s.prog(1, rnd.choice([34, 33]), 112, 64, 10); s.prog(2, rnd.choice([30, 29]), 100, 78, 55, 25)
        s.prog(3, 30, 92, 88, 30, 10); s.prog(4, rnd.choice([16, 17]), 52, 64, 50, 20)
    s.prog(9, 0, 112 if style != 'pop' else 104, 64, 30)
    s.prog(5, s.progs[2][0], 66, 50, 60, 30)                    # lead an octave down in the choruses
    pv, pc = rnd.choice(PROGS[mode]), rnd.choice(PROGS[mode])
    while pc == pv: pc = rnd.choice(PROGS[mode])
    pb = rnd.choice(PROGS[mode])
    form = [('intro', pv, 4), ('verse', pv, 8), ('pre', pb, 4), ('chorus', pc, 8), ('verse', pv, 8), ('chorus', pc, 8), ('bridge', pb, 8), ('chorus', pc, 8), ('chorus', pc, 4), ('outro', pv, 4)]
    if style == 'electric': form = [('intro', pv, 8), ('verse', pv, 8), ('build', pb, 8), ('chorus', pc, 16), ('break', pb, 8), ('build', pv, 4), ('chorus', pc, 16), ('outro', pv, 8)]
    BAR = TPB * 4; S16 = TPB // 4; t = 0
    motifs = {}
    for name, prog, bars in form:
        lo_mel, hi_mel = (root + 12, root + 26) if name in ('chorus',) else (root + 7, root + 21)
        inten = 1.1 if name in ('chorus',) else 0.85 if name in ('intro', 'break', 'outro') else 1.0
        for b in range(bars):
            deg = prog[b % len(prog)]; ch = chord(key, sc, deg, 3); ch7 = chord(key, sc, deg, 4)
            bt = t + b * BAR; last = b == bars - 1
            # drums
            if not (style == 'electric' and name == 'break') and not (name == 'intro' and b < bars // 2 and style != 'rock'):
                drum_bar(s, bt, style, rnd, fill=last and name not in ('outro',), crash=(b == 0 and name not in ('intro',)), intensity=inten)
            # bass
            bn = root - 12 + ch[0]
            if style == 'rock':
                for i in range(8): s.note(1, bt + i * 2 * S16, 2 * S16 - 20, bn, 100 + (8 if i % 2 == 0 else 0))
            elif style == 'electric':
                for i in range(16):
                    if i % 4 != 0: s.note(1, bt + i * S16, S16 - 15, bn + (12 if i % 4 == 2 else 0), 96 if i % 4 == 2 else 80)
            else:
                for st, ln in ((0, 3), (3, 3), (6, 2), (8, 4), (12, 2), (14, 2)):
                    n = bn + (7 if st == 12 else 0); s.note(1, bt + st * S16, ln * S16 - 30, n, 98 if st in (0, 8) else 82)
            # chords / rhythm parts
            if style == 'rock':
                pw = [root - 12 + ch[0], root - 12 + ch[0] + 7, root + ch[0]]
                if name in ('verse',):                                  # palm-muted eighths
                    for i in range(8):
                        for n in pw[:2]: s.note(0, bt + i * 2 * S16, S16, n, 92)
                else:                                                   # open power chords
                    for st, ln in ((0, 6), (6, 2), (8, 6), (14, 2)):
                        for n in pw: s.note(0, bt + st * S16, ln * S16 - 20, n, 108)
                    for st, ln in ((0, 8), (8, 8)):
                        for n in pw: s.note(3, bt + st * S16 + 12, ln * S16 - 20, n + 12, 84)
                if name in ('chorus', 'bridge'):
                    for n in ch: s.note(4, bt, BAR - 20, root + n, 60)
            elif style == 'electric':
                for n in ch7: s.note(3, bt, BAR - 10, root + n, 70 if name != 'break' else 85)
                for i in range(16):                                      # pumping stabs
                    if i % 4 == 2 and name not in ('intro', 'break'):
                        for n in ch: s.note(0, bt + i * S16, S16 * 2 - 10, root + 12 + n, 80)
                if name in ('verse', 'chorus', 'build', 'outro'):        # arpeggio
                    arp = [root + 12 + n for n in ch7] + [root + 24 + ch[0]]
                    for i in range(16): s.note(4, bt + i * S16, S16 - 10, arp[(i * (3 if mode == 'min' else 1)) % len(arp)], 62 + 12 * (i % 4 == 0))
                for i in range(16):                                      # sidechain feel on the pad
                    s.cc(3, bt + i * S16, 11, [40, 70, 100, 120][i % 4])
            else:
                for st, ln in ((0, 3), (3, 3), (6, 4), (10, 2), (12, 4)) if name != 'intro' else ((0, 16),):
                    for n in ch7: s.note(0, bt + st * S16, ln * S16 - 25, root + n, 72 if st == 0 else 60)
                if name in ('chorus', 'bridge', 'outro'):
                    for n in ch: s.note(3, bt, BAR - 10, root + 12 + n, 64)
                if name in ('verse', 'chorus'):
                    for st in (2, 6, 10, 14):
                        for n in ch[:2]: s.note(4, bt + st * S16, S16, root + 12 + n, 58)
        # melody: phrases of two bars, A A' B A
        if name not in ('intro', 'outro', 'break') and not (style == 'rock' and name == 'pre'):
            key_m = name if name != 'build' else 'pre'
            A, motA = make_phrase(rnd, [chord(key, sc, prog[0]), chord(key, sc, prog[1 % len(prog)])], key, sc, lo_mel, hi_mel, motifs.get(key_m))
            motifs[key_m] = motA
            Bp, _ = make_phrase(rnd, [chord(key, sc, prog[2 % len(prog)]), chord(key, sc, prog[3 % len(prog)])], key, sc, lo_mel, hi_mel)
            seq = [A, Bp] * (bars // 4) if bars >= 4 else [A]
            if bars >= 8: seq = [A, Bp, A, Bp] * (bars // 8)
            leadch = 2
            for k, ph in enumerate(seq):
                for st, ln, n in ph:
                    if style == 'electric' and name == 'build' and k % 2 == 1: continue
                    vel = 92 + (8 if st % 8 == 0 else 0) + rnd.randint(-6, 6)
                    s.note(leadch, t + k * 2 * BAR + st * S16, ln * S16 - 30, n + (12 if style == 'rock' and name == 'bridge' else 0), vel)
                    if name == 'chorus' and style != 'rock': s.note(5 if 5 in s.progs else leadch, t + k * 2 * BAR + st * S16, ln * S16 - 30, n - 12, vel - 25)
        t += bars * BAR
    # final chord ring-out
    for n in chord(key, sc, pv[0], 3): s.note(0, t, BAR * 2, root + n, 80)
    s.note(9, t, TPB, CR, 100); s.note(1, t, BAR * 2, root - 12 + chord(key, sc, pv[0])[0], 90)
    return s

def jingle(seed):
    """short radio sting 'Radio Porikopteri'"""
    rnd = random.Random(seed); s = Song(120); key = 60 + rnd.choice([0, 2, 5])
    s.prog(0, 61, 110, 64, 60); s.prog(1, 89, 80, 64, 80); s.prog(9, 0, 100)
    for k, n in enumerate([0, 4, 7, 12, 11, 12]): s.note(0, k * TPB // 2, TPB // 2 - 20 if k < 5 else TPB * 2, key + n, 100)
    for n in (0, 4, 7, 12): s.note(1, 0, TPB * 5, key + n - 12, 70)
    s.note(9, 0, TPB, CR, 100); s.note(9, int(TPB * 2.5), TPB, CR, 110); s.note(9, int(TPB * 2.5), TPB, K, 110)
    return s

def render(mid, wav):
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.55', '-r', '44100', '-R', '1', '-C', '1', '-F', wav, SF2, mid], check=True)

def master(wav, mp3, kbps=96):
    """trim, gentle compression and limiting, loudness to about -15 LUFS (ffmpeg loudnorm), mp3"""
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af',
                    'silenceremove=start_periods=1:start_threshold=-60dB,areverse,silenceremove=start_periods=1:start_threshold=-60dB,areverse,'
                    'acompressor=threshold=-18dB:ratio=3:attack=15:release=200,alimiter=limit=0.89,loudnorm=I=-15:TP=-1.5:LRA=9',
                    '-ar', '44100', '-b:a', f'{kbps}k', mp3], check=True)

if __name__ == '__main__':
    plan = [('pop', [11, 23, 37]), ('electric', [5, 17, 29]), ('rock', [7, 19, 31])]
    for style, seeds in plan:
        for n, sd in enumerate(seeds):
            base = os.path.join(OUT, f'{style}_{n + 1}'); s = song(style, sd); s.save(base + '.mid'); render(base + '.mid', base + '.wav'); master(base + '.wav', base + '.mp3')
            print(base, round(os.path.getsize(base + '.mp3') / 1e6, 2), 'MB')
    for n in range(2):
        base = os.path.join(OUT, f'jingle_{n + 1}'); s = jingle(n + 3); s.save(base + '.mid'); render(base + '.mid', base + '.wav'); master(base + '.wav', base + '.mp3', 96)
