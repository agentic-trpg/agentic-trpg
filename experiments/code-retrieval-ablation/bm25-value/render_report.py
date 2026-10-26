"""Render every numerical table from the committed per-question results."""

# Markdown paragraphs and table rows intentionally remain single output lines.
# ruff: noqa: E501

from analyze import HERE, OUT, load


def pct(x):
    return f"{x * 100:.2f}%"


def render(groups, records, audit):
    lines = [
        "# BM25 补充价值 — 固定第一轮输入的复分析",
        "",
        "日期：2026-10-27（Asia/Shanghai）。本轮只增加离线分析代码及结果，不更新生产源码、docstring、DOC、skills、问题、摘要、向量或第一轮指标。",
        "",
        "**结论：BM25 找到了 C 遗漏的少量正确函数，但固定配额的净收益不稳定。当前继续采用 C Top10；暂不默认预留 3 个 BM25 名额。** 固定 50 候选的 40+10 在中文净减 1 项，在扩展查询净增 2 项；尚无 reranker 或新问题确认其最终排序收益。",
        "",
        "## 性质、口径与输入",
        "",
        "这是第一轮 30 问的复分析，新增的是配额策略比较；不构成独立验证。原 development=20、heldout=10 标签保留，二者均已看过。45+5、35+15 仅在原 development 上探索，主预设保持 40+10；没有根据结果修改查询或摘要，也没有制造新保留集。",
        "",
        "正确项严格指原 annotations.related 内的项；entries 是相关集合的子集。Hit/MRR 沿用原 retrieval.metrics 的入口命中定义，Recall 使用 related。下表 Recall 默认是逐问题宏平均；另列微平均或对应项数时，分母为每条件 95 个原标注问题—函数对应项。中文与扩展条件各有 30 问，不将它们相加称为 60 个独立问题。unlabelled 只表示原标注外，不能当成已确认错误。",
        "",
        f"输入源码固定为 `{audit['source_commit']}`，原实验起点 `35e79ce8d2ac81d0b62902cff429b52fdda05562`。只通过 Git archive 读取该提交的对象库，未读取正在修改中的 SM/RE 源码。{len(audit['source_files'])} 个文件均 exact_git_blob，与原 source-manifest 逐字节一致；本轮不存在 LF/CRLF 转换。节点原始源码保留原换行，未静默归一化。忽略目录下创建只读文件副本，重新抽取的全部节点与原缓存完整相同。",
        "",
        f"已核对 {audit['nodes']} 个节点、{audit['cache_vectors']} 个去重向量（document/query）、原 T0、功能摘要及 T1 构造。voyage-code-4 / 1024 / float，input_type=document/query，truncation=false；原 combine、BM25 分词及 k1=1.2、b=0.75 不变。{audit['replayed_rankings']} 条 A/B/C/T/BM25 路线 Top50 全部从缓存重放吻合，原指标也吻合。模型名、input_type 从原配置和缓存键核验；第一轮未记录供应商不可变模型修订，响应本身不能独立证明 input_type。没有重新请求模型。",
        "",
        f"[输入审计](results/input-audit.json) 含原文件、节点及排名哈希、向量内容哈希根、逐源码文件双份字节身份；逐向量文本／内容哈希清单仍在忽略的 .local/bm25-value/text-vector-manifest.json。第一轮所有 {len(audit['history_file_hashes'])} 个已跟踪实验文件的内容与审阅提交逐字节比较，未改动。协议、配置、汇总和逐问题结果分别见 [PROTOCOL.md](PROTOCOL.md)、[config.json](config.json)、[aggregate.json](results/aggregate.json)、[per-question.json](results/per-question.json)。",
        "",
        "## BM25 Top50 的独有价值",
        "",
        "重合率为 intersection/50，同时保存 intersection/min(实际长度)；本批各路实际长度均为 50，两种重合率相同。Jaccard 按每问计算再平均。并集是扩大候选预算后的覆盖上界，不能用作相同 50 候选方案的效果。",
        "",
        "| 条件 | 向量路 | 独有正确对应项 | 获益问题 | 比例 | 向量Recall50 | 并集Recall | 并集微Recall | 重合率 | Jaccard | 并集平均长度（范围） |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    all_groups = [g for g in groups if g["split"] == "all"]
    for g in all_groups:
        for route, u in g["unique"].items():
            d = u["union_length"]
            lines.append(
                f"| {g['condition']} | {route} | {u['correct_pairs']} | {u['benefited_questions']}/{u['n']} | {pct(u['benefited_fraction'])} | {pct(u['mean_vector_recall50'])} | {pct(u['mean_union_recall'])} | {pct(u['micro_union_recall'])} | {pct(u['mean_overlap_over_50'])} | {u['mean_jaccard']:.4f} | {d['mean']:.2f}（{d['min']}–{d['max']}） |"
            )
    lines += [
        "",
        "相同函数回答不同问题按不同对应项计数；两条件有重复，不应把各自的 5 项当作 10 个不同事实。A 只作辅助，以下主要解释 C。",
        "",
        "| 条件 | 问题 | 领域 | C50 外原标注正确函数 | BM25 原排名 |",
        "|---|---|---|---|---:|",
    ]
    for r in records:
        for item in r["unique"]["C"]["bm25_unique_correct"]:
            lines.append(
                f"| {r['condition']} | {r['question']} | {r['topic']} | `{item['id']}` | {item['bm25_rank']} |"
            )
    lines += [""]
    for g in all_groups:
        topics = "；".join(
            f"{topic}：{t['correct_pairs']}项（{','.join(t['questions'])}）"
            for topic, t in g["unique"]["C"]["topics"].items()
        )
        lines += [f"{g['condition']} 的 C 补充领域：{topics}。", ""]
    lines += [
        "上表给出原排名；部分正确项位置较后，单靠最前面的固定名额不会全部保留。A 的全部补充领域、问题和函数另保存在逐问题结果与汇总 topics 字段中。",
        "",
        "## 相同候选预算：C50 对 40+10",
        "",
        "先取 C 前40，再从 BM25 中排除这40个后取前10；没有排除整个 C50。追加项可能只是保住 C41–50。下表新增／丢失均相对原 C50。",
        "",
        "| 条件 | 新增正确 | 丢失正确 | 净值 | 净获益/受损/持平问题 | C50 Recall | 混合Recall | 原/混合正确项 | 原/混合入口命中 |",
        "|---|---:|---:|---:|---|---:|---:|---|---|",
    ]
    for g in all_groups:
        q = g["quotas"]["40+10"]
        lines.append(
            f"| {g['condition']} | {q['added_correct_pairs']} | {q['lost_correct_pairs']} | {q['net_correct_pairs']:+d} | {q['benefited_questions']}/{q['harmed_questions']}/{q['unchanged_questions']} | {pct(q['baseline']['Recall@pool'])} | {pct(q['mixed']['Recall@pool'])} | {q['baseline']['correct_pairs']}/{q['mixed']['correct_pairs']} | {pct(q['baseline']['EntryHit@pool'])}/{pct(q['mixed']['EntryHit@pool'])} |"
        )
    lines += [
        "",
        "| 条件 | 追加项总数 | 原在C41–50 | 真正C50外 | C50外正确进入 | 原/混合微Recall | 实际池长度（最小/最大） | 空池 |",
        "|---|---:|---:|---:|---:|---|---|---:|",
    ]
    for g in all_groups:
        q = g["quotas"]["40+10"]
        d = q["mixed"]["length_distribution"]
        lines.append(
            f"| {g['condition']} | {q['tail_already_in_baseline'] + q['tail_truly_outside_baseline']} | {q['tail_already_in_baseline']} | {q['tail_truly_outside_baseline']} | {q['outside_correct_entered']} | {pct(q['baseline']['micro_recall_pool'])}/{pct(q['mixed']['micro_recall_pool'])} | {d['min']}/{d['max']} | {d['empty']} |"
        )
    lines += [
        "",
        "本批 BM25 均有50个正分结果，所有池均达到50，无空列表；代码仍保留短列表，不填零分或其他路线。入口池命中均为30/30，没有因固定配额新增入口命中。",
        "",
        "## 最终列表：C10 对 7+3",
        "",
        "保留 C 前7的顺序，追加 BM25 未在这7项中的前3，保持 BM25 顺序。两组前5相同，Hit@5/Recall@5 不可能因本策略变化。",
        "",
        "| 条件 | 方案 | Hit@5 | Hit@10 | MRR@10 | Recall@5 | Recall@10 | 实际长度 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for g in all_groups:
        for arm, label in (("baseline", "C10"), ("mixed", "7+3")):
            m = g["quotas"]["7+3"][arm]
            lines.append(
                f"| {g['condition']} | {label} | {pct(m['Hit@5'])} | {pct(m['Hit@10'])} | {m['MRR@10']:.6f} | {pct(m['Recall@5'])} | {pct(m['Recall@10'])} | {m['length']:.0f} |"
            )
    lines += [
        "",
        "| 条件 | 新增正确 | 丢失正确 | 净值 | 净获益/受损/持平问题 | C10外正确进入 | 原/混合正确项 | 原/混合微Recall10 |",
        "|---|---:|---:|---:|---|---:|---|---|",
    ]
    for g in all_groups:
        q = g["quotas"]["7+3"]
        lines.append(
            f"| {g['condition']} | {q['added_correct_pairs']} | {q['lost_correct_pairs']} | {q['net_correct_pairs']:+d} | {q['benefited_questions']}/{q['harmed_questions']}/{q['unchanged_questions']} | {q['outside_correct_entered']} | {q['baseline']['correct_pairs']}/{q['mixed']['correct_pairs']} | {pct(q['baseline']['micro_recall_pool'])}/{pct(q['mixed']['micro_recall_pool'])} |"
        )
    lines += [
        "",
        "中文净损失，扩展条件正确对应项总量持平，宏Recall10小幅上升；原因是每问相关集合大小不同，不能把宏平均上升解释为新增正确项总量上升。没有新增入口命中或 MRR 收益。净获益/受损按 related 数量净差分类；有新增/有丢失的问题数另在 aggregate 中保存，允许同问同时出现。结果不支持默认挤出 C8–10 给 BM25 保留3席。",
        "",
        "## 逐问题变化与原分层",
        "",
        "下表每条件每问列出新增/丢失/净值；对应候选 ID、独有列表、完整必要排名、长度与入口变化均见 per-question.json。",
        "",
        "| 条件 | 问题 | 原split | 领域 | 40+10 新增/丢失/净 | 7+3 新增/丢失/净 |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        cells = []
        for name in ("40+10", "7+3"):
            q = r["quotas"][name]
            cells.append(
                f"{len(q['added_correct'])}/{len(q['lost_correct'])}/{q['net_correct']:+d}"
            )
        lines.append(
            f"| {r['condition']} | {r['question']} | {r['split']} | {r['topic']} | {cells[0]} | {cells[1]} |"
        )
    lines += [
        "",
        "原分层对照（**heldout 为历史标签，已非独立保留证据**）：",
        "",
        "| 条件 | 原split | n | C独有补充项/问题 | 40+10净值 | C50→混合Recall | 7+3净值 | C10→混合Recall10 |",
        "|---|---|---:|---|---:|---|---:|---|",
    ]
    for g in groups:
        if g["split"] == "all":
            continue
        u, p, t = g["unique"]["C"], g["quotas"]["40+10"], g["quotas"]["7+3"]
        lines.append(
            f"| {g['condition']} | {g['split']} | {u['n']} | {u['correct_pairs']}/{u['benefited_questions']} | {p['net_correct_pairs']:+d} | {pct(p['baseline']['Recall@pool'])}→{pct(p['mixed']['Recall@pool'])} | {t['net_correct_pairs']:+d} | {pct(t['baseline']['Recall@10'])}→{pct(t['mixed']['Recall@10'])} |"
        )
    lines += [
        "",
        "仅原 development 的预声明探索配额（不据此选择最终策略）：",
        "",
        "| 条件 | 配额 | 新增/丢失/净值 | 净获益/受损问题 | C50→混合Recall |",
        "|---|---|---|---|---|",
    ]
    for g in groups:
        if g["split"] != "development":
            continue
        for name in ("45+5", "40+10", "35+15"):
            q = g["quotas"][name]
            lines.append(
                f"| {g['condition']} | {name} | {q['added_correct_pairs']}/{q['lost_correct_pairs']}/{q['net_correct_pairs']:+d} | {q['benefited_questions']}/{q['harmed_questions']} | {pct(q['baseline']['Recall@pool'])}→{pct(q['mixed']['Recall@pool'])} |"
            )
    lines += [
        "",
        "## 标注及未运行的重排",
        "",
        "[补充审阅记录](supplemental-review.json) 为 not_reviewed、空 items；本轮不补标，所有指标只使用原标注。逐问题 bm25_unique_unlabelled 可供未来源码审阅；若做事后补标必须另报，不能覆盖本结果或称为独立验证。",
        "",
        "R1（C50→同一 reranker→10）与 R2（40+10→同一 reranker→10）**NOT RUN**。仅找到 Voyage Embedding 配置及对应环境变量名，未找到明确授权、价格及版本已知的 reranker；未用现有 key 探测。真实新增请求量=0，API 输入量=0 token，API 耗时=0秒，新增API费用=0美元；未产生可比较的重排成绩，实际账单不适用。",
        "",
        "已提供 [rerank.py](rerank.py) 的 prepare/evaluate 离线接口；prepare 将120组请求模板放入忽略的 .local，不发送网络请求。两臂按相同 query、原 C 文本、长度策略（无截断）、节点ID顺序、模型与版本配对；不传标签或原检索分数，score同分按ID。默认模型/版本为空、预算0，不能误称为已运行。补跑须指定可用的本地 reranker 或获授权的模型API、不可变版本、上下文限制/tokenizer及价格与上限；适配器需返回完整索引分数、真实请求/token/耗时/估价并保留未知账单为null。未知响应默认不重试。",
        "",
        "## 建议和证据边界",
        "",
        "当前保留 C Top10 作为默认返回，C50作为固定池基线。BM25 可作为显式辅助发现路线；50+50并集上界证明了少量互补，不能证明固定预算或最终Top10的净提升。扩展查询的40+10可保留为下一次严格配对重排的候选方案，中文的净下降也必须同时报告。没有证据支持默认采用7+3。",
        "",
        "若做确认实验，先冻结查询语言、40+10或其他唯一主方案、同一重排模型/输入策略和评价指标，再采集未参与选择的新问题，单独记录来源、源码审阅流程和标注者；不以这30问选配额后宣称独立验证。当前不足：样本小、标注可能不完整、同一代理参与原摘要与标注、无重排结果、无新问题复现，也不外推到RE或三个仓库全量生产检索。",
        "",
        "## 复现与验证入口",
        "",
        "在原 experiments/code-retrieval-ablation 目录使用已有 Python+NumPy（不需安装游戏依赖）：",
        "",
        "```powershell",
        "python bm25-value/analyze.py --sm-git D:/Projects/agentic-trpg/trpg-state-machine/.git",
        "python bm25-value/render_report.py",
        "python -m unittest discover -s bm25-value -p test_analysis.py -v",
        "python bm25-value/rerank.py prepare",
        "python bm25-value/verify_results.py",
        "git diff --check",
        "```",
        "",
        "analyze 只重写本子目录派生结果和自己的 .local/bm25-value，不调用第一轮 evaluate。测试与独立审计涵盖去重前缀、共同/真正独有项、得失净值、短列表、比例、标注隔离、顺序及指标，并逐问题重算汇总。实际执行退出码见 [validation.json](validation.json)；不声称SM/RE游戏测试或GitHub Actions通过。",
        "",
    ]
    return "\n".join(lines)


def main():
    content = render(
        load(OUT / "aggregate.json"),
        load(OUT / "per-question.json"),
        load(OUT / "input-audit.json"),
    )
    (HERE / "REPORT.md").write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
