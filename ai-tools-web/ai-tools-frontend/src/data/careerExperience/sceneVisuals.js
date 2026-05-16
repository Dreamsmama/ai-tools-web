/** 连续剧场景氛围：镜头标签 + 色调（不依赖 emoji，避免系统渲染成日历等） */
export const SCENE_VISUALS = {
  developer: {
    scene_1: { label: '线上事故', tint: 'alert' },
    scene_2: { label: '临时会议室', tint: 'meeting' },
    scene_3: { label: '工单标红', tint: 'chaos' },
    scene_4: { label: '深夜工位', tint: 'night' },
    scene_5: { label: '生活入侵', tint: 'life' },
  },
  'developer-ep02': {
    scene_1: { label: '准备下班', tint: 'night' },
    scene_2: { label: '问题扩大', tint: 'chaos' },
    scene_3: { label: '临时会议', tint: 'meeting' },
    scene_4: { label: '生活消息', tint: 'life' },
  },
  hr: {
    scene_1: { label: '招聘后台', tint: 'inbox' },
    scene_2: { label: '面试崩盘', tint: 'meeting' },
    scene_3: { label: '员工情绪', tint: 'emotion' },
    scene_4: { label: '绩效会议', tint: 'meeting' },
    scene_5: { label: '保密名单', tint: 'pressure' },
    scene_6: { label: '下不了班', tint: 'life' },
  },
}

export function getSceneVisual(experienceId, sceneId) {
  const bucket =
    SCENE_VISUALS[experienceId] ??
    SCENE_VISUALS[experienceId.replace(/-ep\d+$/, '')] ??
    null
  return bucket?.[sceneId] ?? { label: '工位现场', tint: 'default' }
}
