import { applyMove, findKing, getPiece } from './board'
import { FILES, RANKS, otherSide, type Move, type Position, type Side, type Square } from './types'

function inPalace(sq: Square, side: Side): boolean {
  if (sq.file < 3 || sq.file > 5) return false
  return side === 'red' ? sq.rank >= 0 && sq.rank <= 2 : sq.rank >= 7 && sq.rank <= 9
}

function onBoard(sq: Square): boolean {
  return sq.file >= 0 && sq.file < FILES && sq.rank >= 0 && sq.rank < RANKS
}

function push(moves: Move[], from: Square, to: Square, pos: Position, side: Side): void {
  if (!onBoard(to)) return
  const target = getPiece(pos, to)
  if (target && target.side === side) return
  moves.push({ from, to })
}

function genKing(pos: Position, from: Square, side: Side, moves: Move[]): void {
  const deltas = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ]
  for (const [df, dr] of deltas) {
    const to = { file: from.file + df, rank: from.rank + dr }
    if (!inPalace(to, side)) continue
    push(moves, from, to, pos, side)
  }
}

function genAdvisor(pos: Position, from: Square, side: Side, moves: Move[]): void {
  for (const [df, dr] of [
    [1, 1],
    [1, -1],
    [-1, 1],
    [-1, -1],
  ]) {
    const to = { file: from.file + df, rank: from.rank + dr }
    if (!inPalace(to, side)) continue
    push(moves, from, to, pos, side)
  }
}

function genElephant(pos: Position, from: Square, side: Side, moves: Move[]): void {
  for (const [df, dr] of [
    [2, 2],
    [2, -2],
    [-2, 2],
    [-2, -2],
  ]) {
    const eye = { file: from.file + df / 2, rank: from.rank + dr / 2 }
    if (getPiece(pos, eye)) continue
    const to = { file: from.file + df, rank: from.rank + dr }
    if (!onBoard(to)) continue
    if (side === 'red' && to.rank > 4) continue
    if (side === 'black' && to.rank < 5) continue
    push(moves, from, to, pos, side)
  }
}

function genHorse(pos: Position, from: Square, side: Side, moves: Move[]): void {
  const hops: [number, number, number, number][] = [
    [1, 0, 1, 1],
    [1, 0, 1, -1],
    [-1, 0, -1, 1],
    [-1, 0, -1, -1],
    [0, 1, 1, 1],
    [0, 1, -1, 1],
    [0, -1, 1, -1],
    [0, -1, -1, -1],
  ]
  for (const [bf, br, df, dr] of hops) {
    const block = { file: from.file + bf, rank: from.rank + br }
    if (!onBoard(block) || getPiece(pos, block)) continue
    const to = { file: from.file + bf + df, rank: from.rank + br + dr }
    push(moves, from, to, pos, side)
  }
}

function genSlider(
  pos: Position,
  from: Square,
  side: Side,
  moves: Move[],
  dirs: [number, number][],
  cannon: boolean,
): void {
  for (const [df, dr] of dirs) {
    let jumped = false
    let f = from.file + df
    let r = from.rank + dr
    while (f >= 0 && f < FILES && r >= 0 && r < RANKS) {
      const to = { file: f, rank: r }
      const target = getPiece(pos, to)
      if (!cannon) {
        if (!target) moves.push({ from, to })
        else {
          if (target.side !== side) moves.push({ from, to })
          break
        }
      } else if (!jumped) {
        if (!target) moves.push({ from, to })
        else jumped = true
      } else {
        if (target) {
          if (target.side !== side) moves.push({ from, to })
          break
        }
      }
      f += df
      r += dr
    }
  }
}

function genPawn(pos: Position, from: Square, side: Side, moves: Move[]): void {
  const forward = side === 'red' ? 1 : -1
  push(moves, from, { file: from.file, rank: from.rank + forward }, pos, side)
  const crossed = side === 'red' ? from.rank >= 5 : from.rank <= 4
  if (crossed) {
    push(moves, from, { file: from.file + 1, rank: from.rank }, pos, side)
    push(moves, from, { file: from.file - 1, rank: from.rank }, pos, side)
  }
}

const ORTHO: [number, number][] = [
  [1, 0],
  [-1, 0],
  [0, 1],
  [0, -1],
]

export function generatePseudoMoves(pos: Position, side: Side): Move[] {
  const moves: Move[] = []
  for (let rank = 0; rank < RANKS; rank++) {
    for (let file = 0; file < FILES; file++) {
      const piece = pos.board[rank][file]
      if (!piece || piece.side !== side) continue
      const from = { file, rank }
      switch (piece.kind) {
        case 'K':
          genKing(pos, from, side, moves)
          break
        case 'A':
          genAdvisor(pos, from, side, moves)
          break
        case 'B':
          genElephant(pos, from, side, moves)
          break
        case 'N':
          genHorse(pos, from, side, moves)
          break
        case 'R':
          genSlider(pos, from, side, moves, ORTHO, false)
          break
        case 'C':
          genSlider(pos, from, side, moves, ORTHO, true)
          break
        case 'P':
          genPawn(pos, from, side, moves)
          break
      }
    }
  }
  return moves
}

function kingsFace(pos: Position): boolean {
  const rk = findKing(pos, 'red')
  const bk = findKing(pos, 'black')
  if (!rk || !bk || rk.file !== bk.file) return false
  const lo = Math.min(rk.rank, bk.rank)
  const hi = Math.max(rk.rank, bk.rank)
  for (let r = lo + 1; r < hi; r++) {
    if (pos.board[r][rk.file]) return false
  }
  return true
}

/** 某方是否被将军（含将帅对面） */
export function isInCheck(pos: Position, side: Side): boolean {
  if (kingsFace(pos)) return true
  const king = findKing(pos, side)
  if (!king) return true
  const attacks = generatePseudoMoves(pos, otherSide(side))
  return attacks.some((m) => m.to.file === king.file && m.to.rank === king.rank)
}

export function generateLegalMoves(pos: Position, side: Side = pos.sideToMove): Move[] {
  const pseudo = generatePseudoMoves(pos, side)
  const legal: Move[] = []
  for (const move of pseudo) {
    const target = getPiece(pos, move.to)
    if (target?.kind === 'K') continue
    const next = applyMove({ ...pos, sideToMove: side }, move)
    if (!isInCheck(next, side)) legal.push(move)
  }
  return legal
}

export function isCheckmate(pos: Position, side: Side = pos.sideToMove): boolean {
  return isInCheck(pos, side) && generateLegalMoves(pos, side).length === 0
}

export function isStalemate(pos: Position, side: Side = pos.sideToMove): boolean {
  return !isInCheck(pos, side) && generateLegalMoves(pos, side).length === 0
}
