/** HR 一日体验（固定分支，不接大模型） */
export const hrDayConfig = {
  id: 'hr',
  title: 'HR 的一天',
  subtitle:
    '体验一次真实 HR 工作日：招聘、员工关系与组织节奏交织。你的选择会影响压力、信任感、专业成长与情绪。',
  startCta: '开始上班',
  endingHeadline: '你的 HR 一天结束了',
  initialStats: {
    stress: 32,
    reputation: 52,
    growth: 22,
    mood: 58,
  },
  scenes: [
    {
      id: 'scene_1',
      time: '09:12',
      messages: [
        {
          role: 'system',
          text: '周一 9:12，你刚打开电脑：用人部门负责人发来消息——「这个岗位这周必须到岗，候选人今天能面吗？」',
        },
        {
          role: 'system',
          text: '同时，有位员工在 IM 里问：「我的年假余额好像不对，能帮我查一下吗？」系统里还有两份待归档的入职材料。',
        },
      ],
      options: [
        {
          text: '先排面试，把用人部门稳住',
          nextSceneId: 'scene_2',
          effects: { stress: 8, reputation: 6, growth: 4, mood: -4 },
        },
        {
          text: '先回复员工年假问题，避免舆情',
          nextSceneId: 'scene_2',
          effects: { stress: -6, reputation: 8, growth: 6, mood: 6 },
        },
        {
          text: '先处理入职归档，避免合规风险',
          nextSceneId: 'scene_2',
          effects: { stress: 4, reputation: 4, growth: 10, mood: 2 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '10:35',
      messages: [
        {
          role: 'system',
          text: '你协调好上午的节奏，面试官反馈来了：候选人沟通很强，但背调里有一条「与前主管关系紧张」的备注。',
        },
        {
          role: 'system',
          text: '用人部门负责人说：「业务急，先推进吧，细节后面再说。」',
        },
      ],
      options: [
        {
          text: '坚持补一轮结构化面试，再决定',
          nextSceneId: 'scene_3',
          effects: { stress: -4, reputation: 10, growth: 12, mood: 4 },
        },
        {
          text: '按负责人意思先推进到谈薪',
          nextSceneId: 'scene_3',
          effects: { stress: 10, reputation: -8, growth: -6, mood: -10 },
        },
        {
          text: '私下再联系背调联系人核实细节',
          nextSceneId: 'scene_3',
          effects: { stress: 6, reputation: 6, growth: 8, mood: -6 },
        },
      ],
    },
    {
      id: 'scene_3',
      time: '14:05',
      messages: [
        {
          role: 'system',
          text: '午休刚过，一位员工把你拉到楼梯间：「我想离职，但能不能先别让我 leader 知道？我压力太大了。」',
        },
        {
          role: 'system',
          text: '你知道留面沟通能留住人，但也涉及信息边界与管理者知情权。',
        },
      ],
      options: [
        {
          text: '先倾听并约定下次正式沟通时间',
          nextSceneId: 'scene_4',
          effects: { stress: -8, reputation: 8, growth: 10, mood: 10 },
        },
        {
          text: '建议他直接和 leader 开诚布公谈一次',
          nextSceneId: 'scene_4',
          effects: { stress: 4, reputation: -6, growth: 4, mood: -8 },
        },
        {
          text: '当天就同步给其 leader（避免风险）',
          nextSceneId: 'scene_4',
          effects: { stress: 12, reputation: -14, growth: -4, mood: -14 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '16:40',
      messages: [
        {
          role: 'system',
          text: '管理层临时拉会：「这轮绩效沟通要更『激励』一点，评级分布能不能往高调？」',
        },
        {
          role: 'system',
          text: '你手里有校准规则与历史分布，改口径会影响公平感与员工信任。',
        },
      ],
      options: [
        {
          text: '用数据说明调整对公平与留存的影响',
          nextSceneId: 'scene_5',
          effects: { stress: 6, reputation: 14, growth: 12, mood: 6 },
        },
        {
          text: '先口头答应，会后私下再争取规则',
          nextSceneId: 'scene_5',
          effects: { stress: 14, reputation: -10, growth: -6, mood: -12 },
        },
        {
          text: '建议走正式校准流程，书面确认结论',
          nextSceneId: 'scene_5',
          effects: { stress: -6, reputation: 10, growth: 10, mood: 4 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '19:05',
      messages: [
        {
          role: 'system',
          text: '快下班时，用人部门催你：「候选人手里有竞品 offer，今晚必须把邮件发出去。」',
        },
        {
          role: 'system',
          text: '法务还在邮件里标了一处薪酬结构表述，说「明天再确认更安全」。',
        },
      ],
      options: [
        {
          text: '等法务确认后再发，明确同步风险',
          nextSceneId: '__end__',
          effects: { stress: -12, reputation: 12, growth: 10, mood: 8 },
        },
        {
          text: '先发口头意向，书面 offer 跟法务后补',
          nextSceneId: '__end__',
          effects: { stress: 8, reputation: -12, growth: -8, mood: -10 },
        },
        {
          text: '加班拉着法务和负责人三方对齐一版',
          nextSceneId: '__end__',
          effects: { stress: 18, reputation: 8, growth: 8, mood: -8 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'trust_risk',
      label: '信任透支型',
      summary:
        '你在多方拉扯里几次把「先稳住对方」放在事实与规则之前，短期能灭火，长期容易在员工与管理者心里留下「立场不清」的印象。可以试试：先写清事实与选项，再谈情绪与节奏。',
      match: (s) => s.reputation <= 40 || (s.reputation < 48 && s.stress >= 70),
    },
    {
      id: 'empathy_fatigue',
      label: '共情耗竭型',
      summary:
        '你承接了很多情绪与紧急事项，自己的恢复空间被挤占。HR 的价值也包括「可持续在场」。试着把倾听与行动拆开：共情可以即时，承诺与升级要有边界。',
      match: (s) => s.stress >= 74 || (s.stress >= 60 && s.mood <= 38),
    },
    {
      id: 'process_partner',
      label: '流程伙伴型',
      summary:
        '你在招聘、员工关系与组织规则之间保持了相对清晰的节奏：该对齐数据就对齐，该留痕就留痕，也愿意为人的处境多留半步。这类风格通常更能建立长期信任。',
      match: (s) => s.reputation >= 60 && s.stress <= 56 && s.mood >= 52,
    },
    {
      id: 'steady_balance',
      label: '稳健平衡型',
      summary:
        '你没有追求「所有人都立刻满意」，而是在合规、业务与人之间做了可解释的选择。成长往往来自这种「说得清为什么」的日常。可以多复盘：哪些决定真正减少了二次沟通成本。',
      match: () => true,
    },
  ],
}
