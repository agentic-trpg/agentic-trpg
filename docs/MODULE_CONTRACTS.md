# Agentic TRPG — Module Contracts（目标架构与 MVP）

## 2026-10-27 当前源码与说明维护入口

本批基线为文档 `88bb8dd`、SM `b9ae704`、RE `7bb02b9`（均已 fetch 核对）。
SM 当前 main 已包含 Session RAM、持久提交后发布、运行实例字段及通路反向索引的
受限实现；容器重量／机关索引跨命令复用已有生产接线。当前依据是源码和既有
[实例归属证据](reviews/RUNTIME_INSTANCE_OWNERSHIP.md)，不再把下方 10 月 21 日的
NOT IMPLEMENTED 或“仅配套分支”当作当前 main 的状态。完整恢复／未来多人等原有
限制不因本批说明补充关闭；本批没有重新运行历史游戏验收。

新增强制开发规范见 [源码说明维护](CODE_DOCUMENTATION.md)，覆盖持续维护、仓库级
Skills 和固定检索实验／未来索引输入；本批证据见
[核对报告](reviews/CODE_DOCUMENTATION_AND_SKILLS.md)。历史段落保留日期和原语境。


**2026-10-22 运行实例字段归属补充：** §2.3a 的实例字段、关联／索引与局部准入为
Architecture Decision Status **[DECIDED]**。本分支从 `origin/main@5619e7a` 创建；
下述 10 月 21 日及更早的 `[NOT IMPLEMENTED]`、源码和验收数字保留其原日期，
不代表本次 SM 实现分支的状态。当前实现与验收证据单独见
[运行实例核对](reviews/RUNTIME_INSTANCE_OWNERSHIP.md)，不得仅据字段或类名认定迁移完成。

**2026-10-21 Session 内存运行架构决定：** Architecture Decision Status **[DECIDED]**；完整内存运行层与持久提交后发布协议 Implementation Status **[NOT IMPLEMENTED]**；Acceptance Status **未执行运行验收**。本轮只修改三仓库文档。§0.3、§2.3–§2.4、§4、§6 已协调现行正文，替代“普通业务每次直接读 SQL 装配事实”的目标解释；历史 v0.4 Review、§1.1–§1.7 和原验收数字保留原日期。当前源码及主要差距见 [§1.8](#18-2026-10-21-session-内存运行层基线核对)，迁移沿用 §13 的 C-25／C-27、A2 和演进计划 DS 轨道。

> **版本：** v0.18 / Draft for Review
>
> **日期：** 2026-10-21（文档补充，不冻结新接口版本）
>
> **性质：** 跨模块目标接口的最高权威规范；具体 ABI 仍为草案，**不是已实现 API**
>
> **归属仓库（建议）：** `agentic-trpg/agentic-trpg/docs/MODULE_CONTRACTS.md`
>
> **配套文档：** [MVP Scope](./MVP_SCOPE.md) v0.20、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.14、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.20、[Agent Architecture](./AGENT_ARCHITECTURE.md) v0.18、[Game Core Evolution Plan](./GAME_CORE_EVOLUTION_PLAN.md) v0.7、[World Subsystem Design](./WORLD_SUBSYSTEM_DESIGN.md) v0.4（专项草案，遵循本文）
>
> **历史代码核对基线（§1 历史表沿用 v0.1，2026-10-12 前批有限核对见 §1.1）：** `agentic-trpg/agentic-trpg@4190833`；`agentic-trpg/trpg-rules-engine@64dd920`
>
> **Architecture Decision Status：** `[DECIDED]`、`[PROPOSED]`、`[OPEN]`。
>
> **Implementation Status：** `[IMPLEMENTED]`、`[PARTIALLY IMPLEMENTED]`、`[NOT IMPLEMENTED]`；与架构决定分轴记录，已决定不代表已实现。

**v0.18 修订摘要（2026-10-19）：** 确认运行时只读输入复用、按需派生及事务依赖版本的共同规范（§2.3），规则加载身份契约（§4.3）与 World 的 Grid／Environment 专项相互引用；§2.4 追加 Package 创建参照、完整实例化与统一实例读取要求。§1.4 按当前分支及固定依赖区分已有实现、待落实设计和兼容降级；不新增待办、不修改代码、不合并 main。下述 10 月 17／18 日摘要保留为历史。

**2026-10-20 文档补充：** §2.3 集中维护快照、定向查询、缓存与查询索引的使用原则及性能验收要求；World §2.0b–§2.0c 仅细化空间／环境场景。§1.5 记录本次有限代码核对，修正较早的 Grid 现状引用。本次完成的是文档约束，局部占用查询、局部校验及相关优化仍待实现或验证，没有修复 SM 性能问题、增加接口或关闭实现待办。

**2026-10-17 v0.4 评审同步：** [Module Contracts](./MODULE_CONTRACTS.md) 继续是跨模块最终权威；[v0.4](./reviews/agentic-trpg-architecture-contracts-2026-10-17-v0.4.md) 仅保留审查记录。旧修订摘要中的整场 CombatEpisode／旧 OB 术语仅记录历史，现行目标为 Turn／Round Episode、单一有界 Recent OB List 和 `pending`／`processed`。每条新 OB 必经 Gate 决策（模型可选）；EVA 冻结完整授权近期窗口，processed 可影响 Meta，提交只完成固定 pending 覆盖。代码证据保持原日期／SHA，本次不刷新实现状态或冻结新增 ABI。

**2026-10-18 定向同步：** 上段为 10 月 17 日历史记录。本轮当前代码依据更新至 [MC §1.3](./MODULE_CONTRACTS.md#13-2026-10-18-远端实现核对定向静态调查)，区分 main 当前实现、ObjectSpatial 分支沿革与未实现目标；Scene 结构与环境边界遵循 MC §0.3a。保留 Turn／Round Episode、Recent OB／Gate／EVA、CombatPolicy 及版本／幂等／RNG／事务契约，不扩大 MVP，不冻结新 ABI。

## 0. 用途与冻结策略

本文定义 Agent Host、State Machine、Rule Engine、Perception、NPC Evaluation、DM Narration 与 Adventure Package 的交接边界。既有规则契约与最小安全边界继续作为设计依据；当前以 SM＋RE 为开发/运行基础，按 §14 能力轨道交错验证游戏机制与 Agentic 行为；Evennia 整体迁移不是前置条件。本批不冻结新 ABI，也不将全部 RE 迁移设为最小验证前提。v0.5 统一 P0 Snapshot / Request / Result、封闭 Typed Delta、ProposedEvents、独立 RNG、CommandReceipt 和只读 Availability Query，并澄清 Invocation 错误不立即终止有效 EVA。v0.6 统一 Adventure Package 加载、可信创建幂等、静态模板与 SM 运行时边界（§10），候选 combat.start / rules.effect 复用本协议。v0.7 统一 submit_command / GM Adjudication、有限动态世界操作和 AP-15 按操作类型校验 Actor，并同步只读查询的早期开发计划。v0.8 将 PER-01～PER-08 接入既有事件/可靠工作协议（§7），区分 Signal、察觉判断、授权观察与 NPC 认知。v0.9 明确 OB 短期记忆、独立 Processing / Retention、Game Time TTL / 引用归档、JEV 双职责和有界 EVA 调度，当时未修改 Signal / Event Evidence 计算。

**v0.10 修订摘要（Batch A）：** §7 明确 Event-local / Signal-scoped Evidence、逐 Signal 候选发现与事件级证据并集、可信字段完整性及同一 SQLite 原子提交；区分 `trpg-state-machine@5deea78` 历史实现与目标，新增 §12.5 合成验收目标，事件阶段采集协议仍 [OPEN]。本轮仅更新文档，不实现 Event-time Perception P1。既有状态所有权、Rule Engine、OB 生命周期、Game Time TTL、EVA 调度与 MVP 产品范围不变；结构决策标为 [DECIDED]，具体 API/字段实现仍 [NOT IMPLEMENTED]，未冻结细节单列 [OPEN]。

**v0.11 修订摘要：** 统一 Immediate Mechanical Response / Agent Cognitive Response、WorldEpisode / EpisodeObservation、机械审计分流、状态式规则求值与 Interrupt / Continuation 目标；同步敌方 Agent 宏观自主性验收。§1 记录已核对的 SM / RE 基线，具体 Episode / Continuation ABI 仍 [OPEN; NOT IMPLEMENTED]。章节的目标接口标记不否认 §1 列明的受限本地实现；本轮只改文档，不升级依赖或实现接口。

**v0.13 修订摘要：** 撤回未合并 v0.12 的 Evennia 优先采用决定与强制 EB 顺序，以现有 SM＋RE 补强程序化游戏核心（§0.2），允许基于证据重构/替换子系统。新增可组合世界机制原则（§3.7），受控扩展不绑定 Coding Agent；§14 将真实 Agentic 验证提前并与机制轨道交错。保留 CombatEpisode、信息隔离、可靠处理及已有规则边界；研究与具体方案不等于实现或验收。

**v0.12 修订摘要（历史，采用决定及强制 EB 顺序已由 v0.13 撤回）：** 曾提出 Evennia 优先底座、保留 RE、允许 SM 迁移/重构；整场 CombatEpisode 与受控扩展原则保留。该批没有迁移或运行验收，代码基线与规则完成状态不变。

**证据与状态治理 `[DECIDED]`：** 架构决定与实现状态分别记录；只有源码、对应测试和适当验收证据支持时才标已实现，并限定路径、版本和消费者。历史 Review／旧快照不能覆盖现行决定，代码现状也不自动成为最终架构。当前对齐证据见 §1.6。

**规范层级 `[DECIDED]`：** 本文是跨模块目标接口与状态所有权的最高权威规范；MVP Scope 定义产品范围，State Machine / Agent Architecture 和 Adventure Package Schema 在此契约内细化职责，Game Core Evolution Plan 记录能力演进、机制研究与验证门槛，README 提供入口。项目目标约束实现，旧 Nat20 / Rule Engine 代码只作为待重构的实现和回归证据，不能反过来限定目标架构。本文中的 [DECIDED] 约束持续有效；文档整体 Draft 不撤销这些决定，也不把 [PROPOSED] / [OPEN] 的具体 ABI 字段或实现选择升级为已批准。

**v0.14 修订摘要（2026-10-12）：** 按领域管理状态、按事实确定权威、按操作组织事务（§0.3）。建立状态责任表，确认有状态 Combat Handler（§0.4），将规则、领域和提交校验分责（§6.5）；保留现有公开协议及历史代码基线。原则已决定，具体拆分、Handler API 与日志解耦尚未实施。

**v0.15 修订摘要（2026-10-15）：** 细化 §0.3 的 World / Character / CombatRecords / Activity / Effects 归属，补充 A1 探索与战斗的操作编排分离、A2 StateMachine 模块化与职责边界（§0.5–§0.6）；§1.2 重新只读核对 SM 代码并区分已提交实现与脏工作区。保留历史决策记录，以本次补充替代旧的合并所有权和“Handler 尚不存在”现状描述；不改运行代码、不冻结 Schema / ABI。World 候选组件见专项草案；后续工作仍登记在 §13。

**必须满足的不变量 `[DECIDED]`：**

1. 同一 Game Session 的每项当前游戏事实有明确的权威来源和写入责任。不同领域模块可以管理并持久化自己的状态，通过共享提交设施使一次不可分割操作同成同败（§0.3）；不要求单一 SM 模块理解、保存和批准全部业务细节。`trpg-state-machine` 仍是当前开发与运行基础，各领域不得复制同一当前事实形成双重权威。
2. 最终 Rule Engine 是 **Stateless Rule Evaluation Engine**，彻底替代原 Stateful Combat 执行架构；不能持有独立权威 Runtime State 或直接提交数据库，也不能以持续扩张 Stateful Adapter 作为最终方案。其计算边界见 §4，迁移完成标准见 §14.1。
3. `evaluation.status == "accepted"` 不等于 `commit.status == "committed"`；拟议事件不得提前发布为 WorldEvent。
4. Agent 提交的是意图或提议，不是 HP、骰点、资源支付等机械事实；Narrator 消费已提交、经授权的事实。
5. 可重试、确定性、版本和授权均在可信系统边界实现，不能仅依赖 LLM 自律。
6. 可信提交必须保持原子性与短事务，**不得在写事务内等待 LLM 或长时间 Rule Evaluation**。Python + SQLite WAL 是当前 SM 实现基线，不是未来子系统或可选框架的永久后端约束；改变存储/提交实现须独立验证等价正确性，本批不固定新配置或引入分布式协调。
7. NPC 只有一份 Persistent State；Interactive 活跃期间独占该 NPC 的 LLM 主观认知/自主行动，Background 一次性推理不需要 Interactive Agent Context。新消息/接口均为 `[PROPOSED; NOT IMPLEMENTED]`，架构原则确认不等于 API 已实现。

8. NPC Cognition 与 Perception/Observation 按责任创建/批准 Evaluation Task、管 Gate / 模式 / Observation Completion；Host 仅 LLM Runtime，不持久管理权威游戏状态或完成结果。当前 SM 入口在分阶段演进中可保留。

**目标设计由领域模块负责数据与不变量，RE 负责机械规则，共享提交设施负责共同提交边界；Host/LLM 只提出非权威数据。** 本文未专门指明当前代码的“SM”沿用现有游戏核心入口/职责总称，不能据此要求一个中心类包揽业务。

### 0.1 Immediate Mechanical Response 与 Agent Cognitive Response `[DECIDED]`

| 路径 | 决策与执行 | 依赖边界 |
|---|---|---|
| Immediate Mechanical Response | Combat Handler / 相关领域处理者组织可信机制、受控 Combat Policy 和 RE；即时战术、Reaction、自动效果、战斗触发的候选结果经各领域接口在共享事务提交 | 不依赖 DM Planner、JEV LLM、Cognition Gate 或 EVA；所需察觉/规则资格必须来自可信确定性或机械判定，不把未知当已察觉 |
| Agent Cognitive Response | NPC LLM / EVA 解释授权经历，提议主观 Memory、Belief、Relationship、Goal、Plan、宏观行为和角色对白；Host 执行模型，NPC Cognition 验证并持久保存版本 | 消费已经确认察觉的证据；认知延迟/失败不阻塞即时机械链，也不追溯改写已提交结果。玩家叙事仍由独立 DM Narrator 基于授权事实呈现 |

Combat Policy 是 Combat Handler 协调的可信非 LLM 行为职责，不新增 Agent、服务或仓库；它从已授权目标/策略约束及机械可知视图选择即时 Typed Intent，不能读取 NPC 无权知道的世界秘密。宏观目标可先由 NPC Agent 提议、Cognition 验证采用并交接，之后即时执行无需每回合再次调用 LLM；策略更新只影响后续合法操作。策略算法、版本/授权字段与目标转换协议 [PROPOSED / OPEN; NOT IMPLEMENTED]。机械察觉不足须显式走受支持的机械判断或报告能力缺口，不能让 JEV 猜测后解锁攻击/Reaction。

至少一名敌对 NPC 的 Agent 自主性仍须验收：证明其独立认知/宏观决定实际影响后续受控行为与战后认知；仅运行固定 Policy 不算完成。旧版“敌方 Sub-agent 必须生成每次战术 Intent”的要求由此取代，具体产品验收见 MVP_SCOPE.md A03 / G10。

### 0.2 SM＋RE 主线与游戏核心演进 [DECIDED]

当前以 **trpg-state-machine＋trpg-rules-engine 为开发和运行基础**，补强支持开放行动、持续世界后果与 NPC 私有认知/自主性的程序化游戏核心。LLM 负责语义、情境裁决、人物认知与宏观计划，代码执行可验证机制并让后果影响后续世界；不是先做完整传统 RPG 再加聊天 NPC。早期真实 Agentic 验证与机制建设交错，不以完整 Host 为前置条件（§14）。

保留并回归验证授权、版本、幂等、RNG、回执、规则集成、故障一致性、NPC 私有状态与可靠处理语义；不冻结当前类、表、模块、命令集或逐 Event 管线。可以基于实际依赖与验证结果大幅重构或替换不合适的子系统，包括不兼容旧内部接口；不能仅为保持旧代码形状否决演进，也不能无证据认定现有能力全部缺失。

基础设施、游戏机制、Agentic 能力是三个逻辑关注层，不要求三个服务/仓库。Evennia、CDDA、Ranvier 是机制与可能的组件复用研究来源；逐项区分设计借鉴、框架依赖与代码迁入，不预设全部自建或为少量特性同时接入两套整框架。可复用成熟组件，但不能把属性/回调可扩展等同任意玩法已有支持。

**撤回未合并 v0.12 的“Evennia 优先采用已决定”及 EB-1～EB-3 强制主线顺序。** 整体 Evennia 迁移为 [OPEN] 备选，须有具体原生复用与独立集成证据后再决策；研究不阻塞当前主线。**agentic-trpg/Evennia_base** 改为 **Deferred / Optional evaluation**，不是已创建仓库或必须交付的新项目。

不同表可保存不同事实，授权视图、只读 Snapshot、缓存只是派生数据；禁止维护两份相同权威世界并双向同步。替换原型与当前实现用独立测试 Session，不共同控制同一生产 Session。当前 SQLite / Event-level OB / Outbox 是实现与可复用资产，不是永久实现粒度；原子性、信息隔离、防丢防重和已提交事实保护继续有效，不授权删除既有观察/历史。

RE 保留 D&D 机械求值职责、无权威跨请求状态目标、显式 RNG 和 **accepted ≠ committed**。普通世界操作不必全经 RE；D&D 持续效果、Reaction、连锁规则不能在 SM / Policy / 脚本另造一套公式或结算。不因框架研究重写规则、升级依赖、冻结新 ABI 或扩大已有完成状态。

机制来源与复用限制、主线能力轨道和可选 EB 验证见 [Game Core Evolution Plan](./GAME_CORE_EVOLUTION_PLAN.md) §4 / §8 / §9。技术主线 [DECIDED]，候选能力组合 [PROPOSED]，具体映射/Schema/替换方案 [OPEN]；未实现目标仍 [NOT IMPLEMENTED]。本轮只改文档，无代码或运行验收结果。

### 0.3 按领域管理状态、按事实确定权威、按操作组织事务 `[DECIDED]`

本次决定替代 v0.13 及更早正文中“SM 独占全部 Runtime State”“全部状态仅由 StateMachine 类/单一模块保存和批准”“所有内部变化必须先回到中心 SM”的绝对限制，包括 §0、§4–§6、§9–§10 的旧分工，以及配套文档的对应表述。保留其单一事实权威、授权、原子性、防旧防重和提议/提交分离的目的。历史修订摘要保留原时序，受影响的旧所有权决定以本节为现行规范；不另建重复 ADR 体系。

| 逻辑领域 | 逻辑数据负责人 / 当前权威事实 | 规则计算者 | 提交执行者 | 派生读取者 |
|---|---|---|---|---|
| Session | 身份、固定 Package/Ruleset 绑定、运行元数据、控制关联；引用 World 的唯一世界时钟 | RE 计算适用的机械时间变化；绑定验证不产生另一份配置 | Session 受控接口参与共享 SQLite 事务 | Host、查询和其他 Handler 读取授权绑定/时钟 |
| WorldFacts | 世界时钟、场景、空间/地形/障碍、对象、物体耐久、门锁、容器及物品实际位置/携带/容纳/附着关系；Quest 保留任务领域责任 | RE 判断涉及规则的合法性与计算；普通关系变化由领域验证 | WorldHandler / Service 经 WorldFacts 参与共享事务 | Navigation、CombatHandler、RE 输入组装及 Perception 查询客观事实 |
| CharacterFacts / 角色机械组件 | 唯一实际角色位置、HP、资源、装备和角色机械状态；库存中的物品归属按 World 实例关系投影 | RE 计算机械变化；Character 校验结构与领域不变量 | CharacterFacts / 机械组件受控接口共同提交 | 探索与战斗引用同一 actor_id；机械 Snapshot / 库存视图不成为第二份位置/归属权威 |
| CombatRecords | 遭遇、参战关系、先攻/回合运行记录、待选窗口、已提交行动关联及推进进度；不持有独立当前人物/对象事实 | RE 计算回合索引、行动预算、资源恢复等机械变化 | CombatHandler 编排，由 Records 及相关 Facts 接口共同写入 | Policy、UI、Episode 聚合器读取授权流程投影 |
| Activity | 进行中的活动、目标、步骤、游标、阻塞/取消/完成状态；不另存实际角色位置 | RE 计算适用规则；Navigation / Activity 组织计划与进度 | ActivityHandler / ActivityRecords 与相关 Facts 共同提交 | 调度、Policy 与授权活动查询 |
| Effects | 持续效果、来源/目标、生命周期及效果自身进度/时钟；空间锚定引用 World | RE 计算建立/消耗/到期/连锁规则 | Effects 受控组件与 World、Character、CombatRecords 等共同提交 | RE 输入组装、Perception、Policy 查询适用效果；Activity 不复制效果进度 |
| NPC Cognition | Memory / Belief / Relationship / Goal / Plan 的追加版本历史、当前版本与 Goal/Plan 状态；Evaluation Task、模式及认知完成关联 | NPC LLM 提议主观更新；领域确定性验证 | Cognition 接口在 EVA 完成事务提交整批 Meta、唯一 Result 与可靠交接 | Host Context Builder / 对应 NPC 仅读授权 Meta |
| Perception / Observation | 非战斗阶段证据、战斗固定过滤依据、授权观察与窗口保留；Cognition 管 Gate／认知处理状态 | 可信确定性路径、受限 JEV 判断；正式机械检定由 RE | 证据随来源操作共同提交；后续投影/处理按既有可靠事务推进 | NPC Cognition、Host、授权查询；不能读出他人秘密 |
| 共享提交设施 | 事务、版本/原值、请求关联、幂等回执、权威 RNG 流/版本及可靠通知记录 | 不复制 RE 的法术/能力判定 | 提供统一事务上下文，检查共同提交条件，协调全部参与写入与 COMMIT/ROLLBACK | 各领域、恢复/审计及可靠投递读取相应结果 |

这些是逻辑职责；**Facts / Records 是统一事实访问与受控修改边界：活跃事实由 Session 管理 RAM 运行表示，SQLite 保存同一事实的持久提交表示**。业务调用方不自行选择读 RAM 还是 SQL；二者不独立接受业务写入。现有同名组件的受限实现见 §1.3；新增组件/字段与完整职责迁移仍 `[PROPOSED / OPEN]`，不能按名称判定完成。共享身份沿用 `session_id`、`scene_id`、`actor_id`、`object_id` / `instance_id`，不新建平行目录。CombatHandler 不另存可独立修改的当前 HP、位置或物品归属；参战关系、Snapshot、冻结的终结记录和缓存不是另一份当前权威。

**库存边界：** 当前便携物品以 `objects.object_id` 复用 `instance_id`，`carrier_id` 或 `scene_id + cell` 表达实际位置。`WorldFacts.transfer_item` 改位置，`CharacterFacts.project_item_transfer` 同事务维护机械 `InventoryState.entries` 与 `characters.inventory_json` 的 carried-slug 投影；`validate_portable_inventory` 校验完整便携子集后才按角色筛选。持久化投影仍不得独立改写物品归属；既有非便携机械条目、数量/充能与装备绑定不能因投影而丢失。容器最多两层及相关容量／祖先访问已在 main 实现（§1.3）；统一装备实例绑定、部分数量转移和消耗生命周期联动仍 OPEN，不能把全部库存说成已完全统一。

默认沿现有**进程内、共享持久化**路线演进。经审阅测试的内部 Handler 可通过受控领域接口、进程内类型调用和共享事务上下文共同完成操作，不必把每个字段变化包装成外部 TypedCommand、JSON 或 RPC。共享数据库不赋予任意模块写所有表的权限：写入经数据负责人接口，遵守共同边界。跨领域操作不拆成各领域先提交再补偿；不新增微服务、多数据库、分布式锁、两阶段提交或完整事件溯源平台。

内部信任仅适用于已审阅测试、职责与目标范围受控的实现；Host/LLM 输出、Coding Agent 生成物和未验证脚本不能继承该权限。固定执行协议优先：DM/NPC 提结构化意图或机制组合，只有新底层能力才考虑 §3.6 受控代码扩展。未知字段不产生语义，不能任意写数据库/属性。手动交互与可信自动世界效果使用不同来源校验，但均遵守目标范围、领域不变量与共同提交条件。

#### Session 当前事实的运行表示与修改协调（2026-10-21）

SM 及其所属领域仍是唯一可信状态管理边界。WorldFacts、CharacterFacts、CombatRecords、Effects、Activity、NPC Cognition 等各负其责；Session 统一管理活跃事实的加载、释放、版本一致读取与修改协调，内存可按领域组织，不要求包含全部字段的巨型 SessionState。

RAM 保存**已提交当前事实的运行表示**；SQLite 保存**持久提交事实**，作为崩溃恢复和提交结果对账依据。这是同一套事实的两种表示，不是可分别修改的 HP、位置、物品归属或世界版本。普通服务不得绕过领域接口修改共享对象，也不得绕过统一提交边界直接改库。候选修改与已发布状态隔离，持久 COMMIT 后受控发布，协议见 §6。

每个 Session／世界有唯一权威修改协调者。玩家、NPC、系统时间、机关、Activity、Effects、Meta／Task、感知可靠工作和后台维护的真实写入口都参与对应边界；协调职责不将领域业务集中进提交器。网络请求、只读工作和 NPC／LLM 推理可并行，最终修改有明确顺序；写事务及世界提交临界区不等待玩家、LLM、外部 I/O 或长时间规则求值。返回的异步结果仍重验权限、版本、任务资格及前提，保留 OCC、幂等和防旧结果机制。

当前路线继续为进程内协调与 SQLite，不引入微服务、分布式锁或多服务器共同写同一世界。未来同世界 **5–6 名玩家**是后续并发和合成负载目标，不扩大当前一名玩家／一个 PC 的 MVP。提交顺序仅为工程顺序，不代替先攻或同步争抢的游戏规则。具体协调类、版本粒度、锁策略与 ABI **[OPEN]**；完整统一运行层 **[NOT IMPLEMENTED]**。

### 0.3a World 与 Scene 的目标结构 `[DECIDED]`

World 下并列 WorldObjectService（物体查询与能力分派）、Scene 子系统（SceneService 协调）与 WorldTimeService（统一游戏时间能力）；WorldHandler 保留操作入口与协调，WorldFacts 提供受控事实读写并共用 SQLite 事务。正式名称为 WorldTimeService，TimeService 仅是讨论简称。§1.3 的 10 月 18 日快照当时没有独立 Scene 组件；10 月 19 日当前分支已出现以下受限实现，详见 §1.4，不能把历史缺口当作当前状态，也不能把实现分支称为 main。

| Scene 内组件 | 已确认责任 | 现有基础与独立实现状态 |
|---|---|---|
| SceneService | 初始化、进入／离开、访问记录、Flags、生命周期与内部协调 | 当前分支以 SceneLifecycleService 实现场景生命周期切片；不等于完整目标 SceneService 已交付 |
| GridService | 网格定义、坐标有效性、邻接、距离等基础空间能力 | 当前分支已有 GridReader／GridService／不可变 GridView，复用 RE 几何；已解析输入与拓扑的长期复用仍待落实 |
| TerrainService | 地表、地面高度、困难地形与通行属性，拥有基础地形及受控变化 | 已有 grid／blocked_cells 基础；独立组件和综合合并 [NOT IMPLEMENTED]；读取 ObjectSpatial 动态贡献，不复制第二份可写地形事实 |
| EnvironmentService | 基础环境管理，结合局部空间防护与有效 Effects，按位置／区域查询实际环境 | 当前分支已有服务、显式降水／风防护、按需缓存及事务双版本；生产 WO／Effects 适配接线仍有边界，见 §1.4 |

所有组件共用 Scene Grid 与坐标标识，不各建 Cell。Character 拥有唯一实际角色位置；WorldObject 拥有物体位置与动态空间贡献。查询可直接调用适当组件，不要求一律经过 SceneService；顶层图只展示 SceneService，内部责任由此表细化。实现和具体字段／公共 ABI 仍 [OPEN]，不得由本节新增无需求接口或扩大 MVP。

**环境边界 `[DECIDED]`：** Package 提供环境初值是目标内容约定，当前受控环境导入不等于 Loader 已支持候选字段。运行变化保存到 Session 的 World 状态。支持选择一批 scene_ids 设置天气，不引入世界→地区→场景天气继承；环境可作用于整场景或明确区域。首次进入前的受控修改必须保留，后续初始化只能补齐未初始化基础，不能用模板覆盖已有变化。有效 Cell 环境按需组合基础状态、局部空间防护与有效 Effects，不写回 Cell 形成独立维护的最终态。挡雨、挡风、视觉遮挡、移动阻挡彼此独立，不相互推导；未接通的提供方须明确报告缺口。共同复用规则见 §2.3，双版本与 Grid 的专项约定集中在 [World §2.0b–§2.0c](./WORLD_SUBSYSTEM_DESIGN.md#20b-grid-运行时输入复用-decided)。

Effects 保存法术效果的来源、范围与生命周期，Environment 只消费其环境贡献，不复制效果权威／期限。天气生成、气候继承、流体模拟不是本轮前置要求。角色暴露进度归属 [OPEN]，本轮不自行划给 Environment、Character、Activity 或 Effects。候选 environment／terrain 字段不代表 Loader 已接受，见 Adventure Package §4.4。

### 0.4 Combat Handler：有状态的流程组织者 `[DECIDED]`

应建立/补齐 Combat Handler 职责，允许持久管理遭遇生命周期、当前等待的决定、已提交行动关联与继续推进所需信息。它根据已提交状态等待玩家或调用非 LLM Combat Policy，组织一次行动的 RE 求值和跨领域提交，再推进至下一决策边界、合法暂停或战斗结束，并协调本场 Turn／Round Episode 的关闭与可靠聚合。它不只是不断向中心 SM 申请操作的无状态空壳，也不包揽 Perception、JEV、EVA 或叙事。

回合索引、资源恢复、效果到期等机械变化由 RE 计算，Handler 应用/管理其结果，不能再次递增回合或重复扣资源；一次攻击不默认等于回合结束。自动推进须有有界重试与无进展退出，失败/冲突按既有命令键和回执恢复，禁止无限循环。**当前已有受限 CombatHandler / CombatRecords（§1.3）**；完整推进、通用中途选择和 Episode 协调仍是目标设计。新增 Handler API、调度预算、Continuation Schema `[OPEN; NOT IMPLEMENTED]`，不能据类存在扩大公共支持范围。

#### CombatPolicy 参数生效与认知等待边界（C07）

CombatPolicy 是确定性的即时战术决策组件。它接收 `combat_id`、决策 Actor、版本、授权机械可知视图、已提交认知的受限策略参数及有界选择预算，返回 TypedIntent、受支持的 Reaction 选择或明确无可行动／等待结果。策略参数可以表达对玩家／势力的关系立场、获准目标与战斗意图；具体字段在有消费者时冻结。Policy 不读取完整 NPC 私有 Meta 或玩家秘密，不调用认知 LLM，不生成伤害、骰点等机械结果。

NPC Cognition 负责主观关系和目标，向 CombatPolicy 提供受控、带来源版本的参数投影；投影不成为第二份可独立修改的认知权威。机械状态仍随实际动作更新。当前 Turn 内的反应使用当时已生效的策略参数；该 Turn 引起的认知变化，只有在认知结果提交后才影响后续决策，不追溯修改已执行反应。

CombatHandler 组织 `initialize → await_decision → evaluate/commit → next_boundary → close`，协调 Policy／玩家选择、RE 求值和共同提交，实际状态名称可沿用现有代码。一次行动不自动结束 Turn；没有合法进展时退出而非无限重试。Turn／Round 完成时通过 C15 关闭相应 Episode、建立可靠感知工作；不在每个机械 Event 后启动认知管线。

例如友善 NPC 被玩家攻击：玩家 Turn 完成 → Turn Episode 聚合信号 → 过滤／察觉形成 OB → 按资格启动 EVA → 提交关系／目标更新 → 刷新策略参数 → NPC 后续 Turn 决策。采用认知判断时，不另加“受到攻击即无条件敌对”的并行关系写入路径。如果获准的关键认知任务必须影响该 NPC 紧接着的 Turn，则在其决策边界等待有效提交；等待释放数据库事务，失败或超时走明确恢复流程，不能暗中改成强制敌对或宣称任务已完成。普通 OB 不要求每个 NPC 每个 Turn 都运行 EVA。

即时 Reaction 由 CombatPolicy 根据已有参数与当前机械视图选择，CombatHandler／RE 验证并执行，不等待当前 Turn 的 OB 或认知 LLM。预先声明的 Reaction profile 与通用中途暂停选择是不同能力。后者未来必须有持久选择窗口：所属 command／combat、获准选择者、阶段／窗口序号、合法选项、输入版本、已提交前缀或未提交候选的明确状态、取消与恢复策略。公开响应使用新的幂等命令引用该窗口；仅系统拥有 continuation 数据。未完成该协议时保持 unsupported，不序列化 Python 栈或在事务中等待人／LLM。

### 0.5 A1：探索与战斗的操作编排分离 `[DECIDED]`

StateMachine 保留统一 API / 可信命令入口，按操作上下文分派。探索移动由 **Navigation / Activity + WorldHandler** 组织逐步执行、前提重验和活动进度；战斗移动由 **CombatHandler + Rule Engine** 组织规则判断、行动资源、时序、触发和反应。两条路径只写 CharacterFacts 的唯一实际角色位置，不保存可独立修改的探索位置/战斗位置。活动目标、计划路径和战斗投影都不是当前实际位置。

战斗空间是世界空间的机械投影：沿用同一场景/角色/对象身份，把实际位置映射为 RE 能表示的 cell / zone，连同地形、障碍和通路组装规则输入。当前 `_current_cells` 从角色事实读取同场景 cell；`actor_zone` 在活跃战斗中为派生输入，结束时可冻结审计。未来子区域、坐标原点/尺度或多场景映射 `[OPEN]`，须明示正向与落位转换及适用版本；无法无歧义映射的空间/障碍应报不支持。不能用开战复制、战后双向同步两份位置解决边界。

**互动复用 `[DECIDED]`：** 探索和战斗中的开门、解锁、取放、破坏障碍共享对象事实与底层能力操作；战斗入口额外经 RE 验证/计算行动资格、成本、时序、触发与反应，再由 Handler 协调共同提交。World 保留可达/授权/能力/关系不变量，RE 负责涉及规则的判断与计算，Handler 不写另一套规则公式。当前非战斗入口的活跃战斗禁用、装备/效果/凭据等限制继续有效；**不能直接调用内部方法绕过这些限制**。战斗复用需要显式受控执行上下文、受支持的规则 Delta 和回归证据，协议未定，不因本文开放现有命令。当前开合、凭据门锁、取放等是受限基础；容器取放、破坏与战斗互动是待落实目标。

### 0.6 A2：StateMachine 模块化与职责边界 `[DECIDED]`

StateMachine 是统一 API 与组件装配入口，各子系统通过构造参数等显式依赖协作，共享一个 SqliteStore / 事务上下文。按需要由 **Handler / Service**（操作流程）、**Facts / Records**（所属事实/运行记录读写）、**Supporting Components**（导航、规则适配、时间、事件取证等支持能力）组成；不要求每个子系统具备全部层次，也不要求每种对象专设 Handler，不引入强制 ECS 重构。World 的可选能力组合是项目领域设计，不是 ECS 迁移承诺。

现有显式装配是起点；逐步减少仍通过 Mixin 和共享 `_conn` 隐式协作的路径。每个切片明确读写负责人、依赖、事务参与方式和对外兼容边界；不得将中心 SM 的全部业务搬到一个同样庞大的 WorldHandler。Effects 可先复用现有角色机械组件与 PackageEffects 支持，不宣称独立 Effects 服务已经存在。

**共同提交 `[DECIDED]`：** 一次不可分割操作的所属状态变化、资源结算、RNG、正式事件、实际阶段证据、活动/战斗进度、触发采用记录及回执/可靠工作在一个 SQLite 提交边界同成同败；组件不各自 COMMIT。需要等待外部结果时退出写事务并重验版本。合法尝试的结果失败可能仍支付行动/时间/资源，按 RE 结果提交实际成本和失败事件；非法命令、版本冲突和提交故障不能冒充一次已发生尝试，也不能消耗未获准资源。后续独立命令或既有异步 Observation / EVA 事务沿既有可靠交接推进，不声称跨两个提交原子。阶段证据不由操作结束态重建，Event / Episode / Observation 分工沿用 §7。

### 0.7 v0.4 归并范围、状态与契约索引（2026-10-17）

[评审 v0.4](./reviews/agentic-trpg-architecture-contracts-2026-10-17-v0.4.md) 原文保留为审查记录；本文继续是跨模块契约最终权威。建议字段和实施顺序不自动升级为冻结 ABI。§1.1／§1.2 保留各自日期化代码核对；评审 §1／§13 是另一组 2026-10-15 快照，不是 2026-10-17 当前部署或重新运行的测试。新增能力仍需独立实现验证。

评审 §5 沿用前次 World 复核的四项问题：检定后世界变化遗漏空间一致性检查、无关未知容器阻断取放、async World 支持声明与代码不符、三个恢复测试写死 Windows 路径分隔符。评审仅再次静态确认普通命令／`_submit_dnd` 收尾不同及 async 限三类 RE payload，其余复现沿用前次；本轮没有重现或修复，须后续针对性验收。

| 事实 / 支持职责 | 唯一责任与协作 |
|---|---|
| 物品数量／充能、实际位置／容纳 | World 实例；Character 装备／持握／调谐引用实例，共同转移／消耗／安全解绑，不丢旧非便携机械条目 |
| 当前动作／反应／移动预算 | Character 机械组件；Combat 管回合／先攻和移动 ledger，同一 RE 结果共同更新，不另存位置或可写预算 |
| Effect／Condition／专注 | Effects 管完整身份、来源、应用和生命周期；Character 的有效 Conditions／专注引用为受控投影，固有免疫／感官留在角色／固定定义 |
| Observation / Cognition | Perception 管察觉、授权 OB 和窗口保留；Cognition 管 Gate 采用、pending／processed 转换与 EVA 覆盖；Host 读取无处理副作用 |
| Event / Episode | Event 记录／聚合已提交来源，Combat 提供本场参战关系和 Turn／Round 边界，Perception 定义过滤策略 |
| Quest / StoryProgress | 客观进度／奖励采用按真实消费者增加窄边界；NPC Goal 不等于客观 Quest，不预建任务平台 |
| 共享支持 | CommandCoordinator、RulesAdapter／SnapshotBuilder／ResultApplier、SpatialQuery／Navigation、WorldClock／Scheduler、EventCapture／EpisodeRecorder、TriggerDispatcher、AuthorizedQueries、SqliteStore／UnitOfWork／Outbox 按消费者拆分，不要求同名类、独立表或服务 |

RE DTO 字段属于 CombatState 不决定 SM 事实归属。World／Character 不把 Snapshot JSON 当独立可写事实；Adapter 明确场景单位、格距、坐标原点、足迹与 cell／zone 映射，缺必需依赖不填零库存、空效果或默认位置。Facts 依赖存储／窄查询，跨域编排放 Handler／投影服务，避免隐式写入环。

以下 C01～C21 是评审契约 ID，与 §13 历史开放问题 C-01～C-27 区分：

| 契约 | 本文正式归属 | 配套细化 |
|---|---|---|
| C01 输入适配／角色 | §3.2、§3.5 | Agent §3.1 |
| C02 命令／回执 | §2.2、§3.1、§6.2 | SM §5 |
| C03 授权／能力查询 | §3.5、§4.4 | SM §10 |
| C04 内容／初始化 | §10 | Adventure Package §9.1／§9.1a |
| C05 RE 输入 | §4、§0.7 | SM §5.4 |
| C06 RE 结果／应用 | §5、§6.6 | SM §5.4 |
| C07 Policy／选择 | §0.4、§8 | Agent §4.4、SM §7 |
| C08 准备／提交 | §6.1、§6.6 | SM §5.3 |
| C09 World／空间 | §6.6 | World §2–§5 |
| C10 Character／物品／位置 | §0.3、§0.7、§6.6 | World §2.1、SM §3.4a |
| C11 Activity | §6.6 | SM §3.4a |
| C12 Effects | §6.6 | World §2 |
| C13 时间／调度 | §6.6 | World §5 |
| C14 条件后果／触发 | §3.4、§6.6、§10 | Adventure Package §7 |
| C15 Event／Episode | §7.5 | SM §3.6a、Agent §5.2 |
| C16 Perception／JEV | §7.2–§7.3、§7.5 | SM §6.2 |
| C17 EVA／Meta／交接 | §9.2–§9.7 | Agent §8、SM §3.9 |
| C18 Gate／OB | §7.4、§9.8–§9.9 | Agent §6.6a、SM §3.7a |
| C19 Host | §9.1、§9.7 | Agent §2.1 |
| C20 存储／恢复／投递 | §6.4、§6.6、§9.7 | SM §8 |
| C21 展示／扩展 | §3.5–§3.6、§10 | MVP §5、Adventure Package §9 |

## 1. 实际代码基线与迁移缺口

| 位置（v0.1 历史 main 基线） | 历史事实（非当前实现声明） | 对契约的影响 |
|---|---|---|
| `dnd5e_engine/orchestrator.py` | `_LiveCombat` 持有 Initiative、Combatants、RNG、Round、Effects、Areas、Object State 及很多 sidecar | 需要完整状态依赖盘点，不能只迁移 HP/Turn |
| `orchestrator.py` | 公开 `start_combat`、`submit_player_intent`、`advance_monster_turn`、`end_combat` | 该历史基线未提供目标 `evaluate(...)` 契约 |
| `orchestrator.py` | `PlayerIntent` 是严格类型化的动作输入；该基线 `submit_player_intent` 主要是玩家入口 | 可复用适合目标契约的 Intent 语义 / Resolver，而非重写规则公式 |
| `orchestrator.py` | `_execution_transaction` 深拷贝 `_LiveCombat`、缓存事件并回滚 `random.Random` 状态 | 规则算法与回滚用例可作迁移资产；旧执行器不作为最终依赖，**不可**将其误认为 SQLite 跨模块原子提交 |
| `orchestrator.py` | 怪物回合由 `advance_monster_turn` 内部选策略后执行 | 该历史入口不足以证明敌方 Agent 宏观自主性；即时 Typed Intent 可由受控 Combat Policy 产生（§0.1） |
| `orchestrator.py` | Reaction 以预设触发为主，而非在解析中暂停等待人工选择 | 可暂停的 `needs_choice` 需作为新协议，不可冒称已有 |
| `nat20_bridge/state.py` / `combat_execution.py` | CombatHandle、事件及重试 Receipt 存于 Bridge 进程内；请求指纹与 `request_id` 已有基础机制 | 可复用概念，不可用 Bridge 进程内缓存作为新 State Machine 的权威持久回执 |
| `outcome.py` / `results.py` | `CombatOutcome` 是战斗关闭时的结果投影，并非每一步的完整 Delta | 新契约不得用 `CombatOutcome` 替代逐命令 StateDelta |

以上表格沿用 v0.1 的历史代码审阅基线；前批有限静态代码核对另列 §1.1，不是完整规则审计或运行测试。迁移应按受支持规则建立状态依赖闭包与读写映射；旧 `_LiveCombat` / sidecar 盘点用于发现遗漏、区分权威/派生/临时数据，不能成为目标 Schema 蓝本、永久执行依赖或要求所有规则重构先复制完整旧对象的门槛。

### 1.1 2026-10-12 跨仓库核对（静态代码 / Review，未重跑运行测试）

以下为前一批静态核对的日期化记录，保留原 SHA / 分支 / 能力范围。**当前 SM 核对见 §1.3**；本批未刷新 RE main 或重跑运行测试，不能将本节旧锁定版本用于当前 SM，也不把历史 main 与开发分支状态混同。

| 基线 | 已核对事实与限制 |
|---|---|
| SM 开发集成分支 `feat/sm-b19-b22-gameplay-domain-bridge@058e79f` | Batch B 的 `event-evidence/4` 对已支持世界 Producer 阶段取证；Batch C（`9e7c130`）实现每 NPC 感知引用队列/独立放行；PERF-01/02（`6eb5855`）实现按需水位和 Pending 分页。核对 `events.py`、`perception_queue.py`、迁移及相应 Review；本轮不重设计这些实现 |
| SM 远端 `main@b3f350f`（该次核对基线） | 当时尚未包含上述开发分支提交；“已完成 Batch C / PERF”指开发集成基线，不等于已合入 SM main 或已部署 |
| RE 阶段 Evidence | SM 的 `dnd_runtime.py` 对非空感知 Signals 仍记录 `engine.intermediate_phase_unavailable`；RE 返回最终 Delta / 有序 ProposedEvents，未提供已审计的逐阶段感知证据协议。不从结束态补历史，不把 `intent_submitted` 自动当真实外显动作 |
| 机械审计 / Episode / Continuation | SM 仍包装 ProposedEvents 为 `combat.engine_event`；目标审计/可观察事实分流、WorldEpisode / EpisodeObservation 聚合与通用可持久恢复 Continuation 均 [NOT IMPLEMENTED]。受限预声明 Reaction 不代表通用中途选择已完成 |

SM 的 `pyproject.toml` / `uv.lock` 将 Engine 与 SRD 同时锁定为 **`602dcb8d448e670049427bbb751d6ed226005298`**。RE 远端 `main@38fcfcd4c3a744b30f792775415e798b323d4331` 比该锁定提交多 32 个提交，且本地候选协议不兼容：

| 代码版本 | SM 锁定 RE | RE main |
|---|---|---|
| Request / Result | 接受 `engine-evaluation/1`～`/4` | `engine-evaluation/22` |
| Snapshot | `engine-snapshot/1` / `/2` | `engine-snapshot/16` |
| Evaluator | `dnd5e-evaluation/8` | `dnd5e-evaluation/35` |

依据版本常量及模型，而非锁定提交中较旧的说明文字。RE main 已有更多受限 Stateless 路径及预声明 Reaction，但仍有 Legacy 依赖、完整 `CombatState.event_log` 字段与开放的 C-04 / C-15 / C-16；不等于已满足本次全部目标。升级前须独立审核 Snapshot / Delta / RNG / RulesetBinding 与 SM Consumer，不因本轮文档更新自动升级依赖或冻结共同 ABI。审阅来源：[SM Batch C](https://github.com/agentic-trpg/trpg-state-machine/blob/058e79f300016f7397f0c3401bc03b58554e2b71/docs/reviews/SM_PER3_REVIEW.md)、[SM PERF-01/02](https://github.com/agentic-trpg/trpg-state-machine/blob/058e79f300016f7397f0c3401bc03b58554e2b71/docs/reviews/SM_PERF01_PERF02_REVIEW.md)、[RE 本地协议](https://github.com/agentic-trpg/trpg-rules-engine/blob/38fcfcd4c3a744b30f792775415e798b323d4331/docs/dev/stateless-evaluation.md)。

### 1.2 2026-10-15 SM 当前实现核对（静态代码，未运行测试）

**历史快照：** 下列 GC5 脏工作区、Schema 25 和 RE pin 6755524 只记录当时状态；当前远端实现见 §1.3。保留原记录，不将未提交文件当作 main 能力。

只读仓库 `D:/Projects/agentic-trpg/trpg-state-machine`，remote 为 `https://github.com/agentic-trpg/trpg-state-machine.git`，分支 `feat/sm-gc5-activity-feedback`，HEAD **`1fa7cea5dab7bb95f3f6fa975f8e681c691937a6`**。工作区有已修改文件及未跟踪 GC5 文件；下表基础能力同时核对已提交 HEAD，GC5 另列，**不代表当前远端 main、已部署状态或本批运行验收**。总控仓库及其父目录、SM 根目录未发现 `AGENTS.md`；总控仓库只有 Markdown，未发现已配置文档检查脚本/CI。

| 范围 | 实际代码证据（已提交 HEAD，路径在 `src/trpg_state_machine/`） | 实现状态及缺口 |
|---|---|---|
| 统一入口与显式组合 | [service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/service.py)：装配 SqliteStore、WorldFacts、CharacterFacts、CombatRecords、WorldHandler、ActivityHandler、RulesAdapter、CombatHandler | **部分实现** A2；NPC / Perception / Command 等仍为 Mixin，`_conn` 仍是过渡依赖；不是零基础，也不是全部模块化完成 |
| Facts / Records 与事务 | [domain_facts.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/domain_facts.py)、[storage.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/storage.py)：要求写作用域、不自行提交；SQLite 短事务与 savepoint，HEAD 迁移至 Schema 25 | **已实现的受限基础**；完整新组件集合/跨域故障验收未在本批验证 |
| 探索移动 / 活动 | [activity_handler.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/activity_handler.py)、`activity_records.py`、`navigation_plan.py`、`navigation_driver.py`、`spatial.py`：活动持久进度、World 执行、CharacterFacts.move 写 `actors.current_scene_id/cell` | **已实现的受限探索路径**；Activity 拒绝活跃战斗，不是通用所有活动/导航完成 |
| 战斗 / 空间 | [combat_handler.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/combat_handler.py)、[rules_adapter.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/rules_adapter.py)：受限遭遇/检定/攻击/结束编排，`_current_cells` 读取实际位置，终结时 freeze_positions | **部分实现** A1；当前适配为受限规则切片，不能据投影宣称战斗移动/动态障碍/全部互动已经接通；通用推进/Continuation 仍目标 |
| 门 / 通路 / 物品 | [spatial.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/spatial.py)、`lock_package.py`、`item_package.py`、`domain_facts.py`：共享门、两侧通路、公开持有凭据门锁、单实例取放及库存投影 | **已实现的受限非战斗基础**；撬锁/密码/容器/耐久破坏未核实为公共支持；装备 slug 歧义、效果及施法材料绑定等明确拒绝 |
| 入口保护 | [session_access.py](https://github.com/agentic-trpg/trpg-state-machine/blob/1fa7cea5dab7bb95f3f6fa975f8e681c691937a6/src/trpg_state_machine/session_access.py) `_world_operation_capability`；`spatial.py` `_spatial_combat_guard` | 活跃战斗拒绝普通移动、开合、取放、门锁等；移动阻挡物与关闭的通路门可能阻止战斗初始化；共享互动尚需战斗集成，不能解除 guard 代替实现 |
| 世界时间 / Effects / 事件 | `game_time.py`、`package_effects.py`、`event_capture.py`、`event_persistence.py`、`CharacterFacts.rule_components` | 已有 game_tick / 日程、受限包后果及机械效果组件、实际阶段取证/持久化基础；不是完整环境、陷阱或持续魔法区域系统；保留 Event / Episode / Observation 既有职责 |
| GC5 工作区增量 | 修改中的 `service.py` / `storage.py` 等及未跟踪 `activity_feedback.py`、`npc_activity_feedback.py`、`_migration_26.sql` | **未提交、未验证**；只记录存在，不纳入 HEAD 能力完成声明，不以工作区 Schema 26 代替已提交 Schema 25 |

本次读到 `pyproject.toml` / `uv.lock` 的 Engine / SRD 固定为 **`675552406e67470bf3456fe90e88c4f1595bf324`**；适配器候选消息为 `engine-evaluation/23`、Snapshot `/17`。这是 SM Consumer 的静态事实，不是最新 RE 全量审计，也不宣布冻结跨模块协议。`tests/test_domain_runtime.py`、`test_gc1_doors_and_effects.py`、`test_navigation_activities.py`、`test_item_transfers.py`、`test_lockable_passages.py` 等仅作为已有用例的证据，本批未执行它们。World 更广组件清单均为目标/候选，详见 [专项草案](./WORLD_SUBSYSTEM_DESIGN.md)。

### 1.3 2026-10-18 远端实现核对（定向静态调查）

本轮先检查适用祖先目录与仓库，未发现适用 AGENTS.md；顶层仅有 Markdown，未发现文档检查脚本或 CI。开始时通过 fetch 与 ls-remote 核对远端，三条 SHA 均与调查输入一致。复核期间 SM 远端发生外部合并，当前状态以下表后两行为准；本轮未执行该合并。只修改顶层文档，不修改 SM／RE 业务代码、不合并实现分支，也不合并顶层 main。

| 仓库／引用 | 本轮实际核对 SHA | 状态与取证方式 |
|---|---|---|
| 顶层 `origin/main` | `73d3bd0bf6c064e432d472b9babeec2142b34831` | 文档分支 `docs/world-refactor-scene-alignment` 从此开始；用户原有未跟踪 `docs/FIRST_BLUSH_MVP_REQUIREMENTS.md` 保留 |
| SM `origin/main`（开始） | `a897ae5fca959530a2963cabd350bb408416b4a6` | 开始时 main／Schema32 基线；现已成为历史起点 |
| SM `origin/feat/object-spatial-service` | `0c2c4c78f251aee9ef9fad1448471f425be4cbe2` | 开始时未合并，基于上述 main 多一个提交；复核时已被当前 main 包含，分支引用仍保留 |
| SM `origin/main`（复核／当前） | `97c5af102bd8ca2c397b84bd4d36664983db54a7` | `merge: integrate object spatial service`；父提交为上述两个 SHA，Schema33／Loader /8；与 ObjectSpatial 提交源码树 diff 为空（exit 0），祖先检查 exit 0 |

**取证沿革：** SM checkout 开始为 ObjectSpatial 分支／0c2c4c7，复核为 main／97c5af1，两次工作区均干净。顶层 checkout 期间被外部切至 main，本轮保留全部文档改动并切回原文档分支后交付；顶层 main 仍为 73d3bd0。当前源码链接固定到 97c5af1；开始时 a897ae5 与 ObjectSpatial 增量的比较保留为调查沿革，不继续称它未合并。

**证据边界：** 这是针对指定文件、调用路径、测试源码和 PROGRESS 的定向核对，不是完整代码审阅。以下“已实现”指对应提交中有实现及相关测试源码；本轮没有运行 SM／RE pytest、真实模型、示例或跨仓库集成测试。历史测试结果只引用原记录，不作为本轮重新执行的结果。

| 范围 | 当前 main 已实现与源码依据 | 合并沿革／目标差异 |
|---|---|---|
| 装配、事实、事务与入口 | [service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/service.py)、[domain_facts.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/domain_facts.py)、[session_access.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/session_access.py)：显式装配 WorldFacts／CharacterFacts／CombatRecords、WorldHandler／对象服务／活动／规则适配；共享 SQLite 短事务、授权、OCC、幂等、RNG、Receipt／Outbox | A2 部分实现；Mixin、过渡依赖和全部领域共同 finalize 仍需逐入口验证。类已存在不等于完整契约完成 |
| WorldHandler 当前边界 | [spatial.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/spatial.py)：开合／锁／闩及对象能力分派已委托；时间推进委托 WorldTimeService | 仍保留场景初始化／进入／离开／Flags／访问、角色移动与取放部分路径、通路／共享门端点、拓扑及授权辅助、空间一致性与流程编排；没有独立 Scene 四组件 |
| 物体能力与开合 | [world_objects.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_objects.py)、[world_openable.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_openable.py)：WorldObjectService 查询／分派；Openable 共享开合、锁、闩、卡住方向、操作侧／触及，PickLock／ForceOpen／ClearJam 非战斗检定；[rule_execution.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/rule_execution.py) 在事务外调用真实 RE `evaluate_openable`，提交前重验，成功只采用显式后果 | 活跃战斗费用／Utilize／Fast Hands、Arcane Lock／Knock 与魔法生命周期、真实物体攻击未实现；内部耐久结果应用不是攻击入口 |
| 容器与库存投影 | [world_containers.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_containers.py)：PutItem／TakeItem；移动子树、原祖先及目标祖先相关容量／fit 检查，最多两个容器层级；Openable `allows_contents`／`contents_accessible` 复用于祖先访问；World 位置与 Character 库存投影同事务 | 不是全 Session 容器准入审计；相关容量 unknown 仍拒绝，包括移出。部分数量转移、实例装备／调谐／被动效果解绑生命周期未实现；摧毁 shell 保留内容关系并允许访问，不代表内容物摧毁规则或散落已完成 |
| 空间、光源与机关 | 当前 main 的 [world_spatial.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_spatial.py) 已有固定占地／GM 布置和移动阻挡；[world_lights.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_lights.py) 有开关／模式和受限照明投影，不确定遮挡显式 unknown；[world_mechanisms.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_mechanisms.py) 有受控一次性开合／光源联动 | ObjectSpatial 原分支增量现已合入 main：朝向／旋转、完整占地候选验证、接触查询及 `scene_contributions`，投影独立提供移动阻挡、困难地形、视觉遮挡和 Cover。尚未接通综合 Terrain／Perception／Light／Combat／RE；无挡雨／挡风接口 |
| 时间与兼容 | [world_time.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_time.py)、[time_binding.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/time_binding.py)、[game_time.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/game_time.py)：world-time/1 固定 1 tick = 1 游戏秒，legacy game-clock/1 保留抽象 tick；换算、elapsed／remaining／reached、昼夜与有界 `(start_tick, end_tick]` 边界查询、命令推进委托 | 实时倍率／TimeDriver、Combat Round 时间接线、Activity／Effects 时间消费、燃料／天气后果、秒制 NPC／OB／Gate 尚未完成；阶段换算不等于照明事实已改变 |
| Package 与持久化 | [package.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/package.py)、[world_package.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_package.py)、[world_commands.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/world_commands.py)：开始时 main Loader 为 `state-machine-foundation/1`～`/7`，当前已兼容 `/1`～`/8`，可选顶层完整 time_binding，创建 Session 强类型整体覆盖并固定保存；[Schema32](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/_migration_32.sql) 增加不可变绑定，唯一 tick 仍在 world_states.game_tick | ObjectSpatial 合并带入 Loader `/8` 和 [Schema33](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/_migration_33.sql) 只增加 objects.orientation（旧行默认 north），当前存储为 Schema33，不保存第二份占地投影；environment／terrain 候选字段尚非 Loader 能力 |

**秒制消费限制：** 创建秒制 Session 时拒绝带配置型 NPC State 的 Package；允许未配置 NPC Runtime 的物理 Actor。NPC observation access 和宿主聚合感知投影返回 `unsupported_time_consumer`；秒制无 Runtime 时日程同步为空，发现遗留 Runtime 则拒绝。不把 legacy 日程、OB TTL、Gate 周期按秒解释，也没有旧存档转秒 API。Package 默认与创建请求覆盖是整体选择，非字段级合并；保存后不随 Package 默认变化重解释历史 tick。

**固定依赖：** [pyproject.toml](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/pyproject.toml) 与 [uv.lock](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/uv.lock) 中 Engine／SRD 均为 `d596161060555630019163ab301e1d25fd816549`；分支未改 pin。[rules_adapter.py](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/src/trpg_state_machine/rules_adapter.py) 的请求仍为 `engine-evaluation/23`、Snapshot 为 `engine-snapshot/17`，Openable 局部请求为 `engine-openable/1`。这是当前 SM Consumer 事实，未核对 RE 最新 main，不冻结共同 ABI 或宣布整个 Stateless 迁移完成。

| 测试源码／历史记录 | 本轮读取到的覆盖与引用边界 |
|---|---|
| [Openable checks](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_openable_checks.py)、[一致性](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_openable_consistency.py)、[边界](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_openable_boundaries.py)、[审阅回归](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_openable_review.py)；[Openable PROGRESS](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/docs/OPENABLE_SERVICE_PROGRESS.md) | 真实命令成功／有效失败、单锁后果、非法请求无 RNG、副作用回滚、无写查询、重放／重启、战斗／魔法拒绝。原记录引用最终分区 1,328 passed；不是本轮测试或玩法完整交付 |
| [Container admission](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_container_admission.py)、[Container tests](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_containers.py)；[Container PROGRESS](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/docs/CONTAINER_SERVICE_PROGRESS.md) | 无关容器、两层与第三层拒绝、相关容量、祖先访问、装备／材料／效果限制及事务故障。原记录为专项 50、组合 469（包含专项，非全量），本轮未重跑 |
| [WorldTime tests](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_time_service.py)；[WorldTime PROGRESS](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/docs/WORLD_TIME_SERVICE_PROGRESS.md) | Package／创建覆盖、精确边界分页、legacy、秒制消费者拒绝、不可变绑定、Schema31 升级保存旧行与回执、重启及迁移故障；原记录为专项 42、全量 1,420，本轮未重跑 |
| [ObjectSpatial tests](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_object_spatial_service.py)；[ObjectSpatial PROGRESS](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/docs/OBJECT_SPATIAL_SERVICE_PROGRESS.md) | 旋转／跨墙候选与 audit、完整占地接触、贡献独立性、Combat guard、Schema32 非空存档升级保留旧列与回执；原记录为新增 34、四分区 1,454，本轮未重跑；该记录随原分支进入当前 main，不另行声称合并后重测 |
| [Spatial](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_spatial.py)、[Light](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_lights.py)、[Mechanism](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_mechanisms.py)、[Migration](https://github.com/agentic-trpg/trpg-state-machine/blob/97c5af102bd8ca2c397b84bd4d36664983db54a7/tests/test_world_migration.py) | 配套用例源码记录导航重验、光照不确定性／取证、联动回滚、旧存档保留；本轮不是全套测试源码审计 |

PROGRESS 中较早的 TimeBinding 缺口按其原日期保留；当前固定绑定的实现以上述源码为准，其外围消费缺口仍然有效。§1.1／§1.2 继续保存各历史分支／脏工作区证据，不作为当前 main 的版本说明。

**本轮文档检查：** 仓库无既有文档检查入口，使用本轮临时一致性检查：8 份文档的 95 个本地链接／锚点、110 张表格、48 个代码围栏（含 5 个 JSON 块）、3 个 Mermaid 块的静态结构、版本引用及 48 个固定 SHA 源码路径均通过；git diff --check 通过。Mermaid 未执行渲染或完整解析器验证。v0.4 审查快照、§1.2 历史正文、既有关键认知／版本／RNG／提交契约保持不变；用户未跟踪资料的 SHA256 与开始时一致。没有运行 SM／RE 业务测试。

### 1.4 2026-10-19 运行时复用专项核对（当前分支，静态证据）

本轮顶层基线为 `98e8d36b03bdc6b9578082bcdae1ed99ccbc5997`，分支为 `docs/runtime-data-reuse-principles`；仅有用户原有未跟踪资料，保持不动。适用祖先与顶层仓库未发现 AGENTS.md，仓库仅有 Markdown，无现成文档检查脚本／CI。下面依据当前 checkout、固定依赖代码、服务文档和 progress 定向核对；未切换或修改相邻仓库，未运行其测试，progress 的通过记录不是本轮执行证据。

| 核对对象 | 固定身份／实际状态 | 已实现及限制 |
|---|---|---|
| SM 当前分支 | `feat/environment-derived-snapshot@37885533f79c890337448b8645a344c6ae7f5208`，工作区干净；远端同名分支一致。远端 main 为 `d0fda62eba8f975232f47abe64be95660a791110`，不把本分支新增能力记为已合入 main | 当前 Schema36；Engine／SRD 发布包均为 0.6.0，仍 pin `d596161060555630019163ab301e1d25fd816549` |
| Grid 与场景切片 | [grid.py](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/grid.py)、[Grid progress](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/docs/GRID_SERVICE_PROGRESS.md)、[SceneLifecycle progress](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/docs/SCENE_LIFECYCLE_SERVICE_PROGRESS.md) | 已有 GridReader／GridService／GridView、SceneLifecycleService 切片；GridView.width／height／cell_size_ft 仍 json.loads，_base 仍创建 GridTopology。按固定配置复用解析值／拓扑是本次设计要求，尚未完成；探索拓扑不能作战斗／动态视觉完整能力 |
| 环境版本与缓存 | [environment.py](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/environment.py)、[environment_versions.py](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/environment_versions.py)、[Schema36](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/_migration_36.sql)、[progress](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/docs/ENVIRONMENT_SERVICE_PROGRESS.md) | scene_environment_versions 已有 source_version／protection_version；同步触发器、提供方绑定／依赖登记、时间依赖及提交后发布已实现。32 项防护、512 项按需完整结果的有界缓存；正式路径命中先查版本／绑定，不扫描全部输入。Wind 子输入含基础／局部来源及已登记 Effects 的值、范围、priority、observable；保守推进双版本。冷结果仍构建原始输入，不能称整个运行时复用方案完成 |
| 外部提供方与兼容 | 同上及 [版本测试源码](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/tests/test_environment_versions.py) | 已有 VersionedEnvironmentEffectsProvider／VersionedProtectionProvider 的 SQLite owner 依赖登记；未版本化、未登记／不匹配或禁用路径不跨查询复用。生产 WO／Effects 法术适配仍待接线，不能把 PackageEffects 或角色 EffectState 当成已接通。早期全输入比较属于旧批历史行为，当前正式命中路径已由版本校验替代；既有高度／区间查询保留，须区分参数 |
| 实例配置归属（追加核对） | 同一 SM `3788553` 的 [domain_facts.py](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/domain_facts.py)、[WorldObjectService](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_objects.py)、[Container](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_containers.py)、[Openable](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_openable.py)、[Spatial](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_spatial.py)、[Light](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_lights.py)、[Mechanism](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/world_mechanisms.py)、[Durability](https://github.com/agentic-trpg/trpg-state-machine/blob/37885533f79c890337448b8645a344c6ae7f5208/src/trpg_state_machine/object_durability.py) | object_definition 仍查 package.world_objects，WorldObjectService.view 和各能力 config／操作仍组合模板配置与实例状态，Durability 读取模板 max_hp；这些是 §2.4 要求下的待迁移行为。已有对象位置／朝向、开合／barred／jammed、Light enabled／mode、Mechanism 状态／次数、HP 等实例记录，不等于有效配置已完整实例化。GridReader 已对已初始化场景缺失 live grid 拒绝回填，但不能据此宣称所有实例读取完成重构。本轮未改代码或新增待办 |
| RE 本地 checkout 与 SM 固定依赖 | 本地 `feat/world-openable-support@74d9e0800c22a740614af72930dd77dd3c064561`；原有未跟踪 `.evaluation-worktree/` 保留。核对本地及 pin 的 [evaluation_ruleset.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/d596161060555630019163ab301e1d25fd816549/packages/dnd5e-engine/src/dnd5e_engine/evaluation_ruleset.py)、[loader.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/d596161060555630019163ab301e1d25fd816549/packages/dnd5e-srd-data/src/dnd5e_srd_data/loader.py) | verify_ruleset 仍调用 ruleset_binding 全量枚举有效素材并计算摘要，明确未缓存摘要；BundledAssetLoader 按 slug 读取／解析 JSON。本地及 SM pin 的 evaluator_version 为 dnd5e-evaluation/36，旧 progress 开头的 /35 不是这两个代码基线的值。可信冻结内容／加载身份复用仍为待落实设计；本地分支不等于 RE main |

RE 远端重试已成功：同名分支为上述 `74d9e08`，main 为 `e5254a2ac7166a830a24c46eb35b2b1e0c4f4b80`；通过本地已有 Git 对象只读核对该 main 的 [evaluation_ruleset.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/e5254a2ac7166a830a24c46eb35b2b1e0c4f4b80/packages/dnd5e-engine/src/dnd5e_engine/evaluation_ruleset.py) 与 [loader.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/e5254a2ac7166a830a24c46eb35b2b1e0c4f4b80/packages/dnd5e-srd-data/src/dnd5e_srd_data/loader.py)：evaluator 已为 `/37`，仍逐次全量计算绑定摘要及按需解析素材 JSON。未切换／更新相邻 checkout，也未升级 SM 固定依赖。

这里确认的是有代码及相关测试源码的受限切片，不是完整一致性审计、跨仓库 ABI 冻结、生产适配完成或本轮性能测量。§1.1–§1.3 保留原日期证据；本文及入口文档与上述冲突的旧实现陈述只适用于当时快照。

### 1.5 2026-10-20 快照与查询专项核对（静态证据）

顶层文档基线为 `5d45a0e3964025c2033e752a0e01465c49cbde15`，沿用已创建的 `docs/snapshot-query-principles`。顶层仓库及适用祖先未发现 AGENTS.md，也没有文档检查脚本／CI；保留原有未跟踪资料。SM 当前 checkout 为 `feat/frozen-ruleset-complete-instances@ec9c7147c1da6456342857760ee40c88abaa3a5f`，存在其他工作中的未提交修改，未切换、暂存或写入该仓库。下列被核对的 Grid／Environment／ObjectSpatial 源文件与其 HEAD 一致；本次没有运行 SM 测试或性能基准，不能把分支能力视为 main 已有能力。§1.1–§1.4 保留各自日期／版本的历史证据。

| 本次核对来源 | 当前行为与证据边界 |
|---|---|
| [grid.py](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/src/trpg_state_machine/grid.py)、[Grid 说明](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/docs/GRID_SERVICE.md)、[Grid progress](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/docs/GRID_SERVICE_PROGRESS.md) | 已有只读解析地图／基础拓扑复用；§1.4 中“GridView 属性仍反复解析、基础拓扑复用未完成”只描述旧版本。`read_scene` 仍取场景角色目录、调用 OSS 重新组合场景物体贡献并构造 occupants；`occupied(self, cells)` 规范化目标格后遍历全部 occupants，不是底层格子索引查询。静态复用不能证明动态查询已局部化 |
| [world_spatial.py](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/src/trpg_state_machine/world_spatial.py) | `scene_contributions` 枚举场景物体及相关共享门并逐项投影；`check_candidate` 仍调用 `_check_scene` 进行场景级校验。局部候选校验改造尚未完成，不能因接受单个 candidate 就视为内部工作量受限 |
| [environment.py](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/src/trpg_state_machine/environment.py)、[Environment 说明](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/docs/ENVIRONMENT_SERVICE.md)、[Environment progress](https://github.com/agentic-trpg/trpg-state-machine/blob/ec9c7147c1da6456342857760ee40c88abaa3a5f/docs/ENVIRONMENT_SERVICE_PROGRESS.md) | 已有依赖版本校验及有界防护／最终结果缓存；未命中时按需准备输入和投影，同一查询内可共享准备结果。公开查询仍校验授权和可见性，未登记提供方不跨查询复用；不能据此宣称每个冷查询都只读取局部实体或全部生产提供方已接通 |

本次在 SM 的 `src/`、`examples/` 中查找 `read_scene`、`GridView` 及 `.occupied(`，未找到 `read_scene` 的生产调用方；测试／文档中的调用不算生产接线。没有证据表明自动寻路或 DM Planner 已使用 GridView。当前确认的是上述实现成本路径及局部检查误用它的风险，**不是已测得的生产性能故障**；GridView 的存在本身不是 bug，也不构成删除接口的依据。后续局部查询／索引及校验改造须按 §2.3 验收，不在本次文档批次标完成。

### 1.6 2026-10-20 三仓库 main 对齐

本节是 **Current Implemented Interface** 的日期化索引，不取代各目标章节。三仓库先 fetch，再分别从各自最新 origin/main 建立 `docs/architecture-runtime-contract-alignment`；原工作区未提交内容保留，编辑仅在并列独立 worktree。起始 main：架构 `1ccf7192059bfe13a1bef4bb0b6e4a3adcf5116e`、SM `d5d8c494e2fa102ca924199b31a6d00c2b4910e2`、RE `66384b00363c00fc92622dbbf77ccfea012b1b5d`。RE `docs/agents-architecture-guidance` 与该 main 同为 `66384b00363c00fc92622dbbf77ccfea012b1b5d`，没有遗漏补丁，也未合并／删除旧分支。架构尚未合入 main 的本地 docs/player-input-fast-path、docs/restore-player-fast-path 未纳入本批。

这是源码、对应测试文件与既有 Progress 的交叉静态核对；`[IMPLEMENTED]` 仅表示表内受限路径有实现和测试覆盖，历史执行记录按原 Progress 解释。本轮没有重跑 SM／RE 业务、性能、并发或故障测试，不能把历史测试数字写成本次通过。§1.1–§1.5 和 v0.4 Review 保留原日期／SHA；与本节冲突的旧现状描述不适用于该 main。

| 能力 | Implementation Status／当前证据 | Gap / Migration Requirement |
|---|---|---|
| 实例配置 | `[PARTIALLY IMPLEMENTED]`；Schema39 `instance_configs`、InstanceData／WorldFacts.instances 已覆盖当前 Session 静态配置、Scene 元数据／地图、对象各能力、NPC senses 与辅助读取；配置与唯一位置／HP／开关等状态分责。源码见 [InstanceData](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/instance_data.py)、[Facts](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/domain_facts.py)；[实例无模板读取回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_instance_containment.py)、[旧库迁移回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_instance_config_migration.py)及 [字段／验收记录](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/docs/INSTANCE_CONFIGURATION_PROGRESS.md) | 创建和未实例化目标的首次延迟创建仍可用 Package；已存在实例缺配置拒绝，旧库须显式 upgrade_instance_configs，只补可证明配置、不重置事实。动态 spawn API、一般跨场景创建依赖、实例装备／Effects 生命周期未完成。Package pin、静态事件程序、显式首次机械创建和静态预测仍是合法读取，不等于回退补字段 |
| 冻结 Ruleset | `[IMPLEMENTED]`（固定素材复用）；[freeze／binding](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_ruleset.py)、[冻结数据／UUID](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-srd-data/src/dnd5e_srd_data/frozen.py)、[零扫描验证回归](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/tests/test_frozen_ruleset.py)；SM [Runtime 装配](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/service.py)与 [生产路径计数回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_frozen_ruleset_runtime.py) | SM Engine／SRD 精确 pin a011eba3ea2226e22d8081294ee38d3ec193b325，RE main 相对该 pin 仅文档不同，两个包 src 差异为空。公开 getter 仍深拷贝；原始可变 Loader 仍全量摘要；不自动迁移 /36 存档至 /37，不支持热换规则 |
| World Time | `[PARTIALLY IMPLEMENTED]`；WorldTimeService＋SessionTime／TimeDriver 的显式倍率、暂停恢复、只读 TimeSync、有界工作和真实 Round 接线已有实现；[协调](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/time_coordination.py)、[Driver](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/time_driver.py)、[Round／时间回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_session_time_coordination.py)、[恢复回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_session_time_recovery.py)、[验收及测试替身范围](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/docs/SESSION_TIME_COORDINATION_PROGRESS.md) | 没有默认实时倍率；机关为生产期限提供方。Activity／Effects／NPC schedule／OB／Gate／燃料天气未全面接通；等待回复协调测试不代表生产消费者齐备；秒制 NPC 保护及活跃 Combat 恢复限制保留 |
| Action Availability | `[PARTIALLY IMPLEMENTED]`；RE /13 使用基础攻击共享 preflight，SM 有 PC／获准 NPC 包装；[RE 回归](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/tests/test_npc_availability.py)、[SM 无写入／授权回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_dnd_npc_availability.py) | 仅 combat.intent 的受测基础攻击；unknown 保留能力不足／选择等原因。Openable 有独立外层接口；全操作查询、全量目标目录、目标 CapabilityManifest 未完成 |
| Grid／Environment／Scene／对象领域 | `[PARTIALLY IMPLEMENTED]`；GridMaps 已复用只读解析地图／基础拓扑，Environment 已有双版本与有界派生缓存，SceneLifecycle 已分离初始化与实际 PC 访问，Container 有候选邻接／重量 memo，Openable／Mechanism／OSS 有受限服务 | Terrain／综合动态视觉／战斗互动／世界来源 rules.effect／真实 WO 防护／完整 Effects／生产 Agent Host 不因此完成。Container 局部语义不等于局部 SQL；空间与库存扫描见本节末审查 |

#### Current Implemented Interface 与目标差异

下表字段名／类型取对应 main 源码；代码类型和运行支持分开。`module-contracts/0.2` 是目标概念示例，不是下列版本的别名。当前机械 DTO 要求显式字段（包括 null），不能从示例推断默认值。公共接口冻结状态仍由各目标章节及评审决定。

| 契约 | Current Implemented Interface | Target Architecture Contract / Gap |
|---|---|---|
| TypedCommand／TrustedContext | [commands.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/commands.py)：dataclass，sm-command/1，必需 session_id、command_id、actor_id、command_type、强类型 payload、expected_world_version；可选 check_world_effects、time_wait。[models.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/models.py)：TrustedContext 独立含 principal_id、player_id、controlled_npc_ids 与 can_adjudicate_checks／can_advance_time／can_place_world_objects／can_manage_environment，不从模型 JSON 反序列化 | §3 的可信系统来源、可无 Actor 的联合是目标；当前 actor_id 必填，不能据 AP-15 草案传 null。可信上下文与命令 JSON 分离已实现；认证本身由 Host 负责 |
| CreateSessionRequest | 同 models.py：command_id、adventure_id、package_version、package_digest、players: tuple[PlayerSelection]，time_binding: TimeBinding 或 None；PlayerSelection 含 player_id、pc_template_id。create_session(request, package, *, context)；创建幂等与单人范围已有 [测试](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_sessions.py) | §10／Package §9.1a 的候选信封不是现有 dataclass；多人／动态扩展及一般创建闭包未完成 |
| CommandReceipt | commands.py：session_id、command_id、actor_id、status: str、world_version、event_seqs: tuple[int,...]、error_code: str 或 None；普通结果 committed／rejected／conflict／pending_choice，类型并非目标枚举 | 无独立 receipt_id、Delta、完整 Snapshot、叙事或所有目标字段；合成 pending_choice 有 unsupported 兼容边界。accepted 是 RE 结果状态，不等于 committed；见 [回执／发布](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/session_runtime.py) |
| RuleEvaluationRequest | [evaluation_contracts.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_contracts.py)：engine-evaluation/24；必需 schema_version、session_id、command_id、operation_kind、actor_id、payload、state_snapshot、ruleset_binding、rng_context；operation_kind 联合 combat.intent／rules.check／combat.close／combat.item／rules.save／rules.rest，payload 必须匹配 | RE 能解析的联合不代表 SM 已采用；SM 仍限制基础 combat.intent／check／close、独立 Openable 等路径，无通用 world-source rules.effect 或任意系统 Actor ABI |
| RuleEvaluationResult | 同源码：schema_version、session_id、command_id、input_world_version、input_ruleset_binding、status、read_set、state_delta、proposed_events、stage_facts、rng_transition、choice、error，全部必需。status 为 accepted／rejected／needs_choice／unsupported；accepted 必有 Delta／RNG／StageFacts 且无 choice／error，其余禁止携带机械结果；needs_choice 仅有 choice，另两拒绝态仅有 error | DTO 重验和 verify_request 关联校验不可移除；通用中途 Continuation／前缀提交尚未冻结，前置 needs_choice 不证明中断恢复已完成 |
| ReadVersion | 同源码 kind: world／actor／combat／scene／effects／history，ref: 非空 str，version: 非负 int；[SM result validator](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/rules_adapter.py)当前要求恰好一个 world read，ref=session_id、version=输入 world_version | 这是保守 OCC fence，不证明执行了 Full Audit，也不是已支持每实体细粒度并发。不得因目标有 actor/effects kind 就自行改变 SM 校验 |
| StateDelta | [evaluation_delta.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_delta.py)：operations: tuple[封闭 kind 联合]、expected_world_version；包含 HP／临时 HP、Conditions、死亡、预算／Turn／位置、库存消耗、资源／Effects／专注／Reaction 等类型 | 封闭 Schema 已实现，但 SM delta_changes／check_changes／closure_changes 及 _apply_dnd_changes 的采用白名单更窄；不能将候选整份 Snapshot 当权威覆盖，不承诺全部联合可生产执行 |
| ProposedEvents／EventStageFacts | ProposedEvents=tuple[CombatEvent,...]，禁止额外权威身份字段；StageFacts engine-stage-facts/2 的 complete／uncovered、outside_snapshot_unknown、参与者及有序阶段引用；[阶段结果回归](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/tests/test_event_stage_result.py)、[SM 阶段拒绝回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_frozen_ruleset_runtime.py) | 有序候选与阶段不能当第二份 Delta；complete 仅受审基础 Attack／Pass／Walk 等有界 profile，其他路径显式 uncovered。World 观察者发现、感官 Evidence、Turn／Round Episode 路由不是该字段自带能力 |
| CombatSnapshot／NonCombatSnapshot | [evaluation_state.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_state.py)：engine-snapshot/17，snapshot_kind combat／noncombat；共同必需 session_id、world_version、character_states、resource_state、casting_state、effect_states、inventory_state、scene_state；Combat 另必需 combat_state，保持完整相关依赖闭包；[严格契约回归](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/tests/test_evaluation_contracts.py) | 不含可写 Runtime／Loader／RNG，不含历史 event_log；RE history-free 读取已实现，SM 仍保存审计。不能以“局部查询”删除必要机械成员／效果／资源；完整机械闭包不等于完整 Session |
| RulesetBinding | ruleset_id: 非空 str、data_revision: sha256 加 64 小写十六进制、evaluator_version: 非空 str；当前 dnd5e-evaluation/37，实例 Session 保存三项并核对固定 Loader | Git SHA 是安装锁定，不等于 data_revision；跨模块未来组合／升级迁移格式仍 OPEN。/36 旧 Session 不能在 /37 静默运行 |
| RNGContext／RNGTransition | [evaluation_rng.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_rng.py)：Context(stream_id,version,state)，Transition(stream_id,input_version,input_state,next_state,state_changed)，state 使用 stdlib-mt19937/1 的 words[624]／index／gaussian；校验输入和真实变化 | RE 只返回候选下一状态，SM 同事务保存；无 next_version 字段，流版本推进由 SM 负责。无随机抽样的合法接受与拒绝仍区分；目标逻辑示例不能覆盖编码 |
| ActionAvailabilityRequest／Result | [evaluation_availability.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/66384b00363c00fc92622dbbf77ccfea012b1b5d/packages/dnd5e-engine/src/dnd5e_engine/evaluation_availability.py)：/13；Request(schema_version,session_id,operation_kind=combat.intent,actor_id,payload,state_snapshot:CombatSnapshot,ruleset_binding)。Result(schema_version,session_id,actor_id,operation_kind,snapshot_world_version,ruleset_binding,status,reason:RuleError)，status available／unavailable／unknown | RE 签名 query_action_availability(request, *, loader=None)；SM query_action_availability(session_id,actor_id,payload,package,*,context)。无 command_id／RNG／回执／资源预留；unsupported 通过 unknown＋受控 reason 表达 |
| save_session／resume_session | [service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/service.py)：两者 (session_id,package,*,context) → SessionSnapshot；resume 委托 save 的只读持久事实、绑定／实例／机械／RNG检查；[创建恢复回归](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/tests/test_session_management.py) | 不接收可写 Snapshot，不是文件导出或任意阶段 checkpoint；活跃 Combat 精确跨进程恢复仍 unsupported。加载／恢复验收可检查完整支持作用域，不能把其审查搬进普通命令 |
| Scene／Object 查询 | 同 service.py：read_session／get_object(session_id,actor_id,object_id,package,*,context)、list_scene_objects(session_id,actor_id,package,*,context)、get_spatial_view／read_actor_position／get_illumination；[WOS](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/world_objects.py)按可见性／祖先访问过滤 | 当前返回 detached dataclass／dict／tuple，不是统一冻结 Query ABI；list_scene_objects 底层 Session 枚举，不能按名字宣称局部。内部 GridService 不是公开世界目录 |
| NPC Evaluation／Observation | [NPC Evaluation](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/npc_evaluation.py)及 [可靠输出](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/npc_outputs.py)已有本地任务／授权输入／结果采用；OB／Gate 有本地期限和兼容接口 | MC §7／§9 的统一 NPCEvaluationRequest、单窗口 pending／processed、Turn／Round Episode 与 Host Context 契约尚未全部实施；不能把历史 Pending/Completed 词汇视为现行目标，也不能宣称已接通真实模型 |

全局扫描的分类、调用位置、当前不变量和等价局部替代建议见 SM 的 [普通提交源码](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/commands.py)、[RE 提交源码](https://github.com/agentic-trpg/trpg-state-machine/blob/d5d8c494e2fa102ca924199b31a6d00c2b4910e2/src/trpg_state_machine/rule_execution.py)及该仓库本批 `docs/reviews/RUNTIME_VALIDATION_SCOPE_REVIEW.md`。这些现有 Session 级审查与 §2.3／§6.5 的目标冲突，登记为后续重构，不能通过文档宣称已经修复。无关容器容量审查已经局部化，操作内邻接／重量重复扫描已有改进；全 Session 读取、库存闭包和空间全投影仍须分别验收。

### 1.7 2026-10-21 运行时复用与资料核对

本次总文档起点为 `bdbbdf31cc60f3e83a951541ddf7a70504526190`。SM 当前实现依据为 **尚未合并**的 `refactor/scoped-runtime-validation@4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0`，核实的 `origin/main` 仍为 `7927a382738fc97e2420967c3e1c6280c717d1fb`。不能把该分支能力写成 main 已有能力。§1.1–§1.6、旧 Review 和较早领域现状段保留原日期／SHA 的适用范围。

| 来源与核对范围 | 当前实现与设计差距 |
|---|---|
| SM [world_containers.py](https://github.com/agentic-trpg/trpg-state-machine/blob/4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0/src/trpg_state_machine/world_containers.py)，[Container Progress](https://github.com/agentic-trpg/trpg-state-machine/blob/4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0/docs/CONTAINER_SERVICE_PROGRESS.md) | `[IMPLEMENTED]` 单次操作的 ContainmentState 邻接索引、定义及 weights memo；total_weight 包含实例自身重量 × quantity 和后代，未知传播为 None；relocate 清空重量 memo。validate 读取移动子树、旧／新祖先及必要聚合闭包，再对候选关系准入。没有将 weights 发布为 Service／Store 跨操作缓存；World §2.1b 的跨操作重量缓存为 `[DECIDED; NOT IMPLEMENTED]` |
| SM [分支验收记录](https://github.com/agentic-trpg/trpg-state-machine/blob/4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0/docs/reviews/SCOPED_RUNTIME_VALIDATION_REFACTOR.md)、[容器测试源码](https://github.com/agentic-trpg/trpg-state-machine/blob/4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0/tests/test_container_admission.py)、[局部查询测试源码](https://github.com/agentic-trpg/trpg-state-machine/blob/4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0/tests/test_scoped_runtime_validation.py) | 原记录包含局部读取／准入、Schema40 派生索引和操作阶段复用的历史验收。本次仅查阅源码、测试和已有记录，未重新运行业务或性能测试；不能把历史数字当成本次结果，也不能据通用操作 memo 推断 weights 已跨操作复用。该分支继续固定 Engine／SRD pin `a011eba3ea2226e22d8081294ee38d3ec193b325` |
| RE `main`／`origin/main@f18e0ad0d0bb6641efb050b51bf919dd41a8631f` 的 [evaluation_ruleset.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/f18e0ad0d0bb6641efb050b51bf919dd41a8631f/packages/dnd5e-engine/src/dnd5e_engine/evaluation_ruleset.py)、[frozen.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/f18e0ad0d0bb6641efb050b51bf919dd41a8631f/packages/dnd5e-srd-data/src/dnd5e_srd_data/frozen.py) | 已有固定有效规则素材、冻结身份及 UUID 索引复用；精确 FrozenRuleset 类型校验身份，mutable/custom loader 仍重算摘要。不能推广成全部规则计算都已缓存；RE checkout 与 SM pin 分别归属各自证据 |

规则版本、已核实章节及未核实书籍／冒险正文见 [References](./REFERENCES.md)。本批不改规则集绑定、不新增世界观、不实现缓存、不修改代码／Schema／依赖／CI；检查范围与三仓库工作区基线见 [本次文档记录](./reviews/runtime-reuse-and-references-2026-10-21.md)。

### 1.8 2026-10-21 Session 内存运行层基线核对

本次 fetch 后固定源码：架构 `8cdfc18390d105ff1d4c19ba70712276afb3eee8`；SM `d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34`；RE `34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a`。SM origin/main 已包含用户指定提交，旧 §1.7“未合并”仅为当时事实。详细入口、测试源码与历史验收边界见 [本次静态核对报告](./reviews/SESSION_MEMORY_RUNTIME_SOURCE_REVIEW.md)。

| 主题 | 当前实现静态判断 | 新目标的差距 |
|---|---|---|
| 事实读取／Snapshot | SM Facts、service._snapshot、RulesAdapter 仍通过 SQLite 读取、JSON／DTO 装配 | 已加载事实的查询／检查／RE 输入／角色视图／Snapshot 统一读 RAM，整体 [NOT IMPLEMENTED] |
| 提交与发布 | Store／UnitOfWork 共用事务；SessionRuntime.publish 在事务内写版本／事件，finish 写回执；Store COMMIT 后发布的是派生缓存 | 该 publish 名称不代表完整当前事实的提交后内存发布；故障暂停／对账／重建协议 [NOT IMPLEMENTED] |
| 复用与索引 | GridMaps、Environment 缓存、操作阶段 memo、ContainmentState、Schema40 派生占格索引和验收记录已有实现 | 保留这些资产；跨命令容器重量／机关索引复用、免重复 SQL 装配的统一读取仍待实施 |
| 恢复 | save_session 已说明修改即时持久化；resume 复用非战斗保存检查，活跃战斗有 process_id／combat_unrestorable 限制 | 重建完整活跃 RAM 与持久提交后发布故障验收未实现；事实恢复不等于任意玩法阶段续玩 |
| RE 边界 | evaluate 深拷贝并验证请求，FrozenRuleset 复用；当前公开版本不变 | 接入 RAM 是 SM 消费者内部目标，不改变 Stateless RE、DTO 或 ABI；完整 Stateful 退出仍有既有缺口 |

本次读取源码与测试源码、历史 Progress／验收报告，**没有运行 SM／RE 业务测试、故障注入、规模或多人验收**；历史 2,015 个通过用例不构成本次 RAM 目标证据。Architecture Decision、Implementation 与 Acceptance 分开登记，具体 API／字段／细粒度版本保持 OPEN。

## 2. 统一标识、版本和契约通则（P0）

### 2.1 规范标识 `[PROPOSED]`

- `session_id`：Game Session 稳定 ID。
- `command_id`：由调用方/可信 Host 生成；普通游戏命令在 Session 内唯一，创建前在可信 principal_id 内唯一（§10）；同一幂等键不可用于不同命令内容。
- `principal_id`：来自可信认证环境的发起主体，由可信适配层绑定命令；不是 LLM 自报凭证。
- `actor_id`：适用操作的实际行动 Actor，与 principal_id 区分；Actor 行动必填，受信系统/世界事件操作按具体强类型分支校验（AP-15，§3.1 / §4.1）。
- `command_type` / `expected_world_version` / `payload`：普通命令的封闭类型判别、预期权威版本与对应强类型参数；不使用同一信封的 kind / controller_id 别名。
- `world_version`：该 Session 权威状态版本；发生世界/机械状态变更的成功提交单调推进。仅事件或元数据提交的推进规则为 [OPEN]，不能直接等同 event_seq。
- `component_versions`：可选的对象/Combat/Character 局部版本，用于低冲突的读写集校验；MVP 可以仅使用全局 `world_version` 进行保守 OCC。
- `event_seq`：Session 内严格单调递增的**已提交**事件序号。
- `ruleset_binding`：Required ruleset_id / data_revision / evaluator_version，由 SM 从 Session 固定配置提供；data_revision 区分实际生效数据（含适用 Homebrew），Engine 验证匹配（§4.3）。
- `schema_version`：明确的消息格式版本（例如 `module-contracts/0.2`）。

所有对外 ID 与关系引用都必须遵守 Type/Namespace 校验，不能由 Agent 自选数据库路径或可信身份。所有命令以稳定规范化序列化（Canonical JSON）生成 `command_fingerprint`；普通游戏命令建议包括 `command_type`、`actor_id`、动作 payload 及必要的授权/规则上下文绑定；创建请求包括批准 Package 身份/摘要与 players[] 等实际创建内容（§10），不套用尚不存在的 session_id / actor_id。排除纯传输重试头。具体 canonicalization 算法与版本应在实现前冻结。

评审 §6 建议普通事实／活动／战斗进度或正式外显事件每次提交推进一次 world_version，纯 Meta 用 npc_state_version，投递／处理标记不推进世界版本；仍待兼容验证，C-07 不因此关闭。评审 §16.1 记录显式 `stdlib-mt19937/1`（624 个 32-bit words、index、gaussian、stream_id／version）与 `version += int(state_changed)`；保留固定实现编码，不换 seed-only 或全局 RNG。本文共同 wire schema／跨版本策略仍待验证，不静默改旧协议。

### 2.2 幂等语义 `[DECIDED + PROPOSED]`

Create Session 尚无 session_id，使用可信 `(principal_id, command_id)`，创建结果见 §10。以下适用于普通游戏命令，按 `(session_id, command_id)` 在 State Machine 的**持久数据库**中去重：

- **相同 Fingerprint、已提交：** 返回原 `CommandReceipt`，不重新掷骰、不重复扣资源、不重复发事件。
- **相同 ID、不同 Fingerprint：** `idempotency_conflict`；不执行。
- **首次请求，尚无终态：** 可进入求值；必须解决并发重入（唯一约束 + 原子 claim / 提交校验），不能只在内存中判断。
- **已完成的确定性拒绝：** 可记录原 `CommandReceipt`；变更输入需要新 `command_id`。
- **网络中断，是否提交未知：** 调用 `get_command_receipt(session_id, command_id)` 查询，**不可**简单改用新 ID 重试。

可信端校验 principal_id 的权限与适用时的 Actor 控制绑定，或受信系统/世界事件的机械来源和目标；无 Actor 分支不能绕过授权。Replay 不能突破当前授权策略。原样重试复用 command_id，修改 payload / 裁决后果等命令内容须用新 command_id；状态/反馈未知先查原回执。确定性拒绝不强制重新调用 LLM，仅需新情境语义判断时才有界重规划。

### 2.3 运行时数据复用、派生 Snapshot 与版本有效性 `[DECIDED]`

**全系统原则（2026-10-21）：按需计算，保留值得复用的结果，在有效性得到保证时复用；相关输入变化时更新或使结果失效。** 本原则适用于空间、光照、环境、容器重量、角色观察视图、规则素材处理，以及其他重复准备或派生计算；以下条款共同构成同一规范，不另建缓存协议。资料查阅和来源分类见 [统一参考入口](./REFERENCES.md)。本次仅补充文档，不实现缓存或宣称性能改进；SM 未合并分支的证据另见 §1.7。

本节是跨模块共同规范；Grid／Environment 的依赖细化见 [World §2.0b–§2.0c](./WORLD_SUBSYSTEM_DESIGN.md#20b-grid-运行时输入复用-decided)，RE 数据身份见 §4.3。原则已确定；具体接入与未实现项以 §1 的日期化证据为准，Grid／Environment 本次核对见 §1.5。不要求先建设通用缓存平台或让所有查询创建 Snapshot。本节的快照原则不改变 §4.2 机械 Snapshot 的完整性要求，也不是 EVA 冻结输入或历史 Event Evidence 的替代。

#### 统一运行时读取与 Snapshot 构建（2026-10-21）

**Architecture Decision Status [DECIDED]；完整接入 Implementation Status [NOT IMPLEMENTED]；运行验收未执行。**

1. 已加载且版本有效的活跃事实，普通查询、操作检查、RE 请求组装、角色视图和 Snapshot 构建**统一从 Session 内存运行状态读取**，不另行查询数据库重新装配同一批事实。光照、环境、容器重量等派生计算也从该状态获取必要输入，已有有效结果直接复用。
2. 一次读取／Snapshot 构建绑定同一个一致提交版本；并发修改不得混入其他版本数据。提供给 RE、NPC 或历史记录的固定输入不能被后续发布原地改变。实现可用不可变结构、分离副本或其他经证明的隔离方式，不要求所有读取制作完整 Session Snapshot，也不要求每次复制整个 Session。
3. 命令期间检查未提交中间结果，统一读取**隔离候选状态**及其同阶段索引／派生输入。不能提前改已发布对象，不能读旧数据库事实而漏掉本次候选变化；候选阶段／savepoint 回退与提交版本须区分。
4. 有效性由统一运行时的提交版本、完整依赖维护和生命周期保证。不得为了确认每次内存读取有效，又扫描或装配数据库中的同一批状态。提交时必要数据库约束、版本／原值及并发校验继续保留；缓存命中不豁免授权和披露。
5. SQLite 继续承担持久提交、首次加载、冷数据加载、恢复、持久回执和可靠工作查询。冷数据只从持久实例事实补入，并与本次读取版本一致；若数据库已前进而无法取得该版本所需数据，应重新获取一致读取范围或明确重试，不能拼接时点。无需让全部世界、场景、日志或归档记忆常驻 RAM。
6. 按 Session、活跃场景与真实依赖加载，声明加载／卸载、冷访问、容量预算、引用保留和 Session／Store 关闭释放边界。已提交基础事实可从 SQLite 重建；卸载不能丢失可靠工作或把旧引用改变为新状态。具体预算／淘汰策略 OPEN。

| 数据类别 | 责任与表示 | 生命周期与修改要求 |
|---|---|---|
| 当前基础事实 | 领域拥有；RAM 供运行读取，SQLite 持久保存 | 仅统一提交后发布；HP／位置／关系／版本不双写为独立权威 |
| 查询索引 | Cell→实体、容器父子、机关触发／组件关联 | 由事实维护，可重建；不得独立修改关系；候选与已提交版本隔离 |
| 派生缓存 | 光照、环境合成、容器重量等 | 按完整依赖复用，变化后局部更新或失效；不必写回事实字段 |
| 固定版本输入 | RE／异步 NPC／历史证据所需一致视图 | 必要机械闭包完整；后续提交不原地修改旧输入 |

迁移按领域声明当前事实读取路径。同一操作不得无版本混合旧 SQL 输入与新 RAM 输入，新旧路径不得独立写同一事实。聚合 JSON 拆分、RE 按需依赖组装与 RAM 层相互配合，不能因加入内存表示就宣布存储粒度和请求依赖问题全部解决。

#### 快照与查询的使用原则（2026-10-20）

| 概念 | 用途与边界 |
|---|---|
| 快照（Snapshot／读取 View） | 表示某个读取时点的一致、只读数据或计算结果；范围由消费者需要决定，可以只含局部数据，不自动具备缓存能力 |
| 缓存（Cache） | 复用依赖仍有效的输入或计算结果；必须说明有效性、隔离、容量及生命周期，创建快照本身不等于消除重复计算 |
| 查询索引（Query Index） | 快速定位相关实体或关系，减少无关读取和扫描；不能替代一致性、权限或派生结果有效性检查 |

缓存负责复用，Snapshot 提供某个一致状态下的只读视图，索引帮助定位相关数据。三者可以组合，但不要求每个缓存值都包装成完整 Snapshot；不能相互替代。不因接口名含 View 或 Snapshot 就推定低成本或已缓存。

1. **查询范围与工作量匹配。** 单实体、单格、少量格子或局部范围，应优先使用相应的定向读取／查询；不能为调用便利方法而默认先物化完整场景。接口接受少量格子还不够，内部也须避免读取全场景、遍历所有实体或构建完整快照。若当前缺少这种路径，应明确为待实现能力，不能把全场景扫描包装成已完成的局部优化。SQL 索引、占用投影等实现由所属模块决定，本节不承诺尚未实现的数据结构。已经取得且范围、字段、时点及授权满足本次要求的快照可以复用，不必反向强制查库。
2. **快照必须有明确消费者。** 一次操作在同一状态版本上做大量相关查询，或复用昂贵投影、环境合成和批量计算时，可以准备所需范围的快照。应说明消费方、必要字段、空间范围、读取时点和复用生命周期，同时衡量首次构建成本、查询次数、状态变化频率、缓存命中率及内存成本。“未来可能使用”不足以扩大范围；暂时没有生产调用也不足以未经契约核对删除已有场景快照接口。
3. **一致性不等于全量加载。** 目标中多次定向读取使用同一版本的 Session 内存读取范围；首次／冷加载及迁移期间尚未接入的领域可使用明确的一致数据库读取范围，无需因此加载整个场景。同一次决策不得拼接不同读取时点／修改阶段的数据；定向查询同样遵守权限与可见性。计划执行仍要重验版本和相关前置条件，读取视图不等于执行许可。
4. **按事实和依赖分责。** 地图拓扑等相对稳定输入按实际来源及相关配置版本复用；实体位置、朝向、开关等动态事实仍由现有权威组件管理。占用关联、阻挡、光照和环境合成属于可重建派生数据，必须声明其来源，不能独立改写同一事实，也不能把派生环境复制成 Cell 的权威字段。持久化派生记录须与权威变化事务一致；内存派生数据须处理回滚、隔离、失效和生命周期。
5. **按实际依赖决定失效与更新。** 完整依赖、相关版本和必要的时间边界共同决定有效性。新版本查询不得返回旧结果作为当前状态；旧快照可以继续表示原版本，后续移动、提交、回滚或缓存更新不得原地改变它。静态地图与动态占用应能分别复用／更新，不默认每次移动重建全部场景，也不假定已有局部或增量能力。局部更新、延迟重建、增量维护仅在具备明确依赖追踪和一致性保证时采用；不要求所有模块同用一种缓存策略或所有快照都支持区域增量。允许有明确依赖依据的全场景失效；保守失效及其成本须如实记录，不能称为局部更新已完成。

#### Full Integrity Audit、Local Admission 与合法全量计算 `[DECIDED]`

Full Integrity Audit 检查完整声明作用域内的持久实例、引用、关系和跨实体不变量。正常入口限于初始化完成验收、存档加载／恢复、迁移验证和显式完整性诊断。普通查询、Action Availability、普通命令、局部更新和共享 Commit／Finalize 不得默认执行完整 World／Session 审查；任何例外必须记明消费者、必要范围和架构依据。

Local Admission Check 检查实际操作、候选 StateDelta 的全部受影响实体、位置、关系、状态及必要依赖闭包。移动检查完整候选占格、墙线、通路保留格和相关冲突实体；开门检查目标及受影响双侧通行关系；取放检查移动子树、原／目标祖先和必要容量、重量、访问与装备绑定；规则操作检查 Actor、资源、Effects、物品及完整机械依赖。联动操作按候选中间状态逐步维护闭包，不能只验最初目标。

审查直接及间接调用，按 SQL 实际行范围、实体枚举、JSON 解析、模型／Snapshot 构建、整场投影、审查和缓存／索引维护分类。接受 Object ID／Cell、名称含 check／view 或传入 affected 集合，都不能单独证明底层读取局部化。Full Audit、局部准入、Query／Projection、完整机械闭包与其他必要批量计算须分别记录。

整张地图路径规划、明确要求完整场景输出的批量查询、Encounter 初始化兼容检查和完整必要机械 Snapshot 验证可以有合法全场景消费者；范围由真实依赖决定。不得为性能删除授权、Schema、Snapshot、RNG、RulesetBinding 或规则闭包验证。替换已有 Full Audit 前先列出其保护不变量，证明持久约束与局部校验等价覆盖，包含非法状态及连锁变化的回归；本规范不授权直接删调用。

能在合法写入维护的关系、版本、索引不应靠每次全量审查重新发现；维护须与 Commit／Rollback、OCC、失败重试、依赖失效、Store／Session／Scene 生命周期、重启恢复及迁移一致，不引入独立可写的第二权威。后续局部查询和准入重构须保持目标范围固定，分别增加无关 Scene／Object／Actor／Item，用 SQL 行数、解析／构建／投影／扫描次数证明成本不随无关实体同步增长；真实依赖单列。静态调用链分析不等于已运行规模测试。

#### 性能验收与证据边界

性能验收覆盖真实生产调用链及数据分布，包括读取、解析、模型／快照构建、投影、索引维护、复用检查和最终查询，不能只验证返回值或只测 View 的最后一个方法。后续定向查询改造应在目标范围固定、无关实体逐步增加时，验证无关增长不会导致全场景读取、模型构建或重复投影同步增长；授权和确实影响目标的依赖开销须独立说明，不能为性能跳过校验。

快照路径分别记录首次构建、有效复用、失效后重建及必要的维护成本。优先统计 SQL 次数、读取行数、解析次数、模型构建次数和投影次数，并记录内存／命中情况，耗时作为补充。简化微基准的实体数量分界不能写成项目固定性能承诺。区分已测得的生产问题、代码揭示的潜在误用风险及目标设计；本次文档约束不构成性能修复或运行验收。

#### 权威事实与只读原始输入

事实权威归所属领域；RAM 是统一管理的已提交运行表示，SQLite 是同一事实的持久提交表示与恢复依据。二者均不得独立接受业务写入；索引和派生缓存可丢弃重建，运行事实卸载须遵守上述生命周期。业务修改走既有受控命令／领域接口及共同事务，保留授权、幂等、OCC、RNG、事件证据、Receipt／Outbox。派生环境不得写回 Cell 形成独立维护的状态；Cell、Grid、WorldObject、Environment 等原始输入仍由所属组件管理。

JSON 用于持久化、传输和规范化编码；频繁读取的数据加载后保留适合访问的只读结构，避免每次读取属性都重新解析整段 JSON。共享结构不得由消费者原地修改；计算修改候选时使用独立副本，包括其嵌套可变内容。

| 输入类型 | 复用依据 |
|---|---|
| 固定 Package／Ruleset | 按已验证、有效内容固定的完整身份复用，不能只凭包名或发布版本 |
| 场景地图配置／基础空间结构 | 按场景、所属 Package／Store 及相关配置版本复用；动态贡献另验依赖 |
| 动态游戏事实 | 从统一 RAM 当前版本／隔离候选读取，按完整依赖维护有效性；首次／冷加载单独保证同版本；不得无条件长期复用 |

Package／Ruleset 固定数据的复用仅适用于其定义职责；已存在实例的有效字段来源按 §2.4，不能以缓存模板代替完整实例记录。

不要求所有数据常驻内存或加载整个世界。按活跃场景和常用数据保留，并明确容量上限、所属生命周期、淘汰及 Session／Store 关闭等释放策略；丢弃缓存不能丢失事实。

#### 按需派生与有效性

可复用对象包括解析后的只读配置、查询索引、中间结果、派生数值及只读 Snapshot。按计算成本、访问频率、变化频率及内存成本选择策略；不强制长期缓存每个简单计算结果。局部请求不得为了建立缓存／Snapshot 而额外计算整个场景或整个世界。

**更新范围与增量前提：** 有可靠依赖追踪时，只更新或失效相关结果；允许正确且明确的较粗粒度失效，首次实现不要求精确局部更新。只有缓存对应修改前的有效状态、且掌握完整相关变化时，才可按差量更新。旧值不可靠、变化不完整或规则难以增量处理时，应使相关结果失效并按需重算；不得对已经过期的总数直接加减。容器应用见 [World §2.1b](./WORLD_SUBSYSTEM_DESIGN.md#21b-容器重量派生与跨操作复用)。

针对已确认重复开销复用已产生结果；共享中间结果和最终结果可分别保存。屋顶覆盖 16 格可以共享防护投影，但不意味着这 16 格的风、温度、雾等完整环境相同。只缓存实际算出的结果；一次计算确实得到多格完整结果时可一起保存，不为填满 Snapshot 主动重算整张地图。

版本描述计算所依赖的状态，不描述缓存创建／清空次数。相关事实与依赖版本须在同一事务提交；失败、拒绝、回滚或 COMMIT 故障不得留下错误版本或可供后续命中的候选缓存。合法失败如确有已提交成本／事实变化，仍按实际变化维护依赖版本。

查询从统一内存读取范围取得当前提交／依赖版本，与缓存记录比较；不得重读数据库同批事实来证明有效性。首次／冷加载依上述版本协议处理。只有完整依赖匹配且已有所需结果才复用；不匹配或缺结果即按当前状态计算。版本 7 跳到 9 直接算 9，不补算 8。通知清空与 TTL 可辅助资源管理，不能独自证明有效；目标是可信版本校验，命中时不再扫描全部原始输入来比较，也不能为了确认有效性又完成原来的计算。

外部提供方必须声明完整依赖身份、可变输入、版本推进／读取一致性及生命周期，包括影响结果的时间与适用范围。没有可信版本时，临时路径只能在一次一致读取中计算并复用，跨查询绕过缓存；提供方若无法保证该读取一致性，返回明确能力缺口。兼容期如保留全量输入扫描／比较，必须标为降级及其成本，不能称版本方案完成；不能仅缓存旧摘要而放任底层内容变化。

缓存不要求长期保存每个历史版本。旧读取事务可保留自身一致结果；其发布必须验证仍适用的身份／版本，不得覆盖当前缓存、冒充当前状态或把旧结果贴上新版本。写事务中不同修改阶段须重建或重验共同输入，回滚到相同数值版本也不能让不同候选输入误命中。

#### 共享范围与安全边界

身份和生命周期按实际依赖隔离 Package／Ruleset、数据库／Store、Session、对象／Scene、历史事件及查询参数，并覆盖实际依赖版本、时间条件和必要观察者上下文；无需无差别把所有维度塞入每个键，但不得遗漏会改变结果的维度。同一查询内准备一次共同输入供多目标判断；跨查询复用须明确依赖身份及有效性保证，同一事务不同修改阶段不能共用已经过期的输入。

缓存命中仍执行实际操作需要的当前授权、合法性、并发版本、事务及披露过滤检查。内部真实投影与公开输出保持原边界，不能将一个观察者的过滤结果未经校验交给另一观察者。历史事件计算绑定该事件当时的阶段证据／固定过滤依据，不能用当前 Scene 缓存替换；事件身份及其证据版本必须进入相应复用范围。

清理／淘汰内存缓存本身不得制造业务状态变化。确需持久化派生数据时，须另行明确与事实写入的一致性、依赖维护和重建机制；本原则不授权新增持久化字段。候选缓存不得提前作为已提交结果发布，失败、回滚、重试及旧读取事务不得污染当前缓存；已发布不可变 Snapshot 继续保留原状态，后续变化通过新版本结果体现。

### 2.3a 实例字段、关联与局部准入 `[DECIDED]`

普通查询与操作必须从目标实例出发，沿已有字段、关联和索引访问必要数据；准入检查
限定于候选修改影响的对象、依赖关系及必要中间状态。不得以全 Session、全 Scene
扫描或完整审查代替已有索引和局部检查。全量审查保留于初始化、恢复、迁移、显式诊断
等确有需要的入口；业务确实需要全范围结果时，按请求范围执行并说明成本。

已加载且有效的实例字段及派生结果从同一 Session RAM 版本读取，覆盖普通查询、
候选准入、领域计算、View、RE Snapshot 和固定 NPC 输入；不为获取同一有效数据重新
查库、回查 Package、解析 JSON、遍历实例、组装关系或重算派生值。Package 仅提供创建
模板，首次／冷加载和恢复读取完整持久实例；冻结规则素材沿既有规则绑定共享。

单个实例的事实、关联和值得复用的派生结果由该实例的明确字段持有，可使用有类型的
组件分组。Service 负责行为、计算和受控维护，消费者必须实际使用这些字段，不能只将
通用缓存字典改名。事实只有一个权威来源：目录、父子集合、占用及触发索引是事实的
派生关系，以同一实例引用或稳定 ID 关联；不能复制出可分别改写的物体／角色状态。

| 持有者 | 事实／关联／可复用字段 | 维护边界 |
|---|---|---|
| Object／Item | 自身有效重量、数量、直接位置、能力配置与状态 | 原所属领域经既有事务修改；位置／归属仍为唯一事实 |
| Object.container | 直接内容物关联、内容物重量与自身加后代总重量 | ContainerService 沿父子索引维护／失效受影响祖先；未知重量不变成零 |
| Object.mechanism | 自身触发器、组件和联动关联 | MechanismService 读取实例配置；状态、次数、解除与重置仍由机关事实持有 |
| Scene.spatial | 已解析地图、拓扑、格子占用和动态阻挡索引 | 角色／物体位置和地图事实驱动；局部查占用使用已有索引 |
| Scene.environment | 场景环境事实／来源关联、防护投影、有界位置／高度结果 | 来源、防护、时间边界、配置和外部提供方依赖均进入有效性规则 |
| Scene.lighting | 有效光源贡献关联、几何及有界光照结果 | 光源开启等事实归 Object；携带／嵌套／遮光按实际位置规则贡献 |
| Scene.mechanisms | 本场景机关关联，事件／目标到触发器索引 | 配置、成员和有效场景变化维护；零机关是可复用的有效状态 |
| Scene.objects | 直接放置于该场景的物体目录 | 不混入角色携带物和容器内容物；有效贡献另沿实际位置关联获取 |
| World／相关跨场景实例 | 共享门、跨场景通道及组件反向关联 | 按真实作用范围持有；不复制成多个可独立修改的场景事实 |

没有要求链表或 Cell 运行实例，也不把全部事实塞入 Scene／Session。场景卸载不销毁
仍存在的角色、携带物或效果；效果生命周期仍由实际持有者负责。

只在尚未加载／计算、依赖变化或已有结果未覆盖请求参数／范围时准备数据。低成本关系
增量维护，昂贵结果更新依赖版本或失效后按需重算；无关修改不应导致所有场景失效。
不得为生成缓存键或确认有效性而扫描、排序、哈希或序列化全部候选／全部实例。
复用重量后仍比较容量，复用占用后仍检查候选位置；授权、披露、OCC、绑定、RNG、
必要数据库约束和幂等语义不变。候选容量不得命中与候选内容不匹配的已提交重量。

当前实例与固定 SceneSnapshot、GridView、RE／NPC 输入分开：修改后新读取看到新版本，
旧输入不被原地修改。所有字段沿 §6 的候选隔离、增量 SQLite 提交、提交后 RAM 发布及
故障暂停／恢复处理；savepoint 回退和整体回滚不得污染已发布字段。每次成功修改仍
持久保存全部必要事实、版本、RNG、证据、Receipt、Outbox 和可靠工作，不能改为仅
定期或手动存档，也不能声称 RAM 与 SQLite 跨介质 ACID。

跨连接恢复须使所有相关上下文的旧当前表示失效：可采用恢复代次或等效协议，各上下文
在自己的线程确认有效性后才服务／发布；不能只重建 B 就放行 A 的旧 RAM，也不直接
跨线程操作 A 的 SQLite 连接。历史固定输入可保持其历史含义，无关 Session 保持隔离。

**修改维护与有效命中（2026-10-22 补充）：** 重量等聚合字段的有效读取检查字段自身
有效性／版本，不能每次展开全部内容物及后代依赖证明命中。相关修改须在同一候选边界
维护或失效受影响字段及必要旧／新祖先，事实、关联和有效性状态一起提交／发布；只把
实际计算版本标记为有效。机关索引使用安全只读结构按事件／目标条目访问，不能为查一个
条目复制全表或验证全部配置。能力关联按移动子树、角色携带及实际能力贡献维护；同场景
位移、遮光／访问变化、开关／模式与成员进入／离开分别处理，不能以无关归属变化触发
全场景重新发现。冷准备／恢复和完整必要输出保留真实范围成本，不能把普通命令反复
重建称为冷加载。新辅助关联必须声明事实来源、维护入口、回滚、卸载与恢复规则；不得
成为独立可写事实。实现与确定性计数见 [后续核对](reviews/RUNTIME_INSTANCE_OWNERSHIP.md#2026-10-22-follow-up-field-validity-and-local-associations)。

字段按需加载，保留显式卸载、冷补入及有界预算／淘汰；不预装整个世界或无限保留
位置、高度、观察者组合。验收检查真实消费者、候选／回滚／恢复及 SQL、解析、构造、
键遍历、索引重建和派生计算的独立计数，不以新增字段或耗时相近代替运行证据。

#### 受管理运行输入的身份与版本（2026-10-22）`[DECIDED]`

**局部查询与准备补充（2026-10-22）[DECIDED]：** 光源集合等聚合派生字段的热读取和
上层消费者均只检查完整、修改维护的字段级有效版本，不能把全部叶子依赖向外展开后
逐项复验。成员、源状态、实际位置／容器传递与遮挡几何按实际影响维护，不能因无关
物体修改扩大到所有照明字段。候选事实、关联和失效状态仍在同一 §6 边界提交／发布。

固定 Snapshot／GridView 也需准备或共享与自身版本一致的局部查询索引和计算结构：
单格查占用／按实体 ID 查占格不遍历整个目录；移动和掩体查询不逐次复制、合并整图或
重建相同拓扑。旧视图不能指向后来可变的当前 Scene 索引，公开 DTO／序列化与必要的
未知／不支持拒绝保持。读取地图墙段或尺寸等单个字段，直接取一致范围中的解析字段，
不默认复制其他地图数据。静态配置资格按实际地图版本准备，候选合法性仍按影响范围
检查真实占格、边界、保留格、相关墙边和冲突，不以缓存删除合法性校验。

批量准备共享相同输入；防护输入若只需尺寸，不逐物体复制／编码／解析完整地图。
明确空贡献可在语义许可处提前排除，不能将 None／unknown／unsupported 当作空。
登记提供方的身份／版本／时间边界和未登记提供方的跨查询缓存限制保持。冷准备、
失效重建、热命中、不同请求参数与完整输出分别取证；首次必要建索引和完整范围工作
不混作热命中成本。具体已实现切片、基线与实测见
[本批报告](reviews/RUNTIME_INSTANCE_OWNERSHIP.md#2026-10-22-local-query-reuse)，
不据此声称全系统已消除扫描或序列化。

系统自己维护、有明确实例归属与修改来源的数据，以稳定实例身份、同一 RAM／候选读取
范围的完整相关版本和必要查询参数复用。ID 只确定“是谁”；不能单独证明当前有效。
普通热读取不得先遍历、排序、序列化或哈希完整地图、库存、Snapshot 或依赖集合来制作
键或确认命中，也不得为版本检查重新读库或计算内容摘要。修改路径在同一候选事务维护
事实、关联和版本／失效状态，完整覆盖配置、成员、数量、位置、装备／可访问性等真实
依赖；不得以不完整版本替代完整校验。只有缺失、相关变化或淘汰后才重新准备。

| 逻辑持有者 | 输入／结果与读取 | 维护、隔离与冷准备 |
|---|---|---|
| Scene.spatial | 已解析基础地图、基础拓扑；Grid 与局部几何读取共享 | 地图配置相关版本；角色／物体移动不使基础拓扑整体失效；冷加载验证持久实例 |
| Scene.spatial 的动态关联／索引 | 角色占用、物体占格和门阻挡；局部移动只结合所需格子 | 所属位置／状态事实驱动，保留斜向、墙边、共享门、多格、排除自身及边界语义 |
| Scene.lighting | 光源贡献、几何、单格结果及显式完整投影 | 开关／模式、实际位置、容器透光、遮挡等相关依赖；命中仍授权、几何判断和披露 |
| 角色／库存领域实际持有者 | 库存事实的模型和必要投影；角色读取与规则组件选择 | 归属、数量、装备／调谐及容器可访问性按实际模型依赖维护；选择键区分拥有者和物品集合 |
| Scene.spatial 共享地图的感知模型 | 感知／EventCapture 的完整类型化地图 | 明确模型类型与地图版本；移动模型的默认字段不能冒充完整感知证据 |
| Event 的对应修改阶段 | 固定感知证据、信号与历史结果 | 从本阶段一致状态采集后隔离；保留必要的证据持久化／传输编码 |

这些是职责要求，不冻结示意字段名为公开 API。旧事务、旧 Snapshot、固定外部输入与候选
阶段分别使用自身身份／版本，不能按 scene_id 换成当前地图，也不能用 Python id() 掩盖
可变输入。版本数重复、保存点回退、卸载或恢复不得命中另一份状态；保留有界预算、淘汰、
跨连接恢复栅栏及 COMMIT 后发布协议。外部固定输入没有可信身份／版本时允许按内容识别，
受管理的内部生产路径应避开该降级入口。完整列表、完整证据、协议及必要校验按真实范围
执行；幂等冲突、请求绑定和证据完整性的内容指纹不由 command_id 或普通版本替代。

**实现状态分开取证：** 本分支对应的 SM 地图／Light／库存／阶段地图接入与同口径计数见
[后续实现审查](reviews/RUNTIME_INSTANCE_OWNERSHIP.md#2026-10-22-follow-up-managed-versioned-inputs)。
其中仍保留的严格复杂模型编码、冷聚合索引、真实依赖与独立未修复问题不属于“全系统完成”。
该批当时记录的四个独立问题由下述新验收在具体范围内取代，历史计数不变。

**字段依赖、类型结果与版本维护成本（2026-10-22 四项修复补充） `[DECIDED]`：**
失效依据是 OLD／NEW 中实际变化的结果字段及必要一致性依赖，不能因为同属角色记录或
表就无条件失效库存。位置、HP、行动状态与库存分别维护真实依赖；归属、数量、充能、
可访问性、容器祖先状态、配置及来源一致性仍须完整覆盖。已通过同一完整校验的类型化
结果应由需要它的消费者复用，不能在投影前后再次进行等价完整验证；严格标量、重复身份、
事实／投影一致性与披露要求不变。局部目标检查从行动者和目标身份及关联直接取得事实，
不得为检查一个目标构造全 Session 角色位置副本；求值前后必要的重新确认仍执行。

版本管理本身也受局部成本约束：事务、查询、保存点或提交不得逐次复制／遍历所有已加载
版本记录。允许不可变根、结构共享或等效隔离机制，更新成本随实际修改及索引路径增长；
旧范围不能引用会被新范围原地修改的版本映射。整理／裁剪须明确阈值、摊销和回收，不能
形成无界覆盖链或在阈值附近每次操作都重新全量准备。恢复代次、组合版本和旧读取发布
栅栏仍有效。具体数据结构属于 SM 实施选择，不成为新公开协议或第二套状态目录。

**SQL 语句失败与候选协议 `[DECIDED]`：** SQLite 的 ABORT／FAIL／ROLLBACK 后果不同，
不能假定数据库已撤销所有先前捕获的候选。现有 RuntimeConnection／UnitOfWork 必须协调
SQL、候选事实／关联／字段版本和读取 memo：要么一起恢复，要么把写入范围标记为失败，
在相应回滚前禁止使用不可信候选及正常提交。捕获异常不能绕过该保证。恢复到失败前的
有效保存点后可以继续；整事务回滚释放该失败范围，不永久污染 Session。不得每条 SQL
复制全 Session／缓存／版本表。COMMIT 后错误仍使用原结果未知／发布暂停和对账协议。
本次配套分支实施与复现证据见
[四项修复验收](reviews/RUNTIME_INSTANCE_OWNERSHIP.md#2026-10-22-four-fixes-transaction-and-local-costs)。

### 2.4 Package 创建参照与完整实例化 `[DECIDED; PARTIALLY IMPLEMENTED]`

架构决定为 `[DECIDED]`；整体实现为 `[PARTIALLY IMPLEMENTED]`。§1.6 核对的 Schema39 已完成现有实例配置读取闭包和显式旧库升级；动态 spawn、一般创建依赖及完整实例装备／效果生命周期尚未完成，不能把整体标成完全未实现或全面完成。Package 是静态定义和创建参照，不拥有 Session 中正在运行的游戏状态。创建世界、场景、角色、WorldObject、Item 或 Session 时可从 Package 取得初始属性、能力配置和初始状态；创建完成后，实例的完整有效属性与当前状态由 Session 内所属领域的数据记录持有。固定 Package 版本不能代替完整实例化。

操作已经存在的实例，必须通过实例及所属组件的接口读取有效数据，不得反向查询 Package 初始化定义来补齐缺失的实例字段。完整性覆盖实例声明能力所需的配置、状态及必要关联，具体 World 能力示例见 [World §2.1a](./WORLD_SUBSYSTEM_DESIGN.md#21a-完整实例能力与统一读取-decided-partially-implemented)。实例可修改属性在实例层表达并保存；模板默认值不得覆盖创建后、修改后或恢复后的有效属性。已有实例缺少必要数据时应明确报告不完整／不支持，或走显式迁移，不能静默套模板掩盖缺口。

这是逻辑完整性，不要求把所有字段放进 objects 表，允许按领域组织 RAM 运行表示，不要求大型全字段对象或第二套可独立写状态。各能力／领域记录继续拥有自己的数据，通过统一实例读取入口按实例 ID 组合完整有效能力数据；该入口是受控读取职责，不是另一个独立可写副本。Service 负责行为和协调，不各自回查 Package 填字段。配置与状态的版本、必要关联及读取一致性由所属领域与共享事务保障，缓存仍遵循 §2.3；统一读取入口的具体类名、持久字段和 API 均未在本轮冻结。

本要求覆盖 Session 创建、首次进入场景的延迟初始化、运行中新生成的物体／物品／角色、存档恢复／进程重启及显式实例升级／迁移。尚未创建的实例首次创建时可用 Package；已经存在的实例恢复已保存的有效配置、状态和关联，不能重新应用初始化模板。版本化实例记录须足以支持一致恢复和运行时读取，迁移通过既有受控写入／共同提交，不重置既有事实或绕过幂等、OCC、RNG、事件证据和 Outbox。

Package 仍可用于初始创建、来源追踪、Session 绑定检查、审计及显式迁移；不禁止全部 Package 访问，也不要求将 RE 程序或整套通用规则素材复制到每个实例。通用规则和明确绑定的行为实现可通过固定版本引用调用，但引用不能代替本应由实例持有的有效属性与状态（§4.3）。静态导航模板等 Package 数据的只读复用继续有效；Package 查找索引只能加速静态定义查找，不能修复实例能力字段不完整。运行时物体操作须先确定实例数据所有权和统一读取入口，再考虑索引／缓存优化。

**运行加载补充（2026-10-21）：** 首次创建仍从固定 Package 完整实例化并持久提交；已有实例从持久事实加载／恢复，加载成功后按 §2.3 统一由 RAM 服务查询、检查和 Snapshot 构建，不每次回查数据库装配。缺字段仍拒绝／显式迁移，不从 Package 默认值补齐。冷数据补入遵守一致版本与受控发布，实例化、加载内存与玩家实际入场是不同事件。

## 3. Player / DM Planner / NPC Agent → State Machine：TypedCommand（P0）

C02 目标同步／异步入口应共用操作集合、授权和提交语义；当前 async 只支持特定 RE 路径，不简单把全部命令转发该入口。实际 Python 调用显式 package 时必须验证与 Session 固定绑定相同，调用者不能替换规则／冒险配置。

### 3.1 统一公开入口与命令信封 `[DECIDED; PROPOSED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

所有外部普通游戏命令只经公开逻辑入口 **submit_command(TypedCommand)**，按 command_type 分派 world.* / rules.* / combat.* 的负责领域；此入口不要求中心处理器理解每项规则。create_session、NPC Evaluation 提交、只读查询和回执查询保留独立生命周期。不要求额外公开命令入口；可信内部协作按 §0.3 使用受控类型接口和同一事务上下文，不重复外部信封包装。公开目标与当前实现边界仍按 §1 记录。

以下为原创合成示例，候选消息版本与字段 Schema 尚未实现：

```yaml
schema_version: module-contracts/0.2
session_id: ses.example
command_id: cmd.example.001
principal_id: npc-agent:guard-a        # 可信认证环境绑定，不能采信 LLM 自报
actor_id: npc:guard-a
command_type: combat.intent
expected_world_version: 27
payload:
  intent_type: attack
  target_id: char:hero
  stat_block_action_id: spear
```

信封使用 session_id / command_id、可信 principal_id、expected_world_version、command_type 与强类型 payload；actor_id 按操作分支验证。NPC 控制策略的 controller.kind 与命令信封无关，保留其原语义。command_type 是公开命令路由，SM 将需规则计算的内容适配为 operation_kind / 强类型 payload；二者不是两套幂等键，不混同 payload.intent_type 的动作子类判别。

**AP-15 [DECIDED]：** TypedCommand 与 RuleEvaluationRequest 均建议采用按具体操作类型区分的强类型联合，而不是把 actor_id 全局改为无约束 Optional：

| 操作分支 | Actor 与来源校验 |
|---|---|
| 实际 Actor 行动（如 combat.intent、角色交互/检定） | 必须有真实 actor_id；验证 principal 的控制权、行动身份及目标，不能省略或伪造 NPC |
| 受信系统/世界事件发起的 combat.start、rules.effect 等 | 可以没有实际行动 Actor；仍必须验证可信 principal、机械来源、目标及允许操作范围，不因此豁免 Snapshot / RulesetBinding / RNG 校验 |

分支类型、source_ref、来源权限及具体字段编码 **[PROPOSED / OPEN; NOT IMPLEMENTED]**；ID 本身不能证明来源可信，也不固定虚构的环境 Actor。新操作须经显式 Schema / 允许列表审阅。

**最低权限规则：** NPC Agent 只能控制绑定 NPC、使用其授权投影中的目标并提出有限 Intent。DM Planner 不伪造提交结果；Narrator 没有写权限。Engine 只接收 SM 验证的可信调用/状态，不直接采信 Prompt 输出。

### 3.2 三个验证领域与 GM Adjudication `[DECIDED]`

| 领域 | 责任 |
|---|---|
| DM Planner | 根据主持范围内完整授权 DMView / 适用规则理解情境，决定是否需要检定，提出能力/技能、DC、成功/失败后果及可追溯依据 |
| 领域模块 / 共享提交设施 | 领域检查结构、引用、世界前提及数据生命周期；提交设施检查身份授权、版本/原值、请求关联、幂等和原子性（§6.5）；不证明自然语言语义正确，不新增语义审核 LLM |
| Rule Engine | 验证 D&D 机械合法性，计算骰点、豁免、伤害、资源和效果；不替 DM 决定剧情情境，也不提交权威状态 |

优先采用规则或 Package 已规定的机制/DC；未规定时允许可信 GM 裁决，但能力/技能、DC、成功/失败后果必须在掷骰前确定并可追溯。SM 只验证能确定性检查的内容，机械规则交 Engine；依据记录不要求模型私有推理链。GM 裁决复用 TypedCommand / 受限 payload，不增加 Adjudication API。Planner 不能提交骰点/伤害或任意状态修改，也不能替独立 NPC Agent 决定私人意图。

### 3.3 有限动态世界操作 `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

Package 是静态初始定义，不是 DM 创造力的上限。Planner 可提出原先不存在的简单 Object、World Fact、Scene Connection，通过 SM 已支持的封闭 Typed World Operations 验证并持久化到 Runtime World State，不修改 Package。已有对象优先引用可信 GM View 的 ID；新对象由 SM 分配稳定身份，提交后经既有授权查询可见，重试通过原回执返回同一结果。

叙事描述、未提交创造提议和已提交世界事实必须分开；不信任 LLM 自报对象存在或状态改变。候选 Object / Connection 等领域操作可随实际 MVP 场景审阅扩展，但类型、字段、目标和不变量受限；不能借 World Fact 写 HP/资源/RNG，禁止任意 JSON Patch、SQL、脚本或开放式状态覆盖。完整操作字段、动态复杂 Scene / 战斗地形生成 **[OPEN]**，本轮不冻结或实现，也不新增 World Creation Agent。

此限制针对普通命令绕过可信领域边界，不禁止 §3.6 所述经过验证和受控启用的 Session 扩展。

### 3.4 Conditional World Effect Proposal `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

Planner 可在 TypedCommand 中提出受限的候选成功条件及对应世界变化，尽量复用 Adventure Package 的声明式 Condition / Effect 语义，不建第二套 Event Engine。世界领域根据可信规则结果与权威事实判定条件，经负责接口准备允许效果；LLM 自报成功不能满足条件。提议的封装字段、结果引用和条件/效果子类型 **[OPEN]**。

需要机械计算时复用 §4–§6 的 RuleEvaluationRequest / Result；尽可能在掷骰前确认操作及后果均有受支持的表达路径，不先掷骰再用自由文本补写状态。一次操作提交前能够完整求值时，各领域经共享事务提交世界效果、机械 Delta、RNG、正式事件、CommandReceipt 和 Outbox；已提交事件才引发的后续效果沿用 §10 的可靠幂等独立命令，不虚构跨已提交事务原子性。

Planner 可随 Action Intent 提出按可能执行结果分类的候选 observable_signals，预定义事件/标准规则行为优先复用模板。SM 根据可信结构化执行结果选择匹配 Signals，并与实际事件原子提交，不接受 LLM 自报成功；Schema / 条件字段仍 [PROPOSED / OPEN]，具体边界见 §7.1，不增加 Event Generation Agent。

### 3.5 授权视图、反馈与叙事 `[DECIDED]`

C21 展示端只读取 PlayerView／NarratorView、授权已提交变化、回执和合法选择提示；本地展示缓存不是事实来源，不能拖动 Token 直接写坐标。客观 Quest 进度／奖励复用受控操作、幂等及共享事务，奖励采用一次；NPC Goal／Belief 不自动完成 Quest。新增内容通过受支持 Schema 验证并显式启用；代码能力独立测试／固定版本／部署，Coding Agent 生成物不自动可信。

复用 get_scene_view 等既有查询入口，按可信主体投影 DMView / PlayerView / NPCView：Planner 获取主持范围内完整授权 GM 信息；Player / Narrator 只读玩家可知事实；NPC 通过独立 NPCView / Perception 获取自身授权信息；get_scene_view 面向 NPC 时也必须经过 NPC Perception / 授权投影，不能绕过感知权限（DOC-02）。动态创建且已提交的对象进入后续授权查询，未提交对象或隐藏信息不能泄漏；不新增冗余查询服务。

反馈映射沿用 §5 / §6 / §11：rejected 是规则/世界拒绝，unsupported 是不支持的能力/操作原因，合法机械失败可为 accepted 并提交实际成本；version_conflict 对应 CommandReceipt.conflict，needs_choice 对应 pending_choice。RuleEvaluationResult 四态不变，CommandReceipt 不增加 unsupported 状态，能力不支持可用 rejected + 授权结构化原因表达。Schema/运行时/传输错误与规则拒绝分开，提交未知先查询 (session_id, command_id)。结构化原因经权限过滤供 Planner 使用，拒绝不会强制再调 LLM；重试/重规划按 §2.2。

Narrator 保持游戏世界内的沉浸叙事，不把内部 API、Schema 或 unsupported 错误直接作为玩家叙事。但能力限制不能成为“墙壁永久不可摧毁”“骰点已失败”或“世界已改变”的无依据世界事实；Planner 可以提出合理情境解释，权威效果仍须正式提交。必要的能力/运行时提示由文字入口以可理解方式表达，不伪造机械结果。Narrator 没有写权限。

### 3.6 受控动态能力与 Session 扩展 [DECIDED; OPEN; NOT IMPLEMENTED]

运行时创建内容、组合已有机制、安装 NPC 行为是目标能力。区分配置/模板更新、已有能力组合和真正新增底层机制；已有能力优先受控组合，不要求每个自由行动都生成代码。Coding Agent 是可选代码生成手段，不是这些能力或早期 Agentic 验证的必需前置条件。

各类扩展须校验定义、权限与资源预算；新增代码还须通过适用测试、受限执行与版本化受控启用。任意 Python / JavaScript 回调、人工审批或 reload 本身均不构成安全热部署；目标是准备完成后在安全边界启用，不是任意代码即时生效。本批不实现完整扩展系统。

固定 Adventure Package 仍是 Session 初始基线。运行中新增对象、机制或行为须作为获准的 Session 扩展或运行态变化，不悄悄回写固定包或改变历史执行依赖的定义。扩展来源/版本/启用记录、在途操作版本绑定、行为状态迁移、失败隔离与恢复协议均 [OPEN]；回滚扩展版本不自动撤销已提交游戏事实。不得借扩展让 Host 成为权威状态所有者。

### 3.7 可组合世界机制 [DECIDED; PROPOSED; OPEN; NOT IMPLEMENTED]

**[DECIDED]** 游戏核心应以可复用动作、对象属性与关系表达可执行能力，并让提交后的变化被移动、感知、Policy 等后续机制实际消费；描述文字或不被机制读取的标记不能冒充实现。允许合理的任务/剧情 Flag，但不以每个对象专用命令或不透明 Flag 替代可组合物理/行为语义；也不开放任意 JSON Patch、SQL 或越权属性写入。

**[PROPOSED; NOT IMPLEMENTED]** 原创候选：移动物体阻塞通道 → 移动/感知/Policy 按各自可信语义响应 → 移除障碍后相应限制解除（已发生后果不撤销）。LLM 可把无专用剧情分支的合理行动映射为已有能力组合；不支持或证据不足时明确反馈，不虚构执行结果。不同感官/规则不能共用未经验证的“阻塞即全不可感知”假设。

当前覆盖范围须结合真实 SM / RE 依赖审计；对象关系、动作/活动生命周期、影响传播与保存映射 [OPEN]，此处不冻结 Schema 或新增执行 API。候选场景、成熟机制来源与早期 Agentic 验证证据统一见演进计划 §4–§8。

## 4. Combat Handler / 领域 → Rule Engine：RuleEvaluationRequest（P0）

本章结构决策为 `[DECIDED]`；下列目标类型与示例消息为 **Target Architecture Contract `[PROPOSED]`**，未冻结部分仍 `[NOT IMPLEMENTED]`。同名的 **Current Implemented Interface** 已有受限实现，版本、字段、状态和迁移差异统一见 §1.6；不得从本章目标示例推断当前运行时 ABI。以下 YAML 展示字段关系，尖括号为类型/数据占位，不是可执行 Fixture；`module-contracts/0.2` 是本轮候选消息版本，与文档版本分开。

**最终执行架构 `[DECIDED]`：**

```text
StateSnapshot + Typed Intent + Pinned RulesetBinding + Explicit RNGContext
    -> Stateless Rule Evaluation Engine
    -> RuleEvaluationResult（未提交）
```

Rule Engine 负责动作机械合法性、Attack、Damage、Check、Save、Action Economy、Movement、Spell、Effect、Reaction 等受支持规则的确定性计算，返回四态结果及适用的封闭 Typed StateDelta、ProposedEvents、RNGTransition、ReadSet。Combat Handler / 相关领域组织经验证的显式输入和结果应用，由共享设施提交；不重新计算 D&D 规则，不创建、管理或恢复 Legacy Engine 内部权威对象。Handler 有持久流程状态与 RE 无隐藏跨请求权威状态并不冲突。

**求值粒度 `[DECIDED]`：** 一次请求尽量完成该 Intent 下所有可连续结算的规则效果，包括已授权自动触发、预声明 Reaction 与连带资源/状态变化；不能按每条审计事件拆请求并等待 Planner / JEV / EVA。真正需要中途选择时按 §8 Interrupt / Continuation 目标暂停。Episode 可跨多个请求，不要求把整场战斗塞进一次求值。

**当前状态与审计分离 `[DECIDED; PARTIALLY IMPLEMENTED]`：** 相关领域提供完整的必要当前机械事实；每轮/每回合使用标记、Reaction 窗口、资源支付状态、效果来源/时钟和关键时间点是当前机械状态，由可信规则路径计算、随 Delta 共同更新。不另建一份“精简历史日志”重复这些事实。RE `/17` 的普通求值／Availability 已不读取历史 event_log，SM 也已采用 history-free Snapshot（§1.6）；新增规则仍须逐项证明当前依赖齐全。本次必要结算结果和有序 ProposedEvents 仍是候选结果，提交后可作为审计/Episode 证据按需保留，不自动回灌每次请求。独立重放可以使用保留的历史、检查点、版本、命令/选择与 RNG 证据。历史 RE-HIST-01 的完成部分按 §1.6／RE history-free 文档理解，尚存消费者仍须先审计真实读者、补齐必要状态再移除耦合；不授权将 event_log 置空、删历史表或删除全部 proposed_events。

**最终受支持规则的执行路径不得依赖 Legacy `_LiveCombat`、`CombatHandle`、`_REGISTRY` 或 Stateful Combat Orchestrator**，包括在每次求值中重建旧对象、调用旧执行器后导出 Delta 的永久适配方案。允许单次求值的局部变量、临时计算对象、派生索引或必要上下文；这些对象只服务于计算，不能使旧 `_LiveCombat` 完整内部结构成为长期前提。可以复用 Nat20 的 D&D 算法、Resolver 和声明式规则数据，重构其状态访问与执行依赖，无须重写已经正确的规则公式。

**运行输入边界补充（2026-10-21）[DECIDED]：** 已加载且有效的必要机械事实、配置与版本从 Session RAM 一致读取范围组装；检查候选中间阶段则使用隔离候选范围。不得为构建 RE Snapshot 重读同批 SQL／聚合 JSON。只加载真实依赖，仍覆盖完整必要机械闭包；固定输入不得泄漏可变世界引用，即使进程内调用或共享结构也须证明旧输入隔离。RE 不读取 SM 数据库、不修改共享运行对象，不创建／恢复跨请求世界或战斗权威。RE 返回未提交 typed result、Delta、事件与 RNG transition，SM 验证并按 §6 持久提交／发布。FrozenRuleset、既有绑定、公开 DTO／Schema 版本保持；此消费者目标不恢复 Legacy Stateful Engine。完整 RAM 接入 [NOT IMPLEMENTED]。

### 4.1 请求结构 `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

```yaml
schema_version: module-contracts/0.2
session_id: ses.example
command_id: cmd.example.001
actor_id: npc:guard-a
operation_kind: combat.intent
ruleset_binding:
  ruleset_id: dnd-2024-srd-5.2.1
  data_revision: sha256:<effective-rules-data-hash>
  evaluator_version: <code-or-build-revision>
state_snapshot:
  snapshot_kind: combat
  snapshot_schema_version: combat-snapshot/0.1
  world_version: 27
  character_states: <complete CharacterState records for relevant actors>
  effect_states: <complete relevant EffectState records>
  scene_state: <SceneMechanicalState including required objects and topology>
  combat_state: <CombatState including combat_id roster initiative turn and budgets>
rng_context:
  algorithm: <PRNG algorithm and encoding version; OPEN>
  stream_id: main
  stream_version: 12
  state: <explicit serialized RNG state; encoding OPEN>
payload:
  intent_type: attack
  target_id: char:hero
  stat_block_action_id: spear
```

该 combat.intent 示例分支的顶层字段均 Required。共同字段的 Required 约束不变；actor_id 是否必填按 operation_kind 的具体强类型分支决定（AP-15，§3.1），Actor 行动必须保留真实 actor_id。受信系统/世界事件分支可无行动 Actor，但 SM 必须核验 principal、机械来源、目标和范围，并以可信内部调用上下文/受控来源关联交 Engine 校验；source_ref 与来源权限编码仍 [PROPOSED / OPEN]，不在本轮冻结新字段。Handler 保留 `(session_id, command_id)` 关联，从 Session / 负责领域与共享设施取得固定绑定、权威事实及显式 RNGContext。Engine 不接受 Agent 自报快照/身份，不依赖任何 Legacy `_LiveCombat` 对象、CombatHandle、注册表或 Stateful Orchestrator，也不读取进程全局随机状态。标准 Required / Optional、类型与联合判别校验失败属于 Schema / 输入错误，不伪装为规则拒绝。

`operation_kind` 选择操作级 Payload Schema（如 CombatIntentPayload、AbilityCheckPayload、SavePayload、RestPayload）；`payload` 必须是对应强类型数据。CombatIntentPayload 内的 `intent_type` 区分 attack / cast / move 等动作子类；两层判别职责不同，不能合并，也不接受任意字典或自然语言代替 Payload。具体操作枚举与字段覆盖按已支持规则审阅，不因示例推定全部已实现。

### 4.2 StateSnapshot：CombatSnapshot / NonCombatSnapshot `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

StateSnapshot 是 **CombatSnapshot / NonCombatSnapshot 两种情境**的判别联合，均只读、版本化，共享必要的 CharacterState、InventoryState、EquipmentState、EffectState、SceneMechanicalState 等类型化机械状态组件。Inventory / Equipment / Effect 是组合组件，不按每一种规则操作新增 Snapshot 情境；组件的具体字段与组合编码仍 [PROPOSED / OPEN]。RNGContext 是独立输入，不嵌入 Snapshot。

| Schema | Required | Optional（仅按对应 Schema） |
|---|---|---|
| CombatSnapshot（snapshot_kind=combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state、combat_state | component_versions / 显式 read_set 等版本辅助信息 |
| NonCombatSnapshot（snapshot_kind=non_combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state | component_versions / 显式 read_set 等版本辅助信息；不含 combat_state |

`character_states` / `effect_states` 的集合元素使用相同基础 Schema，库存等组件按基础类型引用/组合。无相关效果时合法空集合仍须明确提供；可选字段的省略/null 规则由普通 Schema 定义，不引入额外缺失状态分类、缺失原因枚举或按 Intent 动态裁剪字段的机制。

当前目标 Snapshot 由负责领域组装，可按相关实体与 Scene 限定集合范围，但每个纳入实体的机械状态必须完整，并保留规则依赖闭包，包括会影响它的其他实体、来源、区域与生命周期状态。不能因本次只攻击而省去 Required 的反应、装备或效果字段；不能把非战斗检定伪造成 Combat。缺 Required 字段报 Schema 错误，尚未支持的规则路径显式 unsupported，不用默认值或隐藏 Engine 状态补齐。

无状态 RE 不要求每次搬运整个世界、深拷贝全部对象或通过网络调用。运行时复用的共同原则已在 §2.3 确定，按需读取的具体接口仍待落实；输入须包含操作真正依赖的完整事实。新读取接口/依赖表达 `[OPEN]`，不直接删除 Snapshot / StateDelta 结构与不变量校验，不将任意整份 Snapshot 覆盖数据库作为本次决定。当前受支持公开接口仍按 §1 的实际实现说明；优化须验证缓存失效、重启恢复及回滚后缓存一致性，未测得性能收益。

§7 的 Event Evidence 只保存感知所需历史字段；其 Signal-scoped 裁剪原则不能用于裁剪本节机械 Snapshot 的 Required 字段或规则依赖闭包。二者用途和完整性标准不同，Event Evidence 不能直接替代 CombatSnapshot / NonCombatSnapshot。

| 基础领域 | 完整机械状态必须覆盖的语义（具体字段映射仍待实施核对） |
|---|---|
| CharacterState / InventoryState / EquipmentState | HP / Temp HP / Death Saves、能力与规则特性、资源池/法术位、库存/数量、装备、动作来源及有限使用次数 |
| CombatState / 关联实体投影 | Combatant roster、Initiative、Round / Turn / Phase、Action Economy、Reaction、移动预算、当前机械使用状态；位置/Reach/Topology 引用负责实体，不另存当前权威 |
| EffectState | Conditions、Concentration、Active Effects、来源与目标、持续时间、持续区域、过期/撤销条件，战斗内外复用 |
| SceneMechanicalState | 必需场景、对象、障碍、光照/遮蔽、环境规则与关系及版本；不传入无关剧情秘密 |
| Pending state（适用时） | 已支持的选择/活动引用与版本；复杂中途 Reaction Continuation 仍 [OPEN]（§8） |

该表不是现成代码类型。每条受支持规则须证明 Snapshot 覆盖其完整状态依赖闭包，包括跨实体、效果来源、Reaction、持续区域和生命周期账本；不能仅迁移 HP / Turn。历史 sidecar 审阅只是遗漏检查的证据，不要求目标 Snapshot 或临时计算上下文复制旧 `_LiveCombat` 的结构。

### 4.3 RulesetBinding 与规则数据复用 `[DECIDED]`

RulesetBinding 的 Required 字段为 `ruleset_id`、`data_revision`、`evaluator_version`。SM 从 Session 固定配置提供；Engine 在求值前验证三者与实际加载规则/数据/求值器匹配，不匹配报独立绑定错误并禁止继续求值，不能静默换规则版本。

`data_revision` 必须区分**实际生效的规则内容**，包括适用的 Homebrew / 数据覆盖及组合；不能只用基础 SRD 名称代替生效内容修订。数据包发布版本、素材内容摘要、ruleset_id 和 evaluator_version 分别标识发布、有效内容、规则集合及求值实现，不能混为一谈。具体跨模块摘要／组合编码仍 [OPEN]，不虚构冻结 API；固定 RNG seed 不能替代绑定。

**加载层要求 `[DECIDED]`；固定素材复用 `[IMPLEMENTED]`（§1.6）：** RE 的 FrozenAssetLoader 捕获最终有效的十一类素材，FrozenRuleset 在冻结时校验身份、typed accessor 和非空 spell UUID 冲突，并由 `_compute_binding()` 对脱离来源的数据计算一次绑定。`freeze_ruleset()`／`get_default_ruleset()` 返回正式固定对象，`ruleset_binding()`／`verify_ruleset()` 对精确 FrozenRuleset 类型比较可信三字段，不重复枚举或摘要。公开 getter 返回防御性深拷贝，不能承诺同一对象或零分配。可变／自定义原始 Loader 仍走完整摘要兼容路径；自定义来源在冻结期间须稳定，修改后必须重新冻结。SM 在 Runtime 装配时选定同一个固定 Loader，供初始化、求值、Availability 与绑定校验复用；不按请求冻结，不静默重绑既有 Session。§1.4 的全量校验描述只适用于其历史 pin。

SM 保存 Session 固定绑定并核对 RE 身份，不另建一套规则素材管理系统。运行中 Session 不静默切换规则、基础素材或引擎版本，升级走显式迁移流程，具体流程仍 [OPEN]。物品实例属性、角色状态等游戏事实由所属领域更新，不等于修改基础模板版本；读取／重载模板默认值不得覆盖实例当前有效属性。只读素材和候选副本遵循 §2.3。

C03 的 CapabilityManifest 是可由现有允许列表派生的轻量逻辑查询，不新增数据库：固定规则／Package、消息版本、命令／Delta 家族、受测组合 profile、非战斗阶段证据／战斗聚合及恢复能力。系统能力取领域输入、RE 受测规则、Adapter 采用、该路径感知必需依据与恢复能力的交集；可解析 Schema 不等于支持。战斗不以逐动作视线证据为准入条件，机械依赖仍须完整。

### 4.4 Action Availability Query `[DECIDED; PARTIALLY IMPLEMENTED]`

当前基础战斗查询已实现 `engine-availability/13`，实际 Request／Result、SM 授权包装及限制见 §1.6。下列是 **Target Architecture Contract `[PROPOSED]`** 的逻辑形状，不能当成当前函数签名；通用操作联合、全部目标枚举和 CapabilityManifest 仍待实现／冻结。独立只读查询供 UI / Agent Planning 查看候选行动的当前可用性，复用明确 Snapshot / RulesetBinding 与按 operation_kind 类型化的 payload：

```text
query_action_availability(session_id, actor_id, operation_kind,
                          payload, state_snapshot, ruleset_binding)
  -> ActionAvailabilityResult(status=available | unavailable | unknown,
                              input_world_version, permitted_reasons)
```

SM 负责授权并构建完整机械快照；Engine 做只读规则查询，SM 向 UI/Agent 返回经权限过滤的结果/原因，不暴露隐藏实体或不可知限制。接口名称与具体查询字段仍 Proposed。

查询不需要 command_id / RNGContext，不掷骰、不修改状态、不生成 StateDelta / ProposedEvents、不产生 CommandReceipt。unknown 表示查询能力不足或当前无法确定，不等于执行合法。available 仅针对查询时快照，不预留资源、不保证后续执行成功；正式 Typed Command 必须重新鉴权、取 Snapshot / RNG 并验证。完整技能列表和全量目标枚举不属于本轮 P0 必须实现功能。

**[DECIDED] 实施顺序**：该查询不依赖 Visual Presentation，可与早期 Stateless Rule Evaluation 实现同步开发，先覆盖基础战斗操作的只读合法性判断并与正式求值共享同一规则逻辑，避免第二套规则系统。当前文字 MVP 不强制调用此接口；视觉 UI 仍为 Post-MVP。已有基础攻击共享 preflight 的查询及无写入测试（§1.6）；其他操作的通用 Availability 仍不是当前支持承诺。

## 5. Rule Engine → 负责领域：RuleEvaluationResult（P0）

### 5.1 四种结果与字段约束 `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

```yaml
schema_version: module-contracts/0.2
session_id: ses.example
command_id: cmd.example.001
input_world_version: 27
input_ruleset_binding:
  ruleset_id: dnd-2024-srd-5.2.1
  data_revision: sha256:<effective-rules-data-hash>
  evaluator_version: <code-or-build-revision>
status: accepted
read_set:
  - ref: actor:npc:guard-a
    version: 27
  - ref: actor:char:hero
    version: 27
state_delta:
  operations:
    - kind: combat.action_budget_update
      actor_id: npc:guard-a
      action_remaining: 0
    - kind: actor.hp_delta
      target_id: char:hero
      amount: -4
  preconditions: []
proposed_events:
  - event_type: combat.attack_resolved
    actor_id: npc:guard-a
    target_ids: [char:hero]
    payload: <typed mechanical event details>
rng_transition:
  stream_id: main
  input_version: 12
  next_state: <successor explicit RNG state; encoding OPEN>
choice: null
error: null
```

共同 Required 字段为 schema_version、session_id、command_id、input_world_version、input_ruleset_binding、status、read_set，以及下表的 state_delta、proposed_events、rng_transition、choice、error。共同字段必须匹配请求/快照，read_set 描述实际依赖实体与版本，不是让 Engine 扩大授权范围；StateDelta 的目标必须在批准的写范围内。空集合与 null 按下表明确区分：

| status | state_delta | proposed_events | rng_transition | choice / error |
|---|---|---|---|---|
| accepted | 完整 Typed StateDelta，operations 可合法为空 | 有序候选机械事件列表，可为空 | 必须提供，可与输入状态相同 | choice=null；error=null |
| rejected | null | [] | null | choice=null；error 必须含结构化规则拒绝码/原因 |
| needs_choice | null | [] | null | choice 必须为结构化前置选择；error=null |
| unsupported | null | [] | null | choice=null；error 必须含不支持的能力/规则码 |

- accepted 是规则求值完成且可提交，**不代表命中、达到目的或已经提交**。合法攻击未命中、豁免成功、被反制且已经合法支付资源的施法等可为 accepted，Delta / 事件 / RNG 必须完整表达实际机械结果与成本。
- rejected 是规则允许的安全拒绝，不提交机械变化/事件/RNG。合法失败仍有成本或效果时必须用 accepted，不能借 rejected 丢掉已发生的支付。
- 本表 needs_choice 仅描述 §8.1 的前置选择候选分支；不提交部分伤害、资源或 RNG。§8.3 的中途 Interrupt 尚未映射为正式 Result ABI，不能直接套用此前置选择形状或私增正式 status。
- unsupported 明确能力不支持，禁止静默成功或部分执行。
- 所有机械变化都必须显式包含在可提交结果中，不存在需要另取 Engine 私有状态的隐含副作用；失败或尚未提交的求值不会改变权威状态。
- **Schema / 输入错误、RulesetBinding 不匹配、运行时异常、传输故障在四种规则结果之外处理**，使用独立错误类别/传输反馈（§11），不能改报 rejected，也不新增第五种 RuleEvaluationResult status。失败响应不携带可提交 Delta / RNG；提交状态未知仍由 SM 按命令键查持久记录。

**C06 StageFacts 与兼容：** 历史 v0.4 基线 SM `/23` 的限制保留在原 Review；当前 SM 固定 a011eba，Evaluation `/24`、StageFacts `/2`，严格重验 DTO 并调用 `verify_request()`。accepted 必带 complete 或 uncovered 阶段，其他状态为显式 null。complete 仅覆盖受审的参与者机械路径，不是完整世界或感知证据；uncovered 不得补造。StageFacts 不再次应用 HP／资源／位置，不自动触发 Signal／OB／JEV／EVA。当前 `_apply_dnd_changes` 仍是受限 actor／combat／ledger／XP 路径，不能删除白名单冒充通用采用；见 §1.6。

### 5.2 StateDelta：封闭 Typed Operation Union `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

StateDelta.operations 必须是**封闭的 Typed Operation Union**，每个 kind 有固定强类型字段、目标/所有者与约束；未知 kind 或额外未允许字段拒绝。具体 Operation 名称/完整字段仍 Proposed，不能用任意 JSON Patch、状态路径、SQL 或**整份权威 Snapshot 覆盖**替代。

| 类别 | 候选 Typed Operation | 关键检查 |
|---|---|---|
| HP / 死亡 | actor.hp_delta、actor.temp_hp_set、actor.death_state_update | 目标、边界及规则结果关联 |
| 资源 | resource.consume / resource.restore | 显式 owner_id / resource_id、数量与归属 |
| 库存 | inventory.consume / inventory.transfer / inventory.item_update | 唯一物品/堆叠、来源和目标、装备/库存一致性 |
| 位置 | actor.position_update | 场景/网格/占位与相关状态一致 |
| 战斗初始化 | combat.create（候选，[PROPOSED; NOT IMPLEMENTED]） | 仅建立受限类型化 Combat 组件；使用相关 NonCombatSnapshot，完整字段/映射 [OPEN]，见 §10 |
| 回合 / Action Economy | combat.turn_update、combat.action_budget_update | Round / Turn / Phase、行动/附赠/移动预算及当前 Actor |
| Condition / Effect / Concentration | condition.update、effect.upsert / effect.expire、concentration.update | 类型化生命周期、来源、目标、引用完整性 |
| Reaction / Limited Uses | combat.reaction_state_update、actor.limited_use_update | 反应资格/次数、Recharge、Legendary、特性/物品 Charges |
| 复杂领域组件 | 受限的类型化组件 create / update / remove（组件种类封闭） | 仅修改该类组件，固定字段/ID/来源/版本及不变量，不借组件更新覆盖整个 Actor / Snapshot |

一次求值的多目标、多 Activity、资源支付及所有连带变化必须完整表达为有序操作，构成**一个不可分割的提交单元**；任一校验失败全部不写。各领域检查归属、引用和数据不变量，共享提交设施检查权限、版本/原值、读写范围及请求关联（§6.5），不重算 D&D 伤害/成本。复杂 Effect / Reaction 字段 [OPEN]，候选名不是冻结 API。Quest / 剧情秘密仍由负责世界领域处理，不授权 Engine 任意改写。

首个黄金用例仍为：同一 Actor 消耗药水、恢复 HP、支付行动预算并生成事件，由库存/角色/战斗等负责接口在同一共享事务全部成功或全部失败。

### 5.3 ProposedEvents → CommittedWorldEvent `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

Engine 返回有序、类型化的候选机械事件，不分配权威 event_id / event_seq。负责领域保留机械审计／恢复与已提交来源；非战斗按受审真实阶段／Signals 形成外显事件，战斗仅在 Turn／Round 边界聚合并固定过滤依据，不能将每条 Mechanical Audit 自动升级为 WorldEvent 或独立 OB。共享提交设施在提交各领域 StateDelta、RNG、CommandReceipt、Outbox 的**同一事务**内分配正式事件身份/序号并保存记录；COMMIT 成功后才成为 CommittedWorldEvent。具体分类/阶段 ABI [OPEN; NOT IMPLEMENTED]，不据事件重算规则。

正式事件保留 `(session_id, source_command_id)` 与命令来源；这里的 source_command_id 是事件关联字段，不是额外的规则操作标识。SM 直接应用并校验 Typed Delta，不根据 ProposedEvents 再计算 HP、伤害或资源扣减。NPC Perception、DM Narration、UI 只能获取经授权的事件/回执投影，不直接获取候选事件或全量隐藏机械细节。

## 6. 共享 Atomic Commit 与 CommandReceipt（P0）

### 6.1 执行时序 `[DECIDED; PARTIALLY IMPLEMENTED]`

既有短事务、绑定／OCC／回执／RNG 为部分基础；新增统一候选与提交后 RAM 发布整体 **[NOT IMPLEMENTED]**，当前入口见 §1.8。以下为目标逻辑流程，不冻结 API。

```text
Command / trusted system work -> authorization + original idempotency-key lookup
-> one consistent Session RAM read scope (load cold persisted instances if needed)
-> fixed required input + independent RNGContext -> RE outside write/commit lock
-> isolated candidate: apply all domain changes, inspect intermediate stages/evidence
-> unique Session/world mutation coordinator + one short SQLite transaction
   -> recheck authorization, task eligibility, idempotency, binding, versions/original values
   -> domain admission for complete affected closure, including linked candidate changes
   -> incrementally persist domain facts + versions + RNG + required events/stage evidence
   -> persist Receipt + Outbox + reliable work/progress
-> SQLite COMMIT succeeds (unknown outcome -> reconcile original durable receipt)
-> publish the corresponding final candidate as current RAM; maintain indexes/dependencies
   and update/invalidate affected derived caches; publication failure -> pause/rebuild
-> current version ready -> admit later current-state operations, return success
   and construct only permitted projections from that version
```

持久写入和运行发布范围由真实变化决定，不每条命令保存、重载或扫描整个世界，不要求全 Session 拷贝。已开始的固定旧读取继续表示旧版本；新当前态操作不能在 SQL 已提交而 RAM 尚未就绪时读落后状态。对外成功必须等待对应内存版本就绪；Receipt 在数据库已提交而发布故障时仍是真实持久结果，不能改称未提交失败。Outbox 投递在提交后可靠重试；需要当前投影的消费者也须等待对应版本可读。

保留 accepted 合法尝试失败（可能支付成本）、rejected、unsupported、conflict、pending_choice 与 Schema／传输／存储故障区别。非 accepted 不应用未获准的部分机械 Delta／RNG／候选事件；获准拒绝记录、任务元数据或持久选择进度确有变化时同样经过提交／发布边界。不能把所有非成功响应解释成无状态变化；Continuation 前缀语义仍按 §8 OPEN 边界处理。

非战斗阶段证据来自实际候选阶段，不能由结束态补造；战斗不逐机械 Event 建感知证据，Turn／Round 关闭后独立可靠聚合，遵守 §7。异步求值返回后仍重验版本、权限、绑定、资格及前提；过期输入返回冲突或有界重新准备，不能套旧 Delta。单写入者不取消 OCC／幂等，提交顺序不代替先攻／争抢规则。world_version／npc_state_version 保留，细粒度依赖版本、仅元数据提交版本策略与锁实现 OPEN。

### 6.2 CommandReceipt `[DECIDED; PROPOSED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

统一使用 `(session_id, command_id)` 关联与查询命令结果；CommandReceipt 是结构化持久结果，不新增独立回执服务、回执 ID、二次 ACK 或独立验证流程。Fingerprint 防止同命令键被不同请求复用。

```yaml
schema_version: module-contracts/0.2
session_id: ses.example
command_id: cmd.example.001
command_fingerprint: sha256:<canonical-request-hash>
status: committed             # committed | rejected | conflict | pending_choice
world_version_before: 27
world_version_after: 28
committed_event_ids: [evt.001]
rng_version_after: 13
result_ref: result.cmd.example.001
```

上述是 committed 分支字段关系。committed 必须与全部状态/RNG/正式事件/Outbox 同事务落盘，数据库 COMMIT 后才成为持久结果；正常成功返回及当前投影还须等待对应 RAM 版本发布就绪（§6.1）。rejected / conflict 必须有结构化原因、不含已提交机械事件；pending_choice 仅关联获授权的 PendingOperation。各分支具体类型与字段可空性仍 [OPEN]，不能据此增加另一套回执协议。

RuleEvaluationResult 与 CommandReceipt 的状态不共用枚举：规则 accepted 经成功提交才对应 committed，规则 rejected / unsupported 可对应 rejected 并保留原因，needs_choice 对应 pending_choice；版本冲突对应 conflict。Schema / 异常 / 传输错误保持各自错误类别，不因此增加规则结果状态；尚未确认提交时先查询持久命令记录。

响应丢失用 `get_command_receipt(session_id, command_id)` 查原结果；已提交不因反馈失败回滚，不更换 ID 再执行。只读 Availability Query 不走该回执。world_version 对机械/世界状态变更单调推进；**仅事件/元数据提交是否及如何推进 World Version 为 [OPEN]**，不在本轮用事件序号代替状态版本或冻结空提交策略。

### 6.3 RNGContext / RNGTransition `[DECIDED; PARTIALLY IMPLEMENTED]`

**适用范围：** 本节描述目标契约；同名当前接口并非全部缺失，见 §1.6 的 Current Implemented Interface／Gap。具体目标字段或未接线分支仍按本节标记，不能以当前受限实现代替目标。

- RNGContext 与 StateSnapshot 是独立输入；共享提交设施提供既有权威流/版本，领域提供相应事实。Context 显式包含算法/编码版本、stream_id、stream_version、可恢复 PRNG state；编码细节为 [OPEN]，本轮不改变现有明确的流/版本策略，不允许各 Handler 任意新建随机流。
- Engine 只使用该显式状态在临时求值上下文计算，accepted 必须返回 RNGTransition，绑定输入流/版本及 next_state；不读全局随机源，不由 Engine 推进权威流。
- **只有共享原子提交成功才推进权威 RNG**。规则拒绝、unsupported、前置 needs_choice、冲突、回滚和未提交异常都不推进。合法未命中等 accepted 结果的随机消耗随角色/效果/战斗等全部必要变化一起落盘，候选事件不提前发布。
- 合法且无随机消耗的 accepted 操作允许 next_state 与输入完全相同；不能为了提交而制造随机调用。RNG 流版本如何表达无消耗提交仍 [OPEN]，不据示例固定为 world_version。
- `draws` 可作为审计辅助字段，不强制完整底层随机调用轨迹。确定性验证依据显式前后状态、固定 Payload / Snapshot / RulesetBinding 与可核验机械结果，不把可选 draws 当正确性的唯一证据。
- 一条 Session 流足够作为 MVP 默认；重算从重新读取的当前权威 RNG 开始，已提交命令只返回原 CommandReceipt。不以 seed 单独承诺跨数据/求值器版本 replay。

### 6.4 原子性与故障 `[DECIDED]`

相关领域事实、版本、RNG、必要正式事件／非战斗阶段证据或战斗审计、Receipt、Outbox 与可靠工作在**同一 SQLite 短事务**内增量提交。SQLite 与 RAM **不是跨介质 ACID 事务**；正确性依靠持久提交、受控发布、版本校验、故障暂停及恢复协议，不能声称两者天然原子同步。RE／LLM／外部 I/O 不占写事务或世界提交临界区。

| 故障边界 | 必须行为 |
|---|---|
| 数据库提交前失败／回滚 | 不发布候选 RAM，不推进权威 RNG，不发送候选事件；旧读取及缓存不受污染 |
| COMMIT 结果未知 | 按原 command_id／既有稳定工作键与持久回执对账；不能直接重掷或重复应用；不能确定则暂停 |
| 数据库已提交、RAM 未发布即崩溃 | 重启从已提交事实、RNG、回执及可靠工作恢复，不依赖旧进程对象 |
| 数据库已提交、RAM 发布异常且进程存活 | 暂停该 Session 的当前态推进，阻止落后读取和后续写入；按数据库对账并重建受影响状态／索引，校验后再开放。不得把持久成功伪装成未提交失败 |
| RAM 已发布、响应丢失 | 原命令重试返回原回执；不再应用 Delta、支付或掷骰 |
| Outbox 投递失败 | 可靠、幂等重试并保留进度；不回滚已提交世界事实 |
| 迁移／导入／修复／维护 | 活跃状态不得被脚本绕过协调直接改库；先停用／排空该 Session，受控持久修改后重新加载校验，再开放。具体工具协议 OPEN |

基础事实恢复与玩法继续分开验收。正常崩溃恢复先核对 Schema、Package／Ruleset、提交结果和可靠工作，再重建活跃 RAM 与必要索引；昂贵派生结果按需重算。定期／手动存档用于一致备份、命名检查点和受控回档，不是普通命令唯一的持久化入口；不能把复制正在写入的 SQLite 主文件等同完整存档。备份须覆盖一致 SQLite 状态，受控回档不能静默覆盖已提交副作用。活跃战斗、PendingChoice／Continuation 的精确续玩限制仍按 MVP／§8，不因事实可恢复而宣称任意阶段可执行。

该完整故障协议 **[NOT IMPLEMENTED]**；现有事务／派生缓存机制不能代替发布失败验收。性能后续分别测量读取／Snapshot、规则求值、提交、发布、索引／缓存维护和内存，不凭本次文档声称收益。

### 6.5 规则、领域与提交校验分责 `[DECIDED]`

| 负责方 | 必须检查 / 计算 | 不承担的重复责任 |
|---|---|---|
| RE | 规则合法性、公式、行动资源、效果生命周期及机械连锁 | 不认证外部主体、不提交持久状态 |
| 各领域模块 | 自己的数据结构、引用、归属、不变量及状态生命周期；应用完整候选结果 | 不为每个法术/能力重算 RE 机械结论 |
| 共享提交设施 | 身份授权、版本/原值、请求与规则绑定关联、幂等、原子性、RNG 提交与可靠发布 | 不以通用提交层实现第二套机械判定 |

**共享 Commit／Finalize 范围 `[DECIDED]`：** 普通命令按实际操作、候选 StateDelta、受影响实体及依赖闭包调用所属领域必要验证，不默认审查整个 Session、全部场景、对象或角色。防御式校验不得退化为每次全表扫描；已有全局检查必须先核实其不变量和等价局部／持久保证，再做后续代码重构。分类、例外和规模验收统一遵循 §2.3。

内部可信代码仍可能出 Bug，结构和不变量校验不能删除；RE 已接受也不能绕过权限、冲突或提交失败。确需规则专用适配时留在明确规则适配边界并记录覆盖范围，当前受限攻击专用白名单须先审计，不能直接删除或声称已经通用化。

一次可连续完成的规则操作是适用提交单位；不把整场战斗、整个 NPC 多步计划、一次 EVA 与未来全部行动/感知处理塞进同一长事务。写锁内不得等玩家、LLM、外部 I/O 或长时间求值。领域协作共享一次 COMMIT/ROLLBACK；提交后的可靠投递重试不同于拆裂操作后的补偿事务。

### 6.6 内部领域协作与持久化细则 `[DECIDED; OPEN; NOT IMPLEMENTED]`

以下是逻辑职责与最小语义，不要求创建空类。已有实现与未验证范围仍按 §1 日期化证据；新增方法名／字段须在实现时冻结。

#### C08 共享准备与提交

推荐内部形状如下；它是职责示意，不要求创建完整通用工作流框架：

```python
prepared = handler.prepare(runtime.consistent_read_scope(), command, authorization)
result = await rules.evaluate(prepared.request) if prepared.needs_rules else None
candidate = handler.isolated_candidate(prepared, result)
with coordinator.commit_scope():  # unique Session/world mutation order; no external waits
    with store.transaction(write=True) as uow:
        coordinator.recheck(prepared, candidate, authorization)
        applied = handler.persist_incremental(uow, candidate)
        coordinator.finalize(uow, applied)
    # only after successful COMMIT; failure pauses the Session and reconciles SQLite
    runtime.publish_committed(candidate, applied)
return applied.receipt  # current RAM version must be ready
```

`prepare` 对完整受支持输入做检查并记下依赖；不产生权威变化。纯世界操作也使用已发布 RAM 与隔离候选；有界确定性准备可在短临界区完成，不以读取旧 SQL 忽略候选。上述方法为逻辑伪代码，名称与具体实现 OPEN。候选应用与 `persist_incremental` 可以调用多个所属组件；非战斗阶段取证发生在实际变化阶段，战斗只保留规则执行／恢复与 Episode 内容所需的已提交记录，不要求逐动作感知证据。`finalize` 按 §2.3／§6.5 的受影响闭包检查必要不变量、维护投影（不默认调用全 Session Audit）、按需分配正式事件身份、持久回执／RNG／可靠工作；战斗机械记录不自动产生感知信号。

**ApplyContext 最小语义：** 当前有效 UnitOfWork、session、命令关联、可信操作来源、适用授权、绑定与预期版本、适用记录通道（非战斗阶段取证或战斗审计／Episode 来源）、受影响实体／关系集合。它由运行层创建，不来自模型 JSON；出了事务不可复用。

领域返回覆盖全部连锁变化与候选中间状态的受影响实体／关系、变化与事件阶段关联、需要更新的投影等类型化结果。不能返回任意 SQL／脚本。共同校验由所属领域提供，不在提交协调器里重写规则公式。

所有可写入口都应经过这一最终边界，包括普通 World、RE 结果、检定条件后果、机关、Package 联动、Activity／Effects、NPC Meta／Task／模式／交接、系统时间、感知工作／清理及后台维护；各入口须盘点其事实、稳定幂等键和提交／发布责任。不同来源保留不同的操作资格：例如远程机关不是玩家伸手开门，但它也不能任意绕过锁具、目标范围和空间约束。

#### C09 World 操作与空间查询

**查询：** ObjectView、Placement、ResolvedPosition、Contents、PassageState、SpatialProjection、Illumination，均带适用版本／已知性。

**写操作：** 已支持的开合、门闩、锁、取放、对象移动、灯光、机关及内部耐久结果应用。参数引用真实对象／物品／凭据身份，操作来源由 ApplyContext 提供。

World 验证对象能力、可达范围／操作侧、当前状态、包含关系、访问与容量、占地，以及相应引用。位置必须唯一，父关系不得成环。未知重量／容量只阻止依赖该信息的相应操作；当前相关容器容量 unknown 仍拒绝移出，不能被无关容器容量检查锁死。

目标空间组合分别读取移动阻挡、困难地形、视觉遮挡、掩护依据和光照；已合入 main 的 ObjectSpatial 只输出对象侧前四类贡献，Light 独立提供受限照明投影，尚无综合结果。不能由 blocks_movement 推断其他性质，也不能由视觉遮挡推断挡雨／挡风。查询应包含 schema／坐标单位、scene、版本和明确未知部分。与规则相关的移动／碰撞特例由 RE 求值；World 的通用检查不能反过来禁止已支持规则中的合法特殊移动。

#### C10 Character 与 World 物品／位置协作

Character 接收已验证的 PositionChange、HPChange、ResourceChange、EquipmentBindingChange 或适用封闭机械更新，保留 expected 值与 source 关联。不能对任意调用方开放“设置 HP”“消耗资源”的绕过入口。

普通探索移动由 Navigation／World 校验通路后调用同一位置写入接口；战斗移动由 RE 决定规则后调用它。二者共享坐标，不共享不适用的资源结算步骤。

物品转移必须共同处理：World 实际位置、实例状态、Character 装备／施法材料等绑定、库存投影与相关约束。不支持安全解绑时明确拒绝，不用清空全部装备或重置充能解决冲突。

#### C11 Activity 与 World／Character／RE

ActivityRecord 最小语义：activity_id、actor／session、类型、目标引用、已接受计划／步骤、cursor、status、activity_version、开始／最近命令关联、中断原因及必要时间边界。计划位置只是预期，不是角色当前位置。

每步重新验证当前事实，调用对应领域操作并与游标推进共同提交。导航路径失效可 blocked／replan，不能执行旧路径直接穿过变化后的障碍。取消只取消未来步骤，不撤销已经提交的移动。

休息、搜索、制作、长施法只有在有实际消费者时扩展。Activity 负责“做了多久、是否中断”；RE 负责适用规则；持续法术的施法活动与施法完成后的 Effect 分别管理，不保存两份相同进度。

#### C12 Effects 与规则／角色／世界

目标 EffectRecord 至少表达稳定完整身份、definition／ruleset 引用、source／caster、target、应用来源、生命周期状态、持续规则、所用时间域、已处理边界／去重记录、适用空间锚点，以及专注／Condition 应用关联。并非所有效果都需要所有字段，应按类型区分。

当前 RE 的效果身份依赖 `(target_id, id, origin)`；适配时必须保留完整身份及来源关系，不能只按法术名删除所有效果。

Effects 提供 `read_applicable`、`read_lifecycle_dependencies`、`apply_verified_lifecycle` 等窄接口。RE 计算建立、续期、豁免、结束和连锁；Effects 验证身份／引用与生命周期原值并持久化结果。World 负责空间实体与锚定位置，Effects 提供临时影响，空间查询组合读取。

Condition 多来源、专注结束、效果取消和区域移除需共同维护引用闭包。不要把同一 Condition 的来源抹掉后，在取消一个来源时错误清除其他来源。结束战斗／切换场景只触发适用规则，不默认全删效果。

第一阶段只给现有 effects_json 与相关记录建立明确访问边界；尚未支持的规则生命周期保持 unsupported。不能为了接口完整而在 World 写一份效果期限或复制 RE 的规则。

#### C13 世界时间与调度

沿用唯一 game_tick。main 已有 WorldTimeService 与固定 TimeBinding：显式 world-time/1 为 1 tick = 1 游戏秒，legacy game-clock/1 仍为抽象 tick，不能未经迁移改称秒。Package 可提供绑定，创建 Session 可整体覆盖并固定保存；换算、昼夜／有界边界查询与获准命令推进已实现（§1.3）。每种规则期限仍须声明 world_time、turn_start、turn_end 等时间域；固定单位不等于生命周期消费已接通。

后续消费目标 [DECIDED; NOT IMPLEMENTED]：输入 expected_tick、目标 tick／获准的时间推进量、来源命令、推进原因及适用流程上下文；输出实际推进、到达的有界边界、已创建可靠工作和未完成边界。当前 AdvanceGameTime 仍是 expected_tick／next_tick，不据此新增公共命令字段。

一次大跨度推进必须按需要处理的确定性边界排序。若需要 RE、选择或外部等待，就在合法边界结束本次提交并保存继续所需进度，不能先跳到终点再异步补完本应影响中间结果的伤害／中断。

战斗内外共享世界时间：一整个 Round 约六个游戏秒，包含各 Actor 的 Turn；实际执行可能耗费几十秒或更久的墙钟时间。只有 TimeBinding 明确 `1 game_tick = 1 秒` 时，一轮才约为六个 tick。不能每个 Actor 的 Turn 都重复增加一整轮时长；同一生命周期边界只处理一次。Host 墙钟用于超时与性能，世界时间用于活动、燃料和观察生命周期。C15 的 Turn／Round 区分是认知交付粒度，不创建不同流速的世界时钟。

当前 SessionTime／TimeDriver 已实现显式倍率、start／pause／resume、余量与有界 Pending Time Work；真实 RE Round Delta 接入单轮 6 tick，Turn 不重复累加。生产期限提供方目前是机关，领域等待回复成功链使用持久化测试适配器；完整 Activity／Effects、燃料、天气、秒制 NPC／OB／Gate 及一般生产等待消费者仍未完成。默认倍率、菜单／断线／一般 LLM 等待宿主政策仍 `[OPEN]`。秒制 unsupported_time_consumer 与活跃 Combat 精确恢复限制继续有效；源码、测试与历史验收见 §1.6。

#### C14 条件后果／Package 触发／机关

声明最小内容：稳定定义／来源引用、受支持 trigger、前置条件、目标范围、白名单操作序列、一次性／重复策略和采用记录。

`CheckWorldEffects` 是预先声明的成功／失败世界后果，RE 只提供检定结果；`PackageEffects` 是剧本联动。建议内部使用不同名称，避免与持续 Effects 混同。

选中分支后通过相同 World 操作与共享提交执行。触发去重记录必须与结果共同提交；失败回滚不能留下“已经触发”的标记。禁止任意脚本、隐式新规则和无限事件级联；保留有界执行与明确超限错误。

如果规则需要“失败也消耗动作／时间”，由获准规则结果和后果定义共同表达，不能把事务错误解释成一次已执行失败的尝试。

#### C20 领域组件 → 持久化与可靠投递

`transaction(write=True)` 创建唯一 UnitOfWork；领域 Repository／Facts 使用该上下文写入，不能自行提交或开启独立连接完成同一个操作。允许 savepoint 做操作失败回滚，外层负责最终回执与提交。

约束至少覆盖唯一键、外键、版本／原值匹配与必要图关系。SQL rollback 后不得继续暴露失败计算的可变缓存；读取返回分离结果，派生缓存必须可失效重建。

Outbox／工作记录与来源提交原子保存；投递发生在提交后。消费者以稳定业务键去重、保存进度并可在崩溃后恢复。不同类型的发送确认、投影完成、认知工作完成分别表达；不能因为某个全局 cursor 前进，就宣称所有 NPC 已处理。

恢复先验证数据库版本与 Package／Ruleset 绑定，对账持久事实、RNG、未完成可靠工作和原回执，再重建活跃内存表示与必要索引，校验后开放当前态读取／推进；昂贵派生值按需重算。不能依赖旧 Python 对象或 Host Context。备份必须覆盖 SQLite 一致性状态，不能只复制正在写入的主文件后承诺完整存档。

活跃战斗精确恢复当前有明确限制；目标未来需保存选择窗口和必要机械流程依赖。该能力未通过独立进程恢复验收前，不宣称任意阶段可继续游玩。

## 7. WorldEvent → Perception → NPC Evidence（P0/P1）

§7.1–§7.3 描述非战斗 Event-level 协议及可复用实现资产，§7.4 为共同 OB 契约；战斗按 §7.5。当保留这种事件记录时，其证据、原子性和信息隔离要求继续适用。它们不要求每次机械行动产生 WorldEvent / 独立 OB，也不冻结未来运行层的永久观察粒度；完整事态目标见 §7.5。

### 7.1 CommittedWorldEvent 与 Observable Signals `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

本节只定义非战斗 Event 路径，整合 PER-01～PER-08，逻辑顺序为：Event + Signals 确定 → 逐 Signal Scope Discovery → Event-local / Signal-scoped Evidence Capture → 原子提交 Event + Signals + Evidence + 可靠 Outbox → 后续 Deterministic / JEV Perception Judgment → Authorized ObservationRecord（OB）→ 既有 NPC Inbox。提交前 Event 仍为待提交事实；这不是多个独立事务，不新增模块、感知状态机或独立认知流程。

CommittedWorldEvent 沿用 session_id、event_id / event_seq、source_command_id、event_type、适用 Actor/参与者、状态版本/游戏时间、受限 payload 和可信事件时证据/历史引用，可包含 **observable_signals[]**。ProposedEvents 未提交前不是 WorldEvent，没有权威事件身份；SM 不从事件或 Signal 重算机械效果。

| Signal 最小候选字段 | 约束 |
|---|---|
| signal_id | 在所属 Event 内唯一；不是独立全局 Task ID |
| channel | 感知渠道，使用已支持的类型，不从自然语言猜测 |
| content | 该 Signal 的可感知内容；向 Observer 投影时仍受授权限制，不等于完整事件 payload |
| scope | SM 能确定性计算的受限类型化感知范围；不另存重复 perception_scope，与机械 Effect Scope 独立 |

Scope 可候选支持 actor / scene / radius / connected_scenes / region / world 等类型；枚举、复杂空间关系、单位/传播参数与完整 Schema **[OPEN]**。仅声明/使用已支持的计算能力，不能让 SM 根据自然语言补传播范围。如下为 evt.001 的候选 Signals 形状示例（非完整 WorldEvent），不代表已冻结或实现的 Schema：

```yaml
observable_signals:
  - signal_id: signal.impact
    channel: hearing
    content: {description: "近处传来一声金属碰响。"}
    scope: {kind: scene, scene_id: scene.synthetic.workshop}
  - signal_id: signal.glimmer
    channel: sight
    content: {description: "门边闪过一道微光。"}
    scope: {kind: scene, scene_id: scene.synthetic.workshop}
```

Planner 的候选 Signals 按可能执行结果分类，预定义事件/标准规则行为优先复用已有模板；SM 根据可信结构化结果选取匹配内容，与实际 WorldEvent、事件时证据和可靠处理任务同事务提交。SM / RE rejected 或 unsupported 不产生该未执行行为的 Signals；accepted 即使未达成目标，也可有合法执行产生的声音/动作 Signals，仍须 SM 提交成功。模板、结果条件/绑定字段 **[PROPOSED / OPEN]**，不新增 Event Generation Agent、不采信模型自报成功。

#### Event-local / Signal-scoped Evidence `[DECIDED]`

以下是统一目标原则；§1.1 已核对开发分支的受限世界 Producer 实现，RE 阶段协议仍 [OPEN; NOT IMPLEMENTED]，不能将两者混为全部已完成或全部未实现。

**Event-local Evidence：** 每个 CommittedWorldEvent 的证据必须对应其 Signals 所描述的**实际发生阶段**，而不是无条件复用整个 Command 完成后的状态。一个 Command 可以产生多个 Event；不同 Event 可以共享未变化的可信证据，但若相关位置、Scene、光照、遮挡、感官或 Conditions 等在阶段间变化，必须保留各自对应的证据及关联。`event_seq` 只是记录顺序，不是完整中间状态快照；相同 world_version / game time 也不证明两个 Event 的相关证据相同。例如同一命令先在 Scene A 发声、再进入 Scene B，不能用 B 的结束态为 A 的发声事件作判断。

**Signal-scoped Evidence：** 保存该 Event 的 Signals 进行感知判断所必需的可信历史数据，按 §7.2 的候选集合裁剪；不复制整个 Session 的感知状态。最小必要性以判断所需的字段完整性为前提，不能把“未保存”解释为“没有该状态”。同一 Event 的多个 Signals 可共享来源、Observer 或环境证据，避免重复存储，但必须保留逐 Signal 的适用范围/关联。

| 证据内容（概念，非冻结 Schema） | 范围与完整性要求 |
|---|---|
| Signal Origin | 该 Signal 实际发生阶段的可信来源 Scene、实体/位置及判断所需属性；不是模型自报或从当前位置反推，具体编码 [OPEN] |
| 相关环境 | 各 Signal Scope / 判断所需的 Scene、空间关系、光照、遮挡等历史数据的并集；不包含无关 Scene / 对象状态 |
| 候选 Observer | 逐 Signal Scope 内全部候选 NPC 的事件时位置、感官、Conditions 及其他必需状态；包含 Inactive 和可能无法察觉的 NPC |
| 来源与恢复关联 | 核验阶段、版本、证据适用范围及可靠恢复所需的最小关联；可共享不可变证据或稳定历史引用，不能只存 event_seq 后查当前世界 |

必要证据必须来自可信 SM 状态、经验证的规则结果或可核验的不可变历史引用，且字段满足受支持判断的完整性。缺失必要位置、感官、Conditions 或环境等证据，不能使用当前 World State 补造，不能默认 Positive 或 Negative，也不能交 JEV 猜测缺失事实；沿用既有未完成工作语义，不冒充已完成投影。Event Evidence 是**感知专用最小证据**；Rule Engine 的 CombatSnapshot / NonCombatSnapshot 必须满足 §4.2 的完整机械规则依赖，两套裁剪原则不能混用。

**原子性 `[DECIDED]`：** Event、Signals、Evidence（或受保护的稳定历史引用）与可靠 Outbox 必须与对应世界变化在同一个 SQLite 原子事务中提交。Capture 可依附可信事件阶段，先保留必要取证依据，待 Event / Signals 确定后完成 Scope 裁剪和证据绑定；逻辑顺序不要求独立事务，也不允许中间可见的部分提交。事务外准备的依据须经提交版本/读集校验，不能在写事务中等待模型或长时间规则求值。异步 Judgment 只能消费已提交证据。

**采集协议 `[OPEN]`：** 必须结合真实 SM 世界操作与 Rule Engine 有序事件语义，验证每个 Event / Signal 对应阶段、可取得的可信状态及共享条件。仅有最终 Delta / 事件序号不能假定可以恢复中间阶段；无法恢复时须显式列为未解决的支持缺口，不得虚构准确的事件时状态。阶段采集、引用编码/保留与大型范围分批策略尚未冻结；本轮不扩展 NPC State Timeline、Signal Channel、全局 Cursor 或 Unresolved 恢复设计。

**历史实现与目标差距（Batch A 历史核对；更新基线见 §1.1）：**

| 层次 | 事实 / 状态 |
|---|---|
| 已实现的指定历史基线 | `trpg-state-machine@5deea78` 的 `events.py::_event_perception_evidence` 使用 `event-evidence/3`，读取 Session 全部已实例化 Actor / Scene（及对象位置）。`service.py::_append_events` 在事件循环前捕获一次，逐 Event 写入同一份内容；世界命令路径在操作/级联之后调用它。该行为不是逐 Signal 裁剪或逐阶段取证 |
| Batch A 当时目标 `[DECIDED]` | 每 Event 对齐实际阶段，逐 Signal Scope Discovery 后取候选/环境并集，保存最小且完整的感知证据并原子提交；在该历史基线未实现，当前开发分支的受限实现另见 §1.1 |
| 待验证 `[OPEN]` | 真实 SM / RE 路径的阶段语义和可恢复性、可信字段来源/依赖与共享条件、候选完整性及分批恢复；本轮已核对范围见 §1.1，不代表部署或全部规则覆盖 |

### 7.2 Discovery、判断与 Observation `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

**C16 战斗请求适用规则：** 战斗 JudgmentRequest 使用类型化 combat／episode／Turn／Round 来源与固定 EpisodeFilterBasis；同 NPC／Episode 多通道合批，不伪造 event_id。请求内每个 signal_id 恰好一个 Boolean；缺漏、重复、额外项、错误或超时不转 false。必需过滤输入缺失维持 unresolved；模型不要求的逐动作感知证据不算缺失。以下阶段／Event 示例只适用于非战斗。

**Scope Discovery `[DECIDED]`：** 对每个 Signal 独立按其类型化 Scope、可信 Origin 和对应阶段的空间/成员关系作确定性候选筛选；再对同一 Event 的候选 NPC 和所需环境证据取并集，保留 NPC 与各 Signal Scope 的对应关系。Discovery 只回答“谁在候选范围内”，**不判断视觉、听觉、遮挡、感官能力或实际察觉**；Scope 内即使失明、耳聋或可能被遮挡的 NPC 也不得提前排除，不能只发现在线 NPC。后续 Perception Judgment 才用完整事件时证据确定性检查感官、位置、明确遮挡及已支持机械约束；并集不意味着每个候选都适用 Event 的每个 Signal。

**边界与分批原则 `[DECIDED]`：**

| 情况 | 处理原则 |
|---|---|
| 零 Signal Event | 合法空 Signals 不触发察觉判断或 OB；不复制 Observer / 环境感知状态，保留必要事件/可靠工作及空结果语义。缺失/非法 Signals 不能当作合法空集合 |
| 多 Signal / 不同 Scene | 分别按各 Signal 自身 Scope / Origin 发现，不用 Event 的单一 scene_id 限制全部候选；证据取并集并共享未变部分，逐 Signal 判断后沿用同 NPC / Event 的 OB 聚合 |
| 无候选 NPC | 可信完整 Discovery 的空集合可可靠完成，无需 JEV / OB，也无需 Observer 状态；缺失范围依据不等于没有候选 |
| 大型 Scope | 若已支持范围本身很大，必要证据集合也可很大；允许可恢复分批发现/取用/判断，沿用既有 Work / Outbox / 去重。不要求一次物理枚举全部 NPC，但原子提交时必须固定完整候选集合或可恢复枚举它的稳定历史依据，以及可恢复的事件时必要证据/引用；不能事后扫描当前 Actor / Scene 补历史，也不能因分页/预算截断漏候选 |

上述逻辑顺序允许大型集合按已提交的可信历史依据分批展开，不允许把 Evidence Capture 延迟成读取当前世界；候选完整性和证据恢复未保证前不能标完成或越过投影水位。具体分页/保留/共享编码 [OPEN]，仅使用已有支持的 Scope 能力，本轮不要求实现新 Scope 类型。

**JEV Perception Judgment：** 只有确定性条件无法判断的情境才交 JEV，明确可判定的 Signal 不必提交。SM 授权、Host 运行，提供最小必要的事件时可信 Observer 状态、相关环境及待判断 Signals；此 JEV Perception 职责只逐项判断是否察觉，不生成 Signal、Observation 文本、Belief / Goal / Plan 或世界变化，与独立的 Cognition Gate Judgment（§9.8）/ NPC EVA 分开。具体模型/传输仍为候选；调用在写事务外。

该可选 JEV 属于后续 Agent Cognitive Response 的感知输入准备，不能成为即时战术/Reaction/自动效果的机械前置依赖。Immediate Mechanical Response 所需察觉只能走可信确定性/RE 路径，未知不得默认已察觉（§0.1）；后续主观认知不能反向补准已经执行的机械响应。

候选请求可批量携带**同一 Observer / Event** 的多个待判断 Signals，返回按 Signal ID 给出明确 Boolean。以下两个 JSON 为原创内部请求/返回的形状示例，字段仍 [PROPOSED; NOT IMPLEMENTED]：

```json
{
  "observer_id": "npc:guard-a",
  "source_event_id": "evt.001",
  "occurrence_context": {
    "observer_state": "<trusted event-time senses, position and relevant state>",
    "environment": "<minimal trusted event-time environment>"
  },
  "signals": [
    {"signal_id": "signal.impact", "channel": "hearing", "content": {"description": "近处传来一声金属碰响。"}},
    {"signal_id": "signal.glimmer", "channel": "sight", "content": {"description": "门边闪过一道微光。"}}
  ]
}
```

```json
{
  "judgments": [
    {"signal_id": "signal.impact", "perceived": true},
    {"signal_id": "signal.glimmer", "perceived": false}
  ]
}
```

SM 校验请求 Signal 均且仅有一个结果，无未知/重复 ID，perceived 必须为 Boolean；缺失、超时、Schema 错误不得默认为 false。复用既有可靠工作/重试机制，未完成判断不冒充已完成处理，不新增 Signal Task ID / ACK。JEV 输出只是候选判断，由 SM 验证、持久记录并形成观察；重投复用已保存判断/Observation，不重新推理改写历史。涉及正式 D&D 感知检定仍交 Rule Engine；复杂检定与异步处理的 RNG / 命令 / 事务编排 **[OPEN]**，JEV 不替代规则掷骰。

**Observation 聚合与投影：** SM 汇总该 Observer / Event 的确定性与已验证 JEV 判断后形成观察，未完成判断不提前标完成。同一 NPC / WorldEvent 的多个已察觉 Signals 默认聚合为一条 ObservationRecord，perceived_signals[] 保存 Signal ID、渠道及授权 Content；全部未察觉可完成处理而不生成 Observation，但缺失/错误判断不能走此路径。持续事件在不同时刻产生的新观察不强行合并。以下是 SM **内部记录**示例，不可原样传给 NPC：

```yaml
observation_id: obs.npc.guard-a.0005
observer_id: npc:guard-a
source_event_id: evt.001           # 内部来源追溯，不是 NPC 可见事件语义
source_event_seq: 35
perceived_signals:
  - signal_id: signal.impact
    channel: hearing
    content: {description: "近处传来一声金属碰响。"}
perceived_at_game_time: 1023
observation_schema_version: observation/0.1
```

投影仍按调用主体的可见性和秘密等级过滤，NPC / 玩家 / Narrator 不接收全量世界真相。source_event_id / source_event_seq 用于 SM 内部审计/排序，不赋予 NPC 对事件类型、真实行动者、隐藏目标等秘密的知识。NPC Context 的事件内容只来自被感知且授权的 Signal Content，不带内部来源语义；既有 observation_id 等证据引用保留用途。听见声音不等于理解其真实原因，是否理解/形成 Belief 交 NPC EVA。

EventObservation 是过去事件的授权感知证据；CurrentPerceptualView 是查看时的授权当前状态（observer_id、view_world_version、view_time 等仍为候选），不伪造历史 source_event_id、不补未目击历史。观察持久化后走既有 Inbox / Gate / Mode Routing，感知判断不等于唤醒 NPC、修改关系或行动成功。

### 7.3 Reliable Observation Delivery `[PROPOSED; NOT IMPLEMENTED]`

按 §7.1–§7.2 在 Commit 同事务内记录 Event、Signals、Event-local / Signal-scoped Evidence / 稳定历史引用及可靠 Outbox / 待处理 Projection 工作；分批 Discovery 仅展开已固定的历史候选依据，投递至少一次。默认聚合按 `(observer_id, event_id, projection_version)`（或等价唯一键）幂等写 Observation；持续事件分时新观察的时刻区分/等价键编码 [OPEN]，不强制合并。NPC 不在线时仍保存应收到的 Event Observation 或可靠重放证据。**原始事实、感知记录、角色信念三者分别持久存储**；`Belief` 不等于 World Fact。

- 分批 Discovery / 判断未完成时不能越过投影水位；全部未察觉也须可靠记录处理完成，不用空 Observation 冒充感知。具体分页、历史保留和索引字段 [OPEN]，沿用既有工作机制。
- `observation_id` 稳定，按 NPC 提供顺序可核验的 Delivery Cursor；相同事件多个 Observation 的次序需有稳定 tie-break。分页返回该 NPC 的投影完成水位/等价完整性证明，不能跨越该 NPC 较早的候选未完成项或适用的既有异常屏障。其他 NPC 的候选未完成项不构成全局阻塞；Session 汇总水位仅供兼容/审计，不覆盖每 NPC 的完整性证明（已实现的 Batch C / PERF 边界见 §1.1）。
- 读取 Cursor / Host 已追加 Context 位置与 SM 内部 Processing / Completed Cursor 分离。读取、追加或模型返回不等于处理完成；SM 仅按必要认知处理与可靠输出交接的持久完成状态推进连续前缀，见 §9.6，不要求 Host 额外 ACK。
- SM 为待处理 Observation 批次建立稳定 `observation_work_id`、任务及幂等处理记录；重复投递不创建第二份逻辑工作。合并批次不能重复占用尚有任务的同一观察；具体索引/表结构未冻结。
- Mode Routing、Gate 领域策略、证据保留和任务完成由 SM 管理；Host 按授权请求执行 Context 追加或模型调用。失败不随 Context 释放而丢失证据。

### 7.4 Recent Observation、Processing 与 Retention `[DECIDED; NOT IMPLEMENTED]`

NPC 维护**单一、有界的 Recent OB List**，按游戏时间窗口保存该 NPC 实际察觉的观察，顺序稳定。窗口的时长、截断规则和必要容量上限应在实现时固定；不要求另设 Pending／Historical OB List 或第三种 OB 处理状态。观察者感知投影水位仍按 C16 独立维护；读取列表、Host 添加 Context 均无处理副作用。

**OB 的 Cognition 处理状态只有 `pending` 和 `processed`：**

| 状态 | 含义与转换 |
|---|---|
| `pending` | 新 OB 的 Gate 判断尚未可靠完成，或 Gate 判定需要 EVA 而本次认知义务尚未由有效任务完成；失败、超时、模式竞争不可默认为 processed。 |
| `processed` | Gate 已可靠判定无需触发 EVA，**或**覆盖该 OB 的有效 EVA 已合法提交；表示当前没有未完成的认知处理义务，**不表示 LLM 一定读取过该 OB**。在游戏时间窗口内仍可被以后 EVA 读取为历史证据。 |

感知 JEV（C16）与 **Cognition Gate** 是不同职责：JEV 判断信号能否被察觉；Gate 判断新 OB 是否需要触发 NPC EVA。每条新 OB 在进入 Cognition 后都必须获得可靠的 Gate 决策；Gate 可以优先使用确定性策略，仅在设计明确需要时调用受限模型。现有 urgent／deferred／irrelevant／uncertain 等分类属于 Gate 的判断结果，不是额外 OB 状态；仅明确无需 EVA 的有效决策可置 `processed`，需要 EVA 则保持 `pending` 并依 Task 资格创建／排队，判断失败或尚未确定则维持 `pending` 并可靠重试。

创建 EVA Task 时固定本次覆盖的 pending OB／Work、认知版本，并冻结**当时整个仍在窗口内、授权且有界的 Recent OB List**（包含 processed 和 pending）作为输入。processed 历史 OB 可以改变 LLM 对当前新 OB 的理解，但再次出现在输入里不构成再次触发或再次消费。合法 EVA Result 只完成本任务固定覆盖的 pending OB；C17 的任务身份、结果幂等、Episode 覆盖和 Meta 原子提交继续适用。同一 NPC 同时只有一个有效 EVA；在途期间新来的 OB 继续接受 Gate 判断，需触发者 pending 并在后续有效任务处理，不修改旧任务的固定输入。

战斗 Gate 处理 C15 的 Turn／Round 聚合 OB，不退回机械 Event 级。一个 Episode 的 OB 不必对应一次 EVA；普通 OB 不暂停战斗。关键任务需要影响下一 NPC Turn 时依 C07 的获准等待边界处理。Gate 负责是否**现在需要认知更新**，而不是裁定 OB 是否有永远的记忆价值。

Recent OB List 按**游戏时间**滑动；到期的 processed OB 可以退出活跃窗口，但被有效 Task、回执、长期 Meta 引用或恢复流程必需的证据仍依相应保留策略保护。到期的 pending OB 也不得无条件删除或隐式置 processed；可从活跃列表移出并独立保护必要证据，直到处理或明确失败／恢复。Host 墙钟超时不推进游戏时间，重试必须保持冻结输入，不能用新的窗口内容覆盖旧 Task。

保留／到期／归档是证据用途与清理条件，不增加第三种认知状态，也不建立独立 Pending／Historical OB List。ObservationWork 是同一 OB 的处理关联；窗口外保护必要恢复证据不构成另一认知输入列表。

Long-term Memory／Belief／Relationship／Goal／Plan 经合法 SourceReference 可多记录引用同一 OB，历史版本也受保护。Meta 提交与清理在事务内核验引用及保护条件；只有处理完成且 Task、输出交接、审计、回执、去重和幂等保护全部解除才可清理。内部归档不自动回注 NPC Context，不制造悬空来源或改变处理水位。到期证据只作标明原始时序、已过期与权限的受限恢复输入；长期 Meta 自有生命周期，不随来源到期删除。TTL 起点／数值、容量／截断和清理算法仍 OPEN。

### 7.5 WorldEpisode、EpisodeObservation 与信息分层 `[DECIDED; NOT IMPLEMENTED]`

**目标：机械计算可以细，认知输入必须有界聚合。** 非战斗沿用 Event 产生 Signal、按实际察觉组成 Episodic OB 的机制。战斗改为 Episode 产生聚合 Signal：参与该战斗的 NPC 按角色 Turn 接收，未参与该战斗的 NPC 按 Round 接收。机械 Event 不逐条生成认知信号，不逐条触发候选判断、OB、JEV、Gate 或 EVA。

Turn 是一个角色的单回合，可以包含移动、多次动作及期间发生的 Reaction；一次 action／attack 不等于一个 Turn。Round 是所有参战者轮流行动的一整轮。整场战斗用 `combat_id` 关联，不再强制“一场战斗只有一个 CombatEpisode”。以下数据名是逻辑职责与字段语义，不要求同名类、独立表或新的服务。

| 数据 | 最小内容与语义 |
|---|---|
| MechanicalAudit | 原请求／结果、固定绑定、RNG 关联及规则执行／恢复所需步骤；与已提交机械变化关联，不直接投影为认知信号 |
| StagedOccurrence | 非战斗的来源命令、阶段、时间／空间、事件类型、受限 payload、Signals 与取证依据；尚无权威 event_seq。战斗机械 Event 不要求逐条转换成此记录 |
| Signal | 稳定 signal_id、类型化来源（非战斗 event 或战斗 episode）、channel、授权内容、类型化 scope／origin；机械作用范围与感知范围分开 |
| Evidence | 非战斗采用不可变阶段证据；战斗采用与 Episode／聚合策略绑定的过滤依据、所需范围与接收能力输入、版本及完整性状态，不要求逐动作视线快照 |
| CommittedWorldEvent | session、event_id／seq、source_command、world_version、发生时间、事件数据及适用 Signals／Evidence 引用；不是每条战斗机械记录的强制包装 |
| WorldEpisode | episode_id、类型、起止／状态、已提交来源引用及必要的真实顺序；可跨多个提交，不承担跨命令回滚 |
| Turn Episode | session／combat、稳定 Turn 身份与所属 Round、行动 Actor、关闭状态、已提交行为／结果来源、聚合信号与过滤依据；包含该 Turn 期间发生的反应 |
| Round Episode | session／combat、稳定 Round 身份、关闭状态、本轮已提交 Turn／机械记录来源、面向战斗外的聚合信号与过滤依据；复用来源，不拼接 NPC 私人 OB |
| EpisodeObservation | observer、episode、适用 revision／来源覆盖、实际察觉的聚合 signal 引用、授权内容、完整性与 retention；收到来源引用不等于得知完整 Episode |

**信号生成与交付边界：**

| 情境 | 信号来源与处理粒度 | 正常形成／交付时机 |
|---|---|---|
| 非战斗 | Event Signals，依据各事件的独立阶段证据形成 Episodic OB | 沿用既有非战斗 Episode 流程 |
| 已参与该 combat 的 NPC | 一个 Turn Episode 的聚合信号 | 该角色 Turn 完成后形成，供后续决策／认知处理；不按内部机械 Event 增量交付 |
| 未参与该 combat 的 NPC | 一个 Round Episode 的聚合信号 | 整轮结束后形成；战斗提前结束时关闭并发布最后一个未满轮的汇总 |

1. **主动采用粗粒度战斗感知。** 聚合器按已提交行为和结果概括“该 Turn／Round 发生了什么”，按受支持感官通道形成有界信号。保留规则、审计、恢复与内容来源所需记录即可；不另建逐动作感知证据链，也不要求补齐每个阶段的旁观者、光照或遮挡快照。RE StageFacts 可作为已有来源，不能因缺少逐动作感知资料而否定本模型，或在审计中重新要求逐 Event 生成信号。
2. **既有过滤继续有效。** Episode 聚合信号仍经范围与 NPC 接收能力过滤；模型不把所有参战者视为全知。聚合策略需要明确基本 scope／origin 的来源、授权内容表达和所需过滤输入，并绑定到可重试的 Episode 版本；具体范围算法在实现时冻结，不在本基线中伪装成逐动作精确感知。收到听觉信号不自动获得完整视觉事实、隐形目标或玩家秘密。
3. **按具体战斗的参与关系路由。** 对同一 combat，参与者接收 Turn 来源，非参与者接收 Round 来源。NPC 即使处于另一场战斗，对本场仍是外部观察者；不能只检查全局 `in_combat`。路由依据与来源覆盖需要固定，重试不得按最新参战状态重新解释旧投影。中途加入／退出的切换边界和去重覆盖须在实现时明确，不以双发 Turn 与 Round 的方式重复处理同一经历；本次未验证旧代码是否已有该能力。
4. **按 Episode 合批判断。** 同一 NPC、同一 Episode 的待判断感官信号作为一个逻辑批次，不按其中的机械 Event 拆分 JEV／Gate／EVA。确定性过滤能完成的判断无需模型。每个实际察觉到内容的 NPC 得到自己的 OB；没有察觉不创建空 OB。每个新 OB 进入单一 Recent OB List 后由 Cognition Gate 判断是否需要 EVA：不需要则 `processed`，需要则 `pending` 并依有效任务资格调度。OB 形成不自动启动 EVA，多个 pending OB 可被后续同一获准任务覆盖；processed OB 在游戏时间窗口内仍参与后续 EVA 的上下文推理。
5. **聚合与机械提交分开。** 只汇总已提交来源；未提交或回滚候选不进入 Episode 内容。Turn／Round 跨多个命令时，机械操作仍分别短事务提交；边界关闭、聚合完成及可靠工作必须有持久幂等身份，可在中断后恢复。Round 引用同一批已提交来源，不再次结算机械结果；不为提高“原子性”把整轮放入长事务。
6. **Reaction 不依赖 OB。** 当前 Turn 内反应由确定性 CombatPolicy、CombatHandler 与 RE 根据已有策略参数和当前机械事实处理，不等待本 Turn 的认知判断。Cognition 采用聚合 OB 后提交的新参数在后续决策中生效；关键任务需影响 NPC 下一 Turn 时按 C07 保存等待边界。
7. **非战斗与旧数据迁移保留。** 非战斗每个 Event 的阶段证据仍独立保存；历史 Event-level OB 与处理进度保留。先建立稳定来源／处理覆盖映射，再切换战斗消费入口并停止相同范围的旧逐 Event 感知任务。历史缺少所选协议必需的来源信息时标注缺口，不补造；不得在聚合或战后总结时重复创建 Meta／Action。非战斗确有增量观察时继续按 episode／observer／revision 或等价覆盖去重，不将其扩展为战斗的逐动作交付要求。

一整场战斗的长期记忆可以由 NPC Cognition 在获准 EVA 中结合本次触发 OB 与窗口内已处理的 Turn／Round OB 汇总形成；这不要求再发布一个包含全部战斗真相的总 OB。

具体消息 Schema、EpisodeFilterBasis、迁移与恢复仍 [OPEN]；语义已确认不代表当前 SM 已实现。

## 8. Pending Choice / Reaction / Continuation（P0 语义，MVP 限制实现）

**实现边界：** §1.1 的 RE main 有受限预声明 Reaction；锁定版本与它不同，两者均不能证明通用“解析中暂停并等待选择”的持久 Continuation 已完成。以下区分前置选择候选协议与中途 Interrupt 目标，不据文档宣称代码已支持。

### 8.1 MVP 首选 `[PROPOSED]`

优先采用**求值前选择**：Rule Engine 返回 `needs_choice`，但不消耗 RNG 或机械资源；负责 Handler 通过共享设施保存**独立的 PendingOperation 元数据**（不是对机械求值部分提交），Host 向有权限的角色请求选择，随后发起新的 `choice.respond` 命令附 `pending_operation_id` 与 `selected_option_id`。负责 Handler / 共享提交边界验证主体、原命令、版本、有效选项及过期/取消状态，再基于新鲜 Snapshot 重新求值与完整提交。

`PendingOperation` 至少包含 `pending_operation_id`、`source_command_id`、`actor_id`、`authorized_responder`、`choice_kind`、`allowed_options`、`input_world_version`、`status`、`creation_time`、`expiration_policy`、`ruleset_binding` 和唯一幂等字段。`choice.respond` 不能任意覆盖原始 Intent。

### 8.2 必须明确不支持的场景 `[OPEN]`

某些 Reaction 在掷骰、命中或部分效果发生后才能决定是否响应。上述**求值前选择**方案无法普遍正确表达这类中途暂停机制。对这种规则路径：

- MVP 可以沿用已验证的**预先声明 Reaction 策略**，但不得声称与所有 SRD 交互式选择完全等价。
- 如果剧本的黄金路径必须支持中途 Reaction，需先设计可持久化的执行检查点、已消耗骰点与信息窗口，再决定最小实施范围。
- 最终 Continuation 使用 Handler 管理的类型化、版本绑定流程状态与负责领域事实，不引用 Legacy `_LiveCombat` / `CombatHandle` 或其他进程私有执行器句柄；也不在外部等待时占住 SQLite 写事务。
- `needs_choice` 不能偷偷提交已经结算的伤害，也不能凭 Narrator 文本作为 continuation 状态。

活跃战斗异常退出后的**精确续玩仍为 Post-MVP**。MVP 需保留明确的 `combat_interrupted`/停止受理/安全重新开始策略，不能悄悄恢复战前状态并覆盖已提交结果。

### 8.3 Interrupt / Continuation 目标 `[DECIDED; OPEN; NOT IMPLEMENTED]`

1. RE 尽量连续结算；在确需新的中途选择、继续将改变合法信息窗口时暂停，交回可信可序列化的待决操作/Continuation 语义，不等待 NPC LLM、JEV 或 EVA。NPC 机械选择由受控 Combat Policy / 已授权预声明策略处理，PC 选择交可信玩家入口。
2. Handler 持久管理待决操作、授权选择范围、版本和执行进度；必要 RNG / 已支付资源证据按负责领域与共享设施关联保存；不保存进程私有 `_LiveCombat` / Handle。重试/恢复沿用持久身份与已采纳选择，已经确定的骰点不能重掷，资源不能重复支付，未完成步骤不能伪装完成。
3. 选择响应需重验主体、窗口、版本和有效选项，防迟到/重复响应；只恢复合法的原执行进度。发生冲突、取消、超时或规则版本不符时显式处理，不能把旧 Continuation 套到新状态或重新从头掷骰来“修复”。
4. 暂停的持久检查点/必要状态与 RNG 转换、对应审计/事件及可靠交接须经各负责接口在同一个共享短事务保存；等待选择和 RE 续算在写事务外。已经提交的可观察阶段不可撤销；尚未提交的部分结果不得提前发布。

**ABI `[OPEN]`：** Interrupt 如何映射 Result / Receipt、Continuation 字段与幂等身份、计算中已消耗 RNG 的保存/预留、哪些前缀机械效果可提交、信息窗口与其他命令的交错/版本政策、取消/到期和最小 MVP 支持范围，尚需真实路径审计。不能用 §8.1 的无消耗 needs_choice 假装完整中途暂停，也不预先新增正式接口/status。目标恢复语义不等于 MVP 承诺任意活跃战斗崩溃精确续玩；未支持路径须在执行前明确边界，不产生虚假的部分成功。

## 9. Agent Host / NPC Evaluation / Memory / DM（P1 接口边界）

本节架构语义按各段 `[DECIDED]` 标记；新增消息、字段和存储协议仍为 **`[PROPOSED; NOT IMPLEMENTED]`**，具体类型、状态编码、版本与数据库结构仍需审阅；不要求新增服务或复杂公共 Receipt 子系统。

### 9.1 EVA、NPC Meta 与 LLM Runtime `[DECIDED]`

**EVA（NPC Evaluation）是认知更新与决策评估，不是 Action Execution。** Memory、Belief、Relationship、Goal、Plan 构成一次原子 NPC Meta 更新单元。NPC 可以提出 Dialogue 与 Action Intent，但实际发布/执行有独立授权和处理路径。

本章只管理 Agent Cognitive Response。即时战术/Reaction/自动效果按 §0.1 独立执行，不等 Gate / EVA；action_intents 可表达宏观行为提议，不能据此要求 LLM 生成每一次机械 Tactical Intent。EpisodeObservation 的目标边界见 §7.5；现有代码须按来源覆盖显式迁移，不宣称已替换。

| 所有者 | 职责 | 边界 |
|---|---|---|
| NPC Cognition / Perception / 共享提交设施 | Cognition 管 Meta / Task / 模式 / Gate；Perception 管证据、Observation／Inbox 与窗口保留，Cognition 管 Gate 采用／pending／processed 与 EVA 覆盖，使用 Session 游戏时间；两者按既有协议协调完成，共享设施保证版本/幂等/事务/可靠交接 | 按 §0.3 分责，不成为持有全部状态的中心 SM；不执行 LLM 主观推理或管理物理 Context |
| Agent Host | JEV / EVA 模型执行、Prompt / Context Builder、Interactive Context 复用/释放、Background One-shot Context、授权 OB 增量/失效通知传输、超时重试取消、Token Budget / Prompt Cache / KV Cache、Tool 传输与调用日志 | 不拥有或持久管理权威游戏状态、Meta、任务完成或行为结果；不做语义筛选 |
| NPC LLM | 基于完整授权 Meta 与观察决定主观认知变化、对白和候选行动 | 只生成预定义 Schema 的非权威数据；不决定身份、任务资格或世界事实 |
| Action Execution | 受限 Action Intent → 稳定 command_id / Typed Command → 负责 Handler / 必要 RE → 领域接口与共享提交 | 独立 Command Receipt；动作成功不是 EVA 完成条件 |

统一逻辑流 **NPC Cognition / 授权 Perception → Host → NPC LLM → NPC Cognition / 共享提交**。本章后续沿用“SM”称呼既有任务/观察协议入口，其目标内部写入责任按 §0.3 分配。Cognition 创建/批准任务，Host 仅组织调用并传输 Result，Cognition 确定性验证并通过共享设施原子提交 Meta / 唯一 Result / 完成及交接。Host 的可信适配身份不使模型输出获得内部领域写权限。

`interactive / inactive` 是 SM 管理的当前 NPC 模式状态；`interactive / background` 是 Evaluation Mode。Interactive 活跃（包括模型请求间空闲）期间，主观 Memory / Belief / Relationship / Goal / Plan 和自主决策均交当前 Interactive LLM；不创建新的 Background EVA 或额外 Memory / Cognition LLM。每条新 OB 均经 Cognition Gate 决策；JEV 模型分类可选，不要求逐条调用。授权观察按事件顺序增量追加，不修改运行中请求、Context 或 KV Cache。

Inactive 不维持持续运行的 Interactive LLM Context。SM 的 Lightweight Gate 可决定优先 Background EVA、Deferred 批量调度或获准 Safe Retention / No-op（§9.8–§9.9）；可选轻量分类由 Host 执行、SM 验证采用，不代 NPC 生成 Memory / Belief。Background 使用一次性 Context，不创建/恢复/激活 Interactive Agent，也可提出行动。Gate 不为 EVA 语义筛选或排序 NPC Meta，实际模型仍可替换。

### 9.2 标识、状态与提交资格 `[PROPOSED; NOT IMPLEMENTED]`

| 标识 / 状态 | 含义与所有者 |
|---|---|
| session_id / npc_id | SM 管理的 Session 与其内稳定 NPC 身份 |
| evaluation_id | SM 本地运行时中可唯一定位的一次逻辑 EVA 任务，也是 Meta 提交幂等键；不是认证凭证 |
| EvaluationStatus | SM 持久管理有效、运行、失败、完成和取消状态；候选编码 authorized / running / failed / completed / cancelled |
| NPCStateVersion | SM 的认知状态版本；任务记录预期版本，示例字段 expected_npc_state_version |
| observation_work_id | SM 关联未完成 Observation Work；模式切换/重试不重复创建逻辑工作 |
| invocation_id | Host 一次模型调用尝试；同一有效 EVA 可多次 Invocation |
| context_id | Host Context 引用；一个 Interactive Context 可服务多个 EVA |
| command_id | Action Execution 独立稳定幂等键，不能用 Evaluation ID 替代 |

有效/运行中的任务才可选择新 Result；失败、完成或取消任务不能写入新结果。已完成任务的相同 Result 重试仅返回原 EvaluationReceipt，不再次写入；取消任务的迟到提交拒绝，新 Invocation 不能恢复资格。调用方不可自行改 Status 或刷新版本。模式切换原子撤销旧有效任务并创建新 Evaluation，不需要独立模式代次计数器，也不依赖 Host 内存状态。

同一 NPC 的有效认知 EVA 串行授权与提交；切换事务撤销旧有效任务后才使新任务有效。旧物理 Invocation 可仍在途，但不再有提交资格；一个 Interactive Context 可依次服务多个 Evaluation，无需模式代次计数器。

### 9.3 请求与最小提交接口 `[PROPOSED; NOT IMPLEMENTED]`

SM 持久 Task 保存 Session/NPC、Evaluation Mode、授权范围、NPCStateVersion、观察/Work、冻结完整 Recent OB 快照、固定 pending 覆盖及已选结果/处理状态。NPCEvaluationRequest 是 SM → Host 的模型运行请求，不同于 P0 RuleEvaluationRequest：

```yaml
schema_version: npc-evaluation/0.1  # 候选消息版本，具体约束待冻结
evaluation_id: eval.guard-a.bg.005
mode: background
reason: significant_observation
observation_work_id: work.guard-a.005
expected_npc_state_version: 8
authorized_npc_meta_ref: meta.guard-a.008.complete
recent_ob_snapshot_ref: recent.guard-a.eval.005  # Task 创建时完整授权窗口，含 processed / pending
covered_pending_observation_ids: [obs.npc.guard-a.0005]
source_observation_ids: [obs.npc.guard-a.0005]
# 受控运行环境绑定可信主体；Task 保存 Session/NPC/权限/版本等
# Background 不需要 Interactive Agent 或既有 context_id
```

候选提交入口仅接收逻辑任务与原始结果：

```python
submit_npc_evaluation_result(
    evaluation_id: str,
    result: NPCEvaluationResult
) -> EvaluationReceipt
```

SM 从 Task 恢复 Session、NPC、模式、版本、Observation 与授权范围；调用身份由可信运行环境提供并核验，不接受 LLM 自报身份/权限。invocation_id / context_id 可用于日志关联，不是必填提交参数。不再需要额外 Proposal 提交信封或一组由调用方重复提供的可信元数据。

| 方向 / 接口 | 语义 |
|---|---|
| SM → Host NPCEvaluationRequest | 已授权 Task、完整授权 Meta／Task 冻结完整 Recent OB List、当前玩家输入（适用时）；Host 执行对应模式 |
| Host → SM submit_npc_evaluation_result | evaluation_id + NPCEvaluationResult；返回结构化 EvaluationReceipt 或验证错误 |
| Host → SM 授权 View / Observation 读取 | 提供完整授权 Meta、事件观察/当前感知；读取不完成任务 |
| Host → SM Runtime 状态 / Gate 分类反馈 | 非权威调用失败/取消/Context 状态或分类候选；SM 维护 Task 与领域结果 |
| Action Execution → SM Typed Command（§3） | 独立稳定 command_id、受限 Actor/Intent；按 §6 提交与查询 Command Receipt |

EvaluationReceipt 只是 EVA 的结构化处理反馈，可包含任务状态、Meta 提交版本、确定性验证错误及 Dialogue / Action Intent 交接信息；类型待冻结，不新增独立服务。读取/状态查询复用本地 Task 持久记录。不要求 Host 独立 ACK，也不要求独立领域 disposition 或模式写入握手。

**固定 EVA 输入 `[DECIDED; NOT IMPLEMENTED]`：** 创建 Task 时固定 NPC 认知版本、本次 pending OB／Work 覆盖，并冻结当时整个仍在游戏时间窗口内、授权且有界的 Recent OB List（含 processed 与 pending）。Task 保存快照引用／版本及原始任务证据；同一 evaluation_id 重试读取原快照，不重读滑动后的列表。processed 仍可影响后续 Meta 推理，但不重复成为处理义务。合法提交仅完成本 Task 固定覆盖的 pending；在途新 OB 进入同一列表并经 Gate 决策，需 EVA 者交后续任务，不改旧输入或完成范围。同 NPC 只有一个有效 EVA；Interactive Context 复用须保持与 Task 冻结输入等价，旧 Token 中过期 OB 不重新获准为 Recent。恢复输入明确原始时序与到期事实，不新增独立 Pending／Historical List。

### 9.4 NPCEvaluationResult、原子 Meta 与结果幂等 `[PROPOSED; NOT IMPLEMENTED]`

两模式使用预定义的同一/兼容 Schema，允许不同 Prompt、Context 和模型。LLM 生成符合 Schema 的数据，不定义 Schema。七字段概念结构保持：

```json
{
  "dialogue": null,
  "memory_updates": [],
  "belief_updates": [],
  "relationship_updates": [],
  "goal_updates": [],
  "plan_updates": [],
  "action_intents": []
}
```

所有字段可为空；全空 Result 仍可合法完成 EVA。原始数据不含可信身份、授权或任务状态。

**Meta 整批验证、原子提交**：Memory / Belief / Relationship / Goal / Plan 一起确定性校验 Schema/类型、NPC 身份/权限、Observation / Memory 引用、NPCStateVersion / EvaluationStatus、允许字段、幂等和数据库约束。任一 Meta 更新非法则整批不提交、也不选定最终 Result，返回结构化错误，由同一当前有效 EVA 有界修正；不能出现 Goal 拒绝而依赖它的 Plan 已写入。

SM 不判断自然语言 Memory 是否忠实于 Observation，不自动修改 Belief 文本；引用存在且授权不等于语义真实。NPC 可以形成错误 Belief，不改变 World Fact。MVP 不引入 Semantic Validator LLM。避免将未成功动作写为已发生 Episode 是输出约束：LLM 必须等待已提交事实/观察，SM 只核验结构化引用与权限，不声称能证明文本忠实。

**每 EVA 最多选定一份最终 Result**：首次通过 Schema 和整批 Meta 验证的 Result，由 SM 在同一 SQLite 事务中重验任务有效性与版本，持久选定 Result / 稳定内容指纹，原子写入全部 Meta、必要输出交接记录和任务完成状态。取消/提交竞争以此事务边界决定，不能先检查任务再在另一事务写 Meta。

- evaluation_id 是 Meta 幂等键；同一已选 Result 重复提交返回原 EvaluationReceipt，不重复认知更新或派发。
- 已有选定结果时，同 Evaluation 提交不同 Result 拒绝；最终结果不可替换。具体稳定比较/指纹规范待冻结。
- 选定之前的非法输出允许同一有效任务有限修正；Timeout / API Error 由 Host 在有效 EVA 内有界重试，Schema 非法重新生成，Meta 非法用结构化错误修正。
- 单次 Invocation Timeout / API Error / Schema 非法 / Meta 验证失败不立即使整个 EVA 最终 failed：任务有效且预算未耗尽时保持 running，允许同一 evaluation_id 使用新的 invocation_id 有界重试/修正。只有重试耗尽或明确无法继续才由 SM 持久记录最终 failed，保留未完成 Observation；模式切换为 cancelled，取消任务拒绝迟到新结果。
- 提交响应丢失先查该 evaluation_id 已持久结果，不盲目重新生成。已提交 Meta 不因反馈丢失而回滚。

### 9.5 模式切换不等待旧 EVA `[PROPOSED; NOT IMPLEMENTED]`

Background → Interactive：SM 在短 SQLite 事务中撤销旧有效 EVA 的提交资格（cancelled），保留此前已合法提交 Meta，移交未完成 Observation Work，记录 interactive 状态并创建新 Interactive Evaluation ID。新任务读取最新完整授权 Meta、未完成观察及当前玩家输入；Host 创建/复用 Interactive Context，并尽力取消旧 Background Invocation。

**不等待旧调用结束、失败回执或 ACK**。旧调用可在物理上迟到返回，但取消任务不能提交，新 Invocation 也不能复活它。若旧结果先合法提交，其 Meta 与输出交接已持久，切换保留且不重做；已经完成的任务不作为未完成 EVA 重新执行。独立已交接 Command 的授权、取消或执行按 Command 流程处理，不靠 EVA 状态伪装撤销已执行动作。

Interactive → Inactive 同样由 SM 原子撤销旧有效 EVA、保留 Meta/可靠交接与未完成 Work，更新当前模式后授权 Background；Host 释放 Context。不需要等待旧 EVA。版本冲突由 SM 反馈并决定合法任务/版本调整或撤销后新建任务，Host 不自行恢复资格。重启依据 SM 持久 Task / Result / Work 对账，全部模型调用在写事务外。

### 9.6 EVA Completion、Action Execution 与 Feedback `[PROPOSED; NOT IMPLEMENTED]`

Meta 合法时原子提交，Action Intent 的领域有效性和实际执行独立处理：非法 Intent 单独拒绝，不回滚 Meta；合法 Intent 交独立 Typed Command，SM 按需调用 Rule Engine 并最终提交，以独立 CommandReceipt 表示提交/拒绝/冲突/pending_choice（对应规则 needs_choice）。

SM 必须在完成 EVA 的事务中可靠记录每个 Action Intent 的交接（或明确拒绝/no-op），并分配/持久关联稳定 command_id（例如关联 evaluation_id 与 Intent 序号，但仍是独立命令键）。执行派发可从本地持久交接记录恢复，重复派发复用同 command_id；不建立独立服务或 Host 权威游戏队列。Meta 成功不意味着行动成功，EVA Completion **不等待 Action Execution 成功**。

Dialogue 发布也独立检查受众、结构化可观察事件引用与叙事权限，并可靠记录发布/拒绝/待处理交接；SM 不承担台词的自然语言真实性判断。Narrator 不叙述未经提交的行动成功。

SM 内部 ObservationProcessingStatus 根据必要认知处理和可靠输出交接状态维护；获准 Safe Retention / No-op 可持久完成本轮认知工作，全空 Result 可完成 EVA，均不要求生成长期 Memory。完成只覆盖 Task 明确关联且实际处理的 Work 范围，调用在途新到达的 OB 不随旧 Result 一并完成。processed OB 在到期前仍是 Recent OB，不能因读取/再次入 Context 重排同一工作；读、Context Append、LLM 返回、模型失败或任务取消本身不代表处理完成。内部 Completed Cursor 不跨未完成认知/未可靠交接项或投影缺口，无独立 ACK；清理不能改变水位语义。

Command 正在执行、失败或等待 choice **不自动使已完成 EVA / 已可靠交接的观察重新变为未完成**；未完成的 Command / PendingOperation 仍单独持久跟踪。动作失败反馈可送现有 Interactive LLM 继续动作交互，不自动重做完整 EVA 或再次写 Meta；若确需新的认知评估，由 SM 显式授权新任务，而非重放旧结果。

### 9.7 完整授权 NPC Meta、Belief History 与恢复 `[PROPOSED; NOT IMPLEMENTED]`

MVP 由 SM 提供该 NPC **完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan** 及有效 Recent OB（含 processed）；待处理 Work 范围另外明确，不能从 Context 中出现哪些 OB 推定完成。授权完整不意味着全量世界/他人秘密。首次构建或重建 Context、Background One-shot 输入完整授权 Meta，Host 只组装，不做 Semantic Retrieval、Memory Ranking、语义筛选或智能压缩，也不增加独立 Memory Agent。超出模型预算明确反馈/保留任务，不能静默漏掉 Meta；已过期 OB 不作为近期输入，受限未完成 Work 恢复见 §7.4。

已有 Interactive Context 可复用，后续按事件顺序增量追加授权观察和已提交 Meta 变化，不要求重注入全量 Meta 或窗口外历史 OB；每次 EVA 仍须提供与 Task 冻结完整 Recent OB 快照等价的有效输入。Memory Persistence 与 Context 资源管理保持分离；MVP 可预算保护、释放/重建 Context，不增加语义总结压缩。更复杂检索/压缩后置。

**Context 中 OB 到期 `[DECIDED]`：** SM 更新权威有效性并停止将其作为新的 Recent 输入；不强制删除现有 Context 历史 Token，不自动 Compression / Compaction。Host 可在下一次 Invocation 前追加 SM 授权的结构化失效通知（候选内容为 Observation ID、原始时间及已失效状态，Schema `[PROPOSED / OPEN]`）；不得异步修改执行中 Invocation 的输入、Context 或 KV Cache。通知本身不重新执行 EVA，不承诺 LLM 严格遗忘已出现文本。新建/重建 Context 不再提供过期 Recent OB；合法长期 Meta 自有持久生命周期，不因其来源 OB 到期而删除。

NPC Cognition 可以持久管理追加版本的 Memory / Belief / Relationship / Goal / Plan，保留旧内容、来源、当前版本与 Goal/Plan 状态。Adventure Package Initial Belief 与运行时 Belief 使用兼容结构；NPC LLM 可修改、降低置信度或放弃旧 Belief，领域只验证结构/引用/权限/版本/约束，不改写文本。全部历史 Goal 不等于当前待执行 Goal，记忆持久化不保证必然避免循环；本轮不新增导航知识图谱、目标树或防循环 Schema。

SM 持续不可用或持久化失败时，Session 停止权威推进，进入暂停/错误/待恢复流程；不能写库时不伪称状态已落盘。Host 不接管游戏状态，无影子权威副本或独立游戏执行队列。恢复依据 SM 持久 Task、已选 Result / Meta、可靠交接和独立 Command Receipt，不重做成功认知或行动；非战斗恢复必需，战斗中断精确续玩仍 Post-MVP。保留单命令响应丢失的幂等查询，不增加分布式协调系统。

### 9.8 JEV 的两个判断职责 `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

允许同一底层轻量 JEV 模型承担两种任务，但使用**不同输入、输出 Schema 与权限验证**，不能混用结果或新增 Memory Agent / 认知状态权威：

| 职责 | 许可输入 | 输出与采用边界 |
|---|---|---|
| Perception Judgment（§7.2） | 待判断 Signals 与可信事件时感知证据 | 逐 Signal Boolean 察觉候选；SM 验证后形成 OB；不生成 Memory / Belief / 世界变化，不替代 RE 机械检定 |
| Cognition Gate Judgment | 已确认察觉且授权的 OB、关联 NPC / Work 与必要调度信息 | 是否需及时认知评估的分类候选；SM 验证采用并路由；不重新判定察觉、不生成主观 Memory / Belief 或其他 Meta |

Cognition Gate 建议分类为 **Urgent / Deferred / Irrelevant / Uncertain（或 Failure）**；分类语义见 §9.9，枚举编码、请求/返回字段和失败错误形状仍 `[PROPOSED / OPEN]`。沿用既有 Gate 分类反馈与持久 Work，不新增独立公共提交/ACK。SM 核验可信调用、任务用途、NPC / OB / Work 归属、分类类型与请求覆盖范围；未知/重复/缺失项、超时、Schema 错误不作为 Irrelevant 或自动完成。Host 执行模型，SM 持有判断采用、模式路由、调度与持久结果。

JEV 不是每条 OB 的必经模型步骤：确定性规则或批量分类均可使用，不必为普通 OB 单独发起 Invocation；模型/Prompt/阈值/成本预算不冻结。Interactive 模式也可选用 Cognition Gate 重要性分类，但主观更新仍独占于现有 Interactive LLM。

每条新 OB 必须有可靠 Cognition Gate 决策；无需 EVA 直接持久标记 processed，需 EVA 或未决／失败保持 pending。模型分类可选；分类不是第三种 OB 状态，也不裁定永久记忆价值。

### 9.9 按模式与优先级调度 EVA `[DECIDED; NOT IMPLEMENTED]`

| Gate 语义 | Inactive NPC | Interactive NPC |
|---|---|---|
| Urgent | 优先授权一次 Background EVA，联合考虑七字段输出；不自动生成长期 Memory | 优先授权现有 Interactive LLM 的下一轮 EVA，不创建 Background EVA |
| Deferred | 保留 Recent OB 与 Pending Work，积累多个 OB；定期调度或最长等待到达时批量 Background EVA | 随正常交互或定期 EVA 批量处理，复用 Context |
| Irrelevant | SM 可持久批准 No-op 完成本轮处理，无须 Background EVA；到期前仍可为 Recent OB | 可受控 No-op，不要求逐条 JEV 或完整 EVA；到期前仍可为近期信息 |
| Uncertain / Failure | 保守保留 Pending 证据，重试/确定性保底并纳入有界调度；不能当作 Irrelevant 清理 | 保留工作，由 SM 路由现有 Context 的后续处理；不启动第二个认知 EVA |

同一 NPC **只允许一个有效认知 EVA**，沿用 §9.2 的串行授权、版本检查与模式切换，不另设并行 Memory/Cognition 队列。新 OB 到达已有 EVA 时，Urgent 提升后续授权优先级，其余按序合并或排队；不能改在途输入或偷扩旧 Task 的完成范围。迟到 Gate 结果须按 SM 当前模式和 Work 状态重新路由，不能唤起旧 Background 任务或重开 processed OB 的 Work。Safe Retention / No-op 是处理结果，不能被解释为立即删掉 Recent OB 或替代长期 Memory Formation。

**定期 EVA `[DECIDED]`：最大调度等待期限必须严格小于相应 OB Lifecycle，并留出执行余量。** 候选约束可表达为同一游戏时间尺度下 `max_scheduling_wait + execution_margin < applicable_ob_ttl`，变长 TTL / 批次要考虑各 OB 的剩余到期窗口，不能反复合批重置最早等待期限。具体周期、最长等待、执行余量与游戏时间/Host 运行耗时的对应方式 `[OPEN]`。正常运行应在到期前完成必要认知处理；周期短于 TTL 并非绝对完成保证。

Background 调用失败、LLM 超时、Mode Switch、Game Time 跳跃、Context Budget 不足、同 NPC 已有运行 EVA、崩溃恢复均可能越过期限。SM 更新有效性并保护 Pending Work / 证据，按原 Task/Result/Receipt 对账后合法续处理或受控 No-op，不能因 TTL 到期丢失、伪造 processed 或盲目重做已提交结果。Expiry 是 Retention 转换，不是唯一 EVA 触发条件；处理完成也不要求 Memory 写入。

## 10. Adventure Package → Session / 负责领域（P1）

**[DECIDED]** Package 是静态、版本固定的数据定义；Session / 世界领域负责加载与一次初始化，Combat Handler 组织 Encounter，相关领域经共享设施提交。保留当前 SM 公开入口，不要求单个模块独占这些数据与业务。统一入口已有受限本地实现（§1.6）；以下候选消息是目标契约 **[PROPOSED]**，未冻结／未接线分支仍 `[NOT IMPLEMENTED]`，目标字段在 [Adventure Package §9.1 / §9.1a](./ADVENTURE_PACKAGE_SCHEMA.md#91-统一-package-loading--validationap-0104) 定义：

创建与恢复必须遵循 §2.4 的完整实例化要求：Package 仅作创建参照，已存在实例的配置／状态从所属领域记录恢复和读取。Schema39 已迁移当前有效配置读取闭包；§1.4 的模板补字段属于历史行为，动态生成／一般依赖创建等剩余缺口见 §1.6。仅固定包版本或增加定义索引均不能满足此要求。

```text
load_adventure_package(package_source)
  -> PackageLoadResult(valid | invalid, structured errors / warnings,
                       approved identity / digest / effective RulesetBinding when valid)
create_session(CreateSessionRequest)
  -> Session ID + creation result + limited metadata
```

加载内部完成安全解析、Schema、引用、规则绑定、声明式操作与必要元数据检查，不暴露半验证状态或独立验证服务。必要机制不支持、Schema/非法引用阻止批准；非核心可选限制可明确 warnings，不能运行时假装支持。valid 后固定 adventure_id / package_version / package_digest / 生效 RulesetBinding。静态验证不证明剧情可玩性/平衡，来源元数据不自动证明版权合法。

CreateSessionRequest 使用 command_id、批准 Package 的身份/摘要和 **players[]**（每项 player_id / pc_template_id，MVP 严格一玩家一 PC）。PC Templates 是 Package 内完整且机械属性经规则验证的只读定义，不要求外部 pc_build_ref 或独立构建服务。principal_id 取自可信认证环境并验证 player/角色控制关系；创建前以 **(principal_id, command_id)** + Fingerprint 幂等，相同请求返回原 Session，不同内容冲突。session_id 由 SM 生成并返回，不新增创建请求/Receipt ID；普通游戏命令仍用 (session_id, command_id)。

Session、世界、Character / Cognition 等负责接口在共享短事务核验固定内容与创建键，原子初始化 SessionRecord / WorldState / 当前必要 Actor/NPC Persistent State / 选定 CharacterState / 入口 Scene / RNG，并保存创建幂等结果；失败不留下半初始化有效 Session。返回有限元数据，不泄漏隐藏世界。Scene 按需初始化一次、NPC 为 Session 级唯一实体，重访不重置；EncounterDefinition 可选，Combat Handler 可组织具有可信规则数据的动态 Encounter。

两个规则调用场景复用 §4–§6，不新增执行协议：

| 场景 | 候选 operation_kind / 输入 | 处理边界 |
|---|---|---|
| Combat Handler 组织启动 Encounter | combat.start；当前相关 NonCombatSnapshot、固定 RulesetBinding、显式 RNGContext、强类型启动 payload | Engine 在 accepted 时返回 Typed Delta / ProposedEvents / RNGTransition，Handler / 相关领域共同建立遭遇/流程与必要状态；候选 combat.create 的具体字段 [OPEN] |
| 世界/效果领域判定 Trap / Hazard 触发 | rules.effect；适用 Snapshot、同一规则绑定/RNG 输入、强类型效果 payload | Engine 算豁免/伤害/Condition，负责领域共同提交；按 AP-15 的具体类型校验 Actor；无行动 Actor 的受信系统/世界事件来源允许受控分支，source_ref / 权限编码仍 [PROPOSED / OPEN]，见 §3.1 / §4.1 |

上述操作/类型 **[PROPOSED; NOT IMPLEMENTED]**。同命令世界效果与机械结果可在提交前完整求值时统一原子提交；若来源 WorldEvent 已提交，再触发效果则可靠交接独立稳定命令，去重/恢复，不承诺跨两个已提交事务原子性，不重复已提交骰点/伤害/奖励。详细编排与复杂 Effect Schema 为 [OPEN]。

EventDefinition 是静态 Trigger / Condition / Effect 声明，CommittedWorldEvent 由 SM 经受控命令提交；动态事件无需全部预定义。世界领域按作用域管理触发历史与允许效果，规则计算交 Engine，不增加独立 Event Engine 服务或任意脚本。RuntimeState 不写回 Package；公开资料只用原创合成示例，First Blush 内容/派生资产仍留本地私有。

## 11. 必须统一的错误和状态（P0）

| 错误/状态 | 权威语义 | 状态与 RNG |
|---|---|---|
| `unauthorized_actor` / `forbidden` | 身份或 Actor 控制越权 | 不提交 |
| `schema_invalid` | Command / Rule Request / Result Schema 或 Required / Optional 类型校验失败，属于输入/契约错误 | 不提交；不映射为规则 rejected |
| `ruleset_binding_mismatch` | Session 固定绑定与实际规则/数据/求值器不匹配 | 禁止求值，不提交 |
| `unsupported_rule` | Engine 不支持操作 | 不提交 |
| `rule_rejected` | RuleEvaluationResult.rejected 的结构化规则拒绝 | 不提交机械变化/事件/RNG |
| `version_conflict` | Snapshot/ReadSet 过时 | 不提交；刷新授权视图，修改 expected_world_version 等请求内容须新 command_id，原样重试仍用原 ID |
| `idempotency_conflict` | 同一 command_id 不同指纹 | 不提交 |
| `choice_pending` | 等待已授权的前置选择 | 只允许独立、明确的 PendingOperation 元数据 |
| `committed` | 负责领域已通过共享设施原子提交全部效果 | RNG、状态、Event、Receipt 全部提交 |
| `committed_response_failed` | **已提交**，但传输/叙事失败 | 保留原提交；调用方查 Receipt |
| `internal_error` / `rule_evaluation_error` | Engine / SM 运行时异常，独立于四种规则结果与 NPC EVA 状态 | 未提交不改变权威事实/RNG；提交未知先查命令键 |
| `transport_error` / `timeout` | 求值或响应传输故障，不是规则拒绝 | 不凭错误推定提交；按 (session_id, command_id) 查 SM 记录 |

**禁止混淆：** `miss`、`save_success`、`attack_failed_after_roll` 可能是**合法机械结果**（有 RNG/行动成本），不等价于 `rule_rejected`。当前 Bridge 的事件型拒绝/回执映射需逐路径核对，避免迁移时改变 D&D 语义。

## 12. MVP 验收用例（需自动测试）

1. **Inventory + Mechanics 同事务：** 同一 Actor 使用有限药水；库存、HP、Action Economy、RNG、事件、Receipt 一次提交，任何验证/事务失败全部不写。
2. **确定性求值：** 固定 Snapshot、Ruleset/Data、Evaluator revision、PRNG State 和 Intent，结果与骰点一致。
3. **无副作用拒绝：** 无权限、资源不足、非法目标、未知规则、Schema 错误均不污染游戏状态或 RNG。
4. **合法失败有成本：** 合法攻击未命中仍完整记录允许的 RNG 消耗和回合/行动成本。
5. **重复与冲突：** 相同 `command_id` 只提交一次；指纹不一致拒绝；竞争取同一物品不会出现两个成功 Owner。
6. **提交后掉线：** 模拟 SQLite COMMIT 成功、HTTP 响应丢失，重新查询/重试拿回原 Receipt，事件不重复。
7. **敌方 Agent 自主性与即时战术分离：** 至少一名敌方 Sub-agent 独立提出可核验的目标/宏观策略及战后认知，合法采用后实际影响 Combat Policy 的后续行为；即时 Typed Intent 经 RE 求值 + SM 提交，无每次战术 LLM 依赖，不冒用 PC 身份或把纯固定策略冒充 Agent 自主性。
8. **多目标与多 Activity：** 效果、资源支付归属与有序事件都对齐现有行为；失败回滚无“半个目标已受伤”。
9. **感知隔离：** A 目击开门、B 后到只看到门打开；玩家/NPC/Narrator 不得得知无权知道的历史事件或 GM Secret。
10. **记忆与 Context：** 重要 Observation 可持久化而不触发 Active Context 压缩；NPC Evaluation 重试不重复写认知/执行动作。
11. **保存恢复边界：** 无活跃战斗的 Session 重启恢复；中断战斗明确标记，不将部分已提交机械变化悄悄丢弃。
12. **迁移对照：** 与旧 API 在受支持合成用例上逐项比较合法性、目标、资源、伤害、Effect、事件顺序、显式 RNG 前后状态/机械骰点结果、拒绝与回滚；可选 draws 不要求完整底层轨迹。

验收使用**公开的原创合成 Fixture**；*First Blush* 端到端场景在独立私有资产中验证。

**v0.5 P0 补充验收目标（尚未执行）：**

- CombatSnapshot / NonCombatSnapshot 分支及 Required / Optional 校验；实体字段不得按 Intent 裁剪，跨实体/效果依赖完整，RNGContext 不混入 Snapshot。
- 同 command_id 经 Request / Result / CommandReceipt 关联；规则绑定不匹配（含生效 Homebrew 修订）禁止求值，operation_kind / payload.intent_type 分层校验。
- 四种 Result 分支满足 §5.1 字段约束；合法未命中/被反制且支付成本仍 accepted；Schema、运行时、传输错误不映射成 rejected。
- 拒绝任意路径、未知 Delta kind 或整份 Snapshot 覆盖；多目标/Effect/Reaction 连带变化完整原子提交，失败无部分状态。
- ProposedEvents 无权威事件 ID/序号；SM 同事务保存正式事件/Delta/RNG/CommandReceipt/Outbox，失败不发布，SM 不从事件重算 HP。
- accepted 无随机消耗可返回相同 RNG state，冲突/回滚不推进权威流；不依赖完整 draws 轨迹才允许验收。
- Availability Query 无掷骰、状态写入、Delta、事件或回执；原因经授权投影，查询 available 后状态变化仍须正式执行重验。

**v0.7 世界命令补充验收目标（尚未执行；使用原创合成场景）：**

- 普通游戏操作统一 submit_command / command_type，信封不含旧 kind / controller_id 别名；创建、NPC Evaluation 与查询/回执生命周期独立，controller.kind 控制策略保留。
- Actor 行动缺失/伪造 actor_id 被拒绝；受信系统/世界事件分支无行动 Actor 时仍校验 principal、机械来源、目标和类型范围，不生成虚构 NPC。
- GM 裁决在掷骰前固定能力/技能、DC、后果和依据；SM 无语义审核 LLM，机械计算仅 Engine；无法表达的操作/后果尽可能在 RNG 前发现。
- 简单动态对象/连接提交后获得 SM 稳定身份、原样重试返回同一结果，静态 Package 不变，DM/Player/NPC 查询投影遵守权限。
- Conditional World Effect 使用可信规则结果/世界状态，不靠模型自报成功；完整同命令效果原子提交，已提交事件的后续命令可靠幂等，不重复伤害/领奖/已提交骰点。
- unsupported 不新增 CommandReceipt 状态，合法机械失败不误报 rejected；确定性拒绝不强制重调 LLM，响应未知先查回执，Narrator 不泄漏内部错误或编造世界事实。

**v0.8 Perception 补充验收目标（尚未执行；原创合成场景）：**

- accepted 未达目标仍可提交实际 Signals；rejected / unsupported 或未提交行为不产生对应 Signals；Signal ID 在 Event 内唯一、Scope 可确定计算。
- NPC 移动/感官变化后仍按事件时证据处理；大型 world Scope 分批 Discovery 可恢复、去重且覆盖 Inactive NPC，不跳过未完成投影。
- 同 Observer / Event 的 JEV 批量结果必须完整且逐项 Boolean；缺失/未知/重复 ID、超时或 Schema 错误不转 false，也不触发 EVA。
- 多个已察觉 Signals 默认一条 Observation；全 false 可无 Observation 完成；分时新观察保留。仅听到声音的 Context 不泄漏事件类型/真实行动者/隐藏目标。
- get_scene_view 的 NPC 投影与既有感知入口等价受限；正式感知检定仍交 RE，既有 Gate / EVA / Cursor / Completion 不被感知判断替代。

### 12.1 v0.2 NPC 双模式合成验收 `[PROPOSED; NOT IMPLEMENTED]`

下列是待实现的验收目标，本轮未运行模型或数据库故障测试；对应 Agent §11.3、State Machine §11.2。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A13 | Interactive 新增 Observation | 原 Context 按序追加；主观认知由当前 Interactive LLM 处理，必经 Gate 决策（模型可选），无逐条模型强制，新 Background / Memory / Cognition LLM 调用数为零 |
| C-A14 | Active Context 暂时无模型请求，重大事件到达 | SM 批准下一次 Interactive Task，Host 执行请求；在途调用期间新增输入排队，不修改执行中请求/KV Cache |
| C-A15 | Interactive Result 含 Dialogue、Belief、Memory、Action Intent | Meta 整批验证原子写入，行动独立 Typed Command，不回滚合法 Meta；全空 Result 合法 |
| C-A16 | Inactive NPC 经 Gate 一次 Background Evaluation 产生行动 | 无 Interactive Agent Context；同一 NPC 权限与共享命令路径，临时 Context 调用后释放 |
| C-A17 | 低价值 Observation / 轻量模型不可用 | 获准 Safe Retention / No-op 持久完成工作、TTL 前仍 Recent；轻量模型不可用保守保留 Pending，关键证据不丢失 |
| C-A18 | Background → Interactive 与提交竞争 | 原子取消旧有效 EVA 并新建，不等旧反馈；先成功 Meta/可靠交接保留，迟到取消任务结果拒绝 |
| C-A19 | Model Failure、重投、版本冲突、完成事务前后崩溃 | Evaluation ID / 唯一 Result / 原子 Meta 与独立 Command ID / 交接防重复，未完成认知/交接缺口不跳过 |
| C-A20 | 任一模式 Memory 持久化成功 | 不强制 Compact / Rebuild；MVP 仅预算保护与必要的安全释放/完整 Meta 重建，不新增智能压缩 |

### 12.2 v0.3 职责与统一协议验收 [PROPOSED; NOT IMPLEMENTED]

以下为待实现的原创合成测试目标；本轮仅静态文档检查。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A21 | SM 创建/批准 Task、采用 Gate 分类 | Host 只运行模型/Context/Tool 传输；领域模式、保留、任务与完成状态归 SM |
| C-A22 | 一 Evaluation 多 Invocation，一个 Context 多 Evaluation | 逻辑与运行时标识分离；Invocation/Context ID 非提交必填，不改变 P0 命令信封 |
| C-A23 | 自报身份/权限/任务状态/版本、仅 Evaluation ID | SM 核验可信主体与 Task 关联的 NPC、范围、引用、版本、状态及幂等，ID 不能认证 |
| C-A24 | 两模式 Result 与最小提交 | 同一/兼容七字段、允许全空；仅 evaluation_id + result，Task 恢复可信关联 |
| C-A25 | 无 ACK、可靠交接后行动失败/needs_choice | EVA / 必要认知处理可完成，Command 独立回执/续项不触发整次 EVA 重做；读/追加/模型返回不完成 |
| C-A26 | Dialogue 发布与 Background Action Intent | 发布验证受众/叙事权限；行动共享 Typed Command、Rule Evaluation、SM Commit |
| C-A27 | SM 持续不可用、提交响应丢失及恢复 | 停止权威推进，Host 无影子状态/游戏队列；查原 Receipt，恢复非战斗，战斗精确续玩后置 |

### 12.3 v0.4 简化 EVA 合成验收 [PROPOSED; NOT IMPLEMENTED]

仅定义待实施用例，不代表本轮已执行运行验收。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A28 | 最小提交、可信运行环境与 Task 恢复 | 只有 evaluation_id + Result 参数，Task 恢复可信关联，Evaluation ID 不认证；Invocation/Context 非必填 |
| C-A29 | 每 EVA 唯一结果 / 修正窗口 | 相同已选 Result 返回原反馈，不同拒绝；选定前非法输出可在有效任务内有限修正，Action 独立 Command ID |
| C-A30 | Meta 整批非法 / 取消与提交竞争 | 全部 Meta 原子写或全部不写；同事务验证 Task / NPCStateVersion 和选定结果，不依赖 Host 内存状态 |
| C-A31 | 切换遇到不可取消模型 | 原子撤销旧有效 EVA/新建，不等旧失败回执；最新 Meta/未完成观察/玩家输入交新任务，迟到旧结果拒绝 |
| C-A32 | 合法 Meta / 非法或失败 Action / Pending Choice | 可靠交接后 EVA 完成，不等执行成功；独立 Command Receipt，失败反馈不自动重做完整 EVA |
| C-A33 | Timeout / API Error / Schema / Meta 错误 / 重试耗尽 / 丢响应 | 预算内保持 running，同 evaluation_id / 新 invocation_id 修正；仅耗尽或无法继续最终 failed，切换 cancelled；先查持久结果，不复活旧资格 |
| C-A34 | 完整授权 Meta 与 Belief History | 六类 Meta + 冻结完整授权 Recent OB List（含 processed／pending），Host 不语义筛选/检索/排名/智能压缩，Context 增量复用；Belief 版本追加保留历史 |
| C-A35 | 非忠实 Memory / 错误 Belief | SM 只确定性校验引用等，不证明自然语言忠实、不改写文本、不新增 Semantic Validator LLM；不改 World Fact |

### 12.4 v0.9 OB Lifecycle 与调度合成验收 `[PROPOSED; NOT IMPLEMENTED]`

以下为实现期测试目标，本轮只做文档一致性检查；覆盖既有 EVA / Work / Cursor 的生命周期扩展。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A36 | Irrelevant No-op / 全空合法 Result | SM 持久完成处理，无需生成长期 Meta；processed OB 到期前可读为 Recent，重复投递/读取不重开同一 Work |
| C-A37 | 游戏暂停 / 墙钟流逝 / Game Time 跳跃 | TTL 仅据 SM Game Time；跳跃移除 Recent 投影，Pending 证据/任务受保护，processed 不因到期重新 EVA |
| C-A38 | 同一 OB 被多个 Meta 及历史版本引用 | 到期归档必要原始证据和来源；不能删成悬空引用，内部归档不自动作为 NPC 近期记忆 |
| C-A39 | 清理与引用提交、任务/交接/审计/幂等竞争 | 同事务保护检查；仅工作完成且全部保护解除才可清理，Cursor / Receipt / 重试语义不破坏 |
| C-A40 | JEV 双用途与错误批次 | Schema / 权限分离，Perception 只判察觉，Gate 只分类已察觉 OB；错误/缺失/超时不当 Irrelevant 或 processed |
| C-A41 | Inactive Urgent / Deferred / Irrelevant | 优先联合 EVA / 有界批量 EVA / 受控 No-op；最多一个有效认知 EVA，保留近期信息，不强制长期 Memory |
| C-A42 | Interactive 分类与在途新 OB | Gate 决策必经，模型分类可选且非逐条调用依赖；Urgent 下一轮优先、Deferred 批量、Irrelevant No-op；无新 Background，不改在途输入/完成范围 |
| C-A43 | 周期、合批、失败/超时/切换/预算/占用/崩溃 | 最大等待严格短于 TTL 且留余量，合批不重置最早期限；异常保留过期 Pending Work 并安全续处理，不谎称完成保证 |
| C-A44 | OB 已入 Context 后到期 | SM 更新有效性，下一 Invocation 可增量通知；不删除旧 Token、不自动压缩、不重做 EVA，重建排除过期 Recent OB |

### 12.5 v0.10 Event Evidence 合成验收 `[PROPOSED; NOT IMPLEMENTED]`

以下为后续实现测试目标；本轮仅以这些原创场景检查文档约束，不宣称已执行运行测试。

| ID | 场景 | 预期断言 |
|---|---|---|
| EV-A01 | 同一 Command 先在 A 发声再进入 B，或阶段间改变光照 / Conditions | 各 Event 按实际 Signals 阶段取证；相同 command_id / world_version 不足以共享变化字段，event_seq 不代替中间状态 |
| EV-A02 | 多 Event 的相关状态未变化 | 可共享可信不可变证据，仍保留各 Event / Signal 适用关联，不重复保存无关 Session 状态 |
| EV-A03 | 同 Event 多 Signal、候选重叠且 Scope 位于不同 Scene | 逐 Signal 发现后取 NPC / 环境并集，保留逐 Signal 候选关系；共享证据不扩大察觉权限，多个已察觉 Signals 沿用 OB 聚合 |
| EV-A04 | Scope 内失明、耳聋、被遮挡或 Inactive NPC | 全部进入候选；察觉阶段才判断能力/遮挡，Discovery 不预先判 Negative |
| EV-A05 | 缺失必要 Observer / Origin / 环境证据，处理时世界已变化 | 不用当前状态补齐、不默认 Positive / Negative、不让 JEV 猜事实；保留既有未完成工作，不假装候选为空 |
| EV-A06 | 零 Signal，或有 Signals 但候选确为空 | 区分合法空结果与缺证据；不生成空 OB、不调用无必要的 JEV，不复制无关感知状态，可靠记录完成 |
| EV-A07 | 大型已支持 Scope 分批、中断恢复及 NPC 随后移动 | 候选完整、去重可恢复，证据来自原子保存的历史依据；无当前态回填、无分页遗漏或跨越未完成水位 |
| EV-A08 | Event / Signals / Evidence / Outbox 任一持久化失败 | 同一 SQLite 事务全部回滚，无中间可见事实或后续 OB；提交后才允许 Perception Judgment |
| EV-A09 | Rule Engine 需要超出最小感知字段的机械状态；某事件中间阶段不可恢复 | 机械 Snapshot 保持完整依赖闭包；不能以感知 Evidence 替代，无法恢复阶段显式列为 OPEN 支持缺口 |

### 12.6 双路径与 Episode 原创合成场景 `[PROPOSED; NOT IMPLEMENTED]`

以下仅是设计推演和后续实现验收目标，不是已运行的 SM/RE/模型集成测试；不含受保护冒险内容。

| 场景 | Immediate Mechanical Response | Agent Cognitive Response / 观察限制 |
|---|---|---|
| 王宫拔剑 | 原创王宫接见中，PC 真正拔剑形成外显阶段；SM 用可信确定性/机械感知、已授权警卫 Combat Policy 与 RE 处理防卫、战斗触发及合法行动/Reaction，不等 Planner、JEV、Cognition Gate 或 EVA。私有“想拔剑”不产生警卫响应，未知察觉不算已看到 | 进入战斗前的拔剑 Event 仍阶段取证；战斗防卫及后续结果按 Turn／Round 聚合，不要求逐动作感知证据。柱后侍从只听到金属声时，EpisodeObservation 不得写“看到 PC 威胁君主”；之后 NPC EVA 才可提议恐惧/关系/记忆或长期追责，Narrator 只呈现玩家获准事实 |
| 火球术 | 原创庭院施法按受支持规则连续处理施法、合法 Reaction 窗口、范围/豁免、伤害、集中与连带效果；不为每条骰点/支付审计调用 LLM。确需中途选择时按 §8.3 暂停/持久保存/恢复，不占写锁；不是“所有人先看到火球才允许 Save” | 战斗施法、反制／爆炸和结果按实际已提交分支进入 Turn／Round 汇总；被反制不能捏造爆炸，不逐机械 Event 生成信号或感知证据。某 NPC 只看见爆炸或只听到巨响，就只聚合该部分，不自动获知施法者、隐藏 Reaction 或完整因果；机械 Audit 不复制进观察/Memory |
| LLM 故障 / 未完整察觉 | Host / JEV / EVA 超时不阻塞已授权即时机械链；机械所需事实缺失仍显式报告能力缺口，不默认 Positive，也不凭认知结果补准历史执行 | 可靠保留既有 Pending Work / 证据；不得谎称已察觉、已完成或自动形成长期 Memory |
| 版本升级 / 中途重试 | SM 锁定 RE 与最新 main 分别验收；Continuation / RNG / 资源仅采用一次，已提交阶段不回滚或重掷 | 非战斗阶段观察与战斗固定过滤依据不可变；聚合不能扩大授权，Episode 路由／覆盖／恢复与 Schema 仍 OPEN |

### 12.7 v0.4 聚合、两状态与固定输入验收 `[PROPOSED; NOT IMPLEMENTED]`

以下仅为后续代码测试目标，本轮未运行。

| 场景 | 必须断言 |
|---|---|
| 一 Turn 多攻击／Reaction，增加机械 Event 数 | 同 NPC／Episode 感官合批数不随内部 Event 数增长；不创建逐 Event 感知工作或取证链 |
| 本场参与者／外部／另一战斗中 NPC | 分别接收 Turn／Round／Round，固定路由与覆盖；加入退出去重，不双发同一经历 |
| 友善 NPC 被攻击 | 当前 Turn Reaction 使用既有效参数；聚合 OB／获准 EVA 提交关系后影响后续 Policy，无自动设敌对并行写入；关键等待释放事务 |
| A、B 无需 EVA，C 触发 EVA | A／B 直接 processed 但仍留窗口；Task 冻结 A／B／C 全部授权近期输入，A／B 可影响 Meta，只完成固定 pending 覆盖 |
| 在途新 OB／重试／窗口滑动 | 原 Task 输入不变，新 OB 经 Gate 排后续任务，无竞争 EVA；过期必要证据与幂等覆盖受保护 |
| 提前结束／聚合发布崩溃／旧逐 Event 入口迁移 | 最后未满轮可靠发布，边界幂等／来源映射可恢复，不重算机械、不重复 OB／Meta／Action |

## 13. 尚需显式批准或验证的开放问题

| ID | 问题 | 初步建议 / 决策要求 |
|---|---|---|
| C-01 | 各受支持规则的完整 Snapshot 依赖闭包与类型化组件映射？ | [OPEN]；逐规则核对状态读写、生命周期与权威/派生/临时数据，形成依赖矩阵；历史 `_LiveCombat` 盘点仅用于查漏，不规定目标结构或永久执行依赖 |
| C-02 | Engine 对外 `evaluate(...)` 与 NPC `combat.intent` 的最小 Python Typed Schema？ | 本草案用于语义审阅，字段名称/类型待代码适配论证，禁止先行声称已实现 |
| C-03 | PRNG 算法/编码及无消耗时 RNG 流版本策略？ | [OPEN]；显式状态/原子推进原则已确认，具体 wire format 与版本需实现对照和确定性测试 |
| C-04 | Interrupt / Continuation 的共同 ABI 与最小实施范围？ | §8.3 暂停/持久化/恢复/RNG 一致性和短事务原则 [DECIDED]；Result / Receipt 映射、前缀提交与 RNG 预留、交错/冲突、取消/到期和最小 MVP 路径 [OPEN; NOT IMPLEMENTED] |
| C-05 | 普通怪物的认知覆盖与 Combat Policy 配置？ | 即时战术不依赖 LLM 已 [DECIDED]；至少一名敌方 Agent 的宏观自主性仍需验收。哪些角色需要认知 Agent、策略选择/版本/目标授权与降级细节 [OPEN] |
| C-06 | 部分规则不支持时如何安全回退？ | `unsupported` 明确拒绝或人工裁决提议；严禁 Narrative 假装规则结果 |
| C-07 | 版本粒度及仅事件/元数据提交的 World Version 推进？ | [OPEN]；MVP 全局 OCC 保守方案，状态变更单调推进已确认，事件型提交推进细则不在本轮冻结 |
| C-08 | 活跃战斗崩溃中断后如何避免覆盖已提交结果？ | 明确 `combat_interrupted` 与安全恢复/阻塞协议；精确续玩 Post-MVP |
| C-09 | 消息版本、Fingerprint 规范及生效规则数据修订编码？ | [OPEN]；三字段 RulesetBinding 与含适用 Homebrew 的内容可区分性已确认，具体 canonicalization/摘要组合和候选消息版本需 ABI 审阅 |
| C-10 | PendingOperation 生命周期与 CommandReceipt 分支字段？ | [OPEN]；仅命令键查询、无独立回执 ID/ACK 已确认；具体持久性、过期与可空性由 SM 实施设计验证 |
| C-11 | EVA Task、输入冻结与唯一 Result 的存储／编码？ | Task 创建时固定 pending 覆盖、认知版本与完整授权 Recent OB 快照（含 processed）；只完成固定 pending，新到 OB 不改在途输入，原子 Meta／唯一 Result／可靠交接已确认；稳定比较、快照版本／恢复编码 [OPEN] |
| C-12 | Observation Cursor、投影水位、批次合并及内部 ProcessingStatus / Completed Cursor Schema？ | 需证明不跨越未投影/未完成项，明确必要认知处理、可靠交接及独立 Command 重入；具体类型待冻结 |
| C-13 | JEV 双职责 / 两种 EVA 模式的模型、Prompt、阈值、预算与取消能力？ | 同一模型可承担两个分离判断任务已确认；实际模型仍候选，通过合成场景测定漏判/延迟/成本，不固定技术选型或 SLO |
| C-14 | NPCEvaluationResult / EvaluationReceipt 的字段类型、元素约束、版本与错误映射？ | 七字段概念结构及两模式兼容原则已确认；JSON Schema、可信运行环境绑定和持久任务编码待审阅，不把草案当成已实现 API |
| C-15 | 完整 Effect / Reaction / 复杂组件 Delta 字段？ | [OPEN]；封闭 Typed Union、完整依赖与原子提交已确认，字段须对照现有生命周期与不变量盘点，禁止任意路径或 Snapshot 覆盖 |
| C-16 | combat.start / combat.create、rules.effect 与触发后续命令？ | AP-15 按操作类型校验 Actor 已 [DECIDED]；source_ref / 来源权限、具体字段与可靠编排仍 [OPEN]，见 §3.1 / §10 和 Adventure Package §11；不扩张为独立服务 |
| C-17 | 动态 World Operations 与 Conditional World Effect Proposal 的具体 Schema？ | [OPEN]；受限类型、SM 稳定身份、授权投影和提交边界已确认，完整 Object / Connection 字段、结果关联及复杂 Scene / 战斗地形生成未冻结 |
| C-18 | Observable Signal / Scope、结果条件与传播 Schema？ | [OPEN]；最小四字段/事件内 ID 与确定性范围原则已确认，具体枚举、复杂空间关系/传播参数、模板绑定与分时观察键仍待设计 |
| C-19 | 事件阶段采集协议、历史证据与正式感知检定的事务编排？ | [OPEN]；§7 的阶段对齐、最小完整证据与原子性已 [DECIDED]，真实 SM / RE 事件阶段及中间状态可恢复性、可信字段依赖/共享、历史引用/保留与完整候选分批仍须验证；无法恢复不虚构状态。RE 负责规则掷骰，RNG / command / 异步事务衔接不由 JEV 替代 |
| C-20 | 单一 Recent OB 窗口、保留与清理？ | 游戏时间有界窗口、pending／processed 两状态、多 Meta／历史引用及恢复／幂等保护 [DECIDED]；TTL 起点／值、容量／截断、证据归档与清理算法 OPEN；不新增独立 Pending／Historical List 或第三状态 |
| C-21 | Gate 分类及定期 EVA / 最长等待的具体协议？ | [PROPOSED / OPEN]；Urgent / Deferred / Irrelevant / Uncertain 或 Failure 编码、批次覆盖验证、周期/执行余量、游戏时间跳跃及资源耗尽恢复细节待评审 |
| C-22 | Context OB 失效通知与过期 Pending Work 的受限恢复输入？ | [PROPOSED / OPEN]；非 Recent 回注、来源权限及通知字段需设计；不修改在途请求/KV Cache、不自动 Compaction 或重做 EVA |
| C-23 | Turn／Round Episode／EpisodeObservation 的共同协议？ | 本场参战者 Turn、外部 Round、Episode 合批、固定过滤依据与机械审计分流 [DECIDED]；scope／origin 聚合算法、参与切换边界、来源覆盖去重、旧消费迁移、关闭／发布恢复与 Schema [OPEN; NOT IMPLEMENTED]。不再采用整场单一 Episode 或战后才聚合的目标 |
| C-24 | Mechanical Audit、StageFacts 与感知边界？ | 非战斗独立阶段证据、战斗 Episode 级过滤依据 [DECIDED]；完整机械依赖不裁剪，不逐机械 Event 发 Signal，不要求逐动作感知取证。真实来源映射、审计保留／重放、固定 RE／Adapter 与迁移仍 [OPEN; NOT IMPLEMENTED] |
| C-25 | 游戏核心事实访问、Session 内存生命周期与替换边界？ | SM＋RE 主线、领域状态责任与操作共享提交 [DECIDED]；已有受限实现见 §1.3。Session RAM 统一读、隔离候选、SQLite 增量提交后发布及故障恢复已 [DECIDED]（§2.3／§6）；整体 [NOT IMPLEMENTED]。World 候选组件/字段分类见专项草案 §3；具体组织、容量、API／版本与替换映射 [OPEN]，与 A1 / A2 一起验证，不新增平行待办；Evennia 仅可选评估 |
| C-26 | 动态能力与 Session 扩展如何受控启用？ | 能力目标及固定冒险基线 [DECIDED]；Coding Agent 可选；来源/版本/权限/预算/启用、在途绑定、行为状态迁移、失败处理 [OPEN; NOT IMPLEMENTED]，版本回滚不撤销已提交事实 |
| C-27 | 有状态 Combat Handler 与按需读取接口？ | 职责与校验分责 [DECIDED]，见 §0.3–§0.4 / §6.5；已有受限 Handler / Records，见 §1.3。统一世界修改协调、全部写入口接入及发布故障恢复尚 [NOT IMPLEMENTED]；完整推进/新增 API、调度预算、Continuation、读取依赖及锁/版本细化 [OPEN; NOT IMPLEMENTED]，不因类已存在扩大支持或删除校验 |
| A1 | 探索与战斗的操作编排分离 | [DECIDED] §0.5；当前探索活动/共享位置/受限战斗编排为部分基础（§1.3）。后续验证战斗移动与 World 投影、共享开合/解锁/取放/破坏的规则资格/成本/反应、入口 guard 和原子失败语义；完整集成 [OPEN; NOT IMPLEMENTED] |
| A2 | StateMachine 模块化与职责边界 | [DECIDED] §0.6；显式组合已有受限实现（§1.3）。逐步减少 Mixin，明确 Facts / Records 与支持组件依赖、库存投影单一权威、共用事务及回滚；不机械分层、不按物体设 Handler、不强制 ECS；剩余切片 [OPEN] |

**迁移名称对应（本轮检索）：** 更新前顶层跟踪文档未检出 W-01／SA-01，不能虚构为已有待办或标记完成。若后续沿用这些讨论简称，World 职责提取对应 A2／C-25／DS-01、DS-02；空间／战斗编排对应 A1／C-27／DS-01、DS-04。后者包含世界投影、唯一位置、资格、时序、触发／反应、推进／暂停、共同提交与恢复，不简化为“扣除战斗资源”。具体切片及验收仍 [OPEN]，WorldHandler 保留业务见 §1.3。

### 13.1 本次同步后的设计／细节／代码状态

本表汇总上述登记，不建立第二套待办；本轮只检查文档。

| 主题 | 已确认设计 | 待冻结／验证 | 后续代码能力（不视为已实现） |
|---|---|---|---|
| 领域与提交 | 单一事实所有者、短事务 UoW、Outbox、幂等、RE accepted ≠ committed | C-01／C-07／C-09／C-15、A1／A2：依赖闭包、版本／Schema、Delta 采用与全部入口终结检查 | 受限基础见 §1；共同 finalize、非战斗 Check 脱离 Combat 职责、跨域故障／缓存一致性仍需实现验收 |
| 战斗观察 | 本场参与者 Turn／外部 Round、同 NPC／Episode 合批、无逐 Event 信号／取证链 | C-18／C-23／C-24：过滤范围／origin、参与切换／覆盖去重、旧入口迁移、关闭／发布恢复 | Turn／Round 聚合及可靠路由尚无本轮运行证据；缺必需依据保留 unresolved，不补造 |
| OB／EVA | 单一游戏时间有界 Recent List、pending／processed、必经 Gate 决策、完整冻结输入、只完成固定 pending | C-11／C-12／C-20～C-22：容量／截断／TTL、快照与覆盖编码、分类／周期／失效／恢复 | 两状态／Task 快照／窗口外证据保护及清理竞争需要专项实现测试；不增加第二输入列表 |
| Meta／Handoff／Policy | 整批 Meta／唯一 Result／可靠交接、独立 command_id；当前 Turn Reaction 不等 EVA、已提交受限参数供后续决策 | C-05／C-13／C-14：Policy 参数／来源版本、关键下一 Turn 等待语义、模型预算与错误映射 | 最小真实 NPC 闭环与友善受击关系更新、参数消费、迟到／重复／故障恢复待验收 |
| 时间／Effects／恢复 | 唯一游戏时钟、有序到期边界、完整效果身份／多来源、原回执对账 | C-03／C-04／C-08／C-15／C-25：RNG 编码兼容、尚未接通的时间消费者、效果映射、选择窗口／Continuation 与支持范围；TimeBinding／TimeDriver／真实 Round 已有 main 实现，默认倍率／宿主政策仍 OPEN | 完整生命周期和中途可恢复选择未完成；活跃战斗精确续玩仍 Post-MVP，不升级为承诺 |

## 14. 能力驱动的交错验证（后续计划，不是本批实现授权）

**[DECIDED]** 以现有 SM＋RE 推进游戏核心，替代 v0.12 的 Evennia 必经验证顺序。按 [演进计划 §8](./GAME_CORE_EVOLUTION_PLAN.md#8-主线能力轨道与早期-agentic-验证) 交错验证对象/动作组合、Encounter / Activity 与真实 RE、当前感知/Policy、Episode 经历和早期 Agentic 行为；这些是能力轨道，不是四个未经审计的代码 Batch 或必须串行的大工程。

先选择最小原创纵向场景，例如环境改变 → 可信感知 → NPC 调查/绕行/必要战斗 → 持久化，按实际依赖补足机制。一旦最小可信执行路径具备就接入受限真实模型，验证无专用分支的合理自然语言行动、世界后果消费、NPC 私有信息差异及自主计划真正执行；不等完整传统引擎或完整 Host，也不无限期推迟 Agentic 验证。至少一名敌方 Agent 的宏观自主性与既有模式独占/完成协议继续验收。

真实模型实验提供语义/体验/自主性证据；确定性回归单独验证执行、权限、版本、幂等、RNG、延迟/重复/失败输出、提交故障和缓存一致性。两者不能互相冒充，本轮均未运行。受控动态扩展目标保留，Coding Agent 不是每个自由行动或首个纵向场景前置条件。

Evennia EB-1～EB-3 仅为演进计划 §9 的**可选替换评估**，不阻塞主线；需要具体可复用能力、独立集成证据和后续工作比较才重新考虑整体采用。原生复用、真实 RE、私有视图、调度/后果及回滚缓存正确性须实证；重大接口差异本身不否决替换，Python/回调能力本身也不证明适用。

RE 能力/依赖盘点与 Stateless 迁移继续按独立切片推进，复用算法并去除隐藏状态。§14.1 的完整完成标准保留，不把全部迁移设为最小能力/可选原型验证前提，也不以 Adapter、文件数量或框架研究宣布完成。

### 14.1 Stateful → Stateless 完成标准 `[DECIDED; NOT IMPLEMENTED]`

- **覆盖可追溯：** 原有规则逐项标明已迁移、仍 Transitional / Legacy 或经显式范围决定不再支持；所有最终声明受支持的规则统一从 Stateless Evaluation 执行。MVP 已选择的机制也必须走该接口，不能暗中落回旧执行器；尚有计划保留能力依赖 Stateful 时不能宣布完整重构完成。
- **旧依赖退出：** 最终 Rule Engine 求值与 SM 集成不再导入、构建、恢复或调用 `_LiveCombat`、`CombatHandle`、`_REGISTRY`、Stateful Combat Orchestrator；每个迁移切片提供依赖检查及实际执行证据。旧 API 只限隔离的回归对照；相关能力完成独立回归并切换全部受支持调用方后，移除其旧生产入口，能力清单完成后退出旧执行器。
- **显式输入/输出：** 完整版本化 Snapshot、Typed Intent、Pinned RulesetBinding 和 Explicit RNGContext 足以求值；无隐藏可变 Session 状态或全局 RNG。同一固定输入得到相同结果，所有状态变化、候选事件、RNG 转换及实际 ReadSet 显式返回。
- **规则与生命周期等价：** 复用正确算法，独立验证既有 Attack / Damage / Check / Save、资源归属、行动经济、移动、法术、效果、反应及跨回合生命周期等所保留能力；旧执行器对照不能替代独立期望结果，也不能把旧缺陷作为正确标准。
- **单一提交域：** 各负责领域在共享事务上下文内验证/应用自己的 Delta，共享设施核验授权/版本/幂等并原子提交 Delta / RNG 及相关 Events / Receipt / 可靠通知记录；具体子系统替换的存储映射仍 OPEN。注入失败、冲突、重复命令、响应丢失和受支持恢复场景证明无部分写入、失败缓存泄漏、重掷骰或双扣费；未提交结果不进入 Perception / Narration。活跃战斗精确恢复仍遵守 MVP 的 Post-MVP 边界。
- **进度指标：** 首先报告已消除/尚存的 Stateful 执行依赖，以及原有规则能力迁移覆盖；另报新规则覆盖和正确性，不以 Adapter、代码文件或新增规则数量宣称架构迁移完成。

### 本文批准条件

- 所有 P0 输入/输出/状态/失败语义没有“谁负责提交”的歧义。
- 提议的字段能完整表达目标规则语义并有可验证的实现路径；历史 Engine 仅用于查漏与回归，不限定目标结构，不能遗漏 Recharge/资源归属、Reaction、RNG 等状态。
- 一次跨领域操作有可验证的单一原子提交域；实际提交实现、对象缓存和可靠通知必须有故障验证，不能仅由既有 SQLite 设计或可选框架能力推定通过。
- 三种关系严格分开：**Proposal ≠ Evaluation ≠ Committed World Fact**；**Event Evidence ≠ NPC Belief**。
- 明确哪些规则还没有足够的实现证据或必须在 MVP 中降级/拒绝。
- 具体 ABI 评审通过前仍为草案，已有 [DECIDED] 架构约束继续有效；不得把任何目标接口当作已实现的公共 API。

## 参考代码（v0.1 历史审阅快照，非当前实现声明）

- [MVP Scope](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/MVP_SCOPE.md)
- [State Machine Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/STATE_MACHINE_ARCHITECTURE.md)
- [Agent Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/AGENT_ARCHITECTURE.md)
- [Rule Engine orchestrator](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/orchestrator.py)
- [Bridge Execution Receipts](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/combat_execution.py)
- [Bridge State](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/state.py)
- [Combat Outcome](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/outcome.py)
