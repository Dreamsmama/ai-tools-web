/** 学法学以后的一天（高考生 · 未来职业体验） */
export const lawStudentDayConfig = {
  id: 'major-law',
  title: '学法学以后的一天',
  subtitle: '材料、庭审与客户沟通——法律人的一天，往往从「有人找你」开始。',
  startCta: '开始体验',
  endingHeadline: '今日体验结束',
  defaultAtmosphere: 'dev-meeting',
  initialStats: { stress: 40, reputation: 50, growth: 24, mood: 52 },
  scenes: [
    {
      id: 'scene_1',
      time: '08:40',
      sceneTitle: '当事人发来长语音',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '当事人微信', text: '律师，我那个合同纠纷，对方昨天又改口了。我语音里都说清楚了，您听听。', tone: 'private', moment: 'voice-message' },
        { role: 'system', source: '带教律师', text: '上午十点前要出一份情况说明，客户下午要用。你先理一版。' },
      ],
      options: [
        { text: '先听语音逐条记录，再查合同原件', nextSceneId: 'scene_2', effects: { stress: 8, reputation: 10, growth: 12, mood: -4 } },
        { text: '先按带教律师要的格式出框架，再补细节', nextSceneId: 'scene_2', effects: { stress: 12, reputation: 6, growth: 8, mood: -6 } },
        { text: '请当事人把关键事实文字整理后发你', nextSceneId: 'scene_2', effects: { stress: 4, reputation: 4, growth: 10, mood: 2 } },
      ],
    },
    {
      id: 'scene_2',
      time: '11:20',
      sceneTitle: '证据链缺一页',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '档案系统', text: '扫描件里缺少签字页，对方律师可能会质疑证据效力。' },
        { role: 'system', source: '带教律师', text: '下午庭前会议，别在证据上翻车。你现在能补到吗？' },
      ],
      options: [
        { text: '联系客户补扫，同时准备说明', nextSceneId: 'scene_3', effects: { stress: 10, reputation: 12, growth: 10, mood: -8 } },
        { text: '先标注缺口，会上主动说明', nextSceneId: 'scene_3', effects: { stress: 6, reputation: 8, growth: 12, mood: -4 } },
        { text: '建议延期庭前会议（可能被否决）', nextSceneId: 'scene_3', effects: { stress: 2, reputation: -6, growth: 4, mood: 0 } },
      ],
    },
    {
      id: 'scene_3',
      time: '15:05',
      sceneTitle: '庭前会议',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '会议室', text: '对方律师质疑你方证据时间线。带教律师看向你，等你补充说明。' },
        { role: 'system', source: '法官书记员', text: '双方注意：调解窗口很短，请明确争议焦点。' },
      ],
      options: [
        { text: '用时间线图表回应，并承认一处瑕疵', nextSceneId: 'scene_4', effects: { stress: 8, reputation: 14, growth: 12, mood: -6 } },
        { text: '坚持己方解释，引用法条与判例', nextSceneId: 'scene_4', effects: { stress: 12, reputation: 6, growth: 10, mood: -10 } },
        { text: '建议先交换补充材料，再谈调解', nextSceneId: 'scene_4', effects: { stress: 6, reputation: 8, growth: 8, mood: -4 } },
      ],
    },
    {
      id: 'scene_4',
      time: '21:30',
      sceneTitle: '自习室关灯前',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '同学微信', text: '法考复习群：今晚还有人刷题吗？我民法还差一章。' },
        { role: 'system', source: '带教律师', text: '材料改得可以。明天把客户沟通纪要也补上，别只靠口头。' },
      ],
      options: [
        { text: '再留一小时补纪要，法考只能周末', nextSceneId: '__end__', effects: { stress: 14, reputation: 10, growth: 8, mood: -12 } },
        { text: '纪要先列要点，平衡法考复习', nextSceneId: '__end__', effects: { stress: 6, reputation: 6, growth: 10, mood: 4 } },
        { text: '今天先休息，明天早起处理', nextSceneId: '__end__', effects: { stress: -6, reputation: -4, growth: 4, mood: 10 } },
      ],
    },
  ],
  endings: [
    {
      id: 'litigation',
      label: '诉讼型法律人',
      punchline: '你喜欢把事实讲清楚，也愿意在压力下开口。',
      summary: '法学很适合需要逻辑、表达与责任感的你。未来无论是律师、法务还是公职，都要习惯「材料不会说谎，但人会」。',
      fitReason: '你能扛住细节，也愿意为结论负责。',
      riskReason: '长期高压下要注意情绪与作息，避免把自己耗成「只会加班」。',
      match: (s) => s.reputation >= 58 && s.growth >= 50,
    },
    {
      id: 'steady',
      label: '稳健法务型',
      punchline: '你更擅长把风险关在流程里。',
      summary: '你倾向于先补证据、留痕、再表态——这在企业法务与合规方向是加分项。',
      fitReason: '谨慎与留痕意识，能降低团队翻车概率。',
      riskReason: '有时过于求稳，可能错过调解或和解的窗口。',
      match: () => true,
    },
  ],
}
