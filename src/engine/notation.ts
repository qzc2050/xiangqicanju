import { applyMove, getPiece, parseFen } from './board'
import { PIECE_LABEL, type Move, type PieceKind, type Position, type Side } from './types'

const RED_NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九'] as const
const BLACK_NUM = ['1', '2', '3', '4', '5', '6', '7', '8', '9'] as const

/** 本方视角：从右到左 1～9 路 */
export function fileToRoad(side: Side, file: number): string {
  if (side === 'red') return RED_NUM[8 - file]
  return BLACK_NUM[file]
}

function isDiagonalPiece(kind: PieceKind): boolean {
  // 马、仕/士、相/象：进退的第四字为目标路号
  return kind === 'N' || kind === 'A' || kind === 'B'
}

function towardEnemy(side: Side, fromRank: number, toRank: number): boolean {
  return side === 'red' ? toRank > fromRank : toRank < fromRank
}

function stepNum(side: Side, steps: number): string {
  return side === 'red' ? RED_NUM[steps - 1] : BLACK_NUM[steps - 1]
}

function findSameOnFile(
  pos: Position,
  side: Side,
  kind: PieceKind,
  file: number,
): { file: number; rank: number }[] {
  const list: { file: number; rank: number }[] = []
  for (let rank = 0; rank < 10; rank++) {
    const p = pos.board[rank][file]
    if (p && p.side === side && p.kind === kind) list.push({ file, rank })
  }
  return list
}

/**
 * 传统中文四字记谱，如「马五进四」「炮二平五」「前车退二」。
 * 红方路数用汉字，黑方用阿拉伯数字；均从本方右侧数起。
 */
export function formatMoveChinese(pos: Position, move: Move): string {
  const piece = getPiece(pos, move.from)
  if (!piece) return '????'

  const { side, kind } = piece
  const name = PIECE_LABEL[side][kind]
  const same = findSameOnFile(pos, side, kind, move.from.file)

  let head: string
  if (same.length >= 2) {
    // 靠近对方为「前」
    const sorted =
      side === 'red'
        ? [...same].sort((a, b) => b.rank - a.rank)
        : [...same].sort((a, b) => a.rank - b.rank)
    const idx = sorted.findIndex(
      (s) => s.file === move.from.file && s.rank === move.from.rank,
    )
    head = `${idx === 0 ? '前' : '后'}${name}`
  } else {
    head = `${name}${fileToRoad(side, move.from.file)}`
  }

  const sameFile = move.from.file === move.to.file
  const sameRank = move.from.rank === move.to.rank

  let dir: string
  let tail: string

  if (sameRank) {
    dir = '平'
    tail = fileToRoad(side, move.to.file)
  } else {
    dir = towardEnemy(side, move.from.rank, move.to.rank) ? '进' : '退'
    if (isDiagonalPiece(kind)) {
      tail = fileToRoad(side, move.to.file)
    } else if (sameFile) {
      tail = stepNum(side, Math.abs(move.to.rank - move.from.rank))
    } else {
      tail = fileToRoad(side, move.to.file)
    }
  }

  return `${head}${dir}${tail}`
}

export function formatLineChinese(startFen: string, moves: Move[]): string[] {
  let pos = parseFen(startFen)
  const out: string[] = []
  for (const m of moves) {
    out.push(formatMoveChinese(pos, m))
    pos = applyMove(pos, m)
  }
  return out
}
