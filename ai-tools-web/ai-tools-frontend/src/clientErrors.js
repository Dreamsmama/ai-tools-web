/** 前端本地能判断的错误；优先鼓励「直接再点一次」，与后端话术一致 */

const RETRY_HINT =
  '无需改内容，直接再点一次提交试试，通常 1～2 次就会好。'

export function httpErrorMessage(status) {
  return (
    `暂时无法完成请求（HTTP ${status}）。\n` +
    `${RETRY_HINT}\n` +
    `若刷新页面后仍反复出现，再联系管理员检查服务。`
  )
}

export const RESPONSE_PARSE_ERROR = `未收到正常数据，可能是网关或页面地址问题。\n${RETRY_HINT}\n若仍不行，请确认网址与 /api 配置是否正确。`

export const NETWORK_UNREACHABLE = `当前请求没连上服务器，请先检查手机/电脑网络是否正常。\n网络恢复后，直接再点一次提交即可。`
