/**
 * 职业观察库：25 个职业详情（前端 Mock）
 * @typedef {{
 *   id: string,
 *   name: string,
 *   libraryTag: string,
 *   libraryTeaser: string,
 *   oneLineTruth: string,
 *   realWork: string,
 *   scenarios: string[],
 *   suitableFor: string,
 *   notSuitableFor: string,
 *   aiImpact: string,
 *   aiEraSummary: string,
 *   learningTips: string,
 * }} CareerDetail
 */

/** @type {CareerDetail[]} */
const CATALOG = [
  {
    id: 'java-dev',
    name: 'Java开发',
    libraryTag: '技术',
    libraryTeaser: '企业级后端、微服务与中间件常见入口方向。',
    oneLineTruth: '多数时间在「把业务规则变成可靠、可维护的服务」。',
    realWork:
      '编写与评审后端代码、设计接口与数据模型、排查线上问题、参与技术方案评审；与产品、测试对齐需求边界与发布节奏。',
    scenarios: ['需求评审与估时', '接口联调与 Code Review', '线上告警定位与 hotfix', '性能与容量评估'],
    suitableFor:
      '喜欢抽象与工程纪律、能接受较长迭代周期；愿意读文档、写测试、对稳定性负责的人。',
    notSuitableFor:
      '极度排斥重复排错、讨厌规范与流程；只想「快速出活」不愿维护存量系统的人。',
    aiImpact:
      'AI 可辅助生成样板代码、单测草稿与文档摘要，但架构取舍、并发与一致性、线上排障仍高度依赖经验。工程师更多转向「定义边界、审模型输出、保障质量」。',
    aiEraSummary: '样板代码与文档加速，架构与线上问题仍靠人兜底。',
    learningTips:
      '巩固语言与 JVM/框架基础；做一个带登录、权限、支付的完整项目；学习单元测试与常见中间件（缓存、消息队列）。',
  },
  {
    id: 'frontend-dev',
    name: '前端开发',
    libraryTag: '技术',
    libraryTeaser: '把交互与视觉落成可访问、可性能优化的 Web 体验。',
    oneLineTruth: '在「浏览器/跨端能力」与「产品体验」之间不断折中。',
    realWork:
      '实现页面与组件、处理状态管理与性能（首屏、包体、渲染）、对接接口与埋点；与设计师、产品沟通还原度与边界情况。',
    scenarios: ['组件库与主题迭代', '复杂表单与可视化', '兼容与无障碍修复', '构建与发布流水线协作'],
    suitableFor:
      '对视觉敏感、愿意抠细节；喜欢即时反馈（改代码立刻看到效果）；能接受技术栈较快更新的人。',
    notSuitableFor:
      '完全不想关心 UI/交互；对「像素级还原」极度不耐烦；排斥工程化（构建、规范）的人。',
    aiImpact:
      'AI 可生成组件草稿与样式建议，但跨端兼容、性能瓶颈、复杂交互与可维护性仍需前端判断与验证。',
    aiEraSummary: 'UI 草稿更快，兼容与性能仍是硬功夫。',
    learningTips:
      '系统学 HTML/CSS/JS 与现代框架；用 Lighthouse 与真实设备练性能；读开源组件库源码理解设计思路。',
  },
  {
    id: 'qa-engineer',
    name: '测试工程师',
    libraryTag: '技术',
    libraryTeaser: '把风险前置，用策略与工具守住质量底线。',
    oneLineTruth: '你不是「点点点」，而是「定义什么叫做好了」。',
    realWork:
      '编写测试用例与自动化、参与需求可测性评审、推动缺陷闭环与回归策略；与研发协作定位问题根因。',
    scenarios: ['版本回归与发布评审', '自动化流水线维护', '探索性测试发现边界 bug', '线上问题复盘'],
    suitableFor:
      '严谨、爱找反例；愿意理解业务规则与系统边界；对「质量责任」有认同感的人。',
    notSuitableFor:
      '只接受机械重复、不愿学习自动化与业务；把测试当成「背锅」而非风险合伙人的人。',
    aiImpact:
      'AI 可生成用例初稿与测试数据，但风险建模、优先级、验收标准与线上事故复盘仍依赖测试思维。',
    aiEraSummary: '用例与数据生成提效，风险判断仍靠人。',
    learningTips:
      '学接口测试与一门脚本语言；了解 CI/CD；从业务路径出发设计「最小高价值」用例集。',
  },
  {
    id: 'ai-app-dev',
    name: 'AI应用开发',
    libraryTag: '技术',
    libraryTeaser: '把模型能力产品化：编排、RAG、评测与护栏。',
    oneLineTruth: '你在搭「能安全上线的 AI 功能」，而不是只调参玩 Demo。',
    realWork:
      '设计 Prompt/工具链、搭建 RAG 与评测集、处理延迟成本与安全合规；与产品定义「可接受失败」的体验。',
    scenarios: ['原型到 PoC', '检索质量与引用展示', '提示词与系统消息迭代', '监控与降级策略'],
    suitableFor:
      '对 LLM 能力边界好奇；愿意同时写代码与做实验记录；能接受快速试错与文档化的人。',
    notSuitableFor:
      '只想「一句话出奇迹」不愿评测；排斥数据与隐私约束；不承担线上后果的人。',
    aiImpact:
      '岗位本身就是 AI 落地前沿：重复实验可由工具辅助，但场景抽象、评测与安全策略是核心竞争力。',
    aiEraSummary: '实验加速，上线与安全仍要工程化负责。',
    learningTips:
      '掌握一门后端语言与向量检索基础；做一个小 RAG 项目并写评测表；学习基础安全（注入、越权、泄露）。',
  },
  {
    id: 'devops-engineer',
    name: '运维工程师',
    libraryTag: '技术',
    libraryTeaser: '保障可用性、成本与发布效率的「系统守门人」。',
    oneLineTruth: '别人睡得好不好，常常取决于你值班那天的预案。',
    realWork:
      '维护监控告警、容量与成本、发布与回滚、基础设施即代码；推动标准化与自动化减少人为失误。',
    scenarios: ['大促或发版窗口值守', '故障应急与事后复盘', 'K8s/网络/存储排障', '安全补丁与合规审计配合'],
    suitableFor:
      '冷静、抗压；喜欢把混乱流程自动化；愿意写 runbook 与沉淀知识的人。',
    notSuitableFor:
      '排斥值班与应急；不愿读日志与文档；把运维当成纯体力活的人。',
    aiImpact:
      'AI 可辅助解析日志摘要、生成变更说明与脚本草稿，但线上因果链判断与变更风险控制仍靠人。',
    aiEraSummary: '日志与脚本草稿更快，变更与应急仍靠经验。',
    learningTips:
      '学 Linux、网络与一门 IaC 工具；从「可观测性三件套」入手；刻意练习故障演练（game day）。',
  },
  {
    id: 'product-manager',
    name: '产品经理',
    libraryTag: '组织',
    libraryTeaser: '在模糊里定义问题，在约束里做取舍。',
    oneLineTruth: '你不是「只写 PRD」，而是「为结果定义成功标准」。',
    realWork:
      '用户与业务调研、需求优先级、原型与流程设计、跨团队推进里程碑；上线后看数据与反馈迭代。',
    scenarios: ['需求评审与砍需求', 'AB 实验与指标复盘', '研发测试 UAT 对齐', '对外与客户/合作方沟通'],
    suitableFor:
      '强同理与结构化表达并存；能接受不确定性与多方压力；愿意对取舍负责的人。',
    notSuitableFor:
      '只想执行指令不愿拍板；极度回避冲突；不承担结果指标的人。',
    aiImpact:
      'AI 可加速竞品扫描、原型文案与用户故事草稿，但优先级、伦理边界与组织协同仍依赖 PM。',
    aiEraSummary: '调研与文档加速，取舍与协同仍是核心。',
    learningTips:
      '练「问题—假设—验证」闭环；学基础 SQL 与埋点；跟完一个完整版本从立项到复盘。',
  },
  {
    id: 'project-manager',
    name: '项目经理',
    libraryTag: '组织',
    libraryTeaser: '让复杂交付「按时、按范围、按质量」落地。',
    oneLineTruth: '你的产品是「可控的交付过程」。',
    realWork:
      '制定计划与里程碑、识别风险与依赖、组织站会与汇报、推动问题解决与范围变更管理。',
    scenarios: ['多乙方/多部门协同', '里程碑延误纠偏', '资源冲突协调', '项目收尾与经验沉淀'],
    suitableFor:
      '细心、强推进；擅长把模糊拆成任务表；能接受大量同步沟通的人。',
    notSuitableFor:
      '讨厌流程与文档；不愿处理人际摩擦；对 deadline 无感的人。',
    aiImpact:
      'AI 可生成周报、风险清单模板与会议纪要草稿，但关键路径判断与干系人管理仍靠人。',
    aiEraSummary: '文书与模板提效，风险与干系人仍靠人。',
    learningTips:
      '学 WBS、关键路径与敏捷基础；练一次真实项目的风险登记册；提升会议效率与决策记录习惯。',
  },
  {
    id: 'data-analyst',
    name: '数据分析',
    libraryTag: '分析',
    libraryTeaser: '用数据讲清业务发生了什么、为什么、怎么办。',
    oneLineTruth: '指标不是数字，是「对行为的共同定义」。',
    realWork:
      '清洗与建模、搭建报表与看板、专题分析（漏斗、留存、归因）、为运营与产品提供决策建议。',
    scenarios: ['活动复盘', '指标体系搭建', '异常波动排查', '实验设计与效果评估'],
    suitableFor:
      '喜欢追问「口径是什么」；愿意和业务反复对齐；能接受 SQL/表格长时间工作的人。',
    notSuitableFor:
      '讨厌脏数据与反复改口径；只想画炫酷图不愿理解业务的人。',
    aiImpact:
      '自然语言取数、代码与图表草稿更快，但指标定义、因果谨慎性与业务翻译仍不可替代。',
    aiEraSummary: '取数与草稿更快，口径与因果仍要人把关。',
    learningTips:
      '精通 SQL 与可视化；学统计基础与实验设计；每次分析写清假设、结论与局限。',
  },
  {
    id: 'product-analyst',
    name: '产品分析',
    libraryTag: '分析',
    libraryTeaser: '把用户行为与功能表现翻译成产品策略。',
    oneLineTruth: '你在连接「数据事实」与「产品动作」。',
    realWork:
      '埋点方案、行为路径分析、功能渗透率与留存拆解、竞品与用户细分；输出可执行的产品建议。',
    scenarios: ['新功能上线评估', '用户分群与画像', '漏斗诊断', '与 PM/研发对齐埋点缺陷'],
    suitableFor:
      '既懂一点技术又懂业务语言；喜欢从数据里讲故事的人。',
    notSuitableFor:
      '排斥细节与埋点治理；不愿跨团队沟通；只做表不做结论的人。',
    aiImpact:
      'AI 可辅助生成分析框架与 SQL 草稿，但埋点质量、业务语境与策略取舍仍靠分析师。',
    aiEraSummary: '框架与查询草稿提效，语境与策略仍靠人。',
    learningTips:
      '熟悉事件模型与埋点规范；练把结论写成「可执行三句话」；跟一次真实上线前后对比。',
  },
  {
    id: 'hr',
    name: 'HR',
    libraryTag: '沟通',
    libraryTeaser: '组织的人才入口、文化与制度枢纽之一。',
    oneLineTruth: '你在处理「人对组织的期待」与「组织对规则的坚持」。',
    realWork:
      '招聘全流程、入职与培训、绩效与员工关系、制度落地与合规沟通；支持业务管理者做人事决策。',
    scenarios: ['面试与人才评估', '薪酬绩效沟通', '员工冲突调解', '政策更新宣导'],
    suitableFor:
      '耐心、保密意识强；擅长倾听与边界感；对组织公平敏感的人。',
    notSuitableFor:
      '极度回避困难对话；把 HR 当成纯行政；缺乏同理与原则平衡的人。',
    aiImpact:
      '简历初筛、JD 润色、培训材料草稿可加速，但敏感沟通、判断与合规仍必须人工。',
    aiEraSummary: '文书与初筛提效，敏感沟通与判断仍靠人。',
    learningTips:
      '学劳动法基础与面试技巧；练习结构化记录与反馈；理解业务岗位画像而非只看关键词。',
  },
  {
    id: 'sales',
    name: '销售',
    libraryTag: '沟通',
    libraryTeaser: '把价值讲进客户心智，并推动成交与回款。',
    oneLineTruth: '业绩背后，是信任节奏的设计。',
    realWork:
      '线索跟进、需求挖掘、方案呈现、商务谈判、合同与回款协调；维护客户预期与内部交付对齐。',
    scenarios: ['客户拜访与演示', '招投标与报价', '异议处理', '与售前售后协同'],
    suitableFor:
      '抗压、目标感强；擅长建立关系与快速学习行业知识的人。',
    notSuitableFor:
      '极度内向且不愿练习表达；排斥指标压力；不愿承担客户关系波动的人。',
    aiImpact:
      '客户资料整理、邮件草稿与话术变体可加速，但信任建立、谈判与临场判断仍靠人。',
    aiEraSummary: '资料与话术草稿更快，信任与谈判仍靠人。',
    learningTips:
      '刻意练习提问与倾听；复盘每次拜访的「下一步」；学习基础财务与合同条款。',
  },
  {
    id: 'customer-success',
    name: '客户成功',
    libraryTag: '沟通',
    libraryTeaser: '让客户「用得好、留得住、扩得开」。',
    oneLineTruth: '你是续费与口碑的「长期关系负责人」。',
    realWork:
      ' onboarding、健康度监控、培训与最佳实践输出、续约与增购机会识别；反馈产品问题给内部。',
    scenarios: ['QBR 业务回顾', '流失预警干预', '大客户护航', '跨产品线的价值扩展'],
    suitableFor:
      '服务心态与商业嗅觉兼具；愿意深耕客户行业与使用数据的人。',
    notSuitableFor:
      '只想一次性交付不愿长期跟进；排斥数据与流程化客户管理的人。',
    aiImpact:
      'AI 可总结用量数据、生成培训提纲与邮件草稿，但关系修复与策略性对话仍靠人。',
    aiEraSummary: '用量总结与材料草稿更快，关系与策略仍靠人。',
    learningTips:
      '学客户旅程与关键里程碑；练把「使用数据」翻译成业务语言；建立客户档案与风险清单习惯。',
  },
  {
    id: 'headhunter',
    name: '猎头',
    libraryTag: '沟通',
    libraryTeaser: '在人才市场「匹配稀缺能力与机会」。',
    oneLineTruth: '你在同时服务「候选人职业生涯」与「客户组织需求」。',
    realWork:
      '寻访与评估候选人、mapping、面试辅导、薪酬谈判与入职跟进；维护行业人脉与信任。',
    scenarios: ['高管/稀缺岗交付', '候选人转介绍', '客户岗位画像对齐', 'offer 谈判'],
    suitableFor:
      '外向、强同理与保密意识；能接受高波动与多线程的人。',
    notSuitableFor:
      '排斥电话与社交；不愿理解行业细节；短期功利损害信任的人。',
    aiImpact:
      '人才清单整理、邮件与职位描述草稿可加速，但判断动机、撮合时机与信任仍靠人。',
    aiEraSummary: '信息整理加速，动机判断与撮合仍靠人。',
    learningTips:
      '深耕 1–2 个细分职能；练习候选人深度访谈；学习薪酬结构与职业发展路径。',
  },
  {
    id: 'new-media-operations',
    name: '新媒体运营',
    libraryTag: '创意',
    libraryTeaser: '在平台规则里做增长与内容复利。',
    oneLineTruth: '你是「算法、用户与品牌调性」的三方翻译。',
    realWork:
      '选题策划、脚本与图文、发布排期、评论区运营、数据分析与迭代；联动投放与活动。',
    scenarios: ['热点响应', '直播/短视频复盘', '账号人设维护', '跨平台分发'],
    suitableFor:
      '网感好、表达欲强；能接受数据反馈快速改稿的人。',
    notSuitableFor:
      '排斥公开表达与反复试错；不愿看数据；对平台规则极度抵触的人。',
    aiImpact:
      '标题/脚本/封面文案草稿可批量生成，但选题判断、真实人设与舆情风险仍靠人。',
    aiEraSummary: '量产草稿容易，选题与人设仍靠人。',
    learningTips:
      '建立选题库与复盘表；学基础剪辑与封面设计；研究平台机制而非只追热点。',
  },
  {
    id: 'e-commerce-operations',
    name: '电商运营',
    libraryTag: '组织',
    libraryTeaser: '用流量、转化与供应链协同把货卖出去。',
    oneLineTruth: '你在管一条「从曝光到签收」的链条。',
    realWork:
      '商品与页面优化、活动与优惠券、推广投放协同、客服与物流异常处理；盯 GMV、转化与库存。',
    scenarios: ['大促筹备', '爆款断货预案', '差评与舆情处理', '竞品与价位监控'],
    suitableFor:
      '结果导向、细心；能接受快节奏与多线程的人。',
    notSuitableFor:
      '排斥数据与表格；不愿处理售后琐碎；对供应链无耐心的人。',
    aiImpact:
      '商品文案、活动页草稿与客服话术模板可加速，但定价策略、库存博弈与平台关系仍靠人。',
    aiEraSummary: '文案与模板提效，策略与博弈仍靠人。',
    learningTips:
      '从一个小店或模拟项目跑通全链路；学基础投放与转化漏斗；关注用户体验与复购。',
  },
  {
    id: 'ui-designer',
    name: 'UI设计',
    libraryTag: '创意',
    libraryTeaser: '让界面既好看又可实现、可访问。',
    oneLineTruth: '你在为「第一眼信任」与「长期使用疲劳」负责。',
    realWork:
      '界面与组件设计、设计规范、切图与走查、与研发还原度对齐；参与用户测试与迭代。',
    scenarios: ['设计系统迭代', '复杂信息架构', '多状态与空页面', '无障碍与对比度'],
    suitableFor:
      '审美与逻辑并存；愿意反复打磨细节；能接受需求变更的人。',
    notSuitableFor:
      '只追求「好看截图」不考虑实现；极度排斥规范与组件化的人。',
    aiImpact:
      'AI 可生成风格 moodboard 与初稿，但信息层级、品牌一致性与可用性走查仍靠设计师。',
    aiEraSummary: '灵感与初稿更快，层级与一致性仍靠人。',
    learningTips:
      '系统学排版与色彩；用真实项目练组件思维；跟研发做一次完整走查清单。',
  },
  {
    id: 'content-planner',
    name: '内容策划',
    libraryTag: '创意',
    libraryTeaser: '用叙事把品牌与用户连接起来。',
    oneLineTruth: '你在设计「人们为什么愿意看下去」。',
    realWork:
      '内容策略、栏目规划、脚本与专题结构、跨平台分发节奏；与法务/品牌/销售对齐口径。',
    scenarios: ['campaign 全案', '系列深度稿', '代言人/合作内容', '舆情口径预案'],
    suitableFor:
      '文字敏感、结构感强；愿意理解商业目标与用户情绪的人。',
    notSuitableFor:
      '排斥修改与协同；只想自嗨表达不顾转化的人。',
    aiImpact:
      '大纲与多版本文案草稿更快，但叙事角度、品牌风险与「一句话立场」仍靠策划。',
    aiEraSummary: '大纲与多版本更快，立场与风险仍靠人。',
    learningTips:
      '建立选题与结构模板库；学基础传播学与案例拆解；练习把 KPI 翻译成内容指标。',
  },
  {
    id: 'admin',
    name: '行政',
    libraryTag: '组织',
    libraryTeaser: '让组织日常运转「有秩序、有温度」。',
    oneLineTruth: '你是「大家习以为常但离不开」的那条线。',
    realWork:
      '办公环境、采购与资产、会议与差旅、制度流程、活动后勤；处理突发行政问题。',
    scenarios: ['年会与团建', '访客与接待', '办公搬迁', '费用与供应商对账'],
    suitableFor:
      '细致、服务意识强；擅长多线程与应急；对成本敏感的人。',
    notSuitableFor:
      '排斥琐碎与重复；不愿做服务者角色；对流程与合规无感的人。',
    aiImpact:
      '行程、通知、表格与清单草稿可自动化，但现场协调、敏感人际与突发判断仍靠人。',
    aiEraSummary: '文书清单自动化，现场与关系仍靠人。',
    learningTips:
      '练时间管理与优先级；学采购与供应商沟通；沉淀 SOP 与联系人网络。',
  },
  {
    id: 'finance',
    name: '财务',
    libraryTag: '分析',
    libraryTeaser: '用数字守住公司「真实经营状况」。',
    oneLineTruth: '你不是只贴发票，你在维护「信任与合规」的底线。',
    realWork:
      '核算、报表、预算与现金流管理、税务与审计配合、经营分析支持管理层决策。',
    scenarios: ['月结与关账', '预算滚动预测', '费用与合同审核', '投融资材料支持'],
    suitableFor:
      '严谨、对数字敏感；愿意长期积累专业资质与行业经验的人。',
    notSuitableFor:
      '粗心、排斥规则；不愿持续学习政策变化的人。',
    aiImpact:
      '票据识别、对账草稿与报表模板可加速，但会计判断、税务边界与内控责任仍靠人。',
    aiEraSummary: '对账与模板加速，判断与内控仍靠人。',
    learningTips:
      '打好会计基础与 Excel/财务软件；理解业务语言；尽早了解内控与审计流程。',
  },
  {
    id: 'doctor',
    name: '医生',
    libraryTag: '医疗',
    libraryTeaser: '临床判断、沟通与规范并重的高责任专业岗。',
    oneLineTruth: '你在「证据、风险与患者信任」之间做连续决策。',
    realWork:
      '问诊查体、辅助检查判读、诊断与治疗方案、病历与知情同意、多学科会诊与交接班；值班应对急症与突发病情变化。',
    scenarios: ['门诊高密度接诊', '手术或操作日', '夜班急诊分诊', '疑难病例讨论与转诊'],
    suitableFor:
      '能承受不确定性与高压；严谨、同理心强；愿意终身学习指南与科研进展的人。',
    notSuitableFor:
      '排斥夜班与情绪劳动；无法面对病痛与死亡；不愿为资质、规培与文书付出长期成本的人。',
    aiImpact:
      '影像与病理辅助判读、病历结构化与文献摘要可提效，但床旁综合判断、伦理沟通与操作责任仍高度依赖医生。',
    aiEraSummary: '辅助判读与文书提效，决策与责任仍靠人。',
    learningTips:
      '夯实生理病理与循证医学；练结构化问诊与鉴别诊断；尽早熟悉指南更新节奏与医患沟通边界。',
  },
  {
    id: 'lawyer',
    name: '律师',
    libraryTag: '专业服务',
    libraryTeaser: '用规则与论证帮客户管理风险与争取权益。',
    oneLineTruth: '你在把「事实、证据与条文」翻译成可执行的行动方案。',
    realWork:
      '事实梳理、法律检索、文书起草与修订、谈判与出庭准备、客户沟通与预期管理；与法官、对方律师及合作方协同推进程序。',
    scenarios: ['合同审查与谈判', '争议解决策略会', '证据交换与庭审', '常年法律顾问例行咨询'],
    suitableFor:
      '逻辑清晰、表达力强；能接受高强度读写与期限压力；对「立场与风险」敏感的人。',
    notSuitableFor:
      '排斥对抗性沟通与反复修改；不愿持续考证与更新法规判例的人。',
    aiImpact:
      '检索、模板与初稿生成更快，但策略取舍、庭审应变与职业伦理判断仍依赖律师经验。',
    aiEraSummary: '检索与草稿加速，策略与伦理仍靠人。',
    learningTips:
      '系统学民刑行核心领域之一；多写法律意见书与代理词；跟案练「事实—争点—请求权基础」链条。',
  },
  {
    id: 'finance-practitioner',
    name: '金融从业',
    libraryTag: '分析',
    libraryTeaser: '银行、证券、保险等机构里与资金、风险与合规打交道的统称方向。',
    oneLineTruth: '你在用「概率、期限与条款」帮别人配置或转移风险。',
    realWork:
      '客户或项目尽调、产品推介与适当性匹配、授信与风控模型输入、交易执行与对账、监管报表与内控配合（具体因条线而异）。',
    scenarios: ['授信评审会', '发行路演材料', '市场波动日客户沟通', '监管检查与整改闭环'],
    suitableFor:
      '对数字与市场敏感；能接受合规边界与业绩压力并存；沟通与文档并重的人。',
    notSuitableFor:
      '排斥规则与重复核对；只想「短炒」不愿理解产品结构与风险来源的人。',
    aiImpact:
      '报表、研报摘要与客户问答草稿可自动化，但适当性判断、风控裁量与监管沟通仍靠从业者。',
    aiEraSummary: '报表与摘要加速，合规与裁量仍靠人。',
    learningTips:
      '先定一条主线（如对公信贷/财富管理/交易风控）；补会计与宏观基础；熟悉反洗钱与适当性相关规范。',
  },
  {
    id: 'civil-servant',
    name: '公务员',
    libraryTag: '组织',
    libraryTeaser: '在机关体系中承担政策执行、公共服务与综合管理。',
    oneLineTruth: '你在「规定动作、程序正义与公众预期」之间找稳定解。',
    realWork:
      '文件起草与流转、窗口或一线执法与服务、督查整改、会议协调与跨部门对接；落实上级部署与属地责任。',
    scenarios: ['专项整治材料', '信访与舆情应对', '预算与采购程序', '突发事件值班与信息报送'],
    suitableFor:
      '稳重、守纪律；能接受节奏相对固定与流程优先；公共服务动机较强的人。',
    notSuitableFor:
      '极度排斥层级与文书；追求极高短期财务回报或强弹性自由职业状态的人。',
    aiImpact:
      '公文模板、数据汇总与知识库问答可提效，但责任认定、现场裁量与政治与法律综合判断仍靠人。',
    aiEraSummary: '文书与检索提效，责任与裁量仍靠人。',
    learningTips:
      '熟悉机关办文办会办事基本规范；练材料「问题—依据—措施」结构；关注本条线法规更新。',
  },
  {
    id: 'state-owned-enterprise',
    name: '国企',
    libraryTag: '组织',
    libraryTeaser: '国资体系内企业：重流程、重考核与战略任务并行的常见职场形态。',
    oneLineTruth: '你在「经营目标、合规红线与组织节奏」里找长期位置。',
    realWork:
      '承接集团战略分解、项目立项与招投标、安全生产与内控、人力与党建等职能条线工作；对上汇报、横向协同、对下督办。',
    scenarios: ['年度预算与 KPI 分解', '重大项目专班', '审计巡视整改', '数字化转型试点对接'],
    suitableFor:
      '适应强组织化环境；愿意在流程中积累资源与资历；稳定性诉求较高的人。',
    notSuitableFor:
      '强烈排斥科层与会议文化；只接受极扁平小团队节奏的人。',
    aiImpact:
      '制度检索、合同与报表草稿、知识管理可加速，但组织政治、资源协调与责任链条仍依赖岗位经验。',
    aiEraSummary: '制度与报表提效，协调与责任链条仍靠人。',
    learningTips:
      '理解公司治理与国资监管常识；练项目化推进与留痕管理；在主业外掌握一项可迁移的数据或法务基础更有余地。',
  },
  {
    id: 'teacher',
    name: '教师',
    libraryTag: '创意',
    libraryTeaser: '用教学设计让学生「真的学会」。',
    oneLineTruth: '你在管理「注意力、动机与反馈」三件事。',
    realWork:
      '备课与教案、课堂组织、作业批改与个别辅导、家校沟通；参与教研与课程改革。',
    scenarios: ['公开课与赛课', '后进生转化', '家长会', '教学评价与反思'],
    suitableFor:
      '有耐心与表达力；愿意观察学生差异；对成长有长期主义的人。',
    notSuitableFor:
      '排斥重复讲解与情绪劳动；不愿承担育人责任的人。',
    aiImpact:
      '习题、板书大纲与多媒体素材草稿可加速，但课堂组织、价值观引导与个别化关怀仍靠教师。',
    aiEraSummary: '素材与习题草稿更快，课堂与关怀仍靠人。',
    learningTips:
      '练「目标—活动—评价」一致性；学习形成性评价；多录课复盘语言节奏与提问技巧。',
  },
]

const byId = Object.fromEntries(CATALOG.map((c) => [c.id, c]))

/** @param {string} id */
export function getCareerById(id) {
  return byId[id] ?? null
}

/** 职业库列表（固定顺序与题目要求一致） */
export function listCareersForLibrary() {
  return [...CATALOG]
}
