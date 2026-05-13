/** 程序员一日体验（固定分支，不接大模型） */
export const developerDayConfig = {
  id: 'developer',
  title: '程序员的一天',
  subtitle: '体验一次真实程序员工作日。线上问题、临时需求、人情和生活，会一起挤进同一天。',
  startCta: '开始上班',
  endingHeadline: '你的程序员一天结束了',
  initialStats: {
    stress: 36,
    reputation: 50,
    growth: 20,
    mood: 58,
  },
  scenes: [
    {
      id: 'scene_1',
      time: '09:08',
      messages: [
        {
          role: 'system',
          source: '线上群',
          text: '主管：支付功能又报错了，客户已经催了，工单标红。',
        },
        {
          role: 'system',
          source: '产品经理私聊',
          text: '昨晚说的那个改动，老板 11 点要看。你这边别卡流程，先推进一下？',
        },
      ],
      options: [
        {
          text: '先修线上 bug，产品经理那边晚点解释',
          nextSceneId: 'scene_2',
          effects: { stress: 8, reputation: 8, growth: 8, mood: -6 },
        },
        {
          text: '先回产品经理，承诺中午前给能演示的版本',
          nextSceneId: 'scene_2',
          effects: { stress: 14, reputation: 4, growth: 2, mood: -10 },
        },
        {
          text: '先拉群说清优先级，让主管决定先做哪个',
          nextSceneId: 'scene_2',
          effects: { stress: 4, reputation: 6, growth: 6, mood: -4 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '10:26',
      messages: [
        {
          role: 'system',
          source: '错误日志',
          text: '你查到问题来自昨晚的一处改动，改的人是隔壁组同事。',
        },
        {
          role: 'system',
          source: '线上群',
          text: '同事：这块我只是按需求改的，先别上升。现在谁能先让系统恢复正常？',
        },
      ],
      options: [
        {
          text: '在群里说明原因和是谁改的',
          nextSceneId: 'scene_3',
          effects: { stress: 6, reputation: -10, growth: 8, mood: -12 },
        },
        {
          text: '先私聊同事，一起撤回改动并补说明',
          nextSceneId: 'scene_3',
          effects: { stress: 10, reputation: 10, growth: 10, mood: -4 },
        },
        {
          text: '自己先临时修一下，事后总结后面再补',
          nextSceneId: 'scene_3',
          effects: { stress: 16, reputation: 4, growth: -4, mood: -14 },
        },
      ],
    },
    {
      id: 'scene_3',
      time: '14:05',
      messages: [
        {
          role: 'system',
          source: '产品经理私聊',
          text: '产品经理：你上午一直在修 bug 我理解，但老板刚问了，今天必须给结果。',
        },
        {
          role: 'system',
          source: '测试群',
          text: '测试：如果 16 点还不给版本，今晚就没法测试了，大家都在等。',
        },
      ],
      options: [
        {
          text: '砍掉不重要的功能，只交最关键流程',
          nextSceneId: 'scene_4',
          effects: { stress: 10, reputation: 8, growth: 8, mood: -8 },
        },
        {
          text: '坚持延期，把线上事故影响写清楚',
          nextSceneId: 'scene_4',
          effects: { stress: 2, reputation: 6, growth: 10, mood: -2 },
        },
        {
          text: '答应今晚交给测试，先把承诺顶住',
          nextSceneId: 'scene_4',
          effects: { stress: 24, reputation: 2, growth: -8, mood: -16 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '17:32',
      messages: [
        {
          role: 'system',
          source: '临时会议',
          text: '主管：客户已经投诉到总监那里了。现在别讲过程，我只问一句，今晚能不能交？',
        },
        {
          role: 'system',
          source: '产品经理',
          text: '产品经理：需求反复不是我一个人的问题，技术方案之前也说能做。',
        },
      ],
      options: [
        {
          text: '列出风险、缺口和今晚能交的范围',
          nextSceneId: 'scene_5',
          effects: { stress: 8, reputation: 14, growth: 12, mood: -4 },
        },
        {
          text: '先说能交，细节会后自己补',
          nextSceneId: 'scene_5',
          effects: { stress: 20, reputation: -8, growth: -6, mood: -18 },
        },
        {
          text: '当场指出需求变更多次导致延期',
          nextSceneId: 'scene_5',
          effects: { stress: 10, reputation: -14, growth: 6, mood: -10 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '20:18',
      messages: [
        {
          role: 'system',
          source: '生活消息',
          text: '女朋友：我已经到餐厅了，你昨天说今天一定不加班的。',
        },
        {
          role: 'system',
          source: '测试群',
          text: '测试：版本呢？再晚就没人重新测试了。老板也在群里。',
        },
      ],
      options: [
        {
          text: '留下发版本，跟她说今天真的走不开',
          nextSceneId: '__end__',
          effects: { stress: 20, reputation: 8, growth: 8, mood: -24 },
        },
        {
          text: '交接清楚先走，明早补完整测试',
          nextSceneId: '__end__',
          effects: { stress: -8, reputation: -8, growth: 6, mood: 8 },
        },
        {
          text: '发一个临时版本，赶去餐厅路上看问题',
          nextSceneId: '__end__',
          effects: { stress: 16, reputation: -18, growth: -8, mood: -14 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'blame_risk',
      label: '背锅风险型',
      summary:
        '你把问题往前推了，但有几次选择让事实、责任和承诺混在一起。短期看像是有人接住了局面，长期可能变成事故总结里那句「当时是谁说能上的」。',
      fitReason:
        '如果你能在压力下保留证据、同步边界，并接受协作里永远会有不完整信息，这类工作会逼你长得很快。',
      riskReason:
        '如果你很难承受被误解、被催促、被临时改优先级，程序员日常里的救火和甩锅会持续消耗你。',
      match: (s) => s.reputation <= 38 || (s.reputation < 46 && s.stress >= 68),
    },
    {
      id: 'high_pressure',
      label: '高压硬扛型',
      summary:
        '你把事情推进下来了，但代价是：你已经默认所有问题都该自己扛。没人明确要求你牺牲生活，可每个消息都在把你往那一步推。',
      fitReason:
        '你适合处理复杂问题和突发故障，尤其能在混乱里抓住今晚最少必须交付的部分。',
      riskReason:
        '如果长期缺少求助、拆解和拒绝，你会把「靠谱」活成「永远在线」。',
      match: (s) => s.stress >= 74 || (s.stress >= 60 && s.mood <= 38),
    },
    {
      id: 'clear_boundary',
      label: '边界清晰型',
      summary:
        '你没有让每个人都满意，但你把事实、风险和交付范围说清楚了。真实职场里，这往往比一句「我尽快」更难，也更值钱。',
      fitReason:
        '你能接受技术之外的沟通成本，并愿意把不确定性翻译成别人听得懂的取舍。',
      riskReason:
        '需要持续练习的是：边界清楚不等于情绪冷，技术判断也要留给关系一点缓冲。',
      match: (s) => s.reputation >= 58 && s.stress <= 56 && s.mood >= 46,
    },
    {
      id: 'steady_growth',
      label: '稳健成长型',
      summary:
        '你在救火、需求和生活之间做了几次不完美但能解释的选择。今天没有漂亮收尾，只有一个程序员很熟悉的晚上：事情还在，人也还在撑。',
      fitReason:
        '如果你能从每次混乱里总结出规则、工具和沟通方式，这份职业会给你稳定的成长反馈。',
      riskReason:
        '如果你期待每次努力都被即时看见，程序员的成就感和委屈感可能会同时出现。',
      match: () => true,
    },
  ],
}
