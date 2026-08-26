import {
  FILES,
  RANKS,
  type Move,
  type Piece,
  type PieceKind,
  type Position,
  type Side,
  type Square,
} from './types'

const FEN_MAP: Record<string, PieceKind> = {
  K: 'K',
  A: 'A',
  B: 'B',
  E: 'B',
  H: 'N',
  N: 'N',
  R: 'R',
  C: 'C',
  P: 'P',
}

export function emptyBoard(): (Piece | null)[][] {
  return Array.from({ length: RANKS }, () => Array.from({ length: FILES }, () => null))
}

export function clonePosition(pos: Position): Position {
  return {
    sideToMove: pos.sideToMove,
    board: pos.board.map((row) => row.slice()),
  }
}

export function getPiece(pos: Position, sq: Square): Piece | null {
  if (sq.file < 0 || sq.file >= FILES || sq.rank < 0 || sq.rank >= RANKS) return null
  return pos.board[sq.rank][sq.file]
}

export function setPiece(pos: Position, sq: Square, piece: Piece | null): void {
  pos.board[sq.rank][sq.file] = piece
}

/** FEN：从上到下为黑方底线→红方底线；大写红、小写黑；w/b 行棋方 */
export function parseFen(fen: string): Position {
  const parts = fen.trim().split(/\s+/)
  const rows = parts[0].split('/')
  if (rows.length !== 10) throw new Error(`Invalid FEN ranks: ${rows.length}`)

  const board = emptyBoard()
  for (let i = 0; i < 10; i++) {
    const rank = 9 - i
    let file = 0
    for (const ch of rows[i]) {
      if (ch >= '1' && ch <= '9') {
        file += Number(ch)
        continue
      }
      const upper = ch.toUpperCase()
      const kind = FEN_MAP[upper]
      if (!kind || file >= FILES) throw new Error(`Bad FEN at rank ${rank}: ${ch}`)
      board[rank][file] = {
        kind,
        side: ch === upper ? 'red' : 'black',
      }
      file += 1
    }
    if (file !== FILES) throw new Error(`Bad FEN width on rank ${rank}`)
  }

  const stm = parts[1] ?? 'w'
  const sideToMove: Side = stm === 'b' || stm === 'B' ? 'black' : 'red'
  return { board, sideToMove }
}

export function toFen(pos: Position): string {
  const rows: string[] = []
  for (let i = 0; i < 10; i++) {
    const rank = 9 - i
    let empty = 0
    let row = ''
    for (let file = 0; file < FILES; file++) {
      const p = pos.board[rank][file]
      if (!p) {
        empty += 1
        continue
      }
      if (empty) {
        row += String(empty)
        empty = 0
      }
      const ch = p.kind === 'B' ? 'B' : p.kind
      row += p.side === 'red' ? ch : ch.toLowerCase()
    }
    if (empty) row += String(empty)
    rows.push(row)
  }
  return `${rows.join('/')} ${pos.sideToMove === 'red' ? 'w' : 'b'}`
}

export function squareToIccs(sq: Square): string {
  return `${String.fromCharCode(97 + sq.file)}${sq.rank}`
}

export function iccsToSquare(iccs: string): Square {
  const file = iccs.charCodeAt(0) - 97
  const rank = Number(iccs.slice(1))
  return { file, rank }
}

export function moveToIccs(move: Move): string {
  return `${squareToIccs(move.from)}${squareToIccs(move.to)}`
}

export function iccsToMove(iccs: string): Move {
  return {
    from: iccsToSquare(iccs.slice(0, 2)),
    to: iccsToSquare(iccs.slice(2, 4)),
  }
}

export function findKing(pos: Position, side: Side): Square | null {
  for (let rank = 0; rank < RANKS; rank++) {
    for (let file = 0; file < FILES; file++) {
      const p = pos.board[rank][file]
      if (p && p.side === side && p.kind === 'K') return { file, rank }
    }
  }
  return null
}

export function applyMove(pos: Position, move: Move): Position {
  const next = clonePosition(pos)
  const piece = getPiece(next, move.from)
  setPiece(next, move.from, null)
  setPiece(next, move.to, piece)
  next.sideToMove = pos.sideToMove === 'red' ? 'black' : 'red'
  return next
}
