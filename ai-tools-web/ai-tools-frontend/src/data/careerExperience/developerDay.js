/** 程序员一日体验（固定分支，不接大模型） */
export const developerDayConfig = {
  id: 'developer',
  title: '程序员的一天',
  subtitle: '体验一次真实程序员工作日。线上 bug、临时需求、开会追责和生活消息，会在同一天排队找你。',
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
          text: '主管：谁来看一下支付页面？客户那边已经在群里@了，工单也标红了。',
        },
        {
          role: 'system',
          source: '产品经理私聊',
          text: '昨晚说的那个改动，老板 11 点要看。你先推进一下，别让我一个人站在风里。',
        },
      ],
      options: [
        {
          text: '先救线上，产品经理那边晚点再解释',
          nextSceneId: 'scene_2',
          effects: { stress: 8, reputation: 8, growth: 8, mood: -6 },
        },
        {
          text: '先安抚产品经理，答应中午前给个能看的版本',
          nextSceneId: 'scene_2',
          effects: { stress: 14, reputation: 4, growth: 2, mood: -10 },
        },
        {
          text: '把主管拉进来，让大家当场决定先救哪个火',
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
          text: '你查到问题来自昨晚的一处改动。改动记录上，名字不是你。',
        },
        {
          role: 'system',
          source: '线上群',
          text: '同事：这块我是按需求改的，先别上升。现在先让页面恢复吧，锅晚点再热。',
        },
      ],
      options: [
        {
          text: '在群里说明原因，也说清不是你改的',
          nextSceneId: 'scene_3',
          effects: { stress: 6, reputation: -10, growth: 8, mood: -12 },
        },
        {
          text: '先私聊同事，一起撤回改动，别让群里炸得更大',
          nextSceneId: 'scene_3',
          effects: { stress: 10, reputation: 10, growth: 10, mood: -4 },
        },
        {
          text: '自己先临时修一下，事后总结先欠着',
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
          text: '产品经理：你上午在修 bug 我理解，但老板刚问了，今天必须有结果。理解归理解，结果归结果。',
        },
        {
          role: 'system',
          source: '测试群',
          text: '测试：16 点前不给版本，今晚就测不了。我们也不是住公司，只是看起来像。',
        },
      ],
      options: [
        {
          text: '砍掉不重要的功能，只交最关键的流程',
          nextSceneId: 'scene_4',
          effects: { stress: 10, reputation: 8, growth: 8, mood: -8 },
        },
        {
          text: '坚持延期，把线上 bug 的影响写清楚',
          nextSceneId: 'scene_4',
          effects: { stress: 2, reputation: 6, growth: 10, mood: -2 },
        },
        {
          text: '答应今晚给测试，先把场面稳住',
          nextSceneId: 'scene_4',
          effects: { stress: 24, reputation: 2, growth: -8, mood: -16 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '17:46',
      messages: [
        {
          role: 'system',
          source: '临时会议',
          text: '主管：客户电话打到总监那里了。现在别讲过程，我只问一句，今晚能不能交？',
        },
        {
          role: 'system',
          source: '产品经理',
          text: '产品经理：需求是有变动，但技术方案之前也说能做。大家都是成年人，别互相伤害。',
        },
      ],
      options: [
        {
          text: '列出风险、缺口和今晚能交的部分',
          nextSceneId: 'scene_5',
          effects: { stress: 8, reputation: 14, growth: 12, mood: -4 },
        },
        {
          text: '先说能交，细节会后自己慢慢还债',
          nextSceneId: 'scene_5',
          effects: { stress: 20, reputation: -8, growth: -6, mood: -18 },
        },
        {
          text: '当场指出需求改了好几次，别只追技术',
          nextSceneId: 'scene_5',
          effects: { stress: 10, reputation: -14, growth: 6, mood: -10 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '21:15',
      messages: [
        {
          role: 'system',
          source: '生活消息',
          text: '女朋友：你今天是不是又不来了？我已经把菜单翻到第三遍了。',
        },
        {
          role: 'system',
          source: '主管私聊',
          text: '今晚最好把需求一起补上，明早客户要看。辛苦一下，明天请你喝咖啡。',
        },
      ],
      options: [
        {
          text: '继续加班，回她一句“真的快了”',
          nextSceneId: '__end__',
          effects: { stress: 22, reputation: 8, growth: 8, mood: -26 },
        },
        {
          text: '把风险说清楚后下班，明早继续补',
          nextSceneId: '__end__',
          effects: { stress: -8, reputation: -10, growth: 8, mood: 8 },
        },
        {
          text: '先交一个临时版本，路上继续盯手机',
          nextSceneId: '__end__',
          effects: { stress: 18, reputation: -18, growth: -8, mood: -16 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'blame_risk',
      label: '成熟背锅侠型程序员',
      punchline: '你不是不能拒绝，你只是每次都刚好心软。',
      visual: {
        symbol: '锅',
        name: '抱锅小人',
        description: '抱着一口锅，眼神清澈但已经熟练，电脑旁边还放着半杯凉咖啡。',
        tags: ['锅在怀里', '咖啡已凉', '表情稳定'],
      },
      summary:
        '你今天看起来很忙，也确实很忙。\n\n线上炸了你在，会议追责你在，最后那句“当时是谁说能上的”，大概率也有你。\n\n恭喜，你已经开始掌握打工人的祖传技能：人在工位坐，锅从群里来。',
      fitReason:
        '今天还算扛住的地方：你知道问题要先解决，也知道事实不能全靠记忆，关键时刻会留下说明。',
      riskReason:
        '今天最扎心的地方：你越想把事情讲清楚，越容易变成“那你来负责一下”。',
      match: (s) => s.reputation <= 38 || (s.reputation < 46 && s.stress >= 68),
    },
    {
      id: 'high_pressure',
      label: '救火队长型程序员',
      punchline: '哪里炸了，哪里就会出现你。',
      visual: {
        symbol: '火',
        name: '工位消防员',
        description: '一边灭火一边回消息，工单红得像过年，电脑风扇正在努力活着。',
        tags: ['到处灭火', '消息爆炸', '工单标红'],
      },
      summary:
        '你今天扛了线上 bug，顶了临时需求，参加了追责会，最后还在安抚生活里的那个人。\n\n团队现在已经默认：有问题先找你。\n\n恭喜你。你已经开始像一个成熟的背锅侠了。',
      fitReason:
        '今天还算扛住的地方：混乱里你能抓重点，知道今晚至少要让哪一块先活下来。',
      riskReason:
        '今天最扎心的地方：“靠谱”一旦用多了，就会被系统自动翻译成“随时在线”。',
      match: (s) => s.stress >= 74 || (s.stress >= 60 && s.mood <= 38),
    },
    {
      id: 'clear_boundary',
      label: '假装下班型程序员',
      punchline: '你不是不负责，你只是知道工作永远做不完。',
      visual: {
        symbol: '走',
        name: '准点撤退人',
        description: '背包已经背好，手机开了静音，脚步很轻，但边界很硬。',
        tags: ['手机静音', '背包走人', '拒绝续杯'],
      },
      summary:
        '你没有接住所有问题。\n\n短期看，有些人会觉得你“不够配合”。\n\n但长期看，你更像一个还能继续活下去的打工人。这在今天已经算稀缺能力。',
      fitReason:
        '今天还算扛住的地方：你敢把风险摊开说，也没有用一句“我尽快”把自己卖掉。',
      riskReason:
        '今天最扎心的地方：边界清楚的人，常常要忍受别人说你“不够积极”。',
      match: (s) => s.reputation >= 58 && s.stress <= 56 && s.mood >= 46,
    },
    {
      id: 'steady_growth',
      label: '深夜补锅型程序员',
      punchline: '你今天不是在写代码，你是在给白天留下的坑贴创可贴。',
      visual: {
        symbol: '夜',
        name: '深夜补锅人',
        description: '窗外已经黑了，电脑蓝光很亮，人还在给白天的坑做售后。',
        tags: ['夜里修 bug', '电脑蓝光', '白天欠债'],
      },
      summary:
        '你今天没有赢，也没有彻底崩。\n\n线上问题压下去了，需求还欠一点，生活消息也还没回明白。\n\n这就是很多程序员的一天：代码会报错，人也会，只是人没有错误日志。',
      fitReason:
        '今天还算扛住的地方：你能在不完美里做选择，至少没有让所有事情同时爆掉。',
      riskReason:
        '今天最扎心的地方：努力不一定被看见，但出问题一定会被看见。',
      match: () => true,
    },
  ],
}
