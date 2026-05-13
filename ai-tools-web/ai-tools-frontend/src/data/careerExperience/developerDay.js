/** 程序员一日体验（固定分支，不接大模型） */
export const developerDayConfig = {
  id: 'developer',
  title: '程序员的一天',
  subtitle: '体验一次真实程序员工作日。你做的每个选择，都会影响压力、评价和职业适配感。',
  startCta: '开始上班',
  endingHeadline: '你的程序员一天结束了',
  initialStats: {
    stress: 30,
    reputation: 50,
    growth: 20,
    mood: 60,
  },
  scenes: [
    {
      id: 'scene_1',
      time: '09:08',
      messages: [
        {
          role: 'system',
          text: '周一 9:08，你刚坐下，leader 在群里发来消息：线上接口 500，客户已经在催。',
        },
        {
          role: 'system',
          text: '同时，产品经理私聊你：上周那个需求今天还能上线吗？',
        },
      ],
      options: [
        {
          text: '先修线上 bug',
          nextSceneId: 'scene_2',
          effects: { stress: -6, reputation: 8, growth: 8, mood: 4 },
        },
        {
          text: '先回复产品经理',
          nextSceneId: 'scene_2',
          effects: { stress: 6, reputation: 5, growth: 3, mood: 2 },
        },
        {
          text: '先假装没看到，整理一下思路',
          nextSceneId: 'scene_2',
          effects: { stress: 16, reputation: -10, growth: -4, mood: -6 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '10:20',
      messages: [
        {
          role: 'system',
          text: '你顺着日志把链路摸清了：线上 500 的改动，来自同事昨天合并的一段代码。',
        },
        {
          role: 'system',
          text: '群里还在问「谁来看一下」，客户的工单已经标红了。',
        },
      ],
      options: [
        {
          text: '直接在群里说明是同事代码导致',
          nextSceneId: 'scene_3',
          effects: { stress: 8, reputation: -16, growth: 4, mood: -12 },
        },
        {
          text: '先私聊同事确认',
          nextSceneId: 'scene_3',
          effects: { stress: -8, reputation: 10, growth: 10, mood: 8 },
        },
        {
          text: '自己先偷偷修掉',
          nextSceneId: 'scene_3',
          effects: { stress: 14, reputation: 4, growth: -6, mood: -14 },
        },
      ],
    },
    {
      id: 'scene_3',
      time: '14:05',
      messages: [
        {
          role: 'system',
          text: '线上暂时稳住，产品经理又发来语音：「今天下班前必须能看到完整功能，老板在看。」',
        },
      ],
      options: [
        {
          text: '直接答应今天上线',
          nextSceneId: 'scene_4',
          effects: { stress: 22, reputation: 2, growth: -8, mood: -14 },
        },
        {
          text: '说明线上问题优先，需求需要延期',
          nextSceneId: 'scene_4',
          effects: { stress: -12, reputation: 10, growth: 8, mood: 10 },
        },
        {
          text: '让产品经理找 leader 排优先级',
          nextSceneId: 'scene_4',
          effects: { stress: -10, reputation: 6, growth: 6, mood: 4 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '17:30',
      messages: [
        {
          role: 'system',
          text: 'leader 把你和几位相关同学叫进小会议室：「现在到底什么风险？今天能不能交付？」',
        },
      ],
      options: [
        {
          text: '如实说明风险',
          nextSceneId: 'scene_5',
          effects: { stress: 6, reputation: 14, growth: 12, mood: 6 },
        },
        {
          text: '只说能解决，不讲细节',
          nextSceneId: 'scene_5',
          effects: { stress: 16, reputation: -10, growth: -4, mood: -12 },
        },
        {
          text: '把问题推给需求变更',
          nextSceneId: 'scene_5',
          effects: { stress: 4, reputation: -20, growth: -8, mood: -10 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '20:40',
      messages: [
        {
          role: 'system',
          text: '晚上 8:40，线上 bug 终于修完，但需求里还有两块核心逻辑没写完，测试同学也在等你。',
        },
      ],
      options: [
        {
          text: '继续加班做需求',
          nextSceneId: '__end__',
          effects: { stress: 22, reputation: 4, growth: 10, mood: -22 },
        },
        {
          text: '明确说明今天不能完成',
          nextSceneId: '__end__',
          effects: { stress: -16, reputation: 12, growth: 8, mood: 12 },
        },
        {
          text: '先糊一个临时版本上线',
          nextSceneId: '__end__',
          effects: { stress: 10, reputation: -26, growth: -12, mood: -16 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'blame_risk',
      label: '背锅风险型',
      summary:
        '你在协作里多次把压力转给「说不清的一方」，或过早给出难以兑现的承诺。短期看似混过去，长期容易在事故复盘里被点名。下一版可以试试：先对齐事实再表态，把「谁错了」换成「怎么止血」。',
      match: (s) => s.reputation <= 38 || (s.reputation < 46 && s.stress >= 68),
    },
    {
      id: 'high_pressure',
      label: '高压硬扛型',
      summary:
        '你倾向于把问题扛在自己身上，情绪和体力消耗很大。能扛事是优点，但若长期缺少求助与排期，容易陷入「越忙越乱」。试着把「我能做完」拆成「今天能交付的切片」，并主动要资源。',
      match: (s) => s.stress >= 72 || (s.stress >= 58 && s.mood <= 40),
    },
    {
      id: 'clear_boundary',
      label: '边界清晰型',
      summary:
        '你在冲突目标之间敢于说明取舍，也愿意同步风险。这样的节奏通常更可持续，团队对你的预期也会更稳定。继续保持：先同步事实与影响面，再谈日期。',
      match: (s) => s.reputation >= 58 && s.stress <= 54 && s.mood >= 50,
    },
    {
      id: 'steady_growth',
      label: '稳健成长型',
      summary:
        '你在救火与推进之间找到了相对平衡：该顶的时候顶上去，该说不的时候也能留痕。成长往往来自这种「可控的硬」——既不逃避，也不自我感动式加班。可以多复盘：哪些选择真正降低了系统风险。',
      match: () => true,
    },
  ],
}
