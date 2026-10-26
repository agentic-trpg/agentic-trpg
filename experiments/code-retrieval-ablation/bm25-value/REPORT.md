# BM25 补充价值 — 固定第一轮输入的复分析

日期：2026-10-27（Asia/Shanghai）。本轮只增加离线分析代码及结果，不更新生产源码、docstring、DOC、skills、问题、摘要、向量或第一轮指标。

**结论：BM25 找到了 C 遗漏的少量正确函数，但固定配额的净收益不稳定。当前继续采用 C Top10；暂不默认预留 3 个 BM25 名额。** 固定 50 候选的 40+10 在中文净减 1 项，在扩展查询净增 2 项；尚无 reranker 或新问题确认其最终排序收益。

## 性质、口径与输入

这是第一轮 30 问的复分析，新增的是配额策略比较；不构成独立验证。原 development=20、heldout=10 标签保留，二者均已看过。45+5、35+15 仅在原 development 上探索，主预设保持 40+10；没有根据结果修改查询或摘要，也没有制造新保留集。

正确项严格指原 annotations.related 内的项；entries 是相关集合的子集。Hit/MRR 沿用原 retrieval.metrics 的入口命中定义，Recall 使用 related。下表 Recall 默认是逐问题宏平均；另列微平均或对应项数时，分母为每条件 95 个原标注问题—函数对应项。中文与扩展条件各有 30 问，不将它们相加称为 60 个独立问题。unlabelled 只表示原标注外，不能当成已确认错误。

输入源码固定为 `b9ae704abe4e5d049fa4664873662d7cf991ac39`，原实验起点 `35e79ce8d2ac81d0b62902cff429b52fdda05562`。只通过 Git archive 读取该提交的对象库，未读取正在修改中的 SM/RE 源码。83 个文件均 exact_git_blob，与原 source-manifest 逐字节一致；本轮不存在 LF/CRLF 转换。节点原始源码保留原换行，未静默归一化。忽略目录下创建只读文件副本，重新抽取的全部节点与原缓存完整相同。

已核对 1059 个节点、4266 个去重向量（document/query）、原 T0、功能摘要及 T1 构造。voyage-code-4 / 1024 / float，input_type=document/query，truncation=false；原 combine、BM25 分词及 k1=1.2、b=0.75 不变。300 条 A/B/C/T/BM25 路线 Top50 全部从缓存重放吻合，原指标也吻合。模型名、input_type 从原配置和缓存键核验；第一轮未记录供应商不可变模型修订，响应本身不能独立证明 input_type。没有重新请求模型。

[输入审计](results/input-audit.json) 含原文件、节点及排名哈希、向量内容哈希根、逐源码文件双份字节身份；逐向量文本／内容哈希清单仍在忽略的 .local/bm25-value/text-vector-manifest.json。第一轮所有 37 个已跟踪实验文件的内容与审阅提交逐字节比较，未改动。协议、配置、汇总和逐问题结果分别见 [PROTOCOL.md](PROTOCOL.md)、[config.json](config.json)、[aggregate.json](results/aggregate.json)、[per-question.json](results/per-question.json)。

## BM25 Top50 的独有价值

重合率为 intersection/50，同时保存 intersection/min(实际长度)；本批各路实际长度均为 50，两种重合率相同。Jaccard 按每问计算再平均。并集是扩大候选预算后的覆盖上界，不能用作相同 50 候选方案的效果。

| 条件 | 向量路 | 独有正确对应项 | 获益问题 | 比例 | 向量Recall50 | 并集Recall | 并集微Recall | 重合率 | Jaccard | 并集平均长度（范围） |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zh | A | 9 | 7/30 | 23.33% | 82.50% | 91.39% | 91.58% | 26.20% | 0.1532 | 86.90（77–92） |
| zh | C | 5 | 4/30 | 13.33% | 87.50% | 92.78% | 92.63% | 28.73% | 0.1710 | 85.63（76–93） |
| expanded | A | 7 | 5/30 | 16.67% | 84.72% | 91.67% | 91.58% | 30.40% | 0.1818 | 84.80（78–92） |
| expanded | C | 5 | 4/30 | 13.33% | 85.28% | 90.56% | 90.53% | 33.33% | 0.2040 | 83.33（74–92） |

相同函数回答不同问题按不同对应项计数；两条件有重复，不应把各自的 5 项当作 10 个不同事实。A 只作辅助，以下主要解释 C。

| 条件 | 问题 | 领域 | C50 外原标注正确函数 | BM25 原排名 |
|---|---|---|---|---:|
| zh | Q05 | 环境快照 | `src/trpg_state_machine/environment.py::EnvironmentService.query_cell@767` | 2 |
| zh | Q05 | 环境快照 | `src/trpg_state_machine/environment.py::EnvironmentService._cell@543` | 31 |
| expanded | Q05 | 环境快照 | `src/trpg_state_machine/environment.py::EnvironmentService.query_cell@767` | 2 |
| expanded | Q05 | 环境快照 | `src/trpg_state_machine/environment.py::EnvironmentService._cell@543` | 38 |
| zh | Q08 | 光照 | `src/trpg_state_machine/domain_facts.py::WorldFacts.placement@1080` | 12 |
| expanded | Q08 | 光照 | `src/trpg_state_machine/domain_facts.py::WorldFacts.placement@1080` | 38 |
| zh | Q10 | 机关索引 | `src/trpg_state_machine/world_mechanisms.py::MechanismService._batch_index@547` | 25 |
| expanded | Q10 | 机关索引 | `src/trpg_state_machine/world_mechanisms.py::MechanismService._batch_index@547` | 13 |
| expanded | Q25 | 机关索引 | `src/trpg_state_machine/runtime_instances.py::TriggerIndex.__deepcopy__@99` | 3 |
| zh | Q30 | 恢复 | `src/trpg_state_machine/storage.py::SqliteStore.reconciliation@419` | 42 |

zh 的 C 补充领域：环境快照：2项（Q05）；光照：1项（Q08）；机关索引：1项（Q10）；恢复：1项（Q30）。

expanded 的 C 补充领域：环境快照：2项（Q05）；光照：1项（Q08）；机关索引：2项（Q10,Q25）。

上表给出原排名；部分正确项位置较后，单靠最前面的固定名额不会全部保留。A 的全部补充领域、问题和函数另保存在逐问题结果与汇总 topics 字段中。

## 相同候选预算：C50 对 40+10

先取 C 前40，再从 BM25 中排除这40个后取前10；没有排除整个 C50。追加项可能只是保住 C41–50。下表新增／丢失均相对原 C50。

| 条件 | 新增正确 | 丢失正确 | 净值 | 净获益/受损/持平问题 | C50 Recall | 混合Recall | 原/混合正确项 | 原/混合入口命中 |
|---|---:|---:|---:|---|---:|---:|---|---|
| zh | 2 | 3 | -1 | 2/3/25 | 87.50% | 86.94% | 83/82 | 100.00%/100.00% |
| expanded | 3 | 1 | +2 | 3/1/26 | 85.28% | 87.50% | 81/83 | 100.00%/100.00% |

| 条件 | 追加项总数 | 原在C41–50 | 真正C50外 | C50外正确进入 | 原/混合微Recall | 实际池长度（最小/最大） | 空池 |
|---|---:|---:|---:|---:|---|---|---:|
| zh | 300 | 19 | 281 | 2 | 87.37%/86.32% | 50/50 | 0 |
| expanded | 300 | 20 | 280 | 3 | 85.26%/87.37% | 50/50 | 0 |

本批 BM25 均有50个正分结果，所有池均达到50，无空列表；代码仍保留短列表，不填零分或其他路线。入口池命中均为30/30，没有因固定配额新增入口命中。

## 最终列表：C10 对 7+3

保留 C 前7的顺序，追加 BM25 未在这7项中的前3，保持 BM25 顺序。两组前5相同，Hit@5/Recall@5 不可能因本策略变化。

| 条件 | 方案 | Hit@5 | Hit@10 | MRR@10 | Recall@5 | Recall@10 | 实际长度 |
|---|---|---:|---:|---:|---:|---:|---:|
| zh | C10 | 96.67% | 96.67% | 0.638889 | 64.44% | 71.67% | 10 |
| zh | 7+3 | 96.67% | 96.67% | 0.638889 | 64.44% | 70.00% | 10 |
| expanded | C10 | 96.67% | 96.67% | 0.728889 | 63.33% | 74.72% | 10 |
| expanded | 7+3 | 96.67% | 96.67% | 0.728889 | 63.33% | 75.28% | 10 |

| 条件 | 新增正确 | 丢失正确 | 净值 | 净获益/受损/持平问题 | C10外正确进入 | 原/混合正确项 | 原/混合微Recall10 |
|---|---:|---:|---:|---|---:|---|---|
| zh | 4 | 6 | -2 | 4/5/21 | 4 | 68/66 | 71.58%/69.47% |
| expanded | 3 | 3 | +0 | 3/3/24 | 3 | 71/71 | 74.74%/74.74% |

中文净损失，扩展条件正确对应项总量持平，宏Recall10小幅上升；原因是每问相关集合大小不同，不能把宏平均上升解释为新增正确项总量上升。没有新增入口命中或 MRR 收益。净获益/受损按 related 数量净差分类；有新增/有丢失的问题数另在 aggregate 中保存，允许同问同时出现。结果不支持默认挤出 C8–10 给 BM25 保留3席。

## 逐问题变化与原分层

下表每条件每问列出新增/丢失/净值；对应候选 ID、独有列表、完整必要排名、长度与入口变化均见 per-question.json。

| 条件 | 问题 | 原split | 领域 | 40+10 新增/丢失/净 | 7+3 新增/丢失/净 |
|---|---|---|---|---|---|
| zh | Q01 | development | 容器重量 | 0/0/+0 | 0/0/+0 |
| expanded | Q01 | development | 容器重量 | 0/0/+0 | 0/0/+0 |
| zh | Q02 | development | 容器重量 | 0/0/+0 | 0/1/-1 |
| expanded | Q02 | development | 容器重量 | 0/0/+0 | 0/0/+0 |
| zh | Q03 | development | 嵌套容器 | 0/1/-1 | 0/0/+0 |
| expanded | Q03 | development | 嵌套容器 | 0/1/-1 | 0/0/+0 |
| zh | Q04 | development | 嵌套容器 | 0/0/+0 | 0/0/+0 |
| expanded | Q04 | development | 嵌套容器 | 0/0/+0 | 0/1/-1 |
| zh | Q05 | development | 环境快照 | 1/0/+1 | 1/0/+1 |
| expanded | Q05 | development | 环境快照 | 1/0/+1 | 1/0/+1 |
| zh | Q06 | development | 环境快照 | 0/1/-1 | 0/0/+0 |
| expanded | Q06 | development | 环境快照 | 0/0/+0 | 0/0/+0 |
| zh | Q07 | development | 光照 | 0/0/+0 | 0/0/+0 |
| expanded | Q07 | development | 光照 | 0/0/+0 | 0/0/+0 |
| zh | Q08 | development | 光照 | 1/0/+1 | 0/0/+0 |
| expanded | Q08 | development | 光照 | 0/0/+0 | 0/0/+0 |
| zh | Q09 | development | 机关索引 | 0/0/+0 | 0/0/+0 |
| expanded | Q09 | development | 机关索引 | 0/0/+0 | 0/0/+0 |
| zh | Q10 | development | 机关索引 | 0/0/+0 | 0/0/+0 |
| expanded | Q10 | development | 机关索引 | 1/0/+1 | 0/0/+0 |
| zh | Q11 | development | 空间查询 | 0/0/+0 | 0/0/+0 |
| expanded | Q11 | development | 空间查询 | 0/0/+0 | 0/0/+0 |
| zh | Q12 | development | 空间查询 | 0/0/+0 | 0/0/+0 |
| expanded | Q12 | development | 空间查询 | 0/0/+0 | 0/0/+0 |
| zh | Q13 | development | 库存版本 | 0/0/+0 | 0/0/+0 |
| expanded | Q13 | development | 库存版本 | 0/0/+0 | 0/0/+0 |
| zh | Q14 | development | 库存版本 | 0/0/+0 | 1/0/+1 |
| expanded | Q14 | development | 库存版本 | 0/0/+0 | 0/0/+0 |
| zh | Q15 | development | 事务失败 | 0/0/+0 | 0/2/-2 |
| expanded | Q15 | development | 事务失败 | 0/0/+0 | 0/0/+0 |
| zh | Q16 | development | 事务失败 | 0/0/+0 | 0/1/-1 |
| expanded | Q16 | development | 事务失败 | 0/0/+0 | 0/1/-1 |
| zh | Q17 | development | 保存点回滚 | 0/0/+0 | 1/0/+1 |
| expanded | Q17 | development | 保存点回滚 | 0/0/+0 | 1/0/+1 |
| zh | Q18 | development | 保存点回滚 | 0/0/+0 | 0/0/+0 |
| expanded | Q18 | development | 保存点回滚 | 0/0/+0 | 0/0/+0 |
| zh | Q19 | development | RAM 发布 | 0/0/+0 | 0/1/-1 |
| expanded | Q19 | development | RAM 发布 | 0/0/+0 | 0/1/-1 |
| zh | Q20 | development | 恢复 | 0/0/+0 | 0/1/-1 |
| expanded | Q20 | development | 恢复 | 0/0/+0 | 0/0/+0 |
| zh | Q21 | heldout | 容器重量 | 0/0/+0 | 0/0/+0 |
| expanded | Q21 | heldout | 容器重量 | 0/0/+0 | 0/0/+0 |
| zh | Q22 | heldout | 嵌套容器 | 0/0/+0 | 0/0/+0 |
| expanded | Q22 | heldout | 嵌套容器 | 0/0/+0 | 0/0/+0 |
| zh | Q23 | heldout | 环境快照 | 0/0/+0 | 0/0/+0 |
| expanded | Q23 | heldout | 环境快照 | 0/0/+0 | 0/0/+0 |
| zh | Q24 | heldout | 光照 | 0/0/+0 | 1/0/+1 |
| expanded | Q24 | heldout | 光照 | 0/0/+0 | 0/0/+0 |
| zh | Q25 | heldout | 机关索引 | 0/0/+0 | 0/0/+0 |
| expanded | Q25 | heldout | 机关索引 | 1/0/+1 | 1/0/+1 |
| zh | Q26 | heldout | 空间查询 | 0/0/+0 | 0/0/+0 |
| expanded | Q26 | heldout | 空间查询 | 0/0/+0 | 0/0/+0 |
| zh | Q27 | heldout | 库存版本 | 0/0/+0 | 0/0/+0 |
| expanded | Q27 | heldout | 库存版本 | 0/0/+0 | 0/0/+0 |
| zh | Q28 | heldout | 事务失败 | 0/1/-1 | 0/0/+0 |
| expanded | Q28 | heldout | 事务失败 | 0/0/+0 | 0/0/+0 |
| zh | Q29 | heldout | 保存点回滚 | 0/0/+0 | 0/0/+0 |
| expanded | Q29 | heldout | 保存点回滚 | 0/0/+0 | 0/0/+0 |
| zh | Q30 | heldout | 恢复 | 0/0/+0 | 0/0/+0 |
| expanded | Q30 | heldout | 恢复 | 0/0/+0 | 0/0/+0 |

原分层对照（**heldout 为历史标签，已非独立保留证据**）：

| 条件 | 原split | n | C独有补充项/问题 | 40+10净值 | C50→混合Recall | 7+3净值 | C10→混合Recall10 |
|---|---|---:|---|---:|---|---:|---|
| zh | development | 20 | 4/3 | +0 | 87.92%→88.75% | -3 | 71.67%→67.50% |
| zh | heldout | 10 | 1/1 | -1 | 86.67%→83.33% | +1 | 71.67%→75.00% |
| expanded | development | 20 | 4/3 | +1 | 87.50%→89.58% | -1 | 72.92%→72.50% |
| expanded | heldout | 10 | 1/1 | +1 | 80.83%→83.33% | +1 | 78.33%→80.83% |

仅原 development 的预声明探索配额（不据此选择最终策略）：

| 条件 | 配额 | 新增/丢失/净值 | 净获益/受损问题 | C50→混合Recall |
|---|---|---|---|---|
| zh | 45+5 | 1/1/+0 | 1/1 | 87.92%→88.33% |
| zh | 40+10 | 2/2/+0 | 2/2 | 87.92%→88.75% |
| zh | 35+15 | 2/1/+1 | 2/1 | 87.92%→90.00% |
| expanded | 45+5 | 1/1/+0 | 1/1 | 87.50%→87.92% |
| expanded | 40+10 | 2/1/+1 | 2/1 | 87.50%→89.58% |
| expanded | 35+15 | 2/1/+1 | 2/1 | 87.50%→89.58% |

## 标注及未运行的重排

[补充审阅记录](supplemental-review.json) 为 not_reviewed、空 items；本轮不补标，所有指标只使用原标注。逐问题 bm25_unique_unlabelled 可供未来源码审阅；若做事后补标必须另报，不能覆盖本结果或称为独立验证。

R1（C50→同一 reranker→10）与 R2（40+10→同一 reranker→10）**NOT RUN**。仅找到 Voyage Embedding 配置及对应环境变量名，未找到明确授权、价格及版本已知的 reranker；未用现有 key 探测。真实新增请求量=0，API 输入量=0 token，API 耗时=0秒，新增API费用=0美元；未产生可比较的重排成绩，实际账单不适用。

已提供 [rerank.py](rerank.py) 的 prepare/evaluate 离线接口；prepare 将120组请求模板放入忽略的 .local，不发送网络请求。两臂按相同 query、原 C 文本、长度策略（无截断）、节点ID顺序、模型与版本配对；不传标签或原检索分数，score同分按ID。默认模型/版本为空、预算0，不能误称为已运行。补跑须指定可用的本地 reranker 或获授权的模型API、不可变版本、上下文限制/tokenizer及价格与上限；适配器需返回完整索引分数、真实请求/token/耗时/估价并保留未知账单为null。未知响应默认不重试。

## 建议和证据边界

当前保留 C Top10 作为默认返回，C50作为固定池基线。BM25 可作为显式辅助发现路线；50+50并集上界证明了少量互补，不能证明固定预算或最终Top10的净提升。扩展查询的40+10可保留为下一次严格配对重排的候选方案，中文的净下降也必须同时报告。没有证据支持默认采用7+3。

若做确认实验，先冻结查询语言、40+10或其他唯一主方案、同一重排模型/输入策略和评价指标，再采集未参与选择的新问题，单独记录来源、源码审阅流程和标注者；不以这30问选配额后宣称独立验证。当前不足：样本小、标注可能不完整、同一代理参与原摘要与标注、无重排结果、无新问题复现，也不外推到RE或三个仓库全量生产检索。

## 复现与验证入口

在原 experiments/code-retrieval-ablation 目录使用已有 Python+NumPy（不需安装游戏依赖）：

```powershell
python bm25-value/analyze.py --sm-git D:/Projects/agentic-trpg/trpg-state-machine/.git
python bm25-value/render_report.py
python -m unittest discover -s bm25-value -p test_analysis.py -v
python bm25-value/rerank.py prepare
python bm25-value/verify_results.py
git diff --check
```

analyze 只重写本子目录派生结果和自己的 .local/bm25-value，不调用第一轮 evaluate。测试与独立审计涵盖去重前缀、共同/真正独有项、得失净值、短列表、比例、标注隔离、顺序及指标，并逐问题重算汇总。实际执行退出码见 [validation.json](validation.json)；不声称SM/RE游戏测试或GitHub Actions通过。
