#!/usr/bin/env python3
"""Extract piece positions from book page board diagrams."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'mydata' / 'pages'

# figure -> (page file, approximate board bbox as fraction of image w,h)
# bbox: (x0, y0, x1, y1) normalized 0-1, tuned per page layout
FIG_PAGES = {f'fig{i}': f'page-{15 + i:03d}.png' for i in range(2, 25)}

PIECE_CHARS = {
    '帅': ('red', 'K'),
    '将': ('black', 'K'),
    '仕': ('red', 'A'),
    '士': ('black', 'A'),
    '相': ('red', 'B'),
    '象': ('black', 'B'),
    '马': ('red', 'N'),
    '馬': ('red', 'N'),
    '炮': ('red', 'C'),
    '砲': ('red', 'C'),
    '车': ('red', 'R'),
    '車': ('red', 'R'),
    '兵': ('red', 'P'),
    '卒': ('black', 'P'),
}

# Black pieces use same char with inverted color detection


def find_board_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    """Locate board by finding dense grid of dark lines."""
    w, h = img.size
    gray = img.convert('L')
    px = gray.load()

    # Scan for horizontal band with many dark pixels (board lines)
    best = None
    for y0_frac in [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35, 0.40, 0.45, 0.50]:
        for x0_frac in [0.45, 0.50, 0.52, 0.55, 0.58, 0.60]:
            x0 = int(w * x0_frac)
            y0 = int(h * y0_frac)
            x1 = min(w, x0 + int(w * 0.42))
            y1 = min(h, y0 + int(h * 0.38))
            if x1 - x0 < 100 or y1 - y0 < 100:
                continue
            dark = 0
            total = 0
            for y in range(y0, y1, 3):
                for x in range(x0, x1, 3):
                    total += 1
                    if px[x, y] < 120:
                        dark += 1
            ratio = dark / total
            score = ratio * (x1 - x0) * (y1 - y0)
            if best is None or score > best[0]:
                best = (score, x0, y0, x1, y1)
    if best is None:
        # fallback right-side board
        return int(w * 0.52), int(h * 0.12), int(w * 0.95), int(h * 0.50)
    _, x0, y0, x1, y1 = best
    return x0, y0, x1, y1


def detect_pieces(img: Image.Image, bbox: tuple[int, int, int, int]) -> list[tuple[str, str, int, int]]:
    x0, y0, x1, y1 = bbox
    board = img.crop(bbox)
    bw, bh = board.size
    cell_w = bw / 8  # 9 files = 8 gaps
    cell_h = bh / 9  # 10 ranks = 9 gaps

    pieces: list[tuple[str, str, int, int]] = []
    rgb = board.convert('RGB')
    px = rgb.load()

    for rank in range(10):
        for file1 in range(1, 10):
            cx = int((file1 - 1) * cell_w)
            cy = int(rank * cell_h)
            # sample circle center region
            rs, gs, bs = 0, 0, 0
            n = 0
            dark = 0
            for dy in range(-8, 9):
                for dx in range(-8, 9):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < bw and 0 <= y < bh and dx * dx + dy * dy <= 64:
                        r, g, b = px[x, y]
                        rs += r
                        gs += g
                        bs += b
                        n += 1
                        if r + g + b < 280:
                            dark += 1
            if n == 0 or dark / n < 0.15:
                continue
            avg = (rs / n, gs / n, bs / n)
            # filled black circle vs hollow red-ish circle
            side = 'black' if avg[0] < 100 and avg[1] < 100 and avg[2] < 100 else 'red'
            # OCR-free: classify by local contrast pattern — use brightness
            if sum(avg) / 3 < 110:
                side = 'black'
            elif sum(avg) / 3 > 180:
                side = 'red'
            else:
                # mixed — skip uncertain
                continue

            # Heuristic kind from neighborhood ink density patterns won't work without OCR.
            # Store placeholder; real extraction needs tesseract on cropped glyphs.
            pieces.append((side, '?', rank, file1))

    return pieces


def main() -> None:
    fig = sys.argv[1] if len(sys.argv) > 1 else 'fig2'
    page = FIG_PAGES[fig]
    img = Image.open(PAGES / page)
    bbox = find_board_bbox(img)
    print(json.dumps({'fig': fig, 'page': page, 'bbox': bbox}, ensure_ascii=False))


if __name__ == '__main__':
    main()
