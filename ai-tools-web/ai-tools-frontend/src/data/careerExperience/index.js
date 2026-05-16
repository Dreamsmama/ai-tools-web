import { developerDayConfig } from './developerDay'
import { developerIncidentNightConfig } from './developerIncidentNight'
import { hrDayConfig } from './hrDay'

const REGISTRY = {
  'developer-ep01': developerDayConfig,
  'developer-ep02': developerIncidentNightConfig,
  'hr-ep01': hrDayConfig,
  /** 职业体验馆沿用旧 id */
  developer: developerDayConfig,
  hr: hrDayConfig,
}

const STAT_KEYS = ['stress', 'reputation', 'growth', 'mood']

export function getCareerExperienceConfig(id) {
  return REGISTRY[id] ?? null
}

/** @param {string} seriesId @param {string} episodeId */
export function getWorkerLabExperienceKey(seriesId, episodeId) {
  return `${seriesId}-${episodeId}`
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

/** @deprecated 使用 workerLabSeries.js */
export function listWorkerLabEpisodes() {
  return [
    {
      id: 'developer-ep01',
      episode: 1,
      episodeLabel: 'EP01',
      title: developerDayConfig.title,
      tagline: developerDayConfig.subtitle,
      posterEmoji: '💻',
      available: true,
      to: '/worker-lab/developer/ep01',
    },
    {
      id: 'hr-ep01',
      episode: 1,
      episodeLabel: 'EP01',
      title: hrDayConfig.title,
      tagline: hrDayConfig.subtitle,
      posterEmoji: '📋',
      available: true,
      to: '/worker-lab/hr/ep01',
    },
  ]
}

/** AI 职业体验馆 · 列表（与原体验馆一致） */
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
      subtitle: '内测',
      available: true,
      to: '/career-experience/hr',
    },
  ]
}
