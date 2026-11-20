# Sepeli (raidesepeli 31.5/63, harmaa graniitti/gabro), saumaton 1,6 m ruutu: albedo, normaali, AO+karheus
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter
rng = np.random.default_rng(7)
N = 1024; TILE = 1.6   # m
def tile_voronoi(npts, N):
    P = rng.random((npts, 2))
    # toistuva: kopiot naapuriruutuihin
    off = np.array([[i, j] for i in (-1, 0, 1) for j in (-1, 0, 1)])
    PP = (P[None, :, :] + off[:, None, :]).reshape(-1, 2); ID = np.tile(np.arange(npts), 9)
    kd = cKDTree(PP)
    y, x = np.mgrid[0:N, 0:N] / N
    q = np.stack([x.ravel(), y.ravel()], 1)
    d, i = kd.query(q, k=2)
    return P, PP, ID, d[:, 0].reshape(N, N), d[:, 1].reshape(N, N), ID[i[:, 0]].reshape(N, N), PP[i[:, 0]].reshape(N, N, 2)
def noise(N, s, seed):
    r = np.random.default_rng(seed).random((N, N))
    return gaussian_filter(r, s, mode='wrap')
def build():
    # kaksi kerrosta: isot kivet + pienemmät väliin
    npts = int((TILE / 0.05) ** 2)
    P, PP, ID, d1, d2, cid, cp = tile_voronoi(npts, N)
    y, x = np.mgrid[0:N, 0:N] / N
    edge = (d2 - d1) * N * TILE / N   # metreinä (suunnilleen)
    edge = (d2 - d1) * TILE           # m
    k = len(P)
    nrm = rng.normal(size=(k, 3)); nrm[:, 2] = np.abs(nrm[:, 2]) * 2.2 + 0.8; nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    base = rng.random(k) * 0.012
    # särmikäs kivi: tasopinta (viisto) + reunoilta pyöristys
    dx = (x - cp[..., 0]) * TILE; dy = (y - cp[..., 1]) * TILE
    n = nrm[cid]
    plane = -(n[..., 0] * dx + n[..., 1] * dy) / n[..., 2] * 0.55
    h = 0.022 + base[cid] + plane - 0.018 * np.exp(-edge / 0.004)
    # toinen viisto (särmä) osaan kivistä
    n2 = rng.normal(size=(k, 3)); n2[:, 2] = np.abs(n2[:, 2]) * 2 + 1; n2 /= np.linalg.norm(n2, axis=1)[:, None]
    pl2 = -(n2[cid][..., 0] * dx + n2[cid][..., 1] * dy) / n2[cid][..., 2] * 0.55 + 0.004
    h = np.minimum(h, 0.022 + base[cid] + pl2)
    h = np.minimum(h, 0.016 + base[cid] + edge * 0.6)   # kartiomainen reuna -> sauma
    h += (noise(N, 1.2, 3) - 0.5) * 0.004
    h = gaussian_filter(h, 0.7, mode='wrap')
    # väri: graniitti (harmaa, osin punertava), pilkut
    tone = rng.random(k)
    g = 0.42 + 0.30 * tone[cid]
    warm = (rng.random(k) < 0.18)[cid]
    r = g * np.where(warm, 1.06, 0.99); gg = g * np.where(warm, 0.99, 1.0); b = g * np.where(warm, 0.94, 1.02)
    speck = noise(N, 0.6, 11); speck = (speck - speck.mean()) / speck.std()
    sp = np.clip(speck * 0.07, -0.15, 0.15)
    dark = (noise(N, 0.5, 12) > np.percentile(noise(N, 0.5, 12), 93)) * -0.12
    col = np.stack([r + sp + dark, gg + sp + dark, b + sp + dark], -1)
    # ruoste ja pöly: ruskea likaantuminen matalissa kohdissa
    low = np.clip((0.02 - h) / 0.02, 0, 1)
    dust = np.array([0.36, 0.31, 0.25])
    col = col * (1 - low[..., None] * 0.6) + dust * low[..., None] * 0.6
    # AO: syvät saumat lähes mustia (alla näkyy varjossa olevia kiviä)
    ao = np.clip(1 - (gaussian_filter(h, 5, mode='wrap') - h) * 40, 0.22, 1)
    ao = ao * np.clip(edge / 0.0025, 0.75, 1)
    gyy, gxx = np.gradient(h * N / TILE)
    nm = np.stack([-gxx, gyy, np.ones_like(h)], -1); nm /= np.linalg.norm(nm, axis=-1, keepdims=True)
    # puoliksi paistettu valo: vino valo, jotta kivet erottuvat myös kaukaa (pelin oma valo lisää normaalikartasta)
    L = np.array([-0.45, 0.45, 0.77]); L /= np.linalg.norm(L)
    lam = np.clip((nm * L).sum(-1), 0, 1)
    col *= (0.45 + 0.55 * ao)[..., None] * (0.55 + 0.6 * lam)[..., None]
    return np.clip(col, 0, 1), nm, ao, h
col, nm, ao, h = build()
Image.fromarray((col ** (1 / 1.0) * 255).astype(np.uint8)).save('../../rata/sepeli_a.jpg', quality=90)
Image.fromarray(((nm * 0.5 + 0.5) * 255).astype(np.uint8)).save('../../rata/sepeli_n.jpg', quality=92)
rough = np.full_like(ao, 0.92)
Image.fromarray((np.stack([ao, rough, np.zeros_like(ao)], -1) * 255).astype(np.uint8)).save('../../rata/sepeli_orm.jpg', quality=90)
# tummempi likainen versio (kiskojen väli: jarrupöly, ruoste)
Image.fromarray((np.clip(col * np.array([0.78, 0.68, 0.58]) + np.array([0.03, 0.015, 0.0]), 0, 1) * 255).astype(np.uint8)).save('../../rata/sepeli_r.jpg', quality=90)
print('ok', col.mean(axis=(0, 1)))
