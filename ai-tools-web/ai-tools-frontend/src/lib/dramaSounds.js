const MUTE_KEY = 'worker_lab_sound_muted'

/** @type {AudioContext | null} */
let ctx = null
let unlocked = false

export function isSoundMuted() {
  try {
    return localStorage.getItem(MUTE_KEY) === '1'
  } catch {
    return false
  }
}

export function setSoundMuted(muted) {
  try {
    localStorage.setItem(MUTE_KEY, muted ? '1' : '0')
  } catch {
    /* ignore */
  }
}

/** 需在用户手势后调用（如点击「开始追剧」） */
export function unlockDramaAudio() {
  if (typeof window === 'undefined') return
  if (!ctx) {
    const Ctx = window.AudioContext || window.webkitAudioContext
    if (!Ctx) return
    ctx = new Ctx()
  }
  if (ctx.state === 'suspended') {
    ctx.resume().catch(() => {})
  }
  unlocked = true
}

/**
 * @param {'group' | 'private' | 'life' | 'call' | 'alert'} tone
 * @param {boolean} muted
 */
export function playDramaSound(tone, muted) {
  if (muted || !unlocked || !ctx) return

  const t = ctx.currentTime
  const master = ctx.createGain()
  master.gain.value = 0.09
  master.connect(ctx.destination)

  const playBeep = (freq, start, dur, type = 'sine', vol = 1) => {
    const osc = ctx.createOscillator()
    const g = ctx.createGain()
    osc.type = type
    osc.frequency.value = freq
    g.gain.setValueAtTime(0, t + start)
    g.gain.linearRampToValueAtTime(vol, t + start + 0.01)
    g.gain.exponentialRampToValueAtTime(0.001, t + start + dur)
    osc.connect(g)
    g.connect(master)
    osc.start(t + start)
    osc.stop(t + start + dur + 0.02)
  }

  switch (tone) {
    case 'private':
      playBeep(880, 0, 0.06, 'sine', 0.7)
      break
    case 'life':
      playBeep(523, 0, 0.1, 'triangle', 0.55)
      playBeep(659, 0.09, 0.12, 'triangle', 0.45)
      break
    case 'call':
      playBeep(440, 0, 0.14, 'square', 0.35)
      playBeep(440, 0.18, 0.14, 'square', 0.35)
      break
    case 'alert':
      playBeep(320, 0, 0.08, 'sawtooth', 0.4)
      playBeep(280, 0.1, 0.1, 'sawtooth', 0.35)
      break
    case 'group':
    default:
      playBeep(740, 0, 0.05, 'sine', 0.65)
      playBeep(988, 0.07, 0.05, 'sine', 0.5)
      break
  }
}
