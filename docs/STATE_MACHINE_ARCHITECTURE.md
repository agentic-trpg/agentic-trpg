# Agentic TRPG — State Machine Architecture（MVP）

> **状态**：Draft v0.9（依据 ADR-001 与统一 TypedCommand / AP-15 决策；具体消息 Schema 与实现仍待审阅）
>
> **日期**：2026-10-10
>
> **建议位置**：`agentic-trpg/agentic-trpg/docs/STATE_MACHINE_ARCHITECTURE.md`
>
> **依赖**：[`ADR-001-UNIFIED-STATE-OWNERSHIP.md`](./ADR-001-UNIFIED-STATE-OWNERSHIP.md)；[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.11；[`ADVENTURE_PACKAGE_SCHEMA.md`](./ADVENTURE_PACKAGE_SCHEMA.md) Draft v0.5；[`AGENT_ARCHITECTURE.md`](./AGENT_ARCHITECTURE.md) v0.8；[`MODULE_CONTRACTS.md`](./MODULE_CONTRACTS.md) v0.7 / Draft
>
> **目标场景**：一位玩家、一个 PC、文字优先、人工整理的单人冒险包；Agent DM 和按需 NPC Sub-agent；不要求可视化引擎、World Creation Agent、多玩家或开放世界模拟。
>
> **证据边界**：本文件是基于已讨论范围和冒险需求的**设计建议**，不是现有 State Machine 代码的完成状态。与 Rule Engine 的 API 适配以实际实现和独立测试为准。

## 1. 目标、边界和核心术语

State Machine 是**一次具体游戏 Session 的游戏领域逻辑管理者、唯一权威运行状态拥有者和最终提交者**，不是剧本生成器、规则引擎或 NPC 对话模型。

它承担六件事：

1. 加载并验证**不可变** Adventure Package；为一次 Session 实例化初始状态。
2. 记录玩家和 NPC 的行动在世界中造成了哪些**已验证、已提交**的变化。
3. 为 Agent DM / NPC Sub-agent 提供**按角色权限过滤**的上下文视图。
4. 将需要机械裁决的动作交给无权威可变状态的 Rule Engine 求值，验证其未提交的 `StateDelta`，再在自身事务中统一提交 World / Character / Combat State、RNG、事件和回执。
5. 使用 Python + SQLite（WAL）持久保存 Session 的全部已提交运行态；MVP 产品仅保证非战斗状态下的安全续玩，不要求恢复进行中的战斗，防止重访重置、事件重复执行、重试重复付款和知识泄漏。
6. 管理 NPC Identity / Memory / Belief / Relationship / Goal / Plan、Perception / Observation / Evidence、Evaluation Task 创建与授权、模式协调元数据、Gate 领域策略、游戏时钟与 Schedule、Proposal / Action Intent 验证、内部 Processing Completion、幂等和持久恢复；Host 仅执行模型与 Context 运行。

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
- 不管理 System Prompt、物理 LLM Context / KV Cache，不执行 LLM 主观推理；这些由 Host 运行时和 NPC LLM 承担。
- 不生成叙事文本和插画，不做实时地图、Token、动画。
- 不执行任意剧本脚本、不建立通用游戏编程语言；只支持已经审核的有限条件与效果。

## 2. 总体运行架构

```text
Human Player / DM Planner -> State Machine domain request / authorization
   SM owns World / Character / Combat / RNG / Persistent NPC State
   SM Perception / Evidence -> reliable Observation
   SM Gate / Schedule / Mode coordinator -> authorized Evaluation Task
                                  |
                         NPCEvaluationRequest
                                  v
                         Agent Host LLM Runtime
                |- Interactive Context / current Interactive LLM
                '- Inactive Background Task / one-shot Context / NPC LLM
                                  |
                        NPCEvaluationResult (data)
                                  |
                     Host submits evaluation_id + Result
                                  v
                      State Machine atomic Meta / sole Result / EVA completion
                |- reliable Dialogue / Action Intent handoff
                '- independent command_id -> Rule Engine -> SM Commit
                                  |
                    EvaluationReceipt / cognitive completion + reliable handoff
                    committed WorldEvent -> Perception
                    player-visible receipts -> DM Narrator -> Text UI
```

统一逻辑信息流是 **State Machine → Agent Host → NPC LLM → State Machine**，不要求微服务或多个数据库。SM 是游戏领域逻辑与权威状态管理者，创建/批准任务、管理 Gate 领域政策和游戏时钟日程，但不执行 LLM 主观推理、不管理 Prompt / 物理 Context / KV Cache。Host 仅做模型运行、Context、预算、重试取消、Tool 适配传输及运行时可观测性；不持久管理游戏状态或任务完成结果。

DM Planner / Narrator 的角色、Context 和权限隔离，允许共享底层模型；Planner 提出主持方案，Narrator 只呈现玩家可见已提交结果。NPC 私有主观认知由对应 NPC LLM 完成。MVP 为 Python + SQLite WAL；Jev 为可替换候选。Engine `_LiveCombat` 是迁移前基线，不能成为另一权威存储。

## 3. 运行时数据模型与状态所有权

依据 ADR-001，CharacterState、CombatState、RNGState 及其版本与 WorldState 在同一权威提交域内；Rule Engine 输入是经验证的只读状态快照，输出只是待提交结果。

建议把 Session 存储划分为少量聚合（aggregate）；下面是**概念数据结构**，不是已经冻结的 JSON/Python Schema。

### 3.1 `SessionRecord`：一次冒险实例

| 字段（建议） | 说明 |
|---|---|
| `session_id` | 稳定、唯一、与其他 Session 隔离 |
| `adventure_id`, `package_version`, `package_digest` | 固定加载的冒险定义版本；重载时校验，禁止静默升级 |
| `ruleset_binding` | 固定 ruleset_id / data_revision / evaluator_version；数据修订区分生效规则及适用 Homebrew，Engine 求值前验证匹配 |
| `players[]` / `pc_actor_id` | 可信认证主体核验的 player_id / pc_template_id / Actor 控制关联；MVP 严格一玩家一 PC，具体存储字段 [PROPOSED; NOT IMPLEMENTED] |
| `current_scene_id`, `current_location_id` | 当前所在场景、地点 |
| `phase` | `exploration` / `combat` / `challenge` / `completed` 等有限阶段（候选） |
| `world_version` | 世界/机械状态变更提交时单调推进，与事件序号不同；仅事件/元数据提交的推进规则 [OPEN] |
| `last_world_event_seq` | 本 Session 已提交事件的稳定全序序号，观察记录据此引用及排序 |
| `last_safe_checkpoint_id` | 最近可核验的非战斗安全恢复点；不意味着活跃战斗可精确恢复 |
| `status` | `active`、`combat_unrestorable`、`completed`、`blocked_reconciliation` 等（候选） |
| `active_combat_ref` | 指向本 Session 的 SM 权威 CombatState，不依赖 Engine 私有 Handle 保存战斗真相 |
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
2. 若本 Session **从未实例化该场景**，应用 `initial_state` 一次，生成对象实例和局部标记；NPC 按 Session 级身份查找，必要时首次创建，不能复制或覆盖已有位置、Memory、Belief、资源。
3. 若已实例化，则保留现有实例状态；**绝不因为重访重放初始掉落、NPC 位置或机关状态**。
4. 按权威状态记录 `scene.entered`，其触发的事件走统一事件审核与提交路径。

注意：静态 `actor_ids[]` 只提供初始在场信息；世界 Actor 的当前位置由运行态单点保存。不能因为玩家重访让已经离开的 NPC 重新出现。

### 3.4 `ActorRuntime` / `NPCState`

- 所有 Actor：稳定身份、当前世界位置、归属、世界层可见状态、可用控制策略。
- 玩家 PC：从 Package 内置的一个或多个完整、只读 PC Templates 中选择一名，经规则验证机械属性后初始化 CharacterState；HP、资源、成长等运行态由 SM 保存。无需独立构建服务或外部 pc_build_ref；未来外部导入 [OPEN]，不实现。
- NPC：唯一 Persistent Identity、Personality、Memory、Belief（允许错误）、Relationship、Goal、Plan 和 Runtime State（Schedule / Current Activity 等）；私有知识、处理游标与控制权一并权威保存，观察收件箱与认知更新分开。
- 敌人/普通怪物：与重要 NPC 一样有身份和状态，但是否调用 LLM 要由策略决定；不要求为每一个普通怪物常驻创建 Agent。

**三个独立命题**：`world_fact_is_true`、`npc_knows_fact`、`npc_believes_fact`。允许 NPC 有错误信念和撒谎，但禁止把信念自动提交为世界事实。

Interactive / Background 是 **LLM Evaluation Mode**，不是两个人格或两份 NPCState。State Machine 管当前模式、Evaluation Task / Status、NPCStateVersion 及内部完成状态；Agent Host 仅管理非权威 Context 与模型运行，不能从 Context 内容反向覆盖权威状态。

### 3.4a `CharacterState`、`CombatState` 与 RNG（统一权威）

State Machine 为每名 Actor 保存 HP/Temp HP、法术位、有限使用次数、装备、Condition、持续效果；活跃 Encounter 持有 Initiative/Turn、行动经济、位置、Concentration、反应窗口、Pending Choice 以及所需技能/规则生命周期账本。SM 另存权威 RNG 流状态/版本，以独立 RNGContext 提供给 Engine。只存储明确规定的权威数据，不复制可由规则确定性计算的派生字段作为第二权威。

同一角色在战斗内外共享角色资源的最终所有权：喝药、开门、取物、移动等跨界动作最终由**同一个 State Machine 事务**提交；Rule Engine 负责计算机械结果。StateSnapshot 采用 CombatSnapshot / NonCombatSnapshot 两种 Schema，共享 CharacterState / EffectState 等基础结构；相关实体范围可限定，但每个实体机械字段及规则依赖必须完整，不按 Intent 裁剪，使用标准 Required / Optional 校验。RulesetBinding 从 Session 固定配置提供，RNGContext 独立于 Snapshot（详见 MODULE_CONTRACTS.md §4）。Rule Engine 内部临时缓存及执行对象不是可持久化权威。

### 3.5 `ChallengeInstance`：非战斗技能挑战

针对撤退、追逐或跨多次检定的任务，建议记录：`challenge_id`、`scene_id`、`successes`、`failures`、`required_successes`、`status`、`resolved_check_ids`。每次检定的 DC/能力/结果由合法规则或显式 GM 裁决产生，**State Machine 仅累计已提交 Result**。

不要把非战斗技能挑战实现为伪造的 Combat；若失败伴随伤害/Condition，需要 State Machine 授权的受控 Hazard / Rule Engine 求值接口，缺失时明确阻塞该场景而不是直接写入 HP。

### 3.6 `WorldEvent`、感知证据与顺序

`WorldEvent` 是**已提交的、不可变的世界事件记录**，最小概念字段：`session_id`、`event_id`、`event_seq`、`event_type`、`source_command_id`、`actor_id`、`object_ids`、`scene_id`、`occurred_at_game_time`、`payload`、`visibility_class`、`perception_evidence_ref`。字段为候选，不代表现有实现。

- `event_seq` 由 Session 中的权威提交顺序分配，单调递增；它是**记录顺序**，不自动证明角色的生理反应速度。
- `WorldEvent` 应记载必要的**发生时刻证据**（行动时地点、参与者位置、光照/可听性、遮挡/秘密等级、相关动作是否外显）。不能在 NPC 数分钟后苏醒时用**当前**视野倒推此前谁看到了什么。
- 可见动作的开始与成功/失败结果是不同的事实；只有实际外显的 `action.started`（候选事件）才允许投影给旁观者。私有 Intent、未执行命令、LLM 私下计划不得伪造为外显动作。
- Rule Engine 产生的拟议机械事件只有在 State Machine 原子提交对应 Delta 后才成为权威 WorldEvent/CombatEvent；未提交的求值结果不得触发永久世界事件或 NPC 观察。

### 3.7 `ObservationRecord`：角色实际收到的观察

建议字段：`observation_id`、`session_id`、`observer_actor_id`、`source_event_id` / `source_event_seq`、`observed_at_game_time`、`perception_kind`（如 sight/hearing/self_action/report）、`observed_payload`、`visibility_basis` / `rule_check_command_id`（若适用，与 session_id 查询 CommandReceipt）、`projection_version`、`delivery_status`。每项 Observation 必须标明**观察者**和**来源**，不能在投影中包含事件对该观察者不可知的隐藏字段。

- MVP 只需同场景、简单视觉/听觉、人物在场状态、明显动作与自我行动结果。遮挡、幻术、远距离声音、误认等高级机制后置；若重要剧情要求检定，不得凭普通同场景规则绕过 Rule Engine。
- 观察投影是确定性、可去重的映射；`(observer_actor_id, source_event_id, projection_kind)` 等候选唯一键防止重试生成重复观察。结果按 `source_event_seq` 有序读取。
- 优先在世界提交事务中一次性落库已确定的观察；若投影较复杂，必须以**持久 Outbox + 事件时证据**处理，并使用幂等投影，避免提交成功但观察永久丢失。
- `ObservationRecord` 是证据而非角色长期记忆。一个 NPC 可以暂时不理解、不在意甚至忘记某个观察，但不能因此篡改原始事件与感知来源。
- 稳定 `observation_id` 与按 NPC 的有序 Delivery Cursor 支持至少一次投递；读取分页位置、Host Context 已追加位置与 SM 内部 Processing / Completed Cursor 分开。完成游标只推进连续已完成前缀，必须以投影完成水位/等价机制防止跳过尚未投影的早期事件；具体字段见 `MODULE_CONTRACTS.md` §7、§9（Proposed / Not Implemented）。

### 3.8 NPC Meta、Episodic Memory 与 Belief History

Memory、Belief、Relationship、Goal、Plan 是同一 NPC 的权威认知状态，作为一个原子更新单元。SM 保留稳定 NPC / 记录 ID、来源 Observation / Memory 引用、epistemic_status（observed / inferred / told）、confidence（如适用）、evaluation_id、NPCStateVersion 与内容版本；承诺回忆引用已确认 Commitment。具体类型/约束为 Proposed / Not Implemented。

Initial Belief 与运行时 Belief 使用兼容结构。同一稳定 Belief 追加新版本，保留来源、版本、当前有效状态及完整旧历史，不直接覆盖/删除；NPC LLM 可修改、降低置信度或放弃旧 Belief，SM 不替它改写文本。

SM 仅确定性验证 Schema/类型、身份权限、Observation / Memory 引用、任务状态/版本、允许字段、幂等与数据库约束。Memory / Belief / Relationship / Goal / Plan 整批合法才在一 SQLite 事务提交；一项非法整批不写，返回结构化错误供同一有效 EVA 有限修正，不能出现 Goal 未写而依赖的 Plan 已写。

**SM 不做自然语言语义验证**：引用合法不证明 Memory 忠实，允许错误主观 Belief，但不改变 World Fact；不增加 Semantic Validator LLM。避免把未执行动作记为已发生是 NPC 输出要求，SM 只能核验结构化来源，不能宣称能判断文本真实性。原始证据、已确认承诺与确定性安全处理仍不等待 LLM。

MVP 向 Host 提供该 NPC 完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan 与新 Observation。Host 只组装 Context，不做语义筛选 / Semantic Retrieval / Memory Ranking / 智能压缩，不增加独立 Memory Agent。已有 Interactive Context 可复用，后续增量追加已提交变化，不要求每 EVA 重注入全量 Meta；完整授权不等于泄漏他人秘密或全量世界。

### 3.9 NPCEvaluationTask 与 ObservationProcessingStatus

SM 持久 Task 关联 evaluation_id、Session/NPC、Evaluation Mode、授权范围、NPCStateVersion、Observation / observation_work_id、玩家输入、EvaluationStatus、最多一份最终 Result / 指纹、Meta 提交与必要输出交接。候选状态 authorized / running / failed / completed / cancelled 的具体编码待评审；仅有效/运行任务可选新 Result，调用者不能自行恢复失败/取消任务资格。

Evaluation ID 是 Meta 幂等键而非认证凭证；提交接口只有 evaluation_id + NPCEvaluationResult，SM 从 Task 恢复可信关联，运行环境提供调用身份。首次合法 Result 在**同一 SQLite 事务**重验任务有效性/认知版本、选定结果、整批提交 Meta、记录可靠输出交接和 completed。相同 Result 重试返回原 EvaluationReceipt，已选定后不同 Result 拒绝；选定前非法输出允许当前有效任务有界修正。

两模式统一七字段 NPCEvaluationResult：dialogue、memory_updates、belief_updates、relationship_updates、goal_updates、plan_updates、action_intents，均可为空。EVA 是认知与决策评估；Action Execution 独立使用稳定 command_id / Typed Command / Command Receipt，不以 Evaluation ID 替代行动幂等。

Host 管 invocation_id / context_id，一 EVA 可多 Invocation，一 Interactive Context 可多 EVA，非提交必填。SM 保留当前 interactive / inactive 状态，不需要模式代次计数器；切换原子撤销旧有效 EVA、移交未完成 Work 并创建新 EVA，不等待旧失败反馈，迟到旧结果拒绝。

ObservationProcessingStatus 根据必要认知处理与可靠输出交接维护。EVA 完成不等行动执行成功；Command 失败/等待 choice 独立跟踪，不自动重开已完成认知。读取、追加、模型返回、取消/失败本身不等于观察完成。新接口/状态模型均 Proposed / Not Implemented。

同一 NPC 的有效认知 EVA 由 SM 串行授权/提交；模式切换的取消与新任务授权原子完成。旧物理 Invocation 未结束不影响新 Task，但旧任务无提交资格；一个 Interactive Context 可依次复用多个 EVA。

## 4. Session 生命周期与场景流程

以下为 [DECIDED] 职责与流程；接口/字段 [PROPOSED; NOT IMPLEMENTED]，不是新增运行时状态：

- **Package Loading / Validation**：统一 load_adventure_package 内部执行安全解析、Schema、引用、规则绑定、声明式操作与必要元数据检查，返回 valid / invalid 和结构化 errors / warnings；不暴露半验证包或独立验证服务。必要机制不支持、非法引用、Schema 错误阻止批准；可选非核心限制明确报告，不假装支持。静态验证不证明可玩性/平衡，来源元数据不证明版权合法。
- **Session Creation**：CreateSessionRequest 使用 players[]（player_id / pc_template_id，MVP 严格一项），SM 从可信认证环境取得 principal_id 并验证控制关系，不接受 LLM 自报身份。创建前以 (principal_id, command_id) + Fingerprint 持久幂等，相同请求返回原 Session，不同内容拒绝。短事务原子初始化 SessionRecord、WorldState、当前必要 Actor/NPC Persistent State、选定 CharacterState、入口 Scene、RNG 及创建幂等结果，固定 adventure_id / package_version / package_digest / 生效 RulesetBinding；失败无半初始化有效 Session。session_id 由 SM 生成，返回 ID、创建结果与有限元数据，不泄漏隐藏世界，不新增创建请求/Receipt ID。普通命令仍用 (session_id, command_id)；详见 Adventure Package §9.1a。
- **Session Interaction**：按当前 Phase 验证命令，读取所需世界视图，选择世界事务或规则执行；根据已提交结果推进世界与事件、计算 Observation；NPC 记忆解释独立于世界状态提交。
- **Save / Resume / Complete**：持久化运行态与 NPC 观察/记忆；重启后恢复**非活跃战斗** Session；活跃战斗不可声称精确恢复，完成后保留最终事实和回执。

允许自由探索和合法的旁路，不建立不可跳过的硬编码场景序列。Scene Graph 只是可达性与条件定义；剧情是否推进由已提交的事实和事件决定。

## 5. Command → Result → World Event 的执行协议

### 5.1 统一 submit_command 与命令信封（概念字段）

```yaml
schema_version: module-contracts/0.2
command_id: cmd.demo.0007
session_id: session.demo.01
actor_id: npc.gate_warden
principal_id: npc-agent:gate_warden   # 可信认证上下文绑定
expected_world_version: 12
command_type: world.operate_object
payload:
  object_id: object.iron_gate
  operation: open
```

这是**原创合成示例 [PROPOSED; NOT IMPLEMENTED]**；普通游戏命令统一公开入口 submit_command(TypedCommand)，内部按 command_type 分派 world.* / rules.* / combat.*，信封及强类型 payload 以 MODULE_CONTRACTS.md §3 为准，不另起一套命名。principal_id 来自可信认证环境；actor_id 按操作类型校验，Actor 行动必填真实 Actor，受信系统/世界事件操作可以没有行动 Actor，但须验证 principal、机械来源和目标（AP-15）。source_ref / 来源权限与具体联合字段 [PROPOSED / OPEN]，不能全局无约束可空。create_session、NPC Evaluation、查询/回执仍为独立生命周期。NPC controller.kind 保留控制策略语义。

### 5.2 内部分派与三个验证领域

| 分支 | 输入 | 权威执行 | 成功后的 State Machine 工作 |
|---|---|---|---|
| **世界操作** | 开门、取物、NPC 位置转移、设旗标 | State Machine 验证条件、权限并提交 | 记录一次世界事件，更新物体/Quest/Scene |
| **规则操作** | Ability Check、Save、Combat Intent、受控 Hazard | Rule Engine 进行无副作用求值；State Machine 统一提交 | 验证待提交 Delta，原子写入角色/战斗/世界状态、RNG、事件和回执 |
| **纯对话** | `NPCEvaluationResult.dialogue` | NPC 提议，经 SM 验证发布权限后成为可呈现内容 | 只有有明确语义的承诺/线索公开/关系变化才持久化；普通一句对话不产生机械效果 |
| **场景转移** | 进入已定义出口、传送剧情事件 | State Machine 的场景与权限判断，必要时 Rule Engine | 更新位置并记录 enter/exit；不重置旧场景 |
| **声明式事件** | 经审查 EventDefinition 与已提交事件/权威条件 | State Machine 内部受限声明式处理 | 执行允许列表的世界效果，一次性/按规定次数去重，不运行脚本 |

**[DECIDED]** 上表普通游戏操作是 submit_command 的内部处理路径，不是独立公开提交 API；纯对话仍沿用独立 NPC Evaluation / 发布生命周期。DM Planner 负责情境语义和 GM 裁决，SM 负责世界事实、身份权限、结构/引用/版本与提交不变量，Rule Engine 负责 D&D 机械合法性与计算。Planner 可基于完整授权 GM View 提出检定、能力/技能、DC 和成功/失败后果，优先使用规则或 Package 的规定；未规定时在掷骰前确定并留下可追溯依据。裁决复用 TypedCommand，不新增 Adjudication API / 语义审核 LLM；SM 只验证可确定性检查的内容，不重算规则，Planner 不提交骰点/伤害或替 NPC 决定私人意图。

Planner 可通过有限 Typed World Operations 提出简单 Object / World Fact / Scene Connection；已有 ID 从可信 GM View 引用，新身份由 SM 分配，正式提交后进入 Runtime World State 和后续授权 get_scene_view 等查询，不修改静态 Package。叙事/提议不是事实，不采信 LLM 自报引用或状态变化。操作封闭且字段受限，禁止任意 Patch、SQL、脚本或整份状态覆盖；完整字段及复杂 Scene/战斗地形生成 [OPEN]，详见 MODULE_CONTRACTS.md §3.3。

### 5.3 世界事务（同一数据库/进程内）

候选最小步骤：

1. 按 `(session_id, command_id)` 查询历史完成回执；同键相同内容返回原结果，**同键不同内容拒绝冲突**。
2. 验证 expected_world_version、可信 principal 权限、适用分支的真实 Actor 控制权或受信机械来源/目标、当前 Phase、可见/可用对象与事件条件。
3. 对需要机械规则的操作，先在**写事务外**调用 Rule Engine 求值得到 `accepted` / `rejected` / `needs_choice` / `unsupported`，并持有返回的预期版本和 RNG 转换；进入短事务后再次验证身份、版本及 Delta 不变量，再将全部 World / Character / Combat / RNG Delta、Events、Receipt 和去重键一并提交。世界操作可直接生成待提交 Delta。
4. **事务提交完成后**才返回 `committed` 并允许 Agent DM 将其叙述为事实；失败/冲突不写任何部分 Delta。

请求 payload 应使用稳定序列化计算指纹，以区分重复提交和同一 `command_id` 下的不同请求。MVP 使用单个本地 SQLite 数据库的原子事务，不引入分布式事务协调器。

**性能与锁纪律（SM-01 已确认）**：Agent 推理、远程/本地 LLM 调用、需要等待的 Rule Engine 调用必须在 SQLite **写事务之外**。读取版本和生成提议后，在短写事务内重新验证 `world_version` 与操作条件，再原子提交 State Delta + World Events + Command Receipt + 去重记录 + 可即时生成的 Observation/Outbox。SQLite WAL 允许并发读，但写事务仍需串行；Session 内逻辑命令协调不等于 SQLite 自带游戏顺序。

### 5.4 单一提交者协议：Rule Evaluation ≠ Commit

**目标语义由 ADR-001 固定。** Rule Engine 不拥有独立的权威可变 Combat；调用 `evaluate(RuleEvaluationRequest)`（含 session_id / command_id / actor_id / operation_kind、强类型 payload、完整 Snapshot、Session 固定 RulesetBinding 与独立 RNGContext） 返回的 `RuleEvaluationResult` **尚未提交**。`accepted` 只是求值完成；只有 State Machine 的 `CommandReceipt.status=committed` 才代表世界已变更。

```text
Load State Snapshot + version + RNG position
  -> Rule Engine evaluate（不得提交）
  -> accepted / rejected / needs_choice / unsupported
  -> State Machine begin short transaction
  -> Validate read set, versions, authorization, delta invariants, idempotency
  -> Apply typed StateDelta + RNG + authoritative Events + CommandReceipt + Outbox
  -> Commit SQLite transaction
  -> Return immutable CommandReceipt / publish perceptions / Narrator output
```

**核心约束**：

- 不能在 SQLite 写事务中等待 LLM、Rule Engine 或远程调用；提交前重新验证输入版本/关联读集；冲突时废弃未提交规则结果并刷新授权视图；原样重试用原 command_id，修改 expected_world_version 等命令内容须新 ID，未提交不推进权威 RNG。
- State Machine 持有权威 RNG 状态或流位置；求值使用独立的显式 RNGContext；accepted 返回 RNGTransition，无随机消耗时状态可不变，draws 仅可选审计辅助；未提交请求、规则拒绝、版本冲突均不得推进权威 RNG。重试遵守幂等回执，不得双掷骰或重复付款。
- Accepted Delta 使用封闭 Typed Operation Union，覆盖 HP/资源/库存/位置/回合/行动经济/Condition/Effect/Concentration/Reaction/Limited Uses 等全部连带变化；允许受限类型化复杂组件操作，禁止任意路径/JSON Patch/整份 Snapshot 覆盖。StateDelta、RNG、正式事件、CommandReceipt、Outbox 同事务提交，SM 不根据 ProposedEvents 重算伤害/HP。
- Engine 的 ProposedEvents 无权威 event_id / event_seq；SM 同事务分配并持久化，提交后才向 NPC / Narrator / UI 发布授权投影。仅事件提交的 World Version 推进、完整 Effect/Reaction Delta 字段及复杂中途 Continuation 仍 [OPEN]。
- `needs_choice` 必须返回可标识、版本绑定的待续裁决状态，不得把未完成动作误写为结果；取消、超时及失效必须明确处理。复杂 Reaction Chain 可能需要可验证的短事务级分段及安全 PendingChoice 状态，实际协议在 Module Contracts 冻结。
- 旧 `_LiveCombat`、`CombatHandle` 和 Bridge 进程内回执属于迁移前代码，不是可继续采用的双权威设计；迁移可以有短期兼容适配，但同一实际 Session 不得出现两个最终状态持有者。
- Perception 只消费 State Machine 的**已提交**事件及其事件时感知证据；Narrator 不得把规则求值结果当作已发生事实。

本节是**目标接口语义**，并非现有 Rule Engine 已具备无状态 evaluate API 的声明。

### 5.5 声明式事件、作用域与链式效果

- Package 的 EventDefinition 只定义 Trigger / Condition / Effect / 重复政策，区别于 SM 生成的 CommittedWorldEvent。SM 加载并按 Session / Scene 等作用域管理定义，根据已提交事件与权威状态判断条件、执行允许世界效果、持久保存触发历史；不增加 Event Engine 服务，禁止 eval / 任意脚本或 LLM 文本直接写状态。
- Event Condition 沿用封闭词汇（all / any / not / flag_equals / actor_present / event_once / challenge_count_at_least 等）；set_flag / set_object_state 等世界效果由 SM 处理，机械计算必须交 Rule Engine。实际事件可由受控动态命令产生，不要求全部预定义在 Package。
- Planner 的受限 Conditional World Effect Proposal 也复用上述 Condition / Effect 语义，不建立第二套 Event Engine。尽可能在掷骰前确认操作、成功条件与后果可表达/受支持；SM 用可信规则结果与权威世界状态判断条件，不信任 LLM 自报成功。具体封装/结果关联 [OPEN]，见 MODULE_CONTRACTS.md §3.4。
- 同一命令提交前可完整求值的世界/机械效果，按 §5.3 原子提交全部 Delta / RNG / 正式事件 / CommandReceipt / 触发历史 / Outbox。未提交 ProposedEvents 不能冒充已提交触发来源。
- 若 WorldEvent 已提交后才触发机械效果，保留先前事实，可靠保存触发历史和后续命令交接，使用独立稳定 command_id 求值与提交；触发消费标记与命令交接同事务，重复投递/崩溃重试不遗失或重复伤害/领奖/已提交骰点。不能声称两个已提交事务原子，也不能因后续失败回滚先前事实。
- 按 event_definition_id、Session / Scene 作用域和重复政策去重，并关联 trigger_event_id / 后续命令键。发现循环可拒绝当前尚未提交命令或停止后续推进，不回滚已提交来源事件。具体索引、复杂 Effect 编排和循环预算仍 [OPEN]。
- 已提交事件只按事件时证据对各 NPC 投影，Observation / Outbox 必须可靠；需要规则检定时在写事务外协调，不持有写锁等待模型或 Engine。

### 5.6 并发取物与竞争动作：提交顺序不是敏捷判定

原创测试情境：金币 `coin.001` 在桌上，NPC A 与 B 都想取走。

1. A、B 基于相同 `world_version=12` 可以各自提交私有 `take_item` Intent。**仅提交 Intent 不意味着角色身体已移动**。
2. 如果是普通依次处理的非竞争命令，A 的取物先有效提交，物品归 A；B 的旧版本请求收到冲突并刷新世界视图。B 若在现场且能够看到 A 的动作，应收到对应 Observation。此时 A 只知道自己拿到金币，**不得**得知 B 的未外显意图。
3. 如果 State Machine 已根据游戏规则/GM 语义裁决确认进入“同步争抢”场景，应先生成可信的外显 `action.started`（仅在确实发生时），以公开的确定性顺序政策或 Rule Engine 执行需要的竞争检定，确定结果。不得按 API 到达先后编造“角色 A 更敏捷”。
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

SM 先可靠保存 Perception / Evidence / Inbox，再创建授权 Task；Host 只执行模型运行：

```text
SM committed event -> reliable Observation / Work
   |- Interactive active (including idle): SM Interactive EVA
   |    -> Host ordered append -> current Interactive LLM
   '- Inactive: SM Gate policy
        |- Safe Retention / No-op -> SM disposition
        '- SM Background EVA -> Host one-shot Context -> NPC LLM -> release
   -> submit_npc_evaluation_result(evaluation_id, result)
   -> SM whole-Meta deterministic validation
   -> same SQLite transaction: Task validity / NPCStateVersion check,
      sole Result + atomic Meta + reliable output handoff + EVA completed
   -> separate Typed Command / Rule Evaluation / SM Commit / Command Receipt
```

Interactive 活跃期间，所有 LLM 主观 Memory / Belief / Relationship / Goal / Plan 与自主决策交当前 Interactive LLM，包括模型空闲期间；不另开 Gate / Background / Memory / Cognition LLM。SM 可因重大事件授权下一次 EVA，Host 排队执行，新输入不修改运行中请求/KV Cache。

Inactive Gate 的触发、保留政策、分类采用和任务结果由 SM 管理；可选轻量模型由 Host 推理、SM 采用候选。Gate 不替 EVA 语义筛选完整授权 Meta、不生成 NPC 主观 Belief。durable / short_term / discard 仍仅安全保留候选，不删除关键证据、未完成投影/任务或权威事件；不确定或失败时保守保留。

Background 使用完整授权 NPC Meta 与新观察，可有独立 Prompt / 模型 / Builder，返回同一/兼容七字段 Result，可全空或独立提出行动；一次性 Context 不创建/恢复/激活 Interactive Agent。SM 不执行主观推理，也不判断自然语言 Memory 忠实性，所有模型调用在写事务外。

### 6.4 Action Intent、日程与模式切换

Interactive / Background EVA 及已审核 Schedule / Policy 可提出 Action Intent，实际执行共用 Actor 授权 → Typed Command → 必要 Rule Evaluation → SM Commit，非机械操作沿用 §5.2。EVA 不执行动作；Meta 合法整批提交，Action Intent 非法单独拒绝、不回滚 Meta，合法意图独立交接和执行。command_id 独立稳定、派发重试复用；Command Receipt 与 EvaluationReceipt 分开。

SM 管游戏时钟、日程、Trigger / 活动版本 / 到期时间 / 完成取消回执，重验存活、失能、地点和环境前提，控制领域防循环；Host 只管调用资源预算与模型队列。确定性安全暂停不等于 NPC 已形成新主观计划，Jev 仍非强制依赖。

**Mode Switching（Proposed / Not Implemented）不等待旧 EVA**：Background → Interactive，SM 在短 SQLite 事务撤销旧有效任务资格、保留已提交 Meta、移交未完成 Work、更新 interactive 状态并创建新 Evaluation ID。新 Interactive LLM 获最新完整授权 Meta、未完成 Observation 与当前玩家输入；Host 尽力取消旧 Invocation，不等待旧调用结束、失败回执或 ACK，SM 拒绝取消任务的迟到结果。若旧结果先提交，则保留原 Meta 和可靠交接，不重做。

Interactive → Inactive 同样原子撤销旧有效任务、保留认知与未完成 Work、更新当前状态后按需创建 Background EVA。已交接 Command 的资格/取消由独立 Command 流程管理，不能因 EVA 切换回滚已提交动作。任务有效性和 Meta 提交必须在同一事务核验，不依赖 Host 内存状态；版本冲突/恢复由 SM 决定有效任务与最新输入，不允许调用方复活旧任务。

### 6.4a EVA Completion、Observation 与独立 Command

- SM 在完成事务内记录唯一 Result、整批 Meta 与 Dialogue / Action Intent 的可靠交接或明确拒绝/no-op，返回必要结构化 EvaluationReceipt；全空 Result 也可完成。
- ObservationProcessingStatus 根据必要认知处理与可靠交接维护；内部 Completed Cursor 不越过认知/交接缺口或未完成投影，不要求 Host 独立 ACK。读、追加 Context、模型返回、失败/取消本身不等于完成。
- **EVA 完成不等待 Action Execution 成功**。稳定 command_id 与持久交接防止遗漏/重复派发；Command 的失败、needs_choice 或未执行项继续以独立 Command Receipt / PendingOperation 跟踪，不阻塞已经完成且可靠交接的 EVA / Observation。
- 动作失败反馈可交现有 Interactive LLM 做动作交互，不自动重做完整 EVA / 重写 Meta；确需认知评估时由 SM 显式授权新任务。
- 单次 Invocation Timeout / API Error / Schema / Meta 验证失败不立即终止 EVA：任务有效且预算未耗尽保持 running，以同 evaluation_id / 新 invocation_id 有界修正，不选最终 Result、不写半批认知；只有耗尽或明确无法继续才最终 failed 并保留未完成观察，模式切换为 cancelled。提交响应丢失按 evaluation_id 查持久结果，行动响应丢失按 command_id 查独立回执。
- SM 不承担自然语言语义验证，不自动修改 Belief，不新增 Semantic Validator LLM。Memory Persistence 与 Context 资源管理独立；MVP 只预算保护、释放/完整 Meta 重建，不增加语义筛选或智能压缩。

### 6.5 对话承诺、知识传播及故障

- NPC 对话可包含谎言、猜测、转述或修辞；话语事实不等于内容是真实世界事实。可观察的已发布话语可以形成 `speech` 类型世界事件，并投影给合适的听众。
- 公开事实、完成承诺、赠与物品只有在结构化意图合法执行并提交后才产生对应**世界副作用**；NPC 自称“我给你金币”不等于金币已转移。私人 Relationship 与其他 Meta 更新整批验证、以 evaluation_id 幂等原子保存，不自动产生公开世界事实。
- Sub-agent 超时或 Schema / Meta 非法：当前有效 EVA 内有界重试/修正，耗尽保存 failed 与未完成 Observation；不能让 DM 静默冒充该 NPC 的独立决定。Action Intent 非法或执行失败独立反馈，不回滚合法 Meta、不重开已完成 EVA / 观察；事先批准的非 LLM 行动策略仍走独立命令授权。

## 7. 战斗：单一权威状态与规则求值

### 7.1 启动 Encounter

**[DECIDED]** SM 决定启动，可以引用 Package 的可选 EncounterDefinition，也可基于当前权威状态动态组建 Encounter；动态参与者必须具可信、已通过规则验证的机械数据。Package 不提供启动执行 API，不因进入 Scene 自动新建或重置 NPC。

1. SM 核验启动命令的可信 principal、适用 Actor 或受信系统/世界事件机械来源、参战实体/资源/位置、当前状态及 Session 固定 RulesetBinding；生成完整相关 NonCombatSnapshot 与独立 RNGContext。
2. 复用 RuleEvaluationRequest / RuleEvaluationResult，候选 operation_kind=combat.start，强类型 payload 描述启动参数。Engine 计算先攻与机械初始化，在 accepted 时返回未提交 Typed StateDelta、ProposedEvents、RNGTransition；不注册独立权威战斗对象。
3. SM 在短 SQLite 事务重验命令键/版本/权限/Delta，原子建立权威 CombatState 与 phase=combat，提交相关 Character/World 状态、RNG、正式事件、CommandReceipt、Outbox，保留合法战前安全点。

combat.start / 候选 Typed Delta combat.create 均 **[PROPOSED; NOT IMPLEMENTED]**；完整字段/初始化映射 [OPEN]，不以整份权威 Snapshot 覆盖代替受限类型化操作。失败不留下部分有效 CombatState，不推进权威 RNG；重试遵守 (session_id, command_id)。

### 7.2 战斗期间

- 每次 PC/NPC 的 Typed Intent 统一到 State Machine Command API。Host 传输受控身份关联，State Machine 核验权限、获取版本化快照并调用 Rule Engine 求值，再对 Delta 和 RNG 进行原子提交。
- CombatState 包括回合顺序、行动预算、位置、Active Effects、Concentration、待处理 Reaction/Choice 等。State Machine **持有和持久化**这些字段但不自行计算规则；Rule Engine 不维护跨调用的私有战斗权威。
- 战斗中打开门、拾取物品、喝药、触发机关等，若世界/机械效果能够在同一命令提交前完整求值，则同事务提交完整副作用，Engine 不提前扣费；已提交事件才触发的后续机械效果使用可靠、幂等的独立命令，不声称跨已提交事务原子（§5.5）。
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

`SessionRecord`、全局世界标记、SceneInstance、唯一 Persistent NPC State（含 Personality、Goal、Plan、Schedule / Current Activity）、**Observation Inbox、事件时感知证据、NPC ObservationProcessingStatus / 内部 Completed Cursor 及待处理 Outbox**、Evaluation Task / Status / Observation Work、唯一选定 Result / Meta 版本、可靠输出交接与独立 Command Receipt、物品与 Quest、Challenge 计数、已提交 Event Log、命令回执与去重键、Package/Ruleset Digest、当前阶段、权威 `CharacterState` / `CombatState` / `RNGState`、待续裁决和规则求值/提交回执。LLM Context / KV Cache 不属于 NPC 权威存档。

**SM-01 已确认的实现基线**：Python + SQLite 单进程 State Machine，启用 `PRAGMA journal_mode=WAL`、`PRAGMA foreign_keys=ON`，优先 `PRAGMA synchronous=FULL` 保障关键存档的断电持久性；合理配置 `busy_timeout`、连接生命周期与备份策略。WAL 并不消除单写者限制；不要在写事务中等待 LLM/Rule Engine。数据库文件放在本地支持可靠文件锁与同步的存储上，不假定可经共享网络盘安全多写。

建议索引/约束（具体表结构待实现）：创建阶段 `UNIQUE(principal_id, command_id)` 与 Fingerprint / 原 Session 映射随初始化同事务保存；普通游戏命令 `UNIQUE(session_id, command_id)`、`UNIQUE(session_id, event_seq)`、`UNIQUE(session_id, observation_id)`、`UNIQUE(evaluation_id)`（在 SM 本地运行时唯一定位 Task）、每个 Evaluation 最多一个最终 Result 的唯一约束，以及按观察者/有序 Delivery Cursor 的索引和原子任务状态/认知版本检查；以实际键模型消除重复副作用。Session 的 Version Gate 与数据库写锁串行性分别负责语义一致性和持久化原子性。

快照可用于快速读取/恢复，但权威一致性来自短事务内提交的 State Delta + Receipt + Event/Observation Outbox；MVP 不必构建完整 Event Sourcing 平台。4–5 名玩家、数百 NPC 的支持属于将来基于真实并发与延迟测试评估的扩展目标，**不是**当前单人 MVP 的功能承诺。

### 8.2 非活跃战斗恢复（MVP 必须）

加载 Session 时：校验包版本与 Ruleset、重建或读取最新 World State、恢复 NPC 知识、私有 Observation Inbox / `observation_cursor` 与 Memory、恢复 Scene 位置、Evaluation Task / Status / Observation Work / 内部 ProcessingStatus、已选 Result / Meta 与可靠交接及 Command Receipt，先对账再续未完成项；重访不得从 `initial_state` 重新复制已改变的实例。**只有处于非战斗状态且不存在未解决的命令/待续裁决，或已有明确受控安全点，才可以宣称 MVP 的成功续玩。**

### 8.3 活跃 Combat 恢复（明确移至 Post-MVP）

**SM-02 已确认**：不要求跨进程恢复活跃战斗的精确回合状态。活跃战斗不能调用普通 `save_session` 返回“可安全续玩”的成功回执。按 §7.4 使用战前 Checkpoint + 显式重新开始资格判定 / 阻塞状态；**不得悄悄回滚已提交机械结算**。未来评估从 State Machine 的持久 `CombatState` 和 PendingChoice/Reaction/RNG 精确续玩，**不再以恢复 Engine 私有 Handle 为前提**。

### 8.4 Replay 与审计

- **世界 Replay**：可根据已提交的有序世界命令/事件恢复或核验；保留各 NPC 的 Observation 来源、投影版本与记忆提议回执；不要求 LLM 对话、记忆解释逐字重生成。
- **机械 Replay**：以固定 Ruleset、已提交的 Snapshot/Intent/RNG 进度和确定性 Rule Evaluation 复算核验；由 State Machine 持久保存权威原始事实，Rule Engine 提供求值一致性。
- **禁止**通过新一次随机执行重建已提交但回执不明确的命令；按 State Machine 的幂等记录恢复或阻塞。

### 8.5 State Machine 不可用

MVP 是 Python + SQLite 单机权威运行时。SM 持续不可用或持久化失败时，Session 停止权威推进，进入暂停、错误或待恢复流程；不能写库时不声称已持久记录暂停。Host 停止派发并提示运行时错误，不接管游戏状态，不维护影子权威副本或独立游戏执行队列。

恢复从 SM 已持久状态、Evaluation Task / Observation Work 和事务回执对账；提交状态未知按原 ID 查回执，不重新生成行动或重掷骰。非战斗 Session 恢复必须支持，未完成工作继续按当前授权处理；战斗中断精确续玩仍为 Post-MVP，沿用 §7.4 安全策略。不增加分布式协调系统。

## 9. 错误分类与安全失败语义（设计建议）

| 分类 | 典型原因 | 世界状态影响 |
|---|---|---|
| `invalid_package` | 文件/引用/规则绑定错误 | 无 Session 创建 |
| `unknown_session` / `unknown_actor` | 身份未定义 | 不提交 |
| `unauthorized_controller` / `knowledge_denied` | 越权 Actor、读取秘密 | 不提交 |
| `state_version_conflict` | 过期 `expected_world_version` | 不提交；要求刷新视图 |
| `rule_refused` / `unsupported_mechanic` | 结构化规则拒绝/能力不支持，区别于合法未命中或被反制但已支付的 accepted | 不提交机械变化/RNG；不能把候选拒绝事件发布为已发生效果 |
| `schema_invalid` / `ruleset_binding_mismatch` | 输入/结果 Schema 或固定规则绑定不匹配 | 求值前拒绝非法输入/绑定，非法结果不提交，不映射为规则 rejected |
| `rule_evaluation_error` / `transport_error` | 求值运行时异常或传输故障，独立于四种规则结果 | 未提交不推进状态/RNG，提交未知按命令键查询 |
| `commit_response_failed` | State Machine 已提交，但响应构建失败 | 查询本地稳定命令回执；不能二次执行 |
| `evaluation_or_commit_unknown` | 网络异常或提交回执未知 | Rule Engine 评估不构成提交；查询 State Machine 命令记录，无法判定则安全阻塞 |
| `world_transaction_failed` | 世界数据库提交异常 | 不产生部分提交；重试按命令回执/去重处理 |
| `agent_unavailable` | NPC 模型调用错误、超时 | 无 NPC 世界副作用；保留观察收件箱，执行明确的故障策略 |
| `observation_projection_pending` | 投影排队、需要受控规则检定或 Agent 尚未消费 | 保留事件及证据/Outbox，不对观察者泄漏秘密或丢事件 |
| `invalid_memory_proposal` | 记忆来源不属于该 NPC、越权编造亲见/引用、错误版本 | 拒绝更新；不污染世界事实或他人记忆 |
| `state_machine_unavailable` | 持续不可用或持久化失败 | 停止权威推进；Host 不接管，恢复先查 SM 持久状态/回执 |
| `combat_unrestorable` | 活跃战斗退出，精确机械状态无安全恢复办法 | 不宣称恢复原回合；检查战前重开条件或阻塞 |

特别区分 rejected、unsupported、合法机械失败（可为 accepted 并提交成本）、version_conflict、pending_choice，以及传输/提交未知。保持 RuleEvaluationResult 四态及 CommandReceipt committed / rejected / conflict / pending_choice 模型，unsupported 作为 rejected 的授权结构化原因，不新增回执状态。Schema/异常另行处理，不能一律映射为“失败，请重新掷骰”。

确定性拒绝不强制调用 LLM，仅新语义判断需要有界重规划；原样重试用原 command_id，修改内容后用新 ID，响应丢失先查询原回执。原因按权限供 DM Planner 使用。Narrator 使用玩家可知投影并保持世界内叙事，不直接暴露 API/Schema/unsupported 错误，也不因系统能力限制编造墙壁永久不可摧毁、骰点失败或未提交世界变化；必要能力/运行时提示由文字入口合理表达。

## 10. 最小公共接口（仅候选名称）

新增接口/消息均 **[PROPOSED; NOT IMPLEMENTED]**，见 `MODULE_CONTRACTS.md` §7、§9、§10。声明式触发调度属于 SM 内部职责（§5.5），需要机械计算时复用候选 rules.effect，不增加独立 Event Engine。SM 发出 NPCEvaluationRequest，Host 执行模型；SM 不实现 Prompt / 主观推理 / KV Cache。内部操作不作为新增跨模块服务。

| 接口 / 方向 | 输入 | 输出 |
|---|---|---|
| load_adventure_package | Package 来源 | valid / invalid、结构化 errors / warnings；valid 才固定 Package 身份/摘要及生效 RulesetBinding |
| create_session | CreateSessionRequest：批准包身份/摘要、command_id、players[]；可信认证上下文 principal_id / 控制关系 | 原子创建的 Session ID / 创建结果 / 有限元数据；(principal_id, command_id) 幂等，不返回隐藏世界 |
| get_scene_view | Session、可信 Viewer / 主持范围 | DMView / PlayerView / NPCView 的授权场景事实，包含已提交动态对象；不新增查询服务 |
| get_npc_view | Session/NPC、可信主体 | 完整授权 Profile / Episodic Memory / Belief History / Relationship / Goal / Plan 及 NPCStateVersion |
| get_event_observations | Session/NPC、读取 Cursor / 范围 | 有序观察、投影水位；读取不完成工作 |
| get_current_perceptual_view | NPC、授权范围 | 当前感知；用于记忆的来源须可核验 |
| request_npc_interaction（DM/UI → SM） | 可信交互请求 / 当前玩家输入 | SM 原子撤销旧有效 EVA、授权新任务，不等待旧反馈 |
| NPCEvaluationRequest（SM → Host） | 已授权 Task、完整授权 Meta / 新观察 / 玩家输入（适用时） | Host 模型运行与 NPCEvaluationResult |
| submit_npc_evaluation_result（Host → SM） | evaluation_id: str, result: NPCEvaluationResult | EvaluationReceipt；从 Task 恢复全部关联，整批 Meta 原子提交 / 结构化错误 |
| Runtime 状态 / Gate 分类反馈（Host → SM） | 非权威失败/取消/Context 状态、分类候选 | SM 采用分类、维护任务与领域状态 |
| 创建/取消 Task、维护 Completion（内部） | 领域触发、必要认知处理与可靠交接 | EvaluationStatus、ObservationProcessingStatus / Completed Cursor |
| project_world_event（内部） | 已提交事件、事件时证据 | 私有 Observation / 持久 Outbox |
| tick_npc_schedule（内部） | 游戏时钟、日程、稳定 Trigger | 合法活动 / 取消 / 重评估任务 |
| submit_command | TypedCommand：session_id / command_id、可信 principal_id、按类型适用的 actor_id、command_type、expected_world_version、强类型 payload | 内部 world.* / rules.* / combat.* 分派；授权 CommandReceipt / 结构化原因，规则部分复用统一求值 |
| evaluate_rule（内部适配器） | RuleEvaluationRequest：session_id / command_id / operation_kind、按操作类型适用的 actor_id / 可信机械来源、强类型 payload、CombatSnapshot 或 NonCombatSnapshot、RulesetBinding、独立 RNGContext | 四种 RuleEvaluationResult；accepted 含完整 Typed Delta / ProposedEvents / RNGTransition |
| query_action_availability（SM → Engine，只读） | 可信 Actor、operation_kind / 强类型 payload、完整 Snapshot / 固定 RulesetBinding | available / unavailable / unknown；SM 过滤原因后供 UI/Agent Planning 使用，无 RNG/Delta/事件/CommandReceipt，执行仍需重新验证 |
| get_command_receipt | session_id、command_id、可信查询主体 | 原持久 CommandReceipt 的授权投影；Fingerprint 防止同 ID 不同请求，无二次 ACK |
| save_session / resume_session | Session、包版本 | 非战斗恢复或中断战斗安全限制 |

submit_world_command / submit_check_request / submit_combat_intent / start_encounter 仅可作为内部处理路径；公开普通游戏提交统一 submit_command。创建、NPC Evaluation 和查询/回执入口保持独立。

NPC Evaluation 提交入口只需 evaluation_id 与 Result；调用身份来自可信运行环境，不接受 LLM 自报。invocation_id / context_id 非必填提交信息，Evaluation ID 不是认证凭证；Action Execution 仍独立 command_id。EvaluationReceipt 是结构化反馈，不新增独立服务/复杂公共 Receipt 系统，也不增加 ACK 握手。

## 11. MVP 开发顺序与验收测试

建议先用**原创、可公开分发**的合成 Adventure Fixture 做最小可运行闭环；不要直接把未经授权的 *First Blush* 剧情/图片嵌入公开代码测试。

### Batch SM-1：统一 Package Loading / Validation + Session / Scene

- 解析/审核固定包，验证悬空引用、ID、Schema/Ruleset 和初始 Scene。
- 创建独立 Session；Scene 初始化一次，打开的门/移动的 NPC 在重访时保留。
- 采用 Python + SQLite WAL + 短事务持久化非活跃战斗 Session；相同可信 (principal_id, command_id) / Fingerprint 不创建重复 Session，冲突拒绝、初始化失败无半有效 Session。
- **完成证据**：至少两个互不污染的 Session，以及一套 create → enter → mutate → leave → revisit → save → restart → resume 测试。

### Batch SM-2：World Commands + Events / Challenges

- submit_command 统一信封、可信身份、按类型 Actor/机械来源、版本、持久去重、有限世界操作与世界事务；GM 裁决及 Conditional Effect 复用同一路径。
- 一次性事件链、条件 AST、成功/失败计数、Rule Check Result 的来源校验。
- **完成证据**：重复领奖、旧版本更新、事件循环、未经提交的检定、错误 NPC 权限全部被拒绝且没有额外状态变化。

### Batch SM-3：WorldEvent / Perception / NPC Memory + Agent Integration

- 事件稳定顺序、外显动作与私有 Intent 区分、事件时感知证据、Perception Projection、各 NPC Observation Inbox 与持久 Outbox。
- 完整授权 Profile / Episodic Memory / Belief History / Relationship / Goal / Plan 隔离，Observation → EVA Result → 整批确定性验证 → Meta 原子保存，不做语义筛选/验证。
- NPC 按需激活与观察游标、提议与提交分离、非 LLM fallback 边界、有限自动反应深度。
- SM 双模式独占、持久 EvaluationStatus / NPCStateVersion、每 EVA 唯一 Result、原子 Meta 与可靠行动交接、内部 Completed Cursor；Host 执行模型与 Context；新接口均待实现。
- **完成证据**：NPC A 无法读到 B 私有 Intent 或秘密；可见争抢各自形成正确 Observation；相同事件重试不重复投影；无论模型认为谁故意抢钱，都不能修改客观世界事实。

### Batch SM-4：Rule Evaluation Adapter + Unified Atomic Commit

- 受控战斗开启、战前安全 Checkpoint、版本化 CombatState/CharacterState/RNG 快照、RuleEvaluationResult、完整 Delta 原子提交、资源归属、不可续战退出与错误回执。
- 必要外部 Hazard 和 NPC 显式 Combat Intent 通过统一命令/规则求值路径与 Rule Engine 团队联合验收。
- Action Availability Query 可与早期 Rule Evaluation Adapter 同步开发，先查询基础战斗操作，与正式求值共享规则逻辑；无 RNG/状态写入/Delta/事件/回执，不等待 Visual Presentation。文字 MVP 不强制调用，视觉 UI 仍 Post-MVP，本轮仅更新计划。
- **完成证据**：战斗中每条动作均恰好产生至多一次 State Machine 权威提交；失败、版本冲突或响应异常不产生重复消耗或推进 RNG；不支持的能力明确报告。

**节奏约束**：上述 Batch 是推荐依赖序列，不是 Codex 可以未经审阅连续开发的授权。在每批次完成后根据实际测试和模块接口重新评估下一批；优先减少影响真实端到端场景的缺口。

### 11.1 合成 MVP 验收矩阵

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A01 | 不同创建键的两个 Session 使用同一只读 Package | 世界数据、NPC 记忆相互隔离；相同可信创建键重试只返回原 Session |
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
| SM-A33 | Interactive Context 空闲时收到重大事件 | SM 批准 Interactive Task，Host 执行当前 Interactive LLM；模式不因无在途请求而变成 Background |
| SM-A34 | 一 Result 包含 Dialogue、Belief、Memory、Action Intent | Meta 整批确定性验证原子写入，Action / Dialogue 独立处理，EVA 完成不等待动作成功 |
| SM-A35 | Inactive NPC 一次 Background Evaluation 决定移动 | 无 Interactive Agent Context 亦能提出并合法提交行动；临时 Context 释放 |
| SM-A36 | 普通低价值 Observation | Safe Retention / No-op 回执后 SM 内部记录完成，不调用完整 NPC LLM，关键证据保留 |
| SM-A37 | Background → Interactive 与旧 EVA 提交竞争 | 取消旧任务/新建与 Meta 事务内资格检查串行；不等旧反馈，保留先提交 Meta/可靠交接，拒绝取消任务结果 |
| SM-A38 | 模型失败、重投、版本冲突、完成事务前后崩溃 | 唯一 Result 与原子 Meta 防半批/重复写，稳定 Command ID / 可靠交接防重复行动；认知/交接缺口不跳过 |
| SM-A39 | Memory 成功持久化 | Host 可继续复用 Active Context；无强制 Compaction / Rebuild |

### 11.3 v0.5 职责与统一协议验收（Proposed / Not Implemented）

以下为待实施的原创合成目标，本轮未运行模型、数据库或故障恢复测试。

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A40 | Evaluation / Gate 触发 | SM 创建授权 Task、维护领域模式与处理状态；Host 分类仅候选，SM 不执行 LLM 推理或 Prompt 管理 |
| SM-A41 | 多 Invocation / Context 复用 | Task ID 与调用尝试分开，Invocation/Context ID 可省略；Evaluation ID 不是认证凭证 |
| SM-A42 | 模型伪造身份/权限/版本/状态 | SM 从持久 Task 恢复关联，并核验可信主体、NPC、范围、引用、版本、任务与幂等，不信任自报 |
| SM-A43 | Interactive / Background Result | 同一/兼容七字段、可全空，最小提交只有 evaluation_id + result；Background 无 Interactive Context 也可提出行动 |
| SM-A44 | 无 ACK、EVA 交接后 Command 失败/等待选择 | Meta / Result / EVA 完成原子持久，可靠交接后 EVA / 必要认知处理可完成，独立 Command / PendingOperation 继续跟踪 |
| SM-A45 | Dialogue 发布或 Action Intent | SM 检查受众/叙事权限，Action 复用共享 Typed Command / Rule Engine / Atomic Commit |
| SM-A46 | SM 持续故障及非战斗恢复 | Session 停止权威推进，Host 不接管；从 SM 持久任务/状态/回执恢复，未知提交先查回执 |

### 11.4 v0.6 简化 EVA 合成验收（Proposed / Not Implemented）

以下是待实现目标，本轮未执行模型或 SQLite 故障注入测试。

| ID | 行为 | 必须通过 |
|---|---|---|
| SM-A47 | 同任务重复/不同结果 | Evaluation ID 幂等，每 EVA 至多一个最终 Result；相同返回原反馈，已选后不同结果拒绝 |
| SM-A48 | Memory / Goal / Plan 任一更新非法 | 整批 Meta、最终 Result 均不提交；同一有效 EVA 有界修正，任务有效性与 Meta 写入同事务核验 |
| SM-A49 | 模式切换与 Meta 提交竞争 | 原子取消旧有效任务并新建，不等旧反馈；先成功 Meta 保留，取消后新 Invocation/迟到结果不能提交 |
| SM-A50 | Meta 成功、Action 非法/失败/needs_choice | Meta 与 EVA 完成保留；可靠交接及独立 command_id 防漏防重，Command / PendingOperation 独立跟踪 |
| SM-A51 | Timeout / API / Schema / Meta 错误 / 重试耗尽 / 反馈丢失 | 有效且有预算保持 running，同 evaluation_id / 新 invocation_id 修正；仅耗尽或无法继续 failed，切换 cancelled；丢响应查原结果 |
| SM-A52 | SM 提供完整 Meta、Host 构建/复用 Context | 六类完整授权 Meta + 新观察，不语义筛选/Ranking/智能压缩；复用后增量变化即可 |
| SM-A53 | Initial / Runtime Belief 演变 | 同一 Belief 追加版本，来源/当前状态/历史保留，NPC 可修改/降低置信度/放弃，SM 不改写 |
| SM-A54 | 自然语言错误但结构/权限/引用合法 | SM 不做忠实性语义判断或引入验证 LLM，错误 Belief 不提升为 World Fact |

## 12. 决策登记与仍需确认的实现细节

下列 `SM-01`–`SM-03` 是本轮讨论中用户**明确确认**的 MVP 决策；带“待设计/待验证”的内容仅是实施提案，不能由开发 Agent 擅自冻结。

| 编号 | 议题 | 当前决定 / 约束 | 状态 |
|---|---|---|---|
| **SM-01** | 持久化语言与数据库 | Python + SQLite WAL、单进程优先、短事务、强持久化默认、Repository/Adapter 边界 | **已确认** |
| **SM-02** | 战斗中途精确恢复 | **MVP 不支持**，列入 Post-MVP；须有明确安全检查点、不可伪恢复及战后可靠结算 | **已确认** |
| **SM-03** | 多 Agent 共同感知与记忆 | WorldEvent → SM Perception / Reliable Observation → SM Task / Mode Routing → Host Runtime → 可选 NPC Evaluation；State Machine 保存和验证 | **已确认基础架构，v0.5 明确 SM 领域任务与 Host Runtime** |
| **SM-04** | 统一权威状态 | State Machine 持有并提交 World/Character/Combat/RNG，Rule Engine 只计算 StateDelta；遵守 ADR-001 | **已确认** |
| **SM-05** | 非交互 NPC 状态 | 简单游戏时钟日程；Inactive Lightweight Gate / Background Evaluation 可产生行动；不要求 Interactive Agent 激活或常驻 LLM | **已确认逻辑设计，具体阈值待实验** |
| **SM-06** | NPC Evaluation Mode Exclusivity / 切换 | SM 管任务/模式、EvaluationStatus / NPCStateVersion、原子 Meta 与可靠交接；切换直接取消旧有效 EVA 并新建、不等旧反馈；Host 管 Context / 模型 | **已确认原则；具体协议 Proposed / Not Implemented** |
| S04 | `Session.phase`、Flag、Condition AST 的最终字段 | 与 Package Validator 一起固定最小集合 | 待设计 |
| S05 | `world_version` 与实体版本粒度 | MVP 先 Session 级版本；更高并发时评估细化 | 建议 |
| S06 | NPC/普通怪物是否默认用 LLM 战术 | **不得降低** `MVP_SCOPE.md` 已规定的至少一个敌方 NPC Sub-agent Typed Combat Intent 验收；普通怪物默认策略尚待明确 | 默认策略待决策 |
| S07 | combat.start / rules.effect 的适配与环境来源 | 复用统一协议；AP-15 按操作类型校验 Actor 已确认；候选 combat.create、复杂 Effect/编排与 source_ref / 来源权限字段尚待设计；不得当作现有支持 | [OPEN]；技术验证待做 |
| S08 | 完整 Meta、Belief 历史与 Context 预算 | MVP 输入完整授权数据、追加 Belief 版本、增量复用 Context；不新增语义筛选/排名/智能压缩，超预算反馈策略待验证 | 细节待设计 |
| S09 | 玩家 PC 模板与未来导入 | Package 内多个完整、机械属性经规则验证的静态模板供选择；MVP 一玩家一 PC，无外部构建服务前提 | [DECIDED]；未来外部导入 [OPEN] / 不实现 |
| S10 | First Blush 许可与发布 | 未经许可，不公开上传受限制的原剧情与派生数据 | 已明确约束 |
| S11 | 感知何时需要规则检定 | MVP 确定性同场景感知 + 个别经审查 Rule Check；复杂遮挡等后置 | 精确触发待设计 |
| S12 | 同步争夺物品的游戏时序 | 禁止按网络先后来断言敏捷；SM 领域时序 / Engine 机械公式的契约待冻结 | 待设计 |
| S13 | Observation Outbox/消费回执/投影唯一键 | 必须能防丢、防重复和追溯；具体字段在 `MODULE_CONTRACTS.md` 固定 | 待设计 |
| S14 | 战前 Checkpoint 可重开资格与已提交副作用的保护 | 不承诺所有崩溃都能自动重开，已提交事件不能被静默回滚 | 待技术验证 |

---

## 13. 文档治理与下一步

### v0.9 修订摘要

统一 submit_command / TypedCommand 命名及内部路由；划分 Planner / SM / Engine 验证领域，有限动态创造与条件式世界效果复用受限语义。同步 AP-15 类型化 Actor / 来源原则、授权反馈和早期只读查询计划；候选 Schema / 复杂生成仍开放，未实现 API。

### v0.8 修订摘要

统一 Package 加载与可信创建幂等、内置 PC Templates 和 players[]；Scene / Encounter / 声明式触发由 SM 管理，combat.start / rules.effect 复用统一规则协议。区分单命令原子提交与已提交事件的可靠后续命令；候选字段和未决细节不视为现有实现。

### v0.7 修订摘要

同步 MODULE_CONTRACTS.md 的 P0 双 Snapshot / 强类型 payload、固定 RulesetBinding、四种规则结果、封闭 Delta、正式事件、独立 RNG 与命令键回执；新增只读 Availability Query 的候选入口。EVA 单次 Invocation 错误在有效且有预算时保持 running，仅耗尽或无法继续最终 failed；不增加 NPC 状态或改变行动隔离。新接口仍 Proposed / Not Implemented，编码、复杂 Delta / Continuation 与事件型版本推进仍 [OPEN]。

### v0.6 相对 v0.5 的修订摘要

1. 简化任务标识与最小 Result 提交，SM 持久 Task / EvaluationStatus / NPCStateVersion，不依赖 Host 内存状态或模式代次计数器。
2. Evaluation ID 为 Meta 幂等键，每 EVA 至多一个最终 Result；同事务验证任务/版本、选定 Result、整批原子写 Meta、记录交接与 completed。
3. 非法 Meta 整批不写，当前有效任务有限修正；SM 仅确定性验证，不做自然语言语义判断、不改写 Belief、不新增验证模型。
4. Action Execution 独立 command_id / Command Receipt，EVA 完成不等动作成功，可靠交接防漏防重，Command 失败/needs_choice 独立跟踪。
5. 模式切换原子取消旧有效任务、保留 Meta、移交 Work 并新建，不等旧调用或失败反馈；取消任务不能靠新 Invocation 恢复资格。
6. 提供完整授权 Meta，Belief 与 Initial Belief 兼容且追加版本保留历史，Host 只组装/增量复用，不新增语义筛选/检索/排名/智能压缩。保留 ADR-001、P0 规则契约、双模式独占及原 MVP 范围。

- 此文档只给出 State Machine 运行时架构与状态权威边界；**不替代**项目总架构 `ARCHITECTURE.md`、Agent 内部设计 `AGENT_ARCHITECTURE.md` 或正式跨模块消息契约 `MODULE_CONTRACTS.md`。
- 发现本架构与 `MVP_SCOPE.md` 已确认决定冲突时，以已确认的 MVP Scope 为准，并在审阅中提出修改，不擅自改动产品范围。
- 公开仓库只存放通用 Schema、原创示例和程序代码；完整 First Blush 内容、地图与实质性转写继续留在合法权限下的本地私有资料中。
- **文档优先级**：ADR-001 是权威架构决策；旧 MVP Scope 的双权威用语为历史遗留，已在 v0.5 修正。

**下一步建议**：审阅 `AGENT_ARCHITECTURE.md` v0.8 与 `MODULE_CONTRACTS.md` v0.7 / Draft 的模式、EvaluationStatus / 原子 Meta / 可靠交接 / EvaluationReceipt 契约，再验证最小接口与故障场景；不将目标设计视为已完成实现。总体架构审阅后再整理根目录 `README.md`。

**本阶段最重要的完成标准不是“状态模型有多少类”，而是一个 Session 能在不重复执行规则、不泄漏 NPC 秘密、不重置场景的前提下，可靠地从剧本初态走到已持久化的结局。**
