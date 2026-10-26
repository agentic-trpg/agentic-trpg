"""Independently recount original-label gains/losses and every report table."""

import json
import math
import os
import re

from analyze import BASE, HERE, LOCAL, OUT, WORK, aggregate, digest, dump, historical_hashes, load
from render_report import render


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)


def check():
    evidence = load(OUT / "input-audit.json")
    assert historical_hashes() == evidence["history_file_hashes"]
    for name, expected in (("PROTOCOL.md", "protocol_sha256"), ("config.json", "config_sha256")):
        assert digest((HERE / name).read_bytes()) == evidence[expected]
    assert digest((LOCAL / "nodes.json").read_bytes()) == evidence["nodes_cache_sha256"]
    assert (
        digest((LOCAL / "complete-rankings.json").read_bytes())
        == evidence["complete_rankings_sha256"]
    )
    assert (
        digest((WORK / "text-vector-manifest.json").read_bytes())
        == evidence["text_vector_manifest_sha256"]
    )
    originals = {(r["question"], r["condition"]): r for r in load(LOCAL / "complete-rankings.json")}
    labels = {r["id"]: r for r in load(BASE / "annotations.json")["items"]}
    rows = load(OUT / "per-question.json")
    groups = load(OUT / "aggregate.json")
    assert len(rows) == 60 and len({(r["question"], r["condition"]) for r in rows}) == 60
    audited = 0
    for r in rows:
        original = originals[(r["question"], r["condition"])]
        label = labels[r["question"]]
        rel = {x["id"] for x in label["related"]}
        entry = set(label["entries"])
        assert rel == set(r["original_related"]) and entry == set(r["original_entries"])
        assert r["rankings"] == {g: original["rankings"][g] for g in ("A", "C", "BM25")}
        for route in ("A", "C"):
            v, b = r["rankings"][route], r["rankings"]["BM25"]
            only = [x for x in b if x not in v]
            u = r["unique"][route]
            assert u["bm25_unique"] == only
            assert u["bm25_unique_correct"] == [
                {"id": x, "bm25_rank": b.index(x) + 1} for x in only if x in rel
            ]
            assert u["bm25_unique_unlabelled"] == [x for x in only if x not in rel]
            assert u["union_length"] == len(set(v + b))
            close(u["union_recall"], len(set(v + b) & rel) / len(rel))
        for name, q in r["quotas"].items():
            prefix, quota = map(int, name.split("+"))
            v, b = r["rankings"]["C"], r["rankings"]["BM25"]
            expected = list(v[:prefix])
            tail = []
            for candidate in b:
                if candidate not in expected and candidate not in tail and len(tail) < quota:
                    tail.append(candidate)
            expected.extend(tail)
            assert q["selected"] == expected
            before = v[: q["baseline_k"]]
            assert q["bm25_tail"] == tail
            assert q["tail_already_in_baseline"] == [x for x in tail if x in before]
            assert q["tail_truly_outside_baseline"] == [x for x in tail if x not in before]
            assert q["outside_correct_entered"] == [x for x in tail if x not in before and x in rel]
            added = (set(expected) - set(before)) & rel
            lost = (set(before) - set(expected)) & rel
            assert set(q["added_correct"]) == added and set(q["lost_correct"]) == lost
            assert q["net_correct"] == len(added) - len(lost)
            assert set(q["added_entries"]) == (set(expected) - set(before)) & entry
            assert set(q["lost_entries"]) == (set(before) - set(expected)) & entry
            for arm, ranking in (("baseline", before), ("mixed", expected)):
                first = next((i for i, x in enumerate(ranking[:10], 1) if x in entry), None)
                close(q[arm]["MRR@10"], 1 / first if first else 0)
                for k in (5, 10):
                    close(q[arm][f"Hit@{k}"], int(bool(set(ranking[:k]) & entry)))
                    close(q[arm][f"Recall@{k}"], len(set(ranking[:k]) & rel) / len(rel))
                close(q[arm]["Recall@pool"], len(set(ranking) & rel) / len(rel))
                assert q[arm]["EntryHit@pool"] == int(bool(set(ranking) & entry))
                assert q[arm]["length"] == len(ranking)
            audited += 1
    # Independent sums of raw candidate membership, rather than trusting stored deltas.
    for g in groups:
        selected = [
            r
            for r in rows
            if r["condition"] == g["condition"]
            and (g["split"] == "all" or r["split"] == g["split"])
        ]
        n = len(selected)
        for route, summary in g["unique"].items():
            counts = [
                len(
                    (set(r["rankings"]["BM25"]) - set(r["rankings"][route]))
                    & set(r["original_related"])
                )
                for r in selected
            ]
            assert summary["correct_pairs"] == sum(counts)
            assert summary["benefited_questions"] == sum(x > 0 for x in counts)
            close(summary["benefited_fraction"], sum(x > 0 for x in counts) / n)
            close(
                summary["mean_union_recall"],
                sum(
                    len(
                        set(r["rankings"][route] + r["rankings"]["BM25"])
                        & set(r["original_related"])
                    )
                    / len(r["original_related"])
                    for r in selected
                )
                / n,
            )
        for name, summary in g["quotas"].items():
            diffs = []
            for r in selected:
                q = r["quotas"][name]
                rel = set(r["original_related"])
                before = set(r["rankings"]["C"][: q["baseline_k"]])
                after = set(q["selected"])
                diffs.append((len((after - before) & rel), len((before - after) & rel)))
            assert summary["added_correct_pairs"] == sum(a for a, _ in diffs)
            assert summary["lost_correct_pairs"] == sum(b for _, b in diffs)
            assert summary["net_correct_pairs"] == sum(a - b for a, b in diffs)
            assert summary["benefited_questions"] == sum(a > b for a, b in diffs)
            assert summary["harmed_questions"] == sum(a < b for a, b in diffs)
            for arm in ("baseline", "mixed"):
                for metric in (
                    "Hit@5",
                    "Hit@10",
                    "MRR@10",
                    "Recall@5",
                    "Recall@10",
                    "Recall@pool",
                    "EntryHit@pool",
                    "length",
                ):
                    close(
                        summary[arm][metric],
                        sum(r["quotas"][name][arm][metric] for r in selected) / n,
                    )
    assert aggregate(rows) == groups
    assert (HERE / "REPORT.md").read_text(encoding="utf-8") == render(groups, rows, evidence)
    review = load(HERE / "supplemental-review.json")
    assert review["status"] == "not_reviewed" and review["items"] == []
    assert not (OUT / "rerank-results.json").exists(), (
        "Unreviewed rerank results must not masquerade as this offline run"
    )
    links = 0
    files = [p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    secret = os.environ.get("VOYAGE_API_KEY")
    for p in files:
        content = p.read_text(encoding="utf-8")
        if secret:
            assert secret not in content, "Actual credential contamination"
        if p.suffix == ".md":
            assert sum(line.startswith("```") for line in content.splitlines()) % 2 == 0
            columns = None
            for line in content.splitlines():
                if line.startswith("|"):
                    count = len(line.split("|")) - 2
                    if columns is None:
                        columns = count
                    assert count == columns, (p.name, line)
                else:
                    columns = None
            for target in re.findall(r"\]\(([^)]+)\)", content):
                if not re.match(r"https?://", target):
                    assert (p.parent / target.split("#")[0]).is_file(), target
                    links += 1
    result = {
        "passed": True,
        "question_conditions": len(rows),
        "quota_comparisons": audited,
        "aggregate_groups": len(groups),
        "original_files_unchanged": len(evidence["history_file_hashes"]),
        "report_exactly_recomputed": True,
        "local_markdown_links": links,
        "secret_scan_passed": True,
        "reranker_status": "not_run",
        "new_api_requests": 0,
    }
    dump(OUT / "audit.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    check()
