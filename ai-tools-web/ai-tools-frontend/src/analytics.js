import { API, apiUrl } from './api'

const PAGE_VIEW_COOLDOWN_MS = 30 * 1000
const lastPageViewByPath = new Map()

function nowMs() {
  return Date.now()
}

function buildEventId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `evt_${nowMs()}_${Math.random().toString(16).slice(2)}`
}

function postEvent(payload) {
  const url = apiUrl(API.trackEvents)
  const body = JSON.stringify({
    ...payload,
    ts: nowMs(),
  })
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    keepalive: true,
  }).catch(() => {})
}

export function trackPageView(path) {
  const normalized = (path || '').trim() || '/'
  const now = nowMs()
  const prev = lastPageViewByPath.get(normalized) || 0
  if (now - prev < PAGE_VIEW_COOLDOWN_MS) return
  lastPageViewByPath.set(normalized, now)
  postEvent({
    event: 'page_view',
    feature: 'global',
    page: normalized,
    event_id: buildEventId(),
  })
}

export function trackSubmit(feature, page, isRetry = false) {
  const eventId = buildEventId()
  postEvent({
    event: 'submit_click',
    feature,
    page,
    event_id: eventId,
    is_retry: isRetry,
  })
  return eventId
}

export function trackApiSuccess(feature, page, eventId, durationMs) {
  postEvent({
    event: 'api_success',
    feature,
    page,
    event_id: eventId || buildEventId(),
    status: 'success',
    duration_ms: Math.max(0, Number(durationMs) || 0),
  })
}

export function trackApiFail(feature, page, eventId, errorCode, durationMs, isRetry = false) {
  postEvent({
    event: 'api_fail',
    feature,
    page,
    event_id: eventId || buildEventId(),
    status: 'fail',
    error_code: String(errorCode || 'unknown').slice(0, 64),
    duration_ms: Math.max(0, Number(durationMs) || 0),
    is_retry: isRetry,
  })
}

export function setupRouteAnalytics(router) {
  trackPageView(router.currentRoute?.value?.path || '/')
  router.afterEach((to) => {
    trackPageView(to.path || '/')
  })
}
