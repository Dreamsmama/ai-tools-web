/** 本地 BGM 目录（相对前端 public） */
export const BGM_PUBLIC_DIR = 'public/short-drama/bgm'

export const BGM_PIANO = 'atlasaudio-emotional-piano-510218.mp3'
export const BGM_AMBIENT = 'atlasaudio-ambient-519913.mp3'
export const BGM_LOFI = 'mondamusic-lofi-lofi-girl-lofi-music-529555.mp3'

/** 与 public/short-drama/bgm/ 下文件名一致 */
export const BGM_TRACKS = [
  {
    file: BGM_PIANO,
    label: 'Emotional Piano · 扎心 / 真实',
    mood: '扎心',
  },
  {
    file: BGM_AMBIENT,
    label: 'Ambient · 压抑 / 紧张',
    mood: '压抑',
  },
  {
    file: BGM_LOFI,
    label: 'Lo-fi Girl · 疲惫 / 搞笑 / 反转',
    mood: '疲惫',
  },
]

export const BGM_MODE_OPTIONS = [
  { value: 'auto', label: '自动匹配', hint: '根据情绪选钢琴 / 氛围 / Lo-fi' },
  { value: 'manual', label: '手动选择', hint: '指定背景音乐' },
  { value: 'none', label: '无 BGM', hint: '仅字幕与画面' },
]

export const DEFAULT_BGM_MODE = 'auto'
export const DEFAULT_BGM_FILE = BGM_PIANO

/** 情绪风格 → BGM（与后端一致） */
export const EMOTION_BGM_HINT = {
  扎心: BGM_PIANO,
  压抑: BGM_AMBIENT,
  疲惫: BGM_LOFI,
  真实: BGM_PIANO,
  搞笑: BGM_LOFI,
  反转: BGM_LOFI,
}

export function suggestBgmFile(emotionStyle) {
  if (!emotionStyle) return DEFAULT_BGM_FILE
  return EMOTION_BGM_HINT[emotionStyle] || DEFAULT_BGM_FILE
}

export function bgmTrackLabel(filename) {
  return BGM_TRACKS.find((t) => t.file === filename)?.label || filename
}
