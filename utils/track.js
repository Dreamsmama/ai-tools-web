// utils/track.js
/**
 * 统一埋点工具
 * 同时上报 wx.reportAnalytics 和云数据库
 */

// 生成或获取匿名用户 ID
function getAnonymousId() {
  let id = wx.getStorageSync('anonymousId');
  if (!id) {
    // 简单方法生成 uuid：时间戳 + 随机数
    id = `anon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    wx.setStorageSync('anonymousId', id);
  }
  return id;
}

// 获取当前页面路径
function getCurrentPage() {
  const pages = getCurrentPages();
  if (pages.length === 0) return '';
  const currentPage = pages[pages.length - 1];
  return currentPage.route || '';
}

/**
 * 埋点函数
 * @param {string} eventName - 事件名（小写下划线格式）
 * @param {object} params - 可选额外参数
 */
function trackEvent(eventName, params = {}) {
  // 确保事件名是小写下划线格式
  const normalizedEvent = String(eventName).toLowerCase().replace(/[^a-z0-9_]/g, '_');
  
  const payload = {
    event: normalizedEvent,
    ts: Date.now(),
    page: getCurrentPage(),
    anonymousId: getAnonymousId(),
    params: params || {}
  };

  // 1. console.log
  console.log('[track]', normalizedEvent, payload);

  // 2. wx.reportAnalytics（如果可用，不阻塞）
  try {
    if (wx.reportAnalytics) {
      wx.reportAnalytics(normalizedEvent, payload.params);
    }
  } catch (e) {
    console.warn('[track] wx.reportAnalytics failed:', e);
  }

  // 3. 写入云数据库（异步，不阻塞）
  wx.cloud.callFunction({
    name: 'track',
    data: payload
  }).catch(err => {
    console.warn('[track] cloud callFunction failed:', err);
  });
}

module.exports = {
  trackEvent
};

