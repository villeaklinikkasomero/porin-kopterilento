# -*- coding: utf-8 -*-
"""Vartalo ja vaatteet edesta ja sivulta (A-asento mallinnusta varten)."""
import math
from piirto import *

ARM_ANGLE = 17.0   # astetta pystysta, A-asento

def vt(C, key, default=None):
    return C["vaatteet"].get(key, default)

def limb_outline(pts, widths):
    """pts: keskiviivan pisteet, widths: puolileveydet -> suljettu aariviiva."""
    L, R = [], []
    n = len(pts)
    for i, (p, w) in enumerate(zip(pts, widths)):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((p[0] + nx * w, p[1] + ny * w))
        R.append((p[0] - nx * w, p[1] - ny * w))
    return L + list(reversed(R))

def arm_geom(B, side, ang=ARM_ANGLE):
    a = math.radians(ang)
    dx, dy = math.sin(a) * side, math.cos(a)
    J = (side * (B.sh - 3.0), B.shoulder_y + 3.5)
    up, fo, ha = B.H * 0.172, B.H * 0.148, B.H * 0.105
    E = (J[0] + dx * up, J[1] + dy * up)
    a2 = math.radians(ang - 4)
    dx2, dy2 = math.sin(a2) * side, math.cos(a2)
    W = (E[0] + dx2 * fo, E[1] + dy2 * fo)
    return J, E, W, (dx2, dy2), ha

def sleeve_outline(B, side, pts, widths):
    """Hiha, jonka ylapaa seuraa olkapaan linjaa (ei laatikkomaista olkaa)."""
    L, R = [], []
    n = len(pts)
    for i, (p, w) in enumerate(zip(pts, widths)):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((p[0] + nx * w, p[1] + ny * w))
        R.append((p[0] - nx * w, p[1] - ny * w))
    outer, inner = (R, L) if side > 0 else (L, R)
    # outer = olkapaan puoli, inner = kainalon puoli
    cap = [(side * B.sh * 0.66, B.shoulder_y - 1.0), (side * (B.sh + 0.6), B.shoulder_y + 1.2)]
    pit = [(side * (B.sh - 5.5), B.shoulder_y + 10)]
    return cap + outer[1:] + list(reversed(inner)) + pit

def arm_front(C, B, side):
    J, E, W, d, ha = arm_geom(B, side)
    k = B.limb
    top = vt(C, "ylä")
    sleeve = top.get("hiha", "pitka")
    coat = vt(C, "takki")
    if coat and coat.get("hiha", True):
        sleeve = "pitka"
    scol = coat["vari"] if (coat and coat.get("hiha", True)) else top["vari"]
    mid1 = ((J[0] + E[0]) / 2, (J[1] + E[1]) / 2)
    mid2 = ((E[0] + W[0]) / 2, (E[1] + W[1]) / 2)
    wd = [5.6 * k, 4.6 * k, 4.1 * k, 3.6 * k, 2.6 * k]
    if sleeve == "lyhyt":
        s = path(smooth(limb_outline([J, mid1, E, mid2, W], wd), t=0.5), C["iho"])
    else:
        s = path(smooth(limb_outline([E, mid2, W], wd[2:]), t=0.5), C["iho"])
    # hiha
    if sleeve == "lyhyt":
        Sx = (J[0] + (E[0] - J[0]) * 0.45, J[1] + (E[1] - J[1]) * 0.45)
        s += path(smooth(sleeve_outline(B, side, [J, Sx], [6.6 * k, 6.0 * k]), t=0.4), scol)
    else:
        ext = 1.0
        Wc = (W[0] - d[0] * 1.0, W[1] - d[1] * 1.0)
        s += path(smooth(sleeve_outline(B, side, [J, mid1, E, mid2, Wc], [6.4 * k, 5.6 * k, 5.0 * k, 4.6 * k, 4.3 * k]), t=0.45), scol)
        cuff = top.get("kalvosin")
        if cuff:
            C1 = (Wc[0] - d[0] * 2.5, Wc[1] - d[1] * 2.5)
            s += path(smooth(limb_outline([C1, Wc], [4.5 * k, 4.4 * k]), t=0.2), cuff)
        # ryppy kyynarpaassa
        s += line([(E[0] - side * 3, E[1] - 1), (E[0] + side * 0.5, E[1] + 1.5)], lw=LW * 0.4)
    s += hand_front(C, B, W, d, ha, side)
    return s

def hand_front(C, B, W, d, ha, side):
    k = B.limb
    gl = C["vaatteet"].get("hanskat")
    col = gl if gl else C["iho"]
    nx, ny = -d[1], d[0]
    P = lambda t, o: (W[0] + d[0] * t + nx * o * side, W[1] + d[1] * t + ny * o * side)
    pts = [P(-0.5, 3.0 * k), P(ha * 0.35, 4.0 * k), P(ha * 0.75, 3.6 * k), P(ha * 1.0, 1.5 * k), P(ha * 0.98, -1.8 * k),
           P(ha * 0.6, -3.4 * k), P(ha * 0.2, -3.1 * k), P(-0.5, -2.8 * k)]
    s = path(smooth(pts, t=0.5), col)
    th = [P(ha * 0.15, -2.6 * k), P(ha * 0.38, -4.6 * k), P(ha * 0.58, -4.3 * k), P(ha * 0.45, -2.6 * k)]
    s += path(smooth(th, t=0.5), col, lw=LW * 0.8)
    for o in (1.6, 0.0):
        s += line([P(ha * 0.62, o * k), P(ha * 0.88, o * k * 0.8)], lw=LW * 0.35)
    return s

def torso_half(C, B, hem_y, extra=0.0, flare=0.0):
    sh, wa, hi = B.sh + extra, B.wa + B.belly + extra, B.hi + extra
    bust = B.bust
    half = [(0, B.hh * 1.06), (B.neck_w * 1.05 + extra, B.hh * 1.02), (sh * 0.78, B.shoulder_y - 0.5),
            (sh, B.shoulder_y + 2.5), (sh - 0.5, B.chest_y - 2), (max(sh - 2.5, wa) + bust * 0.6, B.chest_y + 4)]
    if B.belly > 3:
        half.append((wa + 0.5, (B.chest_y + B.waist_y) / 2 + 4))
    half.append((wa, B.waist_y))
    if hem_y > B.waist_y + 4:
        half.append((hi + (flare * (min(hem_y, B.hip_y) - B.waist_y) / max(1, hem_y - B.waist_y)), min(hem_y - 0.5, B.hip_y)))
    if hem_y > B.hip_y + 4:
        half.append((hi + flare, hem_y, 'c'))
    else:
        half[-1] = (half[-1][0], hem_y, 'c')
    half.append((0, hem_y))
    return half

def legs_front(C, B):
    """Paljaat/sukkahousujalat (piirretaan aina housujen alle)."""
    col = vt(C, "sukat", C["iho"])
    k = B.limb
    s = ""
    for sd in (1, -1):
        hip = (sd * B.hi * 0.5, B.crotch_y - 6)
        knee = (sd * (B.hi * 0.5 + B.feet_x) / 2 * 0.95, B.knee_y)
        ank = (sd * B.feet_x, B.ankle_y)
        calf = ((knee[0] + ank[0]) / 2, (knee[1] + ank[1]) / 2 - 6)
        s += path(smooth(limb_outline([hip, knee, calf, ank], [7.5 * k, 5.0 * k, 5.6 * k, 3.4 * k]), t=0.5), col)
    return s

def pants_front(C, B):
    a = vt(C, "ala")
    col = a["vari"]
    typ = a.get("tyyppi", "housut")
    k = B.limb
    if typ == "hame":
        hem = B.knee_y + a.get("pituus", 6)
        half = [(0, B.waist_y), (B.wa + B.belly * 0.5, B.waist_y), (B.hi + 1, B.hip_y), (B.hi + 7, hem, 'c'), (0, hem)]
        s = path(smooth(mirror(half), t=0.4), col)
        for x in (-0.6, -0.2, 0.2, 0.6):
            s += line([(B.hi * x * 0.6, B.hip_y + 4), (B.hi * x * 1.1, hem - 1)], lw=LW * 0.4)
        return s
    hem_y = B.ankle_y + 1.5 if typ != "shortsit" else B.knee_y - 7
    flare = a.get("levennys", 0.0)
    ank_o = B.feet_x + 4.2 * k + flare
    ank_i = B.feet_x - 4.0 * k - flare * 0.6
    if typ == "shortsit":
        ank_o = (B.hi + B.feet_x) / 2 + 6.5 * k
        ank_i = (B.hi * 0.5 + B.feet_x) / 2 - 5.5 * k
    kx = (B.hi * 0.5 + B.feet_x) / 2 * 0.95
    half = [(0, B.waist_y), (B.wa + B.belly * 0.4 + 0.5, B.waist_y), (B.hi + 0.5, B.hip_y), (B.hi * 0.5 + 8.2 * k, B.crotch_y + 2)]
    if typ != "shortsit":
        half += [(kx + 6.0 * k + flare * 0.2, B.knee_y), (ank_o, hem_y, 'c'), (ank_i, hem_y, 'c'), (kx - 5.4 * k, B.knee_y)]
    else:
        half += [(ank_o, hem_y, 'c'), (ank_i, hem_y, 'c')]
    half += [(1.0, B.crotch_y + 1, 'c'), (0, B.crotch_y)]
    s = path(smooth(mirror(half), t=0.45), col)
    # sivu- ja polvirypyt, saumat
    if a.get("sauma"):
        for sd in (1, -1):
            s += line([(sd * (B.hi * 0.5 + 6.5 * k), B.crotch_y + 3), (sd * (kx + 4.5), B.knee_y), (sd * (ank_o - 1.8), hem_y - 1)],
                      lw=LW * 0.4, stroke=a["sauma"])
    for sd in (1, -1):
        s += line([(sd * (kx - 2), B.knee_y - 2), (sd * (kx + 2.5), B.knee_y - 3)], lw=LW * 0.35)
    if a.get("taskut") == "cargo":
        for sd in (1, -1):
            x0 = sd * (B.hi * 0.5 + 6.5 * k)
            s += path(smooth([(x0 - sd * 0.5, B.crotch_y + 8, 'c'), (x0 + sd * 2.5, B.crotch_y + 8, 'c'),
                              (x0 + sd * 2.2, B.crotch_y + 22, 'c'), (x0 - sd * 1.2, B.crotch_y + 22, 'c')]), shade(col, 0.9), lw=LW * 0.5)
    if a.get("vyo"):
        s += path(smooth([(-B.wa - B.belly * 0.4 - 0.5, B.waist_y, 'c'), (B.wa + B.belly * 0.4 + 0.5, B.waist_y, 'c'),
                          (B.wa + B.belly * 0.4 + 0.7, B.waist_y + 3.2, 'c'), (-B.wa - B.belly * 0.4 - 0.7, B.waist_y + 3.2, 'c')]), a["vyo"], lw=LW * 0.6)
        s += '<rect x="-2.6" y="%s" width="5.2" height="4" fill="%s" stroke="%s" stroke-width="%s" rx="0.6"/>' % (
            f(B.waist_y - 0.4), a.get("solki", "#c9a640"), INK, f(LW * 0.6))
    s += line([(0, B.waist_y + 3), (0, B.crotch_y - 2)], lw=LW * 0.35)
    return s

def shoes_front(C, B):
    sk = vt(C, "kengat")
    col, sole = sk["vari"], sk.get("pohja", "#555555")
    typ = sk.get("tyyppi", "kenka")
    s = ""
    for sd in (1, -1):
        x = sd * (B.feet_x + 0.8)
        top = B.ankle_y - (12 if typ == "saapas" else 20 if typ == "kumisaapas" else 1.5)
        w = 4.6 if typ != "kumisaapas" else 5.2
        pts = [(x - w, top, 'c'), (x + w, top, 'c'), (x + w + 0.6, B.H - 4), (x + sd * 2 + 5.0, B.H - 0.8, 'c'),
               (x + sd * 2 - 5.0, B.H - 0.8, 'c'), (x - w - 0.6, B.H - 4)]
        s += path(smooth(pts, t=0.45), col)
        s += path(smooth([(x + sd * 2 - 5.2, B.H - 1.6, 'c'), (x + sd * 2 + 5.2, B.H - 1.6, 'c'), (x + sd * 2 + 5.3, B.H, 'c'),
                          (x + sd * 2 - 5.3, B.H, 'c')]), sole, lw=LW * 0.6)
        if sk.get("raidat"):
            s += line([(x - 3, B.H - 6), (x + 2, B.H - 3.5)], lw=LW * 1.2, stroke=sk["raidat"])
        if typ == "lenkkari":
            s += line([(x - 2.3, B.ankle_y + 1.5), (x + 2.3, B.ankle_y + 1.5)], lw=LW * 0.4)
            s += line([(x - 2.0, B.ankle_y + 3.2), (x + 2.0, B.ankle_y + 3.2)], lw=LW * 0.4)
    return s

def collar_front(C, B, typ, col):
    nw = B.neck_w
    y = B.hh * 1.02
    if typ == "poolo":
        return path(smooth([(-nw * 1.2, y - 4.5, 'c'), (nw * 1.2, y - 4.5, 'c'), (nw * 1.35, y + 3.0, 'c'), (-nw * 1.35, y + 3.0, 'c')], t=0.3), col) + \
            line([(-nw * 1.2, y - 1), (nw * 1.2, y - 1)], lw=LW * 0.4) + line([(-nw * 1.25, y + 1), (nw * 1.25, y + 1)], lw=LW * 0.4)
    if typ == "pyorea":
        return line([(-nw * 1.05, y - 0.3), (0, y + 3.2), (nw * 1.05, y - 0.3)], lw=LW * 0.7) + \
            line([(-nw * 0.95, y + 1.3), (0, y + 4.6), (nw * 0.95, y + 1.3)], lw=LW * 0.4)
    if typ == "paita":
        s = ""
        for sd in (1, -1):
            s += path(smooth([(0, y + 4, 'c'), (sd * nw * 1.05, y - 2.5, 'c'), (sd * nw * 1.45, y + 1.0, 'c'), (sd * nw * 0.9, y + 7, 'c')]), col, lw=LW * 0.7)
        return s
    if typ == "pysty":
        return path(smooth([(-nw * 1.3, y - 5.5, 'c'), (nw * 1.3, y - 5.5, 'c'), (nw * 1.45, y + 2.5, 'c'), (-nw * 1.45, y + 2.5, 'c')], t=0.3), col)
    if typ == "vpaanta":
        return path(smooth([(-nw * 1.05, y - 0.5, 'c'), (0, y + 9, 'c'), (nw * 1.05, y - 0.5, 'c')], closed=False), None, lw=LW * 0.7)
    return ""

def top_front(C, B):
    t = vt(C, "ylä")
    col = t["vari"]
    hem = {"lantio": B.hip_y + 3, "vyotaro": B.waist_y + 1, "haara": B.crotch_y}.get(t.get("helma", "lantio"), B.hip_y + 3)
    if vt(C, "ala", {}).get("tyyppi") in ("haalari",):
        hem = B.waist_y + 1
    s = path(smooth(mirror(torso_half(C, B, hem)), t=0.45), col)
    pat = t.get("kuvio")
    if pat == "ruutu":
        cid = uid("tc")
        s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (cid, smooth(mirror(torso_half(C, B, hem)), t=0.45), cid)
        for i in range(-12, 13):
            x = i * 4.5
            s += line([(x, B.hh), (x, hem + 2)], lw=LW * 0.9, stroke=t["vari2"])
        for j in range(0, 30):
            yy = B.hh + j * 4.5
            s += line([(-40, yy), (40, yy)], lw=LW * 0.9, stroke=t["vari2"])
        s += "</g>" + path(smooth(mirror(torso_half(C, B, hem)), t=0.45), None)
    if pat == "raita":
        cid = uid("tc")
        s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (cid, smooth(mirror(torso_half(C, B, hem)), t=0.45), cid)
        for j in range(0, 14):
            yy = B.shoulder_y + 6 + j * 6
            s += '<rect x="-40" y="%s" width="80" height="2.6" fill="%s"/>' % (f(yy), t["vari2"])
        s += "</g>" + path(smooth(mirror(torso_half(C, B, hem)), t=0.45), None)
    s += collar_front(C, B, t.get("kaulus", "pyorea"), t.get("kaulusvari", col))
    if t.get("vetoketju"):
        s += line([(0, B.hh * 1.06), (0, hem)], lw=LW * 0.5) + circle(0, B.hh * 1.06 + 7, 0.7, "#c0c0c0", lw=LW * 0.4)
    if t.get("rintatasku"):
        x = -B.sh * 0.45
        s += path(smooth([(x - 4, B.chest_y - 6, 'c'), (x + 4, B.chest_y - 6, 'c'), (x + 4, B.chest_y + 2, 'c'), (x - 4, B.chest_y + 2, 'c')]),
                  shade(col, 0.92), lw=LW * 0.5)
        if t.get("taskuteksti"):
            s += '<text x="%s" y="%s" font-family="Archivo Black" font-size="2.2" text-anchor="middle" fill="%s">%s</text>' % (
                f(x), f(B.chest_y - 1.5), t.get("taskutekstivari", INK), t["taskuteksti"])
    if t.get("logo"):
        lg = t["logo"]
        s += circle(B.sh * 0.42, B.chest_y - 3, 3.4, lg.get("vari", "#ffffff"), lw=LW * 0.5)
        s += '<text x="%s" y="%s" font-family="Archivo Black" font-size="4" text-anchor="middle" fill="%s">%s</text>' % (
            f(B.sh * 0.42), f(B.chest_y - 1.6), lg.get("tekstivari", INK), lg["teksti"])
    if t.get("napit"):
        for i in range(t["napit"]):
            s += circle(0, B.hh * 1.25 + i * 7.5, 0.8, t.get("nappivari", shade(col, 0.6)), lw=LW * 0.35)
    return s

def tie_front(C, B):
    tc = vt(C, "solmio")
    if not tc:
        return ""
    y = B.hh * 1.06
    leveys = vt(C, "solmioleveys", 1.0)
    return path(smooth([(-1.6, y, 'c'), (1.6, y, 'c'), (1.2, y + 3.5, 'c'), (3.4 * leveys, B.waist_y - 8, 'c'), (0, B.waist_y - 4, 'c'),
                        (-3.4 * leveys, B.waist_y - 8, 'c'), (-1.2, y + 3.5, 'c')]), tc, lw=LW * 0.6) + \
        path(smooth([(-1.9, y - 1, 'c'), (1.9, y - 1, 'c'), (1.3, y + 3.5, 'c'), (-1.3, y + 3.5, 'c')]), tc, lw=LW * 0.6)

def coat_front(C, B):
    c = vt(C, "takki")
    if not c:
        return ""
    col = c["vari"]
    hem = {"lantio": B.hip_y + 4, "haara": B.crotch_y + 3, "reisi": B.crotch_y + 16, "polvi": B.knee_y + 8,
           "saari": B.knee_y + 22}[c.get("pituus", "lantio")]
    flare = c.get("levennys", 3.0)
    half = torso_half(C, B, hem, extra=1.3, flare=flare)
    gap_top = B.neck_w * 1.1
    gap_v = c.get("aukko_rinta", 4.0)     # aukon puolileveys rinnan alla
    gap_h = c.get("aukko_helma", 4.0)
    s = ""
    for sd in (1, -1):
        outer = [(sd * p[0], p[1]) + tuple(p[2:]) for p in half[1:-1]]
        inner = [(sd * gap_h, hem, 'c'), (sd * gap_v, B.waist_y), (sd * gap_v * 0.7, B.chest_y + 2), (sd * gap_top, B.hh * 1.04, 'c')]
        pts = outer + inner
        pd = smooth(pts, t=0.4)
        s += path(pd, col)
        if c.get("kuvio") == "ruutu":
            cid = uid("cp")
            s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (cid, pd, cid)
            for i in range(-14, 15):
                s += line([(i * 4.5, B.hh), (i * 4.5, hem + 2)], lw=LW * 0.9, stroke=c["vari2"])
            for j in range(0, 40):
                s += line([(-45, B.hh + j * 4.5), (45, B.hh + j * 4.5)], lw=LW * 0.9, stroke=c["vari2"])
            s += "</g>" + path(pd, None)
        if c.get("kaulus") == "kaannetty":
            lap = [(sd * gap_top, B.hh * 1.03, 'c'), (sd * (gap_top + 4.5), B.shoulder_y - 0.5, 'c'), (sd * (gap_top + 6.0), B.shoulder_y + 6, 'c'),
                   (sd * (gap_top + 3.5), B.shoulder_y + 7.5, 'c'), (sd * gap_v * 0.75, B.chest_y + 3, 'c')]
            s += path(smooth(lap, t=0.3), c.get("kaulusvari", shade(col, 0.82)), lw=LW * 0.7)
        if c.get("napit2"):
            for i in range(c["napit2"]):
                s += circle(sd * (gap_v + 4.5), B.chest_y + 3 + i * 9, 0.9, c.get("nappivari", "#c9a640"), lw=LW * 0.4)
        if c.get("taskut"):
            px = sd * (B.wa + 1.5) * 0.62
            py = B.waist_y + 9
            s += line([(px - 5, py), (px + 5, py)], lw=LW * 0.6)
    if c.get("nappi1"):
        s += circle(0, B.waist_y + 1, 0.9, c.get("nappivari", shade(col, 0.6)), lw=LW * 0.4)
    if c.get("vetoketju"):
        s += line([(0, B.chest_y + 4), (0, hem)], lw=LW * 0.5)
    if c.get("kaulus") == "pysty":
        s += collar_front(C, B, "pysty", c.get("kaulusvari", col))
    if c.get("huppu"):
        s += path(smooth([(-B.neck_w * 2.5, B.shoulder_y - 1.0), (-B.neck_w * 1.6, B.hh * 1.0), (0, B.hh * 1.08), (B.neck_w * 1.6, B.hh * 1.0),
                          (B.neck_w * 2.5, B.shoulder_y - 1.0), (B.neck_w * 1.3, B.shoulder_y + 2.5), (0, B.shoulder_y + 3.5), (-B.neck_w * 1.3, B.shoulder_y + 2.5)], t=0.5),
                  c.get("huppuvari", col), lw=LW * 0.7)
        if c.get("turkis"):
            pass
    if c.get("vyo"):
        y = B.waist_y + 1
        s += path(smooth([(-(B.wa + B.belly + 2), y, 'c'), ((B.wa + B.belly + 2), y, 'c'), ((B.wa + B.belly + 2), y + 3.5, 'c'),
                          (-(B.wa + B.belly + 2), y + 3.5, 'c')]), c["vyo"], lw=LW * 0.6)
    if c.get("olkalaput"):
        for sd in (1, -1):
            s += path(smooth([(sd * (B.sh * 0.55), B.shoulder_y - 1.2, 'c'), (sd * (B.sh + 1), B.shoulder_y + 0.5, 'c'),
                              (sd * (B.sh + 1), B.shoulder_y + 3.2, 'c'), (sd * (B.sh * 0.55), B.shoulder_y + 1.6, 'c')]), shade(col, 0.8), lw=LW * 0.5)
    if c.get("logo"):
        lg = c["logo"]
        s += circle(-(B.sh * 0.45), B.chest_y - 2, 3.6, lg.get("vari", "#ffffff"), lw=LW * 0.5)
        s += '<text x="%s" y="%s" font-family="Archivo Black" font-size="4.6" text-anchor="middle" fill="%s">%s</text>' % (
            f(-(B.sh * 0.45)), f(B.chest_y - 0.3), lg.get("tekstivari", INK), lg["teksti"])
    if c.get("taskuliina"):
        x = -(B.sh * 0.5)
        s += path(smooth([(x - 3, B.chest_y - 1, 'c'), (x - 1.5, B.chest_y - 4.5), (x, B.chest_y - 2.5), (x + 1.5, B.chest_y - 4.8), (x + 3, B.chest_y - 1, 'c')]),
                  c["taskuliina"], lw=LW * 0.5)
        s += line([(x - 3.5, B.chest_y - 1), (x + 3.5, B.chest_y - 1)], lw=LW * 0.6)
    return s

def apron_front(C, B):
    a = vt(C, "esiliina")
    if not a:
        return ""
    col = a["vari"]
    top = B.chest_y - 6
    bot = B.knee_y + 2
    s = line([(-B.neck_w * 1.0, B.hh * 1.04), (-5.5, top)], lw=LW * 1.6, stroke=col)
    s += line([(B.neck_w * 1.0, B.hh * 1.04), (5.5, top)], lw=LW * 1.6, stroke=col)
    pts = [(-6.5, top, 'c'), (6.5, top, 'c'), (7.5, B.waist_y - 1), (B.hi + 1, B.waist_y + 3), (B.hi + 2.5, bot, 'c'), (-B.hi - 2.5, bot, 'c'),
           (-B.hi - 1, B.waist_y + 3), (-7.5, B.waist_y - 1)]
    s += path(smooth(pts, t=0.35), col)
    if a.get("kuvio") == "kukka":
        for (x, y) in [(-8, B.waist_y + 10), (6, B.waist_y + 16), (-3, B.waist_y + 26), (9, B.waist_y + 32), (-10, B.waist_y + 36), (2, B.chest_y + 2)]:
            for ang in range(0, 360, 72):
                r = math.radians(ang)
                s += circle(x + math.cos(r) * 1.3, y + math.sin(r) * 1.3, 1.0, a.get("vari2", "#ffffff"), lw=0)
            s += circle(x, y, 0.7, "#f2c230", lw=0)
    s += path(smooth([(-6, B.waist_y + 12, 'c'), (6, B.waist_y + 12, 'c'), (6, B.waist_y + 20, 'c'), (-6, B.waist_y + 20, 'c')]), shade(col, 0.92), lw=LW * 0.5)
    return s

def accessories_front(C, B):
    s = ""
    for acc in C.get("varusteet", []):
        t = acc["tyyppi"]
        if t == "laukku":
            col = acc["vari"]
            s += path(smooth([(-B.neck_w * 1.4, B.hh * 1.05), (-B.neck_w * 0.6, B.hh * 1.08), (B.hi + 2, B.hip_y + 3), (B.hi + 1, B.hip_y + 7)], closed=True, t=0.1),
                      acc.get("hihna", shade(col, 0.7)), lw=LW * 0.6)
            x0, y0 = B.hi - 4, B.hip_y - 2
            s += path(smooth([(x0, y0, 'c'), (x0 + 13, y0, 'c'), (x0 + 13, y0 + 16, 'c'), (x0, y0 + 16, 'c')], t=0.1), col)
            s += path(smooth([(x0, y0, 'c'), (x0 + 13, y0, 'c'), (x0 + 13, y0 + 7, 'c'), (x0, y0 + 7, 'c')], t=0.1), shade(col, 0.85), lw=LW * 0.6)
            if acc.get("heijastin"):
                s += '<rect x="%s" y="%s" width="9" height="1.4" fill="%s" stroke="%s" stroke-width="%s"/>' % (
                    f(x0 + 2), f(y0 + 10), acc["heijastin"], INK, f(LW * 0.3))
        elif t == "radiopuhelin":
            x, y = -B.sh * 0.42, B.chest_y + 12
            s += '<rect x="%s" y="%s" width="4.4" height="8" rx="0.8" fill="#2a2a2a" stroke="%s" stroke-width="%s"/>' % (f(x - 2.2), f(y - 4), INK, f(LW * 0.5))
            s += line([(x + 1.2, y - 4), (x + 1.2, y - 9)], lw=LW * 1.2)
            s += line([(x - 2, y - 2), (x + 2, y - 2)], lw=LW * 0.3, stroke="#888888")
        elif t == "vyolaukku":
            col = acc["vari"]
            s += path(smooth([(B.wa - 9, B.waist_y + 2, 'c'), (B.wa + 1, B.waist_y + 2, 'c'), (B.wa + 1.5, B.waist_y + 12, 'c'), (B.wa - 9.5, B.waist_y + 12, 'c')], t=0.2), col)
            s += line([(B.wa - 9, B.waist_y + 5), (B.wa + 1, B.waist_y + 5)], lw=LW * 0.5)
        elif t == "kuulokkeet":
            col = acc["vari"]
            y = B.hh * 1.12
            s += line([(-B.neck_w * 1.15, y + 1.5), (0, y + 5.0), (B.neck_w * 1.15, y + 1.5)], lw=LW * 1.8, stroke=col)
            for sd in (1, -1):
                s += ellipse(sd * B.neck_w * 1.3, y + 0.8, 1.9, 2.5, acc.get("vari2", col), lw=LW * 0.6, rot=sd * 20)
        elif t == "huivi":
            col = acc["vari"]
            y = B.hh * 1.02
            s += path(smooth([(-B.neck_w * 1.6, y - 2, 'c'), (B.neck_w * 1.6, y - 2, 'c'), (B.neck_w * 1.9, y + 4, 'c'), (-B.neck_w * 1.9, y + 4, 'c')], t=0.4), col)
            s += path(smooth([(B.neck_w * 0.4, y + 3, 'c'), (B.neck_w * 1.4, y + 3, 'c'), (B.neck_w * 1.6, y + 24, 'c'), (B.neck_w * 0.2, y + 22, 'c')], t=0.3), col)
            s += line([(B.neck_w * 0.25, y + 21), (B.neck_w * 1.55, y + 22.5)], lw=LW * 0.4)
        elif t == "pinssi":
            s += circle(B.sh * 0.45, B.chest_y - 5, 1.8, acc["vari"], lw=LW * 0.5)
        elif t == "kello":
            pass
        elif t == "tarrarulla":
            pass
    return s

def neck_front(C, B):
    nw = B.neck_w
    return path(smooth([(-nw, B.hh * 0.75, 'c'), (nw, B.hh * 0.75, 'c'), (nw * 1.08, B.hh * 1.1, 'c'), (-nw * 1.08, B.hh * 1.1, 'c')], t=0.2), C["iho"]) + \
        path(smooth([(-nw, B.hh * 0.95), (0, B.hh * 1.0), (nw, B.hh * 0.95)], closed=False), None, lw=LW * 0.35)

def figure_front(C, B):
    s = ""
    a_typ = vt(C, "ala").get("tyyppi")
    s += legs_front(C, B)
    s += shoes_front(C, B) if vt(C, "kengat").get("tyyppi") in ("saapas", "kumisaapas") and a_typ in ("hame", "shortsit") else ""
    s += pants_front(C, B)
    if not (vt(C, "kengat").get("tyyppi") in ("saapas", "kumisaapas") and a_typ in ("hame", "shortsit")):
        s += shoes_front(C, B)
    s += neck_front(C, B)
    s += top_front(C, B)
    if a_typ == "haalari":
        pass
    s += tie_front(C, B)
    s += apron_front(C, B)
    s += arm_front(C, B, 1) + arm_front(C, B, -1)
    s += coat_front(C, B)
    s += accessories_front(C, B)
    s += head_front(C, B, "neutraali", True)
    return s

# ======================================================================== SIVU
def head_side(C, B):
    hh, hw = B.hh, B.hw
    fc = C["kasvot"]
    n = fc.get("nenä", 1.0)
    typ = fc.get("nenatyyppi", "suora")
    jaw = fc.get("leuka", 0.78)
    nose_tip = (hh * (0.47 + 0.07 * n), hh * 0.665)
    if typ == "perunanena":
        nose = [(hh * 0.41, hh * 0.5), (hh * 0.52 * (0.9 + 0.1 * n), hh * 0.62), (hh * 0.53, hh * 0.69), (hh * 0.43, hh * 0.72, 'c')]
    elif typ == "koukku":
        nose = [(hh * 0.42, hh * 0.49), (hh * 0.5, hh * 0.58), nose_tip + ('c',), (hh * 0.43, hh * 0.72, 'c')]
    else:
        nose = [(hh * 0.41, hh * 0.5), nose_tip + ('c',), (hh * 0.43, hh * 0.715, 'c')]
    pts = [(-hh * 0.05, 0), (hh * 0.3, hh * 0.08), (hh * 0.41, hh * 0.3), (hh * 0.44, hh * 0.42), (hh * 0.405, hh * 0.47)] + nose + \
          [(hh * 0.445, hh * 0.785), (hh * 0.415, hh * 0.82), (hh * 0.44, hh * 0.86), (hh * 0.395, hh * 0.93), (hh * 0.37, hh * 0.99),
           (hh * 0.2, hh * 1.0), (-hh * 0.1, hh * (0.9 + (jaw - 0.78) * 0.3)), (-hh * 0.18, hh * 0.98), (-hh * 0.45, hh * 0.72),
           (-hh * 0.52, hh * 0.4), (-hh * 0.42, hh * 0.12)]
    s = path(smooth(pts, t=0.5), C["iho"])
    # korva, silma, kulma, suu
    s += path(smooth([(-hh * 0.08, hh * 0.47), (-hh * 0.02, hh * 0.5), (-hh * 0.02, hh * 0.64), (-hh * 0.1, hh * 0.69), (-hh * 0.15, hh * 0.58)]), C["iho"], lw=LW * 0.7)
    s += line([(-hh * 0.05, hh * 0.52), (-hh * 0.1, hh * 0.58), (-hh * 0.06, hh * 0.63)], lw=LW * 0.4)
    s += path("M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" % (f(hh * 0.3), f(hh * 0.5), f(hh * 0.34), f(hh * 0.465), f(hh * 0.385), f(hh * 0.49),
                                                    f(hh * 0.35), f(hh * 0.53), f(hh * 0.3), f(hh * 0.5)), "#fbf8ef", lw=LW * 0.5)
    s += circle(hh * 0.365, hh * 0.495, hh * 0.017, INK, lw=0)
    s += path(smooth([(hh * 0.27, hh * 0.425, 'c'), (hh * 0.35, hh * 0.405), (hh * 0.42, hh * 0.425, 'c'), (hh * 0.35, hh * 0.425)], t=0.4),
              C.get("kulmavari", INK), lw=LW * 0.4)
    s += line([(hh * 0.43, hh * 0.815), (hh * 0.38, hh * 0.818)], lw=LW * 0.7)
    s += line([(hh * 0.44, hh * 0.67), (hh * 0.415, hh * 0.69)], lw=LW * 0.4)
    if fc.get("sanki"):
        s += '<path d="%s" fill="url(#stub)" opacity="%s"/>' % (
            smooth([(hh * 0.0, hh * 0.72), (hh * 0.35, hh * 0.86), (hh * 0.39, hh * 0.98), (hh * 0.2, hh * 1.0), (-hh * 0.12, hh * 0.9)]), f(0.55 * fc["sanki"] + 0.25))
    return s

def hair_side(C, B):
    hh = B.hh
    H = C["hiukset"]
    col, typ = H["vari"], H["tyyli"]
    if typ == "kihara":
        pts = []
        n = 14
        for i in range(n + 1):
            a = math.radians(150 + i * (235 / n))
            rr = 1.0 + (0.08 if i % 2 else 0)
            pts.append((-hh * 0.05 + math.cos(a) * hh * 0.56 * rr, hh * 0.38 + math.sin(a) * hh * 0.5 * rr))
        pts += [(hh * 0.3, hh * 0.22), (hh * 0.05, hh * 0.3), (-hh * 0.05, hh * 0.45), (-hh * 0.25, hh * 0.62)]
        return path(smooth(pts, t=0.55), col)
    if typ == "kalju_sivut":
        return path(smooth([(-hh * 0.2, hh * 0.35), (-hh * 0.45, hh * 0.3), (-hh * 0.56, hh * 0.5), (-hh * 0.45, hh * 0.78), (-hh * 0.22, hh * 0.72),
                            (-hh * 0.05, hh * 0.72), (-hh * 0.02, hh * 0.45)], t=0.5), col)
    if typ == "polkka":
        s = path(smooth([(hh * 0.36, hh * 0.38, 'c'), (hh * 0.38, hh * 0.12), (0, -hh * 0.12), (-hh * 0.5, hh * 0.05), (-hh * 0.6, hh * 0.45),
                         (-hh * 0.45, hh * 0.86, 'c'), (-hh * 0.12, hh * 0.86, 'c'), (-hh * 0.1, hh * 0.45), (hh * 0.15, hh * 0.32)], t=0.5), col)
        if H.get("raita"):
            s += path(smooth([(hh * 0.25, hh * 0.0), (hh * 0.36, hh * 0.15), (hh * 0.36, hh * 0.37, 'c'), (hh * 0.25, hh * 0.3)], t=0.5), H["raita"], lw=LW * 0.5)
        return s
    if typ == "nuttura":
        return circle(-hh * 0.35, -hh * 0.02, hh * 0.22, col) + \
            path(smooth([(hh * 0.35, hh * 0.18), (hh * 0.15, -hh * 0.05), (-hh * 0.3, -hh * 0.03), (-hh * 0.55, hh * 0.35), (-hh * 0.45, hh * 0.7),
                         (-hh * 0.2, hh * 0.6), (-hh * 0.08, hh * 0.45), (hh * 0.2, hh * 0.25)], t=0.5), col)
    if typ == "sivuhiukset_lakki":
        return path(smooth([(-hh * 0.15, hh * 0.25), (-hh * 0.52, hh * 0.25), (-hh * 0.55, hh * 0.6), (-hh * 0.35, hh * 0.75), (-hh * 0.12, hh * 0.6),
                            (-hh * 0.02, hh * 0.45)], t=0.5), col)
    if typ == "foni":
        return path(smooth([(hh * 0.36, hh * 0.15), (hh * 0.25, -hh * 0.2), (-hh * 0.3, -hh * 0.2), (-hh * 0.6, hh * 0.25), (-hh * 0.5, hh * 0.72),
                            (-hh * 0.28, hh * 0.76), (-hh * 0.06, hh * 0.8, 'c'), (-hh * 0.02, hh * 0.45), (hh * 0.15, hh * 0.2)], t=0.5), col)
    if typ in ("liukas", "lyhyt", "sivukampaus"):
        s = path(smooth([(hh * 0.33, hh * 0.18), (hh * 0.15, -hh * 0.07), (-hh * 0.3, -hh * 0.06), (-hh * 0.54, hh * 0.3), (-hh * 0.48, hh * 0.7),
                         (-hh * 0.3, hh * 0.74), (-hh * 0.12, hh * 0.62), (-hh * 0.04, hh * 0.45), (hh * 0.12, hh * 0.22)], t=0.5), col)
        if H.get("ohimot"):
            s += path(smooth([(-hh * 0.02, hh * 0.32), (-hh * 0.16, hh * 0.3), (-hh * 0.14, hh * 0.55), (-hh * 0.03, hh * 0.5)]), H["ohimot"], lw=LW * 0.4)
        return s
    return ""

def facial_hair_side(C, B):
    hh = B.hh
    fc = C["kasvot"]
    col = fc.get("viiksivari", C["hiukset"]["vari"])
    s = ""
    if fc.get("parta"):
        L = fc.get("parran_pituus", 1.0)
        s += path(smooth([(-hh * 0.12, hh * 0.6), (hh * 0.05, hh * 0.78), (hh * 0.3, hh * 0.86), (hh * 0.46, hh * 0.86), (hh * 0.45, hh * (0.98 + 0.07 * L)),
                          (hh * 0.3, hh * (1.04 + 0.16 * L)), (hh * 0.05, hh * (1.0 + 0.12 * L)), (-hh * 0.15, hh * 0.9)], t=0.5), col)
    v = fc.get("viikset")
    if v:
        w = {"mursu": 0.06, "kyna": 0.015, "tuuhea": 0.04}.get(v, 0.04)
        s += path(smooth([(hh * 0.36, hh * 0.73), (hh * 0.455, hh * 0.725), (hh * 0.46, hh * 0.76 + w), (hh * 0.38, hh * 0.78 + w)], t=0.4), col, lw=LW * 0.6)
    if fc.get("lasit"):
        gc = fc["lasit"].get("vari", INK)
        s += line([(hh * 0.42, hh * 0.47), (hh * 0.42, hh * 0.54)], lw=LW * 1.0, stroke=gc)
        s += line([(hh * 0.42, hh * 0.48), (-hh * 0.06, hh * 0.5)], lw=LW * 0.7, stroke=gc)
    return s

def hat_side(C, B):
    hh = B.hh
    h = C.get("paahine")
    if not h:
        return ""
    col = h["vari"]
    if h["tyyppi"] in ("kapteeni", "vartija"):
        s = path(smooth([(-hh * 0.52, hh * 0.26, 'c'), (-hh * 0.6, -hh * 0.08), (0, -hh * 0.18), (hh * 0.42, -hh * 0.06), (hh * 0.36, hh * 0.26, 'c')], t=0.5),
                 h.get("kupu", col))
        s += path(smooth([(-hh * 0.48, hh * 0.12, 'c'), (hh * 0.37, hh * 0.12, 'c'), (hh * 0.36, hh * 0.27, 'c'), (-hh * 0.5, hh * 0.27, 'c')]), h.get("nauha", INK))
        s += path(smooth([(hh * 0.3, hh * 0.25, 'c'), (hh * 0.62, hh * 0.32), (hh * 0.6, hh * 0.36, 'c'), (hh * 0.3, hh * 0.3, 'c')], t=0.4), INK, lw=LW * 0.5)
        return s
    if h["tyyppi"] == "pipo":
        s = path(smooth([(-hh * 0.52, hh * 0.32, 'c'), (-hh * 0.6, hh * 0.0), (-hh * 0.1, -hh * 0.22), (hh * 0.35, -hh * 0.05), (hh * 0.4, hh * 0.3, 'c')], t=0.5), col)
        s += path(smooth([(-hh * 0.56, hh * 0.15, 'c'), (hh * 0.4, hh * 0.15, 'c'), (hh * 0.41, hh * 0.33, 'c'), (-hh * 0.54, hh * 0.33, 'c')], t=0.3), h.get("kaanne", col))
        return s
    if h["tyyppi"] == "lippis":
        s = path(smooth([(-hh * 0.5, hh * 0.3, 'c'), (-hh * 0.55, hh * 0.0), (0, -hh * 0.14), (hh * 0.4, hh * 0.05), (hh * 0.4, hh * 0.3, 'c')], t=0.5), col)
        s += path(smooth([(hh * 0.3, hh * 0.27, 'c'), (hh * 0.72, hh * 0.33), (hh * 0.7, hh * 0.38, 'c'), (hh * 0.3, hh * 0.33, 'c')], t=0.4), h.get("lippa", shade(col, 0.7)), lw=LW * 0.5)
        return s
    return ""

def figure_side(C, B):
    """Sivukuva, hahmo katsoo oikealle (+x)."""
    hh = B.hh
    H = B.H
    k = B.limb
    t = vt(C, "ylä")
    a = vt(C, "ala")
    sk = vt(C, "kengat")
    coat = vt(C, "takki")
    cd, bd, belly, butt = B.chest_d, B.back_d, B.belly, B.butt
    lean = B.stoop
    s = ""
    # jalka (yksi nakyy, toinen hieman taakse)
    leg_col = vt(C, "sukat", C["iho"])
    def leg(dx, col_pants):
        pts = [(cd * 0.65 + dx, B.crotch_y - 10), (6.5 + dx, B.knee_y - 8), (5.2 + dx, B.knee_y), (5.6 + dx, B.knee_y + 10), (3.6 + dx, B.ankle_y),
               (-3.6 + dx, B.ankle_y), (-6.5 + dx, B.knee_y + 9), (-5.2 + dx, B.knee_y), (-bd * 0.9 - butt * 0.6 + dx, B.crotch_y)]
        return pts
    for dx in (-3.0, 0.0):
        s += path(smooth(leg(dx, None), t=0.5), leg_col)
    # kengat
    ktyp = sk.get("tyyppi", "kenka")
    for dx in (-3.0, 0.0):
        top = B.ankle_y - (12 if ktyp == "saapas" else 20 if ktyp == "kumisaapas" else 1.5)
        pts = [(-4.6 + dx, top, 'c'), (4.2 + dx, top, 'c'), (5 + dx, B.ankle_y + 1), (14 + dx, B.H - 4.5), (17 + dx, B.H - 1.5, 'c'), (-6 + dx, B.H - 1.5, 'c'), (-6.2 + dx, B.H - 6)]
        s += path(smooth(pts, t=0.45), sk["vari"])
        s += path(smooth([(-6.2 + dx, B.H - 1.8, 'c'), (17.2 + dx, B.H - 1.8, 'c'), (17.2 + dx, B.H, 'c'), (-6.2 + dx, B.H, 'c')]), sk.get("pohja", "#555555"), lw=LW * 0.5)
    # housut / hame
    typ = a.get("tyyppi", "housut")
    if typ == "hame":
        hem = B.knee_y + a.get("pituus", 6)
        s += path(smooth([(cd * 0.7 + belly * 0.5, B.waist_y, 'c'), (cd * 0.85 + belly * 0.5, B.hip_y), (cd + 3, hem, 'c'), (-bd - butt - 4, hem, 'c'),
                          (-bd - butt, B.hip_y + 3), (-bd * 0.85, B.waist_y, 'c')], t=0.45), a["vari"])
    else:
        hem_y = B.ankle_y + 1.5 if typ != "shortsit" else B.knee_y - 7
        fl = a.get("levennys", 0)
        for dx in (-3.0, 0.0):
            if typ == "shortsit":
                pts = [(cd * 0.75 + dx, B.waist_y), (cd * 0.85 + belly * 0.3 + dx, B.hip_y), (8.5 + dx, hem_y, 'c'), (-8.5 + dx, hem_y, 'c'),
                       (-bd - butt + dx, B.hip_y + 3), (-bd * 0.85 + dx, B.waist_y)]
            else:
                pts = [(cd * 0.75 + belly * 0.4 + dx, B.waist_y), (cd * 0.8 + belly * 0.3 + dx, B.hip_y), (7.3 + dx, B.knee_y - 8), (6.4 + dx, B.knee_y + 2),
                       (5.6 + fl + dx, hem_y, 'c'), (-5.0 - fl + dx, hem_y, 'c'), (-6.6 + dx, B.knee_y + 2), (-bd - butt * 0.6 + dx, B.crotch_y + 2),
                       (-bd - butt + dx, B.hip_y + 3), (-bd * 0.85 + dx, B.waist_y)]
            s += path(smooth(pts, t=0.45), a["vari"])
        if a.get("vyo"):
            s += path(smooth([(cd * 0.75 + belly * 0.4, B.waist_y, 'c'), (-bd * 0.85, B.waist_y, 'c'), (-bd * 0.85, B.waist_y + 3.2, 'c'),
                              (cd * 0.75 + belly * 0.4, B.waist_y + 3.2, 'c')]), a["vyo"], lw=LW * 0.5)
    # kaula
    s += path(smooth([(-hh * 0.2, hh * 0.75, 'c'), (hh * 0.15, hh * 0.85, 'c'), (hh * 0.22, hh * 1.15, 'c'), (-hh * 0.28, hh * 1.1, 'c')]), C["iho"])
    # vartalo
    hem = {"lantio": B.hip_y + 3, "vyotaro": B.waist_y + 1, "haara": B.crotch_y}.get(t.get("helma", "lantio"), B.hip_y + 3)
    if typ == "haalari":
        hem = B.waist_y + 1
    def torso_pts(ext, hem_y, flare=0.0):
        pts = [(hh * 0.18 + ext * 0.5, hh * 1.03), (cd * 0.7 + ext, B.shoulder_y + 3), (cd + B.bust + ext, B.chest_y - 2), (cd * 0.85 + B.bust * 0.6 + ext, B.chest_y + 7)]
        if belly > 2:
            pts.append((cd * 0.75 + belly + ext, (B.chest_y + B.waist_y) / 2 + 6))
        pts.append((cd * 0.75 + belly * 0.7 + ext, B.waist_y))
        if hem_y > B.waist_y + 4:
            pts.append((cd * 0.8 + belly * 0.3 + ext + flare * 0.5, min(hem_y, B.hip_y)))
        pts.append((cd * 0.8 + belly * 0.3 + ext + flare, hem_y, 'c'))
        pts.append((-bd - butt * (1.0 if hem_y > B.hip_y else 0.3) - ext - flare, hem_y, 'c'))
        if hem_y > B.waist_y + 4:
            pts.append((-bd - butt * 0.8 - ext - flare * 0.5, min(hem_y, B.hip_y)))
        pts += [(-bd * 0.8 - ext, B.waist_y - 2), (-bd - ext - lean, B.chest_y - 4), (-bd * 0.85 - ext - lean, B.shoulder_y + 2), (-hh * 0.25 - ext * 0.5 - lean * 0.5, hh * 1.05)]
        return pts
    s += path(smooth(torso_pts(0, hem), t=0.5), t["vari"])
    kaulus = t.get("kaulus")
    if kaulus == "poolo":
        s += path(smooth([(-hh * 0.28, hh * 0.92, 'c'), (hh * 0.2, hh * 0.98, 'c'), (hh * 0.24, hh * 1.18, 'c'), (-hh * 0.32, hh * 1.12, 'c')]), t.get("kaulusvari", t["vari"]))
    if vt(C, "solmio") and not coat:
        s += path(smooth([(hh * 0.2, hh * 1.05), (cd + 1.0, B.chest_y), (cd * 0.85 + 1.0, B.waist_y - 6), (cd * 0.7, B.chest_y)], t=0.3), vt(C, "solmio"), lw=LW * 0.5)
    esi = vt(C, "esiliina")
    if esi:
        s += path(smooth([(cd + B.bust - 1, B.chest_y - 6, 'c'), (cd + B.bust + 1.2, B.chest_y - 2), (cd * 0.75 + belly + 1.2, B.waist_y), (cd * 0.9 + 3, B.knee_y + 2, 'c'),
                          (cd * 0.9 + 1, B.knee_y + 2, 'c'), (cd * 0.75 + belly, B.waist_y + 2), (cd + B.bust - 0.4, B.chest_y - 2)], t=0.4), esi["vari"], lw=LW * 0.6)
    if coat:
        chem = {"lantio": B.hip_y + 4, "haara": B.crotch_y + 3, "reisi": B.crotch_y + 16, "polvi": B.knee_y + 8, "saari": B.knee_y + 22}[coat.get("pituus", "lantio")]
        s += path(smooth(torso_pts(1.4, chem, coat.get("levennys", 3.0) * 0.8), t=0.5), coat["vari"])
        if coat.get("kaulus") == "pysty" or coat.get("huppu"):
            s += path(smooth([(-hh * 0.35, hh * 0.86, 'c'), (hh * 0.05, hh * 0.92, 'c'), (hh * 0.24, hh * 1.18, 'c'), (-hh * 0.4, hh * 1.18, 'c')]),
                      coat.get("huppuvari", coat.get("kaulusvari", coat["vari"])))
        if coat.get("kaulus") == "kaannetty":
            s += path(smooth([(hh * 0.2, hh * 1.05, 'c'), (cd * 0.55, B.shoulder_y + 1), (cd * 0.95, B.chest_y + 4, 'c'), (cd * 0.6, B.shoulder_y + 8)], t=0.4),
                      coat.get("kaulusvari", shade(coat["vari"], 0.82)), lw=LW * 0.6)
    for acc in C.get("varusteet", []):
        if acc["tyyppi"] == "laukku":
            s += path(smooth([(-bd - butt - 3, B.hip_y - 3, 'c'), (-bd - butt + 2, B.hip_y - 3, 'c'), (-bd - butt + 2, B.hip_y + 13, 'c'), (-bd - butt - 4, B.hip_y + 13, 'c')], t=0.2), acc["vari"])
            s += line([(-bd - butt + 1, B.hip_y - 3), (-bd * 0.6, B.shoulder_y + 2)], lw=LW * 2.5, stroke=acc.get("hihna", shade(acc["vari"], 0.7)))
        if acc["tyyppi"] == "radiopuhelin":
            s += '<rect x="%s" y="%s" width="2.6" height="7.5" rx="0.6" fill="#2a2a2a" stroke="%s" stroke-width="%s"/>' % (f(cd + 0.5), f(B.chest_y - 2), INK, f(LW * 0.5))
        if acc["tyyppi"] == "vyolaukku":
            s += path(smooth([(cd * 0.75 + belly * 0.7 - 1, B.waist_y + 2, 'c'), (cd * 0.75 + belly * 0.7 + 4, B.waist_y + 3, 'c'),
                              (cd * 0.75 + belly * 0.7 + 4, B.waist_y + 12, 'c'), (cd * 0.75 + belly * 0.7 - 1, B.waist_y + 12, 'c')], t=0.3), acc["vari"])
        if acc["tyyppi"] == "huivi":
            s += path(smooth([(-hh * 0.32, hh * 0.98, 'c'), (hh * 0.24, hh * 1.02, 'c'), (hh * 0.26, hh * 1.2, 'c'), (-hh * 0.34, hh * 1.16, 'c')]), acc["vari"])
            s += path(smooth([(hh * 0.15, hh * 1.12), (hh * 0.3, hh * 1.18), (cd + 1, B.chest_y + 4), (cd - 2, B.chest_y + 3)], t=0.4), acc["vari"])
    # kasi (sivulla, roikkuu)
    sleeve = t.get("hiha", "pitka")
    scol = t["vari"]
    if coat and coat.get("hiha", True):
        sleeve, scol = "pitka", coat["vari"]
    J = (-1.0 - lean * 0.5, B.shoulder_y + 3)
    E = (-2.5, B.waist_y - 1)
    W = (1.5, B.crotch_y - 4)
    s += path(smooth(limb_outline([J, ((J[0] + E[0]) / 2, (J[1] + E[1]) / 2), E, ((E[0] + W[0]) / 2, (E[1] + W[1]) / 2), W],
                                  [5.0 * k, 4.4 * k, 3.8 * k, 3.4 * k, 2.4 * k]), t=0.5), C["iho"])
    if sleeve == "lyhyt":
        S = (J[0] + (E[0] - J[0]) * 0.45, J[1] + (E[1] - J[1]) * 0.45)
        s += path(smooth(limb_outline([(J[0], J[1] - 3), J, S], [6.0 * k, 6.0 * k, 5.6 * k]), t=0.3), scol)
    else:
        Wc = (W[0] - 0.2, W[1] - 1)
        s += path(smooth(limb_outline([(J[0], J[1] - 3), J, E, Wc], [6.0 * k, 6.0 * k, 4.6 * k, 4.0 * k]), t=0.45), scol)
        if t.get("kalvosin"):
            s += path(smooth(limb_outline([(Wc[0] - 0.4, Wc[1] - 2.5), Wc], [4.1 * k, 4.0 * k]), t=0.2), t["kalvosin"])
    hc = vt(C, "hanskat") or C["iho"]
    hx, hy = W
    s += path(smooth([(hx - 3, hy - 0.5), (hx + 3, hy - 0.5), (hx + 3.6, hy + 6), (hx + 1.5, hy + B.H * 0.1), (hx - 1.5, hy + B.H * 0.095), (hx - 2.8, hy + 5)], t=0.5), hc)
    s += path(smooth([(hx + 2.0, hy + 2), (hx + 4.2, hy + 4.5), (hx + 4.0, hy + 7.5), (hx + 2.4, hy + 6.5)], t=0.5), hc, lw=LW * 0.7)
    # paa
    hd = head_side(C, B)
    s += '<g transform="translate(%s,0)">%s%s%s%s</g>' % (f(0), hd, facial_hair_side(C, B), hair_side(C, B), hat_side(C, B))
    return s
