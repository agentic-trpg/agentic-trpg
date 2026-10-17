# Agentic TRPG — Game Core Evolution Plan

> **版本**：v0.5 / Draft；**日期**：2026-10-17
>
> **当前方向 [DECIDED]**：以 `trpg-state-machine`＋`trpg-rules-engine` 为开发主线，借鉴成熟游戏系统，补强承接开放式行动与自主 NPC 的程序化游戏核心；允许实质性重构和替换不合适的子系统。
>
> **规范关系**：[MODULE_CONTRACTS.md](./MODULE_CONTRACTS.md) v0.16 §0.3–§0.6 / §6.5 是领域状态、A1 / A2 与共享提交的跨模块规范；§0.2 / §3.6–§3.7 / §7.5 的主线/机制/经历原则保留。配套 [SM](./STATE_MACHINE_ARCHITECTURE.md) v0.18、[Agent](./AGENT_ARCHITECTURE.md) v0.16、[MVP](./MVP_SCOPE.md) v0.18、[Adventure Package](./ADVENTURE_PACKAGE_SCHEMA.md) v0.12、[World 专项草案](./WORLD_SUBSYSTEM_DESIGN.md) v0.2。
>
> **状态**：方向/原则 `[DECIDED]`；方案/验收目标 `[PROPOSED]`；未决协议 `[OPEN]`；尚未实现的目标 `[NOT IMPLEMENTED]`。以下不宣称代码、模型测试或运行验收已经完成，也不据机制研究断言现有系统完全缺失这些能力。

**2026-10-17 v0.4 评审同步：** [Module Contracts](./MODULE_CONTRACTS.md) 继续是跨模块最终权威；[v0.4](./reviews/agentic-trpg-architecture-contracts-2026-10-17-v0.4.md) 仅保留审查记录。旧修订摘要中的整场 CombatEpisode／旧 OB 术语仅记录历史，现行目标为 Turn／Round Episode、单一有界 Recent OB List 和 `pending`／`processed`。每条新 OB 必经 Gate 决策（模型可选）；EVA 冻结完整授权近期窗口，processed 可影响 Meta，提交只完成固定 pending 覆盖。代码证据保持原日期／SHA，本次不刷新实现状态或冻结新增 ABI。

## 1. 中心问题与原有产品目标

中心问题是：**如何借助成熟游戏机制，补齐承接开放式行动与自主 NPC 的运行能力？** 开放式行动裁决、具有持续后果的动态世界、基于私有信息与认知自主行动的 NPC，都是项目原有目标，不由 Evennia 或 Coding Agent 引入。

“程序化游戏核心”是无需 LLM 执行每一步机械过程的运行基础，不意味着静态世界、固定玩法或只接收预写动作。LLM 负责语义理解、情境/GM 裁决、人物认知和宏观提议；程序负责可验证执行、信息隔离和持久后果。先补最小执行能力，同时尽早接入真实 Agentic 验证，不采用“完成传统 RPG 后附加聊天 NPC”的路线。

本分支 v0.1 的“优先采用 Evennia 已 DECIDED”在合并前撤回现行规范效力。Evennia、CDDA、Ranvier 是具体设计和组件的研究来源；Evennia 整体迁移为 `[OPEN]` 技术选项，需要实际证据，不是主线前置条件。保留有价值的机制分析、风险及比较标准，不整体回退原 Batch。

## 2. 三层能力，单一可信运行边界

| 层次 | 要承接的能力 | 本项目分工 / 验证重点 |
|---|---|---|
| 基础设施 | 存储、命令、连接、客户端、建造工具 | 可复用成熟独立组件；框架现成能力与项目适配工作分别记录，不能以属性/回调入口证明任意玩法已支持 |
| 程序化机制 | 世界交互、动作生命周期、活动执行、感知、NPC Policy、游戏时间、战斗推进 | 各领域管理事实，有状态 Handler 组织流程，RE 计算机械规则，共享设施提交；新增事实须被后续机制消费 |
| Agentic 能力 | 开放式裁决、人物理解、私有认知、宏观计划、对白 | DM / NPC 提议，Host 执行模型；尽早验证提议进入真实执行、不同信息导致不同回应 |

这是逻辑分层，不新增三个服务或仓库。Evennia 的对象、持久属性、命令、连接/客户端和建造能力可用于可选复用评估；项目的 D&D 语义、可信提交、信息隔离、活动/感知与认知联动仍须具体设计和验证。不能把“框架可扩展”写成完整能力证明，也不编造成本、工期或节省比例。

## 3. 当前仓库职责与正确性

| 仓库 / 职责 | 当前定位 | 约束 |
|---|---|---|
| `agentic-trpg/agentic-trpg` | 总控文档、契约与演进计划 | 本轮只修改 Markdown |
| `agentic-trpg/trpg-state-machine` | **当前开发与运行基础** | 保留已验证能力和回归，不只是等待淘汰的迁移资产；类/表/模块/命令集合/Event 管线可依据证据重构或替换 |
| `agentic-trpg/trpg-rules-engine` | 现有 D&D 规则求值基础 | 保留算法与已支持路径，不升级依赖或扩大完成声明；受限路径不代表整个规则族迁移完成 |
| `agentic-trpg/Evennia_base` | **Deferred / Optional evaluation** | 仅具体替代验证获准时再考虑，本轮不创建；不展示可访问仓库，也不默认 fork 或复制 SM |
| Agent Host | 模型执行与 Context 的逻辑职责 | 不拥有权威游戏事实；不要求先实现完整 Host 产品才验证 Agentic 行为 |

**[DECIDED]** 按 MC §0.3 责任表，各领域可管理/持久化自己的状态；同一事实有明确负责人，同一次不可分割操作共享提交/回滚。替代旧“单一 SM 独占所有状态”限制，不能仅改称 Game Runtime 后仍让中心处理器包揽业务。保留授权、版本、幂等、RNG、回执、NPC 私有状态及可靠处理；同一角色在探索/战斗中只有一份当前 HP、位置、背包，各领域引用共用实体身份。替代原型使用独立测试 Session。

默认现有进程内、共享持久化，已审阅测试的 Handler 用受控领域接口/共享事务协作，不逐字段包装外部命令。共享数据库不意味着任意写表，不拆成各领域先提交再补偿；不新增微服务、多数据库、分布式锁、两阶段提交或完整事件溯源平台。Host/LLM 输出、生成代码与未验证脚本不继承内部权限。

普通世界交互不强制经过 RE；涉及 D&D 机械合法性、攻击、伤害、豁免、资源支付、持续效果、Reaction 或连锁结算时复用 RE，不能在 SM/行为脚本另写一份规则。RE 目标无权威跨请求状态，显式 RNG、返回未提交结果，`accepted ≠ committed`；本批不冻结共同 ABI。

**Combat Handler `[DECIDED]`** 管遭遇/参战/回合流程、等待决定、已提交行动与推进进度；根据已提交状态等玩家或调用非 LLM Policy，组织一次求值/共同提交，推进到下一决策边界、合法暂停或结束。RE 计算回合索引、资源恢复、效果到期，Handler 不重复加回合/扣费，一次攻击不默认结束回合；自动推进有界重试/无进展退出。已有受限 CombatHandler / CombatRecords，完整推进、预算、Continuation Schema 仍 OPEN / NOT IMPLEMENTED，见 MC §1.2。

RE 无隐藏跨请求权威与 Handler 持久流程兼容，调用内候选状态/缓冲区允许存在。按需读取、类型调用、共享不可变值、可重建缓存可研究，不能用默认值漏依赖或直接删 Snapshot/Delta 校验，当前公开支持范围不变。完整日志退出普通求值是目标：RE-HIST-01 先审计真实读者、补齐使用标记/效果时钟/关键时间点等必要当前状态，不另建精简历史日志，不置空 event_log、删历史表或全部 proposed_events。本次有序候选结果和必要审计/Episode 证据仍保留，不宣称性能收益。

代码状态更新到 MC §1.2 的 **2026-10-15 SM 静态核对**：分支 `feat/sm-gc5-activity-feedback@1fa7cea`，脏工作区 GC5 单列；已有组合/导航/门锁/取放与库存投影基础。A1 / A2 部分实现，当前非战斗操作不能在战斗中绕过 guard。MC §1.1 保留历史版本对照，本次未刷新 RE main 或运行跨仓库测试；静态核对不等于集成通过。

**A1 / A2 `[DECIDED]`：** 探索移动由 Navigation / Activity + WorldHandler 编排，战斗移动由 CombatHandler + RE 编排，共享唯一实际角色位置和对象事实。StateMachine 为统一 API / 装配入口，子系统按需组合 Handler / Service、Facts / Records、Supporting Components，通过显式依赖与共享 SQLite 协作并逐步减少 Mixin；不机械分层、不按每种对象设 Handler、不强制 ECS。战斗投影映射、互动资格/资源/时序/反应和合法失败成本以 MC §0.5–§0.6 为准；World 候选字段按专项草案核对，后续工作仍在 MC §13 现有表登记。

## 4. 成熟机制：来源、用途与复用方式

下表“如何应用”是本项目候选设计 `[PROPOSED; NOT IMPLEMENTED]`，并非来源系统已满足本项目需求。当前先借鉴设计；直接依赖组件或迁移代码须另有具体证据，不要求全部自行重写，也不为少量能力引入第二套完整框架。

| 来源 | 机制与官方依据 | 如何应用于本项目 | 限制 | 复用方式 |
|---|---|---|---|---|
| Evennia | [Commands](https://www.evennia.com/docs/latest/Components/Commands.html)：前置、解析/执行、后置钩子 | 分清动作校验、实际发生阶段与提交后后果，避免把 Intent 当成外显动作 | 钩子不自动提供原子性；yield 不持久保存暂停，InterruptCommand 不等于通用 Continuation | 借鉴动作阶段；具体独立组件依赖/代码迁移待评估 |
| Evennia | [Combat Base](https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part3/Beginner-Tutorial-Combat-Base.html) 的 CombatHandler；[Scripts](https://www.evennia.com/docs/latest/Components/Scripts.html) 的持久系统状态/可选定时 | 研究 Encounter Controller、持续活动与 NPC 行为的组织，减少散落的动作循环 | 教学战斗不是 D&D；不照搬行动顺序、墙钟计时或承诺任意崩溃续玩 | 借鉴 Controller / 活动处理；不默认引入整个运行框架 |
| Evennia | [Objects](https://www.evennia.com/docs/latest/Components/Objects.html)、[Typeclasses](https://www.evennia.com/docs/latest/Components/Typeclasses.html)、[Prototypes](https://www.evennia.com/docs/latest/Components/Prototypes.html) | 研究对象模板、能力组合和扩展组织，使不同物体共享受控交互语义 | 添加属性不等于移动/感知/Policy 已消费它；模板更新不能覆盖固定包与历史 | 借鉴设计，组件/代码复用逐项审查 |
| Evennia | [Attributes](https://www.evennia.com/docs/latest/Components/Attributes.html)、[Building](https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part1/Beginner-Tutorial-Building-Quickstart.html)、[Web Client](https://www.evennia.com/docs/latest/Components/Webclient.html) | 比较持久属性、建造工具、文字入口等基础设施是否值得实际复用 | 可变 Attribute 可能自动保存；权限、缓存与提交适配未验证，不以基础设施代替项目机制 | 可选直接依赖能力评估；尚未接入 |
| CDDA | [EOC 环境查询 / 视线 / 声音刺激](https://docs.cataclysmdda.org/JSON/EFFECT_ON_CONDITION.html) | 区分当前环境查询与专用感知刺激，让世界变化影响察觉与行为 | 来源视线/声音规则不是 D&D；同场景、局部通知均不证明已察觉 | 借鉴设计，不迁入 C++ 引擎 |
| CDDA | [Activities](https://docs.cataclysmdda.org/PLAYER_ACTIVITY.html)：start / do_turn / finish / canceled 与序列化 | 组织短期行动目标/进度、开始/执行/完成/取消，目标失效时停止或重新决策 | 活动状态不是长期人物认知；取消/恢复语义须服从本项目已提交事实与 RNG | 借鉴状态生命周期，具体协议 OPEN |
| CDDA | [Reality Bubble 坐标 / 分块加载](https://docs.cataclysmdda.org/c%2B%2B/POINTS_COORDINATES.html) | 研究按需要/活动范围推进模拟，避免无差别扫描全部 NPC | 这是局部模拟组织启发，不证明全部离屏行为可停止或可放弃必要后果 | 借鉴设计，不照搬尺度与完整开放世界模拟 |
| Ranvier | [Scripting / Behaviors](https://ranviermud.com/building/scripting/)：可配置、可组合的小行为 | 组合调查、改道等受控行为；项目要求每次继续执行前重查目标、位置与授权 | 目标失效重查是本项目要求，来源接口不自动保证；配置/回调不等于安全热部署 | 借鉴设计；独立组件/代码需许可与依赖评估 |
| Ranvier | [Room.emit](https://ranviermud.com/jsdoc/Room.html)：向局部对象转发选定事件 | 用局部变化通知使相关行为重新检查前提，减少全局广播 | 通知不是 WorldEvent、感知刺激或 OB 的同义词，也不自带可靠投递/权限 | 借鉴局部通知，不引入第二套 JS 游戏运行层 |

直接依赖组件、迁移代码、借鉴设计分别记录实际采用范围、固定版本、依赖和许可。复制示例、contrib、插件或素材前逐项核对，不假定核心许可证覆盖全部内容；参见 [Evennia Contribs](https://www.evennia.com/docs/latest/Contribs/Contribs-Overview.html)。本轮未复制外部代码。

## 5. 首个候选纵向场景：环境改变产生持续后果

**[PROPOSED; NOT IMPLEMENTED]** 原创两个相连房间，通路旁有可移动物体，两个 NPC 拥有不同信息与目标。玩家用未预写专用剧情分支的合理自然语言要求移动物体、建立通路阻挡；Planner 理解/必要裁决后组合已有能力，SM 验证并真实执行。若已支持能力不足，明确缺口/拒绝/澄清，不伪造成功，也不要求每次自由行动生成代码。

候选闭环是：**移动物体 → 建立阻挡关系 → 移动/感知/Policy 使用该事实 → NPC 调查、改道或合法交战 → 后果持久 → 移除障碍后相应限制解除**。通行、视线、声音的影响分别依已支持语义判断，不假定一件物体同时阻断全部渠道；涉及 D&D 判定仍交 RE。恢复通路不撤销已经发生的支付、观察、记忆或其他事实。

检查事实不仅保存为描述：移动可行性、授权当前感知和 NPC 活动必须真正消费相应属性/关系。优先复用动作、属性和关系语义，避免每种物体组合一个专用命令或无语义 Flag；合理任务/剧情 Flag 仍可用，不开放任意 JSON Patch、SQL 或无授权属性修改。具体能力范围、几何/关系与动作阶段 Schema 均 OPEN。

**未来通过证据：** 原始输入、能力组合/裁决依据、提交回执、状态及其消费结果；两个 NPC 各自获准信息/回应与实际动作；目标离开后重查；移除后的相应恢复、正常重启后的后果。确定性回归另外覆盖非法/越权、重复、版本冲突、故障回滚/缓存、迟到或失败模型结果。本轮未实现或运行该场景。

## 6. 感知、短期行动与完整经历

当前感知、短期行动状态、长期认知各司其职；即时行为可使用可信当前感知或机械判定，不等 EVA。JEV 仍仅在既有授权范围承担 Perception / Cognition Gate 判断，不替代必需规则或可信事实；Host 负责模型执行，不拥有权威状态。

**Episode 目标边界 `[DECIDED; NOT IMPLEMENTED]`：** 本场参战 NPC 接收角色 Turn 来源，外部接收 Round 来源；机械 Event 不逐条生成认知信号或逐动作感知证据链。同 NPC／Episode 合批判断，按范围与接收能力过滤，只汇总已提交来源，提前结束也交付最后未满轮。非战斗保留独立 Event 阶段证据；Schema、切换去重与恢复待冻结，历史数据／可靠进度保留。正式契约见 MC §7.5；Package 不嵌入动态 Episode／Memory 或新增 Episode 文件。

聚合在 Turn／Round 关闭后可靠发布，固定过滤依据，不从当前态补造必需历史；来源覆盖、参战切换和迁移恢复仍 OPEN，不要求战斗逐动作感知取证。旧 OB／Outbox 和幂等证据保留。

## 7. 受控扩展，不绑定 Coding Agent

动态 Agentic 行为是产品目标；Coding Agent 运行时生成代码只是可选实现手段。配置/模板更新、已有能力组合、真正新增底层机制分别处理，日常自由行动不必启动代码生成。测试、权限限制、资源预算、版本启用和安全边界不可省略；任意回调、人工审批或 reload 不等于安全热部署。新代码准备完成后受控启用，不承诺任意代码即时安全生效。

在途操作版本绑定、行为状态迁移、安全切换点、失败停止/恢复、扩展来源/版本/启用记录仍 OPEN。插件版本回滚不撤销已提交事实；固定 Adventure Package 是 Session 初始基线，获准扩展或运行变化不可静默回写基线/改写历史。规范集中于 MC §3.6，本批不重设计整个 Package Schema。

## 8. 主线能力轨道与早期 Agentic 验证

以下为 `[PROPOSED; NOT IMPLEMENTED]` 验收目标，不是四批已审计代码任务、冻结接口或必须串行完成的大工程。先核对已有实现/回归覆盖，补最小缺口；各能力围绕 §5 场景交错推进，已有可用能力可直接进入验证。

| 能力线索 | 候选设计 / 需要的通过证据 |
|---|---|
| 对象交互与动作阶段 | 可组合语义、前提重验、真实发生阶段与持久后果；新状态被移动/感知/行为实际消费，不只改变描述 |
| Encounter / Activity 执行与真实 RE 整合 | 非 LLM 行动推进与开始/完成/取消；固定一个实际已支持 RE 操作验证状态/RNG/幂等/冲突/故障/提交后通知，不要求全部协议同时升级 |
| 感知与 NPC 行为 | 当前授权视图、专用刺激、局部通知、短期目标与重查；不同信息/目标导致不同调查/改道/交战，未知不算已察觉 |
| Episode 经历 | 最小 Turn／Round Episode 授权观察、来源追溯、聚合重试与信息隔离；固定过滤依据与恢复验证，不能由结束态推历史 |
| 早期 Agentic 联动 | 最小机制形成后立即交错验证合理自然语言的能力组合、世界变化影响后续行为、NPC 提议进入实际执行及模型异常的安全处理；完整 Host 不是前置条件 |

**两类证据分开：** 实际模型测试验证语义理解、开放式裁决和人物体验；确定性回归固定已审查输入/模型结果，验证执行、权限、幂等、迟到/重复/失败、RNG 与一致性。模型成功话术不证明执行正确，确定性 fixture 也不证明真实 Agentic 体验。至少一名敌方 NPC 的 Agent 宏观自主性仍须按 MVP 验收，纯 Policy 不能替代。

每条验证记录实际版本、Session、配置、命令与输出、范围和缺口；不把静态文档审查或未运行原型写成通过/失败证据。本轮不运行模型或游戏验证；不等待选型研究完成才补当前机制。

### 8.1 领域分责的分阶段验收 `[PROPOSED; NOT IMPLEMENTED]`

这些只约束本次决定的迁移证据，不是全量大重构计划。先盘点当前读写者/公开入口与回归，选择实际受支持操作切片；可保留原入口并逐步移交责任，任何阶段都不能让新旧 Handler 同时独立写同一事实。各切片保留版本/命令/RNG/恢复证据，未运行不能标通过。

| ID | 后续验收 | 必须提供的证据 |
|---|---|---|
| DS-01 | 探索/战斗引用同一角色 | 同一 Actor 的 HP、位置、背包只有一份当前权威，关系/缓存不可独立改写 |
| DS-01 补充（A1 / A2） | 世界投影、互动复用及模块边界 | 记录 World→战斗空间映射；移动只落唯一角色位置；开合/解锁/取放/破坏复用能力，保留原入口限制并覆盖战斗资格/资源/时序/反应。便携归属与库存投影同事务且不可独立改写；显式依赖切片减少 Mixin，不要求全层/ECS |
| DS-02 | 跨角色/效果/战斗原子回滚 | 注入领域验证/写入/COMMIT 失败，全部状态与 RNG、Receipt/Outbox 同成同败；旧引用、缓存、新查询及后续命令无失败结果泄漏 |
| DS-02 补充（A1 / A2） | 合法失败与拒绝分流 | 合法尝试失败按规则共同提交成本、对象后果、进度、实际阶段证据和回执；非法/版本冲突/存储故障不伪装已发生尝试，不发布未提交阶段 |
| DS-03 | 旧模型结果与重复请求 | 异步结果重验实际相关 world_version / npc_state_version、权限/前提；重复命令/响应丢失不重扣/重掷，单玩家也保留防旧防重 |
| DS-04 | Handler 连续推进与暂停 | 推进到玩家/选择边界或结束；攻击不强制结束回合，机械回合/资源/效果仅应用一次；有界重试/无进展退出，不在写锁等玩家/模型/I/O |
| DS-05 | 必要状态替代完整日志 | RE-HIST-01 审计读者并补齐依赖后，固定事实/行动/绑定/RNG，无完整日志输入仍产生相同机械结果、有序必要事件及 RNG 转换；审计保留独立验证 |
| DS-06 | 当前变化不改历史 | 后续 HP/位置/效果/Meta 变化不改写已关闭 Turn／Round Episode 或阶段证据/历史观察，只聚合实际经历，不由结束态补过去察觉 |
| DS-07 | 内部接口与认知边界 | 内部受控调用可共享事务，LLM/未验证脚本不能直接写数据或越权读秘密；整批 Meta、独立行动结果与既有 Work/Completion/模式失效仍正确 |

优化拷贝/读取/校验须另测缓存失效、正常重启与回滚一致性，再报告性能；不以删校验换简化。通用提交设施不重写法术/能力判定，规则适配/攻击白名单须审计覆盖范围。细粒度版本、读写集和锁策略按证据选择，不逐字段过度设计。

## 9. 可选 Evennia 验证与重新选型条件

EB-1～EB-3 仅是未来具体框架替代评估可复用的检查，**不是项目主线强制流程**，未执行。评估获准后使用独立测试 Session 与固定依赖版本，不与当前 SM 双控生产世界，也不以当前接口不同直接否定框架。

| 可选检查 | 仍有价值的未来证据 |
|---|---|
| EB-1 原生基础设施复用 | 两房间、门、NPC、文字交互、运行时创建/行为配置、正常重启持久性；列出实际复用的对象/属性/模板/钩子/Script/建造工具/客户端，防止仅把框架当壳 |
| EB-2 真实 RE 与故障一致性 | 一个固定已支持真实规则操作；唯一权威、显式 RNG、重复/冲突/故障和可靠提交通知；回滚后数据库、新查询、旧持有对象/Attributes/缓存与后续命令一致，不能只看 SQL 或重启 |
| EB-3 调度与持续后果 | 连续行为、目标失效重查、受控版本切换、角色视图隔离、最小 Turn／Round Episode 和环境变化的持久后果；不等于完整 Host、安全沙箱或通用中断 |

[Django Transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) 指出回滚不自动恢复模型内存字段/应用缓存，提交回调也不属于事务本体；[Evennia Attributes](https://www.evennia.com/docs/latest/Components/Attributes.html) 的缓存/可变值须固定版本实测。可靠交接不能仅以一次回调替代 Outbox 语义。这些风险保留为验证项，不是未经运行的否定结论。

只有出现**具体可复用能力、独立集成结果和合理的后续工作量比较**，才重新讨论整体迁移。比较须覆盖实际原生复用、信息隔离、真实 RE、故障/缓存、运行调度及持续世界后果；Python 可扩展或动态回调不自动批准迁移。若需要大范围重写框架、相同事实双重权威或关键正确性无法满足，停止该整体迁移方案、保留可复用设计；这不停止 SM＋RE 主线，也不自动接入另一完整框架。可继续改变技术路线，但不能让研究阻塞机制开发；不预报成本、工期或尚未运行结果。

## 10. 决定、开放事项与修订记录

| 议题 | 当前状态 |
|---|---|
| SM＋RE 主线，补程序化核心并尽早交错 Agentic 验证 | [DECIDED]；具体机制/测试目标 [PROPOSED; NOT IMPLEMENTED]，先核对实际覆盖 |
| 领域管理状态、事实确定权威、操作共享提交 | [DECIDED]，替代单模块独占限制；已有受限拆分，完整职责/字段迁移 [OPEN]，见 MC §1.2 |
| A1 探索与战斗的操作编排分离 / A2 StateMachine 模块化与职责边界 | [DECIDED]；已有部分基础，完整战斗 World 互动、空间映射扩展、剩余组合切片 [OPEN]，实施与验收未完成；统一待办见 MC §13 |
| 有状态 Combat Handler / 校验分责 / 普通求值退出完整日志 | 原则 [DECIDED]；已有受限 Handler，完整推进/预算/Continuation、读取接口与全量日志解耦 [OPEN]；不据已有适配切片认定全部完成 |
| Turn／Round Episode / EpisodeObservation 与不泄密 | 方向 [DECIDED]；证据/生命周期/同步/聚合算法 [OPEN; NOT IMPLEMENTED] |
| 动态扩展 / Coding Agent | 受控能力目标 [DECIDED]；代码生成手段可选，具体协议 [OPEN]，完整系统 [NOT IMPLEMENTED] |
| Evennia 整体迁移 / Evennia_base | [OPEN] / Deferred / Optional evaluation；不构成主线依赖，本轮无仓库或运行实现 |

**v0.2（2026-10-12，合并前修订）：** 文件由 `EVENNIA_ADOPTION_PLAN.md` 改名；撤回 v0.1 的 Evennia 优先采用决定及强制 EB 顺序，改为当前 SM＋RE 演进。保留官方研究、可组合机制、Episode、扩展与故障验证成果。v0.1 只是本分支未合并草案的历史，不作为现行规范。

**v0.3（2026-10-12）：** 遵循 MC v0.14，替代 SM 独占状态限制，确认领域持久化与共享提交、有状态 Combat Handler、校验分责及普通求值退出完整日志目标；新增 §8.1 有界验收，具体实现选择保持开放。未实施 Handler 重构或 RE 日志解耦。

**v0.4（2026-10-15）：** 以 MC v0.15 补充 A1 / A2、World 职责/组件方向与 DS-01 / DS-02 验收细化；更新当前 SM 静态证据，不把已有切片或未提交 GC5 视为完整目标完成。World 规则基线为 D&D 2024 修订规则（PHB 2024、DMG 2024、MM 2025、SRD 5.2.1），具体规则来源/待确认项见专项草案 §1；车辆/荒野旅行/巢穴/位面/Bastion 为后续扩展，非当前 MVP 必须项。

框架研究在线资料日期沿用前批 2026-10-12，本批未重新开展框架研究；World 规则公开来源核对另见专项草案。`latest` 不是固定依赖版本。本轮仅文档修订和静态检查，未实施游戏机制、框架迁移、模型测试或运行验收，未创建/删除/归档任何仓库。
