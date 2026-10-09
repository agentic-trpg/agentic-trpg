# Agentic TRPG — MVP Scope Specification

> **文档状态：Draft / 待评审**  
> **版本：v0.1**  
> **初稿日期：2026-10-09**  
> **文档级别：项目级（跨 Repository）**  
> **建议仓库位置：** `agentic-trpg/agentic-trpg/docs/MVP_SCOPE.md`  
> **适用范围：** Agent DM、State Machine、Rule Engine、Visual Presentation

## 0. 文档定位与决策状态

本文件定义 Agentic TRPG **首个可实际游玩的端到端 MVP** 的产品边界、游戏场景、跨模块职责与验收目标。它**不是** D&D SRD 的完整实现计划，也不替代各模块的技术设计、规则覆盖矩阵和 Backlog。

为避免在需求尚未讨论时过早锁定技术路线，使用以下标记：

- **[已确认]**：项目已经明确的架构方向或目标。
- **[建议]**：本初稿提出的 MVP 默认范围；需要项目负责人评审后才能成为正式需求。
- **[待决策]**：会显著影响实现范围、成本或系统接口的问题；不能由开发 Agent 擅自决定。

> **治理原则：** 当前文件中的「建议」不等于批准。只有经过明确确认并在决策记录中更新状态的条目，才能成为开发任务的强制验收条件。

## 1. 项目愿景与 MVP 定义

### 1.1 项目愿景

**[已确认]** Agentic TRPG 是一个模块化、可扩展、以 AI Game Master（Agent DM）驱动的 TRPG 平台。它应允许玩家通过自然语言和/或可视化界面参与冒险，并通过独立 Rule Engine 获得可靠的机械规则裁决，通过 State Machine 保持跨场景的权威世界状态，通过 Visual Presentation 展示事件与场景。

核心原则：**能由确定性程序可靠处理的规则计算，不交给 LLM 自行猜测；需要叙事、语义理解和开放式裁决的事情，不强行塞进 Rule Engine。**

### 1.2 MVP 的成功定义

**[建议]** 首个 MVP 的成功标准不是实现全部 SRD，而是：

> 一名玩家能够在 Agent DM 主持下，从创建或载入角色开始，完成一段包含 **NPC 交互、探索、检定、危险/陷阱、至少一次完整战斗、战利品或任务结果、休息/资源恢复以及场景转换** 的小型冒险；四个模块在此过程中共享一致的游戏状态，并能明确识别超出规则支持范围的请求。

一个真正完成的 MVP 必须是**可反复运行的 Vertical Slice**，而不是四个模块分别拥有可调用 API 的集合。

### 1.3 首版候选基线（均待确认）

| 维度 | 初稿建议 | 状态 |
| --- | --- | --- |
| 首个 RuleSet | D&D 2024，依据可合法使用的 SRD 5.2.1 内容 | [建议] |
| 冒险类型 | 叙事探索 + NPC 互动 + 具备战术规则的战斗 | [建议] |
| 验收等级 | 以 1–5 级角色及常见能力作为重点验收范围；**不删除已有高等级实现** | [建议] |
| 玩家模式 | 优先单人玩家；多人实时协作暂不作为 MVP 门槛 | [建议] |
| 初始角色 | 允许预设角色；角色创建器的完整程度另行决定 | [建议] |
| 战斗空间 | 2D 格子地图；高度与完整 3D 非 MVP 门槛 | [建议] |
| 运行形态 | 本地/单实例可运行优先，云端部署形态另议 | [待决策] |
| 冒险内容 | 先以一段可复现的精选小型冒险验收，而不是无限开放世界 | [建议] |

**重要区别：**「首版重点验收 1–5 级」不等于「系统只能支持 1–5 级」；「首版选 D&D」不等于 Agentic TRPG 的其他模块依赖 D&D 专属模型。

## 2. 四个模块及权威边界

| 模块 | 核心职责 | 权威范围 | 不应承担的职责 |
| --- | --- | --- | --- |
| **Agent DM** | 玩家意图理解；情节推进；NPC 对话与动机；选择检查要求、目标及叙事难度；对非机械问题作裁决；根据真实事件叙述结果 | **叙事与语义裁决**，在受控权限内向其他模块提交命令 | 自行伪造骰点、攻击命中、HP/Spell Slot 变化；绕开 Rule Engine 生成机械结果 |
| **State Machine** | Session、Scene、任务、探索对象、世界实体、时间线、跨场景流程与持久化；协调模块执行；校验和应用授权的世界状态变化 | **世界/剧情/会话状态**及跨模块操作协调 | 成为第二个战斗规则计算器；对 Rule Engine 的运行态 HP、Action Economy 等重复判定 |
| **Rule Engine** | Typed RuleSet；行动合法性；骰点和数值计算；攻击、豁免、伤害、效果与行动经济；权威战斗状态转换及规则事件 | **已支持的机械规则与战斗运行态** | 剧情理解、NPC 自由对话、生成视觉内容、完整开放世界状态管理 |
| **Visual Presentation** | 地图、Token、角色状态、行动反馈、事件与叙事呈现；接收玩家 UI 输入 | **展示层的临时交互状态**（例如选中目标、镜头、动画） | 作为权威来源修改游戏数据；用动画结果覆盖实际规则结算 |

### 2.1 状态所有权原则

**[已确认的目标原则] 同一种权威状态只能有一个计算/写入所有者。**

- 战斗中的 HP、临时 HP、Condition、行动预算、集中、持续效果、战斗位置及战斗 RNG：由 **Rule Engine** 负责裁决。
- Session、Scene、任务、NPC 关系、场景物体与游戏世界时间：由 **State Machine** 负责持有并持久化。
- 战斗结束、跨场景或其他明确的同步时点：以 **Rule Engine 输出的类型化 Result/Event** 为依据，由 State Machine 执行相应世界状态提交。
- 对于非战斗世界效果，Agent DM 可以提出有依据的裁决和操作请求，但其写入应经过 **State Machine 的授权与验证**；不允许绕开机械规则直接调整 Rule Engine 权威状态。
- Visual Presentation 只能呈现已经获准的状态和事件，不得将预测动画或 LLM 文本反向视作权威游戏事实。

**[待决策]** 跨场景持续 Effect、物品与装备状态、战斗中断恢复应如何在 State Machine 与 Rule Engine 之间转交所有权，需要在 `MODULE_CONTRACTS.md` 中定义。

### 2.2 目标交互流程（逻辑模型，非固定网络拓扑）

```text
玩家输入（自然语言 / UI）
          |
          v
        Agent DM
  理解意图 / 判断场景 / 形成命令
          |
          v
     State Machine
 授权 / 选择场景与状态 / 协调执行
          |
          +---- 机械规则请求 ----> Rule Engine
          |                         |
          |                 Preflight / Payment
          |                   RNG / Resolution
          |                 Typed Events / Result
          |                         |
          <-------------------------+
          |
          +---- 世界状态提交 / Scene 与任务更新
          |
          +----> Agent DM：基于结果撰写叙事
          |
          +----> Visual Presentation：基于权威状态与事件渲染
```

这表示**职责和权威方向**，不要求所有模块必须部署为独立后端服务；具体是否通过 Python 调用、HTTP、消息队列或 MCP 连接，属于后续技术协议决策。

## 3. MVP 游戏场景目录（Gameplay Scenarios）

以下是**[建议] 候选验收场景**，供评审取舍。只有进入最终验收清单的场景才形成 MVP 必需规则范围。

| ID | 场景 | 玩家体验 / 可观察结果 | 主要模块 | 建议优先级 |
| --- | --- | --- | --- | --- |
| G01 | 开始游戏 / 载入角色 | 创建 Session；载入人物、规则集与初始 Scene；展示当前能力和位置 | State Machine、Rule Engine、Visual | Core |
| G02 | NPC 对话与选择 | 自然语言对话、谈判、接受或拒绝任务；NPC 关系或任务状态更新 | Agent DM、State Machine | Core |
| G03 | 探索 / 搜寻 / 调查 | 发现线索、检查地点、移动至下一场景；必要时使用 Ability / Skill Check | Agent DM、State Machine、Rule Engine | Core |
| G04 | 物体交互与简单陷阱 | 开门、操作机关、尝试解除陷阱；失败可能触发 Save、Damage 或 Condition | State Machine、Agent DM、Rule Engine | Core（有限范围） |
| G05 | 常规战斗 | Initiative、Turn、移动、攻击、掩护、伤害、死亡/失能、敌人行动、结束条件 | Rule Engine、State Machine、Visual | Core |
| G06 | 精选法术 / 职业特性 / 道具 | 使用在范围内的 Ability；合法支付资源；持续效果与可选择目标准确结算 | Rule Engine、Agent DM | Core（精选名单） |
| G07 | 休息和资源恢复 | 短休/长休后 HP、资源及部分状态正确恢复；世界时间推进 | Rule Engine、State Machine | Core |
| G08 | 战斗后结算 / 任务推进 | 胜负、战利品、角色变化和任务结果进入世界状态；场景继续 | Rule Engine、State Machine、Agent DM | Core |
| G09 | 离开再返回 / 读取 Session | 先前选择、线索、任务、人物资源保持一致 | State Machine、Visual | Core（非活跃战斗） |
| G10 | 复杂召唤、变形与动态环境 | 若精选冒险需要则逐项加入；每个机制明确其可支持边界 | Rule Engine、State Machine | Optional |

### 3.1 代表性冒险（待确定具体剧本）

**[建议]** 使用一段不依赖复杂高阶魔法的短篇冒险进行端到端验收：

1. **酒馆/村庄：** 与委托人对话并取得任务；需要时进行社交检定。
2. **荒野/遗迹：** 搜寻线索、检查入口、开锁或处理陷阱；记录探索变化。
3. **地下室/遭遇战：** 在 2D 地图上遭遇敌人；执行移动、攻击、一次精选法术、至少一种资源与 Condition 交互。
4. **战斗后：** 处理胜负、战利品或情报；尝试休息与资源恢复。
5. **返回委托人：** 对话与任务收尾；关闭并重新读取 Session，结果一致。

此场景只是**产品验收样本**，不是对玩家故事内容的硬限制。Agent DM 可以叙述和接受开放式行动，但只有属于支持范围的机械效果才能由 Engine 权威执行。

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

**[建议]** 优先保证以下机制在明确的支持范围内正确：

- 基础 D20 检定、Advantage/Disadvantage、Ability/Skill/Save、DC 和来源追踪。
- Initiative、Round/Turn、Action/Bonus Action/Reaction、移动与目标合法性。
- Attack Roll、Damage、Crit、Resistance/Immunity/Vulnerability、Death Saves、Healing/Temporary HP。
- 常见 Conditions、Exhaustion、Effect 生命周期与 Concentration。
- 基础 2D Grid、LoS、Cover、范围目标和常用 AoE。
- 代表性 Spell/Feature/Item 的 Invocation 选择、支付、效果及失败回滚。
- Rest/Recovery、战斗结果输出以及向世界状态的安全转交。

这些是**需要具备的机制类型**，不是宣称已经完成全部 SRD 边界。具体覆盖必须由单独的 `Rule Support Matrix` 映射到真实规则条目和测试。

### 4.3 明确的首版非目标（待评审）

**[建议]** MVP 暂不以以下内容为发布门槛：

- SRD 5.2.1 **全部**法术、Feat、Monster、Magic Item 与完整职业等级覆盖。
- 复杂位面旅行、全面世界经济、真实物理模拟与完全自主的世界生成。
- 全 3D 空间高度、复杂飞行体积、大型生物多格占位及所有立体 AoE。
- 多人实时联机、分布式一致性、跨 Worker 战斗执行和生产级集群部署。
- 所有复杂召唤、复杂形态变化、任意 Ready/Reaction Trigger 的通用支持。
- 所有开放式叙事命令都能自动转化为机械执行。
- 高级动画、实时语音/视频、精细 3D 角色及完整 VTT 编辑工具链。

未支持内容必须被正确识别，**不能以无效果的“成功执行”充当规则支持**。

### 4.4 不支持规则时的行为

1. **机械规则不支持：** 在任何资源扣减、RNG 消耗或不可逆状态变化前返回结构化拒绝/能力不支持信息（若该执行路径支持 Preflight）；Agent DM 明确告知玩家限制或提供合法替代方案。
2. **需要 GM 裁决：** 明确切换为叙事/世界操作路径；仅在经过授权和验证后提交世界状态，不冒充 Rule Engine 的机械结算。
3. **混合型效果：** 将可执行的机械部分和需要 Host 裁决的部分清楚拆开；不得因一个规则的某个 Activity 可解析，就宣称整个规则效果已实现。
4. **不得静默变更规则：** 若要采用简化、Homebrew 或 DM Override，应留有操作来源与审计记录，并与正式 SRD 机制区分。

## 5. Visual Presentation 最小需求

**[建议]** 首版 Visual Presentation 是消费权威状态的**展示与交互层**，不是另一个物理或规则引擎。

最低能力：

- 展示场景背景/文字、玩家与 NPC/敌人的基础身份及状态。
- 在战斗中显示 2D 地图、角色 Token、当前位置、行动轮次、HP 与重要 Conditions。
- 显示规则事件结果（命中、未命中、豁免、伤害、效果开始/结束）及 Agent DM 的叙事。
- 允许文字输入和基础选择/目标输入，将操作转为结构化命令或交给 Agent DM 理解。
- 错误、不可用能力、等待裁决与已完成结算有明确反馈。
- 不依赖视觉动画本身来判定伤害、位移、行动资源或任务成功。

**[待决策]** 使用 Web/PixiJS、Foundry 适配、原生客户端或其他技术方案；首版美术资产来源和动态生成策略。技术选型不应先于 UI 验收场景确定。

## 6. 跨模块契约最低要求

**本节只列出产品层级的要求，不代替正式的 `MODULE_CONTRACTS.md`。**

### 6.1 Command

- 每次改变权威状态的请求能够追踪 Session、Scene、Actor、请求身份和具体意图。
- 如规则需要玩家选择攻击模式、目标、区域、法术效果或资源池，命令应显式携带选择，不让执行层猜测。
- 规则是否合法，以及哪些资源在成功后扣除，必须由相关权威模块决定。
- 不明确或非法命令应能够拒绝，拒绝原因可被 Agent DM 和 UI 理解。

### 6.2 Result / Event

- 输出区分：执行成功、规则拒绝、需要 GM 裁决、执行异常、已提交但响应失败。
- 规则事件具备确定的顺序、来源和可追溯的影响对象。
- 跨模块结果提交应避免重试导致重复扣费或重复写入。
- Agent DM 的叙述和 Visual Presentation 的显示必须根据已提交结果生成。

### 6.3 状态同步

- State Machine 应有明确的世界状态版本/变更边界；Rule Engine 有独立的战斗权威状态。
- 应建立战斗开始的输入快照与战斗结束的输出/结算协议。
- 需要继续生效的状态（例如 HP、资源、Effect、任务/物品）必须定义跨边界持有者。
- 首版是否需要**进行中的战斗跨进程恢复**尚未确定；在正式支持前必须公开说明限制，不以普通 Session 恢复能力暗示活跃战斗恢复能力。

### 6.4 适配现有 Rule Engine

当前已经存在的 Rule Engine 仓库是：

- <https://github.com/agentic-trpg/trpg-rules-engine>

根据 2026-10-09 的仓库审阅基准（`main`：`64dd920`），已有 `PlayerIntent`、`CombatEvent`、`LiveCombatView`、`CombatOutcome` 及 HTTP Bridge 基础。其能力审核与限制应由该仓库代码及对应审计清单持续维护。

**这些是现有实现的候选对接面，不表示四模块统一契约已经最终确定。** 新建 State Machine、Agent DM、Visual 仓库时不应复制 Rule Engine 内部状态机。

## 7. MVP 验收标准（End-to-End）

以下构成**[建议] 初版验收合同**；正式验收前还需确认测试角色、规则清单、剧情样本与参考规则来源。

| 验收 ID | 场景与操作 | 通过标准 |
| --- | --- | --- |
| A01 | 完整小型冒险 | G01–G09 中获准的 Core 场景在同一 Session 中贯通；可从开始走到明确的任务结果，无人工改数据库或私有 Engine 状态 |
| A02 | 对话与探索 | Agent DM 能解释自由文本意图；需要检定时获得真实 Rule Engine 结果；场景、线索、NPC/任务状态按裁决正确保存 |
| A03 | 常规战斗 | 在公共接口上完成 Initiative、移动、攻击、精选法术/特性、状态变化和战斗结束；Visual 显示与 Engine 事件一致 |
| A04 | 确定性重放 | 相同规则数据、初始状态、Seed 和命令序列产生相同的权威事件、结果与最终状态；外部叙事文本不要求逐字相同 |
| A05 | 不合法指令 / 不支持规则 | 拒绝不会先消费 Action、Slot、Charge 或 RNG，也不会留下半完成的状态；客户端能获知原因 |
| A06 | 重试与异常 | 在已支持的重试作用域内，同一操作不重复提交；意外失败不会造成资源/事件与状态不一致 |
| A07 | 战斗转交世界 | 战斗结束后 HP、Spell Slots、重要状态及获得的物品/任务进度正确进入 State Machine；资源归属不能被误记到目标角色 |
| A08 | 休息与后续场景 | 资源按所选规则恢复，世界时间/场景相应推进；后续场景读取到更新的状态 |
| A09 | 非战斗 Session 读取 | 保存并重新载入 Session 后，人物、场景、任务、关键选择与资源保持一致 |
| A10 | 规则覆盖声明 | 对选定的规则清单，逐项有 SRD/设计依据、可执行入口、边界说明和正反向测试；不能只依据代码行数或总测试数判定完成 |

**独立正确性要求：** 关键规则预期应来自 SRD 5.2.1 对应条文与明确记录的裁决，而不是仅复用引擎当前输出作为黄金真值。对于真实内容源和 SRD 差异，应保留 Provenance 与偏差说明。

### 7.1 最小黄金测试场景

**[建议]** 至少保留一条完整冒险 E2E，以及以下独立的边界回归：

- **支付一致性：** 一个被选择的动作只消费它应付的行动及资源；不会顺带执行物品/武器的其他 Activity。
- **状态与 RNG：** 非法目标、无资源、不支持机制及执行故障不污染游戏状态或随机序列。
- **跨模块同步：** HP/资源/Effect 从 CombatOutcome 写回世界时不会改变所属 Actor。
- **Agent 处理拒绝：** Agent DM 不把规则拒绝伪装成玩家成功，也不自行补写机械结果。
- **UI 权威性：** 战斗显示使用 Engine 已提交的状态与事件；叙事和动画不会产生额外伤害或位移。

## 8. 里程碑与开发决策顺序

| 阶段 | 目标 | 完成标准 |
| --- | --- | --- |
| **M0：Scope 冻结** | 讨论并确认首版游戏场景、规则子集、玩家模式、视觉要求和明确非目标 | 本文件由 Draft 转为 Approved，并形成决策记录 |
| **M1：Rule Engine Correctness Closure** | 修复影响通用场景的核心正确性问题 | 代表性动作/物品调用、资源归属、失败回滚和回归测试通过 |
| **M2：Cross-module Contracts** | 定义 Session、Scene、Command、Event、State 权威及跨模块结果转交 | 四模块可以按同一契约独立实现、测试 |
| **M3：Playable Vertical Slice** | 打通精选冒险的完整路径 | 一次游戏流程中完成探索、交互、战斗、结果持久化和可视反馈 |
| **M4：MVP Acceptance / Release** | 根据实际使用问题收敛规则范围并验收 | A01–A10 中批准的必需验收项通过，已知限制清晰公布 |

### 8.1 与当前 Rule Engine Backlog 的关系

- 规则引擎仓库的 `BACKLOG.md` 是**技术缺口清单**，不是跨项目 MVP 的任务清单。
- 不必为了完成 MVP 清空 `deferred` 法术/物品/职业能力。
- 每次选择新规则工作之前，应说明它服务于哪一个 Core Gameplay Scenario、消除了哪个共用机制缺口、能够验证哪些具体规则。
- Batch 的有效进度衡量包括：规则正确性、受支持机制的实际扩大、端到端场景可用性和跨模块一致性；不以 Commit 数、代码行数或新增测试数替代成果。
- 在当前已审阅的 Rule Engine 中，**修复 Invocation 多 Activity 误执行和 CombatOutcome 资源归属**仍是优先的正确性工作；后续机制扩展应等本项目的 MVP Scope 获得确认后再排序。

## 9. 待决策清单（Decision Register）

| ID | 必须讨论的问题 | 建议默认答案 | 状态 |
| --- | --- | --- | --- |
| D01 | 首版是否仅正式验收 D&D 2024 / SRD 5.2.1？ | 是；架构不锁死其他 RuleSet | [待决策] |
| D02 | 首版重点角色等级范围？ | 1–5 级；已有更高等级能力保留但不承诺完整覆盖 | [待决策] |
| D03 | 玩家形态与控制方式？ | 一名真人玩家 + Agent DM；支持一个或多个预设角色 | [待决策] |
| D04 | 必须支持哪些具体 Spell / Feature / Item / Monster？ | 从黄金冒险与共用机制反向筛选，形成独立规则矩阵 | [待决策] |
| D05 | 自然语言是否是主要操作入口？ | 是；允许 UI 指向与补充结构化目标选择 | [待决策] |
| D06 | Visual Presentation 技术栈与画面深度？ | 优先可编程 Web 2D 表现，暂不承诺特定技术 | [待决策] |
| D07 | 首版需要哪些持久化保障？ | 确保非活跃战斗的 Session/世界状态可保存及恢复；活跃战斗恢复另议 | [待决策] |
| D08 | 游戏规则之外的 GM Override 应如何授权和审计？ | 显式、有限权限、结构化并记录来源 | [待决策] |
| D09 | 冒险内容从何而来？ | 首版精选固定内容；是否支持用户剧本导入另议 | [待决策] |
| D10 | 部署模式及后端成本边界？ | 本地/单实例优先，浏览器客户端与自托管可能性分别评估 | [待决策] |
| D11 | 是否要求所有四个模块作为独立进程/服务？ | 不要求；代码与权威边界独立优先于部署拆分 | [待决策] |
| D12 | 哪些开放世界效果完全由 Host 判定、哪些必须有 Rule Engine 子机制？ | 以具体场景逐项审核，不做“一切由 LLM”或“一切由程序”式规定 | [待决策] |

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

> **本初稿的直接下一步：** 逐项讨论 D01–D12，形成首版批准的 Gameplay Scenarios 和精选规则清单；然后从这些场景反推 `MODULE_CONTRACTS.md` 与 Rule Engine 的下一轮开发优先级。
