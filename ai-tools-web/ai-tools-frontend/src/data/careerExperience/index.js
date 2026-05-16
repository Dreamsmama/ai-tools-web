import { developerDayConfig } from './developerDay'
import { developerIncidentNightConfig } from './developerIncidentNight'
import { hrDayConfig } from './hrDay'
import { lawStudentDayConfig } from './lawStudentDay'
import { financeStudentDayConfig } from './financeStudentDay'
import { medicineStudentDayConfig } from './medicineStudentDay'
import { lawyerDayConfig } from './lawyerDay'
import { doctorDayConfig } from './doctorDay'
import { financePractitionerDayConfig } from './financePractitionerDay'

const REGISTRY = {
  'developer-ep01': developerDayConfig,
  'developer-ep02': developerIncidentNightConfig,
  'hr-ep01': hrDayConfig,
  /** 职业体验馆 · 职场一日 */
  developer: developerDayConfig,
  hr: hrDayConfig,
  lawyer: lawyerDayConfig,
  doctor: doctorDayConfig,
  'finance-practitioner': financePractitionerDayConfig,
  /** 高考生专区 · 学这个专业以后（与职场版剧情不同） */
  'major-law': lawStudentDayConfig,
  'major-finance': financeStudentDayConfig,
  'major-medicine': medicineStudentDayConfig,
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

/** AI 职业体验馆 · 职场人一日（与高考「学专业以后」分开） */
export function listCareerExperienceHubItems() {
  return [
    {
      id: 'developer',
      title: '程序员的一天',
      subtitle: '可体验',
      available: true,
      to: '/career-experience/developer',
    },
    {
      id: 'hr',
      title: 'HR 的一天',
      subtitle: '可体验',
      available: true,
      to: '/career-experience/hr',
    },
    {
      id: 'lawyer',
      title: '律师的一天',
      subtitle: '可体验',
      available: true,
      to: '/career-experience/lawyer',
    },
    {
      id: 'doctor',
      title: '医生的一天',
      subtitle: '可体验',
      available: true,
      to: '/career-experience/doctor',
    },
    {
      id: 'finance-practitioner',
      title: '金融从业者的一天',
      subtitle: '可体验',
      available: true,
      to: '/career-experience/finance-practitioner',
    },
    {
      id: 'pm',
      title: '产品经理的一天',
      subtitle: '开发中',
      available: false,
      to: '',
    },
  ]
}
