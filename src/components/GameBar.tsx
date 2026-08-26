type Props = {
  message: string
  aiThinking: boolean
  status: string
  engineLabel?: string
  playerSide: 'red' | 'black'
  onSideChange: (side: 'red' | 'black') => void
  canUndo: boolean
  onUndo: () => void
  onHint: () => void
  onSolution: () => void
  onReset: () => void
  onNext: () => void
  hasNext: boolean
  solutionMode?: boolean
  showMarkPracticed?: boolean
  onMarkPracticed?: () => void
}

export function GameBar({
  message,
  aiThinking,
  status,
  engineLabel,
  playerSide,
  onSideChange,
  canUndo,
  onUndo,
  onHint,
  onSolution,
  onReset,
  onNext,
  hasNext,
  solutionMode,
  showMarkPracticed,
  onMarkPracticed,
}: Props) {
  return (
    <div className="game-bar">
      {engineLabel && <p className="engine-tag">对手：{engineLabel}</p>}
      {!solutionMode && (
        <div className="side-switch" role="group" aria-label="选择执子方">
          <button
            type="button"
            className={playerSide === 'red' ? 'active red' : ''}
            disabled={aiThinking}
            onClick={() => onSideChange('red')}
          >
            执红
          </button>
          <button
            type="button"
            className={playerSide === 'black' ? 'active black' : ''}
            disabled={aiThinking}
            onClick={() => onSideChange('black')}
          >
            执黑
          </button>
        </div>
      )}
      <p className={`status-msg ${status}`}>{aiThinking ? '引擎思考中…' : message}</p>
      <div className="actions">
        {!solutionMode && (
          <button type="button" disabled={!canUndo} onClick={onUndo}>
            悔棋
          </button>
        )}
        {!solutionMode && (
          <button type="button" disabled={aiThinking || status !== 'playing'} onClick={onHint}>
            提示
          </button>
        )}
        <button type="button" disabled={aiThinking} onClick={onSolution}>
          {solutionMode ? '刷新棋谱' : '正解'}
        </button>
        <button type="button" onClick={onReset}>
          重来
        </button>
        {showMarkPracticed && onMarkPracticed && !solutionMode && (
          <button type="button" onClick={onMarkPracticed}>
            记为已练
          </button>
        )}
        {hasNext && (
          <button type="button" className="primary" onClick={onNext}>
            下一题
          </button>
        )}
      </div>
    </div>
  )
}
