import { API, apiUrl, logApiFailure } from '../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'
import { buildCreateRoutePayload } from '../data/lifeRpgOptions.js'

async function postJson(url, requestBody) {
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

    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      return { ok: false, message: RESPONSE_PARSE_ERROR, kind: 'response_parse_error' }
    }

    if (!payload || payload.code !== 0 || !payload.data) {
      return {
        ok: false,
        message: payload?.message || '请求失败，请稍后再试。',
        kind: payload?.code != null ? `business_${payload.code}` : 'business_error',
      }
    }

    return { ok: true, data: payload.data }
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}

/**
 * 创建人生路线
 * @param {object} form
 */
export async function requestLifeRpgCreateRoute(form) {
  const url = apiUrl(API.lifeRpgCreateRoute)
  return postJson(url, buildCreateRoutePayload(form))
}

/**
 * 生成今日副本
 * @param {object} payload
 */
export async function requestLifeRpgDaily(payload) {
  const url = apiUrl(API.lifeRpgDaily)
  return postJson(url, payload)
}
