import {
  generateLegalMoves,
  isInCheck,
  parseFen,
  findKing,
} from '../src/engine'
import { PUZZLES } from '../src/puzzles/catalog'

for (const p of PUZZLES) {
  try {
    const pos = parseFen(p.fen)
    const moves = generateLegalMoves(pos)
    const rk = findKing(pos, 'red')
    const bk = findKing(pos, 'black')
    const chk = isInCheck(pos, pos.sideToMove)
    console.log(
      p.id,
      'legal',
      moves.length,
      'stm',
      pos.sideToMove,
      'kings',
      rk && bk ? 'ok' : 'MISSING',
      chk ? 'IN_CHECK' : '',
    )
    if (moves.length === 0) console.error('  NO MOVES', p.id)
  } catch (e) {
    console.error('BAD FEN', p.id, e)
  }
}
