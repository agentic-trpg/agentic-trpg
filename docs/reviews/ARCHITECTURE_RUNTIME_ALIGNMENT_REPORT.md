# Architecture and runtime contract alignment — 2026-10-20

本报告记录本批文档对齐及检查范围，不是第二份架构规范。共同权威为 [Module Contracts](../MODULE_CONTRACTS.md)；当前接口证据在 §1.6，通用校验／查询／Finalize 规范在 §2.3、§6.5–§6.6。历史 v0.4 Review 原文未修改。本次只提交 Markdown／AGENTS.md，不修改代码、tests、Schema、依赖、锁文件、Makefile 或 CI，不合并 main。

## Git 与工作区

三个仓库都先 fetch origin，再从各自最新 origin/main 创建 `docs/architecture-runtime-contract-alignment`。独立 worktree 位于原 SM 的 `.test-tmp/architecture-runtime-contract-alignment/` 下，三个目录并列，保留相邻架构读取路径。原工作区的私有资料、空文本文件及 RE `.evaluation-worktree/` 不纳入提交；既有 checkout 分支保持原状。

| 仓库 | 起始 origin/main SHA | 交付分支／目标远端 |
|---|---|---|
| agentic-trpg | `1ccf7192059bfe13a1bef4bb0b6e4a3adcf5116e` | `docs/architecture-runtime-contract-alignment` → 同名 origin 分支 |
| trpg-state-machine | `d5d8c494e2fa102ca924199b31a6d00c2b4910e2` | 同上 |
| trpg-rules-engine | `66384b00363c00fc92622dbbf77ccfea012b1b5d` | 同上 |

最终提交 SHA 与 push 后远端 ref 核验结果随本批最终交付消息报告；本文件不把尚未发生的 push 写成已完成。目标分支创建前本地和远端均不存在。RE `docs/agents-architecture-guidance` 与其 main 同指 `66384b0`，diff 为空，已有增强规范完整保留；没有盲目合并旧代码或删除分支。架构仓库本地尚未合入 main 的 `docs/player-input-fast-path`、`docs/restore-player-fast-path` 不在本批范围；未发现待迁入的 SM docs 分支。其他无关功能分支不做整合。

## 修改文件

各文件路径相对各自仓库根目录。

| 仓库 | 文件 |
|---|---|
| agentic-trpg | `AGENTS.md`（新增）、`README.md`、`docs/MODULE_CONTRACTS.md`、`docs/STATE_MACHINE_ARCHITECTURE.md`、`docs/WORLD_SUBSYSTEM_DESIGN.md`、`docs/ADVENTURE_PACKAGE_SCHEMA.md`、`docs/AGENT_ARCHITECTURE.md`、`docs/MVP_SCOPE.md`、`docs/GAME_CORE_EVOLUTION_PLAN.md`、`docs/reviews/ARCHITECTURE_RUNTIME_ALIGNMENT_REPORT.md`（本报告，新增） |
| trpg-state-machine | `AGENTS.md`、`README.md`、`docs/SESSION_MANAGEMENT.md`、`docs/GRID_SERVICE.md`、`docs/OBJECT_SPATIAL_SERVICE.md`、`docs/SCENE_LIFECYCLE_SERVICE.md`、`docs/CONTAINER_SERVICE_PROGRESS.md`、`docs/reviews/RUNTIME_VALIDATION_SCOPE_REVIEW.md`（新增） |
| trpg-rules-engine | `AGENTS.md`、`README.md`、`docs/dev/stateless-evaluation.md`、`docs/dev/validation.md` |

## A. 已修正的过时描述

| 旧描述 | 当前代码／测试依据 | 本批修正 |
|---|---|---|
| 完整实例化整体未实现，能力配置仍回查 Package | SM Schema39、InstanceData／WorldFacts.instances、实例无模板执行及真实旧库显式升级回归；INSTANCE_CONFIGURATION_PROGRESS | MC §2.4／§1.6、World §2.1a、Package／README／SM 文档改为现有读取闭包已实现、整体部分实现；动态 spawn／一般创建依赖及实例装备／Effects 生命周期继续缺失 |
| RE verify_ruleset 总是全量枚举摘要，SM 尚未固定复用 | RE FrozenAssetLoader／FrozenRuleset、freeze_ruleset／ruleset_binding、冻结／UUID 测试；SM Runtime 装配和实际生产路径计数回归 | MC §4.3／§1.6 与 RE／SM 开发规范确认固定对象快速校验；原始可变 Loader 的完整摘要例外、深拷贝及重建生命周期仍保留 |
| TimeDriver／倍率／Round 整体未实现 | SM SessionTime／TimeDriver、真实 RE Round 时间测试、恢复／等待测试和 SESSION_TIME_COORDINATION_PROGRESS | MC C13、World、SM Architecture、Package、演进表改为显式倍率／有界工作／Round 已接线；没有默认倍率，宿主策略 OPEN，未接通消费者保持缺口 |
| Availability 完全未实现 | RE engine-availability/13 共享基础攻击 preflight；SM PC／获准 NPC、无写入／撤权／版本回归 | MC §4.4／§1.6、MVP、SM Architecture 记录受限实现，通用操作查询和全目标目录未完成 |
| Grid 原始输入复用、独立 Grid／Environment／Scene 切片均缺失 | GridMaps／PreparedGrid、Environment 双版本缓存、SceneLifecycle 和对应测试／Progress | 当前演进表与 World 表订正；动态占用／SQL 局部化、完整 Terrain／Scene／生产提供方仍未完成 |
| 审计历史退出普通 RE 输入仍需从头实施 | 当前 engine-snapshot/17 不含 event_log，history-free 求值和 SM 适配已有实现 | MC §4、SM Architecture、演进计划标明已完成切片；保留审计和新规则完整依赖要求 |
| 旧 module-contracts/0.2 示例及 /23 pin 易被误认为当前 ABI | 当前 RE /24、Snapshot /17、Availability /13、StageFacts /2、evaluator /37；SM pin a011eba，包源码与 RE main 相同 | MC §1.6 完整字段／类型／状态／权限／采用范围矩阵；目标章节分清已实施部分与尚未冻结字段；旧 Review／日期化证据原样保留 |

## B. 新增的共同约束

MC §2.3 定义 Full Integrity Audit、Local Admission、Query／Projection、合法完整机械闭包及其他必要全量消费者，覆盖实际 SQL／JSON／模型／Snapshot／投影及间接调用。MC §6.5 明确普通共享提交不能默认审查全 Session；§6.6 C08 要求传递全部受影响实体／关系和中间候选状态，Finalize 调用所属领域必要验证。

已有全局检查必须先列不变量，证明持久约束和局部检查等价，再做后续代码替换。规模验收固定目标并增长无关 Scene／Object／Actor／Item，优先读取行数、解析／构建／投影／扫描次数，覆盖冷构建、命中、失效、维护和权限。缓存／索引须处理事务回滚、OCC、失败重试、生命周期及恢复，不能成为第二权威。

顶层 AGENTS 的校验政策索引、SM AGENTS 的 Development workflow、RE AGENTS 的 Global integrity audits 与 Current contracts sections 均引用 MC §2.3、§6.5–§6.6。World 只追加领域适用方式。RE 原有 check-plan／check-fast／check-integration／check-auto、Full 条件和 Commit／Push／Review／Snapshot／FrozenRuleset 原则均保留；SM 使用实际 uv／pytest／Ruff，无虚构 make check-fast。

## C. 仍需代码重构

详细函数、固定行号、实际范围、当前不变量和局部替代建议见 SM 分支的 [Runtime validation scope review](https://github.com/agentic-trpg/trpg-state-machine/blob/docs/architecture-runtime-contract-alignment/docs/reviews/RUNTIME_VALIDATION_SCOPE_REVIEW.md)。关键剩余项：

- 普通 commands 提交、RE Delta／Check 条件后果提交仍调用 Session 空间完整审查。
- OSS 单候选检查仍遍历整场景，摆放、Openable／bar／检定结果、耐久应用又触发 Session audit，多个层次可能重复。
- SceneLifecycle 恢复／初始化验收允许完整作用域；普通 ensure／重入仍重新检查整个目标场景，需等价局部保证。
- Container 的准入语义已覆盖移动子树与两端祖先，但 `_rows` 仍读取 Session 全部对象；不要重复实施已完成的邻接／重量复用。
- Character rule_components 先解析／验证 Session 组件与 portable inventory，再按 owner 过滤；sync_world_inventory 仍重建便携子集并遍历全部机械 Actor。
- Combat guard 需要局部 Encounter 兼容验证，但其中仍枚举所有场景定义；list_scene_objects 底层也枚举 Session 对象后过滤。
- Grid 接触／局部步进可能继承整场动态投影成本；完整地图导航规划有合法消费者。Environment 有效命中已有版本复用，冷读取及真实提供方仍须分别验收。

本批不修复上述代码，不宣称规模测试或性能收益。

## D. API 尚未统一

MC §1.6 分别列 Target、Current、Gap：实际 TypedCommand 与可信 TrustedContext 分离；actor_id 仍必填；CreateSessionRequest／CommandReceipt 是现有本地 dataclass，目标 JSON 不构成冻结传输 ABI；ReadVersion 当前采用 Session world fence；RE 操作／Delta 类型范围大于 SM 白名单；stage_facts 不是第二份写指令或感知证据。save／resume 是只读持久状态验收，不是任意活跃战斗 checkpoint。

world-source rules.effect、一般中途 Continuation、Turn／Round Episode 路由、统一 NPC Evaluation／Observation 与 Host Context、生产时间等待回复、完整 Effects／Activity／秒制 NPC／OB／Gate 消费、动态实例创建仍未全部实施；默认倍率、宿主等待策略及部分未来 Schema 仍 OPEN。不能为文档一致性改 API、降低验证或静默重绑 /36 存档。

## E. 检查与三仓库一致性

三个 AGENTS 已以共同顶层架构为工作入口，当前 ABI 来源及 consumer pin 均显式记录。文档同步不代表代码完全符合目标；上述差异仍然存在，三个交付分支也尚未合并 main。

- 顶层及 SM 无现成严格文档构建脚本／文档 CI，本批执行实际 Markdown 标题、相对链接／锚点、表格列、围栏和固定 SHA 源码路径检查；在最终交付记录报告计数。三仓库均检查 `git diff --check`、staged 范围及非任务文件保护。
- RE 使用既有 `python tools/validate.py fast --plan --base 66384b00363c00fc92622dbbf77ccfea012b1b5d`，即 make check-plan 的实际底层入口；当前机器无 make，未虚报执行 make。实际 Fast 入口 `python tools/validate.py fast --base <同一 SHA>` 最终 exit 0，115.52 秒：工具 Ruff／format／mypy、24 项 tooling tests、严格 MkDocs 均通过，未选择业务 pytest 或 examples。
- 初次 RE Fast 因沙箱解释器缓存权限、随后依赖下载 DNS 失败，均未算通过。改用获准执行环境、仓库内缓存和原有解释器，锁定同步后完整 Fast 通过；没有改依赖声明或锁文件。MkDocs 既有未列入 nav 页面 INFO 和 Material 提示不是构建失败。
- 本批未运行 SM／RE 业务全套、Focused Integration、Full、并发／故障／规模性能验收，也未声明远端 CI 成功：这是 docs-only 任务。已实现能力的执行证据只引用原日期 Progress，本批新增核对属于静态源码／测试证据。

必要文档均存在且已定向阅读；顶层 AGENTS 原先不存在，本批新增。原始 v0.4 Review 与所有非 Markdown tracked 文件保持原样，原工作区未跟踪内容保持不变。每仓库按文件选择暂存，分别提交／push 后等待用户与 ChatGPT 审阅，绝不自动合并 main。
