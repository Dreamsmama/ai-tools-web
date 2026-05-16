/** 学金融以后的一天（高考生 · 未来职业体验） */
export const financeStudentDayConfig = {
  id: 'major-finance',
  title: '学金融以后的一天',
  subtitle: '数据、风控与决策会——信息密度很高，容错率很低。',
  startCta: '开始体验',
  endingHeadline: '今日体验结束',
  defaultAtmosphere: 'dev-alert-desk',
  initialStats: { stress: 42, reputation: 48, growth: 26, mood: 50 },
  scenes: [
    {
      id: 'scene_1',
      time: '09:00',
      sceneTitle: '晨会前的数据',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '交易群', text: '某板块早盘波动异常，风控群已标黄。实习生先看一眼持仓暴露。', tone: 'alert', moment: 'feishu-dot' },
        { role: 'system', source: '带教', text: '十点前有晨会材料，把异常原因写成三条，别只贴截图。' },
      ],
      options: [
        { text: '先拉数据核对，再写原因假设', nextSceneId: 'scene_2', effects: { stress: 10, reputation: 12, growth: 12, mood: -6 } },
        { text: '先问带教要口径，避免写错方向', nextSceneId: 'scene_2', effects: { stress: 4, reputation: 8, growth: 10, mood: 0 } },
        { text: '把原始数据打包转发，让对方自己看', nextSceneId: 'scene_2', effects: { stress: 0, reputation: -10, growth: -4, mood: 4 } },
      ],
    },
    {
      id: 'scene_2',
      time: '11:30',
      sceneTitle: '模型和直觉打架',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '晨会', text: '领导：模型显示风险可控，但市场舆情在恶化。你们怎么看？' },
        { role: 'system', source: '同事私聊', text: '别当众硬顶，先把「不确定」写进备注。' },
      ],
      options: [
        { text: '提出补充情景分析（乐观/悲观）', nextSceneId: 'scene_3', effects: { stress: 8, reputation: 12, growth: 14, mood: -4 } },
        { text: '支持模型结论，少说话', nextSceneId: 'scene_3', effects: { stress: 4, reputation: 2, growth: 4, mood: 2 } },
        { text: '建议暂缓相关敞口，等数据更新', nextSceneId: 'scene_3', effects: { stress: 12, reputation: 6, growth: 10, mood: -8 } },
      ],
    },
    {
      id: 'scene_3',
      time: '16:00',
      sceneTitle: '客户电话',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '客户', text: '为什么今天净值波动这么大？我下午要向董事会解释。', tone: 'call', moment: 'call-incoming' },
        { role: 'system', source: '带教', text: '你在旁听，记下客户最担心的三个问题，会后整理答复口径。' },
      ],
      options: [
        { text: '边记问题边查当日归因数据', nextSceneId: 'scene_4', effects: { stress: 14, reputation: 10, growth: 12, mood: -10 } },
        { text: '先安抚客户，承诺书面说明今晚前发出', nextSceneId: 'scene_4', effects: { stress: 10, reputation: 8, growth: 8, mood: -8 } },
        { text: '把电话交给带教，自己做会后纪要', nextSceneId: 'scene_4', effects: { stress: 6, reputation: 4, growth: 6, mood: -4 } },
      ],
    },
    {
      id: 'scene_4',
      time: '22:10',
      sceneTitle: '闭市后的表格',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '带教', text: '归因报告不错。明天把 PPT 里的图表统一口径，别一张表一个算法。' },
        { role: 'system', source: '室友', text: '你还学 CFA 吗？我笔记借你，但别熬夜到两点。' },
      ],
      options: [
        { text: '改完 PPT 再刷题', nextSceneId: '__end__', effects: { stress: 16, reputation: 10, growth: 10, mood: -14 } },
        { text: '今天先到这，明天早起改稿', nextSceneId: '__end__', effects: { stress: 2, reputation: 6, growth: 8, mood: 6 } },
        { text: '申请带教明早一起过一遍', nextSceneId: '__end__', effects: { stress: 6, reputation: 12, growth: 12, mood: 0 } },
      ],
    },
  ],
  endings: [
    {
      id: 'analyst',
      label: '分析型金融人',
      punchline: '你愿意用数据说话，也敢在会议上留余地。',
      summary: '金融方向适合能扛高压、对数字敏感、又愿意沟通的人。AI 会加速报表与检索，但责任与判断仍在你。',
      fitReason: '逻辑与证据意识较强。',
      riskReason: '注意工作生活边界，金融节奏容易「没有下班」。',
      match: (s) => s.growth >= 55,
    },
    {
      id: 'steady_fin',
      label: '稳健风控型',
      punchline: '你知道什么时候该慢一点。',
      summary: '你更倾向于先把风险写清楚，再谈收益——这在风控、合规岗位是核心素质。',
      fitReason: '谨慎与留痕，能降低团队踩雷。',
      riskReason: '过度保守可能错过学习复杂产品的机会。',
      match: () => true,
    },
  ],
}
