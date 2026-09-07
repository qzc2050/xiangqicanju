import {
  generateLegalMoves,
  isInCheck,
  parseFen,
  findKing,
  placementIssues,
} from '../src/engine'
import { PUZZLES } from '../src/puzzles/catalog'

let bad = 0
let placeBad = 0
for (const p of PUZZLES) {
  try {
    const pos = parseFen(p.fen)
    const moves = generateLegalMoves(pos)
    const rk = findKing(pos, 'red')
    const bk = findKing(pos, 'black')
    const chk = isInCheck(pos, pos.sideToMove)
    const place = placementIssues(pos)
    console.log(
      p.id,
      'legal',
      moves.length,
      'stm',
      pos.sideToMove,
      'kings',
      rk && bk ? 'ok' : 'MISSING',
      chk ? 'IN_CHECK' : '',
      place.length ? `PLACE:${place.join(';')}` : '',
    )
    if (moves.length === 0) {
      console.error('  NO MOVES', p.id)
      bad += 1
    }
    if (place.length) {
      console.error('  ILLEGAL PLACE', p.id, place.join('; '))
      placeBad += 1
      bad += 1
    }
  } catch (e) {
    console.error('BAD FEN', p.id, e)
    bad += 1
  }
}
console.log(`placement_illegal ${placeBad}/${PUZZLES.length}`)
if (bad) process.exitCode = 1
