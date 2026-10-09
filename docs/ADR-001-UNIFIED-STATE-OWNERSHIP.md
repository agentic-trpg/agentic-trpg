# ADR-001 — Unified Authoritative Runtime State Ownership

> **项目：** Agentic TRPG  
> **状态：** Accepted（架构方向已确认；具体接口与迁移方案尚待评审）  
> **日期：** 2026-10-09  
> **适用范围：** State Machine、Rule Engine、Agent Host、Agent DM、NPC Sub-agents  
> **性质：** 跨模块架构决策；不是 API Schema、迁移实施计划或现有代码已完成声明

## 1. 背景与问题

原始 MVP 设计采用两个运行态权威：State Machine 保存世界、场景、物品、任务、NPC 记忆等状态；Rule Engine 通过内部活跃战斗对象持有 HP、回合、资源、效果、RNG 等机械战斗状态。双方依靠规则结果和回执同步。

这种分工使喝药、战斗中开门、使用消耗品、移动与环境交互等跨模块操作难以实现真正的单事务提交，并使持久化、重试、恢复和审计需要额外的双权威协调。

目前 Rule Engine 存在 `_LiveCombat`、`CombatHandle`、进程内注册表和规则执行事务。该实现已经具备丰富的规则求值、类型化 Intent、事件和回滚能力，但**不是**本文所决定的新运行时所有权模型。

## 2. 已接受的决策

### ADR-001.1 — 单一权威状态拥有者

**State Machine 是一个 Game Session 内全部权威、可变 Runtime State 的唯一逻辑拥有者及最终提交者。** 其管理范围包括：

- World / Scene / Quest / Object / Inventory State；
- PC / NPC 运行状态及经授权的知识、关系、记忆与 Observation；
- 战斗双方的 HP、临时 HP、死亡状态、位置、先攻、回合、行动经济和资源；
- Conditions、Active Effects、持续时间、Concentration、Reaction、Pending Choice 等需要跨步骤延续的机械状态；
- 权威 RNG 上下文及已提交骰点结果；
- 有序事件、操作回执、幂等记录、版本信息和持久化元数据。

上述内容的**规则解释与计算**仍归 Rule Engine；所有权不等于 State Machine 自行实现 D&D 规则。

### ADR-001.2 — Rule Engine 的职责

**Rule Engine 是无权威持久状态的规则求值与状态转换组件。** 其概念输入为：

```text
State Snapshot + Typed Intent + Pinned Ruleset/Data + Explicit RNG Context
```

其概念输出为：

```text
Rule Evaluation Result
  ├─ accepted / rejected / needs_choice / unsupported
  ├─ typed State Delta（accepted 时）
  ├─ proposed Rule / Combat Events
  ├─ RNG results and next RNG position/state
  ├─ read-set / expected versions / invariants
  └─ failure or continuation information（按需）
```

- **`accepted` 仅表示规则求值完成，绝不表示已提交。** `committed` 只能由 State Machine 成功提交后返回。
- Rule Engine 可以在**一次求值的临时执行上下文**中复制、修改对象，甚至使用现有规则算法和 `_LiveCombat` 的临时适配形式；但不得依赖跨请求存在的、独立于 State Machine 的权威可变战斗注册表。
- 纯函数式外部接口是目标语义，不要求把所有内部算法重写为无局部副作用的函数。
- Rule Engine 不直接提交世界数据库、不直接向 NPC 分发 Observation，也不以叙事文本作为规则权威输入。

### ADR-001.3 — 原子提交边界

State Machine 负责接收玩家或 Agent 的经授权请求、构建快照、调用规则求值，并在**单个本地持久化事务域**中验证与提交：

1. 请求身份、角色权限、稳定 `command_id`、参数指纹和幂等性；
2. 输入快照的版本、相关对象前置条件及必要状态不变量；
3. Rule Engine 返回的类型化、允许列表内的 `StateDelta`；
4. 世界/角色/战斗状态变化及 RNG 进度；
5. `Committed Event`、`Commit Receipt`、去重记录和待投递 Observation / Outbox 元数据。

事务**全部成功或全部失败**。未提交的规则求值结果、事件与骰点不能当作已经发生的游戏事实发布。成功提交后再对 Agent DM、NPC Perception 和 UI 发布权威回执与事件。

**约束：** 上述原子性依赖于所有相关权威写入确实落在同一个事务域内；“都由 State Machine 管理”这个模块命名本身并不能提供跨数据库或跨服务的 ACID 保证。

### ADR-001.4 — Agent 与 Perception 不变

- Agent DM、NPC Sub-agent 和 Agent Host 只能提出 / 转发受授权的 `Typed Intent`、世界操作请求和记忆更新提议；不得自行提交权威状态。
- State Machine 基于已提交事件生成经权限过滤的 `Event Observation` 与 `Current Perceptual View`。
- NPC 的主观记忆由其 Sub-agent 提议，经验证后存储；NPC Belief 不自动成为 World Fact。
- 此决定**不改变** Memory Persistence、Context Compaction、NPC 按需激活与知识隔离的既定架构。

## 3. 规范的最小执行时序

```text
Human / NPC Agent
   │  Typed Intent + command_id
   ▼
Agent Host / State Machine
   │  Authenticate / authorize / preflight
   │  Load authoritative snapshot (version V) + pinned ruleset + RNG
   ▼
Rule Engine.evaluate(...)      [不提交，不生成权威事件]
   │  accepted(StateDelta, proposed events, next_rng) / rejected / needs_choice
   ▼
State Machine
   │  Short DB transaction:
   │    check command_id and fingerprint
   │    compare versions and preconditions
   │    validate typed deltas and invariants
   │    atomically commit State + RNG + Events + Receipt + Outbox
   ▼
Committed Receipt
   │
   ├─> Perception Projection -> private Observation Inboxes
   └─> Agent DM narration / User interface
```

- 规则求值期间及 LLM 生成期间**不持有长时间的 SQLite 写事务**。
- 两个 Agent 争抢同一个对象时，提交版本检查防止重复获得；**具体谁先行动**由游戏时序/经批准的规则裁决决定，不由网络先后或 SQLite 写锁决定。
- 发生状态版本冲突时，该次求值不能直接提交。可以在明确的重试策略下重算；对同一个已经提交的 `command_id` 必须返回原回执，不得二次掷骰或重复扣资源。

## 4. 必须在 Module Contracts 中细化的风险

### 4.1 完整且可版本化的状态快照

`CombatState` 不能仅包含 HP、位置或 Initiative。必须包含规则计算需要的全部持久语义，包括 Reaction / Pending Choice、Concentration、Effect 生命周期、持续区域、资源池、回合序号、RNG 状态等。

状态可按照规则依赖传递受约束的局部快照，但必须具有**完整的依赖闭包**、显式版本和兼容的 Ruleset/Data 版本。不得因为传了一个不完整的快照而产生不可检测的错误结算。

### 4.2 RNG 与确定性重试

- State Machine 维护权威 RNG 状态、流标识或进度及其版本。
- Rule Engine 在显式 RNG 上下文下求值，返回对应消耗与后继状态。
- 只有成功提交才推进权威 RNG；拒绝、崩溃前未提交、版本冲突不会推进已存储 RNG。
- 已提交 `command_id` 的重复调用必须读取持久回执，不得重新评价产生新的骰点。
- 未来的可重复回放还需固定 RuleSet/Data 版本及求值逻辑版本，不能仅依赖随机种子。

### 4.3 多阶段交互与中间选择

Reaction、对抗决策、多步施法等可能需要在一次动作最终完成前向 PC/NPC 请求选择。`needs_choice` 必须有明确的可取消、可验证的 continuation / pending-operation 契约；不得把不可恢复的进程内部对象当作唯一事实来源。

**具体 continuation 结构为待设计事项。** 实施前需根据第一批真实规则路径确定最小机制，不能将复杂反应系统隐藏在无版本的黑盒句柄里。

### 4.4 权限与 State Delta 校验

State Machine 不盲目信任 Rule Engine 返回的任意对象路径或 JSON Patch。所有变化使用受限类型化操作，由 State Machine 验证执行主体、资源归属、读写范围和事务不变量。

例如消耗药水：规则求值同时表达「正确使用者的道具资源减少」及「符合规则的治疗结果」；State Machine 在同一事务内检查库存与资源归属并提交，不会把物品消耗和 HP 恢复拆成两个独立最终提交。

### 4.5 性能边界

按请求序列化 / 反序列化全部深层战斗状态、复制大量效果依赖、反复重建 RNG 与派生索引可能有代价。应为快照构建、Rule Evaluation、事务提交分别测量 p50/p95 和内存开销，并允许**非权威的临时缓存**，而不引入第二份独立权威状态。

## 5. 对 MVP 范围的影响

- MVP 仍为**一名人类玩家控制一名 PC**；多玩家、自动 World Creation Agent、视觉引擎依旧不是当前验收范围。
- 继续采用 Python + SQLite + WAL + 短事务作为本地权威运行时的建议实现。
- 普通非战斗 Session 保存/恢复必须支持。
- **活跃战斗精确跨进程恢复仍为 Post-MVP。** 统一拥有战斗状态不自动意味着产品必须提供此能力。
- 新架构中若每个已完成的战斗动作已持久提交，崩溃时**不能悄悄恢复旧的战前存档并覆盖这些权威结果**。MVP 必须显式定义 `combat_interrupted`、安全重新开始条件或阻塞策略；未定义前不得宣称无损恢复。
- 普通怪物由 LLM Sub-agent 还是确定性策略控制，仍为独立的待决策产品问题，不由本 ADR 擅自确定。

## 6. 实施策略和兼容性

1. **先冻结本 ADR，再设计执行契约。** 先明确 RuleEvaluationRequest/Result、CombatState、StateDelta、RNG、Receipt 和 PendingChoice 的最低语义。
2. **建立现有 Engine 基线。** 盘点 `_LiveCombat` 所有权威字段及其访问/修改位置，确认不遗漏隐藏状态。
3. **迁移时复用规则逻辑。** 可在新 Stateless Evaluation Adapter 中创建临时规则执行上下文，执行现有 Typed Intent / Resolver，并导出结构化 Delta 与候选 Events。
4. **用合成测试做新旧行为对照。** 比对命中、伤害、资源消耗、反应、效果生命周期、事件顺序、RNG 消耗和拒绝/回滚。
5. **分场景迁移，禁止生产双权威混用。** 测试期可同时保留旧 API 与新 API；但同一 Session 的同一领域状态不可一半由 Rule Engine 注册表、另一半由 State Machine 权威持有。
6. **迁移接口后更新文档与验收。** 正式新路径未通过可靠性测试前，不声称旧 Rule Engine 已转换为纯求值器。

## 7. 不采纳的替代方案

| 方案 | 原因 |
|---|---|
| Rule Engine 与 State Machine 分别持有权威状态并用回执同步 | 跨域操作复杂；故障时需要补偿/协调；存档状态容易割裂 |
| 只将 HP 或 Spell Slots 迁移至 State Machine | 更危险的混合权威；Action Economy / Effects 仍可能不一致 |
| 让 State Machine 同时计算 D&D 规则 | 破坏独立确定性 Rule Engine 的目标，产生重复算法与规则分歧 |
| 一次性废弃当前 Rule Engine 并从零重写 | 成本与回归风险过高；应复用已验证的规则求值和测试资产 |

## 8. 影响到的正式文档

| 文档 | 变更目标 |
|---|---|
| `docs/MVP_SCOPE.md` | 修改状态权威与规则裁决措辞，保留原 MVP 产品边界 |
| `docs/ADVENTURE_PACKAGE_SCHEMA.md` | 修改运行时 State Ownership 与规则执行协议；保留静态世界定义 |
| `docs/STATE_MACHINE_ARCHITECTURE.md` | 核心重写：Combat / Character Runtime State、事务、RNG、事件及故障处理 |
| `docs/AGENT_ARCHITECTURE.md` | 更新单一提交路径；保留 Perception / NPC Memory / Context Lifecycle |
| `docs/MODULE_CONTRACTS.md` | **下一项优先设计**：统一规则求值与提交接口 |
| `docs/ARCHITECTURE.md`、根目录 `README.md` | 以后统一按此决策构建整体说明 |

## 9. 完成标准（架构与迁移）

**架构文件可以批准的条件：**

- 状态所有权无二义性，且明确“Rule Engine accepted ≠ State Machine committed”。
- RNG / State Version / Command Idempotency / Pending Choice 与 Delta 语义已有完整设计或清楚标明待决事项。
- 明确一个事务域内的写入范围，避免虚假的跨服务原子性承诺。
- 已列出原始文档的冲突段落及受影响接口，完成对应修订计划。

**迁移实现可以验收的条件（未来代码阶段）：**

- 对至少一种跨领域操作验证库存、机械结果、事件、RNG 与回执原子提交。
- 新旧规则行为对照覆盖正常执行、拒绝、RNG、资源支付和失败回滚。
- 重试不重复扣资源或产生第二份结果；版本冲突不提交过期状态。
- 崩溃、重启和非战斗保存恢复测试通过；活跃战斗恢复功能不做超出 MVP 的承诺。
- Agent/NPC 只能消费已提交结果与自己的授权 Perception。

## 10. 后续步骤

1. 由项目负责人确认本 ADR 并提交到总控仓库。
2. 编写 `docs/MODULE_CONTRACTS.md` 的 **State Machine ↔ Rule Engine** 核心章节（先不冻结所有 Agent 接口）。
3. 基于契约升级 `STATE_MACHINE_ARCHITECTURE.md`；定向修订 Scope、Adventure Package、Agent Architecture。
4. 制定 Rule Engine 的能力盘点和渐进迁移 Batches，再开始代码重构。

---

**本 ADR 仅确定目标架构。** 在实现与验证之前，仓库实际 Rule Engine 仍可能采用原有 `_LiveCombat` 状态持有模型；文档不得把设计目标当作已实现事实。
