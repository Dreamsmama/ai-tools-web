import { API, apiUrl, logApiFailure } from '../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'

/**
 * @param {object} form
 * @returns {Promise<{ ok: true, data: object } | { ok: false, message: string, kind: string }>}
 */
export async function requestInterestExplorer(form) {
  const url = apiUrl(API.interestExplorer)
  const requestBody = {
    life_stage: form.life_stage,
    work_state: form.work_state,
    social_style: form.social_style,
    preferences: form.preferences,
    budget: form.budget,
    weekend_state: form.weekend_state,
    goals: form.goals,
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
        message: payload?.message || '推荐失败，请稍后再试。',
        kind: payload?.code != null ? `business_${payload.code}` : 'business_error',
      }
    }

    return { ok: true, data: payload.data }
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    return { ok: false, message: NETWORK_UNREACHABLE, kind: 'network_error' }
  }
}
