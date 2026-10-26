# 系统与接口总览：架构、契约与开发协调

2026-10-27 源码核对起点：文档 `6bba7ab`、SM `a7b0804`、RE `f1a3235`。
这是面向首次进入仓库的 Codex 的导航页，不是另一份架构权威或可执行接口规范。
这里保存架构决定、目标契约、开发规范和核对证据，不运行游戏 Session。

## 1. 三个仓库如何协作

| 仓库 | 当前职责 | 实现／文档入口 | 不应混淆的边界 |
| --- | --- | --- | --- |
| `agentic-trpg` | 跨模块架构、范围、规范与协调 | 本页、[Module Contracts](MODULE_CONTRACTS.md) | 文档目录不是运行模块，也没有游戏服务入口 |
| `trpg-state-machine`（SM） | 可信命令、领域事实、Session 生命周期、持久提交与运行发布 | `src/trpg_state_machine/service.py` 的 `StateMachine` | 不是规则公式的第二实现，也不负责外部主体认证 |
| `trpg-rules-engine`（RE） | 明确输入下的规则求值、类型化素材和现存兼容宿主 | `packages/dnd5e-engine/src/dnd5e_engine/evaluation.py` 的 `evaluate` | Stateless 求值不提交 SM 世界事实；Legacy/Bridge 确有本地状态 |

通常三个 checkout 在同一逻辑父目录；独立 worktree 也按三库平行定位。
实现细节先读 [SM 总览](https://github.com/agentic-trpg/trpg-state-machine/blob/docs/source-docstrings-and-skills/docs/SYSTEM_OVERVIEW.md)
或 [RE 总览](https://github.com/agentic-trpg/trpg-rules-engine/blob/docs/source-docstrings-and-skills/docs/SYSTEM_OVERVIEW.md)。
链接指向本批分支，不表示已经合入 main；本地优先读取对应 sibling 的同名文件。

已有 SM 运行组件、受限 Stateless 求值、Bridge HTTP 和 Demo 不能等同于完整产品。
完整 Agent Host／玩家 UI、目标中的 Agent 调度与叙事闭环仍需各自实现和验收；
Bridge/Demo 的存在不能代替这些目标组件。范围由 MVP Scope 决定。

## 2. 文档模块及权威层级

| 文档／入口 | 核心职责 | 如何与其他材料协作 |
| --- | --- | --- |
| [Module Contracts](MODULE_CONTRACTS.md) | 最高跨模块状态、接口与一致性约束 | 目标示例和当前接口分开核对；§1 的旧版本索引不能代替源码 |
| [MVP Scope](MVP_SCOPE.md) | 产品目标、验收范围及明确排除项 | 决定本批是否扩展范围；不从现有代码反推产品上限 |
| [SM Architecture](STATE_MACHINE_ARCHITECTURE.md) | 领域所有权、Session 编排、提交及恢复设计 | 在 MC 内细化；对应实现还须查 SM 源码与本地验收 |
| [World Design](WORLD_SUBSYSTEM_DESIGN.md) | World、Scene、对象能力、空间与环境分责 | 细化 MC 的实例读取、关联和局部准入原则 |
| [Agent Architecture](AGENT_ARCHITECTURE.md) | Host、NPC 认知、感知与叙事目标 | 不把计划中的执行器、接口或闭环写成已有运行服务 |
| [Package Schema](ADVENTURE_PACKAGE_SCHEMA.md) | 创建参照、绑定、素材与实例化边界 | Package 提供创建输入，不补写已存在实例的缺失当前字段 |
| [Evolution Plan](GAME_CORE_EVOLUTION_PLAN.md) | 演进轨道、开放设计和后续验收门槛 | 计划不是已实现能力，避免另造重复待办体系 |
| [References](REFERENCES.md) | 规则版本、世界观和工程研究来源 | 区分官方规则、项目适配、工程选择与未核实信息 |
| 实现库领域文档与 Progress | 具体实现切片、限制、日期和原始验证 | 与实际源码、依赖 pin、测试共同构成能力证据 |
| `docs/reviews/` | 有范围和版本的审阅／验收记录 | 保留历史，不覆盖现行契约；见[实例归属核对](reviews/RUNTIME_INSTANCE_OWNERSHIP.md) |
| [源码说明规范](CODE_DOCUMENTATION.md) | docstring、审阅、索引输入和持续维护规范 | 源码说明描述当前行为；本页解释仓库结构 |
| [本地检索工具](LOCAL_CODE_TOOLS.md) | 可选的源码／DOC 检索与静态图导航 | 工具及索引在仓库外；使用前核对版本和最近检查，不代替当前源码或契约 |
| `AGENTS.md`、`.agents/skills/` | 强制工作要求和任务型流程 | Skills 引用权威文档，不另立架构规则 |

冲突处理：先区分“目标决定”和“当前行为”是否只是不同轴上的描述。
MC 是跨模块架构权威，MVP Scope 管范围，领域文档在其内细化；
源码和适当验收说明实际实现，但实现偏差不会自动改写 `[DECIDED]` 规则。
发现真实冲突应记录位置、影响和缺口，再在任务授权范围内处理。
历史 Review、未经验证的推断和目标 YAML 都不能充当当前接口凭据。

## 3. 代表性处理流程

### 运行请求的整体方向

1. 外部可信适配层先完成认证，构造 SM 的 `TrustedContext` 和类型化请求。
   本仓库没有提供一个已经部署的统一 Agent Host。
2. SM 创建／加载 Session，按权限、绑定、版本、幂等和领域前提接收命令。
3. 普通 World 操作由领域组件处理；需要 D&D 规则时，SM 构造固定 Snapshot、
   `RuleEvaluationRequest`、规则绑定及显式 RNG，将计算交给 RE。
4. RE 返回未提交 `RuleEvaluationResult`，包括适用的 Delta、事件和 RNG 后继。
   `accepted` 不是 SM 的 `committed`，也不是对外发布许可。
5. SM 重验关联和当前前提，在共享事务内增量持久化事实及必要证据／回执／可靠工作。
   SQLite COMMIT 后再受控发布 RAM，版本就绪后才能正常返回当前结果。
6. 已提交事件驱动可靠后续消费；NPC 模型只提出认知／行动候选，由 SM 再验证采用。
   这条方向描述已有接口责任，不宣称所有目标 Agent 消费者已接通。

### 一项开发任务如何进入实现

1. 核对三个相关分支、实际 HEAD、dirty 文件及依赖绑定，确认本批授权范围。
2. 先读本页定位仓库；结构／状态／接口问题再进入相关 MC、范围和领域章节。
3. 在实现库从公开入口追踪真实消费者及全部相关写入口，区分当前、候选和固定输入。
4. 修改后同步所需层级：函数／模块说明、系统总览、领域 DOC、接口或 Progress。
   简单局部函数修改不要求重读全部架构或修改全部文档。
5. 按风险检查实现与说明；日期化记录已执行、未执行和未验收事项，按授权提交。

## 4. 数据、状态和材料由谁持有

| 类别 | 实际持有／修改者 | 其他组件如何消费 |
| --- | --- | --- |
| 架构决定、规范、历史证据 | 各仓库 Git 中的对应 DOC | Codex/开发者读取；普通游戏运行不在线检索这些文档裁决规则 |
| 持久世界／角色／流程事实 | SM 的所属领域经共享 SQLite 事务维护 | 初始化／冷读／恢复取持久实例；不从 Package 补当前事实 |
| 已加载当前事实和运行实例字段 | SM `SessionMemory` 与领域 owner | 一致 RAM 范围内读取；修改阶段使用隔离候选 |
| 索引、重量、地图及环境等派生值 | SM 对应实例字段及缓存生命周期 | 依赖变化维护／失效，保留冷重建和有界保留，不是第二套事实权威 |
| 固定规则素材 | RE `FrozenRuleset`／SRD typed assets | 共享经验证的素材身份；getter 防御复制不等于缓存求值结果 |
| 固定请求和未提交规则结果 | SM 提供输入，RE 局部计算并返回提案 | 后续发布不能原地改变旧输入，结果由 SM 验证采用 |

详细规则统一引用 MC §2.3／§2.3a／§2.4、§4 和 §6，不在本页重建完整协议。
SQLite 与 RAM 不是同一个 ACID 事务；提交后发布失败须暂停并对账／重建，
不能把已提交事实报告成未提交失败，也不能继续提供过期当前状态。

## 5. 跨仓库接口查找

| 调用方向 | 当前输入／输出 | 应核对的真实位置 |
| --- | --- | --- |
| 可信宿主→SM | `CreateSessionRequest`／`TypedCommand`、`TrustedContext`→创建结果／回执／授权视图 | SM `models.py`、`commands.py`、`service.py` |
| SM→RE | 固定机械 Snapshot、`RulesetBinding`、`RNGContext`→未提交结果 | SM `rules_adapter.py`、`rule_execution.py`；RE `evaluation_contracts.py` |
| 素材加载→RE／SM 选择绑定 | `AssetLoader`→`FrozenRuleset`、有效内容身份 | RE `evaluation_ruleset.py`、Data `frozen.py`；SM 构造器和创建协调 |
| 模型宿主→SM NPC 接口 | 固定任务输入→`NPCEvaluationResult`→验证后的认知记录／输出交接 | SM `npc_evaluation.py`、`npc_results.py`、`npc_outputs.py` |

接口版本／支持范围是可变实现属性，查当前定义和测试；不能从 MC 目标样例冻结。
SM 安装的 RE 由它的 `pyproject.toml`／`uv.lock` 固定，不自动等于旁边 RE 分支。
需要区分“RE 源码已有能力”“SM pin 中已有能力”和“SM 实际采用白名单已支持”。

## 6. 按任务导航

| 任务 | 先读规范 | 再读实现／流程 |
| --- | --- | --- |
| 容器重量、实例字段或索引 | MC §2.3／§2.3a、World；SM 总览 | SM `world_containers.py`、`runtime_instances.py`、`session_memory.py`；runtime-change |
| 事务、发布或恢复 | MC §6、SM Architecture、Session Management | SM `storage.py`、`session_runtime.py`；atomicity-review |
| 新增规则求值能力 | MC §4、References、RE Stateless 合同 | RE admission／计算／Delta；SM 适配、pin 与采用范围另验 |
| NPC 任务、认知或输出 | MC §7／§9、Agent Architecture | SM 三个 NPC 接口模块；未来 Host 实现单独跟踪 |
| 跨仓库结构／接口同步 | 本页、相关 MC 和当前源码 | 本库 `trpg-contract-sync`；核对两边总览、DOC、Progress 和 pin |
| 局部说明修正 | CODE_DOCUMENTATION 和当前函数／调用方 | 实现库 `trpg-code-documentation`；无需机械改动系统总览 |

## 7. 维护与证据边界

模块职责、公开入口、状态归属或跨仓库接口改变时，同步对应实现库总览；
整体仓库关系或文档职责改变时再同步本页。细节仍以权威契约和当前源码为准。
本页不维护全部文件／函数／调用图，也不成为独立手工检索摘要库。
当前能力和未验收范围看各实现库的日期化证据；本批仅整理源码结构和说明。
完整恢复、未来多人、完整 Stateless 迁移及 Agent 产品闭环不能据此标为已验收。
本批核对与检查见[已有验收记录](reviews/CODE_DOCUMENTATION_AND_SKILLS.md)。
