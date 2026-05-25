import { API, apiUrl, logApiFailure } from '../api.js'

/**
 * 请求 AI 换发型接口。
 * @param {{ image: File, style: string, gender: 'male' | 'female' }} payload
 * @returns {Promise<{ ok: boolean, data?: { resultImageUrl: string, suggestion: string }, kind?: string, message?: string }>}
 */
export async function requestHairstyleGenerate(payload) {
  const url = apiUrl(API.hairstyleGenerate)
  const formData = new FormData()
  formData.append('image', payload.image)
  formData.append('style', payload.style)
  formData.append('gender', payload.gender)

  let res
  try {
    res = await fetch(url, { method: 'POST', body: formData })
  } catch (err) {
    await logApiFailure(url, { style: payload.style, gender: payload.gender }, null, err)
    return { ok: false, kind: 'network', message: '网络错误，请检查连接后重试' }
  }

  if (!res.ok) {
    await logApiFailure(url, { style: payload.style, gender: payload.gender }, res, null)
    return { ok: false, kind: 'api', message: '生成失败，请稍后重试' }
  }

  const data = await res.json()
  return { ok: true, data }
}
