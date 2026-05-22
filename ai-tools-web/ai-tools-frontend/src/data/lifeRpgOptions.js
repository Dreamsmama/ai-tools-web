/** 人生状态（可多选） */
export const LIFE_STATE_OPTIONS = [
  '更自律',
  '更有生活感',
  '更健康',
  '更会表达',
  '更有探索欲',
  '更有职业竞争力',
  '更有创造力',
  '更稳定的情绪',
  '自定义',
]

/** 人生方向模板（单选大卡片） */
export const DIRECTION_TEMPLATES = [
  {
    id: 'growth',
    title: '成长推进型',
    subtitle: '适合：想提升技能、长期成长的人',
    examples: ['学 AI 开发', '提升表达', '做副业', '提高职业竞争力'],
  },
  {
    id: 'recovery',
    title: '生活恢复型',
    subtitle: '适合：最近精神状态偏累的人',
    examples: ['规律生活', '少刷手机', '恢复生活感'],
  },
  {
    id: 'interest',
    title: '兴趣培养型',
    subtitle: '适合：想重新建立兴趣世界的人',
    examples: ['吉他', '摄影', '健身', '阅读'],
  },
  {
    id: 'journal',
    title: '人生记录型',
    subtitle: '适合：想长期记录和推进人生状态的人',
    examples: ['每天记录一点', '保持长期节奏', '推进生活状态'],
  },
]

export const RECOMMENDED_KEYWORDS = [
  'AI开发',
  '健身',
  '摄影',
  '表达',
  '自律',
  '规律生活',
  '少刷手机',
]

export const MAX_LIFE_KEYWORDS = 5

/** @deprecated 兼容旧引用 */
export const TARGET_PERSONA_OPTIONS = LIFE_STATE_OPTIONS.map((s) =>
  s === '自定义' ? '自定义' : `${s}的人`,
)

export const LONG_TERM_DIRECTION_OPTIONS = DIRECTION_TEMPLATES.map((t) => t.title)

export const ENERGY_OPTIONS = ['很累', '一般', '精力不错']

export const DAILY_MODE_OPTIONS = [
  '正常推进',
  '降低难度',
  '想挑战一点',
  '今天只想恢复',
]

export const GO_OUT_OPTIONS = ['不想出门', '可以附近走走', '想出去']

export const IDENTITY_TYPE_OPTIONS = [
  '职场人',
  '学生',
  '创业者',
  '自由职业',
  '待业 / 转型中',
  '暂不填写',
]

const DIRECT_IDENTITY_MAP = {
  学生: '学生',
  创业者: '创业者',
  自由职业: '自由职业',
  '待业 / 求职中': '待业 / 转型中',
  '待业 / 转型中': '待业 / 转型中',
  暂不填写: '暂不填写',
  职场人: '职场人',
  全职家长: '待业 / 转型中',
}

const LEGACY_STATE_MAP = {
  '更自律的人': '更自律',
  '更有生活感的人': '更有生活感',
  '更健康的人': '更健康',
  '更会表达的人': '更会表达',
  '更有趣的人': '更有探索欲',
  '更会社交的人': '更有探索欲',
  '更有职业竞争力的人': '更有职业竞争力',
  '更能坚持兴趣的人': '更有创造力',
}

export function normalizeLifeState(label) {
  const s = (label || '').trim()
  if (!s) return ''
  if (LIFE_STATE_OPTIONS.includes(s)) return s
  if (LEGACY_STATE_MAP[s]) return LEGACY_STATE_MAP[s]
  if (s.endsWith('的人')) {
    const base = s.slice(0, -2)
    if (LIFE_STATE_OPTIONS.includes(base)) return base
  }
  return s
}

export function getResolvedLifeStates(form) {
  const raw = [...(form?.life_states || [])]
  const states = raw
    .map(normalizeLifeState)
    .filter((s) => s && s !== '自定义')
  if (raw.includes('自定义')) {
    const custom = (form?.custom_life_state || '').trim()
    if (custom) states.push(custom)
  }
  return [...new Set(states)]
}

export function getDirectionTemplate(id) {
  return DIRECTION_TEMPLATES.find((t) => t.id === id) || null
}

export function createDefaultCharacterForm() {
  return {
    life_states: [],
    custom_life_state: '',
    direction_template: '',
    life_keywords: [],
    custom_notes: '',
    identity_type: '',
    occupation: '',
  }
}

/** 提交 API 与旧字段映射 */
export function buildCreateRoutePayload(form) {
  const states = getResolvedLifeStates(form)
  const template = getDirectionTemplate(form.direction_template)
  const keywords = [...(form.life_keywords || [])].slice(0, MAX_LIFE_KEYWORDS)
  const notes = (form.custom_notes || '').trim()
  const { identity_type, occupation } = resolveIdentityPayload(form)

  const keywordLine = keywords.length ? `人生关键词：${keywords.join('、')}` : ''
  const combinedGoals = [keywordLine, notes].filter(Boolean).join('\n')

  return {
    life_states: states,
    custom_life_state: (form.custom_life_state || '').trim(),
    direction_template: form.direction_template || '',
    life_keywords: keywords,
    target_person: states[0] || (form.custom_life_state || '').trim() || '人生探索者',
    custom_target_person: (form.custom_life_state || '').trim(),
    long_term_directions: template ? [template.title] : [],
    custom_long_term_goals: combinedGoals,
    identity_type,
    occupation,
    status_notes: notes,
  }
}

export function validateCharacterForm(form) {
  const states = getResolvedLifeStates(form)
  if (!states.length) {
    return { ok: false, message: '请至少选择一项你想靠近的人生状态。' }
  }
  if (form.life_states?.includes('自定义') && !(form.custom_life_state || '').trim()) {
    return { ok: false, message: '请用一句话描述你的自定义状态。' }
  }
  if (!(form.direction_template || '').trim()) {
    return { ok: false, message: '请先选择一个人生方向模板。' }
  }
  if (!(form.life_keywords || []).length) {
    return { ok: false, message: '请至少添加一个人生关键词。' }
  }
  return { ok: true }
}

export function characterFormFromProfile(p) {
  if (!p) return createDefaultCharacterForm()
  const { identity_type, occupation } = identityFieldsFromProfile(p)

  let life_states = []
  const tp = p.targetPerson || p.target_person || ''
  if (p.lifeStates?.length) {
    life_states = p.lifeStates.map(normalizeLifeState).filter((s) => LIFE_STATE_OPTIONS.includes(s))
  } else if (tp) {
    const parts = tp.split(/[、,，]/).map((x) => x.trim()).filter(Boolean)
    for (const part of parts) {
      const norm = normalizeLifeState(part)
      if (LIFE_STATE_OPTIONS.includes(norm)) life_states.push(norm)
      else if (part) {
        life_states.push('自定义')
      }
    }
    if (!life_states.length && tp) {
      const single = normalizeLifeState(tp.endsWith('的人') ? tp : `${tp}的人`)
      if (LIFE_STATE_OPTIONS.includes(single)) life_states = [single]
      else {
        life_states = ['自定义']
      }
    }
  }

  let custom_life_state = p.customLifeState || ''
  if (life_states.includes('自定义') && !custom_life_state) {
    const parts = tp.split(/[、,，]/).map((x) => x.trim()).filter(Boolean)
    custom_life_state = parts.find((x) => !LIFE_STATE_OPTIONS.includes(normalizeLifeState(x))) || custom_life_state
  }

  let direction_template = p.directionTemplate || ''
  if (!direction_template && p.longTermDirections?.length) {
    const title = p.longTermDirections[0]
    const found = DIRECTION_TEMPLATES.find((t) => t.title === title)
    if (found) direction_template = found.id
  }

  let life_keywords = [...(p.lifeKeywords || [])]
  if (!life_keywords.length && p.customLongTermGoals) {
    const m = p.customLongTermGoals.match(/人生关键词[：:]\s*([^\n]+)/)
    if (m) {
      life_keywords = m[1].split(/[、,，]/).map((x) => x.trim()).filter(Boolean)
    }
  }

  let custom_notes = p.customNotes || ''
  if (!custom_notes && p.customLongTermGoals) {
    custom_notes = p.customLongTermGoals.replace(/人生关键词[：:][^\n]+\n?/, '').trim()
  }

  return {
    life_states: [...new Set(life_states)],
    custom_life_state,
    direction_template,
    life_keywords: life_keywords.slice(0, MAX_LIFE_KEYWORDS),
    custom_notes,
    identity_type,
    occupation,
  }
}

export function buildProfileFromRoute(routeData, form) {
  const states = getResolvedLifeStates(form)
  const template = getDirectionTemplate(form.direction_template)
  const keywords = [...(form.life_keywords || [])]
  const { identity_type, occupation } = resolveIdentityPayload(form)
  const notes = (form.custom_notes || '').trim()

  return {
    lifeStates: states,
    directionTemplate: form.direction_template,
    directionTemplateTitle: template?.title || '',
    lifeKeywords: keywords,
    customNotes: notes,
    targetPerson: states.join('、') || (form.custom_life_state || '').trim(),
    longTermDirections: template ? [template.title] : [],
    customLongTermGoals: buildCreateRoutePayload(form).custom_long_term_goals,
    identityType: identity_type,
    occupation,
    identity: occupation || identity_type,
    routeTitle: routeData.route_title,
    routeSummary: routeData.route_summary,
    coreAttributes: routeData.core_attributes || [],
    longTermMainLine: routeData.long_term_main_line || '',
    suggestedGrowthStyle: routeData.suggested_growth_style || '',
    avoidStyle: routeData.avoid_style || '',
    createdAt: Date.now(),
  }
}

export function migrateLegacyIdentity(saved) {
  const identityType = (saved?.identityType || saved?.identity_type || '').trim()
  const occupation = (saved?.occupation || '').trim()
  if (identityType) {
    return { identity_type: identityType, occupation }
  }

  const legacy = (saved?.identity || '').trim()
  if (!legacy) return { identity_type: '', occupation: '' }
  if (DIRECT_IDENTITY_MAP[legacy]) {
    return { identity_type: DIRECT_IDENTITY_MAP[legacy], occupation: '' }
  }
  return { identity_type: '职场人', occupation: legacy }
}

export function normalizeLifeRpgProfile(profile) {
  if (!profile || typeof profile !== 'object') return profile
  const { identity_type, occupation } = migrateLegacyIdentity(profile)
  return {
    ...profile,
    identityType: identity_type,
    occupation,
  }
}

export function identityFieldsFromProfile(p) {
  const norm = normalizeLifeRpgProfile(p)
  return {
    identity_type: norm?.identityType || '',
    occupation: norm?.occupation || '',
  }
}

export function resolveIdentityPayload(form) {
  const identity_type = (form?.identity_type || '').trim()
  const occupation = (form?.occupation || '').trim()
  return {
    identity_type: identity_type || '暂不填写',
    occupation: identity_type === '暂不填写' ? '' : occupation,
  }
}

/** @deprecated */
export function resolveIdentity(form) {
  const { identity_type, occupation } = resolveIdentityPayload(form)
  if (identity_type === '暂不填写') return ''
  if (occupation) return occupation
  return identity_type
}
