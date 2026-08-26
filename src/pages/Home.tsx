import { Link } from 'react-router-dom'
import { CATEGORIES, PUZZLES, puzzlesByCategory } from '../puzzles/catalog'
import { clearedCount, isCleared } from '../storage/progress'

const DIFF = ['', '入门', '进阶', '提高', '较难', '高难']

export function Home() {
  const totalCleared = clearedCount(PUZZLES.map((p) => p.id))

  return (
    <div className="page home">
      <header className="hero">
        <p className="brand">例胜残局</p>
        <h1>中国象棋实用残局</h1>
        <p className="sub">
          按陈松顺增订本目录 · 皮卡鱼防守 · 已练 {totalCleared}/{PUZZLES.length}
        </p>
      </header>

      {CATEGORIES.map((cat) => {
        const list = puzzlesByCategory(cat)
        const done = clearedCount(list.map((p) => p.id))
        return (
          <section key={cat} className="category">
            <div className="cat-head">
              <h2>{cat}</h2>
              <span>
                {done}/{list.length}
              </span>
            </div>
            <ul className="puzzle-list">
              {list.map((p) => (
                <li key={p.id}>
                  <Link to={`/play/${p.id}`} className="puzzle-card">
                    <div>
                      <strong>
                        {p.bookNo ? `（${p.bookNo}）` : ''}
                        {p.title}
                      </strong>
                      <span className="diff">
                        {DIFF[p.difficulty]}
                        {p.goal === 'draw' ? ' · 和' : ' · 胜'}
                      </span>
                    </div>
                    <span className={isCleared(p.id) ? 'badge done' : 'badge'}>
                      {isCleared(p.id) ? (p.goal === 'draw' ? '已练' : '已通关') : '开练'}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )
      })}
    </div>
  )
}
