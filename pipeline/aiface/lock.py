"""Colour lock for AI facades: the AI may repaint detail but not the paint colours.
usage: lock.py ai.png raw.png out.png [k=6]
raw.png = our own orthographic render (exact game colours). Its pixels are clustered into k colour regions (wall, trim, plinth,
roof, glass, sky); inside each region the AI image keeps its own detail (deviation from the region mean) while the region mean
is moved to the render's colour, in Lab, so the walls stay the colour measured from the street photos."""
import sys, numpy as np
from PIL import Image
from skimage.color import rgb2lab, lab2rgb
ai_f, raw_f, out_f = sys.argv[1:4]; k = int(sys.argv[4]) if len(sys.argv) > 4 else 6
ai = np.asarray(Image.open(ai_f).convert('RGB')).astype(np.float32) / 255
raw = np.asarray(Image.open(raw_f).convert('RGB').resize((ai.shape[1], ai.shape[0]), Image.NEAREST)).astype(np.float32) / 255
La, Lr = rgb2lab(ai), rgb2lab(raw)
X = Lr.reshape(-1, 3); rng = np.random.default_rng(0); C = X[rng.choice(len(X), k, replace=False)]
for _ in range(15):                                   # small k-means on the render's colours
    lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(2), 1)
    C = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
lab = lab.reshape(Lr.shape[:2]); out = La.copy()
for i in range(k):
    m = lab == i
    if m.sum() < 50: continue
    mu_ai = La[m].mean(0); mu_r = Lr[m].mean(0)
    out[m] = La[m] - mu_ai + mu_r                    # keep AI detail, use the render's mean colour (L, a, b)
    out[m, 1:] = mu_r[1:] + (La[m, 1:] - mu_ai[1:]) * 0.6   # damp the AI's own hue swings
Image.fromarray((np.clip(lab2rgb(out), 0, 1) * 255).astype(np.uint8)).save(out_f); print(out_f)
