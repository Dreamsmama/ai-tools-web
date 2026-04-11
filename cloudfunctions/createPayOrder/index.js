exports.main = async (event, context) => {
  // 这里以后会用 openid + 微信支付下单
  // 现在先返回“未开通”的提示
  return {
    code: 501,
    message: "微信支付尚未开通（等待商户号/审核/证书）"
  };
};
