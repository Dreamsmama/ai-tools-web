/**
 * cloudfunctions/track/index.js
 * 埋点数据写入云数据库
 */

const cloud = require('wx-server-sdk');

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
});

const db = cloud.database();

exports.main = async (event) => {
  try {
    const { event: eventName, ts, page, anonymousId, params } = event;

    // 参数校验
    if (!eventName || typeof eventName !== 'string') {
      return { ok: false, err: 'event 字段必填且为字符串' };
    }

    // 写入云数据库
    const result = await db.collection('analytics_events').add({
      data: {
        event: eventName,
        ts: ts || Date.now(),
        page: page || '',
        anonymousId: anonymousId || '',
        params: params || {},
        _createTime: new Date()
      }
    });

    return { ok: true, _id: result._id };
  } catch (err) {
    console.error('track error:', err);
    return { 
      ok: false, 
      err: err.message || '写入失败' 
    };
  }
};

