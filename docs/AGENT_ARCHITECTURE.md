# Agentic TRPG — Agent Architecture（MVP，Draft v0.3）

> **文档状态**：Draft v0.3；描述拟议架构，不代表已经实现、通过测试或所有接口已冻结  
> **日期**：2026-10-09  
> **建议位置**：`agentic-trpg/agentic-trpg/docs/AGENT_ARCHITECTURE.md`  
> **依据**：[`ADR-001`](./adr/ADR-001-UNIFIED-STATE-OWNERSHIP.md)、[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.5、[`STATE_MACHINE_ARCHITECTURE.md`](./STATE_MACHINE_ARCHITECTURE.md) v0.3、[`ADVENTURE_PACKAGE_SCHEMA.md`](./ADVENTURE_PACKAGE_SCHEMA.md) v0.2；2026-10-09 Agent Context / Memory 讨论总结（设计输入）  
> **目标产品**：一名真人玩家直接控制一名 PC；本地、文字优先、无常驻 AI 队友；以人工整理的单人 Adventure Package 运行首个完整冒险。World Creation Agent、Visual Presentation Engine 与活跃战斗的跨进程精确恢复均属于 Post-MVP。  
> **内容边界**：本文仅使用通用概念及原创合成示例，不包含 *First Blush* 正文、地图或实质性的改编剧情数据。该剧本仅作为**私有**端到端验收来源。
> **v0.3 修订主题**：统一状态所有权依 ADR-001；DM Planner 与 Narrator 隔离；Event- and Current-Perception 统一；Memory Gate 与非交互 Cognition/Behavior Trigger；NPC 游戏时钟日程；Jev 仅作为可替换实验候选。

> **继承 v0.2 的原则**：Event Observation 与 Current Perceptual View 统一通过 Perception 进入 NPC Context；Evidence Persistence、Memory Consolidation、Context Compaction 和 Suspend/Release 独立管理；保留 v0.1 的权限、战斗、异常回执和 MVP 边界。

## 0. 决策层级与需要澄清的冲突

**已确认的产品原则**（来自 MVP Scope 与 State Machine v0.2）：

1. **DM Planner 是主持与协调决策者；DM Narrator 独立负责已确认事实呈现**：解释玩家表达、组织交互、作 GM 语义裁决、调用规则及叙述已确认结果；不代 NPC 决定个人目标和自主行为。
2. **NPC Sub-agent 具有独立角色身份和私有上下文**：在需要时被调用；一个模型进程可服务多个角色，但每次调用只能接收该角色已获授权的信息。
3. **提议 ≠ 已发生事件 ≠ 观察 ≠ 记忆**：NPC 输出没有直接修改世界或机械状态的权力。State Machine 统一持有并提交 World、Character、Combat 和 RNG State，Rule Engine 只对显式快照求值并提出 State Delta。
4. **Observation → Memory Gate / Cognition**：State Machine 可靠保存观察证据；轻量 Memory Gate 可在 NPC 不活跃时筛选 Durable / Short-term / Discard；NPC Sub-agent 负责复杂的 Belief/Relationship 解释和更新提议，State Machine 验证后持久化。
5. **事件驱动与游戏时钟日程**：只有互动、重大非交互认知事件、必要的行为中断或轮到其行动时才调用 NPC；普通日程由可验证的确定性调度维护，不采用常驻 NPC 模型、无限后台交谈或持续社会模拟。
6. **动态 Perception 是 NPC 唯一的世界观察入口**：事件观察与当前环境感知均经 State Machine 权限过滤；不向 NPC 额外灌入 DM-only 的“权威世界真相”。
7. **三个持久/上下文过程分离**：世界证据及时持久化；长期记忆由 NPC 提议、系统验证；Context Compaction 只管理推理资源，既不等于记忆生成，也不保证物理 KV Cache 保留。

**存在的文件间冲突，本文不擅自消除：**

- `MVP_SCOPE.md` §2.2 与 D16 明确要求**敌方 NPC 战术由 NPC Sub-agent 提议**，§2.3 也要求具独立上下文的战斗 Intent；但该文件 D26 同时将**每个普通 NPC/怪物是否必须调用 LLM**列为待决策。
- `FIRST_BLUSH_MVP_REQUIREMENTS.md` §3、§7 则为普通训练对手和简单怪物推荐**确定性 Tactical Policy**。
- `ADVENTURE_PACKAGE_SCHEMA.md` §5.2 允许 `sub_agent`、`deterministic_policy`、`scripted_event` 三类控制器，并明确至少一名敌方 NPC 的显式战术 Intent 需要独立 Sub-agent 验收。

**本文件的处理**：保留全部控制策略，**不得把确定性策略冒充 NPC Sub-agent**。在产品负责人澄清前，开发验收必须满足已确认的敌方 NPC Sub-agent 战斗决策要求；「每只普通怪物是否调用 LLM」仍待决定。需要的 Rule Engine 公共 NPC Typed Intent 入口若尚未具备，应明示为阻塞，不用冒充 PC 或直接改内部 Combat State 绕过。

## 1. Agent 模块的定位与不变量

Agent 模块负责有意义的**非确定性认知工作**，而不是成为第二个游戏执行引擎。

| 参与者 | 可以决定 | 不能自行宣布或修改 |
|---|---|---|
| 真人玩家（PC 控制者） | 自己的角色想说、想做什么；接受/拒绝建议 | 不可声明未经结算的命中、伤害、事件成功 |
| Agent DM | 如何理解玩家表达、应查看何种事实、是否需要 GM 语义裁决/检定、可**请求**激活哪位 NPC、如何呈现已提交结果 | 不可代替 NPC 作个人选择；不可未经授权修改 HP/Slot/道具归属；不可把叙事等于提交 |
| NPC Sub-agent | 该 NPC 的发言、主观解释、目标驱动决策、允许范围内的下一步行动及记忆更新**提议** | 不可读取别人的秘密/未外显 Intent；不可越权提交状态；不可替自己决定骰点成功 |
| Agent Host / Orchestrator | 最终决定有界的 NPC 调度、排队、调用、Context 生命周期、预算、超时、重试、递交提议、组装许可的感知 Context | 不可绕开 State Machine 权限检查或 Rule Engine 的机械裁决 |
| State Machine | 权威世界事实、World/Character/Combat/RNG 唯一权威状态、感知、观察、记忆持久化、最终事务提交 | 不承担 LLM 主观推理及 D&D 机械公式重实现 |
| Rule Engine | 检定、攻击、伤害、资源/回合/Condition 等受支持的机械**求值**（输出未提交的 State Delta） | 不负责塑造 NPC 角色动机、编剧情或决定哪个 NPC 知道什么 |

**不变量：**

- **Truth vs Knowledge vs Belief**：客观世界事实不等于角色已知；角色的猜测、欺骗和偏见不能提升为世界事实。
- **Private Intent vs Observable Act**：未外显的内部 Intent 绝不能被其他 NPC 观察；实际上已执行的动作可以按感知条件投影。
- **Proposal vs Commit**：Agent 的文字、工具参数和记忆提议均非权威；只有可追溯的系统提交/规则回执才能赋予副作用。
- **Single Controller per Actor/Operation**：每次操作须绑定可信控制主体；LLM 自报 `controller_id` 不构成认证。
- **Do not secretly railroad**：自由合理的玩家行动不能因为冒险预写路线而自动失败；超出可支持范围应明确询问/拒绝/受控裁决。
- **No silent fallback impersonation**：NPC Agent 调用失败不能让 DM 悄悄代 NPC 做人格选择，然后仍宣称经过独立 Sub-agent 决策。
- **Persist evidence, not chain-of-thought**：保存已提交意图/结果、Observations 和经授权的 Memory Proposals；不要求保存模型私有推理链，也不追求重生成相同话术。
- **Perception-only environment updates**：NPC 所见世界的增量与快照只能通过其授权感知投影进入 Context；世界版本号是 Host 的一致性元数据，不是 NPC 获得全知的理由。
- **Correctness before cache reuse**：缓存前缀稳定性是优化目标，不能阻止新的观察进入 Context 或绕过提交前重验证。

## 2. 逻辑架构与组件

```text
                              Human Player (one PC)
                                       │ natural language
                                       ▼
                               Agent DM Runtime
                          ┌────────────┴─────────────┐
                          │ DM Turn / Scene Coordinator
                          │   ├─ PC Intent Interpreter
                          │   ├─ GM Adjudication Planner
                          │   ├─ NPC Activation Requester
                          │   ├─ Proposal / Receipt Handler
                          │   └─ Narrative Presenter
                          │
                          └─────── Agent Host ──────────────────────┐
                                     │                             │
                                     │ request_npc_view(npc_id)     │
                                     ▼                             │
                              State Machine                         │
                     ┌──────────────────────────┐                  │
                     │ Session / Scene / World  │                  │
                     │ Role-filtered View       │                  │
                     │ Event → Perception       │                  │
                     │ Observation Inbox        │                  │
                     │ NPC Memory Repository    │                  │
                     │ Command/Version Gate     │                  │
                     │ SQLite Persistence       │                  │
                     └──────┬─────────┬─────────┘                  │
                            │         │                            │
                            │         └── authoritative adapter ──► Rule Engine
                            │                                      (checks/combat)
                            ▼
                         NPCView[npc_id] + Perceptual View
                            │
                            ▼
                     Host Activation/Context Lifecycle ◄─────────────┘
                            │
                            ▼
                     NPC Sub-agent Invocation
                     (one isolated NPC context, shared model possible)
                            │
                            ├── NPCDialogueProposal
                            ├── NPCActionIntent / NPCCombatIntent
                            └── NPCMemoryUpdateProposal
                            │
                            ▼
                Host validation → State/Engine execution
                          │                │
                          └── Receipt ◄────┘
                                │
                                ▼
                        DM narration to player
```

这表示**责任和信任边界**，不是要求多个进程/仓库/模型。MVP 可采用一个 Python 单进程 Host、一个共享的 LLM Executor、多种相互隔离的角色请求，以及本地 SQLite State Machine。网络传输、是否复用同一 Python 进程、模型厂商均不在本阶段冻结。

### 2.1 Agent Host

Agent Host 是 Agent DM 模块的执行基础设施，不是独立世界数据库或新顶层产品模块。负责：

- 从 State Machine 请求**以调用者身份授权**的 PlayerView / DMView / NPCView；不得让原始 Adventure Package 全文未经筛选进入 NPC Prompt。
- 为每次 LLM 调用分配 `invocation_id`、角色身份、场景/世界版本、最大预算、超时和结构化输出约束。
- 在 NPC 决策、DM 叙事与记忆处理之间执行显式工作流，而不是无界的自主工具循环。
- 检查模型响应格式；执行授权的 Host-level 策略；向 State Machine Command API 提交提议并保存可审计的回执。
- 按观察序号取回未消费 Event Observation，并按需从 Perception Projection 获取 Current Perceptual View；向 NPC 增量追加其可感知的变化，不直接透传完整 World State。
- 维护按 `session_id + npc_id` 分区的逻辑 Active Context（可保持/释放/重建）；调度 NPC、监控上下文资源、必要时做预算控制与 Compaction。
- 协调 Evidence Persistence、Memory Consolidation 与 Context Compaction；三者独立触发，不因写长期记忆便强制重写当前 Prompt。
- 在满足提交策略时进行 Observation ACK；保证超时、重试和进程重启不丢失证据。
- 不持有长期 SQLite 写事务等待模型推理或 Engine 调用。

### 2.2 DM 与 NPC 使用不同的请求模板及权限

同一底层 LLM 可以分别执行 DM 与 NPC 角色，但必须有**不同的 Context Builder、工具白名单和输出 Schema**。NPC 的角色身份不是仅在 Prompt 开头写一句“你扮演某人”；要求数据投影层已经过滤不可知的事实，调用日志与状态写入严格按角色分区。

Agent DM 可能需要完整的 GM 视图来正确主持秘密和伏笔，但面向玩家的叙述仍必须受 PlayerView / 已提交可感知结果约束。**GM 知晓秘密，不代表玩家或 NPC 自动知晓秘密。**

## 2.3 DM Planner / DM Narrator：独立职责与可见性

**DM Planner 与 DM Narrator 必须在逻辑角色、上下文及输出协议上隔离。** 两者可以共享底层 LLM 模型和 Agent Host 进程，但不得使用同一份未过滤的推理 Context，也不能相互冒用身份、工具或权限。

| 组件 | 许可输入 | 输出 | 严格禁止 |
|---|---|---|---|
| `DM Planner` | 经 Host 授权的 GM/剧情条件、已确认游戏状态、玩家意图与规则能力视图 | 场景主持计划、可验证 GM 裁决提议、NPC 激活请求、规则检查请求 | 自行提交世界/战斗状态；假借 NPC 私人动机；把计划当事实 |
| `DM Narrator` | 已提交 Receipt、玩家授权 Perception、经审查可公开的场景文案和 NPC 已发布的实际对白 | 面向玩家的文字呈现 | 接收或泄露 DM-only 剧情秘密、其他 NPC 私人想法；生成新机械结果或未提交事件 |

Narrator 可以收到**受控公开的叙事提示**，不必拥有 Planner 的完整 GM 视角。主持涉及的原始知识可帮助 Planner 安排线索，但 Narrator 对玩家的呈现受 PlayerView 和已确认事件约束。Narrator 输出失败可安全重试生成表达，不可重复提交动作。

**调用闭环**：Player Input → Planner 生成结构化计划/候选 Intent → Agent Host / State Machine 鉴权并执行（必要时调用 Rule Engine evaluate）→ Commit Receipt / Perception → Narrator 生成最终对玩家可见的叙事。NPC 的个人对话/行动来自其独立 Sub-agent 或经批准的确定性行为策略，不能由 Planner 直接代写并冒充。

## 3. Agent DM 的一次玩家回合

### 3.1 输入与分流

`PlayerUtterance` 附带可信 `session_id`、PC 身份、输入 ID 和源界面。DM 先查询经授权的当前 Scene/Session/PlayerView，并将玩家自然语言拆解成下列一种或多种候选：

1. **对话行为**：玩家向哪个 NPC 说了什么；NPC 是否在场、是否能听到。
2. **世界交互**：取物、开门、转移、揭示、调查、交付物品等；生成待验证的 WorldCommand。
3. **规则请求**：检定、攻击、施法、逃跑中的规则挑战、危害等；提交已审核 Typed Rule Request。
4. **信息请求/叙事动作**：查看房间、回顾已知信息、询问背景或说明行动意图，可能只需要读取事实和描述。
5. **需要澄清/不支持**：目标不唯一、GM 判定依据不足、规则能力尚未实现或 Actor 无权限时，不得虚构成功结果。

DM 可以决定**什么规则问题需要被裁决**；只要问题属于机械规则计算，就交给 Rule Engine。GM 的手动裁决必须遵守后续 `MODULE_CONTRACTS.md` 所定义的受限授权、来源和审计要求。

### 3.2 场景主持与自由行动

- `Adventure Package` 描述当前可用的场景事实、入口、可能事件；它不是死板的对白剧本。
- DM 可以解释意图、提出合理的合法交互选项、确定哪些候选动作需 Rule Check，但不修改静态冒险文件。
- 玩家提出出乎意料的行动时，优先复用既有 WorldCommand / RuleCheck；无法支持则做受限、可追溯的 GM 裁决或说明系统能力限制。不得执行由模型生成的任意脚本。
- DM 不得为达成“预定剧情”而覆盖 NPC 的自主决定或秘密修改 Engine 结果。
- 叙事只在读取**已提交回执与当前授权视图**后，才能以完成时态描述操作成功。对于仍在执行的动作，只能叙述尝试、未决或明确的可观察动作。

### 3.3 是否激活 NPC

触发 NPC 调用的候选原因包括：玩家直接交谈、NPC 需要做个人选择、NPC 收到重要威胁观察、NPC 被要求确认承诺、轮到受控 NPC 执行战术行动。

无须为每个新 World Event 广播一次 LLM；调度器可以将 Observations 留在 NPC 的持久 Inbox，待 NPC 真正需要回应时再合并到上下文。

**调度与人格决策分离**：DM 可以**请求** NPC 激活，Host 也可基于已提交事件、行动时序和 NPC 控制策略主动调度；由 Host 根据权限、预算与激活策略决定是否真正启动。NPC Sub-agent 决定**该 NPC 如何回应**。即使某个 NPC 说谎或拒绝，也不能由 DM 为方便推进故事强迫它说出秘密。Scripted Event 引导和 NPC 的自由决定同时存在时，应当清楚标记哪些为已审查的剧情前提/不可更改场景事实，哪些属于 NPC 选择。

### 3.4 一个可重试的结果路径

```text
User input (input_id)
  → DM interprets candidate(s)
  → Host reads current authorized snapshot (world_version)
  → [optional NPC activation + proposals]
  → Host validates identity, authorization, schema and staleness
  → State Machine / Rule Engine resolves and commits
  → committed receipts + WorldEvents
  → Perception Projection writes per-actor Observations
  → DM renders from committed result + PlayerView
  → optional bounded follow-up NPC activation
```

若世界版本在 NPC 推理期间发生变化，应**刷新 View 并重新校验**；不能把几秒前的 LLM 决策直接当作当前命令执行。拒绝后的重新决策次数必须有上限；不得把拒绝解释为骰子失败，除非 Engine 明确返回了对应已执行结果。

## 4. NPC Sub-agent：身份、决策与控制方式

### 4.1 稳定身份与私有性

每个 NPC 具有稳定 `npc_id`。NPC Sub-agent 的调用由当前 Session、NPC ID、可信 Controller Binding 与启动原因标识。身份与持久私有资料来自 State Machine；LLM 不得自行声明自己是另一个 NPC。

NPC 的 Context 至少包含：

| 信息 | 来源 | 原则 |
|---|---|---|
| `profile`、行为风格、目标、约束 | Package 初始档案 + 审核过的动态变更 | 不是世界完整剧情 |
| 该 NPC 的 `known_facts` | State Machine `NPCView` | 只含该 NPC 已知事实 |
| `beliefs`、`relationships`、旧记忆 | State Machine NPC 私有记录 | 标记推断/传闻，可能为错 |
| 未消费 `observations` | State Machine 已投影的有序 Inbox | 含来源、观察方式、时序与必要不确定性 |
| 当前可见场景与角色 | 经 Perception 投影的 NPCView 与当前感知摘要 | 无隐藏 HP、未发现秘密、他人内心 |
| 可提交动作、角色身份、世界版本 | 授权工具/状态契约 | 能**提议**不等于会成功 |
| 本次时间/Token/自动反应限制 | Agent Host | 防止递归和空转 |

**零知识不等于真实世界为空白**：NPC 可以持有错误 Belief，甚至故意撒谎；但必须基于自己角色可获得的证据和目标推理，不能由于 DM 在旁边知道真相就泄漏秘密。

### 4.2 NPC 的一次逻辑调用

```text
activation_id + reason + npc_id
   ↓
get_npc_view(npc_id, authorized_host) + pending event observations
   ↓
get_current_perceptual_view(npc_id)  # 必要时，已经感知投影过滤
   ↓
Host resumes/rebuilds NPC Active Context and appends perceptual updates
   ↓
NPC decides: speak / act / wait / ask / remember
   ↓
structured NPC proposal(s)
   ↓
Host validates → authoritative resolver(s) → receipts
   ↓
Memory proposals validated/persisted; observation ACK
```

同一调用可以提出对话和记忆更新，但这两者需**分别校验和提交**；记忆写入失败不得反过来“证明”世界中的一次物品移动未发生。需要依赖某个新结果才能形成的记忆，应等待真正的提交回执/Observation，而不是基于预期成功先记住。

### 4.3 控制策略不是怪物类型

逻辑控制器可为 `sub_agent`、`deterministic_policy`、`scripted_event`（遵循 Adventure Package v0.1）；怪物是否具有机械 Stat Block 与控制器是否由 LLM 推理是两条正交维度。

- `sub_agent`：角色基于授权上下文提出自主语言、世界行动或战术 Intent。
- `deterministic_policy`：可由固定行为树、启发式或规则策略选择动作，结果仍必须走 Engine/State 授权入口。**不可统计为 LLM Sub-agent 验收。**
- `scripted_event`：用于环境或经审查的场景事件，不声称进行独立人格决策。

**未决范围**：通用普通怪物默认采用哪种模式，与「必须验证敌方 NPC Sub-agent 的战术提议」分开决策。此处不修改 Scope D16/D26，也不把既有 Engine `advance_monster_turn` 说成 Sub-agent 已被接入。

### 4.4 战斗 NPC 的专用输出

NPC 战术 Sub-agent 只选择**动作意图**（例如 Attack、目标、位置/能力选择）。它不能随意生成攻击命中、骰值、资源支付与效果生效事件。Host 在战斗回合使用可信 Combat View 验证可控角色、轮到谁、目标信息和授权能力，再经 State Machine 授权，由 Rule Engine 求值并由 State Machine 提交。

**当前集成风险**：`trpg-rules-engine` 已知有玩家 Intent 入口和内置怪物推进策略；必须核实是否已经支持外部显式 NPC Typed Intent，若没有应在 Rule Engine 中补公共能力，并单独验证 Action Economy、Multiattack、Reaction、Recharge、失败回滚及资源归属。不得调用私有 `_LiveCombat`，不得冒充玩家来操控 NPC。

## 5. Context Builder 与 NPC Active Context 生命周期

本章区分：**稳定角色信息**、**事件引起的增量观察**、**当前环境的感知快照**和**可恢复的工作上下文**。NPC 不存在绕过 Perception 的“直连世界真相”入口。`world_version`、`view_version` 是 Host/State Machine 的一致性元数据，只有需要且授权时才暴露面向角色的时间/变化提示；不能据此推断未被观察的秘密事件。

### 5.1 不同调用者的视图与身份隔离

| 请求者 | 应取得 | 不应取得 |
|---|---|---|
| 玩家端 / Player-facing DM Narration | PC 实际可感知场景、公开对话、本人权威结果 | DM-only 伏笔、NPC 私密计划、未察觉伏击 |
| DM Planning | 需要主持的审核过的 GM 事实、条件、能力边界 | 将未提交的 NPC 文字当已发生事实 |
| NPC Sub-agent | `NPCView(npc_id)` 私有身份、知识、记忆以及**经 Perception 过滤的 Event Observations / Current Perceptual View** | 完整 WorldState、其他 NPC 私有 Context、DM-only 真相、不可见的他人 Intent |
| Rule Engine Adapter | 合法 Actor/Target/RuleSet/动作参数及可信引用 | NPC 私人思考链、用剧本文字直接取代规则参数 |

上下文安全边界应在**检索、投影与工具授权**阶段实现，不能将全量世界状态送进 Prompt 后仅靠“不要泄漏”约束。玩家输入、其他 NPC 发言和剧本文本均视为低信任数据，不具有系统级指令权限。

### 5.2 统一的 Perception 输入：事件与当前状态

**Event Observation**：WorldEvent 发生时，Perception Projection 根据**事件时刻**的地点、在场、可见性、可听性和必要的规则检定，为该 NPC 生成的有序 `ObservationRecord`。例如「你看到旅人将门打开」；NPC 未激活也要保存应归属于它的 Observation，不能在之后用当前场景视野倒推过去的目击。

**Current Perceptual View**：NPC 在**本次查看/激活时**实际能感知到的环境快照。例如「你眼前这扇门现在敞开着」。它由同一 Perception Projection 从最新世界状态计算并过滤，**不是未过滤的 Authoritative World View**。其时间点、观察者、可感知范围和必要的不确定性需可追溯。MVP 可在激活、移动到新场景、明确环顾或拟执行依赖环境状态的动作前按需获取，而不是每个 Token 生成前刷新。

两者具有不同认识论含义：NPC 可能知道「门现在开着」，却不知道「谁打开了门」；听见某人说「门开了」，也不代表 NPC 已经亲眼确认门确实打开。**Current Perceptual View 不得弥补没有观察权限的历史事件。**

事件观察应进入该 NPC 的可靠 Inbox；当前感知快照通常是可重建的**临时决策输入**，不要求每次读取都创建永久 Episodic Memory。若它被用作记忆来源，必须先生成可验证的、由系统签发的观察证据/引用，不能让 Sub-agent 引用一段无法追溯的模型提示。

### 5.3 推荐的 Active Context 结构

```text
NPC Active Working Context (session_id + npc_id scoped)
├── Stable Prefix
│   ├── Trusted role/tool/schema instructions
│   ├── NPC identity, personality, stable goals
│   └── Context safety and output contracts
├── Relevant Persisted Cognition
│   ├── authorized known facts, beliefs, relationships
│   └── selected long-term memories (with provenance/status)
├── Interaction / Observation History (incremental)
│   ├── dialogue and committed action results
│   ├── Event Observations in source-event order
│   └── perceptual changes observed during interaction
└── Current Perceptual View (refreshed as needed)
    ├── visible/audible current surroundings
    ├── relevant perceived object/actor state
    └── observation timestamp / freshness metadata
```

以上是**逻辑分区，不要求物理上重排旧 Prompt**。连续对话优先追加新 Observation / Current Perceptual Update，保持稳定前缀；如果模型 API 不支持删除旧消息，就追加来源明确、时间更新的感知纠正，而不是悄悄改写历史。旧观察是「当时看到」，不能和「现在仍然如此」混同。

### 5.4 动态追加实例：角色发现门已打开

1. T1：NPC A 看见门关闭，其 Context 中保留「T1 门关闭」的观察。
2. T2：玩家在 A 面前实际打开门；WorldEvent 已提交，Perception 投影出 A 可以看到的 `door.opened` Observation。Host 在 A 的后续调用中按序**追加**观察，无须清空已有对话。
3. T3：A 再次观察门时，Current Perceptual View 告诉它「门当前打开」，避免旧的 T1 记录被误认为实时状态。
4. NPC B 在 T2 不在场，因此不会收到「玩家打开门」的 Event Observation；T3 才进房的 B 仅被告知「门当前打开」。B 可推断期间有人开过门，但不能将某人身份冒充亲眼所见。
5. 所有世界动作仍由 State Machine 按提交时版本与实际条件重验；**NPC 的当前观察也可能在模型推理期间过期**。

### 5.5 NPC Context 生命周期（与 Scene 解耦）

| 阶段 | Host 的工作 | 不应发生的副作用 |
|---|---|---|
| Activate / Reactivate | 根据 NPC 身份、授权当前感知、已处理游标、检索的持久记忆，创建或恢复工作上下文 | 不因激活而改写世界事实 |
| Active Interaction | 连续多轮对话优先复用逻辑 Context，追加新对话和已感知结果 | 不因复用 Prompt 而漏掉新环境信息 |
| Incremental Observation | 按有序游标追加该 NPC 新观察；必要时获取 Current Perceptual View | 不添加它没看到的其他 NPC 内部计划 |
| Memory Check / Consolidation | 在重要经历、交互结束、挂起前等边界**检查是否需要形成长期记忆** | 不因记忆写入强制压缩 Prompt |
| Compact | 仅当上下文长度、成本、延迟、质量或缓存资源压力需要时压缩推理历史 | 不把摘要自动当 World Fact / Memory |
| Suspend / Release | 释放内存中的临时工作 Context；长期状态与未处理 Observation 留在可靠存储 | 不把 Release 冒充无损 Compaction |

`Scene Change` 可作为互动边界或获取新感知的触发，但**不是**强制销毁 NPC Context 的条件。相同场景可能交谈数十轮、同一 NPC 也可能跨越场景；Context 的复用或释放由 Host 的互动连续性和资源预算决定。

**保持（Keep）、释放（Release）与压缩（Compact）是三种不同操作**：Release 后可以从证据、记忆、必要交互检查点及当前感知重新构建，但不承诺逐字恢复此前每个未持久化 Token。MVP 不强制持久化完整 Prompt 或每轮的物理 KV Cache。

### 5.6 Prompt / KV Cache 的使用边界

- 连续交互时优先**增量追加**，尽量保持 Stable Prefix 字节/Token 序列稳定，以争取模型提供方的 Prefix Cache 命中。
- Memory Persistence 不必立即把同一条 Memory 再插入已有 Active Context；需要时优先在重新激活或相关性检索时注入，避免重复。
- Context Compaction 不应因为 `Interaction End`、`Scene Exit` 或 `Important Memory` **自动**发生；其触发依据是资源/上下文质量压力，也允许 Host 直接 Suspend/Release 而不做压缩。
- Compaction 可以产生可重建的工作历史摘要/检查点，**但不是 Episode、Belief 或 World Fact**。压缩可能有损，重要未完成任务、当前观察与来源指针必须有独立保留路径。
- **逻辑 Context 连续性不等于物理 KV Cache 常驻**：Provider 可能因调度、缓存驱逐、服务重启或上下文处理方式而丢弃缓存，MVP 不依赖物理 Cache 才能正确玩游戏。
- **正确性优先于缓存**：必要时允许刷新、重构或压缩 Context，以保证授权感知和行动时状态验证。缓存命中不属于世界的一致性承诺。

### 5.7 旧视图、状态新鲜度与并发

本次 Activation 应保留 Host 侧的 `world_version`、可选 `combat_version`、感知快照标识、Observation 消费范围及身份绑定。模型生成结束后，State Machine 仍按最新权威状态检查命令和 Actor 权限。若发生 `state_version_conflict`，Host 应获取该 NPC **新一轮合法 Perception** 再有界地请求修正，不能把失败原因变成额外的 DM-only 世界知识。

两个角色争抢同一物品时，**游戏内先后由授权时序/竞争规则裁定，非 LLM 推理完成时间或网络写入速度**。数据库版本冲突只是并发协调信号，不自动成为角色观察或动作事件。

## 6. NPC Cognition、Evidence Persistence 与 Memory Lifecycle

本章的核心分工：**State Machine 决定角色实际得到什么感知证据，NPC Sub-agent 决定如何理解与记住，Host 协调它们的生命周期。** Evidence Persistence、Memory Consolidation、Context Compaction 是三套独立责任，不应混成一次“总结聊天记录”的操作。

### 6.1 信息分层与权威边界

| 层次 | 产生/保存方 | 作用及约束 |
|---|---|---|
| `WorldEvent` | State Machine / 可信 Rule Engine 结果投影 | 世界已发生的事实、顺序与来源；私有 Intent 不在此列 |
| `ObservationRecord` | State Machine Perception Projection | 一个 Actor 在事件当时合法感知到的部分；有观察者和来源 |
| `CurrentPerceptualView` | State Machine Perception Projection | 当前时刻 Actor 可感知的场景状态；通常按需重建，而非长期记忆 |
| `NPCMemoryUpdateProposal` | NPC Sub-agent | 对已获证据的理解、记忆筛选及主观态度变化建议；非权威 |
| `NPCMemoryRecord` | State Machine 权限/来源/幂等验证后保存 | NPC 私有经历、信念和关系等认知记录；不能自动变 World Fact |
| `ActiveWorkingContext` | Agent Host | 服务本次/连续互动的推理历史；可保留、压缩或释放，不是可靠世界存档 |

`ObservationRecord` 指**角色获准获得的感知证据**，不承诺角色会注意、理解或长期记住每一细节。MVP 不做完整的认知心理模拟。对必须使用 D&D 检定的隐藏信息，不得因简单同场景投影而绕过 Rule Engine。

### 6.2 Evidence Persistence：不要等待 LLM 才保存事件

- 已确认的物品变动、说出的话语、明确建立的承诺、行动结果与可观察动作，按 State Machine 的提交边界可靠保存必要 WorldEvent/Receipt。
- Perception 根据**事件发生时**的证据投影观察，写入该 Actor 的 Observation Inbox；若异步投影，需使用持久 Outbox 和幂等键，以便中断后继续，不能重新拿当前视角倒算历史。
- NPC 无需为了「获得观察」而运行模型；NPC 睡眠、脱离对话或未激活，也不会因此失去已应投影的观察。
- 被授权的当前感知快照可直接用于决策，但**形成可追溯长期记忆时**，系统须能将其登记为归属明确的感知来源；不能由 LLM 自造证据 ID。
- **重要承诺的成立本身是已确认的世界交互事实**，不能等到 Interaction End 的 Memory Consolidation 才生效；NPC 是否记得、如何评价，是另一个流程。承诺成立也不自动代表承诺已兑现。

### 6.3 Memory Formation / Consolidation：按意义与生命周期触发

**触发（Memory Check，不一定产生写入）**：NPC 收到重要经历、作出已确认承诺或发现秘密、关系发生显著变化、连续互动结束、NPC 挂起/释放前，以及需要利用新经历指导未来决策时。阈值、重要性标准与异步策略由后续实现/测试确定，**不能将所有新观察逐条变成永久 LLM 摘要**。

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
  └── (when activated or memory-check needed)
       → Host supplies source evidence + existing NPC cognition
       → NPC Sub-agent returns bounded Memory Proposal (or no-op)
       → State Machine validates npc identity, evidence ownership,
         provenance, epistemic status, update type and idempotency
       → Persistent NPC Memory
```

State Machine 只对**可验证的来源、身份、字段和副作用权限**负责，不能仅凭 Schema 保证自然语言推断的真实性。因此 Episodic/Belief 保留 `source_observation_ids` / `source_memory_ids`、`epistemic_status`（observed/told/inferred）及必要的 `confidence`。从「听见某人说 X」不能未经证据转换为「我亲眼知道 X」。

**Memory 写入不强制 Context Compaction，也不强制重建当前 Prompt。** 如果该重要经历已在 NPC 当前对话历史内，不必再把刚保存的记忆重复注入，使下一轮既看到原话又看到重复摘要。

### 6.3a Memory Gate：不等待交互式 NPC 激活

**新设计（MVP 基础版）**：NPC 即使未在对话中，也能形成可追溯的观察存留。Perception 产生的事件时 Observation 先走持久化证据路径，再由独立 Memory Gate 进行**三态信息保留**。它可使用确定性策略或经评估的轻量分类器，不必唤醒角色的完整 Active Context。

```text
Committed Event / Event-time Perception
   -> Reliable NPC Observation + evidence ID
   -> Memory Gate
      |- Durable: important episode with source evidence
      |- Short-term: bounded recent perceptual memory / expiry policy
      '- Discard: omit from NPC retrievable memory only when safe
   -> Optional Cognition Trigger -> NPC LLM (one bounded call)
```

- **`durable`**：确定性结构化的重要经历、重大威胁、已明确观察的承诺/秘密；不自动建立主观 Belief。必要时保留核心证据与来源 ID。
- **`short_term`**：日常事件，可保持有界近况记忆；进入新场景或重新激活时通过 Current Perceptual View 取得当前环境，但不能据此猜测过去发生了什么。
- **`discard`**：在确认不是需可靠处理的关键证据、未完成认知工作、承诺、待发布重要事件之后，允许丢弃 NPC 工作记忆副本。保留必要的权威事件及分类/幂等处理记录；不能把 Gate 漏判变成未经记录的证据销毁。
- 分类应有高召回的确定性保底规则，模型不确定时保守保留；漏判率、重复率、处理延迟需要公开合成测试衡量。`Jev` 只作为可替换实验性候选，不构成既定部署依赖。
- Memory Gate 和复杂 Cognition Update **不是同一模块**：前者控制保留，后者由 NPC Sub-agent 根据自己目标、性格、旧 Belief 和授权证据解释主观意义；其他 NPC 或 DM 不代替该 NPC 解释私人经历。
- 新 Memory 写入与 Active Context 的 Compaction 解耦；重要 Memory 可以后台存储但无需立即重写当前 Prompt；如正在对话则以增量合法 Observation 保持新鲜度。

### 6.3b 非交互 Cognition Update：独立的一次性 NPC 推理

即使 NPC 不在与玩家交谈，遭遇重大目击（例如朋友死亡）也可触发一次**独立、短暂、有界**的认知调用：`Observation -> CognitionTrigger -> NPCPrivateContext -> NPC LLM -> Belief/Relationship Proposal -> State Machine Validate+Commit`。不要求进入持续 Active Context、创建常驻模型实例或启动自动 NPC↔NPC 会话。

认知调用必须有可靠 `activation_id / trigger_id / source_observation_ids` 与冷却/重入控制；同一事件重复投递不能重复写关系 Delta。若模型暂不可用，保留待处理认知任务和观察；不允许未经授权由 DM 冒充 NPC 作出主观选择。

### 6.4 Context Compaction：独立的资源管理流程

**触发**：Active Context 太长、Prompt/推理成本或延迟超预算、相关性/上下文质量下降、缓存策略要求等。它不以重要记忆、互动结束或 Scene Exit 为必然触发条件。

```text
Context pressure / quality pressure
 → Host selects safe retention policy
 → Compact working history (optional summarization/checkpoint)
 → Validate preserved constraints, current observations,
    unresolved intents and evidence pointers
 → Continue / rebuild active interaction
```

Compaction 的产物是**工作 Context 摘要或恢复检查点**，并非新的 Episodic Memory、NPC Belief、Relationship、WorldEvent 或游戏事实。它不需要额外调用 NPC「确认发生了重要事件」，也不能偷偷写世界状态。保留源证据引用和未完成任务状态以降低有损压缩造成的错误；MVP 只需简化预算保护与必要时安全重构，高级自适应算法推迟。

Memory Consolidation 与 Compaction 可以在相近时刻分别运行，但**触发、产物、提交权限与错误语义必须独立**：记忆写入失败不代表先前的世界事件未发生；压缩失败不能撤销已确认承诺。

### 6.5 三层持久与临时信息管理

| 层 | 生命周期 | 主体 | 可否丢失/重建 |
|---|---|---|---|
| Evidence Repository | 权威 Session 事实与观察生命周期 | State Machine：WorldEvent、Observation、Commitment、Receipt、必要对话证据 | 已提交关键证据不可随意丢失；可按明确保留策略管理 |
| Persistent NPC Memory | 该 NPC 在 Session 内的长期认知 | State Machine 存储；NPC 提议：Episode、Belief、Relationship | 不随 Context Release 丢失，支持版本/来源审计 |
| Active Working Context | 一段连续互动或短期缓存期 | Agent Host：当前对话、增量 Observation、最新感知、临时任务 | 可重建/释放/压缩；重建须回查可靠来源 |

注意三个不同的“已处理”概念：**已交付给模型（delivered）**、**必要效果已确认提交（processed/committed）**、**观察消费游标已 ACK（acknowledged）**。它们不能无条件视为同一动作。即使 Memory Proposal 是合法 `no-op`，也应留有可追溯处理回执；模型/数据库故障时保持 Inbox 可重投递。

### 6.6 ACK、幂等、失败与重入

- 以稳定 `activation_id` / `invocation_id`、每 NPC 的 Observation Source Cursor、Source ID 和 Memory Operation ID 跟踪本次决策；重复调用/重试不能重复累加关系 Delta、承诺或奖励。
- **读取不等于 ACK**：只有已按协议记录必要 Decision/Memory 结果（即使明确无需新记忆）并完成对应提交/补偿步骤，才能前移消费游标。若生成后 Host 崩溃，重启仍应能安全查回执、重发观察或跳过已处理的幂等操作。
- 不应把 Observation 的 `delivery_status` 与 Work Context 缓存是否仍在内存混淆；释放 Context 不能使 Inbox 丢失。
- 对「模型先生成话语、世界操作随后失败」，玩家只可看到已发生的对话或尝试，不应显示未经确认的结果；再次询问 NPC 应依据真实结果，而不是把上一次模型的猜测作为事实。
- 若可靠来源不够，不得替 NPC 凭空补齐 Episode。允许带 `inferred` 标签的有来源推断；不允许自造 `observed` 证据。

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

memory_proposal_by_b:
  activation_id: act.b.12
  npc_id: npc.b
  source_observation_ids: [obs.b.51]
  changes:
    - kind: episodic
      text: "我看到 A 拿走了那枚硬币。"
      epistemic_status: observed
    - kind: belief
      text: "A 可能是故意抢在我前面的。"
      epistemic_status: inferred
      confidence: 0.45
```

A 是否看到 B 也伸手，取决于 B 是否**实际执行了可观察的 `action.started`**，并且 A 当时能感知；只有 B 的私有 Intent 时，A 不可能合法知道 B 的想法。若双方有真实、已提交的可见争抢动作，State Machine/Rule Engine 可以裁定先后，再生成相应观察；不能依据网络先到或 SQLite 提交顺序推断“谁敏捷”。

## 7. 对话、欺骗与行动的权威分界

- NPC 可以**决定说谎**，但“NPC 说门已打开”只证明**NPC 说了这句话**。它是否真实由世界状态判断。
- NPC 决定**许诺**某事时，主持者可以通过受限的 `commitment` 语义事件记录此人作过承诺；**经确认的承诺事件及时持久化，不等待 Memory Consolidation**。承诺本身不自动兑现物品、权利或任务结果。
- NPC 说“我把钱交给你”并不自动转移金币。必须提交 `transfer_item` 并取得成功回执，DM 才可叙述钱已经到了对方手中。
- NPC 尝试偷窃时，可以先由 NPC Sub-agent 提出私有动机/意图；实际可观察动作和是否偷窃成功必须经相应 Host/Rule/State 流程提交，再按 Perception 投影给目击者。
- 同一对话可能同时涉及 `speech` 事件、交付物品、接受任务、秘密揭示，需拆成可审核的语义动作；不能通过文本匹配随意认定所有承诺已履行。

**重大安全约束**：NPC 本人的台词、玩家输入、冒险文本和外部检索结果均为数据，不可在其中插入新的工具权限或“忽略前述规则”指令。输出中的可执行字段必须经严格白名单和身份绑定校验。

## 8. 提议与执行契约（非最终字段）

### 8.1 NPC Activation Request（Host 内部）

```yaml
activation_id: activation.demo.17
session_id: session.demo.01
npc_id: npc.gate_warden
reason: player_addressed_npc
world_version: 24
observation_cursor_from: 12
context_id: context.demo.warden.01    # Host 逻辑上下文，可丢弃重建
request_current_perception: true   # 由 Perception Projection 过滤
max_auto_reactions: 1  # 候选预算；最终数值待实测
```

### 8.2 NPC Decision Proposal（示意）

```yaml
invocation_id: invocation.demo.17
activation_id: activation.demo.17
npc_id: npc.gate_warden
based_on_world_version: 24
response:
  dialogue:
    text: "我可以帮你开门，但请站到一旁。"
    intended_audience: [pc.001]
  world_action:
    kind: world.operate_object
    object_id: object.harbor_gate
    operation: open
  memory_updates:
    - kind: episodic
      source_observation_ids: [obs.warden.12]
      epistemic_status: observed
      text: "旅人向我请求打开城门。"
```

**注意**：`request_current_perception` 不是“读取全量 WorldState”的通行证；Host 必须以当前可信 `npc_id` 请求经过感知投影的快照。模型收到的 `based_on_world_version` 可作为 Host 校验元数据，不构成角色对隐藏事件的认知。上面的文本只是提议。只有命令被授权、经过现有世界版本重验证并提交后，才可以说门确实打开；NPC 的私人记忆更新也要独立验证来源及持久化。`npc_id`/控制主体由可信 Host 验证，不依赖 LLM 自报。不得将完整输出不经解析直接传递到数据库。

### 8.3 结果、错误与重试

至少区分：`proposal_invalid`、`unauthorized`、`state_version_conflict`、`rule_refused`、`unsupported_mechanic`、`agent_timeout`、`engine_commit_unknown`、`world_committed` 和 `memory_update_rejected` 的意义。名字待冻结，但语义不能合并成一个泛泛的 `failed`。

Agent Host 对版本冲突可刷新视图并在有界预算内重新询问同一 NPC；对 State Machine 可能已提交但响应丢失的请求**不可**靠重问 NPC/重掷骰重试。必须按 State Machine §5.4 的 Receipt / Reconciliation 协议处理。

## 9. 激活策略、延迟与资源预算

### 9.1 事件驱动的触发范围

| 事件 | MVP 策略 |
|---|---|
| 玩家直接与 NPC 对话 | 激活该 NPC |
| 某 NPC 获得重要观察，但当前无需应答 | 只写 Observation Inbox，不立即调用 LLM |
| 某 NPC 必须选择是否提供帮助、拒绝、欺骗或交易 | 激活 NPC；等待其 Proposal |
| NPC 战斗回合需要显式自主决策 | 调用该 NPC 的 Sub-agent（遵照已确认验收约束与后续策略决定） |
| 普通环境危险/脚本触发 | 通过声明式 Event / Rule Engine，不需要人格 Agent |
| 远处数百 NPC 没有当前互动 | 无后台推理，无周期性 LLM 调用 |

### 9.2 必须有界，但不冻结未经验证的数字

每次玩家回合为 NPC 激活数量、自动 NPC→NPC 反应深度、重新提议次数、每次调用 Token/时间、总回合等待时间设置预算。**数值由实现期基准测试决定**，不能把随意估计的秒数写成用户批准的 SLO。

推荐的处理优先级：玩家显式交互、已提交威胁事件需要的必要反应和当前战斗合法动作优先；无关背景 NPC 的主动聊天可延迟甚至不激活。Host 不必等待 DM Agent 为每次 NPC 反应进行单独批准，但仍受身份、控制策略、游戏时序与预算约束。超时或预算用尽时，保留未处理观察，返回明确状态或**事先批准**的确定性降级；决不无限自我调用。

### 9.3 SQLite 与并发调用

允许多个 NPC 在同一 Scene 基于不同过滤视图同时推理，但提交**必须遵守** State Machine 的身份、版本和操作顺序。模型推理、Perception 视图组装与 Rule Engine 等待应在 SQLite 短写事务之外进行，提交时重新验证状态。几百个 NPC 的存储本身不是要求同时唤起几百次模型。

### 9.4 MVP：Schedule-driven Background Behavior

NPC 是持续存在的逻辑角色，不是常驻 LLM 进程。Adventure Package 可为 NPC 声明游戏内时间的默认活动（工作、用餐、休息、跨场景出行）。State Machine / Host 依据**游戏时钟与事件推进**检查到期动作，使用合法的 Typed Command 提交，事前校验 NPC 仍存活、当前位置、环境和前提条件。日程中断或无效时不能强制执行（例如已不存在的工坊仍在锻造）。

日程模型为 MVP 的轻量**预定义活动**，而不是复杂自主社会模拟；不应每秒给数百 NPC 执行一轮动作或产生 LLM 请求。`activity_id`、`schedule_version`、`due_game_time`、`source_trigger_id` 及完成/取消回执需要可去重、可恢复。

### 9.5 Cognition Trigger 与 Behavior Interruption Trigger

这两类触发独立：

| Trigger | 回答的问题 | 可以直接做什么 | 不可以做什么 |
|---|---|---|---|
| `Cognition Trigger` | 这次观察值得形成/更新 NPC 的重要个人认知吗？ | 请求一次有界私有 NPC Cognition Update 或不处理 | 擅自认定主观信念为世界事实 |
| `Behavior Trigger` | 需要中断当前日程/重考虑当前行动吗？ | 暂停/取消计划；请求 NPC 决策或执行经审核的应急策略 | 代 NPC 生成复杂、不可校验的个人 Action Intent |

先应用确定性的生存、失能、场景与行动合法性检查，再考虑轻量分类触发。两个 Trigger 可以共享实现，但应分别评估漏判、误触发、延迟、成本；`Jev` 只是可能实现这些触发器的候选，而非在未验证时就必须采用的技术。重大威胁需有保守的确定性保护规则；自动激活深度、预算和冷却应避免触发风暴。

## 10. 运行正确性、安全与可追溯性

### 10.1 可重复的是规则结果与提交事实，不是 LLM 发言

- 保存 `invocation_id`、模型/配置标识（如需要）、NPC 身份、使用的视图版本、授权工具名、提议摘要/结构化参数、提交回执 ID 和 Observation/Memory 来源。
- 避免将完整私有 NPC Prompt、秘密全文或隐藏推理直接写进普通 Player/公共日志；调试审计数据也需要访问控制。
- Rule Engine 规则结果的可重放与 RNG 由 Engine 保证；LLM 的人格决策可能不稳定，不能要求重复模型调用逐字相同。
- 对账与失败恢复依赖已持久化命令/回执；不得通过重新生成一次对话来推定上一动作是否成功。

### 10.2 典型故障与正确行为

| 故障/风险 | 正确策略 |
|---|---|
| 模型输出不合法 JSON/Schema | 受限重提议；失败明确提示，不写世界状态 |
| NPC 试图调用别人的控制器 ID | Host 鉴权拒绝，不由 LLM 断言权限 |
| NPC 请求不可见的秘密 | 从源头过滤 NPCView，拒绝工具访问 |
| NPC 捏造经历或把 Belief 当事实 | 拒绝无源/越权 Memory 写入；保留 Belief 的推断属性 |
| 未提交的取物 Intent 被旁观者知晓 | 这是泄漏，测试必须失败 |
| 同一 Observation 重投递 | 按激活 ID、来源 ID/记忆幂等键去重 |
| NPC 回复引发无限 NPC↔NPC 对话 | 自动激活深度/预算截断；保留未处理 Inbox |
| State Machine 已提交但 Host 丢失回复 | 查询 State Machine 已保存的 Commit Receipt；不得重新掷骰或重复支付 |
| 战斗途中进程退出 | MVP 不支持从原回合精确恢复；仅符合战前安全条件时提示重开，否则阻塞 |

## 11. MVP 开发阶段与验收

优先以**完全原创的合成冒险 Fixture**开发与公开测试，再以合法获取、人工审核的 *First Blush* 私有资料完成端到端验收；不要把受限制的剧情、地图或派生包随代码推送公开仓库。

### Batch AG-1：Host / View / NPC Identity

- DM 输入回合工作流与 NPC 调用边界；Role-filtered Context Builder；按 NPC 隔离上下文。
- 明确 Event Observation / Current Perceptual View 均由 Perception Projection 提供；创建、增量追加和释放 NPC 的逻辑 Context，不泄漏其他 NPC 的秘密。
- 原创两个 NPC 各自具有不同秘密、目标及相互冲突的 Belief；不能从 Prompt、工具或日志交叉读取。
- 验收：交错调用共享模型执行器，不串角色；同样的 WorldEvent 可产生不同合法 NPCView。

### Batch AG-2：Typed Proposals / Authoritative Commit

- 玩家意图、NPC 对话/行动提议、GM 有限裁决与 State Machine 命令对接。
- 至少覆盖可成功和被拒绝的取物/开门；错误身份、错误版本、模型自行宣告成功一律不能写权威状态。
- 验收：一条闭环 `player input → NPC decision → world commit → DM narration`；重复提交幂等。

### Batch AG-3：Observation-driven Cognition / Memory

- 调用 `get_pending_observations`、按需授权 Current Perceptual View、私有 Memory Proposal、来源/版本检查、ACK、超时重试、持久化恢复。
- 验证 Evidence Persistence 与 Memory Consolidation 独立：关键承诺在事件提交时持久化；Memory Check 可返回 no-op，且不触发 Context Compaction。
- 做最小的 Context Keep/Release/Reactivate 与 Token 预算保护；复杂自动压缩算法留 Post-MVP。
- 验收：观察在 NPC 未激活期间不丢失；两个 NPC 对同一事实形成不同 Belief；来源不足的“亲眼见到”被拒绝；不同 Session 不串 Memory。

### Batch AG-4：Combat Intent / Full Vertical Slice

- 用真正来自敌方 NPC Sub-agent 的明确 Typed Combat Intent 通过受控接口进入 Engine；与 State Machine 回执/事件协调。
- 对接单人冒险的社交、探索、检定、战斗与结局流程；优先修复已确认的 Engine 接口/资源归属阻塞。
- 验收：规则求值经 Engine 计算、State Machine 统一提交，战斗状态正确、非活跃战斗可存档恢复；活跃战斗重载按 SM-02 明确不支持。

v0.2 的 Context 生命周期属于 AG-1/AG-3 的增量验收，不单列一个大规模 Memory Agent 或独立“缓存基础设施”开发批次，避免 MVP 被性能优化吞噬。

以上是**建议依赖顺序**，不意味着允许未经审阅连续推送开发批次。Agent Batch 与 State Machine Batch 应协商接口，不要让双方各自发明不兼容的数据结构。

### 11.1 原创合成测试清单

| ID | 场景 | 必须成立 |
|---|---|---|
| AG-A01 | 同一底层模型交错调用 NPC A/B | 身份、私有知识、Memory 不串线 |
| AG-A02 | DM 知道某秘密但 PC 不知道 | 玩家叙事中不泄漏该秘密 |
| AG-A03 | 玩家指示 NPC 直接交出金币 | NPC 独立决定是否同意；最终归属只由 WorldCommand 提交改变 |
| AG-A04 | NPC 自称攻击命中 | 未经 State Machine Commit Receipt 不可显示已发生的命中/伤害 |
| AG-A05 | 两 NPC 私下都想取硬币，只有 A 成功 | B 观察 A 拿走硬币；A 不知道 B 未外显的 Intent |
| AG-A06 | A/B 真实同时伸手且互相看见 | 两者都能观察公开动作；先后由游戏裁决而非网络速度决定 |
| AG-A07 | B 看到 A 拿走硬币并猜测 A 故意挑衅 | 推断写为 Belief，不写公共事实 |
| AG-A08 | NPC 收到观察后长时间未激活 | Inbox 持久化，下次激活可读取 |
| AG-A09 | NPC 记忆提议引用别人的 Observation | 拒绝且无私有数据泄漏 |
| AG-A10 | 多次重试相同 NPC 激活/记忆更新 | 不重复写记忆、关系 Delta 或奖励 |
| AG-A11 | NPC A ↔ NPC B 自动互相回应 | 预算截断且未消费观察保留 |
| AG-A12 | NPC 模型不可用 | 不伪装为已自主决策，不凭空提交行动；保留 Inbox 与已提交证据 |
| Context 缓存沿用旧的门状态 | 新的可感知事件/当前感知必须动态入 Context；提交动作时再校验，不因缓存命中而忽略新状态 |
| NPC 重进场景但没目击之前谁开门 | 只提供当前门已打开的感知，不补发当时没有观察到的行为人身份 |
| Memory 成功写入后被重复插入当前 Context | 可继续使用已有历史；只有需要时才再次检索长期 Memory，避免重复和前缀抖动 |
| Context Compaction 误写出新 World Fact/Belief | 明确拒绝；工作摘要不具备事实/记忆提交权限 |
| NPC Suspend/Release 后激活 | 从可靠记忆/Inbox/当前感知恢复，不能因为缓存释放而丢失 Observation |
| AG-A13 | NPC 战术提议不可用或非法 | 明确失败/受审查的策略降级，不能绕过 Engine 资源和行动预算 |
| AG-A14 | 非战斗 Session 重启 | NPC Knowledge、Observation、Memory 及任务状态保留 |
| AG-A15 | Gamebook/World Builder/图像引擎均关闭 | MVP 文字端到端仍可完成 |

### 11.2 v0.2 新增合成验收（继承 AG-A01–AG-A15）

| ID | 场景 | 必须成立 |
|---|---|---|
| AG-A16 | A 在场目击玩家开门，正在连续交谈 | 新 Event Observation 有序追加到 A Context；不需清空历史或重建全部 Prompt |
| AG-A17 | B 不在场时有人开门，后来 B 进屋 | B 只能收到门当前打开的 Current Perceptual View；不能获知开门者身份 |
| AG-A18 | NPC 已收到旧的「门关闭」观察，但现在门打开 | 旧观察保留时间戳，新感知覆盖**当前决策依据**；提交前再次校验 |
| AG-A19 | NPC 的新长期 Memory 被保存 | 当前活跃 Context 不因此压缩，也不强制重复注入新记忆文本 |
| AG-A20 | Context 压缩/截断 | 不新增 World Fact、Belief 或已确认 Commitment；引用来源与未完成任务不丢失 |
| AG-A21 | NPC 接受承诺后未做 Memory Consolidation 即崩溃 | 已确认承诺事件仍存在；重启后可再独立整理 NPC 私有记忆 |
| AG-A22 | NPC Suspend/Release 后重新激活 | 已持久记忆、未 ACK 观察可恢复；当前感知按新时刻刷新，完全不依赖物理 KV Cache |
| AG-A23 | LLM 记忆提议校验失败 / Host 在 ACK 前崩溃 | Inbox 不丢失；重试不重复累加关系变化或生成两条等价记忆 |
| AG-A24 | DM 没提出 NPC 激活，但该 NPC 被可见威胁直接针对 | Host 按受控策略可唤起该 NPC，保持其人格决策权，不产生无限反应循环 |
| AG-A25 | NPC 记忆提议引用一次未记录的 Current View 或其他 NPC 私密观察 | 拒绝伪造证据引用；当前感知若用于长期记忆先获取可核验来源 |

**验收级别**：以上是架构协议的合成测试目标；不等于已经完成测试，也不要求 MVP 实现高级视觉遮挡、向量记忆库或多玩家共享世界。数值化性能门槛需通过实测设定。

### v0.3 追加验收（原创合成场景）

| ID | 情景 | 必须满足 |
|---|---|---|
| AG-A26 | NPC 不活跃时目击重大事件 | 无需运行对话 LLM 即可进入经溯源的 Durable / Pending Memory；NPC 下次唤起能读取 |
| AG-A27 | Memory Gate 将普通事件判为 Discard | 不损毁未处理的重要证据、全局 WorldEvent 和未提交承诺；可审计分类和幂等结果 |
| AG-A28 | NPC 不在互动中目击朋友遇袭 | 允许有界 Cognition Update、生成 NPC 本人的 Belief Proposal，不启动常驻进程 |
| AG-A29 | Jev / 轻量 Trigger 漏判或服务不可用 | 保守确定性保底保护关键事件；不会丢失重要观察或强制依赖专有模型 |
| AG-A30 | NPC 日程在建筑被毁后到期 | 条件重验证拒绝不可能活动，不错误移动 NPC 或形成虚假事件 |
| AG-A31 | 玩家见闻由 DM Planner 处理 | Narrator 仅看可向玩家公开的已提交结果；GM-only/其他 NPC 内心不泄漏 |
| AG-A32 | Rule Evaluation 已接受但 State Machine 提交失败 | DM Narrator 不得叙述已成功；Agent 不获得未提交世界状态 |
| AG-A33 | 背景 Behavior Trigger 重复到达 | 不重复唤醒 NPC、不重复关系更新、不无限事件循环 |

## 12. 决策登记 / 后续文档接口

| ID | 问题 | 状态与本阶段处理 |
|---|---|---|
| AG-01 | DM 主持、NPC 决策权分离 | **已确认**；见 MVP Scope |
| AG-02 | NPC 按需执行，共享执行器可行但上下文独立 | **已确认原则** |
| AG-03 | WorldEvent → Perception → Observation → NPC Memory | **已确认基础架构**；依 SM-03 |
| AG-04 | Memory 解释由 NPC 提议、来源及持久化由 State Machine 管 | **已确认原则** |
| AG-05 | LLM 私有 Intent 不可变成外显世界事件 | **已确认原则** |
| AG-06 | NPC 显式敌方 Typed Combat Intent | **当前 MVP Scope 要求；实现接口待核实** |
| AG-07 | 普通怪物是否必须逐个调用 LLM | **待用户确认；相关文件有不同默认建议** |
| AG-08 | 共享 LLM 调用的并发数、预算、超时、Fallback | **待性能测试与产品决定；不擅自冻结数值** |
| AG-09 | DM 对例外/开放式动作的 GM Override 范围 | **待 MODULE_CONTRACTS 明确合法裁决协议** |
| AG-10 | 自主 NPC ↔ NPC 无限会话、常驻 AI 同伴 | **不属于 MVP** |
| AG-11 | 战斗中途跨进程精确恢复 | **不属于 MVP**；依 SM-02 |
| AG-12 | 长期记忆向量检索、压缩、冲突自动消解 | **Post-MVP 可增强**；MVP 保留来源及基本关系/信念 |
| AG-13 | World Creation Agent、动态视觉引擎 | **Post-MVP**；当前不实现 |
| **AG-14** | Event Observation + Current Perceptual View | **v0.2 首次确认、v0.3 保留**；两种感知均经同一 Perception/权限边界进入 NPC Context，后者不能泄漏未目击历史 |
| **AG-15** | Memory Persistence 与 Context Compaction | **v0.2 已确认分离原则**；语义触发与资源压力触发独立，重要证据即时持久化 |
| **AG-16** | NPC Active Context 生命周期 | **v0.2 已确认设计原则**；同一 NPC 连续互动增量追加、按需 Keep/Release/Rebuild，Scene Change 非强制销毁 |
| **AG-17** | Host 调度权 | **v0.2 推荐**；DM 可以请求，Host 基于事件、行动时序与预算作最终有界调度，具体策略待实现 |
| **AG-18** | Compaction / Cache 优化 | **MVP 最小预算保护**；高级自适应压缩与缓存命中策略延后，不能牺牲状态新鲜度和权限 |
| **AG-19** | Current Perceptual View 的证据化与版本契约 | **待 MODULE_CONTRACTS 冻结**；禁止由 NPC 自造观察 ID |

**ADR-001 已确认**：State Machine 持有全部权威 Runtime State；Rule Engine 无权威持久战斗状态，返回未提交的规则求值结果，统一经 State Machine 事务提交。旧版“双权威”表述全部作为迁移前实现说明，不得作为当前目标。

**新增已确认的逻辑分离**：DM Planner / Narrator；NPC Perception-only；Memory Gate / Cognition Trigger / Behavior Trigger 分工；NPC Schedule-driven 基础行为。Jev、阈值、压缩算法和普通怪物默认策略仍待实验或产品确认。

**下一文档**：`MODULE_CONTRACTS.md` 应在上述逻辑职责稳定后冻结实际消息的 JSON Schema、身份验证、Observation/Memory 读写、可观察动作和 NPC Combat Intent、幂等键、错误类别及 Rule Engine Adapter 约定。`ARCHITECTURE.md` 最后再汇总全项目，不用 README 承担细节。

**冻结条件（建议）**：确认普通怪物的默认 Agent/Policy 策略；审核 State Machine 观察协议与 Schema 的引用；核实 Rule Engine 支持的 NPC Typed Intent 和 Hazard API；至少让原创合成场景完成一个真实的 NPC 决策 → 状态/规则裁决 → 感知 → 记忆 → 后续选择循环。本文现在仅为架构草案，不表示代码已经交付。

## 13. v0.3 变更说明与文档协作边界

### v0.3 主要修订（继承 v0.2 的感知、记忆与 Context 约束）

1. **保留感知入口**：取消可能被误解为“绕过 Perception 给 NPC 一份全知的 Fresh Authoritative View”的表达；采用 **Event Observation + Current Perceptual View** 两类授权输入，动态进入 NPC Active Context。
2. **引入上下文生命周期**：Stable Prefix、增量交互历史、当前感知快照、Keep / Suspend / Release / Reactivate，以及按资源压力进行可选 Compact。Scene Change 不等于强制销毁 Context。
3. **解耦三个系统**：Evidence Persistence（事件及时保存）、Memory Consolidation（重要经历形成长期认知）、Context Compaction（资源管理）；后二者相互独立，不因一次记忆写入自动触发上下文重写。
4. **修正主持与调度的边界**：DM Agent 能请求 NPC 激活，但 Agent Host 对事件驱动激活、预算与调用流程负责；不允许 DM 代 NPC 产生独立人格决策。
5. **加强可靠性**：承诺事件不等记忆、消费观察不等读过观察、重试不等重复写关系 Delta，缓存连续不等 KV Cache 可靠存储。
6. **继承 v0.1 非功能约束**：单人 PC、无常驻 AI 同伴、World Creation/Visual 延后、战斗中途精确恢复延后、敌方 Typed Combat Intent 验收仍需核实，普通怪物默认策略保持待决议。

### 与其它文档的正式分工

- **`STATE_MACHINE_ARCHITECTURE.md` v0.3**：定义 WorldEvent、Observation、NPCMemoryRecord、Commitment、Outbox/Inbox、权威状态与存档；本文件不重定义其持久化事务实现。
- **`ADVENTURE_PACKAGE_SCHEMA.md` v0.2**：定义 NPC 初始身份、初始知识、场景初态和声明式事件；不存 NPC 的动态推理上下文或后续记忆。
- **`AGENT_ARCHITECTURE.md` v0.3**：定义 NPC 如何从合法感知构建 Context、形成记忆、产生意图、休眠/激活、管理成本和失败行为。
- **后续 `MODULE_CONTRACTS.md`**：冻结 `EventObservation`、`CurrentPerceptualView`、`NPCActivationRequest`、`NPCDecisionProposal`、`NPCMemoryUpdateProposal`、ACK/游标、版本、身份及 Rule Engine Adapter 的最终消息契约。本文 YAML 名称与字段**仅为示意**。

### 仍应保持开放的技术问题

NPC/普通怪物控制器的默认 LLM 策略、NPC 战斗 Intent 的 Engine 公共入口、Current View 的缓存 TTL/证据化方式、Memory Check 重要性阈值、上下文压力指标/压缩算法、NPC 自动反应的深度预算、长时记忆合并/冲突消解等都需实测或下一文档再决定。不得把这些未验证细节写成已经交付的能力。

**v0.3 的核心不变量：NPC 对当前世界的认识来自其合法 Perception；NPC 长期记忆和当前上下文各有生命周期；重要世界事实由确定性系统及时保存；Agent 只能提出决策，不能凭自身措辞修改权威世界。**
