#!/usr/bin/env python3
"""Regenerate the home screen icons.  Run by hand, never at deploy time:
       python3 tools/make-icons.py [book-ink|book-juna|spines-ink|spines-paper]
   Writes apple-touch-icon.png (180), icon-512.png and favicon-32.png into the
   repo root.  iOS rules the output has to obey: PNG, fully opaque (transparency
   is composited onto black), full bleed with no rounded corners of its own
   because iOS applies the squircle mask itself.  Needs Pillow."""
import sys
from PIL import Image, ImageDraw

S = 720                                   # draw at 4x, downsample for clean edges
INK=(27,33,24); PAPER=(243,245,240); GOLD=(176,125,24)
GOLD_L=(214,160,52); JUNA=(122,62,157); ARTUS=(31,122,92); SOFT=(216,221,211)

def canvas(bg):
    im = Image.new("RGB", (S, S), bg)     # RGB, not RGBA: no alpha channel at all
    return im, ImageDraw.Draw(im)

def book(bg=INK):
    """An open book with a gold ribbon."""
    im, d = canvas(bg); cx = S//2; out = 80
    d.polygon([(out,292),(cx-14,244),(cx-14,552),(out,504)], fill=PAPER)
    d.polygon([(S-out,292),(cx+14,244),(cx+14,552),(S-out,504)], fill=PAPER)
    for k in range(2):
        y = 372 + k*78
        d.line([(152,y+10-k*6),(cx-64,y-24-k*6)], fill=SOFT, width=15)
        d.line([(S-152,y+10-k*6),(cx+64,y-24-k*6)], fill=SOFT, width=15)
    d.rectangle([cx-16,238,cx+16,560], fill=GOLD)
    d.rectangle([cx-16,560,cx+16,644], fill=GOLD_L)
    d.polygon([(cx-16,644),(cx,610),(cx+16,644)], fill=bg)
    return im

def spines(bg=INK):
    """Three books rising: Juna's purple, Artus's green, and gold."""
    im, d = canvas(bg); base = S-96; x = 86; gap = 30
    for w, h, col in [(150,318,JUNA),(162,428,ARTUS),(176,538,GOLD)]:
        d.rounded_rectangle([x,base-h,x+w,base], radius=20, fill=col)
        d.rectangle([x,base-h+74,x+w,base-h+114], fill=PAPER)
        d.line([(x+28,base-h+178),(x+w-28,base-h+178)], fill=PAPER, width=12)
        d.line([(x+28,base-h+228),(x+w-46,base-h+228)], fill=PAPER, width=12)
        x += w + gap
    return im

DESIGNS = {"book-ink":  lambda: book(INK),
           "book-juna": lambda: book(JUNA),
           "spines-ink":   lambda: spines(INK),
           "spines-paper": lambda: spines(PAPER)}

name = sys.argv[1] if len(sys.argv) > 1 else "spines-ink"
if name not in DESIGNS:
    sys.exit("pick one of: " + ", ".join(DESIGNS))
master = DESIGNS[name]()
for path, size in [("apple-touch-icon.png",180), ("icon-512.png",512), ("favicon-32.png",32)]:
    img = master.resize((size,size), Image.LANCZOS)
    assert img.mode == "RGB", "iOS needs an opaque icon"
    img.save(path, optimize=True)
print("wrote apple-touch-icon.png, icon-512.png, favicon-32.png from " + name)
