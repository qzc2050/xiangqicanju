import { readFileSync, writeFileSync } from 'fs'
import { parseFen } from '../src/engine/board.ts'

const text = readFileSync('src/puzzles/catalog.ts', 'utf8')
const re = /id: 'o-[cp]-(\d+)'[\s\S]*?fen: '([^']+)'/g
const pages: Record<number, string> = {
  25: 'page-034.png', 26: 'page-035.png', 27: 'page-035.png', 28: 'page-036.png',
  29: 'page-037.png', 30: 'page-037.png', 31: 'page-038.png', 32: 'page-039.png',
  33: 'page-039.png', 34: 'page-040.png', 35: 'page-041.png', 36: 'page-042.png',
  37: 'page-042.png', 38: 'page-043.png', 39: 'page-044.png', 40: 'page-045.png',
  41: 'page-047.png', 42: 'page-048.png', 43: 'page-050.png', 44: 'page-051.png',
  45: 'page-052.png', 46: 'page-053.png', 47: 'page-053.png', 48: 'page-054.png',
  49: 'page-055.png', 50: 'page-056.png', 51: 'page-057.png',
}

const overrides: Record<number, { pieces: [string, string, number, number][]; stm: string }> = {
  25: { pieces: [['black','K',0,6],['black','A',1,5],['black','A',2,4],['red','A',7,6],['red','C',8,2],['red','K',9,5]], stm: 'w' },
  26: { pieces: [['black','K',0,5],['black','C',1,6],['black','A',2,4],['black','A',2,6],['black','B',2,1],['black','B',4,3],['red','B',7,9],['red','A',7,4],['red','K',8,4]], stm: 'w' },
  27: { pieces: [['black','K',0,5],['black','R',5,8],['red','C',7,6],['red','A',8,5],['red','A',9,6],['red','K',9,4]], stm: 'w' },
  28: { pieces: [['black','K',0,5],['black','R',5,8],['red','C',5,5],['red','B',7,5],['red','B',9,3],['red','K',9,5]], stm: 'w' },
  29: { pieces: [['black','K',0,5],['black','B',2,5],['black','B',4,3],['black','C',4,5],['red','R',3,8],['red','K',9,5]], stm: 'w' },
  30: { pieces: [['black','K',0,5],['black','P',3,3],['black','P',3,5],['black','P',3,7],['red','C',7,5],['red','A',8,5],['red','A',9,4],['red','K',9,5]], stm: 'w' },
  31: { pieces: [['black','K',0,5],['black','P',3,5],['black','R',5,7],['red','B',7,5],['red','B',9,3],['red','C',7,5],['red','A',8,5],['red','A',9,4],['red','K',9,5]], stm: 'w' },
  51: { pieces: [['black','K',0,4],['black','A',0,6],['black','A',1,6],['black','B',2,3],['black','B',2,6],['red','P',4,4],['red','P',4,6],['red','P',5,7],['red','K',9,6]], stm: 'w' },
  32: { pieces: [['black','K',2,5],['black','A',1,5],['black','C',0,6],['black','C',2,9],['black','P',8,5],['red','K',7,6],['red','C',9,8]], stm: 'w' },
  33: { pieces: [['black','K',2,5],['black','B',2,6],['red','P',1,6],['red','K',7,6],['red','C',9,8]], stm: 'w' },
}

const out: Record<string, unknown> = {}
let m: RegExpExecArray | null
while ((m = re.exec(text))) {
  const n = +m[1]
  if (n < 25 || n > 51) continue
  if (overrides[n]) {
    out[`fig${n}`] = { ...overrides[n], page: pages[n] }
    continue
  }
  const fen = m[2]
  const p = parseFen(fen)
  const stm = fen.split(' ')[1] === 'b' ? 'b' : 'w'
  const pieces: [string, string, number, number][] = []
  for (let r = 0; r < 10; r++)
    for (let f = 0; f < 9; f++) {
      const pc = p.board[r][f]
      if (pc) pieces.push([pc.side, pc.kind, 9 - r, f + 1])
    }
  out[`fig${n}`] = { pieces, stm: n === 37 ? 'w' : stm, page: pages[n] }
}

process.stdout.write(JSON.stringify(out))
