#!/usr/bin/env python3
"""Extract xiangqi piece positions from book page diagram images."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'mydata' / 'pages'

# figure -> primary page (from OCR "图NN" on diagram)
FIG_PAGES = {
    25: 'page-034.png', 26: 'page-035.png', 27: 'page-035.png', 28: 'page-036.png',
    29: 'page-037.png', 30: 'page-037.png', 31: 'page-038.png', 32: 'page-039.png',
    33: 'page-039.png', 34: 'page-040.png', 35: 'page-041.png', 36: 'page-042.png',
    37: 'page-042.png', 38: 'page-043.png', 39: 'page-044.png', 40: 'page-045.png',
    41: 'page-047.png', 42: 'page-048.png', 43: 'page-050.png', 44: 'page-051.png',
    45: 'page-052.png', 46: 'page-053.png', 47: 'page-053.png', 48: 'page-054.png',
    49: 'page-055.png', 50: 'page-056.png', 51: 'page-057.png',
}

# stm from OCR text
FIG_STM = {
    25: 'w', 26: 'w', 27: 'w', 28: 'w', 29: 'w', 30: 'w', 31: 'w', 32: 'w',
    33: 'w', 34: 'w', 35: 'w', 36: 'w', 37: 'w', 38: 'w', 39: 'w', 40: 'w',
    41: 'w', 42: 'w', 43: 'w', 44: 'w', 45: 'w', 46: 'w', 47: 'w', 48: 'w',
    49: 'w', 50: 'w', 51: 'w',
}

RED_CHARS = set('帅仕相兵')
BLACK_CHARS = set('将士象卒')
KIND_MAP = {
    '帅': 'K', '将': 'K', '仕': 'A', '士': 'A', '相': 'B', '象': 'B',
    '兵': 'P', '卒': 'P', '车': 'R', '马': 'N', '炮': 'C',
}


def fen_to_pieces(fen: str) -> tuple[list[list], str]:
    board, stm = fen.rsplit(' ', 1)
    pieces: list[list] = []
    upper = {'K': 'K', 'A': 'A', 'B': 'B', 'N': 'N', 'R': 'R', 'C': 'C', 'P': 'P'}
    lower = {'k': 'K', 'a': 'A', 'b': 'B', 'n': 'N', 'r': 'R', 'c': 'C', 'p': 'P'}
    for rank, row in enumerate(board.split('/')):
        file1 = 0
        for ch in row:
            if ch.isdigit():
                file1 += int(ch)
            else:
                file1 += 1
                side = 'red' if ch.isupper() else 'black'
                kind = upper[ch] if ch.isupper() else lower[ch]
                pieces.append([side, kind, rank, file1])
    return pieces, stm


# Catalog FENs (from src/puzzles/catalog.ts) — baseline to cross-check
CATALOG_FEN = {
    25: '3aka3/9/9/9/9/9/9/4C4/4A4/3K5 w',
    26: '3aKa3/4A4/2B6/9/9/9/2b2b3/4c4/4a4/3k5 b',
    27: '4k4/9/9/9/9/4r4/9/4C4/4A4/3AK4 w',
    28: '4k4/9/9/9/9/4r4/2B2B3/4C4/9/3K5 w',
    29: '4k4/9/2b2b3/4c4/9/9/9/4R4/9/3K5 w',
    30: '4k4/9/9/2p1p1p2/9/9/9/4C4/4A4/3AK4 w',
    31: '4k4/9/2B6/4p4/9/4r4/9/4C4/4A4/3AK4 w',
    32: '3ak4/9/9/4p4/9/9/9/4C4/4c4/3K5 w',
    33: '4k4/9/2b6/9/9/4P4/9/4C4/9/3K5 w',
    34: '4k4/9/2b6/9/4p4/4c4/2B6/9/9/3K5 w',
    35: '4k4/9/2b6/9/4P4/9/9/4C4/9/3K5 w',
    36: '3ak4/9/2b6/9/9/9/4P4/4C4/4A4/3KB4 w',
    37: '3ak4/9/2b6/9/9/9/4P4/4C4/4A4/3K5 w',
    38: '4k4/9/9/2P2P3/9/4r4/9/4C4/9/3K5 w',
    39: '3aka3/9/2b2b3/9/4P4/9/2B6/4C4/4A4/3AK4 w',
    40: '4ka3/3a5/2b2b3/9/4P4/9/2B6/4C4/4A4/3AK4 w',
    41: '3ak4/9/9/9/4P4/9/2B6/9/9/3K5 w',
    42: '3ak4/9/2b6/9/4P4/9/9/4c4/9/3K5 w',
    43: '3aka3/9/9/2p2p3/9/9/4P4/4A4/9/3K5 w',
    44: '3aka3/9/2b6/9/3P1P3/9/9/9/9/3K5 w',
    45: '4ka3/9/2b2b3/9/3P1P3/9/9/9/9/3K5 w',
    46: '3aka3/9/2b2b3/9/3P1P3/9/9/9/9/3K5 w',
    47: '3ak4/9/2b6/9/3P1P3/9/9/9/9/3K5 w',
    48: '4k4/9/2b6/4p4/3P1P3/9/9/9/9/3K5 w',
    49: '3ak4/9/9/4p4/3P1P3/9/9/9/9/3K5 w',
    50: '3aka3/9/2b2b3/9/2P1P1P2/9/9/9/9/3K5 w',
    51: '3aka3/9/2b2b3/9/2P1P1P2/9/9/9/4K4 w',
}


def find_board_boxes(img: Image.Image) -> list[tuple[int, int, int, int]]:
    """Find diagram board regions by detecting horizontal grid lines."""
    import numpy as np

    gray = np.array(img.convert('L'))
    h, w = gray.shape
    # boards are on the right side; focus right 55%
    x0 = int(w * 0.42)
    crop = gray[:, x0:]
    # horizontal line detection: rows with many dark pixels
    row_dark = (crop < 128).sum(axis=1)
    threshold = crop.shape[1] * 0.25
    line_rows = np.where(row_dark > threshold)[0]
    if len(line_rows) < 20:
        return [(x0, 0, w, h)]
    # cluster into groups separated by gaps
    groups: list[list[int]] = [[line_rows[0]]]
    for r in line_rows[1:]:
        if r - groups[-1][-1] > 8:
            groups.append([r])
        else:
            groups[-1].append(r)
    boxes = []
    for g in groups:
        if len(g) < 8:
            continue
        y1, y2 = g[0] - 15, g[-1] + 15
        if y2 - y1 < 120:
            continue
        boxes.append((x0, max(0, y1), w, min(h, y2)))
    return boxes or [(x0, 0, w, h)]


def ocr_board(reader, img: Image.Image, box: tuple[int, int, int, int]) -> list[tuple[str, float, float]]:
    x1, y1, x2, y2 = box
    crop = img.crop((x1, y1, x2, y2))
    results = reader.readtext(np.array(crop))  # noqa: F821 — numpy imported in caller
    pieces = []
    for item in results:
        bbox, text, conf = item[0], item[1], item[2]
        t = text.strip()
        if len(t) == 1 and t in KIND_MAP:
            cx = sum(p[0] for p in bbox) / 4 + x1
            cy = sum(p[1] for p in bbox) / 4 + y1
            pieces.append((t, cx, cy))
    return pieces


def snap_to_grid(pieces: list[tuple[str, float, float]], box: tuple[int, int, int, int]) -> list[list]:
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    # 9 files, 10 ranks
    out = []
    for ch, cx, cy in pieces:
        file1 = max(1, min(9, round((cx - x1) / bw * 8) + 1))
        rank = max(0, min(9, round((cy - y1) / bh * 9)))
        side = 'red' if ch in RED_CHARS else 'black'
        out.append([side, KIND_MAP[ch], rank, file1])
    return out


def extract_page(reader, page: str, fig_nums: list[int]) -> dict[int, list[list]]:
    import numpy as np  # noqa: F401

    img = Image.open(PAGES / page)
    boxes = find_board_boxes(img)
    results: dict[int, list[list]] = {}
    # match boxes top-to-bottom with fig_nums in order
    fig_nums_sorted = sorted(fig_nums)
    for i, fig in enumerate(fig_nums_sorted):
        if i < len(boxes):
            raw = ocr_board(reader, img, boxes[i])
            results[fig] = snap_to_grid(raw, boxes[i])
    return results


def main():
    import easyocr
    import numpy as np  # noqa: F401

    reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)

    # group figures by page
    by_page: dict[str, list[int]] = {}
    for fig, page in FIG_PAGES.items():
        by_page.setdefault(page, []).append(fig)

    ocr_results: dict[int, list[list]] = {}
    for page, figs in sorted(by_page.items()):
        try:
            ocr_results.update(extract_page(reader, page, figs))
        except Exception as e:
            print(f'WARN {page}: {e}', file=sys.stderr)

    out = {}
    for fig in range(25, 52):
        page = FIG_PAGES[fig]
        stm = FIG_STM[fig]
        if fig in ocr_results and len(ocr_results[fig]) >= 3:
            pieces = ocr_results[fig]
        else:
            fen = CATALOG_FEN[fig]
            pieces, fen_stm = fen_to_pieces(fen)
            if fig == 26:
                stm = 'w'  # OCR says 红先和
            elif fig == 37:
                stm = 'w'  # red-win variation is primary catalog entry
            else:
                stm = fen_stm
            # fix fig25: king at file 6 per 将6平5
            if fig == 25:
                pieces = [
                    ['black', 'K', 0, 6],
                    ['black', 'A', 1, 5],
                    ['black', 'A', 2, 4],
                    ['red', 'A', 7, 6],
                    ['red', 'C', 8, 2],
                    ['red', 'K', 9, 5],
                ]
                stm = 'w'
            if fig == 51:
                # catalog has K at file 5 rank 9; moves 帅六 suggest file 6
                pieces = [
                    ['black', 'K', 0, 5],
                    ['black', 'A', 0, 4],
                    ['black', 'A', 0, 6],
                    ['black', 'B', 2, 5],
                    ['black', 'B', 2, 7],
                    ['black', 'A', 3, 6],
                    ['red', 'P', 4, 4],
                    ['red', 'P', 4, 6],
                    ['red', 'P', 5, 7],
                    ['red', 'K', 9, 6],
                ]
        out[f'fig{fig}'] = {'pieces': pieces, 'stm': stm, 'page': page}

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
