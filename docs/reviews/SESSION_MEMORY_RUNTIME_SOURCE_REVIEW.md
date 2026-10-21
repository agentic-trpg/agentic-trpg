# Session memory runtime source review — 2026-10-21

## 决策、实现与证据等级

Architecture Decision Status **[DECIDED]**：活跃事实由统一 Session RAM 一致读取，隔离候选，SQLite 每次修改短事务增量提交后发布 RAM，版本就绪再正常返回成功及投影。最高规范为 [MC §0.3、§2.3–§2.4、§4、§6](../MODULE_CONTRACTS.md#23-运行时数据复用派生-snapshot-与版本有效性-decided)。

Implementation Status：**完整 Session 内存运行层与发布故障协议 [NOT IMPLEMENTED]**。现有事务、固定输入、实例配置、局部查询及派生缓存是可复用的部分基础，不能以名称或存在一个 publish 方法判定目标完成。具体内存组织、访问 API、细粒度版本／锁及 ABI **[OPEN]**。

Acceptance Status：本次**只做源码／测试源码静态核对和文档检查**，未执行业务测试、性能／规模／故障注入／多人验收。原有带日期 Review（尤其 v0.4）和 Progress／测试结果保留原证据范围；本报告补充新决定，不改写历史。

## 工作区与固定基线

开始 cwd `D:/Projects/agentic-trpg/agentic-trpg`。三个原仓库均在 main，fetch 前 HEAD 与 origin/main 相同，fetch 后远端基线未变；目标分支本地和 origin 均未占用。SM 必需提交祖先检查通过。origin 均为 `https://github.com/agentic-trpg/<repository>.git`；RE 另有 tapestria/nat20 upstream，本次未写 upstream。

| 仓库 | 起始 HEAD／fetch 后 origin/main／源码 SHA | 原有无关内容 |
|---|---|---|
| agentic-trpg | `8cdfc18390d105ff1d4c19ba70712276afb3eee8` | 未跟踪 `docs/FIRST_BLUSH_MVP_REQUIREMENTS.md` |
| trpg-state-machine | `d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34` | 未跟踪 `新建 文本文档.txt` |
| trpg-rules-engine | `34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a` | 未跟踪 `.evaluation-worktree/`（已注册旧分支 worktree） |

三个新分支均为 `docs/session-memory-runtime`，从各自最新 origin/main 创建，隔离 worktree 并列于 `D:/Projects/agentic-trpg/agentic-trpg/.worktrees/session-memory-runtime/<repository>`。逻辑 sibling 文档从并列目录正确解析（`../agentic-trpg/docs/`），不读取旧平行任务文档冒充本批。原 worktree／分支／未跟踪文件保留；不 reset、stash、rebase、force push、删分支或 merge main。只提交本任务 Markdown／AGENTS.md，不改 ChatGPT Page。

## SM 实际调用链与目标差距

以下链接全部固定 SM `d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34`；入口与内部实现实际阅读，不从旧 Review 推断当前 main。

| 入口／源码 | 静态核对的实际行为 | 目标迁移与限制 |
|---|---|---|
| [service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/service.py)、[domain_facts.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/domain_facts.py)、[instance_data.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/instance_data.py) | read_session→只读事务→_snapshot 多表读取／JSON 装配；Facts／Records 同文件按域访问 SQL，实例配置通过 InstanceData | 已加载有效事实与 Snapshot／角色视图应统一从 RAM，当前尚非免 SQL 装配路径 |
| [commands.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/commands.py) 的 CommandRuntime | submit_command 先授权读取／_snapshot，世界路径写事务及 savepoint 应用、expand、publish／finish，退出事务后返回 | 玩家命令仅是入口之一；候选隔离、提交后运行事实发布须补，保留拒绝／冲突／pending_choice 与合法失败成本 |
| [rule_execution.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/rule_execution.py)、[rules_adapter.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/rules_adapter.py)、[mechanical_runtime.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/mechanical_runtime.py) | 真实 RE 读取 Snapshot／RNG，事务外求值、deepcopy，写事务重验／重建 Snapshot 和 RNG；合成路径独立 | 固定必要输入来源改 RAM，保留完整闭包和提交校验，不因单写者取消 OCC；聚合 JSON／请求依赖改造不能仅靠 RAM 宣布完成 |
| [session_runtime.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/session_runtime.py) | publish 要求写事务，推进 SQL world_version 并调用 EventPersistence；finish 保存回执；receipt／replay 从持久表读取 | 当前 publish 不是 COMMIT 后 RAM 当前事实发布；需要内存版本就绪门槛，持久回执对账继续可用 |
| [storage.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/storage.py)、[scoped_reads.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/scoped_reads.py)、[derived_cache.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/derived_cache.py) | 外层 BEGIN／COMMIT／ROLLBACK；COMMIT 后循环发布 derived_pending；memo 受 total_changes 和 savepoint 回滚失效，事务结束清理 | derived cache 与操作 memo 不是完整运行状态；SQL COMMIT 后 RAM 发布异常的暂停／重建尚无完整协议，不能把外层 rollback 当作撤销已提交 SQL |
| [event_capture.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/event_capture.py)、[event_persistence.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/event_persistence.py) | 生产者冻结阶段证据；_append_events 分配序号，保存 events／Evidence／records／event_outbox 并入队 | 候选阶段取证接入统一读取；可靠投递不替代运行事实发布，投递失败不能回滚持久事实 |
| [npc_evaluation.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/npc_evaluation.py)、[npc_results.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/npc_results.py)、[npc_modes.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/npc_modes.py)、[npc_outputs.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/npc_outputs.py) | Task／Meta／Result／模式及交接有独立 _transaction(write=True)；Result 校验 Task 状态／NPC 版本，保存 Meta、唯一回执和输出交接 | 不能只改 CommandRuntime；这些实际写入口也参与唯一协调及 RAM 发布，保留既有稳定工作键／防旧资格 |
| [time_coordination.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/time_coordination.py)、[session_runtime.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/session_runtime.py)、[activity_handler.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/activity_handler.py)、[world_mechanisms.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/world_mechanisms.py) | 有界时间步骤、Pending Work、真实 Round／机关重置及联动沿领域接口；部分系统路径自建事务 | 全部真实写入统一盘点，保持唯一 game_tick，Effects／Activity 等未完成消费者不冒称完成 |
| [grid_maps.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/grid_maps.py)、[grid.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/grid.py)、[world_containers.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/world_containers.py) | GridMaps.scene 先 SELECT state_json，以内容键复用；ContainmentState 建邻接／weights，relocate 清 memo | 接入统一 RAM 后有效读取不再为同批事实反复查库／装配；重量跨命令缓存未实现 |
| [world_mechanisms.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/world_mechanisms.py)、[runtime_integrity.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/runtime_integrity.py)、[scene_lifecycle.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/scene_lifecycle.py) | _build_index 扫实际实例机制配置，_batch_index 在调用方批次 prepared 中复用；Schema40 局部占格／结构证书支持场景准入 | 机关跨命令索引与完整 Session RAM 待实施；Schema40 和局部准入已有成果保留，不能以历史 `_check_scene` 推断普通路径仍全局审查 |
| [service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/src/trpg_state_machine/service.py) save_session／resume_session | save 注明修改已持久化，仅校验／读取；恢复校验绑定、结构、空间及受支持机械事实，resume 委托 save | 不把 save 当唯一持久入口或完整命名备份；先对账／重建 RAM 再开放；活跃 combat process_id／combat_unrestorable 限制保持 |

### 测试源码与历史运行证据分开

本次阅读 [test_session_management.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/tests/test_session_management.py) 的绑定来源、错误结果拒绝、创建故障回滚、延迟 NPC 创建回滚与缺字段拒绝恢复；[test_grid_service.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/tests/test_grid_service.py) 的候选回滚／旧 View 不变与并发 SQLite 读取隔离；[test_scoped_runtime_validation.py](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/tests/test_scoped_runtime_validation.py) 的局部规模、savepoint／旧 reader 索引、任务授权范围与每级联一次机关索引等用例。这些现有断言保护各自当前能力，**没有运行，也不是完整 RAM 运行层的测试证明**。

历史 [Scoped runtime acceptance report](https://github.com/agentic-trpg/trpg-state-machine/blob/d6be5a99b12fefcf8cfc57fdebb81493c1ac4d34/docs/reviews/SCOPED_RUNTIME_VALIDATION_REFACTOR.md) 记录 Schema40、分区 JUnit 共 2,015 个不同通过用例及透明计数；本次未重跑、未重新核验原 JUnit 文件，不能记为本次通过。其他领域 Progress 同样保留原批次证据。

## RE 边界与固定输入

源码固定 RE `34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a`；[evaluation.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a/packages/dnd5e-engine/src/dnd5e_engine/evaluation.py) 的 evaluate 深拷贝／验证请求、核对素材绑定，不持久化 Session；[evaluation_contracts.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a/packages/dnd5e-engine/src/dnd5e_engine/evaluation_contracts.py)、[evaluation_state.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a/packages/dnd5e-engine/src/dnd5e_engine/evaluation_state.py)、[evaluation_ruleset.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a/packages/dnd5e-engine/src/dnd5e_engine/evaluation_ruleset.py) 保持 Evaluation `/24`、Snapshot `/17`、Availability `/13`、evaluator `/37` 与 stage facts `/2`。SM pyproject／lock 仍固定 Engine／SRD `a011eba3ea2226e22d8081294ee38d3ec193b325`，不因读取 RE main 自动升级。

阅读 [test_frozen_ruleset.py](https://github.com/agentic-trpg/trpg-rules-engine/blob/34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a/packages/dnd5e-engine/tests/test_frozen_ruleset.py) 的源数据／getter 深层隔离、固定绑定不扫描素材与不同素材集引用生命周期；这是固定规则素材的已有保护，不能推定任意 SM DTO 或运行结构都不可变。RE 从 SM 获取同版本、必要机械闭包完整的固定输入，不访问 SM SQL 或修改共享运行对象；结果仍未提交。跨进程／进程内／只读结构复用均不改变此边界，不恢复 Legacy Stateful 世界。

## 后续实施与实际检查记录

沿 [演进计划 §8.1a](../GAME_CORE_EVOLUTION_PLAN.md#81a-session-内存运行层的依赖阶段2026-10-21) 和既有 C-25／C-27／A2／DS 跟踪。先盘点与边界，再以现有物品转移验证加载／候选／跨域库存／提交／重试／恢复；接一个真实 RE 操作覆盖 RNG；逐域纳入后台入口、索引缓存，正确性充分后测 5–6 玩家及适量 NPC。API、存储细化及负载阈值不在本批冻结。

实际执行的检查如下（均为本地证据，不推定远端 CI）：

| 检查 | 结果／范围 |
|---|---|
| fetch／baseline／branch／status／worktree／SM 必需提交 ancestry | 三仓库最新 origin/main 确认；新分支未占用；隔离工作区创建成功 |
| `check_docs.py`（任务目录临时检查器，不提交到任何仓库） | 30 Markdown 文件；685 个标题、75 个 fenced block、188 张表；619 条链接中检查 362 条本地链接、37 条本次固定 SHA 源码链接及 5 条配套分支链接，路径／锚点无错误；外部历史网络链接未逐条在线验证 |
| 各仓库 `git diff --check`、`git diff --cached --check` 与 staged diff 审阅 | 通过；只暂存本任务 Markdown／AGENTS.md；没有业务／测试／Schema／依赖／锁／CI 改动 |
| RE `python tools/validate.py fast --plan --base 34ce8e764c1a8b1d5be2c4465a013e322fdbbc5a` | docs=true、tooling=true、packages=[]、tests={}；无业务测试 |
| RE 同基线 `python tools/validate.py fast --base ...`，`UV_OFFLINE=1` 使用现有全局缓存 | **exit 0，218.90s**；Ruff check／format、严格 mypy、24 项 validation 工具测试及 `mkdocs build --strict` 通过；严格文档构建自身 8.07s |
| RE 初次环境准备失败 | 使用另一本地缓存尝试下载 colorama 时 PyPI TLS handshake EOF，sync exit 2；未进入测试／构建，不算通过。随后全局离线缓存完整通过，无依赖配置／锁文件修改 |

原工作区 main／无关未跟踪内容保留，生成的环境／site 只位于新隔离 worktree 的忽略目录。提交及远端分支 SHA 以最终交付报告和 Git refs 为准，本文件不自引用自身最终 commit。尚未执行 SM／RE 业务运行、故障注入、性能、多玩家或新恢复验收；完整 RAM 层、发布异常恢复、跨命令重量／机关索引仍待实施。SQLite 隔离／备份官方资料的本次查阅范围另登记 [References](../REFERENCES.md#2026-10-21-session-ram-设计的工程补核)。
