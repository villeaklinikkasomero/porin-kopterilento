# -*- coding: utf-8 -*-
"""Kokoaa konseptiarkit, muotokuvat, rivikuvan ja mallikortit. Ajo: python kokoa.py <ulos>"""
import os, sys, json, math
import piirto as P
from piirto import f, INK, uid
from vartalo import figure_front, figure_side, neck_front, top_front, tie_front, coat_front, apron_front, accessories_front
from hahmot_data import HAHMOT, TUNTEET, TUNNE_AVAIN

PAPER = "#f1e6c8"
FONT_T = "Anton, 'Archivo Black', Impact, sans-serif"
FONT_B = "'DejaVu Sans Condensed', 'Arial Narrow', Arial, sans-serif"
FONT_H = "'Archivo Black', 'Arial Black', sans-serif"

DEFS = """<defs>
<pattern id="dots" width="1.2" height="1.2" patternUnits="userSpaceOnUse"><circle cx="0.6" cy="0.6" r="0.28" fill="#3a2a1e"/></pattern>
<pattern id="half" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="3.5" cy="3.5" r="1.7" fill="#1b1712"/></pattern>
<pattern id="stub" width="0.75" height="0.75" patternUnits="userSpaceOnUse"><circle cx="0.37" cy="0.37" r="0.14" fill="#3a2a1e"/></pattern>
<pattern id="halfS" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="2.5" cy="2.5" r="1.1" fill="#1b1712"/></pattern>
<pattern id="paper" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(20)"><circle cx="4.5" cy="4.5" r="1.0" fill="#d9c79c" opacity="0.55"/></pattern>
<filter id="tow" color-interpolation-filters="sRGB"><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
</defs>"""

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def wrap(text, n):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out

def text_block(x, y, lines, size, lh=1.3, fill=INK, font=FONT_B, weight="normal"):
    s = '<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" font-weight="%s">' % (f(x), f(y), font, f(size), fill, weight)
    for i, l in enumerate(lines):
        s += '<tspan x="%s" dy="%s">%s</tspan>' % (f(x), f(0 if i == 0 else size * lh), esc(l))
    return s + "</text>"

def shaded(content, sx, sy, scale, shade_x, w=3000, h=3000, opacity=0.24, pat="half"):
    """Piirtaa sisallon ja rasterivarjon (oikea puoli shade_x:sta) maskattuna sisallon muotoon."""
    gid, mid = uid("fig"), uid("msk")
    tf = "translate(%s,%s) scale(%s)" % (f(sx), f(sy), f(scale))
    s = '<g id="%s" transform="%s">%s</g>' % (gid, tf, content)
    s += '<mask id="%s" maskUnits="userSpaceOnUse" x="-5000" y="-5000" width="10000" height="10000"><use href="#%s" filter="url(#tow)"/></mask>' % (mid, gid)
    s += '<rect x="%s" y="-5000" width="%s" height="10000" fill="url(#%s)" opacity="%s" mask="url(#%s)"/>' % (f(shade_x), f(w), pat, f(opacity), mid)
    # aariviivat uudelleen rasterin paalle ei tarvita: rasteri on lapikuultava
    return s

def panel(x, y, w, h, fill="#fbf5e2", lw=5):
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (f(x), f(y), f(w), f(h), fill, INK, f(lw))

def caption(x, y, text, size=22, fill="#f2d13c", tfill=INK, rot=0, pad=8):
    w = len(text) * size * 0.55 + pad * 2
    s = '<g transform="rotate(%s %s %s)">' % (f(rot), f(x), f(y))
    s += '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="3"/>' % (f(x), f(y), f(w), f(size + pad * 1.4), fill, INK)
    s += '<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s">%s</text></g>' % (f(x + pad), f(y + size + pad * 0.35), FONT_T, f(size), tfill, esc(text))
    return s

# ------------------------------------------------------------------ rintakuva
def bust(C, B, emo):
    s = neck_front(C, B) + top_front(C, B) + tie_front(C, B) + coat_front(C, B) + apron_front(C, B) + accessories_front(C, B)
    cid = uid("bc")
    clip = '<clipPath id="%s"><rect x="-80" y="-60" width="160" height="%s"/></clipPath>' % (cid, f(B.hh * 2.15 + 60))
    return clip + '<g clip-path="url(#%s)">%s</g>' % (cid, s) + P.head_front(C, B, emo)

def portrait_svg(C, emo, size=512, bg=None):
    B = P.Body(C)
    sc = size * 0.43 / B.hh
    ox, oy = size / 2, size * 0.2
    body = bust(C, B, emo)
    s = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (size, size, size, size)
    s += DEFS
    if bg:
        s += '<rect width="%d" height="%d" fill="%s"/><rect width="%d" height="%d" fill="url(#paper)"/>' % (size, size, bg, size, size)
    s += shaded(body, ox, oy, sc, ox + B.hw * sc * 0.35, opacity=0.2, pat="halfS")
    return s + "</svg>"

# ------------------------------------------------------------------ props (pienet kuvakkeet)
def ruler(x0, x1, floor_y, sc, top_cm=200):
    s = ""
    for cm in range(0, top_cm + 1, 10):
        y = floor_y - cm * sc
        strong = cm % 50 == 0
        s += '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#b9a676" stroke-width="%s" %s/>' % (
            f(x0), f(y), f(x1), f(y), "1.6" if strong else "0.8", '' if strong else 'stroke-dasharray="4 5"')
        if strong:
            s += '<text x="%s" y="%s" font-family="%s" font-size="15" fill="#8a7a50">%d</text>' % (f(x0 + 4), f(y - 4), FONT_B, cm)
    return s

def sheet_svg(C):
    B = P.Body(C)
    W, Hh = 1800, 1150
    s = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hh, W, Hh)
    s += DEFS
    s += '<rect width="%d" height="%d" fill="%s"/><rect width="%d" height="%d" fill="url(#paper)"/>' % (W, Hh, PAPER, W, Hh)
    # otsikko
    s += '<rect x="30" y="24" width="1080" height="104" fill="%s" stroke="%s" stroke-width="5"/>' % (INK, INK)
    s += '<rect x="30" y="24" width="20" height="104" fill="%s"/>' % C["ui_vari"]
    title = C.get("otsikko", C["nimi"]).upper()
    s += '<text x="70" y="98" font-family="%s" font-size="66" fill="%s" letter-spacing="1">%s</text>' % (FONT_T, C["ui_vari"], esc(title))
    nx = 70 + len(title) * 66 * 0.47 + 30
    rl = wrap(C["rooli"], int((1090 - nx) / 12))
    s += text_block(nx, 62 if len(rl) == 1 else 54, rl, 21, lh=1.15, fill="#f1e6c8", font=FONT_H)
    s += text_block(nx, 114, ["%d v · %d cm · %s" % (C["ika"], C["pituus"], C["id"])], 18, fill="#c9b98a", font=FONT_B)
    s += '<text x="1770" y="62" font-family="%s" font-size="30" fill="%s" text-anchor="end">SATAMAKAUPUNKI</text>' % (FONT_T, INK)
    s += '<text x="1770" y="92" font-family="%s" font-size="17" fill="%s" text-anchor="end">HAHMOKONSEPTI · PORIN KOPTERILENTO · 1960–70-LUVUN SARJAKUVATYYLI</text>' % (FONT_B, INK)
    if C.get("status"):
        s += '<text x="1770" y="118" font-family="%s" font-size="15" fill="#a8402a" text-anchor="end">%s</text>' % (FONT_H, esc(C["status"]))
    # vasen paneeli: edesta + sivulta
    s += panel(30, 150, 740, 970)
    sc = 4.55
    floor = 1085
    s += ruler(36, 764, floor, sc)
    hy = floor - C["pituus"] * sc
    s += '<line x1="36" y1="%s" x2="764" y2="%s" stroke="#a8402a" stroke-width="2"/>' % (f(hy), f(hy))
    s += '<text x="760" y="%s" font-family="%s" font-size="17" fill="#a8402a" text-anchor="end">%d cm</text>' % (f(hy - 6), FONT_H, C["pituus"])
    # maavarjot
    for cx in (245, 575):
        s += '<ellipse cx="%s" cy="%s" rx="80" ry="10" fill="#1b1712" opacity="0.15"/>' % (cx, floor)
    s += shaded(figure_front(C, B), 245, hy, sc, 245 + 4 * sc)
    s += shaded(figure_side(C, B), 575, hy, sc, 575 - 2 * sc)
    s += caption(46, 162, "EDESTÄ (A-ASENTO)", 18, rot=-1.5)
    s += caption(470, 162, "SIVULTA", 18, rot=1.2)
    # ilmeet
    s += panel(800, 150, 970, 610, fill="#fbf5e2")
    cw, ch = 970 / 3, 610 / 2
    for i, emo in enumerate(TUNTEET):
        cx = 800 + (i % 3) * cw
        cy = 150 + (i // 3) * ch
        if i % 3:
            s += '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="3"/>' % (f(cx), f(cy), f(cx), f(cy + ch), INK)
        if i // 3:
            s += '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="3"/>' % (f(cx), f(cy), f(cx + cw), f(cy), INK)
        hsc = 165 / B.hh
        cid = uid("cell")
        s += '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath><g clip-path="url(#%s)">' % (cid, f(cx + 2), f(cy + 2), f(cw - 4), f(ch - 4), cid)
        s += shaded(bust(C, B, emo), cx + cw / 2, cy + 46, hsc, cx + cw / 2 + B.hw * hsc * 0.35, opacity=0.2, pat="halfS")
        s += "</g>"
        s += caption(cx + 10, cy + ch - 40, P.EMO_NIMI[emo], 17, fill=C["ui_vari"], rot=0)
    # tiedot
    s += panel(800, 780, 970, 340, fill="#fbf5e2")
    # paletti
    pal = palette(C)
    s += '<text x="820" y="812" font-family="%s" font-size="20" fill="%s">VÄRIT (sRGB)</text>' % (FONT_T, INK)
    for i, (nm, hx) in enumerate(pal[:14]):
        col, row = i // 7, i % 7
        x, y = 820 + col * 190, 826 + row * 41
        s += '<rect x="%s" y="%s" width="34" height="32" fill="%s" stroke="%s" stroke-width="2.5"/>' % (f(x), f(y), hx, INK)
        s += text_block(x + 42, y + 13, [nm], 13.5, font=FONT_H)
        s += text_block(x + 42, y + 29, [hx], 13, fill="#6a5a40")
    tx = 1210
    s += '<text x="%s" y="812" font-family="%s" font-size="20" fill="%s">KUKA?</text>' % (f(tx), FONT_T, INK)
    y = 836
    s += text_block(tx, y, wrap(C["kuvaus"], 74), 14.5, lh=1.28)
    y += len(wrap(C["kuvaus"], 74)) * 14.5 * 1.28 + 14
    s += '<text x="%s" y="%s" font-family="%s" font-size="18" fill="%s">SILUETTI</text>' % (f(tx), f(y), FONT_T, INK)
    y += 20
    s += text_block(tx, y, wrap(C["siluetti"], 74), 14.5, lh=1.28)
    y += len(wrap(C["siluetti"], 74)) * 14.5 * 1.28 + 14
    if C["rekvisiitta"]:
        s += '<text x="%s" y="%s" font-family="%s" font-size="18" fill="%s">REKVISIITTA</text>' % (f(tx), f(y), FONT_T, INK)
        y += 20
        r = wrap("• " + "  • ".join(C["rekvisiitta"]), 74)
        s += text_block(tx, y, r, 14.5, lh=1.28)
        y += len(r) * 14.5 * 1.28 + 10
    if C["oletukset"]:
        r = wrap("HUOM: " + " ".join(C["oletukset"]), 80)
        s += text_block(tx, y + 8, r, 13, lh=1.28, fill="#a8402a", font=FONT_H)
    return s + "</svg>"

def palette(C):
    v = C["vaatteet"]
    out = [("Iho", C["iho"]), ("Hiukset", C["hiukset"]["vari"])]
    if C["hiukset"].get("raita"):
        out.append(("Hiusraita", C["hiukset"]["raita"]))
    if C["hiukset"].get("ohimot"):
        out.append(("Ohimot", C["hiukset"]["ohimot"]))
    out.append(("Silmät", C["silmavari"]))
    if C["kasvot"].get("viikset") or C["kasvot"].get("parta"):
        out.append(("Parta/viikset", C["kasvot"].get("viiksivari", C["hiukset"]["vari"])))
    if C.get("paahine"):
        out.append(("Päähine", C["paahine"].get("kupu", C["paahine"]["vari"])))
    if v.get("takki"):
        out.append(("Takki", v["takki"]["vari"]))
    out.append(("Yläosa", v["ylä"]["vari"]))
    if v["ylä"].get("vari2"):
        out.append(("Kuvio", v["ylä"]["vari2"]))
    if v.get("solmio"):
        out.append(("Solmio", v["solmio"]))
    if v.get("esiliina"):
        out.append(("Esiliina", v["esiliina"]["vari"]))
    out.append(("Alaosa", v["ala"]["vari"]))
    out.append(("Kengät", v["kengat"]["vari"]))
    for a in C.get("varusteet", []):
        if a.get("vari"):
            out.append((a["tyyppi"].capitalize(), a["vari"]))
    if C["kasvot"].get("huulet"):
        out.append(("Huulet", C["kasvot"]["huulet"]))
    seen, res = set(), []
    for n, h in out:
        if n not in seen:
            seen.add(n)
            res.append((n, h))
    return res

def variantit():
    import copy
    base = next(c for c in HAHMOT if c["id"] == "VARTIJA")
    b = copy.deepcopy(base); b.update(id="VARTIJA_B", otsikko="VARTIJA B", pituus=168)
    b["body"].update(paita=6.8, hartiat=22.0, vyotaro=18.0, lantio=18.0, vatsa=3.5, raajat=1.12)
    b["kasvot"].update(viikset="tuuhea", viiksivari="#2a1e14", leuka=0.95); b["hiukset"]["vari"] = "#2a1e14"; b["iho"] = "#c48a66"
    c = copy.deepcopy(base); c.update(id="VARTIJA_C", otsikko="VARTIJA C", pituus=170)
    c["body"].update(paita=7.2, hartiat=18.0, vyotaro=13.5, lantio=16.5, vatsa=0, rinta=1.2, raajat=0.9)
    c["kasvot"] = dict(leuka=0.72, leuanpaa=0.32, nenä=0.85, ripset=True, huulet="#a8505a")
    c["hiukset"] = dict(tyyli="polkka", vari="#c99a52"); c["iho"] = "#ecc4a4"
    return [b, c]

def lineup_svg():
    HAHMOT_L = HAHMOT + variantit()
    sc = 3.3
    gap = 215
    W = 80 + gap * len(HAHMOT_L) + 20
    Hh = 860
    floor = 760
    s = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hh, W, Hh)
    s += DEFS + '<rect width="%d" height="%d" fill="%s"/><rect width="%d" height="%d" fill="url(#paper)"/>' % (W, Hh, PAPER, W, Hh)
    s += '<text x="30" y="60" font-family="%s" font-size="44" fill="%s">SATAMAKAUPUNKI – HAHMOT RIVISSÄ</text>' % (FONT_T, INK)
    s += '<text x="30" y="88" font-family="%s" font-size="17" fill="%s">Sama mittakaava kaikille · viivat 10 cm välein · tarinan väri = dialogin nimiväri (tarina/data/hahmot.json)</text>' % (FONT_B, INK)
    s += ruler(20, W - 20, floor, sc)
    for i, C in enumerate(HAHMOT_L):
        B = P.Body(C)
        cx = 80 + gap * i + gap / 2
        s += '<ellipse cx="%s" cy="%s" rx="62" ry="8" fill="#1b1712" opacity="0.15"/>' % (f(cx), floor)
        s += shaded(figure_front(C, B), cx, floor - C["pituus"] * sc, sc, cx + 4 * sc)
        s += '<rect x="%s" y="%s" width="%s" height="44" fill="%s" stroke="%s" stroke-width="3"/>' % (f(cx - gap / 2 + 8), floor + 22, f(gap - 16), C["ui_vari"], INK)
        nm = C.get("otsikko", C["nimi"].split(" (")[0]).upper()
        s += '<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="middle">%s</text>' % (
            f(cx), floor + 54, FONT_T, 24 if len(nm) < 12 else 17, INK, esc(nm))
        s += '<text x="%s" y="%s" font-family="%s" font-size="14" fill="%s" text-anchor="middle">%d cm</text>' % (f(cx), floor + 86, FONT_H, "#6a5a40", C["pituus"])
    return s + "</svg>"

def model_card(C):
    B = P.Body(C)
    d = {k: C[k] for k in ("id", "nimi", "rooli", "ika", "pituus", "kuvaus", "luonne", "siluetti", "lahde", "oletukset", "rekvisiitta",
                           "animaatiot", "mallinnus", "makehuman")}
    d["dialogivari"] = C["ui_vari"]
    d["mittasuhteet_cm"] = dict(pituus=C["pituus"], paan_korkeus=round(B.hh, 1), paan_leveys=round(B.hw * 2, 1), hartialeveys=round(B.sh * 2, 1),
                               vyotaro_leveys=round((B.wa + B.belly) * 2, 1), lantio_leveys=round(B.hi * 2, 1),
                               haara_korkeus=round(C["pituus"] - B.crotch_y, 1), polvi_korkeus=round(C["pituus"] - B.knee_y, 1),
                               rinnan_syvyys=round(B.chest_d * 2, 1), paita_pituudessa=round(C["pituus"] / B.hh, 2))
    d["varit"] = {n: {"srgb": h, "blender_linear": P.lin(h)} for n, h in palette(C)}
    d["vaatteet"] = C["vaatteet"]
    d["hiukset"] = C["hiukset"]
    d["kasvot"] = C["kasvot"]
    if C.get("paahine"):
        d["paahine"] = C["paahine"]
    d["varusteet"] = C.get("varusteet", [])
    d["ilmeet"] = [TUNNE_AVAIN.get(t, t) for t in TUNTEET]
    d["muotokuvat"] = ["muotokuvat/%s_%s.png" % (C["id"].lower(), t) for t in TUNTEET]
    d["tyyli"] = dict(aariviiva_cm=P.LW, aariviiva_vari=INK, varjostus="1–2 sävyn toon + rasteripisteet varjopuolella (valo vasemmalta ylhäältä)")
    return d

def main(out):
    for sub in ("arkit", "muotokuvat", "mallikortit"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for C in HAHMOT:
        cid = C["id"].lower()
        open(os.path.join(out, "arkit", cid + ".svg"), "w", encoding="utf-8").write(sheet_svg(C))
        for emo in TUNTEET:
            open(os.path.join(out, "muotokuvat", "%s_%s.svg" % (cid, emo)), "w", encoding="utf-8").write(portrait_svg(C, emo))
        json.dump(model_card(C), open(os.path.join(out, "mallikortit", cid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(out, "rivikuva.svg"), "w", encoding="utf-8").write(lineup_svg())

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ulos")
