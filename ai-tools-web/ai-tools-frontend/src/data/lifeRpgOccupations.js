/**
 * 人生副本 · 职业搜索数据源（复用职业观察库 + 常用别名）
 */
import { listCareersForLibrary } from './careersCatalog.js'

const EXTRA_OCCUPATIONS = [
  { name: '程序员', keywords: ['程序员', '开发', 'engineer', '码农'] },
  { name: '后端开发', keywords: ['后端', 'backend', 'java', 'go'] },
  { name: 'Java开发', keywords: ['java'] },
  { name: 'Go开发', keywords: ['go', 'golang'] },
  { name: 'Python开发', keywords: ['python'] },
  { name: '产品经理', keywords: ['产品', 'pm'] },
  { name: 'UI设计', keywords: ['ui', 'ux', '界面'] },
  { name: '视觉设计', keywords: ['视觉', '平面'] },
  { name: '运营', keywords: ['运营'] },
  { name: '市场', keywords: ['市场', '营销'] },
  { name: '护士', keywords: ['护士', '护理'] },
  { name: '药师', keywords: ['药师'] },
  { name: '心理咨询师', keywords: ['心理', '咨询'] },
  { name: '公务员', keywords: ['公务员', '体制内'] },
  { name: '研究生', keywords: ['研究生', '硕士', '博士'] },
  { name: '本科生', keywords: ['本科', '大学'] },
  { name: '跨境电商', keywords: ['跨境', '电商'] },
  { name: '游戏策划', keywords: ['游戏', '策划'] },
  { name: '插画师', keywords: ['插画'] },
  { name: '摄影师', keywords: ['摄影'] },
]

function uniqueByName(items) {
  const seen = new Set()
  const out = []
  for (const item of items) {
    const key = item.name.trim()
    if (!key || seen.has(key)) continue
    seen.add(key)
    out.push({
      name: key,
      keywords: [...new Set([key, ...(item.keywords || [])])],
    })
  }
  return out
}

let _cache = null

export function getOccupationCatalog() {
  if (_cache) return _cache
  const fromLib = listCareersForLibrary().map((c) => ({
    name: c.name,
    keywords: [c.name, c.libraryTag, c.id].filter(Boolean),
  }))
  _cache = uniqueByName([...fromLib, ...EXTRA_OCCUPATIONS])
  return _cache
}

/**
 * @param {string} query
 * @param {number} [limit]
 */
export function searchOccupations(query, limit = 8) {
  const q = (query || '').trim().toLowerCase()
  if (!q) return []
  const catalog = getOccupationCatalog()
  const scored = []
  for (const item of catalog) {
    const nameLower = item.name.toLowerCase()
    let score = 0
    if (nameLower === q) score = 100
    else if (nameLower.startsWith(q)) score = 80
    else if (nameLower.includes(q)) score = 60
    else if (item.keywords.some((k) => String(k).toLowerCase().includes(q))) score = 40
    if (score > 0) scored.push({ ...item, score })
  }
  scored.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name, 'zh'))
  return scored.slice(0, limit).map(({ name }) => ({ name }))
}
