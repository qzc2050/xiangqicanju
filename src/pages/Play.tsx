import { Link, useNavigate, useParams } from 'react-router-dom'
import { Board } from '../components/Board'
import { GameBar } from '../components/GameBar'
import { ScoreSheet } from '../components/ScoreSheet'
import { usePuzzleGame } from '../hooks/usePuzzleGame'
import { getPuzzle, nextPuzzleId } from '../puzzles/catalog'

export function Play() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const puzzle = getPuzzle(id)

  if (!puzzle) {
    return (
      <div className="page">
        <p>题目不存在</p>
        <Link to="/">返回</Link>
      </div>
    )
  }

  return (
    <PlayInner
      key={puzzle.id}
      puzzle={puzzle}
      onNext={() => {
        const n = nextPuzzleId(puzzle.id)
        if (n) navigate(`/play/${n}`)
      }}
    />
  )
}

function PlayInner({
  puzzle,
  onNext,
}: {
  puzzle: NonNullable<ReturnType<typeof getPuzzle>>
  onNext: () => void
}) {
  const game = usePuzzleGame(puzzle)
  const hasNext = Boolean(nextPuzzleId(puzzle.id))
  const flip = game.playerSide === 'black'

  return (
    <div className="page play">
      <header className="play-head">
        <Link to="/" className="back">
          ← 题库
        </Link>
        <div>
          <h1>
            {puzzle.bookNo ? `（${puzzle.bookNo}）` : ''}
            {puzzle.title}
          </h1>
          <p className="tip">
            {puzzle.goal === 'draw' ? '和局 · ' : '例胜 · '}
            {puzzle.tip ?? puzzle.category}
          </p>
        </div>
      </header>

      <div className={`play-main ${game.solutionMode ? 'with-score' : ''}`}>
        <Board
          pos={game.pos}
          selected={game.selected}
          legalTargets={game.legalTargets}
          hintMove={game.hintMove}
          lastMove={game.lastMove}
          onSquareClick={game.onSquareClick}
          flip={flip}
        />

        {game.solutionMode && (
          <ScoreSheet
            startFen={puzzle.fen}
            moves={game.solutionMoves}
            plyIndex={game.solutionPly}
            loading={game.solutionLoading}
            onGoto={game.solutionGoto}
            onPrev={game.solutionPrev}
            onNext={game.solutionNext}
            onExit={game.exitSolution}
          />
        )}
      </div>

      <GameBar
        message={game.message}
        aiThinking={game.aiThinking || game.solutionLoading}
        status={game.status}
        engineLabel={game.engineLabel}
        playerSide={game.playerSide}
        onSideChange={game.setPlayerSide}
        canUndo={game.canUndo}
        onUndo={game.undo}
        onHint={() => void game.showHint()}
        onSolution={() => void game.openSolution()}
        onReset={game.reset}
        onNext={onNext}
        hasNext={hasNext}
        solutionMode={game.solutionMode}
        showMarkPracticed={puzzle.goal === 'draw'}
        onMarkPracticed={game.markPracticed}
      />
    </div>
  )
}
