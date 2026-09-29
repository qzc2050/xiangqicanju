/**
 * 皮卡鱼 Web Worker：本地 UCI，强力防守。
 * 资源：/wasm/pikafish.{js,wasm} + /wasm/data/pikafish.data
 */
/* eslint-disable no-undef */
importScripts('./pikafish.js')

/** @type {any} */
let engine = null
/** @type {((result: { move: string | null, pv: string[] }) => void) | null} */
let pendingResolve = null
/** @type {string[]} */
let lastPv = []
let ready = false

function post(msg) {
  self.postMessage(msg)
}

function waitReadyok(timeoutMs) {
  return new Promise((resolve, reject) => {
    const prev = engine.read_stdout
    const timer = setTimeout(() => {
      engine.read_stdout = prev
      reject(new Error('engine isready timeout'))
    }, timeoutMs)
    engine.read_stdout = (line) => {
      prev(line)
      if (String(line).includes('readyok')) {
        clearTimeout(timer)
        engine.read_stdout = prev
        resolve()
      }
    }
    engine.send_command('isready')
  })
}

async function initEngine() {
  if (ready) return
  engine = await Pikafish({
    locateFile(file) {
      if (file.endsWith('.data')) return `./data/${file}`
      return `./${file}`
    },
    read_stdout(line) {
      const text = String(line)
      const pvMatch = text.match(/\spv\s+(.+?)\s*$/)
      if (pvMatch && text.includes('info ')) {
        lastPv = pvMatch[1]
          .trim()
          .split(/\s+/)
          .filter((m) => /^[a-i][0-9][a-i][0-9]$/.test(m))
      }
      const m = text.match(/bestmove\s+(\S+)/)
      if (m && pendingResolve) {
        const resolve = pendingResolve
        pendingResolve = null
        const best = m[1] === '(none)' ? null : m[1]
        let pv = lastPv.slice()
        if (best && (pv.length === 0 || pv[0] !== best)) {
          pv = [best, ...pv.filter((x) => x !== best)]
        }
        resolve({ move: best, pv })
      }
    },
  })
  engine.send_command('uci')
  engine.send_command('setoption name Threads value 1')
  engine.send_command('setoption name Hash value 64')
  await waitReadyok(15000)
  engine.send_command('ucinewgame')
  await waitReadyok(10000)
  ready = true
}

/**
 * @param {string} fen
 * @param {number} timeMs
 */
function go(fen, timeMs) {
  return new Promise((resolve) => {
    if (pendingResolve) {
      pendingResolve({ move: null, pv: [] })
      pendingResolve = null
    }
    lastPv = []
    pendingResolve = resolve
    const fullFen = fen.includes(' - ') ? fen : `${fen} - - 0 1`
    engine.send_command(`position fen ${fullFen}`)
    engine.send_command(`go movetime ${Math.max(200, Math.floor(timeMs))}`)
    setTimeout(() => {
      if (pendingResolve === resolve) {
        try {
          engine.send_command('stop')
        } catch {
          /* ignore */
        }
        setTimeout(() => {
          if (pendingResolve === resolve) {
            pendingResolve = null
            resolve({ move: null, pv: lastPv.slice() })
          }
        }, 1500)
      }
    }, timeMs + 4000)
  })
}

self.onmessage = async (ev) => {
  const { id, type, fen, timeMs } = ev.data || {}
  try {
    if (type === 'init') {
      await initEngine()
      post({ id, ok: true, type: 'ready' })
      return
    }
    if (type === 'go' || type === 'goPv') {
      if (!ready) await initEngine()
      const result = await go(fen, timeMs ?? 1200)
      post({
        id,
        ok: true,
        type: 'bestmove',
        move: result.move,
        pv: result.pv,
      })
      return
    }
    post({ id, ok: false, error: `unknown type ${type}` })
  } catch (e) {
    post({
      id,
      ok: false,
      error: e instanceof Error ? e.message : String(e),
    })
  }
}
