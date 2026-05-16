/** HR 一日体验（固定分支，不接大模型） */
export const hrDayConfig = {
  id: 'hr-ep01',
  seriesId: 'hr',
  episodeId: 'ep01',
  episodeCode: 'EP01',
  episodeLabel: 'EP01',
  title: 'HR 的一天',
  subtitle: '所有人都在找你解决问题，但没人问你累不累。指标、情绪和流程，会在同一天把你夹扁。',
  startCta: '开始追剧',
  endingHeadline: '🎬 EP01 · 收工',
  endingSectionTitle: '本集状态',
  endingKicker: '今天的你，更接近',
  defaultAtmosphere: 'hr-office',
  initialStats: {
    stress: 38,
    reputation: 52,
    growth: 22,
    mood: 56,
  },
  scenes: [
    {
      id: 'scene_1',
      time: '09:12',
      sceneTitle: '招聘群开始催人',
      atmosphere: 'hr-inbox',
      sceneBg: '/drama/hr/scene-1.svg',
      messages: [
        {
          role: 'system',
          source: '用人部门群',
          text: '用人部门负责人：这个岗位空了两周了，老板在看。本周不到岗，我这边真不好交代。',
          tone: 'group',
          moment: 'feishu-dot',
        },
        {
          role: 'system',
          source: '候选人微信',
          text: '不好意思，上午突然有事，面试能改到晚上吗？另外我手里还有一个录用通知。',
          tone: 'private',
        },
      ],
      options: [
        {
          text: '先稳住候选人，再去求面试官晚上加一场',
          nextSceneId: 'scene_2',
          effects: { stress: 16, reputation: 6, growth: 8, mood: -10 },
        },
        {
          text: '告诉用人部门这个人有风险，先看备选人',
          nextSceneId: 'scene_2',
          effects: { stress: 6, reputation: 4, growth: 6, mood: -4 },
        },
        {
          text: '直接要求候选人今天必须面，不然就算放弃',
          nextSceneId: 'scene_2',
          effects: { stress: 2, reputation: -12, growth: -6, mood: -8 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '10:47',
      sceneTitle: '面试临时崩盘',
      atmosphere: 'hr-meeting',
      sceneBg: '/drama/hr/scene-2.svg',
      messages: [
        {
          role: 'system',
          source: '面试官私聊',
          text: '我 11 点被拉去客户会了，面不了。你跟候选人说一下，后面再补。',
        },
        {
          role: 'system',
          source: '用人部门群',
          text: '负责人：别卡流程。这个人如果没了，你帮我解释给老板？',
        },
      ],
      options: [
        {
          text: '临时找备选面试官，先把今天这场保住',
          nextSceneId: 'scene_3',
          effects: { stress: 18, reputation: 8, growth: 10, mood: -12 },
        },
        {
          text: '如实改期，把面试官时间冲突同步给用人部门',
          nextSceneId: 'scene_3',
          effects: { stress: 4, reputation: 6, growth: 8, mood: -4 },
        },
        {
          text: '先让候选人等着，等面试官会后再说',
          nextSceneId: 'scene_3',
          effects: { stress: 8, reputation: -14, growth: -6, mood: -10 },
        },
      ],
    },
    {
      id: 'scene_3',
      time: '14:20',
      sceneTitle: '员工突然情绪崩溃',
      atmosphere: 'hr-office',
      sceneBg: '/drama/hr/scene-3.svg',
      messages: [
        {
          role: 'system',
          source: '员工私聊',
          text: '我真的有点撑不住了。但能不能先别让我主管知道？我不想把事情闹大。',
          tone: 'private',
          moment: 'phone-vibrate',
        },
        {
          role: 'system',
          source: '部门群',
          text: '该员工主管：下午帮我约他聊一下，最近状态不太对。你先别说是我说的。',
        },
      ],
      options: [
        {
          text: '先接住情绪，说明哪些能保密、哪些必须升级',
          nextSceneId: 'scene_4',
          effects: { stress: 4, reputation: 12, growth: 12, mood: -2 },
        },
        {
          text: '建议员工直接跟主管摊开说',
          nextSceneId: 'scene_4',
          effects: { stress: -2, reputation: -8, growth: 4, mood: -8 },
        },
        {
          text: '马上同步给主管，避免事情继续扩大',
          nextSceneId: 'scene_4',
          effects: { stress: 10, reputation: -16, growth: -4, mood: -16 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '16:40',
      sceneTitle: '绩效沟通会',
      atmosphere: 'hr-meeting',
      sceneBg: '/drama/hr/scene-4.svg',
      messages: [
        {
          role: 'system',
          source: '临时会议',
          text: '老板：这轮绩效不能太难看，奖金预算也不能超，离职率别再上去了。你们 HR 把一下。',
        },
        {
          role: 'system',
          source: '用人部门负责人',
          text: '我们组今年真挺苦的，评级不能太低。你们别只看表格，也看看活是谁干的。',
        },
      ],
      options: [
        {
          text: '拿历史数据和预算限制，推动大家当场对齐',
          nextSceneId: 'scene_5',
          effects: { stress: 8, reputation: 14, growth: 12, mood: -4 },
        },
        {
          text: '先按老板口径调分布，员工沟通后面再慢慢解释',
          nextSceneId: 'scene_5',
          effects: { stress: 14, reputation: -10, growth: -8, mood: -14 },
        },
        {
          text: '帮用人部门争取更好评级，同时提示预算会爆',
          nextSceneId: 'scene_5',
          effects: { stress: 12, reputation: 4, growth: 8, mood: -8 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '18:46',
      sceneTitle: '名单不能外传',
      atmosphere: 'hr-office',
      sceneBg: '/drama/hr/scene-5.svg',
      messages: [
        {
          role: 'system',
          source: '人员调整会',
          text: '你刚听到名单：下午找你倾诉的那位员工，可能下个月会被裁掉。现在不能外传。',
        },
        {
          role: 'system',
          source: '员工私聊',
          text: '他又发来：我准备报个课，想在公司再拼半年。你觉得我还有机会吗？',
        },
      ],
      options: [
        {
          text: '提前暗示他多看机会，但不说名单',
          nextSceneId: 'scene_6',
          effects: { stress: 16, reputation: -8, growth: 8, mood: -18 },
        },
        {
          text: '严格保密，只回应当下表现和沟通建议',
          nextSceneId: 'scene_6',
          effects: { stress: 10, reputation: 10, growth: 10, mood: -12 },
        },
        {
          text: '转移话题，等正式通知再处理',
          nextSceneId: 'scene_6',
          effects: { stress: 6, reputation: -14, growth: -6, mood: -10 },
        },
      ],
    },
    {
      id: 'scene_6',
      time: '20:50',
      sceneTitle: '朋友问你为什么又加班',
      atmosphere: 'hr-night-office',
      sceneBg: '/drama/hr/scene-6.svg',
      messages: [
        {
          role: 'system',
          source: '生活消息',
          text: '朋友：你是不是又加班？电影都快开场了，你已经连续放我两次鸽子了。我票都买了。',
          tone: 'life',
          moment: 'phone-vibrate',
        },
        {
          role: 'system',
          source: '招聘负责人私聊',
          text: '候选人现在想谈薪资，你能回一下吗？他说再晚就接受另一家公司了。老板也在催到岗。',
          tone: 'private',
          moment: 'feishu-dot',
        },
        {
          role: 'system',
          source: '员工私聊',
          text: '他又发来一句：在吗？今天聊完我感觉好一点了，谢谢你。……你还在公司吗？',
          tone: 'private',
        },
      ],
      options: [
        {
          text: '先处理候选人，跟朋友说“马上马上”',
          nextSceneId: '__end__',
          effects: { stress: 18, reputation: 8, growth: 8, mood: -20 },
        },
        {
          text: '先认真回朋友，候选人晚点再谈',
          nextSceneId: '__end__',
          effects: { stress: -6, reputation: -10, growth: 4, mood: 8 },
        },
        {
          text: '两边都回一句“我看下”，然后原地发呆三十秒',
          nextSceneId: '__end__',
          effects: { stress: 10, reputation: -8, growth: -4, mood: -8 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'relationship_keeper',
      label: '组织润滑剂型 HR',
      episodeCoda:
        '晚上 9:51，你终于把今天的待办清到只剩一条：「回复自己」。\n\n但候选人又发来一句「在吗」，你还是点了已读。',
      punchline: '你今天不是在上班，你是在给组织补漏洞。',
      visual: {
        symbol: '补',
        name: '组织补丁人',
        description: '一手胶带一手日程表，哪里漏水贴哪里，贴完还要微笑说“收到”。',
        tags: ['流程补洞', '两边安抚', '微笑待机'],
      },
      summary:
        '你今天把候选人哄住了，把用人部门稳住了，把员工情绪接住了，还顺手把朋友鸽了。\n\n每个人都觉得你应该再多理解一下他。\n\n很好，HR 的一天又成功证明：你不是万能的，但大家会先假装你是。',
      fitReason:
        '今天还算扛住的地方：你能把难听的话翻译得不那么难听，也能让快散架的流程继续往前走。',
      riskReason:
        '今天最扎心的地方：你照顾了很多人的感受，但你的感受排在待办事项最后一行。',
      match: (s) => s.reputation <= 42 || (s.reputation < 50 && s.stress >= 68),
    },
    {
      id: 'empathy_fatigue',
      label: '情绪垃圾桶型 HR',
      episodeCoda:
        '你关掉电脑的那一刻，微信还在闪。\n\n员工、候选人、用人部门——所有人都在找你，但没人问你累不累。',
      punchline: '团队觉得你很会沟通，但没人问你累不累。',
      visual: {
        symbol: '桶',
        name: '情绪收纳桶',
        description: '一边接电话，一边安慰员工，表情还在线，内存已经快满了。',
        tags: ['接住情绪', '电话不断', '内心过载'],
      },
      summary:
        '你今天听了候选人的犹豫，员工的委屈，主管的压力，老板的指标。\n\n一天结束后，没有人问你：“那你还好吗？”\n\n系统没有崩，你快了。',
      fitReason:
        '今天还算扛住的地方：你能听见别人没直接说出口的压力，也没有立刻把人推开。',
      riskReason:
        '今天最扎心的地方：共情用多了，自己会变成情绪垃圾桶，还不一定有盖子。',
      match: (s) => s.stress >= 76 || (s.stress >= 62 && s.mood <= 36),
    },
    {
      id: 'boundary_holder',
      label: '夹层求生型 HR',
      episodeCoda:
        '你 18:30 走出办公楼，手机静音，表情平静。\n\n你知道明天还会有人觉得「就帮个小忙」，但你至少今晚还属于自己。',
      punchline: '你不是冷漠，你只是知道有些话说早了会炸。',
      visual: {
        symbol: '夹',
        name: '夹心求生人',
        description: '上面是老板，下面是员工，中间是你。每天的工作：让两边都别炸。',
        tags: ['上压下顶', '谨慎措辞', '夹缝呼吸'],
      },
      summary:
        '你今天没有把每个问题都做成“帮个忙”。\n\n有人会觉得你冷，有人会觉得你不够灵活。\n\n但你至少没有把保密信息当人情送出去，也没有把自己的生活完全交出去。',
      fitReason:
        '今天还算扛住的地方：你知道边界不是摆架子，是为了别让事情以后更难看。',
      riskReason:
        '今天最扎心的地方：守边界的人，常常要先承受别人失望的眼神。',
      match: (s) => s.reputation >= 60 && s.stress <= 60 && s.mood >= 42,
    },
    {
      id: 'organization_balancer',
      label: '微笑崩溃型 HR',
      episodeCoda:
        '晚上 10:18，你对着镜子练习了一下「收到」。\n\n表情很稳，内心消息已 99+。这一集，你活下来了，但下一集还没播。',
      punchline: '你脸上写着“收到”，心里写着“救命”。',
      visual: {
        symbol: '笑',
        name: '微笑乱码人',
        description: '表面稳定输出，内心消息刷屏。你看起来没崩，只是熟练地崩着。',
        tags: ['表面微笑', '内心乱码', '消息爆炸'],
      },
      summary:
        '你今天没有真正解决所有问题。\n\n候选人还在犹豫，员工还在难过，老板还要数字，朋友还在电影院门口看时间。\n\nHR 的一天很多时候就是这样：看起来在聊天，其实是在给组织漏水的地方贴胶带。',
      fitReason:
        '今天还算扛住的地方：你能接受事情没有标准答案，也能在乱局里先做一个不太坏的选择。',
      riskReason:
        '今天最扎心的地方：很多 HR 的工作，做对了没人发现，做慢了所有人都发现。',
      match: () => true,
    },
  ],
}
