import { API, apiUrl, logApiFailure } from '../../../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../../../clientErrors.js'

/** 整次生成：文案分析 + 多段即梦配图，长文案常需 10～20 分钟 */
const GENERATE_TIMEOUT_MS = 1_800_000

/**
 * @param {{
 *   input_mode?: 'script'|'ai',
 *   script?: string,
 *   career?: string,
 *   theme?: string,
 *   emotion_style?: string,
 * }} form
 */
export async function requestShortDramaGenerate(form) {
  const url = apiUrl(API.aiShortDramaGenerate)
  const mode = form.input_mode || 'script'
  const requestBody = {
    input_mode: mode,
    generate_dynamic_materials: true,
  }
  if (mode === 'script') {
    requestBody.script = form.script
    if (form.career) requestBody.career = form.career
  } else {
    requestBody.career = form.career
    requestBody.theme = form.theme
    requestBody.emotion_style = form.emotion_style
  }

  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), GENERATE_TIMEOUT_MS)

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      return { ok: false, message: httpErrorMessage(res.status), kind: `http_${res.status}` }
    }

    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      return { ok: false, message: RESPONSE_PARSE_ERROR, kind: 'response_parse_error' }
    }

    if (payload?.success === false) {
      return {
        ok: false,
        message: payload?.message || '生成失败，请稍后再试。',
        stage: payload?.stage,
        kind: payload?.stage ? `stage_${payload.stage}` : 'business_error',
      }
    }

    if (!payload || payload.code !== 0 || !payload.data) {
      return {
        ok: false,
        message: payload?.message || '生成失败，请稍后再试。',
        stage: payload?.stage,
        kind: payload?.code != null ? `business_${payload.code}` : 'business_error',
      }
    }

    return { ok: true, data: payload.data }
  } catch (err) {
    if (err?.name === 'AbortError') {
      const mins = Math.round(GENERATE_TIMEOUT_MS / 60_000)
      return {
        ok: false,
        message: `生成超时（已等待 ${mins} 分钟）。AI 逐段配图较慢，长文案可能需要 15 分钟以上；可缩短文案后重试。`,
        kind: 'client_timeout',
      }
    }
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  } finally {
    window.clearTimeout(timer)
  }
}

/**
 * @param {{
 *   title: string,
 *   segments?: Array<{ segmentNo: number, duration: number, text: string, imageUrl?: string, material?: { url?: string } }>,
 *   shots?: Array<{ shotNo: number, duration: number, subtitle: string, imageUrl?: string, material?: { url?: string } }>,
 * }} payload
 */
export async function requestShortDramaRenderVideo(payload) {
  const url = apiUrl(API.aiShortDramaRenderVideo)
  const segments = payload.segments?.length
    ? payload.segments
    : (payload.shots || []).map((s) => ({
        segmentNo: s.shotNo,
        duration: s.duration,
        text: s.subtitle,
        imageUrl: s.imageUrl || s.material?.url || '',
      }))

  const requestBody = {
    title: payload.title || '',
    bgm_mode: payload.bgm_mode || 'auto',
    segments: segments.map((s) => ({
      segmentNo: s.segmentNo,
      duration: s.duration,
      text: s.text,
      emotion: s.emotion || '',
      imageUrl: s.imageUrl || s.material?.url || '',
    })),
    shots: segments.map((s) => ({
      shotNo: s.segmentNo,
      duration: s.duration,
      subtitle: s.text,
      imageUrl: s.imageUrl || s.material?.url || '',
    })),
  }
  if (payload.emotion_style) {
    requestBody.emotion_style = payload.emotion_style
  }
  if (payload.bgm_mode === 'manual' && payload.bgm_file) {
    requestBody.bgm_file = payload.bgm_file
  }
  if (payload.voice_id) {
    requestBody.voice_id = payload.voice_id
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      return { ok: false, message: httpErrorMessage(res.status), kind: `http_${res.status}` }
    }

    let body
    try {
      body = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      return { ok: false, message: RESPONSE_PARSE_ERROR, kind: 'response_parse_error' }
    }

    if (!body || body.code !== 0) {
      return {
        ok: false,
        message: body?.message || '视频生成失败，请稍后再试。',
        kind: body?.code != null ? `business_${body.code}` : 'business_error',
        data: body?.data,
      }
    }

    if (!body.data?.videoUrl) {
      return {
        ok: false,
        message: body?.message || '视频生成失败，请稍后再试。',
        kind: 'business_error',
      }
    }

    return { ok: true, data: body.data, message: body?.message || '' }
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}
