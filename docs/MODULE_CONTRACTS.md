# Agentic TRPG — Module Contracts（MVP）

> **版本：** v0.3 / Draft for Review
>
> **日期：** 2026-10-10
>
> **性质：** 跨仓库目标接口契约草案；**不是已实现 API**
>
> **归属仓库（建议）：** `agentic-trpg/agentic-trpg/docs/MODULE_CONTRACTS.md`
>
> **依据：** [ADR-001](./ADR-001-UNIFIED-STATE-OWNERSHIP.md)（Accepted）、[MVP Scope](./MVP_SCOPE.md) v0.7、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.2、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.5、[Agent Architecture](./AGENT_ARCHITECTURE.md) v0.5
>
> **历史代码核对基线（沿用 v0.1，本轮未重审 Engine）：** `agentic-trpg/agentic-trpg@4190833`；`agentic-trpg/trpg-rules-engine@64dd920`
>
> **标记：** `[DECIDED]` 已有架构决定；`[PROPOSED]` 本文推荐、待评审；`[OPEN]` 需要进一步决策；`[NOT IMPLEMENTED]` 不可宣称现有代码已有

## 0. 用途与冻结策略

本文定义 Agent Host、State Machine、Rule Engine、Perception、NPC Evaluation、DM Narration 与 Adventure Package 的交接边界。优先冻结**最小可实施的 State Machine ↔ Rule Engine 垂直闭环**；其余模块先定义最小跨模块契约和安全边界，避免过早扩大实现面。v0.3 澄清 SM 领域职责、Host 运行时边界、统一 Evaluation Result 与内部 Processing Completion；§2–§6 的 P0 Typed Command、RuleEvaluationRequest / Result、StateDelta、RNG、Atomic Commit 契约保持不变，示例 `module-contracts/0.1` 不是文档版本遗漏。

**必须满足的不变量 `[DECIDED]`：**

1. State Machine 是同一 Game Session 内 World、Character、Combat、RNG、NPC 持久认知的**唯一权威状态持有者与最终提交者**。
2. Rule Engine 负责规则求值，不能持有跨请求的独立权威战斗状态，不能直接提交数据库。规则求值内部允许临时可变数据结构。
3. `evaluation.status == "accepted"` 不等于 `commit.status == "committed"`；拟议事件不得提前发布为 WorldEvent。
4. Agent 提交的是意图或提议，不是 HP、骰点、资源支付等机械事实；Narrator 消费已提交、经授权的事实。
5. 可重试、确定性、版本和授权均在可信系统边界实现，不能仅依赖 LLM 自律。
6. 单数据库 SQLite + WAL + 短事务是 MVP 方案；**不得在 SQLite 写事务内等待 LLM 或长时间的 Rule Evaluation**。
7. NPC 只有一份 Persistent State；Interactive 活跃期间独占该 NPC 的 LLM 主观认知/自主行动，Background 一次性推理不需要 Interactive Agent Context。新消息/接口均为 `[PROPOSED; NOT IMPLEMENTED]`，架构原则确认不等于 API 已实现。

8. SM 创建/批准 Evaluation Task、管 Gate / 模式 / Observation Completion；Host 仅 LLM Runtime，不持久管理权威游戏状态或完成结果。

**状态机承担游戏领域逻辑、权威状态与合法性/权限/事务边界，不执行 LLM 主观推理、不管理物理模型 Context，也不重新实现 D&D 机械规则。**

## 1. 实际代码基线与迁移缺口

| 位置（已核对 main） | 当前事实 | 对契约的影响 |
|---|---|---|
| `dnd5e_engine/orchestrator.py` | `_LiveCombat` 持有 Initiative、Combatants、RNG、Round、Effects、Areas、Object State 及很多 sidecar | 需要完整状态依赖盘点，不能只迁移 HP/Turn |
| `orchestrator.py` | 公开 `start_combat`、`submit_player_intent`、`advance_monster_turn`、`end_combat` | 目标 `evaluate(...)` 尚未实现 |
| `orchestrator.py` | `PlayerIntent` 是严格类型化的动作输入；目前 `submit_player_intent` 主要是玩家入口 | 应优先复用 Intent schema / resolver，而非重写动作语义 |
| `orchestrator.py` | `_execution_transaction` 深拷贝 `_LiveCombat`、缓存事件并回滚 `random.Random` 状态 | 可复用规则执行路径；**不可**将其误认为 SQLite 跨模块原子提交 |
| `orchestrator.py` | 怪物回合由 `advance_monster_turn` 内部选策略后执行 | MVP 要求**至少一条**敌方 NPC Sub-agent 的显式 Combat Intent 路径；当前公共入口不足以证明支持 |
| `orchestrator.py` | Reaction 以预设触发为主，而非在解析中暂停等待人工选择 | 可暂停的 `needs_choice` 需作为新协议，不可冒称已有 |
| `nat20_bridge/state.py` / `combat_execution.py` | CombatHandle、事件及重试 Receipt 存于 Bridge 进程内；请求指纹与 `request_id` 已有基础机制 | 可复用概念，不可用 Bridge 进程内缓存作为新 State Machine 的权威持久回执 |
| `outcome.py` / `results.py` | `CombatOutcome` 是战斗关闭时的结果投影，并非每一步的完整 Delta | 新契约不得用 `CombatOutcome` 替代逐命令 StateDelta |

以上沿用 v0.1 的历史代码审阅基线，本轮仅同步架构文档，未重新验证 Engine 现状，也不是完整规则审计。`_LiveCombat` 各字段的 authoritative / derived / ephemeral 分类必须在实施前补充验证。

## 2. 统一标识、版本和契约通则（P0）

### 2.1 规范标识 `[PROPOSED]`

- `session_id`：Game Session 稳定 ID。
- `command_id`：由调用方/可信 Host 生成、在 Session 内唯一的幂等键；同一键不可用于不同命令内容。
- `actor_id`：游戏世界中的实际行动者，与 `principal_id`（发起调用的账户、Host、NPC Agent 身份）区分。
- `world_version`：该 Session 权威状态提交序号；每次**发生权威状态变更**的成功事务单调递增。
- `component_versions`：可选的对象/Combat/Character 局部版本，用于低冲突的读写集校验；MVP 可以仅使用全局 `world_version` 进行保守 OCC。
- `event_seq`：Session 内严格单调递增的**已提交**事件序号。
- `ruleset_binding`：不可歧义的规则版本、数据修订/hash 以及 Evaluation Adapter 版本。
- `schema_version`：明确的消息格式版本（例如 `module-contracts/0.1`）。

所有对外 ID 与关系引用都必须遵守 Type/Namespace 校验，不能由 Agent 自选数据库路径或可信身份。所有命令以稳定规范化序列化（Canonical JSON）生成 `command_fingerprint`；建议包括 `command_type`、`actor_id`、动作 payload 及必要的授权/规则上下文绑定，排除纯传输重试头。具体 canonicalization 算法与版本应在实现前冻结。

### 2.2 幂等语义 `[DECIDED + PROPOSED]`

按 `(session_id, command_id)` 在 State Machine 的**持久数据库**中去重：

- **相同 Fingerprint、已提交：** 返回原 `CommitReceipt`，不重新掷骰、不重复扣资源、不重复发事件。
- **相同 ID、不同 Fingerprint：** `idempotency_conflict`；不执行。
- **首次请求，尚无终态：** 可进入求值；必须解决并发重入（唯一约束 + 原子 claim / 提交校验），不能只在内存中判断。
- **已完成的确定性拒绝：** 可记录原 `RejectionReceipt`；变更输入需要新 `command_id`。
- **网络中断，是否提交未知：** 调用 `get_command_receipt(session_id, command_id)` 查询，**不可**简单改用新 ID 重试。

`principal_id` 和 `actor_id` 的绑定在可信端校验；Replay 不能突破当前授权策略。

## 3. Host / Agent → State Machine：Typed Command（P0）

### 3.1 结构 `[PROPOSED]`

```yaml
schema_version: module-contracts/0.1
session_id: ses.example
command_id: cmd.example.001
principal_id: npc-agent:guard-a        # 经 Host 认证；不能信任客户端自称
actor_id: npc:guard-a
command_type: combat.intent           # 封闭枚举；也支持 world.interact 等
expected_world_version: 27
payload:
  intent_type: attack                 # 复用/映射现有 PlayerIntent 的受支持字段
  target_id: char:hero
  stat_block_action_id: spear
```

命令分两条路：

1. `world.*`：场景、物品、任务、有限世界流程等，由 State Machine 校验固定的声明式操作及事件条件；若需机械计算则转 Rule Engine。
2. `rules.*` / `combat.*`：State Machine 读取可信 Snapshot、Pinned Ruleset 和 RNG，调用 Rule Engine Evaluation API，最后验证与提交。

**最低权限规则：** NPC Agent 只能控制绑定的 NPC、看到权限投影的目标、提出有限 Intent。DM Planner 可以请求合法的 GM Adjudication，却不能伪造已提交结果。Narrator 没有任何写权限。Engine 只接收 Host/State Machine 可信字段，而非任意 Prompt 输出。

## 4. State Machine → Rule Engine：RuleEvaluationRequest（P0）

### 4.1 示例结构 `[PROPOSED; NOT IMPLEMENTED]`

```yaml
schema_version: module-contracts/0.1
operation_id: op.example.001
session_id: ses.example
source_command_id: cmd.example.001
actor_id: npc:guard-a
operation_kind: combat.intent
ruleset_binding:
  ruleset_id: dnd-2024-srd-5.2.1
  data_revision: sha256:<pinned-data-hash>
  evaluator_version: <code-or-build-revision>
state_snapshot:
  snapshot_schema_version: combat-snapshot/0.1
  world_version: 27
  combat_id: cmb.example
  character_state: { ... }     # 可信受限投影，不是 Agent 可写 JSON
  combat_state: { ... }        # 必须覆盖本次求值的完整状态依赖
  relevant_world_state: { ... }
  read_set: [combat:cmb.example, actor:npc:guard-a, actor:char:hero]
rng_context:
  algorithm: python-mt19937-v1    # 仅示例；算法和状态编码需明确冻结
  stream_id: main
  stream_version: 27
  state_ref: <serialized-rng-state>
typed_intent:
  intent_type: attack
  target_id: char:hero
  stat_block_action_id: spear
```

**约束：** `state_snapshot` 必须包含本次规则执行需要的完整依赖闭包，或清楚地声明尚不支持该操作。不能在执行中偷偷读取 Engine 旧有权威 `_LiveCombat` 注册表。`ruleset_binding` 的 hash / revision 不匹配时 fail closed。`rng_context` 是已授权的显式输入；Engine 不得从进程级全局随机状态自行掷骰。

### 4.2 Character / Combat Snapshot 最低覆盖 `[PROPOSED]`

| 类别 | MVP 必须建模的权威语义（字段名未冻结） |
|---|---|
| Character | HP / Temp HP / Death Saves、能力与必要规则投影、资源池与法术位、物品及数量、装备、可用动作来源 |
| Combat | Combatant roster、Initiative 排序、Round / Current Turn / Phase、Alive / KO 等、行动/附赠行动/反应、每回合移动剩余、Position / Reach / Topology |
| Effects | Conditions、Concentration、Active Effects、来源、剩余持续时间、区域/持续效果、合法撤销或过期条件 |
| Limited Uses | 消耗型怪物动作、Recharge、Legendary Actions/Resistances、额外攻击计数、Class Feature / Item Charges 等 |
| World context | 必需场景、对象、障碍、光照、遮蔽、环境规则、目标关系及版本 |
| RNG | PRNG 算法/序列化版本、Stream、位置/状态、版本 |
| Continuation | 尚未结束且合法的操作/选择窗口；若该语义不支持则必须显式 `unsupported` |

上述为**语义覆盖清单**而非现成 `CombatState` 类型。实际 `_LiveCombat` 包含更多 sidecar；其中可能具有规则影响的内部状态也必须纳入快照或重建为可验证的派生状态。应建立字段级映射表，并按新旧行为一致性测试验收。

## 5. Rule Engine → State Machine：RuleEvaluationResult（P0）

### 5.1 统一结果 `[PROPOSED; NOT IMPLEMENTED]`

```yaml
schema_version: module-contracts/0.1
operation_id: op.example.001
source_command_id: cmd.example.001
input_world_version: 27
input_ruleset_revision: sha256:<pinned-data-hash>
status: accepted       # accepted | rejected | needs_choice | unsupported
read_set:
  - ref: actor:npc:guard-a
    version: 27
  - ref: actor:char:hero
    version: 27
state_delta:
  operations:
    - kind: resource.consume
      owner_id: npc:guard-a
      resource_id: action
      amount: 1
    - kind: actor.hp_delta
      target_id: char:hero
      amount: -4
  preconditions: [...]        # 显式、可验证的先决条件
proposed_events:
  - type: combat.attack_resolved
    actor_id: npc:guard-a
    target_ids: [char:hero]
    mechanical_details: {...}
rng_transition:
  stream_id: main
  input_version: 27
  draws: [...]                # 足够审计；具体 wire format 待冻结
  next_state_ref: <serialized-rng-state>
choice: null
error: null
```

规范约束：

- `accepted`：**求值已完成且可提交**，包含完整 Delta + Proposed Events + RNG Transition + 读写集。可以表达一次攻击**未命中**或豁免**成功**——这些属于已发生的合法机械尝试，不能误归类为 `rejected`。
- `rejected`：请求在可安全拒绝的规则边界不予执行；不提交世界变化、机械事件或权威 RNG 进度。若规则允许失败后扣费/触发事件，应输出 `accepted` 并体现完整成本与事件。
- `unsupported`：当前 Engine 未提供该规则语义；**禁止静默降级为假成功**。
- `needs_choice`：要求调用者在执行前补充结构化选择（详见 §8）；除明确批准的 PendingOperation 记录外，不提交部分机械结果。
- Engine 的 `proposed_events` 没有权威 `event_id` 或 `event_seq`；由 State Machine 在事务中分配。
- State Machine 负责检查 Schema、权限、读写范围、版本和不变量。不得接受任意 JSON Patch/任意 SQL 路径更新。

### 5.2 StateDelta：受限、原子、可测试 `[PROPOSED]`

建议首版封闭 Operation Union（具体名称审阅后冻结）：

| 类别 | 典型 Operation | 关键检查 |
|---|---|---|
| HP / 战斗 | `actor.hp_delta`、`actor.temp_hp_set`、`actor.death_state_update` | 目标合法、边界、相关效果可追溯 |
| 资源 | `resource.consume` / `resource.restore` | 资源确属 `owner_id`，数量合法，无负库存 |
| 道具 | `inventory.consume` / `inventory.transfer` | 唯一物品/堆叠数量、来源和目标所有权 |
| 位置 | `combat.move_actor` | 场景位置与占位不变量、与引擎结算一致 |
| 回合 | `combat.turn_update`、`combat.action_budget_update` | 当前 Actor / Phase / Turn Serial 一致 |
| 效果 | `effect.upsert` / `effect.expire`、`condition.update`、`concentration.update` | 生命周期与来源一致；多个目标处理完整 |
| 特殊资源 | `combat.limited_use_update` / `combat.reaction_state_update` | Recharge/Legendary/Reaction 按规则写入 |
| 事件/任务 | 通过受信世界操作提交 Quest / Object / Scene 变化 | 不允许 Engine 任意改写剧情秘密 |

**多 Activity、多个目标与支付归属：** 一个 Evaluation 可以包含多个排序后的 Operation；所有操作构成**单个不可分割的提交单元**。每个 `consume` 必须显式 `owner_id` / `resource_id`，不能根据事件叙述猜测支付者。变化前后的组合必须满足跨实体不变量。MVP 首个黄金用例：**消耗同一 Actor 的一件药水，同时治疗 HP、消耗行动预算并生成相应事件**。

## 6. State Machine Atomic Commit 与 Receipt（P0）

### 6.1 执行时序 `[DECIDED + PROPOSED]`

```text
Typed Command → authenticate/authorize/idempotency lookup
→ obtain authoritative Snapshot + Ruleset binding + RNG
→ Rule Engine.evaluate(request)             [no DB write transaction]
→ begin short SQLite transaction
   → re-check command fingerprint / existing receipt / world_version
   → re-check read-set, permissions, ruleset pin, typed Delta invariants
   → commit StateDelta + authoritative RNG + WorldEvents
   → write durable CommitReceipt + idempotency record + Outbox metadata
→ COMMIT SQLite transaction
→ publish only committed events from Outbox
→ return CommitReceipt / permitted views
```

**OCC：** 如快照过时则不提交；返回 `version_conflict` 或在有界、授权、完整重新取 Snapshot + RNG 的条件下重算。重新执行不能把旧 Delta 套在新世界上。SQLite 使用唯一约束防止不同执行者对同一 `command_id` 双重提交。全局版本作为保守 MVP 默认；以后再优化精细读写集。

### 6.2 CommitReceipt `[PROPOSED]`

```yaml
schema_version: module-contracts/0.1
session_id: ses.example
command_id: cmd.example.001
command_fingerprint: sha256:<canonical-request-hash>
status: committed             # committed | rejected | conflict | pending_choice
world_version_before: 27
world_version_after: 28
committed_event_ids: [evt.001, evt.002]
rng_version_after: 28
result_ref: result.cmd.example.001
```

`committed` 只可能由 State Machine 在数据库事务成功后形成。**响应发送失败不意味着未提交**；任何查询或重试必须能找回该持久回执。`rejected` / `conflict` / `pending_choice` 的详细字段和数据库版本推进策略另行实现时固定；禁止把拒绝事件当成已发生的伤害事件。

### 6.3 RNG `[DECIDED + PROPOSED]`

- 一条 Session RNG 流足够作为 MVP 默认，可在架构上保留 `stream_id`。算法/编码及 ruleset/evaluator 版本固定，便于确定性测试。
- 拒绝、版本冲突、未提交求值、异常中断均不得推进**权威 RNG**。
- `accepted` 的机械尝试即使未命中，合法消耗的骰点仍随完整提交写入；不可将“动作结果失败”误判为“执行拒绝”。
- 同一已提交 `command_id` 返回原 Receipt，不能重掷。发生重算只能从重新读取的**当前权威 RNG** 开始。
- 不以 RNG seed 单独承诺跨 Engine 版本精确 replay；还要保留 PRNG State、Ruleset/Data hash、Evaluator 版本和命令/事件序列。

### 6.4 原子性与故障 `[DECIDED]`

`StateDelta + RNG + Committed Events + Durable Receipt + Outbox` 同属一个 SQLite 事务。向 LLM、NPC 或 UI 发送内容是提交**之后**的派生行为，不能参与数据库事务。发出失败由 Outbox 幂等补偿，不回滚成功的游戏事实。

## 7. WorldEvent → Perception → NPC Evidence（P0/P1）

### 7.1 事件事实与可见性 `[DECIDED + PROPOSED]`

`CommittedWorldEvent` 建议字段：`session_id`、`event_id`、`event_seq`、`source_command_id`、`event_type`、`actor_id`、`participants`、`state_version`、`game_time`、可信事件时刻的 `occurrence_context`（Scene、位置、遮挡/光照/可听性、可见信息等级等）、受限事件 payload。

- `proposed_events` **不是** WorldEvent；只有 Atomic Commit 后才获得 event_id/event_seq。
- `Affected NPC Discovery` 使用事件发生时的位置及足够的证据元数据，生成每个 NPC 的 `ObservationRecord`；不能以 NPC 当前所在位置倒推历史目击。
- `EventObservation`（过去亲眼看到/听到事件）与 `CurrentPerceptualView`（现在能看到的世界）是两个不同 API；一个 NPC 看到门开着不代表知道谁开门。
- Projection 必须按调用主体的可见性和秘密级别过滤。NPC/玩家/Narrator **绝不可**收到全量世界真相。

### 7.2 最小消息 `[PROPOSED]`

```yaml
observation_id: obs.npc.guard-a.0005
observer_id: npc:guard-a
source_event_id: evt.001
source_event_seq: 35
perception_kind: witnessed_event   # witnessed_event | heard_event | other_evidence
observed_content: {...}            # 经 Projection 脱敏的事实，不是完整 WorldEvent
perceived_at_game_time: 1023
observation_schema_version: observation/0.1
```

`CurrentPerceptualView` 则应有 `observer_id`、`view_world_version`、`view_time`、经权限投影的实体/环境/不确定性描述，但不伪造 `source_event_id`。

### 7.3 Reliable Observation Delivery `[PROPOSED; NOT IMPLEMENTED]`

在 Commit 同事务内记录待投递 Event / Projection Job；投递至少一次，State Machine Perception 按 `(observer_id, event_id, projection_version)`（或等价唯一键）幂等写 Observation。NPC 不在线时仍保存应收到的 Event Observation 或可靠重放证据。**原始事实、感知记录、角色信念三者分别持久存储**；`Belief` 不等于 World Fact。

- `observation_id` 稳定，按 NPC 提供顺序可核验的 Delivery Cursor；相同事件多个 Observation 的次序需有稳定 tie-break。分页返回投影完成水位/等价完整性证明，不能因较早事件还在 Outbox 而让消费跳过它。
- 读取 Cursor / Host 已追加 Context 位置与 SM 内部 Processing / Completed Cursor 分离。读取、追加或模型返回不等于处理完成；SM 仅按持久终态推进连续完成前缀，见 §9.6，不要求 Host 额外 ACK。
- SM 为待处理 Observation 批次建立稳定 `observation_work_id`、任务及幂等处理记录；重复投递不创建第二份逻辑工作。合并批次不能重复占用尚有任务的同一观察；具体索引/表结构未冻结。
- Mode Routing、Gate 领域策略、证据保留和任务完成由 SM 管理；Host 按授权请求执行 Context 追加或模型调用。失败不随 Context 释放而丢失证据。

## 8. Pending Choice / Reaction / Continuation（P0 语义，MVP 限制实现）

**当前限制已验证：** Rule Engine 现有 Reaction 流程主要是提前 `ready`，不提供完整的“解析到一半停下并等待 NPC/PC 选择”的公共可序列化 continuation。

### 8.1 MVP 首选 `[PROPOSED]`

优先采用**求值前选择**：Rule Engine 返回 `needs_choice`，但不消耗 RNG 或机械资源；State Machine 保存**独立的 PendingOperation 元数据**（不是对机械求值部分提交），Host 向有权限的角色请求选择，随后发起新的 `choice.respond` 命令附 `pending_operation_id` 与 `selected_option_id`。State Machine 验证主体、原命令、版本、有效选项及过期/取消状态，再基于新鲜 Snapshot 重新求值与完整提交。

`PendingOperation` 至少包含 `pending_operation_id`、`source_command_id`、`actor_id`、`authorized_responder`、`choice_kind`、`allowed_options`、`input_world_version`、`status`、`creation_time`、`expiration_policy`、`ruleset_binding` 和唯一幂等字段。`choice.respond` 不能任意覆盖原始 Intent。

### 8.2 必须明确不支持的场景 `[OPEN]`

某些 Reaction 在掷骰、命中或部分效果发生后才能决定是否响应。上述**求值前选择**方案无法普遍正确表达这类中途暂停机制。对这种规则路径：

- MVP 可以沿用已验证的**预先声明 Reaction 策略**，但不得声称与所有 SRD 交互式选择完全等价。
- 如果剧本的黄金路径必须支持中途 Reaction，需先设计可持久化的执行检查点、已消耗骰点与信息窗口，再决定最小实施范围。
- 绝不只持有进程内部 `_LiveCombat` 句柄作为唯一 continuation，也不在外部等待时占住 SQLite 写事务。
- `needs_choice` 不能偷偷提交已经结算的伤害，也不能凭 Narrator 文本作为 continuation 状态。

活跃战斗异常退出后的**精确续玩仍为 Post-MVP**。MVP 需保留明确的 `combat_interrupted`/停止受理/安全重新开始策略，不能悄悄恢复战前状态并覆盖已提交结果。

## 9. Agent Host / NPC Evaluation / Memory / DM（P1 接口边界）

本节新增消息、字段、接口和内部处理模型均为 **`[PROPOSED; NOT IMPLEMENTED]`**；不是现有 HTTP Endpoint、Python 类型或数据库表。职责原则已确认，具体字段类型、约束和版本仍待审阅。

### 9.1 领域状态与模型运行时 `[DECIDED]`

| 概念 | 内容 | 所有者与边界 |
|---|---|---|
| Persistent NPC State | 唯一 Identity、Personality、Memory、Belief、Relationship、Goal、Plan、Runtime State（Schedule / Current Activity） | State Machine 权威持久保存 |
| Evaluation Task / Mode / Processing | 任务创建与授权、模式资格和 epoch、Observation Work、Gate 领域触发与保留、完成状态、游戏时间日程 | State Machine 游戏领域逻辑；不执行 LLM 主观推理 |
| Interactive Context | NPC 专属可复用交互输入、增量 Observation、Compaction | Host 创建、复用、释放和调用；不是权威状态 |
| Background Context | 当前授权 NPC View、相关认知与新 Observation 的一次性输入 | Host 构建并释放；不创建、恢复或激活 Interactive Agent |
| LLM Runtime | Prompt / Builder、Token Budget / Cache、模型队列、超时重试取消、Tool Adapter、调用日志/延迟/Usage | Host 基础设施；仅临时 Runtime Metadata，不持久决定游戏任务完成或行为结果 |

**统一逻辑信息流：State Machine → Agent Host → NPC LLM → State Machine。** SM 创建或批准任务，提供授权视图、观察、任务信息及可信身份绑定；Host 组织 Context / Prompt 并调用模型，传输结构化结果及工具请求；SM 是逻辑提交目标，验证领域合法性、调用 Rule Engine 并事务提交。Host 将权威回执反馈后续调用，不接管状态或领域决策。§2–§6 的可信 Host / 调用方描述指受控传输及命令构造，最终 Actor 权限、领域合法性与提交仍由 SM 检查。

`inactive` 是没有 Active Interactive Context 的调度状态，不是第三种 Evaluation Mode。Interactive 活跃（包括暂时无在途请求）期间，该 NPC 所有需要 LLM 的 Memory、Belief、Relationship、Goal、Plan 和自主行动判断均由当前 Interactive LLM 完成；不额外调用 Gate / Background / Memory / Cognition LLM。新观察按序追加，在途请求的新输入排队，不修改运行中请求或物理 KV Cache；重大事件由 SM 批准下一次 Interactive Evaluation。

Inactive NPC 才进入 SM 的 Lightweight Gate 领域策略：确定性判断可选择 Safe Retention / No-op 或创建 Background Task。若需轻量模型，Host 执行推理并返回非权威分类候选，SM 验证、采用并决定后续任务；轻量模型失败不丢失关键证据。Memory / Cognition / Behavior Trigger 可联合判断，不强制多个模型；Jev 仅可替换候选。确定性证据记录、已确认承诺与必要安全处理不受 LLM 独占限制。

### 9.2 标识与可信关联 `[DECIDED]`

| 标识 | 含义与所有者 |
|---|---|
| `session_id` | SM 管理的 Game Session |
| `npc_id` | 该 Session 内的稳定 NPC 身份 |
| `evaluation_id` | SM 创建或授权的一次逻辑 NPC Evaluation Task |
| `invocation_id` | Host 的一次具体模型调用尝试，属于 Runtime Observability |
| `context_id` | Host 管理的物理/逻辑模型 Context 引用 |
| `mode_epoch` | SM 管理的协调版本，用于模式切换及过期提交资格校验 |

一次 Evaluation 可包含多次 Invocation；一个 Interactive Context 可服务多次 Evaluation。`invocation_id`、`context_id` 不要求成为 SM 提交接口的必填字段，可作为可选追踪信息。**`evaluation_id` 本身不是认证凭证**：SM 仍核验可信 principal、Session/NPC 绑定、授权范围、epoch、版本和幂等性。身份、模式、权限及版本来自受控任务/调用上下文，不信任模型自报。

### 9.3 跨模块请求与接口 `[PROPOSED; NOT IMPLEMENTED]`

| 方向 / 候选接口 | 输入 | 输出与权限约束 |
|---|---|---|
| SM → Host `NPCEvaluationRequest` | SM 授权 Task、NPC View / Observation、身份绑定及版本 | Host 执行指定模式的模型评估；不自己创建领域任务 |
| Host → SM `get_npc_view` / `get_event_observations` / `get_current_perceptual_view` | 可信 principal、Session/NPC、受限读取 Cursor / 范围 | 授权视图、稳定有序观察和投影水位；读取不完成工作 |
| Host → SM `submit_npc_update_proposal` | 同一 `NPCEvaluationResult` 加可信 Evaluation 关联的 `NPCUpdateProposal` 信封 | SM 验证并记录私有更新、Dialogue 处置及 Action Command 回执 |
| Host → SM 统一 Typed Command（§3） | 受控调用上下文绑定的受限 Action Intent / Tool 请求 | SM 验证 Actor、前提、版本，必要时 Rule Evaluation 后原子提交；不新增 NPC 动作执行协议 |
| Host → SM Gate 分类候选 / Runtime 状态反馈 | 授权分类任务关联、非权威分类或超时/取消/Context 可用性信号 | SM 决定采用、重试、模式资格和终态；不是 Host 的完成声明 |

`ack_observations()` 不是 MVP 必需公共接口；也不要求 Host 调用独立 disposition / mode-epoch 写接口。SM 内部创建 Task、协调模式、处置观察和推进完成状态；请求交互的 DM/UI、Host Runtime 信号仅作为输入，不能自行指定权威 epoch 或宣布工作完成。具体函数名与传输形式待设计。

`NPCEvaluationRequest` 替代旧 Host 内部 `RequestNPCEvaluation` / `RequestNPCCognition` 概念，涵盖可选认知与行为决策；与 P0 `RuleEvaluationRequest` 不同，SM 发送请求不表示 SM 执行模型推理。Background 请求示例：

```yaml
schema_version: npc-evaluation/0.1  # 候选版本，不改 P0 schema
session_id: ses.example
npc_id: npc:guard-a
evaluation_id: eval.guard-a.bg.005
observation_work_id: work.guard-a.005
mode: background
mode_epoch: 4
reason: significant_observation
source_observation_ids: [obs.npc.guard-a.0005]
input_world_version: 27
expected_npc_state_version: 8
authorized_npc_view_ref: view.guard-a.008
# 可信主体/权限通过受控调用上下文绑定；不交给 LLM 自行生成
# context_id / invocation_id 由 Host 运行时管理，不是任务身份
```

Interactive 请求可复用既有 Context；首次交互由 SM 批准模式后 Host 创建。Background 从新鲜授权 View 建一次性 Context。Host 的模型执行队列、Context Build / Append / Release、`dm.plan` / `dm.narrate` 仅是运行时操作或逻辑角色，不据此要求网络服务。SM 内部 Perception、Evidence、Gate 与游戏日程也不成为独立模型服务。

### 9.4 统一原始结果与可信提交信封 `[PROPOSED; NOT IMPLEMENTED]`

两种模式遵守预定义的同一或兼容版本 `NPCEvaluationResult` Schema；可以用不同 Prompt、Context、模型。**LLM 生成符合 Schema 的非权威数据，不自行定义 Schema。** 概念结构如下，字段类型、元素约束和版本尚未冻结：

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

所有字段均可为空；不要求每次改变记忆/信念或产生行动。Background 可独立产生 Action Intent，通常没有对白；Dialogue 仍使用同一字段和发布约束。原始 Result 不含可信 Session/NPC/Evaluation/权限/模式/版本。

`NPCUpdateProposal` 仅是提交信封，其 `result` **就是上述 NPCEvaluationResult**，不另定义 `response.updates` 等分叉协议。下例展示一次 Interactive 结果，信封元数据由受控任务关联填入：

```yaml
schema_version: npc-evaluation/0.1
session_id: ses.example
npc_id: npc:guard-a
evaluation_id: eval.guard-a.005
observation_work_id: work.guard-a.005
proposal_id: proposal.guard-a.005
mode: interactive
mode_epoch: 5
based_on_world_version: 27
expected_npc_state_version: 8
source_observation_ids: [obs.npc.guard-a.0005]
result:
  dialogue: {text: "我会去查看，请留在这里。", intended_audience: [char:hero]}
  memory_updates:
    - {kind: episodic, text: "我听到院子传来求救。", epistemic_status: observed, source_observation_ids: [obs.npc.guard-a.0005]}
  belief_updates:
    - {text: "院子里可能有人需要帮助。", epistemic_status: inferred, source_observation_ids: [obs.npc.guard-a.0005]}
  relationship_updates: []
  goal_updates: []
  plan_updates: []
  action_intents:
    - {command_type: world.interact, payload: {operation: move, destination_id: scene.yard}}
# invocation_id / context_id 可选追踪，不是提交必填或认证依据
```

SM 选定一份可提交候选并在执行副作用前持久保存其内容、稳定 Proposal / 子操作 / Command ID 与指纹；Host 只适配传输。私有更新只能影响本 NPC，保留来源及 `observed / told / inferred` 标签，不修改 Identity 绑定、他人认知或 World Fact。已确认承诺才可 Recall，未执行动作不能记为成功。Dialogue 发布需验证受众、可观察事件与叙事权限。

Action Intent 复用 §3 Typed Command；SM 验证并按需调用 Engine，最终走 §6 Commit。私有更新成功不代表行动成功；版本前移后，行动读取新快照并重验，不直接套旧 Delta。Schedule / Policy 也走统一命令路径，不能计作敌方 LLM Sub-agent 战斗验收。

### 9.5 SM 模式协调、并发与过期结果 `[PROPOSED; NOT IMPLEMENTED]`

SM 按 `(session_id, npc_id)` 持久管理模式资格、Task 与 `mode_epoch`，使同 NPC 的主观评估及结果处置有序；Host 按授权请求安排运行时调用，不靠 Host 内存锁作为权威保证。

默认 Background → Interactive **取消并拒绝旧结果**：

1. SM 停止新 Gate / Background 授权，短事务 CAS 推进 epoch，撤销旧任务及派生 Action Command 的未提交资格。
2. Host 尽力取消模型；无法取消的物理调用可结束，但 SM 拒绝迟到旧 epoch 输出。正确性不依赖 provider 取消成功。
3. SM 对账已持久 NPC Update / Command Receipt：切换前已提交结果保留，未提交候选终态拒绝；不以新 ID 重放已完成副作用。
4. SM 把未完成工作及已有回执关联到当前模式的新授权任务；Host 基于新鲜 NPC View 与授权观察创建/复用 Interactive Context。需要新决定交当前 Interactive LLM，不让旧 Proposal 覆盖新认知。

Interactive → Inactive 同样由 SM 完成或撤销任务、对账并推进 epoch，再允许 Gate / Background；Host 释放 Context 并报告运行时状态，不自行改权威模式。重启先从 SM 持久状态撤销过期资格/对账，再重建 Context。版本冲突先查回执，SM 决定有界重新评估；全部模型调用在 SQLite 写事务外。

### 9.6 SM 内部 Observation Processing Completion `[PROPOSED; NOT IMPLEMENTED]`

- SM 维护 `ObservationProcessingStatus` 与稳定 Work / Task 关联；模式切换、重复投递和 Invocation 重试不创建可重复副作用的新工作。同键不同指纹拒绝。
- SM 根据持久 Proposal、更新/Dialogue 处置、Command Receipt、Safe Retention / No-op / Rejection 等终态，判断工作是否完成；全空 Result 可记录为明确 No-op。Host 不持久管理此状态。
- 部分操作已提交时保存并复用原回执，只处理未完成义务；取消/冲突后不得重新累加 Memory / Relationship 或重复行动。候选替换保留审计关联，不能覆盖已有回执。
- `needs_choice` 等待续工作须持久保存，工作保持未完成。模型返回、读取、Context Append、模型失败、epoch 撤销本身均不等于工作完成；任务取消只有在相关义务被明确处置或转交后才能判断工作状态。
- SM 可在同一终态事务中更新处理状态，或由持久回执幂等恢复。内部 Completed Cursor 仅前移连续完成且投影水位可证明的前缀，不跨越未投影或未完成项；无需 Host 再调用 ACK 握手。
- 单次提交响应丢失按原 ID 查 SM Receipt；未完成证据不会随 Context 释放丢失。

Memory Persistence 与 Context Compaction 独立：SM 管 Evidence / NPC 认知与处理状态；Host 管模型和 Context。两种 LLM 均可提议 Memory，SM 验证持久化；成功写入不强制 Compact / Rebuild / 重复注入。Compaction 只因 Token、延迟、成本或质量压力触发，摘要不成为权威认知或事实。

### 9.7 State Machine 不可用与恢复 `[DECIDED; implementation NOT IMPLEMENTED]`

MVP 是 Python + SQLite 的本地权威运行时。SM 持续不可用或持久化失败时，Session 停止权威推进，进入暂停、错误或待恢复流程；若无法写库，不能伪称已持久记录暂停。Host 可提示运行时故障、停止模型派发，但不接管状态、不建立影子权威副本或独立游戏执行队列。

恢复依据 SM 已持久状态、任务和事务回执，先核对提交状态再续未完成工作；非战斗 Session 恢复必须支持。战斗中断精确续玩仍为 Post-MVP，沿用 `combat_interrupted` 安全策略。保留单条命令响应丢失时的幂等回执查询，不增加分布式协调系统。

## 10. Adventure Package → State Machine（P1）

最小加载契约 `[PROPOSED]`：

```text
validate_package(package, schema_version, ruleset_binding)
  → ValidationReport（引用完整性、许可/公开边界、Ruleset 存在性、可用操作约束）
initialize_session(validated_package_id, player_pc_config, session_id)
  → SessionCreated（世界/场景/人物/Encounter 初始状态 + pinned package/ruleset revisions）
```

Adventure Package 是**静态**定义和初始化来源；RuntimeState 不写回剧本文件。通用公开仓库只放原创合成 Fixture、Schema、代码、测试；未经授权的 *First Blush* 具体剧情/角色/遭遇与改编材料保留私有，不纳入本仓库的提交。

## 11. 必须统一的错误和状态（P0）

| 错误/状态 | 权威语义 | 状态与 RNG |
|---|---|---|
| `unauthorized_actor` / `forbidden` | 身份或 Actor 控制越权 | 不提交 |
| `schema_invalid` | Typed Command 结构不合法 | 不提交 |
| `unsupported_rule` | Engine 不支持操作 | 不提交 |
| `rule_rejected` | 在合法求值前安全拒绝 | 不提交 |
| `version_conflict` | Snapshot/ReadSet 过时 | 不提交；允许有界重算 |
| `idempotency_conflict` | 同一 command_id 不同指纹 | 不提交 |
| `choice_pending` | 等待已授权的前置选择 | 只允许独立、明确的 PendingOperation 元数据 |
| `committed` | State Machine 已原子提交全部效果 | RNG、状态、Event、Receipt 全部提交 |
| `committed_response_failed` | **已提交**，但传输/叙事失败 | 保留原提交；调用方查 Receipt |
| `internal_error` / `evaluation_failed` | Engine 或 State Machine 意外失败 | 若事务未提交则不改变权威游戏事实；若提交状态未知先查 Receipt |

**禁止混淆：** `miss`、`save_success`、`attack_failed_after_roll` 可能是**合法机械结果**（有 RNG/行动成本），不等价于 `rule_rejected`。当前 Bridge 的事件型拒绝/回执映射需逐路径核对，避免迁移时改变 D&D 语义。

## 12. MVP 验收用例（需自动测试）

1. **Inventory + Mechanics 同事务：** 同一 Actor 使用有限药水；库存、HP、Action Economy、RNG、事件、Receipt 一次提交，任何验证/事务失败全部不写。
2. **确定性求值：** 固定 Snapshot、Ruleset/Data、Evaluator revision、PRNG State 和 Intent，结果与骰点一致。
3. **无副作用拒绝：** 无权限、资源不足、非法目标、未知规则、Schema 错误均不污染游戏状态或 RNG。
4. **合法失败有成本：** 合法攻击未命中仍完整记录允许的 RNG 消耗和回合/行动成本。
5. **重复与冲突：** 相同 `command_id` 只提交一次；指纹不一致拒绝；竞争取同一物品不会出现两个成功 Owner。
6. **提交后掉线：** 模拟 SQLite COMMIT 成功、HTTP 响应丢失，重新查询/重试拿回原 Receipt，事件不重复。
7. **显式敌方 NPC Intent：** 至少一个敌方 Sub-agent 选择其自身受权限约束的战术意图，经 Rule Engine 求值 + State Machine 提交；不是冒用 PC 身份，也不是内置 Monster AI 假装 Sub-agent。
8. **多目标与多 Activity：** 效果、资源支付归属与有序事件都对齐现有行为；失败回滚无“半个目标已受伤”。
9. **感知隔离：** A 目击开门、B 后到只看到门打开；玩家/NPC/Narrator 不得得知无权知道的历史事件或 GM Secret。
10. **记忆与 Context：** 重要 Observation 可持久化而不触发 Active Context 压缩；NPC Evaluation 重试不重复写认知/执行动作。
11. **保存恢复边界：** 无活跃战斗的 Session 重启恢复；中断战斗明确标记，不将部分已提交机械变化悄悄丢弃。
12. **迁移对照：** 与旧 API 在受支持合成用例上逐项比较合法性、目标、资源、伤害、Effect、事件顺序、RNG Draw 数量、拒绝与回滚。

验收使用**公开的原创合成 Fixture**；*First Blush* 端到端场景在独立私有资产中验证。

### 12.1 v0.2 NPC 双模式合成验收 `[PROPOSED; NOT IMPLEMENTED]`

下列是待实现的验收目标，本轮未运行模型或数据库故障测试；对应 Agent §11.3、State Machine §11.2。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A13 | Interactive 新增 Observation | 原 Context 按序追加；只有当前 Interactive LLM 处理，额外 Gate / Background / Memory / Cognition LLM 调用数为零 |
| C-A14 | Active Context 暂时无模型请求，重大事件到达 | SM 批准下一次 Interactive Task，Host 执行请求；在途调用期间新增输入排队，不修改执行中请求/KV Cache |
| C-A15 | 单个 Interactive 响应含 Dialogue、Belief、Memory、Action Intent | 可选更新与行动分别验证；世界事件只有统一 Typed Command 提交后产生；合法全空/no-op 同样可处置 |
| C-A16 | Inactive NPC 经 Gate 一次 Background Evaluation 产生行动 | 无 Interactive Agent Context；同一 NPC 权限与共享命令路径，临时 Context 调用后释放 |
| C-A17 | 低价值 Observation / 轻量模型不可用 | 不调用完整 NPC LLM或按保守策略留待处理；Safe Retention / No-op 有回执，关键证据不丢失 |
| C-A18 | Background → Interactive 与提交竞争 | epoch 变更前的成功提交先对账；变更后旧 Proposal / Action 拒绝，无重复认知/行动或过期覆盖 |
| C-A19 | Model Failure、重复 Observation、版本冲突、完成状态落盘前崩溃 | 稳定 work / Proposal / Command ID 与回执防重复；未完成观察不推进 Completed Cursor、不跳过投影缺口 |
| C-A20 | 任一模式 Memory 持久化成功 | 不强制 Compact / Rebuild；资源或质量压力才触发 Context Compaction |

### 12.2 v0.3 职责与统一协议验收 [PROPOSED; NOT IMPLEMENTED]

以下为待实现的原创合成测试目标；本轮仅静态文档检查。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A21 | SM 创建/批准 Task、采用 Gate 分类 | Host 只运行模型/Context/Tool 传输；领域模式、保留、任务与完成状态归 SM |
| C-A22 | 一 Evaluation 多 Invocation，一个 Context 多 Evaluation | 逻辑与运行时标识分离；Invocation/Context ID 非提交必填，不改变 P0 命令信封 |
| C-A23 | 自报身份/版本、仅 Evaluation ID | SM 核验可信主体、NPC 绑定、授权范围、epoch、版本及幂等，ID 不能认证 |
| C-A24 | 两模式 Result 与可信信封 | 同一/兼容七字段，允许全空；信封 result 原样承载，可信元数据来自受控任务 |
| C-A25 | 无 ACK、部分提交后故障、Pending Choice | SM 从持久终态更新 Completion；回执复用不重复副作用，读/追加/模型返回不完成，等待续项不提前完成 |
| C-A26 | Dialogue 发布与 Background Action Intent | 发布验证受众/叙事权限；行动共享 Typed Command、Rule Evaluation、SM Commit |
| C-A27 | SM 持续不可用、提交响应丢失及恢复 | 停止权威推进，Host 无影子状态/游戏队列；查原 Receipt，恢复非战斗，战斗精确续玩后置 |

## 13. 尚需显式批准或验证的开放问题

| ID | 问题 | 初步建议 / 决策要求 |
|---|---|---|
| C-01 | `_LiveCombat` 哪些字段权威、哪些可推导？ | 先做字段/读写路径 Inventory，生成快照依赖矩阵；这是任何重构前阻塞项 |
| C-02 | Engine 对外 `evaluate(...)` 与 NPC `combat.intent` 的最小 Python Typed Schema？ | 本草案用于语义审阅，字段名称/类型待代码适配论证，禁止先行声称已实现 |
| C-03 | PRNG 状态 wire format 与版本？ | 选定稳定显式编码和提交策略，并测定副作用边界 |
| C-04 | Reaction / Pending Choice 是否允许 mid-resolution pause？ | MVP 默认预先声明；必须逐个黄金用例识别不能等价支持的规则 |
| C-05 | 每个普通怪物是否需要独立 LLM Sub-agent？ | **仍未决定**。但 MVP 必须验证至少一条真正敌方 Sub-agent 显式 Intent 路径 |
| C-06 | 部分规则不支持时如何安全回退？ | `unsupported` 明确拒绝或人工裁决提议；严禁 Narrative 假装规则结果 |
| C-07 | 全局 `world_version` 还是细粒度读写集？ | MVP 全局 OCC 简单安全；预留 finer-grained 版本及 Benchmark |
| C-08 | 活跃战斗崩溃中断后如何避免覆盖已提交结果？ | 明确 `combat_interrupted` 与安全恢复/阻塞协议；精确续玩 Post-MVP |
| C-09 | Schema version、Canonical JSON hash 与 Evaluation Adapter version 怎样固定？ | 测试资产与 ABI 审阅后决定 |
| C-10 | `needs_choice` 的持久性/过期及对外 Receipt 状态？ | v0.1 先冻结正确性边界，具体数据库模型由 SM 实施设计验证 |
| C-11 | Mode epoch / Evaluation 授权关联、Work / Task、处理回执的最小存储/编码？ | 本文确定撤销旧资格及提交时校验语义，字段、CAS 和恢复实现仍待论证 |
| C-12 | Observation Cursor、投影水位、批次合并及内部 ProcessingStatus / Completed Cursor Schema？ | 需证明不跨越未投影/未完成项，明确子操作终态与重入；具体类型待冻结 |
| C-13 | Gate / 两种模式的模型、Prompt、阈值、预算与取消能力？ | Jev 仅候选；通过合成场景测定漏判/延迟/成本，不擅自固定技术选型或 SLO |
| C-14 | NPCEvaluationResult / 可信信封的字段类型、元素约束、版本与错误映射？ | 七字段概念结构及两模式兼容原则已确认；JSON Schema、可信调用绑定和持久任务编码待审阅，不把草案当成已实现 API |

## 14. 建议实施顺序（在本契约评审通过之后）

**Batch 0 — Contract review / State inventory：** 对照 `orchestrator.py`、`types/combat.py` 和现有测试列出权威/派生状态字段、RNG 读写点、Effect 生命周期、NPC Intent 空缺。修复契约歧义，不改大规模业务代码。

**Batch 1 — Evaluation Adapter 最小纵切：** 在测试分支把**一条** `combat.intent`（可以从基础攻击开始）转换为从 Snapshot 输入/结果 Delta 输出的无权威状态评估；兼容旧执行器对照测试，保持旧公开 API 不受影响。

**Batch 2 — SQLite Atomic Commit 最小闭环：** 建 `Session + Snapshot + idempotency + RNG + Delta + Event + Receipt + Outbox` 单事务。完成药水跨领域、重试、冲突和注入失败测试。

**Batch 3 — NPC/Perception & DM 最小集成：** 验证 Interactive 独占与 Inactive Gate / Background、SM 模式协调及内部 Processing Completion；让一条显式敌方 NPC Typed Intent、一次 NPC Event Observation 与 Player-facing Narration 完整通路成功；不要求先实现 Jev 或复杂记忆治理。

**Batch 4 — First Blush 私有冒险集成与 MVP 验收：** 仅在通用闭环可测后导入人工整理的私有 Package；按真实剧本验证完整游玩，不上传受限素材。

### 本文批准条件

- 所有 P0 输入/输出/状态/失败语义没有“谁负责提交”的歧义。
- 提议的字段能对照实际 Engine 数据和代码找到实现路径；不能抽象遗漏充值/资源归属、Reaction、RNG 等状态。
- 一次跨领域操作可在 SQLite **一个原子事务**完成。
- 三种关系严格分开：**Proposal ≠ Evaluation ≠ Committed World Fact**；**Event Evidence ≠ NPC Belief**。
- 明确哪些规则还没有足够的实现证据或必须在 MVP 中降级/拒绝。
- 批准前，本文件始终为草案；不得让 Codex 直接把它当作已实现的公共 API。

## 参考代码（v0.1 历史审阅快照，非当前实现声明）

- [ADR-001](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/ADR-001-UNIFIED-STATE-OWNERSHIP.md)
- [MVP Scope](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/MVP_SCOPE.md)
- [State Machine Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/STATE_MACHINE_ARCHITECTURE.md)
- [Agent Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/AGENT_ARCHITECTURE.md)
- [Rule Engine orchestrator](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/orchestrator.py)
- [Bridge Execution Receipts](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/combat_execution.py)
- [Bridge State](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/state.py)
- [Combat Outcome](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/outcome.py)
