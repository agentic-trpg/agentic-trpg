# Agentic TRPG — Agent Architecture（MVP，Draft v0.18）

> **文档状态**：Draft v0.18；World / 角色 / 编排分责，运行时复用专项实现见 MC §1.4；本轮无运行验证
>
> **日期**：2026-10-19
>
> **建议位置**：`agentic-trpg/agentic-trpg/docs/AGENT_ARCHITECTURE.md`
>
> **依据**：[`MODULE_CONTRACTS.md`](./MODULE_CONTRACTS.md) v0.18（跨模块最高规范）、[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.20、[`STATE_MACHINE_ARCHITECTURE.md`](./STATE_MACHINE_ARCHITECTURE.md) v0.20、[`ADVENTURE_PACKAGE_SCHEMA.md`](./ADVENTURE_PACKAGE_SCHEMA.md) v0.14、[`GAME_CORE_EVOLUTION_PLAN.md`](./GAME_CORE_EVOLUTION_PLAN.md) v0.7、[`WORLD_SUBSYSTEM_DESIGN.md`](./WORLD_SUBSYSTEM_DESIGN.md) v0.4
>
> **目标产品**：一名真人玩家直接控制一名 PC；本地、文字优先、无常驻 AI 队友；以人工整理的单人 Adventure Package 运行首个完整冒险。World Creation Agent、Visual Presentation Engine 与活跃战斗的跨进程精确恢复均属于 Post-MVP。
>
> **内容边界**：本文仅使用通用概念及原创合成示例，不包含 *First Blush* 正文、地图或实质性的改编剧情数据。该剧本仅作为**私有**端到端验收来源。
>
> **v0.15 修订主题（2026-10-15）**：同步 MC 的 A1 / A2 和 World 事实边界；StateMachine 统一入口/装配、显式依赖与共享 SQLite，Host 只提议。物理遮蔽与感官源属于 World，发现/密码知识属于感知/知识，仍按实际阶段取证；Event / Episode / Observation、NPC EVA 和独立行动机制不另行改造。
>
> **v0.14 修订主题（2026-10-12）**：按 MC §0.3 替代旧 SM 独占所有状态限制。Cognition 管版本化 Meta，Perception 管授权观察，Combat Handler 管持久战斗流程，共享设施保障各次操作提交；Host/LLM 不继承内部领域写权限。EVA 与未来行动仍独立。
>
> **v0.13 修订主题**：当前 SM＋RE 主线允许子系统重构/替换，以机制支持开放行动、持续世界后果及 NPC 私有认知；真实 Agentic 验证尽早交错，不等完整 Host。受控扩展不绑定 Coding Agent；保留 CombatEpisode、OB/EVA 生命周期及模型/权威状态边界。
>
> **v0.12 修订主题（历史，优先采用/强制 EB 顺序已由 v0.13 撤回）**：曾提出 Evennia 优先运行层；三类感知/行动/认知、CombatEpisode 与受控扩展原则保留，未取得迁移或运行证据。
>
> **v0.11 修订主题**：分离即时机械响应与 NPC 认知，Combat Policy 承担即时战术；WorldEpisode / EpisodeObservation 仅聚合授权已察觉阶段。保留敌方 Agent 宏观自主性验收，Episode / Policy / Continuation 具体 ABI 仍 OPEN / NOT IMPLEMENTED。
>
> **v0.10 修订主题**：OB 直接承担短期感知记忆；Processing / Retention 独立，游戏时间 TTL、来源归档与有界定期 EVA；JEV 可承担两个隔离判断职责，Interactive 可选 Gate 分类但无新 Background EVA，Context 到期不自动压缩。接口/参数仍待评审。
>
> **v0.9 修订主题（历史）**：将 Observable Signals / Discovery / 受限 JEV 察觉判断接入既有 Perception / Inbox；内部事件追溯与 NPC 可见内容分离。本次不修复 Event-time Perception P1，不改变 Signal / Event Evidence 计算。
>
> **v0.8 修订主题**：普通游戏命令统一 submit_command / TypedCommand；明确 GM 裁决、有限动态世界创造、条件式效果与授权反馈；同步 AP-15 和只读查询开发计划，候选字段尚未实现。
>
> **v0.7 修订主题**：同步 P0 命令/规则结果/只读查询与回执边界；有效 EVA 的单次 Invocation 失败保持 running 并有界重试，不新增状态或 API 实现。
>
> **v0.6 修订主题**：简化 EVA 标识/状态与最小提交；整批 Meta 原子写入、独立行动可靠交接、完整授权输入与 Belief History。保留 SM 唯一权威、Host Runtime、双模式独占与原 MVP 范围。

> **继承 v0.2 的原则**：Event Observation 与 Current Perceptual View 统一通过 Perception 进入 NPC Context；Evidence Persistence、Memory Consolidation、Context Compaction 和 Suspend/Release 独立管理；保留 v0.1 的权限、战斗、异常回执和 MVP 边界。

**2026-10-19 运行时复用同步：** Package 完整实例化以 MC §2.4 为准；共同复用约定以 [MC §2.3](./MODULE_CONTRACTS.md#23-运行时数据复用派生-snapshot-与版本有效性-decided) 为准；Grid／Environment 细化见 World §2.0b–§2.0c，RE 加载身份见 MC §4.3。当前实现专项核对见 [MC §1.4](./MODULE_CONTRACTS.md#14-2026-10-19-运行时复用专项核对当前分支静态证据)，下述较早日期摘要及待办保留原时点，不作为最新完成状态。本轮仅文档，未新增待办或运行验收。

**2026-10-17 v0.4 评审同步：** [Module Contracts](./MODULE_CONTRACTS.md) 继续是跨模块最终权威；[v0.4](./reviews/agentic-trpg-architecture-contracts-2026-10-17-v0.4.md) 仅保留审查记录。旧修订摘要中的整场 CombatEpisode／旧 OB 术语仅记录历史，现行目标为 Turn／Round Episode、单一有界 Recent OB List 和 `pending`／`processed`。每条新 OB 必经 Gate 决策（模型可选）；EVA 冻结完整授权近期窗口，processed 可影响 Meta，提交只完成固定 pending 覆盖。代码证据保持原日期／SHA，本次不刷新实现状态或冻结新增 ABI。

**2026-10-18 引用同步：** 上段为历史记录；当前远端与实现边界见 [MC §1.3](./MODULE_CONTRACTS.md#13-2026-10-18-远端实现核对定向静态调查)。SM main 已由外部合并更新到 97c5af1／Schema33，ObjectSpatial 原分支现已合入；本轮仅同步现状引用与版本，不改产品范围、Host／认知契约或实施业务代码。


**2026-10-20 三仓库对齐基线：** 当前实现和接口以 [MC §1.6](./MODULE_CONTRACTS.md#16-2026-10-20-三仓库-main-对齐) 的固定 main、源码／测试及 Progress 为准；§1.1–§1.5 与带日期 Review 保留历史适用范围。Schema39 实例配置、冻结规则复用、TimeDriver／Round 及受限 Availability 已有实现，完整动态实例／时间消费者／通用 API 仍有缺口。Full Audit、局部准入、查询及共享 Finalize 的共同规范只维护于 MC §2.3、§6.5–§6.6；本批只改 Markdown，不运行或宣称通过业务／性能测试。

## 0. 决策层级与需要澄清的冲突

**已确认的产品原则**（遵循 Module Contracts v0.18、MVP Scope v0.20 与 State Machine v0.20）：

当前仍以 `trpg-state-machine`＋RE 为基础；目标内部责任以 MC §0.3 状态表为准，不再要求单一 SM 模块拥有全部状态。本文其余“SM”沿用现有任务/观察/命令协议入口，目标内部由 NPC Cognition、Perception、实体/效果领域及 Handler 负责，通过共享设施提交。部分显式组合已实现，剩余目标见 MC §1.3 / A2；Host 不持有影子事实。Evennia / CDDA / Ranvier 研究与可选整体迁移边界不变。

1. **DM Planner 是主持与协调决策者；DM Narrator 独立负责已确认事实呈现**：解释玩家表达、组织交互、作 GM 语义裁决、调用规则及叙述已确认结果；不代 NPC 决定个人目标和自主行为。
2. **NPC Sub-agent 具有独立角色身份和私有上下文**：在需要时被调用；一个模型进程可服务多个角色，但每次调用只能接收该角色已获授权的信息。
3. **提议 ≠ 已发生事件 ≠ 观察 ≠ 记忆**：Agent DM / NPC 输出只能提出规则意图和受限提议。各领域可持久管理其负责事实；RE 用显式事实、Intent、绑定、RNG 求值并返回未提交结果，各领域验证数据不变量后共同提交。提交层不重算机械规则，RE accepted 不绕过授权、版本或提交失败。
4. **Observation → Mode Routing → NPC Evaluation**：SM 可靠保存 OB，它直接承担短期感知记忆；Inactive Gate 决定优先/Deferred 批量 Background 或受控 No-op。Interactive 新 OB 增量进入现有 Context，必经 Gate 决策（模型可选），不逐条强制模型前置。两种模式共享同一份权威 NPC 状态。
5. **事件驱动与游戏时钟日程**：互动、重大认知事件、宏观目标调整及 Pending OB 的定期/最长等待调度可触发 NPC LLM；普通日程确定性维护，即时战斗轮次/Reaction 不触发必经 EVA。无 Pending Work/有效认知 Trigger 的 NPC 不需周期性 LLM，不采用常驻 NPC 模型、无限后台交谈或持续社会模拟。
6. **动态 Perception 是 NPC 唯一的世界观察入口**：事件观察与当前环境感知均经 State Machine 权限过滤；不向 NPC 额外灌入 DM-only 的“权威世界真相”。
7. **三个持久/上下文过程分离**：世界证据及时持久化；长期记忆由 NPC 提议、系统验证；Context Compaction 只管理推理资源，既不等于记忆生成，也不保证物理 KV Cache 保留。
8. **NPC Evaluation Mode Exclusivity**：同一 NPC 的 Interactive Mode 活跃期间，所有需要 LLM 的主观 Memory Formation、Belief / Relationship Update、Goal / Plan Revision 和自主 Action Decision 均由当前 Interactive LLM 处理；不另调 Background LLM、Memory LLM 或 Cognition LLM。空闲但保留 Active Context 仍属于 Interactive Mode。

**控制边界统一 `[DECIDED]`：** 旧版“敌方 Sub-agent 必须生成每次战术 Intent”的冲突已由 MODULE_CONTRACTS.md §0.1 取代。NPC LLM / EVA 负责独立认知、关系、记忆、目标、宏观行为与角色对白；SM 协调确定性机制、受控 Combat Policy 与 RE 执行即时战术、Reaction、自动效果和战斗触发，不等 DM Planner、JEV LLM、Cognition Gate 或 EVA。机械需要的察觉必须可信且确定性/规则可判，未知不能当已察觉。

至少一名敌方 NPC 仍须证明 Agent 宏观决定实际影响后续行为及战后认知；固定策略本身不能冒充 Agent 自主性。普通怪物需要多少认知覆盖、Policy 配置及授权编码仍 [OPEN]，不以单一 `controller.kind` 限定同一 NPC 的全部层次；具体绑定 Schema [PROPOSED; NOT IMPLEMENTED]。Interactive / Background 独占约束只限制主观 LLM 认知，不能阻塞合法即时机械响应。

## 1. Agent 模块的定位与不变量

Agent 模块负责有意义的**非确定性认知工作**，而不是成为第二个游戏执行引擎。

| 参与者 | 可以决定 | 不能自行宣布或修改 |
|---|---|---|
| 真人玩家（PC 控制者） | 自己的角色想说、想做什么；接受/拒绝建议 | 不可声明未经结算的命中、伤害、事件成功 |
| Agent DM | 如何理解玩家表达、应查看何种事实、是否需要 GM 语义裁决/检定、可**请求**激活哪位 NPC、如何呈现已提交结果 | 不可代替 NPC 作个人选择；不可未经授权修改 HP/Slot/道具归属；不可把叙事等于提交 |
| NPC Sub-agent | 该 NPC 的发言、主观解释、目标/宏观行为及记忆更新**提议** | 不可读取别人的秘密/未外显 Intent；不可越权提交状态；不可替自己决定骰点或成为每次战术/Reaction 的执行前置 |
| Agent Host / Orchestrator | 模型执行队列、调用、Context / Prompt / Cache、资源预算、超时重试取消、工具适配传输、运行时日志 | 不拥有或持久管理游戏状态、NPC 认知、领域任务完成或行为结果 |
| NPC Cognition | 私有 Meta 版本/当前状态、Task / 模式 / Gate 与认知完成，验证并持久管理提议 | 不把 Belief 当 World Fact，不包揽感知/战斗或模型 Context |
| Perception / Observation | 授权证据、观察与处理/保留生命周期，按既有协议可靠交接 | 不通过共享对象接口泄漏秘密，不从结束态补过去感知 |
| Combat Handler / 实体与效果领域 / 共享提交 | Handler 管流程、实体/效果负责人管各自事实，共享设施保障版本/授权/幂等/RNG/原子性 | 不复制 HP/位置/背包，不重复 D&D 规则，不将内部接口开放给模型 |
| Rule Engine | 检定、攻击、伤害、资源/回合/Condition 等受支持的机械**求值**（输出未提交的 State Delta） | 不负责塑造 NPC 角色动机、编剧情或决定哪个 NPC 知道什么 |

**不变量：**

- **Truth vs Knowledge vs Belief**：客观世界事实不等于角色已知；角色的猜测、欺骗和偏见不能提升为世界事实。
- **Private Intent vs Observable Act**：未外显的内部 Intent 绝不能被其他 NPC 观察；实际上已执行的动作可以按感知条件投影。
- **Proposal vs Commit**：Agent 的文字、工具参数和记忆提议均非权威；只有可追溯的系统提交/规则回执才能赋予副作用。
- **Single Controller per Actor/Operation**：每次操作须绑定可信控制主体；principal_id 由可信认证环境绑定；LLM 自报身份不构成认证。
- **Do not secretly railroad**：自由合理的玩家行动不能因为冒险预写路线而自动失败；超出可支持范围应明确询问/拒绝/受控裁决。
- **No silent fallback impersonation**：NPC Agent 调用失败不能让 DM 悄悄代 NPC 做人格选择，然后仍宣称经过独立 Sub-agent 决策。
- **Persist evidence, not chain-of-thought**：保存已提交意图/结果、Observations 和经授权的 Memory Proposals；不要求保存模型私有推理链，也不追求重生成相同话术。
- **Perception-only environment updates**：NPC 所见世界的增量与快照只能通过其授权感知投影进入 Context；世界版本号是 Host 的一致性元数据，不是 NPC 获得全知的理由。
- **Correctness before cache reuse**：缓存前缀稳定性是优化目标，不能阻止新的观察进入 Context 或绕过提交前重验证。

## 2. 逻辑架构与组件

```text
Human Player -> DM Planner -> submit_command(TypedCommand) / trusted authorization
                   Game core: current SM + RE; target domain split not implemented
                                    |
                   Immediate path -> stateful Combat Handler / authorized Combat Policy
                                  -> RE for D&D only -> owning domain interfaces / shared Commit
                                    |  [independent of all cognitive LLM calls]
                   Perception / Evidence / Observation -> NPC Cognition
                   Meta versions / EvaluationStatus / NPCStateVersion / Gate / Schedule
                                    |
                       NPCEvaluationRequest (authorized)
                                    v
                         Agent Host LLM Runtime
                   |- Interactive: reusable Context, including idle
                   '- Background: one-shot Context, inactive NPC only
                                    |
                                 NPC LLM
                                    |
                      NPCEvaluationResult (non-authoritative)
                                    |
                   Host submits evaluation_id + Result
                                    v
                       NPC Cognition + shared commit: atomic Meta / Result / EVA completion
                   |- reliable Dialogue / Action Intent handoff
                   '- independent command_id / Typed Command -> SM authorization
                      -> ordinary world handling OR D&D evaluation (validated Snapshot / Intent
                         + pinned RulesetBinding + explicit RNGContext -> uncommitted Result)
                      -> responsible domains / shared Atomic Commit / Command Receipt
                                    |
                      Perception / player-visible DM Narrator
```

认知路径的逻辑信息流为 **可信游戏运行层 → Agent Host → NPC LLM → 可信游戏运行层**；这是责任与信任边界，不要求多个进程/服务，也不是即时机械执行的必经链。当前 SM＋RE 提供执行基础，替换提交实现须独立验证；模型厂商及传输形式仍待选择。本批不实现 Host，后续最小受限模型接入可支持早期 Agentic 验证，不等完整 Host。

### 2.1 Agent Host

Agent Host 严格是 **LLM Runtime / Orchestration Infrastructure**，属于 Agent DM 内部基础设施，不是游戏领域的权威调度中心。负责：

- 接收 SM 创建或批准的 JEV / EVA 运行请求、授权 NPC View / Recent OB / Work 与可信身份绑定，按任务用途/角色构建 Prompt / Context，传输授权 OB 增量及失效通知，禁止原始完整 Package 进入 NPC Prompt。
- 模型调用、超时、有限重试、尽力取消；分配每次尝试的 `invocation_id`，记录日志、延迟、Token Usage 和模型配置。
- Interactive Context 的创建、复用、按序追加、预算保护、释放/重建（MVP 不新增智能压缩）；Background One-shot Context 的创建与释放，不隐式激活 Interactive Agent。
- Context Builder、Token Budget、Prompt Cache 优化、运行时模型执行队列及临时 Runtime Metadata。
- 检查输出格式，执行 Tool Call 的受控适配与传输，以 evaluation_id + Result 递交 SM，分别反馈 EvaluationReceipt / Command Receipt；不语义筛选 Meta。
- 向 SM 报告超时、取消、Context 可用性等运行时信号，由 SM 判断领域任务、模式与完成状态。

Host **不拥有或持久管理** World / NPC Meta、ObservationProcessingStatus、游戏结果或任务完成决定；缓存和日志不成为第二权威。WorldFacts 管唯一世界时钟，Session 提供引用，Cognition 管 Schedule / Gate / 任务授权 / 模式，Perception 管观察生命周期，模型等待不占写锁。已审阅测试的内部模块可经受控领域/持久化接口管理本领域状态，不必反复包装成外部 Agent；Host/LLM 输出、Coding Agent 生成物及未验证脚本不继承这种信任。固定结构化协议与已有机制组合优先，未知字段不产生执行语义，禁止任意数据库/属性写入。

### 2.2 DM 与 NPC 使用不同的请求模板及权限

同一底层 LLM 可以分别执行 DM 与 NPC 角色，但必须有**不同的 Context Builder、工具白名单和输出 Schema**。NPC 的角色身份不是仅在 Prompt 开头写一句“你扮演某人”；要求数据投影层已经过滤不可知的事实，调用日志与状态写入严格按角色分区。

DM Planner 可取得主持范围内完整授权 DMView / GM 信息来正确主持秘密和伏笔；Player / Narrator 只取得 PlayerView，NPC 通过独立 NPCView / Perception 获取信息。复用 get_scene_view 等既有查询入口，动态创建且已提交的对象进入后续授权查询，不新增查询服务；面向玩家的叙述仍受已提交可知结果约束。**GM 知晓秘密，不代表玩家或 NPC 自动知晓秘密。**

### 2.3 DM Planner / DM Narrator：独立职责与可见性

**DM Planner 与 DM Narrator 必须在逻辑角色、上下文及输出协议上隔离。** 两者可以共享底层 LLM 模型和 Agent Host 进程，但不得使用同一份未过滤的推理 Context，也不能相互冒用身份、工具或权限。

| 组件 | 许可输入 | 输出 | 严格禁止 |
|---|---|---|---|
| `DM Planner` | 经 SM 授权、Host 传输的 GM/剧情条件、已确认游戏状态、玩家意图与规则能力视图 | 场景主持计划、GM 裁决/有限世界创造提议、统一 TypedCommand、独立 NPC 激活请求 | 自行提交世界/战斗状态；假借 NPC 私人动机；把计划当事实 |
| `DM Narrator` | 已提交 Receipt、玩家授权 Perception、经审查可公开的场景文案和 NPC 已发布的实际对白 | 面向玩家的文字呈现 | 接收或泄露 DM-only 剧情秘密、其他 NPC 私人想法；生成新机械结果或未提交事件 |

Narrator 可以收到**受控公开的叙事提示**，不必拥有 Planner 的完整 GM 视角。主持涉及的原始知识可帮助 Planner 安排线索，但 Narrator 对玩家的呈现受 PlayerView 和已确认事件约束。Narrator 输出失败可安全重试生成表达，不可重复提交动作。

**调用闭环**：Player Input → Planner 生成计划/候选 TypedCommand → 可信适配层绑定身份 / submit_command → 负责 Handler 鉴权、组织领域处理与必要 RE 求值 → 各领域接口 / 共享提交 → CommandReceipt / Perception → Narrator。NPC 对话/宏观行动来自独立 Sub-agent；即时战术由 Combat Handler 根据已提交状态等待玩家或调用非 LLM Policy，并在选择边界停止、有界重试/无进展退出。Handler 不包揽认知与叙事，具体 API/预算/Continuation OPEN。

## 3. Agent DM 的一次玩家回合

### 3.1 输入与分流

来自授权 UI 的结构化操作经类型验证直接进 SM，自由文本进 Planner；文本看似 JSON 不赋予系统身份，也不新增 JEV Router。

`PlayerUtterance` 附带可信 `session_id`、PC 身份、输入 ID 和源界面。DM 先查询经授权的当前 Scene/Session/PlayerView，并将玩家自然语言拆解成下列一种或多种候选：

1. **对话行为**：玩家向哪个 NPC 说了什么；NPC 是否在场、是否能听到。
2. **世界交互**：取物、开门、转移、揭示、调查、交付物品等；生成 command_type=world.* 的待验证 TypedCommand。
3. **规则请求**：检定、攻击、施法、逃跑中的规则挑战、危害等；生成 command_type=rules.* / combat.* 的强类型 TypedCommand，由 SM 适配统一 RuleEvaluationRequest。
4. **信息请求/叙事动作**：查看房间、回顾已知信息、询问背景或说明行动意图，可能只需要读取事实和描述。
5. **需要澄清/不支持**：目标不唯一、GM 判定依据不足、规则能力尚未实现或 Actor 无权限时，不得虚构成功结果。

**[DECIDED] 三个验证领域**：Planner 根据可信 GM View 和适用规则判断情境语义与 GM 裁决，SM 验证世界事实、可信身份/权限、结构/引用和版本，Rule Engine 验证 D&D 机械合法性并计算结果。Planner 可提出是否检定、能力/技能、DC 与成功/失败后果，优先使用规则或 Package 的规定；未规定时允许 GM 裁决，但须在掷骰前确定并保留可追溯依据。SM 仅检查可确定性验证的内容，不新增语义审核 LLM、不重算 D&D 规则；不要求模型私有推理链作为依据。

普通游戏命令统一 submit_command(TypedCommand)，包含 session_id / command_id、可信 principal_id、适用操作的 actor_id、command_type、expected_world_version、强类型 payload，按 MODULE_CONTRACTS.md §3 定义，不新增 Adjudication API。Actor 行动须真实 actor_id；受信系统/世界事件的 combat.start / rules.effect 等可无行动 Actor，但须验证 principal、机械来源与目标（AP-15）。强类型联合、source_ref / 来源权限字段仍 [PROPOSED / OPEN; NOT IMPLEMENTED]；不是将 actor_id 全局无约束可空。创建、NPC Evaluation、查询/回执入口继续独立。

### 3.2 场景主持与自由行动

**World 与编排边界 `[DECIDED]`：** Planner 的意图仍经 StateMachine 统一命令入口；探索移动采用 Navigation / Activity + WorldHandler，战斗移动采用 CombatHandler + RE，共享唯一实际角色位置和对象事实。战斗开合/解锁/取放/破坏额外协调规则资格、资源、时序、触发与反应，不能绕过现有非战斗入口限制；Handler 只编排，规则判断/计算归 RE。当前受限实现及缺口见 MC §1.3，目标/候选 World 能力见专项草案。合法失败可能仍支付成本，Narrator 根据已提交结果描述，不能把 unsupported 或版本冲突讲成骰点失败。

- **[DECIDED]** Adventure Package 是静态初始定义，不是 DM 创造力的上限。Planner 可以解释和创造情境，通过 SM 已支持的有限 Typed World Operations 提议简单 Object / World Fact / Scene Connection，不修改静态 Package，也不新增 World Creation Agent。
- 已有对象优先使用可信 GM View 的 ID，新对象由 SM 分配稳定身份。叙事描述、未提交提议和已提交 Runtime World State 必须分开；不能信任 LLM 自报引用存在或状态已变。
- Planner 可提出受限 Conditional World Effect Proposal，复用 Package 的 Condition / Effect 语义。SM 根据可信规则结果和权威世界状态判断条件并执行允许效果；尽可能在掷骰前确认操作与后果有受支持的表达路径。
- 机械计算仍经统一 RuleEvaluationRequest / Result。可在一个命令提交前完整求值时同事务提交世界/机械效果、RNG、事件与 CommandReceipt / Outbox；已提交事件的后续效果采用可靠幂等独立命令，不声称跨已提交事务原子性。
- 普通命令使用封闭受限类型/字段，禁止借此执行任意 JSON Patch、SQL、脚本或开放状态覆盖；受控 Session 扩展另按 §4.5 / MC §3.6 处理。具体 Object / Connection / Conditional Effect 字段与动态复杂 Scene / 战斗地形生成 **[OPEN]**；候选接口 **[PROPOSED; NOT IMPLEMENTED]**，详见 MODULE_CONTRACTS.md §3.3–§3.4。
- Planner 不得直接提交骰点、伤害、任意状态变化或覆盖 Engine 结果；独立 NPC Agent 的私人意图不由 Planner 代决。叙事须读取已提交回执与当前授权视图，才能描述已发生效果；提议或 accepted 求值仍不是提交。

### 3.3 是否激活 NPC

触发 NPC LLM 的候选原因包括：玩家直接交谈、NPC 需要宏观个人选择、NPC 收到重要威胁观察、NPC 被要求确认承诺或调整长期目标。轮到即时战术/Reaction 不构成必须等待 LLM 的触发；由 SM 协调 Combat Policy / RE。

无须为每个新 World Event 广播一次 LLM；SM 可将 OB 留在持久 Inbox 按优先级合批，但 Pending Work 受定期/最长等待期限约束，不能无限等到玩家唤醒或 TTL 到期。

**调度与人格决策分离**：DM 可以请求开始 Interactive Mode；SM 依据交互请求、权限、游戏时序和领域预算批准模式与任务；Host 执行 Context / 模型运行。已活跃 NPC 复用 Interactive Context；Inactive NPC 的非交互选择可以由 Background One-shot LLM 完成，无须激活 Interactive Agent。NPC 自己决定如何回应；DM 不为推进剧情强迫其说出秘密。Scripted Event 的已审核前提与 NPC 自由选择仍需明确区分。

### 3.4 一个可重试的结果路径

```text
User input (input_id)
  → DM interprets candidate(s)
  → Host reads current authorized snapshot (world_version)
  → State Machine creates/approves Task -> Host runtime -> NPC LLM Result
  → Host transports Result + trusted task binding
  → State Machine validates identity, scope, versions and idempotency
  → Rule Engine evaluates when needed -> State Machine commits
  → committed receipts + WorldEvents
  → Perception Projection writes per-actor Observations
  → DM renders from committed result + PlayerView
  → optional bounded follow-up NPC Evaluation (respect mode exclusivity)
```

若世界版本在 NPC 推理期间发生变化，应**刷新 View 并重新校验**；不能把几秒前的 LLM 决策直接当作当前命令执行。拒绝后的重新决策次数必须有上限；不得把拒绝解释为骰子失败，除非 Engine 明确返回了对应已执行结果。

## 4. NPC Sub-agent：身份、决策与控制方式

### 4.1 稳定身份与私有性

每个 NPC 具有稳定 `npc_id`。NPC Sub-agent 的调用由当前 Session、NPC ID、可信 Controller Binding 与启动原因标识。身份与持久私有资料来自 State Machine；LLM 不得自行声明自己是另一个 NPC。

**Persistent NPC State** 沿同一实体身份关联，NPC Cognition 可持久管理 Personality 与追加版本的 Memory / Belief / Relationship / Goal / Plan，保留旧内容、来源、当前版本及 Goal/Plan 状态；Schedule / Current Activity 通过负责流程接口管理。历史 Goal 不全部待执行，记忆不保证必然避免循环；本轮不新增复杂导航图谱、目标树或防循环 Schema。**LLM Evaluation Context** 只是 Host 的授权派生输入，两模式不各自持有另一份人格/计划；释放、切换或更换模型不新建 NPC，也不强制压缩 Context。

| NPC Evaluation Mode | Context 与职责 | 可选结构化输出 |
|---|---|---|
| `interactive` / Interactive Mode | NPC 专属可复用 Context；主观认知/行为，增量接收授权 Observation | 同一/兼容 NPCEvaluationResult 七字段，均可为空 |
| `background` / Background Mode | Inactive NPC 的独立一次性授权 Context；可用不同 Prompt / 模型 / Builder | 同一/兼容 NPCEvaluationResult 七字段；通常 dialogue 为空，其他更新与行动也可为空 |

`inactive` 表示没有 Active Interactive Context，是调度状态而非第三种 Evaluation Mode；Background 任务可以排队或执行。所有输出是**可选提议**，合法 `no-op` 不要求写 Memory，也不要求每轮对白都产生世界行动。独占约束针对 LLM 认知和行为决策；State Machine 仍独立记录事件、原始证据、已确认承诺并进行必要的确定性安全处理。

NPC 的 Context 至少包含：

| 信息 | 来源 | 原则 |
|---|---|---|
| 完整授权 Profile、行为风格、目标、约束 | SM 从 Package 初始化及合法动态更新 | 不是世界完整剧情 |
| 该 NPC 的 `known_facts` | State Machine `NPCView` | 只含该 NPC 已知事实 |
| 完整 Episodic Memory / Belief History / Relationship / Goal / Plan | NPC Cognition 私有 Meta | 首次构建/重建输入完整授权数据；版本/来源/当前有效及 Goal/Plan 状态明确，不语义排名筛选 |
| 有效 Recent OB 与本次待处理 Work | State Machine 已投影的有序 Inbox / Work | Recent 含未过期 processed OB；Pending 范围单独标识，不把 Context 出现等同待处理；过期不作为近期输入 |
| 当前可见场景与角色 | 经 Perception 投影的 NPCView 与当前感知摘要 | 无隐藏 HP、未发现秘密、他人内心 |
| 可提交动作、角色身份、世界版本 | 授权工具/状态契约 | 能**提议**不等于会成功 |
| 本次时间/Token/自动反应限制 | SM 领域预算；Host 调用资源预算 | 防止递归和空转 |

**零知识不等于真实世界为空白**：NPC 可以持有错误 Belief，甚至故意撒谎；但必须基于自己角色可获得的证据和目标推理，不能由于 DM 在旁边知道真相就泄漏秘密。

### 4.2 两种模式的执行流程

```text
SM persists OB / Evidence / Work -> mode and priority routing
   |- Interactive active (including idle)
   |    -> Host ordered append; required Gate decision (optional model)
   |    -> existing Interactive LLM: Urgent next EVA / Deferred batch
   |       or SM controlled No-op
   '- Inactive -> SM Gate policy
         |- Irrelevant -> SM Safe Retention / No-op (processed, still Recent)
         |- Deferred -> pending batch at periodic / maximum-wait deadline
         '- Urgent -> priority Background EVA
              -> Host one-shot Context -> NPC LLM -> release
   EVA paths only -> submit_npc_evaluation_result(evaluation_id, NPCEvaluationResult)
   -> SM deterministic validation of whole NPC Meta batch
      |- invalid: no Meta / final Result commit -> bounded correction in valid EVA
      '- valid: same SQLite transaction checks Task / NPCStateVersion,
                selects sole Result, commits Meta + reliable output handoff,
                records EVA completed / EvaluationReceipt
   -> separate Action Execution: stable command_id / Typed Command
                -> optional Rule Evaluation -> SM Commit / Command Receipt
```

**EVA 是认知更新与决策评估，不是 Action Execution。** 同一次 Result 可含七字段，也可全空。Memory、Belief、Relationship、Goal、Plan 整批确定性验证与原子写入；任一 Meta 更新非法整批不提交，由当前有效 EVA 有限修正。Action Intent 非法独立拒绝、不回滚合法 Meta；合法意图可靠交接独立 Command，EVA 完成不等待行动成功。

Interactive 期间不创建新的 Background EVA 或额外 Memory / Cognition LLM，包括模型暂时空闲；Cognition Gate JEV 可选作重要性分类，不要求每条 OB 先运行。Urgent 优先下一次 Interactive EVA，Deferred 随正常交互/定期 EVA 批处理，Irrelevant 可受控 No-op。Host 按序追加、排队执行，不能修改在途 Invocation 的输入、Context 或 KV Cache。Gate 若需轻量分类，Host 只推理、SM 采用，不能替 EVA 生成主观 Meta 或语义筛选 Meta。Background 可独立提出行动，无须激活 Interactive Agent。实际行动共享 Actor 授权、Typed Command、必要 Rule Evaluation 与 SM Commit；Schedule / Policy 也沿用该路径。

LLM 不得将尚未成功动作写成已发生 Episode，须等待提交事实/Observation；SM 只检查引用、类型和权限，不能证明自然语言忠实或替 NPC 改写 Belief。

Action Execution 使用独立 (session_id, command_id)。SM → Engine 的 Request 保留该键、按操作类型校验的 actor_id / operation_kind，payload 按操作类别强类型化，内部 intent_type 仅区分动作子类；合法未命中或被反制且合法支付仍可 accepted，Schema/运行时/传输错误另行反馈。UI / Agent Planning 可经 SM 查询只读 Action Availability，原因受权限限制；查询无 RNG/Delta/事件/CommandReceipt，available 不保证随后执行成功，实际命令必须重验。完整技能列表与目标枚举非本轮 P0 必须实现。查询可与早期 Stateless Rule Evaluation 实现同步开发，基础战斗操作与正式求值共享规则逻辑，无需等待 Visual Presentation；当前文字 MVP 不强制调用，视觉 UI 仍 Post-MVP，本轮不实现。

### 4.3 控制策略不是怪物类型

逻辑控制器可为 `sub_agent`、`deterministic_policy`、`scripted_event`（遵循 Adventure Package v0.7）；怪物是否具有机械 Stat Block、是否有认知 Agent、采用何种即时 Combat Policy 是不同维度，具体组合编码仍 OPEN。

- `sub_agent`：角色基于授权上下文提出自主语言、世界行动与宏观目标/策略；不要求逐次战术 LLM。
- `deterministic_policy`：可由固定行为树、启发式或规则策略选择动作，结果仍必须走 Engine/State 授权入口。**不可统计为 LLM Sub-agent 验收。**
- `scripted_event`：用于环境或经审查的场景事件，不声称进行独立人格决策。

**未决范围**：普通怪物的认知覆盖、Combat Policy 算法/版本和绑定权限尚待设计；MVP D16/D26 与至少一名敌方 Agent 宏观自主性验收已经同步。既有 Engine `advance_monster_turn` 或固定策略不能证明该 Agent 闭环已接入。

### 4.4 战斗 NPC 的宏观输出与即时 Policy `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

NPC LLM 可基于授权经历提出“保护某人”“撤退”等宏观行为/策略，复用既有 Goal / Plan / Action Intent 提议边界；不新增正式 Result 字段，也不把自然语言目标直接当可执行战术命令。SM 采用合法提议后，受控 Combat Policy 在机械可知视图与授权约束内选择目标/位置/能力的 Typed Intent，RE 算规则，SM 提交。具体目标到 Policy 的转换、Schema/版本/取消权限仍 OPEN，不能随意生成命中、骰值、支付或效果事实。

**集成验证边界**：即时战术、Reaction、自动效果与战斗触发不依赖 Planner / JEV / Cognition Gate / EVA；机械察觉未知不能默认 Positive。一次 RE 请求尽量完成连续规则链，真正中途选择按 MODULE_CONTRACTS.md §8.3 Interrupt / Continuation 目标处理，不由 NPC 主观认知回路代替。必须验证至少一名敌方 Agent 的宏观选择真实影响 Policy、资源/Action Economy 与战后认知；不能冒充 PC、访问私有 Engine 状态或将固定 AI 当作 Agent 验收。当前 SM / RE 分支与接口差距见 MODULE_CONTRACTS.md §1.1。

#### CombatPolicy 的受限参数与生效边界

CombatPolicy 是确定性的即时战术决策组件。它接收 `combat_id`、决策 Actor、版本、授权机械可知视图、已提交认知的受限策略参数及有界选择预算，返回 TypedIntent、受支持的 Reaction 选择或明确无可行动／等待结果。策略参数可以表达对玩家／势力的关系立场、获准目标与战斗意图；具体字段在有消费者时冻结。Policy 不读取完整 NPC 私有 Meta 或玩家秘密，不调用认知 LLM，不生成伤害、骰点等机械结果。

NPC Cognition 负责主观关系和目标，向 CombatPolicy 提供受控、带来源版本的参数投影；投影不成为第二份可独立修改的认知权威。机械状态仍随实际动作更新。当前 Turn 内的反应使用当时已生效的策略参数；该 Turn 引起的认知变化，只有在认知结果提交后才影响后续决策，不追溯修改已执行反应。

CombatHandler 组织 `initialize → await_decision → evaluate/commit → next_boundary → close`，协调 Policy／玩家选择、RE 求值和共同提交，实际状态名称可沿用现有代码。一次行动不自动结束 Turn；没有合法进展时退出而非无限重试。Turn／Round 完成时按 MC §7.5 关闭相应 Episode、建立可靠感知工作；不在每个机械 Event 后启动认知管线。

例如友善 NPC 被玩家攻击：玩家 Turn 完成 → Turn Episode 聚合信号 → 过滤／察觉形成 OB → 按资格启动 EVA → 提交关系／目标更新 → 刷新策略参数 → NPC 后续 Turn 决策。采用认知判断时，不另加“受到攻击即无条件敌对”的并行关系写入路径。如果获准的关键认知任务必须影响该 NPC 紧接着的 Turn，则在其决策边界等待有效提交；等待释放数据库事务，失败或超时走明确恢复流程，不能暗中改成强制敌对或宣称任务已完成。普通 OB 不要求每个 NPC 每个 Turn 都运行 EVA。

即时 Reaction 由 CombatPolicy 根据已有参数与当前机械视图选择，CombatHandler／RE 验证并执行，不等待当前 Turn 的 OB 或认知 LLM。预先声明的 Reaction profile 与通用中途暂停选择是不同能力。后者未来必须有持久选择窗口：所属 command／combat、获准选择者、阶段／窗口序号、合法选项、输入版本、已提交前缀或未提交候选的明确状态、取消与恢复策略。公开响应使用新的幂等命令引用该窗口；仅系统拥有 continuation 数据。未完成该协议时保持 unsupported，不序列化 Python 栈或在事务中等待人／LLM。

### 4.5 受控动态扩展与可选 Coding Agent 的边界 `[DECIDED; OPEN; NOT IMPLEMENTED]`

运行时创建内容、组合机制和安装 NPC 行为是目标能力，受控启用规范集中于 MODULE_CONTRACTS.md §3.6–§3.7。配置/模板、已有能力组合与新增底层机制分别验证；前两类不要求代码生成，Coding Agent 仅为可选手段，不是每个自由行动或早期验证前置条件。新增代码需适用测试、权限/资源预算限制及版本化受控启用；回调、人工审批、reload 均不等于安全热部署。在途版本绑定、行为状态迁移、失败处理仍 OPEN，版本回滚不撤销已提交事实；固定 Adventure Package 初始基线不变。

## 5. Context Builder 与 NPC Active Context 生命周期

本章区分：**稳定角色信息**、**事件引起的增量观察**、**当前环境的感知快照**和**可恢复的工作上下文**。NPC 不存在绕过 Perception 的“直连世界真相”入口。`world_version`、`view_version` 是 Host/State Machine 的一致性元数据，只有需要且授权时才暴露面向角色的时间/变化提示；不能据此推断未被观察的秘密事件。

### 5.1 不同调用者的视图与身份隔离

| 请求者 | 应取得 | 不应取得 |
|---|---|---|
| 玩家端 / Player-facing DM Narration | PC 实际可感知场景、公开对话、本人权威结果 | DM-only 伏笔、NPC 私密计划、未察觉伏击 |
| DM Planning | 主持范围内完整授权 DMView / GM 事实、条件、能力边界和结构化反馈 | 将未提交的 NPC 文字当已发生事实 |
| NPC Sub-agent | `NPCView(npc_id)` 私有身份、知识、记忆以及**经 Perception 过滤的 Event Observations / Current Perceptual View** | 完整 WorldState、其他 NPC 私有 Context、DM-only 真相、不可见的他人 Intent |
| Rule Evaluation 调用边界（SM → Engine） | 经验证的 Typed Snapshot / Intent、Pinned RulesetBinding、Explicit RNGContext 及可信引用 | NPC 私人思考链、用剧本文字直接取代规则参数、Legacy 执行器对象 |

get_scene_view 给 NPC 返回信息时也必须经过 NPC Perception / 授权投影，不能绕过 get_npc_view / get_current_perceptual_view 等既有入口的感知边界（DOC-02）；不新增查询服务。内部 source_event_id / source_event_seq 只供追溯/排序，不能将事件类型、真实行动者或隐藏目标随引用泄漏给 NPC。

上下文安全边界应在**检索、投影与工具授权**阶段实现，不能将全量世界状态送进 Prompt 后仅靠“不要泄漏”约束。玩家输入、其他 NPC 发言和剧本文本均视为低信任数据，不具有系统级指令权限。

### 5.2 统一的 Perception 输入：事件与当前状态

非战斗 Event Observation 继续采用独立实际阶段证据，不拿当前位置或结束态补历史；正式机械检定交 RE。Current Perceptual View 表示查看时的授权环境，不补未目击历史；作为长期 Meta 来源时须有系统签发的可验证引用。

战斗以 combat_id 关联，本场参战 NPC 接收角色 Turn Episode 聚合来源，外部 NPC 接收 Round Episode 来源（在另一场战斗中也算本场外部）。Turn 含期间 Reaction、多次动作／攻击；一次 action 不等于 Turn。Turn 关闭交付内部、Round 关闭交付外部，提前结束也关闭并发布最后未满轮，不再强制一场只有一个 CombatEpisode。

只聚合已提交来源，固定路由／过滤依据／来源覆盖，范围与接收能力过滤继续有效，同 NPC／Episode 合批感官判断，未察觉不建空 OB。机械 Event 不逐条生成认知信号或工作，不另建逐动作感知证据链；非战斗独立 Event 阶段证据保留。EpisodeFilterBasis、Schema、加入／退出边界、去重覆盖与恢复仍 OPEN／NOT IMPLEMENTED；重试不按最新参战状态解释旧投影。历史 Event-level 进度先建映射再切换旧消费入口，不删观察或重复 Meta／Action。长期整场记忆可由 EVA 结合窗口内聚合 OB 提议，无需全知总 OB。

Perception 判能否察觉，JEV 只返回受限逐 Signal Boolean，不生成 Memory／Belief／世界事实；缺漏、重复、额外项、错误或超时不转 false。仅受支持不确定判断由 Host 在写事务外运行模型。听到爆响不自动知道施法者、完整战果或隐藏因果，来源引用不授予读取来源全集权限。察觉不等于触发 EVA，新 OB 的 Gate 决策见 §6.3a。

### 5.3 Active Context 输入：完整授权 Meta 与增量复用

MVP 首次构建/重建 Context 与 Background One-shot 使用 SM 提供的完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan 和有效 Recent OB（含 processed）；Pending Work 单独关联。完整授权数据仍是该 NPC 的私有视图，不包含他人秘密或全知 WorldState。Host 只组装，不做语义筛选、Semantic Retrieval、Memory Ranking、独立 Memory Agent 或智能压缩；认知更新由 EVA LLM 判断。

```text
NPC Context (session_id + npc_id scoped)
├── Trusted role / tool / predefined result schema instructions
├── Complete authorized NPC Meta at construction / rebuild
│   ├── Profile / Episodic Memory
│   ├── Belief History (versions / sources / current status)
│   └── Relationship / Goal / Plan
├── Incremental authorized Observation / committed Meta changes
├── Current player input (Interactive, when applicable)
└── Current Perceptual View / committed action feedback (as needed)
```

已有 Interactive Context 可连续复用，增量追加授权观察与已提交 Meta 变化，不要求每次 EVA 重注入全量 Meta。旧观察与当前感知分别保留时间/来源；不能把旧状态当实时事实。Token Budget 不授权静默丢弃或语义排序 Meta，预算不足明确反馈并保留任务，模型容量/预算细节仍待实现验证。

**固定 EVA 输入 `[DECIDED; NOT IMPLEMENTED]`：** 创建 Task 时固定 NPC 认知版本、本次 pending OB／Work 覆盖，并冻结当时整个仍在游戏时间窗口内、授权且有界的 Recent OB List（含 processed 与 pending）。Task 保存快照引用／版本及原始任务证据；同一 evaluation_id 重试读取原快照，不重读滑动后的列表。processed 仍可影响后续 Meta 推理，但不重复成为处理义务。合法提交仅完成本 Task 固定覆盖的 pending；在途新 OB 进入同一列表并经 Gate 决策，需 EVA 者交后续任务，不改旧输入或完成范围。同 NPC 只有一个有效 EVA；Interactive Context 复用须保持与 Task 冻结输入等价，旧 Token 中过期 OB 不重新获准为 Recent。恢复输入明确原始时序与到期事实，不新增独立 Pending／Historical List。

### 5.4 动态追加实例：角色发现门已打开

1. T1：NPC A 看见门关闭，其 Context 中保留「T1 门关闭」的观察。
2. T2：玩家在 A 面前实际打开门；WorldEvent 及视觉 Signal 已提交，Perception 投影出 A 确实察觉的授权 Content「旅人将门打开」，不原样传递内部事件类型。Host 在 A 的后续调用中按序**追加**观察，无须清空已有对话。
3. T3：A 再次观察门时，Current Perceptual View 告诉它「门当前打开」，避免旧的 T1 记录被误认为实时状态。
4. NPC B 在 T2 不在场，因此不会收到「玩家打开门」的 Event Observation；T3 才进房的 B 仅被告知「门当前打开」。B 可推断期间有人开过门，但不能将某人身份冒充亲眼所见。
5. 所有世界动作仍由 State Machine 按提交时版本与实际条件重验；**NPC 的当前观察也可能在模型推理期间过期**。

### 5.5 NPC Context 生命周期（与 Scene 解耦）

| 阶段 | Host 的工作 | 边界 |
|---|---|---|
| Activate / Reactivate | SM 原子撤销旧有效 EVA 并授权新任务后，以最新完整授权 Meta、有效 Recent OB、未完成 Work 和玩家输入建/复用 Context | 不等待旧 EVA 结束或失败反馈；不改写人格 |
| Active Interaction / Idle | 复用 Context，后续追加已提交 Meta 变化 | 无在途调用仍为 Interactive，不另开 Background |
| Incremental Observation | 有序追加新观察；在途输入供下一次调用，按需获取当前感知 | Gate 决策必经、模型可选，不修改运行中输入/Context/KV Cache |
| Memory / Cognition Evaluation | 当前 Interactive LLM 提出可选整批 Meta 更新 | 不另调 Memory / Cognition LLM，持久化不强制重建 Context |
| Resource Pressure | Token 计数、预算保护，必要时通知 SM 后释放/从完整授权 Meta 重建 | MVP 不新增语义筛选或智能总结压缩；不能静默漏掉 Meta |
| Suspend / Release | SM 撤销旧有效任务、更新当前模式并保留未完成 Work；Host 尽力取消调用、释放 Context | 不依赖 Host 内存取消保证正确性，不等待旧失败回执 |

Scene Change 不是强制销毁 Context 的条件。Keep / Release / Rebuild 由运行时资源和交互连续性决定，领域任务资格由 SM 决定；释放不丢持久 Meta / Belief History / Observation。MVP 不承诺保存完整 Prompt 或物理 KV Cache，也不承诺逐字恢复未持久 Token。

### 5.6 Prompt / KV Cache 与 Compaction 边界

连续互动优先增量追加，保持稳定前缀以争取 Prompt Cache。Meta 提交成功不要求立即重复注入相同内容或重建 Context；后续追加已提交变化即可。逻辑 Context 复用不等于物理 KV Cache 常驻，缓存命中不能替代权限/版本检查。

Memory Persistence 与 Context Compaction 继续分离，但 MVP 不增加语义总结、智能压缩、Memory Ranking 或 Semantic Retrieval；最低要求是预算保护与安全释放/重建，完整授权 Meta 不被静默筛掉。未来压缩摘要也不能变成 NPC Meta / World Fact，复杂压缩与检索后置。

### 5.7 旧视图、状态新鲜度与并发

本次 Activation 应保留 Host 侧的 `world_version`、可选 `combat_version`、感知快照标识、Observation 消费范围及身份绑定。模型生成结束后，State Machine 仍按最新权威状态检查命令和 Actor 权限。若发生 `state_version_conflict`，由 SM 决定有界重评估，Host 获取该 NPC **新一轮合法 Perception** 并执行调用，不能把失败原因变成额外的 DM-only 世界知识。

两个角色争抢同一物品时，**游戏内先后由授权时序/竞争规则裁定，非 LLM 推理完成时间或网络写入速度**。数据库版本冲突只是并发协调信号，不自动成为角色观察或动作事件。

### 5.8 Mode Switching：撤销旧 EVA，不等待调用

**Proposed / Not Implemented**，见 [`MODULE_CONTRACTS.md` §9](./MODULE_CONTRACTS.md#9-agent-host--npc-evaluation--memory--dmp1-接口边界)。SM 持久保存当前 interactive / inactive 状态、EvaluationStatus、NPCStateVersion 和 Observation Work，Host 管 Context / Invocation。

Background → Interactive：

1. SM 在短 SQLite 事务内撤销旧有效 EVA 的提交资格，保留已经合法提交 Meta，移交未完成 observation_work_id，记录 Interactive 状态并创建新 Evaluation ID。
2. Host 以最新完整授权 Meta、未完成观察和当前玩家输入建立/复用 Interactive Context；不等待旧 EVA 完成、失败回执或 ACK。
3. Host 尽力取消旧 Invocation；物理调用可迟到返回，但 SM 拒绝已取消任务结果，不能通过新 Invocation 恢复资格。
4. 若旧提交先成功，则原子 Meta、唯一选定 Result 与输出交接保留，不重做；独立已交接 Command 的后续授权/取消由 Command 流程处理，不由 EVA 切换回滚已提交行动。

Interactive → Inactive 同样撤销旧有效 EVA、移交未完成 Work、更新当前状态并按需创建新 Background EVA；Host 释放 Context。SM 在**同一 Meta 提交事务**校验任务有效性和 NPCStateVersion，不依赖 Host 内存任务状态，也不需要模式代次计数器。

Evaluation ID 是任务与 Meta 幂等键，不是认证凭证。SM 仍核验可信调用主体、NPC 绑定、授权范围、引用和数据库约束。重启从持久 Task / Result / Meta / 交接与 Command Receipt 恢复；模型调用在写事务外。

## 6. NPC Cognition、Evidence Persistence 与 Memory Lifecycle

本章分工：**Perception 管角色授权感知证据与处理生命周期，NPC Sub-agent 提议理解与记忆，NPC Cognition 管版本化 Meta / 任务，共享设施保障提交，Host 管模型与 Context。** Evidence Persistence、Memory Consolidation、Context Compaction 保持独立。

### 6.1 信息分层与权威边界

| 层次 | 产生/保存方 | 作用及约束 |
|---|---|---|
| `WorldEvent` | 负责领域 / 可信规则结果，经共享提交 | 世界已发生的事实、顺序与来源；私有 Intent 不在此列 |
| `ObservationRecord` / Recent OB | Perception Projection / Inbox | 已实际察觉的授权 Signals，短期感知记忆；Processing 与 Retention 独立 |
| `CurrentPerceptualView` | 授权 Perception Projection | 当前可感知场景；按需重建，不泄漏秘密或未目击历史 |
| 短期行动状态 | 可信运行层 / 非 LLM Policy 的活动控制 | 当前目标、行动阶段及必要前提；执行前重查目标/环境，不等同 Recent OB、长期认知或新增短期记忆系统；映射 OPEN |
| `EpisodeObservation` | 目标运行层授权经历聚合 | 非战斗 Event 或战斗 Turn／Round 聚合的已察觉部分，过滤／迁移仍待验证，不是全知战斗摘要 |
| `NPCEvaluationResult` | 当前模式的 NPC LLM | 统一七字段非权威数据，均可为空 |
| `EvaluationReceipt` | Cognition / 共享提交 | evaluation_id 关联的原子 Meta / EVA 反馈，独立于 Command Receipt |
| `NPCMemoryRecord` / Long-term Episodic Memory | NPC LLM 提议，Cognition 验证，共享设施提交 | NPC 私有长期经历；其他 Meta 同样版本化，均不自动变 World Fact |
| `LLMEvaluationContext` | Agent Host | 可复用 Interactive Context 或一次性 Background Context；均为派生推理输入，不是可靠世界存档 |

`ObservationRecord` 指**角色已实际察觉且获授权的感知证据**，不承诺理解或长期记住每一细节；不另设独立 Short-term Memory。MVP 不做完整的认知心理模拟。对必须使用 D&D 检定的隐藏信息，不得因简单同场景投影而绕过 Rule Engine。

### 6.2 Evidence Persistence：不要等待 LLM 才保存事件

- 已确认的物品变动、说出的话语、明确建立的承诺、行动结果与可观察动作，按 State Machine 的提交边界可靠保存必要 WorldEvent/Receipt。
- Perception 根据**事件发生时**的证据投影观察，写入该 Actor 的 Observation Inbox；若异步投影，需使用持久 Outbox 和幂等键，以便中断后继续，不能重新拿当前视角倒算历史。
- NPC 无需为了「获得观察」而运行模型；NPC 睡眠、脱离对话或未激活，也不会因此失去已应投影的观察。
- 被授权的当前感知快照可直接用于决策，但**形成可追溯长期记忆时**，系统须能将其登记为归属明确的感知来源；不能由 LLM 自造证据 ID。
- **重要承诺的成立本身是已确认的世界交互事实**，不能等到 Interaction End 的 Memory Consolidation 才生效；NPC 是否记得、如何评价，是另一个流程。承诺成立也不自动代表承诺已兑现。

### 6.3 Memory Formation / Consolidation：按意义与生命周期触发

**触发（Memory Check，不一定产生写入）**：NPC 收到重要经历、作出已确认承诺或发现秘密、关系发生显著变化、连续互动结束、NPC 挂起/释放前、Deferred OB 定期/最长等待到达，以及需要利用新经历指导未来决策时。统一由当前模式 EVA 联合评估，不增设独立 Memory 调用；阈值、重要性标准与异步策略仍待实现/测试，**不能将所有新观察逐条变成永久 LLM 摘要**。

可记录的最小类型：

| 类型 | 示例 | 来源约束 |
|---|---|---|
| Episodic Memory | 「我看到旅人打开了门」 | `source_observation_ids` + observed/told 标签 |
| Belief | 「我怀疑旅人在试探我」 | inferred 标签、可选 confidence；允许错误 |
| Relationship / Affect | 「我对旅人的警惕提高了」 | 仅允许改变本 NPC 自己的私有关系状态 |
| Commitment Recall | 「我答应明早支付报酬」 | 指向已提交的 commitment event/record，不能自行创建承诺 |

最小执行语义：

```text
Committed WorldEvent / authorized Observation
  ├── Evidence Persistence → WorldEvent / Observation Inbox / committed receipts
  │
  └── SM authorizes Task by NPC Evaluation Mode; Host runs model
       → active: append to Interactive Context; current Interactive LLM decides
       → inactive: Lightweight Gate; optional Background One-shot LLM
       → submit_npc_evaluation_result(evaluation_id, NPCEvaluationResult)
       → State Machine validates npc identity, evidence ownership,
         provenance, epistemic status, update type and idempotency
       → atomic NPC Meta + sole Result + reliable handoff + EVA completed
```

State Machine 仅确定性验证**引用、身份、字段、版本、任务状态、权限、幂等与数据库约束**，不做自然语言忠实性判断、不改写 Belief，不增加 Semantic Validator LLM。整批 Meta 任一项非法都不提交。因此 Episodic/Belief 保留 `source_observation_ids` / `source_memory_ids`、`epistemic_status`（observed/told/inferred）及必要的 `confidence`。从「听见某人说 X」不能未经证据转换为「我亲眼知道 X」。

**Memory 写入不强制 Context Compaction，也不强制重建当前 Prompt。** 如果该重要经历已在 NPC 当前对话历史内，不必再把刚保存的记忆重复注入，使下一轮既看到原话又看到重复摘要。

### 6.3a Lightweight Gate：优先级分类与模式路由 `[DECIDED]`

每条新 OB 进入单一 Recent OB List 后均须有可靠 Gate 决策；模型可选。无需 EVA 直接 processed，需 EVA 保持 pending；未决、失败／超时仍 pending。分类不增加状态；processed 留在游戏时间窗口，后续 EVA 仍冻结并读取它。

`Lightweight Gate` 复用原 Cognition Gate / Cognition Trigger / Behavior Trigger 入口，不是新 Memory Agent。领域策略、分类采用、保留、任务与完成由 SM 管理；Host 执行可选 JEV 推理。Gate 只判断已察觉 OB 是否需要及时认知评估，不生成 Memory / Belief / Relationship / Goal / Plan。确定性规则、轻量模型、批量分类可组合，不要求每条普通 OB 单独调用 JEV。

```text
Committed Event / Event-time Perception
   -> Reliable NPC Observation + evidence ID
   -> SM checks current mode / Work / authorized Gate candidate
   -> Lightweight Gate
      |- Urgent -> Inactive priority Background / Interactive next EVA
      |- Deferred -> retain Pending OB, periodic / maximum-wait batch EVA
      |- Irrelevant -> controlled No-op; processed OB remains Recent until expiry
      '- Uncertain / Failure -> protect Pending evidence; bounded safe handling
```

- 建议分类 Urgent / Deferred / Irrelevant / Uncertain（或 Failure）的具体枚举和消息 Schema 仍 `[PROPOSED / OPEN; NOT IMPLEMENTED]`；完整跨模块语义集中于 MODULE_CONTRACTS.md §9.8–§9.9。旧 `durable / short_term / discard` 分类由此取代，不建立另一套短期 Memory 或直接删除路径。
- Inactive 不维持持续 Interactive Context。Urgent 优先一次联合 Background EVA，Deferred 积累 OB 后按定期/最长等待批处理，Irrelevant 可持久批准 No-op 且仍保留有效 Recent OB。一次 EVA 统一考虑七字段，不因 Urgent 必须写长期 Memory。
- Interactive 可选 Cognition Gate 重要性分类，不能要求每条 OB 先调用 JEV；主观判断由当前 Interactive LLM 完成，不创建新 Background EVA。迟到分类按当前模式/Work 重验路由，不复活旧任务。
- Uncertain、模型失败或批次缺项不当作 Irrelevant / processed。SM 保守保留 Pending 证据并采用确定性保底/有界后续处理；实际模型、阈值、批量预算及漏判/成本指标仍待实验。
- **JEV 双职责允许共享底层模型**：Perception Judgment 只输入可信事件时感知证据与 Signals、输出察觉 Boolean；Cognition Gate Judgment 只对已确认察觉的 OB 分类。输入、输出 Schema 与权限验证分离，Host 执行、SM 采用，不替代 RE 的正式机械感知检定。

### 6.3b Background Evaluation：认知与行为可在一次调用中完成

Inactive NPC 遭遇重大目击时，可经 Gate 触发**独立、一次性、有界**的 Background LLM Evaluation。Context Builder 组装 SM 提供的完整授权 Profile / Episodic Memory / Belief History / Relationship / Goal / Plan 和 Task 冻结的完整授权 Recent OB List（含 processed／pending），不做语义筛选；可使用与 Interactive Mode 不同的 System Prompt、模型和 Builder。输出统一 `NPCEvaluationResult`，以 evaluation_id + Result 递交 SM；Memory、Belief、Relationship、Goal、Plan 和 Action Intent 均可为空；不限制为只有认知更新。

Background 调用**不创建、不恢复、不激活 NPC Interactive Agent**，调用完成后释放临时 Context；唯一选定 Result、原子 Meta、待处理任务及可靠输出交接由 SM 保存；执行另用 Command Receipt。稳定 `evaluation_id / trigger_id / source_observation_ids` 与 EvaluationStatus / NPCStateVersion、预算及重入控制防止重复认知/行动。模型失败保留 Observation 与任务，不允许 DM 冒充 NPC。Active Interactive NPC 收到相同重大观察时由 SM 批准任务、Host 执行其当前 Interactive LLM，无须等待玩家先发言，也不另开 Background 调用。

### 6.4 Context 资源管理与 Memory Persistence 独立

重要记忆提交、互动结束或 Scene Exit 不自动触发 Context 重建。MVP 以 Token 计数、预算保护、必要时释放/从完整授权 Meta 重建为边界，不增加语义总结或智能压缩机制；完整 Meta 超预算须明确反馈，不静默筛选。复杂 Context Compaction、Semantic Retrieval / Ranking 后置。

未来工作摘要也不是 Episodic Memory、Belief、Relationship 或 World Fact；任何资源管理失败不能撤销已提交 Meta、承诺或世界事件。可靠任务/Observation 来源由 SM 保存，不依赖 Context 缓存。

### 6.5 三层持久与临时信息管理

| 层 | 生命周期 | 主体 | 可否丢失/重建 |
|---|---|---|---|
| Evidence Repository | 权威 Session 事实与观察生命周期 | State Machine：WorldEvent、Observation、Commitment、Receipt、必要对话证据 | 已提交关键证据不可随意丢失；可按明确保留策略管理 |
| Persistent NPC State | 该 NPC 在 Session 内的唯一权威身份与状态 | State Machine：Identity、Personality、Memory、Belief、Relationship、Goal、Plan、Runtime State | 不随模式切换或 Context Release 丢失，支持版本/来源审计 |
| LLM Evaluation Context | 连续互动或单次 Background Evaluation | Agent Host：授权状态投影、对话/Observation、当前感知 | Interactive 可复用/安全重建；MVP 不新增智能压缩；Background 一次性释放 |

区分模型交付、EVA 完成与 Action Execution 结果：SM 以原子 Meta 与可靠输出交接完成 EVA / 必要认知工作，不等待行动成功；Command Receipt 独立跟踪。内部 Completed Cursor 无需跨模块 ACK，模型/数据库失败保留未完成 Inbox。

### 6.6 EVA Completion、Feedback 与 Observation Processing

- 每个 evaluation_id 最多持久选定一份最终 Result。首次通过 Schema / 整批 Meta 验证，在同一 SM SQLite 事务校验有效任务与版本，选定 Result 并原子写入全部认知更新、可靠输出交接及 completed 状态。
- 相同 Result 重试返回原 EvaluationReceipt；已有选定结果时同任务不同 Result 拒绝。尚未选定前，Schema / Meta 验证错误由当前有效 EVA 有界修正，不留下半批 Meta。
- 单次 Invocation Timeout / API Error / Schema 非法 / Meta 验证失败不立即使 EVA failed；有效且预算未耗尽保持 running，以同 evaluation_id / 新 invocation_id 有界重试/修正。只有耗尽或明确无法继续才由 SM 记录最终 failed，保留未完成观察；模式切换为 cancelled。取消任务拒绝迟到结果，新 Invocation 不能复活旧 EVA。响应丢失先查持久结果，不重新生成来猜测提交。
- Action Intent 非法独立拒绝，不回滚合法 Meta；合法意图可靠交接独立 Typed Command，每个行动关联独立稳定 command_id，派发重试复用它。CommandReceipt 单独表示动作提交/拒绝/冲突/pending_choice（对应规则 needs_choice）。
- **EVA 完成不等待 Action Execution 成功**；SM 在完成事务中可靠记录交接或明确拒绝/no-op。动作失败可反馈现有 Interactive LLM 继续动作交互，不自动重做完整 EVA 或重写 Meta。
- SM 内部 ObservationProcessingStatus 据必要认知处理与可靠交接维护；Command 失败/等待 choice 仍独立跟踪，不自动重新打开已完成 EVA。读、Context Append、模型返回、取消/失败本身不等于观察完成；内部 Completed Cursor 不跨认知/交接缺口和投影水位，不需要额外 ACK。
- Dialogue 发布独立核验受众、结构化引用与叙事权限，不以台词推定动作成功；SM 不证明自然语言真实性。NPC 不得将未执行动作记为已发生，Prompt 约束与可验证来源共同使用，不能冒称有语义验证器。

### 6.6a OB Processing / Retention 与 Context 到期 `[DECIDED; NOT IMPLEMENTED]`

NPC 维护**单一、有界的 Recent OB List**，按游戏时间窗口保存该 NPC 实际察觉的观察，顺序稳定。窗口的时长、截断规则和必要容量上限应在实现时固定；不要求另设 Pending／Historical OB List 或第三种 OB 处理状态。观察者感知投影水位仍按 MC §7.3 独立维护；读取列表、Host 添加 Context 均无处理副作用。

**OB 的 Cognition 处理状态只有 `pending` 和 `processed`：**

| 状态 | 含义与转换 |
|---|---|
| `pending` | 新 OB 的 Gate 判断尚未可靠完成，或 Gate 判定需要 EVA 而本次认知义务尚未由有效任务完成；失败、超时、模式竞争不可默认为 processed。 |
| `processed` | Gate 已可靠判定无需触发 EVA，**或**覆盖该 OB 的有效 EVA 已合法提交；表示当前没有未完成的认知处理义务，**不表示 LLM 一定读取过该 OB**。在游戏时间窗口内仍可被以后 EVA 读取为历史证据。 |

感知 JEV（MC §7.2）与 **Cognition Gate** 是不同职责：JEV 判断信号能否被察觉；Gate 判断新 OB 是否需要触发 NPC EVA。每条新 OB 在进入 Cognition 后都必须获得可靠的 Gate 决策；Gate 可以优先使用确定性策略，仅在设计明确需要时调用受限模型。现有 urgent／deferred／irrelevant／uncertain 等分类属于 Gate 的判断结果，不是额外 OB 状态；仅明确无需 EVA 的有效决策可置 `processed`，需要 EVA 则保持 `pending` 并依 Task 资格创建／排队，判断失败或尚未确定则维持 `pending` 并可靠重试。

创建 EVA Task 时固定本次覆盖的 pending OB／Work、认知版本，并冻结**当时整个仍在窗口内、授权且有界的 Recent OB List**（包含 processed 和 pending）作为输入。processed 历史 OB 可以改变 LLM 对当前新 OB 的理解，但再次出现在输入里不构成再次触发或再次消费。合法 EVA Result 只完成本任务固定覆盖的 pending OB；MC §9 的任务身份、结果幂等、Episode 覆盖和 Meta 原子提交继续适用。同一 NPC 同时只有一个有效 EVA；在途期间新来的 OB 继续接受 Gate 判断，需触发者 pending 并在后续有效任务处理，不修改旧任务的固定输入。

战斗 Gate 处理 MC §7.5 的 Turn／Round 聚合 OB，不退回机械 Event 级。一个 Episode 的 OB 不必对应一次 EVA；普通 OB 不暂停战斗。关键任务需要影响下一 NPC Turn 时依 MC §0.4 的获准等待边界处理。Gate 负责是否**现在需要认知更新**，而不是裁定 OB 是否有永远的记忆价值。

Recent OB List 按**游戏时间**滑动；到期的 processed OB 可以退出活跃窗口，但被有效 Task、回执、长期 Meta 引用或恢复流程必需的证据仍依相应保留策略保护。到期的 pending OB 也不得无条件删除或隐式置 processed；可从活跃列表移出并独立保护必要证据，直到处理或明确失败／恢复。Host 墙钟超时不推进游戏时间，重试必须保持冻结输入，不能用新的窗口内容覆盖旧 Task。

SM 保留多 Meta／历史版本、Task／交接／审计／回执和幂等证据，清理事务内重验。Host 不另建 Historical List 或自动回注归档。到期仅更新有效性，可在下一 Invocation 追加失效通知，不删旧 Token、不改在途输入／KV Cache、不自动 Compaction 或重做 EVA。

### 6.7 原创合成示例：两位 NPC 争取同一枚硬币

```yaml
world_event:
  event_id: evt.coin.taken.by.a
  event_seq: 51
  kind: item.transferred
  actor_id: npc.a
  object_id: item.coin.001
  to_owner_id: npc.a
  # npc.b 的私有拾取 Intent 不在此事件内

observation_for_b:
  observation_id: obs.b.51
  observer_actor_id: npc.b
  source_event_id: evt.coin.taken.by.a
  perception_kind: sight
  observed_payload:
    actor_id: npc.a
    action: took_item
    object_id: item.coin.001

evaluation_submission_by_b:  # SM Task 绑定 npc.b / work.b.51 / 认知版本
  evaluation_id: eval.b.12
  result:  # 统一七字段 NPCEvaluationResult
    dialogue: null
    memory_updates:
      - kind: episodic
        text: "我看到 A 拿走了那枚硬币。"
        epistemic_status: observed
        source_observation_ids: [obs.b.51]
    belief_updates:
      - text: "A 可能是故意抢在我前面的。"
        epistemic_status: inferred
        source_observation_ids: [obs.b.51]
        confidence: 0.45
    relationship_updates: []
    goal_updates: []
    plan_updates: []
    action_intents: []
```

A 是否看到 B 也伸手，取决于 B 是否**实际执行了可观察的 `action.started`**，并且 A 当时能感知；只有 B 的私有 Intent 时，A 不可能合法知道 B 的想法。若双方有真实、已提交的可见争抢动作，State Machine/Rule Engine 可以裁定先后，再生成相应观察；不能依据网络先到或 SQLite 提交顺序推断“谁敏捷”。

## 7. 对话、欺骗与行动的权威分界

- NPC 可以**决定说谎**，但“NPC 说门已打开”只证明**NPC 说了这句话**。它是否真实由世界状态判断。
- NPC 决定**许诺**某事时，主持者可以通过受限的 `commitment` 语义事件记录此人作过承诺；**经确认的承诺事件及时持久化，不等待 Memory Consolidation**。承诺本身不自动兑现物品、权利或任务结果。
- NPC 说“我把钱交给你”并不自动转移金币。必须提交 `transfer_item` 并取得成功回执，DM 才可叙述钱已经到了对方手中。
- NPC 尝试偷窃时，可以先由 NPC Sub-agent 提出私有动机/意图；实际可观察动作和是否偷窃成功必须由 Host 传输、SM 验证并按需调用 Rule Engine 后提交，再按 Perception 投影给目击者。
- 同一对话可能同时涉及 `speech` 事件、交付物品、接受任务、秘密揭示，需拆成可审核的语义动作；不能通过文本匹配随意认定所有承诺已履行。

**重大安全约束**：NPC 本人的台词、玩家输入、冒险文本和外部检索结果均为数据，不可在其中插入新的工具权限或“忽略前述规则”指令。输出中的可执行字段必须经严格白名单和身份绑定校验。

## 8. EVA 提交与 Action Execution（Proposed / Not Implemented）

### 8.1 NPCEvaluationRequest：SM → Host

SM 创建／批准逻辑 Task，保存 Session／NPC、模式、版本、权限、固定 pending 覆盖与冻结的完整授权 Recent OB 快照，提供完整授权 Meta，Host 负责运行模型。与 RuleEvaluationRequest 不同：

```yaml
schema_version: npc-evaluation/0.1
evaluation_id: evaluation.demo.17
mode: interactive
reason: player_addressed_npc
observation_work_id: work.warden.12
expected_npc_state_version: 8
authorized_npc_meta_ref: meta.warden.8.complete
recent_ob_snapshot_ref: recent.warden.eval.17  # Task 创建时完整授权窗口，含 processed / pending
covered_pending_observation_ids: [obs.warden.12]
source_observation_ids: [obs.warden.12]
current_player_input_ref: input.demo.17
```

session_id / npc_id 由 SM 管理，evaluation_id 是逻辑任务/Meta 幂等键，EvaluationStatus 控制提交资格，NPCStateVersion 控制认知版本，observation_work_id 关联未完成工作。invocation_id 是 Host 一次模型尝试，context_id 是 Context 引用；一 EVA 可多 Invocation，一 Context 可多 EVA，后两者非提交必填。command_id 仍为独立行动幂等键。

**固定 EVA 输入 `[DECIDED; NOT IMPLEMENTED]`：** 创建 Task 时固定 NPC 认知版本、本次 pending OB／Work 覆盖，并冻结当时整个仍在游戏时间窗口内、授权且有界的 Recent OB List（含 processed 与 pending）。Task 保存快照引用／版本及原始任务证据；同一 evaluation_id 重试读取原快照，不重读滑动后的列表。processed 仍可影响后续 Meta 推理，但不重复成为处理义务。合法提交仅完成本 Task 固定覆盖的 pending；在途新 OB 进入同一列表并经 Gate 决策，需 EVA 者交后续任务，不改旧输入或完成范围。同 NPC 只有一个有效 EVA；Interactive Context 复用须保持与 Task 冻结输入等价，旧 Token 中过期 OB 不重新获准为 Recent。恢复输入明确原始时序与到期事实，不新增独立 Pending／Historical List。

### 8.2 统一 NPCEvaluationResult 与最小提交入口

Interactive / Background 使用预定义同一/兼容 Schema，允许不同 Prompt / Context / 模型。LLM 生成数据，不定义 Schema；字段可全空：

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

```python
submit_npc_evaluation_result(
    evaluation_id: str,
    result: NPCEvaluationResult
) -> EvaluationReceipt
```

不需要额外 Proposal 信封。SM 从 Task 恢复 Session、NPC、模式、版本、观察与权限，可信调用身份来自运行环境，不接受 LLM 自报。EvaluationReceipt 是必要结构化反馈，不新增独立服务或复杂公共回执系统。详细语义见 [`MODULE_CONTRACTS.md` §9.4](./MODULE_CONTRACTS.md#94-npcevaluationresult原子-meta-与结果幂等-proposed-not-implemented)。

Meta 整批合法才原子提交，一项非法整批不写、当前有效 EVA 有限修正；SM 仅确定性验证，不做自然语言语义核验或改写 Belief。Action Intent 独立拒绝/交接 Typed Command，不回滚合法 Meta，Command Receipt 与 EvaluationReceipt 分开。

### 8.3 故障、修正与恢复

Timeout / API Error、Schema 非法、Meta 验证失败分别反馈：单次 Invocation 失败不终止整个 EVA，任务有效且有预算时保持 running，同 evaluation_id 可换新 invocation_id 有界重试/修正。只有重试耗尽或明确无法继续才最终 failed，SM 保存未完成 Observation；模式切换为 cancelled。模式切换直接撤销旧有效 EVA、授权新 Task，不等待旧反馈。取消任务不能借新 Invocation 继续提交。

EVA 提交响应丢失查询 evaluation_id 的持久结果；Command 响应丢失查 command_id 的独立回执，不盲目重问模型或重掷骰。动作失败反馈可以继续动作交互，不自动重做整次 EVA。

SM 持续不可用/持久化失败则停止权威推进，进入暂停/错误/待恢复，无法写库时不伪称已落盘。Host 不接管状态、无影子权威副本或独立游戏队列。恢复依据 SM Task / 已选 Result / Meta / 可靠交接 / Command Receipt；非战斗恢复必需，战斗精确续玩仍 Post-MVP，不增加分布式协调。

## 9. 激活策略、延迟与资源预算

### 9.1 事件驱动的触发范围

| 事件 | MVP 策略 |
|---|---|
| 玩家直接与 NPC 对话 | 经模式切换进入/复用 Interactive Mode |
| Interactive NPC 获得新 Observation | 按序追加现有 Context；必经 Gate 决策（模型可选），不逐条强制；无新 Background EVA |
| Interactive Context Active 但模型暂时空闲，收到重大事件 | SM 批准下一次 Interactive Task，Host 执行调用 |
| Inactive NPC 获得 Observation | 先可靠保存；Gate 路由 Urgent 优先 EVA / Deferred 定期批处理 / Irrelevant 受控 No-op |
| NPC 必须选择是否提供帮助、拒绝、欺骗或交易 | 正在交互交给当前 Interactive LLM；非交互可一次 Background Evaluation |
| NPC 即时战斗轮次 / Reaction / 自动效果 | SM 协调 Combat Policy / RE，无必经 LLM；宏观目标重评估与战后认知另按合法 Trigger 授权 EVA |
| 普通环境危险/脚本触发 | 通过声明式 Event / Rule Engine，不需要人格 Agent |
| 远处数百 NPC 没有互动、Pending OB 或有效 Trigger | 无周期性 LLM 调用；有 Pending OB 则按有界定期/最长等待处理，不等到 TTL 才触发 |

### 9.2 必须有界，但不冻结未经验证的数字

每次玩家回合为 NPC 激活数量、自动 NPC→NPC 反应深度、重新提议次数、每次调用 Token/时间、总回合等待时间设置预算。**数值由实现期基准测试决定**，不能把随意估计的秒数写成用户批准的 SLO。

推荐的处理优先级：玩家显式交互、已提交威胁事件需要的必要反应和当前战斗合法动作优先；无关背景 NPC 的主动聊天可延迟甚至不激活。SM 可依据领域触发批准任务，无须 DM 为每次反应单独请求；Host 按授权执行并限制调用资源。超时或预算用尽时，保留未处理观察，返回明确状态或**事先批准**的确定性降级；决不无限自我调用。

### 9.3 SQLite 与并发调用

允许多个 NPC 在同一 Scene 基于不同过滤视图同时推理，但提交**必须遵守** State Machine 的身份、版本和操作顺序。模型推理、Perception 视图组装与 Rule Engine 等待应在 SQLite 短写事务之外进行，提交时重新验证状态。几百个 NPC 的存储本身不是要求同时唤起几百次模型。

### 9.4 MVP：Schedule-driven Background Behavior

NPC 是持续存在的逻辑角色，不是常驻 LLM 进程。Adventure Package 可为 NPC 声明游戏内时间的默认活动（工作、用餐、休息、跨场景出行）。State Machine 依据**游戏时钟与事件推进**检查到期动作，使用合法的 Typed Command 提交，事前校验 NPC 仍存活、当前位置、环境和前提条件。日程中断或无效时不能强制执行（例如已不存在的工坊仍在锻造）。

日程模型为 MVP 的轻量**预定义活动**，而不是复杂自主社会模拟；不应每秒给数百 NPC 执行一轮动作或产生 LLM 请求。`activity_id`、`schedule_version`、`due_game_time`、`source_trigger_id` 及完成/取消回执需要可去重、可恢复。

Evennia Script / 活动控制、CDDA 短期活动与 Ranvier 小型行为是机制研究来源，不是已选框架映射（演进计划 §4）。当前 SM 的活动/Policy 子系统可据证据演进，游戏时间衔接仍须验证。连续行动必须重新检查目标仍在场、权限及当前条件，不能因先前选择继续攻击已离开的目标；即时攻击、移动或持续效果不要求逐次 NPC EVA。

### 9.5 Memory / Cognition / Behavior Trigger 是可联合的逻辑职责

这些职责可以共享一次判断和一次 Evaluation，不代表必须创建独立模型或 Session：

| Trigger | 回答的问题 | 可以直接做什么 | 不可以做什么 |
|---|---|---|---|
| `Memory Trigger` | 已察觉 OB 是否需要及时认知评估？ | Gate 可作重要性分类，SM 路由当前模式 EVA / Deferred / 获准 No-op | Gate 直接生成长期 Memory 或把证据保留等同 Memory Formation |
| `Cognition Trigger` | 是否需要重考虑 Belief / Relationship / Goal / Plan？ | 请求当前模式的一次 NPC Evaluation | 擅自认定信念为世界事实 |
| `Behavior Trigger` | 是否需要中断日程或重考虑行动？ | 请求当前模式 Evaluation，或执行已审核的确定性安全策略 | 将 Trigger / Intent 视为世界行动已执行 |

先应用确定性的生存、失能、场景与合法性检查。Interactive 的主观认知/决策由当前 LLM 处理；可选 Cognition Gate JEV 只分类重要性，SM 授权下一次 Task，Host 排队执行。Inactive Gate 可联合判断优先 Background、Deferred 批次或受控 No-op。分别衡量漏判、误触发、延迟和成本；实际模型、阈值、深度预算与冷却仍待实验。

### 9.6 定期 EVA 与故障余量 `[DECIDED; NOT IMPLEMENTED]`

SM 管 Pending OB 的定期 EVA 与最长等待，**最大调度等待期限必须严格小于适用 OB Lifecycle，并留出执行余量**。Deferred 不能无限等玩家唤醒或到期；Inactive 批量 Background，Interactive 随正常交互或定期任务复用 Context。同一 NPC 至多一个有效认知 EVA，新 Urgent OB 提升后续优先级，不并发改同一 Meta、不改在途输入；合批不得重置最早等待期限。

正常运行应在到期前完成所需处理，但周期短于 TTL 不保证完成。Background 失败、LLM 超时、Mode Switch、Game Time 跳跃、Context Budget 不足、其他 EVA 占用与崩溃恢复均保护未完成证据/Work，先查 SM 持久 Result / Receipt，再合法续处理；到期仅移除 Recent 资格，不删除 Pending Work、不假装成功。Host 报资源/调用故障，不能自行完成或创建第二套权威队列。周期、最长等待、执行余量及游戏时间与运行耗时的对应仍 `[OPEN]`。

## 10. 运行正确性、安全与可追溯性

### 10.1 可重复的是规则结果与提交事实，不是 LLM 发言

- 保存 `invocation_id`、模型/配置标识（如需要）、NPC 身份、使用的视图版本、授权工具名、提议摘要/结构化参数、命令键 (session_id, command_id) / EVA evaluation_id 和 Observation/Memory 来源。
- 避免将完整私有 NPC Prompt、秘密全文或隐藏推理直接写进普通 Player/公共日志；调试审计数据也需要访问控制。
- Rule Engine 基于固定 Snapshot / Payload / RulesetBinding / 显式 RNGContext 保证机械求值一致性，权威 RNG 仅由 SM 成功原子提交推进；LLM 的人格决策可能不稳定，不能要求重复模型调用逐字相同。
- 对账与失败恢复依赖已持久化命令/回执；不得通过重新生成一次对话来推定上一动作是否成功。

**世界命令反馈 [DECIDED]**：区分 rejected、unsupported、合法机械失败、version_conflict、pending_choice 和传输/提交未知；RuleEvaluationResult 四态与 CommandReceipt 模型保持不变，unsupported 不新增回执状态，可由 rejected + 授权结构化原因反馈 Planner。确定性拒绝不强制再调用 LLM，仅新语义判断才有界重规划；原样重试用原 command_id，修改命令内容须新 ID，响应丢失先查原 CommandReceipt，不重掷或重复提交。

Narrator 保持游戏世界内的沉浸表达，不向玩家叙事直接暴露 API、Schema 或 unsupported 错误；也不能因为系统不支持就断言墙壁永久不可摧毁、骰点已失败或变化已发生。Planner 可提出合理情境解释，权威效果仍需正式提交；必要能力/运行时反馈由文字入口清楚表达，不伪造成世界事实。

### 10.2 典型故障与正确行为

| 故障/风险 | 正确策略 |
|---|---|
| 模型输出不合法 JSON/Schema | 受限重提议；失败明确提示，不写世界状态 |
| NPC 试图调用别人的控制器 ID | SM 核验可信主体与 NPC 绑定后拒绝，不由 LLM 断言权限 |
| NPC 请求不可见的秘密 | 从源头过滤 NPCView，拒绝工具访问 |
| NPC 捏造经历或把 Belief 当事实 | 拒绝无源/越权 Memory 写入；保留 Belief 的推断属性 |
| 未提交的取物 Intent 被旁观者知晓 | 这是泄漏，测试必须失败 |
| 同一 Observation 重投递 | 按稳定 observation_work_id / 来源 ID 去重，evaluation_id 防重复 Meta，command_id 防重复行动 |
| NPC 回复引发无限 NPC↔NPC 对话 | 自动激活深度/预算截断；保留未处理 Inbox |
| State Machine 已提交但 Host 丢失回复 | EVA 按 evaluation_id 查询已选 Result / EvaluationReceipt；行动按 command_id 查询 Command Receipt，不重新生成、不重掷或重复支付 |
| State Machine 持续不可用 / 持久化失败 | 停止权威推进；Host 无影子状态/游戏队列；按 SM 持久任务与回执恢复非战斗 |
| 战斗途中进程退出 | MVP 不支持从原回合精确恢复；仅符合战前安全条件时提示重开，否则阻塞 |

## 11. MVP 开发阶段与验收

**主线与早期验证 `[DECIDED]`：** 当前 SM＋RE 机制建设与 Agentic 验证交错推进（演进计划 §8）。最小可信动作/状态路径具备时，用受限真实模型验证自然语言能力组合、世界变化消费、NPC 私有信息/目标差异和宏观计划真正执行，不等完整传统引擎或完整 Host。延迟、重复及失败模型输出的授权/版本/幂等与一致性另做确定性回归，模型实验不替代这些证据。本轮未运行两类验证。下列 Host / Agent 清单不构成全量前置条件；完整 Coding Agent、沙箱、通用中断也不阻塞早期验证。v0.12 强制 EB 顺序撤回；EB-1～EB-3 只保留为可选 Evennia 评估，至少一名敌方 Agent 的宏观自主性验收不变。

优先以**完全原创的合成冒险 Fixture**开发与公开测试，再以合法获取、人工审核的 *First Blush* 私有资料完成端到端验收；不要把受限制的剧情、地图或派生包随代码推送公开仓库。

### 既有集成清单 AG-1：Host / View / NPC Identity

- DM 输入回合工作流与 NPC 调用边界；Role-filtered Context Builder；按 NPC 隔离上下文。
- 明确 Event Observation / Current Perceptual View 均由 Perception Projection 提供；创建、增量追加和释放 NPC 的逻辑 Context，不泄漏其他 NPC 的秘密。
- 原创两个 NPC 各自具有不同秘密、目标及相互冲突的 Belief；不能从 Prompt、工具或日志交叉读取。
- 验收：交错调用共享模型执行器，不串角色；同样的 WorldEvent 可产生不同合法 NPCView。

### 既有集成清单 AG-2：Typed Proposals / Authoritative Commit

- 玩家/NPC 行动、GM 有限裁决、简单世界创造和 Conditional Effect 对接统一 submit_command；NPC Evaluation / 对话发布生命周期保持独立。
- 至少覆盖可成功和被拒绝的取物/开门；错误身份、错误版本、模型自行宣告成功一律不能写权威状态。
- 验收：一条闭环 `player input → NPC decision → world commit → DM narration`；重复提交幂等。

### 既有集成清单 AG-3：Mode Routing / Observation-driven NPC Evaluation

- 调用 `get_event_observations`、按需授权 Current Perceptual View、统一 Result 最小提交、原子 Meta、引用/任务/版本检查、SM 内部完成状态、超时重试、持久化恢复。
- 验证 Evidence Persistence 与 Memory Consolidation 独立：关键承诺在事件提交时持久化；Memory Check 可返回 no-op，且不触发 Context Compaction。
- 做最小的 Context Keep/Release/Reactivate 与 Token 预算保护；复杂自动压缩算法留 Post-MVP。
- 验证 Interactive 独占、Inactive Gate / Background 一次调用、任务资格原子撤销与新建及内部 Processing Completion；接口仍为 Proposed / Not Implemented。
- 验收：观察在 NPC 未激活期间不丢失；两个 NPC 对同一事实形成不同 Belief；不合法/越权来源引用被拒绝（不声称证明文本忠实）；不同 Session 不串 Memory。

### 既有集成清单 AG-4：Agent 宏观自主性 / Combat Policy / Full Vertical Slice

- 验证敌方 NPC Agent 独立认知/宏观决定 → SM 合法采用 → Combat Policy 的即时 Typed Intent → RE / SM 提交 → 授权 Turn／Round 聚合观察及后续认知；不要求每次战术由 LLM 产生。
- 用 MODULE_CONTRACTS.md §12.6 原创王宫拔剑 / 火球术场景检查即时路径无 Planner / JEV / Gate / EVA 依赖、机械未知不当已察觉、Episode 聚合不泄密；Episode / 通用 Continuation 仍待接口设计，不宣称场景已经可执行。
- 对接单人冒险的社交、探索、检定、战斗与结局流程；优先修复已确认的 Engine 接口/资源归属阻塞。
- 验收：规则求值经 Engine 计算、State Machine 统一提交，战斗状态正确、非活跃战斗可存档恢复；活跃战斗重载按 SM-02 明确不支持。

v0.2 的 Context 生命周期属于 AG-1/AG-3 的增量验收，不单列一个大规模 Memory Agent 或独立“缓存基础设施”开发批次，避免 MVP 被性能优化吞噬。

以上为既有能力与集成检查清单，不要求按编号串行完成或等全量 Host 后才试验 Agentic 行为。后续实现按实际依赖切片并审阅 SM / Agent / RE 交接，遵循 MODULE_CONTRACTS，不在本轮生成新代码批次或冻结接口。

### 11.1 原创合成测试清单

| ID | 场景 | 必须成立 |
|---|---|---|
| AG-A01 | 同一底层模型交错调用 NPC A/B | 身份、私有知识、Memory 不串线 |
| AG-A02 | DM 知道某秘密但 PC 不知道 | 玩家叙事中不泄漏该秘密 |
| AG-A03 | 玩家指示 NPC 直接交出金币 | NPC 独立决定是否同意；最终归属只由 submit_command 的 world.* TypedCommand 提交改变 |
| AG-A04 | NPC 自称攻击命中 | 未经 State Machine 的 CommandReceipt 确认已提交，不可显示已发生的命中/伤害 |
| AG-A05 | 两 NPC 私下都想取硬币，只有 A 成功 | B 观察 A 拿走硬币；A 不知道 B 未外显的 Intent |
| AG-A06 | A/B 真实同时伸手且互相看见 | 两者都能观察公开动作；先后由游戏裁决而非网络速度决定 |
| AG-A07 | B 看到 A 拿走硬币并猜测 A 故意挑衅 | 推断写为 Belief，不写公共事实 |
| AG-A08 | NPC 收到观察后长时间未激活 | Inbox / Pending Work 可靠保存并受有界调度；下次激活读取有效 Recent OB，过期未完成证据仅走受限恢复输入 |
| AG-A09 | NPC 记忆提议引用别人的 Observation | 拒绝且无私有数据泄漏 |
| AG-A10 | 多次重试相同 NPC 激活/记忆更新 | 不重复写记忆、关系 Delta 或奖励 |
| AG-A11 | NPC A ↔ NPC B 自动互相回应 | 预算截断且未消费观察保留 |
| AG-A12 | NPC 模型不可用 | 不伪装为已自主决策，不凭空提交行动；保留 Inbox 与已提交证据 |
| — | Context 缓存沿用旧的门状态 | 新的可感知事件/当前感知必须动态入 Context；提交动作时再校验，不因缓存命中而忽略新状态 |
| — | NPC 重进场景但没目击之前谁开门 | 只提供当前门已打开的感知，不补发当时没有观察到的行为人身份 |
| — | Memory 成功写入后被重复插入当前 Context | 可继续使用已有历史；后续增量追加已提交变化，不逐 EVA 全量重注入，不增加语义检索/Ranking |
| — | Context 资源管理试图写入新 World Fact / Belief | 不具备 Meta/事实写权限，MVP 不新增智能摘要压缩 |
| — | NPC Suspend/Release 后激活 | 从可靠记忆/Inbox/当前感知恢复，不能因为缓存释放而丢失 Observation |
| AG-A13 | NPC 宏观提议或即时 Policy 输出不可用/非法 | 分别验证/反馈，不以等待 EVA 代替即时执行，也不绕过 Engine 资源/行动预算；缺机械证据不默认已察觉 |
| AG-A14 | 非战斗 Session 重启 | NPC Knowledge、Observation、Memory 及任务状态保留 |
| AG-A15 | Gamebook/World Builder/图像引擎均关闭 | MVP 文字端到端仍可完成 |

### 11.2 v0.2 新增合成验收（继承 AG-A01–AG-A15）

| ID | 场景 | 必须成立 |
|---|---|---|
| AG-A16 | A 在场目击玩家开门，正在连续交谈 | 新 Event Observation 有序追加到 A Context；不需清空历史或重建全部 Prompt |
| AG-A17 | B 不在场时有人开门，后来 B 进屋 | B 只能收到门当前打开的 Current Perceptual View；不能获知开门者身份 |
| AG-A18 | NPC 已收到旧的「门关闭」观察，但现在门打开 | 旧观察保留时间戳，新感知覆盖**当前决策依据**；提交前再次校验 |
| AG-A19 | NPC 的新长期 Memory 被保存 | 当前活跃 Context 不因此压缩，也不强制重复注入新记忆文本 |
| AG-A20 | Context 预算压力 / 安全重建 | 不新增 World Fact / Belief / Commitment，不静默筛掉完整授权 Meta；MVP 不新增智能压缩 |
| AG-A21 | NPC 接受承诺后未做 Memory Consolidation 即崩溃 | 已确认承诺事件仍存在；重启后可再独立整理 NPC 私有记忆 |
| AG-A22 | NPC Suspend/Release 后重新激活 | 已持久记忆、未完成 观察可恢复；当前感知按新时刻刷新，完全不依赖物理 KV Cache |
| AG-A23 | Meta 验证失败 / 完成事务前后崩溃 | 非法批次全部不写且不选最终 Result；已提交结果重试只返回原 EvaluationReceipt |
| AG-A24 | DM 没提出 NPC 激活，但该 NPC 被可见威胁直接针对 | SM 按领域策略批准 Task，Host 调用该 NPC，保持其人格决策权，不产生无限反应循环 |
| AG-A25 | NPC 记忆提议引用一次未记录的 Current View 或其他 NPC 私密观察 | 拒绝伪造证据引用；当前感知若用于长期记忆先获取可核验来源 |

**验收级别**：以上是架构协议的合成测试目标；不等于已经完成测试，也不要求 MVP 实现高级视觉遮挡、向量记忆库或多玩家共享世界。数值化性能门槛需通过实测设定。

### v0.3 追加验收（原创合成场景）

| ID | 情景 | 必须满足 |
|---|---|---|
| AG-A26 | NPC 不活跃时目击重大事件 | 无需运行对话 LLM 即可持久保存 OB / Pending Work；后续合法 EVA 可选提出长期 Memory，不能将 OB 自动称为长期 Memory |
| AG-A27 | Inactive Gate 将普通 OB 判为 Irrelevant | 获准 No-op 完成工作，TTL 前仍 Recent；到期后仅满足全部保护条件才清理，不损毁重要证据、WorldEvent 或承诺 |
| AG-A28 | Inactive NPC 目击朋友遇袭 | Gate 可触发一次 Background Evaluation，生成本人可选认知/行动提议，不创建 Interactive Agent |
| AG-A29 | Jev / 轻量 Trigger 漏判或服务不可用 | 保守确定性保底保护关键事件；不会丢失重要观察或强制依赖专有模型 |
| AG-A30 | NPC 日程在建筑被毁后到期 | 条件重验证拒绝不可能活动，不错误移动 NPC 或形成虚假事件 |
| AG-A31 | 玩家见闻由 DM Planner 处理 | Narrator 仅看可向玩家公开的已提交结果；GM-only/其他 NPC 内心不泄漏 |
| AG-A32 | Rule Evaluation 已接受但 State Machine 提交失败 | DM Narrator 不得叙述已成功；Agent 不获得未提交世界状态 |
| AG-A33 | 背景 Behavior Trigger 重复到达 | 不重复派发 Evaluation、不重复关系更新、不无限事件循环 |

### 11.3 v0.4 双模式合成验收（设计目标，尚未执行）

| ID | 场景 | 必须满足 |
|---|---|---|
| AG-A34 | Interactive NPC 连续收到新 Observation | 原 Context 按序增量追加，当前 Interactive LLM 处理；必经 Gate 决策（模型可选） 无逐条强制，新 Background / Memory / Cognition LLM 调用数为零 |
| AG-A35 | Context Active，模型请求暂时空闲，重大事件到达 | SM 批准下一次 Interactive Task，Host 执行推理；在途请求的新观察排队供后续调用，不修改执行中请求/KV Cache |
| AG-A36 | 一次 Interactive Result 包含 Dialogue、Belief、Memory、Action Intent | Meta 整批验证原子提交；Dialogue / Action 独立交接，行动只有 Command Commit 后成事实，全空 Result 也合法 |
| AG-A37 | Inactive NPC 经 Gate 决定追查目击事件 | 一次 Background LLM 产生 Goal / Plan 与独立 Action Intent；不创建/恢复/激活 Interactive Context，临时 Context 释放 |
| AG-A38 | 普通低价值 Observation | Safe Retention / No-op 有回执并由 SM 记录完成；不调用完整 NPC LLM，不丢关键证据 |
| AG-A39 | Background 在途时开始 Interactive | SM 原子取消旧有效 EVA、保留 Meta、移交 Work 并新建 Evaluation，不等旧反馈；迟到结果拒绝，新输入含玩家输入 |
| AG-A40 | 模型失败、重复投递、版本冲突或完成事务前后崩溃 | evaluation_id / 唯一 Result 防重复 Meta，command_id / 可靠交接防重复行动；失败保留未完成认知/交接工作 |
| AG-A41 | 任一模式 Meta 持久化成功 | 不强制重建或重复注入；资源压力只要求预算保护/安全重建，MVP 无智能压缩 |

### 11.4 v0.5 职责与统一协议验收（Proposed / Not Implemented）

这些是待实施的原创合成验收目标，本轮只验证文档一致性。

| ID | 场景 | 必须满足 |
|---|---|---|
| AG-A42 | 触发 Evaluation / 轻量 Gate | SM 创建授权 Task、验证采用分类候选；Host 只运行模型，不持久决定任务或观察完成 |
| AG-A43 | 一 Task 重试、多 Task 复用 Context | Evaluation ID 稳定，多 Invocation；Interactive Context 可服务多 Evaluation，Invocation/Context ID 非提交必填 |
| AG-A44 | LLM 自报 NPC / 任务状态 / 版本或仅 Evaluation ID | SM 核验可信运行主体及 Task 内身份/权限/引用/版本/状态，ID 不认证，也不能恢复取消资格 |
| AG-A45 | 两种模式联合或全空输出 | 同一/兼容七字段 Result，只提交 evaluation_id + result；可信关联从 Task 恢复，模型不生成可信元数据 |
| AG-A46 | EVA 已提交并可靠交接，行动失败/等待选择 | EVA / 必要认知处理可完成，无 ACK；Command 独立跟踪，反馈不自动重做完整 EVA，读/追加/模型返回本身不完成 |
| AG-A47 | Dialogue 夹带未执行动作或越权秘密 | SM 验证发布/受众/可观察事件权限，Narrator 只消费获准已提交事实 |
| AG-A48 | SM 持续不可用后恢复 | 停止权威推进，Host 无影子游戏状态或独立执行队列；依 SM 持久任务与回执恢复非战斗 |

### 11.5 v0.6 简化 EVA 合成验收（Proposed / Not Implemented）

以下为待实现目标，本轮仅静态检查文档，未运行模型或数据库故障测试。

| ID | 场景 | 必须满足 |
|---|---|---|
| AG-A49 | 同 EVA 相同/不同 Result 重试 | 每任务至多一个最终 Result，相同返回原 EvaluationReceipt，已选后不同结果拒绝；独立行动仍用 command_id |
| AG-A50 | 未选定前 Schema / Meta 非法 | 当前有效 EVA 有界修正；任一 Meta 非法整批不写，Goal 拒绝不会留下依赖 Plan |
| AG-A51 | Meta 合法、Action Intent 非法或执行失败 | Meta 保留、EVA 可完成，可靠交接/明确拒绝持久；独立 Command Receipt，反馈不自动重做完整 EVA |
| AG-A52 | 切换时旧 Invocation 无法取消 | SM 原子取消旧有效 EVA 并新建、不等旧反馈；新输入含最新 Meta/未完成观察/玩家输入，新 Invocation 不复活旧任务 |
| AG-A53 | Invocation Timeout / API / Schema / Meta 错误 / 耗尽 / 丢响应 | 有效且有预算保持 running，同 evaluation_id / 新 invocation_id 重试；仅耗尽或无法继续 failed，切换 cancelled；先查持久结果 |
| AG-A54 | 完整 Meta 首次输入、Context 复用和预算压力 | 完整授权六类 Meta + 冻结完整授权 Recent OB List（含 processed／pending），Host 不语义筛选/检索/排名/智能压缩；后续增量追加，不每 EVA 全量重注入 |
| AG-A55 | Initial Belief 被修改/降置信度/放弃 | 兼容结构、稳定 Belief 追加版本，来源/有效状态/旧历史保留；SM 不改写文本 |
| AG-A56 | 合法引用却错误的主观 Belief / Memory 文本 | SM 不声称判断自然语言忠实性、不改写文本，不新增 Semantic Validator LLM；错误信念不改 World Fact |

### 11.6 v0.10 OB Lifecycle 与调度合成验收 `[PROPOSED; NOT IMPLEMENTED]`

以下是待实施的原创合成目标，运行测试尚未执行；跨模块细节见 MODULE_CONTRACTS.md §12.4。

| ID | 场景 | 必须满足 |
|---|---|---|
| AG-A57 | Irrelevant No-op / 全空 EVA | 完成不要求长期 Meta；processed OB 在 TTL 前仍可为近期背景，重复读取不重排同一 Work |
| AG-A58 | Inactive Urgent / Deferred 批次 | 无持续 Interactive Context；Urgent 优先联合七字段 EVA，Deferred 定期/最长等待批处理，同 NPC 至多一个有效认知 EVA |
| AG-A59 | Interactive Urgent / Deferred / Irrelevant | 下一轮优先 / 正常或定期批量 / 受控 No-op；Gate 决策必经，模型无逐 OB 强制调用，无新 Background EVA，不改在途输入或旧 Task 完成范围 |
| AG-A60 | OB 入 Context 后游戏时间到期 | SM 改有效性，Host 下一 Invocation 可通知；不删旧 Token/自动压缩/重做 EVA，不承诺严格遗忘，重建排除过期 Recent OB |
| AG-A61 | OB 多 Meta / 历史引用到期 | 必要原始证据/来源归档，内部保留不等仍记得，不自动将归档原文回注 Context |
| AG-A62 | 定期调度异常越期 | 最大等待严格小于 TTL 且留余量；失败/超时/切换/跳时/预算/占用/崩溃保留 Pending Work，先查持久结果再合法续处理 |
| AG-A63 | JEV 模型复用两任务 | 输入输出 Schema / 权限分离，Gate 只分类已察觉 OB、不生成 Memory/Belief；确定性/批量分类可替代逐条模型调用 |

## 12. 决策登记 / 后续文档接口

| ID | 问题 | 状态与本阶段处理 |
|---|---|---|
| AG-01 | DM 主持、NPC 决策权分离 | **已确认**；见 MVP Scope |
| AG-02 | NPC 按需执行，共享执行器可行但上下文独立 | **已确认原则** |
| AG-03 | WorldEvent → Perception → Observation → NPC Memory | **已确认基础架构**；依 SM-03 |
| AG-04 | Memory 解释由 NPC 提议，Cognition 管版本/来源并持久化 | **已确认；2026-10-12 按 MC §0.3 修订旧 SM 独占限制** |
| AG-05 | LLM 私有 Intent 不可变成外显世界事件 | **已确认原则** |
| AG-06 | 敌方 Agent 宏观自主性与即时 Combat Policy | **[DECIDED]**；至少一名敌方 Agent 的决定实际影响受控行为/后续认知，无每次 Tactical Intent LLM 要求；绑定接口 [OPEN] |
| AG-07 | 普通怪物的认知 Agent 覆盖 / Policy 配置 | 即时战术无必经 LLM 已 [DECIDED]；认知覆盖与具体配置 [OPEN]，见 MVP D26 / AP T02 |
| AG-08 | 共享 LLM 调用的并发数、预算、超时、Fallback | **待性能测试与产品决定；不擅自冻结数值** |
| AG-09 | DM 对例外/开放式动作的 GM Override 范围 | **待 MODULE_CONTRACTS 明确合法裁决协议** |
| AG-10 | 自主 NPC ↔ NPC 无限会话、常驻 AI 同伴 | **不属于 MVP** |
| AG-11 | 战斗中途跨进程精确恢复 | **不属于 MVP**；依 SM-02 |
| AG-12 | 长期记忆向量检索、压缩、冲突自动消解 | **Post-MVP 可增强**；MVP 保留来源及基本关系/信念 |
| AG-13 | World Creation Agent、动态视觉引擎 | **Post-MVP**；当前不实现 |
| **AG-14** | Event Observation + Current Perceptual View | **v0.2 首次确认、v0.3 保留**；两种感知均经同一 Perception/权限边界进入 NPC Context，后者不能泄漏未目击历史 |
| **AG-15** | Memory Persistence 与 Context Compaction | **v0.2 已确认分离原则**；语义触发与资源压力触发独立，重要证据即时持久化 |
| **AG-16** | NPC Active Context 生命周期 | **v0.2 已确认设计原则**；同一 NPC 连续互动增量追加、按需 Keep/Release/Rebuild，Scene Change 非强制销毁 |
| **AG-17** | 领域任务 / Host 模型运行 | **v0.5 原则保留，v0.14 按 MC §0.3 分责**；Cognition 管任务／模式／Gate／pending／processed，Perception 管察觉／观察保留，Host 只管模型/Context/预算 |
| **AG-18** | Compaction / Cache 优化 | **MVP 最小预算保护**；高级自适应压缩与缓存命中策略延后，不能牺牲状态新鲜度和权限 |
| **AG-19** | Current Perceptual View 的证据化与版本契约 | **待 MODULE_CONTRACTS 冻结**；禁止由 NPC 自造观察 ID |
| **AG-20** | Persistent State / Evaluation Context 与双模式独占 | **v0.4 已确认原则**；当前 Interactive LLM 独占主观认知/行为；Inactive Background 不激活 Interactive Agent |
| **AG-21** | 模式切换、EvaluationStatus / Result / Processing Completion | **已确认可靠性要求，协议 Proposed / Not Implemented**；取消并拒绝旧结果，已提交结果先对账；具体字段与预算待评审 |
| **AG-22** | OB 短期记忆与双生命周期 | **[DECIDED] 2026-10-11**；Processing 不等 Retention，Game Time TTL、来源归档、过期 Pending 保护；无独立 Short-term Memory，接口/清理参数仍开放 |
| **AG-23** | JEV 双职责与定期 EVA | **[DECIDED] 2026-10-11**；可共享模型但 Schema/权限分离，Interactive 必经 Gate 决策（模型可选） / 无新 Background，最大调度等待严格短于生命周期且留余量；具体编码/模型/周期未冻结 |
| **AG-24** | 运行与认知分离（v0.12 历史采用路线已撤回） | Host 无权威游戏状态、即时行为与认知分离、CombatEpisode 及受控扩展原则保留；Evennia 优先采用/强制 EB 顺序由 v0.13 撤回，EVA 标识/完成协议不重设计 |
| **AG-25** | SM＋RE 主线与早期 Agentic 验证 | **[DECIDED] 2026-10-12**；机制与真实模型试验交错，代码负责可验证执行/后果，NPC 保留私有认知与宏观自主性；具体扩展/聚合协议 OPEN，未运行验收 |

**最终执行原则 `[DECIDED]`**：MC §0.3 规定领域状态负责人和共享提交，不再要求 SM 持有全部 Runtime State。RE 无隐藏跨请求权威状态、无 Legacy Stateful 执行依赖，允许调用内候选状态/临时事件缓冲。一次不可分割规则操作中角色/效果/战斗/RNG 同成同败；EVA 的 Meta / 唯一 Result / 完成及可靠交接仍是独立事务，不能把未来全部行动和感知处理一起并入。旧 API 退出标准见 MC §14.1；此决定不声称 Handler 重构或 RE 日志解耦已完成。

**已确认的逻辑分离**：DM Planner / Narrator；NPC Perception-only；NPC State / Evaluation Context；Interactive / Background Mode Exclusivity；Memory / Cognition / Behavior Trigger 可联合判断；NPC Schedule-driven 基础行为。Jev、模型、阈值、压缩算法和普通怪物默认策略仍待实验或产品确认。

**后续接口审阅**：以 `MODULE_CONTRACTS.md` 为跨模块目标接口最高规范，在已有 [DECIDED] 约束内继续评审实际 JSON Schema、身份验证、Observation/Memory 读写、NPC Combat Intent、幂等键、错误类别及 Stateless 求值字段；具体 ABI 的 [PROPOSED] / [OPEN] 不因本次架构对齐变为已批准或已实现。README 只提供架构概览与正式文档入口。

**冻结条件（建议）**：确认普通怪物的默认 Agent/Policy 策略；审核 State Machine Task / Status、原子 Meta、可靠交接及完整输入的 Schema；核实 Rule Engine 支持的 NPC Typed Intent 和 Hazard API；至少让原创合成场景完成一个真实的 NPC 决策 → 状态/规则裁决 → 感知 → 记忆 → 后续选择循环。本文现在仅为架构草案，不表示代码已经交付。

## 13. 变更说明与文档协作边界

### v0.14 领域状态与共同提交（2026-10-12）

按 MC v0.14 §0.3 替代 SM 独占所有状态限制，更新图、数据表、调用链及 AG-04 / AG-17。NPC Cognition 管追加版本 Meta，Perception 管授权观察，Combat Handler 管持久流程；内部受控接口不向模型开放。Evaluation 身份/授权/模式/版本失效、近期观察、可靠 Work、整批 Meta 与独立行动输出/结果边界保留。仅文档，未实施 Handler 重构或 RE 日志解耦。

### v0.13 游戏核心与早期 Agentic 验证

恢复当前 SM＋RE 主线，撤回 Evennia 必经路线；保留模型执行/权威状态分离、私有认知、CombatEpisode 与既有 EVA/OB 协议。机制研究与可选 Coding Agent 服务于开放行动和真正可执行的 NPC 计划，早期真实模型试验与确定性回归分开取证。本批只修文档，不实现 Host、扩展系统或运行测试。

### v0.12 运行与认知边界同步（历史，采用路线/强制 EB 顺序由 v0.13 撤回）

明确 Evennia 目标运行层与可替换 SM 实现、RE 规则求值及 Host 模型运行的分工；同步整场 CombatEpisode、三类感知/行动/认知信息及受控扩展。开发优先级改为 EB-1～EB-3，保留 NPC 宏观自主性和既有 EVA/OB 生命周期。本批仅文档，无迁移或运行验收结果。

### v0.11 双路径、WorldEpisode 与控制边界同步

消除每次敌方 Tactical Intent 必经 Sub-agent 的旧冲突，保留独立 NPC 认知、宏观决策及其行为影响验收。即时机制由 SM / Combat Policy / RE 执行，不依赖任何认知 LLM；JEV 只用于后续认知观察准备。目标 EpisodeObservation 只聚合已察觉部分，阶段结果仍不可变；Schema、增量/生命周期及通用 Continuation ABI 保持 OPEN。仅文档，代码状态统一引用 MODULE_CONTRACTS.md §1.1，既有 Host / EVA / OB 可靠性边界不变。

### v0.10 OB Lifecycle 与调度同步

OB 直接承担短期感知记忆，完成后到期前仍可用；Processing / Retention、长期 Meta 来源归档与 Context Token 生命周期分开。JEV 两种判断可共享模型、Schema / 权限隔离；Inactive 优先/定期批量/No-op，Interactive 复用现有 Context、Gate 分类可选、无新 Background EVA。新增故障保护和合成验收；未实现接口、未冻结 TTL/模型/算法，也不修复 Event-time Perception P1。

### v0.9 NPC Perception 契约同步

事件 Signals 经事件时 Discovery 与确定性/受限 JEV 判断，SM 验证形成授权 Observation；内部来源不成为 NPC 全知信息，通用查询也不能绕过感知。沿用既有 Context / Inbox / Gate / EVA，完整字段和检定编排仍待设计。

### v0.8 世界命令与 GM 裁决同步

统一 TypedCommand 信封与普通提交入口；明确三个验证领域、有限动态创造、条件式效果和授权反馈，AP-15 按操作类型核验 Actor / 来源。查询允许早期同步开发，NPC 模式、Meta / EVA 与 Action Execution 隔离原则不变，具体字段仍待设计。

### v0.7 P0 同步与 EVA 失败澄清

规则执行仍由 SM 提供完整 CombatSnapshot / NonCombatSnapshot、Session 固定 RulesetBinding 与独立 RNGContext，Engine 返回四种规则结果；Schema/运行时/传输错误另行处理。Meta / EVA 与 Action Execution 继续隔离。Invocation 预算内失败不使整个 EVA 最终 failed，也不重新引入额外标识或 ACK。接口结构与只读查询见 MODULE_CONTRACTS.md §4–§6，均为目标设计。

### v0.6 相对 v0.5 的主要修订

1. Evaluation ID / Status、NPCStateVersion 与 Observation Work 形成任务提交边界；最小入口只需 evaluation_id + Result，可信身份来自运行环境与 SM Task。
2. 每 EVA 至多一个持久最终 Result，Evaluation ID 为 Meta 幂等键；首次合法结果在同一 SQLite 事务选定、整批提交 Meta、可靠交接输出并完成任务。
3. Memory / Belief / Relationship / Goal / Plan 任一项非法整批不写、有效任务有限修正；SM 不验证自然语言忠实性、不改写 Belief、不新增 Semantic Validator LLM。
4. EVA 与 Action Execution 分离，command_id / Command Receipt 独立；完成不等动作成功，可靠交接防漏防重，动作失败不自动重做完整 EVA。
5. 模式切换直接撤销旧有效 EVA、保留 Meta、移交 Work 并新建；新 Interactive 输入含玩家输入，不等旧调用/失败反馈/ACK。
6. MVP 输入完整授权 Meta、保留追加版本的 Belief History，Host 不语义筛选/检索/排名/智能压缩；Context 可增量复用。保留唯一权威、双模式独占、DM 隔离、原 MVP 范围和故障恢复边界。

### 与其它文档的正式分工

- **`STATE_MACHINE_ARCHITECTURE.md` v0.20**：当前 SM 基础与目标领域模块、有状态 Handler、共享提交/恢复；本文件不重定义事务实现。
- **`ADVENTURE_PACKAGE_SCHEMA.md` v0.14**：NPC 初态、固定包、一次初始化与 Session 扩展，不保存后续推理 Context/动态 Meta。
- **`AGENT_ARCHITECTURE.md` v0.18**：模式独占、Cognition / Perception 分责、Host Runtime、Context 与失败边界。
- **`MODULE_CONTRACTS.md` v0.18 / Draft**：最高规范，领域状态表及校验/提交分责，具体 ABI 仍 Proposed / OPEN；本文 YAML 仅为示意，演进计划不另立规范。

### 仍应保持开放的技术问题

NPC/普通怪物的认知覆盖、Combat Policy 算法/绑定/授权与目标转换、受控 NPC Intent 的跨版本 Consumer、Current View 的缓存 TTL/证据化方式、Cognition Gate 重要性阈值、上下文压力指标/压缩算法、NPC 自动反应的深度预算、长时记忆合并/冲突消解等都需实测或下一文档再决定。不得把这些未验证细节写成已经交付的能力。

**v0.13 的核心不变量：NPC 持久事实具有单一权威来源；当前模式的 LLM 提议主观认知与宏观意图，即时机制独立执行；Interactive 活跃时不额外启动 Background 认知；Perception、Memory 与 Context 各有生命周期；世界变化只由可信运行层提交。**
