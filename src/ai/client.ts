import {
  applyMove,
  generateLegalMoves,
  iccsToMove,
  isCheckmate,
  moveToIccs,
  parseFen,
  toFen,
  type Move,
} from '../engine'
import {
  isPikafishSupported,
  pikafishBestMove,
  pikafishPv,
  warmPikafish,
} from './pikafish'
import type { AiRequest, AiResponse } from './worker'

type Pending = {
  resolve: (move: Move | null) => void
  reject: (err: Error) => void
}

let fallbackWorker: Worker | null = null
let seq = 1
const pending = new Map<number, Pending>()
let engineMode: 'pikafish' | 'fallback' | 'unknown' = 'unknown'

function getFallbackWorker(): Worker {
  if (!fallbackWorker) {
    fallbackWorker = new Worker(new URL('./worker.ts', import.meta.url), {
      type: 'module',
    })
    fallbackWorker.onmessage = (ev: MessageEvent<AiResponse>) => {
      const job = pending.get(ev.data.id)
      if (!job) return
      pending.delete(ev.data.id)
      if (!ev.data.ok) {
        job.reject(new Error(ev.data.error ?? 'AI error'))
        return
      }
      job.resolve(ev.data.move)
    }
    fallbackWorker.onerror = (err) => {
      for (const [, job] of pending) {
        job.reject(new Error(err.message || 'AI worker failed'))
      }
      pending.clear()
    }
  }
  return fallbackWorker
}

function fallbackBestMove(
  fen: string,
  timeMs: number,
  maxDepth: number,
): Promise<Move | null> {
  const id = seq++
  const req: AiRequest = { id, fen, timeMs, maxDepth }
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject })
    getFallbackWorker().postMessage(req)
  })
}

/** 预热强引擎（进对局页时调用） */
export async function prepareEngine(): Promise<'pikafish' | 'fallback'> {
  if (engineMode === 'pikafish') return 'pikafish'
  if (engineMode === 'fallback') return 'fallback'
  if (!isPikafishSupported()) {
    engineMode = 'fallback'
    return 'fallback'
  }
  try {
    await warmPikafish()
    engineMode = 'pikafish'
    return 'pikafish'
  } catch {
    engineMode = 'fallback'
    return 'fallback'
  }
}

export function getEngineMode(): typeof engineMode {
  return engineMode
}

export async function requestBestMove(
  fen: string,
  timeMs = 1200,
  maxDepth = 8,
): Promise<Move | null> {
  const mode = await prepareEngine()
  if (mode === 'pikafish') {
    try {
      return await pikafishBestMove(fen, timeMs)
    } catch {
      engineMode = 'fallback'
      return fallbackBestMove(fen, Math.min(timeMs, 800), maxDepth)
    }
  }
  return fallbackBestMove(fen, Math.min(timeMs, 800), maxDepth)
}

function filterLegalLine(startFen: string, moves: Move[]): Move[] {
  let pos = parseFen(startFen)
  const line: Move[] = []
  for (const m of moves) {
    const legal = generateLegalMoves(pos)
    const ok = legal.find(
      (x) =>
        x.from.file === m.from.file &&
        x.from.rank === m.from.rank &&
        x.to.file === m.to.file &&
        x.to.rank === m.to.rank,
    )
    if (!ok) break
    line.push(ok)
    pos = applyMove(pos, ok)
  }
  return line
}

/** 生成可浏览的正解/参考变例（棋谱） */
export async function requestSolutionLine(
  fen: string,
  seedIccs?: string[],
  maxPlies = 36,
): Promise<Move[]> {
  if (seedIccs?.length) {
    const seeded = filterLegalLine(
      fen,
      seedIccs.map((s) => iccsToMove(s)),
    )
    if (seeded.length) return seeded
  }

  const mode = await prepareEngine()
  let line: Move[] = []

  if (mode === 'pikafish') {
    try {
      const pv = await pikafishPv(fen, 2200)
      line = filterLegalLine(fen, pv)
    } catch {
      engineMode = 'fallback'
    }
  }

  let pos = parseFen(fen)
  for (const m of line) pos = applyMove(pos, m)

  // PV 够长就直接给棋谱；太短再逐步补到将死/上限
  const limit = line.length >= 8 ? line.length : maxPlies
  while (line.length < limit && !isCheckmate(pos, pos.sideToMove)) {
    const move = await requestBestMove(
      toFen(pos),
      mode === 'pikafish' ? 700 : 400,
      6,
    )
    if (!move) break
    const legal = generateLegalMoves(pos)
    const ok = legal.find(
      (x) =>
        x.from.file === move.from.file &&
        x.from.rank === move.from.rank &&
        x.to.file === move.to.file &&
        x.to.rank === move.to.rank,
    )
    if (!ok) break
    line.push(ok)
    pos = applyMove(pos, ok)
  }

  return line
}

export async function requestBestMoveIccs(
  fen: string,
  timeMs = 1200,
): Promise<string | null> {
  const move = await requestBestMove(fen, timeMs)
  return move ? moveToIccs(move) : null
}
