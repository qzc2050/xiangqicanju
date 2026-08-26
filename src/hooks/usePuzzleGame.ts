import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  getEngineMode,
  prepareEngine,
  requestBestMove,
  requestSolutionLine,
} from '../ai/client'
import {
  applyMove,
  formatMoveChinese,
  generateLegalMoves,
  isCheckmate,
  parseFen,
  sameSq,
  toFen,
  type Move,
  type Position,
  type Side,
  type Square,
} from '../engine'
import type { Puzzle } from '../puzzles/catalog'
import { markCleared } from '../storage/progress'

export type GameStatus = 'playing' | 'won' | 'lost' | 'draw'

const AI_MOVE_MS = 1200
const AI_HINT_MS = 1500

type HistoryEntry = { fen: string; move: Move | null }

export function usePuzzleGame(puzzle: Puzzle) {
  const initial = useMemo(() => parseFen(puzzle.fen), [puzzle.fen])
  const [pos, setPos] = useState<Position>(initial)
  const [selected, setSelected] = useState<Square | null>(null)
  const [hintMove, setHintMove] = useState<Move | null>(null)
  const [lastMove, setLastMove] = useState<Move | null>(null)
  const [status, setStatus] = useState<GameStatus>('playing')
  const [message, setMessage] = useState('正在加载皮卡鱼引擎…')
  const [aiThinking, setAiThinking] = useState(false)
  const [engineLabel, setEngineLabel] = useState('加载中')
  const [history, setHistory] = useState<HistoryEntry[]>([{ fen: puzzle.fen, move: null }])
  const [playerSide, setPlayerSideState] = useState<Side>(puzzle.winSide)
  const [solutionMode, setSolutionMode] = useState(false)
  const [solutionLoading, setSolutionLoading] = useState(false)
  const [solutionMoves, setSolutionMoves] = useState<Move[]>([])
  const [solutionPly, setSolutionPly] = useState(0)
  const historyRef = useRef(history)
  historyRef.current = history

  const pushHistory = useCallback((entry: HistoryEntry) => {
    setHistory((h) => [...h, entry])
  }, [])

  const legal = useMemo(() => {
    if (
      solutionMode ||
      status !== 'playing' ||
      pos.sideToMove !== playerSide ||
      aiThinking
    ) {
      return []
    }
    return generateLegalMoves(pos, playerSide)
  }, [pos, playerSide, status, aiThinking, solutionMode])

  const legalTargets = useMemo(() => {
    if (!selected) return []
    return legal.filter((m) => sameSq(m.from, selected)).map((m) => m.to)
  }, [legal, selected])

  const maybeClear = useCallback(
    (side: Side) => {
      if (puzzle.goal === 'draw') return
      if (side === puzzle.winSide) markCleared(puzzle.id)
    },
    [puzzle.goal, puzzle.id, puzzle.winSide],
  )

  const markPracticed = useCallback(() => {
    markCleared(puzzle.id)
    setMessage(puzzle.goal === 'draw' ? '已记为练过（和局）' : '已记为通关')
  }, [puzzle.goal, puzzle.id])

  const finishIfMate = useCallback(
    (next: Position, side: Side = playerSide) => {
      if (isCheckmate(next, next.sideToMove)) {
        if (next.sideToMove !== side) {
          if (puzzle.goal === 'draw') {
            setStatus('lost')
            setMessage('破和了：和局题不以将死为通关')
            return true
          }
          setStatus('won')
          setMessage(side === puzzle.winSide ? '将死！通关' : '将死！（防守方练习）')
          maybeClear(side)
          return true
        }
        setStatus('lost')
        setMessage('被将死了，再试一次')
        return true
      }
      return false
    },
    [maybeClear, playerSide, puzzle.goal, puzzle.winSide],
  )

  const playAi = useCallback(
    async (afterPlayer: Position, side: Side = playerSide) => {
      if (afterPlayer.sideToMove === side) return
      setAiThinking(true)
      setMessage(`${getEngineMode() === 'pikafish' ? '皮卡鱼' : 'AI'} 思考中…`)
      try {
        const move = await requestBestMove(toFen(afterPlayer), AI_MOVE_MS, 8)
        if (!move) {
          setStatus('won')
          setMessage(side === puzzle.winSide ? '对方无棋，通关' : '对方无棋')
          maybeClear(side)
          return
        }
        const next = applyMove(afterPlayer, move)
        setPos(next)
        setLastMove(move)
        pushHistory({ fen: toFen(next), move })
        if (!finishIfMate(next, side)) setMessage('轮到你走')
      } catch {
        setMessage('引擎暂不可用，可悔棋或看正解')
      } finally {
        setAiThinking(false)
      }
    },
    [finishIfMate, maybeClear, playerSide, puzzle.winSide, pushHistory],
  )

  const clearSolution = useCallback(() => {
    setSolutionMode(false)
    setSolutionLoading(false)
    setSolutionMoves([])
    setSolutionPly(0)
  }, [])

  const applySolutionPly = useCallback(
    (moves: Move[], ply: number) => {
      let cur = parseFen(puzzle.fen)
      let last: Move | null = null
      for (let i = 0; i < ply; i++) {
        last = moves[i]
        cur = applyMove(cur, moves[i])
      }
      setPos(cur)
      setLastMove(last)
      setSolutionPly(ply)
      setSelected(null)
      setHintMove(null)
      if (ply === 0) setMessage('正解 · 开局，点下一步或点棋谱')
      else if (ply >= moves.length) setMessage('正解 · 已到变例末手')
      else setMessage(`正解 · 第 ${ply}/${moves.length} 手`)
    },
    [puzzle.fen],
  )

  const reset = useCallback(
    (side: Side = playerSide) => {
      clearSolution()
      const p = parseFen(puzzle.fen)
      setPos(p)
      setSelected(null)
      setHintMove(null)
      setLastMove(null)
      setStatus('playing')
      setAiThinking(false)
      setHistory([{ fen: puzzle.fen, move: null }])
      if (p.sideToMove === side) {
        setMessage('轮到你走')
      } else {
        setMessage('等待引擎先走…')
        void playAi(p, side)
      }
    },
    [clearSolution, playAi, playerSide, puzzle.fen],
  )

  const setPlayerSide = useCallback(
    (side: Side) => {
      if (aiThinking || solutionLoading) return
      clearSolution()
      setPlayerSideState(side)
      const p = parseFen(puzzle.fen)
      setPos(p)
      setSelected(null)
      setHintMove(null)
      setLastMove(null)
      setStatus('playing')
      setHistory([{ fen: puzzle.fen, move: null }])
      if (p.sideToMove === side) {
        setMessage(`执${side === 'red' ? '红' : '黑'} · 轮到你走`)
      } else {
        void playAi(p, side)
      }
    },
    [aiThinking, clearSolution, playAi, puzzle.fen, solutionLoading],
  )

  useEffect(() => {
    setPlayerSideState(puzzle.winSide)
  }, [puzzle.id, puzzle.winSide])

  useEffect(() => {
    reset(puzzle.winSide)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [puzzle.id])

  useEffect(() => {
    let alive = true
    setMessage('正在加载皮卡鱼引擎…')
    void prepareEngine().then((mode) => {
      if (!alive) return
      if (mode === 'pikafish') {
        setEngineLabel('皮卡鱼')
        setMessage('皮卡鱼已就绪，轮到你走')
      } else {
        setEngineLabel('内置弱引擎')
        setMessage('皮卡鱼加载失败，已用弱引擎 · 轮到你走')
      }
    })
    return () => {
      alive = false
    }
  }, [puzzle.id])

  const tryMove = useCallback(
    async (from: Square, to: Square) => {
      if (
        solutionMode ||
        status !== 'playing' ||
        aiThinking ||
        pos.sideToMove !== playerSide
      ) {
        return
      }
      const move = legal.find((m) => sameSq(m.from, from) && sameSq(m.to, to))
      if (!move) {
        setSelected(null)
        return
      }
      const next = applyMove(pos, move)
      setPos(next)
      setLastMove(move)
      setSelected(null)
      setHintMove(null)
      pushHistory({ fen: toFen(next), move })
      if (finishIfMate(next)) return
      await playAi(next)
    },
    [
      aiThinking,
      finishIfMate,
      legal,
      playAi,
      playerSide,
      pos,
      pushHistory,
      solutionMode,
      status,
    ],
  )

  const onSquareClick = useCallback(
    (sq: Square) => {
      if (
        solutionMode ||
        status !== 'playing' ||
        aiThinking ||
        pos.sideToMove !== playerSide
      ) {
        return
      }
      const piece = pos.board[sq.rank][sq.file]
      if (selected) {
        if (sameSq(selected, sq)) {
          setSelected(null)
          return
        }
        const canGo = legalTargets.some((t) => sameSq(t, sq))
        if (canGo) {
          void tryMove(selected, sq)
          return
        }
        if (piece && piece.side === playerSide) {
          setSelected(sq)
          return
        }
        setSelected(null)
        return
      }
      if (piece && piece.side === playerSide) setSelected(sq)
    },
    [
      aiThinking,
      legalTargets,
      playerSide,
      pos,
      selected,
      solutionMode,
      status,
      tryMove,
    ],
  )

  const undo = useCallback(() => {
    if (solutionMode || aiThinking || historyRef.current.length <= 1) return
    let hist = historyRef.current.slice(0, -1)
    while (hist.length > 1) {
      const p = parseFen(hist[hist.length - 1].fen)
      if (p.sideToMove === playerSide) break
      hist = hist.slice(0, -1)
    }
    setHistory(hist)
    const p = parseFen(hist[hist.length - 1].fen)
    setPos(p)
    setLastMove(hist[hist.length - 1].move)
    setSelected(null)
    setHintMove(null)
    setStatus('playing')
    setMessage('轮到你走')
  }, [aiThinking, playerSide, solutionMode])

  const showHint = useCallback(async () => {
    if (
      solutionMode ||
      status !== 'playing' ||
      aiThinking ||
      pos.sideToMove !== playerSide
    ) {
      return
    }
    setMessage('皮卡鱼计算提示…')
    try {
      const move = await requestBestMove(toFen(pos), AI_HINT_MS, 8)
      if (move) {
        setHintMove(move)
        setSelected(move.from)
        setMessage(`提示：${formatMoveChinese(pos, move)}`)
      } else setMessage('没有合法着法')
    } catch {
      setMessage('提示失败')
    }
  }, [aiThinking, playerSide, pos, solutionMode, status])

  const openSolution = useCallback(async () => {
    if (aiThinking || solutionLoading) return
    setHintMove(null)
    setSelected(null)
    setSolutionMode(true)
    setSolutionLoading(true)
    setMessage('正在生成棋谱…')
    try {
      const line = await requestSolutionLine(puzzle.fen, undefined, 36)
      if (!line.length) {
        setMessage('未能生成变例')
        setSolutionMode(false)
        return
      }
      setSolutionMoves(line)
      applySolutionPly(line, 0)
      setStatus('playing')
      setHistory([{ fen: puzzle.fen, move: null }])
    } catch {
      setMessage('生成棋谱失败')
      setSolutionMode(false)
    } finally {
      setSolutionLoading(false)
    }
  }, [aiThinking, applySolutionPly, puzzle.fen, solutionLoading])

  const solutionGoto = useCallback(
    (ply: number) => {
      if (!solutionMoves.length) return
      const clamped = Math.max(0, Math.min(ply, solutionMoves.length))
      applySolutionPly(solutionMoves, clamped)
    },
    [applySolutionPly, solutionMoves],
  )

  const solutionPrev = useCallback(() => {
    solutionGoto(solutionPly - 1)
  }, [solutionGoto, solutionPly])

  const solutionNext = useCallback(() => {
    solutionGoto(solutionPly + 1)
  }, [solutionGoto, solutionPly])

  const exitSolution = useCallback(() => {
    reset(playerSide)
  }, [playerSide, reset])

  return {
    pos,
    selected,
    legalTargets,
    hintMove,
    lastMove,
    status,
    message,
    aiThinking,
    engineLabel,
    playerSide,
    setPlayerSide,
    onSquareClick,
    undo,
    reset: () => reset(playerSide),
    showHint,
    openSolution,
    solutionMode,
    solutionLoading,
    solutionMoves,
    solutionPly,
    solutionGoto,
    solutionPrev,
    solutionNext,
    markPracticed,
    exitSolution,
    canUndo: !solutionMode && history.length > 1 && !aiThinking,
  }
}
