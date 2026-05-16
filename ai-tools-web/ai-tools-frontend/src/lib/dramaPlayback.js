/**
 * @param {number} min
 * @param {number} max
 */
export function dramaDelay(min, max) {
  return new Promise((resolve) => {
    setTimeout(resolve, min + Math.random() * (max - min))
  })
}

/**
 * @param {string} [source]
 * @returns {'group' | 'private' | 'life' | 'call' | 'alert'}
 */
export function inferMessageTone(source) {
  if (!source) return 'group'
  if (/生活|女友|朋友|老妈|家人|对象/.test(source)) return 'life'
  if (/电话|来电|总监.*电话/.test(source)) return 'call'
  if (/工单|报警|标红|错误日志/.test(source)) return 'alert'
  if (/私聊|微信|候选人/.test(source) && !/群/.test(source)) return 'private'
  return 'group'
}

/**
 * @param {string} [source]
 */
export function inferTypingName(source) {
  if (!source) return '对方'
  const map = [
    [/产品经理/, '产品经理'],
    [/主管/, '主管'],
    [/面试官/, '面试官'],
    [/候选人/, '候选人'],
    [/员工/, '员工'],
    [/女朋友/, '女朋友'],
    [/朋友/, '朋友'],
    [/老妈/, '老妈'],
    [/老板/, '老板'],
    [/负责人/, '负责人'],
    [/同事/, '同事'],
    [/测试/, '测试同学'],
  ]
  for (const [re, name] of map) {
    if (re.test(source)) return name
  }
  return source.replace(/群|私聊|消息/g, '').slice(0, 8) || '对方'
}

/**
 * @param {{ time: string, sceneTitle?: string }} scene
 */
export function formatSceneChapter(scene) {
  const title = scene.sceneTitle || '新场景'
  return `${scene.time}｜${title}`
}

/** @type {Record<string, { label: string, emoji: string }>} */
export const DRAMA_MOMENTS = {
  'ticket-red': { label: '工单已标红', emoji: '🔴' },
  'feishu-dot': { label: '飞书 99+', emoji: '💬' },
  'call-incoming': { label: '来电', emoji: '📞' },
  'voice-message': { label: '语音消息', emoji: '🎤' },
  'phone-vibrate': { label: '手机震动', emoji: '📳' },
  'meeting-pop': { label: '会议弹窗', emoji: '📅' },
}
