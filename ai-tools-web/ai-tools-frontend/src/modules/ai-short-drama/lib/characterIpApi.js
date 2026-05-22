import { API, apiUrl, logApiFailure } from '../../../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../../../clientErrors.js'

const AI_GENERATE_TIMEOUT_MS = 280_000
const PROFESSIONS_TIMEOUT_MS = 8_000
const WORKBENCH_TIMEOUT_MS = 8_000

async function parseEnvelope(res, url, requestBody) {
  if (!res.ok) {
    await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
    return { ok: false, message: httpErrorMessage(res.status) }
  }
  let payload
  try {
    payload = await res.json()
  } catch (parseErr) {
    await logApiFailure(url, requestBody, res, parseErr)
    return { ok: false, message: RESPONSE_PARSE_ERROR }
  }
  if (!payload || payload.code !== 0) {
    return { ok: false, message: payload?.message || '操作失败' }
  }
  return { ok: true, data: payload.data, message: payload.message }
}

export async function fetchProfessions({ signal } = {}) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/professions`)
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), PROFESSIONS_TIMEOUT_MS)
  const abortOnParent = () => controller.abort()
  if (signal) {
    if (signal.aborted) controller.abort()
    else signal.addEventListener('abort', abortOnParent, { once: true })
  }
  try {
    const res = await fetch(url, { signal: controller.signal })
    return parseEnvelope(res, url, {})
  } catch (err) {
    if (err?.name === 'AbortError') {
      return { ok: false, message: '职业列表加载超时，请确认后端未被长任务占用后刷新' }
    }
    await logApiFailure(url, {}, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  } finally {
    window.clearTimeout(timer)
    if (signal) signal.removeEventListener('abort', abortOnParent)
  }
}

export async function createProfession({ name, description = '', styleHint = '' }) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/professions`)
  const body = { name, description, styleHint }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    return parseEnvelope(res, url, body)
  } catch (err) {
    await logApiFailure(url, body, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}

export async function updateProfession(professionId, { name, description, styleHint }) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/professions/${encodeURIComponent(professionId)}`)
  const body = {}
  if (name !== undefined) body.name = name
  if (description !== undefined) body.description = description
  if (styleHint !== undefined) body.styleHint = styleHint
  try {
    const res = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    return parseEnvelope(res, url, body)
  } catch (err) {
    await logApiFailure(url, body, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}

export async function deleteProfession(professionId) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/professions/${encodeURIComponent(professionId)}`)
  try {
    const res = await fetch(url, { method: 'DELETE' })
    return parseEnvelope(res, url, { professionId })
  } catch (err) {
    await logApiFailure(url, { professionId }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}

export async function fetchCharacterIpWorkbench({ signal } = {}) {
  const url = apiUrl(API.aiShortDramaCharacterIpWorkbench)
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), WORKBENCH_TIMEOUT_MS)
  const abortOnParent = () => controller.abort()
  if (signal) {
    if (signal.aborted) controller.abort()
    else signal.addEventListener('abort', abortOnParent, { once: true })
  }
  try {
    const res = await fetch(url, { signal: controller.signal })
    return parseEnvelope(res, url, {})
  } catch (err) {
    if (err?.name === 'AbortError') {
      return { ok: false, message: '角色库加载超时，已显示职业列表' }
    }
    await logApiFailure(url, {}, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  } finally {
    window.clearTimeout(timer)
    if (signal) signal.removeEventListener('abort', abortOnParent)
  }
}

export async function uploadCharacterIpBase(file, role) {
  const url = apiUrl(API.aiShortDramaCharacterIpUpload)
  const form = new FormData()
  form.append('file', file)
  form.append('role', role)
  try {
    const res = await fetch(url, { method: 'POST', body: form })
    return parseEnvelope(res, url, { role })
  } catch (err) {
    await logApiFailure(url, { role }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}

export async function aiGenerateCharacterIpCandidates(role, description = '') {
  const url = apiUrl(API.aiShortDramaCharacterIpAiGenerate)
  const form = new FormData()
  form.append('role', role)
  const desc = String(description || '').trim()
  if (desc) form.append('description', desc)
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), AI_GENERATE_TIMEOUT_MS)
  try {
    const res = await fetch(url, { method: 'POST', body: form, signal: controller.signal })
    return parseEnvelope(res, url, { role, description: desc })
  } catch (err) {
    if (err?.name === 'AbortError') {
      return { ok: false, message: 'AI 角色生成超时，请稍后重试' }
    }
    await logApiFailure(url, { role }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  } finally {
    window.clearTimeout(timer)
  }
}

export async function activateCharacterIp(ipId) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/${encodeURIComponent(ipId)}/activate`)
  try {
    const res = await fetch(url, { method: 'POST' })
    return parseEnvelope(res, url, { ipId })
  } catch (err) {
    await logApiFailure(url, { ipId }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}

export async function deleteCharacterIp(ipId) {
  const url = apiUrl(`${API.aiShortDramaCharacterIp}/${encodeURIComponent(ipId)}`)
  try {
    const res = await fetch(url, { method: 'DELETE' })
    return parseEnvelope(res, url, { ipId })
  } catch (err) {
    await logApiFailure(url, { ipId }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE }
  }
}
