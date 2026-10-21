# Runtime reuse and references — 2026-10-21 文档记录

## 范围与起始状态

本批仅 Markdown／AGENTS.md，不实现缓存，不改业务代码、Schema、依赖、规则数据或 CI。三个仓库分别提交并正常 push，不 merge。开始前读取三仓库 AGENTS.md；已 fetch origin 核实下列 main 基线。无关未提交项与本批文件不重叠，原地保留，不暂存；SM 按任务直接在已有重构分支追加，保留全部既有提交。

| 仓库／cwd | 起始分支与 HEAD | 核实的 origin/main／实际工作分支 | 原有未提交项 |
|---|---|---|---|
| `D:/Projects/agentic-trpg/agentic-trpg` | `docs/runtime-reuse-and-references` / `bdbbdf31cc60f3e83a951541ddf7a70504526190` | main 同起始 HEAD；复用当前文档分支 | `docs/FIRST_BLUSH_MVP_REQUIREMENTS.md` 未跟踪，保留；起始 SHA256 `1DBA4ABD39C73F052F8FAC0043FF9FFF2D9DD79533BE7DA084DABCE27AE3C4F7` |
| `D:/Projects/agentic-trpg/trpg-state-machine` | `refactor/scoped-runtime-validation` / `4341f69cbb560edd9c9c1b1bd907ed6c599c0ed0` | `7927a382738fc97e2420967c3e1c6280c717d1fb`；直接追加到原重构分支 | 未跟踪 `新建 文本文档.txt`，保留；起始 SHA256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `D:/Projects/agentic-trpg/trpg-rules-engine` | `main` / `f18e0ad0d0bb6641efb050b51bf919dd41a8631f` | main 同起始 HEAD；从 origin/main 新建 `docs/runtime-reuse-and-references` | 未跟踪 `.evaluation-worktree/` 为已有独立 worktree，不修改、不加入提交 |

远端分别为 `https://github.com/agentic-trpg/agentic-trpg.git`、`https://github.com/agentic-trpg/trpg-state-machine.git`、`https://github.com/agentic-trpg/trpg-rules-engine.git`。RE 的 upstream 保持不变且不推送。已检查 worktree 清单；SM 指定分支由主目录使用，`.test-tmp/scoped-runtime-validation` 属于另一个 `codex/` 分支，不在那里替代本次工作。

## 决策与实现证据

通用原则集中补充 MC §2.3；World §2.1b 只细化容器，跨操作内存重量缓存为 `[DECIDED; NOT IMPLEMENTED]`。SM 指定分支**尚未合并 main**，单次操作的 ContainmentState.weights、relocate 清空及相关闭包准入的证据见 [MC §1.7](../MODULE_CONTRACTS.md#17-2026-10-21-运行时复用与资料核对)。原重构记录、v0.4 review 和旧 Progress 的日期／测试数字不改写。

规则基线不变；规则、世界观与工程资料的版本、用途、核实方式和未核实范围集中于 [References](../REFERENCES.md)。未读取三本完整规则书或 First Blush 正文，不新增设定。外部资料仅用于开发查阅，不增加普通运行时在线依赖。

## 验证边界

三仓库 `git diff --check` 均通过。对本批完整 Markdown 文件进行只读结构检查（不将检查脚本加入项目），结果如下：

| 仓库 | 文件 | 标题 | 相对链接／其中锚点 | 围栏对 | 表格 | 结果 |
|---|---:|---:|---:|---:|---:|---|
| 总文档 | 9 | 302 | 144 / 79 | 38 | 97 | 通过 |
| SM | 2 | 15 | 12 / 1 | 1 | 3 | 通过 |
| RE | 2 | 16 | 6 / 2 | 0 | 2 | 通过 |

RE 实际门禁入口为 `uv run --no-project python tools/validate.py fast --plan --base f18e0ad0d0bb6641efb050b51bf919dd41a8631f`：退出 0，但原有 `.evaluation-worktree/` 被选择器列为 unknown path，建议扩大至完整 workspace runtime 检查。该目录为已有无关 worktree；本次按用户 docs-only 范围使用同一既有工具的显式 `docs` 层级：`uv run --no-project python tools/validate.py docs --base f18e0ad0d0bb6641efb050b51bf919dd41a8631f`，执行 locked 文档环境与 `mkdocs build --strict`，退出 0，报告 `VALIDATION docs: PASSED in 22.22s`，没有业务测试。未执行被扩大选择的 fast／integration，也不声称它们通过。MkDocs 的既有非 nav 页面为 INFO，构建成功。

最终提交及 push 结果在交付消息中报告。没有重新运行 SM／RE 业务、性能或全量集成测试；没有将旧验收数字作为本次通过结果，也没有宣称远端 CI 通过。
