const { trackEvent } = require('../../utils/track');

Page({
  data: {
    inputText: '',
    result: null,
    showUnlockModal: false // 解锁弹窗显示状态
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value })
  },

  // 获取使用次数
  getSummaryCount() {
    return wx.getStorageSync('summary_used_count') || 0
  },

  // 增加使用次数
  incrementSummaryCount() {
    const count = this.getSummaryCount()
    wx.setStorageSync('summary_used_count', count + 1)
  },

  // 检查是否需要显示解锁提示
  checkUnlock() {
    const count = this.getSummaryCount()
    if (count >= 3) {
      this.setData({ showUnlockModal: true })
      // 解锁弹窗显示埋点
      trackEvent('summary_unlock_show');
      return true // 需要显示弹窗
    }
    return false // 不需要显示弹窗
  },

  // 关闭解锁弹窗
  onCloseUnlockModal() {
    this.setData({ showUnlockModal: false })
  },

  // 点击"解锁更多"
  onUnlockClick() {
    // 解锁点击埋点
    trackEvent('summary_unlock_click');
    // 暂时只记录点击，不做真实支付
    wx.showToast({ 
      title: '功能开发中', 
      icon: 'none' 
    })
    this.setData({ showUnlockModal: false })
  },

  async onSummarize() {
    const text = (this.data.inputText || '').trim()
    if (!text) {
      wx.showToast({ title: '先粘贴聊天内容', icon: 'none' })
      return
    }

    // 检查是否需要显示解锁提示（轻提示，不强制拦截）
    this.checkUnlock()
    // 注意：这里不 return，允许用户继续使用

    wx.showLoading({ title: '总结中...' })

    try {
      const res = await wx.cloud.callFunction({
        name: 'summarize',
        data: { inputText: text }
      })

      const r = res?.result
      if (r?.code !== 0) {
        console.log('summarize fail:', r)
        wx.showToast({ title: r?.message || '生成失败，请重试', icon: 'none' })
        return
      }

      // 成功生成总结后，使用次数 +1
      this.incrementSummaryCount()
      
      this.setData({ result: r.data })
      
      // 聊天总结生成成功埋点
      trackEvent('summary_generate', {
        count: this.getSummaryCount()
      });
    } catch (e) {
      console.log('callFunction error:', e)
      wx.showToast({ title: '网络异常', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  copyReply() {
    if (!this.data.result?.reply) return
    wx.setClipboardData({
      data: this.data.result.reply,
      success: () => wx.showToast({ title: '已复制', icon: 'success' })
    })
  }
})
