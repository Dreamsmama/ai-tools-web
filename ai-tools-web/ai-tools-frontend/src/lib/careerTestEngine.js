import { careerTestQuestions, DIMENSION_ORDER, dimensionLabels } from '../data/careerTestQuestions'
import { getCareerById } from '../data/careersCatalog'

/** @typedef {import('../data/careerTestQuestions').CareerDimension} CareerDimension */

/** 各维度推荐职业 id（与职业库 id 一致，每维 5 个） */
export const DIMENSION_CAREER_IDS = {
  technical: ['java-dev', 'frontend-dev', 'qa-engineer', 'ai-app-dev', 'devops-engineer'],
  communication: ['hr', 'sales', 'customer-success', 'headhunter', 'project-manager'],
  analysis: ['data-analyst', 'product-analyst', 'finance', 'project-manager', 'product-manager'],
  creative: ['new-media-operations', 'ui-designer', 'content-planner', 'e-commerce-operations', 'teacher'],
  organization: ['product-manager', 'project-manager', 'e-commerce-operations', 'admin', 'new-media-operations'],
}

function dedupeKeepOrder(ids) {
  const seen = new Set()
  const out = []
  for (const id of ids) {
    if (seen.has(id)) continue
    seen.add(id)
    out.push(id)
  }
  return out
}

/** @param {string[]} ids @param {CareerDimension} primaryKey */
function ensureFiveCareerIds(ids, primaryKey) {
  const out = dedupeKeepOrder(ids)
  const pool = DIMENSION_CAREER_IDS[primaryKey]
  for (let i = 0; out.length < 5 && i < pool.length; i++) {
    const id = pool[i]
    if (!out.includes(id)) out.push(id)
  }
  return out.slice(0, 5)
}

/**
 * @param {(number|null)[]} answers 每题所选 option 索引
 * @returns {Record<CareerDimension, number>}
 */
export function computeDimensionScores(answers) {
  /** @type {Record<CareerDimension, number>} */
  const totals = {
    technical: 0,
    communication: 0,
    analysis: 0,
    creative: 0,
    organization: 0,
  }
  answers.forEach((optIdx, qIdx) => {
    if (optIdx === null || optIdx === undefined) return
    const q = careerTestQuestions[qIdx]
    if (!q?.options?.[optIdx]?.scores) return
    const s = q.options[optIdx].scores
    DIMENSION_ORDER.forEach((d) => {
      totals[d] += s[d] ?? 0
    })
  })
  return totals
}

/**
 * @param {Record<CareerDimension, number>} scores
 */
export function rankDimensions(scores) {
  const sorted = DIMENSION_ORDER.map((key) => ({ key, score: scores[key] ?? 0 })).sort(
    (a, b) => b.score - a.score,
  )
  return {
    primary: sorted[0].key,
    secondary: sorted[1].key,
    sorted,
  }
}

function dimensionsAreClose(top, second) {
  if (top <= 0) return false
  return top - second <= Math.max(3, top * 0.12)
}

/**
 * @param {Record<CareerDimension, number>} scores
 * @param {{ sorted: { key: CareerDimension, score: number }[] }} ranked
 */
export function pickRecommendedCareerIds(scores, ranked) {
  const top = ranked.sorted[0]
  const second = ranked.sorted[1]
  const close = dimensionsAreClose(top.score, second.score)
  const poolPrimary = [...DIMENSION_CAREER_IDS[top.key]]
  if (!close) return ensureFiveCareerIds(poolPrimary, top.key)

  const poolSecondary = [...DIMENSION_CAREER_IDS[second.key]]
  const merged = [...poolPrimary, ...poolSecondary]
  return ensureFiveCareerIds(merged, top.key)
}

const workStyleHints = {
  technical:
    '你更可能喜欢「目标清晰、可验证产出、能深度专注」的工作方式；把复杂问题拆成工程步骤会让你有掌控感。',
  communication:
    '你更可能喜欢「高频对齐、多方斡旋、用语言与共识推进」的方式；面对面或即时沟通往往比纯文档更能激发你。',
  analysis:
    '你更可能喜欢「先证据后结论」的节奏：查数、建模、写备忘录，用逻辑减少不确定性。',
  creative:
    '你更可能喜欢「有表达空间」的方式：叙事、审美、版本迭代，让想法被看见比单纯执行清单更吸引你。',
  organization:
    '你更可能喜欢「排期、拆解、推进里程碑」的方式：把模糊变成路径，并对结果负责。',
}

const unsuitableHints = {
  technical: '高度依赖口头传递、缺乏文档与工程规范、长期无法沉淀工具链的环境。',
  communication: '极度封闭、几乎零人际协作、长期不需要影响他人的岗位。',
  analysis: '只追求速度、不允许验证数据、或「结论先行」压制质疑的文化。',
  creative: '只接受固定模板、零创作余地、反馈模糊且反复无常的环境。',
  organization: '责任边界混乱、优先级每日推翻、无人对决策负责的组织状态。',
}

/**
 * @param {(number|null)[]} answers
 */
export function buildTestResult(answers) {
  const scores = computeDimensionScores(answers)
  const ranked = rankDimensions(scores)
  const { primary, secondary } = ranked
  const close = dimensionsAreClose(ranked.sorted[0].score, ranked.sorted[1].score)

  const ids = pickRecommendedCareerIds(scores, ranked)
  const recommendations = ids.map((id) => {
    const c = getCareerById(id)
    const name = c?.name ?? id
    const recommendReason = close
      ? `你的「${dimensionLabels[primary]}」与「${dimensionLabels[secondary]}」得分接近；${name}常需要其中一种或多种能力组合。`
      : `你的「${dimensionLabels[primary]}」倾向最突出；${name}通常更强调与该项匹配的技能与日常动作。`
    return {
      id,
      name,
      recommendReason,
      aiEraChange: c?.aiEraSummary ?? '',
      careerId: id,
    }
  })

  const workStyleText = close
    ? `你的主倾向偏「${dimensionLabels[primary]}」，同时「${dimensionLabels[secondary]}」也很明显：${workStyleHints[primary]} ${workStyleHints[secondary]}`
    : `你的主倾向偏「${dimensionLabels[primary]}」，次要倾向为「${dimensionLabels[secondary]}」：${workStyleHints[primary]} 若岗位中能顺带发挥「${dimensionLabels[secondary]}」的一面，往往更顺手。`

  const unsuitableText = close
    ? `综合你的前两项倾向，你可能不太适合：${unsuitableHints[primary]} 以及：${unsuitableHints[secondary]}`
    : `你可能不太适合：${unsuitableHints[primary]} 若次要倾向「${dimensionLabels[secondary]}」也较强，完全压抑该侧面的环境同样容易让你疲惫。`

  return {
    scores,
    primaryDimension: primary,
    secondaryDimension: secondary,
    primaryLabel: dimensionLabels[primary],
    secondaryLabel: dimensionLabels[secondary],
    blended: close,
    workStyleText,
    unsuitableText,
    recommendations,
  }
}
