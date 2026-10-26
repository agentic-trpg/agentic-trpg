# 源码说明与开发工作流程

2026-10-27。此规范适用于 SM、RE 及其自维护 Python 包；不改变业务、公开接口、
数据库、规则、依赖或运行架构。架构规则仍由 [Module Contracts](MODULE_CONTRACTS.md)
负责，产品范围由 [MVP Scope](MVP_SCOPE.md) 负责。当前源码说明描述实际行为，目标设计
和未完成能力在契约中另列，不能用历史摘要代替当前实现核对。

## 持续维护要求

- 新增模块、类、函数／方法时提供与复杂程度相称的 docstring。模块说明职责、主要
  入口和边界；类说明数据、生命周期和协作，不堆叠成员摘要；函数说明实际动作、
  返回值含义和必要输入约束。需独立理解的嵌套函数也适用。
- 数据模型和 Protocol 描述共同语义；重载声明不机械重复实现说明。简单访问器一句
  即可，不强制冗长模板，不复述类型注解。
- 重构改变职责、输入输出、副作用、异常或约束时同步修改说明；行为不变不要求
  重写全部旧说明。保留更完整旧说明中的关键约束，避免用短摘要覆盖。
- 复杂函数按实际需要解释候选／发布状态、事务、保存点、回滚、旧输入隔离、缓存
  版本／失效／重建、未知值、单位和失败语义。Stateless 工具不虚构持久状态；RE
  返回未提交结果，不提交 SM 世界事实。现存 Legacy 路径须按实际边界说明。
- 审阅检查说明与实现一致，尤其是异常、写入及缓存行为。规则来源沿用
  [References](REFERENCES.md)，不凭记忆补造结论。不把 TODO、计划或未经测量的
  性能／复杂度承诺写成事实。
- 沿用仓库语言约定，优先准确、一致、可维护；不为中文检索机械添加双语副本。
  不手工维护签名、完整调用清单、所属类、路径、行号或提交号，这些由工具提取。

## 系统总览与说明层级

三个仓库的 `docs/SYSTEM_OVERVIEW.md` 是结构／接口变更的精简阅读入口；本库的
[总览](SYSTEM_OVERVIEW.md)还解释文档权威和跨仓库分工。函数细节、模块背景、
仓库协作关系分别归函数说明、模块说明和系统总览；总览只做导航，不另立契约。
职责、状态归属、公开入口或跨库接口变化时检查并同步总览；局部函数或 docstring
修改不要求重读全部架构或机械更新总览。详细决定继续引用 MC 和相关领域 DOC。

## 运行原则的权威入口

[MC §2.3、§2.3a](MODULE_CONTRACTS.md#23a-实例字段关联与局部准入-decided)、
§2.4、§6.5–§6.6 及 [SM Architecture](STATE_MACHINE_ARCHITECTURE.md) 约束后续改动：
沿所属实例字段和关联索引读取有效事实及派生数据；普通局部操作不默认扫描 Session
或 Scene。修改路径维护相关版本、有效性和关联，实际消费者必须接入字段。
有效命中不应靠遍历所有依赖、全状态序列化或完整索引复制来重新证明有效性。
覆盖所有相关写入入口、候选阶段、保存点、回滚和恢复。SQLite COMMIT 与 RAM 发布
不是同一个 ACID 事务，遵循现有暂停／对账／重建契约。冷加载、必要全量消费者、
按需重建和有界内存保留仍合法，不能绝对禁止扫描。

以上是规范入口，不是本批运行验收。当前实现见
[本批核对](reviews/CODE_DOCUMENTATION_AND_SKILLS.md)；旧日期记录保留原有适用范围。

## 仓库级 Skills

按 [Codex 官方说明](https://developers.openai.com/codex/skills/) 使用
`.agents/skills/<name>/SKILL.md`，必需 YAML 字段为 `name`、`description`。
不依赖兄弟仓库自动发现，也不修改用户全局配置。AGENTS.md 的强制要求独立于触发。

| 仓库 | 安装工作流程 | 使用情境 |
| --- | --- | --- |
| SM | `trpg-runtime-change` | 实例字段、缓存、索引、Snapshot 和写入变更 |
| SM | `trpg-locality-review` | 真实调用链、冷热成本与规模证据审阅 |
| SM | `trpg-atomicity-review` | SQL、UoW、SessionMemory、发布及恢复审阅 |
| SM、RE | `trpg-code-documentation` | 新增／重构代码、补充和检查 docstring |
| 文档库 | `trpg-contract-sync` | 跨仓库契约、实现状态和证据同步 |

SM／RE 的源码说明 Skill 是同一流程的两份安装副本，均引用本文；修改通用流程时
同步并逐字比较两份 SKILL.md 及验证脚本。领域差异由各自源码和本地文档提供。
从 Skill 目录上溯至仓库根后，按逻辑工作区定位 `../agentic-trpg/docs/`；独立
worktree 也应提供平行 sibling。找不到时明确报告，不能用历史记录冒充已读规范。
静态格式／链接检查不等于实际触发验证，交付须区分。

## 历史实验与未来索引

固定实验分支 `experiment/code-retrieval-ablation`，版本
`35e79ce8d2ac81d0b62902cff429b52fdda05562`。2026-10-27 fetch 后远程仍是该版本，
没有后续提交；本批不整体合入实验分支。
[REPORT.md](https://github.com/agentic-trpg/agentic-trpg/blob/35e79ce8d2ac81d0b62902cff429b52fdda05562/experiments/code-retrieval-ablation/REPORT.md)
是结论入口；同一固定目录的 source-manifest、summaries、summary-semantics、
annotations、freeze、protocol-lock 及 README 保存语料、标注和方法。

实验仅覆盖 SM 的 83 文件／1,059 函数、30 个人工问题。源码基线已能找到多数入口，
摘要有助于部分 Top-5 相关覆盖；等权 RRF 未稳定优于合并向量。样本量、共同作者、
候选预算和非穷尽标注限制外推，不构成三个仓库或正式检索服务验收。

- 实验脚本、固定问题、标注、配置示例、摘要、排名及报告保留在 Git。向量、原始
  API 响应、临时索引和恢复缓存留在本地并忽略；不得整体忽略实验目录或删除历史。
  新增 `.gitignore` 不会取消已经跟踪的文件，须用 `git ls-files` 核对。
- 历史摘要保持固定，不随源码持续改写；只作为 SM 新说明的初稿。映射核对路径、
  所属类、完整限定名称和源码哈希；不能只按函数名或旧行号匹配。哈希变更时重读。
- 当前 docstring 是未来索引相应功能说明的主要维护来源。新索引读取当前源码、
  docstring 和自动提取的模块／类背景与结构元数据；源码已含函数 docstring 时，
  不应再次机械拼接同一文本，也不另建长期手工摘要副本。
- docstring 修改意味着检索输入改变，需更新受影响向量并记录新语料身份，旧向量
  不得标作当前版本。原 A/B/C 等实验固定在原语料，不能混用新旧输入比较或承诺
  复现旧指标。本批不调用 Embedding API，不建设 Code Graph、向量库、索引服务
  或新融合算法。

## 验证和交付

检查语法、仓库适用 lint／格式及 `__future__` 位置。与明确基线比较 AST，仅删除
Module／ClassDef／FunctionDef／AsyncFunctionDef 的首个字符串表达式 docstring，
不能删除任意字符串常量；签名、表达式和业务逻辑必须一致。检查 `__doc__`／
`inspect.getdoc` 消费，包括 API 文档及 CLI 帮助。AST 相等不能证明说明语义正确。

按实际风险验证复杂说明、Markdown 链接／锚点／表格／代码块、Skill 元数据及入口。
纯说明修改不默认运行整个游戏套件；有文档构建工具的仓库执行适用严格构建。
记录覆盖范围、补充和保留数量、实验复用／修正情况、命令退出码、未执行项与遗留
问题。发现业务缺陷记录位置和影响，不在本批顺手修复。仅暂存任务文件，按仓库
报告起始基线、分支、最终 SHA 和 push 结果；不自动 merge。
