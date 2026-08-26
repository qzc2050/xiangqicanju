import { applyMove, findKing, generateLegalMoves, isInCheck, toFen } from '../engine'
import type { Move, PieceKind, Position, Side } from '../engine'

const MATERIAL: Record<PieceKind, number> = {
  K: 100000,
  R: 1000,
  C: 450,
  N: 400,
  B: 200,
  A: 200,
  P: 100,
}

/** 简单位置分：过河兵、车占中等 */
function evalPos(pos: Position, perspective: Side): number {
  let score = 0
  for (let rank = 0; rank < 10; rank++) {
    for (let file = 0; file < 9; file++) {
      const p = pos.board[rank][file]
      if (!p) continue
      let v = MATERIAL[p.kind]
      if (p.kind === 'P') {
        if (p.side === 'red' && rank >= 5) v += 40 + (rank - 5) * 10
        if (p.side === 'black' && rank <= 4) v += 40 + (4 - rank) * 10
      }
      if (p.kind === 'R' || p.kind === 'C') {
        if (file === 4) v += 15
      }
      score += p.side === perspective ? v : -v
    }
  }
  if (isInCheck(pos, perspective === 'red' ? 'black' : 'red')) score += 30
  if (isInCheck(pos, perspective)) score -= 30

  const myKing = findKing(pos, perspective)
  const opKing = findKing(pos, perspective === 'red' ? 'black' : 'red')
  if (myKing && opKing) {
    score -= Math.abs(myKing.file - opKing.file) * 2
  }
  return score
}

type SearchResult = { move: Move | null; score: number; nodes: number }

function orderMoves(pos: Position, moves: Move[]): Move[] {
  return moves
    .map((m) => {
      const cap = pos.board[m.to.rank][m.to.file]
      const see = cap ? MATERIAL[cap.kind] : 0
      return { m, see }
    })
    .sort((a, b) => b.see - a.see)
    .map((x) => x.m)
}

function alphabeta(
  pos: Position,
  depth: number,
  alpha: number,
  beta: number,
  perspective: Side,
  deadline: number,
  state: { nodes: number; aborted: boolean },
): number {
  if (performance.now() > deadline) {
    state.aborted = true
    return evalPos(pos, perspective)
  }
  state.nodes += 1

  const side = pos.sideToMove
  const moves = generateLegalMoves(pos, side)
  if (moves.length === 0) {
    if (isInCheck(pos, side)) {
      return side === perspective ? -90000 + (4 - depth) : 90000 - (4 - depth)
    }
    return 0
  }
  if (depth <= 0) return evalPos(pos, perspective)

  const ordered = orderMoves(pos, moves)
  if (side === perspective) {
    let best = -Infinity
    for (const move of ordered) {
      const next = applyMove(pos, move)
      const score = alphabeta(next, depth - 1, alpha, beta, perspective, deadline, state)
      if (score > best) best = score
      if (best > alpha) alpha = best
      if (alpha >= beta || state.aborted) break
    }
    return best
  }
  let best = Infinity
  for (const move of ordered) {
    const next = applyMove(pos, move)
    const score = alphabeta(next, depth - 1, alpha, beta, perspective, deadline, state)
    if (score < best) best = score
    if (best < beta) beta = best
    if (alpha >= beta || state.aborted) break
  }
  return best
}

export function findBestMove(
  pos: Position,
  timeMs = 500,
  maxDepth = 4,
): { move: Move | null; fen: string; nodes: number } {
  const deadline = performance.now() + timeMs
  const perspective = pos.sideToMove
  const rootMoves = orderMoves(pos, generateLegalMoves(pos, perspective))
  if (rootMoves.length === 0) {
    return { move: null, fen: toFen(pos), nodes: 0 }
  }

  let best: SearchResult = { move: rootMoves[0], score: -Infinity, nodes: 0 }

  for (let depth = 1; depth <= maxDepth; depth++) {
    const state = { nodes: 0, aborted: false }
    let iterBest: SearchResult = { move: rootMoves[0], score: -Infinity, nodes: 0 }
    let alpha = -Infinity
    const beta = Infinity

    for (const move of rootMoves) {
      if (performance.now() > deadline) {
        state.aborted = true
        break
      }
      const next = applyMove(pos, move)
      const score = alphabeta(next, depth - 1, alpha, beta, perspective, deadline, state)
      if (score > iterBest.score) {
        iterBest = { move, score, nodes: state.nodes }
        alpha = score
      }
    }
    iterBest.nodes = state.nodes
    if (!state.aborted || depth === 1) best = iterBest
    if (state.aborted) break
    if (best.score > 80000) break
  }

  return { move: best.move, fen: toFen(pos), nodes: best.nodes }
}
