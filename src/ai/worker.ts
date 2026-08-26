import { parseFen, type Move } from '../engine'
import { findBestMove } from './search'

export type AiRequest = {
  id: number
  fen: string
  timeMs?: number
  maxDepth?: number
}

export type AiResponse = {
  id: number
  ok: boolean
  move: Move | null
  error?: string
  nodes?: number
}

self.onmessage = (ev: MessageEvent<AiRequest>) => {
  const { id, fen, timeMs = 450, maxDepth = 3 } = ev.data
  try {
    const pos = parseFen(fen)
    const result = findBestMove(pos, timeMs, maxDepth)
    const response: AiResponse = {
      id,
      ok: true,
      move: result.move,
      nodes: result.nodes,
    }
    postMessage(response)
  } catch (e) {
    const response: AiResponse = {
      id,
      ok: false,
      move: null,
      error: e instanceof Error ? e.message : String(e),
    }
    postMessage(response)
  }
}
