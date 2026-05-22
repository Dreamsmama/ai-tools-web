/** 角色 IP 职业列表（与后端 VALID_ROLES 对齐） */
export const CHARACTER_ROLES = [
  { value: 'programmer', label: '程序员' },
  { value: 'product_manager', label: '产品经理' },
  { value: 'hr', label: 'HR' },
  { value: 'tester', label: '测试' },
  { value: 'devops', label: '运维' },
  { value: 'sales', label: '销售' },
]

export function roleLabel(role) {
  return CHARACTER_ROLES.find((r) => r.value === role)?.label || role
}

/** 中文职业名 → 角色 key（与后端 ROLE_CN_TO_KEY 对齐） */
export const CAREER_CN_TO_ROLE = {
  程序员: 'programmer',
  产品经理: 'product_manager',
  HR: 'hr',
  测试: 'tester',
  运维: 'devops',
  销售: 'sales',
}

export function careerToRoleKey(careerCn) {
  const cn = (careerCn || '').trim()
  if (!cn) return ''
  return CAREER_CN_TO_ROLE[cn] || ''
}

/** @deprecated 请使用 useProfessionStore().careerOptions() */
export const CAREER_OPTIONS_FROM_BUILTIN = CHARACTER_ROLES.map((r) => r.label)
