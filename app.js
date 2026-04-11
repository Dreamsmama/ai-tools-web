App({
  onLaunch() {
    if (!wx.cloud) {
      console.error('请使用 2.2.3+ 的基础库以使用云能力');
      return;
    }
    wx.cloud.init({
      env: 'cloud1-6gvw9k2h05ff9651', // 替换为你的云环境 ID；也可不填用默认
      traceUser: true
    });
  }
});
