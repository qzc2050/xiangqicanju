const KEY = 'xiangqi-endgame-progress-v1'

export type ProgressMap = Record<string, { cleared: boolean; clearedAt?: number }>

export function loadProgress(): ProgressMap {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return {}
    return JSON.parse(raw) as ProgressMap
  } catch {
    return {}
  }
}

export function markCleared(puzzleId: string): ProgressMap {
  const map = loadProgress()
  map[puzzleId] = { cleared: true, clearedAt: Date.now() }
  localStorage.setItem(KEY, JSON.stringify(map))
  return map
}

export function isCleared(puzzleId: string): boolean {
  return Boolean(loadProgress()[puzzleId]?.cleared)
}

export function clearedCount(ids: string[]): number {
  const map = loadProgress()
  return ids.filter((id) => map[id]?.cleared).length
}
