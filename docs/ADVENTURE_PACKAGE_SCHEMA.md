# Agentic TRPG — Adventure Package Schema（MVP）

> **状态**：Draft v0.6（遵循 Module Contracts 的统一权威状态与 Stateless 目标，具体 Schema 尚未冻结为代码契约）
>
> **日期**：2026-10-10
>
> **级别**：项目级跨模块文档
>
> **建议位置**：`agentic-trpg/agentic-trpg/docs/ADVENTURE_PACKAGE_SCHEMA.md`
>
> **相关文档**：[`MODULE_CONTRACTS.md`](./MODULE_CONTRACTS.md)（跨模块目标接口最高规范）；[`MVP_SCOPE.md`](./MVP_SCOPE.md) v0.11；私有工作资料 `FIRST_BLUSH_MVP_REQUIREMENTS.md`
>
> **范围**：只定义**人工整理的静态冒险包**及其初始化/验证边界；不开发 World Creation Agent、视觉引擎或完整通用剧情编译器。

## 1. 目的与非目标

### 1.1 目标

首个 MVP 使用一个人工审阅、人工适配的 D&D 单人冒险包，初始化**一名玩家 PC**、场景、NPC、物体、谜题、必要的战斗与事件状态。由 State Machine 维护世界事实及持久化；Agent DM 主持和协调；需要独立决策的 NPC 使用 NPC Sub-agent；Rule Engine 计算受支持的规则与战斗机械状态转换（不持有权威战斗状态）。

本 Schema 的直接验收对象是一份固定、经过审核的本地 *First Blush* 冒险包，但**公开 Schema、示例和测试数据不得包含其未经授权的具体剧情、对白、地图或实质性改编内容**。下面所有示例均为**专门编写的合成场景**，不是从该作品中抽取。

成功标准是：`静态内容 → 校验 → 创建 Session → 运行/回访 Scene → 执行 NPC 决策与规则 → 保存/恢复`，不需要 PDF 解析、自动生成内容、图像或真实的视觉地图。

### 1.2 明确不在 MVP 内

- 自动读取或编译任意 PDF/HTML/Gamebook 的 World Creation Agent。
- 通用脚本执行引擎、复杂表达式语言、任意 Python/JavaScript 钩子、开放世界模拟。
- 完整地图/Token/动画与视觉同步；少量静态插画可选、非权威。
- 多玩家和可招募的常驻 AI 队友系统；剧本中角色的偶发援助不自动构成队友。
- 把所有 D&D 法术、规则和怪物能力补齐；未知机制应标记为待映射/不支持。
- 保证活跃 Combat 可以跨进程精确续玩（已明确放到 Post-MVP）。

### 1.3 设计取舍

**小而明确的 Schema，优先真实运行闭环，不为未来的 World Builder 提前构建抽象宇宙模型。** `Adventure Package` 是静态、版本固定、只读的内容定义；Session Runtime State 是单独的可变数据。内容中的自然语言只是描述与 Agent 上下文，**不是可执行规则或绕过验证的状态写入指令**。

---

## 2. 模块责任与数据所有权

| 数据或行为 | 定义者 | 运行时权威 | 约束 |
| --- | --- | --- | --- |
| 剧本背景、场景结构、进入条件、起始模板 | Adventure Package 作者（MVP 手工） | State Machine | 初始化模板只能在创建 Session / 特定实体首次实例化时应用一次 |
| PC Templates、职业/数值/装备的静态定义与审核 | Package 提供完整模板，玩家选择，机械属性经规则验证 | **State Machine**（选定角色的成长/HP/资源等运行状态） | 多个只读模板供选择，MVP 仍一玩家一 PC；不要求外部角色构建服务 |
| NPC Profile、动机、角色可知事实 | Adventure Package | State Machine 管理内容实例、知识与记忆 | NPC 只收到自身允许访问的数据 |
| NPC 对话或行动选择 | 对应 NPC Sub-agent / 经审查的非 LLM 策略 | 仅为提议；不直接获得状态写权限 | Agent DM 不替需要独立决策的 NPC 直接编造行为 |
| Scene、Quest、物体归属、剧情标志、世界时间 | Adventure Package 初始模板 | State Machine | 经过授权的结构化事件更新 |
| 攻击、豁免、伤害、集中、战斗位置、行动预算、RNG | Stateless Rule Engine 规则求值与显式输入 | **State Machine（所有已提交机械状态和 RNG）** | Engine 返回未提交的 Typed Delta / ProposedEvents / RNGTransition；SM 验证并原子提交，不重写规则 |
| 玩家可见文本和可选插画 | Agent DM / 界面 | 非权威 | 不能把描述当成已经提交的状态变更 |

**静态 / 动态边界**：Package 可以定义静态规则数据、规则绑定和初始状态模板；经审核的规则数据版本由 Session 的 Pinned RulesetBinding 固定。模板只在合法初始化时应用，后续 Inventory / Equipment、Effect、Reaction、Combat、RNG 等动态状态均以 SM 的已提交 Runtime State 为准，不从 Package 重置或补写，不使 Package 成为第二权威来源。Engine 接收 SM 的完整 Typed Snapshot 与显式 RNG，不从 Package 推断当前状态；规则求值目标遵循 MODULE_CONTRACTS.md §4–§6，不依赖 Legacy LiveCombat。

**执行协议原则**：Package 定义「什么可以发生」与「何时可以提议」，不宣告「一个需要掷骰的行为已经成功」。已有 Session 的游戏命令统一 submit_command(TypedCommand)，携带 session_id / command_id、可信 principal_id、command_type、expected_world_version、强类型 payload 及按具体类型适用的 actor_id（AP-15，见 §6.3 / MODULE_CONTRACTS.md §3）；创建前的幂等键见 §9.1a。规则求值无权威副作用，由 SM 按单个命令原子提交；已提交事件的后续效果使用可靠独立命令，不承诺跨已提交事务原子性（§7.3）。具体 HTTP/Python 消息格式将在 `MODULE_CONTRACTS.md` 评审冻结。

---

## 3. 文件组织、格式与版本

MVP 建议使用 **UTF-8 YAML** 表示人工录入数据，外加 JSON Schema/Pydantic 验证器（具体工具未定）。通用运行时不得通过加载 YAML 标签实例化任意类；解析必须限制在普通标量、列表和字典。

建议单个本地包目录为：

```text
adventure-pack/
├── manifest.yaml          # 必需：身份、版本、规则基线、入口场景、来源/许可
├── world.yaml             # 必需：世界事实、地点、全局初始标志
├── scenes.yaml            # 必需：场景、连接、场景初始模板与可见范围
├── actors.yaml            # 必需：NPC Profile、控制策略、角色知识（不包括运行时存档）
├── pc_templates.yaml      # 必需逻辑数据：一个或多个完整只读初始 PC Templates
├── encounters.yaml        # 可选：预定义 Encounter；真实 Encounter 也可由 SM 动态启动
├── events.yaml            # 必需：触发条件与允许的世界效果（无事件时为空列表）
├── rule_bindings.yaml     # 必需：规则版本引用及已审核的 ID 映射
└── assets/                # 可选：合法使用的本地静态素材；MVP 可以不存在
```

**MVP 可以把小规模内容放在更少文件中**，只要字段和引用关系等价、校验可复现。上述布局是逻辑推荐，不要求先做通用包加载插件系统。

### 3.1 Manifest 必需字段

| 字段 | 类型 | 用途/验证 |
| --- | --- | --- |
| `schema_version` | string | 例如 `0.1.0`；解析器拒绝未支持的重大版本 |
| `adventure_id` | string | 全局稳定、命名空间化，如 `example.harbor_watch` |
| `package_version` | string | 内容的不可变版本标识，不等于游戏存档版本 |
| `title` | string | 面向作者/用户的标题；公开示例为原创标题 |
| `entry_scene_id` | string | 必须指向已定义的场景 |
| `ruleset_binding` | object | ruleset_id / data_revision / evaluator_version；加载批准后固定生效绑定，数据修订含适用 Homebrew，具体编码 [OPEN] |
| `player_setup` | object | player_count=1、pc_count=1、可选模板的起始约束；不要求独立构建服务，不预置 AI 队友 |
| `content_provenance` | object | 来源类型、审阅记录、许可/访问约束、是否允许再分发 |
| `compatibility` | object | 已审查/未解决的旧版规则差异和适配版本引用 |

禁止仅凭外部资产的同名 `slug` 就认定 Rule Engine 支持相应机制。包版本与已批准的 RuleSet/数据源版本在 Session 创建时固定；运行中升级必须是显式迁移，不能静默替换。

### 3.2 ID 与引用约定

- 推荐使用具语义前缀的稳定 ID，例如 `scene.harbor_gate`、`npc.gate_warden`、`object.iron_gate`、`encounter.dock_ambush`、`event.gate_opened`；大小写/字符集及最长长度由实现 Validator 固定。
- 作用域内 ID 不得重复；Scene/NPC/Object/Encounter/Event/Rule Binding 的引用必须能够解析。
- 实例 ID 与定义 ID 不同：`npc.gate_warden` 为定义，Session 内运行实例可以再带 `instance_id`。不要使用显示名称作为主键。
- 数值和时间单位必须明确（如 `feet`、`rounds`、`seconds`），禁止从描述文本推导计算规则。
- 通过引用复用已有 Engine Canonical ID；剧本特殊规则可用 `host_adjudicated` 明确标注，不能冒充 Canonical 法术/怪物。

---

## 4. 世界与场景模型

### 4.1 `world.yaml`（世界静态事实）

最小字段：

- `locations[]`：`location_id`、`name`、`description`（可为空）及包含的 `scene_ids`；**地点**不等同于一个运行时 Scene。
- `world_facts[]`：稳定 `fact_id`、`statement`、`visibility`（`public` / `dm_only` / `npc_scoped`）以及必要来源。只有 `public` 的事实可以无条件公开。
- `initial_flags`：MVP 需要的有限布尔/枚举/整数标志及其初值；不应将 HP、法术槽、攻击结果当成世界 Flag。
- `starting_location_id`：入口场景所属地点。

`world_facts` 表示世界客观事实；NPC 对事实的了解、误解和态度是**另一份独立数据**，不能把 `world_facts` 直接全部交给 NPC Sub-agent。

### 4.2 `scenes.yaml`（场景静态定义与初始状态）

每个 `scene` 最小字段：

| 字段 | 含义 | MVP 验证 |
| --- | --- | --- |
| `scene_id` / `location_id` | 唯一标识和位置归属 | 引用有效 |
| `description` | DM 可使用的背景描述 | 不自动成为结构化事实变更 |
| `exits[]` | 连接到其他 Scene 的有向出口 | `to_scene_id` 存在，条件必须可验证 |
| `initial_state` | 只在 Session 初始化/首次实例化时应用的模板 | 重访不重置 |
| `actor_ids[]` | 初始在场 NPC 定义引用 | NPC 位置与当前可用身份一致 |
| `objects[]` | 场景可交互世界物体及起始状态 | 物体稳定 ID，变更有权限 |
| `event_definition_ids[]` | 在场景适用的静态 EventDefinition 引用 | 定义存在，与实际 CommittedWorldEvent.event_id 分开 |
| `encounter_ids[]`（可选） | 预定义 Encounter 的引用 | 有引用须有效；可不预定义，不意味着进入即开战 |
| `access_policy` | DM / NPC / 玩家在此场景允许观察的字段边界 | 默认不公开隐秘事实 |

**关键不变量**：`Scene Definition` 是只读内容；`Scene Runtime State` 才记录开门、线索、机关、掉落、NPC 位置等变化。重访时读取 Runtime State；若未实例化，则从静态模板创建一次。允许玩家以合理选择改变预期路线，禁止通过强制每幕顺序跳转覆盖既有状态。

### 4.3 Scene、Event 与时间

- `scene.entered`、`scene.exited` 可作为结构化事件，不直接暗示剧本完成。
- 游戏内轮数由 State Machine **最终已提交**的 `Turn/Round` 规则事件驱动；世界时间由 State Machine 管理。不得依赖 LLM 在文本中自行数回合。
- “第 N 回合”“获得某项线索后才能进入”“累计若干成功”需独立字段或累计状态，而非运行时解析自然语言。
- 如果一个场景始终无法满足入口条件，系统要返回拒绝/解释，不能偷偷修改事实以确保剧情继续。

---

## 5. Actor 与 NPC 的最小 Schema

### 5.1 区分 PC、NPC、怪物、非人物交互者

- `pc_templates[]`：Package 内置一个或多个完整初始 PC Templates，供玩家选择；静态机械属性须经规则验证，实例化后的 CharacterState 由 SM 保存，不由 Package 覆盖。
- `npc`：独立实体，至少包含 `actor_id`、`name`、`role`、`controller`、`profile`、`initial_location_id`、`knowledge`、`relationship_state` 和必要 `rule_binding_id`。
- `monster`：可被 Encounter 引用的敌人模板，拥有机械 `rule_binding_id`；是否调用 LLM 是控制策略，与怪物的规则身份分开。
- `interactive_entity`：可交谈的非生物对象（例如合成演示中的会说话的钟），可具有 NPC 决策接口，但不等同于可攻击的 Actor。

### 5.1a 内置 PC Templates（AP-05）

**[DECIDED]** 每个模板为只读静态定义，具有稳定 pc_template_id、展示信息及完整初始机械角色数据（构建、属性、特性、装备/库存、HP/资源初值等），并符合固定规则绑定与冒险起始约束。模板类型及具体字段为 **[PROPOSED; NOT IMPLEMENTED]**，须复用/映射共享 CharacterState 等基础结构并验证规则合法性，不能只有一段角色文案或不可解析的外部引用。

一个 Package 可以提供多个完整模板，但 Create Session 的 players[] 在当前 MVP 中仅有一项、选择一个 pc_template_id。角色成长、当前 HP、已消耗资源等在 SM 中持续演化，不回写模板。独立角色构建服务或外部 pc_build_ref 不是 MVP 前提；未来可扩展外部导入，协议/校验仍 [OPEN]，本轮不实现。

### 5.2 控制策略与 Sub-agent

`controller.kind` 建议允许：

| 值 | 用途 | 约束 |
| --- | --- | --- |
| `sub_agent` | 需要角色自主对话、策略/战术选择的 NPC | 按需执行；上下文隔离；只返回提议 |
| `deterministic_policy` | 经审核的有限行为策略 | 非 LLM；不能伪称是一个自主推理的 NPC Agent |
| `scripted_event` | 无自主决策的客观事件、情节援助、环境危险 | 不能作为长期 NPC 队友系统 |

**待决策**：普通敌人是否默认调用 `sub_agent`。`MVP_SCOPE.md` 目前要求**至少一名敌方 NPC 的显式战术 Intent**来自独立 NPC Sub-agent；这与“每个普通怪物都要调用 LLM”不是一回事。实现可对其它低复杂度怪物使用 `deterministic_policy`，但不得把它当作已完成上述 Sub-agent 验收。

### 5.2a NPC Schedule 初始模板（可选、MVP 基础）

`actors.yaml` 可以包含 `default_schedule` / `initial_activity` / `schedule_conditions`，表达 NPC 在游戏内时间下的预设工作、用餐、休息和初始位置。内容只规定**候选日程与初始条件**；实际 `current_activity`、日程取消/中断、下一游戏时刻、活动完成回执是 State Machine 持久化的 Runtime State。具体时间格式及触发 AST 待 `MODULE_CONTRACTS.md` 验证。不得从日程文本直接执行未授权动作、瞬间传送或越过 Rule Engine 求值。

### 5.3 NPC 知识隔离

将同一 NPC 的资料分为：

1. `profile`：稳定身份、说话风格、目标、行为约束、可用行动类别。
2. `initial_knowledge_ids`：该 NPC **起初已知**的 `fact_id`，不等于世界全部事实。
3. `initial_beliefs`：与运行时 Belief History 使用兼容结构，保留稳定 Belief 标识、来源、版本、confidence（适用时）与当前有效状态；可为错误主观判断，不覆盖 World Fact。运行时修改/降低置信度/放弃由 NPC LLM 提议，SM 仅确定性验证并追加新版本，不覆盖/删除旧历史；具体 Schema Proposed / Not Implemented。
4. `relationship_state`：与 PC 或其他 NPC 的关系与初始标记。
5. `memory_policy`：哪些**已提交**的重要互动才允许成为记忆，谁有权读取；原始私有推理轨迹不作为世界事实存储。
6. `secrets`：只有具该角色权限的上下文可见；不能以一个 `dm_only` 密文的引用自动授权给 NPC。

NPC Agent 输入应是 State Machine 从上述字段**按当前权限投影出的 NPC View**，而不是冒险包的原始全量文件。MVP 首次构建/重建 Context 提供完整授权 Profile、Episodic Memory、Belief History、Relationship、Goal、Plan 和新 Observation，Host 只组装、不语义筛选；已有 Interactive Context 后续可增量追加已提交变化，不要求每次全量重注入。任何对话或行动都先成为提议，再经授权/验证转换为正式世界变更。NPC 的谎言、预测或临时想法不等于事实已经改变。

---

## 6. Encounter、规则映射与环境危险

### 6.1 Scene / Encounter 的运行时边界（AP-11、AP-13）

**[DECIDED]** Package 提供只读 SceneDefinition、可选 EncounterDefinition 及初始模板，不提供执行 Scene/Encounter 的 API。encounters.yaml 可省略；存在时每项可描述 encounter_id、scene_id、participants[]、start_conditions、initial_positions、victory_or_exit_conditions、rule_binding_ids[] 与适用的 solo_adaptation_ref。静态引用存在时必须有效，但不要求所有真实战斗事先预定义。

SceneInstance 由 SM 在一个 Session 内按需初始化一次，入口场景在创建事务中初始化；之后进入、退出、重访、恢复均由 SM 读取/更新实例。NPC 是 Session 级唯一实体，Scene 的 actor_ids[] 只是初始引用，不能重建已存在 NPC、重置其位置/资源/Memory/Belief 或复制掉落/机关。

SM 可基于当前权威状态动态启动 Encounter，不强制 EncounterDefinition 存在；参与实体及初始位置须可信、机械数据经过规则验证，不能从 LLM 文本伪造 Monster Stat Block。Encounter 的结局可以是胜利、撤退、投降等，不能预设敌人必须死亡；单人适配仍需人工追溯，不允许篡改已掷结果。

先攻与战斗初始化复用统一 RuleEvaluationRequest / RuleEvaluationResult（MODULE_CONTRACTS.md §4–§6）。候选 operation_kind=`combat.start`，payload 为强类型启动参数，输入当前相关 **NonCombatSnapshot**、固定 RulesetBinding 与独立 RNGContext。Engine 在 accepted 时返回未提交 Typed StateDelta、ProposedEvents、RNGTransition；SM 重新验证并在同一事务建立权威 CombatState、相关状态、RNG、正式事件、CommandReceipt 和 Outbox；规则拒绝、求值故障或提交失败不建立部分有效 CombatState，不推进权威 RNG。

`combat.start` / 其 Payload 及候选 Typed Delta `combat.create` 均 **[PROPOSED; NOT IMPLEMENTED]**；combat.create 的完整字段、初始化映射与不变量为 [OPEN]，不能覆盖整个权威 Snapshot。Enemy Sub-agent 的显式战术 Intent 仍走同一授权/求值/提交边界，不以本轮文档宣称现有公共 API 已支持。

### 6.2 `rule_bindings.yaml`

每条 `rule_binding` 建议包含：

```yaml
binding_id: rules.monster.small_guard
source_kind: canonical_monster
canonical_id: some-reviewed-srd-id
ruleset_id: dnd-2024-srd-5.2.1
review_status: needs_verification
source_revision: null
adapter_notes: "Synthetic example; not an assertion that this ID exists."
```

上述为**字段示意**，`canonical_id` 是示意占位，不应被当作现有仓库的真实资源。实现加载时必须拒绝未经审核的真实绑定、未知 ID、来源规则版本不符及未支持的强制机制，并给出结构化错误。旧版模组数值到 D&D 2024 的变更应保留**原始值、目标值、理由、审阅状态**，不能默默覆盖。

### 6.3 机关、环境危害、非战斗技能挑战（AP-14）

**[DECIDED]** SM 判断 Trap / Hazard / Mechanical Effect 的声明式触发条件，Rule Engine 计算豁免、伤害、Condition 等机械结果，SM 提交状态、RNG、事件、CommandReceipt 与 Outbox；不根据自然语言或 ProposedEvents 重算伤害。

候选 operation_kind=`rules.effect`，复用统一 RuleEvaluationRequest / RuleEvaluationResult、当前适用的 CombatSnapshot / NonCombatSnapshot、Session 固定 RulesetBinding 与显式 RNGContext。该操作及具体 Payload / Effect Schema 均 **[PROPOSED; NOT IMPLEMENTED]**，复杂字段与编排为 [OPEN]；必要机制无可验证支持时阻止 Package 批准，不能直接写 PC HP。

**AP-15 [DECIDED]**：TypedCommand / RuleEvaluationRequest 的 actor_id 是否必填由具体操作类型决定。Actor 行动必须有真实 actor_id；受信系统/世界事件发起的 combat.start、rules.effect 等可以没有行动 Actor，但必须验证可信 principal、机械来源和目标，不虚构 NPC，也不将全部操作无约束可空。按操作类型区分的强类型联合、source_ref / 来源权限与具体 Schema 字段仍 **[PROPOSED / OPEN; NOT IMPLEMENTED]**，以 MODULE_CONTRACTS.md §3.1 / §4.1 为准；本轮不实现。事务组合与可靠后续命令边界见 §7.3。

Skill Challenge 由 SM 保存成功/失败计数与状态，每次检定经统一 Rule Evaluation 和 (session_id, command_id) 关联的已提交结果去重。剧情威胁不必伪造成可战斗怪物；其机械后果仍须受控规则求值，非机械世界效果仅使用允许列表。

---

## 7. Event/Condition/Effect：受限声明式流程

### 7.1 静态 EventDefinition 与权威触发事件（AP-12）

**[DECIDED]** Package 的 EventDefinition（候选 event_definition_id、trigger / condition / effect / repeat / scope 字段）是静态声明，不是已经发生的 CommittedWorldEvent。后者由 SM 经受控命令提交后分配 event_id / event_seq，保留 source_command_id；动态交互也可生成实际世界事件，不要求它们都预定义在 Package。SM 管理定义的作用域、触发条件、历史和执行，Package 不运行脚本，不新增独立 Event Engine 服务。字段编码仍 [PROPOSED; NOT IMPLEMENTED]。

预定义 EventDefinition / 标准行为可提供按可能执行结果分类的候选 Observable Signal 模板，Planner 也可随 Intent 提议；SM 只按可信结构化结果选择并与实际 WorldEvent 原子提交。Signal 的最小四字段、察觉与授权规则以 MODULE_CONTRACTS.md §7 为准；EventDefinition 的触发/重复作用域、机械 Effect Scope 和 Signal 感知 Scope 各有独立职责，不另存 perception_scope。模板/条件/Scope Schema [PROPOSED / OPEN; NOT IMPLEMENTED]，不由静态 Package 执行传播或新增 Event Generation Agent。

MVP 候选 `trigger.type`：

| Trigger | 权威产生者 | 例子 |
| --- | --- | --- |
| `scene.entered` / `scene.exited` | State Machine | 首次进入、离开 |
| `object.interacted` | State Machine 经授权的交互提交 | 检查/操作机关 |
| `check.resolved` | State Machine 最终提交的 Rule Engine 检定求值结果 | 通过 DC、失败 |
| `npc.decision_accepted` | State Machine 已合法执行并提交的 NPC 决定/对应事件 | 已发布话语、已确认承诺或已执行行动；Host 接受 Proposal 本身不触发 |
| `combat.event_committed` / `combat.ended` | State Machine 提交的机械规则求值事件/结果 | 指定回合、离场、结算 |
| `world.flag_changed` | State Machine 事务 | 线索、门、任务标志改变 |
| `challenge.updated` | State Machine | 技能挑战计数变化 |

**LLM Proposal / Action Intent 不是已提交 Trigger。** 对话谜题须先对结构化 `utterance` / `fact_revealed` 提议进行权限与场景合法性验证，实际执行提交后才可通过 `npc.decision_accepted` 事件触发条件。Interactive / Background 或经审查的策略复用同一 Typed Command 路径；不将任意文本解释为脚本。

### 7.2 条件表达式：MVP 用封闭词汇，不支持 `eval`

建议只允许 `all`、`any`、`not` 组合以及简单类型断言：`flag_equals`、`actor_present`、`object_state_equals`、`fact_known_by`、`challenge_count_at_least`、`event_once`；未知 Operator 加载时拒绝。

条件查询需要明确 `subject`、可见范围与来源，不能通过从 Agent DM 自由文本中匹配字符串作出权威状态判断。

### 7.3 世界效果允许列表与事务边界（AP-12）

**[DECIDED]** SM 加载声明式定义、按 Session / Scene 等作用域判断触发条件并保存触发历史。允许的世界效果沿用 set_flag、set_object_state、move_world_actor、grant_or_transfer_world_item、reveal_fact_to_actor、update_relationship、advance_challenge、start_encounter_request、transition_scene_request；具体 AST / Payload 编码仍 **[PROPOSED; NOT IMPLEMENTED]**。涉及机械资源/库存规则或 HP/豁免/Condition 等计算的部分必须交 Rule Engine，不能用世界字段直接宣称已生效。

区分两条提交路径：

1. **同一命令提交前可完整求值**：基于已有权威状态/已提交触发来源，将所需世界效果与完整规则结果准备好，再由 SM 在一个短 SQLite 事务统一校验与提交全部变化、RNG、正式事件、CommandReceipt、触发历史及 Outbox。失败全部不写；求值在写事务外。
2. **先前 WorldEvent 已提交后才触发机械效果**：保留该已提交事实，SM 可靠记录触发历史与后续命令交接，使用独立稳定 command_id 幂等求值/提交。触发消费标记与命令交接同事务保存，不能先标完成再遗失派发；重试复用原命令键并查询持久结果。不得虚构跨两个已提交事务的原子性，也不得因后续失败回滚先前事实。

重复投递/重启不能重复伤害、领奖或重新掷已提交命令的骰点。once_per_session / once_per_scene 等重复政策按定义与作用域去重，同时保留触发来源；失败/待处理命令及 Outbox 可恢复。未提交 ProposedEvents 不能冒充已提交 Trigger。复杂效果组合、可靠调度的具体存储/编排与循环限额为 [OPEN]；不新增独立 Event Engine 服务、跨服务事务状态机或 ACK 协议。

---

## 8. 示例：完全原创的最小冒险片段

以下片段是 **字段关系与行为语义提案**，不是已冻结的机器 Schema 或可直接批准的完整 Package。未展开 §5.1a 的完整 PC Templates（创建示例引用 pc_template.harbor.scout），规则版本也是占位；真实加载必须补齐并验证，不得将此片段当作 valid Package。用于公开测试时请继续使用本类合成内容，**不要复制 First Blush 的场景事实**。

```yaml
# manifest.yaml
schema_version: "0.1.0"
adventure_id: example.harbor_watch
package_version: "0.1.0"
title: "Harbor Watch (synthetic test fixture)"
entry_scene_id: scene.harbor_gate
ruleset_binding:
  ruleset_id: dnd-2024-srd-5.2.1
  data_revision: "<effective-data-revision; requires validation>"
  evaluator_version: "<matching-evaluator-revision>"
player_setup:
  player_count: 1
  pc_count: 1
  start_level: 1
content_provenance:
  origin: original_synthetic_fixture
  redistribution: permitted
compatibility:
  review_status: synthetic_only
```

```yaml
# world.yaml
starting_location_id: location.harbor
locations:
  - location_id: location.harbor
    name: Harbor
    scene_ids: [scene.harbor_gate, scene.harbor_yard]
world_facts:
  - fact_id: fact.gate_key_location
    statement: "The gate key is stored in the harbor office."
    visibility: dm_only
initial_flags:
  gate_open: false
```

```yaml
# scenes.yaml
scenes:
  - scene_id: scene.harbor_gate
    location_id: location.harbor
    description: "A quiet harbor gate with a watch post."
    actor_ids: [npc.gate_warden]
    initial_state:
      entered_once: false
    objects:
      - object_id: object.harbor_gate
        kind: door
        initial_state: closed
    exits:
      - to_scene_id: scene.harbor_yard
        when: {flag_equals: {key: gate_open, value: true}}
    event_definition_ids: [event.warden_opens_gate]
    encounter_ids: []
    access_policy: {private_facts_visible_to_player: false}
  - scene_id: scene.harbor_yard
    location_id: location.harbor
    description: "An empty storage yard."
    actor_ids: []
    initial_state: {}
    objects: []
    exits: []
    event_definition_ids: []
    encounter_ids: []
    access_policy: {private_facts_visible_to_player: false}
```

```yaml
# actors.yaml
actors:
  - actor_id: npc.gate_warden
    kind: npc
    name: Gate Warden
    initial_location_id: location.harbor
    controller: {kind: sub_agent}
    profile:
      goal: "Keep the gate secure without needlessly detaining visitors."
      style: "Brief and courteous."
    initial_knowledge_ids: [fact.gate_key_location]
    initial_beliefs: []
    relationship_state: {}
    memory_policy: {record_accepted_commitments: true}
    rule_binding_id: null
```

```yaml
# events.yaml
# Agent dialogue is not enough. Only a State Machine committed object interaction
# after authorized execution can satisfy this event; Host acceptance is insufficient.
events:
  - event_definition_id: event.warden_opens_gate
    trigger:
      type: object.interacted
      actor_id: npc.gate_warden
      object_id: object.harbor_gate
      operation: open
    conditions:
      all:
        - {object_state_equals: {object_id: object.harbor_gate, value: open}}
        - {actor_present: {actor_id: npc.gate_warden, scene_id: scene.harbor_gate}}
    effects:
      - {set_flag: {key: gate_open, value: true}}
    repeat: once_per_session
```

```yaml
# encounters.yaml
encounters: []
```

```yaml
# rule_bindings.yaml (no mechanics invoked by this synthetic fragment)
bindings: []
```

**注意**：例子中 `Gate Warden` 决定是否开门，仍需要由 State Machine 验证其身份、授权以及世界中的交互前提；Host 仅传输可信任务关联与模型结果。`rule_bindings.yaml` 为空仅因示例没有规则检定/战斗，不代表真实 MVP 可以不对实际机械行为进行映射。

---

## 9. 加载、运行、保存与回放协议

### 9.1 统一 Package Loading / Validation（AP-01～04）

**[DECIDED]** 对外只有一个逻辑加载入口，内部由 SM 完成安全解析、Schema、引用、规则绑定、声明式操作及必要元数据验证。没有独立加载/验证服务，不暴露可供创建 Session 使用的半验证状态。

候选接口与数据类型均 **[PROPOSED; NOT IMPLEMENTED]**：

```text
load_adventure_package(package_source)
  -> PackageLoadResult(status=valid | invalid, errors, warnings,
                       approved_package_metadata when valid)
```

errors / warnings 是带 code、位置/引用及原因的结构化问题，字段编码仍待设计。Schema 错误、非法引用、无法匹配的规则绑定或必要机制不支持均返回 invalid，不能批准后等到运行时假装可执行。不阻塞核心路径的可选内容限制可以明确 warnings，并保持该内容不可执行/受限；不能把它当已支持规则。valid 时 errors 为空，可有上述明确 warnings。

通过后固定 adventure_id、package_version、package_digest 和**生效 RulesetBinding**（ruleset_id / data_revision / evaluator_version，含适用 Homebrew）；SM 创建与恢复 Session 均核验这些固定值，不能按同名目录静默换内容。具体摘要/绑定编码沿用 MODULE_CONTRACTS.md 的 [OPEN] 项。

静态验证只证明已执行的结构/能力检查，不证明剧情可玩、战斗平衡或行为必然正确。来源/许可元数据检查支持人工审阅与发布限制，不是自动版权合法性证明；First Blush 内容仍仅本地私有保存。

### 9.1a Create Session（AP-06～10）

**[DECIDED]** SM 接收已批准 Package 的固定身份/摘要与玩家选择，生成并返回 session_id。PC 来自 §5.1a 的内置完整只读模板；HP、成长与资源在初始化后属于 SM 运行状态，不写回模板。不要求独立角色构建服务或外部角色引用。

候选 CreateSessionRequest（**[PROPOSED; NOT IMPLEMENTED]**，原创关系示例；模板完整机械数据在此不展开）：

```json
{
  "command_id": "cmd.create.harbor.001",
  "adventure_id": "example.harbor_watch",
  "package_version": "0.1.0",
  "package_digest": "sha256:<approved-package-digest>",
  "players": [
    {
      "player_id": "player.demo",
      "pc_template_id": "pc_template.harbor.scout"
    }
  ]
}
```

即使单人也使用 players[]，MVP 严格只允许一个玩家选择一个 PC。principal_id 来自可信认证环境；SM 验证该主体与 player_id / 角色控制关系，不接受 LLM 自报权限。该主体不等同于未经验证的 player_id，客户端也不提供新 Session 的 session_id。

创建前尚无 Session，以可信 **(principal_id, command_id)** 在 SM 持久数据库中幂等处理；对规范化请求保留 Fingerprint，同键相同内容返回原 Session / 原创建结果，同键不同内容拒绝冲突。并发创建与响应丢失后的相同请求重试不能生成第二份 Session；不新增创建请求 ID、Receipt ID 或二次 ACK。普通游戏命令仍以 (session_id, command_id) 处理。

模板机械验证、必要求值与准备在写事务外完成；SM 在短 SQLite 事务重新核验批准摘要/规则绑定、可信控制关系及创建键，原子初始化 SessionRecord、WorldState、当前必要的唯一 Actor/NPC Persistent State、选定 CharacterState、入口 SceneInstance、权威 RNG 等，并记录创建键到 Session/结果的映射。失败不得留下半初始化的有效 Session；完整创建记录与幂等映射同成同败。RNG 算法/编码不在本轮冻结。

返回 Session ID、创建结果及有限的 Package/版本等元数据；不返回全量 WorldState、GM Secret、隐藏 NPC 或未发现事件。后续视图按可信权限读取。创建其他独立 Session 使用新的创建 command_id；多个模板选择不意味着支持多玩家或 AI 队友。

### 9.2 一次交互

```text
Player intent / NPC decision proposal
    -> validate controller identity, visible facts, scene version
    -> decide: world operation / Engine rule invocation / narrative-only
    -> prepare unique command_id, expected_world_version
    -> SM obtains full relevant Snapshot + pinned RulesetBinding + independent RNGContext
    -> Rule Engine evaluates if required (outside write transaction)
    -> SM validates and atomically commits this command's state/RNG/events/receipt/Outbox
    -> receive typed committed result (or structured refusal)
    -> Perception persists authorized Observations; optional NPC updates validated separately
    -> DM narrates from the committed state
```

最终数据库提交/响应边界按 (session_id, command_id) 查询稳定 CommandReceipt，无独立回执 ID 或二次 ACK；未提交求值不推进权威 RNG。事件后续触发机械效果时按 §7.3 的可靠独立命令处理，不将两个已提交事务叙述成同一次原子提交。

### 9.3 保存与恢复

- Adventure Package 不随玩家操作改变；Session 保存固定 Package / RulesetBinding、世界/场景/NPC 状态、已选角色 CharacterState、RNG、触发历史、待处理命令/Outbox 与按命令键查询的 CommandReceipt。
- SceneInstance 按需初始化一次，入口在创建事务中初始化；重访/恢复读取已有状态，不重生奖励、机关或 NPC。NPC 为 Session 级唯一实体，位置、Memory、Belief 与资源不因另一场景初始化被复制/重置。
- MVP 最少支持非活跃战斗 Session 保存/恢复。活跃战斗精确续玩仍 Post-MVP，不能装作已恢复或悄悄覆盖已提交结果。
- Deterministic Replay 依据已提交命令序列、固定 RulesetBinding、初始 Snapshot / 显式 RNG 状态，不以 seed 单独承诺重放，不要求模型输出逐字一致或公开私有推理轨迹。

---

## 10. 校验规则与错误处理（MVP 的最低门槛）

| 编号 | 校验 | 预期失败行为 |
| --- | --- | --- |
| V01 | 目录/文件缺失、YAML 无法解析、非法额外字段 | 加载失败，定位文件和路径 |
| V02 | `adventure_id` / Schema 版本错误或不能解析 | 加载拒绝；不静默迁移 |
| V03 | 重复 ID / 悬空 Scene、Actor、Event、Object、Encounter 引用 | 加载拒绝 |
| V04 | 静态检查发现核心必经路径被确定阻断/非核心路径不可达 | 核心结构错误 invalid；非核心限制可 warnings 并要求作者审核，不证明剧情可玩性 |
| V05 | 非法/不匹配规则绑定、必要机制不支持 | invalid、阻止批准；仅非核心可选内容限制可 warnings，运行时仍不可假装支持 |
| V06 | Actor 控制权不匹配、NPC 读取未授权事实 | 拒绝提议/脱敏，零世界状态变化 |
| V07 | NPC 提议包含直接 HP/Slot/RNG 结果 | 拒绝，不进入世界事件 |
| V08 | 未提交/失败的检定却触发剧情奖励 | 不触发；保留失败原因 |
| V09 | Scene 重访、重复事件、重试命令 | 不重新初始化、不重复领奖励或消费资源 |
| V10 | 世界版本冲突 / 已提交但响应失败 | 返回冲突或可恢复回执，不重复执行 |
| V11 | 公共仓库包含受限来源内容/地图/原文 | 发布前检查失败；本地私有资料独立保存 |
| V12 | 关闭 Visual、World Builder、全部可选插画 | 完整文字游戏运行不受影响 |

加载前校验能发现结构问题；**不能**通过静态 Schema 校验宣称剧情必然可通关、NPC 绝不泄密、单人战斗平衡、魔法规则符合 SRD。这些仍需分别进行行为测试、独立规则 Oracle 和真实冒险验收。

### 10.1 公共合成 Fixture 的最低验收测试

以下为 [PROPOSED; NOT IMPLEMENTED] 验收目标；本轮仅更新文档，未执行运行时或故障注入测试。

- 可信主体使用两个不同创建 command_id 得到两个隔离 Session；同 (principal_id, command_id) 相同请求/并发/丢响应重试只返回原 Session，不同内容冲突拒绝。
- 离开/重访场景不会重置门状态、奖励或 NPC 的关键记忆。
- Sub-agent A 不能通过自己视图读取只属于 B/DM 的秘密。
- NPC 提出非法操作不会修改 State，也不能伪造 Rule Engine 结果。
- 同一 `command_id` 重试一次或多次，世界副作用仍只提交一次。
- 一次 Scene Event 的条件不满足时不触发，满足后仅触发其允许次数。
- 带 `check.resolved` 的事件只有在实际权威结果提交后才修改 Flag。
- Package 版本改变时，旧 Session 的恢复流程不能静默按新包重置。
- 一个无图像、无 World Builder 的端到端合成冒险可执行至结束。
- load_adventure_package 只批准完整 valid 结果；错误分类/可选限制 warnings、固定身份/绑定及来源元数据边界正确，不暴露半验证包。
- 多个完整 PC Templates 可选择，players[] 严格一项，可信控制关系验证；创建异常无半初始化 Session/重复幂等映射。
- Scene 重访/动态 Encounter 不复制 Session 级 NPC；combat.start 使用 NonCombatSnapshot，规则结果与 CombatState 建立同事务提交。
- 同命令世界/机械效果原子提交；已提交事件的后续命令在崩溃/重投下可恢复且不重复伤害/领奖/已提交骰点，无跨已提交事务原子性假象。

### 10.2 *First Blush* 的私有验收

以私有 `FIRST_BLUSH_MVP_REQUIREMENTS.md` 中已核对的场景需求为基准：导师/朋友互动、训练与真实遭遇、物品及机关、魔法对话谜题、定时威胁、独立技能挑战和结局存档。**这些是本地覆盖目标，不应把对应原文故事、角色设定、地图和实质性派生数据复制到公开 Fixture 中。** 需要为旧版 D&D 规则差异与 Solo Adaptation 分别附带人工审阅记录。

---

## 11. 仍待决定 / 不得让开发 Agent 擅自冻结

| 编号 | 问题 | MVP 默认提案 | 状态 |
| --- | --- | --- | --- |
| T01 | 文件格式 / Validator 技术 | YAML + 严格验证；Schema 设计独立于编程语言 | 待设计 |
| T02 | NPC/Monster `controller.kind` 默认值 | 重要 NPC 按需 `sub_agent`；普通怪物可使用确定性策略，但至少一次敌方 Sub-agent Intent 必须完成验收 | **产品决策未完全确认** |
| T03 | 内置完整 PC Templates 与未来外部导入 | 多模板只读供选择，机械属性规则验证，MVP 一玩家一 PC；无需外部构建服务 | [DECIDED]；外部导入 [OPEN] / 不实现 |
| T04 | Scene / Encounter 运行时所有权 | SM 原子创建入口、后续 Scene 按需一次初始化，支持动态 Encounter | [DECIDED]；具体字段 [PROPOSED; NOT IMPLEMENTED] |
| T05 | Rule Engine 的 Stateless Hazard / NPC 显式战斗 Intent Evaluation | 先验证公开接口，缺失则作为 MVP 集成阻塞项 | 必须技术验证 |
| T06 | 单人遭遇、非致命训练、旧版规则数据 | 独立人工裁定并追溯记录，不篡改骰点 | 待场景审阅 |
| T07 | 活跃战斗精确续玩 | MVP 仅承诺非战斗 Session 恢复；活跃战斗跨进程精确续玩在 MVP 之后 | 已确认范围 |
| T08 | 世界事件条件 AST 的精确编码与限制 | 固定少量 Operator，默认拒绝未知类型 | 待实现确认 |
| T09 | 来源及许可元数据的自动发布检查 | 首版可结合人工审查 + CI 中的限制路径检查 | 待设计 |
| T10 | World Builder 与 Visual Schema 未来如何扩展 | 只留 `schema_version` 与可选 Assets，不提前实现 | MVP 后 |
| T11 | AP-15 Actor / 系统来源的具体字段 | 按操作类型校验 Actor 已确认；Actor 行动必填，受信系统/世界事件操作须验证 principal / 机械来源 / 目标；source_ref / 来源权限编码待设计 | 原则 [DECIDED]；字段 [PROPOSED / OPEN] |
| T12 | combat.start / combat.create、rules.effect 与复杂编排/Effect Schema | 复用统一规则求值和单命令提交，可靠后续命令不虚构跨事务原子性；具体类型/存储须实施验证 | [OPEN] |

---

## 12. 进入实施阶段的门槛

此文件从 Draft 转为 Approved 前，至少应完成：

1. 确认本 Schema 的最小字段和 Source/Secrets 边界可表示私有 *First Blush* 需求矩阵中的所有 **MVP Core** 场景，不要求记录作品原文。
2. 建立一个**公开可提交的原创合成 Fixture**，通过引用、条件、幂等与权限校验。
3. 明确 Rule Engine 已有接口与缺失接口，特别是 NPC 显式 Combat Intent 和受控 Hazard 结算；给出真正的 MVP 阻塞项。
4. 确认普通 Monster 是否强制 Sub-agent；明确 MVP 至少一条敌方 NPC Sub-agent 战斗验证链。
5. 冻结 `MODULE_CONTRACTS.md` 中的 Session Commands、RuleEvaluationResult + State Machine CommandReceipt、World Events 和 State Version 边界，避免两套权威状态。

**实施顺序建议**：先实现统一 `load_adventure_package`（内部含验证）+ SM 原子 Session Creation / Scene Persistence 的最小闭环，再加入 NPC Knowledge Projection、World Events/Skill Challenges，最后接入经审核的规则入口与完整 Golden Adventure。未通过一次可重访且可恢复的端到端测试前，不应扩成通用世界模拟系统。
