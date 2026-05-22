/** 规范化 AI 结果，兼容旧版 main_quest.actions */

const DEFAULT_REWARD = { energy: 0, explore: 0, express: 0, discipline: 0, social: 0, growth: 1 }

const JSON_ARTIFACT = /^"?\w+"?\s*:\s*/

function cleanDisplayText(value) {
  if (value == null) return ''
  let text = String(value).trim()
  if (!text) return ''
  const kv = text.match(/^"?\w+"?\s*:\s*"?(.+?)"?,?\s*$/s)
  if (kv) return kv[1].trim()
  if (JSON_ARTIFACT.test(text) || text === '{') return ''
  return text
}

function clampReward(reward) {
  const r = { ...DEFAULT_REWARD, ...(reward || {}) }
  for (const k of Object.keys(DEFAULT_REWARD)) {
    const n = Number(r[k]) || 0
    r[k] = Math.min(3, Math.max(0, n))
  }
  return r
}

function normalizeMainTasks(main) {
  if (!main) return []
  if (main.tasks?.length) {
    return main.tasks.map((t, idx) => ({
      id: t.id || `task_${idx + 1}`,
      title: cleanDisplayText(t.title) || `子任务 ${idx + 1}`,
      action: cleanDisplayText(t.action) || '',
      estimated_time: cleanDisplayText(t.estimated_time) || '约 10 分钟',
      reward: clampReward(t.reward),
    }))
  }
  const actions = main.actions || []
  if (actions.length) {
    return actions.map((act, idx) => {
      const text = String(act).trim()
      return {
        id: `task_${idx + 1}`,
        title: text.slice(0, 24) || `子任务 ${idx + 1}`,
        action: text,
        estimated_time: '约 10 分钟',
        reward: { ...DEFAULT_REWARD, growth: 1 },
      }
    })
  }
  return []
}

function normalizeSideQuests(list) {
  return (list || []).map((sq, idx) => {
    const reward = clampReward(sq.reward)
    const hasReward = Object.values(reward).some((v) => v > 0)
    return {
      id: sq.id || `side_${idx + 1}`,
      title: cleanDisplayText(sq.title) || '支线',
      action: cleanDisplayText(sq.action) || '',
      reward: hasReward ? reward : { ...DEFAULT_REWARD, growth: 1 },
      reward_text: sq.reward_text || '',
    }
  })
}

export function normalizeLifeRpgResult(raw) {
  if (!raw) return null
  const data = { ...raw }
  const main = { ...(data.main_quest || {}) }
  let tasks = normalizeMainTasks(main)
  while (tasks.length < 3) {
    const i = tasks.length
    tasks.push({
      id: `task_${i + 1}`,
      title: `轻量行动 ${i + 1}`,
      action: '完成一件今天能做的小事',
      estimated_time: '约 10 分钟',
      reward: { ...DEFAULT_REWARD, growth: 1 },
    })
  }
  tasks = tasks.slice(0, 3)
  const world = { ...(data.world_state || {}) }
  data.world_state = {
    title: cleanDisplayText(world.title),
    description: cleanDisplayText(world.description),
  }
  data.route_continuation = cleanDisplayText(data.route_continuation)
  data.main_quest = {
    title: cleanDisplayText(main.title) || '',
    goal: cleanDisplayText(main.goal) || '',
    estimated_time: cleanDisplayText(main.estimated_time) || '',
    tasks,
  }
  data.side_quests = normalizeSideQuests(data.side_quests)

  if (!data.route_continuation && data.role_summary) {
    data.route_continuation = data.role_summary
  }

  if (!data.result_id) {
    data.result_id = String(data.saved_at || Date.now())
  }
  return data
}


export function collectAllTasks(result) {
  const main = (result?.main_quest?.tasks || []).map((t) => ({ ...t, kind: 'main' }))
  const side = (result?.side_quests || []).map((t) => ({ ...t, kind: 'side' }))
  return [...main, ...side]
}

export function findTaskById(result, taskId) {
  return collectAllTasks(result).find((t) => t.id === taskId) || null
}
