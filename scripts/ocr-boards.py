#!/usr/bin/env python3
"""OCR xiangqi diagrams from book page PNGs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'mydata' / 'pages'

FIG_PAGES = {
    25: ('page-034.png', 0), 26: ('page-035.png', 0), 27: ('page-035.png', 1),
    28: ('page-036.png', 0), 29: ('page-037.png', 0), 30: ('page-037.png', 1),
    31: ('page-038.png', 0), 32: ('page-039.png', 0), 33: ('page-039.png', 1),
    34: ('page-040.png', 0), 35: ('page-041.png', 0), 36: ('page-042.png', 0),
    37: ('page-042.png', 1), 38: ('page-043.png', 0), 39: ('page-044.png', 0),
    40: ('page-045.png', 0), 41: ('page-047.png', 0), 42: ('page-048.png', 0),
    43: ('page-050.png', 0), 44: ('page-051.png', 0), 45: ('page-052.png', 0),
    46: ('page-053.png', 0), 47: ('page-053.png', 1), 48: ('page-054.png', 0),
    49: ('page-055.png', 0), 50: ('page-056.png', 0), 51: ('page-057.png', 0),
}

RED = set('帅仕相兵')
KIND = {'帅': 'K', '将': 'K', '仕': 'A', '士': 'A', '相': 'B', '象': 'B',
        '兵': 'P', '卒': 'P', '车': 'R', '马': 'N', '炮': 'C'}


def find_boards(gray: np.ndarray) -> list[tuple[int, int, int, int]]:
    h, w = gray.shape
    x0 = int(w * 0.40)
    crop = gray[:, x0:]
    row_dark = (crop < 140).sum(axis=1)
    thr = crop.shape[1] * 0.22
    lines = np.where(row_dark > thr)[0]
    if len(lines) < 10:
        return [(x0, 0, w, h)]
    groups: list[list[int]] = [[lines[0]]]
    for r in lines[1:]:
        if r - groups[-1][-1] > 10:
            groups.append([r])
        else:
            groups[-1].append(r)
    boxes = []
    for g in groups:
        if len(g) < 10:
            continue
        y1, y2 = max(0, g[0] - 20), min(h, g[-1] + 20)
        if y2 - y1 < 100:
            continue
        boxes.append((x0, y1, w, y2))
    return boxes or [(x0, 0, w, h)]


def ocr_board(reader, img: Image.Image, box: tuple[int, int, int, int]) -> list[list]:
    x1, y1, x2, y2 = box
    crop = img.crop(box)
    cw, ch = crop.size
    results = reader.readtext(np.array(crop), paragraph=False)
    pieces = []
    for bbox, text, _conf in results:
        t = ''.join(c for c in text if c in KIND)
        if not t:
            continue
        ch = t[0]
        cx = sum(p[0] for p in bbox) / 4
        cy = sum(p[1] for p in bbox) / 4
        file1 = max(1, min(9, round(cx / cw * 8) + 1))
        rank = max(0, min(9, round(cy / ch * 9)))
        side = 'red' if ch in RED else 'black'
        pieces.append([side, KIND[ch], rank, file1])
    return pieces


def main():
    import easyocr
    reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)

    by_page: dict[str, list[tuple[int, int]]] = {}
    for fig, (page, idx) in FIG_PAGES.items():
        by_page.setdefault(page, []).append((fig, idx))

    extracted: dict[int, list[list]] = {}
    for page, entries in sorted(by_page.items()):
        entries.sort(key=lambda x: x[1])
        img = Image.open(PAGES / page)
        gray = np.array(img.convert('L'))
        boxes = find_boards(gray)
        for fig, idx in entries:
            if idx < len(boxes):
                pcs = ocr_board(reader, img, boxes[idx])
                if len(pcs) >= 3:
                    extracted[fig] = pcs
                    print(f'fig{fig}: {len(pcs)} pieces from {page}[{idx}]', file=sys.stderr)

    print(json.dumps({str(k): v for k, v in sorted(extracted.items())}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
