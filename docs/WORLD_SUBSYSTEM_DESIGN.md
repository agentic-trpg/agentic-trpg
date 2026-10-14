# Agentic TRPG — World Subsystem Design

> **版本**：v0.1 / Draft；**日期**：2026-10-15
>
> **规范关系**：[Module Contracts](./MODULE_CONTRACTS.md) v0.15 §0.3 / §0.5–§0.6 为最高职责规范；本文细化 World 候选能力。配套 [State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md) v0.17、[Game Core Evolution Plan](./GAME_CORE_EVOLUTION_PLAN.md) v0.4、[Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) v0.11。
>
> **状态**：职责/复用方向 `[DECIDED]`；组件和字段 `[PROPOSED; OPEN]`；超出 MC §1.2 受限实现的能力是目标设计，不能宣称已支持。本文不冻结 SQL Schema、跨模块消息或公共操作集合；仅修改总控文档。

## 1. 基线、范围与规则依据

本设计使用 **D&D 2024 修订规则：PHB 2024、DMG 2024、MM 2025、SRD 5.2.1**。这里的组件、字段和职责是项目工程设计，**不是官方数据库规范，也不宣称覆盖全部规则书**。官方版本依据：[PHB 2024](https://www.dndbeyond.com/posts/1810-updates-in-the-players-handbook-2024)、[DMG 2024](https://wpn.wizards.com/en/products/2024-dungeon-masters-guide)、[MM 2025](https://www.dndbeyond.com/posts/1913-updates-in-the-monster-manual-2025)、[SRD 5.2.1 发布与下载](https://www.dndbeyond.com/srd)。2026-10-15 核对公开版本信息及下列 SRD 条目；未逐章核对三本完整规则书，不从版本信息推断具体机制支持。

| 设计关注点 | 本次核对的公开依据 | 使用边界 |
|---|---|---|
| 对象互动与战斗时序 | [SRD 5.2.1](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=11) p.11–12 Interacting with Objects、p.13–14 Combat | 对象互动需要按情境处理；本文不统一规定开门/取物/撬锁都免费或都耗 Action，具体成本/资格由 RE 的受支持规则或显式裁决决定 |
| 光照与遮蔽 | 同一 [SRD](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=11) p.11 Vision and Light，p.15 Cover | 区分视觉遮蔽、遮挡和机械 Cover；不把阻挡移动等同阻挡所有感官，具体感官例外逐项待确认 |
| 物体受损 | 同一 [SRD](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=180) p.180 Damage Threshold | 阈值是有条件适用的规则概念，不能给所有物体默认加阈值；材质 AC/HP 表、免疫/抗性和破坏后果的具体取值/映射 **待确认** |
| 环境与陷阱 | 同一 [SRD](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=195) p.195 Environmental Effects、p.199 Traps | 仅确认可供逐项映射的条目；DC、触发/解除、伤害和时序未在本文列为已核实规则 |
| 持续魔法区域 | SRD Spells 与具体已启用法术条目 | 本次不规定统一法术公式；区域、移动、进入/离开/回合触发、集中与到期须逐法术核实并由 RE 执行，**待确认** |

World 覆盖世界时间、场景、空间/地形/障碍、基础对象、位置关系、物体耐久、开合/通路、锁具、容器/资源、光源/遮蔽、环境、陷阱/危险、隐藏与感官来源、通用交互、持续魔法区域的建模方向。**组件目录不是当前 MVP 全部完成清单**：按 MVP 已选场景启用最小能力，缺口明确拒绝/记录。车辆、荒野旅行、巢穴、位面和 Bastion 为 **后续扩展**，不成为当前 MVP 门槛，不因此扩大内容或引入完整物理模拟。

### 1.1 当前实现与目标的区别

实际 checkout / SHA / 脏工作区和静态证据统一见 [MC §1.2](./MODULE_CONTRACTS.md#12-2026-10-15-sm-当前实现核对静态代码未运行测试)。本批未运行 SM、RE 或真实模型测试。

| 能力 | 本次确认的基础 | 仍为目标/未核实范围 |
|---|---|---|
| 时间、场景、空间 | game_tick、一次实例化/重访、网格位置、障碍与通路查询 | 日历/天气/任意空间尺度及完整时间驱动后果未核实 |
| 对象、门锁、物品 | WorldFacts / WorldHandler、共享门的开合及通路关系、持有公开凭据开锁、便携实例地面/携带切换与库存投影 | 可选能力的完整组合模型、通用耐久破坏、容器嵌套、附着、撬锁/密码未核实为受支持操作 |
| 编排与存储 | StateMachine 显式装配部分组件，共享 SqliteStore；Navigation / Activity 的非战斗执行；受限 CombatHandler | A1 / A2 部分实现；战斗世界互动/移动扩展及全部 Mixin 退出未完成 |
| 感知/效果 | 事件阶段取证、已有感知机制、受限 PackageEffects 和角色机械效果组件 | 通用 World 感官/环境/陷阱组件与持续魔法区域集成未核实；不据本文宣布 Episode / Continuation 已实现 |

## 2. 职责与依赖 `[DECIDED]`

StateMachine 是统一 API 和组件装配入口；WorldHandler / Service 编排世界操作，WorldFacts 读写所属事实，导航、时间、空间查询、规则适配与事件取证等按需作为 Supporting Components。通过显式依赖引用 CharacterFacts、Activity、CombatRecords、Effects 和共享 SqliteStore，不给每个对象类型配置一个 Handler，不机械套用全部层次，不强制 ECS。

**WorldFacts** 管场景、空间、对象、物体耐久、门锁、容器、物品实际位置关系及世界时钟。**CharacterFacts / 角色机械组件** 管唯一实际角色位置、HP、资源和装备。**CombatRecords** 管战斗运行记录；**Activity** 管进行中的活动与执行进度；**Effects** 管持续效果及其自身进度/时钟。Facts / Records 是领域读写组件，实际数据保存在 SQLite。Handler 不是另一份事实仓库，规则判断/计算归 RE。

World 的对象位置查询可以解析携带者的实际角色位置，不能复制一份可写角色坐标。Effects 区域引用 World 空间，World 的光照/阻挡等查询消费相关效果；效果实例、集中与到期不在 World 再存一套。物体耐久与角色 HP 分责，Creature/Actor 的伤害不能因使用“对象”统称转到 World。

### 2.1 身份、位置关系与库存

沿用现有 `session_id`、`scene_id`、`actor_id`、`object_id`，便携 `instance_id` 与 `objects.object_id` 是同一实例身份；不按名字另建 WorldEntity / InventoryItem 目录。模板绑定沿用 Package / 数据修订，新增关系键须先核对已有字段，本文字段拼写仅作候选。

当前便携物品落地为 `scene_id + cell`，携带为 `carrier_id`；位置互斥且引用有效。目标扩展为置于容器或附着于对象时，同一物品仍只有一个直接实际位置关系，容纳/附着链不得成环；沿父关系解析实际空间。装备是角色机械绑定，不能自动等同位置；被装备实例仍须属于合法持有关系，取放应维护或拒绝无法安全解除的绑定。

`WorldFacts.transfer_item → CharacterFacts.project_item_transfer` 在同事务更新 World 位置、机械 `InventoryState.entries` 和 carried-slug 投影，并以 `validate_portable_inventory` 校验完整便携子集，再按角色投影。**持久化的库存投影不是另一份可独立改写的物品归属权威**。当前 `item_json` 含 item_slug、quantity、charges_remaining_per_unit 等，转移不能重置数量/充能或丢失非便携条目；相关规则消耗须按受控机械结果共同更新。slug 装备不能无歧义识别实例、活动效果/施法材料绑定等当前限制保留。容器内可访问性、递归携带重量、资源耗用与统一实例装备协议 `[OPEN]`。

### 2.2 客观世界与认知

墙体遮挡、暗门的物理伪装、锁的客观机制和感官源存在性属于 World。谁发现暗门、听到了什么、知道密码或相信门后有宝物，属于 Perception / Observation / Knowledge / NPC Cognition；不能用 `discovered_by` 一类世界对象字段替代角色认知记录。World 可保存受控机制引用，但密码知识、秘密与发现结果只能通过授权视图/证据进入角色上下文。

光源/声音来源、通路、物理 Cover、视觉遮蔽、声音传播分别建模/查询，不能用一个 `hidden` 或 `blocks_passage` 同时解释所有规则。角色感官能力和机械 Conditions 来自角色/Effects；Perception 按实际事件阶段证据判断。World 提供来源和客观环境，不能直接写“所有同场景 NPC 已发现”。

## 3. 可选能力组合 `[DECIDED; PROPOSED]`

对象只装配需要的能力：**门 = 基础对象 + 位置 + 可选耐久 + 开合 + 可选锁具 + 通路关联**；**箱子 = 基础对象 + 位置 + 可选耐久 + 开合 + 可选锁具 + 容器**。箱子可没有锁，门可不可破坏，光源可附着于任意合适对象；能力缺失不伪造默认行为。木门、铁门以模板材质/规则参数区分，共用能力操作逻辑，不分别实现木门/铁门处理器。

以下按组件列候选字段及用途。**T = 模板配置**（固定定义/初始值）；**S = 持久实例状态**（只由所属接口写）；**R = 关联**（引用同 Session 已有身份/来源）；**D = 派生查询**（可缓存，不能独立修改）。表中全部字段 `[PROPOSED; OPEN]`；与现有字段同义时复用现有结构，新增拼写不意味着新增 SQL 列或冻结跨模块协议。R 可持久化，但须指定唯一关系负责人；D 如物化，须有失效/一致性规则。

| 组件 / 用途 | T：模板配置候选 | S：持久实例候选 | R：关联候选 | D：派生查询候选 |
|---|---|---|---|---|
| 世界时间：推进共同时间 | `time_unit`、`initial_tick`、可选 `calendar_ref`，定义刻度/显示；不预设战斗秒数 | 复用 `game_tick`，保存唯一已提交时间 | 复用 `session_id`；活动/效果引用同一时基 | 日期/昼夜、下一到期点；不另开可写探索/战斗时钟 |
| 场景：实例化与边界 | 复用 Scene 定义、初始 flags、空间配置，提供首次基线 | 复用 scene_instances 的 flags / visited_count，保留回访后果 | `scene_id`、Package 版本/定义引用 | 当前在场角色/对象与授权出口；不按静态 actor_ids 重生角色 |
| 空间 / 地形 / 障碍：导航和机械输入 | 复用 grid、blocked_cells、地形定义；候选 `terrain_ref` / `geometry_ref` 描述成本/形状 | 候选地形覆盖/障碍实例变化，保存实际改变 | scene_id、对象/区域与 passage 引用 | 可通行边、距离、占用、LoS / Cover 输入；规则成本由 RE 算 |
| 基础对象：身份与能力装配 | 复用对象定义；候选 `template_ref`、`capabilities`、`material_ref` 表达可支持能力/材质 | 复用 objects 实例身份/普通 state；候选启用/失效状态 | session_id / object_id、Package 定义 | 可用能力集合、授权描述；不按名称推断新能力 |
| 位置 / 携带 / 容纳 / 附着：实际位置 | 复用 initial_cell / initial_owner_id；候选允许关系类型 | 复用 scene_id / cell / carrier_id；候选容纳/附着的互斥关系状态 | `container_id`、`attached_to_id`、候选局部锚点；复用 actor/object 身份 | 解析后的实际场景/坐标、直接持有者/祖先链；不存独立库存 owner |
| 物体耐久：受损与破坏 | 候选 `max_hp`、`ac_ref`、可选 `damage_threshold`、`damage_profile_ref`，指向经核实规则/裁决 | 候选 `current_hp`、`damage_state`，保存实际损坏 | object_id、规则来源/已提交结算关联 | 是否仍能承重/阻挡/使用；破坏并不默认删除身份或抹掉历史 |
| 开合 / 通路：状态影响世界连接 | 复用 open/closed 初始 state、passages / endpoints；候选允许开合政策 | 复用 objects.state；候选卡住/破损状态，不把 unlocked 等同 open | 复用 `door_object_id`、`passage_id`、两侧 scene/standing_cell/threshold_cell | 当前通路可用性、双侧交互可达性；不为门两侧各保存一份门状态 |
| 锁具：控制合法开启条件 | 复用 `initial_locked`、`policy`、`credential_instance_ids`；候选检定/密码机制引用 | 复用 door_locks.locked；候选损坏/禁用状态 | object_id、door_credentials 与物品实例；未来秘密机制受控引用 | 当前是否有合法开锁路径；不从查询泄漏密码、钥匙秘密或未知目标 |
| 容器 / 物资资源：容纳与有限存量 | 候选 `capacity_ref`、`accepts_ref`、`resource_kind`、`initial_quantity`，约束内容/计量 | 候选容器自身状态、未实体化物资的 `remaining_quantity`；实体物品不再计一份可写数量 | 容纳关系反向查询；实物实例/补给来源引用 | 内容列表、剩余容量/可访问性/合计重量；角色资源池留在 Character 机械组件 |
| 光源：提供客观照明 | 候选 `light_profile_ref`、`fuel_policy_ref`，定义范围/消耗来源 | 候选 `enabled`、实际燃料存量；有物品充能时引用原实例余额 | 来源 object_id / actor_id / effect_id、空间锚点 | 当前受照区域与强度；燃料/充能不在两处独立扣减 |
| 遮蔽 / 遮挡：按渠道描述物理影响 | 候选 `occlusion_profile_ref`、`cover_geometry_ref`、`channel_mask`，分别表达视线/声音/机械遮掩 | 候选启用状态或几何变化，必要时直接派生自门/障碍状态 | 对象/地形/效果来源及空间 | 各渠道连通、视觉遮蔽与 Cover 候选；不直接得出角色已察觉 |
| 环境：持续客观条件 | 候选 `environment_profile_ref`、作用域与规则引用，表达天气/温度/水体等 | 候选当前强度/状态、已提交变化时间 | scene / region、来源效果与世界时间 | 某位置适用环境集合；机械伤害/豁免由 RE 算，非全物理模拟 |
| 陷阱 / 危险：受控触发与后果 | 候选 `trigger_ref`、`resolution_ref`、`reset_policy`，绑定已支持规则/包声明 | 候选 armed / disabled / spent、剩余使用次数与触发采用记录 | 对象/区域、触发 Event、后续稳定 command_id | 可触发候选/受影响对象；发现/识破知识不存入陷阱状态 |
| 隐藏与感官来源：提供察觉依据 | 候选 `concealment_ref`、`sensory_profile_ref`，描述物理伪装与光/声等源 | 候选源启停、伪装实际状态及变化时间 | source object/actor/effect、空间与已提交阶段 | 供 Signals / Scope Discovery 的客观来源和环境；发现结果由既有感知组件管理 |
| 通用交互：按能力复用操作 | 候选 `interaction_refs`、支持操作/前提政策、规则/裁决引用 | 通常不复制事实；确有需要仅存交互自身冷却/使用进度 | actor、目标能力、Activity / Command / Event 关联 | 当前授权可用性；query 不支付资源，执行时重验 |
| 持续魔法区域：空间与效果协作 | 候选形状/锚定/传播政策与具体法术规则引用 | World 仅保存必要空间锚定变化；持续效果状态/进度由 Effects 持有 | effect_id、source/target、scene/anchor、集中来源 | 当前覆盖与进入/离开候选；RE 计算触发/结算，不能另存一份效果时钟 |

**字段演进顺序：** 先为一个已选场景核对定义/实例/关联/查询消费者，再提出最小字段与操作；优先复用现有 objects、passages、door_locks、door_credentials、portable_items、机械组件与活动结构。WorldTime / Position 等是逻辑称呼，不要求建同名表。不得因 `location` / `position`、`item_id` / `instance_id` 命名差异重复建设；具体 SQL、约束、迁移、版本和跨模块协议必须在实现切片另行评审。

## 4. 探索、战斗与底层互动 `[DECIDED]`

**探索移动：** `StateMachine → Navigation / Activity → WorldHandler → CharacterFacts.move`，World 提供空间/通路/门/障碍事实，ActivityRecords 只保存目标与进度。当前每步重验，活跃战斗拒绝探索执行；世界时间是否随某活动推进由具体受支持政策决定。

**战斗移动目标：** `StateMachine → CombatHandler → RE → CharacterFacts + CombatRecords + 相关领域共同提交`。从实际世界位置组装战斗空间投影，RE 计算移动资格/成本、触发与反应，结果落回唯一实际角色位置及相关记录。当前 `_current_cells` 使用同场景网格坐标；未来子地图原点/尺度/zone、跨场景与动态障碍映射保持 OPEN。无法表达的范围/障碍显式不支持；战后冻结记录只供审计，不能反向覆盖角色位置。

**共享互动目标：** 开门、解锁、取放、破坏障碍按能力调用共同领域操作。探索入口执行适用授权、可达性、凭据/活动约束及需要的 RE 检定；战斗入口额外经 RE 协调行动资格、行动资源、时序、触发与反应。Handler 组织顺序、阶段取证和提交，不能自定规则公式。门/箱/容器共享开合和锁具能力，不复制对象事实或取放权威。

**当前限制是实施边界：** `_world_operation_capability` 拒绝活跃战斗的非战斗命令；`_spatial_combat_guard` 拒绝部分动态障碍/关闭通路门；物品/锁具还有公开性、凭据、装备、效果/活动等限制。复用须先设计受控战斗执行上下文及 Delta 适配，并逐项证明原有限制仍正确或已有明确替代；不得删除 guard 或直接调用内部 `_operate*` 作为“支持战斗互动”。撬锁、强行破门、箱内取物只是目标例子，不是当前支持声明。

## 5. 事务、尝试结果与阶段证据 `[DECIDED]`

各 Facts / Records 使用调用方的共享 SQLite 事务；Handler / 提交设施组织边界，组件不自行 COMMIT。一次不可分割的互动应共同提交对象/角色/活动/战斗/效果变化、资源结算、RNG、触发采用记录、事件及实际阶段证据、Receipt / 可靠工作。求值、LLM、外部 I/O 与等待选择在写锁外，提交前重验权限、版本与前提。失败回滚还须防止缓存/已有引用泄漏候选状态。

| 情况 | 权威处理 | 反馈/重试 |
|---|---|---|
| 非法 / 越权 / 不支持的命令 | 不发生未获准行动、不消耗未获准资源、不发布动作事实；按已有协议保存允许的拒绝回执 | 授权范围内 rejected / unsupported 原因；不得编造骰点失败 |
| 版本 / 原值冲突 | 未提交变化和 RNG 不生效 | 原命令查询回执；刷新并改变内容/版本需新 command_id |
| 合法尝试成功或结果失败 | RE 或受控非机械政策确定实际后果；合法失败**可能仍消耗**行动、时间、工具/资源并产生可观察动作，必要变化原子提交 | 用已提交结果叙述；accepted 不保证任务目标成功，不能把结果失败统一回滚为未尝试 |
| 存储/提交故障或响应未知 | 失败事务整体回滚；未知先查原回执 | 防止重复扣费/重掷，不把传输失败当角色尝试失败 |

实际阶段捕获 Evidence：例如取物前的地面源位置、放下后的实际源位置，或破坏前后的可观察分支，不能在操作全部结束后用当前坐标补造先前视听。可信阶段可先缓冲，最终与对应 Event / Signals / 可靠工作共同提交；缺失阶段明确记录缺口，不能让 JEV 猜历史。

沿用 MC §7 的 **Event / Episode / Observation** 职责、事件时证据、Outbox、游标与既有 NPC EVA/Knowledge 管线，不新增世界专属感知队列/记忆体系。战斗整段 Episode 的目标聚合只使用已授权阶段，不能泄漏未察觉内容。提交后需独立机械命令的后果按现有稳定 command_id 可靠交接，不宣称两个已提交操作可一起回滚；异步感知/认知处理仍在各自可靠事务完成。

## 6. 后续落实与修订关系

唯一架构待办登记沿用 [MC §13](./MODULE_CONTRACTS.md#13-尚需显式批准或验证的开放问题) 的 **A1 / A2、C-18 / C-19、C-25–C-27**，实现验收复用演进计划 §8.1 的 DS-01–DS-07。本文不建平行 Backlog，不把完整组件目录变成强制 MVP 工程批次。

仍待确认：最小场景所需能力与规则来源、坐标/战斗投影映射、装备实例与容器可访问性、物体耐久/破坏及连带后果、锁具检定/密码授权、时间单位/推进策略、环境/陷阱/区域逐规则 Delta、支持组件依赖与故障验证。新增字段/规则不能由本草案直接视作运行能力。

本草案细化 MC v0.14 的领域所有权决定，不撤销其单一事实权威、共享提交或 Host / RE 边界；与旧“Character / World Object 合并责任”表述冲突时，采用 MC v0.15 §0.3。历史 ADR / 决策登记及历史实现快照保留，不另建 ADR 体系；本次没有运行实现、Schema 迁移、规则依赖升级或全规则书覆盖验收。
