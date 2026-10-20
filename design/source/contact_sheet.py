#!/usr/bin/env python3
"""Build overview sheets of the screen renders, one per group (A, B, C…).

Usage: python3 contact_sheet.py <screens_dir> <out_dir>
Writes <out_dir>/overview-<group>.html; render each with shot.js using the
width and height printed for it.
"""
import os
import sys
from collections import defaultdict

GROUPS = {
    "A": "First-run setup", "B": "Today", "C": "Garden", "D": "Snap & Ask",
    "E": "Plan", "F": "Journal", "G": "Learn and Me",
}
PER_ROW, THUMB_W, THUMB_H, GAP, PAD = 4, 300, 565, 28, 48


def main(screens_dir, out_dir):
    groups = defaultdict(list)
    for name in sorted(os.listdir(screens_dir)):
        if name.endswith(".png") and name[0] in GROUPS:
            groups[name[0]].append(name)
    for letter, files in sorted(groups.items()):
        rows = (len(files) + PER_ROW - 1) // PER_ROW
        width = PAD * 2 + PER_ROW * THUMB_W + (PER_ROW - 1) * GAP
        height = PAD * 2 + 70 + rows * (THUMB_H + 40 + GAP)
        cells = "".join(
            f'<figure><img src="{os.path.relpath(os.path.join(screens_dir, f), out_dir)}">'
            f'<figcaption>{f[:-4].split("-", 1)[0]} · {f[:-4].split("-", 1)[1].replace("-", " ")}</figcaption></figure>'
            for f in files)
        html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@600;800&display=swap" rel="stylesheet">
<style>
body {{ margin: 0; background: #E9ECE4; font-family: Figtree, sans-serif; color: #1F2A20; }}
.wrap {{ width: {width}px; padding: {PAD}px; box-sizing: border-box; }}
h1 {{ margin: 0 0 24px; font-size: 34px; font-weight: 800; }}
.grid {{ display: grid; grid-template-columns: repeat({PER_ROW}, {THUMB_W}px); gap: {GAP}px; }}
figure {{ margin: 0; }}
img {{ width: {THUMB_W}px; height: {THUMB_H}px; object-fit: contain; display: block; }}
figcaption {{ font-size: 17px; font-weight: 800; text-align: center; margin-top: 6px; text-transform: capitalize; }}
</style></head><body><div class="wrap"><h1>{letter} · {GROUPS[letter]}</h1><div class="grid">{cells}</div></div></body></html>"""
        path = os.path.join(out_dir, f"overview-{letter}.html")
        with open(path, "w") as f:
            f.write(html)
        print(path, width, height)


if __name__ == "__main__":
    main(*sys.argv[1:3])
