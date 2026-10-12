# Agentic TRPG — Evennia Adoption Plan

> **版本**：v0.1 / Draft；**日期**：2026-10-12
>
> **技术方向 [DECIDED]**：优先采用 Evennia 作为游戏运行底座，保留现有 D&D Rule Engine，允许迁移和重构 State Machine。迁移与运行验收尚未执行。
>
> **规范关系**：[MODULE_CONTRACTS.md](./MODULE_CONTRACTS.md) v0.12 §0.2 / §3.6 / §7.5 是跨模块规范；本文记录采用理由、复用目标和验证计划，不另立状态所有权或 ABI。配套 [State Machine](./STATE_MACHINE_ARCHITECTURE.md) v0.14、[Agent](./AGENT_ARCHITECTURE.md) v0.12、[MVP Scope](./MVP_SCOPE.md) v0.14、[Adventure Package](./ADVENTURE_PACKAGE_SCHEMA.md) v0.8。
>
> **状态**：`[DECIDED]` 是方向/原则已定，`[PROPOSED]` 是待验证方案，`[OPEN]` 是未决事项，`[NOT IMPLEMENTED]` 是目标尚未实现；框架官方文档存在不等于本项目集成或验收通过。本轮只修改总控仓库 Markdown，不创建仓库、安装依赖、初始化游戏或实施 EB-1。

## 1. 为什么采用框架

我们需要可交互、可保存、可持续行动的文字游戏运行环境。优先采用 Evennia 的理由是实际复用对象、持久属性、模板、命令与动作钩子、Script、建造工具和文字客户端，把自研工作集中在 D&D 集成、可信提交、信息隔离与人物认知。若仍在框架内重写一套对象数据库、通用命令引擎、活动循环和客户端，再让 Evennia 仅转发消息，就没有实现本次采用目的。

以下“框架已有”仅指官方文档所述能力；“本项目用途”均为复用目标 `[PROPOSED; NOT IMPLEMENTED]`，不是已经适配的能力，也不冻结依赖版本。

| 实际复用目标 | 官方能力依据 | 本项目用途与限制 |
|---|---|---|
| 对象 / Typeclass | [Objects](https://www.evennia.com/docs/latest/Components/Objects.html)、[Typeclasses](https://www.evennia.com/docs/latest/Components/Typeclasses.html)：房间、出口、角色和物体可用原生对象表达 | 两房间、门、NPC 与动态物体；门的领域状态/钩子仍需小型游戏实现，不另造平行 Scene/Object 引擎。Session 隔离、Actor ID 映射待验证 |
| 持久属性 | [Attributes](https://www.evennia.com/docs/latest/Components/Attributes.html)：持久属性与不跨 reload 保存的 NAttributes 有区别 | 复用持久属性承载适合的事实；机械状态、索引及认知任务是否适合 Attribute 或领域表须验证，不把临时属性当可靠存档。可变 Attribute 可能自动保存，不能直接当无副作用 RE Snapshot |
| 模板 / 运行时创建 | [Spawner and Prototypes](https://www.evennia.com/docs/latest/Components/Prototypes.html) | 经授权从批准模板创建对象，避免另造通用模板/建造平台；模板更新不能改写 Session 固定定义或历史执行版本 |
| 动作生命周期 / 钩子 | [Commands](https://www.evennia.com/docs/latest/Components/Commands.html) 的前置、解析、执行和后置钩子；Objects 的移动钩子 | 接入可信验证、普通世界操作、RE 求值与提交后通知；原生钩子不自动提供本项目幂等/原子性。命令暂停或 InterruptCommand 不等于可持久恢复的 D&D Continuation |
| Script / 活动处理 | [Scripts](https://www.evennia.com/docs/latest/Components/Scripts.html)：可保存系统状态、附着对象，定时组件可选 | 组合 Encounter / Activity Controller、持续 NPC Policy 与按需推进；这些 Controller 是项目方案，不是现成 D&D 功能。不照搬示例定时器作为权威 Game Time 或保证崩溃续玩 |
| 建造工具 / 文字客户端 | [Building Quickstart](https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part1/Beginner-Tutorial-Building-Quickstart.html)、[Web Client](https://www.evennia.com/docs/latest/Components/Webclient.html) | 先用原生建造入口和文字交互完成纵切；限制建造权限，不自动赋予模型管理员权限。地图、Token、动画后续单独设计，不因框架支持多人扩大 MVP |

[EvAdventure Combat Base](https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part3/Beginner-Tutorial-Combat-Base.html) 展示共享 CombatHandler / 行动对象的组织方式；它是教学系统，不作为 D&D 攻击、伤害、豁免、支付或效果规则实现。实际 D&D 求值仍交现有 RE。

## 2. 仓库分工与迁移资产

| 仓库 / 职责 | 状态 | 定位 |
|---|---|---|
| `agentic-trpg/agentic-trpg` | Existing；本轮工作仓库 | 总控决定、跨模块契约、采用门槛与验证记录；不承载本轮运行实现 |
| `agentic-trpg/Evennia_base` | **Planned / [NOT IMPLEMENTED]**；本轮不创建 | 基于 Evennia 的游戏项目与运行集成层；优先固定版本依赖，不默认 fork 整个 Evennia，也不复制旧 SM 后改名；尚无可访问仓库/实现承诺 |
| `agentic-trpg/trpg-rules-engine` | Existing；既有完成状态不变 | 保留 D&D 求值算法与受支持规则，不因采用框架重写规则或升级依赖；按实际锁定版本验证 Consumer |
| `agentic-trpg/trpg-state-machine` | Existing；迁移资产与回归对照 | 暂不删除、归档或宣布废弃；允许替换具体实现，不要求逐类逐表搬迁 |
| Agent Host | 既有逻辑职责，非本轮新仓库 | 仅模型执行、Context、预算和传输；本轮不实现 Host，不改变 EVA 标识/完成协议 |

优先保留旧 SM 已验证的规则集成、授权、幂等、RNG、回执、故障用例、NPC 私有状态和可靠处理语义。是否直接复用代码须逐项检查依赖与许可；保留旧实现不是将 Evennia 降为外壳的理由。新旧实现使用**独立测试 Session**对照同一输入/期望结果，不共同控制同一生产 Session，也不建立默认双向同步桥。

MODULE_CONTRACTS.md §1.1 保留 2026-10-12 前一批有限静态审查记录：明确 SM main 与开发分支、SM 锁定 RE 与当时 RE main 的区别。本轮不刷新这些 SHA/能力状态，不把旧 Review 或静态核对说成完整运行测试；EB 开始时须重新只读记录实际版本与能力证据。

## 3. 权威状态、RE 与提交边界

单一事实来源与可信提交原则由 MODULE_CONTRACTS.md §0.2 定义。Evennia 对象系统和新增领域服务可以承接原 SM 职责；同一事实不得在 Evennia 与旧 SM 各存一份并双向同步。不同表可保存不同事实；Snapshot、授权视图和缓存是派生数据，不成为第二权威。对象/Attribute/领域表映射、提交边界、数据库配置均 `[OPEN]`。

普通移动、交互、创建对象等若只需要已支持的世界规则，可由可信运行层验证/提交；涉及 D&D 机械裁决时才调用 RE。RE 保持无权威跨请求状态、显式 Snapshot / Intent / RulesetBinding / RNG、未提交 Result；`accepted` 不等于 `committed`。Evennia 钩子、构建命令和 Script 也不能绕过授权、版本与资源正确性。

EB-2 必须同时验证数据库与对象缓存。Django 官方说明事务回滚不会自动恢复模型内存字段或应用缓存，提交后回调也不是数据库事务的一部分；Evennia Typeclass / Attribute 的缓存和可变值行为须在固定版本实测，不能以 SQL 回滚成功推导对象已恢复。[Django Transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)、[Evennia Attributes](https://www.evennia.com/docs/latest/Components/Attributes.html)。可靠通知须保留可恢复交接语义，不能仅以一次 on_commit 回调替代可靠 Outbox；具体载体待验证。

## 4. 成熟机制的复用与借鉴

不同时接入 Evennia 与 Ranvier。Evennia 是优先依赖框架；CDDA / Ranvier 仅提供设计借鉴。下表的用途是本项目选择，不能反向宣称来源系统已经解决本项目的问题。

| 来源 | 机制与依据 | 用途 / 复用方式 | 限制 |
|---|---|---|---|
| Evennia | [命令生命周期](https://www.evennia.com/docs/latest/Components/Commands.html)、[对象](https://www.evennia.com/docs/latest/Components/Objects.html) / [模板](https://www.evennia.com/docs/latest/Components/Prototypes.html)、[Scripts](https://www.evennia.com/docs/latest/Components/Scripts.html)；Combat Base 展示 Controller 组织 | **依赖框架能力**构建实际运行项目；Encounter / Activity Controller 借鉴并适配 | 不是现成 D&D、可靠任务系统或安全代码沙箱；直接复制示例代码另行审查 |
| CDDA | [环境条件 / 视线与声音刺激](https://docs.cataclysmdda.org/JSON/EFFECT_ON_CONDITION.html)、[Activities](https://docs.cataclysmdda.org/PLAYER_ACTIVITY.html) 的持续行动状态、[Reality Bubble 坐标 / 分块加载](https://docs.cataclysmdda.org/c%2B%2B/POINTS_COORDINATES.html) | **仅借鉴设计**：当前环境查询、专用感知刺激、短期行动状态、按需要/活动范围推进 | 不搬迁 C++ 引擎、完整模拟、坐标尺度或其规则；本文不假定所有离屏行为都停止，也不把来源的视线判断当 D&D 判定 |
| Ranvier | [Scripting](https://ranviermud.com/building/scripting/) 的可配置小型 Behavior；[Room.emit](https://ranviermud.com/jsdoc/Room.html) 的局部事件转发 | **仅借鉴设计**：组合小行为、对象局部通知，避免通用全局事件转发一切 | 不引入第二套运行框架 / JavaScript 回调执行层；局部通知本身不证明察觉、授权或可靠投递 |

**直接复用代码**、**依赖框架能力**与**借鉴设计**分别记录。未来实际采用示例、contrib、插件或资源前，应按具体文件/包/版本核对来源、许可与依赖；不假定核心项目许可证覆盖全部示例、插件和素材；Evennia 的 [Contribs Overview](https://www.evennia.com/docs/latest/Contribs/Contribs-Overview.html) 也区分可选贡献组件及其集成要求，具体许可仍须逐项核对。本轮未复制这些项目代码或内容。

## 5. 即时行为、感知与完整经历

遵循 MODULE_CONTRACTS.md §0.1 / §7.5：即时行动由可信游戏运行层、非 LLM Policy 和必要 RE 协作，不要求每次攻击、移动或持续效果调用 NPC EVA。当前感知是眼下的授权环境/机械可知信息；短期行动状态是目标、进度、失效条件等运行状态；长期人物认知是 NPC LLM / EVA 的 Memory、Belief、Relationship、Goal、Plan 提议。Host 执行模型，不持有这些权威事实。

JEV 可以承担已有权限内的 Perception Judgment / Memory Gate Judgment 语义判断，不获得新规则权限；不能代替必需的规则判定、未知的可信事实或即时战术资格。目标消失、移动或条件变化后，行为必须重新查询/验证，不永久沿用先前“看见目标”的结果。

**[DECIDED] 一场完整战斗对应一个 CombatEpisode**，作为 WorldEpisode 的战斗事态边界；EpisodeObservation 是 NPC 对整段经历中自己已察觉部分的逻辑观察单位。Round / Action 不默认各建 Episode；机械事件不默认包装成 WorldEvent，也不默认产生独立 OB。运行时感知可以支持即时行为，战后聚合整体经历，不等待认知聚合解锁战术。

**[PROPOSED; NOT IMPLEMENTED]** 比较“战时保存必要察觉结果或可信证据，战后统一聚合”与基于完整可信历史的重建方案。任何方案都不能从战斗结束态补造过去感知，不能泄漏未察觉内容、隐藏行动者或因果；实际保留阶段须有对应时间/证据且结果可追溯。证据 Schema、粒度、Episode 边界细节、异常结束、聚合/重试及既有 TTL / Work / 来源引用映射 `[OPEN]`。Event-level OB / Outbox 是当前实现和迁移资产，不是永久目标；本轮不删除观察或历史记录，不重设计 EVA ID / Completion。

## 6. Coding Agent 扩展与冒险基线

运行时创建内容、组合机制和安装 NPC 行为是目标能力 `[DECIDED]`；完整 Coding Agent 扩展系统 `[NOT IMPLEMENTED]`，不作为 EB-1 的前置条件。分清三层：

| 扩展层次 | 目标处理方式 | 待验证范围 |
|---|---|---|
| 配置 / 模板更新 | 对已支持字段/模板进行授权、验证和版本记录 | 什么可在运行时更新，实例与定义如何隔离 |
| 已有能力组合 | 从受控能力/Behavior 组合机制、安装到批准对象 | 参数/权限/依赖验证、资源预算、失败隔离 |
| 真正新增底层机制 | 生成代码先完成验证、权限限制和受控启用，再进入安全边界 | 验证/隔离技术、能力授予、状态迁移、兼容与故障政策；不承诺任意动态代码安全执行 |

任意 Python / JavaScript 回调、人工审批或 reload 都不等于安全热部署。目标是**准备完成后在安全边界启用**，不是任意代码即时生效。原生框架扩展入口也不自动满足此目标。在途操作绑定哪些定义/规则/行为版本、切换安全点、行为状态迁移、失败后的停止/恢复、撤销权限与回滚程序均 `[OPEN]`；回滚扩展版本不自动撤销已提交游戏事实。

固定 Adventure Package 仍是 Session 初始基线。获准的新对象、机制或行为是 Session 扩展或运行态变化，不悄悄回写固定包，不改变历史执行依赖的定义。扩展来源、版本、启用记录与 RulesetBinding 的关系 `[OPEN]`；本轮只同步 Adventure Package 边界，不重新设计整套 Schema。

## 7. 已决定与待验证事项

| 议题 | 状态 | 决定 / 下一证据 |
|---|---|---|
| 优先 Evennia + 保留 RE + 允许 SM 迁移/重构 | [DECIDED] | 具体能力正式迁移以 EB 证据和映射审查为条件，迁移未执行 |
| 单一事实来源、可信提交、运行与认知分离 | [DECIDED] | 不绑定旧 SM 类、表或仓库边界；不建默认双重权威同步 |
| `Evennia_base` 游戏项目、固定版本依赖优先 | Planned / [NOT IMPLEMENTED] | 版本、数据库、部署配置 [OPEN]；本轮不创建或安装 |
| 对象 / 属性 / 领域表与提交映射 | [PROPOSED / OPEN] | EB-1 原生复用，EB-2 原子性/缓存/通知证据 |
| CombatEpisode / 整段 EpisodeObservation | [DECIDED]；算法 [OPEN] | EB-3 比较最小经历保留 / 重建方案，尚未实现 |
| Coding Agent 动态扩展 | 目标 [DECIDED]；完整系统 [NOT IMPLEMENTED] | 在途版本、迁移、安全启用与失败协议 [OPEN]，不扩大 EB-1 |
| Host / EVA / 通用 Continuation | 既有规范；本轮不实施 | 不以 Script 定时、reload 或基础验证通过声称完整交付 |

## 8. EB-1～EB-3 验证计划 `[PROPOSED; NOT IMPLEMENTED]`

以下均为**未来通过条件**，本轮无运行结果。每阶段记录固定源码/依赖版本、数据库配置、独立测试 Session、操作与断言、失败注入/日志和已知缺口；给出可复现命令与实际输出后才能标“运行验收通过”。不编造工期、节省比例或绿色结果。

### 8.1 EB-1：原生世界基础

建立原创两相连房间、一扇门、一个 NPC 与单 PC；通过原生文字客户端交互、移动、查看、开关门，运行时创建对象并配置受控 NPC 行为，正常停服重启后状态保持。

**通过证据：** 对象/出口/属性/Prototype/Command 钩子/Script 与建造入口的实际调用、文字操作记录、重启前后身份/位置/门状态/动态对象/行为配置的持久一致性，以及越权建造拒绝。明确门和行为的游戏代码与框架复用部分。不能用自建完整 Object/Command/存储平台或每次启动重放模板重置世界来通过。此阶段不要求完整 Host、RE 全协议升级、Coding Agent 沙箱或完整冒险。

### 8.2 EB-2：真实 RE 集成

开始前固定**一个实际已支持的真实规则操作**及 RE / RulesetBinding / Snapshot 协议版本，优先已有执行证据的基础攻击；若该锁定版本不支持则先明确阻塞或选定另一已证实操作，不能用 mock RE 代替。由 Evennia 运行集成层构造隔离只读输入和显式 RNG，RE 求值，可信层校验后提交状态/RNG/回执/可靠通知。不要求同时升级所有 RE 协议。

**通过证据：** 合法与非法操作的真实结果、支付/HP 等完整连带变化、相同输入/RNG 的确定性、重复提交只采用一次、同键不同内容拒绝、并发/版本冲突不提交旧结果。注入求值故障、数据库写入/提交失败、提交成功但回复/通知失败；验证不双扣、不重掷、不发未提交通知，提交后通知可恢复且授权正确。

**缓存专项证据：** 修改前先持有对象/Attribute 引用并读取缓存；在受控事务中变更后注入回滚，再同时从数据库、新查询、旧持有引用、属性容器和后续命令读取。证明无脏位置/资源/门状态等残留、重试基于真实权威版本，无自动保存容器继续写入已废弃状态。须实际验证失效/重载/恢复策略，不能仅展示 SQL 值正确或重启后正确；也不能假定通知钩子天然在 COMMIT 之后。

### 8.3 EB-3：运行机制与信息隔离

用受控非 LLM Policy / Script 或活动处理验证 NPC 连续行为；目标离开/不可感知后重新检查，停止或按批准行为调整，不能追踪无权知道的位置。验证一个受控行为版本切换、在途操作与行为状态的处理，以及两个角色授权视图互不泄漏秘密。

构造最小原创完整战斗，整场只有一个 CombatEpisode；记录 NPC 实际获得的最小经历并在结束后聚合 EpisodeObservation。包含只听见部分、后到未目击、未知/缺证据等边界，证明没有把每条机械 Audit 变 OB，也没有从结束态补历史或泄漏隐藏因果。比较必要战时记录与可信历史重建的可行性，不能预先把任一算法当正式 ABI。

**通过证据：** 连续行为/重新检查日志、受控版本切换与失败停止结果、跨角色/跨 Session 越权拒绝、阶段时间/来源追溯与战后授权聚合输出、聚合重试无重复经历，以及记录成本/完整性和未支持路径。此阶段不等于完整 Host、长期认知系统、安全沙箱或通用中断系统完成；敌方 Agent 宏观自主性仍留给完整 MVP 验收。

## 9. 采用条件、暂停与退出条件

EB-1 先证明原生复用，EB-2 证明真实规则与提交正确性，EB-3 证明持续机制和信息隔离；通过后才能对已验证能力提出正式迁移映射/切换计划，不把三阶段通过等同整个产品完成。生产 Session 切换、数据迁移/备份、回退资格和旧实现处置须另行设计，不因本轮自动授权执行。

如果关键能力必须大范围重写框架、必须维持同一事实的双重权威，或无法保证资源/RNG/幂等/事务与对象缓存一致性/信息隔离，应**停止整体迁移**，记录失败证据与范围，保留可复用设计和旧实现，再重新决策。不能用“方向已决定”掩盖正确性失败，也不自动转为同时接入 Ranvier。

允许阶段结果为通过、失败或部分验证；缺少关键证据不能标通过。当前状态：**技术方向已选定；EB-1～EB-3、代码迁移、运行验收均未执行；Evennia_base 仍 Planned**。

## 10. 版本与来源范围

v0.1：记录 Evennia 优先路线、实际复用目标与旧 SM 迁移定位；同步 CombatEpisode、受控动态扩展及 EB 验证门槛。官方在线资料核对日期为 2026-10-12，`latest` 页面会变化，只用于能力/限制依据，不表示已锁定框架版本。进入验证时记录固定版本与对应源码，直接复用代码另做逐项来源/许可审查。本轮不改变既有 RE / SM 规则能力完成状态。
