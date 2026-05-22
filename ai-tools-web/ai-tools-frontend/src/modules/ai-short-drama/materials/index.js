/** 素材库 mock（与后端 MATERIAL_CATALOG 保持同步，供本地预览/扩展） */
export const MATERIAL_CATALOG = [
  {
    id: 'programmer_tired_001',
    name: '疲惫程序员',
    url: '/short-drama/programmer_tired_001.png',
    tags: ['programmer', 'tired', 'night_office'],
  },
  {
    id: 'programmer_error_001',
    name: '报错日志屏',
    url: '/short-drama/programmer_error_001.png',
    tags: ['programmer', 'error_log', 'night_office'],
  },
  {
    id: 'programmer_hoodie_001',
    name: '灰色卫衣工位',
    url: '/short-drama/programmer_hoodie_001.png',
    tags: ['programmer', 'hoodie', 'office'],
  },
  {
    id: 'pm_meeting_001',
    name: '产品经理开会',
    url: '/short-drama/pm_meeting_001.png',
    tags: ['product_manager', 'meeting', 'confident'],
  },
  {
    id: 'pm_laptop_001',
    name: '拿电脑的 PM',
    url: '/short-drama/pm_laptop_001.png',
    tags: ['product_manager', 'laptop', 'office'],
  },
  {
    id: 'hr_interview_001',
    name: 'HR 面试现场',
    url: '/short-drama/hr_interview_001.png',
    tags: ['hr', 'interview', 'resume'],
  },
  {
    id: 'hr_messages_001',
    name: '飞书消息轰炸',
    url: '/short-drama/hr_messages_001.png',
    tags: ['hr', 'messages', 'office'],
  },
  {
    id: 'tester_bug_001',
    name: '测试背锅现场',
    url: '/short-drama/tester_bug_001.png',
    tags: ['tester', 'bug', 'blame'],
  },
  {
    id: 'ops_alert_001',
    name: '凌晨报警',
    url: '/short-drama/ops_alert_001.png',
    tags: ['ops', 'alert', 'night', 'oncall'],
  },
  {
    id: 'sales_phone_001',
    name: '销售电话跟进',
    url: '/short-drama/sales_phone_001.png',
    tags: ['sales', 'phone', 'pressure'],
  },
  {
    id: 'office_night_001',
    name: '深夜办公室',
    url: '/short-drama/office_night_001.png',
    tags: ['night_office', 'office', 'late'],
  },
  {
    id: 'meeting_room_001',
    name: '会议室',
    url: '/short-drama/meeting_room_001.png',
    tags: ['meeting', 'office'],
  },
]

export const DEFAULT_MATERIAL = {
  id: 'material_missing',
  name: '缺少可用素材',
  url: '',
  tags: [],
}

/** @param {string[]} imageTags */
export function matchMaterial(imageTags) {
  const normalized = (imageTags || []).map((t) => String(t).trim().toLowerCase()).filter(Boolean)
  if (!normalized.length) return { ...DEFAULT_MATERIAL }

  const tagSet = new Set(normalized)
  let best = null
  let bestScore = 0

  for (const item of MATERIAL_CATALOG) {
    const itemTags = new Set((item.tags || []).map((t) => t.toLowerCase()))
    let score = 0
    for (const t of tagSet) {
      if (itemTags.has(t)) score += 1
    }
    if (score > bestScore) {
      bestScore = score
      best = item
    }
  }

  return best && bestScore > 0 ? { ...best } : { ...DEFAULT_MATERIAL }
}
