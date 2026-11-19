"""1726 Pohjoiskauppatori 3, Antinkatu gable (SV 19.11.2026, panos Antinkatu 10: 8.93,146.5 and 6.51,136.01).

1726 is a photo-facade building (index.html PHS, drawn by the game, not baked), so its gable is a drawn texture, not facades.json:
    python3 tools/rautalanka/facades/f1726.py [game folder]   ->  ph_1726g.jpg  (512 x 1024, the whole gable once: 12.59 m x 24.2 m)
index.html: PHS[1726] second style { t: 'ph_1726g', bw: 12.59, cut: -17.612 } (walls west of the cut line = the gable only) and a thin
end-wall fin that continues the gable plane 1.42 m north to Antinkatu 10 (1725): the scanned shell is 11.09 m wide and left a slot there,
the real tiled gable is 12.2 m.  Nothing of the Street View image is used: only measures, colours and materials.

Drawn in w = metres from the north end of the fin (0 .. 12.59); the game's wall coordinate is u = w - 1.5 (the texture is rolled by 1.5 m,
the fin samples u < 0 through the horizontal repeat).  Measured on the rectified views (raw s -1.0..11.2, z 0.85..21.4):
  w = (s + 1.0) * 1.032;  street floor z' = 1.316 (z - 0.85) up to the tile edge at 3.75 (as high as the photo strip's street floor
  on the other walls), upper floors on the photo strip's storey lines (4.48 + 3.287 i), so the rows meet round the corner.
  terracotta tiles 12 across, 7 rows per storey; 6 rows of 2 windows near the north end (1.0 and 1.5 raw m wide), the south 60 % blank;
  black pub front: fascia, 3 window bays, black panels; open corner arcade with a black-tiled round column.
The building is drawn 24.2 m high (LoD2 eave); on the rectified views the tiled wall is only about 20.5 m (storeys 2.9 m): not changed here."""
import sys, os, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 512, 1024; LEN, EAVE = 12.59, 24.2; K = 1.032; ROLL = 1.5
random.seed(1726)
im = Image.new('RGB', (W, H), (144, 90, 76)); d = ImageDraw.Draw(im)
X = lambda u: u / LEN * W
Y = lambda z: H - z / EAVE * H
def rect(u0, u1, z0, z1, c): d.rectangle([round(X(u0)), round(Y(z1)), round(X(u1)) - 1, round(Y(z0)) - 1], fill=c)

# ---- terracotta tiles
TB = 3.75; tw = LEN / 12; th = 3.287 / 7
r = 0
while TB + r * th < EAVE:
    for c in range(12):
        k = random.randint(-7, 7); g = random.randint(-3, 3)
        rect(c * tw, (c + 1) * tw, TB + r * th, min(EAVE, TB + (r + 1) * th), (144 + k, 90 + k // 2 + g, 76 + k // 2 + g))
    r += 1
for rr in range(r + 1):
    y = round(Y(TB + rr * th)); d.line([(0, y), (W, y)], fill=(102, 62, 52))
for c in range(13):
    x = min(W - 1, round(X(c * tw))); d.line([(x, Y(EAVE)), (x, Y(TB))], fill=(106, 64, 54))
rect(0, LEN, EAVE - 0.14, EAVE, (62, 60, 60))                                   # sheet-metal coping

# ---- windows: dark recessed frames, grey glass, blinds in some
for i in range(6):
    z0 = 5.2 + 3.287 * i; z1 = z0 + 1.55
    for (u0, u1, mull) in ((1.56 * K, 2.60 * K, None), (3.60 * K, 5.14 * K, 0.68)):
        rect(u0 - 0.05, u1 + 0.05, z0 - 0.07, z0, (92, 52, 42))                  # sill shadow line
        rect(u0, u1, z0, z1, (26, 26, 28))
        gl = (66 + 4 * i, 74 + 4 * i, 82 + 4 * i)
        rect(u0 + 0.09, u1 - 0.09, z0 + 0.09, z1 - 0.2, gl)
        rect(u0 + 0.09, u1 - 0.09, z1 - 0.34, z1 - 0.2, (40, 42, 46))            # shade of the reveal on the glass
        if random.random() < 0.55: rect(u0 + 0.09, u1 - 0.09, z0 + 0.09, z0 + random.choice((0.5, 0.75, 1.0)), (176, 176, 170))   # blind / curtain
        if mull:
            m = u0 + (u1 - u0) * mull; rect(m - 0.04, m + 0.04, z0, z1, (26, 26, 28))

# ---- street floor: black pub front and the open corner arcade
rect(0, LEN, 0, TB, (22, 23, 25))
rect(0, LEN, 2.76, 2.82, (58, 58, 56))                                          # light edge under the fascia
for (u0, u1, lit) in ((1.0 * K, 4.3 * K, False), (4.65 * K, 7.9 * K, True), (8.1 * K, 9.45 * K, True)):
    rect(u0, u1, 1.32, 2.76, (36, 38, 40) if not lit else (92, 86, 66))
    if lit:
        rect(u0, u1, 1.32, 1.75, (122, 112, 86)); rect(u0, u1, 2.5, 2.76, (52, 50, 40))
        n = 2 if u1 - u0 > 2 else 1
        for k in range(1, n): rect(u0 + (u1 - u0) * k / n - 0.03, u0 + (u1 - u0) * k / n + 0.03, 1.32, 2.76, (22, 23, 25))
    else: rect(u0, u1, 2.3, 2.76, (28, 29, 31))
    rect(u0, u1, 0.16, 1.26, (30, 31, 34)); rect(u0 + 0.12, u1 - 0.12, 0.3, 1.12, (25, 26, 28))      # panel under the window
rect(9.6 * K, LEN - 0.05, 0, 3.62, (12, 12, 14))                                   # arcade: dark recess
rect(9.6 * K, LEN - 0.05, 0, 0.5, (30, 30, 30))
cu0, cu1 = 10.85 * K, 11.45 * K                                                          # black-tiled round column
for k in range(12):
    f = (k + 0.5) / 12; sh = int(26 + 34 * max(0, 1 - abs(f - 0.38) * 2.6))
    rect(cu0 + (cu1 - cu0) * k / 12, cu0 + (cu1 - cu0) * (k + 1) / 12, 0, 3.62, (sh, sh + 1, sh + 3))
z = 0.0
while z < 3.62:
    d.line([(X(cu0), Y(z)), (X(cu1), Y(z))], fill=(16, 16, 18)); z += 0.16
rect(0, LEN, 0, 0.12, (46, 46, 48))                                             # plinth
rect(11.5 * K, 11.95 * K, 4.1, 4.22, (214, 214, 208))                                 # street name plate

im = im.filter(ImageFilter.GaussianBlur(0.45))
from PIL import ImageChops
im = ImageChops.offset(im, -round(ROLL / LEN * W), 0)                             # u = 0 (north end of the scanned wall) at the left edge
out = os.path.join(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pori', 'ph_1726g.jpg')
im.save(out, quality=92); print(out, im.size)
