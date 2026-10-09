# Agentic TRPG — State Machine Architecture（MVP）

> **状态**：Draft v0.4（依据 ADR-001 与 NPC Evaluation Mode 决策；具体消息 Schema 与实现仍待审阅）\
> **日期**：2026-10-10\
> **建议位置**：`agentic-trpg/agentic-trpg/docs/STATE_MACHINE_ARCHITECTURE.md`  
> **依赖**：[`ADR-001-UNIFIED-STATE-OWNERSHIP.md`](./ADR-001-UNIFIED-STATE-OWNERSHIP.md)；[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.6；[`ADVENTURE_PACKAGE_SCHEMA.md`](./ADVENTURE_PACKAGE_SCHEMA.md) Draft v0.2；[`AGENT_ARCHITECTURE.md`](./AGENT_ARCHITECTURE.md) v0.4；[`MODULE_CONTRACTS.md`](./MODULE_CONTRACTS.md) v0.2 / Draft\
> **目标场景**：一位玩家、一个 PC、文字优先、人工整理的单人冒险包；Agent DM 和按需 NPC Sub-agent；不要求可视化引擎、World Creation Agent、多玩家或开放世界模拟。  
> **证据边界**：本文件是基于已讨论范围和冒险需求的**设计建议**，不是现有 State Machine 代码的完成状态。与 Rule Engine 的 API 适配以实际实现和独立测试为准。

## 1. 目标、边界和核心术语

State Machine 是**一次具体游戏 Session 的唯一权威运行状态拥有者和最终提交者**，不是剧本生成器、规则引擎或 NPC 对话模型。

它承担六件事：

1. 加载并验证**不可变** Adventure Package；为一次 Session 实例化初始状态。
2. 记录玩家和 NPC 的行动在世界中造成了哪些**已验证、已提交**的变化。
3. 为 Agent DM / NPC Sub-agent 提供**按角色权限过滤**的上下文视图。
4. 将需要机械裁决的动作交给无权威可变状态的 Rule Engine 求值，验证其未提交的 `StateDelta`，再在自身事务中统一提交 World / Character / Combat State、RNG、事件和回执。
5. 使用 Python + SQLite（WAL）持久保存 Session 的全部已提交运行态；MVP 产品仅保证非战斗状态下的安全续玩，不要求恢复进行中的战斗，防止重访重置、事件重复执行、重试重复付款和知识泄漏。
6. 在权威事件提交后以内部 Perception 生成按角色过滤的 Observation，持久保存 Evidence、Observation、NPC Memory 与权威认知；提供可靠投递、NPC Update Proposal 验证和 ACK 接口。LLM 模式、Gate、Context 和推理调度由 Agent Host 协调。

### 1.1 四个容易混淆的概念

| 概念 | 内容 | 可变？ | 谁拥有权威？ |
|---|---|---|---|
| **Adventure Definition** | 地点、静态世界事实、NPC 初始档案、剧情条件、规则绑定 | **不可变**（Session 固定版本） | Adventure Package 作者 / 验证器 |
| **Session Runtime State** | 当前场景、场景实例、世界标记、物体归属、任务、NPC 记忆、事件记录 | **可变** | **State Machine** |
| **Mechanical Combat State** | 战斗中的 HP、位置、Action Economy、RNG、Conditions、集中、回合等 | **可变** | **State Machine（唯一权威）** |
| **LLM Evaluation Context** | DM Context；NPC 可复用 Interactive / 一次性 Background Context | **临时派生视图** | Agent Host 管生命周期；State Machine 提供授权状态与证据 |

**不变量（ADR-001）**：静态模板不是当前状态；描述不是命令；提议不是提交；叙事不是规则计算结果。World、Character、Combat 和 RNG 只有 State Machine 一份持久权威；Rule Engine 只计算而不提交，可使用单次求值内的临时可变对象。

### 1.2 行动、观察与记忆的认识论边界

| 概念 | 由谁产生 / 确认 | 是否成为世界事实 | 可供 NPC 使用的方式 |
|---|---|---|---|
| `Intent` / `Proposal` | PC/Agent/Host 提交的**内部提议** | **否**；被拒绝的私有意图尤其不能公开 | 提议者可获合法拒绝回执；其他角色不可据此读心 |
| `ObservableActionStarted` | **真实在世界中发生**且被提交的外部动作（例如实际伸手） | **是，该外显动作已经发生**；但目标效果未必成功 | 通过 Perception 判断哪些角色看到了动作 |
| `WorldEvent` | State Machine 原子提交的世界/规则事件 | **是，记录客观行为或结果** | 不能向所有 NPC 原样广播含秘密的事件 |
| `Observation` | State Machine 的 Perception Projection（必要机械判定来自 Rule Engine） | **是，该角色获得了某项观察**；观察内容不一定涵盖全部事实 | 构成该角色后续认知的证据，按角色私有保存 |
| `Belief / Memory / Relationship / Goal / Plan` | 当前模式的 NPC LLM 提出可选更新；State Machine 校验后保存 | **成为 NPC 私有权威状态，不自动成为客观世界事实** | 两种模式都读取同一份授权持久状态 |

**关键区别**：Agent A 获得金币，不等于 A 知道 B 也想拿金币。只有 B 真正作出可观察的动作并被 A 感知，A 才能基于观察判断双方是否发生争抢。世界事件的排序也不能直接替代游戏世界的“谁更快”的规则裁决。

### 1.3 不属于此模块的工作

- 不解析 PDF、不自动创建世界：这是 MVP 之后的 World Creation Agent。
- 不计算 Attack、Damage、Save、Spell Slot、Concentration、战斗行动顺序；应复用 Rule Engine。
- 不替 NPC 决定动机、谎言、主观记忆解释或战斗行动；NPC Sub-agent 提议，State Machine 只审核与提交。
- 不生成叙事文本和插画，不做实时地图、Token、动画。
- 不执行任意剧本脚本、不建立通用游戏编程语言；只支持已经审核的有限条件与效果。

## 2. 总体运行架构

```text
Human Player -> DM Planner -> Agent Host / NPC Mode Coordinator
                              |- Interactive active: ordered append -> current LLM
                              |- Inactive: Lightweight Gate
                              |    |- Safe Retention / No-op
                              |    '- Background one-shot LLM (no Interactive Agent)
                              '- Context lifecycle / scheduling / mode switching
                                         |
                       NPCUpdateProposal + shared Typed Command
                                         v
              State Machine（单一权威 Session 状态）
               |- Adventure Package（不可变，只读定义）
               |- World / Scene / Character / Combat / RNG State
               |- Persistent NPC Identity / Personality / Memory / Belief /
               |    Relationship / Goal / Plan / Runtime State
               |- Command / Proposal Validation / Version + Epoch Gate / Commit
               |- Event Log / Evidence Repository / Event-time Perception
               |- Reliable Observation Inbox / Processing Receipts / ACK
               |- Calendar / Due Schedule / Commitment / Durable Outbox
               '- Rule Evaluation Adapter <--> Rule Engine（无提交权）
                       |                         Snapshot + Intent + RNG
                       |                         -> uncommitted Delta / RuleEvents
                       v
              Committed State + WorldEvent
                       |- internal Perception -> reliable Observation -> Host mode routing
                       '- player-visible Receipt / View -> DM Narrator -> Text UI
```

**DM Planner 与 DM Narrator 是逻辑隔离的职责和上下文，可共享底层 LLM，但不得共享同一未经授权的推理视图。** Planner 可以提出合法世界裁决方案，但不能绕过 State Machine；Narrator 只组织已确认、可向玩家展示的结果，不能暗自改写事实或泄露 GM-only 内容。NPC 的私有认知由对应 NPC Sub-agent 处理。

本文定义逻辑组件，不要求微服务、常驻模型或新数据库。State Machine 首版为 Python + SQLite WAL；Perception、证据、观察、持久认知及确定性日程校验是内部职责。Lightweight Gate、Background / Interactive LLM Evaluation 由 Host 协调，Jev 仅为可替换、待实验候选。Rule Engine 使用内存 `_LiveCombat` 的记录是**迁移前实现基线**，不能视为目标架构。

## 3. 运行时数据模型与状态所有权

依据 ADR-001，CharacterState、CombatState、RNGState 及其版本与 WorldState 在同一权威提交域内；Rule Engine 输入是经验证的只读状态快照，输出只是待提交结果。

建议把 Session 存储划分为少量聚合（aggregate）；下面是**概念数据结构**，不是已经冻结的 JSON/Python Schema。

### 3.1 `SessionRecord`：一次冒险实例

| 字段（建议） | 说明 |
|---|---|
| `session_id` | 稳定、唯一、与其他 Session 隔离 |
| `adventure_id`, `package_version`, `package_digest` | 固定加载的冒险定义版本；重载时校验，禁止静默升级 |
| `ruleset_id`, `ruleset_digest`（如可用） | 固定机械规则及数据来源 |
| `pc_actor_id` | 仅一名玩家可直接控制的 PC |
| `current_scene_id`, `current_location_id` | 当前所在场景、地点 |
| `phase` | `exploration` / `combat` / `challenge` / `completed` 等有限阶段（候选） |
| `world_version` | 成功提交世界事务后单调递增的版本号；与事件流水号不同 |
| `last_world_event_seq` | 本 Session 已提交事件的稳定全序序号，观察记录据此引用及排序 |
| `last_safe_checkpoint_id` | 最近可核验的非战斗安全恢复点；不意味着活跃战斗可精确恢复 |
| `status` | `active`、`combat_unrestorable`、`completed`、`blocked_reconciliation` 等（候选） |
| `active_combat_ref` | 非空时只指向 Engine 战斗 Handle/会话，不保存另一套战斗真相 |
| `created_at`, `updated_at` | 运行元数据，不直接决定游戏世界时间 |

**注意**：`phase` 不等于每个场景固定的剧情幕数。玩家可合法往返 Scene，不应被强制套入不可逆的线性故事进度。

### 3.2 `WorldState`：会话全局事实

包括 `flags`、`quest_state`、`game_time`、`world_actor_locations`、`object_instances` / `inventory_ownership`、已解锁的内容标记等。

约束：

- `flags` 仅用于剧情/场景状态，不能成为 HP、Slot、Action Budget 等机械变量的替代品。
- 物品 `owner_id`、当前位置与 `quantity` 由 State Machine 唯一维护；在活跃战斗中也由 State Machine 原子提交，机械消耗与合法性先经 Rule Engine 求值。
- 人物身份在 World State 中稳定；战斗中 `Combatant` 是同一 Actor 的临时机械表示，其结束结果通过映射返回世界。
- 若两个场景引用同一个世界 Actor，不复制成互不关联的角色实例。

### 3.3 `SceneInstance`：场景懒初始化、只初始化一次

建议字段：`scene_id`、`initialized`、`visited_count`、`local_flags`、`object_ids`、`trigger_history`、`last_visit_seq`。

进入场景流程：

1. 根据 `scene_id` 查询静态 Scene Definition，验证入口/出口及任何状态条件。
2. 若本 Session **从未实例化该场景**，应用 `initial_state` 一次，生成对象实例和局部标记。
3. 若已实例化，则保留现有实例状态；**绝不因为重访重放初始掉落、NPC 位置或机关状态**。
4. 按权威状态记录 `scene.entered`，其触发的事件走统一事件审核与提交路径。

注意：静态 `actor_ids[]` 只提供初始在场信息；世界 Actor 的当前位置由运行态单点保存。不能因为玩家重访让已经离开的 NPC 重新出现。

### 3.4 `ActorRuntime` / `NPCState`

- 所有 Actor：稳定身份、当前世界位置、归属、世界层可见状态、可用控制策略。
- 玩家 PC：角色身份与所属；**机械角色构建**由已审核的 Build/Rule Engine 获取，不得凭剧本文字凭空生成等级与 HP。
- NPC：唯一 Persistent Identity、Personality、Memory、Belief（允许错误）、Relationship、Goal、Plan 和 Runtime State（Schedule / Current Activity 等）；私有知识、处理游标与控制权一并权威保存，观察收件箱与认知更新分开。
- 敌人/普通怪物：与重要 NPC 一样有身份和状态，但是否调用 LLM 要由策略决定；不要求为每一个普通怪物常驻创建 Agent。

**三个独立命题**：`world_fact_is_true`、`npc_knows_fact`、`npc_believes_fact`。允许 NPC 有错误信念和撒谎，但禁止把信念自动提交为世界事实。

Interactive / Background 是 **LLM Evaluation Mode**，不是两个人格或两份 NPCState。Agent Host 管理模式切换与非权威 Context；State Machine 仅持久保存其提交验证所需的 epoch / evaluation 凭证、版本和处理回执等协调元数据，不能从 Context 内容反向覆盖权威状态。

### 3.4a `CharacterState`、`CombatState` 与 RNG（统一权威）

State Machine 为每名 Actor 保存 HP/Temp HP、法术位、有限使用次数、装备、Condition、持续效果；活跃 Encounter 持有 Initiative/Turn、行动经济、位置、Concentration、反应窗口、Pending Choice、RNG 流位置以及所需技能/规则生命周期账本。只存储明确规定的权威数据，不复制可由规则确定性计算的派生字段作为第二权威。

同一角色在战斗内外共享角色资源的最终所有权：喝药、开门、取物、移动等跨界动作最终由**同一个 State Machine 事务**提交；Rule Engine 负责计算机械结果。State Snapshot 必须完整、版本化并固定 Ruleset Digest。Rule Engine 内部临时缓存及执行对象不是可持久化权威。

### 3.5 `ChallengeInstance`：非战斗技能挑战

针对撤退、追逐或跨多次检定的任务，建议记录：`challenge_id`、`scene_id`、`successes`、`failures`、`required_successes`、`status`、`resolved_check_ids`。每次检定的 DC/能力/结果由合法规则或显式 GM 裁决产生，**State Machine 仅累计已提交 Result**。

不要把非战斗技能挑战实现为伪造的 Combat；若失败伴随伤害/Condition，需要受控 Rule Engine/Host Hazard 接口，缺失时明确阻塞该场景而不是直接写入 HP。

### 3.6 `WorldEvent`、感知证据与顺序

`WorldEvent` 是**已提交的、不可变的世界事件记录**，最小概念字段：`session_id`、`event_id`、`event_seq`、`event_type`、`source_command_id` / `engine_operation_id`、`actor_id`、`object_ids`、`scene_id`、`occurred_at_game_time`、`payload`、`visibility_class`、`perception_evidence_ref`。字段为候选，不代表现有实现。

- `event_seq` 由 Session 中的权威提交顺序分配，单调递增；它是**记录顺序**，不自动证明角色的生理反应速度。
- `WorldEvent` 应记载必要的**发生时刻证据**（行动时地点、参与者位置、光照/可听性、遮挡/秘密等级、相关动作是否外显）。不能在 NPC 数分钟后苏醒时用**当前**视野倒推此前谁看到了什么。
- 可见动作的开始与成功/失败结果是不同的事实；只有实际外显的 `action.started`（候选事件）才允许投影给旁观者。私有 Intent、未执行命令、LLM 私下计划不得伪造为外显动作。
- Rule Engine 产生的拟议机械事件只有在 State Machine 原子提交对应 Delta 后才成为权威 WorldEvent/CombatEvent；未提交的求值结果不得触发永久世界事件或 NPC 观察。

### 3.7 `ObservationRecord`：角色实际收到的观察

建议字段：`observation_id`、`session_id`、`observer_actor_id`、`source_event_id` / `source_event_seq`、`observed_at_game_time`、`perception_kind`（如 sight/hearing/self_action/report）、`observed_payload`、`visibility_basis` / `rule_check_receipt_id`（若适用）、`projection_version`、`delivery_status`。每项 Observation 必须标明**观察者**和**来源**，不能在投影中包含事件对该观察者不可知的隐藏字段。

- MVP 只需同场景、简单视觉/听觉、人物在场状态、明显动作与自我行动结果。遮挡、幻术、远距离声音、误认等高级机制后置；若重要剧情要求检定，不得凭普通同场景规则绕过 Rule Engine。
- 观察投影是确定性、可去重的映射；`(observer_actor_id, source_event_id, projection_kind)` 等候选唯一键防止重试生成重复观察。结果按 `source_event_seq` 有序读取。
- 优先在世界提交事务中一次性落库已确定的观察；若投影较复杂，必须以**持久 Outbox + 事件时证据**处理，并使用幂等投影，避免提交成功但观察永久丢失。
- `ObservationRecord` 是证据而非角色长期记忆。一个 NPC 可以暂时不理解、不在意甚至忘记某个观察，但不能因此篡改原始事件与感知来源。
- 稳定 `observation_id` 与按 NPC 的有序 Delivery Cursor 支持至少一次投递；读取分页位置、Context 已追加位置、已完成处理及 ACK 位置分别跟踪。ACK 只推进连续已完成前缀，必须以投影完成水位/等价机制防止跳过尚未投影的早期事件；具体字段见 `MODULE_CONTRACTS.md` §7、§9（Proposed / Not Implemented）。

### 3.8 `NPCMemoryRecord`：角色内部认知的持久表达

建议将 NPC 私有记忆分为 `episodic`（经历摘要）、`belief`（主观判断，允许错误）、`relationship`（对他人的态度）逻辑记录；Goal / Plan 同属权威 NPC 认知状态。统一保留 `npc_id`、稳定记录 ID、`source_observation_ids` / `source_memory_ids`、`epistemic_status`（observed / inferred / told）、`confidence`（如适用）、`evaluation_id`、`proposal_id`、模式 epoch 和内容版本；承诺回忆引用另存的已确认 Commitment。

**主观 Memory、Belief、Relationship、Goal / Plan 更新由当前模式的 NPC LLM 提议**；State Machine 验证 Actor 权限、来源、受限字段、版本、模式资格及幂等性后保存。Interactive 活跃期间不另开 Background / Memory / Cognition LLM。Schema 不能证明自然语言推断真实，故保留来源与推断/听说标签；确定性知识授予、原始证据、已确认承诺及必要安全处理无需等待 LLM。

## 4. Session 生命周期与场景流程

建议明确四个最小生命周期：

- **Package Validation**：解析 YAML/JSON、安全字段、Schema 版本、引用完整性、规则绑定、内容来源；失败不创建 Session。
- **Session Creation**：固定 `package_digest` / `ruleset`；创建一个 PC Slot、初始世界和 NPC 实例，初始化入口 Scene；同一创建请求不能生成两个会话。
- **Session Interaction**：按当前 Phase 验证命令，读取所需世界视图，选择世界事务或规则执行；根据已提交结果推进世界与事件、计算 Observation；NPC 记忆解释独立于世界状态提交。
- **Save / Resume / Complete**：持久化运行态与 NPC 观察/记忆；重启后恢复**非活跃战斗** Session；活跃战斗不可声称精确恢复，完成后保留最终事实和回执。

允许自由探索和合法的旁路，不建立不可跳过的硬编码场景序列。Scene Graph 只是可达性与条件定义；剧情是否推进由已提交的事实和事件决定。

## 5. Command → Result → World Event 的执行协议

### 5.1 命令信封（概念字段）

```yaml
command_id: cmd.demo.0007
session_id: session.demo.01
actor_id: npc.gate_warden
controller_id: npc_controller.gate_warden
expected_world_version: 12
kind: world.operate_object
payload:
  object_id: object.iron_gate
  operation: open
```

这是**原创合成示例**；命令类型和字段是设计提案。具体 API 名称应在 `MODULE_CONTRACTS.md` 冻结。最小要求为身份、权限、命令唯一键、预期版本、操作参数和可关联来源。

### 5.2 按操作来源采用不同执行分支

| 分支 | 输入 | 权威执行 | 成功后的 State Machine 工作 |
|---|---|---|---|
| **世界操作** | 开门、取物、NPC 位置转移、设旗标 | State Machine 验证条件、权限并提交 | 记录一次世界事件，更新物体/Quest/Scene |
| **规则操作** | Ability Check、Save、Combat Intent、受控 Hazard | Rule Engine 进行无副作用求值；State Machine 统一提交 | 验证待提交 Delta，原子写入角色/战斗/世界状态、RNG、事件和回执 |
| **纯对话** | `NPCDialogueProposal` | NPC 提议，经 Host 校验后成为可呈现内容 | 只有有明确语义的承诺/线索公开/关系变化才持久化；普通一句对话不产生机械效果 |
| **场景转移** | 进入已定义出口、传送剧情事件 | State Machine 的场景与权限判断，必要时 Rule Engine | 更新位置并记录 enter/exit；不重置旧场景 |
| **脚本事件** | 经审查的 `event_id` 触发及条件满足 | State Machine 的受限声明式 Event Executor | 执行允许列表的世界效果，一次性/按规定次数去重 |

### 5.3 世界事务（同一数据库/进程内）

候选最小步骤：

1. 按 `(session_id, command_id)` 查询历史完成回执；同键相同内容返回原结果，**同键不同内容拒绝冲突**。
2. 验证 `expected_world_version`、Actor 控制权、当前 Phase、可见/可用对象与事件条件。
3. 对需要机械规则的操作，先在**写事务外**调用 Rule Engine 求值得到 `accepted` / `rejected` / `needs_choice` / `unsupported`，并持有返回的预期版本和 RNG 转换；进入短事务后再次验证身份、版本及 Delta 不变量，再将全部 World / Character / Combat / RNG Delta、Events、Receipt 和去重键一并提交。世界操作可直接生成待提交 Delta。
4. **事务提交完成后**才返回 `committed` 并允许 Agent DM 将其叙述为事实；失败/冲突不写任何部分 Delta。

请求 payload 应使用稳定序列化计算指纹，以区分重复提交和同一 `command_id` 下的不同请求。MVP 使用单个本地 SQLite 数据库的原子事务，不引入分布式事务协调器。

**性能与锁纪律（SM-01 已确认）**：Agent 推理、远程/本地 LLM 调用、需要等待的 Rule Engine 调用必须在 SQLite **写事务之外**。读取版本和生成提议后，在短写事务内重新验证 `world_version` 与操作条件，再原子提交 State Delta + World Events + Command Receipt + 去重记录 + 可即时生成的 Observation/Outbox。SQLite WAL 允许并发读，但写事务仍需串行；Session 内逻辑命令协调不等于 SQLite 自带游戏顺序。

### 5.4 单一提交者协议：Rule Evaluation ≠ Commit

**目标语义由 ADR-001 固定。** Rule Engine 不拥有独立的权威可变 Combat；调用 `evaluate(snapshot, typed_intent, pinned_ruleset, rng_context)` 返回的 `RuleEvaluationResult` **尚未提交**。`accepted` 只是求值完成；只有 State Machine 的 `CommitReceipt.status=committed` 才代表世界已变更。

```text
Load State Snapshot + version + RNG position
  -> Rule Engine evaluate（不得提交）
  -> accepted / rejected / needs_choice / unsupported
  -> State Machine begin short transaction
  -> Validate read set, versions, authorization, delta invariants, idempotency
  -> Apply World + Character + Combat + RNG deltas and Events + Outbox
  -> Commit SQLite transaction
  -> Return immutable CommitReceipt / publish perceptions / Narrator output
```

**核心约束**：

- 不能在 SQLite 写事务中等待 LLM、Rule Engine 或远程调用；提交前重新验证输入版本/关联读集；冲突时废弃未提交的规则结果，并根据稳定命令 ID 与 RNG 语义受控重试。
- State Machine 持有权威 RNG 状态或流位置；求值使用显式 RNG Snapshot；未提交请求、规则拒绝、版本冲突均不得推进权威 RNG。重试遵守幂等回执，不得双掷骰或重复付款。
- Accepted Delta 必须覆盖一次动作的全部机械及世界副作用（例如药水消耗、恢复 HP、行动经济），状态更新、事件、RNG 和 Receipt 原子提交；不能用 Engine 自身的最终提交回执替代状态事务。
- `needs_choice` 必须返回可标识、版本绑定的待续裁决状态，不得把未完成动作误写为结果；取消、超时及失效必须明确处理。复杂 Reaction Chain 可能需要可验证的短事务级分段及安全 PendingChoice 状态，实际协议在 Module Contracts 冻结。
- 旧 `_LiveCombat`、`CombatHandle` 和 Bridge 进程内回执属于迁移前代码，不是可继续采用的双权威设计；迁移可以有短期兼容适配，但同一实际 Session 不得出现两个最终状态持有者。
- Perception 只消费 State Machine 的**已提交**事件及其事件时感知证据；Narrator 不得把规则求值结果当作已发生事实。

本节是**目标接口语义**，并非现有 Rule Engine 已具备无状态 evaluate API 的声明。

### 5.5 事件驱动与链式触发

- 只有**由 State Machine 最终提交的权威事件**能触发 `events.yaml` 条件。LLM 的自述、未接受的 NPC 决策或草稿对话不是 Event。
- Event Condition 使用既定封闭表达式词汇（`all`、`any`、`not`、`flag_equals`、`actor_present`、`event_once`、`challenge_count_at_least` 等），禁止 `eval`。
- 可执行的 World Effect 只使用 `ADVENTURE_PACKAGE_SCHEMA.md` 的允许列表；机械效果必须先经 Rule Engine 求值，随后由 State Machine 验证并提交完整 State Delta。
- 为防止 Event A → Event B → Event A 的无限循环，按 `event_id + trigger_event_id + session_id` 去重，并设定每个外部命令的最大链式事件数。发现循环应**整体拒绝世界事务**或进入显式故障状态；具体限额待实现期确定。
- 一次“获得宝物”“取消机关”“完成任务”的世界效果应具有持久事件身份，不能因重试或再次进入场景重复发奖。
- 事件链完成提交后，向 Perception Projection 提供事件时证据；观察对各 NPC **分别投影**而非广播完整世界事件。下游 Agent 激活可以异步，但对应 Observation/Outbox 不能无记录地丢失。若投影依赖额外 Rule Check，则在事务外协调受控检定并持久化待定状态，不能持有数据库写锁等待检定。

### 5.6 并发取物与竞争动作：提交顺序不是敏捷判定

原创测试情境：金币 `coin.001` 在桌上，NPC A 与 B 都想取走。

1. A、B 基于相同 `world_version=12` 可以各自提交私有 `take_item` Intent。**仅提交 Intent 不意味着角色身体已移动**。
2. 如果是普通依次处理的非竞争命令，A 的取物先有效提交，物品归 A；B 的旧版本请求收到冲突并刷新世界视图。B 若在现场且能够看到 A 的动作，应收到对应 Observation。此时 A 只知道自己拿到金币，**不得**得知 B 的未外显意图。
3. 如果规则/Host 已明确进入“同步争抢”场景，应先生成可信的外显 `action.started`（仅在确实发生时），以公开的确定性顺序政策或 Rule Engine 执行需要的竞争检定，确定结果。不得按 API 到达先后编造“角色 A 更敏捷”。
4. 裁决后记录 A 获得金币、B 未获得的实际结果及适用的外显动作；按事件**当时**的感知条件投影给双方。A 只有在观察到 B 的伸手动作时才可记得“我与 B 争抢过”；B 若看到 A 抢先成功，可以将“我慢了一步”作为经历，而“对方有意羞辱我”仅是 Belief。
5. 两个 NPC 的后续愤怒、信任变化与行动选择由各自 Sub-agent 根据 Observation 提议，不预置所有 NPC 都会愤怒。其提议仍需权限、版本与来源校验。

本节只定义**语义要求**；哪些自由行动进入竞争流程、游戏时刻如何排序和检定公式，由 Agent DM 的授权裁决与 Rule Engine 适配在 `MODULE_CONTRACTS.md` 进一步冻结。

## 6. 知识隔离、感知投影、NPC 记忆与激活

### 6.1 视图类别与可观察事实

| 视图 | 允许包括 | 禁止包括 |
|---|---|---|
| `PlayerView` | PC 已感知的场景、已发现线索、合法已公开世界结果、本人资源摘要与最新观察 | DM-only 世界秘密、未发现伏击、其他 NPC 私人记忆、未观察到的隐藏动作 |
| `DMView` | 场景的完整审核信息、关键剧情条件、Rule Engine 能力边界、真实游戏状态 | 将未经规则确认的 Agent 文本标成机械成功 |
| `NPCView(npc_id)` | 该 NPC Profile、已知事实 ID、私人 Beliefs/Goals、合法 Memory、该 NPC 的 Observation Inbox 与眼前可观察状态 | 世界全部 `dm_only` 内容、其他 NPC 私有上下文、未见过的玩家秘密、其他 NPC 未外显的 Intent |
| `EngineRequest` | 合法 Actor、目标、可选能力、机械输入、固定规则快照 | 原始 NPC 私人思考、剧情文案作为伪规则参数 |

**实现约束**：在检索/投影层做行级与字段级过滤；不要先把全量 Adventure Package 或全局 Event Log 交给 NPC Agent，再靠 Prompt 要求它“不要看秘密”。Rule Engine 不负责决定谁看见了什么；需要 Perception / Insight 等机械判定时使用受控 Rule Check 入口。

### 6.2 `WorldEvent → Observation`：事实如何成为角色经历

1. State Machine 在世界操作或 Rule Engine 求值结果**成功原子提交后**，持久化带顺序、来源与事件发生时证据的 `WorldEvent`。
2. Perception Projection 使用该事件**发生时**的角色位置、在场状态、光照、可听范围、已审查可见性标签及必要规则检定，按 `observer_actor_id` 生成不同的 `ObservationRecord`。
3. 只给每个角色提交自己可知的观察文本/结构；例如 NPC 见到某人倒下，不自动知道其隐藏 HP 或凶手的内心动机。
4. Observation 先保存到该角色的私有有序收件箱（inbox）；可在其下一次激活时消费。离线 NPC 不需要运行 LLM，也不能因延迟激活而从**现在**的 WorldState 重算先前视野。
5. Observation 的投影/分发可通过本地持久 Outbox 异步完成；事件已提交但投影或唤起失败时，应安全重试且不重复生成、不给其他 NPC 泄密。

**没有可观察事件就没有旁观者读心**：仅有 B 的 `Intent: take_coin` 不得通知 A“B 想抢钱”；若 B 实际伸手且 A 看见了，则 A 可以收到外显动作观察。对话、误认、隐匿、感知检定及证人转述的特殊情况要保留各自来源，不得把“听说”冒充“亲眼目击”。

### 6.3 Observation Delivery 与 NPC Evaluation Mode Exclusivity

Observation 无须等待任何模型运行，先由 State Machine 的 Perception / Evidence / Inbox 可靠保存，再交给 Host 按模式路由：

```text
Committed WorldEvent -> State Machine Perception -> Reliable NPC Observation
   -> Agent Host Mode Routing
      |- Interactive Mode active (including idle)
      |    -> ordered append to existing Interactive Context
      |    -> current Interactive LLM at next scheduled request
      '- Inactive NPC -> Lightweight Gate
           |- No LLM Required -> Safe Retention / No-op
           '- Background Evaluation Required -> One-shot NPC LLM
                -> optional Memory / Belief / Relationship / Goal / Plan Update
                -> optional Action Intent
   -> State Machine validation / commit / durable disposition -> ACK
```

**Interactive 独占**：所有需要 LLM 的主观记忆、Belief / Relationship、Goal / Plan 修订和自主行动判断统一交给当前 Interactive LLM；不对每条 Observation 单独调用 Lightweight Gate，不额外启动 Background / Memory / Cognition LLM。Context 可在无模型请求期间保持 Active；重要事件由 Host 主动安排下一次 Interactive 推理。在途请求的新观察排队供下一次调用，不假设能修改执行中请求或物理 KV Cache。

**Inactive Gate**：Lightweight Gate 由 Host 协调，可用确定性规则、轻量模型或组合；Memory / Cognition / Behavior Trigger 是可联合的逻辑职责。Gate 只判断安全保留与是否需 Background Evaluation，不替 NPC 主观修订 Belief / Goal / Plan。候选 `durable / short_term / discard` 仅作用于安全保留策略，不将保留证据当成 LLM 已形成主观记忆。`discard` 不删除权威 WorldEvent、未完成投影、关键证据或未处理任务；不确定时保守保留。

**Background Evaluation**：输入同一 NPC 当前权威身份、人格、相关 Memory / Belief / Relationship / Goal / Plan 与新 Observation；可使用独立 System Prompt、模型和 Context Builder。一次输出可联合包含可选认知更新及 Action Intent；调用完成释放临时 Context，**不创建、不恢复、不激活 NPC Interactive Agent**。

State Machine 对两种模式的统一 `NPCUpdateProposal` 验证来源、身份、认知归属、Schema、版本、epoch 和幂等性，保存私有权威状态而不提升为 World Fact。原始证据、已确认承诺和必要确定性安全处理继续独立运行；所有 LLM 调用在 SQLite 写事务之外。

### 6.4 自主 Action Intent、日程与模式切换

NPC 的 Action Intent 可来自 Interactive LLM、Background One-shot LLM 或已审核的 Deterministic Schedule / Policy。三者共享 **Actor 授权 → Typed Command → 必要的 Rule Engine Evaluation → State Machine Commit** 路径；非机械世界操作沿用 §5.2 分支。Intent 不代表已执行，合法提交后才产生 WorldEvent，无须先激活 Interactive Agent。

简单日程仍由游戏时钟驱动；State Machine 保存活动/计划版本、稳定 trigger ID、到期时间和完成/取消回执，并重验地点、存活、失能和环境前提。Host 控制评估次数、预算、冷却与防循环；确定性安全暂停不等于 LLM 已替 NPC 做出新计划。Jev 为可替换实验候选，非 MVP 依赖。

**Mode Switching（Proposed / Not Implemented）**：Host 按 NPC 串行切换；State Machine 持久校验 `mode_epoch` / evaluation 凭证。Background → Interactive 时先停止派发并以短事务 CAS 撤销旧 Background 提交资格，尽力取消模型；迟到结果因旧 epoch 拒绝。先查已提交 NPC Update / Action Receipt，再以最新权威状态和未 ACK Observation 建立交互 Context。切换之前已成功提交的结果保留；切换后旧任务尚未提交的更新或行动拒绝，不覆盖新的 Belief / Goal / Plan。Interactive → Inactive 同样先完成或撤销旧请求并对账、推进 epoch，之后才允许 Background。

同一模式也不得有两个无协调的主观 Evaluation。Proposal 与其派生 Action Command 在短提交事务中重验 epoch、NPC 状态版本及世界前置条件；版本冲突不得盲目重放旧 Delta。模式切换的 CAS 和提交校验须处于同一持久协调边界，不能只靠 Host 内存取消标记。故障重启先撤销过期资格、对账回执，再重建模式和 Context；协议字段尚待 `MODULE_CONTRACTS.md` §9 评审。

### 6.4a 处理回执、ACK 与 Memory / Context 独立性

- 读取分页 Cursor、追加到 Context、模型已返回、处理完成与 ACK 分别记录。只有 State Machine 已保存 Safe Retention / No-op，或被选定 Proposal 的可选更新和 Action Intent 均有终态处置回执后，才可完成处理并 ACK；Pending Choice 等待续工作可靠保存且相应 Observation 保持未完成。
- Observation 批次使用跨模式稳定 `observation_work_id`；执行前持久选定 Proposal 及子操作义务。使用稳定 `evaluation_id / proposal_id / command_id`，重试先查回执；重复投递、模型/进程故障和版本冲突不重复写 Memory / Relationship Delta 或行动。已提交槽位对账复用，未完成项交当前模式处理，不能通过新评估 ID 重做已完成副作用。
- ACK 仅推进连续完成前缀，不能跨越未处理项或较早投影缺口。模型失败、取消、旧 epoch Proposal 本身不构成成功处理；关键证据及待处理任务不能随 Context 释放消失。
- State Machine 负责 Evidence、Observation、Persistent Memory 与权威认知；Host 负责 Model Evaluation、Context Lifecycle 和调度。**Memory Persistence 不强制触发 Context Compaction / Rebuild**；Compaction 仅因 Token、延迟、成本或上下文质量压力发生，摘要无权改写 NPC 状态。

### 6.5 对话承诺、知识传播及故障

- NPC 对话可包含谎言、猜测、转述或修辞；话语事实不等于内容是真实世界事实。可观察的已发布话语可以形成 `speech` 类型世界事件，并投影给合适的听众。
- 公开事实、完成承诺、赠与物品只有在结构化意图合法执行并提交后才产生对应**世界副作用**；NPC 自称“我给你金币”不等于金币已转移。私人 Relationship 更新由 NPCUpdateProposal 独立验证保存，不自动产生公开世界事实。
- Sub-agent 超时、输出不合法或提出不可能行为：返回 `proposal_rejected`/`agent_unavailable`，保留未确认 Observation，允许有限次重新提议或由事先批准的非 LLM 策略接管；不能让 DM 静默冒充该 NPC 的独立决定。

## 7. 战斗：单一权威状态与规则求值

### 7.1 战斗开始

1. State Machine 加载 Encounter 定义、角色资源、初始位置与固定 Ruleset，验证玩家与 NPC 的 Actor 归属、战斗许可与相关 WorldState。
2. 通过 Rule Engine **计算**初始化（包括先攻 RNG、起始效果、回合顺序），得到初始 `CombatStateDelta + RuleEvents + next_rng_context`；Rule Engine 不注册一个独立的权威活跃战斗对象。
3. State Machine 在短写事务中原子提交 `phase=combat`、Encounter/Combat State、Character State、RNG、事件、Receipt 和必要 Outbox；同时保留合法的战前安全 Checkpoint 及战斗入口元信息。

### 7.2 战斗期间

- 每次 PC/NPC 的 Typed Intent 统一到 State Machine Command API。Host 绑定身份与权限，State Machine 获取版本化快照并调用 Rule Engine 求值，再对 Delta 和 RNG 进行原子提交。
- CombatState 包括回合顺序、行动预算、位置、Active Effects、Concentration、待处理 Reaction/Choice 等。State Machine **持有和持久化**这些字段但不自行计算规则；Rule Engine 不维护跨调用的私有战斗权威。
- 战斗中打开门、拾取物品、喝药、触发机关等跨世界/规则动作必须经**同一最终事务域**提交完整副作用，不能在 Rule Engine 内偷偷提前扣费。
- 已提交的 Combat/World Events 经事件时 Perception 分发，可供 DM Narrator 叙述；未提交的规则求值或 LLM 提议不能被叙述为已发生。
- `needs_choice`、Reaction、未完成效果生命周期及 RNG 语义必须有显式待续裁决契约，不能假设一步求值总可完成；具体协议在 `MODULE_CONTRACTS.md` 冻结。

### 7.3 战斗结束

- Rule Engine 只计算结束条件和对应 State Delta/Rewards；State Machine 原子提交状态/任务/战利品/事件与最终 Receipt，并切换 `phase`。不存在“结束后从另一个权威战斗内存回写世界”的阶段。
- 资源始终按原 Actor 的实际支付者归属记录；既有 `CombatOutcome.expended_resources` 的已知缺陷必须通过独立正确性用例检验，不能照搬旧有错误聚合。

### 7.4 活跃战斗恢复的 MVP 边界（SM-02）

**统一持有并持久化 CombatState 不等于承诺精确的中途战斗续玩。** MVP 必须保证正常连续战斗和已提交动作的可靠性；非战斗 Session 恢复为发布要求。中途退出后的 PendingChoice、反应窗口、特殊效果延续和完整 Replay 能否精确恢复仍属于 Post-MVP 验证目标。

若进程中断且处于活跃战斗：系统不能宣称能够无损续玩；可以在确认不违反已提交副作用与版本要求时**经玩家确认**从战前 Checkpoint 重新开始，否则明确阻塞并给出故障信息。不能悄悄回滚已永久提交的规则操作。安全重新开始是否支持及限制条件需要独立验收。

## 8. 持久化与恢复边界

### 8.1 需要保存的最小状态

`SessionRecord`、全局世界标记、SceneInstance、唯一 Persistent NPC State（含 Personality、Goal、Plan、Schedule / Current Activity）、**Observation Inbox、事件时感知证据、NPC 处理/ACK 游标及待处理 Outbox**、Evaluation / Proposal / 子操作回执与模式 epoch 协调记录、物品与 Quest、Challenge 计数、已提交 Event Log、命令回执与去重键、Package/Ruleset Digest、当前阶段、权威 `CharacterState` / `CombatState` / `RNGState`、待续裁决和规则求值/提交回执。LLM Context / KV Cache 不属于 NPC 权威存档。

**SM-01 已确认的实现基线**：Python + SQLite 单进程 State Machine，启用 `PRAGMA journal_mode=WAL`、`PRAGMA foreign_keys=ON`，优先 `PRAGMA synchronous=FULL` 保障关键存档的断电持久性；合理配置 `busy_timeout`、连接生命周期与备份策略。WAL 并不消除单写者限制；不要在写事务中等待 LLM/Rule Engine。数据库文件放在本地支持可靠文件锁与同步的存储上，不假定可经共享网络盘安全多写。

建议索引/约束（具体表结构待实现）：`UNIQUE(session_id, command_id)`、`UNIQUE(session_id, event_seq)`、`UNIQUE(session_id, observation_id)`、`UNIQUE(session_id, npc_id, evaluation_id)`、`UNIQUE(session_id, npc_id, proposal_id)`，以及按观察者/有序 Delivery Cursor 的查询索引和模式 epoch CAS；以实际键模型消除重复副作用。Session 的 Version Gate 与数据库写锁串行性分别负责语义一致性和持久化原子性。

快照可用于快速读取/恢复，但权威一致性来自短事务内提交的 State Delta + Receipt + Event/Observation Outbox；MVP 不必构建完整 Event Sourcing 平台。4–5 名玩家、数百 NPC 的支持属于将来基于真实并发与延迟测试评估的扩展目标，**不是**当前单人 MVP 的功能承诺。

### 8.2 非活跃战斗恢复（MVP 必须）

加载 Session 时：校验包版本与 Ruleset、重建或读取最新 World State、恢复 NPC 知识、私有 Observation Inbox / `observation_cursor` 与 Memory、恢复 Scene 位置及已提交事件去重集合；重访不得从 `initial_state` 重新复制已改变的实例。**只有处于非战斗状态且不存在未解决的命令/待续裁决，或已有明确受控安全点，才可以宣称 MVP 的成功续玩。**

### 8.3 活跃 Combat 恢复（明确移至 Post-MVP）

**SM-02 已确认**：不要求跨进程恢复活跃战斗的精确回合状态。活跃战斗不能调用普通 `save_session` 返回“可安全续玩”的成功回执。按 §7.4 使用战前 Checkpoint + 显式重新开始资格判定 / 阻塞状态；**不得悄悄回滚已提交机械结算**。未来评估从 State Machine 的持久 `CombatState` 和 PendingChoice/Reaction/RNG 精确续玩，**不再以恢复 Engine 私有 Handle 为前提**。

### 8.4 Replay 与审计

- **世界 Replay**：可根据已提交的有序世界命令/事件恢复或核验；保留各 NPC 的 Observation 来源、投影版本与记忆提议回执；不要求 LLM 对话、记忆解释逐字重生成。
- **机械 Replay**：以固定 Ruleset、已提交的 Snapshot/Intent/RNG 进度和确定性 Rule Evaluation 复算核验；由 State Machine 持久保存权威原始事实，Rule Engine 提供求值一致性。
- **禁止**通过新一次随机执行重建已提交但回执不明确的命令；按 State Machine 的幂等记录恢复或阻塞。

## 9. 错误分类与安全失败语义（设计建议）

| 分类 | 典型原因 | 世界状态影响 |
|---|---|---|
| `invalid_package` | 文件/引用/规则绑定错误 | 无 Session 创建 |
| `unknown_session` / `unknown_actor` | 身份未定义 | 不提交 |
| `unauthorized_controller` / `knowledge_denied` | 越权 Actor、读取秘密 | 不提交 |
| `state_version_conflict` | 过期 `expected_world_version` | 不提交；要求刷新视图 |
| `rule_refused` / `unsupported_mechanic` | Engine 不接受目标、成本或机制 | 不得凭空写入机械成功；可有已发布的拒绝事件 |
| `commit_response_failed` | State Machine 已提交，但响应构建失败 | 查询本地稳定命令回执；不能二次执行 |
| `evaluation_or_commit_unknown` | 网络异常或提交回执未知 | Rule Engine 评估不构成提交；查询 State Machine 命令记录，无法判定则安全阻塞 |
| `world_transaction_failed` | 世界数据库提交异常 | 不产生部分提交；重试按命令回执/去重处理 |
| `agent_unavailable` | NPC 模型调用错误、超时 | 无 NPC 世界副作用；保留观察收件箱，执行明确的故障策略 |
| `observation_projection_pending` | 投影排队、需要受控规则检定或 Agent 尚未消费 | 保留事件及证据/Outbox，不对观察者泄漏秘密或丢事件 |
| `invalid_memory_proposal` | 记忆来源不属于该 NPC、越权编造亲见/引用、错误版本 | 拒绝更新；不污染世界事实或他人记忆 |
| `combat_unrestorable` | 活跃战斗退出，精确机械状态无安全恢复办法 | 不宣称恢复原回合；检查战前重开条件或阻塞 |

特别区分：**Rule Evaluation rejected**、**Rule Evaluation failed**、**State Machine Commit failed/unknown**、**Committed response delivery failed**；不能一律映射为“失败，请重新掷骰”。

## 10. 最小公共接口（仅候选名称）

以下是候选接口，不是现有实现或强制 REST 端点；新增 NPC 消息均为 **Proposed / Not Implemented**，由 `MODULE_CONTRACTS.md` §7、§9 审阅。Host ↔ State Machine 的读/写是跨模块边界，`project_world_event` / 日程检查是内部逻辑操作，`RequestNPCEvaluation` / Mode Routing / Gate 是 Host 内部职责，不作为 State Machine 执行 LLM 的 API。

| 接口 | 输入 | 输出 |
|---|---|---|
| `validate_package` | Package 路径/数据 | 完整性检查与 Ruleset Binding 报告 |
| `create_session` | `adventure_id`、包版本、唯一 PC Build/身份、命令 ID | `session_id`、入口 Scene View、初始化回执 |
| `get_scene_view` | Session、Viewer 身份 | 经过可见性过滤的场景事实 |
| `get_npc_view` | Session、`npc_id`、可信请求主体 | 唯一 NPC State 的授权 Identity / Personality / Memory / Belief / Relationship / Goal / Plan / Runtime View 及版本 |
| `get_event_observations` | Session、`npc_id`、授权 Host、读取 Cursor | 稳定 ID、有序观察、投影水位和分页 Cursor；读取不 ACK |
| `get_current_perceptual_view` | Session、`npc_id`、授权范围 | 当前时刻过滤后的感知；用于长期记忆须有可核验证据引用 |
| `ack_observations` | NPC、连续完成范围、持久处理回执引用 | 校验处理义务及投影水位后前移 ACK Cursor |
| `submit_npc_update_proposal` | 可信 Evaluation 凭证、epoch、状态版本、源证据、proposal ID、可选更新 | 私有 Memory / Belief / Relationship / Goal / Plan 提交或拒绝回执；Action Intent 另走共享 Typed Command |
| `record_npc_observation_disposition` | 稳定处理 ID、Observation IDs、Safe Retention / No-op 或完成回执 | 持久处理证明；不能凭读取/模型返回完成 ACK |
| `coordinate_npc_mode` | 授权 Host、预期 epoch、目标调度状态、任务引用 | CAS 更新持久提交资格；不创建模型 Context、不执行推理 |
| `project_world_event`（内部） | 已提交 Event 与事件时证据、投影版本 | 各观察者独立 Observation / 持久待处理投影 |
| `tick_npc_schedule`（内部） | 游戏时间、NPC 当前活动及日程模板、稳定 trigger ID | 已提交的合法到期活动 / 取消回执 / 重新评估请求 |
| `submit_world_command` | 身份/控制者、命令 ID、版本、操作 | 提交/拒绝回执、World Events、新版本 |
| `submit_check_request` | 合法规则参数、GM 裁决来源、稳定操作 ID | Rule Evaluation + State Machine 最终 Commit Receipt |
| `start_encounter` | `encounter_id`、Actors、Rule Binding、起始坐标 | State Machine 新建并提交的 CombatState、事件或受控拒绝 |
| `submit_combat_intent` | PC/NPC 控制权证明、Actor、Typed Intent、请求 ID | State Machine 的 Commit Receipt + 已提交 Combat/World Events |
| `evaluate_rule`（内部适配器） | 版本化快照、Typed Intent、固定规则数据及 RNG 上下文 | 尚未提交的 RuleEvaluationResult / StateDelta；必须交由 State Machine Commit |
| `save_session` / `resume_session` | Session ID、包版本 | 一致的非活跃战斗世界快照，或活跃战斗不可恢复/待协调的明确拒绝 |

**权限特别说明**：由 Host 注入可信 `controller_id`，不要把用户/LLM 在 JSON 内随意提供的 `controller_id` 当作已认证身份。

## 11. MVP 开发顺序与验收测试

建议先用**原创、可公开分发**的合成 Adventure Fixture 做最小可运行闭环；不要直接把未经授权的 *First Blush* 剧情/图片嵌入公开代码测试。

### Batch SM-1：Package Validator + Session / Scene

- 解析/审核固定包，验证悬空引用、ID、Schema/Ruleset 和初始 Scene。
- 创建独立 Session；Scene 初始化一次，打开的门/移动的 NPC 在重访时保留。
- 采用 Python + SQLite WAL + 短事务持久化非活跃战斗 Session；相同创建 `command_id` 不创建重复 Session。
- **完成证据**：至少两个互不污染的 Session，以及一套 create → enter → mutate → leave → revisit → save → restart → resume 测试。

### Batch SM-2：World Commands + Events / Challenges

- Command 身份、版本、持久去重、允许列表、世界事务。
- 一次性事件链、条件 AST、成功/失败计数、Rule Check Result 的来源校验。
- **完成证据**：重复领奖、旧版本更新、事件循环、未经提交的检定、错误 NPC 权限全部被拒绝且没有额外状态变化。

### Batch SM-3：WorldEvent / Perception / NPC Memory + Agent Integration

- 事件稳定顺序、外显动作与私有 Intent 区分、事件时感知证据、Perception Projection、各 NPC Observation Inbox 与持久 Outbox。
- NPC Profile/Knowledge/Beliefs/Memory 隔离，Observation → Memory Proposal → 版本/来源/权限验证 → 私有记忆保存。
- NPC 按需激活与观察游标、提议与提交分离、非 LLM fallback 边界、有限自动反应深度。
- Host 双模式路由与独占，SM 持久 epoch、NPC Update Proposal / 子操作去重、连续 ACK；新接口均待实现。
- **完成证据**：NPC A 无法读到 B 私有 Intent 或秘密；可见争抢各自形成正确 Observation；相同事件重试不重复投影；无论模型认为谁故意抢钱，都不能修改客观世界事实。

### Batch SM-4：Rule Evaluation Adapter + Unified Atomic Commit

- 受控战斗开启、战前安全 Checkpoint、版本化 CombatState/CharacterState/RNG 快照、RuleEvaluationResult、完整 Delta 原子提交、资源归属、不可续战退出与错误回执。
- 必要外部 Hazard 和 NPC 显式 Combat Intent API 与 Rule Engine 团队联合验收。
- **完成证据**：战斗中每条动作均恰好产生至多一次 State Machine 权威提交；失败、版本冲突或响应异常不产生重复消耗或推进 RNG；不支持的能力明确报告。

**节奏约束**：上述 Batch 是推荐依赖序列，不是 Codex 可以未经审阅连续开发的授权。在每批次完成后根据实际测试和模块接口重新评估下一批；优先减少影响真实端到端场景的缺口。

### 11.1 合成 MVP 验收矩阵

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A01 | 两个 Session 使用同一只读 Package | 世界数据、NPC 记忆相互隔离 |
| SM-A02 | 场景开门→离开→重访 | 门仍打开，不重新初始化 |
| SM-A03 | NPC 从 A Scene 移到 B Scene | 重访 A 不会凭静态 `actor_ids` 复制 NPC |
| SM-A04 | NPC 查询全局秘密 | 不应泄露 `dm_only` 或其他 NPC 的私密事实 |
| SM-A05 | NPC 提议开门/取物 | 校验 Actor 权限与世界条件后才提交 |
| SM-A06 | 同一 Command ID 重试/不同 Payload | 相同请求返回旧回执；冲突请求不执行 |
| SM-A07 | World Version 过期 | 不覆盖新状态，返回版本冲突 |
| SM-A08 | 多事件链与循环 | 合法链执行一次，循环/无限触发被阻断 |
| SM-A09 | Skill Challenge 三次检定成功 | 只累计权威 Result，重复结果不重复计数 |
| SM-A10 | 规则拒绝/故障 | 不伪造机械结果，不能直接修改 HP/Slot |
| SM-A11 | 战斗中多步事务及重试 | PC/NPC 资源归属正确，World/Character/Combat/RNG 一次原子提交，无战后双权威同步 |
| SM-A12 | State Machine 提交后响应丢失 | 按命令 ID 读取本地 Receipt，不能二次扣资源或重掷 |
| SM-A13 | 重载非战斗 Session | Scene/NPC/任务/物品/挑战状态一致 |
| SM-A14 | 关闭插画及视觉模块 | 纯文字端到端流程继续运行 |
| SM-A15 | A、B 同时提交内部取物 Intent，A 优先成功 | 金币只属 A，B 刷新状态；**A 不得从 B 的私有 Intent 读取“争抢”** |
| SM-A16 | A、B 已真实外显伸手并在彼此视线内争抢 | 记录 `action.started` 与裁定结果；双方获得匹配自己视角的 Observation；不以网络抢先宣称敏捷高 |
| SM-A17 | B 背对 A，或 B 不在场 | B 不得获“目击 A 取物”的观察；只可通过后续合法发现/转述知晓 |
| SM-A18 | NPC 收到 Observation 而未激活 LLM | 事件/收件箱持久化，不调用该 NPC 模型；下次激活仍能正确读取 |
| SM-A19 | NPC 将看到 A 取物解释为“故意羞辱” | 可保存带来源的推断 Belief，不得把“故意”写成世界事实/目击内容 |
| SM-A20 | 伪造其它 NPC 的 Observation ID 提交 Memory | 拒绝越权记忆更新；原记忆/已知事实不受污染 |
| SM-A21 | 世界事件重试 / Observation 投影失败后补投递 | WorldEvent、每 NPC Observation、游标和记忆各不重复、不丢失 |
| SM-A22 | NPC A/B 对话相互触发循环 | 有限激活深度/预算；未处理观察保留而非无限唤起 |
| SM-A23 | 非战斗进程重启 | SQLite 中的 NPC 观察/记忆、世界版本、事件与回执无丢失或串 Session |
| SM-A24 | 活跃战斗中途退出后尝试精确恢复 | 明确不支持；仅满足战前重开安全条件时提示可重开，否则阻塞，不重掷已提交操作 |
| SM-A25 | Rule Evaluation accepted 但状态提交失败 | 不改变任何权威状态/RNG，不发布事件；可受控刷新状态后重新求值 |

### v0.3 追加合成验收

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A26 | 战斗中同时支付资源和恢复 HP | 单个 State Machine 事务处理规则 Delta、库存、行动预算和 RNG；不存在 Engine 自己的最终提交 |
| SM-A27 | Rule Engine 求值成功但提交前版本失效 | 不发布未提交机械事件，不推进权威 RNG，重试受控制 |
| SM-A28 | Inactive NPC 获得重大 Observation | 经可靠 Outbox 和 Lightweight Gate 保留溯源，不强制进行长时对话推理 |
| SM-A29 | Inactive NPC 的 Background Evaluation 超时 | 未处理观察与任务可恢复，重复触发不重复修改 Belief / Relationship 或执行行动 |
| SM-A30 | NPC 日程遇到环境前提改变 | State Machine 拒绝失效活动，不错误转移 NPC 或污染世界事件 |
| SM-A31 | DM Narrator 读取玩家视图 | 不可获得 Planner GM Secret，不能擅自叙述未提交的 Rule Evaluation |

### 11.2 v0.4 双模式合成验收（设计目标，尚未执行）

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A32 | Active Interactive NPC 新增 Observation | SM 可靠保存并有序投递；Host 仅追加现有 Context，无逐条 Gate / 额外 Background LLM |
| SM-A33 | Interactive Context 空闲时收到重大事件 | Host 可调度当前 Interactive LLM；模式不因无在途请求而变成 Background |
| SM-A34 | 一响应包含 Dialogue、Belief、Memory、Action Intent | 可选认知更新验证来源/版本；行动统一 Typed Command；提交前不发布世界事实 |
| SM-A35 | Inactive NPC 一次 Background Evaluation 决定移动 | 无 Interactive Agent Context 亦能提出并合法提交行动；临时 Context 释放 |
| SM-A36 | 普通低价值 Observation | Safe Retention / No-op 回执后 ACK，不调用完整 NPC LLM，关键证据保留 |
| SM-A37 | Background → Interactive 与旧 Proposal 提交竞争 | epoch 撤销和提交检查串行；先对账已提交项，拒绝迟到更新/动作，不覆盖新认知 |
| SM-A38 | 模型失败、Observation 重投、DB 版本冲突、提交后 ACK 前崩溃 | 不重复 Memory / 关系 Delta / 行动；未完成前缀不 ACK，读/投影缺口不漏处理 |
| SM-A39 | Memory 成功持久化 | Host 可继续复用 Active Context；无强制 Compaction / Rebuild |

## 12. 决策登记与仍需确认的实现细节

下列 `SM-01`–`SM-03` 是本轮讨论中用户**明确确认**的 MVP 决策；带“待设计/待验证”的内容仅是实施提案，不能由开发 Agent 擅自冻结。

| 编号 | 议题 | 当前决定 / 约束 | 状态 |
|---|---|---|---|
| **SM-01** | 持久化语言与数据库 | Python + SQLite WAL、单进程优先、短事务、强持久化默认、Repository/Adapter 边界 | **已确认** |
| **SM-02** | 战斗中途精确恢复 | **MVP 不支持**，列入 Post-MVP；须有明确安全检查点、不可伪恢复及战后可靠结算 | **已确认** |
| **SM-03** | 多 Agent 共同感知与记忆 | WorldEvent → SM Perception / Reliable Observation → Host Mode Routing → 可选 NPC Evaluation；State Machine 保存和验证 | **已确认基础架构，v0.4 明确双模式** |
| **SM-04** | 统一权威状态 | State Machine 持有并提交 World/Character/Combat/RNG，Rule Engine 只计算 StateDelta；遵守 ADR-001 | **已确认** |
| **SM-05** | 非交互 NPC 状态 | 简单游戏时钟日程；Inactive Lightweight Gate / Background Evaluation 可产生行动；不要求 Interactive Agent 激活或常驻 LLM | **已确认逻辑设计，具体阈值待实验** |
| **SM-06** | NPC Evaluation Mode Exclusivity / 切换 | Host 协调模式与 Context；SM 验证 epoch / 状态版本、持久回执与 ACK；旧 Background 资格撤销后拒绝迟到结果 | **已确认原则；具体协议 Proposed / Not Implemented** |
| S04 | `Session.phase`、Flag、Condition AST 的最终字段 | 与 Package Validator 一起固定最小集合 | 待设计 |
| S05 | `world_version` 与实体版本粒度 | MVP 先 Session 级版本；更高并发时评估细化 | 建议 |
| S06 | NPC/普通怪物是否默认用 LLM 战术 | **不得降低** `MVP_SCOPE.md` 已规定的至少一个敌方 NPC Sub-agent Typed Combat Intent 验收；普通怪物默认策略尚待明确 | 默认策略待决策 |
| S07 | 外部 Hazard 与 NPC 显式战斗入口 | 先核实 Rule Engine 公共 API，缺失则列为 MVP 集成阻塞项 | 技术验证待做 |
| S08 | 记忆筛选、压缩、冲突与预算 | MVP 只需 Episode/Belief/Relationship + 溯源/幂等；高级 Compression/Dedup 后置 | 细节待设计 |
| S09 | 玩家 PC 构建来源 | 优先经审核的一名一级 PC；是否开放全部构建另定 | 待决策 |
| S10 | First Blush 许可与发布 | 未经许可，不公开上传受限制的原剧情与派生数据 | 已明确约束 |
| S11 | 感知何时需要规则检定 | MVP 确定性同场景感知 + 个别经审查 Rule Check；复杂遮挡等后置 | 精确触发待设计 |
| S12 | 同步争夺物品的游戏时序 | 禁止按网络先后来断言敏捷；Host/Engine 裁定条件与公式待冻结 | 待设计 |
| S13 | Observation Outbox/消费回执/投影唯一键 | 必须能防丢、防重复和追溯；具体字段在 `MODULE_CONTRACTS.md` 固定 | 待设计 |
| S14 | 战前 Checkpoint 可重开资格与已提交副作用的保护 | 不承诺所有崩溃都能自动重开，已提交事件不能被静默回滚 | 待技术验证 |

---

## 13. 文档治理与下一步

### v0.4 相对 v0.3 的修订摘要

1. 明确 SM 内部 Perception / Evidence / Observation / Persistent NPC State，与 Host Evaluation / Gate / Context 生命周期分工。
2. Active Interactive 独占主观 LLM 认知和行为；Inactive NPC 经 Gate 安全保留或一次 Background Evaluation，可独立产生行动。
3. 统一 NPC Update Proposal 和 Typed Command 路由，增加模式 epoch、版本重验证、取消/拒绝迟到结果及对账语义。
4. 加强可靠投递、处理回执、幂等和连续 ACK，保持 Memory Persistence / Context Compaction 独立与写事务外推理。
5. 新增八项合成验收目标；保留 ADR-001、DM 隔离、简单日程、Jev 候选与原 MVP 产品边界。


- 此文档只给出 State Machine 运行时架构与状态权威边界；**不替代**项目总架构 `ARCHITECTURE.md`、Agent 内部设计 `AGENT_ARCHITECTURE.md` 或正式跨模块消息契约 `MODULE_CONTRACTS.md`。
- 发现本架构与 `MVP_SCOPE.md` 已确认决定冲突时，以已确认的 MVP Scope 为准，并在审阅中提出修改，不擅自改动产品范围。
- 公开仓库只存放通用 Schema、原创示例和程序代码；完整 First Blush 内容、地图与实质性转写继续留在合法权限下的本地私有资料中。
- **文档优先级**：ADR-001 是权威架构决策；旧 MVP Scope 的双权威用语为历史遗留，已在 v0.5 修正。

**下一步建议**：审阅 `AGENT_ARCHITECTURE.md` v0.4 与 `MODULE_CONTRACTS.md` v0.2 / Draft 的模式、Proposal / ACK 契约，再验证最小接口与故障场景；不将目标设计视为已完成实现。总体架构审阅后再整理根目录 `README.md`。

**本阶段最重要的完成标准不是“状态模型有多少类”，而是一个 Session 能在不重复执行规则、不泄漏 NPC 秘密、不重置场景的前提下，可靠地从剧本初态走到已持久化的结局。**
