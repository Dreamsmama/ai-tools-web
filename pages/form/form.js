const { trackEvent } = require('../../utils/track');

Page({
  data: {
    symptom: "",
    report: "",
    target: "",
    loading: false
  },

  onLoad() {
    // 就医助手入口埋点（确保通过 navigator 进入也能记录）
    trackEvent('medical_entry');
  },

  // 输入框绑定
  onSymptomInput(e) {
    this.setData({ symptom: e.detail.value });
  },

  onReportInput(e) {
    this.setData({ report: e.detail.value });
  },

  onTargetInput(e) {
    this.setData({ target: e.detail.value });
  },

  // 点击"生成问诊准备"
  async onGenerate() {
    if (this.data.loading) return;

  // ✅ 解锁后直接放行
  // 【已注释】暂时关闭医生助手的解锁功能
  // const count = wx.getStorageSync("consult_count") || 0;

  // if (count >= 2) {
  //   wx.showModal({
  //     title: "体验次数已用完",
  //     content: "继续使用需要解锁完整功能。",
  //     confirmText: "去解锁",
  //     cancelText: "再想想",
  //     success: (r) => {
  //       if (r.confirm) {
  //         wx.redirectTo({
  //           url: "/pages/pay/pay"
  //         })
  //       }
  //     }
  //   });
  //   return;
  // }



    const symptom = (this.data.symptom || "").trim();
    const report = (this.data.report || "").trim();
    const target = (this.data.target || "").trim();

    // ✅ 最基本校验（防止一句话废输入）
    if (!symptom || symptom.length < 3) {
      wx.showToast({
        title: "请尽量详细描述症状（至少一句话）",
        icon: "none"
      });
      return;
    }

    this.setData({ loading: true });
    wx.showLoading({ title: "生成中…" });

    try {
      const res = await wx.cloud.callFunction({
        name: "prepareConsult",
        data: {
          symptom,
          report,
          target
        }
      });

      console.log("prepareConsult res:", res);

      const payload = res?.result;
      if (!payload || payload.code !== 0) {
        throw new Error(payload?.message || "生成失败");
      }

      // ✅ 关键：存 AI 结果，给 result 页用
      wx.setStorageSync("consult_result", payload.data);

     // ✅ 仅在未解锁状态才计数
     // 【已注释】暂时关闭医生助手的解锁功能
     // const count2 = wx.getStorageSync("consult_count") || 0;
     // wx.setStorageSync("consult_count", count2 + 1);


      // ✅ 跳转结果页
      wx.navigateTo({
        url: "/pages/result/result"
      });
    } catch (err) {
      console.error("generate error:", err);
      wx.showToast({
        title: err.message || "生成失败，请重试",
        icon: "none"
      });
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  onResetTrial() {
    wx.removeStorageSync("consult_count");
    wx.removeStorageSync("consult_unlocked");
    wx.showToast({ title: "已重置", icon: "none" });
  }
});
