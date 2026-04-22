/**
 * 线上：请求须走 /api/...，与 Nginx 的 location /api/ 一致。
 * 开发：Vite proxy 将路径改写到后端真实路由（见 vite.config.js）。
 *
 * Nginx 若使用 `location /api/ { proxy_pass http://127.0.0.1:8000/; }`，则
 * /api/summary → 后端 /summary。
 * /api/medical-assistant 需单独 rewrite 到 /prepare-consult（后端路径名不同），
 * 例如：`location = /api/medical-assistant { proxy_pass http://127.0.0.1:8000/prepare-consult; }`
 *
 * 可选 VITE_API_BASE：如 https://yourdomain.com（无末尾斜杠），最终为 `${VITE_API_BASE}/api/summary`。
 */

/** 与线上一致的对外路径（由 Nginx 转发到后端 /summary、/prepare-consult 等） */
export const API = {
  summary: '/api/summary',
  medicalAssistant: '/api/medical-assistant',
  health: '/api/health',
  trackEvents: '/api/track/events',
  trackStats: '/api/track/stats',
  ragKbs: '/api/rag/kbs',
  ragUpload: '/api/rag/documents/upload',
  ragIngest: (documentId) => `/api/rag/documents/${documentId}/ingest`,
  ragAsk: '/api/rag/ask',
}

export function apiUrl(path) {
  const p = path.startsWith('/') ? path : `/${path}`
  const raw = import.meta.env.VITE_API_BASE
  if (raw == null || String(raw).trim() === '') {
    return p
  }
  const base = String(raw).replace(/\/$/, '')
  return `${base}${p}`
}

/**
 * 请求失败时打印，便于线上排查（不改变用户可见提示文案）。
 */
export async function logApiFailure(url, requestBody, res, err) {
  let responseSnippet = null
  if (res) {
    try {
      responseSnippet = (await res.clone().text()).slice(0, 2000)
    } catch (e) {
      responseSnippet = String(e)
    }
  }
  console.error('[ai-tools-api]', {
    url,
    requestBody,
    status: res != null ? res.status : undefined,
    responseSnippet,
    error: err,
  })
}
