#!/usr/bin/env python3
"""Turn tools/icon-source.png into the home screen icons.  Run by hand:

       python3 tools/prepare-icon.py

Writes apple-touch-icon.png (180), icon-512.png and favicon-32.png to the repo
root.  iOS rules the output has to obey: PNG, fully opaque (transparency is
composited onto black), and full bleed to the edges with no rounded corners of
its own, because iOS applies its own squircle mask (radius ~22.5% of the icon).
Artwork that already has rounded corners would otherwise be masked twice and
show pale notches, so any flat corner area is flooded with the background colour
first.  Needs Pillow."""
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "icon-source.png")

im = Image.open(SRC)
im = Image.alpha_composite(Image.new("RGBA", im.size, (255,255,255,255)),
                           im.convert("RGBA")).convert("RGB") if im.mode in ("RGBA","LA","P") \
     else im.convert("RGB")

w, h = im.size
if w != h:                                   # centre-crop to a square
    side = min(w, h)
    im = im.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2))
    w = h = side

# background colour, averaged from the middle of each edge
pts = [(w//2, 2), (w//2, h-3), (2, h//2), (w-3, h//2)]
sample = [im.getpixel(p) for p in pts]
bg = tuple(sum(c[i] for c in sample)//len(sample) for i in range(3))

# flood the four corners so the icon reaches the edge in every direction
for corner in [(0,0), (w-1,0), (0,h-1), (w-1,h-1)]:
    if im.getpixel(corner) != bg:
        ImageDraw.floodfill(im, corner, bg, thresh=60)

for path, size in [("apple-touch-icon.png",180), ("icon-512.png",512), ("favicon-32.png",32)]:
    out = im.resize((size,size), Image.LANCZOS)
    assert out.mode == "RGB", "iOS needs an opaque icon"
    out.save(os.path.join(ROOT, path), optimize=True)
print("wrote apple-touch-icon.png, icon-512.png, favicon-32.png  (background %s)" % (bg,))
