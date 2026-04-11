const { trackEvent } = require('../../utils/track');

Page({
  data: {
    summary: [],
    questions: [],
    notes: []
  },

  onLoad() {
    const data = wx.getStorageSync("consult_result");
    console.log("consult_result raw:", data);

    const summary = Array.isArray(data?.summary) ? data.summary : [];
    const questions = Array.isArray(data?.questions) ? data.questions : [];
    const notes = Array.isArray(data?.notes) ? data.notes : [];

    console.log("len:", summary.length, questions.length, notes.length);

    this.setData({ summary, questions, notes });
    
    // 就医整理完成埋点
    trackEvent('medical_complete');
  }
});
