import { buildTestResult, rankDimensions } from './careerTestEngine'
import { computeDimensionScores } from './careerTestEngine'
import { dimensionLabels } from '../data/careerTestQuestions'
import {
  CAUTION_MAJOR_IDS,
  DIMENSION_MAJOR_IDS,
  getMajorById,
  majorsCatalog,
} from '../data/gaokao/majorsCatalog'
import { getCareerById } from '../data/careersCatalog'

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

function ensureMajorIds(ids, primaryKey) {
  const out = dedupeKeepOrder(ids)
  const pool = DIMENSION_MAJOR_IDS[primaryKey] ?? []
  for (let i = 0; out.length < 5 && i < pool.length; i++) {
    if (!out.includes(pool[i])) out.push(pool[i])
  }
  return out.slice(0, 5)
}

/**
 * @param {Record<string, number>} scores
 * @param {{ sorted: { key: string, score: number }[] }} ranked
 */
function pickRecommendedMajorIds(scores, ranked) {
  const top = ranked.sorted[0]
  const second = ranked.sorted[1]
  const close = top.score - second.score <= Math.max(3, top.score * 0.12)
  const poolPrimary = [...(DIMENSION_MAJOR_IDS[top.key] ?? [])]
  if (!close) return ensureMajorIds(poolPrimary, top.key)

  const merged = [...poolPrimary, ...(DIMENSION_MAJOR_IDS[second.key] ?? [])]
  return ensureMajorIds(merged, top.key)
}

function pickNotRecommendedMajorIds(recommendedIds, primaryKey) {
  const recSet = new Set(recommendedIds)
  const weakPool = majorsCatalog
    .filter((m) => !m.dimensions.includes(primaryKey))
    .map((m) => m.id)
  const caution = CAUTION_MAJOR_IDS.filter((id) => !recSet.has(id))
  const merged = dedupeKeepOrder([...caution, ...weakPool])
  return merged.filter((id) => !recSet.has(id)).slice(0, 4)
}

/**
 * @param {(number|null)[]} answers
 */
export function buildGaokaoTestResult(answers) {
  const base = buildTestResult(answers)
  const scores = computeDimensionScores(answers)
  const ranked = rankDimensions(scores)
  const majorIds = pickRecommendedMajorIds(scores, ranked)
  const notRecommendedIds = pickNotRecommendedMajorIds(majorIds, ranked.primary)

  const recommendedMajors = majorIds.map((id) => {
    const m = getMajorById(id)
    const careers = (m?.careerIds ?? [])
      .map((cid) => getCareerById(cid))
      .filter(Boolean)
      .map((c) => ({ id: c.id, name: c.name }))
    return {
      id,
      name: m?.name ?? id,
      futureDirection: m?.futureDirection ?? '',
      aiRisk: m?.aiRisk ?? '',
      aiRiskLevel: m?.aiRiskLevel ?? 'medium',
      careers,
      caution: m?.caution ?? '',
    }
  })

  const notRecommendedMajors = notRecommendedIds.map((id) => {
    const m = getMajorById(id)
    return {
      id,
      name: m?.name ?? id,
      reason: m?.caution ?? `与你的「${dimensionLabels[ranked.primary]}」主倾向匹配度较低，填报前建议多了解真实课程与就业路径。`,
    }
  })

  const industryDirections = [
    `基于你的「${dimensionLabels[ranked.primary]}」倾向，优先考虑与${recommendedMajors
      .slice(0, 3)
      .map((m) => m.name)
      .join('、')}相关的行业赛道。`,
    ranked.blended
      ? `你的「${dimensionLabels[ranked.secondary]}」也很突出，适合选能同时发挥两种能力的交叉专业或双学位方向。`
      : `次要倾向为「${dimensionLabels[ranked.secondary]}」，可作为第二专业或辅修参考。`,
  ]

  const aiEraAnalysis = {
    summary: `AI 正在重塑各专业的工作方式，但不是「均匀替代」。你的画像更偏向「${dimensionLabels[ranked.primary]}」型能力，应优先选择能积累判断力、协作与复杂问题拆解的专业，而不是只追热门名称。`,
    risks: recommendedMajors.map((m) => ({
      major: m.name,
      level: m.aiRiskLevel,
      text: m.aiRisk,
    })),
    highRiskNote:
      '填报时警惕：课程仍以死记硬背为主、缺乏实践与数字化技能训练的专业；以及产业周期明显下行、却仍在扩招的方向。',
  }

  const careerPaths = recommendedMajors.flatMap((m) =>
    m.careers.map((c) => ({
      majorId: m.id,
      majorName: m.name,
      careerId: c.id,
      careerName: c.name,
    })),
  )

  const seenCareers = new Set()
  const uniqueCareerPaths = []
  for (const p of careerPaths) {
    if (seenCareers.has(p.careerId)) continue
    seenCareers.add(p.careerId)
    uniqueCareerPaths.push(p)
  }

  return {
    ...base,
    mode: 'gaokao',
    recommendedMajors,
    notRecommendedMajors,
    industryDirections,
    aiEraAnalysis,
    careerPaths: uniqueCareerPaths.slice(0, 8),
  }
}
