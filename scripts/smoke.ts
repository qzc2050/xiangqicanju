import { findBestMove } from '../src/ai/search'
import {
  applyMove,
  generateLegalMoves,
  moveToIccs,
  parseFen,
} from '../src/engine'
import { PUZZLES } from '../src/puzzles/catalog'

for (const p of PUZZLES) {
  const pos = parseFen(p.fen)
  const moves = generateLegalMoves(pos)
  console.log(p.id, 'legal', moves.length, 'stm', pos.sideToMove)
  if (moves.length === 0) console.error('NO MOVES', p.id)
  if (p.solution) {
    let cur = pos
    for (const s of p.solution) {
      const legal = generateLegalMoves(cur).map(moveToIccs)
      if (!legal.includes(s)) {
        console.error('BAD SOLUTION', p.id, s, 'legal', legal.slice(0, 12))
        break
      }
      const m = generateLegalMoves(cur).find((x) => moveToIccs(x) === s)!
      cur = applyMove(cur, m)
    }
  }
}
const pos = parseFen(PUZZLES[0].fen)
const best = findBestMove(pos, 300, 3)
console.log('AI', best.move ? moveToIccs(best.move) : null, 'nodes', best.nodes)
