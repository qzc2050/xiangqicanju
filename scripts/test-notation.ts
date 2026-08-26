import { formatMoveChinese, parseFen, type Move } from '../src/engine'

// 开局：炮二平五
const start = parseFen('rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w')
const c2e2: Move = { from: { file: 7, rank: 2 }, to: { file: 4, rank: 2 } }
console.log('炮二平五?', formatMoveChinese(start, c2e2))

// 马二进三：红马从 h0(file7,rank0) 到 g2(file6,rank2) — 初始马在 b0 和 h0
// 红右马：file 7 rank 0 -> file 6 rank 2 = 马二进三
const n2: Move = { from: { file: 7, rank: 0 }, to: { file: 6, rank: 2 } }
console.log('马二进三?', formatMoveChinese(start, n2))

// 相三进五：file 6 rank 0 -> file 4 rank 2
const b: Move = { from: { file: 6, rank: 0 }, to: { file: 4, rank: 2 } }
console.log('相三进五?', formatMoveChinese(start, b))
