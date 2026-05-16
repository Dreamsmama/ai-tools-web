/**
 * 专业方向库（高考模式输出，非志愿填报数据）
 * @typedef {'technical'|'communication'|'analysis'|'creative'|'organization'} CareerDimension
 * @typedef {{
 *   id: string,
 *   name: string,
 *   dimensions: CareerDimension[],
 *   futureDirection: string,
 *   aiRisk: string,
 *   aiRiskLevel: 'low'|'medium'|'high',
 *   careerIds: string[],
 *   caution?: string,
 * }} MajorProfile
 */

/** @type {MajorProfile[]} */
export const majorsCatalog = [
  {
    id: 'computer-science',
    name: '计算机',
    dimensions: ['technical', 'analysis'],
    futureDirection: '软件工程、AI 应用、数据平台、网络安全等方向持续需要「能把 AI 用起来」的工程人才。',
    aiRisk: '纯重复编码岗位被压缩，但架构、业务抽象、质量与 AI 协作能力反而更值钱。',
    aiRiskLevel: 'medium',
    careerIds: ['java-dev', 'frontend-dev', 'ai-app-dev', 'data-analyst'],
  },
  {
    id: 'information-management',
    name: '信息管理',
    dimensions: ['technical', 'organization'],
    futureDirection: '信息系统、数字化运营、企业数据治理与产品化信息管理岗位。',
    aiRisk: '流程性录入类工作减少，懂业务+系统的复合人更吃香。',
    aiRiskLevel: 'medium',
    careerIds: ['product-manager', 'data-analyst', 'project-manager'],
  },
  {
    id: 'psychology',
    name: '心理学',
    dimensions: ['communication', 'analysis'],
    futureDirection: '用户体验研究、组织发展、心理健康服务、教育与咨询等需「理解人」的场景。',
    aiRisk: '标准化测评可被工具辅助，深度访谈、伦理判断与危机干预仍依赖人。',
    aiRiskLevel: 'low',
    careerIds: ['hr', 'teacher'],
    caution: '若只冲「心理咨询师」单一路径，需提前了解执业门槛与长期投入。',
  },
  {
    id: 'finance',
    name: '金融学',
    dimensions: ['analysis', 'organization'],
    futureDirection: '投研、风控、金融科技、企业财务与资产管理等仍需要严谨数理与合规意识。',
    aiRisk: '基础报表与常规分析自动化，策略判断、合规与客户关系仍关键。',
    aiRiskLevel: 'medium',
    careerIds: ['finance', 'finance-practitioner', 'data-analyst'],
  },
  {
    id: 'new-media',
    name: '新媒体',
    dimensions: ['creative', 'communication'],
    futureDirection: '内容策划、品牌传播、短视频与社区运营、AIGC 内容工作流设计。',
    aiRisk: '低质搬运内容贬值，有审美、叙事与数据复盘能力者更易出头。',
    aiRiskLevel: 'medium',
    careerIds: ['new-media-operations', 'content-planner', 'e-commerce-operations'],
  },
  {
    id: 'law',
    name: '法学',
    dimensions: ['analysis', 'communication'],
    futureDirection: '律师、法务、合规、仲裁与公共政策相关岗位，重逻辑与表达。',
    aiRisk: '检索与文书初稿被 AI 加速，出庭、谈判与责任认定仍高度依赖人。',
    aiRiskLevel: 'low',
    careerIds: ['lawyer', 'civil-servant'],
  },
  {
    id: 'clinical-medicine',
    name: '临床医学',
    dimensions: ['analysis', 'technical'],
    futureDirection: '临床诊疗、医学研究、公共卫生与医疗管理，周期长但壁垒高。',
    aiRisk: '影像与辅助诊断被 AI 增强，诊疗决策、沟通与手术仍不可替代。',
    aiRiskLevel: 'low',
    careerIds: ['doctor'],
    caution: '学制长、强度大，需确认自己是否适应长期学习与高压环境。',
  },
  {
    id: 'education',
    name: '教育学',
    dimensions: ['communication', 'creative'],
    futureDirection: 'K12/职业教育、教研、培训产品设计与教育科技运营。',
    aiRisk: '标准化讲题与批改被辅助，班级管理、激励与个性化引导仍靠教师。',
    aiRiskLevel: 'low',
    careerIds: ['teacher'],
  },
  {
    id: 'civil-service-prep',
    name: '行政管理 / 公考方向',
    dimensions: ['organization', 'communication'],
    futureDirection: '公务员、事业单位、国企综合岗与政策执行类工作。',
    aiRisk: '材料起草效率提升，现场协调、责任落实与政治素养仍核心。',
    aiRiskLevel: 'low',
    careerIds: ['civil-servant', 'state-owned-enterprise'],
  },
  {
    id: 'architecture',
    name: '建筑设计',
    dimensions: ['creative', 'technical'],
    futureDirection: '建筑方案、城市规划、室内与可持续设计、BIM 数字化设计。',
    aiRisk: '效果图与常规方案生成加速，规范审查、现场协调与创意审美仍重要。',
    aiRiskLevel: 'medium',
    careerIds: ['ui-designer', 'project-manager'],
  },
  {
    id: 'game-design',
    name: '游戏设计',
    dimensions: ['creative', 'technical'],
    futureDirection: '关卡策划、系统策划、游戏 UX、引擎工具与电竞运营周边。',
    aiRisk: '资产生成提效，玩法创新、数值平衡与玩家社区仍依赖团队创造力。',
    aiRiskLevel: 'medium',
    careerIds: ['ui-designer', 'content-planner', 'frontend-dev'],
  },
  {
    id: 'ai-engineering',
    name: '人工智能',
    dimensions: ['technical', 'analysis'],
    futureDirection: '算法工程、AI 应用落地、智能体与工作流、行业大模型产品化。',
    aiRisk: '入门门槛抬高，「只会调 API」竞争力弱，工程+业务+评测闭环更稳。',
    aiRiskLevel: 'medium',
    careerIds: ['ai-app-dev', 'data-analyst', 'java-dev'],
  },
  {
    id: 'accounting',
    name: '会计学',
    dimensions: ['analysis', 'organization'],
    futureDirection: '审计、税务、管理会计与企业财务数字化。',
    aiRisk: '记账与报表自动化明显，复杂合规、判断与沟通仍需要人。',
    aiRiskLevel: 'high',
    careerIds: ['finance-practitioner', 'finance'],
    caution: '若排斥数字与细则，长期会比较吃力。',
  },
  {
    id: 'english',
    name: '英语 / 涉外方向',
    dimensions: ['communication', 'creative'],
    futureDirection: '翻译、国际商务、跨文化沟通、出海运营与内容本地化。',
    aiRisk: '基础翻译被工具冲击，高语境谈判、创意写作与领域专长仍值钱。',
    aiRiskLevel: 'high',
    careerIds: ['new-media-operations', 'sales'],
  },
  {
    id: 'pure-theory',
    name: '纯理论冷门基础学科',
    dimensions: ['analysis'],
    futureDirection: '科研、高校、交叉学科深造或转向应用型硕士。',
    aiRisk: '就业面窄时需提前规划深造或跨界技能，不宜「随大流」填报。',
    aiRiskLevel: 'high',
    careerIds: ['teacher'],
    caution: '除非真心热爱学术路径，否则不建议仅因「听起来高级」而选。',
  },
]

/** @type {Record<CareerDimension, string[]>} */
export const DIMENSION_MAJOR_IDS = {
  technical: [
    'computer-science',
    'ai-engineering',
    'information-management',
    'game-design',
    'architecture',
  ],
  communication: ['psychology', 'law', 'education', 'civil-service-prep', 'english', 'new-media'],
  analysis: [
    'finance',
    'clinical-medicine',
    'law',
    'psychology',
    'accounting',
    'computer-science',
  ],
  creative: ['new-media', 'game-design', 'architecture', 'education', 'english'],
  organization: [
    'civil-service-prep',
    'finance',
    'information-management',
    'accounting',
  ],
}

/** 与主维度弱相关、常作「慎选」提示 */
export const CAUTION_MAJOR_IDS = ['pure-theory', 'english', 'accounting']

export function getMajorById(id) {
  return majorsCatalog.find((m) => m.id === id) ?? null
}
