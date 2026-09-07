#!/usr/bin/env python3
"""Tile images into a labelled contact sheet for cheap visual triage.

One 4x4 sheet costs ~2,300 image tokens for 16 images (~137 each), against
~3,400 tokens to view a single image at full resolution.

    python3 src/contact_sheet.py OUT.jpg IMG [IMG ...]
    python3 src/contact_sheet.py OUT.jpg --dir path/to/candidates
"""
import sys, pathlib
from PIL import Image, ImageDraw

CELL, COLS, LABEL = 320, 4, 18

def build(paths, out):
    paths = [p for p in paths if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}]
    if not paths:
        print("no images"); return 1
    rows = (len(paths) + COLS - 1) // COLS
    sheet = Image.new("RGB", (CELL * COLS, (CELL + LABEL) * rows), "white")
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        try:
            im = Image.open(p)
            im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
            im.thumbnail((CELL - 8, CELL - 8))
        except Exception as e:
            print(f"  skip {p.name}: {e}", file=sys.stderr); continue
        cx, cy = (i % COLS) * CELL, (i // COLS) * (CELL + LABEL)
        sheet.paste(im, (cx + (CELL - im.width) // 2, cy + (CELL - im.height) // 2))
        draw.text((cx + 4, cy + CELL + 3), p.stem[:40], fill="black")
    sheet.save(out, quality=82)
    tok = (sheet.width * sheet.height) / 750
    print(f"{len(paths)} images -> {out}  {sheet.width}x{sheet.height}  ~{tok:,.0f} tokens ({tok/len(paths):,.0f}/image)")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    out = sys.argv[1]
    if sys.argv[2] == "--dir":
        paths = sorted(pathlib.Path(sys.argv[3]).iterdir())
    else:
        paths = [pathlib.Path(a) for a in sys.argv[2:]]
    sys.exit(build(paths, out))
