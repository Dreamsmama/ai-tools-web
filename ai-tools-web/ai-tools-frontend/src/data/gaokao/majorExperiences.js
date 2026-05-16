/**
 * 专业 → 未来职业一日体验（体验馆扩展元数据）
 * @typedef {{
 *   id: string,
 *   majorLabel: string,
 *   title: string,
 *   tagline: string,
 *   available: boolean,
 *   to: string,
 *   posterEmoji: string,
 * }} MajorExperienceItem
 */

/** @type {MajorExperienceItem[]} */
export const majorFutureExperiences = [
  {
    id: 'developer',
    majorLabel: '计算机',
    title: '学计算机以后的一天',
    tagline: '像追剧一样，体验代码、需求与线上消息同时爆炸。',
    available: true,
    to: '/career-experience/developer',
    posterEmoji: '💻',
  },
  {
    id: 'lawyer',
    majorLabel: '法学',
    title: '学法学以后的一天',
    tagline: '材料、庭审与客户沟通——未来法律人的真实节奏。',
    available: true,
    to: '/career-experience/major-law',
    posterEmoji: '⚖️',
  },
  {
    id: 'finance',
    majorLabel: '金融',
    title: '学金融以后的一天',
    tagline: '数据、风控与决策会——感受金融行业的信息密度。',
    available: true,
    to: '/career-experience/major-finance',
    posterEmoji: '📈',
  },
  {
    id: 'doctor',
    majorLabel: '医学',
    title: '学医学以后的一天',
    tagline: '查房、病历与突发状况——长学制背后的日常强度。',
    available: true,
    to: '/career-experience/major-medicine',
    posterEmoji: '🩺',
  },
]
