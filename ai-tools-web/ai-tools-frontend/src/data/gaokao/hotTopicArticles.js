import { gaokaoHotTopics } from './hotTopics.js'

/**
 * @typedef {{
 *   slug: string,
 *   readMinutes: number,
 *   updatedAt: string,
 *   sections: { heading: string, body: string[] }[],
 *   takeaways: string[],
 *   relatedMajorIds: string[],
 *   relatedCareerIds: string[],
 * }} HotTopicArticle
 */

/** @type {Record<string, HotTopicArticle>} */
export const hotTopicArticles = {
  'ai-risk-majors': {
    slug: 'ai-risk-majors',
    readMinutes: 4,
    updatedAt: '2026-05',
    sections: [
      {
        heading: '先分清：被替代的是「岗位任务」，不是整个专业',
        body: [
          'AI 更擅长处理规则清晰、重复性高、可被标准化的工作片段。选专业时，真正要警惕的是：课程仍停在「背知识点 + 写八股」，却很少训练判断、沟通、跨学科协作的方向。',
          '很多专业不是「不能选」，而是要想清楚：你毕业后具体做哪一类岗位，这类岗位的核心动作会不会被工具快速覆盖。',
        ],
      },
      {
        heading: '风险相对更高的方向（需谨慎评估）',
        body: [
          '纯翻译、基础记账、模板化内容搬运、低门槛数据处理等——若学校培养仍停留在工具操作层，毕业后容易陷入价格战。',
          '「名字很热门、课程很空」的交叉专业：课程堆砌概念，却缺少项目实践与行业导师，也要警惕。',
        ],
      },
      {
        heading: '不是不能选，而是要选「AI 增强型」路径',
        body: [
          '计算机、信息管理、数据科学：重点看学校是否教工程化、产品思维与 AI 协作，而不是只会调包。',
          '法学、医学、教育：AI 辅助检索与文书，但责任认定、伦理与现场判断仍依赖人。',
          '设计、新媒体：工具能出图，审美、叙事与品牌理解仍是壁垒。',
        ],
      },
    ],
    takeaways: [
      '别只问「热不热」，要问「毕业后具体做什么动作」。',
      '优先选能积累判断力、协作与复杂问题拆解的专业。',
      '大学期间就要学会用 AI 提效，而不是回避 AI。',
    ],
    relatedMajorIds: ['computer-science', 'accounting', 'english', 'new-media'],
    relatedCareerIds: ['ai-app-dev', 'lawyer', 'new-media-operations'],
  },
  'family-caution': {
    slug: 'family-caution',
    readMinutes: 5,
    updatedAt: '2026-05',
    sections: [
      {
        heading: '普通家庭选专业，多算一笔「结构账」',
        body: [
          '除了兴趣，还要同时看：学制长短、实习资源、行业周期、地域就业市场、家庭可承受的时间成本。',
          '四年本科 + 二年硕士的路径，对很多家庭意味着更长的「只投入、未见回报」阶段，选之前要和父母坦诚沟通预期。',
        ],
      },
      {
        heading: '慎选信号（不是歧视，是现实约束）',
        body: [
          '极度依赖名校光环、但自己分数段只能进普通院校同类专业——要想好差异化出路（证书、项目、考研、转码等）。',
          '需要长期深造才有对口岗位（医学、部分理学），却对未来强度与收入预期不清晰。',
          '行业下行周期仍大举扩招的方向，毕业人数与岗位缺口不匹配。',
        ],
      },
      {
        heading: '更稳妥的策略',
        body: [
          '选「专业技能 + 可迁移能力」并重的专业：沟通、写作、数据分析、项目管理到哪里都需要。',
          '提前规划大二实习、竞赛或作品集，比大四临时抱佛脚有效得多。',
          '允许「先宽后窄」：大类招生、转专业、辅修，都是降低一次押错成本的方式。',
        ],
      },
    ],
    takeaways: [
      '家庭资源有限时，学制与现金流同样重要。',
      '普通院校更要靠项目与实习建立可信度。',
      '和父母对齐预期，比盲目冲热门更减压。',
    ],
    relatedMajorIds: ['clinical-medicine', 'finance', 'education', 'information-management'],
    relatedCareerIds: ['civil-servant', 'teacher', 'finance-practitioner'],
  },
  'liberal-arts-path': {
    slug: 'liberal-arts-path',
    readMinutes: 4,
    updatedAt: '2026-05',
    sections: [
      {
        heading: '文科生的核心资产是什么',
        body: [
          '表达、洞察、共情、组织与价值判断——这些在 AI 时代反而更稀缺，因为机器不擅长承担「责任」与「关系」。',
          '文科不是「只会写」，而是「能把复杂世界讲清楚、协调多方、推动共识」。',
        ],
      },
      {
        heading: '适合的方向举例',
        body: [
          '法学 / 公共管理：规则、谈判、合规与政策理解。',
          '新闻传播 / 新媒体：内容策略、品牌叙事、用户洞察。',
          '心理学 / 教育学：理解人、设计学习与支持系统。',
          '市场营销 / 国际商务：跨文化沟通与商业判断。',
        ],
      },
      {
        heading: '需要补强的技能',
        body: [
          '基础数据分析：会用表格、会看指标，写报告更有说服力。',
          '数字化工具：Notion、协作软件、AI 辅助写作与调研。',
          '作品集思维：公众号、策划案、竞赛、实习项目，都是证明。',
        ],
      },
    ],
    takeaways: [
      '文科出路在「表达 + 洞察 + 组织」，不是死背。',
      '主动补数据和工具，竞争力会明显提升。',
      '用作品和实习证明能力，比空喊兴趣更有用。',
    ],
    relatedMajorIds: ['law', 'new-media', 'psychology', 'education'],
    relatedCareerIds: ['lawyer', 'new-media-operations', 'teacher', 'hr'],
  },
  'future-hot-majors': {
    slug: 'future-hot-majors',
    readMinutes: 5,
    updatedAt: '2026-05',
    sections: [
      {
        heading: '未来 5–10 年：人口与产业结构在变',
        body: [
          '老龄化带来医疗、养老、康复、健康管理需求；数字化带来软件、数据、网络安全与 AI 应用岗位。',
          '新能源、高端制造、供应链本土化，需要工程 + 管理的复合人才。',
          '内容经济与出海业务，需要懂语言、文化与运营的国际化人才。',
        ],
      },
      {
        heading: '更可能「吃香」的能力组合',
        body: [
          '技术 + 业务：能把 AI 落到具体场景（金融风控、医疗辅助、教育个性化）。',
          '数据 + 决策：会分析、会沟通、敢对结果负责。',
          '创意 + 运营：会做内容，更懂增长与商业转化。',
        ],
      },
      {
        heading: '理性看待「热门」',
        body: [
          '热门专业若招生暴涨，四年后可能出现「人人都会、溢价下降」。',
          '真正稀缺的是：在同一届里，谁更有项目、实习、作品与跨界能力。',
        ],
      },
    ],
    takeaways: [
      '趋势看「人口 + 产业 + 技术」三条线。',
      '热门专业也要做差异化，不能躺赢。',
      '复合能力（专业 × 数据 × 沟通）更抗风险。',
    ],
    relatedMajorIds: ['ai-engineering', 'clinical-medicine', 'finance', 'computer-science'],
    relatedCareerIds: ['ai-app-dev', 'doctor', 'data-analyst'],
  },
}

export function getHotTopicArticle(slug) {
  return hotTopicArticles[slug] ?? null
}

export function listHotTopicsWithArticles() {
  return gaokaoHotTopics.map((t) => ({
    ...t,
    article: hotTopicArticles[t.slug] ?? null,
    hasArticle: Boolean(hotTopicArticles[t.slug]),
  }))
}
