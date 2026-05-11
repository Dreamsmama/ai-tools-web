/**
 * 职业倾向测试题库（12 题 × 4 选项）
 * 每选项对 5 维度加分：technical / communication / analysis / creative / organization
 * 题干偏日常、好理解，不依赖互联网或特定行业黑话。
 */

/** @typedef {'technical'|'communication'|'analysis'|'creative'|'organization'} CareerDimension */

/**
 * @typedef {{ label: string, scores: Partial<Record<CareerDimension, number>> }} CareerOption
 * @typedef {{ id: number, question: string, options: CareerOption[] }} CareerQuestion
 */

/** @type {CareerQuestion[]} */
export const careerTestQuestions = [
  {
    id: 1,
    question: '老师或老板布置了一件你没做过的事，你第一反应更接近？',
    options: [
      { label: '先自己查资料、动手试一试，错了再改', scores: { technical: 3, analysis: 1 } },
      { label: '先找懂的人问清楚，再动手', scores: { communication: 3, organization: 1 } },
      { label: '先想清楚目标、步骤和可能的风险', scores: { analysis: 3, organization: 1 } },
      { label: '先想几种有意思的做法，选最想试的那个', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 2,
    question: '周末有一段完整空闲时间，你更可能选哪种？',
    options: [
      { label: '研究一个小东西：修家电、装软件、做手工模型等', scores: { technical: 3, analysis: 1 } },
      { label: '约朋友见面聊天，或线上聊很久', scores: { communication: 4 } },
      { label: '整理账单、做预算表，或玩需要动脑的策略游戏', scores: { analysis: 3, organization: 1 } },
      { label: '拍照、画画、写东西、剪一段小视频', scores: { creative: 4 } },
    ],
  },
  {
    id: 3,
    question: '几个人一起做事，意见不一时，你更倾向？',
    options: [
      { label: '用事实、例子说明「哪种更行得通」', scores: { technical: 1, analysis: 3 } },
      { label: '多听几方说法，帮忙找大家都能接受的折中', scores: { communication: 3, organization: 2 } },
      { label: '把利弊一条条写出来，再一起选', scores: { analysis: 3, organization: 1 } },
      { label: '提议换个新点子，说不定比原来两个都好', scores: { creative: 2, communication: 2 } },
    ],
  },
  {
    id: 4,
    question: '下面哪类事做完，你最常有「做对了」的感觉？',
    options: [
      { label: '把一个东西弄明白了、弄好了，别人用起来省心', scores: { technical: 4 } },
      { label: '把误会聊开了，或把关系缓和了', scores: { communication: 4 } },
      { label: '把一件复杂的事理清楚，别人一看就懂', scores: { analysis: 4 } },
      { label: '做出一个好看、好玩或让人眼前一亮的成品', scores: { creative: 4 } },
    ],
  },
  {
    id: 5,
    question: '学一样完全不会的新技能（比如做菜、乐器、办公软件），你更习惯？',
    options: [
      { label: '跟着视频一步步做，多练几遍形成手感', scores: { technical: 3, organization: 1 } },
      { label: '找会的人带一带，边问边学', scores: { communication: 3, creative: 1 } },
      { label: '先看几本教程或笔记，搞懂原理再练', scores: { analysis: 3, organization: 1 } },
      { label: '先模仿喜欢的作品，再慢慢改成自己的风格', scores: { creative: 3, technical: 1 } },
    ],
  },
  {
    id: 6,
    question: '明天就要交稿 / 交作业 / 交报告，时间很紧，你更可能？',
    options: [
      { label: '先攻克最难的那一块，保证核心能交', scores: { technical: 2, analysis: 2 } },
      { label: '先跟老师或同伴说清楚进度，争取理解或分工', scores: { communication: 3, organization: 1 } },
      { label: '先列提纲和数据，避免写到一半发现逻辑不通', scores: { analysis: 3, organization: 2 } },
      { label: '先定一个整体风格或故事线，再往里填内容', scores: { creative: 2, organization: 2 } },
    ],
  },
  {
    id: 7,
    question: '别人夸你时，下面哪句最让你心里舒服？',
    options: [
      { label: '「这事交给你我放心，靠谱」', scores: { technical: 2, organization: 2 } },
      { label: '「跟你说话不累，你听得懂别人要什么」', scores: { communication: 4 } },
      { label: '「你想得细，一说我就明白了」', scores: { analysis: 4 } },
      { label: '「你有想法，做出来和别人不一样」', scores: { creative: 4 } },
    ],
  },
  {
    id: 8,
    question: '下面哪种日常节奏，你更不觉得累？（可以想学习或打工）',
    options: [
      { label: '长时间专心做一件事，偶尔才被打断', scores: { technical: 3, analysis: 1 } },
      { label: '电话、消息、见面穿插进行，一天见很多人', scores: { communication: 3, organization: 1 } },
      { label: '一个人对着材料、数字或题目琢磨很久', scores: { analysis: 3, technical: 1 } },
      { label: '改一版又一版，直到看起来顺眼、读起来顺耳', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 9,
    question: '要做一个决定（比如选课、换工作、买大件），你更依赖？',
    options: [
      { label: '现实条件：时间、钱、体力能不能撑住', scores: { technical: 1, analysis: 2, organization: 2 } },
      { label: '家人朋友的意见和长期相处是否舒服', scores: { communication: 3, analysis: 1 } },
      { label: '查资料、对比数据，想清楚再定', scores: { analysis: 3, organization: 1 } },
      { label: '直觉和喜好：喜不喜欢、愿不愿意长期做', scores: { creative: 2, analysis: 1, communication: 1 } },
    ],
  },
  {
    id: 10,
    question: '如果可以自由安排「理想的一天」，更像下面哪一种？',
    options: [
      { label: '安静做事，结束时手里有一件具体成果', scores: { technical: 3, organization: 1 } },
      { label: '见不同的人、聊不同的事，信息量很大', scores: { communication: 3, creative: 1 } },
      { label: '读、想、写，把一个问题想透并记下来', scores: { analysis: 4 } },
      { label: '创作或布置一样东西，拍照留念也很开心', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 11,
    question: '对于「规矩、流程、表格」这类东西，你更接近？',
    options: [
      { label: '愿意遵守，但会琢磨有没有更省事的办法', scores: { technical: 3, organization: 1 } },
      { label: '愿意带头提醒大家按流程来，少出岔子', scores: { organization: 3, communication: 2 } },
      { label: '希望知道「为什么这样定」，才更愿意照做', scores: { analysis: 3, organization: 1 } },
      { label: '太死板会难受，希望留一点自由发挥的空间', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 12,
    question: '想象一下几年后的你，你最希望别人用哪句话形容你？',
    options: [
      { label: '「动手能力强，难一点的事也能搞定」', scores: { technical: 3, analysis: 1 } },
      { label: '「人缘好，难事找 TA 协调会顺很多」', scores: { communication: 3, organization: 1 } },
      { label: '「脑子清楚，大事问 TA 心里更有底」', scores: { analysis: 3, communication: 1 } },
      { label: '「有风格，一看就知道是 TA 做的」', scores: { creative: 4 } },
    ],
  },
]

export const DIMENSION_ORDER = /** @type {const} */ ([
  'technical',
  'communication',
  'analysis',
  'creative',
  'organization',
])

export const dimensionLabels = {
  technical: '技术执行型',
  communication: '沟通协调型',
  analysis: '分析研究型',
  creative: '创意表达型',
  organization: '组织推进型',
}
