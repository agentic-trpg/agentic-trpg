# Agentic TRPG — MVP Scope Specification

> **文档状态：Draft / 部分产品决策已确认，其余待评审**  
> **版本：v0.3**  
> **初稿日期：2026-10-09**  
> **文档级别：项目级（跨 Repository）**  
> **建议仓库位置：** `agentic-trpg/agentic-trpg/docs/MVP_SCOPE.md`  
> **适用范围：** Agent DM（包括 NPC Sub-agent）、State Machine、Rule Engine；Visual Presentation 作为 MVP 后续阶段

## 0. 文档定位与决策状态

本文件定义 Agentic TRPG **首个可实际游玩的端到端 MVP** 的产品边界、游戏场景、跨模块职责与验收目标。它**不是** D&D SRD 的完整实现计划，也不替代各模块的技术设计、规则覆盖矩阵和 Backlog。

为避免在需求尚未讨论时过早锁定技术路线，使用以下标记：

- **[已确认]**：项目已经明确的架构方向或目标。
- **[建议]**：本初稿提出的 MVP 默认范围；需要项目负责人评审后才能成为正式需求。
- **[待决策]**：会显著影响实现范围、成本或系统接口的问题；不能由开发 Agent 擅自决定。

> **治理原则：** 当前文件中的「建议」不等于批准。只有经过明确确认并在决策记录中更新状态的条目，才能成为开发任务的强制验收条件。

### 0.1 已确认的产品决定（2026-10-09）

- **[已确认] 首版体验：** 用一个完整可玩的 D&D 小型冒险验证端到端系统，覆盖剧情对话、探索、检定、战斗、休息和任务推进；不追求全 SRD 覆盖或无限开放世界。
- **[已确认] 玩家模式：** 一名真人玩家**只直接控制一名玩家角色（PC）**。
- **[已确认] 首版采用单人剧本、没有 AI 队友：** MVP 不提供常驻 NPC 同伴、招募入队或 AI 队友战斗控制系统；不将“1 PC + AI 队友”作为验收场景。普通剧情 NPC 仍可以出场、对话、冲突，NPC 的偶发非战斗帮助不等于正式的队友系统。
- **[已确认] NPC 控制方式：** 需要自主对话、做出选择、采取行动的 **NPC（包括对话角色和敌对角色）由 NPC Sub-agent 控制**，不由 Agent DM 直接替每个 NPC 生成个人决策。NPC Sub-agent 是 Agent DM 模块下可独立调用、具角色身份和独立上下文的执行单元；**不新增第五个顶层产品模块**。
- **[已确认] Agent DM 职责：** 主持故事、理解玩家意图、决定场景推进与 GM 语义裁决、协调 NPC Sub-agent；不得把“协调 NPC”变成“代 NPC 作出所有行动决定”。
- **[已确认] 交互方式：** MVP 以文字、自然语言交互为核心。简单文字界面足以满足演示；可选根据 DM 的描述生成插画。
- **[已确认] 视觉分期：** 与 Rule Engine、State Machine 深度联动的地图、Token、动画、场景渲染及游戏世界可视化**不属于 MVP 验收条件**，在 MVP 后单独推进。

**重要架构边界：** “没有战术画面”不等于“没有权威战术状态”；“NPC Sub-agent 有自主决策能力”不等于它可以修改世界状态、决定骰点或绕过 Rule Engine；“一个 NPC 一个独立角色上下文”也**不等于**必须为每个 NPC 常驻部署独立模型或进程。

## 1. 项目愿景与 MVP 定义

### 1.1 项目愿景

**[已确认]** Agentic TRPG 是一个模块化、可扩展、以 AI Game Master（Agent DM）驱动的 TRPG 平台。长期规划包含 Rule Engine、State Machine、Agent DM、Visual Presentation 四个相互独立的模块。**首个 MVP 仅要求前三个核心模块协同工作，并由轻量文字交互入口提供游玩体验。** Visual Presentation 在 MVP 之后建设；可选插画不构成新的权威状态系统。

核心原则：**能由确定性程序可靠处理的规则计算，不交给 LLM 自行猜测；需要叙事、语义理解和开放式裁决的事情，不强行塞进 Rule Engine。**

### 1.2 MVP 的成功定义

**[已确认的产品方向；细节仍待验收设计]** 首个 MVP 的成功标准不是实现全部 SRD，而是：

> **一名真人玩家只控制一名 PC、没有 AI 队友**，在 Agent DM 主持下通过自然语言完成一段 D&D 单人冒险，包含 **NPC 对话、探索、检定、危险/陷阱、至少一次完整战斗、战利品或任务结果、休息/资源恢复以及场景转换**。对话 NPC 和战斗敌人的实际决策通过有独立角色上下文的 **NPC Sub-agent** 提出；Agent DM 负责主持、协调与叙述。State Machine 管理世界/会话权威，Rule Engine 管理已支持的机械计算和战斗状态。所有越权或不支持的规则必须有明确反馈。

MVP 必须是**可反复运行的文字版 Vertical Slice**，不是若干模块各自拥有 API 的集合。关闭图片生成后仍应完整可玩；**不以 NPC 同伴系统替代 NPC Sub-agent 的独立性验证**。

### 1.3 首版产品基线（已确认与候选项分列）

| 维度 | MVP 产品范围 | 决策状态 |
| --- | --- | --- |
| 首个 RuleSet | 优先以 D&D 2024 / 可合法使用的 SRD 5.2.1 为内容基线；不将其他模块设计为 D&D 专用 | [建议] |
| 冒险类型 | 单人叙事探索、NPC 互动、检定、具备战术规则的战斗、休息及任务推进，组成完整小型冒险 | [已确认] |
| 玩家模式 | **一名真人玩家，只直接控制一名 PC** | [已确认] |
| AI 队友 / 同伴 | **首版没有 AI 队友**；不做招募、组队控制、队友战斗管理及同伴专属玩法 | [已确认：不纳入 MVP] |
| NPC 控制 | **NPC Sub-agent 控制 NPC 的对话与行为选择**；含非战斗 NPC 和敌方 Actor | [已确认] |
| NPC Sub-agent 的执行形态 | 角色身份/知识/目标与记忆隔离；按需唤起，可复用底层 LLM 与工作进程 | [已确认：逻辑隔离；实现方式待设计] |
| 主要交互方式 | 文字/自然语言；规则结果和重要状态以文字呈现 | [已确认] |
| Visual Presentation | 不要求可交互战术画面、Token 或画面与规则/世界状态的深度绑定 | [已确认：MVP 后] |
| AI 场景插画 | 可选、非阻塞增强，不参与规则裁决 | [已确认：可选] |
| 验收等级 | 以 1–5 级常见能力作为重点候选范围；不删除已有高等级实现 | [建议] |
| 角色准备 | 至少允许载入预设玩家角色；完整创建器范围另行决定 | [建议] |
| 战斗空间 | Engine 内部维持权威 2D 网格/位置、范围及掩护计算；无需渲染地图 | [建议] |
| 单人战斗平衡 | 选用可由一名 PC 独自面对的遭遇，必须保留正常失败、死亡和撤退可能，不通过 DM 任意改骰“保护剧情” | [建议] |
| 运行形态 | 本地/单实例优先；Agent 模型、调用成本、并发规模另议 | [待决策] |
| 冒险内容 | 先用一段可复现的小型单人冒险验收；不要求无限开放世界 | [已确认] |

**边界说明：** 不开发 AI 队友系统，不妨碍故事中的商人、守卫、委托人、盗匪和怪物出现，也不妨碍 NPC 做出不利于玩家、并非 DM 预定的选择。NPC 的身份与会话状态必须稳定；NPC Sub-agent 的文本输出与内部 LLM 推断不构成可重放的规则结果。

## 2. 四个模块及权威边界

MVP 的**顶层核心模块仍只有 Agent DM、State Machine、Rule Engine，加一个最低限度的文字交互入口**。**NPC Sub-agent 是 Agent DM 模块的内部多智能体能力，而非新增第五个顶层 Repository 的强制要求。** Visual Presentation 属于 MVP 后的开发阶段。

| 模块 | 核心职责 | 权威范围 | 不应承担的职责 | MVP 地位 |
| --- | --- | --- | --- | --- |
| **Agent DM** | 解释玩家意图、主持场景、安排 NPC Sub-agent 调用、GM 难度/线索和叙事裁决、将已提交结果叙述给玩家 | **场景组织与语义裁决** | 直接代替 NPC Sub-agent 做人物决策；伪造命中/骰点、HP 或 Rule Engine 结果 | **核心** |
| **NPC Sub-agent**（属于 Agent DM） | 基于 NPC 自身角色设定、当前知识、目标与记忆决定说什么、做什么；给出对话或结构化行动提议 | **角色层面的决策提议，不具备权威状态写入权限** | 查看角色不应知道的秘密；写 HP/Slot/世界状态；自行确认机械动作成功 | **核心内部能力** |
| **State Machine** | Session、Scene、任务、世界实体、时间、NPC 记忆/关系、Actor 控制权限、持久化及协调结果提交 | **世界、会话与角色背景事实** | 再实现攻击、伤害、行动经济；直接把 NPC 提议当成已提交状态 | **核心** |
| **Rule Engine** | Typed RuleSet、规则合法性、骰点、攻击/豁免、行动经济、战斗机械状态转换及事件 | **明确支持的机械规则与战斗运行态**，与发起提议的 Agent 无关 | 扮演 NPC、决定 NPC 的动机、管理剧情与完整世界 | **核心** |
| **Visual Presentation** | 将来的地图、Token、动画与场景呈现 | **只拥有展示层状态** | 直接决定伤害、HP、位置或合法性 | **MVP 后** |

### 2.1 状态所有权原则

**[已确认的目标原则] 一份权威状态只能有一个计算/写入所有者。**

- 战斗中的 HP、临时 HP、Condition、行动预算、集中、持续效果、战斗位置及 RNG：由 **Rule Engine** 负责裁决；玩家 PC 与敌方 NPC 走相同的规则正确性标准。
- Session、Scene、任务、NPC 身份、已知事实、目标、人物关系、持久化记忆、场景物体、控制权限和世界时间：由 **State Machine** 保存或管理权威版本。
- NPC Sub-agent 只接收经过权限/知识筛选的角色视角上下文；做出角色决定，并输出**待验证**的对话或行动意图。Sub-agent 不能直接写入世界数据，也不能自行宣告命中、伤害或资源消耗。
- Agent DM 对 NPC 行动进行**世界可行性与规则执行协调**，负责 GM 裁决和对外叙事；不能任意覆盖 NPC Sub-agent 的人物决策，仅因剧情想要某种结果就替其发言或作弊改骰。
- 战斗结束及其他明确同步时点，State Machine 根据 **Rule Engine 已提交的 Event/Result** 写回世界状态；不得从 DM/NPC 的自由文本推断机械资源变化。
- 可选图片及文字展示不属于权威状态来源。

**[待决策]** 跨场景 Effect、库存装备、NPC 记忆的精简/冲突处理以及活跃战斗恢复的最终契约由后续 `MODULE_CONTRACTS.md` 设计。

### 2.2 Actor 控制权与权限

| Actor / 操作类别 | 决策者 | 权限与事实检查 | 机械裁决 |
| --- | --- | --- | --- |
| 玩家的唯一 PC | **真人玩家**；Agent DM 负责把语言映射为候选 Intent 和请求必要选择 | State Machine / Host | Rule Engine |
| 非战斗 NPC（委托人、商人、证人等） | **对应 NPC Sub-agent**，在其知道的世界事实及目标范围内自主回应 | State Machine / Host；DM 协调场景 | 需要机械检定时交由 Rule Engine |
| 敌方 NPC、Monster（战斗中） | **对应 NPC Sub-agent** 提出战术行动或反应提议 | State Machine / Host 校验 actor、回合、受控信息 | Rule Engine；不得直接写入战斗状态 |
| 常驻 AI 队友 / 可招募同伴 | **MVP 不适用** | — | — |

- 玩家始终只控制自己的 PC。NPC 即便接受了玩家的请求，也应由自己的 Sub-agent 根据角色目标和知识决定回应，而非将玩家的话直接视为 NPC Action。
- Agent DM 可决定场景中出现哪些角色、何时轮到哪个角色与玩家交互，但 NPC 自身的发言、意图和战术选择应交给相应 Sub-agent。
- Rule Engine 不应因 NPC 是 LLM 控制便给予免费攻击、无成本施法或自动成功；Actor 控制权校验应在外围 API/Host 进行。
- NPC Sub-agent 可以提议不合法的动作；系统应向它反馈结构化拒绝，并允许有限次数的重新选择，而不是绕过规则强制成功。
- **[边界]** 不要求 NPC 在玩家不在场时永久后台自主运行；不要求 NPC 之间开展无限自动对话或形成独立社会模拟。

### 2.3 NPC Sub-agent 的 MVP 最小执行模型

**目标是 NPC 决策逻辑独立，而不是为每一个 NPC 常驻运行一个昂贵的模型进程。**

1. **稳定身份与隔离上下文：** 每个 NPC 有唯一 `npc_id`，自己的角色设定、动机、可见事实、关系和必要记忆。角色上下文不与其他 NPC 混用。
2. **事件驱动、按需调用：** 仅在玩家与该 NPC 交互、NPC 需要做关键选择或轮到该 NPC 战斗行动时唤起其 Sub-agent；空闲角色不消耗持续推理资源。
3. **输入受限：** State Machine/Agent DM 提供经过筛选的角色视角 Snapshot、允许的行为范围与必要的近期事件；NPC 不直接获得世界全部隐藏信息或其他 NPC 的私人思考。
4. **输出结构化：** 普通对话产生 `NPCDialogueProposal`（表述、意图、必要的世界行动提议）；战斗产生 `NPCActionIntent`（actor、动作、目标/能力选择及必要参数）；字段名称只是产品级示例，最终 schema 待设计。
5. **授权与提交分离：** DM/State Machine 校验世界交互；需要规则效果的行动交 Rule Engine 检查并执行；只有经过权威提交的结果进入长期世界状态。
6. **记忆持续：** 关键 NPC 能在玩家再次见面时记得先前重要互动、承诺或冲突，存储由 State Machine 负责，Sub-agent 消费角色可知的摘要。
7. **有限交互循环：** 明确每次行动的模型调用预算、拒绝重试上限与超时行为；不得出现 NPC 无限自发循环或调用风暴。具体数字待决策。
8. **可重放性：** 保存已提交的 NPC 意图及其权威结果；**不要求**相同种子下 LLM 每次生成完全相同的话或选择。

**[待设计的关键接口]** 现有 Rule Engine `submit_player_intent` 是玩家行动入口，而 `advance_monster_turn` 具有内置怪物动作选择。要让**NPC Sub-agent 真正决定敌人的行动**，必须核实并在必要时补齐**由 Host 授权的 NPC/Monster 显式 Intent 公共执行接口**，复用 Engine 的行动预算、Recharge、Multiattack、Reaction、状态与失败回滚，不能私自操作 `_LiveCombat` 或假借 PC 身份。

### 2.4 目标交互流程（逻辑模型，非固定网络拓扑）

```text
玩家（唯一 PC） ──自然语言──> Agent DM（主持者/协调器）
                                    |
                                    +──场景与事实查询──> State Machine
                                    |
                                    +──需要 NPC 决策时──> NPC Sub-agent [npc_id]
                                    |                       |
                                    |                 对话 / 待验证 Action
                                    |                       |
                                    <───────────────────────+
                                    |
                                    +──世界操作────────────> State Machine 授权/提交
                                    |
                                    +──机械 Intent─────────> Rule Engine
                                    |                         |
                                    <──────已提交 Events / Result ─────────+
                                    |
                              用权威结果叙述、推动 Scene
                                    |
                                    v
                                  文字界面
                    （可选图像只读叙事，不写入游戏状态）
```

该图表示责任和信任边界，而不是强制把 Sub-agent、Agent DM、State Machine、Rule Engine 分别部署成服务。单一 LLM 可以在不同隔离上下文下承担不同 NPC 角色，但 NPC 必须通过独立 Sub-agent 调用与输出契约作决定，不能退化为 DM 对所有角色的直接代言。

## 3. MVP 游戏场景目录（Gameplay Scenarios）

以下根据已确认的单人模式和 NPC Sub-agent 设计提出**[建议] 验收场景**。所有 Core 场景都必须在没有地图渲染、Token 和 AI 插画的情况下成立。

| ID | 场景 | 玩家体验 / 可观察结果 | 主要模块 | MVP 优先级 |
| --- | --- | --- | --- | --- |
| G01 | 开始游戏 / 载入唯一 PC | 创建 Session、载入单人 PC、RuleSet、初始 Scene，以文字显示基本状态 | State Machine、Rule Engine、Agent DM | Core |
| G02 | NPC 独立对话、任务选择 | 玩家与委托人/商人等交流；NPC Sub-agent 根据个人目标、已知信息和关系回应；任务状态经授权更新 | NPC Sub-agent、Agent DM、State Machine | Core |
| G03 | 探索、搜寻、调查 | 自由语言探索、发现线索和切换场景；必要时以 Engine 处理 Ability / Skill Check | Agent DM、State Machine、Rule Engine | Core |
| G04 | 物体交互与基础陷阱 | 开门、调查物体、解除机关；失败在审定范围内可触发 Save、Damage、Condition | State Machine、Agent DM、Rule Engine | Core（有限范围） |
| G05 | **单人 PC 对敌方 NPC 的战斗** | 玩家选择自己 PC 动作，敌方 NPC Sub-agent 选择合法攻击/战术意图；Engine 管理规则、资源与回合 | NPC Sub-agent、Rule Engine、State Machine | Core |
| G06 | 精选法术、职业能力与道具 | 已获准的动作正确检查目标、支付资源、产生状态/事件并可拒绝非法调用 | Rule Engine、Agent DM | Core（精选） |
| G07 | 休息与资源恢复 | HP、Slots、特性等按规则恢复；世界时间由 State Machine 推进 | Rule Engine、State Machine | Core |
| G08 | 战后状态与任务推进 | PC 及相关敌人状态正确写回；战利品与剧情分支可验证 | Rule Engine、State Machine、Agent DM | Core |
| G09 | Session 保存与读取 | 非活跃战斗时重新载入仍保存 PC、任务、Scene、关键 NPC 记忆与关系 | State Machine、Agent DM | Core |
| G10 | **NPC Sub-agent 的身份、知识与自主性** | 至少一个 NPC 在多次互动之间记得关键事实；另外验证敌人战术由自己的 Sub-agent 提议，而非 DM 直接决定 | NPC Sub-agent、State Machine、Agent DM | **Core** |
| G11 | 高阶环境、复杂召唤和变形 | 仅按精选冒险实际需要逐项支持，禁止从基础 Activity 推断全覆盖 | Rule Engine、State Machine | Optional |
| G12 | AI 场景插画 | 根据 DM 描述生成 NPC/地点/关键事件图；关闭后无行为变化 | Agent DM、可选图像服务 | Optional |

**明确排除的首版场景：** 1 PC + AI 队友组队战斗、同伴招募/控制、多玩家合作、完整 NPC 后台生活模拟、NPC 之间无限自动社交。

### 3.1 代表性单人短篇冒险（待确认具体剧本）

1. **村庄接任务：** 玩家以唯一 PC 与一位委托人 NPC 交谈。委托人的话语及取舍由其 **NPC Sub-agent** 决定；DM 提供情境、解释世界和必要检定。
2. **调查遗迹：** 玩家探索线索、检查机关、决定进入路线；State Machine 记录发现与已改变的物体，Rule Engine 完成必要检定。
3. **独自遭遇敌人：** 至少一名敌方 NPC/Monster 由自己的 **NPC Sub-agent** 根据可知事实与可用行动提交战斗意图；玩家仅控制自己的 PC。所有战斗资源、RNG、效果与状态由 Engine 裁决。
4. **战斗或撤退之后：** 处理失败、胜利或离开战场等合法结果；保存 PC 的 HP/资源与敌方 NPC 的关键世界状态。**不依赖 AI 队友参与战斗。**
5. **返回委托人：** 与同一位 NPC 再次交流，其 Sub-agent 读取此前对话中的重要记忆，按关系、承诺和任务结果回应。保存并重新载入 Session 后这些事实仍存在。

**强制验证：** 至少一次非战斗 NPC 的独立对话决策、一次敌人 Sub-agent 的真实战斗行动、一次 NPC 重要记忆的跨场景读取。NPC 决策应受角色目标/知识约束；不要求每次生成同样的句子，也不承诺开放世界里每个 NPC 永久在线。

这个场景是**产品验收样本**，不是故事只能这样发展。玩家的开放式行动可由 DM 理解和裁决，但只有明确已支持的机械效果才能由 Engine 权威执行。

## 4. Rule Engine 支持范围政策

### 4.1 范围分类（产品优先级）

| 分类 | 定义 | 应对方式 |
| --- | --- | --- |
| **Core Required** | MVP 核心场景不可缺少、机制高度共用，且不正确会破坏状态一致性 | 必须实现并进行端到端规则验收 |
| **Selected Support** | 有明确玩法价值，但不是所有内容都需要 | 按精选 Ability、Item、Spell、Monster 或机制族审核启用 |
| **Host Adjudicated** | 结果主要由剧情、NPC、环境或 GM 判断决定 | Agent DM 作语义裁决；State Machine 通过受控操作提交世界结果；机械副作用仍应走 Engine |
| **Out of Scope** | 对首版价值较低、实现代价过高或依赖大型模拟系统 | 明确不承诺执行，并提供可理解的不支持边界 |

**重要：以上四类是“是否需要实现”的产品分类；不能与现有 Rule Engine 的 `executable` / `bounded` / `host_narrative` / `deferred` 技术执行分类混为一谈。** 一个项目范围内的 Core Required 仍可能处于 Deferred，意味着存在阻塞；一个已有 Executable 规则也未必需要进入 MVP 重点验收清单。

### 4.2 Core Required 的候选共用机制

**[建议]** 优先保证以下机制在明确支持范围内正确：

- 基础 D20 检定、Advantage/Disadvantage、Ability/Skill/Save、DC 和来源追踪。
- Initiative、Round/Turn、Action/Bonus Action/Reaction、移动与目标合法性。
- Attack Roll、Damage、Crit、Resistance/Immunity/Vulnerability、Death Saves、Healing/Temporary HP。
- 常见 Conditions、Exhaustion、Effect Lifecycle 与 Concentration。
- 基础 2D Grid、LoS、Cover、范围目标和常用 AoE；不要求视觉地图。
- 代表性 Spell/Feature/Item 的 Invocation 选择、支付、效果及失败回滚。
- **单 PC + 敌方 NPC 的权威战斗执行：** NPC Sub-agent 提交自身合法 Intent，Host 审核 Actor 权限，Engine 负责全部机械结果；不能只以 Engine 的默认怪物 AI 代替该验收。
- Rest/Recovery、战斗结果输出以及向世界状态的安全转交。

这些是**需要具备的机制类型**，不是声明已完成全部 SRD。具体内容必须通过 `Rule Support Matrix` 映射到真实的 Spell、Feature、Item 和 Monster，并有独立规则依据。

### 4.3 明确的首版非目标（待评审）

**[建议]** MVP 暂不以以下内容为发布门槛：

- SRD 5.2.1 **全部**法术、Feat、Monster、Magic Item 与完整职业等级覆盖。
- **AI 队友、常驻 NPC 同伴、招募/入队系统、由玩家直接管理一整支队伍**。这是已确认不纳入 MVP 的范围。
- 复杂位面旅行、全面世界经济、真实物理模拟、完全开放的世界生成。
- 全 3D 空间高度、复杂飞行体积、大型生物多格占位及所有立体 AoE。
- 多人实时联机、分布式一致性、跨 Worker 战斗执行和生产级集群部署。
- **每个 NPC 常驻独立模型/进程**、NPC 离屏永久行动、完全自主的 NPC 社会模拟、无界的多 Agent 对话或递归委派。**不排除每个活跃 NPC 有自己的逻辑 Sub-agent 和记忆上下文。**
- 所有复杂召唤、形态变化、任意 Ready/Reaction Trigger 的通用支持。
- 所有开放式叙事命令都能自动转化为机械执行。
- 可交互视觉游戏世界、地图 Token、深度状态驱动动画、实时语音/视频及完整 VTT 编辑工具链。

未支持内容必须被正确识别，**不能以无效果的“成功执行”充当规则支持**。

### 4.4 不支持规则时的行为

1. **机械规则不支持：** 在任何资源扣减、RNG 消耗或不可逆状态变化前返回结构化拒绝/能力不支持信息（若该执行路径支持 Preflight）；Agent DM 明确告知玩家限制或提供合法替代方案。
2. **需要 GM 裁决：** 明确切换为叙事/世界操作路径；仅在经过授权和验证后提交世界状态，不冒充 Rule Engine 的机械结算。
3. **混合型效果：** 将可执行的机械部分和需要 Host 裁决的部分清楚拆开；不得因一个规则的某个 Activity 可解析，就宣称整个规则效果已实现。
4. **不得静默变更规则：** 若要采用简化、Homebrew 或 DM Override，应留有操作来源与审计记录，并与正式 SRD 机制区分。

## 5. 文字交互 MVP 与可选插画（Visual Presentation 延后）

**[已确认] MVP 不交付完整 Visual Presentation 模块。** 三个核心模块只需一个最低限度的文字交互入口（CLI、轻量 Chat UI 或其他形式待技术选型），便可完整游玩。

### 5.1 MVP 必需的文字交互能力

- 玩家可以通过自然语言描述行动并接收 Agent DM 的场景描写、NPC 回应和规则结果。
- 玩家能以文字获知必要的 PC 状态、行动资源、任务进度、当前可交互对象及自身的位置/距离等信息；不要求全部数据每回合完整输出。
- 当规则执行需要补充选定目标、位置、法术模式、骰点来源等信息时，Agent DM 能询问玩家或提出明确选项；不能猜测或擅自操作玩家 PC。
- 受支持的战斗能够通过文字叙述、结构化状态摘要和必要的坐标/位置提示完成，不要求提供实时地图、Token 或动画。
- 拒绝、裁决不确定、世界状态提交以及工具执行故障有可理解的文本反馈。

### 5.2 可选的 AI 插画

- 允许依据 **Agent DM 的叙事描述**生成场景、NPC 或关键事件插画；具体模型、提供方、频次和成本**待决策**。
- 插画应为可跳过、可关闭的非阻塞增强；生成失败不阻断冒险。
- 图像不作为地形、HP、距离、物品归属或任何规则数据的权威来源。
- MVP 不要求将 Rule Engine / State Machine 的结构化场景状态转换成可交互画面，也不要求从图片反向解析世界状态。

### 5.3 MVP 后的 Visual Presentation 阶段

以下不属于本版发布条件：PixiJS / 专用 Scene Engine 选型、可编程 VTT 地图、角色 Token、行动动画、与 Rule Engine/State Machine 深度同步的世界可视化、图像资产管线和 UI 战术操作系统。未来仍应**只读消费权威事件和状态**，避免成为第二个规则或世界引擎。

**独立验收门槛：** 在禁用图片生成、没有地图渲染的环境下，A01 的完整冒险仍必须成功。
## 6. 跨模块契约最低要求

**本节列出产品层级要求，不替代最终的 `MODULE_CONTRACTS.md`。**

### 6.1 Command / NPC Decision

- 每个改变权威状态的请求都能追踪 Session、Scene、Actor、调用源及请求身份。
- 真人玩家仅能直接代表唯一 PC；NPC 的行为选择由对应 `npc_id` 的 NPC Sub-agent 提出，State Machine/Host 校验 NPC 身份、控制权、状态版本与可见信息；Agent DM 只做合法协调，不代其直接下决定。
- NPC Sub-agent 的结构化产出必须区分 `dialogue`（可叙述内容）、`world_action_proposal`（待世界审核操作）和 `combat_intent`（待 Rule Engine 执行动作）；最终的具体数据 Schema 尚待设计。
- NPC 决策不能直接携带“成功造成多少伤害”“把某目标 HP 改成多少”之类最终机械结论。含攻击模式、目标、法术效果和资源的命令必须明确选择。
- PC 和 NPC 可以共享 Engine 机械语义，Controller 权限在外围执行，不能通过伪造 `actor_id` 越权。
- 引擎或 Host 对非法提议应提供可解释的拒绝，NPC Sub-agent 可以在受限预算内重新选择；异常不能制造已提交的假象。

### 6.2 Result / Event

- 区分：执行成功、规则拒绝、GM 裁决、执行异常、已提交但响应失败。
- 提交后的规则事件具备稳定顺序、来源和受影响对象；NPC Sub-agent 的原始提议与最终结果不能混为一谈。
- 重试不会重复扣减 Action、Slot、Charges 或写入同一世界操作。
- Agent DM 的叙事要以已提交结果为依据；任何 NPC 即兴表述都不能让未执行的行动自动变为事实。
- 为审计与 Replay 保存已提交的 NPC Intents 和关联 Result；不要求保留完整的 Sub-agent 私有推理过程。

### 6.3 State / Memory / Knowledge

- State Machine 明确管理世界版本、场景、NPC 身份、角色私有与公共记忆、任务/关系的合法写入方式。
- NPC Sub-agent 只读获取被授权的 NPC 视角：`npc_id`、角色设定、动机、可知事实、相关互动记忆、当前场景及可用动作摘要；不向 NPC 泄漏 DM 全知视角或其他 NPC 私密内容。
- 已提交重要对话与剧情事件驱动记忆更新，确保同一个 NPC 跨场景和 Session 仍有连续人格与事实；记忆压缩/冲突解决属于后续契约的实现问题。
- 战斗开始需要输入快照，结束需要输出/结算协议；HP、资源与 Effect 所有权明确，不能用 DM/NPC 自由文本推算扣减。
- 首版是否支持**活跃战斗跨进程恢复**仍待决策，不能将一般 Session 保存等同于战斗恢复。

### 6.4 适配现有 Rule Engine

现有仓库：<https://github.com/agentic-trpg/trpg-rules-engine>。

根据 2026-10-09 审计基准（`main`：`64dd920`），已有 `PlayerIntent`、`CombatEvent`、`LiveCombatView`、`CombatOutcome`、HTTP Bridge 等。上述接口仍是候选对接面，不代表所有 NPC Sub-agent 决策都能直接运行。

**[必须优先验证的集成缺口]** 现有玩家行动主要经 `submit_player_intent`，怪物通过 `advance_monster_turn` 使用内部行为选择。若 MVP 要求**NPC Sub-agent 而非 Engine 内置 AI 决定敌人行动**，必须提供受 Host 授权、可表达目标/能力选择的 NPC 显式 Intent 执行契约（或证明已有公共入口能实现同等效果）。它必须复用共享合法性、资源、事件、RNG 与回滚，不能绕过到 `_LiveCombat`，也不能把 NPC 临时冒充为 Player Character。

## 7. MVP 验收标准（End-to-End）

以下为**[建议] MVP 验收合同**；等级、精选规则、具体单人剧本及成本上限仍需讨论。**AI 队友已明确排除，不再保留同伴战斗的强制或候选发布门槛。**

| 验收 ID | 场景与操作 | 通过标准 |
| --- | --- | --- |
| A01 | 完整文字单人冒险 | G01–G10 获批准的 Core 场景贯通同一 Session；仅一名 PC、无 AI 队友；从接受任务到合法结局，无需人工修改数据库或 Engine 私有状态 |
| A02 | NPC 对话与探索 | 委托人等 NPC 的发言及选择由其自身 Sub-agent 提出；Agent DM 不直接代言；世界变化经 Host 验证保存 |
| A03 | **单人 PC + 敌人 NPC Sub-agent 战斗** | 玩家仅选 PC 动作，敌人自己的 Sub-agent 提交至少一个显式、合法的战术 Intent；Engine 计算回合、移动、攻击/豁免、资源、伤害与结束条件，无视觉地图 |
| A04 | 机械确定性重放 | 相同规则数据、初始状态、Seed 和**已提交的 PC/NPC 命令序列**产生相同权威事件、结果和最终状态；不要求 LLM 决策或文案逐字相同 |
| A05 | 非法/不支持请求 | 无效 Actor 权限、目标、资源或规则在相应 Preflight 边界拒绝；没有额外资源扣除、RNG 消耗或越权修改 |
| A06 | 重试与异常 | 已提交 Command 按约定幂等；意外故障不导致状态、资源或事件不一致 |
| A07 | 战斗转交世界 | 玩家 PC 与敌方 NPC 的机械状态按真实来源归属安全写回，资源不误记到施法目标或其他角色 |
| A08 | 休息与场景推进 | 玩家资源按已选规则恢复，世界时间/Scene 正确推进 |
| A09 | Session 保存与读取 | 重载非战斗 Session 后，PC、任务、Scene、NPC 重要记忆与人物关系一致 |
| A10 | 已支持规则正确性 | 每个纳入范围的机械规则有 SRD/明确裁决依据、公共执行入口、正确/拒绝用例和已知边界 |
| A11 | 角色决策隔离 | 玩家只直接控制唯一 PC；NPC Sub-agent 有自己角色知识与目标；DM 仅主持和协调，不替 NPC 选择行动或偷偷改权威结果 |
| A12 | 纯文字运行 | 关闭图像生成，无地图/Token/动画仍可完整游玩；插画无法影响状态 |
| A13 | **NPC 持续身份与记忆** | 重要 NPC 在至少两次跨场景互动中保持身份、记得已知承诺/冲突；同一 NPC 的私有事实不泄漏给其他 NPC |
| A14 | **NPC 子代理故障/拒绝** | NPC 提议非法动作时获得结构化反馈并在有界次数内重试；超时/失败不凭空创建对话事实、伤害或世界状态变更 |
| A15 | 单人遭遇失败分支 | 验证撤退、失败/倒地/死亡至少一种合法处理路径，不允许因“只有一个 PC”而在未获授权时篡改骰点保护主线 |

**独立正确性要求：** 关键规则预期来自 SRD 5.2.1 或有记录的公开裁决，而不是用 Engine 自身输出生成正确答案。多 Agent 能力另需测试角色可知事实与行动授权，不等同于规则测试。

### 7.1 最小黄金测试场景

- **Invocation/Payment：** 选一个动作，仅执行其所选 Activity 并支付相应 Action/Slot/Charge。
- **PC/NPC Actor 隔离：** 玩家仅操作 PC；敌人的 NPC Sub-agent 发出行动提议，Host 做权限验证，Engine 执行结果。
- **NPC 知识边界：** 给 NPC 一个它不知道的世界秘密，确保回答与战术不依赖该事实；同一 NPC 后续能读取明确获知的线索。
- **Agent 处理拒绝：** 不把失败提议说成已经成功；重试/超时受控。
- **状态与 RNG：** 无效目标、缺少资源、不支持机制及注入故障均不污染权威状态或随机序列。
- **跨模块同步：** HP/Slot/Effect 从 CombatOutcome 写回世界时保持所属 Actor。
- **展示非权威：** 无需视觉层也能完成冒险；文字和插画不会自行造成伤害、位移或资源变更。

## 8. 里程碑与开发决策顺序

| 阶段 | 目标 | 完成标准 |
| --- | --- | --- |
| **M0：Scope 冻结** | 确认单人剧本、NPC Sub-agent 自主性、精选规则与非视觉范围 | 文档状态升级为 Approved，待定项收敛，产品决策记录齐全 |
| **M1：Rule Engine Correctness Closure** | 修复影响单人战斗的核心正确性问题 | Activity 选择、支付归属、拒绝回滚、重复请求等有公共测试 |
| **M2：Cross-module Contracts / NPC Intent** | 定义 Session、Scene、NPC Role Memory、Command、Event、状态权威和**NPC 战斗显式控制入口** | NPC Sub-agent 不访问 Engine 私有状态也能合法选取敌方动作；非战斗 NPC 能做独立对话决定 |
| **M3：Text-first Solo Adventure Vertical Slice** | 打通一段真实单人剧本、NPC 独立互动、敌方 Agent 战斗、结局持久化 | A01/A02/A03/A09/A13 全部通过；图片完全可关闭 |
| **M4：MVP Acceptance / Release** | 依据实际玩家体验收敛问题与规则范围 | 获准的 A01–A15 均有验收证据，明确记录未支持规则与 Agent 成本限制 |

### 8.1 与 Rule Engine Backlog 的关系

- `trpg-rules-engine/BACKLOG.md` 是**技术缺口清单**，不是跨项目的 MVP 任务清单；不必清空 Deferred 才宣布 MVP 完成。
- 每项新规则需求都要对应明确的单人冒险场景及可独立验证的机械结果。
- **新增优先级依赖：** 因敌方 NPC 行动需要来自 NPC Sub-agent 而不是默认 Monster AI，必须验证 Rule Engine 的 NPC 显式决策入口能否使用；若不具备，应在基础正确性修复之后优先补足，而不是继续拓展冷门法术。
- Batch 的有效进度应由规则正确性、可执行场景、跨模块状态一致性和 NPC Agent 独立行为证明，而非新增行数、Commit 数或测试数量决定。
- 当前已审阅 Engine 的 Invocation 多 Activity 误执行和 `CombatOutcome` 支出归属错误，仍是优先正确性工作。

## 9. 决策登记（Decision Register）

| ID | 产品问题 | 当前决定或建议 | 状态 |
| --- | --- | --- | --- |
| D01 | 首版正式 RuleSet？ | 推荐 D&D 2024 / SRD 5.2.1，其他模块不绑定 D&D 专属机制 | [待决策：具体基线] |
| D02 | 首版重点角色等级？ | 候选 1–5 级，已有高等级实现保留 | [待决策] |
| D03 | 真人玩家与角色数？ | **一个真人玩家，仅控制一个 PC** | **[已确认]** |
| D04 | 首版精选 Spell / Feature / Item / Monster？ | 从单人冒险和共用机制反推 Rule Support Matrix | [待决策] |
| D05 | 交互方式？ | **文字/自然语言优先** | **[已确认]** |
| D06 | Visual Presentation 是否进入 MVP？ | **不进入；战术视觉/场景深度联动留待 MVP 后** | **[已确认]** |
| D07 | 首版持久化保障？ | 先支持非活跃战斗的 Session 恢复；活跃战斗另议 | [待决策] |
| D08 | GM Override 权限与审计？ | 显式授权、结构化、有限范围并记录来源 | [待决策] |
| D09 | 冒险内容来源？ | 精选单人短篇剧本；外部剧本导入方式另议 | [待决策] |
| D10 | 部署与成本边界？ | 本地/单实例优先；NPC Sub-agent 按需执行 | [待决策：预算上限] |
| D11 | 三大核心模块是否独立进程？ | 不强制，先保证逻辑职责和状态权威独立 | [待决策] |
| D12 | 开放世界裁决边界？ | 从场景选择 Engine vs Host 的规则职责 | [待决策] |
| D13 | AI 队友是否进入 MVP？ | **不使用 AI 队友；以单人剧本代替同伴组队验证** | **[已确认]** |
| D14 | NPC 由谁控制？ | **NPC Sub-agent 独立决定对话与行动；Agent DM 仅主持、协调和裁决** | **[已确认]** |
| D15 | AI 插画是否必需？ | 可选，且不影响规则与状态 | **[已确认：非必需]** |
| D16 | 敌方 NPC 战术由谁选择？ | **对应 NPC Sub-agent 提议战斗 Intent；Rule Engine 做机械裁决** | **[已确认]** |
| D17 | NPC Sub-agent 并发数量、调用预算和降级方式？ | 事件驱动、按需调用、有界执行；具体数值尚待性能测试 | [待决策] |
| D18 | NPC 的长期记忆及知识粒度？ | 角色可知事实、动机、关系、关键互动记忆由 State Machine 维护 | [已确认：原则；Schema 待设计] |
| D19 | NPC 和 DM 是否使用相同底层模型？ | 可以复用模型与进程，**必须逻辑上隔离角色上下文和决策接口** | [已确认：允许共享；技术待选型] |
| D20 | NPC 决策如何接入当前 Engine 怪物战斗？ | 需检验并必要时建立 Host 授权的 NPC 显式 Intent API，不能只把现有默认怪物 AI 当作 Sub-agent | [待设计：MVP 集成阻塞] |

**当前下一步：** 明确 NPC Sub-agent 的**最小行为和记忆契约**（对话 NPC、敌方 NPC、什么情况下唤起、怎么获得可知信息、如何处理非法行动），之后再决定首版等级与精选规则清单。这个方向已经取代先前的“是否增加 AI 队友”讨论。

## 10. 文档维护与变更规则

1. 本文件是**跨 Repository 的 MVP 产品范围依据**；正式确定后，模块设计和 Backlog 应引用它，而不是私下重新定义首版目标。
2. 改变产品范围时应注明：变化原因、受影响的 Gameplay Scenario、规则成本、四模块接口影响、需要更新的验收项。
3. 各个模块仓库可保留更全面的技术债或未来 Feature 清单；进入 MVP 开发范围必须有对应的场景/验收理由。
4. 最新实现是否已具备能力，始终以对应模块的实际代码、测试及审核清单为准。本文件的历史实现快照不作为持续更新的完成状态表。
5. 每完成若干开发 Batch，应回看 MVP 场景是否更接近可玩状态；如果只是扩大规则条目但没有改善场景体验，需要重新考虑优先级。
6. 文件审批人、文档维护流程以及决策记录位置：**[待决策]**。

---

## 附录 A：相关资源

- [现有 Rule Engine Repository](https://github.com/agentic-trpg/trpg-rules-engine)
- [Rule Engine 技术 Backlog](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/BACKLOG.md)
- [Rule Engine Capability Matrix](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/docs/capabilities.md)
- [Engine / Bridge Intent Parity](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/docs/dev/bridge-intent-parity.md)
- [Rule Engine Development Standards](https://github.com/agentic-trpg/trpg-rules-engine/blob/main/AGENTS.md)

> **下一步：** 先确认 D13（是否强制包含 AI 同伴参战），再依序确认角色等级、规则支持清单和 State Machine↔Engine 的 NPC/PC Actor 路由。后续使用已确认的 Gameplay Scenarios 反推 `MODULE_CONTRACTS.md` 与 Rule Engine 工作优先级。
