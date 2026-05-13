import { developerDayConfig } from './developerDay'

const REGISTRY = {
  developer: developerDayConfig,
}

const STAT_KEYS = ['stress', 'reputation', 'growth', 'mood']

export function getCareerExperienceConfig(id) {
  return REGISTRY[id] ?? null
}

/** @param {Record<string, number>} base @param {Record<string, number>} delta */
export function applyStatEffects(base, delta) {
  const next = { ...base }
  for (const k of STAT_KEYS) {
    const d = delta[k]
    if (typeof d === 'number' && !Number.isNaN(d)) {
      next[k] = Math.max(0, Math.min(100, (next[k] ?? 0) + d))
    }
  }
  return next
}

/** @param {Record<string, number>} stats @param {Array<{ match: (s: Record<string, number>) => boolean }>} endings */
export function resolveExperienceEnding(stats, endings) {
  for (const rule of endings) {
    if (rule.match(stats)) return rule
  }
  return endings[endings.length - 1]
}

/** 体验馆首页列表（含未开放占位） */
export function listCareerExperienceHubItems() {
  return [
    {
      id: 'developer',
      title: '程序员的一天',
      subtitle: '内测',
      available: true,
      to: '/career-experience/developer',
    },
    {
      id: 'pm',
      title: '产品经理的一天',
      subtitle: '开发中',
      available: false,
      to: '',
    },
    {
      id: 'hr',
      title: 'HR 的一天',
      subtitle: '开发中',
      available: false,
      to: '',
    },
  ]
}
