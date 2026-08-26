import { formatLineChinese, type Move } from '../engine'

type Props = {
  startFen: string
  moves: Move[]
  /** 0 = 开局，n = 已走到第 n 手之后 */
  plyIndex: number
  loading?: boolean
  onGoto: (plyIndex: number) => void
  onPrev: () => void
  onNext: () => void
  onExit: () => void
}

export function ScoreSheet({
  startFen,
  moves,
  plyIndex,
  loading,
  onGoto,
  onPrev,
  onNext,
  onExit,
}: Props) {
  const notations = formatLineChinese(startFen, moves)
  const atStart = plyIndex <= 0
  const atEnd = plyIndex >= moves.length

  return (
    <aside className="score-sheet" aria-label="正解棋谱">
      <div className="score-head">
        <strong>棋谱</strong>
        <button type="button" className="score-exit" onClick={onExit}>
          回练习
        </button>
      </div>

      {loading ? (
        <p className="score-loading">正在生成变例…</p>
      ) : (
        <>
          <div className="score-nav">
            <button type="button" disabled={atStart} onClick={onPrev}>
              上一步
            </button>
            <span className="score-progress">
              {plyIndex}/{moves.length}
            </span>
            <button type="button" disabled={atEnd} onClick={onNext}>
              下一步
            </button>
          </div>

          <ol className="score-list">
            <li>
              <button
                type="button"
                className={plyIndex === 0 ? 'active' : ''}
                onClick={() => onGoto(0)}
              >
                <span className="score-num">0.</span>
                <span>开局</span>
              </button>
            </li>
            {notations.map((text, i) => {
              const ply = i + 1
              return (
                <li key={ply}>
                  <button
                    type="button"
                    className={plyIndex === ply ? 'active' : ''}
                    onClick={() => onGoto(ply)}
                  >
                    <span className="score-num">{ply}.</span>
                    <span>{text}</span>
                  </button>
                </li>
              )
            })}
          </ol>
        </>
      )}
    </aside>
  )
}
