import { normalizeLifeRpgProfile } from '../data/lifeRpgOptions.js'

const KEYS = {
  profile: 'life_rpg_profile',
  lastResult: 'life_rpg_last_result',
  attributes: 'life_rpg_attributes',
  dailyForm: 'life_rpg_daily_form',
  completedTasks: 'life_rpg_completed_tasks',
}

export const DEFAULT_ATTRIBUTES = {
  energy: 0,
  explore: 0,
  express: 0,
  discipline: 0,
  social: 0,
  growth: 0,
}

function safeParse(raw, fallback) {
  if (!raw) return fallback
  try {
    return JSON.parse(raw)
  } catch {
    return fallback
  }
}

/** 是否已创建完整人生路线 */
export function hasLifeRpgProfile() {
  const p = loadProfile()
  return !!(p && (p.routeTitle || p.route_title))
}

export function loadProfile() {
  const raw = safeParse(localStorage.getItem(KEYS.profile), null)
  return normalizeLifeRpgProfile(raw)
}

export function saveLifeRpgProfile(profile) {
  if (!profile) return
  localStorage.setItem(KEYS.profile, JSON.stringify(normalizeLifeRpgProfile(profile)))
}

export function loadAttributes() {
  const data = safeParse(localStorage.getItem(KEYS.attributes), null)
  if (!data || typeof data !== 'object') return { ...DEFAULT_ATTRIBUTES }
  return { ...DEFAULT_ATTRIBUTES, ...data }
}

export function saveAttributes(attrs) {
  localStorage.setItem(KEYS.attributes, JSON.stringify({ ...DEFAULT_ATTRIBUTES, ...attrs }))
}

function applyDelta(attrs, reward, sign) {
  const next = { ...attrs }
  for (const key of Object.keys(DEFAULT_ATTRIBUTES)) {
    const delta = (Number(reward[key]) || 0) * sign
    if (delta) next[key] = Math.max(0, (next[key] || 0) + delta)
  }
  return next
}

export function applyReward(reward) {
  const current = loadAttributes()
  const next = applyDelta(current, reward, 1)
  saveAttributes(next)
  return next
}

export function subtractReward(reward) {
  const current = loadAttributes()
  const next = applyDelta(current, reward, -1)
  saveAttributes(next)
  return next
}

export function loadCompletedTasks() {
  const data = safeParse(localStorage.getItem(KEYS.completedTasks), null)
  if (!data || typeof data !== 'object') {
    return { resultId: '', completedTaskIds: [] }
  }
  return {
    resultId: data.resultId || data.result_id || '',
    completedTaskIds: Array.isArray(data.completedTaskIds)
      ? [...data.completedTaskIds]
      : [],
  }
}

export function saveCompletedTasks(resultId, completedTaskIds) {
  localStorage.setItem(
    KEYS.completedTasks,
    JSON.stringify({
      resultId: String(resultId),
      completedTaskIds: [...completedTaskIds],
    }),
  )
}

export function loadLastResult() {
  return safeParse(localStorage.getItem(KEYS.lastResult), null)
}

export function saveLastResult(result) {
  if (!result) return
  localStorage.setItem(KEYS.lastResult, JSON.stringify(result))
}

export function loadDailyForm() {
  return safeParse(localStorage.getItem(KEYS.dailyForm), null)
}

export function saveDailyForm(form) {
  if (!form) return
  localStorage.setItem(KEYS.dailyForm, JSON.stringify(form))
}

const LEGACY_STORAGE_KEYS = ['life_rpg_selected_path']

/** 清理已废弃的 localStorage 项 */
export function purgeLegacyLifeRpgStorage() {
  LEGACY_STORAGE_KEYS.forEach((key) => localStorage.removeItem(key))
}

/** 重置角色与副本数据（保留可重新创建） */
export function resetLifeRpgAll() {
  Object.values(KEYS).forEach((key) => localStorage.removeItem(key))
  purgeLegacyLifeRpgStorage()
}
