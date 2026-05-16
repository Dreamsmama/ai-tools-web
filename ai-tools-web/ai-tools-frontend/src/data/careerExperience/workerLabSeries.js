/** 打工人格实验室 · 连续剧系列列表（仅展示与路由，不含玩法逻辑） */
export const WORKER_LAB_SERIES = [
  {
    id: 'developer',
    title: '程序员系列',
    tagline: '从白天救火到深夜事故，一集比一集更接近真实工位。',
    posterEmoji: '💻',
    posterClass: 'developer',
    episodes: [
      {
        id: 'ep01',
        code: 'EP01',
        title: '程序员的一天',
        tagline: '今天到底是先修 bug，还是先回产品经理？',
        status: 'open',
        experienceKey: 'developer-ep01',
        to: '/worker-lab/developer/ep01',
        posterEmoji: '☀️',
      },
      {
        id: 'ep02',
        code: 'EP02',
        title: '线上事故的一夜',
        tagline: '本来想下班，结果客户群突然炸了。',
        status: 'open',
        experienceKey: 'developer-ep02',
        to: '/worker-lab/developer/ep02',
        posterEmoji: '🌙',
      },
      {
        id: 'ep03',
        code: 'EP03',
        title: '年终绩效沟通',
        tagline: '你以为是复盘，其实是重新定义责任。',
        status: 'coming',
        experienceKey: 'developer-ep03',
        to: '',
        posterEmoji: '📊',
      },
      {
        id: 'ep04',
        code: 'EP04',
        title: '周末突然上线',
        tagline: '周五晚上那句「很快就好」，一般都不太可信。',
        status: 'coming',
        experienceKey: 'developer-ep04',
        to: '',
        posterEmoji: '🚀',
      },
    ],
  },
  {
    id: 'hr',
    title: 'HR 系列',
    tagline: '所有人都在找你解决问题，但没人问你累不累。',
    posterEmoji: '📋',
    posterClass: 'hr',
    episodes: [
      {
        id: 'ep01',
        code: 'EP01',
        title: 'HR 的一天',
        tagline: '所有人都在找你解决问题，但没人问你累不累。',
        status: 'open',
        experienceKey: 'hr-ep01',
        to: '/worker-lab/hr/ep01',
        posterEmoji: '📋',
      },
    ],
  },
]

/** @returns {typeof WORKER_LAB_SERIES[number] | undefined} */
export function getWorkerLabSeries(seriesId) {
  return WORKER_LAB_SERIES.find((s) => s.id === seriesId)
}

/** 首页预览：每系列取第一集已开放项 */
export function listWorkerLabHomePreview() {
  return WORKER_LAB_SERIES.map((series) => {
    const featured =
      series.episodes.find((ep) => ep.status === 'open') ?? series.episodes[0]
    return { series, featured }
  })
}
