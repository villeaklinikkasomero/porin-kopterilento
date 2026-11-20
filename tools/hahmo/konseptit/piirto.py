# -*- coding: utf-8 -*-
"""
Satamakaupunki - hahmokonseptien piirtokirjasto (SVG, 1960-70-luvun sarjakuvatyyli).
Kaikki mitat senttimetreina hahmon omassa koordinaatistossa: x oikealle, y alas,
paalaki y=0, lattia y=H. Piirtofunktiot palauttavat SVG-merkkijonoja.
"""
import math

INK = "#1b1712"
LW = 0.55          # aariviivan paksuus cm (skaalataan figuurin mukana)

_uid = [0]
def uid(p="c"):
    _uid[0] += 1
    return "%s%d" % (p, _uid[0])

# ---------------------------------------------------------------- apurit
def f(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")

def smooth(pts, closed=True, t=0.5):
    """Catmull-Rom -> kuutiollinen Bezier. pts: [(x,y)], piste voi olla (x,y,'c') = terava kulma."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 for p in pts]
    n = len(P)
    if n < 2:
        return ""
    d = "M%s,%s" % (f(P[0][0]), f(P[0][1]))
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        k1 = 0 if sharp[i] else t / 3.0
        k2 = 0 if sharp[(i + 1) % n] else t / 3.0
        c1 = (p1[0] + (p2[0] - p0[0]) * k1, p1[1] + (p2[1] - p0[1]) * k1)
        c2 = (p2[0] - (p3[0] - p1[0]) * k2, p2[1] - (p3[1] - p1[1]) * k2)
        d += " C%s,%s %s,%s %s,%s" % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1]))
    if closed:
        d += " Z"
    return d

def mirror(half):
    """half: pisteet oikealta puolelta ylhaalta alas (x>=0). Palauttaa koko suljetun listan."""
    left = [((-p[0],) + tuple(p[1:])) for p in reversed(half)]
    # poista keskiviivan tuplat
    out = list(half)
    for p in left:
        if abs(p[0]) < 1e-6 and any(abs(q[0]) < 1e-6 and abs(q[1] - p[1]) < 1e-6 for q in out):
            continue
        out.append(p)
    return out

def path(d, fill, lw=LW, stroke=INK, extra=""):
    if fill is None:
        fill = "none"
    s = '<path d="%s" fill="%s"' % (d, fill)
    if stroke and lw:
        s += ' stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round"' % (stroke, f(lw))
    return s + extra + "/>"

def line(pts, lw=LW, stroke=INK, closed=False, t=0.5):
    return path(smooth(pts, closed, t), None, lw, stroke)

def circle(x, y, r, fill, lw=LW, stroke=INK):
    s = '<circle cx="%s" cy="%s" r="%s" fill="%s"' % (f(x), f(y), f(r), fill)
    if lw:
        s += ' stroke="%s" stroke-width="%s"' % (stroke, f(lw))
    return s + "/>"

def ellipse(x, y, rx, ry, fill, lw=LW, stroke=INK, rot=0):
    s = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"' % (f(x), f(y), f(rx), f(ry), fill)
    if lw:
        s += ' stroke="%s" stroke-width="%s"' % (stroke, f(lw))
    if rot:
        s += ' transform="rotate(%s %s %s)"' % (f(rot), f(x), f(y))
    return s + "/>"

def g(items, tf=""):
    return "<g%s>%s</g>" % ((' transform="%s"' % tf) if tf else "", "".join(items))

def shade(hexc, k):
    """k<1 tummentaa, k>1 vaalentaa kohti valkoista."""
    h = hexc.lstrip("#")
    r, gg, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if k <= 1:
        r, gg, b = r * k, gg * k, b * k
    else:
        a = k - 1
        r, gg, b = r + (255 - r) * a, gg + (255 - gg) * a, b + (255 - b) * a
    return "#%02x%02x%02x" % (int(max(0, min(255, r))), int(max(0, min(255, gg))), int(max(0, min(255, b))))

def lin(hexc):
    """sRGB hex -> lineaarinen RGB (Blenderin Base Color)."""
    h = hexc.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(round(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4, 3))
    return out

# ---------------------------------------------------------------- mittasuhteet
class Body:
    def __init__(s, C):
        b = C["body"]
        s.H = H = C["pituus"]
        s.hh = H / b.get("paita", 7.2)            # paan korkeus
        s.hw = s.hh * b.get("paan_leveys", 0.39)   # puolikas paan leveys
        s.sh = b["hartiat"]        # hartioiden puolileveys
        s.wa = b["vyotaro"]
        s.hi = b["lantio"]
        s.belly = b.get("vatsa", 0)
        s.bust = b.get("rinta", 0)
        s.limb = b.get("raajat", 1.0)
        s.chest_d = b.get("rinta_syv", 11)
        s.back_d = b.get("selka_syv", 9)
        s.butt = b.get("takapuoli", 3)
        s.stoop = b.get("kumara", 0)
        s.neck_y = s.hh * 1.0
        s.shoulder_y = s.hh * 1.33
        s.chest_y = s.hh * 1.9
        s.waist_y = H * 0.40
        s.hip_y = H * 0.48
        s.crotch_y = H * 0.535
        s.knee_y = H * 0.725
        s.ankle_y = H * 0.955
        s.neck_w = s.hw * 0.5 * b.get("kaula", 1.0)
        s.feet_x = H * 0.055

# ---------------------------------------------------------------- paa edesta
EMO = {
    #            silma  ylaluomi kulma(sis.) kulma_nosto pupilli_dx  pupilli_dy suu
    "neutraali":  dict(eye=1.0, lid=0.0, brow_in=0.0, brow_up=0.0, px=0.0, py=0.0, mouth="neutral"),
    "iloinen":    dict(eye=0.85, lid=0.0, brow_in=-0.15, brow_up=0.12, px=0.0, py=0.0, mouth="smile"),
    "vihainen":   dict(eye=0.85, lid=0.35, brow_in=0.9, brow_up=-0.12, px=0.0, py=0.05, mouth="angry"),
    "yllattynyt": dict(eye=1.35, lid=0.0, brow_in=-0.35, brow_up=0.55, px=0.0, py=0.0, mouth="o"),
    "huolestunut":dict(eye=1.05, lid=0.0, brow_in=-0.85, brow_up=0.18, px=0.0, py=0.1, mouth="worry"),
    "ovela":      dict(eye=0.8, lid=0.55, brow_in=0.25, brow_up=0.0, px=0.22, py=0.0, mouth="smirk", brow_asym=0.5),
}
EMO_NIMI = {"neutraali": "NEUTRAALI", "iloinen": "ILOINEN", "vihainen": "VIHAINEN",
            "yllattynyt": "YLLÄTTYNYT", "huolestunut": "HUOLESTUNUT", "ovela": "OVELA"}

def head_shape(C, B):
    hw, hh = B.hw, B.hh
    fc = C["kasvot"]
    jaw, chin = fc.get("leuka", 0.78), fc.get("leuanpaa", 0.36)
    cheek = fc.get("posket", 1.0)
    half = [(0, 0), (hw * 0.72, hh * 0.07), (hw * 0.98, hh * 0.32), (hw * 0.97 * cheek, hh * 0.56),
            (hw * jaw, hh * 0.80), (hw * chin, hh * 0.965), (0, hh * 1.0)]
    return smooth(mirror(half))

def ear(C, B, side):
    hw, hh = B.hw, B.hh
    x = side * hw * 0.95
    d = smooth([(x, hh * 0.47), (x + side * hw * 0.17, hh * 0.43), (x + side * hw * 0.2, hh * 0.56),
                (x + side * hw * 0.08, hh * 0.69), (x, hh * 0.68)], closed=False)
    return path(d + " Z", C["iho"]) + line([(x + side * hw * 0.05, hh * 0.52), (x + side * hw * 0.12, hh * 0.5),
                                              (x + side * hw * 0.1, hh * 0.6)], lw=LW * 0.6)

def eye_svg(C, B, side, e, asym=0.0):
    hw, hh = B.hw, B.hh
    fc = C["kasvot"]
    cx = side * hw * 0.40
    cy = hh * 0.50
    ew = hw * 0.30 * fc.get("silmat", 1.0)
    open_ = e["eye"]
    lid = e["lid"]
    if asym and side < 0:
        lid = max(0.0, lid - asym)
    eh = hh * 0.055 * open_
    top = cy - eh * (1.0 - lid * 0.75)
    bot = cy + eh * 0.85
    d = "M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" % (
        f(cx - ew / 2), f(cy), f(cx), f(top - eh * 0.9), f(cx + ew / 2), f(cy),
        f(cx), f(bot + eh * 0.5), f(cx - ew / 2), f(cy))
    cid = uid("eye")
    pr = min(eh * 0.95, ew * 0.27)
    px = cx + e["px"] * ew * 0.35 * (1 if side > 0 else 1)
    py = cy + e["py"] * eh + eh * 0.1
    s = '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d)
    s += path(d, "#fbf8ef", lw=LW * 0.5)
    s += '<g clip-path="url(#%s)">%s%s%s</g>' % (cid, circle(px, py, pr, C.get("silmavari", "#3b5a7a"), lw=0),
                                                 circle(px, py, pr * 0.55, INK, lw=0),
                                                 circle(px + pr * 0.35, py - pr * 0.35, pr * 0.22, "#ffffff", lw=0))
    # ylaluomen paksu viiva
    s += path("M%s,%s Q%s,%s %s,%s" % (f(cx - ew / 2 - ew * 0.06), f(cy + eh * 0.1), f(cx), f(top - eh * 0.9),
                                      f(cx + ew / 2 + ew * 0.04), f(cy)), None, lw=LW * 1.25)
    if fc.get("ripset"):
        ox = cx + side * ew / 2
        s += line([(ox, cy), (ox + side * ew * 0.18, cy - eh * 0.9)], lw=LW * 0.9)
        s += line([(ox - side * ew * 0.12, cy - eh * 0.55), (ox + side * ew * 0.02, cy - eh * 1.5)], lw=LW * 0.8)
    if fc.get("silmapussit"):
        s += line([(cx - ew * 0.35, bot + eh * 0.65), (cx, bot + eh * 0.95), (cx + ew * 0.35, bot + eh * 0.65)], lw=LW * 0.5)
    return s

def brow_svg(C, B, side, e, asym=0.0):
    hw, hh = B.hw, B.hh
    fc = C["kasvot"]
    cx = side * hw * 0.40
    by = hh * 0.405 - e["brow_up"] * hh * 0.07
    if asym and side < 0:
        by -= asym * hh * 0.06
    bw = hw * 0.36
    th = hh * 0.022 * fc.get("kulmat", 1.0)
    inner = cx - side * bw / 2
    outer = cx + side * bw / 2
    di = e["brow_in"] * hh * 0.045      # + = sisapaa alas
    if asym and side < 0:
        di = -abs(di) * 0.6
    pts = [(inner, by + di), (cx, by - hh * 0.018), (outer, by + hh * 0.012)]
    top = [(x, y - th) for x, y in pts]
    d = smooth(pts + list(reversed(top)), closed=True, t=0.3)
    return path(d, C.get("kulmavari", INK), lw=LW * 0.4)

def nose_svg(C, B, e):
    hw, hh = B.hw, B.hh
    n = C["kasvot"].get("nenä", 1.0)
    typ = C["kasvot"].get("nenatyyppi", "suora")
    y0, y1 = hh * 0.5, hh * 0.69
    if typ == "perunanena":
        s = path(smooth([(-hw * 0.12 * n, y1 - hh * 0.06), (0, y1 - hh * 0.12), (hw * 0.12 * n, y1 - hh * 0.06),
                         (hw * 0.08 * n, y1 + hh * 0.02), (-hw * 0.08 * n, y1 + hh * 0.02)]), shade(C["iho"], 0.93), lw=LW * 0.7)
        return s
    if typ == "koukku":
        return line([(hw * 0.05, y0), (hw * 0.12 * n, y1 - hh * 0.02), (hw * 0.04, y1 + hh * 0.01),
                     (-hw * 0.06, y1 - hh * 0.005)], lw=LW * 0.75, t=0.4)
    return line([(hw * 0.03, y0 + hh * 0.03), (hw * 0.09 * n, y1 - hh * 0.03), (hw * 0.07 * n, y1 + hh * 0.008),
                 (-hw * 0.02, y1 + hh * 0.003)], lw=LW * 0.75, t=0.4) + \
        line([(-hw * 0.11 * n, y1 - hh * 0.012), (-hw * 0.07 * n, y1 + hh * 0.005)], lw=LW * 0.6)

def mouth_svg(C, B, e):
    hw, hh = B.hw, B.hh
    fc = C["kasvot"]
    my = hh * 0.805
    mw = hw * 0.36 * fc.get("suu", 1.0)
    lip = fc.get("huulet")
    m = e["mouth"]
    red, teeth = "#7a2420", "#fbf8ef"
    if m == "neutral":
        s = line([(-mw * 0.8, my), (0, my + hh * 0.006), (mw * 0.8, my)], lw=LW * 0.85)
        s += line([(-mw * 0.25, my + hh * 0.045), (mw * 0.25, my + hh * 0.045)], lw=LW * 0.4)
    elif m == "smile":
        d = smooth([(-mw, my - hh * 0.02, 'c'), (0, my + hh * 0.005), (mw, my - hh * 0.02, 'c'),
                    (mw * 0.45, my + hh * 0.07), (0, my + hh * 0.085), (-mw * 0.45, my + hh * 0.07)], t=0.6)
        cid = uid("m")
        s = '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d) + path(d, red, lw=0)
        s += '<g clip-path="url(#%s)"><rect x="%s" y="%s" width="%s" height="%s" fill="%s"/></g>' % (
            cid, f(-mw), f(my - hh * 0.03), f(2 * mw), f(hh * 0.035), teeth)
        s += path(d, None, lw=LW * 0.85)
        s += line([(-mw * 1.12, my - hh * 0.04), (-mw * 1.0, my - hh * 0.015)], lw=LW * 0.6)
        s += line([(mw * 1.12, my - hh * 0.04), (mw * 1.0, my - hh * 0.015)], lw=LW * 0.6)
    elif m == "angry":
        d = smooth([(-mw * 0.9, my + hh * 0.03, 'c'), (0, my - hh * 0.01), (mw * 0.9, my + hh * 0.03, 'c'),
                    (mw * 0.6, my + hh * 0.06, 'c'), (-mw * 0.6, my + hh * 0.06, 'c')], t=0.4)
        cid = uid("m")
        s = '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d) + path(d, teeth, lw=0)
        s += '<g clip-path="url(#%s)">' % cid
        for k in (-0.5, -0.17, 0.17, 0.5):
            s += line([(mw * k, my - hh * 0.02), (mw * k, my + hh * 0.08)], lw=LW * 0.4)
        s += line([(-mw, my + hh * 0.028), (mw, my + hh * 0.028)], lw=LW * 0.4) + "</g>"
        s += path(d, None, lw=LW * 0.85)
    elif m == "o":
        s = ellipse(0, my + hh * 0.025, mw * 0.32, hh * 0.05, red, lw=LW * 0.85)
    elif m == "worry":
        s = line([(-mw * 0.8, my + hh * 0.025), (-mw * 0.35, my + hh * 0.005), (mw * 0.1, my + hh * 0.022),
                  (mw * 0.5, my + hh * 0.008), (mw * 0.85, my + hh * 0.03)], lw=LW * 0.85)
    elif m == "smirk":
        s = line([(-mw * 0.7, my + hh * 0.012), (0, my + hh * 0.015), (mw * 0.6, my - hh * 0.005),
                  (mw * 0.95, my - hh * 0.035)], lw=LW * 0.9)
        s += line([(mw * 0.85, my - hh * 0.05), (mw * 1.02, my - hh * 0.02)], lw=LW * 0.55)
    if lip and m in ("neutral", "smirk", "worry"):
        s = line([(-mw * 0.7, my + hh * 0.004), (-mw * 0.2, my - hh * 0.018), (0, my - hh * 0.008),
                  (mw * 0.2, my - hh * 0.018), (mw * 0.7, my + hh * 0.004)], lw=LW * 1.6, stroke=lip) + s
    return s

def emo_extras(C, B, e, emo):
    hw, hh = B.hw, B.hh
    s = ""
    if emo == "huolestunut":
        x, y = hw * 1.02, hh * 0.28
        s += path("M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" % (f(x), f(y), f(x + hw * 0.13), f(y + hh * 0.1), f(x + hw * 0.06), f(y + hh * 0.13),
                                                        f(x - hw * 0.04), f(y + hh * 0.1), f(x), f(y)), "#bfe3ff", lw=LW * 0.6)
    if emo == "vihainen":
        x, y = -hw * 0.78, hh * 0.13
        for a in (0, 90, 180, 270):
            r = math.radians(a + 45)
            s += line([(x + math.cos(r) * hw * 0.04, y + math.sin(r) * hw * 0.04),
                       (x + math.cos(r) * hw * 0.13, y + math.sin(r) * hw * 0.13)], lw=LW * 0.9, stroke="#c0281c")
    if emo == "yllattynyt":
        for k in (-1, 0, 1):
            a = math.radians(-90 + k * 28)
            s += line([(math.cos(a) * hw * 1.3, hh * 0.45 + math.sin(a) * hh * 0.62),
                       (math.cos(a) * hw * 1.5, hh * 0.45 + math.sin(a) * hh * 0.72)], lw=LW * 0.9)
    if C["kasvot"].get("posket_puna") and emo in ("iloinen", "neutraali", "ovela"):
        for sd in (-1, 1):
            s += ellipse(sd * hw * 0.55, hh * 0.68, hw * 0.13, hh * 0.035, C["kasvot"]["posket_puna"], lw=0)
    return s

def stubble(C, B):
    hw, hh = B.hw, B.hh
    amt = C["kasvot"].get("sanki", 0)
    if not amt:
        return ""
    cid = uid("st")
    half = [(hw * 0.9, hh * 0.68), (hw * 0.7, hh * 0.87), (hw * 0.35, hh * 0.975), (0, hh * 1.0),
            (0, hh * 0.88), (hw * 0.3, hh * 0.86), (hw * 0.45, hh * 0.79), (hw * 0.7, hh * 0.72)]
    d = smooth(mirror(half), t=0.4)
    return '<path d="%s" fill="url(#stub)" opacity="%s"/>' % (d, f(0.45 * amt + 0.2))

def moustache(C, B):
    hw, hh = B.hw, B.hh
    typ = C["kasvot"].get("viikset")
    col = C["kasvot"].get("viiksivari", C["hiukset"]["vari"])
    if not typ:
        return ""
    y = hh * 0.745
    if typ == "mursu":
        half = [(0, y - hh * 0.03), (hw * 0.25, y - hh * 0.035), (hw * 0.45, y + hh * 0.01),
                (hw * 0.5, y + hh * 0.09, 'c'), (hw * 0.32, y + hh * 0.05), (hw * 0.12, y + hh * 0.055), (0, y + hh * 0.04)]
    elif typ == "kyna":
        half = [(0, y + hh * 0.005), (hw * 0.12, y - hh * 0.005), (hw * 0.33, y + hh * 0.01, 'c'),
                (hw * 0.14, y + hh * 0.014), (0, y + hh * 0.02)]
    else:  # tuuhea 70-luku
        half = [(0, y - hh * 0.02), (hw * 0.2, y - hh * 0.03), (hw * 0.38, y), (hw * 0.4, y + hh * 0.05, 'c'),
                (hw * 0.2, y + hh * 0.035), (0, y + hh * 0.03)]
    return path(smooth(mirror(half), t=0.4), col, lw=LW * 0.7)

def beard(C, B):
    hw, hh = B.hw, B.hh
    if not C["kasvot"].get("parta"):
        return ""
    col = C["kasvot"].get("viiksivari", C["hiukset"]["vari"])
    L = C["kasvot"].get("parran_pituus", 1.0)
    half = [(0, hh * 0.735), (hw * 0.35, hh * 0.72), (hw * 0.72, hh * 0.66), (hw * 0.97, hh * 0.5), (hw * 1.02, hh * 0.78),
            (hw * 0.8, hh * (1.0 + 0.08 * L)), (hw * 0.38, hh * (1.04 + 0.18 * L)), (0, hh * (1.06 + 0.2 * L))]
    s = path(smooth(mirror(half), t=0.45), col, lw=LW * 0.7)
    for k in (-0.5, -0.15, 0.2, 0.55):
        s += line([(hw * k, hh * 0.98), (hw * k * 1.05, hh * (1.0 + 0.1 * L))], lw=LW * 0.35, stroke=shade(col, 0.7))
    return s

def glasses(C, B):
    hw, hh = B.hw, B.hh
    gl = C["kasvot"].get("lasit")
    if not gl:
        return ""
    col = gl.get("vari", INK)
    r = hw * 0.2 * gl.get("koko", 1.0)
    s = ""
    for sd in (-1, 1):
        cx = sd * hw * 0.4
        if gl.get("muoto") == "pyorea":
            s += circle(cx, hh * 0.505, r, gl.get("linssi", "rgba(230,240,255,0.25)"), lw=LW * 0.9, stroke=col)
        elif gl.get("muoto") == "pilotti":
            s += path(smooth([(cx - sd * r * 1.2, hh * 0.45), (cx + sd * r * 1.25, hh * 0.45), (cx + sd * r * 1.0, hh * 0.6), (cx, hh * 0.63), (cx - sd * r * 1.1, hh * 0.56)], t=0.45),
                      gl.get("linssi", "rgba(230,240,255,0.25)"), lw=LW * 0.8, stroke=col)
        else:
            s += path(smooth([(cx - r * 1.15, hh * 0.46), (cx + r * 1.15, hh * 0.46), (cx + r, hh * 0.56), (cx - r, hh * 0.56)], t=0.25),
                      gl.get("linssi", "rgba(230,240,255,0.25)"), lw=LW * 0.9, stroke=col)
        s += line([(cx + sd * r * 1.05, hh * 0.48), (sd * hw * 0.97, hh * 0.47)], lw=LW * 0.7, stroke=col)
    s += line([(-hw * 0.4 + r, hh * 0.49), (0, hh * 0.475), (hw * 0.4 - r, hh * 0.49)], lw=LW * 0.7, stroke=col)
    if gl.get("ketju"):
        s += line([(hw * 0.97, hh * 0.48), (hw * 1.05, hh * 0.85), (hw * 0.9, hh * 1.15)], lw=LW * 0.4, stroke="#b8902a")
        s += line([(-hw * 0.97, hh * 0.48), (-hw * 1.05, hh * 0.85), (-hw * 0.9, hh * 1.15)], lw=LW * 0.4, stroke="#b8902a")
    return s

# ---------------------------------------------------------------- hiukset (edesta) -> (taka, etu)
def hair_front(C, B):
    hw, hh = B.hw, B.hh
    H = C["hiukset"]
    col, typ = H["vari"], H["tyyli"]
    dark = shade(col, 0.75)
    back, front = "", ""
    if typ == "kihara":
        # kiharapilvi: aaltoreuna
        pts = []
        n = 15
        for i in range(n + 1):
            a = math.pi * (1.0 + i / n)
            rr = 1.0 + (0.09 if i % 2 else 0.0)
            pts.append((math.cos(a) * hw * 1.1 * rr, hh * 0.40 + math.sin(a) * hh * 0.5 * rr))
        pts = pts[::-1]
        d = smooth([(hw * 1.02, hh * 0.52)] + pts[::-1][::-1] + [(-hw * 1.02, hh * 0.52)], closed=False, t=0.6)
        top = smooth([(-hw * 1.02, hh * 0.52), (-hw * 0.95, hh * 0.38), (-hw * 0.6, hh * 0.24), (-hw * 0.2, hh * 0.27),
                      (hw * 0.15, hh * 0.22), (hw * 0.55, hh * 0.27), (hw * 0.92, hh * 0.36), (hw * 1.02, hh * 0.52)], closed=False)
        back = path(smooth([(hw * 1.05, hh * 0.6)] + pts + [(-hw * 1.05, hh * 0.6)], closed=True, t=0.6), col)
        fr = [(-hw * 1.02, hh * 0.52), (-hw * 1.08, hh * 0.3), (-hw * 0.9, hh * 0.05), (-hw * 0.5, -hh * 0.08),
              (0, -hh * 0.12), (hw * 0.5, -hh * 0.08), (hw * 0.95, hh * 0.06), (hw * 1.08, hh * 0.3), (hw * 1.02, hh * 0.52),
              (hw * 0.9, hh * 0.33), (hw * 0.6, hh * 0.22), (hw * 0.3, hh * 0.26), (0, hh * 0.2), (-hw * 0.3, hh * 0.25),
              (-hw * 0.6, hh * 0.21), (-hw * 0.9, hh * 0.32)]
        front = path(smooth(fr, t=0.55), col)
        for (x, y) in [(-0.6, 0.02), (-0.2, -0.05), (0.25, -0.03), (0.65, 0.05), (-0.85, 0.2), (0.85, 0.2), (0, 0.1), (-0.4, 0.13), (0.45, 0.14)]:
            front += path("M%s,%s q%s,%s %s,%s" % (f(hw * x - hw * 0.08), f(hh * y + hh * 0.05), f(hw * 0.08), f(-hh * 0.06), f(hw * 0.16), f(0)),
                          None, lw=LW * 0.5, stroke=dark)
    elif typ == "kalju_sivut":
        side = [(hw * 0.98, hh * 0.25), (hw * 1.1, hh * 0.32), (hw * 1.14, hh * 0.5), (hw * 1.02, hh * 0.62), (hw * 0.94, hh * 0.5)]
        for sd in (1, -1):
            front += path(smooth([(sd * x, y) for x, y in side]), col)
            # pulisongit
            front += path(smooth([(sd * hw * 0.95, hh * 0.5), (sd * hw * 1.0, hh * 0.52), (sd * hw * 0.97, hh * 0.74),
                                  (sd * hw * 0.88, hh * 0.72)]), col)
        # kiiltava kalju
        front += path("M%s,%s q%s,%s %s,%s" % (f(-hw * 0.45), f(hh * 0.12), f(hw * 0.2), f(-hh * 0.08), f(hw * 0.45), f(-hh * 0.06)),
                      None, lw=LW * 0.9, stroke="#ffffff")
        front += line([(-hw * 0.3, hh * 0.3), (0, hh * 0.28), (hw * 0.3, hh * 0.3)], lw=LW * 0.4)
    elif typ == "polkka":
        streak = H.get("raita")
        back = path(smooth([(hw * 1.18, hh * 0.85, 'c'), (hw * 1.25, hh * 0.3), (hw * 0.8, -hh * 0.08), (0, -hh * 0.13),
                            (-hw * 0.8, -hh * 0.08), (-hw * 1.25, hh * 0.3), (-hw * 1.15, hh * 0.78, 'c')], t=0.55), col)
        fr = [(-hw * 1.15, hh * 0.78, 'c'), (-hw * 1.2, hh * 0.3), (-hw * 0.8, -hh * 0.06), (0, -hh * 0.11), (hw * 0.8, -hh * 0.06),
              (hw * 1.2, hh * 0.3), (hw * 1.18, hh * 0.85, 'c'), (hw * 0.95, hh * 0.62), (hw * 0.9, hh * 0.35),
              (hw * 0.6, hh * 0.36, 'c'), (hw * 0.1, hh * 0.32), (-hw * 0.5, hh * 0.38, 'c'), (-hw * 0.85, hh * 0.36), (-hw * 0.95, hh * 0.6)]
        front = path(smooth(fr, t=0.5), col)
        if streak:
            front += path(smooth([(hw * 0.25, -hh * 0.1), (hw * 0.55, -hh * 0.06), (hw * 0.75, hh * 0.33, 'c'), (hw * 0.45, hh * 0.35, 'c'),
                                  (hw * 0.3, hh * 0.1)], t=0.5), streak, lw=LW * 0.5)
        front += line([(-hw * 0.2, hh * 0.0), (-hw * 0.45, hh * 0.3)], lw=LW * 0.4, stroke=dark)
    elif typ == "nuttura":
        back = circle(0, -hh * 0.1, hw * 0.48, col) + line([(-hw * 0.3, -hh * 0.12), (hw * 0.3, -hh * 0.06)], lw=LW * 0.4, stroke=dark)
        fr = [(-hw * 1.02, hh * 0.55), (-hw * 1.1, hh * 0.25), (-hw * 0.7, -hh * 0.04), (0, -hh * 0.06), (hw * 0.7, -hh * 0.04),
              (hw * 1.1, hh * 0.25), (hw * 1.02, hh * 0.55), (hw * 0.88, hh * 0.3), (hw * 0.4, hh * 0.18), (0, hh * 0.12, 'c'),
              (-hw * 0.4, hh * 0.18), (-hw * 0.88, hh * 0.3)]
        front = path(smooth(fr, t=0.5), col)
        for k in (-0.6, -0.3, 0.3, 0.6):
            front += line([(0, hh * 0.1), (hw * k, hh * 0.03), (hw * k * 1.55, hh * 0.25)], lw=LW * 0.35, stroke=dark)
    elif typ == "sivuhiukset_lakki":
        for sd in (1, -1):
            front += path(smooth([(sd * hw * 0.9, hh * 0.22), (sd * hw * 1.1, hh * 0.3), (sd * hw * 1.08, hh * 0.55),
                                  (sd * hw * 0.95, hh * 0.55)]), col)
    elif typ == "liukas":
        temple = H.get("ohimot", col)
        back = path(smooth([(hw * 1.04, hh * 0.55), (hw * 1.1, hh * 0.2), (hw * 0.7, -hh * 0.07), (0, -hh * 0.1), (-hw * 0.7, -hh * 0.07),
                            (-hw * 1.1, hh * 0.2), (-hw * 1.04, hh * 0.55)], t=0.5), col)
        fr = [(-hw * 1.02, hh * 0.5), (-hw * 1.08, hh * 0.2), (-hw * 0.7, -hh * 0.06), (0, -hh * 0.09), (hw * 0.7, -hh * 0.06),
              (hw * 1.08, hh * 0.2), (hw * 1.02, hh * 0.5), (hw * 0.92, hh * 0.25), (hw * 0.5, hh * 0.17), (hw * 0.15, hh * 0.15),
              (0, hh * 0.25, 'c'), (-hw * 0.15, hh * 0.15), (-hw * 0.5, hh * 0.17), (-hw * 0.92, hh * 0.25)]
        front = path(smooth(fr, t=0.45), col)
        for sd in (1, -1):
            front += path(smooth([(sd * hw * 0.93, hh * 0.25), (sd * hw * 1.07, hh * 0.25), (sd * hw * 1.03, hh * 0.5), (sd * hw * 0.95, hh * 0.48)]),
                          temple, lw=LW * 0.4)
        for k in (-0.5, -0.2, 0.2, 0.5):
            front += line([(hw * k * 0.4, hh * 0.13), (hw * k, -hh * 0.03), (hw * k * 1.7, hh * 0.15)], lw=LW * 0.4, stroke=shade(col, 1.6))
    elif typ == "sivukampaus":
        fr = [(-hw * 1.02, hh * 0.5), (-hw * 1.07, hh * 0.25), (-hw * 0.8, hh * 0.05), (-hw * 0.3, -hh * 0.03), (hw * 0.4, -hh * 0.04),
              (hw * 0.95, hh * 0.08), (hw * 1.08, hh * 0.28), (hw * 1.02, hh * 0.5), (hw * 0.92, hh * 0.25), (hw * 0.3, hh * 0.16),
              (-hw * 0.5, hh * 0.13), (-hw * 0.92, hh * 0.27)]
        front = path(smooth(fr, t=0.45), col)
        for k in (0.2, 0.0, -0.2):
            front += line([(-hw * 0.6, hh * (0.08 + k * 0.1)), (hw * 0.2, hh * (0.02 + k * 0.12)), (hw * 0.85, hh * (0.12 + k * 0.08))],
                          lw=LW * 0.35, stroke=dark)
    elif typ == "foni":
        back = path(smooth([(hw * 1.12, hh * 0.62), (hw * 1.2, hh * 0.15), (hw * 0.8, -hh * 0.2), (0, -hh * 0.26), (-hw * 0.8, -hh * 0.2),
                            (-hw * 1.2, hh * 0.15), (-hw * 1.12, hh * 0.62)], t=0.5), col)
        fr = [(-hw * 1.05, hh * 0.5), (-hw * 1.14, hh * 0.15), (-hw * 0.85, -hh * 0.16), (-hw * 0.2, -hh * 0.27), (hw * 0.5, -hh * 0.22),
              (hw * 1.05, -hh * 0.02), (hw * 1.12, hh * 0.3), (hw * 1.03, hh * 0.5), (hw * 0.9, hh * 0.24), (hw * 0.4, hh * 0.13),
              (-hw * 0.3, hh * 0.1), (-hw * 0.9, hh * 0.26)]
        front = path(smooth(fr, t=0.5), col)
        for sd in (1, -1):
            front += path(smooth([(sd * hw * 0.93, hh * 0.4), (sd * hw * 1.04, hh * 0.42), (sd * hw * 1.0, hh * 0.8, 'c'), (sd * hw * 0.88, hh * 0.76, 'c')], t=0.4), col)
        for k in (-0.1, 0.05, 0.2):
            front += line([(-hw * 0.8, hh * (0.05 + k * 0.4)), (-hw * 0.1, -hh * (0.12 - k * 0.6)), (hw * 0.75, hh * (0.0 + k * 0.5))], lw=LW * 0.45, stroke=dark)
    elif typ == "lyhyt":
        fr = [(-hw * 1.01, hh * 0.45), (-hw * 1.05, hh * 0.2), (-hw * 0.7, -hh * 0.03), (0, -hh * 0.06), (hw * 0.7, -hh * 0.03),
              (hw * 1.05, hh * 0.2), (hw * 1.01, hh * 0.45), (hw * 0.9, hh * 0.25), (hw * 0.4, hh * 0.18), (0, hh * 0.2),
              (-hw * 0.4, hh * 0.18), (-hw * 0.9, hh * 0.25)]
        front = path(smooth(fr, t=0.5), col)
        if H.get("ohimot"):
            for sd in (1, -1):
                front += path(smooth([(sd * hw * 0.92, hh * 0.24), (sd * hw * 1.04, hh * 0.24), (sd * hw * 1.01, hh * 0.46), (sd * hw * 0.94, hh * 0.44)]),
                              H["ohimot"], lw=LW * 0.4)
    return back, front

def hat_front(C, B):
    hw, hh = B.hw, B.hh
    h = C.get("paahine")
    if not h:
        return ""
    typ, col = h["tyyppi"], h["vari"]
    s = ""
    if typ in ("kapteeni", "vartija"):
        top = h.get("kupu", col)
        # kupu
        s += path(smooth([(-hw * 1.18, hh * 0.1), (-hw * 1.1, -hh * 0.04), (0, -hh * 0.09), (hw * 1.1, -hh * 0.04), (hw * 1.18, hh * 0.1),
                          (hw * 1.0, hh * 0.2, 'c'), (-hw * 1.0, hh * 0.2, 'c')], t=0.5), top)
        # nauha
        s += path(smooth([(-hw * 1.0, hh * 0.12, 'c'), (hw * 1.0, hh * 0.12, 'c'), (hw * 1.02, hh * 0.28, 'c'), (-hw * 1.02, hh * 0.28, 'c')]),
                  h.get("nauha", INK))
        # lippa
        s += path(smooth([(-hw * 0.95, hh * 0.27, 'c'), (hw * 0.95, hh * 0.27, 'c'), (hw * 0.7, hh * 0.37), (0, hh * 0.4), (-hw * 0.7, hh * 0.37)], t=0.5),
                  INK, lw=LW * 0.6)
        s += path("M%s,%s q%s,%s %s,%s" % (f(-hw * 0.5), f(hh * 0.33), f(hw * 0.5), f(hh * 0.04), f(hw * 1.0), f(0)), None, lw=LW * 0.7, stroke="#55606a")
        badge = h.get("merkki")
        if badge:
            s += circle(0, hh * 0.05, hw * 0.15, badge.get("vari", "#d9b13b"), lw=LW * 0.6)
            if badge.get("teksti"):
                s += '<text x="0" y="%s" font-family="Archivo Black" font-size="%s" text-anchor="middle" fill="%s">%s</text>' % (
                    f(hh * 0.05 + hw * 0.09), f(hw * 0.24), "#ffffff", badge["teksti"])
        if typ == "kapteeni":
            s += line([(-hw * 0.6, hh * 0.25), (hw * 0.6, hh * 0.25)], lw=LW * 0.8, stroke="#d9b13b")
    elif typ == "pipo":
        s += path(smooth([(-hw * 1.1, hh * 0.28, 'c'), (-hw * 1.16, hh * 0.05), (-hw * 0.85, -hh * 0.1), (-hw * 0.2, -hh * 0.16), (hw * 0.55, -hh * 0.14),
                          (hw * 1.05, -hh * 0.03), (hw * 1.1, hh * 0.28, 'c')], t=0.55), col)
        for k in range(-4, 5):
            s += line([(hw * k * 0.22, hh * 0.18), (hw * k * 0.2, -hh * 0.06)], lw=LW * 0.35, stroke=shade(col, 0.78))
        s += path(smooth([(-hw * 1.13, hh * 0.18, 'c'), (hw * 1.13, hh * 0.18, 'c'), (hw * 1.11, hh * 0.33, 'c'), (-hw * 1.11, hh * 0.33, 'c')], t=0.3),
                  h.get("kaanne", col))
        for k in range(-9, 10):
            s += line([(hw * k * 0.115, hh * 0.2), (hw * k * 0.115, hh * 0.31)], lw=LW * 0.3, stroke=shade(col, 0.75))
    elif typ == "lippis":
        s += path(smooth([(-hw * 1.08, hh * 0.28, 'c'), (-hw * 1.05, hh * 0.0), (-hw * 0.6, -hh * 0.12), (0, -hh * 0.15), (hw * 0.6, -hh * 0.12),
                          (hw * 1.05, hh * 0.0), (hw * 1.08, hh * 0.28, 'c')], t=0.5), col)
        s += line([(0, -hh * 0.15), (0, hh * 0.2)], lw=LW * 0.4)
        s += circle(0, -hh * 0.15, hw * 0.06, col, lw=LW * 0.5)
        s += path(smooth([(-hw * 1.05, hh * 0.26, 'c'), (hw * 1.05, hh * 0.26, 'c'), (hw * 0.8, hh * 0.42), (0, hh * 0.47), (-hw * 0.8, hh * 0.42)], t=0.5),
                  h.get("lippa", shade(col, 0.7)))
        if h.get("logo"):
            s += '<text x="0" y="%s" font-family="Archivo Black" font-size="%s" text-anchor="middle" fill="%s">%s</text>' % (
                f(hh * 0.18), f(hw * 0.3), h.get("logovari", "#ffffff"), h["logo"])
    return s

def head_front(C, B, emo="neutraali", body_mode=False):
    """Koko paa edesta (origo paalaki-keskella)."""
    e = EMO[emo]
    asym = e.get("brow_asym", 0.0)
    hb, hf = hair_front(C, B)
    s = hb
    s += ear(C, B, 1) + ear(C, B, -1)
    s += path(head_shape(C, B), C["iho"])
    # varjo leuan alla / kasvojen oikea puoli
    s += stubble(C, B)
    s += emo_extras(C, B, e, emo)
    s += beard(C, B)
    for sd in (1, -1):
        s += eye_svg(C, B, sd, e, asym)
    s += nose_svg(C, B, e)
    s += moustache(C, B)
    s += mouth_svg(C, B, e)
    if C["kasvot"].get("pisamat"):
        for (x, y) in [(-0.55, 0.62), (-0.45, 0.66), (-0.62, 0.68), (0.55, 0.62), (0.45, 0.66), (0.62, 0.68), (-0.1, 0.6), (0.1, 0.6)]:
            s += circle(B.hw * x, B.hh * y, B.hw * 0.018, shade(C["iho"], 0.7), lw=0)
    s += hf
    for sd in (1, -1):
        s += brow_svg(C, B, sd, e, asym)
    s += glasses(C, B)
    s += hat_front(C, B)
    return s
