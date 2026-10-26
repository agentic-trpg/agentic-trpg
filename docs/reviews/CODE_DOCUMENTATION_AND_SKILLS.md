# 源码说明与 Skills 核对 — 2026-10-27

## 分支、范围与原工作区

| 仓库 | fetch 后起始 origin/main | 独立任务分支 |
| --- | --- | --- |
| agentic-trpg | `88bb8dd47e006b511e2b61a4d228d19e1702bb60` | `docs/code-documentation-and-skills` |
| trpg-state-machine | `b9ae704abe4e5d049fa4664873662d7cf991ac39` | `docs/source-docstrings-and-skills` |
| trpg-rules-engine | `7bb02b955609f68fc78ff57dac2d51a0c2333366` | `docs/source-docstrings-and-skills` |

三个 origin 均为 GitHub `agentic-trpg/<仓库名>`。原 checkout 均在 main；文档库保留
未跟踪 `.worktrees/`、`docs/FIRST_BLUSH_MVP_REQUIREMENTS.md`，SM 保留 `.worktrees/`
和用户文本文件，RE 保留 `.evaluation-worktree/`。未覆盖原工作。任务 worktree 在
SM 的 `.worktrees/code-documentation-and-skills/` 下按三仓库平行放置。
三个新分支名在创建前均不存在，起点为各自 fetch 后 origin/main。

本批仅改变生产 docstring、开发规范／文档入口、AGENTS.md、仓库 Skills 及其 AST
验证脚本。无业务重构、公开签名、数据库结构、规则、依赖或游戏架构修改。
不修改 Pages，不整体合入实验，不 merge、不创建 PR、不请求付费 Embedding。

## 覆盖与说明来源

| 范围 | 模块已有→最终 | 类已有→最终 | 函数已有→最终 | 本批新增 |
| --- | ---: | ---: | ---: | --- |
| SM `src/trpg_state_machine` | 83→83 | 60→330 | 179→1,059 | 270 类、880 函数；80 文件 |
| RE 四个自维护生产包 | 186→192 | 275→515 | 813→1,658 | 6 模块、240 类、845 函数；154 文件 |

RE 包含 Engine、SRD Data、nat20-bridge、Demo 的 `src`；其中生产 CLI/audit 模块同样
覆盖。测试、examples、离线维护 tools、第三方／vendored／生成／临时文件不纳入
说明补齐；未为全部测试函数生成说明。包含嵌套函数；Protocol 和简单模型采用简洁
职责／约束说明，不生成与类型签名重复的长模板。

保留 SM 原有 322 处、RE 原有 1,274 处模块／类／函数说明，原说明值逐项比对相同。
SM 实验的 83 个文件哈希与本批起始源码全部相同；1,059 条候选摘要以路径、类和完整
限定名称（含嵌套作用域）映射，880 条用于缺失函数说明的初稿并改写为英文，已有
179 条函数说明保留。模块／类职责根据当前结构另写，不堆叠函数摘要。
RE 没有使用 SM 摘要，按当前 Stateless、数据加载、Legacy、Bridge/Demo 责任编写。

语义复核重点为命令提交、事务／保存点、未知 COMMIT、发布失败、规则采用、冻结
素材复制、伤害／集中和阶段证据。首轮 22 项定向复核修订中包含 6 个 SM 核心说明扩展，
以及 RE 同名节点的上下文修正，例如 HomebrewStore.remove 与 CombatObjectState.remove、
速度修饰器与运行态的 `__post_init__`、不同 candidate 的集中／死亡处理。
另扩展 24 处复杂入口说明，并纠正素材读取优先级、条件 slug 返回值和 Legacy View 共享值边界。
不能凭 AST 相同或覆盖率推定自然语言说明已获独立完整语义证明。

## 规范与工作流程

[统一维护规范](../CODE_DOCUMENTATION.md) 集中规定新增／重构同步说明、审阅一致性、
说明归属、保持既有约束、当前实现与目标分开、未来索引输入及实验保留。
三个 AGENTS.md 给出强制要求和本地 Skill 入口，不能以自动触发代替规范。

MC §2.3／§2.3a／§6 继续是实例读取、版本维护、候选／保存点／回滚／恢复、
持久提交后发布、冷加载和有界保留的权威；Skills 引用这些章节，不复制另一套契约。
当前入口新增日期化说明：SM main 已包含受限 SessionMemory／实例字段／重量／机关
及通路索引接线；10 月 21 日的未实现和后续“仅分支”记录保留历史语境，不能继续
当作当前 main 状态。既有证据未被重新计作本批运行验收。

| 仓库安装 | 流程 |
| --- | --- |
| 文档 `.agents/skills/trpg-contract-sync/` | 分支／接口／绑定／状态／证据同步 |
| SM `.agents/skills/trpg-runtime-change/` | 所有者、写入口、消费者、受影响版本与发布生命周期 |
| SM `.agents/skills/trpg-locality-review/` | 真实调用链、冷／重建／命中成本及无关规模对照 |
| SM `.agents/skills/trpg-atomicity-review/` | 按风险选故障点，比较 SQL／RAM／旧引用／索引／缓存 |
| SM、RE `.agents/skills/trpg-code-documentation/` | 说明维护、语义／结构核对及 AST 验证 |

六份安装的 SKILL.md 均通过 bundled `quick_validate.py`；Windows 使用 `python -X utf8`
避免系统 GBK 解码错误。SM／RE 的通用流程与验证脚本逐字一致。无全局安装／配置。
静态情境核对：新增容器重量字段→runtime-change；公开操作命中仍复制整索引→
locality-review；COMMIT 后发布失败→atomicity-review；跨仓库接口／状态同步→
contract-sync；SM/RE 新函数或说明过期→各自 code-documentation。
已确认入口、元数据、读取指引和逻辑 sibling 访问方式；未在新的 Codex 会话实际
验证自动发现、触发率或自主执行效果，此项仅静态验证。

## 验证证据和边界

- 两仓库 AST verifier 均退出 0：全部 83／192 个生产 Python 文件可编译，删除真正
  docstring 后的 AST 与各自固定基线相同，无签名、表达式或控制流变化。
- 验证器六项正反例通过：说明变化忽略，普通返回字符串、条件内字符串和签名变化
  仍能识别，嵌套说明正确处理，非法 `__future__` 位置由编译拒绝。
- 检查 `__doc__`／getdoc 消费。既有 audit 模块的 argparse 读取模块说明，原模块
  说明保留；RE API 的 mkdocstrings 和 Pydantic Schema 会暴露新说明。
- 使用既有 RE 环境比较 718 份 validation／serialization Schema：仅 description
  元数据可变，去除 description 后逐项相同。FrozenRuleset 的三字段绑定保持一致：
  evaluator `dnd5e-evaluation/37`，data revision
  `sha256:f1f2b8d5e9bef154940cb14c615f2f4ac7301a4ab9d869841bc1b86e9664c44e`。
- 两仓库适用 lint／格式、RE 严格文档构建和本批 Markdown 检查的最终命令／退出码见
  [SM 证据](https://github.com/agentic-trpg/trpg-state-machine/blob/docs/source-docstrings-and-skills/docs/reviews/CODE_DOCUMENTATION_AND_SKILLS.md)
  与 [RE 证据](https://github.com/agentic-trpg/trpg-rules-engine/blob/docs/source-docstrings-and-skills/docs/dev/source-documentation-acceptance.md)。

相关生成消费者的既有小范围测试 128 项通过；首轮 CLI 两项因临时父目录缺失而在 fixture 阶段报错，创建目录后单独重跑通过。两处历史 R23/R24 锚点补为跨 GitHub／MkDocs 的显式稳定锚点。
23 份本批 Markdown 的本地链接、显式／标题锚点、表格和代码块静态检查通过；无新增或剩余链接发现。三个仓库工作区／暂存差异检查作为提交门禁执行。
未执行完整游戏套件、新运行性能／故障验收、远程 Actions 状态验证或检索重跑。
AST 检查不验证自然语言正确性；Schema 对比的范围为实际选定模型，不声称所有动态
消费者均已穷尽。没有发现并顺手修复业务缺陷；原有受限恢复／Legacy 未完成等问题
保持原跟踪。最终提交 SHA 与 push 结果由 Git 和交付消息提供，不能自嵌到同一提交。

## 实验保留

fetch 后 `origin/experiment/code-retrieval-ablation` 仍为
`35e79ce8d2ac81d0b62902cff429b52fdda05562`，无后续差异。
固定 [REPORT](https://github.com/agentic-trpg/agentic-trpg/blob/35e79ce8d2ac81d0b62902cff429b52fdda05562/experiments/code-retrieval-ablation/REPORT.md)
及同目录语料清单、摘要、标注、方法、配置和排名保持原样。
Git 固定树中未发现 `.local`、向量或原始响应被跟踪；本批不复制这些本地文件。
新索引读取当前源码说明和自动提取背景，新说明不沿用旧语料／向量版本或旧 A/B/C
比较结论。正式图谱、向量数据库、自动索引与新融合算法均不在本批范围。
