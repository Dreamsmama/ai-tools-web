/** 金融从业者的一天（职场人 · 职业体验馆） */
export const financePractitionerDayConfig = {
  id: 'finance-practitioner',
  title: '金融从业者的一天',
  subtitle: '研报、路演与风控——从业者的信息密度，比课本更高。',
  startCta: '开始上班',
  endingHeadline: '你的金融从业者一天结束了',
  defaultAtmosphere: 'dev-alert-desk',
  initialStats: { stress: 45, reputation: 50, growth: 28, mood: 48 },
  scenes: [
    {
      id: 'scene_1',
      time: '08:30',
      sceneTitle: '晨会冲突',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '晨会', text: '领导：某行业评级下调，持仓客户会问。谁负责更新观点？', tone: 'alert', moment: 'feishu-dot' },
        { role: 'system', source: '同事', text: '昨晚模型跑完了，但数据和公开口径不一致，你要不要先核对？' },
      ],
      options: [
        { text: '先核对数据源，再写一页更新摘要', nextSceneId: 'scene_2', effects: { stress: 10, reputation: 14, growth: 12, mood: -6 } },
        { text: '先用昨晚结论开会，会后再改', nextSceneId: 'scene_2', effects: { stress: 8, reputation: 4, growth: 4, mood: -4 } },
        { text: '请数据同事一起进会议室', nextSceneId: 'scene_2', effects: { stress: 6, reputation: 10, growth: 10, mood: -2 } },
      ],
    },
    {
      id: 'scene_2',
      time: '13:00',
      sceneTitle: '路演提问',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '客户', text: '你们报告说景气度回升，但库存数据还在恶化。你们到底信哪个？' },
        { role: 'system', source: '合规', text: '（私信）回答避免承诺收益，引用公开信息来源。' },
      ],
      options: [
        { text: '分情景说明乐观/悲观两种路径', nextSceneId: 'scene_3', effects: { stress: 8, reputation: 12, growth: 14, mood: -4 } },
        { text: '坚持原报告结论，强调长期逻辑', nextSceneId: 'scene_3', effects: { stress: 6, reputation: 6, growth: 8, mood: -2 } },
        { text: '承认短期不确定，建议客户降低敞口', nextSceneId: 'scene_3', effects: { stress: 4, reputation: 10, growth: 10, mood: 0 } },
      ],
    },
    {
      id: 'scene_3',
      time: '16:45',
      sceneTitle: '风控预警',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '风控系统', text: '组合波动触发预警，需提交归因与是否调仓说明。', moment: 'ticket-red' },
        { role: 'system', source: '投资经理', text: '今晚前给我结论：减仓还是对冲？' },
      ],
      options: [
        { text: '建议先对冲，保留核心仓位', nextSceneId: 'scene_4', effects: { stress: 12, reputation: 12, growth: 10, mood: -8 } },
        { text: '建议小幅减仓，观察一周', nextSceneId: 'scene_4', effects: { stress: 8, reputation: 8, growth: 8, mood: -6 } },
        { text: '坚持不改，写长说明备查', nextSceneId: 'scene_4', effects: { stress: 6, reputation: 2, growth: 6, mood: -4 } },
      ],
    },
    {
      id: 'scene_4',
      time: '23:20',
      sceneTitle: '研报截止',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '编辑器', text: '深度报告还差行业比较章节，明早 8 点交易所披露。' },
        { role: 'system', source: '室友', text: '你还考 CFA 吗？别把自己卷没了。' },
      ],
      options: [
        { text: '熬夜补完，质量自己把关', nextSceneId: '__end__', effects: { stress: 18, reputation: 8, growth: 8, mood: -14 } },
        { text: '先交核心章节，比较部分上午补', nextSceneId: '__end__', effects: { stress: 10, reputation: 10, growth: 10, mood: -8 } },
        { text: '申请推迟发布（需领导批准）', nextSceneId: '__end__', effects: { stress: 4, reputation: -4, growth: 4, mood: 2 } },
      ],
    },
  ],
  endings: [
    {
      id: 'research',
      label: '研究驱动型金融人',
      punchline: '你愿意为结论负责，也敢在客户面前留余地。',
      summary: '金融从业适合数理与沟通兼备、能承受节奏的人。工具会加速分析，判断仍在你。',
      fitReason: '证据与表达较平衡。',
      riskReason: '注意合规边界与作息，行业节奏容易过载。',
      match: (s) => s.growth >= 52,
    },
    {
      id: 'steady',
      label: '稳健风控型金融人',
      punchline: '你知道什么时候该把风险写进报告里。',
      summary: '你倾向先讲不确定，再讲机会——这在风控与研究岗都是加分项。',
      fitReason: '谨慎与合规意识强。',
      riskReason: '可适度锻炼路演与决策速度。',
      match: () => true,
    },
  ],
}
