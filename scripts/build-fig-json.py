#!/usr/bin/env python3
"""Generate fig2-fig24 JSON with FEN strings."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Positions from page PNG reads + OCR move notation (files: 九=1..一=9 left-to-right)
SPECS: dict[str, tuple[list[tuple[str, str, int, int]], str, str]] = {
    'fig2': (
        [
            ('black', 'A', 0, 5),
            ('black', 'A', 2, 4),
            ('black', 'K', 2, 5),
            ('red', 'N', 4, 1),
            ('red', 'K', 9, 4),
        ],
        'w',
        'page-017.png',
    ),
    'fig3': (
        [
            ('black', 'K', 0, 4),
            ('black', 'B', 2, 3),
            ('red', 'N', 3, 9),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-018.png',
    ),
    'fig4': (
        [
            ('black', 'K', 1, 6),
            ('red', 'N', 3, 6),
            ('black', 'B', 4, 3),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-019.png',
    ),
    'fig5': (
        [
            ('black', 'K', 1, 6),
            ('black', 'P', 3, 3),
            ('red', 'N', 7, 9),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-019.png',
    ),
    'fig6': (
        [
            ('black', 'K', 0, 5),
            ('black', 'P', 4, 5),
            ('red', 'N', 6, 9),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-020.png',
    ),
    'fig7': (
        [
            ('black', 'K', 0, 5),
            ('black', 'C', 0, 7),
            ('black', 'A', 2, 4),
            ('black', 'A', 2, 6),
            ('red', 'N', 3, 3),
            ('red', 'K', 9, 4),
        ],
        'w',
        'page-021.png',
    ),
    'fig8': (
        [
            ('black', 'C', 0, 5),
            ('black', 'A', 1, 5),
            ('black', 'K', 2, 4),
            ('black', 'A', 2, 6),
            ('black', 'P', 4, 5),
            ('red', 'N', 2, 3),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-021.png',
    ),
    'fig9': (
        [
            ('black', 'K', 0, 5),
            ('black', 'R', 5, 7),
            ('red', 'N', 8, 4),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-022.png',
    ),
    'fig10': (
        [
            ('black', 'K', 0, 6),
            ('black', 'R', 5, 7),
            ('red', 'N', 3, 5),
            ('red', 'B', 9, 3),
            ('red', 'K', 9, 4),
        ],
        'w',
        'page-022.png',
    ),
    'fig11': (
        [
            ('black', 'K', 0, 5),
            ('red', 'B', 2, 3),
            ('red', 'B', 2, 6),
            ('red', 'N', 3, 5),
            ('black', 'R', 5, 8),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-023.png',
    ),
    'fig12': (
        [
            ('black', 'K', 0, 5),
            ('black', 'N', 3, 5),
            ('black', 'B', 4, 3),
            ('black', 'B', 4, 5),
            ('red', 'R', 7, 5),
            ('red', 'K', 9, 4),
        ],
        'w',
        'page-023.png',
    ),
    'fig13': (
        [
            ('black', 'K', 0, 5),
            ('black', 'B', 4, 7),
            ('black', 'R', 6, 7),
            ('red', 'N', 5, 7),
            ('red', 'P', 6, 5),
            ('red', 'B', 7, 5),
            ('red', 'K', 8, 5),
        ],
        'w',
        'page-024.png',
    ),
    'fig14': (
        [
            ('black', 'K', 1, 4),
            ('black', 'N', 3, 3),
            ('black', 'P', 7, 6),
            ('red', 'P', 6, 2),
            ('red', 'A', 8, 4),
            ('red', 'K', 9, 5),
            ('red', 'A', 8, 6),
        ],
        'w',
        'page-025.png',
    ),
    'fig15': (
        [
            ('black', 'B', 0, 3),
            ('black', 'A', 0, 4),
            ('black', 'K', 0, 5),
            ('black', 'A', 1, 5),
            ('black', 'B', 2, 5),
            ('red', 'P', 1, 6),
            ('red', 'N', 4, 3),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-025.png',
    ),
    'fig16': (
        [
            ('black', 'K', 0, 5),
            ('black', 'N', 5, 5),
            ('black', 'P', 4, 6),
            ('red', 'B', 7, 3),
            ('red', 'B', 7, 7),
            ('red', 'A', 8, 4),
            ('red', 'A', 8, 6),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-026.png',
    ),
    'fig17': (
        [
            ('black', 'K', 0, 5),
            ('black', 'N', 4, 8),
            ('black', 'P', 7, 6),
            ('red', 'K', 8, 4),
            ('red', 'A', 9, 5),
            ('red', 'B', 7, 5),
            ('red', 'B', 7, 9),
        ],
        'w',
        'page-027.png',
    ),
    'fig18': (
        [
            ('black', 'K', 0, 5),
            ('black', 'N', 8, 9),
            ('black', 'P', 8, 4),
            ('red', 'B', 5, 3),
            ('red', 'A', 7, 5),
            ('red', 'A', 8, 5),
            ('red', 'K', 8, 6),
        ],
        'w',
        'page-028.png',
    ),
    'fig19': (
        [
            ('black', 'K', 0, 6),
            ('black', 'A', 1, 5),
            ('black', 'A', 2, 4),
            ('black', 'B', 2, 1),
            ('red', 'P', 2, 5),
            ('red', 'N', 3, 6),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-028.png',
    ),
    'fig20': (
        [
            ('black', 'K', 0, 4),
            ('black', 'C', 2, 3),
            ('black', 'B', 4, 7),
            ('red', 'P', 1, 5),
            ('red', 'N', 3, 3),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-029.png',
    ),
    'fig21': (
        [
            ('black', 'K', 0, 5),
            ('red', 'C', 4, 5),
            ('black', 'N', 6, 8),
            ('red', 'K', 7, 4),
            ('black', 'P', 8, 5),
        ],
        'w',
        'page-030.png',
    ),
    'fig22': (
        [
            ('black', 'A', 0, 4),
            ('black', 'K', 0, 5),
            ('red', 'N', 2, 3),
            ('red', 'P', 2, 5),
            ('black', 'N', 2, 7),
            ('red', 'B', 7, 5),
            ('red', 'K', 8, 6),
        ],
        'w',
        'page-031.png',
    ),
    'fig23': (
        [
            ('black', 'K', 0, 5),
            ('black', 'A', 0, 6),
            ('black', 'C', 1, 1),
            ('red', 'P', 2, 5),
            ('red', 'N', 3, 6),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-032.png',
    ),
    'fig24': (
        [
            ('black', 'K', 0, 4),
            ('black', 'B', 2, 5),
            ('black', 'B', 2, 9),
            ('red', 'N', 4, 4),
            ('red', 'P', 4, 7),
            ('red', 'K', 9, 5),
        ],
        'w',
        'page-033.png',
    ),
}


def main() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location('fen_helper', Path(__file__).resolve().parent / 'fen-helper.py')
    fh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fh)
    build_fen = fh.build_fen

    out: dict[str, dict] = {}
    for i in range(2, 25):
        key = f'fig{i}'
        pieces, stm, page = SPECS[key]
        fen = build_fen(pieces, stm)
        entry = {
            'pieces': [list(p) for p in pieces],
            'stm': stm,
            'fen': fen,
            'page': page,
        }
        out[key] = entry
        out[f'o-m-{i:02d}'] = entry
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
