import {
  DIRECTION_TEMPLATES,
  getDirectionTemplate,
  getResolvedLifeStates,
} from '../data/lifeRpgOptions.js'

const TEMPLATE_PREVIEW = {
  growth: {
    direction: '探索成长型',
    personality: '以能力与长期积累为主线的成长路线',
    world: '你正在沿成长路线稳步推进。',
    theme: 'growth',
  },
  recovery: {
    direction: '生活恢复型',
    personality: '以节奏与感受重建为主线的恢复路线',
    world: '你正在慢慢找回生活的真实感。',
    theme: 'recovery',
  },
  interest: {
    direction: '兴趣滋养型',
    personality: '以热爱与好奇心为主线的兴趣路线',
    world: '你正在重新拾起自己的兴趣节奏。',
    theme: 'explore',
  },
  journal: {
    direction: '人生记录型',
    personality: '以记录与节奏为主线的长期推进路线',
    world: '你正在建立属于自己的生活节奏。',
    theme: 'explore',
  },
}

function uniqueTags(list, max = 5) {
  const out = []
  for (const t of list) {
    const s = (t || '').trim()
    if (!s || out.includes(s)) continue
    out.push(s)
    if (out.length >= max) break
  }
  return out
}

function hasInput(form) {
  return !!(
    getResolvedLifeStates(form).length ||
    form.direction_template ||
    (form.life_keywords || []).length ||
    (form.custom_notes || '').trim()
  )
}

function corpusOf(form) {
  const states = getResolvedLifeStates(form).join(' ')
  const kw = (form.life_keywords || []).join(' ')
  const notes = (form.custom_notes || '').trim()
  const occ = (form.occupation || '').trim()
  return `${states} ${kw} ${notes} ${occ}`.toLowerCase()
}

/**
 * @param {Record<string, unknown>} form
 */
export function buildCharacterPreview(form) {
  const forming = !hasInput(form)
  const states = getResolvedLifeStates(form)
  const template = getDirectionTemplate(form.direction_template)
  const keywords = [...(form.life_keywords || [])]
  const corpus = corpusOf(form)

  let lifeDirection = '待你选择人生状态与方向'
  let personalityRoute = 'AI 将根据你的关键词，勾勒人格路线轮廓'
  let tendencies = [...keywords]
  let worldLine = 'AI 正在根据你的选择，勾勒属于你的人生路线。'

  if (template && TEMPLATE_PREVIEW[template.id]) {
    const p = TEMPLATE_PREVIEW[template.id]
    lifeDirection = p.direction
    personalityRoute = p.personality
    worldLine = p.world
  }

  if (/ai|开发|技术|程序/.test(corpus) && (keywords.length || states.includes('更自律'))) {
    lifeDirection = '技术成长探索型'
    personalityRoute = '长期学习 + 自我推进的人格路线'
    tendencies = uniqueTags([...keywords, '长期成长', '深度学习'], 5)
  } else if (
    /刷手机|生活感|恢复|累|规律/.test(corpus) ||
    template?.id === 'recovery' ||
    states.includes('更有生活感')
  ) {
    lifeDirection = '生活恢复探索型'
    personalityRoute = '恢复节奏 + 精神减压的人格路线'
    tendencies = uniqueTags([...keywords, '恢复现实感', '建立生活节奏'], 5)
  } else if (states.length) {
    lifeDirection = `${states.slice(0, 2).join(' · ')}导向`
    personalityRoute = `围绕「${states[0]}」延展的长期人格路线`
    tendencies = uniqueTags([...keywords, ...states.slice(0, 2)], 5)
  }

  if (!tendencies.length && forming) {
    tendencies = ['等待你的关键词']
  }

  return {
    title: '你的人生角色正在形成',
    subtitle: '根据你的状态与方向，AI 会帮你整理一条长期路线。',
    lifeDirection,
    tendencies,
    personalityRoute,
    worldLine,
    isForming: forming,
  }
}
