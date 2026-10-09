# Agentic TRPG — State Machine Architecture（MVP）

> **状态**：Draft v0.2（已记录明确产品/技术决策；具体消息 Schema 与实现仍待审阅）  
> **日期**：2026-10-09  
> **建议位置**：`agentic-trpg/agentic-trpg/docs/STATE_MACHINE_ARCHITECTURE.md`  
> **依赖**：[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.4；[`ADVENTURE_PACKAGE_SCHEMA.md`](./ADVENTURE_PACKAGE_SCHEMA.md) Draft v0.1  
> **目标场景**：一位玩家、一个 PC、文字优先、人工整理的单人冒险包；Agent DM 和按需 NPC Sub-agent；不要求可视化引擎、World Creation Agent、多玩家或开放世界模拟。  
> **证据边界**：本文件是基于已讨论范围和冒险需求的**设计建议**，不是现有 State Machine 代码的完成状态。与 Rule Engine 的 API 适配以实际实现和独立测试为准。

## 1. 目标、边界和核心术语

State Machine 是**一次具体游戏 Session 的权威世界状态协调器**，不是剧本生成器、规则引擎或 NPC 对话模型。

它承担五件事：

1. 加载并验证**不可变** Adventure Package；为一次 Session 实例化初始状态。
2. 记录玩家和 NPC 的行动在世界中造成了哪些**已验证、已提交**的变化。
3. 为 Agent DM / NPC Sub-agent 提供**按角色权限过滤**的上下文视图。
4. 将需要机械裁决的动作交给 Rule Engine，并根据**已提交的** Result / Events 做世界层同步。
5. 使用 Python + SQLite（WAL）保存和恢复**非活跃战斗**的 Session，防止重访重置、事件重复执行、重试重复付款和知识泄漏。
6. 在权威事件提交后生成按角色过滤的 Observation，持久化观察溯源，并向 Agent Host 提供按需激活及记忆更新的安全接口。

### 1.1 四个容易混淆的概念

| 概念 | 内容 | 可变？ | 谁拥有权威？ |
|---|---|---|---|
| **Adventure Definition** | 地点、静态世界事实、NPC 初始档案、剧情条件、规则绑定 | **不可变**（Session 固定版本） | Adventure Package 作者 / 验证器 |
| **Session Runtime State** | 当前场景、场景实例、世界标记、物体归属、任务、NPC 记忆、事件记录 | **可变** | **State Machine** |
| **Mechanical Combat State** | 战斗中的 HP、位置、Action Economy、RNG、Conditions、集中等 | **可变** | **Rule Engine** |
| **Agent Working Context** | DM / NPC 当次推理看到的许可信息与最近事件 | **临时派生视图** | State Machine 提供事实边界；Agent 生成非权威提议 |

**不变量**：静态模板不是当前状态；描述不是命令；提议不是提交；叙事不是规则计算结果；State Machine 不维护第二份独立可写的战斗规则状态。

### 1.2 行动、观察与记忆的认识论边界

| 概念 | 由谁产生 / 确认 | 是否成为世界事实 | 可供 NPC 使用的方式 |
|---|---|---|---|
| `Intent` / `Proposal` | PC/Agent/Host 提交的**内部提议** | **否**；被拒绝的私有意图尤其不能公开 | 提议者可获合法拒绝回执；其他角色不可据此读心 |
| `ObservableActionStarted` | **真实在世界中发生**且被提交的外部动作（例如实际伸手） | **是，该外显动作已经发生**；但目标效果未必成功 | 通过 Perception 判断哪些角色看到了动作 |
| `WorldEvent` | State Machine 或可信 Rule Engine Result 的已提交投影 | **是，记录客观行为或结果** | 不能向所有 NPC 原样广播含秘密的事件 |
| `Observation` | State Machine 的 Perception Projection（必要机械判定来自 Rule Engine） | **是，该角色获得了某项观察**；观察内容不一定涵盖全部事实 | 构成该角色后续认知的证据，按角色私有保存 |
| `Belief / Memory` | NPC Sub-agent 根据观察、目标与既有记忆**提出解释和更新**；State Machine 校验后保存 | **否，不自动成为客观世界事实** | NPC 后续决策和对话的私有上下文 |

**关键区别**：Agent A 获得金币，不等于 A 知道 B 也想拿金币。只有 B 真正作出可观察的动作并被 A 感知，A 才能基于观察判断双方是否发生争抢。世界事件的排序也不能直接替代游戏世界的“谁更快”的规则裁决。

### 1.3 不属于此模块的工作

- 不解析 PDF、不自动创建世界：这是 MVP 之后的 World Creation Agent。
- 不计算 Attack、Damage、Save、Spell Slot、Concentration、战斗行动顺序；应复用 Rule Engine。
- 不替 NPC 决定动机、谎言、主观记忆解释或战斗行动；NPC Sub-agent 提议，State Machine 只审核与提交。
- 不生成叙事文本和插画，不做实时地图、Token、动画。
- 不执行任意剧本脚本、不建立通用游戏编程语言；只支持已经审核的有限条件与效果。

## 2. 总体运行架构

```text
Human Player ──自然语言──► Agent DM（主持与语义裁决）
                                  │
                                  ├── query_view(player / dm)
                                  ├── request_npc_decision(npc_id)
                                  │        │
                                  │        ▼
                                  │   NPC Sub-agent
                                  │   （私有知识 + 目标 + 记忆）
                                  │        │
                                  │        └── NPC proposal（非权威）
                                  ▼
                       State Machine（Session 权威）
                         ├── Package Registry（只读定义）
                         ├── Session / Scene / NPC State
                         ├── Permissions / Knowledge Projection
                         ├── Command Validator / Version Gate
                         ├── Event Condition / Effect Executor
                         ├── World Event Log / Event-time Evidence
                         ├── Perception Projection / Observation Inbox
                         ├── NPC Memory Repository / View Projection
                         ├── Rule Engine Adapter ───────► Rule Engine
                         │                               （战斗/检定权威）
                         ◄──────── typed receipt / authoritative events ──┘
                         └── SQLite Persistence / Outbox / Recovery
                                  │
                     ┌────────────┴─────────────┐
                     ▼                          ▼
              Committed World Events     Per-Actor Observations
                     │                          │
                     ▼                          ▼
              Agent DM 叙事             Agent Host 按需激活 NPC
                                                │
                                                ▼
                                       NPC Memory Proposal
                                                │
                                                ▼
                                       校验 / 持久化私有记忆
                     │
                     ▼
                 最小文字 UI
```

图示为**逻辑组件**，不意味着 MVP 必须拆为微服务、消息队列或独立数据库。Perception 是 State Machine 内部子系统；Agent Host 负责激活 NPC（属于 Agent DM 运行模块）。MVP 优先 Python 单进程 + SQLite WAL，未来再决定部署拓扑。

## 3. 运行时数据模型与状态所有权

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
- 物品 `owner_id`、当前位置与 `quantity` 由世界事务唯一维护；在活跃战斗期间涉及装备/消耗的行为需遵守 Engine 的权威结算边界。
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
- NPC：私有 `known_fact_ids`、`beliefs`（允许错误）、`goals`、`relationship_state`、`committed_memories`、`observation_cursor`、`controller.kind`；观察收件箱与记忆更新分开保存。
- 敌人/普通怪物：与重要 NPC 一样有身份和状态，但是否调用 LLM 要由策略决定；不要求为每一个普通怪物常驻创建 Agent。

**三个独立命题**：`world_fact_is_true`、`npc_knows_fact`、`npc_believes_fact`。允许 NPC 有错误信念和撒谎，但禁止把信念自动提交为世界事实。

### 3.5 `ChallengeInstance`：非战斗技能挑战

针对撤退、追逐或跨多次检定的任务，建议记录：`challenge_id`、`scene_id`、`successes`、`failures`、`required_successes`、`status`、`resolved_check_ids`。每次检定的 DC/能力/结果由合法规则或显式 GM 裁决产生，**State Machine 仅累计已提交 Result**。

不要把非战斗技能挑战实现为伪造的 Combat；若失败伴随伤害/Condition，需要受控 Rule Engine/Host Hazard 接口，缺失时明确阻塞该场景而不是直接写入 HP。

### 3.6 `WorldEvent`、感知证据与顺序

`WorldEvent` 是**已提交的、不可变的世界事件记录**，最小概念字段：`session_id`、`event_id`、`event_seq`、`event_type`、`source_command_id` / `engine_operation_id`、`actor_id`、`object_ids`、`scene_id`、`occurred_at_game_time`、`payload`、`visibility_class`、`perception_evidence_ref`。字段为候选，不代表现有实现。

- `event_seq` 由 Session 中的权威提交顺序分配，单调递增；它是**记录顺序**，不自动证明角色的生理反应速度。
- `WorldEvent` 应记载必要的**发生时刻证据**（行动时地点、参与者位置、光照/可听性、遮挡/秘密等级、相关动作是否外显）。不能在 NPC 数分钟后苏醒时用**当前**视野倒推此前谁看到了什么。
- 可见动作的开始与成功/失败结果是不同的事实；只有实际外显的 `action.started`（候选事件）才允许投影给旁观者。私有 Intent、未执行命令、LLM 私下计划不得伪造为外显动作。
- Rule Engine 相关事件必须从可信的已提交结果投影；战斗期间可能存在暂未持久结算的临时 Engine 事件，应按第 7 节的战斗隔离边界处理，不得冒充已永久提交的世界状态。

### 3.7 `ObservationRecord`：角色实际收到的观察

建议字段：`observation_id`、`session_id`、`observer_actor_id`、`source_event_id` / `source_event_seq`、`observed_at_game_time`、`perception_kind`（如 sight/hearing/self_action/report）、`observed_payload`、`visibility_basis` / `rule_check_receipt_id`（若适用）、`projection_version`、`delivery_status`。每项 Observation 必须标明**观察者**和**来源**，不能在投影中包含事件对该观察者不可知的隐藏字段。

- MVP 只需同场景、简单视觉/听觉、人物在场状态、明显动作与自我行动结果。遮挡、幻术、远距离声音、误认等高级机制后置；若重要剧情要求检定，不得凭普通同场景规则绕过 Rule Engine。
- 观察投影是确定性、可去重的映射；`(observer_actor_id, source_event_id, projection_kind)` 等候选唯一键防止重试生成重复观察。结果按 `source_event_seq` 有序读取。
- 优先在世界提交事务中一次性落库已确定的观察；若投影较复杂，必须以**持久 Outbox + 事件时证据**处理，并使用幂等投影，避免提交成功但观察永久丢失。
- `ObservationRecord` 是证据而非角色长期记忆。一个 NPC 可以暂时不理解、不在意甚至忘记某个观察，但不能因此篡改原始事件与感知来源。

### 3.8 `NPCMemoryRecord`：角色内部认知的持久表达

建议将 NPC 私有记忆分为 `episodic`（经历摘要）、`belief`（主观判断，允许错误）、`relationship`（对他人的态度/承诺）三类逻辑记录；统一保留 `npc_id`、`memory_id`、`source_observation_ids` / `source_memory_ids`、`epistemic_status`（observed / inferred / told）、`confidence`（如适用）、`created_from_activation_id` 和可选内容版本。

**记忆的内容解释、重要性以及关系变化建议由 NPC Sub-agent 提出**；State Machine 只验证 Actor 权限、数据格式、可访问的来源引用、允许的更新种类、幂等版本和隐私边界，并持久化。仅靠 Schema 校验**不能证明** LLM 自然语言解释真实无误，故应保留来源、信心度和“推断/听说”标签，不将其提升为客观真相。基础已知事实的确定性授予（例如权威 `reveal_fact_to_actor`）仍由 State Machine 执行，不需要等待 LLM。

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
| **规则操作** | Ability Check、Save、Combat Intent、受控 Hazard | Rule Engine（或明确授权的 GM 判定协议） | 消费已提交结果，再决定关联世界事件 |
| **纯对话** | `NPCDialogueProposal` | NPC 提议，经 Host 校验后成为可呈现内容 | 只有有明确语义的承诺/线索公开/关系变化才持久化；普通一句对话不产生机械效果 |
| **场景转移** | 进入已定义出口、传送剧情事件 | State Machine 的场景与权限判断，必要时 Rule Engine | 更新位置并记录 enter/exit；不重置旧场景 |
| **脚本事件** | 经审查的 `event_id` 触发及条件满足 | State Machine 的受限声明式 Event Executor | 执行允许列表的世界效果，一次性/按规定次数去重 |

### 5.3 世界事务（同一数据库/进程内）

候选最小步骤：

1. 按 `(session_id, command_id)` 查询历史完成回执；同键相同内容返回原结果，**同键不同内容拒绝冲突**。
2. 验证 `expected_world_version`、Actor 控制权、当前 Phase、可见/可用对象与事件条件。
3. 生成具体 State Delta；同一事务中应用 Delta、递增 `world_version`、追加 World Events、记录命令回执与事件去重键。
4. **事务提交完成后**才返回 `committed` 并允许 Agent DM 将其叙述为事实；失败/冲突不写任何部分 Delta。

请求 payload 应使用稳定序列化计算指纹，以区分重复提交和同一 `command_id` 下的不同请求。MVP 使用单个本地 SQLite 数据库的原子事务，不引入分布式事务协调器。

**性能与锁纪律（SM-01 已确认）**：Agent 推理、远程/本地 LLM 调用、需要等待的 Rule Engine 调用必须在 SQLite **写事务之外**。读取版本和生成提议后，在短写事务内重新验证 `world_version` 与操作条件，再原子提交 State Delta + World Events + Command Receipt + 去重记录 + 可即时生成的 Observation/Outbox。SQLite WAL 允许并发读，但写事务仍需串行；Session 内逻辑命令协调不等于 SQLite 自带游戏顺序。

### 5.4 Rule Engine 跨边界提交：不可假装原子性

State Machine 与 Rule Engine **不是天然共享一个事务**。尤其现有 Bridge 的重试回执为进程内数据，不能据此宣称断电/跨 Worker 的永久 Exactly-once 保证。

建议最小操作日志模型（最终枚举待冻结）：

```text
prepared -> engine_requested -> engine_committed -> world_committed
                      │                 │
                      ├── refused ───────┘（无成功的机械世界副作用）
                      └── uncertain / requires_reconciliation
```

关键纪律：

- 发起调用前持久记录本次 `operation_id` / `command_id` 与经过验证的目标；发送给 Engine 时使用稳定 `request_id`。
- `EngineResult` 必须明确是 `not_executed`、`rule_refused`、`committed`、`rolled_back` 还是`commit_unknown`（规范化候选分类）。**不能仅以 HTTP 是否为 200 判断有没有花费资源。**
- 当确认 Engine 已提交后，在本地世界事务中完成**一次**对应同步和事件追加；同一 `engine_operation_id` 重放不得重复写入奖励、HP 或进度。
- 如 Engine 已提交但 HTTP 响应丢失，优先用同一 Request ID 获取回执；若回执不可恢复（例如 Bridge 进程重启），将 Session 标记为 `blocked_reconciliation`，暂停影响状态的后续指令，**不得重新随机执行本次动作**。
- `world_committed` 前后的任何异常都要可以通过幂等记录辨认；跨模块未解决缺口必须成为显式发布阻塞/部署限制，不能在日志中伪称“已原子提交”。

**MVP 已确认范围**：主流程优先部署为单进程，对非活跃战斗做可靠持久化；不提供活跃 Combat 跨进程精确恢复。但即使不支持此能力，也必须拒绝伪恢复和重复付款，明确显示需要人工/受控恢复。

### 5.5 事件驱动与链式触发

- 只有**已提交的权威事件**能触发 `events.yaml` 条件。LLM 的自述、未接受的 NPC 决策或草稿对话不是 Event。
- Event Condition 使用既定封闭表达式词汇（`all`、`any`、`not`、`flag_equals`、`actor_present`、`event_once`、`challenge_count_at_least` 等），禁止 `eval`。
- 可执行的 World Effect 只使用 `ADVENTURE_PACKAGE_SCHEMA.md` 的允许列表；机械结果必须发起 Rule Engine 请求并消费结果。
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

1. State Machine 在世界操作成功后，或在消费可信的 Rule Engine 已提交回执后，持久化带顺序和来源的 `WorldEvent`。
2. Perception Projection 使用该事件**发生时**的角色位置、在场状态、光照、可听范围、已审查可见性标签及必要规则检定，按 `observer_actor_id` 生成不同的 `ObservationRecord`。
3. 只给每个角色提交自己可知的观察文本/结构；例如 NPC 见到某人倒下，不自动知道其隐藏 HP 或凶手的内心动机。
4. Observation 先保存到该角色的私有有序收件箱（inbox）；可在其下一次激活时消费。离线 NPC 不需要运行 LLM，也不能因延迟激活而从**现在**的 WorldState 重算先前视野。
5. Observation 的投影/分发可通过本地持久 Outbox 异步完成；事件已提交但投影或唤起失败时，应安全重试且不重复生成、不给其他 NPC 泄密。

**没有可观察事件就没有旁观者读心**：仅有 B 的 `Intent: take_coin` 不得通知 A“B 想抢钱”；若 B 实际伸手且 A 看见了，则 A 可以收到外显动作观察。对话、误认、隐匿、感知检定及证人转述的特殊情况要保留各自来源，不得把“听说”冒充“亲眼目击”。

### 6.3 `Observation → Memory`：NPC 的推理权与 State Machine 的保存权

记忆形成分两步：

- **自动阶段（不调用 LLM）**：State Machine/Perception Projection 记录结构化 Observation 与来源、顺序、观察者权限。若事件本身明确授予已知事实（如 `reveal_fact_to_actor`），可确定性更新 `known_fact_ids`。
- **NPC 激活阶段（按需 LLM）**：Agent Host 将尚未消费的重要 Observation、NPC 私有历史、Goals、Relationships、已有 Beliefs 提供给该 NPC Sub-agent。Sub-agent 可提出 `NPCMemoryUpdateProposal`：新增情景记忆、形成/修正 Belief、关系/态度变化或无须额外长时记忆。并非每次观察必须生成一次 LLM 摘要。

State Machine 验证 Proposal 的 `npc_id`、可信激活身份、来源 `source_observation_ids` 是否属于该 NPC、允许更新的类型、数据形状、因果/版本关系和幂等键。**它不能凭 Schema 验证 LLM 对心理动机的解释真伪**；因此必须保留 `epistemic_status`（亲历观察 / 推断 / 听说）与 `confidence`，禁止将推断写为共同的世界事实或伪造亲见经历。

`episodic` 不等于永久储存逐字对话；`belief` 可以错误；`relationship` 的变化应遵循该 NPC 的合法更新策略，不能借机修改目标角色的关系或覆盖公共世界事实。NPC 的私有记忆可修改其自身下一轮行为，但不能直接触发对其他人物、物品、Quest 的未经审查的 State Delta。

**示例（原创场景，字段均为候选）：**

```yaml
observation:
  observation_id: obs.24
  observer_actor_id: npc.b
  source_event_id: evt.coin_transferred_to_a
  perception_kind: sight
  observed_payload:
    actor: npc.a
    action: picked_up
    object_id: item.coin_001
    before_my_attempt: true # 只能依据 B 自己的已提交动作时序来断言

memory_update_proposal:
  npc_id: npc.b
  source_observation_ids: [obs.24]
  changes:
    - kind: episodic
      text: "A 比我先拿起了金币。"
      epistemic_status: observed
    - kind: belief
      text: "A 可能故意与我争抢。"
      epistemic_status: inferred
      confidence: 0.5
```

这里 `before_my_attempt` 不是投影系统随意从 Intent 推出来的；如果 B 尚无实际可观察/已提交的尝试，应改为只报告 A 取走金币，不添加竞争关系。

### 6.4 Agent Activation：按需响应、不常驻监听

1. Host 因玩家与 NPC 交谈、NPC 面临明确情境选择、关键已观察威胁或当前战斗轮到其行动，决定是否激活该 NPC；不得把所有 NPC 事件都变成 LLM 调用。
2. State Machine 为特定 NPC 生成授权 `NPCView`，其中包括按 `source_event_seq` 排序的待消费 Observation、必要旧记忆、当前可执行动作摘要与对应 `world_version`。
3. Sub-agent 产生对话/行动/记忆更新**提议**。Host 分别向 State Machine 或 Rule Engine 的受控入口提交；提议期间世界可能已变化，执行前必须再次校验世界版本与权限。
4. 只有 Observation 确实被投递、且结果按协议完成后，才能移动 `observation_cursor` / 确认消费；Agent 失败、超时、进程重启不得使观察永久丢失或重复变成多条记忆。激活请求和记忆更新各有稳定幂等 ID。
5. 为防止 NPC A 回复触发 B、B 回复又触发 A 的无限循环，限制单次玩家行动的自动 NPC 反应深度、激活数量及 Token/时间预算；超过预算保留待处理观察，不得假装角色已经回应。

**权责归属**：State Machine 负责谁观察到了什么、记忆怎样验证/保存；NPC Sub-agent 负责如何理解、选择是否提升为长期记忆、怎样作出下一步决定；Agent Host 负责何时激活与调用预算。长期记忆压缩、相关性检索、虚假记忆检测和复杂冲突解决可在 `AGENT_ARCHITECTURE.md` 进一步设计，MVP 不引入独立 Memory Agent。

### 6.5 对话承诺、知识传播及故障

- NPC 对话可包含谎言、猜测、转述或修辞；话语事实不等于内容是真实世界事实。可观察的已发布话语可以形成 `speech` 类型世界事件，并投影给合适的听众。
- 公开事实、完成承诺、赠与物品、关系改变等只有在结构化意图获批并提交后才产生其对应**世界副作用**；NPC 自行宣称“我给你金币”不等于金币已转移。
- Sub-agent 超时、输出不合法或提出不可能行为：返回 `proposal_rejected`/`agent_unavailable`，保留未确认 Observation，允许有限次重新提议或由事先批准的非 LLM 策略接管；不能让 DM 静默冒充该 NPC 的独立决定。

## 7. 战斗与世界交接

### 7.1 战斗开始

1. State Machine 验证 Encounter 已满足触发条件、当前 PC 与 NPC World State、规则绑定及进场参数。
2. 在请求启动 Engine Combat **之前**先持久化一个安全的 `pre_combat_checkpoint`（Session/Scene/World/Actor/Inventory/NPC Observations + 相关非战斗机械资料的可信引用）；同时将 Encounter 标记为待启动。
3. 根据 Actor 到 Combatant 的**审查过的映射**请求启动 Rule Engine Combat；带 `session_id`、`encounter_id`、幂等命令标识和初始位置约束。只有在可核验的入口回执后才确立 `active_combat_ref`。
4. State Machine 保存 `active_combat_ref`、映射 ID、规则版本和进度操作记录；战斗期间不另建可变 HP/Slot/Position 镜像作为权威。
5. Agent DM/NPC Sub-agent 仅能提交合法角色身份的动作提议；Host 验证 Actor 控制权，Rule Engine 负责合法性、支付、RNG 和状态变化。

**既有集成阻塞**：先验证 `trpg-rules-engine` 是否已有受 Host 授权的 NPC/Monster 显式 Typed Intent 入口；不可用时必须补公共机制或修改已批准的 MVP 范围，不能假装内置 `advance_monster_turn` 等于 NPC Sub-agent 决策。

### 7.2 战斗期间

- State Machine 可以读取 Engine 暴露的只读 `LiveCombatView`，但不通过文本或镜像修改伤害和行动预算。
- NPC 战术 Sub-agent 不可只因其决定攻击就获得自动命中；它只输出 Action/Target 等 Intent 参数。
- 场景事件（例如若干回合后出现威胁）只消费**已提交的 Engine Round/Turn 事件**，并遵守已有战斗状态边界；这些战斗内事件可供当前进程叙事/观察，但未安全结算前不得被误写成已永久落库的最终世界结果。
- 不允许把场景剧情失败自动转成隐藏的 HP 修改；若缺少受控 Hazard/External Damage 接口，必须把该能力列为实现阻塞项。

### 7.3 战斗结束与结算

- Rule Engine 提供权威结束事件、`CombatOutcome`、最终影响世界的结果和资源来源。
- State Machine 用稳定 `combat_id`/`settlement_id` **一次性**结算死亡、HP/资源、Quest、战利品、NPC 地点等可持久化结果；保持 Actor 身份归属一致。
- Rule Engine 之外的世界物品与任务进度由 State Machine 按世界事务提交；**不得由叙事文本推算资源支出**。
- 当前 Rule Engine `CombatOutcome.expended_resources` 曾在代码审阅中发现对集中法术的支出归属问题；在独立修复与验收前不能把该字段未经校验地写回持久角色资源。
- 战斗结束后清除当前活跃引用，并设置持久的已结算标记；重复结算只返回旧回执。
- **战斗结果落库边界**：持久世界更新、角色资源同步、战利品/任务变化、已经确认的战斗相关重要观察与 Settlement Receipt 要按可恢复的结算协议一次性推进；不可将已结算 HP 与未结算资源拆成互不关联的永久事实。
- **不可简单把整场战斗当作 SQLite 长事务**：战斗可能持续数分钟，必须使用入口安全检查点 + Engine 权威执行 + 有记录的结算阶段。战斗期间若允许非机械世界事件独立提交，需证明它们可以安全保留/回滚；MVP 可限制此类跨边界写入以简化恢复。

### 7.4 活跃战斗中断的 MVP 故障语义（SM-02 已确认）

- **不在 MVP 范围**：战斗进行中退出应用、断线或进程崩溃后，从原回合恢复完整 Engine 状态（RNG、Reaction Queue、Concentration、Action Economy、持续效果）。不提供“战斗中途精确续玩”的功能承诺。
- 正常游玩中的战斗必须能够跨多个回合连续执行，退出/恢复功能限制不影响战斗合法性或战后结算。
- 只有在可证明 Engine 尚未持久提交不可撤销副作用、战前 Checkpoint 与规则/世界版本均匹配，且期间没有已永久提交的不可回滚事件时，才可**明确提示玩家**重新开始该场遭遇；这是重新开始而不是恢复原回合。若条件不满足，Session 进入 `combat_unrestorable` 或 `blocked_reconciliation`，停止影响状态的操作并给出恢复/人工处理路径。
- 尤其当 Engine 操作**可能已提交**但回执丢失时，不允许静默载入战前存档后重新 RNG 或二次扣除资源。此时优先按原 `operation_id` 核对 Receipt；无法确定则阻塞，而非假定未执行。

## 8. 持久化与恢复边界

### 8.1 需要保存的最小状态

`SessionRecord`、全局世界标记、SceneInstance、NPC 身份/知识/记忆/关系、**Observation Inbox、事件时感知证据、NPC 观察消费游标及待处理 Outbox**、物品与 Quest、Challenge 计数、已提交 Event Log、命令回执与去重键、Package/Ruleset Digest、当前阶段及必要的 Engine 操作/结算引用。

**SM-01 已确认的实现基线**：Python + SQLite 单进程 State Machine，启用 `PRAGMA journal_mode=WAL`、`PRAGMA foreign_keys=ON`，优先 `PRAGMA synchronous=FULL` 保障关键存档的断电持久性；合理配置 `busy_timeout`、连接生命周期与备份策略。WAL 并不消除单写者限制；不要在写事务中等待 LLM/Rule Engine。数据库文件放在本地支持可靠文件锁与同步的存储上，不假定可经共享网络盘安全多写。

建议索引/约束（具体表结构待实现）：`UNIQUE(session_id, command_id)`、`UNIQUE(session_id, event_seq)`、`UNIQUE(session_id, observation_id)`、`UNIQUE(session_id, npc_id, activation_id)`、`UNIQUE(session_id, settlement_id)`，以及按 `(session_id, observer_actor_id, source_event_seq)` 的观察查询索引；以实际键模型消除重复副作用。Session 的 Version Gate 与数据库写锁串行性分别负责语义一致性和持久化原子性。

快照可用于快速读取/恢复，但权威一致性来自短事务内提交的 State Delta + Receipt + Event/Observation Outbox；MVP 不必构建完整 Event Sourcing 平台。4–5 名玩家、数百 NPC 的支持属于将来基于真实并发与延迟测试评估的扩展目标，**不是**当前单人 MVP 的功能承诺。

### 8.2 非活跃战斗恢复（MVP 必须）

加载 Session 时：校验包版本与 Ruleset、重建或读取最新 World State、恢复 NPC 知识、私有 Observation Inbox / `observation_cursor` 与 Memory、恢复 Scene 位置及已提交事件去重集合；重访不得从 `initial_state` 重新复制已改变的实例。**只有不存在活跃战斗及未解决 Engine 操作，或已完成受控结算的安全点，才可以宣称成功恢复。**

### 8.3 活跃 Combat 恢复（明确移至 Post-MVP）

**SM-02 已确认**：不要求跨进程恢复活跃战斗的精确回合状态。活跃战斗不能调用普通 `save_session` 返回“可安全续玩”的成功回执。按 §7.4 使用战前 Checkpoint + 显式重新开始资格判定 / 阻塞状态；**不得悄悄回滚已提交机械结算**。未来版本再考虑 Engine Handle、RNG、Reaction Queue、Concentration 和 Active Effect 的完整序列化与恢复。

### 8.4 Replay 与审计

- **世界 Replay**：可根据已提交的有序世界命令/事件恢复或核验；保留各 NPC 的 Observation 来源、投影版本与记忆提议回执；不要求 LLM 对话、记忆解释逐字重生成。
- **机械 Replay**：要求同一已审核规则数据、初始种子及**已提交 Intent 序列**生成同样权威结果。实际由 Rule Engine 提供与验证。
- **禁止**通过新一次随机执行重建已有已提交且状态未知的 Engine 调用。

## 9. 错误分类与安全失败语义（设计建议）

| 分类 | 典型原因 | 世界状态影响 |
|---|---|---|
| `invalid_package` | 文件/引用/规则绑定错误 | 无 Session 创建 |
| `unknown_session` / `unknown_actor` | 身份未定义 | 不提交 |
| `unauthorized_controller` / `knowledge_denied` | 越权 Actor、读取秘密 | 不提交 |
| `state_version_conflict` | 过期 `expected_world_version` | 不提交；要求刷新视图 |
| `rule_refused` / `unsupported_mechanic` | Engine 不接受目标、成本或机制 | 不得凭空写入机械成功；可有已发布的拒绝事件 |
| `engine_committed_response_failed` | Engine 已提交，但响应构建失败 | 通过同一请求身份恢复；不能二次执行 |
| `reconciliation_required` | 不确定 Engine 是否已提交，回执不可取得 | 暂停影响该状态的操作；人工/受控恢复 |
| `world_transaction_failed` | 世界数据库提交异常 | 不产生部分提交；重试按命令回执/去重处理 |
| `agent_unavailable` | NPC 模型调用错误、超时 | 无 NPC 世界副作用；保留观察收件箱，执行明确的故障策略 |
| `observation_projection_pending` | 投影排队、需要受控规则检定或 Agent 尚未消费 | 保留事件及证据/Outbox，不对观察者泄漏秘密或丢事件 |
| `invalid_memory_proposal` | 记忆来源不属于该 NPC、越权编造亲见/引用、错误版本 | 拒绝更新；不污染世界事实或他人记忆 |
| `combat_unrestorable` | 活跃战斗退出，精确机械状态无安全恢复办法 | 不宣称恢复原回合；检查战前重开条件或阻塞 |

特别区分：**Rule refused**、**Engine execution failed**、**Result delivery failed after commit**、**World settlement failed** 四种情况，不能一律映射为“失败，请重试并重新掷骰”。

## 10. 最小公共接口（仅候选名称）

以下 API 是为明确职责提出的**逻辑接口**，不是现有实现或强制 REST 端点；之后由 `MODULE_CONTRACTS.md` 规范正式消息结构和传输方式。

| 接口 | 输入 | 输出 |
|---|---|---|
| `validate_package` | Package 路径/数据 | 完整性检查与 Ruleset Binding 报告 |
| `create_session` | `adventure_id`、包版本、唯一 PC Build/身份、命令 ID | `session_id`、入口 Scene View、初始化回执 |
| `get_scene_view` | Session、Viewer 身份 | 经过可见性过滤的场景事实 |
| `get_npc_view` | Session、`npc_id`、可信请求主体 | 授权的 Profile、Knowledge、Beliefs、Memory、待处理 Observations、合法动作上下文 |
| `get_pending_observations` | Session、`npc_id`、授权的 Host、游标 | 按来源事件序号排序的私有 Observation 批次 |
| `ack_observations` | Session、`npc_id`、已确认激活/消费回执、游标 | 持久化确认位置；不越权修改世界事实 |
| `submit_npc_memory_proposal` | 可信 NPC 激活凭证、源 Observation IDs、受限记忆变更、幂等 ID | 已提交/拒绝的 NPC 私有记忆更新回执 |
| `project_world_event`（内部） | 已提交 Event 与事件时证据、投影版本 | 各观察者独立 Observation / 持久待处理投影 |
| `request_npc_activation`（Host 责任） | NPC ID、场景/交互原因、调用预算 | 获授权 NPC View 与后续行动/记忆提议；**不等于数据库后台任务** |
| `submit_world_command` | 身份/控制者、命令 ID、版本、操作 | 提交/拒绝回执、World Events、新版本 |
| `submit_check_request` | 合法规则参数、GM 裁决来源、稳定操作 ID | Engine 检定 Result + 世界条件消费 |
| `start_encounter` | `encounter_id`、Actors、Rule Binding、起始坐标 | Combat Ref、初始事件或受控拒绝 |
| `submit_combat_intent` | PC/NPC 控制权证明、Actor、Typed Intent、请求 ID | Engine Receipt + Events；必要的 World Reconciliation |
| `apply_engine_result` | 可信 Engine 回执、操作关联 ID | 幂等世界同步及事件 |
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
- **完成证据**：NPC A 无法读到 B 私有 Intent 或秘密；可见争抢各自形成正确 Observation；相同事件重试不重复投影；无论模型认为谁故意抢钱，都不能修改客观世界事实。

### Batch SM-4：Rule Engine Adapter + World Settlement

- 受控战斗开启、战前安全 Checkpoint、权威结果消费、资源归属、世界结算、不可续战退出与错误回执。
- 必要外部 Hazard 和 NPC 显式 Combat Intent API 与 Rule Engine 团队联合验收。
- **完成证据**：同一场战斗结果最多结算一次；失败和已提交响应异常不产生重复消耗；不支持的能力明确报告。

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
| SM-A11 | 战斗结算及重试 | PC/NPC 资源归属正确，世界只同步一次 |
| SM-A12 | 引擎提交后网络中断 | 有回执时恢复；回执丢失时暂停而不是重掷 |
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
| SM-A25 | 战斗 Engine 已提交、世界同步/回执异常 | 依稳定 ID 协调后最多结算一次；不得把已花费资源的战斗当成未开始 |

## 12. 决策登记与仍需确认的实现细节

下列 `SM-01`–`SM-03` 是本轮讨论中用户**明确确认**的 MVP 决策；带“待设计/待验证”的内容仅是实施提案，不能由开发 Agent 擅自冻结。

| 编号 | 议题 | 当前决定 / 约束 | 状态 |
|---|---|---|---|
| **SM-01** | 持久化语言与数据库 | Python + SQLite WAL、单进程优先、短事务、强持久化默认、Repository/Adapter 边界 | **已确认** |
| **SM-02** | 战斗中途精确恢复 | **MVP 不支持**，列入 Post-MVP；须有明确安全检查点、不可伪恢复及战后可靠结算 | **已确认** |
| **SM-03** | 多 Agent 共同感知与记忆 | WorldEvent → Perception → per-Actor Observation → 按需 NPC 激活；Sub-agent 解释 Memory、State Machine 保存/校验 | **已确认基础架构** |
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
| S14 | 战前 Checkpoint 可重开资格与 Engine 协调 | 不承诺所有崩溃都能自动重开，存在不确定提交则阻塞 | 待技术验证 |

---

## 13. 文档治理与下一步

### v0.2 相对 v0.1 的修订摘要

1. 将 Python + SQLite WAL 单进程持久化及短事务锁纪律登记为 **SM-01 已确认**。
2. 将“活跃战斗跨进程精确恢复”明确移出 MVP，补充安全战前 Checkpoint、战后 Settlement 和未知提交状态保护（**SM-02**）。
3. 新增 `WorldEvent`、`ObservableActionStarted`、`ObservationRecord`、`NPCMemoryRecord`、`AgentActivation` 的权威边界与按需调用路径（**SM-03**）。
4. 通过 A/B 争抢金币明确私有 Intent 不可泄漏、事件时感知与游戏排序不等同数据库提交顺序。
5. 扩展合成验收 SM-A15–SM-A25，覆盖视角、主观推断、幂等、掉线/重试和 NPC 内存隔离。


- 此文档只给出 State Machine 运行时架构与状态权威边界；**不替代**项目总架构 `ARCHITECTURE.md`、Agent 内部设计 `AGENT_ARCHITECTURE.md` 或正式跨模块消息契约 `MODULE_CONTRACTS.md`。
- 发现本架构与 `MVP_SCOPE.md` 已确认决定冲突时，以已确认的 MVP Scope 为准，并在审阅中提出修改，不擅自改动产品范围。
- 公开仓库只存放通用 Schema、原创示例和程序代码；完整 First Blush 内容、地图与实质性转写继续留在合法权限下的本地私有资料中。
- **下一文档建议**：`AGENT_ARCHITECTURE.md`（DM 与 NPC Sub-agent 的边界、Context Projection、Intent / Proposal、记忆与调用预算），随后 `MODULE_CONTRACTS.md` 冻结跨模块消息。完成总体架构审阅后再整理根目录 `README.md`。

**本阶段最重要的完成标准不是“状态模型有多少类”，而是一个 Session 能在不重复执行规则、不泄漏 NPC 秘密、不重置场景的前提下，可靠地从剧本初态走到已持久化的结局。**
