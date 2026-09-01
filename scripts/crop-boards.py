#!/usr/bin/env python3
"""Crop board diagrams from book pages for visual inspection."""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'mydata' / 'pages'
OUT = ROOT / 'mydata' / 'boards'
OUT.mkdir(exist_ok=True)

# Manual bboxes tuned per page (x0,y0,x1,y1) after visual inspection
BOARDS = {
    17: [(520, 95, 980, 520)],  # fig2
    18: [(520, 80, 980, 500), (520, 520, 980, 920)],  # fig3 top, fig4 ref bottom text only - fig4 on 19
    19: [(520, 80, 980, 480), (520, 520, 980, 920)],  # fig4, fig5
    20: [(520, 200, 980, 620)],  # fig6
    21: [(520, 180, 980, 580), (520, 600, 980, 980)],  # fig7, fig8
    22: [(520, 120, 980, 480), (520, 520, 980, 880)],  # fig9, fig10
    23: [(520, 380, 980, 780), (520, 80, 980, 360)],  # fig11 bottom area, fig12 top
    24: [(520, 280, 980, 680)],  # fig13
    25: [(520, 80, 980, 420), (520, 480, 980, 860)],  # fig14, fig15
    26: [(520, 80, 980, 420), (520, 480, 980, 860)],  # fig16, fig17? 
    27: [(520, 380, 980, 780)],  # fig17
    28: [(520, 80, 980, 420), (520, 480, 980, 860)],  # fig18, fig19
    29: [(520, 80, 980, 420), (520, 480, 980, 860)],  # fig19, fig20
    30: [(520, 280, 980, 680)],  # fig21
    31: [(520, 200, 980, 580)],  # fig22
    32: [(520, 80, 980, 420), (520, 500, 980, 860)],  # fig23, fig24 header
    33: [(520, 80, 980, 480)],  # fig24
}

fig_map = {
    2: (17, 0), 3: (18, 0), 4: (19, 0), 5: (19, 1), 6: (20, 0),
    7: (21, 0), 8: (21, 1), 9: (22, 0), 10: (22, 1),
    11: (23, 0), 12: (23, 1), 13: (24, 0), 14: (25, 0), 15: (25, 1),
    16: (26, 0), 17: (27, 0), 18: (28, 0), 19: (28, 1), 20: (29, 1),
    21: (30, 0), 22: (31, 0), 23: (32, 0), 24: (33, 0),
}

for fig, (pg, idx) in fig_map.items():
    img = Image.open(PAGES / f'page-{pg:03d}.png')
    bbox = BOARDS[pg][idx]
    crop = img.crop(bbox).resize((450, 500), Image.Resampling.LANCZOS)
    crop.save(OUT / f'fig{fig:02d}.png')

print('cropped', len(fig_map), 'boards')
