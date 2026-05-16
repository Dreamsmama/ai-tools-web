/** 医生的一天（职场人 · 职业体验馆） */
export const doctorDayConfig = {
  id: 'doctor',
  title: '医生的一天',
  subtitle: '门诊、急诊与病历——住院医师的一天，常常没有「按计划完成」。',
  startCta: '开始上班',
  endingHeadline: '你的医生一天结束了',
  defaultAtmosphere: 'dev-alert-desk',
  initialStats: { stress: 46, reputation: 54, growth: 30, mood: 46 },
  scenes: [
    {
      id: 'scene_1',
      time: '08:00',
      sceneTitle: '门诊加号',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '护士站', text: '主任：上午门诊已满，走廊还有 6 位患者要求加号。', tone: 'alert', moment: 'feishu-dot' },
        { role: 'system', source: '患者家属', text: '医生，我们从外地来的，能不能今天看上？' },
      ],
      options: [
        { text: '向主任申请加 2 个号，其余改下午', nextSceneId: 'scene_2', effects: { stress: 10, reputation: 10, growth: 8, mood: -6 } },
        { text: '先做急症评估，非急症改预约', nextSceneId: 'scene_2', effects: { stress: 6, reputation: 12, growth: 12, mood: -4 } },
        { text: '全部加号（自己节奏会被打乱）', nextSceneId: 'scene_2', effects: { stress: 18, reputation: 4, growth: 4, mood: -12 } },
      ],
    },
    {
      id: 'scene_2',
      time: '12:30',
      sceneTitle: '急诊会诊',
      atmosphere: 'dev-alert-desk',
      messages: [
        { role: 'system', source: '急诊科', text: '会诊：疑似肺栓塞，需要你们科意见。患者已在抢救室。', tone: 'call', moment: 'call-incoming' },
        { role: 'system', source: '护士', text: '您门诊还没结束，主任问谁能先去？' },
      ],
      options: [
        { text: '交接门诊给同事，立刻去急诊', nextSceneId: 'scene_3', effects: { stress: 14, reputation: 14, growth: 12, mood: -10 } },
        { text: '先远程看检验单，再决定是否去', nextSceneId: 'scene_3', effects: { stress: 8, reputation: 8, growth: 10, mood: -6 } },
        { text: '请二线值班医师先去，你收尾门诊', nextSceneId: 'scene_3', effects: { stress: 4, reputation: 4, growth: 6, mood: -2 } },
      ],
    },
    {
      id: 'scene_3',
      time: '17:00',
      sceneTitle: '病历质控',
      atmosphere: 'dev-meeting',
      messages: [
        { role: 'system', source: '质控科', text: '您昨日出院病历被抽中，诊断与医嘱时间线需说明。今日 18 点前提交。' },
        { role: 'system', source: '主任', text: '这个月再被扣分，科室排名会受影响。' },
      ],
      options: [
        { text: '停下手头事，优先写说明', nextSceneId: 'scene_4', effects: { stress: 10, reputation: 10, growth: 8, mood: -8 } },
        { text: '请管床护士一起核对时间线', nextSceneId: 'scene_4', effects: { stress: 6, reputation: 12, growth: 10, mood: -4 } },
        { text: '申请宽限到明早（可能被拒）', nextSceneId: 'scene_4', effects: { stress: 4, reputation: -6, growth: 4, mood: 0 } },
      ],
    },
    {
      id: 'scene_4',
      time: '21:40',
      sceneTitle: '夜班前',
      atmosphere: 'dev-night-office',
      messages: [
        { role: 'system', source: '值班表', text: '今晚你二线。明早 7 点交班，记得看 8 床术后情况。' },
        { role: 'system', source: '家人', text: '这周能休息一天吗？孩子想你了。', tone: 'life', moment: 'phone-vibrate' },
      ],
      options: [
        { text: '回一句周末尽量，继续准备交班', nextSceneId: '__end__', effects: { stress: 12, reputation: 8, growth: 6, mood: -14 } },
        { text: '协调同事换班（不一定成功）', nextSceneId: '__end__', effects: { stress: 6, reputation: 4, growth: 4, mood: -6 } },
        { text: '交班材料整理好再回电话', nextSceneId: '__end__', effects: { stress: 8, reputation: 10, growth: 8, mood: -8 } },
      ],
    },
  ],
  endings: [
    {
      id: 'clinical',
      label: '临床攻坚型医生',
      punchline: '你在混乱里仍能抓住病人的优先级。',
      summary: '临床医生需要责任心、体力与持续学习。AI 可辅助检索，但 bedside 判断无法替代。',
      fitReason: '急症与压力下决策较稳。',
      riskReason: '长期注意作息与支持系统，避免燃尽。',
      match: (s) => s.reputation >= 55 && s.stress >= 50,
    },
    {
      id: 'steady',
      label: '稳健执业型医生',
      punchline: '你知道病历和沟通，和手术一样重要。',
      summary: '你重视流程与质控，这在医疗体系里是长期安全的做法。',
      fitReason: '严谨与协作意识好。',
      riskReason: '可主动争取更多独立判断与操作机会。',
      match: () => true,
    },
  ],
}
