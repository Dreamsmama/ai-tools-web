import { API, apiUrl, logApiFailure } from '../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'

/**
 * @typedef {Object} EveningPlanFormPayload
 * @property {string} city
 * @property {string} current_time
 * @property {string} energy_level
 * @property {string} mood
 * @property {string} go_out
 * @property {string} social
 * @property {string} budget
 * @property {string[]} interests
 * @property {string} [extra_notes]
 */

/**
 * @param {EveningPlanFormPayload} form
 * @returns {Promise<{ ok: true, data: object } | { ok: false, message: string, kind: string }>}
 */
export async function requestEveningPlan(form) {
  const url = apiUrl(API.eveningPlan)
  const requestBody = {
    city: form.city,
    current_time: form.current_time,
    energy_level: form.energy_level,
    mood: form.mood,
    go_out: form.go_out,
    social: form.social,
    budget: form.budget,
    interests: form.interests,
    extra_notes: form.extra_notes || '',
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
        message: payload?.message || '安排失败，请稍后再试。',
        kind: payload?.code != null ? `business_${payload.code}` : 'business_error',
      }
    }

    return { ok: true, data: payload.data }
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}
