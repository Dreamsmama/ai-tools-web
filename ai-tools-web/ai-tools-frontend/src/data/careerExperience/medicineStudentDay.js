/** 学医学以后的一天（高考生 · 未来职业体验） */
export const medicineStudentDayConfig = {
  id: 'major-medicine',
  title: '学医学以后的一天',
  subtitle: '查房、病历与突发状况——长学制里很普通的一天，也可能很漫长。',
  startCta: '开始体验',
  endingHeadline: '今日体验结束',
  defaultAtmosphere: 'dev-alert-desk',
  initialStats: { stress: 44, reputation: 52, growth: 28, mood: 48 },
  scenes: [
    {
      id: 'scene_1',
      time: '07:15',
      sceneTitle: '查房前的夜班交接',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '夜班同学', text: '12 床夜间血压波动，已处理。新入院 15 床胸痛待查，主任八点要看初评。', tone: 'alert', moment: 'ticket-red' },
        { role: 'system', source: '带教医师', text: '你跟查房，病历昨晚谁写的？检验结果核对了吗？' },
      ],
      options: [
        { text: '先核对检验与用药，再进病房', nextSceneId: 'scene_2', effects: { stress: 10, reputation: 12, growth: 12, mood: -6 } },
        { text: '先跟夜班交接清楚，再写查房笔记', nextSceneId: 'scene_2', effects: { stress: 8, reputation: 10, growth: 10, mood: -4 } },
        { text: '直接进病房问病史（可能被带教叫停）', nextSceneId: 'scene_2', effects: { stress: 14, reputation: -4, growth: 6, mood: -10 } },
      ],
    },
    {
      id: 'scene_2',
      time: '10:30',
      sceneTitle: '病历被退回',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '病历系统', text: '退回原因：主诉与现病史时间线不一致；缺少关键阴性体征记录。' },
        { role: 'system', source: '带教医师', text: '下午教学查房你要汇报 15 床，中午前改完。' },
      ],
      options: [
        { text: '回病房补问病史，按模板重写', nextSceneId: 'scene_3', effects: { stress: 12, reputation: 14, growth: 12, mood: -10 } },
        { text: '请夜班同学一起核对时间线', nextSceneId: 'scene_3', effects: { stress: 8, reputation: 10, growth: 10, mood: -6 } },
        { text: '先改能改的，细节下午再补', nextSceneId: 'scene_3', effects: { stress: 6, reputation: 4, growth: 6, mood: -4 } },
      ],
    },
    {
      id: 'scene_3',
      time: '14:50',
      sceneTitle: '教学查房提问',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '主任', text: '这个胸痛病人，你现在最担心的并发症是什么？依据是什么？' },
        { role: 'system', source: '同学群', text: '（小声）昨天那套题考的就是这个……' },
      ],
      options: [
        { text: '按证据链回答，并承认不确定处', nextSceneId: 'scene_4', effects: { stress: 10, reputation: 14, growth: 14, mood: -8 } },
        { text: '背标准答案，尽量流畅', nextSceneId: 'scene_4', effects: { stress: 8, reputation: 6, growth: 8, mood: -6 } },
        { text: '说需要再查文献，会后整理', nextSceneId: 'scene_4', effects: { stress: 4, reputation: 8, growth: 10, mood: -2 } },
      ],
    },
    {
      id: 'scene_4',
      time: '23:00',
      sceneTitle: '宿舍台灯还亮着',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '家人', text: '这周能回家吗？你爸说别总熬夜。', tone: 'life', moment: 'phone-vibrate' },
        { role: 'system', source: '自己', text: '执业考试大纲还有两章。明天六点又要跟晨间查房。' },
      ],
      options: [
        { text: '再刷一章，周末不回家', nextSceneId: '__end__', effects: { stress: 18, reputation: 8, growth: 12, mood: -16 } },
        { text: '定闹钟早起，今晚先睡', nextSceneId: '__end__', effects: { stress: 4, reputation: 6, growth: 8, mood: 8 } },
        { text: '给家里人回语音，说明学制与节奏', nextSceneId: '__end__', effects: { stress: 6, reputation: 4, growth: 6, mood: 4 } },
      ],
    },
  ],
  endings: [
    {
      id: 'clinician',
      label: '临床型医学人',
      punchline: '你能扛住细节，也愿意为病人多留一分钟。',
      summary: '医学适合责任心强、能长期学习、沟通也不差的人。AI 可辅助检索，但 bedside 的判断与伦理无法外包。',
      fitReason: '严谨与责任感突出。',
      riskReason: '注意长期作息与情绪支持，别把「能熬」当成唯一优势。',
      match: (s) => s.reputation >= 55 && s.growth >= 52,
    },
    {
      id: 'steady_med',
      label: '稳健成长型',
      punchline: '你知道医学是马拉松，不是冲刺赛。',
      summary: '你倾向于把能做的事做扎实，这在医学路径里比「看起来很忙」更重要。',
      fitReason: '稳扎稳打，利于长学制积累。',
      riskReason: '有时需主动争取操作与汇报机会，避免只会跟跑。',
      match: () => true,
    },
  ],
}
