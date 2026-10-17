# Agentic TRPG — MVP Scope Specification

> **文档状态：Draft / 部分产品决策已确认，其余待评审**
>
> **版本：v0.18**
>
> **初稿日期：2026-10-09**
>
> **修订日期：2026-10-17；同步 v0.4 目标契约，产品范围不变；仅文档，无运行验收**
>
> **文档级别：项目级（跨 Repository）**
>
> **建议仓库位置：** `agentic-trpg/agentic-trpg/docs/MVP_SCOPE.md`
>
> **适用范围：** Agent DM（包括 NPC Sub-agent）、State Machine、Rule Engine 与轻量文字入口；World Creation Agent、Visual Presentation Engine 均属于 MVP 后续阶段

**2026-10-17 v0.4 评审同步：** [Module Contracts](./MODULE_CONTRACTS.md) 继续是跨模块最终权威；[v0.4](./reviews/agentic-trpg-architecture-contracts-2026-10-17-v0.4.md) 仅保留审查记录。旧修订摘要中的整场 CombatEpisode／旧 OB 术语仅记录历史，现行目标为 Turn／Round Episode、单一有界 Recent OB List 和 `pending`／`processed`。每条新 OB 必经 Gate 决策（模型可选）；EVA 冻结完整授权近期窗口，processed 可影响 Meta，提交只完成固定 pending 覆盖。代码证据保持原日期／SHA，本次不刷新实现状态或冻结新增 ABI。

## 0. 文档定位与决策状态

本文件定义 Agentic TRPG **首个可实际游玩的端到端 MVP** 的产品边界、游戏场景、跨模块职责与验收目标。它**不是** D&D SRD 的完整实现计划，也不替代各模块的技术设计、规则覆盖矩阵和 Backlog。

为避免在需求尚未讨论时过早锁定技术路线，使用以下标记：

- **[已确认]**：项目已经明确的架构方向或目标。
- **[建议]**：本初稿提出的 MVP 默认范围；需要项目负责人评审后才能成为正式需求。
- **[待决策]**：会显著影响实现范围、成本或系统接口的问题；不能由开发 Agent 擅自决定。
- **跨模块标记对应：** `[DECIDED]` 为已确认语义，`[PROPOSED]` 为候选协议，`[OPEN]` 为未决事项，`[NOT IMPLEMENTED]` 为尚未实现的目标；实现事实须注明 Commit / 分支，不能由产品目标推定。

> **治理原则：** 当前文件中的「建议」不等于批准。只有经过明确确认并在决策记录中更新状态的条目，才能成为开发任务的强制验收条件。

### 0.1 已确认的产品决定（2026-10-09）

- **[已确认] 首版体验：** 用一个完整可玩的 D&D 小型冒险验证端到端系统，覆盖剧情对话、探索、检定、战斗、休息和任务推进；不追求全 SRD 覆盖或无限开放世界。
- **[已确认] 玩家模式：** 一名真人玩家**只直接控制一名玩家角色（PC）**。
- **[已确认] 首版采用单人剧本、没有 AI 队友：** MVP 不提供常驻 NPC 同伴、招募入队或 AI 队友战斗控制系统；不将“1 PC + AI 队友”作为验收场景。普通剧情 NPC 仍可以出场、对话、冲突，NPC 的偶发非战斗帮助不等于正式的队友系统。
- **[DECIDED] NPC 控制方式：** NPC Sub-agent 保留独立认知、对白、记忆/关系/目标和宏观行为决定，Agent DM 不代其作人物选择。即时战术、Reaction、自动效果与战斗触发由 SM 协调可信确定性机制、受控 Combat Policy 与 RE，不能依赖 Planner、JEV LLM、Cognition Gate 或 EVA。NPC Sub-agent 属于 Agent DM 内部能力；Combat Policy 是受控逻辑职责，**不新增顶层产品模块/仓库**。
- **[已确认] Agent DM 职责：** 主持故事、理解玩家意图、决定场景推进与 GM 语义裁决、协调 NPC Sub-agent；不得把“协调 NPC”变成“代 NPC 作出所有行动决定”。
- **[已确认] 交互方式：** MVP 以文字、自然语言交互为核心。简单文字界面足以满足演示；可选根据 DM 的描述生成插画。
- **[已确认] 视觉分期：** 与 Rule Engine、State Machine 深度联动的地图、Token、动画、场景渲染及游戏世界可视化**不属于 MVP 验收条件**，在 MVP 后单独推进。
- **[已确认] 黄金冒险剧本：** 选用 **First Blush**（D&D Duet）作为首个 MVP 的**本地端到端验收剧本**。不再编造一部代替它的原创剧情；具体地点、NPC、Encounter、线索和分支，必须在取得剧本原文后逐项提取和核对，不能凭介绍猜测。
- **[已确认] World Creation Agent 后置：** MVP **不开发** PDF/HTML/Markdown 自动剧本解析、跨剧本通用编译器、World Creation Agent，亦不要求兼容 Gamebook-style Adventure。首个冒险采用**人工整理、人工审核**的本地 Adventure Package（也可以先用最小化结构化配置）驱动，作为未来 World Builder 的参考样本。
- **[已确认] 视觉引擎后置：** 可交互的 Visual Representation / Presentation Engine、自动地图资产管线、实时视觉状态同步均在 MVP 后开发。少量不影响游戏状态的 AI 插画仍可选；本地 Golden Adventure 无插画也须可通关。

**已批准的目标架构**：以 [MODULE_CONTRACTS.md](./MODULE_CONTRACTS.md) v0.16 为跨模块最高规范。**[DECIDED] 当前 SM＋RE 为开发/运行基础，允许证据驱动的子系统重构/替换**；同一事实只有一个权威来源，可信运行层提交，不冻结现有类/表/接口。撤回未合并的 Evennia 优先采用与必经 EB 顺序；整体迁移 OPEN，`agentic-trpg/Evennia_base` 为 Deferred / Optional evaluation，本批不创建。机制研究与主线验证见 [演进计划](./GAME_CORE_EVOLUTION_PLAN.md)。RE Stateless 目标/完成标准不变，不因文档修订扩大实现声明。

开放合理行动、持久世界后果与 NPC 私有认知/自主性是原有产品目标。程序化核心提供可复用且后果可被后续机制消费的能力，LLM 负责语义/情境裁决及人物认知；不是完整传统 RPG 加聊天 NPC。真实 Agentic 验证应尽早与机制建设交错，不等完整 Host。

**长期重构与 MVP 分期**：MVP 不要求实现全部 SRD 5.2.1 规则，但已经选择支持的机制必须按 `StateSnapshot + Typed Intent + Pinned RulesetBinding + Explicit RNGContext → RuleEvaluationResult` 求值并由 SM 原子提交；不能落回依赖 Legacy `_LiveCombat` / `CombatHandle` / `_REGISTRY` / Stateful Combat Orchestrator 的路径。长期目标是将计划保留的原有规则能力统一迁入 Stateless 体系并退出旧执行器（MODULE_CONTRACTS.md §14.1）。增加 Stateless 规则覆盖、完成 MVP 子集与完成整个执行架构迁移是不同的验收结论，均须有实际证据。

**[已确认] DM 职责隔离**：DM Planner 负责游戏规划/主持与结构化提议；DM Narrator 只依据玩家可见的已提交结果进行叙事，不共享未经授权的 GM Secret/其他 NPC 私有认知，可使用同一 LLM 但需隔离上下文和权限。

**[已确认，2026-10-11；2026-10-12 按领域责任修订] NPC 双模式 Evaluation**：NPC 身份共用同一 Session 实体关联；Cognition 管 Personality / Memory / Belief / Relationship / Goal / Plan 版本与 Task / Mode / Gate，Perception 管 Observation / Work / Completion / Retention，WorldFacts 管世界时钟、Session 提供引用。Host 只管模型及 Interactive / Background Context。Interactive 独占主观认知/自主行动，必经 Gate 决策（模型可选）但不逐 OB 强制、无新 Background EVA；Inactive Gate 路由优先/定期 Background 或受控 No-op，Background 不激活 Interactive Agent。简单日程、模式/版本失效和既有完成协议保留。

**[已确认，2026-10-11] OB 生命周期约束**：Recent OB 直接承担短期感知记忆，不另建 Short-term Memory；Processing 与 Retention 独立，processed 在 TTL 前仍可用但不重排同一工作。Game Time 决定到期，待处理 Work 与受引用证据必须保护；定期 EVA 最大等待严格小于适用 OB 生命周期且留执行余量，不能保证异常时必然完成。长期 Memory 仍由 NPC EVA 可选提议；本次仅同步既有 MVP 可靠性约束，具体 TTL / Schema / 周期 / 清理算法未冻结。

**重要架构边界：** “没有战术画面”不等于“没有权威战术状态”；“NPC Sub-agent 有自主决策能力”不等于它可以修改世界状态、决定骰点或绕过 Rule Engine；“一个 NPC 一个独立角色上下文”也**不等于**必须为每个 NPC 常驻部署独立模型或进程。

## 1. 项目愿景与 MVP 定义

**[DECIDED] 状态责任补充（2026-10-15）**：遵循 MODULE_CONTRACTS.md v0.16 §0.3 / §0.5–§0.6。领域管理事实、操作共享 SQLite 提交；StateMachine 统一入口/装配，A1 分开探索与战斗编排并复用位置/对象能力，A2 按需显式组合减少 Mixin。已有受限基础见 MC §1.2，完整目标仍 OPEN；产品与恢复范围不变。

### 1.1 项目愿景

**[已确认]** Agentic TRPG 是一个模块化、可扩展、以 AI Game Master（Agent DM）驱动的 TRPG 平台。长期规划包含 Rule Engine、State Machine、Agent DM、Visual Presentation 四个相互独立的模块。**首个 MVP 仅要求前三个核心模块协同工作，并由轻量文字交互入口提供游玩体验。** Visual Presentation 在 MVP 之后建设；可选插画不构成新的权威状态系统。

核心原则：**能由确定性程序可靠处理的规则计算，不交给 LLM 自行猜测；需要叙事、语义理解和开放式裁决的事情，不强行塞进 Rule Engine。**

### 1.2 MVP 的成功定义

**[已确认的产品方向；细节仍待验收设计]** 首个 MVP 的成功标准不是实现全部 SRD 或自动编译任意冒险，而是：

> **一名真人玩家只控制一名 PC、没有 AI 队友**，在 Agent DM 主持下通过自然语言完成选定的 **First Blush** 单人冒险（经人工适配），核心流程涵盖**剧本实际包含的 NPC 互动、探索、检定、战斗、状态转移与合法结局**；休息/资源恢复等若未自然出现在剧本内的共用能力，通过独立集成测试验收。对话 NPC 和战斗敌人的实际决策通过有独立角色上下文的 **NPC Sub-agent** 提出；Agent DM 负责主持、协调与叙述。各领域管理其负责的世界、角色、效果、战斗流程及认知事实，一次不可分割操作共享提交；RE 按固定规则集计算机械结果，不持有隐藏跨请求权威状态。所有越权或不支持的规则必须有明确反馈。

标识关系：session_id / npc_id / evaluation_id、EvaluationStatus / NPCStateVersion / observation_work_id 由 SM 管理，invocation_id（一次模型尝试）与 context_id（模型 Context 引用）由 Host 管理。一次 Evaluation 可多次 Invocation，一个 Interactive Context 可服务多个 Evaluation；后两者不要求提交必填，Evaluation ID 不是认证凭证。SM 仍核验可信主体、NPC 绑定、授权范围、版本与幂等。

MVP 必须是**可反复运行的文字版 Vertical Slice**，不是若干模块各自拥有 API 的集合。关闭图片生成后仍应完整可玩；**不以 NPC 同伴系统替代 NPC Sub-agent 的独立性验证**。

### 1.3 首版产品基线（已确认与候选项分列）

| 维度 | MVP 产品范围 | 决策状态 |
| --- | --- | --- |
| 首个 RuleSet | D&D 2024 修订规则：PHB 2024、DMG 2024、MM 2025、SRD 5.2.1；First Blush 旧版细节逐项核对/适配，不将其他模块设计为 D&D 专用 | [DECIDED] 设计基线；具体支持待验证 |
| 冒险类型 | 单人叙事探索、NPC 互动、检定、具备战术规则的战斗、休息及任务推进，组成完整小型冒险 | [已确认] |
| 玩家模式 | **一名真人玩家，只直接控制一名 PC** | [已确认] |
| AI 队友 / 同伴 | **首版没有 AI 队友**；不做招募、组队控制、队友战斗管理及同伴专属玩法 | [已确认：不纳入 MVP] |
| NPC 控制 | **NPC Sub-agent 负责独立认知/宏观行为，Combat Policy 负责即时战术**；含敌方 Actor，至少一名敌方 Agent 自主性仍须验收 | [DECIDED]；具体配置 [OPEN] |
| NPC Sub-agent 的执行形态 | 唯一持久角色状态；Interactive / Background Evaluation Context 隔离、按需调用；可共享底层模型/进程 | [已确认：双模式与独占原则；Schema / 技术选型待设计] |
| 主要交互方式 | 文字/自然语言；规则结果和重要状态以文字呈现 | [已确认] |
| Visual Presentation | 不要求可交互战术画面、Token 或画面与规则/世界状态的深度绑定 | [已确认：MVP 后] |
| AI 场景插画 | 可选、非阻塞增强，不参与规则裁决 | [已确认：可选] |
| 验收等级 | 以 1–5 级常见能力作为重点候选范围；不删除已有高等级实现 | [建议] |
| 角色准备 | Package 内可含多个完整、机械属性经规则验证的静态 PC Templates，选一名；MVP 严格一玩家一 PC，无独立构建服务或外部角色导入前提 | [DECIDED]；完整创建器/未来导入 [OPEN] |
| 战斗空间 | 实体负责领域保存唯一当前位置，战斗引用其网格投影；RE 计算移动、范围/掩护，无需渲染地图 | [建议：空间模型；事实不重复为 DECIDED] |
| 单人战斗平衡 | 选用可由一名 PC 独自面对的遭遇，必须保留正常失败、死亡和撤退可能，不通过 DM 任意改骰“保护剧情” | [建议] |
| 运行形态 | 本地/单实例优先；Agent 模型、调用成本、并发规模另议 | [待决策] |
| 黄金冒险内容 | **First Blush**，人工编写/审核本地 Adventure Package；移除对 AI 队友的依赖、审查单人遭遇安全性 | [已确认；内容适配待核对] |
| World Creation Agent | **不纳入 MVP**；不要求自动读取或编译其他 D&D 模组 | [已确认：MVP 后] |
| 游戏内容分发 | 代码/通用 Schema 可开源；未经权利人许可不得把 First Blush 正文、地图或实质性改编数据提交公开仓库 | [已确认：发布约束] |

**边界说明：** 不开发 AI 队友系统，不妨碍故事中的商人、守卫、委托人、盗匪和怪物出现，也不妨碍 NPC 做出不利于玩家、并非 DM 预定的选择。NPC 的身份与会话状态必须稳定；NPC Sub-agent 的文本输出与内部 LLM 推断不构成可重放的规则结果。

## 2. 四个模块及权威边界

MVP 的**顶层核心模块仍只有 Agent DM、State Machine、Rule Engine，加一个最低限度的文字交互入口**。**NPC Sub-agent 是 Agent DM 模块的内部多智能体能力，而非新增第五个顶层 Repository 的强制要求。** Visual Presentation 属于 MVP 后的开发阶段。

这里是逻辑模块划分，不固定仓库数量、现有类/表或子系统接口。当前 SM＋RE 为基础，Evennia / CDDA / Ranvier 是机制/可复用组件研究来源；整体框架迁移不是单玩家/单 PC/文字 MVP 前置条件，不扩大多人范围。

| 模块 | 核心职责 | 权威范围 | 不应承担的职责 | MVP 地位 |
| --- | --- | --- | --- | --- |
| **Agent DM** | 解释玩家意图、主持场景、请求 SM 批准 NPC Evaluation、GM 难度/线索和叙事裁决、将已提交结果叙述给玩家 | **场景组织与语义裁决** | 直接代替 NPC Sub-agent 做人物决策；伪造命中/骰点、HP 或 Rule Engine 结果 | **核心** |
| **NPC Sub-agent**（属于 Agent DM） | 基于 NPC 自身角色设定、当前知识、目标与记忆决定说什么、做什么；给出对话或结构化行动提议 | **角色层面的决策提议，不具备权威状态写入权限** | 查看角色不应知道的秘密；写 HP/Slot/世界状态；自行确认机械动作成功 | **核心内部能力** |
| **State Machine 当前基础 / 目标领域模块** | StateMachine 统一 API / 装配；WorldFacts、CharacterFacts、CombatRecords、Activity、Effects、认知/感知各管其事实，共享 SQLite 提交 | **每项事实一个负责领域，跨领域操作共同提交**（MC §0.3） | 单模块包揽全部业务；重复位置/物品归属；再实现 RE 规则；把模型提议当事实 | **核心；已有受限组合，完整目标待落实，见 MC §1.2** |
| **Agent Host**（Agent DM 内部基础设施） | LLM 调用、Context / Prompt / Budget / Cache、Tool 传输与运行时日志 | 仅临时 Runtime Metadata | 权威游戏状态、NPC 认知、领域任务完成与游戏结果 | **核心内部能力** |
| **Rule Engine** | Typed RuleSet、规则合法性、骰点、攻击/豁免、行动经济、战斗机械状态转换计算及拟议事件 | **明确支持的机械规则求值，不拥有独立权威运行态**，与发起提议的 Agent 无关 | 扮演 NPC、决定 NPC 的动机、管理剧情与完整世界 | **核心** |
| **Visual Presentation** | 将来的地图、Token、动画与场景呈现 | **只拥有展示层状态** | 直接决定伤害、HP、位置或合法性 | **MVP 后** |

### 2.1 状态所有权原则

**[DECIDED] 每项当前事实有明确负责领域；机械规则由 RE 计算；一次不可分割操作经共享设施共同提交。**

当前 SM 为开发/运行基础，保留授权、可靠提交与私有状态等已验证语义，允许重构或替换子系统，不冻结现有实现。不同表可保存不同事实，授权视图/缓存不是第二权威；禁止两份相同世界双向同步。替换原型与现有实现使用独立测试 Session，以下所有权均指领域职责。

- WorldFacts 管场景/空间/对象/物体耐久/门锁/容器/物品实际关系；CharacterFacts / 机械组件管角色唯一实际位置、HP、资源和装备；库存归属受控投影。Effects 管持续效果与自身进度；Activity 管进行中的活动；CombatRecords 管战斗运行记录，CombatHandler 编排，不另存人物当前事实。RE 计算机械变化，PC/NPC 同一正确性标准。
- Session 管身份/固定绑定和元数据；WorldFacts 管世界时钟/Scene 等，Quest 保留任务状态责任；Cognition 管追加版本的 Meta / Task / Mode / Gate，Perception 管授权证据/观察/处理生命周期。各领域共用同一实体身份，历史 Goal 不全是当前任务，记忆不保证避免循环。
- 共享提交设施负责授权、版本/原值、请求关联、幂等、RNG、原子性及可靠通知；领域仍检查自己的结构/引用/生命周期，不以通用提交层重写法术或能力判定。现有攻击适配白名单未经审计不得删除或冒称通用。
- **Agent Host** 严格负责 LLM Runtime：模型调用、超时重试取消、Interactive / Background Context、Prompt / Builder / Token Budget / Cache、Tool 适配传输、Invocation 日志/延迟/Usage。仅临时 Runtime Metadata，不拥有或持久管理任何权威游戏状态、NPC 认知、观察完成或行为结果。SM 不执行 LLM 主观推理、不管理物理 Context。
- NPC Sub-agent 只接收经过权限/知识筛选的角色视角上下文；做出角色决定，并输出**待验证**的对话或行动意图。Sub-agent 不能直接写入世界数据，也不能自行宣告命中、伤害或资源消耗。
- Agent DM 对 NPC 行动进行**世界可行性与规则执行协调**，负责 GM 裁决和对外叙事；不能任意覆盖 NPC Sub-agent 的人物决策，仅因剧情想要某种结果就替其发言或作弊改骰。
- RE **未提交的 Evaluation Result** 经各领域受控接口在一次共享事务提交；不存在战斗结束从第二份权威 HP/位置回写的阶段。默认进程内/共享持久化，内部协作无需逐字段外部 TypedCommand/JSON/RPC，不能任意写表或继承模型输出的未验证语义；不新增分布式设施。
- 可选图片及文字展示不属于权威状态来源。

**[待决策]** 跨场景 Effect、库存装备、NPC 记忆的精简/冲突处理以及活跃战斗恢复的最终契约由后续 `MODULE_CONTRACTS.md` 设计。

### 2.2 Actor 控制权与权限

| Actor / 操作类别 | 决策者 | 权限与事实检查 | 机械裁决 |
| --- | --- | --- | --- |
| 玩家的唯一 PC | **真人玩家**；Agent DM 负责把语言映射为候选 Intent 和请求必要选择 | State Machine（Host 传输可信关联） | Rule Engine |
| 非战斗 NPC（委托人、商人、证人等） | **对应 NPC Sub-agent**，在其知道的世界事实及目标范围内自主回应 | State Machine（Host 传输可信关联）；DM 协调场景 | 需要机械检定时交由 Rule Engine |
| 敌方 NPC、Monster（战斗中） | **受控 Combat Policy** 选择即时战术/Reaction；对应 Sub-agent 决定角色宏观目标/策略 | State Machine 校验 actor、回合、策略授权及机械可知信息 | Rule Engine；未知察觉不默认 Positive，不等 LLM |
| 常驻 AI 队友 / 可招募同伴 | **MVP 不适用** | — | — |

- 玩家始终只控制自己的 PC。NPC 即便接受了玩家的请求，也应由自己的 Sub-agent 根据角色目标和知识决定回应，而非将玩家的话直接视为 NPC Action。
- Agent DM 协调场景与交互；NPC 的发言与宏观个人选择交相应 Sub-agent，即时战术交受控 Combat Policy / RE，不因轮到 NPC 就先等待 EVA。
- Rule Engine 不应因 NPC 是 LLM 控制便给予免费攻击、无成本施法或自动成功；Actor 控制权最终由 State Machine 校验，Host 仅传输可信关联。
- NPC Sub-agent 可以提议不合法的动作；系统应向它反馈结构化拒绝，并允许有限次数的重新选择，而不是绕过规则强制成功。
- **[边界]** 不要求 NPC 在玩家不在场时永久后台自主运行；不要求 NPC 之间开展无限自动对话或形成独立社会模拟。

### 2.3 NPC Sub-agent 的 MVP 最小执行模型

目标是 NPC 独立决策，仍不要求常驻模型、每条观察调用完整 LLM 或复杂社会模拟。已确认架构原则见 §0.1；新增字段、Schema 与具体存储协议仍 **Proposed / Not Implemented**。

1. NPC 共用同一实体身份，Cognition 管版本化 Meta，Perception 管观察/处理；不各建 NPC 目录。两模式使用同一/兼容七字段 NPCEvaluationResult：dialogue、memory_updates、belief_updates、relationship_updates、goal_updates、plan_updates、action_intents，均可为空。
2. Interactive 活跃（含模型空闲）时当前 LLM 独占主观认知/决策，新 OB 有序增量追加；Gate 决策必经，重要性模型分类可选，不逐条强制，不新建 Background EVA 或额外 Memory / Cognition LLM，不改运行中输入/Context/KV Cache。
3. Inactive 不维持持续 Interactive Context，SM Gate 路由 Urgent 优先 Background、Deferred 定期/最长等待批量或 Irrelevant 受控 No-op；确定性/批量分类可替代逐条模型调用，Host 执行、SM 采用。Background 一次性 Context 不创建/恢复/激活 Interactive Agent，可独立提出行动。
4. EVA 是认知与决策评估。SM 创建 evaluation_id、维护 EvaluationStatus / NPCStateVersion / observation_work_id，Host 管 invocation_id / context_id；一 EVA 可多 Invocation，一 Context 可多 EVA，运行时 ID 非必填提交，Evaluation ID 不是认证。
5. 提交简化为 submit_npc_evaluation_result(evaluation_id, result) → EvaluationReceipt。SM 从 Task 恢复 Session/NPC/模式/版本/观察/权限，可信运行环境提供调用身份，不信任模型自报，不需要额外 Proposal 信封。
6. Memory / Belief / Relationship / Goal / Plan 整批确定性验证。一项非法整批不写、由当前有效 EVA 有限修正；首次合法 Result 在同一 SQLite 事务验证任务/版本、选定唯一结果、原子提交 Meta、可靠交接输出并完成任务。evaluation_id 为 Meta 幂等键，相同 Result 返回原反馈，已选后不同 Result 拒绝。
7. Action Execution 独立使用稳定 command_id / Typed Command、必要 Rule Evaluation 和 SM Commit / Command Receipt。非法 Intent 不回滚合法 Meta；EVA 完成不等待行动成功，但必须可靠记录交接防漏/防重。动作失败反馈可继续动作交互，不自动重做完整 EVA。
8. 模式切换原子撤销旧有效 EVA、保留已提交 Meta、移交未完成观察并创建新 Evaluation ID；新 Interactive LLM 获最新 Meta/观察/玩家输入。Host 尽力取消，不等待旧失败反馈或 ACK，取消任务新 Invocation 也不能提交。
9. SM 只检查 Schema/类型、身份/权限、引用、任务/版本、允许字段、幂等与数据库约束，不验证自然语言忠实性、不改写 Belief、不增加 Semantic Validator LLM。完整授权 Profile / Episodic Memory / Belief History / Relationship / Goal / Plan 和 Task 冻结的完整授权 Recent OB List（含 processed／pending）由 SM 提供，Host 不做语义筛选/检索/Ranking/智能压缩。Interactive 复用后只需增量追加变化。
10. Belief 与 Initial Belief 使用兼容结构，同一 Belief 追加版本、保留来源/有效状态及旧历史，NPC 可修改/降置信度/放弃，SM 不替代决定。Memory Persistence 与资源管理独立，MVP 只预算保护和安全释放/完整 Meta 重建。
11. 单次 Invocation Timeout / API Error / Schema 非法 / Meta 非法不立即使 EVA failed；有效且有预算保持 running，同 evaluation_id 可用新 invocation_id 有界重试/修正，仅耗尽或明确无法继续最终 failed，模式切换为 cancelled；未完成观察保留。SM 内部 Completion 据必要认知处理及可靠交接维护，无独立 ACK；动作 needs_choice/失败独立跟踪，不提前伪装执行成功，也不重新打开已完成 EVA。响应丢失先按 Evaluation / Command ID 查持久结果。
12. SM 持续不可用停止权威推进，Host 不接管或维持影子状态/游戏队列；从持久 Task / Meta / Result / 交接 / Receipt 恢复。非战斗恢复必需，战斗精确续玩后置，不增加分布式协调。

确定性 Schedule / Combat Policy 复用统一命令路径；仅固定策略不能完成敌方 Agent 自主性验收，但由 Agent 宏观决定约束 Policy 的即时执行符合双路径设计（D16 / D26）。保存已提交意图和结果，不要求逐字重生成模型输出；自动反应/调用预算仍有界，具体数字待验证。

现有受限 NPC Intent / Stateless 基础攻击路径不代表全部怪物动作已完成跨模块适配；Multiattack、Recharge、Reaction 等支持范围及受控 Combat Policy 的公共 Consumer 仍须逐项核实/补齐，复用规则、资源与回滚语义，不能操作私有 _LiveCombat 或冒充 PC。锁定 RE 与最新 main 的差距见 MODULE_CONTRACTS.md §1.1。

**[DECIDED] 双路径 / Episode 产品边界：** 本场参战 NPC 接收 Turn 来源、外部接收 Round 来源；机械 Event 不逐条生成认知信号，不另建逐动作感知证据链，同 NPC／Episode 合批，按范围与接收能力过滤。非战斗仍独立阶段取证。即时 Reaction 使用已有参数与机械事实，不等待当前 Turn EVA；已提交认知参数影响后续决策。聚合／路由／迁移／恢复仍 NOT IMPLEMENTED／OPEN，旧观察与可靠进度保留，见 MC §7.5。

**规则粒度与暂停边界：** RE 一次请求尽量连续结算已授权效果/触发；真正中途选择按 MODULE_CONTRACTS.md §8.3 的 Interrupt / Continuation 目标暂停、持久化、保持 RNG / 支付一致性并恢复，不占 SQLite 长事务。共同 ABI 和最小 MVP 支持路径 [OPEN]；这不扩大为任意活跃战斗崩溃精确续玩承诺。审计/重放保留，正常求值目标使用完整必要当前机械事实，不另建精简历史日志；完整 Combat Event Log 退出输入须先按 RE-HIST-01 审计真实读者并补齐状态；实现差距见 MODULE_CONTRACTS.md §1.1。

### 2.4 目标交互流程（逻辑模型，非固定网络拓扑）

```text
玩家（唯一 PC） ──自然语言──> Agent DM（主持者/协调器）
                                    |
                                    +──场景与事实查询──> 授权领域视图 / Perception
                                    |
                                    +──请求 NPC 决策────> NPC Cognition 批准 Task
                                    |                       |
                                    |                 Agent Host Runtime -> NPC LLM
                                    |                       |
                                    |                 Result -> Cognition / 共享提交
                                    |                       |
                                    |                 已授权发布的对白 / 权威回执
                                    |                       |
                                    <───────────────────────+
                                    |
                                    +──世界操作────────────> 世界/实体领域接口 -> 共享提交
                                    |
                                    +──机械 Intent─────────> Combat / 负责 Handler -> RE
                                    |                       -> 领域接口 / 同一共享事务
                                    |                         |
                                    <──────最终 CommandReceipt / Perception Events ─────────+
                                    |
                              用权威结果叙述、推动 Scene
                                    |
                                    v
                                  文字界面
                    （可选图像只读叙事，不写入游戏状态）
```

该图表示责任和信任边界，而不是强制把 Sub-agent、Agent DM、State Machine、Rule Engine 分别部署成服务。单一 LLM 可以在不同隔离上下文下承担不同 NPC 角色，但 NPC 必须通过独立 Sub-agent 调用与输出契约作决定，不能退化为 DM 对所有角色的直接代言。

## 3. MVP 游戏场景目录（Gameplay Scenarios）

以下根据已确认的单人模式和 NPC Sub-agent 设计提出**[建议] 验收场景**。所有 Core 场景都必须在没有地图渲染、Token 和 AI 插画的情况下成立。

| ID | 场景 | 玩家体验 / 可观察结果 | 主要模块 | MVP 优先级 |
| --- | --- | --- | --- | --- |
| G01 | 开始游戏 / 载入唯一 PC | 创建 Session、载入单人 PC、RuleSet、初始 Scene，以文字显示基本状态 | State Machine、Rule Engine、Agent DM | Core |
| G02 | NPC 独立对话、任务选择 | 玩家与委托人/商人等交流；NPC Sub-agent 根据个人目标、已知信息和关系回应；任务状态经授权更新 | NPC Sub-agent、Agent DM、State Machine | Core |
| G03 | 探索、搜寻、调查 | 自由语言探索、发现线索和切换场景；必要时以 Engine 处理 Ability / Skill Check | Agent DM、State Machine、Rule Engine | Core |
| G04 | 物体交互与基础陷阱 | 开门、调查物体、解除机关；失败在审定范围内可触发 Save、Damage、Condition | State Machine、Agent DM、Rule Engine | Core（有限范围） |
| G05 | **单人 PC 对敌方 NPC 的战斗** | 玩家选择 PC 动作，敌方 Combat Policy 选择合法即时战术；NPC Agent 独立宏观目标实际约束受控行为，SM 提交机械状态，RE 算规则/资源/回合 | NPC Sub-agent、Combat Policy、Rule Engine、State Machine | Core |
| G06 | 精选法术、职业能力与道具 | 已获准的动作正确检查目标、支付资源、产生状态/事件并可拒绝非法调用 | Rule Engine、Agent DM | Core（精选） |
| G07 | 休息与资源恢复 | HP、Slots、特性等按规则恢复；世界时间由 State Machine 推进 | Rule Engine、State Machine | Core |
| G08 | 战后状态与任务推进 | PC 及相关敌人状态正确写回；战利品与剧情分支可验证 | Rule Engine、State Machine、Agent DM | Core |
| G09 | Session 保存与读取 | 非活跃战斗时重新载入仍保存 PC、任务、Scene、关键 NPC 记忆与关系 | State Machine、Agent DM | Core |
| G10 | **NPC Sub-agent 的身份、知识与自主性** | 至少一个 NPC 多轮互动记得关键事实；至少一名敌方 Agent 独立认知/宏观选择实际影响后续 Policy 行为与战后认知，不要求每次战术 LLM | NPC Sub-agent、State Machine、Agent DM | **Core** |
| G11 | 高阶环境、复杂召唤和变形 | 仅按精选冒险实际需要逐项支持，禁止从基础 Activity 推断全覆盖 | Rule Engine、State Machine | Optional |
| G12 | AI 场景插画 | 根据 DM 描述生成 NPC/地点/关键事件图；关闭后无行为变化 | Agent DM、可选图像服务 | Optional |

**明确排除的首版场景：** 1 PC + AI 队友组队战斗、同伴招募/控制、多玩家合作、完整 NPC 后台生活模拟、NPC 之间无限自动社交。

### 3.1 黄金冒险：First Blush（已选定）

**[已确认]** First Blush 是首个本地 MVP Golden Adventure。我们选择它，是因为它面向一名 PC 和一名 DM，适合评估开放式自然语言冒险、NPC 决策和确定性规则协作。**不得凭封面、宣传页或过往假设写入该剧本的具体剧情事实。**

**MVP 的内容准备流程是人工的，不是 World Creation Agent：**

1. 通过作者或授权分发平台合法取得剧本；仅在授权范围内使用和保存原文。
2. 人工审阅实际正文，抽取场景、场景连接、出场 NPC、NPC 可知信息与目标、事件前置条件、互动对象、怪物/Encounter、结局条件和原始数值。
3. 将内容整理成**本地 Adventure Package**（建议至少包含 `manifest`、`scenes`、`npc_profiles`、`encounters`、`initial_state`、`rule_bindings`、`source_trace`）。MVP 允许针对 First Blush 编写最小数据结构，不承担“任意模组导入”的兼容责任。
4. 逐条将原剧本涉及的规则映射到 SRD 5.2.1 / 现有 Rule Engine，记录不兼容能力、规则替代和来源。由于版本差异，不应直接把旧数据视为 2024 版权威数据。
5. 核对是否依赖 Sidekick/友方战斗角色；MVP **不引入 AI 队友**。如须调整遭遇平衡、剧情触发或可选辅助，记录为透明的**本地 Solo Adaptation**，不要擅自更改掷骰结果。
6. 使用该固定、人工审核的数据集初始化 Session，再测试 NPC 子代理交互、合法战斗意图、规则拒绝、场景转移和重载。

**验收覆盖与忠于剧本同时成立：** 检定、NPC 对话、探索、一次合法战斗及结局推进应来自实际剧本；如某项工程性能力（例如短休、再次会见同一 NPC）在原剧本里不自然出现，应以**独立集成测试**验收，不能为凑 Checklist 强行编造剧本片段。NPC 持续记忆可用同一角色的多轮互动验证，是否要求跨场景重逢待正文审查。

**可发布性限制：** First Blush 可免费取得并不等于允许公开改编和再分发。除非获得明确许可，**不得**将原文、地图、插画、受保护的场景表达或实质性转写的 Adventure Package 推送到公开的 `agentic-trpg` 仓库。公开仓库只放通用 Schema、工具、文档、测试协议与不包含受保护表达的合成数据；完整本地 Fixture 应被 Git 忽略。未来若需要开箱即玩的开源 Demo，再另选开放授权剧本或取得许可。

## 4. Rule Engine 支持范围政策

**设计基线 `[DECIDED]`：** D&D 2024 修订规则（PHB 2024、DMG 2024、MM 2025、SRD 5.2.1）。具体已启用内容仍须精选规则矩阵、来源核对和真实实现证据；不宣称覆盖全部规则书。World 组件字段是工程候选，不是官方数据库规范，已核对来源及待确认细节见 [World 草案 §1](./WORLD_SUBSYSTEM_DESIGN.md#1-基线范围与规则依据)。

### 4.1 范围分类（产品优先级）

| 分类 | 定义 | 应对方式 |
| --- | --- | --- |
| **Core Required** | MVP 核心场景不可缺少、机制高度共用，且不正确会破坏状态一致性 | 必须实现并进行端到端规则验收 |
| **Selected Support** | 有明确玩法价值，但不是所有内容都需要 | 按精选 Ability、Item、Spell、Monster 或机制族审核启用 |
| **GM Adjudicated**（旧称 Host Adjudicated，非 Agent Host Runtime） | 结果主要由剧情、NPC、环境或 GM 判断决定 | Agent DM 作语义裁决；State Machine 通过受控操作提交世界结果；机械副作用仍应走 Engine |
| **Out of Scope** | 对首版价值较低、实现代价过高或依赖大型模拟系统 | 明确不承诺执行，并提供可理解的不支持边界 |

**重要：以上四类是“是否需要实现”的产品分类；不能与现有 Rule Engine 的 `executable` / `bounded` / `host_narrative` / `deferred` 技术执行分类混为一谈。** 一个项目范围内的 Core Required 仍可能处于 Deferred，意味着存在阻塞；一个已有 Executable 规则也未必需要进入 MVP 重点验收清单。

### 4.2 Core Required 的候选共用机制

**[建议]** 优先保证以下机制在明确支持范围内正确：

- 基础 D20 检定、Advantage/Disadvantage、Ability/Skill/Save、DC 和来源追踪。
- Initiative、Round/Turn、Action/Bonus Action/Reaction、移动与目标合法性。
- Attack Roll、Damage、Crit、Resistance/Immunity/Vulnerability、Death Saves、Healing/Temporary HP。
- 常见 Conditions、Exhaustion、Effect Lifecycle 与 Concentration。
- 基础 2D Grid、LoS、Cover、范围目标和常用 AoE；不要求视觉地图。
- 代表性 Spell/Feature/Item 的 Invocation 选择、支付与效果；非法/冲突/提交故障回滚，合法失败按规则保留实际成本。
- **单 PC + 敌方 NPC 的权威战斗执行：** 受控 Combat Policy 提交即时合法 Intent，SM 审核 Actor/策略/机械可知范围，RE 算全部机械结果；同时验收至少一名敌方 Agent 的独立宏观决定及真实行为影响，不能只用默认怪物 AI 证明自主性。
- Rest/Recovery、战斗结果输出以及向世界状态的安全转交。

这些是**需要具备的机制类型**，不是声明已完成全部 SRD。具体内容必须通过 `Rule Support Matrix` 映射到真实的 Spell、Feature、Item 和 Monster，并有独立规则依据。

### 4.3 明确的首版非目标（待评审）

**[建议]** MVP 暂不以以下内容为发布门槛：

- SRD 5.2.1 **全部**法术、Feat、Monster、Magic Item 与完整职业等级覆盖。
- **AI 队友、常驻 NPC 同伴、招募/入队系统、由玩家直接管理一整支队伍**。这是已确认不纳入 MVP 的范围。
- 复杂位面旅行、全面世界经济、真实物理模拟、完全开放的世界生成。
- 车辆、荒野旅行、巢穴、位面和 Bastion 的完整子系统；均为后续扩展，World 组件目录不将其变成当前 MVP 门槛。
- 全 3D 空间高度、复杂飞行体积、大型生物多格占位及所有立体 AoE。
- 多人实时联机、分布式一致性、跨 Worker 战斗执行和生产级集群部署。
- **每个 NPC 常驻独立模型/进程**、NPC 离屏永久行动、完全自主的 NPC 社会模拟、无界的多 Agent 对话或递归委派。**不排除每个活跃 NPC 有自己的逻辑 Sub-agent 和记忆上下文。**
- 所有复杂召唤、形态变化、任意 Ready/Reaction Trigger 的通用支持。
- 所有开放式叙事命令都能自动转化为机械执行。
- 可交互视觉游戏世界、地图 Token、深度状态驱动动画、实时语音/视频及完整 VTT 编辑工具链。

未支持内容必须被正确识别，**不能以无效果的“成功执行”充当规则支持**。

### 4.4 不支持规则时的行为

1. **机械规则不支持：** 在任何资源扣减、RNG 消耗或不可逆状态变化前返回结构化拒绝/能力不支持信息（若该执行路径支持 Preflight）；能力限制经授权结构化反馈给 Planner，由文字入口提供可理解说明或合法替代方案；Narrator 不直接暴露 API/Schema/unsupported 错误，也不伪造成骰点失败或墙壁永久不可摧毁等世界事实。
2. **需要 GM 裁决：** 明确切换为叙事/世界操作路径；仅在经过授权和验证后提交世界状态，不冒充 Rule Engine 的机械结算。
3. **混合型效果：** 将可执行的机械部分和需要 GM 语义裁决的部分清楚拆开；不得因一个规则的某个 Activity 可解析，就宣称整个规则效果已实现。
4. **不得静默变更规则：** 若要采用简化、Homebrew 或 DM Override，应留有操作来源与审计记录，并与正式 SRD 机制区分。

## 5. 文字交互 MVP 与可选插画（World Builder / Visual Engine 均延后）

**[已确认] MVP 不交付完整 Visual Presentation 模块。** 三个核心模块只需一个最低限度的文字交互入口（CLI、轻量 Chat UI 或其他形式待技术选型），便可完整游玩。

保留轻量文字入口，客户端/基础设施复用可按具体组件评估，不预设整体 Evennia；地图/Token/动画仍为后续独立呈现工作。

### 5.1 MVP 必需的文字交互能力

- 玩家可以通过自然语言描述行动并接收 Agent DM 的场景描写、NPC 回应和规则结果。
- 玩家能以文字获知必要的 PC 状态、行动资源、任务进度、当前可交互对象及自身的位置/距离等信息；不要求全部数据每回合完整输出。
- 当规则执行需要补充选定目标、位置、法术模式、骰点来源等信息时，Agent DM 能询问玩家或提出明确选项；不能猜测或擅自操作玩家 PC。
- 受支持的战斗能够通过文字叙述、结构化状态摘要和必要的坐标/位置提示完成，不要求提供实时地图、Token 或动画。
- 拒绝、裁决不确定、世界状态提交以及工具执行故障有可理解的文本反馈。

### 5.2 可选的 AI 插画

- 允许依据 **Agent DM 的叙事描述**生成场景、NPC 或关键事件插画；具体模型、提供方、频次和成本**待决策**。
- 插画应为可跳过、可关闭的非阻塞增强；生成失败不阻断冒险。
- 图像不作为地形、HP、距离、物品归属或任何规则数据的权威来源。
- MVP 不要求将 Rule Engine / State Machine 的结构化场景状态转换成可交互画面，也不要求从图片反向解析世界状态。

### 5.3 MVP 后的 World Creation Agent 与 Visual Presentation 阶段

以下均**不属于本版发布条件**：

- **World Creation Agent**：自动读取 PDF/HTML/Markdown 剧本、从 DM-oriented 或 Gamebook-style 模组生成通用世界、自动生成 NPC Profile、自动编排 Scene Initial State、自动转换地图/图片、跨剧本通用性及质量评估。
- **Visual Presentation Engine**：PixiJS / 专用 Scene Engine 选型、可编程 VTT 地图、角色 Token、行动动画、与 Rule Engine/State Machine 深度同步的世界可视化、图像资产管线和 UI 战术操作系统。

运行时创建内容、组合机制和安装 NPC 行为是受控扩展目标（MC §3.6–§3.7），不等于自动剧本编译或任意代码执行。Coding Agent 是可选生成手段，不是每个自由行动或早期 Agentic 验证前提；完整扩展系统不是本版发布条件。不承诺任意动态代码安全执行、完整开放世界模拟或任意战斗崩溃续玩。固定冒险包仍是初始基线，扩展不可悄悄回写它。

MVP **仍需要可加载的 First Blush 本地结构化内容和场景初始状态**；后置的是“让 Agent 自动创建这些内容”，而不是取消 State Machine 的 `Scene`/`NPC` 初始化能力。未来视觉层仍应消费权威事件和状态，避免成为第二个规则或世界引擎。

**独立验收门槛：** 在禁用图片生成、没有地图渲染、没有 World Creation Agent 的环境下，读取**人工审核的本地 First Blush Adventure Package**，A01 的完整冒险仍必须成功。
## 6. 跨模块契约最低要求

**本节列出产品层级要求，不替代最终的 `MODULE_CONTRACTS.md`。**

### 6.0 冒险内容的静态输入（不是自动生成器）

- MVP 必须能**加载**经过人工整理的固定 `Adventure Package`，从中初始化 Session、初始 Scene、NPC Profiles、初始 NPC 知识与关系、任务/世界标记、必要 Encounter 和 Rule Bindings。
- **[DECIDED]** 统一 load_adventure_package 内部验证后批准并固定包身份/摘要/RulesetBinding；静态验证不保证可玩性/平衡或版权合法。SM Create Session 使用 players[]（player_id / pc_template_id，严格一项）及可信 (principal_id, command_id) / Fingerprint 幂等并原子初始化，不留下半有效 Session。接口/字段 **[PROPOSED; NOT IMPLEMENTED]**，详见 ADVENTURE_PACKAGE_SCHEMA.md §9.1 / §9.1a。
- `Adventure Package` 是**不可变的内容定义/初始状态模板**；`Runtime State` 由 State Machine 管理，初始模板在 Session 创建或相关实体/Scene 首次按需初始化时应用一次，不得在重访时重置已发生的世界变化；NPC 是 Session 级唯一实体。
- MVP 不包含自动 PDF/HTML 解析、内容抽取 Agent、自动 NPC 生成、自动图片生成管线或一般化内容编译器。静态内容的人工准备是测试/内容工作，不是运行时服务。
- 每个规则映射应留存来源或适配记录；未知 Actor/Spell/Item/Feature 不得静默当成合法规则执行。
- **发布/保密**：完整 First Blush 原文及派生数据不得未经许可公开上传；Private fixture 与公开 Schema、合成测试 Fixture 分开存储。

### 6.1 Command / NPC Decision

- **[DECIDED]** 普通游戏命令统一 submit_command(TypedCommand)：session_id / command_id、可信 principal_id、command_type、expected_world_version、强类型 payload 及按操作类型适用的 actor_id；创建、NPC Evaluation、查询/回执保持独立。AP-15：Actor 行动必填真实 Actor，受信系统/世界事件操作可无行动 Actor，但须核验 principal / 机械来源 / 目标；具体来源字段 [PROPOSED / OPEN; NOT IMPLEMENTED]。
- 真人玩家仅代表唯一 PC；NPC 的角色认知/宏观行为由对应 Sub-agent 提议，即时战术/Reaction 由受控 Combat Policy 执行。SM 校验身份、控制权、状态版本及可知信息，Agent DM 不代人物作个人决定。
- 原始 `NPCEvaluationResult` 使用统一七字段；提交只需 evaluation_id + result，SM 从 Task 恢复可信关联，Meta 整批验证原子写入、每任务至多一个最终结果；Action Intent 映射为统一 Typed Command 的世界/规则操作，最终 Schema 为 Proposed / Not Implemented。
- NPC 决策不能直接携带“成功造成多少伤害”“把某目标 HP 改成多少”之类最终机械结论。含攻击模式、目标、法术效果和资源的命令必须明确选择。
- PC 和 NPC 可以共享 Engine 机械语义，Controller 权限在 State Machine 执行，不能通过伪造 `actor_id` 越权。
- State Machine 返回自身验证或 Engine 求值的可解释拒绝，Host 传输回模型，NPC Sub-agent 可以在受限预算内重新选择；异常不能制造已提交的假象。

DM Planner 负责情境语义/GM 裁决（优先规则/Package，未规定时掷骰前确定 DC/后果并可追溯）；SM 负责确定性世界事实/身份/结构/版本验证，Engine 负责 D&D 机械合法性与计算。有限动态 Object / Fact / Connection 及 Conditional World Effect 复用 TypedCommand / Package 受限语义，运行态由 SM 提交，不改静态包、不增加 World Creation Agent；复杂字段/生成仍 [OPEN]，详见 MODULE_CONTRACTS.md §3。

### 6.2 Result / Event

- 区分：执行成功、规则拒绝、GM 裁决、执行异常、State Machine 已提交但响应失败。
- 提交后的规则事件具备稳定顺序、来源和受影响对象；NPC Sub-agent 的原始提议与最终结果不能混为一谈。
- 重试不会重复扣减 Action、Slot、Charges 或写入同一世界操作。
- Agent DM 的叙事要以已提交结果为依据；任何 NPC 即兴表述都不能让未执行的行动自动变为事实。
- 为审计与 Replay 保存已提交的 NPC Intents 和关联 Result；不要求保留完整的 Sub-agent 私有推理过程。

### 6.3 State / Memory / Knowledge

- Session / 世界、Cognition、Perception 等领域明确各自事实和合法写接口；共享设施保障世界/认知版本与授权提交。
- NPC Sub-agent 只读获取被授权的 NPC 视角：完整 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan 和新 Observation，以及当前场景及可用动作摘要；Host 负责组装、不语义筛选，不向 NPC 泄漏 DM 全知视角或其他 NPC 私密内容。
- 已提交重要对话与剧情事件驱动记忆更新，确保同一个 NPC 跨场景和 Session 仍有连续人格与事实；Belief 以追加版本保留来源/状态/历史，不覆盖旧文本，语义压缩/检索和冲突自动消解后置。
- 规则求值采用 CombatSnapshot / NonCombatSnapshot，共享 CharacterState / EffectState 等完整机械基础结构，不按 Intent 裁剪实体字段。SM 提供 Session 固定 RulesetBinding 与独立 RNGContext，Engine 返回强类型 Delta / 候选事件，SM 原子提交状态、RNG、正式事件、CommandReceipt、Outbox；不能用 DM/NPC 文本或事件重算 HP/伤害。
- **MVP 已决定不支持活跃战斗跨进程精确续玩**，只要求非战斗安全恢复与正常战斗结束；不能将 State Machine 持久保存 CombatState 等同于已具备精确中途恢复。

### 6.4 历史 Rule Engine 基线与 Stateless 迁移

现有仓库：<https://github.com/agentic-trpg/trpg-rules-engine>。

2026-10-09 历史审阅基准（当时 `main`：`64dd920`）包含 `PlayerIntent`、`CombatEvent`、`LiveCombatView`、`CombatOutcome`、HTTP Bridge 等；这不是本轮对最新实现的审计或最终接口定义。可以复用正确的规则算法、Resolver、声明式数据与独立回归用例，但须改造状态依赖与执行架构，旧 View / Handle / Stateful API 只属 Transitional / Legacy。

**[必须优先验证的集成缺口]** 该历史基线的玩家入口与内置怪物策略不足以证明当前跨模块闭环。历史有限核对保留于 MC §1.1；2026-10-15 当前 SM checkout / 依赖与实现证据见 §1.2，不能把历史锁定版本当作当前。已有受限组合/导航/门锁/物品与战斗基础，完整战斗 World 集成、Episode / Continuation 等仍待落实；本批未运行集成测试。MVP 仍需受 SM 授权的 NPC Typed Intent → Stateless Evaluation → 原子提交路径，Intent 可由 Combat Policy 产生；独立验收敌方 Agent 宏观决定的真实影响，不要求每次战术来自 LLM，不绕过到私有 Engine 或冒充 PC。

### 6.5 NPC EVA / Action Execution / DM 分离（目标协议摘要）

- SM 提供 Perception 过滤的新 Observation 与完整授权 NPC Meta；首次构建/重建 Context 输入完整 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan，Interactive 后续可复用并增量追加，不必每 EVA 重注入。Host 不做语义筛选、Semantic Retrieval、Memory Ranking 或智能压缩，不增加独立 Memory Agent。
- Interactive 独占主观认知/决策，无新 Background / Memory / Cognition LLM；Gate 决策必经，重要性模型分类可选不逐条强制。Inactive 无持续 Interactive Context，Gate 路由优先 Background、定期/最长等待批次或受控 No-op。
- 统一七字段 Result 通过 submit_npc_evaluation_result(evaluation_id, result) 提交。SM 恢复 Task 关联并确定性整批验证 Meta，任务有效性/版本检查、唯一 Result 选定、Meta 原子提交、可靠交接与 completed 在同一 SQLite 事务；非法 Meta 整批不写并有限修正。
- 模式切换原子取消旧有效 EVA、保留 Meta、移交未完成 Work 并创建新 EVA，不等待旧结束/失败反馈或 ACK；新 Interactive 输入包括当前玩家输入，取消任务不能借新 Invocation 复活。
- Action Intent 合法则可靠交接独立 command_id / Typed Command，非法则独立拒绝，不回滚合法 Meta。EVA / Observation Completion 据必要认知处理与可靠交接维护，不等待 Action Execution 成功；Command Receipt、Pending Choice 独立跟踪。动作失败反馈不自动重做完整 EVA。
- SM 不做自然语言语义验证、不改写 Belief、不增加 Semantic Validator LLM。Belief 版本追加并保留来源/有效状态/历史，错误主观信念不改变世界；LLM 不得将未执行动作记为已发生，SM 只核验结构化来源而不证明文本忠实。
- Recent OB 直接承担短期记忆，`processed` / `pending` 与有效性分离；长期 Meta 可经合法 SourceReference 多记录引用 OB，到期保护历史引用、Pending Work、审计和幂等后才可清理。Game Time 为 TTL 权威，定期 EVA 最大等待严格短于生命周期并留余量；失败/超时/切换/跳时/预算/占用/恢复不能丢失未完成工作。
- Memory Persistence 与 Context 资源管理独立；已入 Context 的 OB 到期不删历史 Token、不自动 Compression / Compaction、不重新 EVA、不保证严格遗忘，下一 Invocation 可增量通知；重建不提供过期 Recent OB。MVP 只预算保护/安全释放和完整 Meta 重建，LLM 调用在写事务外。SM 管简单游戏时钟日程、证据、承诺与安全政策，Intent 不等于行动。
- DM Planner / Narrator 的 Context / 权限隔离，Narrator 只消费玩家获准已提交事实。SM 持续不可用停止权威推进，Host 无影子状态/独立游戏队列，按 SM 持久 Task / Result / Meta / 交接与回执恢复非战斗，战斗精确续玩仍后置。
- P0 规则接口按 MODULE_CONTRACTS.md §4–§6 统一：command_id / operation_kind / 强类型 payload，四种规则结果与 Schema/异常/传输故障分离，封闭 Typed Delta，CommandReceipt 按 (session_id, command_id) 查询。只读 Availability Query 供 UI/Planning，不掷骰/写状态/生成回执，不保证执行成功；完整技能列表/目标枚举非本轮必需实现。查询允许与早期 Stateless Rule Evaluation 实现同步开发，与正式求值共享规则逻辑，不等待 Visual Presentation；文字 MVP 不强制调用，视觉 UI 仍 Post-MVP，本轮不实现。World / Character / Effect / Combat 的负责接口与 RNG 在同一共享事务生效；新接口及内部拆分仍 Proposed / OPEN / Not Implemented。

## 7. MVP 验收标准（End-to-End）

以下为**[建议] MVP 验收合同**；等级、精选规则、具体 First Blush 场景的人工审阅及成本上限仍需讨论。**AI 队友已明确排除，不再保留同伴战斗的强制或候选发布门槛。**

| 验收 ID | 场景与操作 | 通过标准 |
| --- | --- | --- |
| A01 | First Blush 完整文字单人冒险 | 从人工审核、本地载入的 First Blush Adventure Package 初始化 Session；仅一名 PC、无 AI 队友；忠于原剧本的关键场景与合法结局可运行，无需手工修改运行中数据库或 Engine 私有状态 |
| A02 | NPC 对话与探索 | 选定剧本中实际存在的可交互 NPC 由其 Sub-agent 提出角色决策；Agent DM 不直接代言；世界变化经 SM 验证提交保存 |
| A03 | **单人 PC + 敌方 Agent 宏观自主性 / Combat Policy 战斗** | 至少一名敌方 Agent 基于自身授权知识独立作宏观选择；合法采用后可验证地改变 Policy 的后续受控行为，并在合法观察后体现战后认知。Policy 即时 Typed Intent 经 RE / SM 提交，不等 Planner / JEV / Gate / EVA；仅固定策略不能达标，无逐次战术 LLM 要求 |
| A04 | 机械确定性重放 | 相同规则数据、初始状态、独立 RNGContext 和**已提交的 PC/NPC 命令序列**产生相同权威事件、结果和最终状态；不要求 LLM 决策或文案逐字相同 |
| A05 | 非法/不支持请求 | 无效 Actor 权限、目标、资源或规则在相应 Preflight 边界拒绝；没有额外资源扣除、RNG 消耗或越权修改 |
| A06 | 重试与异常 | 已提交 Command 按约定幂等；意外故障不导致状态、资源或事件不一致 |
| A07 | 战斗转交世界 | 玩家 PC 与敌方 NPC 的机械状态按真实来源归属被 State Machine 安全提交，资源不误记到施法目标或其他角色 |
| A08 | 休息与场景推进 | 玩家资源按已选规则恢复，世界时间/Scene 正确推进；若原剧本没有自然休息环节，允许独立集成测试验收，不修改原剧情 |
| A09 | Session 保存与读取 | 重载非战斗 Session 后，PC、任务、Scene、NPC 重要记忆与人物关系一致 |
| A18 | 领域事实与共享提交 | 同一角色探索/战斗共用 HP/实际位置；物品位置与库存投影不能独立改写归属。用药/互动经负责接口同事务提交必要变化、资源/RNG/事件/阶段证据/进度/回执；提交故障回滚，合法结果失败按规则可能仍扣成本；accepted 不等 committed |
| A19 | DM Planner / Narrator 隔离 | Planner 可处理 GM 机密但 Narrator 不读取未公开秘密，不把未提交内容作为世界事实 |
| A20 | NPC Lightweight Gate / Background Evaluation | Inactive NPC 目击重大事件可靠保留证据，必要时一次 Background Evaluation 提出可选认知/行动，重试不重复改变关系 |
| A21 | NPC 日程合法性 | 游戏时钟触发活动，若地点/前提变化则安全中止；不常驻运行所有 NPC 的 LLM |
| A10 | 已支持规则正确性 | 每个纳入范围的机械规则有 SRD/明确裁决依据、公共执行入口、正确/拒绝用例和已知边界 |
| A11 | 角色决策隔离 | 玩家只直接控制唯一 PC；NPC Sub-agent 有自己角色知识与目标；DM 仅主持和协调，不替 NPC 选择行动或偷偷改权威结果 |
| A12 | 纯文字运行 | 关闭图像生成，无地图/Token/动画仍可完整游玩；插画无法影响状态 |
| A13 | **NPC 持续身份与记忆** | 重要 NPC 在多轮互动及必要的 Session 重载后保持身份、记得已知承诺/冲突；不泄漏其他 NPC 的私有事实。是否要求跨场景重逢，以 First Blush 正文为准 |
| A14 | **NPC 子代理故障/拒绝** | NPC 提议非法动作时获得结构化反馈并在有界次数内重试；超时/失败不凭空创建对话事实、伤害或世界状态变更 |
| A15 | 单人遭遇失败分支 | 验证撤退、失败/倒地/死亡至少一种合法处理路径，不允许因“只有一个 PC”而在未获授权时篡改骰点保护主线 |
| A16 | 本地 Adventure Package 初始化 | SM 从人工审核的静态定义原子创建 Session、按需一次初始化 Scene / 唯一 NPC；Encounter 可动态启动，不强制预定义；重访不重置状态；**无 World Creation Agent** 时可重复运行 |
| A17 | 内容授权边界 | 公开代码仓库没有 First Blush 原文、地图、插画或实质性转写的完整剧情包；本地 Fixture 按许可隔离 |
| A22 | Interactive Observation 增量 | 原 Context 按事件顺序增量追加；必经 Gate 决策（模型可选），无逐条 JEV 前置依赖、无新 Background / Memory / Cognition LLM，不改在途输入/Context/KV Cache |
| A23 | Interactive 暂时空闲但 Active | 重大事件可由 SM 批准 Task、Host 执行下一次 Interactive 推理，在途请求输入排队，不修改执行中请求/KV Cache |
| A24 | 一次响应联合输出 | Meta 整批确定性验证原子提交；Dialogue / Action 独立可靠交接，全空 Result 可完成，行动未提交不得叙述成功 |
| A25 | Background 独立行动 | Inactive NPC 经 Gate 一次调用产生行动意图，无需创建/恢复/激活 Interactive Context，最终复用统一命令与规则提交路径 |
| A26 | 低价值 Observation | 获准 Safe Retention / No-op 无完整 NPC LLM 调用，SM 持久完成本轮工作；TTL 前仍 Recent，不强制长期 Memory、不重排同一工作 |
| A27 | Background → Interactive 切换 | SM 原子撤销旧有效 EVA、保留 Meta、移交 Work 并新建，输入含玩家输入；不等旧失败反馈，迟到结果拒绝 |
| A28 | Model Failure / 重投 / 版本冲突 | 唯一 Result / 原子 Meta 与独立 command_id / 可靠交接防重复；未完成认知/交接缺口不跳过 |
| A29 | Memory / Context 解耦 | Meta 提交不强制重建/重复注入，MVP 仅预算保护与安全释放/完整 Meta 重建，无新增智能压缩 |
| A30 | 领域职责与模型运行时 | SM 创建/批准 Task、管 Gate / 模式 / Completion；Host 仅执行模型与 Context，不持久管理游戏状态 |
| A31 | Evaluation / Invocation / Context 标识 | Evaluation 可多次 Invocation，Interactive Context 可多次 Evaluation；Invocation/Context ID 不要求提交必填，Evaluation ID 不能充当认证 |
| A32 | 原始 Result 与最小提交 | 两模式兼容七字段可全空，只提交 evaluation_id + result，SM 从 Task 恢复关联，拒绝模型自报身份/权限 |
| A33 | 无 ACK 的 EVA 完成 / 行动交接 | SM 以原子 Meta / Result / 可靠交接完成 EVA；动作失败/等待 choice 独立跟踪，不自动重做 EVA，读/追加/模型返回不完成 |
| A34 | SM 持续不可用及恢复 | 停止权威推进，Host 无影子状态/游戏队列；从 SM 状态/任务/回执恢复非战斗，战斗精确续玩后置 |
| A35 | 最小提交与唯一 Result | evaluation_id + result、可信运行环境与 Task 恢复；相同返回原反馈，已选后不同拒绝，行动独立 command_id |
| A36 | 原子 Meta 与有界修正 | 任一更新非法整批不写，不留下 Goal/Plan 半批；有效 EVA 内修正，任务/版本检查与提交同事务 |
| A37 | 非阻塞模式切换 / Invocation 失败恢复 | 预算内 running，同 evaluation_id / 新 invocation_id 重试；仅耗尽或无法继续 failed，切换 cancelled 并新建、不等旧反馈；未完成观察持久，丢响应先查，不复活旧任务 |
| A38 | EVA / Action Execution 分离 | Meta 合法不因行动非法/失败回滚，可靠交接后 EVA 完成，Command 失败/choice 独立跟踪，反馈不自动重做 EVA |
| A39 | 完整授权 Meta 与 Belief 演变 | 六类完整授权 Meta + 冻结完整授权 Recent OB List（含 processed／pending）、Host 不语义筛选/检索/排名/智能压缩，Context 增量复用；Belief 追加版本保留来源/状态/历史 |
| A40 | 确定性验证边界 | SM 不判断自然语言忠实、不改写 Belief、不新增语义验证模型；错误主观信念不能改变世界事实 |
| A41 | OB 游戏时间与双生命周期 | `processed` / `pending` 与 Recent / Expired 分离；TTL 只据 Game Time，到期移出近期输入，Pending 证据保留、processed 不重触发 |
| A42 | OB 引用与清理保护 | 多长期 Meta / 历史引用归档必要证据；工作完成且无保护关系才可清理，不破坏任务/交接/审计/幂等，内部保留不等 NPC 记得 |
| A43 | 双用途 JEV 与模式调度 | Perception / Cognition Gate 的输入输出及权限分离；Urgent / Deferred / Irrelevant 路由当前模式，错误不当 No-op，同 NPC 至多一个有效认知 EVA |
| A44 | 定期 EVA 与异常越期 | 最大等待严格短于 OB 生命周期且留余量；失败/超时/切换/跳时/预算/占用/崩溃保护 Pending Work，周期短于 TTL 不冒称完成保证 |
| A45 | Context 中 OB 到期 | 下一 Invocation 可增量通知；不删旧 Token/自动压缩/重做 EVA、不保证严格遗忘；新建/重建排除过期 Recent OB |

**独立正确性要求：** 关键规则预期来自 SRD 5.2.1 或有记录的公开裁决，而不是用 Engine 自身输出生成正确答案。多 Agent 能力另需测试角色可知事实与行动授权，不等同于规则测试。

A22–A45 为公开原创合成场景的架构验收目标，细节见 `AGENT_ARCHITECTURE.md` §11.3–§11.6、`STATE_MACHINE_ARCHITECTURE.md` §11.2–§11.5、`MODULE_CONTRACTS.md` §12.1–§12.4；本轮只检查文档，不表示运行测试已通过，不扩写 First Blush 剧情或 MVP 产品范围。

### 7.1 最小黄金测试场景

- **Invocation/Payment：** 选一个动作，仅执行其所选 Activity 并支付相应 Action/Slot/Charge。
- **PC/NPC Actor 隔离：** 玩家仅操作 PC；敌方 Agent 的宏观提议经可信关联采用，Combat Policy 发出受授权即时 Typed Intent，SM 验证并提交 RE 结果；机械可知视图不泄漏秘密。
- **NPC 知识边界：** 给 NPC 一个它不知道的世界秘密，确保回答与战术不依赖该事实；同一 NPC 后续能读取明确获知的线索。
- **Agent 处理拒绝：** 不把失败提议说成已经成功；重试/超时受控。
- **状态与 RNG：** 无效目标、缺少资源、不支持机制及注入故障均不污染权威状态或随机序列。
- **共同提交：** HP/Slot/Effect/Inventory/战斗流程/RNG 必要变化经负责接口在同一共享事务提交，Actor 归属正确，无双权威 CombatOutcome 回写；Handler 推进/暂停及回滚证据见演进计划 §8.1。
- **展示非权威：** 无需视觉层也能完成冒险；文字和插画不会自行造成伤害、位移或资源变更。

## 8. 里程碑与开发决策顺序

**能力轨道与早期验证 `[DECIDED]`：** 以当前 SM＋RE 推进对象/动作、活动、感知/Policy、真实规则集成与 Episode，并尽早交错验证真实模型的开放行动映射、世界后果及 NPC 私有自主行为（演进计划 §8）；不等完整传统引擎或完整 Host。确定性回归单独验证执行/授权/幂等/RNG/故障及延迟、重复、失败模型输出。v0.14 强制 EB 顺序撤回，EB-1～EB-3 仅作可选框架评估。下列 M0～M4 保留产品里程碑，不是早期 Agentic 试验的全量或严格串行前置条件。本批未执行任何运行试验。

| 阶段 | 目标 | 完成标准 |
| --- | --- | --- |
| **M0：Scope 冻结** | 确认 First Blush、NPC Sub-agent 自主性、精选规则、人工内容录入及非视觉/无 World Builder 范围 | 文档状态升级为 Approved，待定项收敛，产品决策记录齐全 |
| **M1：MVP Stateless Evaluation / State Cutover + Correctness Closure** | 按 MODULE_CONTRACTS.md 将 MVP 选定的原有规则能力迁入无 Legacy 执行依赖的求值路径，修复单人战斗核心正确性问题 | 完整 Snapshot / Typed Intent / Pinned RulesetBinding / Explicit RNG → Result 与 SM 原子提交有执行证据；Activity 选择、支付归属、拒绝回滚、重复请求均被验证，并列明仍未迁移的旧能力；不宣称全 Engine 迁移完成 |
| **M2：Cross-module Contracts / NPC Intent** | 定义双路径、Session / Scene、NPC Role Memory、Command / Event、统一权威 State/Delta/Commit 与受控 NPC 求值入口 | 敌方 Agent 宏观决定经授权影响 Combat Policy，即时动作不依赖 LLM；非战斗 NPC 独立对话，Episode / Continuation 未决 ABI 先审阅 |
| **M3：First Blush Text-first Vertical Slice** | 人工整理剧本数据，加载场景初始状态，打通 NPC 独立互动、敌方 Agent 战斗、结局持久化 | A01/A02/A03/A09/A13 全部通过；图片完全可关闭 |
| **M4：MVP Acceptance / Release** | 依据实际玩家体验收敛问题与规则范围 | 获准的 A01–A40 均有验收证据，明确记录未支持规则与 Agent 成本限制 |

只读 Action Availability Query 可随 M1 的 Stateless Evaluation 早期开发，先覆盖基础战斗操作并共享合法性逻辑，无 RNG/写状态/Delta/事件/回执；不依赖视觉阶段，也不作为当前文字入口发布条件。

**后续阶段（不阻塞 MVP）：** `World Creation Agent` 自动从合法输入剧本生成多类型 Adventure Package；`Visual Presentation Engine` 消费已有的权威状态和事件进行视觉呈现。二者是未来方向，不要提前作为当前 Milestone 的依赖。

### 8.1 与 Rule Engine Backlog 的关系

- `trpg-rules-engine/BACKLOG.md` 是**技术缺口清单**，不是跨项目的 MVP 任务清单；不必清空 Deferred 才宣布 MVP 完成。
- 每项新规则需求都要对应明确的单人冒险场景及可独立验证的机械结果。
- **新增优先级依赖：** 验证受控 Combat Policy 的 NPC Typed Intent 入口、敌方 Agent 宏观决定的授权/行为影响，以及机械感知与 RE 阶段协议；不能只以默认 Monster AI 宣称自主性达标。SM 锁定 RE 的升级须独立兼容性验收。
- Refactor 进度首先由**已消除的 Stateful 执行依赖和真正迁移的原有规则能力**证明，再结合规则正确性、可执行场景、跨模块一致性与 NPC Agent 独立行为；新增规则、Adapter、文件、Commit 或测试数量不能代表完成迁移。
- 历史审阅记录的 Invocation 多 Activity 误执行和 `CombatOutcome` 支出归属问题须在当前代码中核对处理状态，并作为独立正确性回归；不把旧代码事实当作最新完成情况。

## 9. 决策登记（Decision Register）

| ID | 产品问题 | 当前决定或建议 | 状态 |
| --- | --- | --- | --- |
| D01 | 首版正式 RuleSet？ | 设计基线为 D&D 2024 修订规则：PHB 2024、DMG 2024、MM 2025、SRD 5.2.1；精选内容/规则来源仍逐项核实 | [DECIDED] 基线；具体覆盖/取值待确认，不等于全规则书支持 |
| D02 | 首版重点角色等级？ | 候选 1–5 级，已有高等级实现保留 | [待决策] |
| D03 | 真人玩家与角色数？ | **一个真人玩家，仅控制一个 PC** | **[已确认]** |
| D04 | 首版精选 Spell / Feature / Item / Monster？ | 从单人冒险和共用机制反推 Rule Support Matrix | [待决策] |
| D05 | 交互方式？ | **文字/自然语言优先** | **[已确认]** |
| D06 | Visual Presentation 是否进入 MVP？ | **不进入；战术视觉/场景深度联动留待 MVP 后** | **[已确认]** |
| D07 | 首版持久化保障？ | **非战斗 Session 可恢复；活跃战斗跨进程精确恢复在 MVP 之后** | **[已确认]** |
| D08 | GM Override 权限与审计？ | 显式授权、结构化、有限范围并记录来源 | [待决策] |
| D09 | 冒险内容来源？ | **First Blush** 作为首个本地 MVP Golden Adventure，需合法获取与人工审核/适配 | **[已确认；正文核对待做]** |
| D10 | 部署与成本边界？ | 本地/单实例优先；NPC Sub-agent 按需执行 | [待决策：预算上限] |
| D11 | 三大核心模块是否独立进程？ | 不强制，先保证逻辑职责和状态权威独立 | [待决策] |
| D12 | 开放世界裁决边界？ | 从场景选择 Engine 机械求值与 GM 语义裁决 / SM 提交的职责 | [待决策] |
| D13 | AI 队友是否进入 MVP？ | **不使用 AI 队友；以单人剧本代替同伴组队验证** | **[已确认]** |
| D14 | NPC 由谁控制？ | **NPC Sub-agent 独立认知/对白/宏观行为；受控 Combat Policy 即时执行；Agent DM 主持协调** | **[DECIDED] 2026-10-12 更新** |
| D15 | AI 插画是否必需？ | 可选，且不影响规则与状态 | **[已确认：非必需]** |
| D16 | 敌方 NPC 即时战术由谁选择？ | **SM 协调 Combat Policy / 确定性机制与 RE；不依赖 Planner、JEV LLM、Cognition Gate 或 EVA，机械察觉未知不当已察觉；至少一名敌方 Agent 宏观自主性仍验收** | **[DECIDED] 2026-10-12 取代逐次 Sub-agent 战术要求** |
| D17 | NPC Sub-agent 并发数量、调用预算和降级方式？ | 事件驱动、按需调用、有界执行；具体数值尚待性能测试 | [待决策] |
| D18 | NPC 的长期记忆及知识粒度？ | 角色可知事实由授权 Perception 提供，动机/关系/关键记忆由 Cognition 维护版本，按 MC §0.3 修订旧分工 | [已确认：原则；Schema 待设计] |
| D19 | NPC 和 DM 是否使用相同底层模型？ | 可以复用模型与进程，**必须逻辑上隔离角色上下文和决策接口** | [已确认：允许共享；技术待选型] |
| D20 | NPC 决策如何接入当前 Engine 怪物战斗？ | 验证宏观 Agent → SM 授权 Policy → NPC Typed Intent / RE / Commit；固定策略不是独立认知验收，版本差异见 MODULE_CONTRACTS.md §1.1 | [PROPOSED / OPEN]；集成待验证 |
| D21 | World Creation Agent 是否进入 MVP？ | **不进入**；MVP 使用人工整理的本地 First Blush Adventure Package，不开发通用剧本导入和自动世界构建 | **[已确认：MVP 后]** |
| D22 | 支持 Gamebook-style Adventure 自动转换？ | **不作为 MVP 交付**；第二种剧本格式待 World Creation Agent 阶段讨论 | **[已确认：MVP 后]** |
| D23 | Visual Representation Engine 是否进入 MVP？ | **不进入**；文字优先，可选非权威静态插画 | **[已确认：MVP 后]** |
| D24 | 第一部剧本如何初始化世界和 NPC？ | **人工审阅并制作最小静态 Adventure Package + Initial State Templates**，由 State Machine 加载 | **[已确认：原则；Schema 待设计]** |
| D25 | First Blush 能否公开随项目分发？ | 未取得单独再分发/改编授权，不随公开仓库发布其原文、地图或实质性改编内容 | **[发布限制]** |
| D26 | 普通 NPC/怪物的认知 Agent 覆盖？ | 即时战术统一不依赖 LLM；哪些角色需要认知 Agent 及默认 Policy 配置仍待审，至少一名敌方 Agent 的宏观自主性验收保留 | 即时边界 [DECIDED]；认知覆盖 [OPEN] |
| D27 | NPC Persistent State 与两种 Evaluation Mode？ | **唯一权威状态；Interactive 活跃独占 LLM 认知/行为；Inactive Gate / 一次性 Background 不激活 Interactive Agent** | **[已确认：2026-10-10 架构原则]** |
| D28 | 模式切换 / Observation Processing Completion 最终 Schema 与预算？ | 取消旧有效 EVA 并新建、不等旧反馈；Meta 原子提交与可靠交接完成 EVA，行动独立回执；状态编码、模型/Gate 阈值及预算待验证 | [原则已确认；接口 Proposed / Not Implemented，技术细节待评审] |
| D29 | OB 短期记忆、引用与 EVA 调度？ | OB 直接承担短期记忆，处理/保留分离、Game Time TTL、引用归档与 Pending 保护；定期最大等待严格短于生命周期且留余量，Interactive 必经 Gate 决策（模型可选）、无新 Background EVA | **[已确认：2026-10-11]**；TTL / Schema / 模型 / 周期 / 清理算法仍待评审 |
| D30 | 完整事态观察与机械审计？ | 本场参与者 Turn／外部 Round 聚合 OB；机械审计不自动进入感知，Event-level OB 非永久粒度 | [DECIDED]；过滤／参战切换／迁移恢复待验证，Schema / 生命周期 [OPEN; NOT IMPLEMENTED] |
| D31 | 中途选择与正常求值历史依赖？ | 连续规则尽量一次求值；目标 Interrupt 可持久暂停/恢复、RNG 一致且不占长事务；正常求值不反复加载完整 Event Log | [DECIDED]；通用 ABI / 最小路径 [OPEN; NOT IMPLEMENTED] |
| D32 | 游戏核心演进与动态扩展？ | 当前 SM＋RE 主线，可替换子系统；Evennia 整体迁移 OPEN，`Evennia_base` Deferred / Optional evaluation；扩展不改固定包，Coding Agent 可选 | [DECIDED] 2026-10-12；具体机制/扩展协议 OPEN，无运行验收，单人文字范围不扩大 |
| D33 | 状态持有与事务组织？ | WorldFacts、CharacterFacts / 机械组件、CombatRecords、Activity、Effects 分责；Facts / Records 读写 SQLite，一次操作共享提交 | [DECIDED]；部分基础已实现见 MC §1.2，完整目标/预算 OPEN |
| D34 | A1 / A2 与 World 设计如何落实？ | 探索 Navigation / Activity + WorldHandler；战斗 CombatHandler + RE；共用实际位置/对象能力。StateMachine 统一 API / 装配，按需显式组合减少 Mixin，不强制全层/ECS | [DECIDED] 方向，完整目标未完成；架构待办统一 MC §13 的 A1 / A2，字段候选见 World 草案，不设平行 Backlog |

**当前下一步：** 按演进计划 §8 审计现有能力并选择最小原创纵向场景，游戏机制与早期真实 Agentic 证据交错推进；可选 Evennia 评估见 §9，不阻塞主线。完整产品仍须合法取得并核对 First Blush、人工准备本地内容与精选规则、验收敌方 Agent 宏观自主性。本批不实现或创建仓库。

## 10. 文档维护与变更规则

1. 本文件是**跨 Repository 的 MVP 产品范围依据**；正式确定后，模块设计和 Backlog 应引用它，而不是私下重新定义首版目标。
2. 改变产品范围时应注明：变化原因、受影响的 Gameplay Scenario、规则成本、四模块接口影响、需要更新的验收项。
3. 各个模块仓库可保留更全面的技术债或未来 Feature 清单；进入 MVP 开发范围必须有对应的场景/验收理由。
4. 最新实现是否已具备能力，始终以对应模块的实际代码、测试及审核清单为准。本文件的历史实现快照不作为持续更新的完成状态表。
5. 每完成若干开发 Batch，应回看 MVP 场景是否更接近可玩状态；如果只是扩大规则条目但没有改善场景体验，需要重新考虑优先级。
6. 文件审批人、文档维护流程以及决策记录位置：**[待决策]**。

**v0.17 修订范围（2026-10-15）**：遵循 MC v0.15 细化 World / Character / CombatRecords / Activity / Effects、A1 / A2 和合法失败语义，更新设计规则基线，引用当前实现静态证据与 World 候选草案；不要求完成整个组件目录，不扩张单人文字/恢复范围，不修改运行代码。

**v0.16 修订范围（2026-10-12）**：按 MC v0.14 同步领域状态责任、有状态 Combat Handler 与共享提交，修订旧 SM 独占限制；目标拆分不代表实现。规则/领域/提交校验、防旧防重、观察/认知隔离及 EVA 独立行动协议保留；后续定向验收见演进计划 §8.1。仅 Markdown，未实施 Handler 重构或 RE 日志解耦，不扩张产品范围。

**v0.15 修订范围**：恢复 SM＋RE 当前基础定位，撤回 Evennia 优先采用/强制 EB 顺序；同步可组合机制与早期 Agentic 交错验证、可选 Coding Agent。保留单玩家/单 PC、文字、敌方宏观自主性、CombatEpisode、固定冒险基线和恢复边界；只改文档，无代码/运行验收。

**v0.14 修订范围（历史，采用路线/强制顺序已由 v0.15 撤回）**：同步 Evennia 已选方向、SM 可替换实现、整场 CombatEpisode、受控扩展与 EB 验证顺序；保留单人/单 PC/文字优先、敌方 Agent 宏观自主性、固定冒险包及战斗恢复边界。仅文档，迁移与运行验证未执行。

**v0.13 修订范围**：按已确定双路径更新 D14/D16/D20/D26、G05/G10/A03 及集成里程碑；保留至少一名敌方 Agent 的独立认知/宏观行为影响，取消每次战术必经 LLM 要求。同步 Episode / 审计 / Interrupt 目标，具体 ABI 未冻结，无代码/依赖升级，不扩张单人/视觉/内容和活跃战斗恢复范围。

**v0.12 修订范围**：仅同步 OB Processing / Retention、Game Time TTL / 引用保护、JEV 双职责、当前模式及有界定期 EVA 的既有可靠性验收；Context 到期与持久化/压缩分离。无实现代码、不冻结参数、不修复 Event-time Perception P1，也不扩张 MVP 产品范围。

**v0.11 修订范围**：同步统一 TypedCommand、GM 裁决/有限世界创造边界、AP-15 类型化 Actor 约束及只读查询的早期开发计划；没有实现 API 或扩张视觉/多人范围。

**v0.10 修订范围**：统一内置 PC Templates、可信创建幂等与 Scene 按需一次初始化；保持单人和既有恢复范围，候选接口不代表实现。

**v0.9 修订范围**：同步 P0 Snapshot / Payload / Ruleset / Typed Delta / RNG / 事件 / 命令键回执及只读查询的目标语义，澄清预算内 Invocation 错误保持 EVA running；不修改 MVP 产品范围、不要求本轮实现接口。

**v0.8 修订范围**：简化 EVA 最小提交和任务状态，原子 Meta、独立 Action Execution / 可靠交接、完整授权 Meta 输入与 Belief 历史；保留 First Blush、一名 PC、无 AI 队友、敌方 NPC Sub-agent 自主战斗、文字交互、简单日程与非战斗存档恢复要求。当时的统一权威状态与 Rule Engine 核心契约未作重设计。

---

## 附录 A：相关资源

- [现有 Rule Engine Repository](https://github.com/agentic-trpg/trpg-rules-engine)
- [Rule Engine 技术 Backlog](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/BACKLOG.md)
- [Rule Engine Capability Matrix](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/docs/capabilities.md)
- [Engine / Bridge Intent Parity](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/docs/dev/bridge-intent-parity.md)
- [Rule Engine Development Standards](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/AGENTS.md)

> **下一步：** 获取并审阅 First Blush 原始剧本（当前未提供正文，尚不能声称完整提取或兼容验证）；以它的真实内容确定 Adventure Package/Initial State Schema、NPC/PC Actor 路由和精选规则清单。World Creation Agent、Gamebook 转换及可交互视觉引擎均延后。
