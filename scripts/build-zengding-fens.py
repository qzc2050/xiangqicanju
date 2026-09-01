#!/usr/bin/env python3
"""Build FEN JSON for 增订 section puzzles from piece coordinates."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'fen_helper', Path(__file__).resolve().parent / 'fen-helper.py'
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build_fen = _mod.build_fen

# (side, kind, rank, file1)  rank 0=top, file 1-9 LTR
PUZZLES: dict[str, tuple[list[tuple[str, str, int, int]], str, str, str]] = {
    # 马类 图3-14
    'x-m-03': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 4), ('black', 'B', 2, 3),
         ('red', 'N', 6, 5), ('red', 'P', 7, 6), ('red', 'K', 9, 4)],
        'w', '082', '图3',
    ),
    'x-m-04': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 4), ('black', 'A', 1, 6),
         ('black', 'B', 2, 3), ('red', 'N', 6, 5), ('red', 'P', 7, 7),
         ('red', 'K', 9, 4)],
        'w', '083', '图5',
    ),
    'x-m-05': (
        [('black', 'K', 1, 5), ('black', 'A', 0, 4), ('black', 'B', 2, 3),
         ('red', 'N', 6, 5), ('red', 'P', 7, 5), ('red', 'K', 9, 4)],
        'w', '084', '图6',
    ),
    'x-m-06': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 4), ('black', 'B', 2, 3),
         ('red', 'N', 6, 5), ('red', 'P', 4, 5), ('red', 'K', 9, 4)],
        'w', '085', '图7',
    ),
    'x-m-07': (
        [('black', 'K', 0, 4), ('black', 'A', 1, 5), ('black', 'A', 2, 6),
         ('black', 'B', 3, 3), ('red', 'N', 6, 5), ('red', 'P', 1, 6),
         ('red', 'K', 9, 5)],
        'w', '086', '图8',
    ),
    'x-m-08': (
        [('black', 'K', 1, 4), ('black', 'A', 0, 6), ('black', 'B', 2, 5),
         ('black', 'B', 4, 3), ('red', 'N', 4, 2), ('red', 'P', 1, 6),
         ('red', 'K', 9, 5)],
        'w', '087', '图9',
    ),
    'x-m-09': (
        [('black', 'K', 1, 4), ('black', 'A', 0, 5), ('black', 'B', 2, 9),
         ('black', 'B', 3, 7), ('red', 'N', 4, 6), ('red', 'P', 1, 6),
         ('red', 'K', 9, 5)],
        'w', '088', '图10',
    ),
    'x-m-10': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 6), ('black', 'R', 5, 1),
         ('red', 'P', 4, 5), ('red', 'N', 7, 5), ('red', 'A', 7, 6),
         ('red', 'A', 8, 5), ('red', 'K', 9, 5)],
        'w', '089', '图11',
    ),
    'x-m-11': (
        [('black', 'K', 0, 4), ('black', 'A', 0, 6), ('black', 'B', 0, 3),
         ('black', 'R', 5, 4), ('red', 'P', 3, 3), ('red', 'N', 3, 6),
         ('red', 'A', 8, 4), ('red', 'K', 9, 5), ('red', 'A', 9, 6)],
        'w', '089', '图12',
    ),
    'x-m-12': (
        [('black', 'K', 0, 6), ('black', 'A', 0, 5), ('black', 'A', 2, 5),
         ('black', 'P', 9, 8), ('red', 'K', 9, 5), ('red', 'A', 8, 6),
         ('red', 'N', 3, 8), ('red', 'P', 1, 7)],
        'w', '090', '图13',
    ),
    'x-m-13': (
        [('black', 'K', 0, 5), ('black', 'B', 0, 4), ('black', 'B', 2, 5),
         ('black', 'C', 2, 9), ('red', 'K', 9, 5), ('red', 'P', 1, 5),
         ('red', 'N', 3, 1)],
        'w', '091', '图14',
    ),
    # 双马双炮 图15-22
    'x-nn-01': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 5), ('black', 'A', 2, 6),
         ('black', 'C', 1, 8), ('red', 'N', 5, 2), ('red', 'N', 5, 8),
         ('red', 'K', 9, 5)],
        'w', '093', '图15',
    ),
    'x-nn-02': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 5), ('black', 'A', 2, 6),
         ('black', 'N', 2, 9), ('red', 'N', 3, 4), ('red', 'N', 5, 6),
         ('red', 'K', 9, 5)],
        'w', '094', '图16',
    ),
    'x-nn-03': (
        [('black', 'K', 0, 4), ('black', 'B', 2, 5), ('black', 'B', 3, 7),
         ('red', 'B', 6, 3), ('red', 'B', 6, 7), ('red', 'C', 9, 5),
         ('red', 'C', 9, 6), ('red', 'K', 8, 5)],
        'w', '096', '图17',
    ),
    'x-nn-04': (
        [('black', 'K', 0, 4), ('black', 'B', 2, 5), ('black', 'B', 3, 7),
         ('red', 'B', 6, 7), ('red', 'C', 9, 5), ('red', 'C', 9, 6),
         ('red', 'K', 8, 5)],
        'w', '096', '图18',
    ),
    'x-nn-05': (
        [('black', 'K', 0, 5), ('black', 'C', 1, 7), ('black', 'B', 2, 5),
         ('black', 'N', 2, 7), ('red', 'B', 5, 3), ('red', 'K', 7, 4),
         ('red', 'A', 7, 6), ('red', 'B', 7, 9), ('red', 'C', 8, 5)],
        'w', '098', '图19',
    ),
    'x-nn-06': (
        [('black', 'K', 0, 6), ('black', 'A', 0, 5), ('black', 'A', 1, 6),
         ('black', 'B', 0, 7), ('black', 'B', 2, 6), ('black', 'N', 4, 8),
         ('red', 'N', 1, 7), ('red', 'B', 6, 7), ('red', 'B', 7, 1),
         ('red', 'A', 7, 4), ('red', 'A', 7, 6), ('red', 'K', 8, 5),
         ('red', 'C', 9, 7)],
        'w', '100', '图21',
    ),
    'x-nn-07': (
        [('black', 'K', 1, 6), ('black', 'C', 0, 6), ('black', 'N', 4, 4),
         ('red', 'R', 3, 3), ('red', 'K', 9, 5)],
        'w', '101', '图22',
    ),
    # 兵类 图23-24
    'x-p-01': (
        [('black', 'K', 0, 5), ('black', 'A', 1, 5), ('black', 'A', 2, 6),
         ('red', 'P', 0, 9), ('red', 'P', 3, 5), ('red', 'K', 9, 5)],
        'w', '102', '图23',
    ),
    'x-p-02': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'A', 0, 6),
         ('black', 'P', 5, 5), ('black', 'P', 5, 6),
         ('red', 'R', 4, 3), ('red', 'K', 9, 5)],
        'w', '103', '图24',
    ),
    # 车类 图25-49
    'x-r-01': (
        [('black', 'K', 0, 6), ('black', 'N', 2, 6), ('black', 'N', 4, 4),
         ('red', 'R', 4, 5), ('red', 'K', 9, 5)],
        'w', '104', '图25',
    ),
    'x-r-02': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 6), ('black', 'A', 1, 5),
         ('black', 'C', 8, 9), ('red', 'B', 5, 8), ('red', 'R', 6, 9),
         ('red', 'A', 7, 7), ('red', 'K', 8, 6)],
        'w', '106', '图28',
    ),
    'x-r-03': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'B', 2, 3),
         ('black', 'R', 2, 7), ('black', 'N', 3, 8),
         ('red', 'R', 2, 2), ('red', 'B', 9, 7), ('red', 'A', 9, 4),
         ('red', 'A', 9, 6), ('red', 'K', 9, 5)],
        'w', '107', '图29',
    ),
    'x-r-04': (
        [('black', 'K', 0, 6), ('black', 'A', 0, 5), ('black', 'A', 0, 7),
         ('black', 'B', 0, 4), ('black', 'B', 2, 6), ('black', 'N', 5, 2),
         ('black', 'P', 5, 1), ('black', 'R', 8, 1),
         ('red', 'R', 7, 8), ('red', 'P', 7, 1), ('red', 'B', 8, 4),
         ('red', 'B', 9, 7), ('red', 'A', 8, 5), ('red', 'A', 9, 6),
         ('red', 'K', 9, 5)],
        'w', '108', '图30',
    ),
    'x-r-05': (
        [('black', 'K', 0, 6), ('black', 'A', 0, 4), ('black', 'A', 1, 4),
         ('black', 'B', 1, 5), ('black', 'R', 2, 5), ('black', 'P', 5, 2),
         ('red', 'R', 7, 8), ('red', 'B', 8, 5), ('red', 'B', 9, 3),
         ('red', 'K', 9, 5)],
        'w', '110', '图32',
    ),
    'x-r-06': (
        [('black', 'K', 1, 6), ('black', 'A', 0, 4), ('black', 'A', 1, 5),
         ('black', 'N', 2, 4), ('black', 'C', 2, 6),
         ('red', 'P', 3, 1), ('red', 'R', 3, 6),
         ('red', 'A', 7, 5), ('red', 'A', 9, 5), ('red', 'K', 9, 6)],
        'w', '111', '图33',
    ),
    'x-r-07': (
        [('black', 'K', 2, 4), ('black', 'B', 0, 7), ('black', 'B', 2, 9),
         ('black', 'P', 5, 4), ('black', 'R', 5, 5),
         ('red', 'P', 1, 6), ('red', 'R', 3, 1),
         ('red', 'B', 7, 9), ('red', 'A', 8, 5),
         ('red', 'K', 9, 5), ('red', 'B', 9, 7)],
        'w', '112', '图35',
    ),
    'x-r-08': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'A', 0, 6),
         ('black', 'R', 6, 4),
         ('red', 'N', 4, 3), ('red', 'R', 5, 4),
         ('red', 'B', 2, 3), ('red', 'B', 2, 7),
         ('red', 'K', 9, 5)],
        'w', '114', '图37',
    ),
    'x-r-09': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'A', 1, 5),
         ('black', 'B', 0, 7), ('black', 'R', 2, 2), ('black', 'B', 3, 9),
         ('red', 'P', 3, 4), ('red', 'N', 4, 5), ('red', 'R', 4, 6),
         ('red', 'B', 5, 7), ('red', 'B', 7, 5), ('red', 'K', 9, 6)],
        'w', '115', '图38',
    ),
    'x-r-10': (
        [('black', 'K', 0, 4), ('black', 'A', 0, 6), ('black', 'B', 0, 3),
         ('black', 'A', 1, 5), ('black', 'B', 2, 1), ('black', 'R', 2, 4),
         ('red', 'P', 3, 2), ('red', 'R', 3, 6), ('red', 'N', 5, 8),
         ('red', 'A', 7, 6), ('red', 'B', 7, 9), ('red', 'A', 8, 5),
         ('red', 'B', 9, 7), ('red', 'K', 9, 5)],
        'w', '116', '图39',
    ),
    'x-r-11': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'A', 0, 6),
         ('black', 'B', 2, 5), ('black', 'B', 2, 6), ('black', 'R', 5, 2),
         ('red', 'N', 5, 8), ('red', 'P', 4, 3), ('red', 'R', 6, 7),
         ('red', 'A', 8, 5), ('red', 'K', 9, 5)],
        'w', '117', '图40',
    ),
    'x-r-12': (
        [('black', 'K', 0, 5), ('black', 'B', 2, 3), ('black', 'B', 2, 7),
         ('black', 'R', 5, 5),
         ('red', 'R', 4, 4), ('red', 'C', 8, 5), ('red', 'A', 7, 6),
         ('red', 'K', 9, 6)],
        'w', '119', '图42',
    ),
    'x-r-13': (
        [('black', 'K', 0, 5), ('black', 'B', 2, 5), ('black', 'B', 2, 6),
         ('black', 'R', 5, 5),
         ('red', 'R', 1, 5), ('red', 'C', 9, 5), ('red', 'B', 9, 3),
         ('red', 'K', 9, 6)],
        'w', '121', '图44',
    ),
    'x-r-14': (
        [('black', 'K', 0, 4), ('black', 'B', 2, 5), ('black', 'R', 5, 4),
         ('red', 'R', 7, 5), ('red', 'C', 9, 3), ('red', 'B', 9, 7),
         ('red', 'K', 9, 5)],
        'w', '122', '图45',
    ),
    'x-r-15': (
        [('black', 'K', 0, 6), ('black', 'R', 5, 6), ('black', 'P', 3, 2),
         ('red', 'R', 4, 5), ('red', 'B', 9, 1), ('red', 'K', 9, 5)],
        'w', '124', '图49',
    ),
    # 实战选评 图90-94
    'x-z-01': (
        [('black', 'K', 0, 4), ('black', 'R', 3, 4), ('black', 'P', 5, 4),
         ('red', 'R', 5, 5), ('red', 'C', 7, 9), ('red', 'A', 8, 6),
         ('red', 'K', 9, 5)],
        'w', '149', '图90',
    ),
    'x-z-02': (
        [('black', 'K', 0, 4), ('black', 'A', 0, 5), ('black', 'A', 1, 4),
         ('black', 'B', 0, 6), ('black', 'B', 2, 4), ('black', 'C', 9, 1),
         ('black', 'R', 4, 4), ('black', 'P', 8, 4), ('black', 'P', 8, 5),
         ('red', 'R', 5, 5), ('red', 'C', 9, 2), ('red', 'A', 9, 3),
         ('red', 'K', 9, 4)],
        'w', '152', '图92',
    ),
    'x-z-03': (
        [('black', 'K', 0, 5), ('black', 'A', 0, 4), ('black', 'A', 0, 6),
         ('black', 'B', 2, 5), ('black', 'B', 2, 6), ('black', 'P', 6, 5),
         ('black', 'P', 7, 1), ('black', 'P', 7, 9),
         ('red', 'R', 4, 3), ('red', 'B', 8, 4), ('red', 'B', 9, 6),
         ('red', 'A', 8, 5), ('red', 'K', 9, 5)],
        'w', '153', '图94',
    ),
}


def main() -> None:
    out: dict[str, dict[str, str]] = {}
    for key, (pieces, stm, page, book_fig) in PUZZLES.items():
        fen = build_fen(pieces, stm)
        board, side = fen.rsplit(' ', 1)
        out[key] = {
            'pieces': board,
            'stm': side,
            'page': page,
            'bookFig': book_fig,
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
