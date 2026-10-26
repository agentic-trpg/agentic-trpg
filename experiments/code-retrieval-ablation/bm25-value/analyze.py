"""Offline paired reanalysis. Reads frozen caches; never reads live game source."""

import argparse
import io
import json
import os
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# Keep this directory first: round one also has report.py and audit.py,
# whose imports execute historical report generation as a side effect.
sys.path.append(str(HERE.parent))
from prepare import BASE, LOCAL, digest, dump, extract  # noqa: E402
from retrieval import BM25, combine, key, load, metrics, overlap, unique  # noqa: E402

CONFIG = load(HERE / "config.json")
OUT = HERE / "results"
WORK = LOCAL / "bm25-value"


def supplement(vector, lexical, prefix, quota):
    chosen = unique(vector)[:prefix]
    tail = [x for x in unique(lexical) if x not in set(chosen)][:quota]
    return chosen + tail


def delta(before, after, related, entries):
    before, after, related, entries = map(set, (before, after, related, entries))
    added = sorted((after - before) & related)
    lost = sorted((before - after) & related)
    return {
        "added_correct": added,
        "lost_correct": lost,
        "net_correct": len(added) - len(lost),
        "added_entries": sorted((after - before) & entries),
        "lost_entries": sorted((before - after) & entries),
    }


def pool_metrics(rank, entries, related):
    return {
        **metrics(rank, entries, related),
        "Recall@pool": len(set(rank) & set(related)) / len(related),
        "EntryHit@pool": int(bool(set(rank) & set(entries))),
        "length": len(rank),
    }


def unique_analysis(vector, lexical, related):
    v, b, rel = set(vector), set(lexical), set(related)
    only = [x for x in lexical if x not in v]
    correct = [x for x in only if x in rel]
    union = v | b
    return {
        "overlap": overlap(vector, lexical, 50),
        "bm25_unique": only,
        "bm25_unique_correct": [{"id": x, "bm25_rank": lexical.index(x) + 1} for x in correct],
        "bm25_unique_unlabelled": [x for x in only if x not in rel],
        "benefited": bool(correct),
        "vector_correct": len(v & rel),
        "vector_recall50": len(v & rel) / len(rel),
        "union_correct": len(union & rel),
        "union_recall": len(union & rel) / len(rel),
        "union_length": len(union),
    }


def quota_analysis(vector, lexical, prefix, quota, baseline_k, entries, related):
    baseline = vector[:baseline_k]
    mixed = supplement(vector, lexical, prefix, quota)
    tail = mixed[len(vector[:prefix]) :]
    shared = [x for x in tail if x in set(baseline)]
    outside = [x for x in tail if x not in set(baseline)]
    return {
        "quota": [prefix, quota],
        "baseline_k": baseline_k,
        "selected": mixed,
        "bm25_tail": tail,
        "tail_already_in_baseline": shared,
        "tail_truly_outside_baseline": outside,
        "outside_correct_entered": [x for x in outside if x in set(related)],
        "baseline": pool_metrics(baseline, entries, related),
        "mixed": pool_metrics(mixed, entries, related),
        **delta(baseline, mixed, related, entries),
    }


def mean(values):
    return sum(values) / len(values) if values else None


def distribution(values):
    return {"min": min(values), "max": max(values), "mean": mean(values), "empty": values.count(0)}


def summarize_uniques(records, route):
    rows = [r["unique"][route] for r in records]
    pairs = sum(len(r["bm25_unique_correct"]) for r in rows)
    benefited = sum(r["benefited"] for r in rows)
    topics = {}
    for r in records:
        n = len(r["unique"][route]["bm25_unique_correct"])
        if n:
            t = topics.setdefault(r["topic"], {"correct_pairs": 0, "questions": []})
            t["correct_pairs"] += n
            t["questions"].append(r["question"])
    denominators = sum(len(r["original_related"]) for r in records)
    return {
        "n": len(rows),
        "correct_pairs": pairs,
        "benefited_questions": benefited,
        "benefited_fraction": benefited / len(rows),
        "mean_vector_recall50": mean([r["vector_recall50"] for r in rows]),
        "mean_union_recall": mean([r["union_recall"] for r in rows]),
        "micro_union_recall": sum(r["union_correct"] for r in rows) / denominators,
        "union_correct_pairs": sum(r["union_correct"] for r in rows),
        "related_pairs": denominators,
        "mean_overlap_over_50": mean([r["overlap"]["overlap_over_k"] for r in rows]),
        "mean_overlap_over_min_length": mean(
            [
                r["overlap"]["overlap_over_min_length"]
                for r in rows
                if r["overlap"]["overlap_over_min_length"] is not None
            ]
        ),
        "mean_jaccard": mean(
            [r["overlap"]["jaccard"] for r in rows if r["overlap"]["jaccard"] is not None]
        ),
        "vector_length": distribution([r["overlap"]["length_a"] for r in rows]),
        "bm25_length": distribution([r["overlap"]["length_b"] for r in rows]),
        "union_length": distribution([r["union_length"] for r in rows]),
        "topics": topics,
    }


def summarize_quotas(records, name):
    rows = [r["quotas"][name] for r in records]
    added = sum(len(r["added_correct"]) for r in rows)
    lost = sum(len(r["lost_correct"]) for r in rows)
    n = len(rows)
    result = {
        "n": n,
        "added_correct_pairs": added,
        "lost_correct_pairs": lost,
        "net_correct_pairs": added - lost,
        "benefited_questions": sum(r["net_correct"] > 0 for r in rows),
        "harmed_questions": sum(r["net_correct"] < 0 for r in rows),
        "unchanged_questions": sum(r["net_correct"] == 0 for r in rows),
        "questions_with_additions": sum(bool(r["added_correct"]) for r in rows),
        "questions_with_losses": sum(bool(r["lost_correct"]) for r in rows),
        "questions_with_entry_gains": sum(
            r["mixed"]["EntryHit@pool"] > r["baseline"]["EntryHit@pool"] for r in rows
        ),
        "questions_with_entry_losses": sum(
            r["mixed"]["EntryHit@pool"] < r["baseline"]["EntryHit@pool"] for r in rows
        ),
        "tail_already_in_baseline": sum(len(r["tail_already_in_baseline"]) for r in rows),
        "tail_truly_outside_baseline": sum(len(r["tail_truly_outside_baseline"]) for r in rows),
        "outside_correct_entered": sum(len(r["outside_correct_entered"]) for r in rows),
    }
    result["benefited_fraction"] = result["benefited_questions"] / n
    result["harmed_fraction"] = result["harmed_questions"] / n
    for arm in ("baseline", "mixed"):
        result[arm] = {m: mean([r[arm][m] for r in rows]) for m in rows[0][arm]}
        result[arm]["length_distribution"] = distribution([r[arm]["length"] for r in rows])
        correct = sum(
            round(r[arm]["Recall@pool"] * len(q["original_related"]))
            for r, q in zip(rows, records, strict=True)
        )
        result[arm]["correct_pairs"] = correct
        result[arm]["micro_recall_pool"] = correct / sum(
            len(q["original_related"]) for q in records
        )
    return result


def aggregate(records):
    result = []
    for condition in CONFIG["conditions"]:
        for split in ("development", "heldout", "all"):
            rs = [
                r
                for r in records
                if r["condition"] == condition and (split == "all" or r["split"] == split)
            ]
            names = ["40+10", "7+3"] + (["45+5", "35+15"] if split == "development" else [])
            result.append(
                {
                    "condition": condition,
                    "split": split,
                    "unique": {g: summarize_uniques(rs, g) for g in ("A", "C")},
                    "quotas": {name: summarize_quotas(rs, name) for name in names},
                }
            )
    return result


def historical_hashes():
    repo = BASE.parents[1]
    raw_zip = subprocess.check_output(
        [
            "git",
            "archive",
            "--format=zip",
            CONFIG["reviewed_experiment_commit"],
            "experiments/code-retrieval-ablation",
        ],
        cwd=repo,
    )
    archive = zipfile.ZipFile(io.BytesIO(raw_zip))
    result = {}
    for name in sorted(n for n in archive.namelist() if not n.endswith("/")):
        expected = archive.read(name)
        actual = (repo / name).read_bytes()
        if actual != expected:
            raise RuntimeError("Historical tracked bytes changed: " + name)
        result[name] = digest(actual)
    return result


def verify_inputs(sm_git):
    for name, expected in load(BASE / "protocol-lock.json")["files"].items():
        assert digest((BASE / name).read_bytes()) == expected, name
    history = historical_hashes()
    manifest = load(BASE / "source-manifest.json")
    cached_nodes = load(LOCAL / "nodes.json")
    # git archive reads the object database, never the current working tree.
    raw_zip = subprocess.check_output(
        ["git", "--git-dir", str(sm_git), "archive", "--format=zip", CONFIG["source_commit"], "src"]
    )
    archive = zipfile.ZipFile(io.BytesIO(raw_zip))
    assert sorted(p for p in archive.namelist() if p.endswith(".py")) == sorted(
        f["path"] for f in manifest["files"]
    )
    source_rows = []
    fixed = WORK / "fixed-source"
    for f in manifest["files"]:
        blob = archive.read(f["path"])
        mode = "exact_git_blob"
        restored = blob
        if digest(blob) != f["sha256"]:
            restored = blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            mode = "explicit_LF_to_CRLF_to_match_original_manifest"
        if digest(restored) != f["sha256"] or len(restored) != f["bytes"]:
            raise RuntimeError("Cannot recover original file bytes: " + f["path"])
        p = fixed / f["path"]
        if p.exists():
            assert p.read_bytes() == restored, "Existing fixed copy drift"
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(restored)
            p.chmod(0o444)
        source_rows.append(
            {
                "path": f["path"],
                "git_blob_sha256": digest(blob),
                "git_blob_bytes": len(blob),
                "original_manifest_sha256": digest(restored),
                "original_manifest_bytes": len(restored),
                "recovery": mode,
            }
        )
    files, nodes = extract(fixed)
    assert files == manifest["files"]
    assert json.loads(json.dumps(nodes)) == cached_nodes, (
        "Cached node content differs from fixed source"
    )
    assert digest("\n".join(n["id"] for n in nodes)) == manifest["node_ids_sha256"]
    summaries = load(BASE / "summaries.json")["records"]
    authored = load(BASE / "summary-semantics.json")["summaries"]
    assert [s["id"] for s in summaries] == [n["id"] for n in nodes]
    texts = []
    for n, s in zip(nodes, summaries, strict=True):
        assert digest(n["source"]) == n["source_sha256"] == s["source_sha256"]
        assert n["file_sha256"] == s["file_sha256"]
        assert s["summary"] == authored[n["id"]]
        blocks = [
            f"Path: {n['path']}\nQualified name: {n['qualname']}\n"
            f"Class: {n['class'] or '(module)'}",
            n["signature"],
        ]
        module, cls = n["module_doc"][:400], "\n".join(n["class_docs"])[:400]
        if module:
            blocks.append("Module context: " + module)
        if cls:
            blocks.append("Class context: " + cls)
        if n["docstring"]:
            blocks.append(n["docstring"])
        assert "\n\n".join(blocks) == s["T0"]
        t1 = s["T0"] + "\nSummary: " + s["summary"]
        texts.append(
            {
                "id": n["id"],
                "A": n["source"],
                "B": combine(n["source"], s["T0"]),
                "C": combine(n["source"], t1),
                "T": t1,
            }
        )
    work = {}
    for t in texts:
        for group in ("A", "B", "C", "T"):
            work[key(t[group], "document")] = ("document", t[group])
    questions = load(BASE / "questions.json")
    for q in questions:
        for condition in CONFIG["conditions"]:
            work[key(q[condition], "query")] = ("query", q[condition])
    cache_rows, vectors = [], {}
    for k, (kind, text) in sorted(work.items()):
        p = LOCAL / "vectors" / (k + ".json")
        if not p.exists():
            raise RuntimeError(f"Missing frozen {kind} vector {k}; no API fallback")
        v = np.asarray(load(p), dtype=np.float64)
        assert v.shape == (1024,) and np.isfinite(v).all() and np.linalg.norm(v) > 0
        vectors[k] = v
        cache_rows.append(
            {
                "key": k,
                "input_type": kind,
                "text_sha256": digest(text),
                "vector_sha256": digest(p.read_bytes()),
            }
        )
    dump(WORK / "text-vector-manifest.json", cache_rows)
    records = load(LOCAL / "complete-rankings.json")
    assert len(records) == 60
    byq = {q["id"]: q for q in questions}
    assert {(r["question"], r["condition"]) for r in records} == {
        (q["id"], c) for q in questions for c in CONFIG["conditions"]
    }
    ids = [t["id"] for t in texts]
    matrices = {}
    for group in ("A", "B", "C", "T"):
        m = np.asarray([vectors[key(t[group], "document")] for t in texts])
        matrices[group] = m / np.linalg.norm(m, axis=1, keepdims=True)
    bm = BM25([t["T"] for t in texts])
    labels = {x["id"]: x for x in load(BASE / "annotations.json")["items"]}
    for r in records:
        q = byq[r["question"]]
        assert r["split"] == q["split"]
        v = vectors[key(q[r["condition"]], "query")]
        v = v / np.linalg.norm(v)
        for group, m in matrices.items():
            scores = m @ v
            order = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))[:50]
            assert [ids[i] for i in order] == r["rankings"][group], (q["id"], group)
        assert bm.rank(q[r["condition"]], ids) == r["rankings"]["BM25"]
        for group in ("A", "B", "C", "T", "BM25"):
            label = labels[q["id"]]
            assert (
                metrics(r["rankings"][group], label["entries"], [x["id"] for x in label["related"]])
                == r["metrics"][group]
            )
    cfg = load(BASE / "config.example.json")
    evidence = {
        "source_commit": CONFIG["source_commit"],
        "source_files": source_rows,
        "nodes": len(nodes),
        "node_ids_sha256": manifest["node_ids_sha256"],
        "nodes_cache_sha256": digest((LOCAL / "nodes.json").read_bytes()),
        "complete_rankings_sha256": digest((LOCAL / "complete-rankings.json").read_bytes()),
        "history_file_hashes": history,
        "embedding": {k: cfg[k] for k in ("model", "dimension", "dtype")},
        "input_types": ["document", "query"],
        "truncation": False,
        "text_construction": (
            "Original build_texts.py T0/T1 and retrieval.combine; "
            "exact strings, no newline normalization"
        ),
        "cache_identity_limit": (
            "Model/input_type metadata are bound in original cache key and historical config; "
            "response files alone do not independently attest input_type. "
            "Provider's immutable model revision is not recorded in round one."
        ),
        "cache_vectors": len(cache_rows),
        "cache_by_input_type": dict(Counter(r["input_type"] for r in cache_rows)),
        "text_vector_manifest_sha256": digest((WORK / "text-vector-manifest.json").read_bytes()),
        "cache_key_content_root": digest(
            json.dumps(cache_rows, ensure_ascii=False, sort_keys=True)
        ),
        "replayed_rankings": 60 * 5,
        "replay_all_match": True,
        "protocol_sha256": digest((HERE / "PROTOCOL.md").read_bytes()),
        "config_sha256": digest((HERE / "config.json").read_bytes()),
        "reranker_check": {
            "experiment_configuration": "Embedding endpoint only; no reranker configuration",
            "available_tool": "No reranker connector",
            "relevant_environment_names": sorted(
                k
                for k in os.environ
                if any(
                    s in k.upper()
                    for s in ("RERANK", "VOYAGE", "COHERE", "JINA", "OLLAMA", "HF_HOME")
                )
            ),
            "conclusion": "No explicitly authorized reranker with known cost found; no probe sent",
        },
        "new_api_requests": 0,
        "new_api_input_tokens": 0,
        "new_api_seconds": 0,
        "new_api_cost_usd": 0,
    }
    dump(OUT / "input-audit.json", evidence)
    return records, texts


def analyze(records):
    questions = {q["id"]: q for q in load(BASE / "questions.json")}
    labels = {q["id"]: q for q in load(BASE / "annotations.json")["items"]}
    result = []
    for r in records:
        q, label = questions[r["question"]], labels[r["question"]]
        related, entries = [x["id"] for x in label["related"]], label["entries"]
        assert set(entries) <= set(related) and related
        ranks = {g: r["rankings"][g] for g in ("A", "C", "BM25")}
        for rank in ranks.values():
            assert len(rank) == len(set(rank)) and len(rank) <= 50
        quotas = {
            "40+10": quota_analysis(ranks["C"], ranks["BM25"], 40, 10, 50, entries, related),
            "7+3": quota_analysis(ranks["C"], ranks["BM25"], 7, 3, 10, entries, related),
        }
        if q["split"] == "development":
            for prefix, quota in CONFIG["exploratory_development_quotas"]:
                quotas[f"{prefix}+{quota}"] = quota_analysis(
                    ranks["C"], ranks["BM25"], prefix, quota, 50, entries, related
                )
        result.append(
            {
                "question": q["id"],
                "topic": q["topic"],
                "split": q["split"],
                "condition": r["condition"],
                "original_entries": entries,
                "original_related": related,
                "rankings": ranks,
                "unique": {
                    g: unique_analysis(ranks[g], ranks["BM25"], related) for g in ("A", "C")
                },
                "quotas": quotas,
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sm-git",
        type=Path,
        required=True,
        help="SM Git object database; working tree source is never read",
    )
    args = parser.parse_args()
    records, _ = verify_inputs(args.sm_git)
    result = analyze(records)
    dump(OUT / "per-question.json", result)
    dump(OUT / "aggregate.json", aggregate(result))
    # This file is intentionally excluded from all metrics paths.
    if not (HERE / "supplemental-review.json").exists():
        dump(
            HERE / "supplemental-review.json",
            {
                "status": "not_reviewed",
                "original_annotations_unchanged": True,
                "posthoc": True,
                "warning": "unlabelled does not mean incorrect; no supplemental metrics computed",
                "items": [],
            },
        )
    print(
        json.dumps(
            {"question_conditions": len(result), "new_api_requests": 0, "rankings_replayed": 300}
        )
    )


if __name__ == "__main__":
    main()
