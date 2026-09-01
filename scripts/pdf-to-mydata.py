#!/usr/bin/env python3
"""Export scanned PDF pages to PNG + OCR text into mydata/."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / (
    '中国象棋实用残局增订本 (陈松顺著, 陈松顺著, 陈松顺) '
    '(z-library.sk, 1lib.sk, z-lib.sk).pdf'
)
DEFAULT_OUT = ROOT / 'mydata'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='PDF → mydata (pages + OCR)')
    p.add_argument('--pdf', type=Path, default=DEFAULT_PDF)
    p.add_argument('--out', type=Path, default=DEFAULT_OUT)
    p.add_argument('--zoom', type=float, default=2.0, help='Render scale for PNG')
    p.add_argument('--start', type=int, default=1, help='1-based start page')
    p.add_argument('--end', type=int, default=0, help='1-based end page (0 = all)')
    p.add_argument('--skip-ocr', action='store_true', help='Only export PNG pages')
    p.add_argument('--resume', action='store_true', help='Skip pages that already have OCR txt')
    p.add_argument('--fresh', action='store_true', help='Delete output dir before run')
    return p.parse_args()


def box_bounds(box) -> tuple[float, float, float, float]:
    """EasyOCR box: 4 corners -> x0, y0, x1, y1."""
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return min(xs), min(ys), max(xs), max(ys)


def sort_reading_order(items: list[tuple]) -> list[str]:
    """Sort OCR boxes top-to-bottom, then left-to-right."""
    if not items:
        return []
    normalized: list[tuple[tuple[float, float, float, float], str]] = []
    for entry in items:
        box = entry[0]
        text = entry[1]
        normalized.append((box_bounds(box), str(text)))
    heights = [b[3] - b[1] for b, _ in normalized if b[3] > b[1]]
    line_tol = (sum(heights) / len(heights) * 0.6) if heights else 20
    normalized.sort(key=lambda x: (x[0][1], x[0][0]))
    lines: list[list[tuple[tuple[float, float, float, float], str]]] = []
    for box, text in normalized:
        y = box[1]
        if not lines or abs(y - lines[-1][0][0][1]) > line_tol:
            lines.append([(box, text)])
        else:
            lines[-1].append((box, text))
    out: list[str] = []
    for group in lines:
        group.sort(key=lambda x: x[0][0])
        out.append(' '.join(t.strip() for _, t in group if t.strip()))
    return out


def create_ocr_engine():
    import easyocr

    return easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)


def ocr_page(reader, image_path: Path) -> tuple[str, int]:
    raw = reader.readtext(str(image_path))
    lines = sort_reading_order(raw)
    text = '\n'.join(lines).strip()
    return text, len(lines)


def export_page(doc: pymupdf.Document, page_index: int, zoom: float, png_path: Path) -> None:
    page = doc.load_page(page_index)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(png_path))


def write_readme(out: Path, meta: dict) -> None:
    readme = f"""陈松顺《中国象棋实用残局增订本》解析数据
生成时间: {meta['generated_at']}
源 PDF: {meta['pdf']}
页数: {meta['page_count']}
OCR 引擎: {meta['ocr_engine']}

目录说明:
  pages/           每页 PNG（对照摆棋）
  ocr/             每页 OCR 文本（UTF-8）
  ocr_combined.txt 全书合并文本，便于搜索
  index.json       页码索引

注意:
  - 源 PDF 为扫描版；OCR 结果可能有错字，录入 FEN/棋谱时请人工核对。
  - OCR 不能自动生成 FEN；棋盘请对照 pages/ 里的图片人工摆棋。
  - {meta.get('ocr_note', '')}
"""
    (out / 'README.txt').write_text(readme, encoding='utf-8')


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf.resolve()
    out_dir = args.out.resolve()

    if not pdf_path.is_file():
        print(f'PDF not found: {pdf_path}', file=sys.stderr)
        return 1

    if args.fresh and out_dir.exists():
        shutil.rmtree(out_dir)

    pages_dir = out_dir / 'pages'
    ocr_dir = out_dir / 'ocr'
    pages_dir.mkdir(parents=True, exist_ok=True)
    ocr_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(str(pdf_path))
    page_count = doc.page_count
    start = max(1, args.start)
    end = page_count if args.end <= 0 else min(args.end, page_count)

    reader = None
    ocr_engine = 'none'
    ocr_note = ''
    if not args.skip_ocr:
        try:
            reader = create_ocr_engine()
            ocr_engine = 'EasyOCR (ch_sim + en, CPU)'
            ocr_note = (
                'PaddleOCR 3.7 已安装于 .venv-ocr，但在本机 Windows/Python 3.13 上 '
                '触发 oneDNN 兼容错误，故实际 OCR 使用 EasyOCR。'
            )
        except Exception as exc:  # noqa: BLE001
            print(f'OCR init failed: {exc}', file=sys.stderr)
            return 1

    index_pages: list[dict] = []
    combined_parts: list[str] = []
    t0 = time.time()

    for page_no in range(start, end + 1):
        page_index = page_no - 1
        stem = f'page-{page_no:03d}'
        png_path = pages_dir / f'{stem}.png'
        txt_path = ocr_dir / f'{stem}.txt'

        if not png_path.exists():
            export_page(doc, page_index, args.zoom, png_path)

        char_count = 0
        line_count = 0
        ocr_status = 'skipped' if args.skip_ocr else 'pending'

        if reader is not None:
            if args.resume and txt_path.exists():
                text = txt_path.read_text(encoding='utf-8')
                char_count = len(text)
                line_count = len([ln for ln in text.splitlines() if ln.strip()])
                ocr_status = 'resumed'
            else:
                text, line_count = ocr_page(reader, png_path)
                txt_path.write_text(text + '\n', encoding='utf-8')
                char_count = len(text)
                ocr_status = 'done'

            combined_parts.append(f'\n===== 第 {page_no} 页 / {page_count} =====\n')
            combined_parts.append(txt_path.read_text(encoding='utf-8'))

        index_pages.append(
            {
                'page': page_no,
                'png': str(png_path.relative_to(out_dir)).replace('\\', '/'),
                'ocr': str(txt_path.relative_to(out_dir)).replace('\\', '/')
                if reader is not None
                else None,
                'char_count': char_count,
                'line_count': line_count,
                'ocr_status': ocr_status,
            }
        )

        elapsed = time.time() - t0
        print(f'[{page_no}/{end}] png ok, ocr={ocr_status}, chars={char_count}, elapsed={elapsed:.0f}s')

    doc.close()

    if reader is not None:
        (out_dir / 'ocr_combined.txt').write_text(''.join(combined_parts), encoding='utf-8')

    meta = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'pdf': str(pdf_path),
        'output_dir': str(out_dir),
        'page_count': page_count,
        'processed_pages': list(range(start, end + 1)),
        'ocr_engine': ocr_engine,
        'ocr_note': ocr_note,
        'zoom': args.zoom,
        'elapsed_seconds': round(time.time() - t0, 1),
        'pages': index_pages,
    }
    (out_dir / 'index.json').write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    write_readme(out_dir, meta)
    print(f'Done. Output: {out_dir}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
