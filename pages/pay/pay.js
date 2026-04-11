/*
Page({
  onFakeUnlock() {
    // ✅ 假解锁：给一个“解锁标记”，让你能继续用
    wx.setStorageSync("consult_unlocked", true);

    wx.showToast({ title: "已解锁（体验）", icon: "none" });

    // 返回上一页继续生成
    setTimeout(() => {
      wx.navigateBack();
    }, 600);
  }
});
*/

Page({
  async onPay() {
    wx.showLoading({ title: "发起支付…" });
    try {
      const res = await wx.cloud.callFunction({
        name: "createPayOrder",
        data: { sku: "consult_once", priceFen: 990 }
      });

      const payload = res?.result;
      if (!payload || payload.code !== 0) {
        throw new Error(payload?.message || "支付暂不可用");
      }

      // 真支付时会走这里：wx.requestPayment(payload.payment)
      // 现在先不走
    } catch (e) {
      wx.showToast({ title: e.message || "支付暂不可用", icon: "none" });
    } finally {
      wx.hideLoading();
    }
  },

  onFakeUnlock() {
    wx.setStorageSync("consult_unlocked", true);
    wx.showToast({ title: "已解锁（体验）", icon: "none" });
    setTimeout(() => wx.navigateBack(), 600);
  }
});



