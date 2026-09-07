import { getPiece } from './board'
import {
  FILES,
  RANKS,
  type PieceKind,
  type Position,
  type Side,
  type Square,
} from './types'

function key(file: number, rank: number): string {
  return `${file},${rank}`
}

const ADVISOR_SQUARES: Record<Side, ReadonlySet<string>> = {
  red: new Set([key(3, 0), key(5, 0), key(4, 1), key(3, 2), key(5, 2)]),
  black: new Set([key(3, 9), key(5, 9), key(4, 8), key(3, 7), key(5, 7)]),
}

const ELEPHANT_SQUARES: Record<Side, ReadonlySet<string>> = {
  red: new Set([
    key(2, 0),
    key(6, 0),
    key(0, 2),
    key(4, 2),
    key(8, 2),
    key(2, 4),
    key(6, 4),
  ]),
  black: new Set([
    key(2, 9),
    key(6, 9),
    key(0, 7),
    key(4, 7),
    key(8, 7),
    key(2, 5),
    key(6, 5),
  ]),
}

function inPalace(sq: Square, side: Side): boolean {
  if (sq.file < 3 || sq.file > 5) return false
  return side === 'red' ? sq.rank >= 0 && sq.rank <= 2 : sq.rank >= 7 && sq.rank <= 9
}

function kindLabel(kind: PieceKind, side: Side): string {
  if (kind === 'K') return side === 'red' ? '帅' : '将'
  if (kind === 'A') return side === 'red' ? '仕' : '士'
  if (kind === 'B') return side === 'red' ? '相' : '象'
  return kind
}

/** 将/士/象是否落在规则允许的格子上（不检查走法路径） */
export function placementIssues(pos: Position): string[] {
  const issues: string[] = []
  for (let rank = 0; rank < RANKS; rank++) {
    for (let file = 0; file < FILES; file++) {
      const piece = getPiece(pos, { file, rank })
      if (!piece) continue
      const { kind, side } = piece
      const k = key(file, rank)
      if (kind === 'K' && !inPalace({ file, rank }, side)) {
        issues.push(`${kindLabel(kind, side)} 在九宫外 (${file},${rank})`)
      }
      if (kind === 'A' && !ADVISOR_SQUARES[side].has(k)) {
        issues.push(`${kindLabel(kind, side)} 不在士角/花心 (${file},${rank})`)
      }
      if (kind === 'B' && !ELEPHANT_SQUARES[side].has(k)) {
        issues.push(`${kindLabel(kind, side)} 不在象位 (${file},${rank})`)
      }
    }
  }
  return issues
}
