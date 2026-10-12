# Agentic TRPG — Module Contracts（目标架构与 MVP）

> **版本：** v0.12 / Draft for Review
>
> **日期：** 2026-10-12
>
> **性质：** 跨模块目标接口的最高权威规范；具体 ABI 仍为草案，**不是已实现 API**
>
> **归属仓库（建议）：** `agentic-trpg/agentic-trpg/docs/MODULE_CONTRACTS.md`
>
> **配套文档：** [MVP Scope](./MVP_SCOPE.md) v0.14、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.8、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.14、[Agent Architecture](./AGENT_ARCHITECTURE.md) v0.12、[Evennia Adoption Plan](./EVENNIA_ADOPTION_PLAN.md) v0.1（复用与验证计划，遵循本文）
>
> **历史代码核对基线（§1 历史表沿用 v0.1，2026-10-12 前批有限核对见 §1.1）：** `agentic-trpg/agentic-trpg@4190833`；`agentic-trpg/trpg-rules-engine@64dd920`
>
> **标记：** `[DECIDED]` 已有架构决定；`[PROPOSED]` 本文推荐、待评审；`[OPEN]` 需要进一步决策；`[NOT IMPLEMENTED]` 不可宣称现有代码已有

## 0. 用途与冻结策略

本文定义 Agent Host、State Machine、Rule Engine、Perception、NPC Evaluation、DM Narration 与 Adventure Package 的交接边界。既有规则契约与最小安全边界继续作为设计依据；当前优先执行 §14 的 Evennia 验证，本批不冻结新 ABI，也不将全部 RE 迁移设为基础验证前提。v0.5 统一 P0 Snapshot / Request / Result、封闭 Typed Delta、ProposedEvents、独立 RNG、CommandReceipt 和只读 Availability Query，并澄清 Invocation 错误不立即终止有效 EVA。v0.6 统一 Adventure Package 加载、可信创建幂等、静态模板与 SM 运行时边界（§10），候选 combat.start / rules.effect 复用本协议。v0.7 统一 submit_command / GM Adjudication、有限动态世界操作和 AP-15 按操作类型校验 Actor，并同步只读查询的早期开发计划。v0.8 将 PER-01～PER-08 接入既有事件/可靠工作协议（§7），区分 Signal、察觉判断、授权观察与 NPC 认知。v0.9 明确 OB 短期记忆、独立 Processing / Retention、Game Time TTL / 引用归档、JEV 双职责和有界 EVA 调度，当时未修改 Signal / Event Evidence 计算。

**v0.10 修订摘要（Batch A）：** §7 明确 Event-local / Signal-scoped Evidence、逐 Signal 候选发现与事件级证据并集、可信字段完整性及同一 SQLite 原子提交；区分 `trpg-state-machine@5deea78` 历史实现与目标，新增 §12.5 合成验收目标，事件阶段采集协议仍 [OPEN]。本轮仅更新文档，不实现 Event-time Perception P1。既有状态所有权、Rule Engine、OB 生命周期、Game Time TTL、EVA 调度与 MVP 产品范围不变；结构决策标为 [DECIDED]，具体 API/字段实现仍 [NOT IMPLEMENTED]，未冻结细节单列 [OPEN]。

**v0.11 修订摘要：** 统一 Immediate Mechanical Response / Agent Cognitive Response、WorldEpisode / EpisodeObservation、机械审计分流、状态式规则求值与 Interrupt / Continuation 目标；同步敌方 Agent 宏观自主性验收。§1 记录已核对的 SM / RE 基线，具体 Episode / Continuation ABI 仍 [OPEN; NOT IMPLEMENTED]。章节的目标接口标记不否认 §1 列明的受限本地实现；本轮只改文档，不升级依赖或实现接口。

**v0.12 修订摘要：** 正式记录 Evennia 优先底座、保留 RE、允许 SM 迁移/重构（§0.2）；明确 CombatEpisode 的整场战斗边界（§7.5）与受控 Coding Agent 扩展目标（§3.6），EB-1～EB-3 优先验证（§14）。方向已定不等于迁移或运行验收完成；既有代码基线与规则完成状态不变。

**规范层级 `[DECIDED]`：** 本文是跨模块目标接口与状态所有权的最高权威规范；MVP Scope 定义产品范围，State Machine / Agent Architecture 和 Adventure Package Schema 在此契约内细化职责，Evennia Adoption Plan 记录复用理由与验证门槛，README 提供入口。项目目标约束实现，旧 Nat20 / Rule Engine 代码只作为待重构的实现和回归证据，不能反过来限定目标架构。本文中的 [DECIDED] 约束持续有效；文档整体 Draft 不撤销这些决定，也不把 [PROPOSED] / [OPEN] 的具体 ABI 字段或实现选择升级为已批准。

**必须满足的不变量 `[DECIDED]`：**

1. 同一 Game Session 的每项游戏事实只有一个权威来源，游戏变化只由可信运行层验证并提交。本文 **State Machine / SM 指领域职责**，包括 World / Scene / Quest / Object、Character、Combat、资源/效果/Reaction、RNG、NPC 私有状态/观察/任务、版本与回执；不绑定旧 `trpg-state-machine` 的类、表结构或仓库。目标允许 Evennia 对象系统与领域服务分担不同事实，禁止同一事实在新旧 SM 各存一份并双向同步（§0.2）。
2. 最终 Rule Engine 是 **Stateless Rule Evaluation Engine**，彻底替代原 Stateful Combat 执行架构；不能持有独立权威 Runtime State 或直接提交数据库，也不能以持续扩张 Stateful Adapter 作为最终方案。其计算边界见 §4，迁移完成标准见 §14.1。
3. `evaluation.status == "accepted"` 不等于 `commit.status == "committed"`；拟议事件不得提前发布为 WorldEvent。
4. Agent 提交的是意图或提议，不是 HP、骰点、资源支付等机械事实；Narrator 消费已提交、经授权的事实。
5. 可重试、确定性、版本和授权均在可信系统边界实现，不能仅依赖 LLM 自律。
6. 可信提交必须保持原子性与短事务，**不得在写事务内等待 LLM 或长时间 Rule Evaluation**。SQLite + WAL 是旧 SM 的实现基线/原实施提案；Evennia 目标的存储映射、提交边界和数据库配置仍 [OPEN]，不以本轮固定后端或引入分布式协调。
7. NPC 只有一份 Persistent State；Interactive 活跃期间独占该 NPC 的 LLM 主观认知/自主行动，Background 一次性推理不需要 Interactive Agent Context。新消息/接口均为 `[PROPOSED; NOT IMPLEMENTED]`，架构原则确认不等于 API 已实现。

8. SM 创建/批准 Evaluation Task、管 Gate / 模式 / Observation Completion；Host 仅 LLM Runtime，不持久管理权威游戏状态或完成结果。

**状态机承担游戏领域逻辑、权威状态与合法性/权限/事务边界，不执行 LLM 主观推理、不管理物理模型 Context，也不重新实现 D&D 机械规则。**

### 0.1 Immediate Mechanical Response 与 Agent Cognitive Response `[DECIDED]`

| 路径 | 决策与执行 | 依赖边界 |
|---|---|---|
| Immediate Mechanical Response | SM 协调可信确定性机制、受控 Combat Policy 和 RE；即时战术、Reaction、自动效果、战斗触发通过受授权的 Typed Intent / 规则结果由 SM 提交 | 不依赖 DM Planner、JEV LLM、Memory Gate 或 EVA；所需察觉/规则资格必须来自可信确定性或机械判定，不把未知当已察觉 |
| Agent Cognitive Response | NPC LLM / EVA 解释授权经历，提议主观 Memory、Belief、Relationship、Goal、Plan、宏观行为和角色对白；Host 执行模型，SM 验证并保存 | 消费已经确认察觉的证据；认知延迟/失败不阻塞即时机械链，也不追溯改写已提交结果。玩家叙事仍由独立 DM Narrator 基于授权事实呈现 |

Combat Policy 是 SM 协调的可信非 LLM 行为职责，不新增 Agent、服务或仓库；它从已授权目标/策略约束及机械可知视图选择即时 Typed Intent，不能读取 NPC 无权知道的世界秘密。宏观目标可先由 NPC Agent 提议、SM 采用，之后即时执行无需每回合再次调用 LLM；策略更新只影响后续合法操作。策略算法、版本/授权字段与目标转换协议 [PROPOSED / OPEN; NOT IMPLEMENTED]。机械察觉不足须显式走受支持的机械判断或报告能力缺口，不能让 JEV 猜测后解锁攻击/Reaction。

至少一名敌对 NPC 的 Agent 自主性仍须验收：证明其独立认知/宏观决定实际影响后续受控行为与战后认知；仅运行固定 Policy 不算完成。旧版“敌方 Sub-agent 必须生成每次战术 Intent”的要求由此取代，具体产品验收见 MVP_SCOPE.md A03 / G10。

### 0.2 Evennia 采用与可替换运行实现 `[DECIDED]`

优先采用 Evennia 作为游戏运行底座，保留现有 D&D RE，允许迁移和重构 SM；这是已选择的技术方向，不是普通参考候选，也不代表迁移完成。实际复用对象、持久属性、模板、动作钩子、Script / 活动处理、建造工具和文字客户端，避免在 Evennia 内再造通用引擎。`agentic-trpg/Evennia_base` 为 **Planned / [NOT IMPLEMENTED]** 的游戏项目与运行集成层，优先固定版本依赖，不默认 fork Evennia；本轮不创建仓库、不安装依赖。

旧 `trpg-state-machine` 保留为现有实现、迁移资产与回归对照，暂不删除/归档/宣布废弃。优先保留已验证的授权、幂等、RNG、回执、规则集成、故障测试、NPC 私有状态与可靠处理语义，允许更换具体实现，不要求逐类逐表搬迁。新旧实现只用独立测试 Session 对照，不共同控制同一生产 Session。不同时接入 Evennia 与 Ranvier；CDDA / Ranvier 仅为机制借鉴来源。

不同表可保存不同事实，授权视图、只读 Snapshot 和缓存不构成第二权威；同一位置、资源或 NPC 状态不能因两套系统分别持有而双向同步。Evennia 对象/Attribute 与领域表如何映射、可信提交怎样覆盖状态/RNG/幂等/回执/可靠交接、对象缓存如何随回滚恢复，均 [OPEN]，须经过 EB 验证。下文 SQLite / WAL、现有表与 Event-level OB / Outbox 的具体描述属于当前实现或原实施方案，**不冻结 Evennia 的目标配置或永久处理粒度**；其中单一事实来源、原子性、信息隔离、防丢防重与已提交事实保护仍有效。

本节取代旧文将“SM 唯一权威”解释为“当前 SM 实现/仓库必须不可替换”、将 SQLite 配置视为新底座已冻结、或将现有逐事件观察协议视为永久目标的约束。RE 仍无权威跨请求状态，显式 RNG、`accepted ≠ committed` 与已有规则完成状态不变；普通世界操作不必经过 RE，涉及 D&D 机械裁决才求值。不因采用 Evennia 重写攻击/伤害/豁免/支付/效果或采用示例战斗代替 D&D。

具体复用、官方依据、EB-1～EB-3 证据和退出门槛见 [Evennia Adoption Plan](./EVENNIA_ADOPTION_PLAN.md)。方向 [DECIDED]，正式迁移范围、存储/接口 [PROPOSED / OPEN]，目标集成 [NOT IMPLEMENTED]，EB 运行验收未执行；本轮不升级依赖、不冻结新 ABI。

## 1. 实际代码基线与迁移缺口

| 位置（v0.1 历史 main 基线） | 历史事实（非当前实现声明） | 对契约的影响 |
|---|---|---|
| `dnd5e_engine/orchestrator.py` | `_LiveCombat` 持有 Initiative、Combatants、RNG、Round、Effects、Areas、Object State 及很多 sidecar | 需要完整状态依赖盘点，不能只迁移 HP/Turn |
| `orchestrator.py` | 公开 `start_combat`、`submit_player_intent`、`advance_monster_turn`、`end_combat` | 该历史基线未提供目标 `evaluate(...)` 契约 |
| `orchestrator.py` | `PlayerIntent` 是严格类型化的动作输入；该基线 `submit_player_intent` 主要是玩家入口 | 可复用适合目标契约的 Intent 语义 / Resolver，而非重写规则公式 |
| `orchestrator.py` | `_execution_transaction` 深拷贝 `_LiveCombat`、缓存事件并回滚 `random.Random` 状态 | 规则算法与回滚用例可作迁移资产；旧执行器不作为最终依赖，**不可**将其误认为 SQLite 跨模块原子提交 |
| `orchestrator.py` | 怪物回合由 `advance_monster_turn` 内部选策略后执行 | 该历史入口不足以证明敌方 Agent 宏观自主性；即时 Typed Intent 可由受控 Combat Policy 产生（§0.1） |
| `orchestrator.py` | Reaction 以预设触发为主，而非在解析中暂停等待人工选择 | 可暂停的 `needs_choice` 需作为新协议，不可冒称已有 |
| `nat20_bridge/state.py` / `combat_execution.py` | CombatHandle、事件及重试 Receipt 存于 Bridge 进程内；请求指纹与 `request_id` 已有基础机制 | 可复用概念，不可用 Bridge 进程内缓存作为新 State Machine 的权威持久回执 |
| `outcome.py` / `results.py` | `CombatOutcome` 是战斗关闭时的结果投影，并非每一步的完整 Delta | 新契约不得用 `CombatOutcome` 替代逐命令 StateDelta |

以上表格沿用 v0.1 的历史代码审阅基线；本轮的有限静态代码核对另列 §1.1，不是完整规则审计或运行测试。迁移应按受支持规则建立状态依赖闭包与读写映射；旧 `_LiveCombat` / sidecar 盘点用于发现遗漏、区分权威/派生/临时数据，不能成为目标 Schema 蓝本、永久执行依赖或要求所有规则重构先复制完整旧对象的门槛。

### 1.1 2026-10-12 跨仓库核对（静态代码 / Review，未重跑运行测试）

以下为前一批静态核对的日期化记录，本次 Evennia docs-only Batch 保留原 SHA / 分支 / 能力范围，未刷新仓库现状或运行测试。后续 EB 实施前重新只读记录实际锁定版本，不把历史 main 与开发分支状态混同。

| 基线 | 已核对事实与限制 |
|---|---|
| SM 开发集成分支 `feat/sm-b19-b22-gameplay-domain-bridge@058e79f` | Batch B 的 `event-evidence/4` 对已支持世界 Producer 阶段取证；Batch C（`9e7c130`）实现每 NPC 感知引用队列/独立放行；PERF-01/02（`6eb5855`）实现按需水位和 Pending 分页。核对 `events.py`、`perception_queue.py`、迁移及相应 Review；本轮不重设计这些实现 |
| SM 远端 `main@b3f350f` | 尚未包含上述开发分支提交；“已完成 Batch C / PERF”指开发集成基线，不等于已合入 SM main 或已部署 |
| RE 阶段 Evidence | SM 的 `dnd_runtime.py` 对非空感知 Signals 仍记录 `engine.intermediate_phase_unavailable`；RE 返回最终 Delta / 有序 ProposedEvents，未提供已审计的逐阶段感知证据协议。不从结束态补历史，不把 `intent_submitted` 自动当真实外显动作 |
| 机械审计 / Episode / Continuation | SM 仍包装 ProposedEvents 为 `combat.engine_event`；目标审计/可观察事实分流、WorldEpisode / EpisodeObservation 聚合与通用可持久恢复 Continuation 均 [NOT IMPLEMENTED]。受限预声明 Reaction 不代表通用中途选择已完成 |

SM 的 `pyproject.toml` / `uv.lock` 将 Engine 与 SRD 同时锁定为 **`602dcb8d448e670049427bbb751d6ed226005298`**。RE 远端 `main@38fcfcd4c3a744b30f792775415e798b323d4331` 比该锁定提交多 32 个提交，且本地候选协议不兼容：

| 代码版本 | SM 锁定 RE | RE main |
|---|---|---|
| Request / Result | 接受 `engine-evaluation/1`～`/4` | `engine-evaluation/22` |
| Snapshot | `engine-snapshot/1` / `/2` | `engine-snapshot/16` |
| Evaluator | `dnd5e-evaluation/8` | `dnd5e-evaluation/35` |

依据版本常量及模型，而非锁定提交中较旧的说明文字。RE main 已有更多受限 Stateless 路径及预声明 Reaction，但仍有 Legacy 依赖、完整 `CombatState.event_log` 字段与开放的 C-04 / C-15 / C-16；不等于已满足本次全部目标。升级前须独立审核 Snapshot / Delta / RNG / RulesetBinding 与 SM Consumer，不因本轮文档更新自动升级依赖或冻结共同 ABI。审阅来源：[SM Batch C](https://github.com/agentic-trpg/trpg-state-machine/blob/058e79f300016f7397f0c3401bc03b58554e2b71/docs/reviews/SM_PER3_REVIEW.md)、[SM PERF-01/02](https://github.com/agentic-trpg/trpg-state-machine/blob/058e79f300016f7397f0c3401bc03b58554e2b71/docs/reviews/SM_PERF01_PERF02_REVIEW.md)、[RE 本地协议](https://github.com/agentic-trpg/trpg-rules-engine/blob/38fcfcd4c3a744b30f792775415e798b323d4331/docs/dev/stateless-evaluation.md)。

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

此限制针对普通命令绕过可信领域边界，不禁止 §3.6 所述经过验证和受控启用的 Session 扩展。

### 3.4 Conditional World Effect Proposal `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

Planner 可在 TypedCommand 中提出受限的候选成功条件及对应世界变化，尽量复用 Adventure Package 的声明式 Condition / Effect 语义，不建第二套 Event Engine。SM 根据可信规则结果和权威世界状态判定条件、执行允许类型化效果；LLM 自报成功不能满足条件。提议的封装字段、结果引用和条件/效果子类型 **[OPEN]**。

需要机械计算时复用 §4–§6 的 RuleEvaluationRequest / Result；尽可能在掷骰前确认操作及后果均有受支持的表达路径，不先掷骰再用自由文本补写状态。一个命令提交前能够完整求值时，SM 同事务提交世界效果、机械 Delta、RNG、正式事件、CommandReceipt 和 Outbox；已提交事件才引发的后续效果沿用 §10 的可靠幂等独立命令，不虚构跨已提交事务原子性。

Planner 可随 Action Intent 提出按可能执行结果分类的候选 observable_signals，预定义事件/标准规则行为优先复用模板。SM 根据可信结构化执行结果选择匹配 Signals，并与实际事件原子提交，不接受 LLM 自报成功；Schema / 条件字段仍 [PROPOSED / OPEN]，具体边界见 §7.1，不增加 Event Generation Agent。

### 3.5 授权视图、反馈与叙事 `[DECIDED]`

复用 get_scene_view 等既有查询入口，按可信主体投影 DMView / PlayerView / NPCView：Planner 获取主持范围内完整授权 GM 信息；Player / Narrator 只读玩家可知事实；NPC 通过独立 NPCView / Perception 获取自身授权信息；get_scene_view 面向 NPC 时也必须经过 NPC Perception / 授权投影，不能绕过感知权限（DOC-02）。动态创建且已提交的对象进入后续授权查询，未提交对象或隐藏信息不能泄漏；不新增冗余查询服务。

反馈映射沿用 §5 / §6 / §11：rejected 是规则/世界拒绝，unsupported 是不支持的能力/操作原因，合法机械失败可为 accepted 并提交实际成本；version_conflict 对应 CommandReceipt.conflict，needs_choice 对应 pending_choice。RuleEvaluationResult 四态不变，CommandReceipt 不增加 unsupported 状态，能力不支持可用 rejected + 授权结构化原因表达。Schema/运行时/传输错误与规则拒绝分开，提交未知先查询 (session_id, command_id)。结构化原因经权限过滤供 Planner 使用，拒绝不会强制再调 LLM；重试/重规划按 §2.2。

Narrator 保持游戏世界内的沉浸叙事，不把内部 API、Schema 或 unsupported 错误直接作为玩家叙事。但能力限制不能成为“墙壁永久不可摧毁”“骰点已失败”或“世界已改变”的无依据世界事实；Planner 可以提出合理情境解释，权威效果仍须正式提交。必要的能力/运行时提示由文字入口以可理解方式表达，不伪造机械结果。Narrator 没有写权限。

### 3.6 Coding Agent 与受控 Session 扩展 `[DECIDED; OPEN; NOT IMPLEMENTED]`

运行时创建内容、组合已有机制、安装 NPC 行为是目标能力；区分配置/模板更新、已有能力组合和真正新增底层机制。前两类也须校验权限与定义，第三类生成代码还须经过验证、权限限制和受控启用。任意 Python / JavaScript 回调、人工审批或 reload 本身均不构成安全热部署；目标是准备完成后在安全边界启用，不是任意代码即时生效。完整 Coding Agent 扩展系统不是 EB-1 前置条件，也不是本批实现范围。

固定 Adventure Package 仍是 Session 初始基线。运行中新增对象、机制或行为须作为获准的 Session 扩展或运行态变化，不悄悄回写固定包或改变历史执行依赖的定义。扩展来源/版本/启用记录、在途操作版本绑定、行为状态迁移、失败隔离与恢复协议均 [OPEN]；回滚扩展版本不自动撤销已提交游戏事实。不得借扩展让 Host 成为权威状态所有者。

## 4. State Machine → Rule Engine：RuleEvaluationRequest（P0）

本章的结构决策为 `[DECIDED]`；API、具体类型定义及示例消息版本仍为 **`[PROPOSED; NOT IMPLEMENTED]`**。以下 YAML 展示字段关系，尖括号为类型/数据占位，不是可执行 Fixture；`module-contracts/0.2` 是本轮候选消息版本，与文档版本分开。

**最终执行架构 `[DECIDED]`：**

```text
StateSnapshot + Typed Intent + Pinned RulesetBinding + Explicit RNGContext
    -> Stateless Rule Evaluation Engine
    -> RuleEvaluationResult（未提交）
```

Rule Engine 负责动作机械合法性、Attack、Damage、Check、Save、Action Economy、Movement、Spell、Effect、Reaction 等受支持规则的确定性计算，返回四态结果及适用的封闭 Typed StateDelta、ProposedEvents、RNGTransition、ReadSet。State Machine 只提供经验证的这些类型化输入并提交结果，不重新计算 D&D 规则，不创建、管理或恢复 Engine 内部对象。

**求值粒度 `[DECIDED]`：** 一次请求尽量完成该 Intent 下所有可连续结算的规则效果，包括已授权自动触发、预声明 Reaction 与连带资源/状态变化；不能按每条审计事件拆请求并等待 Planner / JEV / EVA。真正需要中途选择时按 §8 Interrupt / Continuation 目标暂停。Episode 可跨多个请求，不要求把整场战斗塞进一次求值。

**当前状态与归纳历史 `[DECIDED; NOT IMPLEMENTED]`：** SM 持有完整权威 Combat State；RE 正常求值依赖当前机械状态和必要的类型化历史摘要/账本，例如每轮/每回合使用记录、Reaction 窗口、已支付资源、效果来源与生命周期。摘要必须由可信规则路径维护、随 Delta 原子更新，不是 LLM 总结。不得每次为推导这些依赖而重新加载/扫描完整 Combat Event Log。机械审计历史仍保留，结合初始状态/检查点、规则及策略版本、已采纳命令/选择和 RNG 转换支持审计与确定性重放；重放是独立能力，不是每次求值的必经步骤。当前本地 Snapshot 的 event_log 迁出须先审计真实规则依赖，不能直接删字段或丢失历史。

**最终受支持规则的执行路径不得依赖 Legacy `_LiveCombat`、`CombatHandle`、`_REGISTRY` 或 Stateful Combat Orchestrator**，包括在每次求值中重建旧对象、调用旧执行器后导出 Delta 的永久适配方案。允许单次求值的局部变量、临时计算对象、派生索引或必要上下文；这些对象只服务于计算，不能使旧 `_LiveCombat` 完整内部结构成为长期前提。可以复用 Nat20 的 D&D 算法、Resolver 和声明式规则数据，重构其状态访问与执行依赖，无须重写已经正确的规则公式。

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

该 combat.intent 示例分支的顶层字段均 Required。共同字段的 Required 约束不变；actor_id 是否必填按 operation_kind 的具体强类型分支决定（AP-15，§3.1），Actor 行动必须保留真实 actor_id。受信系统/世界事件分支可无行动 Actor，但 SM 必须核验 principal、机械来源、目标和范围，并以可信内部调用上下文/受控来源关联交 Engine 校验；source_ref 与来源权限编码仍 [PROPOSED / OPEN]，不在本轮冻结新字段。SM 保留 `(session_id, command_id)`，提供 Session 固定规则配置、权威 Snapshot 和独立 RNGContext。Engine 不接受 Agent 自报快照/身份，不依赖任何 Legacy `_LiveCombat` 对象、CombatHandle、注册表或 Stateful Orchestrator，也不读取进程全局随机状态。标准 Required / Optional、类型与联合判别校验失败属于 Schema / 输入错误，不伪装为规则拒绝。

`operation_kind` 选择操作级 Payload Schema（如 CombatIntentPayload、AbilityCheckPayload、SavePayload、RestPayload）；`payload` 必须是对应强类型数据。CombatIntentPayload 内的 `intent_type` 区分 attack / cast / move 等动作子类；两层判别职责不同，不能合并，也不接受任意字典或自然语言代替 Payload。具体操作枚举与字段覆盖按已支持规则审阅，不因示例推定全部已实现。

### 4.2 StateSnapshot：CombatSnapshot / NonCombatSnapshot `[DECIDED; NOT IMPLEMENTED]`

StateSnapshot 是 **CombatSnapshot / NonCombatSnapshot 两种情境**的判别联合，均只读、版本化，共享必要的 CharacterState、InventoryState、EquipmentState、EffectState、SceneMechanicalState 等类型化机械状态组件。Inventory / Equipment / Effect 是组合组件，不按每一种规则操作新增 Snapshot 情境；组件的具体字段与组合编码仍 [PROPOSED / OPEN]。RNGContext 是独立输入，不嵌入 Snapshot。

| Schema | Required | Optional（仅按对应 Schema） |
|---|---|---|
| CombatSnapshot（snapshot_kind=combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state、combat_state | component_versions / 显式 read_set 等版本辅助信息 |
| NonCombatSnapshot（snapshot_kind=non_combat） | snapshot_kind、snapshot_schema_version、world_version、character_states、effect_states、scene_state | component_versions / 显式 read_set 等版本辅助信息；不含 combat_state |

`character_states` / `effect_states` 的集合元素使用相同基础 Schema，库存等组件按基础类型引用/组合。无相关效果时合法空集合仍须明确提供；可选字段的省略/null 规则由普通 Schema 定义，不引入额外缺失状态分类、缺失原因枚举或按 Intent 动态裁剪字段的机制。

SM 可以按相关实体与 Scene 限定集合范围，但每个纳入实体的机械状态必须完整，并保留规则依赖闭包，包括会影响它的其他实体、来源、区域与生命周期账本。不能因本次只攻击而省去该角色的反应、装备或持续效果字段；不能把非战斗检定伪造成 Combat。缺 Required 字段报 Schema 错误，完整输入所需的规则路径尚未支持则显式 unsupported，不以隐藏 Engine 状态补齐。

§7 的 Event Evidence 只保存感知所需历史字段；其 Signal-scoped 裁剪原则不能用于裁剪本节机械 Snapshot 的 Required 字段或规则依赖闭包。二者用途和完整性标准不同，Event Evidence 不能直接替代 CombatSnapshot / NonCombatSnapshot。

| 基础领域 | 完整机械状态必须覆盖的语义（具体字段映射仍待实施核对） |
|---|---|
| CharacterState / InventoryState / EquipmentState | HP / Temp HP / Death Saves、能力与规则特性、资源池/法术位、库存/数量、装备、动作来源及有限使用次数 |
| CombatState | Combatant roster、Initiative、Round / Turn / Phase、Action Economy、Reaction、移动预算、位置/Reach/Topology 及跨步骤账本 |
| EffectState | Conditions、Concentration、Active Effects、来源与目标、持续时间、持续区域、过期/撤销条件，战斗内外复用 |
| SceneMechanicalState | 必需场景、对象、障碍、光照/遮蔽、环境规则与关系及版本；不传入无关剧情秘密 |
| Pending state（适用时） | 已支持的选择/活动引用与版本；复杂中途 Reaction Continuation 仍 [OPEN]（§8） |

该表不是现成代码类型。每条受支持规则须证明 Snapshot 覆盖其完整状态依赖闭包，包括跨实体、效果来源、Reaction、持续区域和生命周期账本；不能仅迁移 HP / Turn。历史 sidecar 审阅只是遗漏检查的证据，不要求目标 Snapshot 或临时计算上下文复制旧 `_LiveCombat` 的结构。

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

**[DECIDED] 实施顺序**：该查询不依赖 Visual Presentation，可与早期 Stateless Rule Evaluation 实现同步开发，先覆盖基础战斗操作的只读合法性判断并与正式求值共享同一规则逻辑，避免第二套规则系统。当前文字 MVP 不强制调用此接口；视觉 UI 仍为 Post-MVP。此处只更新计划，不代表已实现。

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
- 本表 needs_choice 仅描述 §8.1 的前置选择候选分支；不提交部分伤害、资源或 RNG。§8.3 的中途 Interrupt 尚未映射为正式 Result ABI，不能直接套用此前置选择形状或私增正式 status。
- unsupported 明确能力不支持，禁止静默成功或部分执行。
- 所有机械变化都必须显式包含在可提交结果中，不存在需要另取 Engine 私有状态的隐含副作用；失败或尚未提交的求值不会改变权威状态。
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

Engine 返回有序、类型化的候选机械事件，不分配权威 event_id / event_seq。SM 保留机械审计结果，并依据受审的真实发生阶段/Signals 语义形成可观察世界事实，不能将每条 Mechanical Audit 自动升级为 NPC 感知事件。SM 在提交 StateDelta、RNG、CommandReceipt、Outbox 的**同一事务**内分配正式事件身份/序号并保存相应记录；只有 COMMIT 成功后才成为 CommittedWorldEvent，对外发布见 §7。具体审计/可观察事件分类及阶段交接 ABI [OPEN; NOT IMPLEMENTED]，SM 不据事件重算规则。

正式事件保留 `(session_id, source_command_id)` 与命令来源；这里的 source_command_id 是事件关联字段，不是额外的规则操作标识。SM 直接应用并校验 Typed Delta，不根据 ProposedEvents 再计算 HP、伤害或资源扣减。NPC Perception、DM Narration、UI 只能获取经授权的事件/回执投影，不直接获取候选事件或全量隐藏机械细节。

## 6. State Machine Atomic Commit 与 CommandReceipt（P0）

### 6.1 执行时序 `[DECIDED; NOT IMPLEMENTED]`

```text
Typed Command -> authenticate / authorize / (session_id, command_id) lookup
-> ordinary world operation: trusted deterministic domain handling
   OR D&D adjudication: Snapshot + pinned RulesetBinding + RNGContext
      -> Rule Engine.evaluate(RuleEvaluationRequest)    [outside DB write transaction]
      -> accepted result
-> begin short authoritative commit transaction        [Evennia mapping OPEN]
   -> re-check fingerprint / existing CommandReceipt / authoritative versions
   -> re-check read set, permissions, ruleset pin, typed Delta invariants
   -> retain mechanical audit; determine observable events / Signals from trusted stages
   -> per-Signal Scope Discovery -> event-local Evidence Capture / binding [§7; stage protocol OPEN]
   -> apply all StateDelta + authoritative RNG successor
   -> allocate event IDs / sequence and persist events + Signals + Evidence
   -> persist CommandReceipt + idempotency + Outbox
-> COMMIT -> return CommandReceipt / publish only permitted committed projections
```

非 accepted 不进入上述机械提交；可持久记录结构化拒绝、冲突或前置选择元数据，但不写部分机械 Delta / RNG / 候选事件。Schema / 异常 / 传输错误分别处理，不伪造规则结果。

上述事件步骤表示逻辑依赖，不要求等全部 Delta 应用完才采集证据；可信阶段取证及最终裁剪/绑定遵守 §7，不能用命令结束态冒充各事件阶段。具体阶段采集协议仍 [OPEN]，不由 SM 根据事件重算机械规则。

**OCC / 幂等**：可信运行层承接 SM 的权威版本、Fingerprint、权限、Delta 不变量与短事务职责。过期 Snapshot 返回 version_conflict，或在授权/有界条件下重新取完整 Snapshot + RNG 重算，不能把旧 Delta 套在新状态上。持久唯一键 `(session_id, command_id)` 防双提交；相同已提交请求只查原回执，不重新求值。并发/重算的内部尝试不增加公共操作标识。SQLite 是旧 SM 的实现基线；Evennia 目标提交映射须经 EB-2 验证，包含数据库回滚后的对象、Attributes 和派生缓存一致性。

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

采用现有 Event 协议时，`StateDelta + RNG + CommittedWorldEvent（含 Signals）+ Event Evidence / 稳定历史引用 + CommandReceipt + Outbox` 同属一个原子提交域，全部成功或全部失败；旧 SM 使用 SQLite 事务。目标运行层须保留等价正确性，具体数据库配置与提交映射 [OPEN]，不要求每条机械审计都生成 WorldEvent。LLM/Rule Engine 求值及对 UI/NPC 的发送均在写事务外；提交后投递失败须可靠、幂等补偿，不回滚已提交世界事实。Schema 错误、求值异常、传输故障、Commit failed/unknown 与 committed response failed 必须分别报告，不能一律要求重新掷骰。

模块边界不意味着分布式 ACID：Engine 没有要与可信运行层协调提交的第二份权威状态，也不建立 Evennia / 旧 SM 的双写同步。EB-2 必须验证 SQL 回滚后内存对象/缓存不会继续暴露或提交失败结果，不能只靠重启恢复；提交后回调也不自动等于可靠 Outbox。性能验证应分别测量 Snapshot 构建、规则求值、提交的 p50 / p95 延迟与内存；派生缓存可丢弃，正确性不依赖缓存跨请求存活。

## 7. WorldEvent → Perception → NPC Evidence（P0/P1）

§7.1–§7.4 描述当前 Event-level 协议及迁移资产；当保留这种事件记录时，其证据、原子性和信息隔离要求继续适用。它们不要求每次机械行动产生 WorldEvent / 独立 OB，也不冻结 Evennia 的永久观察粒度；完整事态目标见 §7.5。

### 7.1 CommittedWorldEvent 与 Observable Signals `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

本节整合 PER-01～PER-08，逻辑顺序为：Event + Signals 确定 → 逐 Signal Scope Discovery → Event-local / Signal-scoped Evidence Capture → 原子提交 Event + Signals + Evidence + 可靠 Outbox → 后续 Deterministic / JEV Perception Judgment → Authorized ObservationRecord（OB）→ 既有 NPC Inbox。提交前 Event 仍为待提交事实；这不是多个独立事务，不新增模块、感知状态机或独立认知流程。

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

#### Event-local / Signal-scoped Evidence `[DECIDED]`

以下是统一目标原则；§1.1 已核对开发分支的受限世界 Producer 实现，RE 阶段协议仍 [OPEN; NOT IMPLEMENTED]，不能将两者混为全部已完成或全部未实现。

**Event-local Evidence：** 每个 CommittedWorldEvent 的证据必须对应其 Signals 所描述的**实际发生阶段**，而不是无条件复用整个 Command 完成后的状态。一个 Command 可以产生多个 Event；不同 Event 可以共享未变化的可信证据，但若相关位置、Scene、光照、遮挡、感官或 Conditions 等在阶段间变化，必须保留各自对应的证据及关联。`event_seq` 只是记录顺序，不是完整中间状态快照；相同 world_version / game time 也不证明两个 Event 的相关证据相同。例如同一命令先在 Scene A 发声、再进入 Scene B，不能用 B 的结束态为 A 的发声事件作判断。

**Signal-scoped Evidence：** 保存该 Event 的 Signals 进行感知判断所必需的可信历史数据，按 §7.2 的候选集合裁剪；不复制整个 Session 的感知状态。最小必要性以判断所需的字段完整性为前提，不能把“未保存”解释为“没有该状态”。同一 Event 的多个 Signals 可共享来源、Observer 或环境证据，避免重复存储，但必须保留逐 Signal 的适用范围/关联。

| 证据内容（概念，非冻结 Schema） | 范围与完整性要求 |
|---|---|
| Signal Origin | 该 Signal 实际发生阶段的可信来源 Scene、实体/位置及判断所需属性；不是模型自报或从当前位置反推，具体编码 [OPEN] |
| 相关环境 | 各 Signal Scope / 判断所需的 Scene、空间关系、光照、遮挡等历史数据的并集；不包含无关 Scene / 对象状态 |
| 候选 Observer | 逐 Signal Scope 内全部候选 NPC 的事件时位置、感官、Conditions 及其他必需状态；包含 Inactive 和可能无法察觉的 NPC |
| 来源与恢复关联 | 核验阶段、版本、证据适用范围及可靠恢复所需的最小关联；可共享不可变证据或稳定历史引用，不能只存 event_seq 后查当前世界 |

必要证据必须来自可信 SM 状态、经验证的规则结果或可核验的不可变历史引用，且字段满足受支持判断的完整性。缺失必要位置、感官、Conditions 或环境等证据，不能使用当前 World State 补造，不能默认 Positive 或 Negative，也不能交 JEV 猜测缺失事实；沿用既有未完成工作语义，不冒充已完成投影。Event Evidence 是**感知专用最小证据**；Rule Engine 的 CombatSnapshot / NonCombatSnapshot 必须满足 §4.2 的完整机械规则依赖，两套裁剪原则不能混用。

**原子性 `[DECIDED]`：** Event、Signals、Evidence（或受保护的稳定历史引用）与可靠 Outbox 必须与对应世界变化在同一个 SQLite 原子事务中提交。Capture 可依附可信事件阶段，先保留必要取证依据，待 Event / Signals 确定后完成 Scope 裁剪和证据绑定；逻辑顺序不要求独立事务，也不允许中间可见的部分提交。事务外准备的依据须经提交版本/读集校验，不能在写事务中等待模型或长时间规则求值。异步 Judgment 只能消费已提交证据。

**采集协议 `[OPEN]`：** 必须结合真实 SM 世界操作与 Rule Engine 有序事件语义，验证每个 Event / Signal 对应阶段、可取得的可信状态及共享条件。仅有最终 Delta / 事件序号不能假定可以恢复中间阶段；无法恢复时须显式列为未解决的支持缺口，不得虚构准确的事件时状态。阶段采集、引用编码/保留与大型范围分批策略尚未冻结；本轮不扩展 NPC State Timeline、Signal Channel、全局 Cursor 或 Unresolved 恢复设计。

**历史实现与目标差距（Batch A 历史核对；更新基线见 §1.1）：**

| 层次 | 事实 / 状态 |
|---|---|
| 已实现的指定历史基线 | `trpg-state-machine@5deea78` 的 `events.py::_event_perception_evidence` 使用 `event-evidence/3`，读取 Session 全部已实例化 Actor / Scene（及对象位置）。`service.py::_append_events` 在事件循环前捕获一次，逐 Event 写入同一份内容；世界命令路径在操作/级联之后调用它。该行为不是逐 Signal 裁剪或逐阶段取证 |
| Batch A 当时目标 `[DECIDED]` | 每 Event 对齐实际阶段，逐 Signal Scope Discovery 后取候选/环境并集，保存最小且完整的感知证据并原子提交；在该历史基线未实现，当前开发分支的受限实现另见 §1.1 |
| 待验证 `[OPEN]` | 真实 SM / RE 路径的阶段语义和可恢复性、可信字段来源/依赖与共享条件、候选完整性及分批恢复；本轮已核对范围见 §1.1，不代表部署或全部规则覆盖 |

### 7.2 Discovery、判断与 Observation `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

**Scope Discovery `[DECIDED]`：** 对每个 Signal 独立按其类型化 Scope、可信 Origin 和对应阶段的空间/成员关系作确定性候选筛选；再对同一 Event 的候选 NPC 和所需环境证据取并集，保留 NPC 与各 Signal Scope 的对应关系。Discovery 只回答“谁在候选范围内”，**不判断视觉、听觉、遮挡、感官能力或实际察觉**；Scope 内即使失明、耳聋或可能被遮挡的 NPC 也不得提前排除，不能只发现在线 NPC。后续 Perception Judgment 才用完整事件时证据确定性检查感官、位置、明确遮挡及已支持机械约束；并集不意味着每个候选都适用 Event 的每个 Signal。

**边界与分批原则 `[DECIDED]`：**

| 情况 | 处理原则 |
|---|---|
| 零 Signal Event | 合法空 Signals 不触发察觉判断或 OB；不复制 Observer / 环境感知状态，保留必要事件/可靠工作及空结果语义。缺失/非法 Signals 不能当作合法空集合 |
| 多 Signal / 不同 Scene | 分别按各 Signal 自身 Scope / Origin 发现，不用 Event 的单一 scene_id 限制全部候选；证据取并集并共享未变部分，逐 Signal 判断后沿用同 NPC / Event 的 OB 聚合 |
| 无候选 NPC | 可信完整 Discovery 的空集合可可靠完成，无需 JEV / OB，也无需 Observer 状态；缺失范围依据不等于没有候选 |
| 大型 Scope | 若已支持范围本身很大，必要证据集合也可很大；允许可恢复分批发现/取用/判断，沿用既有 Work / Outbox / 去重。不要求一次物理枚举全部 NPC，但原子提交时必须固定完整候选集合或可恢复枚举它的稳定历史依据，以及可恢复的事件时必要证据/引用；不能事后扫描当前 Actor / Scene 补历史，也不能因分页/预算截断漏候选 |

上述逻辑顺序允许大型集合按已提交的可信历史依据分批展开，不允许把 Evidence Capture 延迟成读取当前世界；候选完整性和证据恢复未保证前不能标完成或越过投影水位。具体分页/保留/共享编码 [OPEN]，仅使用已有支持的 Scope 能力，本轮不要求实现新 Scope 类型。

**JEV Perception Judgment：** 只有确定性条件无法判断的情境才交 JEV，明确可判定的 Signal 不必提交。SM 授权、Host 运行，提供最小必要的事件时可信 Observer 状态、相关环境及待判断 Signals；此 JEV Perception 职责只逐项判断是否察觉，不生成 Signal、Observation 文本、Belief / Goal / Plan 或世界变化，与独立的 Memory Gate Judgment（§9.8）/ NPC EVA 分开。具体模型/传输仍为候选；调用在写事务外。

该可选 JEV 属于后续 Agent Cognitive Response 的感知输入准备，不能成为即时战术/Reaction/自动效果的机械前置依赖。Immediate Mechanical Response 所需察觉只能走可信确定性/RE 路径，未知不得默认已察觉（§0.1）；后续主观认知不能反向补准已经执行的机械响应。

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

按 §7.1–§7.2 在 Commit 同事务内记录 Event、Signals、Event-local / Signal-scoped Evidence / 稳定历史引用及可靠 Outbox / 待处理 Projection 工作；分批 Discovery 仅展开已固定的历史候选依据，投递至少一次。默认聚合按 `(observer_id, event_id, projection_version)`（或等价唯一键）幂等写 Observation；持续事件分时新观察的时刻区分/等价键编码 [OPEN]，不强制合并。NPC 不在线时仍保存应收到的 Event Observation 或可靠重放证据。**原始事实、感知记录、角色信念三者分别持久存储**；`Belief` 不等于 World Fact。

- 分批 Discovery / 判断未完成时不能越过投影水位；全部未察觉也须可靠记录处理完成，不用空 Observation 冒充感知。具体分页、历史保留和索引字段 [OPEN]，沿用既有工作机制。
- `observation_id` 稳定，按 NPC 提供顺序可核验的 Delivery Cursor；相同事件多个 Observation 的次序需有稳定 tie-break。分页返回该 NPC 的投影完成水位/等价完整性证明，不能跨越该 NPC 较早的候选未完成项或适用的既有异常屏障。其他 NPC 的候选未完成项不构成全局阻塞；Session 汇总水位仅供兼容/审计，不覆盖每 NPC 的完整性证明（已实现的 Batch C / PERF 边界见 §1.1）。
- 读取 Cursor / Host 已追加 Context 位置与 SM 内部 Processing / Completed Cursor 分离。读取、追加或模型返回不等于处理完成；SM 仅按必要认知处理与可靠输出交接的持久完成状态推进连续前缀，见 §9.6，不要求 Host 额外 ACK。
- SM 为待处理 Observation 批次建立稳定 `observation_work_id`、任务及幂等处理记录；重复投递不创建第二份逻辑工作。合并批次不能重复占用尚有任务的同一观察；具体索引/表结构未冻结。
- Mode Routing、Gate 领域策略、证据保留和任务完成由 SM 管理；Host 按授权请求执行 Context 追加或模型调用。失败不随 Context 释放而丢失证据。

### 7.4 Recent Observation、Processing 与 Retention `[DECIDED; NOT IMPLEMENTED]`

**Observation（OB）直接承担短期感知记忆职责**，不再另设 Short-term Memory 概念或与 Inbox 重复的短期存储。OB 保存 NPC 已实际察觉且获授权的 Signals，是真实感知证据；Long-term Episodic Memory 由 NPC EVA LLM 提议、SM 验证持久化，Belief / Relationship / Goal / Plan 仍为 NPC Meta。OB 不自动转化为长期 Memory，合法 EVA 也可以不产生任何 Meta。

每条 OB 有两个独立生命周期；下表是**概念状态，不要求照搬为数据库枚举**。ObservationProcessingStatus 继续表示必要认知工作，不兼任 Retention 状态：

| 生命周期 | 概念状态 | 权威语义 |
|---|---|---|
| Processing | Pending | 尚有认知工作；创建 Task、启动 Invocation、读取/追加 Context、模型返回未提交结果均不完成 |
| Processing | Completed | 合法 EVA Result 及必要可靠交接已提交，或 SM 已持久采用获准 Safe Retention / No-op；不重新排入同一认知工作 |
| Retention | Recent | 仍在游戏时间有效期内，可作为短期信息；既包括 Pending，也包括 Completed OB |
| Retention | Expired | 不再作为 Recent Observation 提供给新的 NPC Context 输入；Pending 工作仍须保护 |
| Retention | Archived | 为长期 Meta 来源追溯保留必要原始证据与来源关联，不因此向 NPC 提供近期信息 |
| Retention | Discardable | 到期、认知工作完成且所有保护条件解除后，允许安全清理；不是到期立即删除 |

Retention 描述有效性与保留用途：Expired OB 可以同时需要归档或待处理证据保护，不要求编码成互斥线性状态机。**Completed + Recent 仍可用于后续决策，但不是待处理队列项；Pending + Expired 仍有工作，但不是新的近期信息。** 已完成 OB 可作新任务的近期背景，不能借此重做同一 Work、重复 Meta 或行动交接。

**Game Time `[DECIDED]`：** SM 管理的权威游戏时间决定 OB 有效期；`expires_at_game_tick` 只是候选字段 `[PROPOSED]`。真实墙钟可供 Host 超时/性能计量，不能作为 OB 游戏生命周期的权威来源。TTL 数值、起算点、时间编码及是否按事件类型区分 TTL 均 `[OPEN]`，不从自然语言或模型输出推定。正常认知调度在到期前进行，不能把 TTL 当作唯一 EVA 触发器（§9.9）。

**SourceReference 与清理 `[DECIDED; PROPOSED]`：** 沿用既有 Observation / Memory 来源引用，以合法 SourceReference 关联 observation_id，不建立第二套来源系统；`source_observation_ids` 等现有示例可表达此关联，完整联合类型仍待评审。一条 OB 可被多个 Long-term Memory / Belief / Relationship / Goal / Plan 记录引用。SM 在 Meta 提交与清理的事务边界核验引用和保护条件，避免引用提交与清理竞争造成悬空来源。

到期时 SM 按既有 Inbox / Work / Cursor 协议处理：

1. 从 NPC 可用 Recent Observation 投影移除；Completed OB 不因到期重新触发 EVA。
2. Pending Work 保留必要原始证据、原始时序和任务关联，等待合法重试、移交或获准安全处理；TTL 本身不构成 No-op 批准。
3. 长期 Meta 仍引用的 OB 归档必要证据与关联；多记录及历史版本引用均受保护。内部保存不代表 NPC 仍记得事件，也不将归档原文自动送回 Context。
4. 无需保护的引用且认知工作全部完成时，才可进入安全清理；未完成任务/输出交接、历史版本、审计、Receipt、去重键及幂等关系不能被破坏。具体保留粒度、索引/引用计数、归档位置与清理算法 `[OPEN]`。

到期前已授权任务的未完成证据仍可按原 Work 的受限恢复输入处理，须明确其已过期及原始时序；这不是 Recent OB 回注或历史全量读取权限。新建/重建普通 Context 不提供已过期 OB，必要恢复证据的传输字段/权限校验 `[PROPOSED / OPEN]`。有效在途 EVA 的处理资格不由 TTL 自动撤销，提交仍重验 Task / NPCStateVersion 与来源权限；Action Execution 另按当前事实重验。

### 7.5 WorldEpisode、EpisodeObservation 与信息分层 `[DECIDED; NOT IMPLEMENTED]`

**WorldEpisode 是一段完整事态的逻辑组织单位；一场完整战斗对应一个 CombatEpisode。** 不默认按 Round / Action 建立 Episode，也不默认把每条机械事件包装成 WorldEvent 或生成独立 OB。Episode 不必与 TypedCommand 一对一，可跨命令、自动触发、Interrupt / Continuation 和多个原子提交。需要记录的外显阶段仍保留自己的发生时间、可信 Evidence、Signals 和已确认因果顺序；event_seq / 提交先后不自动证明物理先后或因果。Episode 关联不引入跨已提交事务 ACID，也不允许回滚已发生事实。

| 概念 | 职责与可见性 |
|---|---|
| Mechanical Audit | 规则求值、骰点、支付、内部触发/步骤的可信审计；支持排错/重放，不自动进入 NPC Perception |
| Observable WorldEvent | 已实际发生且提交的外显世界事实/结果；只有其合法 Signals 进入感知，不能广播隐藏 payload |
| WorldEpisode | 组织相关阶段及可信因果关系的 SM 领域概念；不是给 NPC 的全知故事摘要或新增执行 API |
| Signal | 某阶段实际产生的可感知内容、渠道与 Scope，仍按 §7.1–§7.2 判断 |
| Event Evidence | 各 Signal 判断必需的可信历史证据；不等于机械 Snapshot、审计全集或角色信念 |
| EpisodeObservation | NPC 对完整事态的**已察觉部分**的目标逻辑观察单位；聚合其合法阶段结果，不泄漏未察觉阶段、隐藏身份或客观因果边 |
| Long-term Memory | NPC EVA 对经历的主观长期认知提议，由 SM 验证持久化；不自动从 Episode / OB 复制，不必每个 Episode 都生成 |

EpisodeObservation 是 NPC 对整段经历的逻辑观察单位。已记录的阶段感知结果保持不可变、可追溯，不能因后续阶段加入而改写此前 Positive / Negative，或把 Unresolved 补成已察觉。运行时感知可支持即时行为，不等待 EVA 或战斗结束；战后可统一聚合 NPC 的整体观察。聚合允许只有声音、后续结果或局部经历，不能泄漏未察觉内容、隐藏身份或因果；NPC 对原因的猜测只能是主观 Belief。

**[PROPOSED; OPEN; NOT IMPLEMENTED]** 战时保存必要感知结果或证据、战后聚合是 EB-3 待验证方案，可与使用可信历史记录的重建比较，不是冻结算法；禁止从战斗结束态补造过去感知。Episode 身份/起止/因果、增量交付、去重、证据 Schema 及 Processing / Retention / TTL / SourceReference 映射仍须设计。现有 Event-level OB / Outbox 是当前实现和迁移资产，不是永久目标；此决定替代“每个机械 Event 必须有独立 OB”的目标解释，不授权删除已有观察或历史记录。映射批准前既有 Inbox / Work / Gate / EVA、Game Time TTL、Pending 保护、模式独占、任务标识与完成协议继续有效，本批不重新设计这些协议。

## 8. Pending Choice / Reaction / Continuation（P0 语义，MVP 限制实现）

**实现边界：** §1.1 的 RE main 有受限预声明 Reaction；锁定版本与它不同，两者均不能证明通用“解析中暂停并等待选择”的持久 Continuation 已完成。以下区分前置选择候选协议与中途 Interrupt 目标，不据文档宣称代码已支持。

### 8.1 MVP 首选 `[PROPOSED]`

优先采用**求值前选择**：Rule Engine 返回 `needs_choice`，但不消耗 RNG 或机械资源；State Machine 保存**独立的 PendingOperation 元数据**（不是对机械求值部分提交），Host 向有权限的角色请求选择，随后发起新的 `choice.respond` 命令附 `pending_operation_id` 与 `selected_option_id`。State Machine 验证主体、原命令、版本、有效选项及过期/取消状态，再基于新鲜 Snapshot 重新求值与完整提交。

`PendingOperation` 至少包含 `pending_operation_id`、`source_command_id`、`actor_id`、`authorized_responder`、`choice_kind`、`allowed_options`、`input_world_version`、`status`、`creation_time`、`expiration_policy`、`ruleset_binding` 和唯一幂等字段。`choice.respond` 不能任意覆盖原始 Intent。

### 8.2 必须明确不支持的场景 `[OPEN]`

某些 Reaction 在掷骰、命中或部分效果发生后才能决定是否响应。上述**求值前选择**方案无法普遍正确表达这类中途暂停机制。对这种规则路径：

- MVP 可以沿用已验证的**预先声明 Reaction 策略**，但不得声称与所有 SRD 交互式选择完全等价。
- 如果剧本的黄金路径必须支持中途 Reaction，需先设计可持久化的执行检查点、已消耗骰点与信息窗口，再决定最小实施范围。
- 最终 Continuation 使用 SM 持久保存的类型化、版本绑定状态，不引用 Legacy `_LiveCombat` / `CombatHandle` 或其他进程私有执行器句柄；也不在外部等待时占住 SQLite 写事务。
- `needs_choice` 不能偷偷提交已经结算的伤害，也不能凭 Narrator 文本作为 continuation 状态。

活跃战斗异常退出后的**精确续玩仍为 Post-MVP**。MVP 需保留明确的 `combat_interrupted`/停止受理/安全重新开始策略，不能悄悄恢复战前状态并覆盖已提交结果。

### 8.3 Interrupt / Continuation 目标 `[DECIDED; OPEN; NOT IMPLEMENTED]`

1. RE 尽量连续结算；在确需新的中途选择、继续将改变合法信息窗口时暂停，交回可信可序列化的待决操作/Continuation 语义，不等待 NPC LLM、JEV 或 EVA。NPC 机械选择由受控 Combat Policy / 已授权预声明策略处理，PC 选择交可信玩家入口。
2. SM 持久化待决操作、授权选择范围、规则/状态版本、执行进度与必要 RNG / 已支付资源证据；不保存进程私有 `_LiveCombat` / Handle。重试/恢复沿用持久身份与已采纳选择，已经确定的骰点不能重掷，资源不能重复支付，未完成步骤不能伪装完成。
3. 选择响应需重验主体、窗口、版本和有效选项，防迟到/重复响应；只恢复合法的原执行进度。发生冲突、取消、超时或规则版本不符时显式处理，不能把旧 Continuation 套到新状态或重新从头掷骰来“修复”。
4. 暂停的持久检查点/必要状态与 RNG 转换、对应审计/事件及可靠交接须在 SM 的短 SQLite 原子边界保存；等待选择和 RE 续算在写事务外。已经提交的可观察阶段不可撤销；尚未提交的部分结果不得提前发布。

**ABI `[OPEN]`：** Interrupt 如何映射 Result / Receipt、Continuation 字段与幂等身份、计算中已消耗 RNG 的保存/预留、哪些前缀机械效果可提交、信息窗口与其他命令的交错/版本政策、取消/到期和最小 MVP 支持范围，尚需真实路径审计。不能用 §8.1 的无消耗 needs_choice 假装完整中途暂停，也不预先新增正式接口/status。目标恢复语义不等于 MVP 承诺任意活跃战斗崩溃精确续玩；未支持路径须在执行前明确边界，不产生虚假的部分成功。

## 9. Agent Host / NPC Evaluation / Memory / DM（P1 接口边界）

本节架构语义按各段 `[DECIDED]` 标记；新增消息、字段和存储协议仍为 **`[PROPOSED; NOT IMPLEMENTED]`**，具体类型、状态编码、版本与数据库结构仍需审阅；不要求新增服务或复杂公共 Receipt 子系统。

### 9.1 EVA、NPC Meta 与 LLM Runtime `[DECIDED]`

**EVA（NPC Evaluation）是认知更新与决策评估，不是 Action Execution。** Memory、Belief、Relationship、Goal、Plan 构成一次原子 NPC Meta 更新单元。NPC 可以提出 Dialogue 与 Action Intent，但实际发布/执行有独立授权和处理路径。

本章只管理 Agent Cognitive Response。即时战术/Reaction/自动效果按 §0.1 独立执行，不等 Gate / EVA；action_intents 可表达宏观行为提议，不能据此要求 LLM 生成每一次机械 Tactical Intent。EpisodeObservation 的目标聚合边界见 §7.5，尚未替换现有 OB 契约。

| 所有者 | 职责 | 边界 |
|---|---|---|
| State Machine | 唯一权威 World / Character / Combat / RNG / NPC State、Evaluation Task / Status、模式、Gate 判断采用与调度、Observation / Inbox / Work / Processing Completion、游戏时间 TTL / Retention / Archive、来源关联、幂等、事务及恢复 | 不执行 LLM 主观推理，不管理物理 Context，不做自然语言语义验证 |
| Agent Host | JEV / EVA 模型执行、Prompt / Context Builder、Interactive Context 复用/释放、Background One-shot Context、授权 OB 增量/失效通知传输、超时重试取消、Token Budget / Prompt Cache / KV Cache、Tool 传输与调用日志 | 不拥有或持久管理权威游戏状态、Meta、任务完成或行为结果；不做语义筛选 |
| NPC LLM | 基于完整授权 Meta 与观察决定主观认知变化、对白和候选行动 | 只生成预定义 Schema 的非权威数据；不决定身份、任务资格或世界事实 |
| Action Execution | 受限 Action Intent → 稳定 command_id / Typed Command → 必要 Rule Evaluation → SM Commit | 独立 Command Receipt；动作成功不是 EVA 完成条件 |

统一逻辑流 **SM → Host → NPC LLM → SM**。SM 创建/批准任务并提供可信授权输入，Host 组织调用和传输 Result，SM 确定性验证、提交 Meta 并可靠交接输出；Host 将反馈送回相应调用。§2–§6 的可信 Host / 调用方描述指受控传输与命令构造，最终领域权限与提交仍由 SM 检查。

`interactive / inactive` 是 SM 管理的当前 NPC 模式状态；`interactive / background` 是 Evaluation Mode。Interactive 活跃（包括模型请求间空闲）期间，主观 Memory / Belief / Relationship / Goal / Plan 和自主决策均交当前 Interactive LLM；不创建新的 Background EVA 或额外 Memory / Cognition LLM。可选 Memory Gate JEV 只作重要性分类，不要求每条 OB 先调用模型。授权观察按事件顺序增量追加，不修改运行中请求、Context 或 KV Cache。

Inactive 不维持持续运行的 Interactive LLM Context。SM 的 Lightweight Gate 可决定优先 Background EVA、Deferred 批量调度或获准 Safe Retention / No-op（§9.8–§9.9）；可选轻量分类由 Host 执行、SM 验证采用，不代 NPC 生成 Memory / Belief。Background 使用一次性 Context，不创建/恢复/激活 Interactive Agent，也可提出行动。Gate 不为 EVA 语义筛选或排序 NPC Meta，实际模型仍可替换。

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

SM 内部 ObservationProcessingStatus 根据必要认知处理和可靠输出交接状态维护；获准 Safe Retention / No-op 可持久完成本轮认知工作，全空 Result 可完成 EVA，均不要求生成长期 Memory。完成只覆盖 Task 明确关联且实际处理的 Work 范围，调用在途新到达的 OB 不随旧 Result 一并完成。Completed OB 在到期前仍是 Recent OB，不能因读取/再次入 Context 重排同一工作；读、Context Append、LLM 返回、模型失败或任务取消本身不代表处理完成。内部 Completed Cursor 不跨未完成认知/未可靠交接项或投影缺口，无独立 ACK；清理不能改变水位语义。

Command 正在执行、失败或等待 choice **不自动使已完成 EVA / 已可靠交接的观察重新变为未完成**；未完成的 Command / PendingOperation 仍单独持久跟踪。动作失败反馈可送现有 Interactive LLM 继续动作交互，不自动重做完整 EVA 或再次写 Meta；若确需新的认知评估，由 SM 显式授权新任务，而非重放旧结果。

### 9.7 完整授权 NPC Meta、Belief History 与恢复 `[PROPOSED; NOT IMPLEMENTED]`

MVP 由 SM 提供该 NPC **完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan** 及有效 Recent OB（含 Completed）；待处理 Work 范围另外明确，不能从 Context 中出现哪些 OB 推定完成。授权完整不意味着全量世界/他人秘密。首次构建或重建 Context、Background One-shot 输入完整授权 Meta，Host 只组装，不做 Semantic Retrieval、Memory Ranking、语义筛选或智能压缩，也不增加独立 Memory Agent。超出模型预算明确反馈/保留任务，不能静默漏掉 Meta；已过期 OB 不作为近期输入，受限未完成 Work 恢复见 §7.4。

已有 Interactive Context 可复用，后续按事件顺序增量追加授权观察和已提交 Meta 变化，不要求每 EVA 重注入全量 Meta 或全部历史 OB。Memory Persistence 与 Context 资源管理保持分离；MVP 可预算保护、释放/重建 Context，不增加语义总结压缩。更复杂检索/压缩后置。

**Context 中 OB 到期 `[DECIDED]`：** SM 更新权威有效性并停止将其作为新的 Recent 输入；不强制删除现有 Context 历史 Token，不自动 Compression / Compaction。Host 可在下一次 Invocation 前追加 SM 授权的结构化失效通知（候选内容为 Observation ID、原始时间及已失效状态，Schema `[PROPOSED / OPEN]`）；不得异步修改执行中 Invocation 的输入、Context 或 KV Cache。通知本身不重新执行 EVA，不承诺 LLM 严格遗忘已出现文本。新建/重建 Context 不再提供过期 Recent OB；合法长期 Meta 自有持久生命周期，不因其来源 OB 到期而删除。

Adventure Package Initial Belief 与运行时 Belief 使用兼容结构：同一稳定 Belief 追加新版本，保留来源、版本、当前有效状态及旧历史，不直接覆盖/删除。NPC LLM 可修改、降低置信度或放弃旧 Belief；SM 仅校验结构、引用、权限、版本和数据库约束，不替它改写文本。

SM 持续不可用或持久化失败时，Session 停止权威推进，进入暂停/错误/待恢复流程；不能写库时不伪称状态已落盘。Host 不接管游戏状态，无影子权威副本或独立游戏执行队列。恢复依据 SM 持久 Task、已选 Result / Meta、可靠交接和独立 Command Receipt，不重做成功认知或行动；非战斗恢复必需，战斗中断精确续玩仍 Post-MVP。保留单命令响应丢失的幂等查询，不增加分布式协调系统。

### 9.8 JEV 的两个判断职责 `[DECIDED; PROPOSED; NOT IMPLEMENTED]`

允许同一底层轻量 JEV 模型承担两种任务，但使用**不同输入、输出 Schema 与权限验证**，不能混用结果或新增 Memory Agent / 认知状态权威：

| 职责 | 许可输入 | 输出与采用边界 |
|---|---|---|
| Perception Judgment（§7.2） | 待判断 Signals 与可信事件时感知证据 | 逐 Signal Boolean 察觉候选；SM 验证后形成 OB；不生成 Memory / Belief / 世界变化，不替代 RE 机械检定 |
| Memory Gate Judgment | 已确认察觉且授权的 OB、关联 NPC / Work 与必要调度信息 | 是否需及时认知评估的分类候选；SM 验证采用并路由；不重新判定察觉、不生成主观 Memory / Belief 或其他 Meta |

Memory Gate 建议分类为 **Urgent / Deferred / Irrelevant / Uncertain（或 Failure）**；分类语义见 §9.9，枚举编码、请求/返回字段和失败错误形状仍 `[PROPOSED / OPEN]`。沿用既有 Gate 分类反馈与持久 Work，不新增独立公共提交/ACK。SM 核验可信调用、任务用途、NPC / OB / Work 归属、分类类型与请求覆盖范围；未知/重复/缺失项、超时、Schema 错误不作为 Irrelevant 或自动完成。Host 执行模型，SM 持有判断采用、模式路由、调度与持久结果。

JEV 不是每条 OB 的必经模型步骤：确定性规则或批量分类均可使用，不必为普通 OB 单独发起 Invocation；模型/Prompt/阈值/成本预算不冻结。Interactive 模式也可选用 Memory Gate 重要性分类，但主观更新仍独占于现有 Interactive LLM。

### 9.9 按模式与优先级调度 EVA `[DECIDED; NOT IMPLEMENTED]`

| Gate 语义 | Inactive NPC | Interactive NPC |
|---|---|---|
| Urgent | 优先授权一次 Background EVA，联合考虑七字段输出；不自动生成长期 Memory | 优先授权现有 Interactive LLM 的下一轮 EVA，不创建 Background EVA |
| Deferred | 保留 Recent OB 与 Pending Work，积累多个 OB；定期调度或最长等待到达时批量 Background EVA | 随正常交互或定期 EVA 批量处理，复用 Context |
| Irrelevant | SM 可持久批准 No-op 完成本轮处理，无须 Background EVA；到期前仍可为 Recent OB | 可受控 No-op，不要求逐条 JEV 或完整 EVA；到期前仍可为近期信息 |
| Uncertain / Failure | 保守保留 Pending 证据，重试/确定性保底并纳入有界调度；不能当作 Irrelevant 清理 | 保留工作，由 SM 路由现有 Context 的后续处理；不启动第二个认知 EVA |

同一 NPC **只允许一个有效认知 EVA**，沿用 §9.2 的串行授权、版本检查与模式切换，不另设并行 Memory/Cognition 队列。新 OB 到达已有 EVA 时，Urgent 提升后续授权优先级，其余按序合并或排队；不能改在途输入或偷扩旧 Task 的完成范围。迟到 Gate 结果须按 SM 当前模式和 Work 状态重新路由，不能唤起旧 Background 任务或重开 Completed Work。Safe Retention / No-op 是处理结果，不能被解释为立即删掉 Recent OB 或替代长期 Memory Formation。

**定期 EVA `[DECIDED]`：最大调度等待期限必须严格小于相应 OB Lifecycle，并留出执行余量。** 候选约束可表达为同一游戏时间尺度下 `max_scheduling_wait + execution_margin < applicable_ob_ttl`，变长 TTL / 批次要考虑各 OB 的剩余到期窗口，不能反复合批重置最早等待期限。具体周期、最长等待、执行余量与游戏时间/Host 运行耗时的对应方式 `[OPEN]`。正常运行应在到期前完成必要认知处理；周期短于 TTL 并非绝对完成保证。

Background 调用失败、LLM 超时、Mode Switch、Game Time 跳跃、Context Budget 不足、同 NPC 已有运行 EVA、崩溃恢复均可能越过期限。SM 更新有效性并保护 Pending Work / 证据，按原 Task/Result/Receipt 对账后合法续处理或受控 No-op，不能因 TTL 到期丢失、伪造 Completed 或盲目重做已提交结果。Expiry 是 Retention 转换，不是唯一 EVA 触发条件；处理完成也不要求 Memory 写入。

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
7. **敌方 Agent 自主性与即时战术分离：** 至少一名敌方 Sub-agent 独立提出可核验的目标/宏观策略及战后认知，合法采用后实际影响 Combat Policy 的后续行为；即时 Typed Intent 经 RE 求值 + SM 提交，无每次战术 LLM 依赖，不冒用 PC 身份或把纯固定策略冒充 Agent 自主性。
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
| C-A13 | Interactive 新增 Observation | 原 Context 按序追加；主观认知由当前 Interactive LLM 处理，可选重要性 Gate 无逐条强制，新 Background / Memory / Cognition LLM 调用数为零 |
| C-A14 | Active Context 暂时无模型请求，重大事件到达 | SM 批准下一次 Interactive Task，Host 执行请求；在途调用期间新增输入排队，不修改执行中请求/KV Cache |
| C-A15 | Interactive Result 含 Dialogue、Belief、Memory、Action Intent | Meta 整批验证原子写入，行动独立 Typed Command，不回滚合法 Meta；全空 Result 合法 |
| C-A16 | Inactive NPC 经 Gate 一次 Background Evaluation 产生行动 | 无 Interactive Agent Context；同一 NPC 权限与共享命令路径，临时 Context 调用后释放 |
| C-A17 | 低价值 Observation / 轻量模型不可用 | 获准 Safe Retention / No-op 持久完成工作、TTL 前仍 Recent；轻量模型不可用保守保留 Pending，关键证据不丢失 |
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

### 12.4 v0.9 OB Lifecycle 与调度合成验收 `[PROPOSED; NOT IMPLEMENTED]`

以下为实现期测试目标，本轮只做文档一致性检查；覆盖既有 EVA / Work / Cursor 的生命周期扩展。

| ID | 场景 | 预期断言 |
|---|---|---|
| C-A36 | Irrelevant No-op / 全空合法 Result | SM 持久完成处理，无需生成长期 Meta；Completed OB 到期前可读为 Recent，重复投递/读取不重开同一 Work |
| C-A37 | 游戏暂停 / 墙钟流逝 / Game Time 跳跃 | TTL 仅据 SM Game Time；跳跃移除 Recent 投影，Pending 证据/任务受保护，Completed 不因到期重新 EVA |
| C-A38 | 同一 OB 被多个 Meta 及历史版本引用 | 到期归档必要原始证据和来源；不能删成悬空引用，内部归档不自动作为 NPC 近期记忆 |
| C-A39 | 清理与引用提交、任务/交接/审计/幂等竞争 | 同事务保护检查；仅工作完成且全部保护解除才可清理，Cursor / Receipt / 重试语义不破坏 |
| C-A40 | JEV 双用途与错误批次 | Schema / 权限分离，Perception 只判察觉，Gate 只分类已察觉 OB；错误/缺失/超时不当 Irrelevant 或 Completed |
| C-A41 | Inactive Urgent / Deferred / Irrelevant | 优先联合 EVA / 有界批量 EVA / 受控 No-op；最多一个有效认知 EVA，保留近期信息，不强制长期 Memory |
| C-A42 | Interactive 分类与在途新 OB | 可选 Gate，非逐条前置依赖；Urgent 下一轮优先、Deferred 批量、Irrelevant No-op；无新 Background，不改在途输入/完成范围 |
| C-A43 | 周期、合批、失败/超时/切换/预算/占用/崩溃 | 最大等待严格短于 TTL 且留余量，合批不重置最早期限；异常保留过期 Pending Work 并安全续处理，不谎称完成保证 |
| C-A44 | OB 已入 Context 后到期 | SM 更新有效性，下一 Invocation 可增量通知；不删除旧 Token、不自动压缩、不重做 EVA，重建排除过期 Recent OB |

### 12.5 v0.10 Event Evidence 合成验收 `[PROPOSED; NOT IMPLEMENTED]`

以下为后续实现测试目标；本轮仅以这些原创场景检查文档约束，不宣称已执行运行测试。

| ID | 场景 | 预期断言 |
|---|---|---|
| EV-A01 | 同一 Command 先在 A 发声再进入 B，或阶段间改变光照 / Conditions | 各 Event 按实际 Signals 阶段取证；相同 command_id / world_version 不足以共享变化字段，event_seq 不代替中间状态 |
| EV-A02 | 多 Event 的相关状态未变化 | 可共享可信不可变证据，仍保留各 Event / Signal 适用关联，不重复保存无关 Session 状态 |
| EV-A03 | 同 Event 多 Signal、候选重叠且 Scope 位于不同 Scene | 逐 Signal 发现后取 NPC / 环境并集，保留逐 Signal 候选关系；共享证据不扩大察觉权限，多个已察觉 Signals 沿用 OB 聚合 |
| EV-A04 | Scope 内失明、耳聋、被遮挡或 Inactive NPC | 全部进入候选；察觉阶段才判断能力/遮挡，Discovery 不预先判 Negative |
| EV-A05 | 缺失必要 Observer / Origin / 环境证据，处理时世界已变化 | 不用当前状态补齐、不默认 Positive / Negative、不让 JEV 猜事实；保留既有未完成工作，不假装候选为空 |
| EV-A06 | 零 Signal，或有 Signals 但候选确为空 | 区分合法空结果与缺证据；不生成空 OB、不调用无必要的 JEV，不复制无关感知状态，可靠记录完成 |
| EV-A07 | 大型已支持 Scope 分批、中断恢复及 NPC 随后移动 | 候选完整、去重可恢复，证据来自原子保存的历史依据；无当前态回填、无分页遗漏或跨越未完成水位 |
| EV-A08 | Event / Signals / Evidence / Outbox 任一持久化失败 | 同一 SQLite 事务全部回滚，无中间可见事实或后续 OB；提交后才允许 Perception Judgment |
| EV-A09 | Rule Engine 需要超出最小感知字段的机械状态；某事件中间阶段不可恢复 | 机械 Snapshot 保持完整依赖闭包；不能以感知 Evidence 替代，无法恢复阶段显式列为 OPEN 支持缺口 |

### 12.6 双路径与 Episode 原创合成场景 `[PROPOSED; NOT IMPLEMENTED]`

以下仅是设计推演和后续实现验收目标，不是已运行的 SM/RE/模型集成测试；不含受保护冒险内容。

| 场景 | Immediate Mechanical Response | Agent Cognitive Response / 观察限制 |
|---|---|---|
| 王宫拔剑 | 原创王宫接见中，PC 真正拔剑形成外显阶段；SM 用可信确定性/机械感知、已授权警卫 Combat Policy 与 RE 处理防卫、战斗触发及合法行动/Reaction，不等 Planner、JEV、Memory Gate 或 EVA。私有“想拔剑”不产生警卫响应，未知察觉不算已看到 | 拔剑、防卫及后续结果可属同一 Episode，各阶段独立取证。柱后侍从只听到金属声时，EpisodeObservation 不得写“看到 PC 威胁君主”；之后 NPC EVA 才可提议恐惧/关系/记忆或长期追责，Narrator 只呈现玩家获准事实 |
| 火球术 | 原创庭院施法按受支持规则连续处理施法、合法 Reaction 窗口、范围/豁免、伤害、集中与连带效果；不为每条骰点/支付审计调用 LLM。确需中途选择时按 §8.3 暂停/持久保存/恢复，不占写锁；不是“所有人先看到火球才允许 Save” | 施法、反制/爆炸及受影响结果按真实发生分支形成 Episode 阶段；被反制不能捏造爆炸阶段。某 NPC 只看见爆炸或只听到巨响，就只聚合该部分，不自动获知施法者、隐藏 Reaction 或完整因果；机械 Audit 不复制进观察/Memory |
| LLM 故障 / 未完整察觉 | Host / JEV / EVA 超时不阻塞已授权即时机械链；机械所需事实缺失仍显式报告能力缺口，不默认 Positive，也不凭认知结果补准历史执行 | 可靠保留既有 Pending Work / 证据；不得谎称已察觉、已完成或自动形成长期 Memory |
| 版本升级 / 中途重试 | SM 锁定 RE 与最新 main 分别验收；Continuation / RNG / 资源仅采用一次，已提交阶段不回滚或重掷 | 阶段观察不可变，聚合不能扩大授权；Episode Schema、增量和生命周期仍 OPEN |

## 13. 尚需显式批准或验证的开放问题

| ID | 问题 | 初步建议 / 决策要求 |
|---|---|---|
| C-01 | 各受支持规则的完整 Snapshot 依赖闭包与类型化组件映射？ | [OPEN]；逐规则核对状态读写、生命周期与权威/派生/临时数据，形成依赖矩阵；历史 `_LiveCombat` 盘点仅用于查漏，不规定目标结构或永久执行依赖 |
| C-02 | Engine 对外 `evaluate(...)` 与 NPC `combat.intent` 的最小 Python Typed Schema？ | 本草案用于语义审阅，字段名称/类型待代码适配论证，禁止先行声称已实现 |
| C-03 | PRNG 算法/编码及无消耗时 RNG 流版本策略？ | [OPEN]；显式状态/原子推进原则已确认，具体 wire format 与版本需实现对照和确定性测试 |
| C-04 | Interrupt / Continuation 的共同 ABI 与最小实施范围？ | §8.3 暂停/持久化/恢复/RNG 一致性和短事务原则 [DECIDED]；Result / Receipt 映射、前缀提交与 RNG 预留、交错/冲突、取消/到期和最小 MVP 路径 [OPEN; NOT IMPLEMENTED] |
| C-05 | 普通怪物的认知覆盖与 Combat Policy 配置？ | 即时战术不依赖 LLM 已 [DECIDED]；至少一名敌方 Agent 的宏观自主性仍需验收。哪些角色需要认知 Agent、策略选择/版本/目标授权与降级细节 [OPEN] |
| C-06 | 部分规则不支持时如何安全回退？ | `unsupported` 明确拒绝或人工裁决提议；严禁 Narrative 假装规则结果 |
| C-07 | 版本粒度及仅事件/元数据提交的 World Version 推进？ | [OPEN]；MVP 全局 OCC 保守方案，状态变更单调推进已确认，事件型提交推进细则不在本轮冻结 |
| C-08 | 活跃战斗崩溃中断后如何避免覆盖已提交结果？ | 明确 `combat_interrupted` 与安全恢复/阻塞协议；精确续玩 Post-MVP |
| C-09 | 消息版本、Fingerprint 规范及生效规则数据修订编码？ | [OPEN]；三字段 RulesetBinding 与含适用 Homebrew 的内容可区分性已确认，具体 canonicalization/摘要组合和候选消息版本需 ABI 审阅 |
| C-10 | PendingOperation 生命周期与 CommandReceipt 分支字段？ | [OPEN]；仅命令键查询、无独立回执 ID/ACK 已确认；具体持久性、过期与可空性由 SM 实施设计验证 |
| C-11 | EvaluationStatus / NPCStateVersion、Work / Task、唯一 Result 与可靠交接的最小存储/编码？ | 原子撤销旧 EVA 并新建、Meta 事务内校验任务/版本；状态编码、稳定 Result 比较和恢复实现待论证 |
| C-12 | Observation Cursor、投影水位、批次合并及内部 ProcessingStatus / Completed Cursor Schema？ | 需证明不跨越未投影/未完成项，明确必要认知处理、可靠交接及独立 Command 重入；具体类型待冻结 |
| C-13 | JEV 双职责 / 两种 EVA 模式的模型、Prompt、阈值、预算与取消能力？ | 同一模型可承担两个分离判断任务已确认；实际模型仍候选，通过合成场景测定漏判/延迟/成本，不固定技术选型或 SLO |
| C-14 | NPCEvaluationResult / EvaluationReceipt 的字段类型、元素约束、版本与错误映射？ | 七字段概念结构及两模式兼容原则已确认；JSON Schema、可信运行环境绑定和持久任务编码待审阅，不把草案当成已实现 API |
| C-15 | 完整 Effect / Reaction / 复杂组件 Delta 字段？ | [OPEN]；封闭 Typed Union、完整依赖与原子提交已确认，字段须对照现有生命周期与不变量盘点，禁止任意路径或 Snapshot 覆盖 |
| C-16 | combat.start / combat.create、rules.effect 与触发后续命令？ | AP-15 按操作类型校验 Actor 已 [DECIDED]；source_ref / 来源权限、具体字段与可靠编排仍 [OPEN]，见 §3.1 / §10 和 Adventure Package §11；不扩张为独立服务 |
| C-17 | 动态 World Operations 与 Conditional World Effect Proposal 的具体 Schema？ | [OPEN]；受限类型、SM 稳定身份、授权投影和提交边界已确认，完整 Object / Connection 字段、结果关联及复杂 Scene / 战斗地形生成未冻结 |
| C-18 | Observable Signal / Scope、结果条件与传播 Schema？ | [OPEN]；最小四字段/事件内 ID 与确定性范围原则已确认，具体枚举、复杂空间关系/传播参数、模板绑定与分时观察键仍待设计 |
| C-19 | 事件阶段采集协议、历史证据与正式感知检定的事务编排？ | [OPEN]；§7 的阶段对齐、最小完整证据与原子性已 [DECIDED]，真实 SM / RE 事件阶段及中间状态可恢复性、可信字段依赖/共享、历史引用/保留与完整候选分批仍须验证；无法恢复不虚构状态。RE 负责规则掷骰，RNG / command / 异步事务衔接不由 JEV 替代 |
| C-20 | OB TTL、Retention / Archive / SourceReference 的字段与清理保护？ | [OPEN]；游戏时间权威、双生命周期、多 Meta / 历史引用保护已确认；起算点、数值/分类型 TTL、编码、归档粒度与清理算法待设计 |
| C-21 | Gate 分类及定期 EVA / 最长等待的具体协议？ | [PROPOSED / OPEN]；Urgent / Deferred / Irrelevant / Uncertain 或 Failure 编码、批次覆盖验证、周期/执行余量、游戏时间跳跃及资源耗尽恢复细节待评审 |
| C-22 | Context OB 失效通知与过期 Pending Work 的受限恢复输入？ | [PROPOSED / OPEN]；非 Recent 回注、来源权限及通知字段需设计；不修改在途请求/KV Cache、不自动 Compaction 或重做 EVA |
| C-23 | CombatEpisode / EpisodeObservation 的共同协议？ | 一场完整战斗一个 CombatEpisode、整段经历只聚合已察觉部分 [DECIDED]；战时取证/战后聚合与可信历史重建比较 [PROPOSED]，身份/边界/因果、证据与生命周期映射 [OPEN; NOT IMPLEMENTED] |
| C-24 | Mechanical Audit 分流、RE 阶段 Evidence 与历史摘要？ | 目标 [DECIDED]；需审核真实事件语义、感知/机械字段依赖、审计保留/重放和版本迁移，不能从最终状态或 intent_submitted 虚构外显阶段；共同 ABI [OPEN; NOT IMPLEMENTED] |
| C-25 | Evennia 权威事实、数据库与提交边界如何映射？ | 采用方向及禁止相同事实双重权威 [DECIDED]；对象/领域服务/存储分工、缓存回滚与可靠通知须经 EB-1 / EB-2 验证 [OPEN; NOT IMPLEMENTED] |
| C-26 | Coding Agent 扩展如何受控启用？ | 能力目标及固定冒险基线 [DECIDED]；来源/版本/权限/启用、在途绑定、行为状态迁移、失败处理 [OPEN; NOT IMPLEMENTED]，版本回滚不撤销已提交事实 |

## 14. 建议实施顺序（后续验证，不是本批实现授权）

**[DECIDED]** Evennia 采用决定替代 v0.11 中以自建 SM / SQLite 闭环为先的开发顺序；旧实现与历史证据保留。后续先按 [采用计划 §8](./EVENNIA_ADOPTION_PLAN.md#8-eb-1eb-3-验证计划-proposed-not-implemented) 执行阶段验证，各阶段结果目前均未取得：

1. **EB-1 原生世界基础：** 两房间、门、NPC、文字交互、运行时对象创建/行为配置与正常重启持久性，证明实际复用框架。
2. **EB-2 真实 RE 集成：** 固定一个已支持操作与版本，验证唯一权威、显式 RNG、幂等、冲突、故障、回滚后对象/缓存一致性及提交后可靠通知。无需同时升级所有 RE 协议；受限旧集成不等于完整 Stateless 迁移完成。
3. **EB-3 运行机制与信息隔离：** 连续非 LLM 行为、目标离开后重查、受控版本切换、授权视图及最小 CombatEpisode 经历记录；不代表完整 Host、安全沙箱或通用 Continuation。

若必须大范围重写框架、维持相同事实双重权威，或无法满足关键正确性，应停止整体迁移并保留可复用设计，不自动转接另一框架。阶段通过后才另行安排完整 Package / Host / NPC 认知集成与单人文字 MVP；至少一名敌方 Agent 的宏观自主性、既有模式独占/任务完成语义及私有内容边界仍须验收。完整 Coding Agent 扩展系统不阻塞 EB-1。

RE 的能力/依赖盘点及 Stateless 迁移继续按独立切片推进，复用算法并去除隐藏状态；原有完整完成标准保留于 §14.1，不将其全部工作设为 EB-1 / EB-2 前置条件，不以 Adapter、文件数量或框架采用宣布规则迁移完成。

### 14.1 Stateful → Stateless 完成标准 `[DECIDED; NOT IMPLEMENTED]`

- **覆盖可追溯：** 原有规则逐项标明已迁移、仍 Transitional / Legacy 或经显式范围决定不再支持；所有最终声明受支持的规则统一从 Stateless Evaluation 执行。MVP 已选择的机制也必须走该接口，不能暗中落回旧执行器；尚有计划保留能力依赖 Stateful 时不能宣布完整重构完成。
- **旧依赖退出：** 最终 Rule Engine 求值与 SM 集成不再导入、构建、恢复或调用 `_LiveCombat`、`CombatHandle`、`_REGISTRY`、Stateful Combat Orchestrator；每个迁移切片提供依赖检查及实际执行证据。旧 API 只限隔离的回归对照；相关能力完成独立回归并切换全部受支持调用方后，移除其旧生产入口，能力清单完成后退出旧执行器。
- **显式输入/输出：** 完整版本化 Snapshot、Typed Intent、Pinned RulesetBinding 和 Explicit RNGContext 足以求值；无隐藏可变 Session 状态或全局 RNG。同一固定输入得到相同结果，所有状态变化、候选事件、RNG 转换及实际 ReadSet 显式返回。
- **规则与生命周期等价：** 复用正确算法，独立验证既有 Attack / Damage / Check / Save、资源归属、行动经济、移动、法术、效果、反应及跨回合生命周期等所保留能力；旧执行器对照不能替代独立期望结果，也不能把旧缺陷作为正确标准。
- **单一提交域：** 可信运行层承接 SM 职责，在经验证的提交边界内校验并原子提交 Delta / RNG 及相关 Events / Receipt / 可靠通知记录；具体 Evennia 存储映射仍 OPEN。注入失败、冲突、重复命令、响应丢失和受支持恢复场景证明无部分写入、失败缓存泄漏、重掷骰或双扣费；未提交结果不进入 Perception / Narration。活跃战斗精确恢复仍遵守 MVP 的 Post-MVP 边界。
- **进度指标：** 首先报告已消除/尚存的 Stateful 执行依赖，以及原有规则能力迁移覆盖；另报新规则覆盖和正确性，不以 Adapter、代码文件或新增规则数量宣称架构迁移完成。

### 本文批准条件

- 所有 P0 输入/输出/状态/失败语义没有“谁负责提交”的歧义。
- 提议的字段能完整表达目标规则语义并有可验证的实现路径；历史 Engine 仅用于查漏与回归，不限定目标结构，不能遗漏 Recharge/资源归属、Reaction、RNG 等状态。
- 一次跨领域操作有可验证的单一原子提交域；Evennia 数据库/对象缓存/可靠通知映射须经 EB-2 验证，不能仅由旧 SQLite 设计推定通过。
- 三种关系严格分开：**Proposal ≠ Evaluation ≠ Committed World Fact**；**Event Evidence ≠ NPC Belief**。
- 明确哪些规则还没有足够的实现证据或必须在 MVP 中降级/拒绝。
- 具体 ABI 评审通过前仍为草案，已有 [DECIDED] 架构约束继续有效；不得把任何目标接口当作已实现的公共 API。

## 参考代码（v0.1 历史审阅快照，非当前实现声明）

- [MVP Scope](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/MVP_SCOPE.md)
- [State Machine Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/STATE_MACHINE_ARCHITECTURE.md)
- [Agent Architecture](https://github.com/agentic-trpg/agentic-trpg/blob/419083376dc58587208cf87ffd1c29fc1fbbfcd8/docs/AGENT_ARCHITECTURE.md)
- [Rule Engine orchestrator](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/orchestrator.py)
- [Bridge Execution Receipts](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/combat_execution.py)
- [Bridge State](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/nat20-bridge/src/nat20_bridge/state.py)
- [Combat Outcome](https://github.com/agentic-trpg/trpg-rules-engine/blob/64dd920507de29602908b4bea1635eedc4385370/packages/dnd5e-engine/src/dnd5e_engine/outcome.py)
