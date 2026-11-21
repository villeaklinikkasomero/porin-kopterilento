"""IC2-sisätilan tekstuurit (proseduraaliset, PIL): verhoilu, matto, muovimatto, seinäpaneeli, katto, pöytälaminaatti, patterin säleikkö."""
import numpy as np, os
from PIL import Image, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sisa_tex'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
def save(n, a): Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, n + '.png'))
def noise(n, s):
    a = rng.random((n // s + 2, n // s + 2)); im = Image.fromarray((a * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC); return np.asarray(im) / 255.0
N = 512
# verhoilu: tummansininen kudos (sidos), pieni vaaleansininen ja vihreä kuvio (VR IC2 2. luokka)
y, x = np.mgrid[0:N, 0:N]
weave = ((x // 2 + y // 2) % 2) * 0.5 + ((x // 2) % 2) * 0.25
base = np.array([52, 64, 92], float)
f = base[None, None, :] * (0.82 + 0.18 * weave[..., None]) * (0.9 + 0.2 * noise(N, 8)[..., None])
dots = ((x % 32 < 3) & (y % 32 < 3)) | (((x + 16) % 32 < 2) & ((y + 16) % 32 < 2))
f[dots] = [96, 128, 170]
f[((x + 8) % 64 < 2) & ((y + 40) % 64 < 2)] = [90, 160, 70]
save('verhoilu', f)
# matto: siniharmaa, nukka
c = np.array([74, 80, 92], float); m = c[None, None, :] * (0.8 + 0.25 * rng.random((N, N, 1))) * (0.92 + 0.12 * noise(N, 16)[..., None]); save('matto', m)
# muovimatto (eteinen, portaat): harmaa pilkullinen
c = np.array([138, 142, 143], float); v = c[None, None, :] * (0.93 + 0.1 * noise(N, 32)[..., None]); sp = rng.random((N, N)) > 0.985
v[sp] = [90, 94, 96]; v[rng.random((N, N)) > 0.99] = [205, 205, 200]; save('muovimatto', v)
# seinäpaneeli: vaalea, hienojakoinen kuvio, paneelisauma 1,8 m välein (tekstuuri toistuu 1,8 m)
c = np.array([226, 227, 222], float); w = c[None, None, :] * (0.97 + 0.04 * noise(N, 64)[..., None]); w[:, :3] = [150, 152, 150]; w[:, 3:5] = [245, 245, 242]; save('seina', w)
# katto: valkoinen rei'itetty akustiikkalevy
k = np.full((N, N, 3), 238.0); k[(x % 16 < 3) & (y % 16 < 3)] = [205, 207, 205]; k[:, :2] = [190, 190, 188]; save('katto', k)
# pöytä: vaaleanharmaa laminaatti, hieno juovitus
t = np.array([170, 173, 175], float)[None, None, :] * (0.95 + 0.06 * np.sin(y[..., None] * 0.9 + 3 * noise(N, 32)[..., None])); save('poyta', t)
# patterin säleikkö
g = np.full((N, N, 3), 120.0); g[(x % 16 < 8)] = [60, 62, 64]; save('saleikko', g)
print('tekstuurit', sorted(os.listdir(OUT)))
