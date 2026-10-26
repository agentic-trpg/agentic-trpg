# BM25 补充价值复分析协议 — 2026-10-27

本协议在本轮计算前写入。第一轮 30 问已被查看：本轮均为复分析／探索性分析，原 development/heldout 标签只作历史分层，不能视为新的独立验证。无新 API 请求；不修改第一轮输入、指标、排序或报告。配置见 [config.json](config.json)。

## 输入及隔离

使用 experiment/code-retrieval-ablation 原有独立 worktree，起点为已审阅的 35e79ce8d2ac81d0b62902cff429b52fdda05562；只修改本子目录，不合并 main/docstring 分支。

先核对原 protocol-lock、冻结问题／标签／摘要／脚本、source-manifest、缓存节点、向量键和向量内容。只从 SM Git 对象库的 b9ae704abe4e5d049fa4664873662d7cf991ac39 读取 src 文件，不读 SM/RE 当前源码。Git blob 与原清单字节如不同，仅允许在能精确匹配清单时恢复 LF→CRLF，逐文件记录两种哈希、长度和转换；不对送入模型的文本隐式归一化。恢复副本放在忽略的 .local/bm25-value/fixed-source，不是工作 checkout；分析器不修改它的已有内容。缓存 nodes 的源文本必须与该副本重新抽取的全部节点完全相同。

复用第一轮 T0、摘要，按原 combine 构造 A/B/C/T1，核对源哈希与摘要来源，确认缓存键绑定模型、维度、dtype、input_type、truncation=false、精确 UTF-8 文本哈希。核对全部缓存内容哈希、维度及有限值；重放四条向量路及 BM25 Top50，与原完整排名逐条比较。向量仍为 voyage-code-4 / 1024 / float，document/query 类型不变。BM25 复用原 T1、分词、k1=1.2、b=0.75、正分过滤及同分按节点 ID 规则。重放无需联网，不调用原 evaluate（会覆盖历史）。

## 预设比较

- 独有性：A、C 各 Top50 对 BM25 Top50；重合率同时报 intersection/50 和 intersection/min(实际长度)，Jaccard、独有候选、原标注内独有正确项及其 BM25 原排名、问题获益比例、并集长度与 Recall。
- 主要候选池：C Top50 对 C Top40 + BM25 未在已选 C40 中的前 10 条。只按前缀去重，追加项区分 C41–50 与 C50 外；不足保留实际长度，不回填。记录新增／丢失原标注相关项和入口、净增益、宏平均及微平均 Recall、获益／受损／持平和实际数量。
- 探索候选池：仅原 development 分层，预声明 45+5、35+15；主要方案固定为 40+10，不根据结果挑选“最优”。
- 最终列表：C Top10 对 C Top7 + BM25 未在已选 C7 中的前 3 条；前缀 C 顺序，尾部 BM25 顺序。沿用原 metrics：Hit/MRR 使用 entries，Recall 使用 related（含 entries）。报 Hit@5/10、MRR@10、Recall@5/10；新增／丢失、净值、获益／受损，及 C10 外正确项是否进入。
- 每种比较分别报原中文 zh、中文+原英文扩展 expanded，并保留原 split。问题—函数对应项按每个 condition 单独计数，不能将双语言相加称为独立问题；同一函数回答不同问题是不同对应项。
- 原标注外只称 unlabelled，不能视为已确认错误。不以结果改问题、摘要或原标注。补充审阅单独保存，若未来补标，指标必须另命名并注明事后补标非独立验证。本轮不进行事后补标。

## 重排边界及复现接口

已检查实验配置、已有工具及当前进程相关环境变量名；仅 Embedding 配置可见，没有明确授权且费用已知的 reranker。禁止用 Embedding key 推定 rerank 权限，不发探测请求。R1/R2 状态为 NOT RUN，真实请求数、输入量、耗时及新增 API 费用均为 0；模型账单不适用。

`rerank.py prepare` 可生成本地、无答案和检索分数的成对请求文件：R1=C50，R2=C40+BM25去重10；同 query、同原 C 文本、node ID 顺序、无截断、返回10。完整请求仅在 .local/bm25-value/rerank。未来运行需先锁定同一模型及不可变版本、接口、输入长度限制与 tokenizer、明确价格和请求/token/费用上限；超过输入限制两组一起失败。原请求哈希为缓存身份，默认不重试（避免未知响应重复计费）。

外部适配器返回各 request_key、全部候选 index/score；`rerank.py evaluate SCORES.json` 离线校验双组齐备、请求哈希、index 无缺失/重复、有限分数，再以 score 降序／ID 升序取10并复用原指标。输出独立 rerank-results.json，包含 provider usage、实际请求量、输入 token、耗时及费用估算；账单未知必须保留 null。此接口不自带网络或计费服务。

## 验证

少量 unittest 覆盖前缀去重、共同与真独有项、新增丢失净值、空和短列表、问题比例、标注分离、顺序和原指标语义。audit 独立从逐问题输出重算汇总，并校验新报告表格、原历史文件不变、链接／fence 与 git diff --check。不运行 SM/RE 游戏测试。
