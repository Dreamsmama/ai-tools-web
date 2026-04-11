/**
 * 开发环境：Vite proxy 把 /summary、/prepare-consult 转到后端，使用相对路径即可。
 * 生产环境：构建前设置 VITE_API_BASE（如 https://api.example.com，无末尾斜杠），
 * 请求会发往 `${VITE_API_BASE}/summary` 等。
 */
export function apiUrl(path) {
  const p = path.startsWith('/') ? path : `/${path}`
  const raw = import.meta.env.VITE_API_BASE
  if (raw == null || String(raw).trim() === '') {
    return p
  }
  const base = String(raw).replace(/\/$/, '')
  return `${base}${p}`
}
