export const MATERIAL_TYPES = [
  { value: 'character', label: '角色 character' },
  { value: 'scene', label: '场景 scene' },
  { value: 'ui', label: '界面 ui' },
  { value: 'props', label: '道具 props' },
  { value: 'effects', label: '特效 effects' },
  { value: 'placeholder', label: '占位 placeholder' },
]

/** 素材来源筛选 */
export const MATERIAL_SOURCE_FILTERS = [
  { value: '', label: '全部来源' },
  { value: 'false', label: '手动上传' },
  { value: 'true', label: 'AI 生成' },
]

/** 快速分类 Tab */
export const MATERIAL_CATEGORY_TABS = [
  { value: '', label: '全部' },
  { value: 'character', label: '角色' },
  { value: 'scene', label: '场景' },
  { value: 'ui', label: 'UI' },
  { value: 'props', label: '道具' },
]

/** 上传时必选职业（不含 none） */
export const MATERIAL_ROLES_UPLOAD = [
  { value: 'programmer', label: '程序员 programmer' },
  { value: 'product_manager', label: '产品经理 product_manager' },
  { value: 'hr', label: 'HR' },
  { value: 'tester', label: '测试 tester' },
  { value: 'devops', label: '运维 devops' },
  { value: 'sales', label: '销售 sales' },
]

export const MATERIAL_ROLES = [
  { value: 'none', label: '不限' },
  { value: 'programmer', label: '程序员 programmer' },
  { value: 'product_manager', label: '产品经理 product_manager' },
  { value: 'hr', label: 'HR' },
  { value: 'tester', label: '测试 tester' },
  { value: 'devops', label: '运维 devops' },
  { value: 'sales', label: '销售 sales' },
]

export const MATERIAL_EMOTIONS = [
  { value: 'none', label: '不限' },
  { value: 'normal', label: '正常 normal' },
  { value: 'tired', label: '疲惫 tired' },
  { value: 'stressed', label: '压力 stressed' },
  { value: 'shocked', label: '震惊 shocked' },
  { value: 'angry', label: '愤怒 angry' },
  { value: 'happy', label: '开心 happy' },
  { value: 'confused', label: '困惑 confused' },
]

export const MATERIAL_SCENES = [
  { value: 'none', label: '不限' },
  { value: 'night_office', label: '深夜办公室' },
  { value: 'meeting_room', label: '会议室' },
  { value: 'desk', label: '工位 desk' },
  { value: 'interview_room', label: '面试间' },
  { value: 'server_room', label: '机房 server_room' },
  { value: 'office', label: '办公室 office' },
]

export function labelOf(options, value) {
  return options.find((o) => o.value === value)?.label || value
}

/** 根据下拉选项自动生成基础 tags（用户可不手填） */
export function buildAutoTags({ type, role, emotion, scene }) {
  const tags = []
  const push = (v) => {
    const t = String(v || '').trim().toLowerCase()
    if (t && t !== 'none' && !tags.includes(t)) tags.push(t)
  }
  push(type)
  push(role)
  push(emotion)
  push(scene)
  return tags
}

export function mergeTags(manualTags, autoTags) {
  const out = []
  for (const t of [...(manualTags || []), ...(autoTags || [])]) {
    const n = String(t).trim().toLowerCase()
    if (n && !out.includes(n)) out.push(n)
  }
  return out
}
