/** 律师的一天（职场人 · 职业体验馆） */
export const lawyerDayConfig = {
  id: 'lawyer',
  title: '律师的一天',
  subtitle: '案源、出庭与合伙人意见——执业律师的一天，很少只写在日程表里。',
  startCta: '开始上班',
  endingHeadline: '你的律师一天结束了',
  defaultAtmosphere: 'dev-meeting',
  initialStats: { stress: 44, reputation: 52, growth: 28, mood: 48 },
  scenes: [
    {
      id: 'scene_1',
      time: '09:20',
      sceneTitle: '客户催进度',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '客户微信', text: '王律师，对方律师函来了，说我们不撤诉就反诉。今天能给策略吗？', tone: 'private', moment: 'feishu-dot' },
        { role: 'system', source: '合伙人', text: '这个客户今年续费关键。你中午前给我一页纸：风险、成本、建议路径。' },
      ],
      options: [
        { text: '先开会所案例库，再给客户电话', nextSceneId: 'scene_2', effects: { stress: 10, reputation: 12, growth: 10, mood: -6 } },
        { text: '先回客户稳住情绪，策略下午再给', nextSceneId: 'scene_2', effects: { stress: 8, reputation: 8, growth: 6, mood: -4 } },
        { text: '建议客户先公证现有证据', nextSceneId: 'scene_2', effects: { stress: 6, reputation: 10, growth: 12, mood: -2 } },
      ],
    },
    {
      id: 'scene_2',
      time: '14:00',
      sceneTitle: '开庭前改口径',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '助理', text: '法官助理来电：对方提交了补充证据，建议你们庭前先看。距开庭还有 40 分钟。' },
        { role: 'system', source: '对方律师', text: '（邮件）我方坚持合同解除权成立，附件为补充说明。' },
      ],
      options: [
        { text: '快速改答辩要点，放弃部分非核心主张', nextSceneId: 'scene_3', effects: { stress: 14, reputation: 10, growth: 8, mood: -10 } },
        { text: '申请延期质证（可能被驳回）', nextSceneId: 'scene_3', effects: { stress: 6, reputation: -4, growth: 4, mood: -4 } },
        { text: '按原方案开庭，庭后补充书面意见', nextSceneId: 'scene_3', effects: { stress: 10, reputation: 6, growth: 10, mood: -8 } },
      ],
    },
    {
      id: 'scene_3',
      time: '16:30',
      sceneTitle: '庭后复盘',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '合伙人', text: '客户对庭审表现满意，但问费用能不能分期。你怎么谈？' },
        { role: 'system', source: '财务', text: '该客户尚有上期账单未结清，系统已标黄。' },
      ],
      options: [
        { text: '提出分期但提高首期比例', nextSceneId: 'scene_4', effects: { stress: 8, reputation: 12, growth: 10, mood: -4 } },
        { text: '坚持先结清旧账再谈新案', nextSceneId: 'scene_4', effects: { stress: 4, reputation: 6, growth: 8, mood: 0 } },
        { text: '请合伙人出面谈商务条款', nextSceneId: 'scene_4', effects: { stress: 2, reputation: 4, growth: 6, mood: 4 } },
      ],
    },
    {
      id: 'scene_4',
      time: '22:00',
      sceneTitle: '案卷与案源',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '老同学', text: '有个劳动纠纷想咨询，能不能先帮看看？' },
        { role: 'system', source: '自己', text: '明天还要写代理词，本月案源指标还差一格。' },
      ],
      options: [
        { text: '接咨询，当作潜在案源', nextSceneId: '__end__', effects: { stress: 12, reputation: 8, growth: 10, mood: -10 } },
        { text: '推荐所里专门做劳动的同事', nextSceneId: '__end__', effects: { stress: 4, reputation: 10, growth: 8, mood: 2 } },
        { text: '今晚只写完代理词，咨询改周末', nextSceneId: '__end__', effects: { stress: 8, reputation: 4, growth: 6, mood: 4 } },
      ],
    },
  ],
  endings: [
    {
      id: 'partner_track',
      label: '诉讼合伙人型律师',
      punchline: '你能扛庭审，也能扛客户的情绪。',
      summary: '律师职业适合逻辑强、表达稳、对结果负责的人。案源与商务永远和专业并行。',
      fitReason: '压力下仍能抓住争议焦点。',
      riskReason: '注意收费边界与精力分配，避免「什么都接」。',
      match: (s) => s.reputation >= 55,
    },
    {
      id: 'steady',
      label: '稳健执业型律师',
      punchline: '你知道法律工作一半是沟通，一半是文书。',
      summary: '你倾向于留痕、讲清风险，这在长期执业里比「赢一次」更重要。',
      fitReason: '风险意识与沟通平衡较好。',
      riskReason: '可适当争取出庭与谈判机会，避免只做幕后。',
      match: () => true,
    },
  ],
}
