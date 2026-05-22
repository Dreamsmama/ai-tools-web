/** 今日副本进度文案 */

export function getProgressFeedback(completed, total) {
  if (total <= 0) {
    return { completed: 0, total: 0, percent: 0, text: '今日副本尚未推进' }
  }
  const percent = Math.round((completed / total) * 100)
  let text = '今日副本尚未推进'
  if (completed === 0) {
    text = '今日副本尚未推进'
  } else if (completed >= total) {
    text = '今日副本完成，角色获得完整成长反馈'
  } else if (completed / total >= 0.5) {
    text = '今日路线正在推进中'
  } else if (completed === 1) {
    text = '角色状态开始发生变化'
  } else {
    text = '今日路线正在推进中'
  }
  return { completed, total, percent, text }
}
