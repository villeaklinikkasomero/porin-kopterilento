import sys
from PIL import Image, ImageFilter, ImageChops, ImageOps
sv, g, out = sys.argv[1:4]
A = Image.open(sv).convert('RGB').resize((800, 450)); Bm = Image.open(g).convert('RGB').resize((800, 450))
e = Bm.convert('L').filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
wire = A.copy(); red = Image.new('RGB', A.size, (255, 40, 40)); wire.paste(red, (0, 0), e)   # model edges in red on the photo
c = Image.new('RGB', (800, 900)); c.paste(Bm, (0, 0)); c.paste(wire, (0, 450)); c.save(out, quality=88)
