/** HR 一日体验（固定分支，不接大模型） */
export const hrDayConfig = {
  id: 'hr',
  title: 'HR 的一天',
  subtitle: '体验一次真实 HR 工作日。上面要结果，下面要说法，中间的人要把边界守住。',
  startCta: '开始上班',
  endingHeadline: '你的 HR 一天结束了',
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
      messages: [
        {
          role: 'system',
          source: '用人部门群',
          text: '用人部门负责人：这个岗位空了两周了，老板在看，今天必须给结果。',
        },
        {
          role: 'system',
          source: '候选人微信',
          text: '不好意思，上午临时有事，面试能改到晚上吗？另外我手里还有一个录用通知。',
        },
      ],
      options: [
        {
          text: '先稳住候选人，重新协调面试官晚上面',
          nextSceneId: 'scene_2',
          effects: { stress: 16, reputation: 6, growth: 8, mood: -10 },
        },
        {
          text: '告诉用人部门候选人不稳定，先看备选人',
          nextSceneId: 'scene_2',
          effects: { stress: 6, reputation: 4, growth: 6, mood: -4 },
        },
        {
          text: '压候选人今天必须面，不然默认放弃',
          nextSceneId: 'scene_2',
          effects: { stress: 2, reputation: -12, growth: -6, mood: -8 },
        },
      ],
    },
    {
      id: 'scene_2',
      time: '10:47',
      messages: [
        {
          role: 'system',
          source: '面试官私聊',
          text: '我 11 点被拉去客户会了，面不了。你跟候选人说一下，后面再补。',
        },
        {
          role: 'system',
          source: '业务群',
          text: '负责人：别卡流程。这个人如果没了，你帮我解释给老板？',
        },
      ],
      options: [
        {
          text: '临时找备选面试官，保住今天流程',
          nextSceneId: 'scene_3',
          effects: { stress: 18, reputation: 8, growth: 10, mood: -12 },
        },
        {
          text: '如实改期，并把面试官时间冲突同步给用人部门',
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
      time: '14:08',
      messages: [
        {
          role: 'system',
          source: '员工私聊',
          text: '我其实不想把事情闹大，但我真的撑不住了。能不能先别让我主管知道？',
        },
        {
          role: 'system',
          source: '部门群',
          text: '该员工主管：下午帮我约他聊一下，最近状态不太对，别让团队受影响。',
        },
      ],
      options: [
        {
          text: '先接住情绪，约定哪些信息会保密、哪些必须升级',
          nextSceneId: 'scene_4',
          effects: { stress: 4, reputation: 12, growth: 12, mood: -2 },
        },
        {
          text: '建议员工直接跟主管摊开说',
          nextSceneId: 'scene_4',
          effects: { stress: -2, reputation: -8, growth: 4, mood: -8 },
        },
        {
          text: '马上同步给主管，避免管理风险',
          nextSceneId: 'scene_4',
          effects: { stress: 10, reputation: -16, growth: -4, mood: -16 },
        },
      ],
    },
    {
      id: 'scene_4',
      time: '16:32',
      messages: [
        {
          role: 'system',
          source: '临时会议',
          text: '老板：这轮绩效不能太难看，但奖金预算也不能超。低绩效比例你们 HR 把一下。',
        },
        {
          role: 'system',
          source: '用人部门负责人',
          text: '我们组今年很辛苦，不能太低。你们别只看表格，要看业务感受。',
        },
      ],
      options: [
        {
          text: '拿历史数据和预算限制，推动大家正式对齐',
          nextSceneId: 'scene_5',
          effects: { stress: 8, reputation: 14, growth: 12, mood: -4 },
        },
        {
          text: '先按老板口径调分布，员工沟通后面再补',
          nextSceneId: 'scene_5',
          effects: { stress: 14, reputation: -10, growth: -8, mood: -14 },
        },
        {
          text: '帮用人部门争取更好评级，同时提示预算风险',
          nextSceneId: 'scene_5',
          effects: { stress: 12, reputation: 4, growth: 8, mood: -8 },
        },
      ],
    },
    {
      id: 'scene_5',
      time: '18:46',
      messages: [
        {
          role: 'system',
          source: '人员调整会',
          text: '你刚听到名单：下午找你倾诉的那位员工，可能在下月岗位调整范围里。现在不能外传。',
        },
        {
          role: 'system',
          source: '员工私聊',
          text: '他又发来：我准备报个课程，想在公司再坚持半年。你觉得我还有机会吗？',
        },
      ],
      options: [
        {
          text: '提前暗示他多看机会，但不说名单',
          nextSceneId: '__end__',
          effects: { stress: 16, reputation: -8, growth: 8, mood: -18 },
        },
        {
          text: '严格保密，只回应当下表现和沟通建议',
          nextSceneId: '__end__',
          effects: { stress: 10, reputation: 10, growth: 10, mood: -12 },
        },
        {
          text: '转移话题，等正式通知再处理',
          nextSceneId: '__end__',
          effects: { stress: 6, reputation: -14, growth: -6, mood: -10 },
        },
      ],
    },
  ],
  endings: [
    {
      id: 'relationship_keeper',
      label: '关系维稳型',
      summary:
        '你一直在帮所有人把话说得没那么难听，把流程推进得没那么难看。但一天结束后，没有人真正问过你累不累。',
      fitReason:
        '如果你能在多人诉求之间保持耐心，并愿意承担大量看不见的沟通成本，HR 工作会让你理解一家公司真实运转的方式。',
      riskReason:
        '如果你习惯用讨好换和平，HR 工作的夹层压力会很快把你的情绪余额耗光。',
      match: (s) => s.reputation <= 42 || (s.reputation < 50 && s.stress >= 68),
    },
    {
      id: 'empathy_fatigue',
      label: '情绪消耗型',
      summary:
        '你接住了候选人、员工、用人部门和老板的情绪，却很难把自己的感受放进流程里。HR 最难的不是会聊天，而是聊天之后还要守住边界。',
      fitReason:
        '你适合需要高度共情和细腻判断的工作，尤其能听见别人没说出口的压力。',
      riskReason:
        '如果你没有清晰的信息边界和恢复方式，这份工作会让你把别人的焦虑带回家。',
      match: (s) => s.stress >= 76 || (s.stress >= 62 && s.mood <= 36),
    },
    {
      id: 'boundary_holder',
      label: '边界清晰型',
      summary:
        '你没有把每个问题都做成「人情题」。你尽量让业务、员工和规则在同一张桌上说话，这很慢，也很费力，但能减少后面的二次伤害。',
      fitReason:
        '你可能适合 HR 工作，因为你能承受不被所有人喜欢，也愿意把模糊的人情变成可解释的规则。',
      riskReason:
        '需要注意的是，过度强调边界也可能显得冷。HR 的专业感要和人的温度一起出现。',
      match: (s) => s.reputation >= 60 && s.stress <= 60 && s.mood >= 42,
    },
    {
      id: 'organization_balancer',
      label: '组织平衡型',
      summary:
        '你没有轻松解决任何一个问题，只是在组织、风险和人的感受之间留下了还算可解释的选择。HR 的一天很多时候就是这样：不漂亮，但要尽量不伤人。',
      fitReason:
        '如果你能接受结果常常延迟显现，并愿意在不完全清楚的情况下做判断，这个职业会训练你看见更大的系统。',
      riskReason:
        '如果你只想做清晰、确定、立刻有反馈的工作，HR 工作的模糊边界和多方压力会让你很难放松。',
      match: () => true,
    },
  ],
}
