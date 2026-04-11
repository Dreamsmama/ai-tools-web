const { trackEvent } = require('../../utils/track');

Page({
  onShow() {
    // 首页显示埋点
    trackEvent('home_view');
  },

  goStart() {
    // 就医助手入口埋点
    trackEvent('medical_entry');
    wx.navigateTo({ url: '/pages/form/form' });
  },

  goSummary() {
    // 聊天总结入口埋点
    trackEvent('summary_entry');
    wx.navigateTo({
      url: '/pages/summary/summary',
      fail: (err) => { console.log('跳转失败', err) }
    });
  }
});
