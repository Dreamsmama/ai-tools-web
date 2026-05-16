/** 程序员系列 EP02：线上事故的一夜（固定分支） */
export const developerIncidentNightConfig = {
  id: 'developer-ep02',
  seriesId: 'developer',
  episodeId: 'ep02',
  episodeCode: 'EP02',
  episodeLabel: 'EP02',
  title: '线上事故的一夜',
  subtitle: '本来想下班，结果客户群突然炸了。',
  startCta: '开始追剧',
  endingHeadline: '🎬 EP02 · 收工',
  endingSectionTitle: '本集状态',
  endingKicker: '这一夜的你，更接近',
  defaultAtmosphere: 'dev-night-office',
  initialStats: {
    stress: 42,
    reputation: 52,
    growth: 24,
    mood: 54,
  },
  scenes: [
    {
      id: 'scene_1',
      time: '20:43',
      sceneTitle: '刚准备下班',
      atmosphere: 'dev-night-office',
      sceneBg: '/drama/developer/scene-4.svg',
      messages: [
        {
          role: 'system',
          source: '线上群',
          text: '你刚合上电脑，群里突然有人@你。',
          tone: 'alert',
          moment: 'feishu-dot',
        },
        {
          role: 'system',
          source: '主管',
          text: '主管：支付页面又报错了，客户那边已经在群里问了。',
        },
      ],
      options: [
        {
          text: '立刻重新打开电脑排查',
          nextSceneId: 'scene_2',
          effects: { stress: 12, reputation: 10, growth: 6, mood: -10 },
        },
        {
          text: '先问清楚影响范围',
          nextSceneId: 'scene_2',
          effects: { stress: 4, reputation: 8, growth: 10, mood: -4 },
        },
        {
          text: '让值班同事先看一下',
          nextSceneId: 'scene_2',
          effects: { stress: -4, reputation: -6, growth: 4, mood: 6 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '21:10',
      sceneTitle: '问题扩大',
      atmosphere: 'dev-alert-desk',
      sceneBg: '/drama/developer/scene-3.svg',
      messages: [
        {
          role: 'system',
          source: '工单系统',
          text: '工单开始标红，产品经理私聊：「这个问题今晚能恢复吗？客户明早要用。」',
          tone: 'alert',
          moment: 'ticket-red',
        },
        {
          role: 'system',
          source: '同事私聊',
          text: '同事：我刚看了下，好像和你下午合的代码有关。',
          tone: 'private',
        },
      ],
      options: [
        {
          text: '先查日志，确认是不是自己的问题',
          nextSceneId: 'scene_3',
          effects: { stress: 8, reputation: 12, growth: 12, mood: -8 },
        },
        {
          text: '在群里说明需要一起排查',
          nextSceneId: 'scene_3',
          effects: { stress: 6, reputation: 6, growth: 8, mood: -6 },
        },
        {
          text: '先回滚下午的改动',
          nextSceneId: 'scene_3',
          effects: { stress: 14, reputation: 4, growth: 4, mood: -12 },
        },
      ],
    },
    {
      id: 'scene_3',
      time: '22:30',
      sceneTitle: '临时会议',
      atmosphere: 'dev-meeting',
      sceneBg: '/drama/developer/scene-2.svg',
      messages: [
        {
          role: 'system',
          source: '临时会议',
          text: '主管拉了临时会议。他说：「现在先别讨论是谁的问题，先看怎么恢复。」',
          tone: 'call',
          moment: 'call-incoming',
        },
        {
          role: 'system',
          source: '会议现场',
          text: '但会议里大家都在等你说方案。',
        },
      ],
      options: [
        {
          text: '给出临时恢复方案',
          nextSceneId: 'scene_4',
          effects: { stress: 10, reputation: 14, growth: 10, mood: -6 },
        },
        {
          text: '先要求确认责任边界',
          nextSceneId: 'scene_4',
          effects: { stress: 4, reputation: -8, growth: 6, mood: -4 },
        },
        {
          text: '硬着头皮继续排查',
          nextSceneId: 'scene_4',
          effects: { stress: 18, reputation: 6, growth: 8, mood: -14 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '23:50',
      sceneTitle: '生活消息',
      atmosphere: 'dev-night-office',
      sceneBg: '/drama/developer/scene-5.svg',
      messages: [
        {
          role: 'system',
          source: '生活消息',
          text: '朋友/家人发来消息：「你不是说今天早点休息吗？」',
          tone: 'life',
          moment: 'phone-vibrate',
        },
        {
          role: 'system',
          source: '线上群',
          text: '同时线上群又弹出：「客户问还要多久。」',
          tone: 'alert',
          moment: 'feishu-dot',
        },
      ],
      options: [
        {
          text: '继续处理线上，先不回生活消息',
          nextSceneId: '__end__',
          effects: { stress: 16, reputation: 10, growth: 6, mood: -22 },
        },
        {
          text: '简单解释一下，再继续处理',
          nextSceneId: '__end__',
          effects: { stress: 10, reputation: 6, growth: 8, mood: -12 },
        },
        {
          text: '明确说今晚只能先恢复核心功能',
          nextSceneId: '__end__',
          effects: { stress: 6, reputation: 12, growth: 10, mood: -8 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'all_night_fix',
      label: '通宵恢复型程序员',
      episodeCoda:
        '凌晨 00:37，页面终于恢复了。\n\n群里只剩下一句：辛苦。\n\n你看着还没关掉的电脑，突然想不起自己今晚原本打算做什么。',
      punchline: '辛苦两个字，常常换不来明天的轻松。',
      visual: {
        symbol: '夜',
        name: '凌晨收工人',
        description: '屏幕终于绿了，人还坐在工位，窗外已经一点声音都没有。',
        tags: ['页面恢复', '电脑还亮', '群里一句辛苦'],
      },
      summary:
        '这一夜你没有赢，只是把火压下去了。\n\n客户群安静了，工单也不红了，但你知道明天还会有人问：为什么又出了这个问题。',
      fitReason: '这一夜还算扛住的地方：混乱里你知道先让核心功能活下来。',
      riskReason: '这一夜最扎心的地方：恢复之后，很少有人记得你原本打算下班。',
      match: (s) => s.stress >= 70 || (s.stress >= 58 && s.mood <= 40),
    },
    {
      id: 'boundary_night',
      label: '只救核心型程序员',
      episodeCoda:
        '凌晨 00:37，页面终于恢复了。\n\n群里只剩下一句：辛苦。\n\n你看着还没关掉的电脑，突然想不起自己今晚原本打算做什么。',
      punchline: '你不是不负责，你只是知道今晚只能做到这里。',
      visual: {
        symbol: '界',
        name: '核心功能守门人',
        description: '只开了最关键的那盏灯，其他需求先躺在待办里。',
        tags: ['只救核心', '边界清楚', '明天继续'],
      },
      summary:
        '你没有答应所有事，但也没有让系统彻底躺平。\n\n这在事故夜里已经很难得——只是别人未必会记得你拒绝过什么。',
      fitReason: '这一夜还算扛住的地方：你敢把「今晚只能到这里」说清楚。',
      riskReason: '这一夜最扎心的地方：边界清楚的人，常常要独自承受「不够积极」的眼神。',
      match: (s) => s.reputation >= 58 && s.stress <= 62,
    },
    {
      id: 'deflect_shift',
      label: '值班甩锅型程序员',
      episodeCoda:
        '凌晨 00:37，页面终于恢复了。\n\n群里只剩下一句：辛苦。\n\n你看着还没关掉的电脑，突然想不起自己今晚原本打算做什么。',
      punchline: '锅可以晚一点背，但消息不会晚一点到。',
      visual: {
        symbol: '推',
        name: '先推一步的人',
        description: '值班群、私聊、会议邀请同时在闪，你总想让别人先看一眼。',
        tags: ['值班先上', '责任模糊', '消息还在响'],
      },
      summary:
        '你今晚可能没背最大的锅，但也没真正从这场夜里抽身。\n\n因为最后恢复的时候，大家还是会默认：你也在线。',
      fitReason: '这一夜还算扛住的地方：你知道不能所有事都一个人硬顶。',
      riskReason: '这一夜最扎心的地方：推得了一时，推不掉「你也在群里」。',
      match: (s) => s.reputation <= 48,
    },
    {
      id: 'steady_night',
      label: '事故夜幸存者',
      episodeCoda:
        '凌晨 00:37，页面终于恢复了。\n\n群里只剩下一句：辛苦。\n\n你看着还没关掉的电脑，突然想不起自己今晚原本打算做什么。',
      punchline: '这一夜没有赢家，只有还没倒下的人。',
      visual: {
        symbol: '熬',
        name: '事故夜幸存者',
        description: '日志、会议、生活消息叠在一起，你至少把今晚熬过去了。',
        tags: ['事故夜', '勉强恢复', '生活消息未读'],
      },
      summary:
        '这一夜你做了很多次选择，有的对，有的只是没那么糟。\n\n这就是很多程序员的夜晚：没有英雄，只有还没关掉的电脑。',
      fitReason: '这一夜还算扛住的地方：你没有让所有线同时断掉。',
      riskReason: '这一夜最扎心的地方：恢复之后，很少人问你累不累。',
      match: () => true,
    },
  ],
}
