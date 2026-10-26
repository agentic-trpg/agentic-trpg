"""Offline paired reranking interchange. No HTTP client or credentials."""

import argparse
import json
import math
from pathlib import Path

from analyze import BASE, HERE, LOCAL, OUT, WORK, digest, dump, historical_hashes, load
from retrieval import combine, metrics


def request_pair(record, query, documents, settings):
    requests = []
    for arm, ids in (
        ("R1", record["rankings"]["C"][:50]),
        ("R2", record["quotas"]["40+10"]["selected"]),
    ):
        ordered = sorted(ids)
        body = {
            "model": settings["model"],
            "version": settings["version"],
            "query": query,
            "documents": [documents[x] for x in ordered],
            "truncation": False,
            "return_scores_for_all": True,
        }
        requests.append(
            {
                "question": record["question"],
                "condition": record["condition"],
                "arm": arm,
                "node_ids": ordered,
                "request": body,
                "request_key": digest(json.dumps(body, ensure_ascii=False, sort_keys=True)),
            }
        )
    return requests


def prepare(config_path):
    historical_hashes()
    audit = load(OUT / "input-audit.json")
    assert digest((LOCAL / "nodes.json").read_bytes()) == audit["nodes_cache_sha256"]
    nodes = {n["id"]: n for n in load(LOCAL / "nodes.json")}
    docs = {
        s["id"]: combine(nodes[s["id"]]["source"], s["T0"] + "\nSummary: " + s["summary"])
        for s in load(BASE / "summaries.json")["records"]
    }
    questions = {q["id"]: q for q in load(BASE / "questions.json")}
    settings = load(config_path)["reranker"]
    requests = []
    for r in load(OUT / "per-question.json"):
        requests.extend(request_pair(r, questions[r["question"]][r["condition"]], docs, settings))
    result = {
        "status": "templates_only_not_dispatched",
        "settings": settings,
        "settings_sha256": digest(json.dumps(settings, sort_keys=True)),
        "potential_requests": len(requests),
        "potential_document_utf8_bytes": sum(
            len(d.encode()) for r in requests for d in r["request"]["documents"]
        ),
        "potential_query_utf8_bytes": sum(len(r["request"]["query"].encode()) for r in requests),
        "actual_requests": 0,
        "actual_input_tokens": 0,
        "requests": requests,
    }
    dump(WORK / "rerank" / "requests.json", result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "potential_requests",
                    "potential_document_utf8_bytes",
                    "actual_requests",
                )
            }
        )
    )


def validate_scores(pack, scores):
    settings = pack["settings"]
    if not settings["model"] or not settings["version"]:
        raise ValueError(
            "A locked model and version are required; default templates cannot be evaluated"
        )
    assert scores["model"] == settings["model"] and scores["version"] == settings["version"]
    assert scores["settings_sha256"] == pack["settings_sha256"]
    expected = {(r["question"], r["condition"], r["arm"]): r for r in pack["requests"]}
    rows = scores["results"]
    assert len(rows) == len(expected)
    ranked = {}
    for row in rows:
        ident = (row["question"], row["condition"], row["arm"])
        assert ident in expected and ident not in ranked
        request = expected[ident]
        assert row["request_key"] == request["request_key"]
        assert row["request_key"] == digest(
            json.dumps(request["request"], ensure_ascii=False, sort_keys=True)
        )
        ids = request["node_ids"]
        pairs = row["scores"]
        assert len(pairs) == len(ids)
        assert sorted(x["index"] for x in pairs) == list(range(len(ids)))
        assert all(
            type(x["index"]) is int
            and type(x["score"]) in (int, float)
            and math.isfinite(x["score"])
            for x in pairs
        )
        ranked[ident] = [
            ids[x["index"]]
            for x in sorted(pairs, key=lambda x: (-x["score"], ids[x["index"]]))[:10]
        ]
    return ranked


def evaluate(scores_path):
    historical_hashes()
    pack = load(WORK / "rerank" / "requests.json")
    scores = load(scores_path)
    ranked = validate_scores(pack, scores)
    # Caller must report real usage, including failed/unknown requests and retries.
    usage = scores["usage"]
    for k in ("actual_requests", "input_tokens", "seconds", "estimated_cost_usd"):
        assert type(usage[k]) in (int, float) and math.isfinite(usage[k]) and usage[k] >= 0
    assert usage["actual_requests"] >= len(pack["requests"])
    assert "actual_billed_usd" in usage and "pricing_basis" in usage
    settings = pack["settings"]
    assert usage["actual_requests"] <= settings["max_requests"]
    assert usage["input_tokens"] <= settings["max_input_tokens"]
    assert usage["estimated_cost_usd"] <= settings["max_cost_usd"]
    records = load(OUT / "per-question.json")
    rows = []
    for r in records:
        routes = {arm: ranked[(r["question"], r["condition"], arm)] for arm in ("R1", "R2")}
        rows.append(
            {
                "question": r["question"],
                "condition": r["condition"],
                "split": r["split"],
                "rankings": routes,
                "metrics": {
                    arm: metrics(route, r["original_entries"], r["original_related"])
                    for arm, route in routes.items()
                },
            }
        )
    aggregate = []
    for condition in ("zh", "expanded"):
        for split in ("all", "development", "heldout"):
            selected = [
                r
                for r in rows
                if r["condition"] == condition and (split == "all" or r["split"] == split)
            ]
            aggregate.append(
                {
                    "condition": condition,
                    "split": split,
                    "n": len(selected),
                    "metrics": {
                        arm: {
                            k: sum(r["metrics"][arm][k] for r in selected) / len(selected)
                            for k in selected[0]["metrics"][arm]
                        }
                        for arm in ("R1", "R2")
                    },
                }
            )
    dump(
        OUT / "rerank-results.json",
        {
            "status": "external_scores_imported_posthoc",
            "usage": usage,
            "settings": settings,
            "scores_sha256": digest(Path(scores_path).read_bytes()),
            "per_question": rows,
            "aggregate": aggregate,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=["prepare", "evaluate"])
    parser.add_argument("scores", nargs="?", type=Path)
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    args = parser.parse_args()
    if args.step == "prepare":
        prepare(args.config)
    else:
        if not args.scores:
            parser.error("evaluate needs an external scores file")
        evaluate(args.scores)
