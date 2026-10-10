# Agentic TRPG — Module Contracts（MVP）

> **版本：** v0.8 / Draft for Review
>
> **日期：** 2026-10-10
>
> **性质：** 跨仓库目标接口契约草案；**不是已实现 API**
>
> **归属仓库（建议）：** `agentic-trpg/agentic-trpg/docs/MODULE_CONTRACTS.md`
>
> **依据：** [ADR-001](./ADR-001-UNIFIED-STATE-OWNERSHIP.md)（Accepted）、[MVP Scope](./MVP_SCOPE.md) v0.11、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.6、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.10、[Agent Architecture](./AGENT_ARCHITECTURE.md) v0.9
>
> **历史代码核对基线（沿用 v0.1，本轮未重审 Engine）：** `agentic-trpg/agentic-trpg@4190833`；`agentic-trpg/trpg-rules-engine@64dd920`
>
> **标记：** `[DECIDED]` 已有架构决定；`[PROPOSED]` 本文推荐、待评审；`[OPEN]` 需要进一步决策；`[NOT IMPLEMENTED]` 不可宣称现有代码已有

## 0. 用途与冻结策略

本文定义 Agent Host、State Machine、Rule Engine、Perception、NPC Evaluation、DM Narration 与 Adventure Package 的交接边界。优先冻结**最小可实施的 State Machine ↔ Rule Engine 垂直闭环**；其余模块先定义最小跨模块契约和安全边界，避免过早扩大实现面。v0.5 统一 P0 Snapshot / Request / Result、封闭 Typed Delta、ProposedEvents、独立 RNG、CommandReceipt 和只读 Availability Query，并澄清 Invocation 错误不立即终止有效 EVA。v0.6 统一 Adventure Package 加载、可信创建幂等、静态模板与 SM 运行时边界（§10），候选 combat.start / rules.effect 复用本协议。v0.7 统一 submit_command / GM Adjudication、有限动态世界操作和 AP-15 按操作类型校验 Actor，并同步只读查询的早期开发计划。v0.8 将 PER-01～PER-08 接入既有事件/可靠工作协议（§7），区分 Signal、察觉判断、授权观察与 NPC 认知。已确认的所有权、NPC 架构与 MVP 范围不变；结构决策标为 [DECIDED]，具体 API/字段实现仍 [NOT IMPLEMENTED]，未冻结细节单列 [OPEN]。

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

| 位置（v0.1 历史 main 基线） | 历史事实（非当前实现声明） | 对契约的影响 |
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

### 2.2 幂等语义 `[DECIDED + PROPOSED]`

Create Session 尚无 session_id，使用可信 `(principal_id, command_id)`，创建结果见 §10。以下适用于普通游戏命令，按 `(session_id, command_id)` 在 State Machine 的**持久数据库**中去重：

- **相同 Fingerprint、已提交：** 返回原 `CommandReceipt`，不重新掷骰、不重复扣资源、不重复发事件。
- **相同 ID、不同 Fingerprint：** `idempotency_conflict`；不执行。
- **首次请求，尚无终态：** 可进入求值；必须解决并发重入（唯一约束 + 原子 claim / 提交校验），不能只在内存中判断。
- **已完成的确定性拒绝：** 可记录原 `CommandReceipt`；变更输入需要新 `command_id`。
- **网络中断，是否提交未知：** 调用 `get_command_receipt(session_id, command_id)` 查询，**不可**简单改用新 ID 重试。

可信端校验 principal_id 的权限与适用时的 Actor 控制绑定，或受信系统/世界事件的机械来源和目标；无 Actor 分支不能绕过授权。Replay 不能突破当前授权策略。原样重试复用 command_id，修改 payload / 裁决后果等命令内容须用新 command_id；状态/反馈未知先查原回执。确定性拒绝不强制重新调用 LLM，仅需新情境语义判断时才有界重规划。

## 3. Player / DM Planner / NPC Agent → State Machine：TypedCommand（P0）

### 3.1 统一公开入口与命令信封 `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

所有普通游戏命令只经公开逻辑入口 **submit_command(TypedCommand)**，内部以 command_type 分派 world.* / rules.* / combat.*。create_session、NPC Evaluation 提交、只读查询和回执查询保留独立生命周期，不塞入此信封。不要求 submit_world_command / submit_check_request / submit_combat_intent 等独立公开入口；旧名最多描述内部处理路径，不是额外服务。

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
| State Machine | 确定性验证结构、可信身份/权限、引用存在、世界事实/前置条件、版本、操作能力和提交不变量；不证明自然语言语义正确，不新增语义审核 LLM |
| Rule Engine | 验证 D&D 机械合法性，计算骰点、豁免、伤害、资源和效果；不替 DM 决定剧情情境，也不提交权威状态 |

优先采用规则或 Package 已规定的机制/DC；未规定时允许可信 GM 裁决，但能力/技能、DC、成功/失败后果必须在掷骰前确定并可追溯。SM 只验证能确定性检查的内容，机械规则交 Engine；依据记录不要求模型私有推理链。GM 裁决复用 TypedCommand / 受限 payload，不增加 Adjudication API。Planner 不能提交骰点/伤害或任意状态修改，也不能替独立 NPC Agent 决定私人意图。

### 3.3 有限动态世界操作 `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

Package 是静态初始定义，不是 DM 创造力的上限。Planner 可提出原先不存在的简单 Object、World Fact、Scene Connection，通过 SM 已支持的封闭 Typed World Operations 验证并持久化到 Runtime World State，不修改 Package。已有对象优先引用可信 GM View 的 ID；新对象由 SM 分配稳定身份，提交后经既有授权查询可见，重试通过原回执返回同一结果。

叙事描述、未提交创造提议和已提交世界事实必须分开；不信任 LLM 自报对象存在或状态改变。候选 Object / Connection 等领域操作可随实际 MVP 场景审阅扩展，但类型、字段、目标和不变量受限；不能借 World Fact 写 HP/资源/RNG，禁止任意 JSON Patch、SQL、脚本或开放式状态覆盖。完整操作字段、动态复杂 Scene / 战斗地形生成 **[OPEN]**，本轮不冻结或实现，也不新增 World Creation Agent。

### 3.4 Conditional World Effect Proposal `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

Planner 可在 TypedCommand 中提出受限的候选成功条件及对应世界变化，尽量复用 Adventure Package 的声明式 Condition / Effect 语义，不建第二套 Event Engine。SM 根据可信规则结果和权威世界状态判定条件、执行允许类型化效果；LLM 自报成功不能满足条件。提议的封装字段、结果引用和条件/效果子类型 **[OPEN]**。

需要机械计算时复用 §4–§6 的 RuleEvaluationRequest / Result；尽可能在掷骰前确认操作及后果均有受支持的表达路径，不先掷骰再用自由文本补写状态。一个命令提交前能够完整求值时，SM 同事务提交世界效果、机械 Delta、RNG、正式事件、CommandReceipt 和 Outbox；已提交事件才引发的后续效果沿用 §10 的可靠幂等独立命令，不虚构跨已提交事务原子性。

Planner 可随 Action Intent 提出按可能执行结果分类的候选 observable_signals，预定义事件/标准规则行为优先复用模板。SM 根据可信结构化执行结果选择匹配 Signals，并与实际事件原子提交，不接受 LLM 自报成功；Schema / 条件字段仍 [PROPOSED / OPEN]，具体边界见 §7.1，不增加 Event Generation Agent。

### 3.5 授权视图、反馈与叙事 `[DECIDED]`

复用 get_scene_view 等既有查询入口，按可信主体投影 DMView / PlayerView / NPCView：Planner 获取主持范围内完整授权 GM 信息；Player / Narrator 只读玩家可知事实；NPC 通过独立 NPCView / Perception 获取自身授权信息；get_scene_view 面向 NPC 时也必须经过 NPC Perception / 授权投影，不能绕过感知权限（DOC-02）。动态创建且已提交的对象进入后续授权查询，未提交对象或隐藏信息不能泄漏；不新增冗余查询服务。

反馈映射沿用 §5 / §6 / §11：rejected 是规则/世界拒绝，unsupported 是不支持的能力/操作原因，合法机械失败可为 accepted 并提交实际成本；version_conflict 对应 CommandReceipt.conflict，needs_choice 对应 pending_choice。RuleEvaluationResult 四态不变，CommandReceipt 不增加 unsupported 状态，能力不支持可用 rejected + 授权结构化原因表达。Schema/运行时/传输错误与规则拒绝分开，提交未知先查询 (session_id, command_id)。结构化原因经权限过滤供 Planner 使用，拒绝不会强制再调 LLM；重试/重规划按 §2.2。

Narrator 保持游戏世界内的沉浸叙事，不把内部 API、Schema 或 unsupported 错误直接作为玩家叙事。但能力限制不能成为“墙壁永久不可摧毁”“骰点已失败”或“世界已改变”的无依据世界事实；Planner 可以提出合理情境解释，权威效果仍须正式提交。必要的能力/运行时提示由文字入口以可理解方式表达，不伪造机械结果。Narrator 没有写权限。

## 4. State Machine → Rule Engine：RuleEvaluationRequest（P0）

本章的结构决策为 `[DECIDED]`；API、具体类型定义及示例消息版本仍为 **`[PROPOSED; NOT IMPLEMENTED]`**。以下 YAML 展示字段关系，尖括号为类型/数据占位，不是可执行 Fixture；`module-contracts/0.2` 是本轮候选消息版本，与文档版本分开。

### 4.1 请求结构 `[DECIDED; NOT IMPLEMENTED]`

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

该 combat.intent 示例分支的顶层字段均 Required。共同字段的 Required 约束不变；actor_id 是否必填按 operation_kind 的具体强类型分支决定（AP-15，§3.1），Actor 行动必须保留真实 actor_id。受信系统/世界事件分支可无行动 Actor，但 SM 必须核验 principal、机械来源、目标和范围，并以可信内部调用上下文/受控来源关联交 Engine 校验；source_ref 与来源权限编码仍 [PROPOSED / OPEN]，不在本轮冻结新字段。SM 保留 `(session_id, command_id)`，提供 Session 固定规则配置、权威 Snapshot 和独立 RNGContext。Engine 不接受 Agent 自报快照/身份，不在执行中读取旧权威 `_LiveCombat` 注册表或进程全局随机状态。标准 Required / Optional、类型与联合判别校验失败属于 Schema / 输入错误，不伪装为规则拒绝。

`operation_kind` 选择操作级 Payload Schema（如 CombatIntentPayload、AbilityCheckPayload、SavePayload、RestPayload）；`payload` 必须是对应强类型数据。CombatIntentPayload 内的 `intent_type` 区分 attack / cast / move 等动作子类；两层判别职责不同，不能合并，也不接受任意字典或自然语言代替 Payload。具体操作枚举与字段覆盖按已支持规则审阅，不因示例推定全部已实现。

### 4.2 StateSnapshot：CombatSnapshot / NonCombatSnapshot `[DECIDED; NOT IMPLEMENTED]`

StateSnapshot 是两种明确 Schema 的判别联合，均只读、版本化，共享必要的 CharacterState、EffectState、InventoryState、SceneMechanicalState 等基础结构。RNGContext 是独立输入，不嵌入 Snapshot。

| Schema | Required | Optional（仅按对应 Schema） |
|---|---|---|
| CombatSnapshot（snapshot_kind=combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state、combat_state | component_versions / 显式 read_set 等版本辅助信息 |
| NonCombatSnapshot（snapshot_kind=non_combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state | component_versions / 显式 read_set 等版本辅助信息；不含 combat_state |

`character_states` / `effect_states` 的集合元素使用相同基础 Schema，库存等组件按基础类型引用/组合。无相关效果时合法空集合仍须明确提供；可选字段的省略/null 规则由普通 Schema 定义，不引入额外缺失状态分类、缺失原因枚举或按 Intent 动态裁剪字段的机制。

SM 可以按相关实体与 Scene 限定集合范围，但每个纳入实体的机械状态必须完整，并保留规则依赖闭包，包括会影响它的其他实体、来源、区域与生命周期账本。不能因本次只攻击而省去该角色的反应、装备或持续效果字段；不能把非战斗检定伪造成 Combat。缺 Required 字段报 Schema 错误，完整输入所需的规则路径尚未支持则显式 unsupported，不以隐藏 Engine 状态补齐。

| 基础领域 | 完整机械状态必须覆盖的语义（具体字段映射仍待实施核对） |
|---|---|
| CharacterState / InventoryState | HP / Temp HP / Death Saves、能力与规则特性、资源池/法术位、库存/数量、装备、动作来源及有限使用次数 |
| CombatState | Combatant roster、Initiative、Round / Turn / Phase、Action Economy、Reaction、移动预算、位置/Reach/Topology 及跨步骤账本 |
| EffectState | Conditions、Concentration、Active Effects、来源与目标、持续时间、持续区域、过期/撤销条件，战斗内外复用 |
| SceneMechanicalState | 必需场景、对象、障碍、光照/遮蔽、环境规则与关系及版本；不传入无关剧情秘密 |
| Pending state（适用时） | 已支持的选择/活动引用与版本；复杂中途 Reaction Continuation 仍 [OPEN]（§8） |

该表不是现成代码类型。实施前需盘点历史 `_LiveCombat` 的 sidecar，区分权威/派生/临时字段并验证完整依赖，不能仅迁移 HP / Turn。

### 4.3 RulesetBinding `[DECIDED; NOT IMPLEMENTED]`

RulesetBinding 的 Required 字段为 `ruleset_id`、`data_revision`、`evaluator_version`。SM 从 Session 固定配置提供；Engine 在求值前验证三者与实际加载规则/数据/求值器匹配，不匹配报独立绑定错误并禁止继续求值，不能静默换规则版本。

`data_revision` 必须区分**实际生效的规则内容**，包括适用的 Homebrew / 数据覆盖及组合；不能只用基础 SRD 名称代替生效内容修订。具体摘要/组合编码为 [OPEN]，本轮不决定发布/热更新机制。固定 RNG seed 也不能替代此绑定。

### 4.4 Action Availability Query `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

独立只读查询供 UI / Agent Planning 查看候选行动的当前可用性，复用明确 Snapshot / RulesetBinding 与按 operation_kind 类型化的 payload：

```text
query_action_availability(session_id, actor_id, operation_kind,
                          payload, state_snapshot, ruleset_binding)
  -> ActionAvailabilityResult(status=available | unavailable | unknown,
                              input_world_version, permitted_reasons)
```

SM 负责授权并构建完整机械快照；Engine 做只读规则查询，SM 向 UI/Agent 返回经权限过滤的结果/原因，不暴露隐藏实体或不可知限制。接口名称与具体查询字段仍 Proposed。

查询不需要 command_id / RNGContext，不掷骰、不修改状态、不生成 StateDelta / ProposedEvents、不产生 CommandReceipt。unknown 表示查询能力不足或当前无法确定，不等于执行合法。available 仅针对查询时快照，不预留资源、不保证后续执行成功；正式 Typed Command 必须重新鉴权、取 Snapshot / RNG 并验证。完整技能列表和全量目标枚举不属于本轮 P0 必须实现功能。

**[DECIDED] 实施顺序**：该查询不依赖 Visual Presentation，可与早期 Rule Evaluation Adapter 同步开发，先覆盖基础战斗操作的只读合法性判断并与正式求值共享同一规则逻辑，避免第二套规则系统。当前文字 MVP 不强制调用此接口；视觉 UI 仍为 Post-MVP。此处只更新计划，不代表已实现。

## 5. Rule Engine → State Machine：RuleEvaluationResult（P0）

### 5.1 四种结果与字段约束 `[DECIDED; NOT IMPLEMENTED]`

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
- needs_choice 仅按 §8 的 MVP 前置选择路径返回；不提交部分伤害、资源或 RNG。SM 可另存授权 PendingOperation 元数据，不把它当机械结果。
- unsupported 明确能力不支持，禁止静默成功或部分执行。
- **Schema / 输入错误、RulesetBinding 不匹配、运行时异常、传输故障在四种规则结果之外处理**，使用独立错误类别/传输反馈（§11），不能改报 rejected，也不新增第五种 RuleEvaluationResult status。失败响应不携带可提交 Delta / RNG；提交状态未知仍由 SM 按命令键查持久记录。

### 5.2 StateDelta：封闭 Typed Operation Union `[DECIDED; NOT IMPLEMENTED]`

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

一次求值的多目标、多 Activity、资源支付及所有连带变化必须完整表达为有序操作，构成**一个不可分割的提交单元**；任一校验失败全部不写。SM 校验类型、权限、读写范围、版本、归属和组合不变量，不重算 D&D 伤害/成本。复杂 Effect / Reaction 等组件的完整字段为 [OPEN]，不把表中候选名视为已冻结 API。Quest / 剧情秘密等世界流程仍由受信世界操作管理，不授权 Engine 任意改写。

首个黄金用例仍为：同一 Actor 消耗药水、恢复 HP、支付行动预算并生成事件，在同一 SM 事务全部成功或全部失败。

### 5.3 ProposedEvents → CommittedWorldEvent `[DECIDED; NOT IMPLEMENTED]`

Engine 返回有序、类型化的候选机械事件，不分配权威 event_id / event_seq。SM 在提交 StateDelta、RNG、CommandReceipt、Outbox 的**同一事务**内分配正式事件身份/序号并保存；只有 COMMIT 成功后才成为 CommittedWorldEvent，对外发布见 §7。

正式事件保留 `(session_id, source_command_id)` 与命令来源；这里的 source_command_id 是事件关联字段，不是额外的规则操作标识。SM 直接应用并校验 Typed Delta，不根据 ProposedEvents 再计算 HP、伤害或资源扣减。NPC Perception、DM Narration、UI 只能获取经授权的事件/回执投影，不直接获取候选事件或全量隐藏机械细节。

## 6. State Machine Atomic Commit 与 CommandReceipt（P0）

### 6.1 执行时序 `[DECIDED; NOT IMPLEMENTED]`

```text
Typed Command -> authenticate / authorize / (session_id, command_id) lookup
-> obtain CombatSnapshot or NonCombatSnapshot + pinned RulesetBinding + RNGContext
-> Rule Engine.evaluate(RuleEvaluationRequest)          [outside DB write transaction]
-> accepted result -> begin short SQLite transaction
   -> re-check fingerprint / existing CommandReceipt / authoritative versions
   -> re-check read set, permissions, ruleset pin, typed Delta invariants
   -> apply all StateDelta + authoritative RNG successor
   -> allocate event IDs / sequence and persist committed events
   -> persist CommandReceipt + idempotency + Outbox
-> COMMIT -> return CommandReceipt / publish only permitted committed projections
```

非 accepted 不进入上述机械提交；可持久记录结构化拒绝、冲突或前置选择元数据，但不写部分机械 Delta / RNG / 候选事件。Schema / 异常 / 传输错误分别处理，不伪造规则结果。

**OCC / 幂等**：SM 承担权威版本、Fingerprint、权限、Delta 不变量与短 SQLite 事务。过期 Snapshot 返回 version_conflict，或在授权/有界条件下重新取完整 Snapshot + RNG 重算，不能把旧 Delta 套在新状态上。持久唯一键 `(session_id, command_id)` 防双提交；相同已提交请求只查原回执，不重新求值。并发/重算的内部尝试不增加公共操作标识。

### 6.2 CommandReceipt `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

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

上述是 committed 分支字段关系。committed 必须与全部状态/RNG/正式事件/Outbox 同事务落盘，只能在 COMMIT 成功后对外报告。rejected / conflict 必须有结构化原因、不含已提交机械事件；pending_choice 仅关联获授权的 PendingOperation。各分支具体类型与字段可空性仍 [OPEN]，不能据此增加另一套回执协议。

RuleEvaluationResult 与 CommandReceipt 的状态不共用枚举：规则 accepted 经成功提交才对应 committed，规则 rejected / unsupported 可对应 rejected 并保留原因，needs_choice 对应 pending_choice；版本冲突对应 conflict。Schema / 异常 / 传输错误保持各自错误类别，不因此增加规则结果状态；尚未确认提交时先查询持久命令记录。

响应丢失用 `get_command_receipt(session_id, command_id)` 查原结果；已提交不因反馈失败回滚，不更换 ID 再执行。只读 Availability Query 不走该回执。world_version 对机械/世界状态变更单调推进；**仅事件/元数据提交是否及如何推进 World Version 为 [OPEN]**，不在本轮用事件序号代替状态版本或冻结空提交策略。

### 6.3 RNGContext / RNGTransition `[DECIDED; NOT IMPLEMENTED]`

- RNGContext 与 StateSnapshot 是独立输入，均由 SM 提供。Context 显式包含算法/编码版本、stream_id、stream_version、可恢复的 PRNG state；具体算法和序列化编码为 [OPEN]，示例不指定 Python 随机实现。
- Engine 只使用该显式状态在临时求值上下文计算，accepted 必须返回 RNGTransition，绑定输入流/版本及 next_state；不读全局随机源，不由 Engine 推进权威流。
- **只有 SM 原子提交成功才推进权威 RNG**。规则拒绝、unsupported、前置 needs_choice、冲突、回滚和未提交异常都不推进。合法未命中等 accepted 结果的随机消耗随完整提交落盘。
- 合法且无随机消耗的 accepted 操作允许 next_state 与输入完全相同；不能为了提交而制造随机调用。RNG 流版本如何表达无消耗提交仍 [OPEN]，不据示例固定为 world_version。
- `draws` 可作为审计辅助字段，不强制完整底层随机调用轨迹。确定性验证依据显式前后状态、固定 Payload / Snapshot / RulesetBinding 与可核验机械结果，不把可选 draws 当正确性的唯一证据。
- 一条 Session 流足够作为 MVP 默认；重算从重新读取的当前权威 RNG 开始，已提交命令只返回原 CommandReceipt。不以 seed 单独承诺跨数据/求值器版本 replay。

### 6.4 原子性与故障 `[DECIDED]`

`StateDelta + RNG + CommittedWorldEvent + CommandReceipt + Outbox` 同属一个 SQLite 事务，全部成功或全部失败。LLM/Rule Engine 求值及对 UI/NPC 的发送均在写事务外；提交后投递失败由 Outbox 幂等补偿，不回滚已提交世界事实。Schema 错误、求值异常、传输故障、Commit failed/unknown 与 committed response failed 必须分别报告，不能一律要求重新掷骰。

## 7. WorldEvent → Perception → NPC Evidence（P0/P1）

### 7.1 CommittedWorldEvent 与 Observable Signals `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

本节整合 PER-01～PER-08：CommittedWorldEvent + Observable Signals → Scope Discovery → Deterministic / JEV Perception Judgment → Authorized ObservationRecord → 既有 NPC Inbox。不新增模块、感知状态机或独立认知流程。

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

### 7.2 Discovery、判断与 Observation `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

**事件时证据与 Discovery：** SM 在事件提交事务内保存足以恢复 NPC/位置/感官/环境/相关状态的证据或稳定历史引用，以及可靠待处理工作；不要求保存完整 World Snapshot。Discovery 先按每个 Signal 的类型化 Scope 找候选 NPC，再按事件时状态确定性检查感官能力、位置、明确遮挡及已支持的机械约束。不能用异步处理时的当前状态倒推历史，也不能只发现在线 NPC。全局/大型事件允许可靠分批 Discovery，沿用持久任务/Outbox、去重和恢复，不强制一次枚举全部 NPC。

**JEV Perception Judgment：** 只有确定性条件无法判断的情境才交 JEV，明确可判定的 Signal 不必提交。SM 授权、Host 运行，提供最小必要的事件时可信 Observer 状态、相关环境及待判断 Signals；JEV 只逐项判断是否察觉，不生成 Signal、Observation 文本、Belief / Goal / Plan 或世界变化，也不替代 NPC Gate / EVA。具体模型/传输仍为候选；调用在写事务外。

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

在 Commit 同事务内记录事件时证据/稳定历史引用与待处理 Discovery / Projection 工作；投递至少一次。默认聚合按 `(observer_id, event_id, projection_version)`（或等价唯一键）幂等写 Observation；持续事件分时新观察的时刻区分/等价键编码 [OPEN]，不强制合并。NPC 不在线时仍保存应收到的 Event Observation 或可靠重放证据。**原始事实、感知记录、角色信念三者分别持久存储**；`Belief` 不等于 World Fact。

- 分批 Discovery / 判断未完成时不能越过投影水位；全部未察觉也须可靠记录处理完成，不用空 Observation 冒充感知。具体分页、历史保留和索引字段 [OPEN]，沿用既有工作机制。
- `observation_id` 稳定，按 NPC 提供顺序可核验的 Delivery Cursor；相同事件多个 Observation 的次序需有稳定 tie-break。分页返回投影完成水位/等价完整性证明，不能因较早事件还在 Outbox 而让消费跳过它。
- 读取 Cursor / Host 已追加 Context 位置与 SM 内部 Processing / Completed Cursor 分离。读取、追加或模型返回不等于处理完成；SM 仅按必要认知处理与可靠输出交接的持久完成状态推进连续前缀，见 §9.6，不要求 Host 额外 ACK。
- SM 为待处理 Observation 批次建立稳定 `observation_work_id`、任务及幂等处理记录；重复投递不创建第二份逻辑工作。合并批次不能重复占用尚有任务的同一观察；具体索引/表结构未冻结。
- Mode Routing、Gate 领域策略、证据保留和任务完成由 SM 管理；Host 按授权请求执行 Context 追加或模型调用。失败不随 Context 释放而丢失证据。

## 8. Pending Choice / Reaction / Continuation（P0 语义，MVP 限制实现）

**历史代码审阅限制（本轮未重审实现）：** v0.1 基线的 Reaction 主要提前 `ready`，未证明有完整的“解析到一半停下并等待 NPC/PC 选择”的公共可序列化 continuation；不得据目标契约宣称现有代码已支持。

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

本节新增消息、字段、接口及生命周期均为 **`[PROPOSED; NOT IMPLEMENTED]`**。职责原则已确认，具体类型、状态编码、版本与数据库结构仍需审阅；不要求新增服务或复杂公共 Receipt 子系统。

### 9.1 EVA、NPC Meta 与 LLM Runtime `[DECIDED]`

**EVA（NPC Evaluation）是认知更新与决策评估，不是 Action Execution。** Memory、Belief、Relationship、Goal、Plan 构成一次原子 NPC Meta 更新单元。NPC 可以提出 Dialogue 与 Action Intent，但实际发布/执行有独立授权和处理路径。

| 所有者 | 职责 | 边界 |
|---|---|---|
| State Machine | 唯一权威 World / Character / Combat / RNG / NPC State、Evaluation Task / Status、模式、Gate 领域政策、Observation / Evidence / Completion、游戏时钟日程、验证、事务及恢复 | 不执行 LLM 主观推理，不管理物理 Context，不做自然语言语义验证 |
| Agent Host | Prompt / Context Builder、Interactive Context 复用/释放、Background One-shot Context、模型执行队列、超时重试取消、Token / Cache、Tool 适配传输、Invocation 日志/延迟/Usage | 不拥有或持久管理权威游戏状态、Meta、任务完成或行为结果；不做语义筛选 |
| NPC LLM | 基于完整授权 Meta 与观察决定主观认知变化、对白和候选行动 | 只生成预定义 Schema 的非权威数据；不决定身份、任务资格或世界事实 |
| Action Execution | 受限 Action Intent → 稳定 command_id / Typed Command → 必要 Rule Evaluation → SM Commit | 独立 Command Receipt；动作成功不是 EVA 完成条件 |

统一逻辑流 **SM → Host → NPC LLM → SM**。SM 创建/批准任务并提供可信授权输入，Host 组织调用和传输 Result，SM 确定性验证、提交 Meta 并可靠交接输出；Host 将反馈送回相应调用。§2–§6 的可信 Host / 调用方描述指受控传输与命令构造，最终领域权限与提交仍由 SM 检查。

`interactive / inactive` 是 SM 管理的当前 NPC 模式状态；`interactive / background` 是 Evaluation Mode。Interactive 活跃（包括模型请求间空闲）期间，主观 Memory / Belief / Relationship / Goal / Plan 和自主决策均交当前 Interactive LLM；不额外调用 Gate / Background / Memory / Cognition LLM。授权观察按序增量追加，不修改运行中请求或 KV Cache。

Inactive 时 SM 的 Lightweight Gate 可决定 Safe Retention / No-op 或创建 Background Task；可选轻量分类由 Host 执行、SM 验证采用，不代 NPC 生成 Belief。Background 使用一次性 Context，不创建/恢复/激活 Interactive Agent，也可提出行动。Gate 只管领域触发和证据保留，不为 EVA 语义筛选或排序 NPC Meta；Jev 仍为可替换候选。

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

SM 持久 Task 保存 Session/NPC、Evaluation Mode、授权范围、NPCStateVersion、观察/Work、当前输入及已选结果/处理状态。NPCEvaluationRequest 是 SM → Host 的模型运行请求，不同于 P0 RuleEvaluationRequest：

```yaml
schema_version: npc-evaluation/0.1  # 候选消息版本，具体约束待冻结
evaluation_id: eval.guard-a.bg.005
mode: background
reason: significant_observation
observation_work_id: work.guard-a.005
expected_npc_state_version: 8
authorized_npc_meta_ref: meta.guard-a.008.complete
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
| SM → Host NPCEvaluationRequest | 已授权 Task、完整授权 Meta / Observation、当前玩家输入（适用时）；Host 执行对应模式 |
| Host → SM submit_npc_evaluation_result | evaluation_id + NPCEvaluationResult；返回结构化 EvaluationReceipt 或验证错误 |
| Host → SM 授权 View / Observation 读取 | 提供完整授权 Meta、事件观察/当前感知；读取不完成任务 |
| Host → SM Runtime 状态 / Gate 分类反馈 | 非权威调用失败/取消/Context 状态或分类候选；SM 维护 Task 与领域结果 |
| Action Execution → SM Typed Command（§3） | 独立稳定 command_id、受限 Actor/Intent；按 §6 提交与查询 Command Receipt |

EvaluationReceipt 只是 EVA 的结构化处理反馈，可包含任务状态、Meta 提交版本、确定性验证错误及 Dialogue / Action Intent 交接信息；类型待冻结，不新增独立服务。读取/状态查询复用本地 Task 持久记录。不要求 Host 独立 ACK，也不要求独立领域 disposition 或模式写入握手。

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

SM 内部 ObservationProcessingStatus 根据必要认知处理和可靠输出交接状态维护；Safe Retention / No-op 可确定性完成观察，全空 Result 可完成 EVA。读、Context Append、LLM 返回、模型失败或任务取消本身不代表处理完成。内部 Completed Cursor 不跨未完成认知/未可靠交接项或投影缺口，无独立 ACK。

Command 正在执行、失败或等待 choice **不自动使已完成 EVA / 已可靠交接的观察重新变为未完成**；未完成的 Command / PendingOperation 仍单独持久跟踪。动作失败反馈可送现有 Interactive LLM 继续动作交互，不自动重做完整 EVA 或再次写 Meta；若确需新的认知评估，由 SM 显式授权新任务，而非重放旧结果。

### 9.7 完整授权 NPC Meta、Belief History 与恢复 `[PROPOSED; NOT IMPLEMENTED]`

MVP 由 SM 提供该 NPC **完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan** 及新 Observation；授权完整不意味着全量世界/他人秘密。首次构建或重建 Context、Background One-shot 输入完整授权 Meta，Host 只组装，不做 Semantic Retrieval、Memory Ranking、语义筛选或智能压缩，也不增加独立 Memory Agent。超出模型预算明确反馈/保留任务，不能静默漏掉 Meta。

已有 Interactive Context 可复用，后续增量追加授权观察和已提交 Meta 变化，不要求每 EVA 重注入全量 Meta。Memory Persistence 与 Context 资源管理保持分离；MVP 可预算保护、释放/重建 Context，不增加语义总结压缩。更复杂检索/压缩后置。

Adventure Package Initial Belief 与运行时 Belief 使用兼容结构：同一稳定 Belief 追加新版本，保留来源、版本、当前有效状态及旧历史，不直接覆盖/删除。NPC LLM 可修改、降低置信度或放弃旧 Belief；SM 仅校验结构、引用、权限、版本和数据库约束，不替它改写文本。

SM 持续不可用或持久化失败时，Session 停止权威推进，进入暂停/错误/待恢复流程；不能写库时不伪称状态已落盘。Host 不接管游戏状态，无影子权威副本或独立游戏执行队列。恢复依据 SM 持久 Task、已选 Result / Meta、可靠交接和独立 Command Receipt，不重做成功认知或行动；非战斗恢复必需，战斗中断精确续玩仍 Post-MVP。保留单命令响应丢失的幂等查询，不增加分布式协调系统。

## 10. Adventure Package → State Machine（P1）

**[DECIDED]** Package 是静态、版本固定的数据定义，SM 独占加载后的 Session / Scene / Encounter 初始化、触发与运行时提交。统一逻辑入口及候选类型均 **[PROPOSED; NOT IMPLEMENTED]**，详细字段仅在 [Adventure Package §9.1 / §9.1a](./ADVENTURE_PACKAGE_SCHEMA.md#91-统一-package-loading--validationap-0104) 定义，避免另起一套协议：

```text
load_adventure_package(package_source)
  -> PackageLoadResult(valid | invalid, structured errors / warnings,
                       approved identity / digest / effective RulesetBinding when valid)
create_session(CreateSessionRequest)
  -> Session ID + creation result + limited metadata
```

加载内部完成安全解析、Schema、引用、规则绑定、声明式操作与必要元数据检查，不暴露半验证状态或独立验证服务。必要机制不支持、Schema/非法引用阻止批准；非核心可选限制可明确 warnings，不能运行时假装支持。valid 后固定 adventure_id / package_version / package_digest / 生效 RulesetBinding。静态验证不证明剧情可玩性/平衡，来源元数据不自动证明版权合法。

CreateSessionRequest 使用 command_id、批准 Package 的身份/摘要和 **players[]**（每项 player_id / pc_template_id，MVP 严格一玩家一 PC）。PC Templates 是 Package 内完整且机械属性经规则验证的只读定义，不要求外部 pc_build_ref 或独立构建服务。principal_id 取自可信认证环境并验证 player/角色控制关系；创建前以 **(principal_id, command_id)** + Fingerprint 幂等，相同请求返回原 Session，不同内容冲突。session_id 由 SM 生成并返回，不新增创建请求/Receipt ID；普通游戏命令仍用 (session_id, command_id)。

SM 在短事务核验固定内容与创建键，原子初始化 SessionRecord / WorldState / 当前必要 Actor/NPC Persistent State / 选定 CharacterState / 入口 Scene / RNG，并保存创建幂等结果；失败不留下半初始化有效 Session。返回有限元数据，不泄漏隐藏世界。Scene 按需初始化一次、NPC 为 Session 级唯一实体，重访不重置；EncounterDefinition 可选，SM 可动态启动具有可信规则数据的 Encounter。

两个规则调用场景复用 §4–§6，不新增执行协议：

| 场景 | 候选 operation_kind / 输入 | 处理边界 |
|---|---|---|
| SM 决定启动 Encounter | combat.start；当前相关 NonCombatSnapshot、固定 RulesetBinding、显式 RNGContext、强类型启动 payload | Engine 在 accepted 时返回 Typed Delta / ProposedEvents / RNGTransition，SM 原子建立权威 CombatState；候选 combat.create 的具体字段 [OPEN] |
| SM 判定 Trap / Hazard / Mechanical Effect 触发 | rules.effect；适用 Snapshot、同一规则绑定/RNG 输入、强类型效果 payload | Engine 算豁免/伤害/Condition，SM 提交；按 AP-15 的具体类型校验 Actor；无行动 Actor 的受信系统/世界事件来源允许受控分支，source_ref / 权限编码仍 [PROPOSED / OPEN]，见 §3.1 / §4.1 |

上述操作/类型 **[PROPOSED; NOT IMPLEMENTED]**。同命令世界效果与机械结果可在提交前完整求值时统一原子提交；若来源 WorldEvent 已提交，再触发效果则可靠交接独立稳定命令，去重/恢复，不承诺跨两个已提交事务原子性，不重复已提交骰点/伤害/奖励。详细编排与复杂 Effect Schema 为 [OPEN]。

EventDefinition 是静态 Trigger / Condition / Effect 声明，CommittedWorldEvent 由 SM 经受控命令提交；动态事件无需全部预定义。SM 按作用域管理触发历史与允许世界效果，规则计算交 Engine，不增加独立 Event Engine 服务或任意脚本。RuntimeState 不写回 Package；公开资料只用原创合成示例，First Blush 内容/派生资产仍留本地私有。

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
| `committed` | State Machine 已原子提交全部效果 | RNG、状态、Event、Receipt 全部提交 |
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
7. **显式敌方 NPC Intent：** 至少一个敌方 Sub-agent 选择其自身受权限约束的战术意图，经 Rule Engine 求值 + State Machine 提交；不是冒用 PC 身份，也不是内置 Monster AI 假装 Sub-agent。
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
| C-A13 | Interactive 新增 Observation | 原 Context 按序追加；只有当前 Interactive LLM 处理，额外 Gate / Background / Memory / Cognition LLM 调用数为零 |
| C-A14 | Active Context 暂时无模型请求，重大事件到达 | SM 批准下一次 Interactive Task，Host 执行请求；在途调用期间新增输入排队，不修改执行中请求/KV Cache |
| C-A15 | Interactive Result 含 Dialogue、Belief、Memory、Action Intent | Meta 整批验证原子写入，行动独立 Typed Command，不回滚合法 Meta；全空 Result 合法 |
| C-A16 | Inactive NPC 经 Gate 一次 Background Evaluation 产生行动 | 无 Interactive Agent Context；同一 NPC 权限与共享命令路径，临时 Context 调用后释放 |
| C-A17 | 低价值 Observation / 轻量模型不可用 | 不调用完整 NPC LLM或按保守策略留待处理；Safe Retention / No-op 有回执，关键证据不丢失 |
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
| C-A34 | 完整授权 Meta 与 Belief History | 六类 Meta + 新观察，Host 不语义筛选/检索/排名/智能压缩，Context 增量复用；Belief 版本追加保留历史 |
| C-A35 | 非忠实 Memory / 错误 Belief | SM 只确定性校验引用等，不证明自然语言忠实、不改写文本、不新增 Semantic Validator LLM；不改 World Fact |

## 13. 尚需显式批准或验证的开放问题

| ID | 问题 | 初步建议 / 决策要求 |
|---|---|---|
| C-01 | `_LiveCombat` 哪些字段权威、哪些可推导？ | 先做字段/读写路径 Inventory，生成快照依赖矩阵；这是任何重构前阻塞项 |
| C-02 | Engine 对外 `evaluate(...)` 与 NPC `combat.intent` 的最小 Python Typed Schema？ | 本草案用于语义审阅，字段名称/类型待代码适配论证，禁止先行声称已实现 |
| C-03 | PRNG 算法/编码及无消耗时 RNG 流版本策略？ | [OPEN]；显式状态/原子推进原则已确认，具体 wire format 与版本需实现对照和确定性测试 |
| C-04 | 复杂中途 Reaction Continuation？ | [OPEN]；MVP 前置选择/预先声明不提交部分机械结果，中途暂停需按真实规则路径另行设计 |
| C-05 | 每个普通怪物是否需要独立 LLM Sub-agent？ | **仍未决定**。但 MVP 必须验证至少一条真正敌方 Sub-agent 显式 Intent 路径 |
| C-06 | 部分规则不支持时如何安全回退？ | `unsupported` 明确拒绝或人工裁决提议；严禁 Narrative 假装规则结果 |
| C-07 | 版本粒度及仅事件/元数据提交的 World Version 推进？ | [OPEN]；MVP 全局 OCC 保守方案，状态变更单调推进已确认，事件型提交推进细则不在本轮冻结 |
| C-08 | 活跃战斗崩溃中断后如何避免覆盖已提交结果？ | 明确 `combat_interrupted` 与安全恢复/阻塞协议；精确续玩 Post-MVP |
| C-09 | 消息版本、Fingerprint 规范及生效规则数据修订编码？ | [OPEN]；三字段 RulesetBinding 与含适用 Homebrew 的内容可区分性已确认，具体 canonicalization/摘要组合和候选消息版本需 ABI 审阅 |
| C-10 | PendingOperation 生命周期与 CommandReceipt 分支字段？ | [OPEN]；仅命令键查询、无独立回执 ID/ACK 已确认；具体持久性、过期与可空性由 SM 实施设计验证 |
| C-11 | EvaluationStatus / NPCStateVersion、Work / Task、唯一 Result 与可靠交接的最小存储/编码？ | 原子撤销旧 EVA 并新建、Meta 事务内校验任务/版本；状态编码、稳定 Result 比较和恢复实现待论证 |
| C-12 | Observation Cursor、投影水位、批次合并及内部 ProcessingStatus / Completed Cursor Schema？ | 需证明不跨越未投影/未完成项，明确必要认知处理、可靠交接及独立 Command 重入；具体类型待冻结 |
| C-13 | Gate / 两种模式的模型、Prompt、阈值、预算与取消能力？ | Jev 仅候选；通过合成场景测定漏判/延迟/成本，不擅自固定技术选型或 SLO |
| C-14 | NPCEvaluationResult / EvaluationReceipt 的字段类型、元素约束、版本与错误映射？ | 七字段概念结构及两模式兼容原则已确认；JSON Schema、可信运行环境绑定和持久任务编码待审阅，不把草案当成已实现 API |
| C-15 | 完整 Effect / Reaction / 复杂组件 Delta 字段？ | [OPEN]；封闭 Typed Union、完整依赖与原子提交已确认，字段须对照现有生命周期与不变量盘点，禁止任意路径或 Snapshot 覆盖 |
| C-16 | combat.start / combat.create、rules.effect 与触发后续命令？ | AP-15 按操作类型校验 Actor 已 [DECIDED]；source_ref / 来源权限、具体字段与可靠编排仍 [OPEN]，见 §3.1 / §10 和 Adventure Package §11；不扩张为独立服务 |
| C-17 | 动态 World Operations 与 Conditional World Effect Proposal 的具体 Schema？ | [OPEN]；受限类型、SM 稳定身份、授权投影和提交边界已确认，完整 Object / Connection 字段、结果关联及复杂 Scene / 战斗地形生成未冻结 |
| C-18 | Observable Signal / Scope、结果条件与传播 Schema？ | [OPEN]；最小四字段/事件内 ID 与确定性范围原则已确认，具体枚举、复杂空间关系/传播参数、模板绑定与分时观察键仍待设计 |
| C-19 | 正式感知检定与异步处理的事务编排？ | [OPEN]；RE 负责规则掷骰，事件时历史引用/保留、可靠批处理与 RNG / command / 事务衔接须实施设计，不由 JEV 替代 |

## 14. 建议实施顺序（在本契约评审通过之后）

**Batch 0 — Contract review / State inventory：** 对照 `orchestrator.py`、`types/combat.py` 和现有测试列出权威/派生状态字段、RNG 读写点、Effect 生命周期、NPC Intent 空缺。修复契约歧义，不改大规模业务代码。

**Batch 1 — Evaluation Adapter 最小纵切：** 在测试分支把**一条** `combat.intent`（可以从基础攻击开始）转换为从 Snapshot 输入/结果 Delta 输出的无权威状态评估；兼容旧执行器对照测试，保持旧公开 API 不受影响。可同步开发基础战斗操作的只读 Action Availability Query，共享规则合法性逻辑且无 RNG/状态写入/Delta/事件/回执；不等待 Visual Presentation，也不作为当前文字入口的强制依赖。

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
