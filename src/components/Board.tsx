import {
  PIECE_LABEL,
  type Move,
  type Position,
  type Square,
} from '../engine'
import type { ReactNode } from 'react'

type Props = {
  pos: Position
  selected: Square | null
  legalTargets: Square[]
  hintMove: Move | null
  lastMove: Move | null
  onSquareClick: (sq: Square) => void
  flip?: boolean
}

/** 交叉点坐标系：边距 50，格距 100 → 9 路 × 10 线 */
const PAD = 50
const STEP = 100
const VB_W = PAD * 2 + STEP * 8
const VB_H = PAD * 2 + STEP * 9

/** 逻辑坐标 → SVG（红方在下；flip 时整盘视觉对调） */
function xy(file: number, rank: number, flip: boolean): { x: number; y: number } {
  const f = flip ? 8 - file : file
  const r = flip ? rank : 9 - rank
  return { x: PAD + f * STEP, y: PAD + r * STEP }
}

const MARKS: Square[] = [
  { file: 1, rank: 2 },
  { file: 7, rank: 2 },
  { file: 1, rank: 7 },
  { file: 7, rank: 7 },
  { file: 0, rank: 3 },
  { file: 2, rank: 3 },
  { file: 4, rank: 3 },
  { file: 6, rank: 3 },
  { file: 8, rank: 3 },
  { file: 0, rank: 6 },
  { file: 2, rank: 6 },
  { file: 4, rank: 6 },
  { file: 6, rank: 6 },
  { file: 8, rank: 6 },
]

function CornerMark({ x, y }: { x: number; y: number }) {
  const s = 10
  const g = 4
  const segs: [number, number, number, number][] = []
  const left = x > PAD + 1
  const right = x < PAD + STEP * 8 - 1
  if (left) {
    segs.push(
      [x - g - s, y - g, x - g, y - g],
      [x - g, y - g - s, x - g, y - g],
      [x - g - s, y + g, x - g, y + g],
      [x - g, y + g, x - g, y + g + s],
    )
  }
  if (right) {
    segs.push(
      [x + g, y - g, x + g + s, y - g],
      [x + g, y - g - s, x + g, y - g],
      [x + g, y + g, x + g + s, y + g],
      [x + g, y + g, x + g, y + g + s],
    )
  }
  return (
    <g className="board-mark">
      {segs.map(([x1, y1, x2, y2], i) => (
        <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} />
      ))}
    </g>
  )
}

function BoardLines() {
  const lines: ReactNode[] = []

  for (let i = 0; i < 10; i++) {
    const y = PAD + i * STEP
    lines.push(
      <line
        key={`h-${i}`}
        className="board-line"
        x1={PAD}
        y1={y}
        x2={PAD + STEP * 8}
        y2={y}
      />,
    )
  }

  // 竖线在河界（rank4 与 rank5 之间，y=450~550）断开
  const yBlackBottom = PAD + 4 * STEP // 视觉上方半区底 = 黑方河界线 rank5
  const yRedTop = PAD + 5 * STEP // 视觉下方半区顶 = 红方河界线 rank4
  for (let file = 0; file < 9; file++) {
    const x = PAD + file * STEP
    lines.push(
      <line
        key={`vt-${file}`}
        className="board-line"
        x1={x}
        y1={PAD}
        x2={x}
        y2={yBlackBottom}
      />,
      <line
        key={`vb-${file}`}
        className="board-line"
        x1={x}
        y1={yRedTop}
        x2={x}
        y2={PAD + STEP * 9}
      />,
    )
  }

  lines.push(
    <rect
      key="frame"
      className="board-frame"
      x={PAD}
      y={PAD}
      width={STEP * 8}
      height={STEP * 9}
      fill="none"
    />,
  )

  // 九宫：红 ranks 0-2，黑 ranks 7-9，files 3-5（红在下的固定画法）
  const palace = [
    [3, 0, 5, 2],
    [5, 0, 3, 2],
    [3, 7, 5, 9],
    [5, 7, 3, 9],
  ] as const
  for (const [f1, r1, f2, r2] of palace) {
    const a = xy(f1, r1, false)
    const b = xy(f2, r2, false)
    lines.push(
      <line
        key={`pal-${f1}${r1}-${f2}${r2}`}
        className="board-line"
        x1={a.x}
        y1={a.y}
        x2={b.x}
        y2={b.y}
      />,
    )
  }

  for (const sq of MARKS) {
    const { x, y } = xy(sq.file, sq.rank, false)
    lines.push(<CornerMark key={`mk-${sq.file}-${sq.rank}`} x={x} y={y} />)
  }

  return <g>{lines}</g>
}

export function Board({
  pos,
  selected,
  legalTargets,
  hintMove,
  lastMove,
  onSquareClick,
  flip = false,
}: Props) {
  const points: Square[] = []
  for (let rank = 0; rank < 10; rank++) {
    for (let file = 0; file < 9; file++) points.push({ file, rank })
  }

  const riverY = PAD + 4.5 * STEP

  return (
    <div className="board-wrap">
      <svg
        className="board-svg"
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        role="img"
        aria-label="象棋棋盘"
      >
        <defs>
          <linearGradient id="wood" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#e2c48a" />
            <stop offset="55%" stopColor="#d4b078" />
            <stop offset="100%" stopColor="#c4a060" />
          </linearGradient>
        </defs>

        <rect className="board-bg" x="0" y="0" width={VB_W} height={VB_H} rx="14" />

        {/* 线盘本身不翻转；棋子坐标随 flip 变 */}
        <g transform={flip ? `rotate(180 ${VB_W / 2} ${VB_H / 2})` : undefined}>
          <BoardLines />
          <text
            className="river-text"
            x={VB_W / 2}
            y={riverY}
            textAnchor="middle"
            dominantBaseline="middle"
            transform={flip ? `rotate(180 ${VB_W / 2} ${riverY})` : undefined}
          >
            楚 河　　汉 界
          </text>
        </g>

        {Array.from({ length: 9 }, (_, file) => {
          const top = xy(file, 9, flip)
          const bot = xy(file, 0, flip)
          const arab = flip ? 9 - file : file + 1
          const cn = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
          const cnLabel = flip ? cn[file] : cn[8 - file]
          return (
            <g key={`lab-${file}`}>
              <text className="coord" x={top.x} y={22} textAnchor="middle">
                {arab}
              </text>
              <text className="coord" x={bot.x} y={VB_H - 10} textAnchor="middle">
                {cnLabel}
              </text>
            </g>
          )
        })}

        {lastMove &&
          [lastMove.from, lastMove.to].map((sq, i) => {
            const { x, y } = xy(sq.file, sq.rank, flip)
            return <circle key={`last-${i}`} className="hl-last" cx={x} cy={y} r={42} />
          })}
        {hintMove &&
          [hintMove.from, hintMove.to].map((sq, i) => {
            const { x, y } = xy(sq.file, sq.rank, flip)
            return <circle key={`hint-${i}`} className="hl-hint" cx={x} cy={y} r={44} />
          })}
        {selected && (
          <circle
            className="hl-selected"
            cx={xy(selected.file, selected.rank, flip).x}
            cy={xy(selected.file, selected.rank, flip).y}
            r={44}
          />
        )}

        {legalTargets.map((sq) => {
          const { x, y } = xy(sq.file, sq.rank, flip)
          const cap = Boolean(pos.board[sq.rank][sq.file])
          return (
            <circle
              key={`t-${sq.file}-${sq.rank}`}
              className={cap ? 'target-cap' : 'target-dot'}
              cx={x}
              cy={y}
              r={cap ? 40 : 12}
            />
          )
        })}

        {points.map((sq) => {
          const piece = pos.board[sq.rank][sq.file]
          if (!piece) return null
          const { x, y } = xy(sq.file, sq.rank, flip)
          return (
            <g
              key={`pc-${sq.file}-${sq.rank}`}
              className={`piece-g ${piece.side}`}
              transform={`translate(${x} ${y})`}
            >
              <circle className="piece-disk" r="38" />
              <text className="piece-text" textAnchor="middle" dominantBaseline="central">
                {PIECE_LABEL[piece.side][piece.kind]}
              </text>
            </g>
          )
        })}

        {points.map((sq) => {
          const { x, y } = xy(sq.file, sq.rank, flip)
          return (
            <circle
              key={`hit-${sq.file}-${sq.rank}`}
              className="hit"
              cx={x}
              cy={y}
              r="46"
              onClick={() => onSquareClick(sq)}
            />
          )
        })}
      </svg>
    </div>
  )
}
