/**
 * 职业倾向测试题库（12 题 × 4 选项）
 * 每选项对 5 维度加分：technical / communication / analysis / creative / organization
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
    question: '接到一个新任务时，你最先想做的是？',
    options: [
      { label: '搞清楚技术实现路径，动手搭原型或写脚本验证', scores: { technical: 3, analysis: 1 } },
      { label: '先找相关人同步背景、目标和各方期待', scores: { communication: 3, organization: 1 } },
      { label: '拆解指标、找历史数据或对标案例', scores: { analysis: 3, technical: 1 } },
      { label: '脑暴几种呈现方式，先画草图或写大纲', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 2,
    question: '在团队协作里，你更享受哪种状态？',
    options: [
      { label: '长时间专注一块复杂模块，少被打断', scores: { technical: 3, analysis: 1 } },
      { label: '跨部门拉通、对齐话术和推进节奏', scores: { communication: 3, organization: 2 } },
      { label: '做调研、建模型，用结论说服大家', scores: { analysis: 3, communication: 1 } },
      { label: '负责视觉/文案/演示，让方案「好懂又好记」', scores: { creative: 3, organization: 1 } },
    ],
  },
  {
    id: 3,
    question: '面对模糊需求时，你的本能反应更接近？',
    options: [
      { label: '先写个最小可行版本，用结果反推需求', scores: { technical: 2, analysis: 2 } },
      { label: '约会议，把干系人拉齐问清楚', scores: { communication: 3, organization: 1 } },
      { label: '列假设清单，一条条用数据验证或推翻', scores: { analysis: 3, organization: 1 } },
      { label: '做用户故事板或 Demo 稿，帮助大家一起想象', scores: { creative: 2, communication: 2 } },
    ],
  },
  {
    id: 4,
    question: '你更擅长哪种「输出物」？',
    options: [
      { label: '可运行的代码、脚本、自动化流水线', scores: { technical: 4 } },
      { label: '会议纪要、邮件、方案宣讲与谈判要点', scores: { communication: 3, organization: 1 } },
      { label: '分析报告、指标体系、决策备忘录', scores: { analysis: 4 } },
      { label: '海报、短视频脚本、PPT 叙事与品牌文案', scores: { creative: 4 } },
    ],
  },
  {
    id: 5,
    question: '学习新东西时，你更偏好的路径是？',
    options: [
      { label: '看文档 + 自己敲一遍，在错误里学会', scores: { technical: 3, analysis: 1 } },
      { label: '找人请教、旁听讨论，在对话里消化', scores: { communication: 3, creative: 1 } },
      { label: '系统读论文/行业报告，做笔记对比框架', scores: { analysis: 3, organization: 1 } },
      { label: '模仿优秀作品，边做边改出自己的风格', scores: { creative: 3, technical: 1 } },
    ],
  },
  {
    id: 6,
    question: '项目快上线时，你更愿意扛哪类压力？',
    options: [
      { label: '修 Bug、压测、兜底线上稳定性', scores: { technical: 4, organization: 1 } },
      { label: '对外解释进度、管理客户/老板预期', scores: { communication: 3, organization: 2 } },
      { label: '核对数据口径、验收逻辑是否自洽', scores: { analysis: 4 } },
      { label: '优化文案与体验细节，避免「翻车」舆情', scores: { creative: 2, communication: 2 } },
    ],
  },
  {
    id: 7,
    question: '哪种反馈会让你更有成就感？',
    options: [
      { label: '「系统很稳 / 性能很好 / 代码好维护」', scores: { technical: 4 } },
      { label: '「和你合作很省心，沟通特别清楚」', scores: { communication: 4 } },
      { label: '「结论靠谱，数据说服了我」', scores: { analysis: 4 } },
      { label: '「眼前一亮，这个创意/设计戳中我」', scores: { creative: 4 } },
    ],
  },
  {
    id: 8,
    question: '日常工作中，你更常处于哪种节奏？',
    options: [
      { label: '迭代开发、排期、Code Review、发版', scores: { technical: 2, organization: 2 } },
      { label: '电话/会议/拜访/群消息不断', scores: { communication: 3, organization: 1 } },
      { label: '独处思考、建表、写分析、做复盘', scores: { analysis: 3, technical: 1 } },
      { label: '追热点、改稿、多版本创意试错', scores: { creative: 3, organization: 1 } },
    ],
  },
  {
    id: 9,
    question: '做决策时你更依赖？',
    options: [
      { label: '工程约束、技术债与实现成本', scores: { technical: 2, analysis: 2 } },
      { label: '各方立场与关系，寻找可接受的折中', scores: { communication: 3, organization: 2 } },
      { label: '数据与逻辑链，尽量量化利弊', scores: { analysis: 3, organization: 1 } },
      { label: '用户情绪与品牌调性，直觉+审美', scores: { creative: 2, analysis: 1, communication: 1 } },
    ],
  },
  {
    id: 10,
    question: '你理想的一天更像？',
    options: [
      { label: '安静写代码或配环境，产出可交付增量', scores: { technical: 4 } },
      { label: '见客户/候选人/合作方，推进多线程事项', scores: { communication: 3, organization: 1 } },
      { label: '钻一个复杂问题，晚上写出清晰结论', scores: { analysis: 4 } },
      { label: '拍摄/设计/写稿，有可见的成品', scores: { creative: 4 } },
    ],
  },
  {
    id: 11,
    question: '你对「流程与规范」的态度是？',
    options: [
      { label: '愿意遵守，但常想能不能用工具自动化', scores: { technical: 3, organization: 1 } },
      { label: '擅长在流程里协调人，让流程真的跑起来', scores: { organization: 3, communication: 2 } },
      { label: '希望流程背后有数据与原因，否则难说服我', scores: { analysis: 3, organization: 1 } },
      { label: '流程要有空间给创意，讨厌僵化填表', scores: { creative: 3, communication: 1 } },
    ],
  },
  {
    id: 12,
    question: '三年后你更希望别人这样介绍你？',
    options: [
      { label: '「技术专家 / 架构或 AI 应用很熟」', scores: { technical: 3, analysis: 1 } },
      { label: '「很会连接资源、搞定复杂人际关系」', scores: { communication: 3, organization: 1 } },
      { label: '「洞察强，关键判断常问 TA」', scores: { analysis: 3, communication: 1 } },
      { label: '「作品出圈，风格一眼能认出」', scores: { creative: 4 } },
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
