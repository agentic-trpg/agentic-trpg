"""Independent audit of frozen experiment artifacts; no game imports or network."""

import json
import os
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from prepare import BASE, LOCAL, digest, dump, verify


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check():
    cfg = load(BASE / "config.example.json")
    nodes = verify(Path(cfg["source_root"]))
    ids = {n["id"] for n in nodes}
    labels = {q["id"]: q for q in load(BASE / "annotations.json")["items"]}
    questions = load(BASE / "questions.json")
    assert len(ids) == 1059 and len(questions) == 30
    assert sum(q["split"] == "heldout" for q in questions) == 10
    lock = load(BASE / "protocol-lock.json")
    for name, expected in lock["files"].items():
        assert digest((BASE / name).read_bytes()) == expected, name
    records = load(LOCAL / "complete-rankings.json")
    assert len(records) == 60
    for record in records:
        label = labels[record["question"]]
        entries = set(label["entries"])
        related = {x["id"] for x in label["related"]}
        assert entries <= related <= ids
        for group, ranking in record["rankings"].items():
            assert len(ranking) <= 50 and len(ranking) == len(set(ranking))
            assert set(ranking) <= ids
            metric = record["metrics"][group]
            first = next((i + 1 for i, v in enumerate(ranking[:10]) if v in entries), None)
            assert metric["MRR@10"] == (1 / first if first else 0)
            for k in (5, 10):
                assert metric[f"Hit@{k}"] == int(any(v in entries for v in ranking[:k]))
                assert metric[f"Recall@{k}"] == len(set(ranking[:k]) & related) / len(related)
        for text, group in [("T", "D"), ("BM25", "E")]:
            scores = defaultdict(Fraction)
            for route in ("A", text):
                for rank, ident in enumerate(record["rankings"][route], 1):
                    scores[ident] += Fraction(1, 60 + rank)
            expected = sorted(scores, key=lambda ident: (-scores[ident], ident))[:50]
            assert expected == record["rankings"][group]
    for group in load(BASE / "results" / "aggregate.json"):
        selected = [
            r
            for r in records
            if r["condition"] == group["condition"]
            and (group["split"] == "all" or r["split"] == group["split"])
        ]
        assert len(selected) == group["n"]
        for name in ("Hit@5", "Hit@10", "MRR@10", "Recall@5", "Recall@10"):
            expected = sum(r["metrics"][group["group"]][name] for r in selected) / len(selected)
            assert expected == group[name]
    summaries = load(BASE / "summaries.json")["records"]
    assert {s["id"] for s in summaries} == ids
    byid = {n["id"]: n for n in nodes}
    for item in summaries:
        assert item["source_sha256"] == byid[item["id"]]["source_sha256"]
        assert item["summary"] and len(item["summary"]) < 150
    missing = 0
    from retrieval import tasks

    for key in tasks():
        vector = LOCAL / "vectors" / (key + ".json")
        missing += not vector.exists()
        values = load(vector)
        assert len(values) == 1024
    assert missing == 0
    local_links = 0
    for path in [BASE / "README.md", BASE / "REPORT.md", *sorted((BASE / "results").glob("*.md"))]:
        value = path.read_text(encoding="utf-8")
        assert (
            sum(
                line.startswith("~~~") or line.startswith(chr(96) * 3)
                for line in value.splitlines()
            )
            % 2
            == 0
        ), path.name
        for target in re.findall(r"\]\(([^)]+)\)", value):
            if re.match(r"https?://", target):
                continue
            filename = target.split("#", 1)[0]
            assert (path.parent / filename).is_file(), (path.name, target)
            local_links += 1
    # Inspect only explicitly task-owned files. Never print the actual env value.
    secret = os.environ.get("VOYAGE_API_KEY")
    files = [
        p
        for p in BASE.rglob("*")
        if p.is_file() and ".local" not in p.parts and "__pycache__" not in p.parts
    ]
    for p in files:
        content = p.read_bytes()
        if secret:
            assert secret.encode() not in content, "Credential contamination"
    result = {
        "source_files": len(load(BASE / "source-manifest.json")["files"]),
        "candidates": len(ids),
        "question_conditions": len(records),
        "metric_routes_audited": len(records) * 7,
        "rrf_fraction_audits": len(records) * 2,
        "missing_embeddings": missing,
        "local_markdown_links": local_links,
        "task_files_scanned_for_actual_env_secret": len(files),
        "env_secret_present": bool(secret),
        "secret_leak_found": False,
        "protocol_lock_matches": True,
        "all_checks_passed": True,
    }
    dump(BASE / "results" / "audit.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    check()
