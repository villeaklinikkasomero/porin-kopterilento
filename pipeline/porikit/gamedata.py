"""Read the game's own data files (city.js, lod2.js) so the pipeline speaks in the game's building indices."""
from __future__ import annotations
import json, math, os, re
from functools import lru_cache

GAME = os.environ.get('PORI_GAME', os.path.join(os.path.dirname(__file__), '..', '..'))   # repo root with index.html


def _load_js_object(path: str):
    s = open(path, encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


@lru_cache(None)
def city():
    return _load_js_object(os.path.join(GAME, 'city.js'))


@lru_cache(None)
def lod2():
    return _load_js_object(os.path.join(GAME, 'lod2.js'))


def footprint(i: int):
    p = city()['b'][i]['p']; return [(p[k] / 10, p[k + 1] / 10) for k in range(0, len(p), 2)]


def eave(i: int) -> float | None:
    b = lod2()['b'].get(str(i))
    if b: return float(b.get('e') or b.get('h'))
    h = city()['b'][i].get('h'); return float(h) if h else None


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def street_names():
    return sorted({r['n'] for r in city()['r'] if r.get('n')})


def guess_street(filename: str):
    """'Keskusta 23 Katariinakatu.jpg' -> 'Katariinankatu' (tolerates the photographers' spellings)."""
    stop = {'keskusta', 'kesäinen', 'päiväkoti', 'koulu', 'osa'}
    words = [w for w in re.findall(r'[A-Za-zÅÄÖåäö\-]{5,}', filename) if w.lower() not in stop]
    names = street_names(); best, bs = None, 0
    for w in words:
        wl = w.lower()
        for n in names:
            nl = n.lower(); common = os.path.commonprefix([wl, nl])
            sc = len(common) / max(len(nl), 1)
            if len(common) >= 5 and sc > bs: best, bs = n, sc
    return best


def buildings_near_street(name: str, dist: float = 45.0, limit: int = 60):
    """Building indices whose footprint comes within dist metres of the named street, nearest first."""
    segs = []
    for r in city()['r']:
        if r.get('n') != name: continue
        p = r['p']
        for k in range(0, len(p) - 3, 2): segs.append((p[k], p[k + 1], p[k + 2], p[k + 3]))
    out = []
    for i, b in enumerate(city()['b']):
        pts = footprint(i); cx = sum(x for x, _ in pts) / len(pts); cy = sum(y for _, y in pts) / len(pts)
        d = min((_seg_dist(cx, cy, *s) for s in segs), default=1e9)
        if d < dist + 25: out.append((d, i))
    out.sort(); return [i for _, i in out[:limit]], segs
