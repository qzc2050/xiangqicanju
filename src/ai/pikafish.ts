import { iccsToMove, type Move } from '../engine'

type GoResult =
  | { ok: true; move: Move | null; pv: Move[] }
  | { ok: false; error: string }

let worker: Worker | null = null
let seq = 1
let initPromise: Promise<void> | null = null
const pending = new Map<
  number,
  { resolve: (v: GoResult) => void; reject: (e: Error) => void }
>()

function parseMoves(list: string[] | undefined): Move[] {
  if (!list?.length) return []
  const out: Move[] = []
  for (const s of list) {
    try {
      out.push(iccsToMove(s))
    } catch {
      break
    }
  }
  return out
}

function ensureWorker(): Worker {
  if (!worker) {
    worker = new Worker(`${import.meta.env.BASE_URL}wasm/pikafish-worker.js`)
    worker.onmessage = (ev: MessageEvent) => {
      const data = ev.data as {
        id: number
        ok: boolean
        type?: string
        move?: string | null
        pv?: string[]
        error?: string
      }
      const job = pending.get(data.id)
      if (!job) return
      pending.delete(data.id)
      if (!data.ok) {
        job.resolve({ ok: false, error: data.error ?? 'pikafish error' })
        return
      }
      if (data.type === 'ready') {
        job.resolve({ ok: true, move: null, pv: [] })
        return
      }
      let move: Move | null = null
      if (data.move) {
        try {
          move = iccsToMove(data.move)
        } catch {
          job.resolve({ ok: false, error: `bad move ${data.move}` })
          return
        }
      }
      job.resolve({ ok: true, move, pv: parseMoves(data.pv) })
    }
    worker.onerror = (err) => {
      for (const [, job] of pending) {
        job.resolve({ ok: false, error: err.message || 'pikafish worker failed' })
      }
      pending.clear()
      worker = null
      initPromise = null
    }
  }
  return worker
}

function call(payload: Record<string, unknown>): Promise<GoResult> {
  const id = seq++
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject })
    ensureWorker().postMessage({ ...payload, id })
  })
}

/** 懒加载皮卡鱼（首次约下载数 MB 引擎+NNUE） */
export function warmPikafish(): Promise<void> {
  if (!initPromise) {
    initPromise = call({ type: 'init' }).then((r) => {
      if (!r.ok) {
        initPromise = null
        throw new Error(r.error)
      }
    })
  }
  return initPromise
}

export async function pikafishBestMove(
  fen: string,
  timeMs = 1200,
): Promise<Move | null> {
  await warmPikafish()
  const r = await call({ type: 'go', fen, timeMs })
  if (!r.ok) throw new Error(r.error)
  return r.move
}

/** 返回主变 PV（含 bestmove） */
export async function pikafishPv(
  fen: string,
  timeMs = 2000,
): Promise<Move[]> {
  await warmPikafish()
  const r = await call({ type: 'goPv', fen, timeMs })
  if (!r.ok) throw new Error(r.error)
  if (r.pv.length) return r.pv
  return r.move ? [r.move] : []
}

export function isPikafishSupported(): boolean {
  return typeof Worker !== 'undefined' && typeof WebAssembly !== 'undefined'
}
