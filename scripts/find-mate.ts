import {
  applyMove,
  generateLegalMoves,
  isCheckmate,
  moveToIccs,
  parseFen,
  type Move,
  type Position,
} from '../src/engine'

function searchMate(fen: string, maxPlies: number): string[] | null {
  const root = parseFen(fen)

  function dfs(pos: Position, line: string[], ply: number): string[] | null {
    if (isCheckmate(pos, pos.sideToMove)) return line
    if (ply >= maxPlies) return null
    const moves = generateLegalMoves(pos)
    // 优先将军/吃子以加速
    const ordered = [...moves].sort((a, b) => score(pos, b) - score(pos, a))
    for (const m of ordered) {
      const next = applyMove(pos, m)
      const found = dfs(next, [...line, moveToIccs(m)], ply + 1)
      if (found) return found
    }
    return null
  }

  return dfs(root, [], 0)
}

function score(pos: Position, m: Move): number {
  const cap = pos.board[m.to.rank][m.to.file]
  return cap ? 10 : 0
}

for (const fen of [
  '4k4/9/9/9/9/9/9/9/9/3K4R w',
  '3k5/9/9/9/9/9/9/9/9/4K2R1 w',
  '4k4/9/9/9/9/9/9/9/9/R2K2R2 w',
]) {
  console.log(fen, '->', searchMate(fen, 5))
}
