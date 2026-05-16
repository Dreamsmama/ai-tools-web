/**
 * 高考热点内容卡片（静态 Mock，预留 slug 便于后续接 AI 生成）
 * @typedef {{ id: string, slug: string, title: string, teaser: string, tag: string, tone: 'alert'|'insight'|'guide' }} GaokaoHotTopic
 */

/** @type {GaokaoHotTopic[]} */
export const gaokaoHotTopics = [
  {
    id: 'ai-risk-majors',
    slug: 'ai-risk-majors',
    title: 'AI 时代最危险的专业',
    teaser: '哪些方向容易被自动化替代？选专业前先看风险，而不是只看热度。',
    tag: '风险',
    tone: 'alert',
  },
  {
    id: 'family-caution',
    slug: 'family-caution',
    title: '普通家庭慎选专业',
    teaser: '投入产出、地域与行业周期——不是泼冷水，而是帮你少踩结构性坑。',
    tag: '避坑',
    tone: 'insight',
  },
  {
    id: 'liberal-arts-path',
    slug: 'liberal-arts-path',
    title: '文科生适合什么方向',
    teaser: '表达、洞察与组织力可以落在哪些专业？别被「文科没出路」带偏。',
    tag: '文科',
    tone: 'guide',
  },
  {
    id: 'future-hot-majors',
    slug: 'future-hot-majors',
    title: '哪些专业未来更吃香',
    teaser: '结合 AI 协作、产业升级与人口结构，看 5–10 年的方向差。',
    tag: '趋势',
    tone: 'insight',
  },
]

export function getHotTopicBySlug(slug) {
  return gaokaoHotTopics.find((t) => t.slug === slug) ?? null
}
