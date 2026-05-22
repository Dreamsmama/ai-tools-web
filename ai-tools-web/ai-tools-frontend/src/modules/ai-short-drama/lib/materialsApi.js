import { API, apiUrl, logApiFailure } from '../../../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../../../clientErrors.js'

async function parseEnvelope(res, url, requestBody) {
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
  if (!payload || payload.code !== 0) {
    return {
      ok: false,
      message: payload?.message || '操作失败，请稍后再试。',
      kind: payload?.code != null ? `business_${payload.code}` : 'business_error',
    }
  }
  return { ok: true, data: payload.data }
}

/**
 * @param {File} file
 */
export async function uploadMaterialFile(file) {
  const url = apiUrl(API.aiShortDramaMaterialUpload)
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch(url, { method: 'POST', body: form })
    return parseEnvelope(res, url, { filename: file.name })
  } catch (err) {
    await logApiFailure(url, { filename: file.name }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

/**
 * @param {object} material
 */
export async function createMaterialRecord(material) {
  const url = apiUrl(API.aiShortDramaMaterials)
  const requestBody = {
    id: material.id,
    name: material.name,
    type: material.type,
    role: material.role,
    emotion: material.emotion,
    scene: material.scene,
    url: material.url,
    tags: material.tags,
  }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })
    return parseEnvelope(res, url, requestBody)
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

/** 将 uploads/short-drama 磁盘图片同步进素材库 */
export async function syncMaterialsFromDisk() {
  const url = apiUrl(`${API.aiShortDramaMaterials}/sync-from-disk`)
  try {
    const res = await fetch(url, { method: 'POST' })
    return parseEnvelope(res, url, {})
  } catch (err) {
    await logApiFailure(url, {}, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

/**
 * @param {{ type?: string, role?: string, emotion?: string, tag?: string }} filters
 */
export async function fetchMaterials(filters = {}) {
  const params = new URLSearchParams()
  if (filters.type) params.set('type', filters.type)
  if (filters.role) params.set('role', filters.role)
  if (filters.emotion) params.set('emotion', filters.emotion)
  if (filters.tag) params.set('tag', filters.tag)
  if (filters.aiGenerated === true || filters.aiGenerated === 'true') {
    params.set('ai_generated', 'true')
  } else if (filters.aiGenerated === false || filters.aiGenerated === 'false') {
    params.set('ai_generated', 'false')
  }
  const qs = params.toString()
  const url = apiUrl(`${API.aiShortDramaMaterials}${qs ? `?${qs}` : ''}`)
  try {
    const res = await fetch(url)
    const parsed = await parseEnvelope(res, url, filters)
    if (!parsed.ok) return parsed
    return { ok: true, data: parsed.data?.items || [] }
  } catch (err) {
    await logApiFailure(url, filters, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

/**
 * @param {File} file
 * @param {{ role: string, name?: string }} options
 */
export async function aiTagAndSaveMaterial(file, { role, name = '' }) {
  const url = apiUrl(API.aiShortDramaMaterialAiTag)
  const form = new FormData()
  form.append('file', file)
  form.append('role', role)
  if (name) form.append('name', name)
  try {
    const res = await fetch(url, { method: 'POST', body: form })
    return parseEnvelope(res, url, { role, name, filename: file.name })
  } catch (err) {
    await logApiFailure(url, { role, name }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

export async function deleteMaterial(id) {
  const url = apiUrl(`${API.aiShortDramaMaterials}/${encodeURIComponent(id)}`)
  try {
    const res = await fetch(url, { method: 'DELETE' })
    return parseEnvelope(res, url, { id })
  } catch (err) {
    await logApiFailure(url, { id }, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}
