export type Side = 'red' | 'black'

export type PieceKind = 'K' | 'A' | 'B' | 'N' | 'R' | 'C' | 'P'

export type Piece = {
  kind: PieceKind
  side: Side
}

/** file 0-8 (a-i), rank 0-9 (红方底线为 0) */
export type Square = {
  file: number
  rank: number
}

export type Move = {
  from: Square
  to: Square
}

export type Position = {
  board: (Piece | null)[][]
  sideToMove: Side
}

export const FILES = 9
export const RANKS = 10

export const PIECE_LABEL: Record<Side, Record<PieceKind, string>> = {
  red: { K: '帅', A: '仕', B: '相', N: '马', R: '车', C: '炮', P: '兵' },
  black: { K: '将', A: '士', B: '象', N: '马', R: '车', C: '炮', P: '卒' },
}

export function otherSide(side: Side): Side {
  return side === 'red' ? 'black' : 'red'
}

export function sqKey(sq: Square): string {
  return `${sq.file},${sq.rank}`
}

export function sameSq(a: Square, b: Square): boolean {
  return a.file === b.file && a.rank === b.rank
}
