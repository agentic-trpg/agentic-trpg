# Agentic TRPG — Module Contracts（MVP）

> **版本：** v0.2 / Draft for Review\
> **日期：** 2026-10-10  
> **性质：** 跨仓库目标接口契约草案；**不是已实现 API**  
> **归属仓库（建议）：** `agentic-trpg/agentic-trpg/docs/MODULE_CONTRACTS.md`  
> **依据：** [ADR-001](./ADR-001-UNIFIED-STATE-OWNERSHIP.md)（Accepted）、[MVP Scope](./MVP_SCOPE.md) v0.6、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.2、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.4、[Agent Architecture](./AGENT_ARCHITECTURE.md) v0.4\
> **历史代码核对基线（沿用 v0.1，本轮未重审 Engine）：** `agentic-trpg/agentic-trpg@4190833`；`agentic-trpg/trpg-rules-engine@64dd920`\
> **标记：** `[DECIDED]` 已有架构决定；`[PROPOSED]` 本文推荐、待评审；`[OPEN]` 需要进一步决策；`[NOT IMPLEMENTED]` 不可宣称现有代码已有

## 0. 用途与冻结策略

本文定义 Agent Host、State Machine、Rule Engine、Perception、NPC Evaluation、DM Narration 与 Adventure Package 的交接边界。优先冻结**最小可实施的 State Machine ↔ Rule Engine 垂直闭环**；其余模块先定义最小跨模块契约和安全边界，避免过早扩大实现面。v0.2 仅扩展 NPC 模式/Observation/Proposal 边界；§2–§6 的 P0 Typed Command、RuleEvaluationRequest / Result、StateDelta、RNG、Atomic Commit 契约保持不变，示例 `module-contracts/0.1` 不是文档版本遗漏。

**必须满足的不变量 `[DECIDED]`：**

1. State Machine 是同一 Game Session 内 World、Character、Combat、RNG、NPC 持久认知的**唯一权威状态持有者与最终提交者**。
2. Rule Engine 负责规则求值，不能持有跨请求的独立权威战斗状态，不能直接提交数据库。规则求值内部允许临时可变数据结构。
3. `evaluation.status == "accepted"` 不等于 `commit.status == "committed"`；拟议事件不得提前发布为 WorldEvent。
4. Agent 提交的是意图或提议，不是 HP、骰点、资源支付等机械事实；Narrator 消费已提交、经授权的事实。
5. 可重试、确定性、版本和授权均在可信系统边界实现，不能仅依赖 LLM 自律。
6. 单数据库 SQLite + WAL + 短事务是 MVP 方案；**不得在 SQLite 写事务内等待 LLM 或长时间的 Rule Evaluation**。
7. NPC 只有一份 Persistent State；Interactive 活跃期间独占该 NPC 的 LLM 主观认知/自主行动，Background 一次性推理不需要 Interactive Agent Context。新消息/接口均为 `[PROPOSED; NOT IMPLEMENTED]`，架构原则确认不等于 API 已实现。

**状态机仅承担权威写入与合法性/权限/事务边界，不重新实现 D&D 的机械规则。**

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
- `read_cursor` / 已追加 Context 位置 / `processing_cursor` / `ack_cursor` 分离。读取或模型返回不自动 ACK；ACK 只推进连续完成且已持久记录处置的前缀，细节见 §9.6。
- Host 为待处理 Observation 批次建立稳定 `observation_work_id`、claim 与幂等处理记录；重复投递不创建第二份逻辑工作。合并批次不能重复占用尚有任务的同一观察；具体索引/表结构未冻结。
- Mode Routing 由 Host 负责：Interactive 直接按序追加，Inactive 经 Lightweight Gate。证据保留与投递由 SM 负责，失败不随模型 Context 释放而丢失。

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

本节所有新增消息、字段、接口和协调协议均为 **`[PROPOSED; NOT IMPLEMENTED]`**；不表示已存在 HTTP Endpoint、Python 类型或数据库表。已确认原则与候选 wire schema 分别说明。

### 9.1 Persistent NPC State、Evaluation Context 与 Mode `[DECIDED]`

| 概念 | 内容 | 所有者与边界 |
|---|---|---|
| Persistent NPC State | 唯一 Identity、Personality、Memory、Belief、Relationship、Goal、Plan、Runtime State（Schedule / Current Activity 等） | State Machine 权威持久保存；Context 不是副本权威 |
| Interactive Context | NPC 专属可复用的角色/交互/Observation 历史 | Agent Host 管生命周期、追加、模型调用和预算 |
| Background Context | 当前权威身份/人格、相关 Memory / Belief / Relationship / Goal / Plan、新 Observation 的一次性授权视图 | Host 构建并在调用完成后释放；可用不同 System Prompt、模型和 Builder |
| NPC Evaluation Mode | `interactive` 或 `background` | Host 协调当前推理模式；State Machine 持久校验提交资格及版本 |

`inactive` 是没有 Active Interactive Context 的调度状态，不是第三种 Evaluation Mode。Context Active 但无在途模型请求仍处于 Interactive Mode。Background **不创建、不恢复、不激活 NPC Interactive Agent**，NPC 不因切换模型或 Context 释放改变身份。

**NPC Evaluation Mode Exclusivity**：Interactive 活跃期间，所有需要 LLM 的主观 Memory Formation、Belief / Relationship Update、Goal / Plan Revision、自主 Action Decision 均交给当前 Interactive LLM。新授权 Observation 按序增量追加，不逐条调 Lightweight Gate、不另调 Background / Memory / Cognition LLM；重要事件可由 Host 安排下一次 Interactive 请求。在途请求的新观察排队，不能假定修改正在执行的调用或物理 KV Cache。

Inactive 时由 Host 协调 Lightweight Gate（确定性规则、轻量模型或组合）：`No LLM Required → Safe Retention / No-op`，或 `Background Evaluation Required → One-shot NPC LLM`。Memory、Cognition、Behavior Trigger 可联合判断，不要求多个模型/Session。Jev 仅为可替换实验候选。确定性事件、证据、已确认承诺和必要安全处理不受 LLM 独占限制。

### 9.2 真正的跨模块接口 `[PROPOSED; NOT IMPLEMENTED]`

| 方向 / 候选接口 | 输入 | 输出与权限约束 |
|---|---|---|
| Host → SM `get_npc_view` | 可信 principal、session、npc | 授权 Persistent State View 与 `npc_state_version` / `world_version`；无其他 NPC 私有认知或 GM Secret |
| Host → SM `get_event_observations` | npc、读取 Cursor、授权范围 | 稳定 ID、有序观察、分页 Cursor / 投影水位；读取不 ACK |
| Host → SM `get_current_perceptual_view` | npc、授权范围 | 当前感知快照；不补历史目击，长期记忆引用须可验证 |
| Host → SM `coordinate_npc_mode` | 可信 Host、npc、预期 epoch、目标调度状态、task refs | 短事务 CAS 更新持久 `mode_epoch` / evaluation 提交资格；不执行模型调用 |
| Host → SM `submit_npc_update_proposal` | Evaluation 凭证、epoch、NPC / 世界版本、源证据、稳定 Proposal ID、可选 updates | 校验归属/类型/来源/版本/幂等后私有更新或拒绝；不直接执行 Action Intent |
| Host → SM `record_npc_observation_disposition` | work ID、Observation IDs、Safe Retention / No-op 或各子操作回执 | 持久处理记录；保留关键证据，不以模型返回充当提交 |
| Host → SM `ack_observations` | npc、连续完成范围、持久处理回执引用 | 校验义务和投影水位后前移 ACK Cursor；不删除未处理证据 |
| Host → SM 统一 Typed Command（§3） | Interactive / Background / 审核的 Schedule 或 Policy 产生的受限 Action Intent | 相同 Actor 授权、Typed Command、必要 Rule Evaluation 与 SM Commit；不新增 NPC 动作执行协议 |

Evaluation 来源及 epoch 可绑定在可信命令授权元数据/持久记录中，**不改写 §3 的核心信封**；不能信任 LLM 自报 mode、npc 或凭证。SM 在最终提交时验证授权仍有效，防止 Host 校验之后切换导致竞态。单纯 NPC 私有更新不经 Rule Engine；涉及世界/机械行动时沿用 §3、§6 的执行分支。

### 9.3 Host 内部 RequestNPCEvaluation `[PROPOSED; NOT IMPLEMENTED]`

旧 `RequestNPCCognition` / `cognition.request` 概念扩展为 **`RequestNPCEvaluation`**：涵盖可选记忆、认知、Goal / Plan 与自主 Action Decision。不是 State Machine 调用 LLM 的跨模块 API，也不与 RuleEvaluationRequest 混用。

以下为 Background 请求示例；§9.4 展示另一次 Interactive 响应，二者不是同一请求/响应对。

```yaml
schema_version: npc-evaluation/0.1   # 独立候选消息版本，不改 P0 schema
session_id: ses.example
npc_id: npc:guard-a
observation_work_id: work.guard-a.005
evaluation_id: eval.guard-a.bg.005
mode: background                   # interactive | background
mode_epoch: 4                      # 可信协调元数据
reason: significant_observation
source_observation_ids: [obs.npc.guard-a.0005]
read_cursor: cursor.guard-a.005
input_world_version: 27
expected_npc_state_version: 8
authorized_npc_view_ref: view.guard-a.008
context_policy_ref: policy.background.basic
# Background 不需要 interactive_context_id 或 Interactive Agent activation
```

Interactive 请求引用已有 Interactive Context（首次交互先按 §9.5 协调创建/恢复），Host 追加授权观察。Background 请求从当前权威视图单独构建一次性 Context。`evaluation_id` 标识逻辑评估，`invocation_id` 标识模型尝试；有限重试不得把同一 Observation 变成可重复提交的新工作。

**内部操作与 API 区分**：Mode Routing、Gate、Context Build / Append / Release、Memory / Cognition / Behavior Trigger、`dm.plan`、`dm.narrate` 是 Host 的逻辑操作/模型角色，不能据此声称存在相应网络服务。SM 内部 `project_world_event`、Evidence 写入和日程检查也不是独立跨模块模型 API。Planner 可处理授权 GM View 并提出主持方案；Narrator 仅接收玩家可见已提交回执/事件/对白，不写权威状态。

### 9.4 统一 NPCUpdateProposal 与 Action Intent `[PROPOSED; NOT IMPLEMENTED]`

两种模式使用同一或兼容信封；旧 `NPCMemoryUpdateProposal` / Cognition Proposal 可映射为其 `updates` 子集。所有输出均可省略；不要求每轮对话写记忆或行动。示例是一次 Interactive 响应同时包含四种输出：

```yaml
schema_version: npc-evaluation/0.1
session_id: ses.example
npc_id: npc:guard-a
observation_work_id: work.guard-a.005
evaluation_id: eval.guard-a.005
invocation_id: invoke.guard-a.005.1
proposal_id: proposal.guard-a.005
mode: interactive
mode_epoch: 5
based_on_world_version: 27
expected_npc_state_version: 8
source_observation_ids: [obs.npc.guard-a.0005]
response:
  dialogue: {text: "我会去查看，请留在这里。", intended_audience: [char:hero]}
  updates:
    memory:
      - kind: episodic
        text: "我听到院子传来求救。"
        epistemic_status: observed
        source_observation_ids: [obs.npc.guard-a.0005]
    belief:
      - text: "院子里可能有人需要帮助。"
        epistemic_status: inferred
        source_observation_ids: [obs.npc.guard-a.0005]
    relationship: []
    goal: []
    plan: []
  action_intents:
    - command_type: world.interact
      payload: {operation: move, destination_id: scene.yard}
```

这是原创合成、未冻结字段。Host 持久选定一份合法 Proposal、为更新子操作及 Action Intent 分配稳定幂等 ID / 指纹，再分别路由。SM 可在短事务中原子保存允许的私有更新及子操作回执；Action Intent 经 §3 Typed Command 单独授权、重验前提并提交，不能把私有更新成功当成行动成功。若私有更新使全局版本前移，行动仍须读取新快照并验证原意图适用性，不直接套旧 Delta。

Memory / Belief / Relationship / Goal / Plan 更新只能影响本 NPC，保留证据和 `observed / told / inferred` 标签，不能更改 Identity 绑定、他人认知或 World Fact。Commitment Recall 只引用已确认承诺；涉及尚未执行的行动不能先记为成功。Dialogue 也是待发布提议，含世界副作用的语义需独立验证。

Background 可输出同样的可选 `updates` 与 `action_intents`，通常无交互对白；完成后释放临时 Context，不能为执行 Intent 而隐式激活 Interactive Agent。Deterministic Schedule / Policy 同样使用统一命令路径，但不计作敌方 LLM Sub-agent 战斗验收。

### 9.5 Mode Switching、并发与过期结果 `[PROPOSED; NOT IMPLEMENTED]`

Host 按 `(session_id, npc_id)` 协调模式；同一 NPC 不允许两个无协调的主观评估结果同时写 Belief / Relationship / Goal / Plan。SM 持久 epoch / evaluation 凭证使校验覆盖跨进程故障，不能只依赖内存锁。

**默认 Background → Interactive 策略：取消并拒绝旧结果。**

1. Host 停止新 Gate / Background 派发，串行进入切换；SM 短事务 CAS 推进 epoch，撤销旧 Background 的更新及派生 Action Command 提交资格。
2. 尽力取消请求；模型不能取消仍可完成物理调用，但旧 epoch 的迟到输出不可提交。取消完成不是正确性的前提。
3. 查询已持久 NPC Update / Command Receipt：epoch 变更前已提交结果保留并合入当前视图；之后旧任务未提交部分终态拒绝。不得以新 ID 重放已完成部分。
4. 将未完成 Observation 工作及子操作回执交当前模式，以最新权威 NPC State / Memory / Goal / Plan 和授权新观察建立/恢复 Interactive Context，再允许交互推理。旧 Proposal 不盲目重验证后直接覆盖新决定；需要重新决策时由当前 Interactive LLM 完成。

Interactive → Inactive 同样完成或撤销当前请求、对账并推进 epoch 后，才允许 Gate / Background。同一模式内 Evaluation 与输出处置串行，最终提交重验 epoch、NPC 状态版本、来源和世界前提；发生冲突先查回执、刷新视图后有界重评估，不能将旧增量强行套在新认知上。所有 LLM / 轻量模型调用都在 SQLite 写事务之外。

重启先撤销过期资格并对账，才重建 Context / 派发任务。协调状态编码、CAS 存储、provider 取消能力和超时预算待实现论证；取消/拒绝过期结果的语义已经明确。

### 9.6 Proposal 幂等、处理义务与 ACK `[PROPOSED; NOT IMPLEMENTED]`

- 同一 Observation 逻辑工作复用稳定 `observation_work_id`，模式切换/模型重试不创建第二份工作；每次尝试先检查已选定 Proposal 及子操作回执。不同模型尝试可有不同 invocation ID，但只选一份可提交输出；同 ID 不同指纹拒绝。
- Proposal、更新子操作、Action Command 均有稳定 ID。必须在执行第一个副作用前可靠保存被选定输出、子操作和待执行义务；不是只把模型响应放内存。提交后响应丢失按原 ID 查回执，不能重问模型生成新 Memory / Action ID 来规避去重。
- 已完成更新或行动不会因另一子操作失败而消失。切换/冲突后的新评估只处理未完成义务，并读取已提交结果；同一工作已经完成的 Memory / 行动槽位不能再次产生等价写入/执行。需要改变未提交候选时须显式废弃旧候选并保留审计关联，不得改写已有回执。
- `processed`：No LLM Required 已记录 Safe Retention / No-op，或 Proposal 的所有可选更新与行动已有终态提交/拒绝/no-op 处置。`needs_choice` 等待续工作必须可靠保存，相应观察保持未完成；epoch 撤销、模型失败或无输出不等于 processed。
- `ACK`：SM 验证持久处理回执、工作归属和投影水位后，仅推进连续完成前缀；读取、Context Append、模型返回不是 ACK。明确模型输出 no-op 可以完成处理，但须记录无更新/无行动的可追溯结果。
- 故障、取消、版本冲突和重复投递保留未完成证据；已完成子操作复用回执，未完成项由当前模式有界重试。不重复累加 Memory / Relationship Delta，不生成重复行动；关键证据不能随 Context 释放或 Gate 漏判丢失。

**Memory Persistence 与 Context Compaction 独立 `[DECIDED]`**：SM 管 Evidence / Observation / Persistent NPC Memory 与认知，Host 管 Model Evaluation / Context Lifecycle / 调度。两种 LLM 都可提议 Memory，SM 统一验证和持久化；成功写入不强制压缩、重建或重复注入 Active Context。Compaction 仅由 Token、延迟、成本或上下文质量压力触发，工作摘要不得变成认知或世界事实。

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
| C-A14 | Active Context 暂时无模型请求，重大事件到达 | Host 安排下一次 Interactive 请求；在途调用期间新增输入排队，不修改执行中请求/KV Cache |
| C-A15 | 单个 Interactive 响应含 Dialogue、Belief、Memory、Action Intent | 可选更新与行动分别验证；世界事件只有统一 Typed Command 提交后产生；合法全空/no-op 同样可处置 |
| C-A16 | Inactive NPC 经 Gate 一次 Background Evaluation 产生行动 | 无 Interactive Agent Context；同一 NPC 权限与共享命令路径，临时 Context 调用后释放 |
| C-A17 | 低价值 Observation / 轻量模型不可用 | 不调用完整 NPC LLM或按保守策略留待处理；Safe Retention / No-op 有回执，关键证据不丢失 |
| C-A18 | Background → Interactive 与提交竞争 | epoch 变更前的成功提交先对账；变更后旧 Proposal / Action 拒绝，无重复认知/行动或过期覆盖 |
| C-A19 | Model Failure、重复 Observation、版本冲突、ACK 前崩溃 | 稳定 work / Proposal / Command ID 与回执防重复；未完成观察不 ACK、不跳过投影缺口 |
| C-A20 | 任一模式 Memory 持久化成功 | 不强制 Compact / Rebuild；资源或质量压力才触发 Context Compaction |

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
| C-11 | Mode epoch / Evaluation 凭证、work claim、处理回执的最小存储/编码？ | 本文确定撤销旧资格及提交时校验语义，字段、CAS 和恢复实现仍待论证 |
| C-12 | Observation Cursor、投影水位、批次合并及 ACK Schema？ | 需证明不跨越未投影/未完成项，明确子操作终态与重入；具体类型待冻结 |
| C-13 | Gate / 两种模式的模型、Prompt、阈值、预算与取消能力？ | Jev 仅候选；通过合成场景测定漏判/延迟/成本，不擅自固定技术选型或 SLO |

## 14. 建议实施顺序（在本契约评审通过之后）

**Batch 0 — Contract review / State inventory：** 对照 `orchestrator.py`、`types/combat.py` 和现有测试列出权威/派生状态字段、RNG 读写点、Effect 生命周期、NPC Intent 空缺。修复契约歧义，不改大规模业务代码。

**Batch 1 — Evaluation Adapter 最小纵切：** 在测试分支把**一条** `combat.intent`（可以从基础攻击开始）转换为从 Snapshot 输入/结果 Delta 输出的无权威状态评估；兼容旧执行器对照测试，保持旧公开 API 不受影响。

**Batch 2 — SQLite Atomic Commit 最小闭环：** 建 `Session + Snapshot + idempotency + RNG + Delta + Event + Receipt + Outbox` 单事务。完成药水跨领域、重试、冲突和注入失败测试。

**Batch 3 — NPC/Perception & DM 最小集成：** 验证 Interactive 独占与 Inactive Gate / Background、模式切换及可靠 ACK；让一条显式敌方 NPC Typed Intent、一次 NPC Event Observation 与 Player-facing Narration 完整通路成功；不要求先实现 Jev 或复杂记忆治理。

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
