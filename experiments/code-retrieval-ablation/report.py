"""Offline aggregation only. No network or changes to retrieval, labels or summaries."""

import json
from collections import defaultdict

from prepare import BASE, LOCAL, digest, dump
from retrieval import byte_bound, load, tasks, texts

GROUPS = ("A", "B", "C", "D", "E", "T", "BM25")
records = load(LOCAL / "complete-rankings.json")
questions = {q["id"]: q for q in load(BASE / "questions.json")}
labels = {a["id"]: a for a in load(BASE / "annotations.json")["items"]}
aggregate = load(BASE / "results" / "aggregate.json")


def mean(values):
    return sum(values) / len(values) if values else None


def selected(condition, split):
    return [
        r
        for r in records
        if r["condition"] == condition and (split == "all" or r["split"] == split)
    ]


def short(ident):
    return ident.split("::")[1]


def rankof(route, ident):
    return route.index(ident) + 1 if ident in route else None


def row(*cols):
    return "| " + " | ".join(str(c) for c in cols) + " |"


def table(headers, rows):
    return "\n".join([row(*headers), row(*["---"] * len(headers)), *[row(*r) for r in rows]])


overlap_rows = []
rescue_rows = []
unique_records = []
for condition in ("zh", "expanded"):
    for split in ("development", "heldout", "all"):
        rs = selected(condition, split)
        for pair in ("A-vs-T", "A-vs-BM25", "T-vs-BM25"):
            for j, k in enumerate((5, 10, 50)):
                values = [r["overlaps"][pair][j] for r in rs]
                overlap_rows.append(
                    {
                        "condition": condition,
                        "split": split,
                        "pair": pair,
                        "k": k,
                        "n": len(rs),
                        "mean_overlap_over_k": mean([v["overlap_over_k"] for v in values]),
                        "mean_jaccard": mean(
                            [v["jaccard"] for v in values if v["jaccard"] is not None]
                        ),
                        "empty_both": sum(v["length_a"] == v["length_b"] == 0 for v in values),
                        "length_a_minmax": [
                            min(v["length_a"] for v in values),
                            max(v["length_a"] for v in values),
                        ],
                        "length_b_minmax": [
                            min(v["length_b"] for v in values),
                            max(v["length_b"] for v in values),
                        ],
                    }
                )
        for text, fusion in [("T", "D"), ("BM25", "E")]:
            vs = [r["rescue"][text] for r in rs]
            rescue_rows.append(
                {
                    "condition": condition,
                    "split": split,
                    "text": text,
                    "fusion": fusion,
                    "n": len(rs),
                    "mean_union_length": mean([v["union_length"] for v in vs]),
                    "mean_union_recall": mean([v["union_recall"] for v in vs]),
                    "mean_code_recall50": mean([v["code_route_recall50"] for v in vs]),
                    "unique_correct_pairs": sum(len(v["text_unique_correct"]) for v in vs),
                    "unique_unlabelled_pairs": sum(len(v["text_unique_unlabelled"]) for v in vs),
                    "rescued_pairs_into_top10": sum(
                        len(v["rescued_into_fusion_top10"]) for v in vs
                    ),
                }
            )
for r in records:
    relevant = {a["id"] for a in labels[r["question"]]["related"]}
    for text, fusion in [("T", "D"), ("BM25", "E")]:
        for k in (5, 10, 50):
            only = set(r["rankings"][text][:k]) - set(r["rankings"]["A"][:k])
            unique_records.append(
                {
                    "question": r["question"],
                    "split": r["split"],
                    "condition": r["condition"],
                    "text": text,
                    "k": k,
                    "actual_code_length": len(r["rankings"]["A"][:k]),
                    "actual_text_length": len(r["rankings"][text][:k]),
                    "correct": sorted(only & relevant),
                    "unlabelled": sorted(only - relevant),
                    "correct_entering_fusion10": sorted(
                        only & relevant & set(r["rankings"][fusion][:10])
                    ),
                }
            )
dump(BASE / "results" / "overlap-summary.json", overlap_rows)
dump(BASE / "results" / "rescue-summary.json", rescue_rows)
dump(BASE / "results" / "text-unique.json", unique_records)

lines = [
    "# 逐问题检索结果",
    "",
    (
        "入口计入相关集合；标注不是穷尽调用图。>50 表示本路 Top-50 未出现。"
        "完整 Top-10 节点 ID 见 per-question.json；"
        "Top-50 在本地 .local/complete-rankings.json。"
    ),
    "",
]
for qid, q in questions.items():
    lines.extend(
        [
            f"## {qid} — {q['split']} — {q['topic']}",
            "",
            q["zh"],
            "",
            q["expanded"].split("\n", 1)[1],
            "",
        ]
    )
    for condition in ("zh", "expanded"):
        r = next(r for r in records if r["question"] == qid and r["condition"] == condition)
        rows = []
        for g in GROUPS:
            ranks = "; ".join(
                f"{short(i)}={rankof(r['rankings'][g], i) or '>50'}" for i in labels[qid]["entries"]
            )
            rows.append(
                [
                    g,
                    *[
                        f"{r['metrics'][g][m]:.3f}"
                        for m in ("Hit@5", "Hit@10", "MRR@10", "Recall@5", "Recall@10")
                    ],
                    ranks,
                ]
            )
        lines.extend(
            [
                f"### {condition}",
                "",
                table(["组", "Hit5", "Hit10", "MRR10", "Recall5", "Recall10", "入口排名"], rows),
                "",
            ]
        )
        rows = [
            [short(a["id"]), *[rankof(r["rankings"][g], a["id"]) or ">50" for g in GROUPS]]
            for a in labels[qid]["related"]
        ]
        lines.extend([table(["标注相关节点", *GROUPS], rows), ""])
(BASE / "results" / "questions.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

# Publish counts and representative IDs, never the full Top-50 retrieval cache.
dump(LOCAL / "text-unique.json", unique_records)
public_unique = []
for item in unique_records:
    public_unique.append(
        {
            **{k: v for k, v in item.items() if k != "unlabelled"},
            "unlabelled_count": len(item["unlabelled"]),
            "unlabelled_examples": item["unlabelled"][:3],
        }
    )
dump(BASE / "results" / "text-unique.json", public_unique)
public_records = []
for item in records:
    rescue = {}
    for route, value in item["rescue"].items():
        rescue[route] = {
            **{k: v for k, v in value.items() if k != "text_unique_unlabelled"},
            "text_unique_unlabelled_count": len(value["text_unique_unlabelled"]),
            "text_unique_unlabelled_examples": value["text_unique_unlabelled"][:3],
        }
    public_records.append(
        {
            **item,
            "rankings": {g: ranking[:10] for g, ranking in item["rankings"].items()},
            "rescue": rescue,
        }
    )
dump(BASE / "results" / "per-question.json", public_records)

# Associate successful raw responses with document/query roles using vector hashes.
work = tasks()
roles = {k: kind for k, (kind, _) in work.items()}
vector_roles = defaultdict(set)
for p in (LOCAL / "vectors").glob("*.json"):
    if p.stem in roles:
        vector_roles[digest(json.dumps(load(p)))].add(roles[p.stem])
usage = defaultdict(lambda: {"batches": 0, "tokens": 0, "vectors": 0})
for p in (LOCAL / "responses").glob("*.json"):
    data = load(p)
    kinds = set()
    for item in data["data"]:
        kinds.update(
            vector_roles.get(digest(json.dumps(item["embedding"])), {"probe_or_superseded"})
        )
    role = next(iter(kinds)) if len(kinds) == 1 else "mixed_or_superseded"
    usage[role]["batches"] += 1
    usage[role]["tokens"] += data["usage"]["total_tokens"]
    usage[role]["vectors"] += len(data["data"])
logical_estimates = {}
ts = texts()
for group in ("A", "B", "C", "T"):
    strings = {n[group] for n in ts}
    logical_estimates[group] = {
        "unique_texts": len(strings),
        "utf8_bytes": sum(len(t.encode()) for t in strings),
        "byte_token_bound": sum(byte_bound(t) for t in strings),
    }
dump(
    BASE / "results" / "usage-breakdown.json",
    {
        "successful_response_usage_by_role": dict(usage),
        "per_group_byte_estimates": logical_estimates,
        "note": (
            "Includes superseded concatenation and probe; invoice unavailable. "
            "Unknown-response charges cannot be proved from response counters."
        ),
    },
)

summary = [
    "# 汇总指标",
    "",
    (
        "A=源码向量；B=源码+T0；C=源码+T1；D=源码/文字向量 RRF；"
        "E=源码向量/文字 BM25 RRF；T=文字向量。宏平均，所有组最终 K 相同。"
    ),
    "",
]
for condition in ("zh", "expanded"):
    for split in ("development", "heldout", "all"):
        values = [a for a in aggregate if a["condition"] == condition and a["split"] == split]
        rows = [
            [
                a["group"],
                a["n"],
                *[f"{a[m]:.3f}" for m in ("Hit@5", "Hit@10", "MRR@10", "Recall@5", "Recall@10")],
                f"{a['mean_local_query_ms']:.2f}",
            ]
            for a in values
        ]
        summary.extend(
            [
                f"## {condition} / {split}",
                "",
                table(
                    ["组", "n", "Hit5", "Hit10", "MRR10", "Recall5", "Recall10", "本地 ms"], rows
                ),
                "",
            ]
        )
summary.extend(
    [
        "## 两路重合",
        "",
        (
            "Overlap=交集/K；Jaccard=交集/并集。短列表不补零分项，长度另列；"
            "均空为 null，不计高重合。逐问题还提供交集/min(实际长度)。"
        ),
        "",
    ]
)
rows = [
    [
        a["condition"],
        a["split"],
        a["pair"],
        a["k"],
        f"{a['mean_overlap_over_k']:.3f}",
        f"{a['mean_jaccard']:.3f}" if a["mean_jaccard"] is not None else "null",
        a["length_a_minmax"],
        a["length_b_minmax"],
    ]
    for a in overlap_rows
]
summary.extend(
    [
        table(["条件", "集合", "两路", "K", "Overlap", "Jaccard", "A 长度", "B 长度"], rows),
        "",
        "## 融合前候选并集与补回",
        "",
        "计数单位为问题—函数对。标注外不等于审查确认错误。每路最多50，并集可能超过50，不能将候选预算扩张全部归因于排序。",
        "",
    ]
)
rows = [
    [
        a["condition"],
        a["split"],
        a["text"],
        f"{a['mean_union_length']:.1f}",
        f"{a['mean_code_recall50']:.3f}",
        f"{a['mean_union_recall']:.3f}",
        a["unique_correct_pairs"],
        a["unique_unlabelled_pairs"],
        a["rescued_pairs_into_top10"],
    ]
    for a in rescue_rows
]
summary.extend(
    [
        table(
            [
                "条件",
                "集合",
                "文字路",
                "并集长度均值",
                "A Recall50",
                "并集 Recall",
                "文字独有正确",
                "标注外",
                "进入融合10",
            ],
            rows,
        ),
        "",
    ]
)
(BASE / "results" / "summary.md").write_text("\n".join(summary).rstrip() + "\n", encoding="utf-8")
print("Wrote offline aggregate, per-question and cost reports")
