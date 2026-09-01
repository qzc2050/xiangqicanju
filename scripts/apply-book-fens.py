#!/usr/bin/env python3
"""Apply book FEN updates to src/puzzles/catalog.ts. Keeps o-m-01 unchanged."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'src' / 'puzzles' / 'catalog.ts'

# rank 0=top, file 1-9; side red|black, kind K/A/B/N/R/C/P
KIND = {
    ('red', 'K'): 'K', ('red', 'A'): 'A', ('red', 'B'): 'B', ('red', 'N'): 'N',
    ('red', 'R'): 'R', ('red', 'C'): 'C', ('red', 'P'): 'P',
    ('black', 'K'): 'k', ('black', 'A'): 'a', ('black', 'B'): 'b', ('black', 'N'): 'n',
    ('black', 'R'): 'r', ('black', 'C'): 'c', ('black', 'P'): 'p',
}


def build_fen(pieces: list[tuple[str, str, int, int]], stm: str = 'w') -> str:
    grid: list[list[str | None]] = [[None] * 9 for _ in range(10)]
    for side, kind, rank, file1 in pieces:
        ch = KIND[(side, kind)]
        f = file1 - 1
        if grid[rank][f] is not None:
            raise ValueError(f'overlap rank={rank} file={file1}')
        grid[rank][f] = ch
    rows: list[str] = []
    for rank in range(10):
        row = ''
        empty = 0
        for f in range(9):
            ch = grid[rank][f]
            if ch is None:
                empty += 1
            else:
                if empty:
                    row += str(empty)
                    empty = 0
                row += ch
        if empty:
            row += str(empty)
        if row == '':
            row = '9'
        rows.append(row)
    return '/'.join(rows) + f' {stm}'


def p(side: str, kind: str, rank: int, file: int) -> tuple[str, str, int, int]:
    return (side, kind, rank, file)


# fmt: off
UPDATES: dict[str, tuple[str, str | None]] = {
    # id -> (fen, bookNo suffix like '·图18' or None to keep bookNo)
    # === 原本·马类 o-m-02..24 (skip o-m-01) ===
    'o-m-02': (build_fen([p('black','A',0,5),p('black','A',2,4),p('black','K',2,5),p('red','N',4,1),p('red','K',9,4)]), '·图2'),
    'o-m-03': (build_fen([p('black','K',0,4),p('black','B',2,3),p('red','N',3,9),p('red','K',9,5)]), '·图3'),
    'o-m-04': (build_fen([p('black','K',1,6),p('red','N',3,6),p('black','B',4,3),p('red','K',9,5)]), '·图4'),
    'o-m-05': (build_fen([p('black','K',1,6),p('black','P',3,3),p('red','N',7,9),p('red','K',9,5)]), '·图5'),
    'o-m-06': (build_fen([p('black','K',0,5),p('black','P',4,5),p('red','N',6,9),p('red','K',9,5)]), '·图6'),
    'o-m-07': (build_fen([p('black','K',0,5),p('black','C',0,7),p('black','A',2,4),p('black','A',2,6),p('red','N',3,3),p('red','K',9,4)]), '·图7'),
    'o-m-08': (build_fen([p('black','C',0,5),p('black','A',1,5),p('black','K',2,4),p('black','A',2,6),p('black','P',4,5),p('red','N',2,3),p('red','K',9,5)]), '·图8'),
    'o-m-09': (build_fen([p('black','K',0,5),p('black','R',5,7),p('red','N',8,4),p('red','K',9,5)]), '·图9'),
    'o-m-10': (build_fen([p('black','K',0,6),p('black','R',5,7),p('red','N',3,5),p('red','B',9,3),p('red','K',9,4)]), '·图10'),
    'o-m-11': (build_fen([p('black','K',0,5),p('red','B',2,3),p('red','B',2,6),p('red','N',3,5),p('black','R',5,8),p('red','K',9,5)]), '·图11'),
    'o-m-12': (build_fen([p('black','K',0,5),p('black','N',3,5),p('black','B',4,3),p('black','B',4,5),p('red','R',7,5),p('red','K',9,4)]), '·图12'),
    'o-m-13': (build_fen([p('black','K',0,5),p('black','B',4,7),p('black','R',6,7),p('red','N',5,7),p('red','P',6,5),p('red','B',7,5),p('red','K',8,5)]), '·图13'),
    'o-m-14': (build_fen([p('black','K',1,4),p('black','N',3,3),p('black','P',7,6),p('red','P',6,2),p('red','A',8,4),p('red','K',9,5),p('red','A',8,6)]), '·图14'),
    'o-m-15': (build_fen([p('black','B',0,3),p('black','A',0,4),p('black','K',0,5),p('black','A',1,5),p('black','B',2,5),p('red','P',1,6),p('red','N',4,3),p('red','K',9,5)]), '·图15'),
    'o-m-16': (build_fen([p('black','K',0,5),p('black','N',5,5),p('black','P',4,6),p('red','B',7,3),p('red','B',7,7),p('red','A',8,4),p('red','A',8,6),p('red','K',9,5)]), '·图16'),
    'o-m-17': (build_fen([p('black','K',0,5),p('black','N',4,8),p('black','P',7,6),p('red','K',8,4),p('red','A',9,5),p('red','B',7,5),p('red','B',7,9)]), '·图17'),
    'o-m-18': (build_fen([p('black','K',0,5),p('black','N',7,2),p('black','P',5,4),p('red','K',8,6),p('red','A',8,5),p('red','A',9,6),p('red','B',9,3)]), '·图18'),
    'o-m-19': (build_fen([p('black','K',0,6),p('black','A',1,5),p('black','A',2,4),p('black','B',2,1),p('red','P',2,5),p('red','N',3,6),p('red','K',9,5)]), '·图19'),
    'o-m-20': (build_fen([p('black','K',0,4),p('black','C',2,3),p('black','B',4,7),p('red','P',1,5),p('red','N',3,3),p('red','K',9,5)]), '·图20'),
    'o-m-21': (build_fen([p('black','K',0,5),p('red','C',4,5),p('black','N',6,8),p('red','K',7,4),p('black','P',8,5)]), '·图21'),
    'o-m-22': (build_fen([p('black','A',0,4),p('black','K',0,5),p('red','N',2,3),p('red','P',2,5),p('black','N',2,7),p('red','B',7,5),p('red','K',8,6)]), '·图22'),
    'o-m-23': (build_fen([p('black','K',0,5),p('black','A',0,6),p('black','C',1,1),p('red','P',2,5),p('red','N',3,6),p('red','K',9,5)]), '·图23'),
    'o-m-24': (build_fen([p('black','K',0,4),p('black','B',2,5),p('black','B',2,9),p('red','N',4,4),p('red','P',4,7),p('red','K',9,5)]), '·图24'),
    # === 原本·炮类 图25-40 ===
    'o-c-25': (build_fen([p('black','K',0,6),p('black','A',1,5),p('black','A',2,4),p('red','A',7,6),p('red','C',8,2),p('red','K',9,5)]), '·图25'),
    'o-c-26': (build_fen([p('black','K',0,5),p('black','C',1,6),p('black','A',2,4),p('black','A',2,6),p('black','B',2,1),p('black','B',4,3),p('red','B',7,9),p('red','A',7,4),p('red','K',8,4)]), '·图26'),
    'o-c-27': (build_fen([p('black','K',0,5),p('black','R',5,8),p('red','C',7,6),p('red','A',8,5),p('red','A',9,6),p('red','K',9,4)]), '·图27'),
    'o-c-28': (build_fen([p('black','K',0,5),p('black','R',5,8),p('red','C',5,5),p('red','B',7,5),p('red','B',9,3),p('red','K',9,5)]), '·图28'),
    'o-c-29': (build_fen([p('black','K',0,5),p('black','B',2,5),p('black','B',4,3),p('black','C',4,5),p('red','R',3,8),p('red','K',9,5)]), '·图29'),
    'o-c-30': (build_fen([p('black','K',0,5),p('black','P',3,3),p('black','P',3,5),p('black','P',3,7),p('red','C',7,5),p('red','A',8,5),p('red','A',9,4),p('red','K',9,5)]), '·图30'),
    'o-c-31': (build_fen([p('black','K',0,5),p('black','P',6,4),p('black','R',6,3),p('red','C',9,5),p('red','B',9,2),p('red','B',7,4),p('red','A',8,4),p('red','K',9,4)]), '·图31'),
    'o-c-32': (build_fen([p('black','K',2,5),p('black','A',1,5),p('black','C',0,6),p('black','C',2,9),p('black','P',8,5),p('red','K',7,6),p('red','C',9,8)]), '·图32'),
    'o-c-33': (build_fen([p('black','K',2,5),p('black','B',2,6),p('red','P',1,6),p('red','K',7,6),p('red','C',9,8)]), '·图33'),
    'o-c-34': (build_fen([p('red','K',9,4),p('red','B',6,3),p('black','C',5,5),p('black','P',4,5),p('black','B',2,3),p('black','K',0,5)]), '·图34'),
    'o-c-35': (build_fen([p('red','K',9,4),p('red','C',7,5),p('red','P',4,5),p('black','B',2,3),p('black','K',0,5)]), '·图35'),
    'o-c-36': (build_fen([p('red','K',9,4),p('red','B',9,5),p('red','A',8,5),p('red','C',7,5),p('red','P',6,5),p('black','B',2,3),p('black','A',0,4),p('black','K',0,5)]), '·图36'),
    'o-c-37': (build_fen([p('red','K',9,4),p('red','A',8,5),p('red','C',7,5),p('red','P',6,5),p('black','B',2,3),p('black','A',0,4),p('black','K',0,5)]), '·图37'),
    'o-c-38': (build_fen([p('red','K',9,4),p('red','C',7,5),p('black','R',5,5),p('red','P',3,3),p('red','P',3,6),p('black','K',0,5)]), '·图38'),
    'o-c-39': (build_fen([p('red','A',9,4),p('red','K',9,5),p('red','A',8,5),p('red','C',7,5),p('red','B',6,3),p('red','P',4,5),p('black','B',2,3),p('black','B',2,6),p('black','A',0,4),p('black','K',0,5),p('black','A',0,6)]), '·图39'),
    'o-c-40': (build_fen([p('red','A',9,4),p('red','K',9,5),p('red','A',8,5),p('red','C',7,5),p('red','B',6,3),p('red','P',4,5),p('black','B',2,3),p('black','B',2,6),p('black','A',1,4),p('black','K',0,5),p('black','A',0,6)]), '·图40'),
    # === 原本·兵类 图41-51 ===
    'o-p-41': (build_fen([p('red','K',9,4),p('red','B',6,3),p('red','P',4,5),p('black','A',0,4),p('black','K',0,5)]), '·图41'),
    'o-p-42': (build_fen([p('red','K',9,4),p('black','C',7,5),p('red','P',4,5),p('black','B',2,3),p('black','A',0,4),p('black','K',0,5)]), '·图42'),
    'o-p-43': (build_fen([p('red','K',9,4),p('red','A',7,5),p('red','P',6,5),p('black','P',3,3),p('black','P',3,6),p('black','A',0,4),p('black','K',0,5),p('black','A',0,6)]), '·图43'),
    'o-p-44': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','B',2,3),p('black','A',0,4),p('black','K',0,5),p('black','A',0,6)]), '·图44'),
    'o-p-45': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','B',2,3),p('black','B',2,6),p('black','K',0,5),p('black','A',0,6)]), '·图45'),
    'o-p-46': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','B',2,3),p('black','B',2,6),p('black','A',0,4),p('black','K',0,5),p('black','A',0,6)]), '·图46'),
    'o-p-47': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','B',2,3),p('black','A',0,4),p('black','K',0,5)]), '·图47'),
    'o-p-48': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','P',3,5),p('black','B',2,3),p('black','K',0,5)]), '·图48'),
    'o-p-49': (build_fen([p('red','K',9,4),p('red','P',4,4),p('red','P',4,6),p('black','P',3,5),p('black','A',0,4),p('black','K',0,5)]), '·图49'),
    'o-p-50': (build_fen([p('red','K',9,4),p('red','P',4,3),p('red','P',4,5),p('red','P',4,7),p('black','B',2,3),p('black','B',2,6),p('black','A',0,4),p('black','K',0,5),p('black','A',0,6)]), '·图50'),
    'o-p-51': (build_fen([p('black','K',0,4),p('black','A',0,6),p('black','A',1,6),p('black','B',2,3),p('black','B',2,6),p('red','P',4,4),p('red','P',4,6),p('red','P',5,7),p('red','K',9,6)]), '·图51'),
    # === 原本·车类 图52-70 ===
    'o-r-52': (build_fen([p('black','K',0,5),p('black','R',6,7),p('red','K',9,5),p('red','A',8,5),p('red','A',9,6),p('red','B',7,5),p('red','B',9,7)]), '·图52'),
    'o-r-53': (build_fen([p('black','K',0,4),p('black','A',0,6),p('black','A',1,5),p('black','B',0,7),p('black','B',2,9),p('red','K',8,5),p('red','R',9,9)]), '·图53'),
    'o-r-54': (build_fen([p('black','A',0,4),p('black','K',1,6),p('black','A',2,6),p('black','B',2,5),p('black','B',4,3),p('red','R',2,3),p('red','K',8,5)]), '·图54'),
    'o-r-55': (build_fen([p('black','K',0,5),p('black','A',0,6),p('black','A',1,5),p('black','N',1,6),p('red','R',3,4),p('red','K',9,5)]), '·图55'),
    'o-r-56': (build_fen([p('black','A',0,5),p('black','K',0,6),p('black','A',1,6),p('black','N',2,4),p('red','R',3,7),p('red','K',9,5)]), '·图56'),
    'o-r-57': (build_fen([p('black','K',0,6),p('black','R',2,6),p('red','C',5,3),p('red','R',5,5),p('red','K',8,5)]), '·图57'),
    'o-r-58': (build_fen([p('black','K',0,6),p('black','R',5,5),p('red','C',4,5),p('red','R',5,8),p('red','K',9,5)]), '·图58'),
    'o-r-59': (build_fen([p('black','K',1,6),p('black','R',4,6),p('red','P',0,4),p('red','R',5,5),p('red','K',9,5)]), '·图59'),
    'o-r-60': (build_fen([p('black','K',0,6),p('black','R',1,5),p('black','A',1,6),p('red','P',1,4),p('red','A',7,4),p('red','R',7,6),p('red','K',8,5)]), '·图60'),
    'o-r-61': (build_fen([p('black','K',0,5),p('black','A',1,5),p('black','R',2,5),p('black','P',8,6),p('red','R',7,4),p('red','A',7,6),p('red','K',8,4)]), '·图61'),
    'o-r-62': (build_fen([p('black','K',0,5),p('red','B',2,3),p('black','P',3,3),p('black','P',3,6),p('black','R',5,5),p('red','R',7,5),p('red','A',8,5),p('red','A',9,4),p('red','K',9,5)]), '·图62'),
    'o-r-63': (build_fen([p('black','A',0,4),p('black','K',0,5),p('black','A',0,6),p('black','B',2,3),p('black','B',2,6),p('red','P',4,4),p('red','P',4,6),p('black','R',5,5),p('red','R',7,5),p('red','K',9,5)]), '·图63'),
    'o-r-64': (build_fen([p('black','K',0,5),p('red','B',2,3),p('black','P',3,5),p('black','R',5,5),p('red','R',7,5),p('red','K',9,5)]), '·图64'),
    'o-r-65': (build_fen([p('black','K',0,5),p('black','B',2,7),p('red','P',4,5),p('black','R',5,5),p('red','R',7,5),p('red','K',9,5)]), '·图65'),
    'o-r-66': (build_fen([p('black','K',0,5),p('black','B',2,3),p('black','B',2,6),p('red','P',4,5),p('black','R',5,5),p('red','B',6,3),p('red','R',7,5),p('red','A',8,5),p('red','K',9,5)]), '·图66'),
    'o-r-67': (build_fen([p('black','A',0,4),p('black','K',0,5),p('black','A',0,6),p('black','B',2,3),p('black','B',2,6),p('black','P',3,3),p('black','P',3,6),p('red','P',4,5),p('red','R',7,5),p('red','K',9,5)]), '·图67'),
    'o-r-68': (build_fen([p('black','K',0,5),p('black','R',5,4),p('black','R',5,6),p('red','C',7,5),p('red','A',8,5),p('red','A',9,4),p('red','K',9,5)]), '·图68'),
    'o-r-69': (build_fen([p('black','A',0,4),p('black','K',0,5),p('black','A',0,6),p('black','R',5,5),p('red','B',6,3),p('red','B',6,6),p('black','C',7,5),p('red','R',8,4),p('red','R',8,6),p('red','K',9,5)]), '·图69'),
    'o-r-70': (build_fen([p('black','A',0,4),p('black','K',0,5),p('black','A',0,6),p('black','B',2,3),p('black','B',2,7),p('black','R',5,8),p('red','B',6,3),p('red','C',7,5),p('red','R',8,5),p('red','A',8,6),p('red','K',9,5),p('red','A',9,4)]), '·图70'),
    # === 增订 (x-m-01/02 already book; skip x-k basic kills) ===
    'x-m-03': ('4k4/3a5/2b6/9/9/9/4N4/5P3/9/3K5 w', '增三·图3'),
    'x-m-04': ('4k4/3a1a3/2b6/9/9/9/4N4/6P2/9/3K5 w', '增四·图5'),
    'x-m-05': ('3a5/4k4/2b6/9/9/9/4N4/4P4/9/3K5 w', '增五·图6'),
    'x-m-06': ('4k4/3a5/2b6/9/4P4/9/4N4/9/9/3K5 w', '增六·图7'),
    'x-m-07': ('3k5/4aP3/5a3/2b6/9/9/4N4/9/9/4K4 w', '增七·图8'),
    'x-m-08': ('5a3/3k1P3/4b4/9/1Nb6/9/9/9/9/4K4 w', '增八·图9'),
    'x-m-09': ('4a4/3k1P3/8b/6b2/5N3/9/9/9/9/4K4 w', '增九·图10'),
    'x-m-10': ('4ka3/9/9/9/4P4/r8/9/4NA3/4A4/4K4 w', '增十·图11'),
    'x-m-11': ('2bk1a3/9/9/2P2N3/9/3r5/9/9/3A5/4KA3 w', '增十一·图12'),
    'x-m-12': ('4ak3/6P2/4a4/7N1/9/9/9/9/5A3/4K2p1 w', '增十二·图13'),
    'x-m-13': ('3bk4/4P4/4b3c/N8/9/9/9/9/9/4K4 w', '增十三·图14'),
    'x-nn-01': ('4k4/4a2c1/5a3/9/9/1N5N1/9/9/9/4K4 w', '图15'),
    'x-nn-02': ('4k4/4a4/5a2n/3N5/9/5N3/9/9/9/4K4 w', '图16'),
    'x-nn-03': ('3k5/9/4b4/6b2/9/9/2B3B2/9/4K4/4CC3 w', '图17'),
    'x-nn-04': ('3k5/9/4b4/6b2/9/9/6B2/9/4K4/4CC3 w', '图18'),
    'x-nn-05': ('4k4/6c2/4b1n2/9/9/2B6/9/3K1A2B/4C4/9 w', '图19'),
    'x-nn-06': ('4akb2/5aN2/5b3/9/7n1/9/6B2/B2A1A3/4K4/6C2 w', '图21'),
    'x-nn-07': ('5c3/5k3/9/2R6/3n5/9/9/9/9/4K4 w', '图22'),
    'x-p-01': ('4k3P/4a4/5a3/4P4/9/9/9/9/9/4K4 w', '图23'),
    'x-p-02': ('3aka3/9/9/9/2R6/4pp3/9/9/9/4K4 w', '图24'),
    'x-r-01': ('5k3/9/5n3/9/3nR4/9/9/9/9/4K4 w', '图25'),
    'x-r-02': ('4ka3/4a4/9/9/9/7B1/8R/6A2/5K2c/9 w', '图28'),
    'x-r-03': ('3ak4/9/1Rb3r2/7n1/9/9/9/9/9/3AKAB2 w', '图29'),
    'x-r-04': ('3baka2/9/5b3/9/9/pn7/9/P6R1/r2BA4/4KAB2 w', '图30'),
    'x-r-05': ('3a1k3/3ab4/4r4/9/9/1p7/9/7R1/4B4/2B1K4 w', '图32'),
    'x-r-06': ('3a5/4ak3/3n1c3/P4R3/9/9/9/4A4/9/4AK3 w', '图33'),
    'x-r-07': ('6b2/5P3/3k4b/R8/9/3pr4/9/8B/4A4/4K1B2 w', '图35'),
    'x-r-08': ('3aka3/9/2B3B2/9/2N6/3R5/3r5/9/9/4K4 w', '图37'),
    'x-r-09': ('3ak1b2/4a4/1r7/3P4b/4NR3/6B2/9/4B4/9/5K3 w', '图38'),
    'x-r-10': ('2bk1a3/4a4/b2r5/1P3R3/9/7N1/9/5A2B/4A4/4K1B2 w', '图39'),
    'x-r-11': ('3aka3/9/4bb3/9/2P6/1r5N1/6R2/9/4A4/4K4 w', '图40'),
    'x-r-12': ('4k4/9/2b3b2/9/3R5/4r4/9/5A3/4C4/5K3 w', '图42'),
    'x-r-13': ('4k4/4R4/4bb3/9/9/4r4/9/9/9/2B1CK3 w', '图44'),
    'x-r-14': ('3k5/9/4b4/9/9/3r5/9/4R4/9/2C1K1B2 w', '图45'),
    'x-r-15': ('5k3/9/9/1p7/4R4/5r3/9/9/9/B3K4 w', '图49'),
    'x-z-01': ('3k5/9/9/3r5/9/3pR4/9/8C/5A3/4K4 w', '图90'),
    'x-z-02': ('3k1a3/3p3C1/3r1a1P1/b8/9/3CR4/9/5A3/4B4/2BAK4 w', '二·图92'),
    'x-z-03': ('3aka3/9/4bb3/9/2R6/9/4p4/p7p/3BA4/4KB3 w', '图94'),
}
# fmt: on

SKIP = {'o-m-01', 'x-k-01', 'x-k-02', 'x-k-03', 'x-k-04', 'x-k-05', 'x-k-06', 'x-k-07'}


def patch_catalog() -> int:
    text = CATALOG.read_text(encoding='utf-8')
    count = 0
    for pid, (fen, book_suffix) in UPDATES.items():
        if pid in SKIP:
            continue
        block_re = re.compile(
            rf"(\{{\s*\n\s*id: '{re.escape(pid)}',.*?fen: ')([^']+)(')",
            re.DOTALL,
        )
        m = block_re.search(text)
        if not m:
            print(f'MISSING block: {pid}', file=sys.stderr)
            continue
        if m.group(2) == fen:
            pass
        else:
            text = text[: m.start(2)] + fen + text[m.end(2) :]
            count += 1
        if book_suffix:
            bn_re = re.compile(
                rf"(id: '{re.escape(pid)}',.*?bookNo: ')([^']*)(')",
                re.DOTALL,
            )
            bm = bn_re.search(text)
            if bm:
                base = bm.group(2).split('·')[0].split('例')[0]
                if '增' in book_suffix:
                    new_bn = book_suffix
                elif '·图' not in bm.group(2):
                    new_bn = base + book_suffix
                else:
                    new_bn = bm.group(2)
                if bm.group(2) != new_bn:
                    text = text[: bm.start(2)] + new_bn + text[bm.end(2) :]
    CATALOG.write_text(text, encoding='utf-8')
    return count


def main() -> None:
    n = patch_catalog()
    print(f'Updated {n} FEN entries in catalog.ts')
    r = subprocess.run(
        ['npx', 'tsx', 'scripts/validate-puzzles.ts'],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    bad = [ln for ln in r.stdout.splitlines() if 'BAD FEN' in ln or 'NO MOVES' in ln]
    if bad:
        print('Validation issues:', file=sys.stderr)
        for ln in bad:
            print(ln, file=sys.stderr)
        sys.exit(1)
    print('All puzzles validate OK')


if __name__ == '__main__':
    main()
