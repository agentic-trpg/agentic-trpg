# SM 代码检索对照实验

这是 State Machine 生产 Python 源码的函数检索试点，不是三个仓库的完整检索验收。固定源码、问题、标注和逐函数摘要随实验提交，向量及完整排名留在被忽略的 `.local/`。阅读 [实验报告](REPORT.md)。

## 独立环境与运行

需要 Python 3.12，唯一第三方依赖为 NumPy。使用官方 Voyage HTTP API，不安装游戏依赖、SDK、GPU、向量数据库或图服务。

```powershell
cd D:\Projects\agentic-trpg\trpg-state-machine\.worktrees\code-retrieval-ablation\agentic-trpg\experiments\code-retrieval-ablation
python -m venv .local/venv
.local/venv/Scripts/python.exe -m pip install -r requirements.txt
# VOYAGE_API_KEY 由进程环境提供；不要把密钥写到命令、配置或报告。
.local/venv/Scripts/python.exe prepare.py prepare D:/Projects/agentic-trpg/trpg-state-machine
.local/venv/Scripts/python.exe build_texts.py
.local/venv/Scripts/python.exe retrieval.py selftest
.local/venv/Scripts/python.exe -m unittest -v test_experiment.py
.local/venv/Scripts/python.exe retrieval.py probe
.local/venv/Scripts/python.exe retrieval.py estimate
.local/venv/Scripts/python.exe retrieval.py index
.local/venv/Scripts/python.exe retrieval.py evaluate
.local/venv/Scripts/python.exe report.py
.local/venv/Scripts/python.exe audit.py
```

本次实际使用 Codex 自带 Python 3.12.14 / NumPy 2.3.5，无安装动作；未使用或修改 SM/RE 的环境依赖。示例命令安装的是可选独立复现环境。更换机器可编辑配置中的 source_root；源内容必须匹配清单，分支名本身不保证一致。

`config.example.json` 同时是本次运行配置，不含密钥。先检查估算、请求/token/费用上限及账户限额再运行 index。每次网络尝试预留预算；失败请求和结果未知也保留预留，不假设免费。只对 429 有限重试；认证、明确计费或其他错误停止。收到完整有效响应后按模型、维度、dtype、input_type、截断策略和文本哈希缓存。重新运行 index 只请求缺失文本。

不得并行运行两个 index。中断后已落盘缓存可复用；网络已接收但本地未保存的响应可能产生少量重复费用，HTTP 端点没有本实验可用的幂等承诺。固定源码漂移时脚本拒绝混用，需另建一轮清单、问题标注与摘要。

prepare 不导入生产包，只读取 src/**/*.py；build_texts 不读取问题、答案或结果；evaluate 在固定规则下对开发集和保留集各评估一次，没有选择参数。摘要新增或更新需要重新按源码审阅，不能凭旧摘要哈希自动代表新代码。

## 文件

- prepare.py：AST/tokenizer 节点、原始源码与哈希，明确嵌套/装饰器切分。
- summary-semantics.json / summaries.json：Codex 独立派生语义及 T0，上下文均绑定源码哈希。
- questions.json / annotations.json / freeze.json：20 开发问题、10 保留问题、人工式源码标注及冻结摘要。
- retrieval.py / test_experiment.py：缓存、安全 HTTP、精确余弦、中文 BM25、RRF 与指标。
- report.py / results/：可复算汇总、逐问题指标及 Top-10；完整 Top-50 在 .local。
- provenance.json / source-manifest.json / reading-manifest.json：版本、实际读取哈希及职责核对来源。

重新运行会更新派生指标和耗时，不应把不同运行的 JSON 混作同一轮结果。官方资料和局限见报告。
