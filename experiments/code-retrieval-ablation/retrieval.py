"""Independent CPU retrieval runner; only numpy is external. No game imports."""

import argparse
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
from prepare import BASE, LOCAL, digest, dump, verify

VERSION = "retrieval-v1"
CONFIG = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def frozen():
    f = load(BASE / "freeze.json")
    for name in ("questions", "annotations"):
        if digest((BASE / (name + ".json")).read_bytes()) != f[name + "_sha256"]:
            raise RuntimeError("Question/label freeze changed")


def unique(xs):
    return list(dict.fromkeys(xs))


def rrf(*routes):
    scores = {}
    for route in routes:
        for rank, ident in enumerate(unique(route)[:50], 1):
            scores[ident] = scores.get(ident, 0) + 1 / (60 + rank)
    return sorted(scores, key=lambda ident: (-scores[ident], ident))


def metrics(rank, entry, related):
    entry, related = set(entry), set(related)
    hits = [i for i, x in enumerate(rank[:10], 1) if x in entry]
    out = {"MRR@10": 1 / min(hits) if hits else 0}
    for k in (5, 10):
        out["Hit@" + str(k)] = int(bool(set(rank[:k]) & entry))
        out["Recall@" + str(k)] = len(set(rank[:k]) & related) / len(related)
    return out


def overlap(a, b, k):
    a, b = set(a[:k]), set(b[:k])
    inter = len(a & b)
    union = len(a | b)
    return {
        "k": k,
        "length_a": len(a),
        "length_b": len(b),
        "intersection": inter,
        "overlap_over_k": inter / k,
        "overlap_over_min_length": inter / min(len(a), len(b)) if a and b else None,
        "jaccard": inter / union if union else None,
    }


def tokenize_bm25(s):
    # Language-neutral Chinese unigram+overlapping bigram, no answer dictionary.
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", s).lower().replace("_", " ")
    out = re.findall(r"[a-z0-9]+", s)
    for span in re.findall(r"[\u3400-\u9fff]+", s):
        out.extend(span)
        out.extend(span[i : i + 2] for i in range(len(span) - 1))
    return out


class BM25:
    def __init__(self, texts):
        self.docs = [Counter(tokenize_bm25(t)) for t in texts]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lengths) / len(self.docs)
        df = Counter(t for d in self.docs for t in d)
        self.idf = {t: math.log(1 + (len(self.docs) - n + 0.5) / (n + 0.5)) for t, n in df.items()}

    def rank(self, q, ids):
        ts = set(tokenize_bm25(q))
        scores = []
        for ident, d, length in zip(ids, self.docs, self.lengths, strict=True):
            score = sum(
                self.idf.get(t, 0) * (d[t] * 2.2) / (d[t] + 1.2 * (0.25 + 0.75 * length / self.avg))
                for t in ts
                if d[t]
            )
            if score > 0:
                scores.append((ident, score))
        return [ident for ident, _ in sorted(scores, key=lambda v: (-v[1], v[0]))[:50]]


def combine(source, background):
    # Whitespace-normalized duplicate blocks across sides; source body is preserved.
    def normalize(value):
        return " ".join(value.split())

    normalized = normalize(source)
    kept = []
    for block in unique(background.split("\n\n")):
        prefix, separator, summary = block.partition("\nSummary: ")
        if separator and normalize(prefix) in normalized:
            block = "Summary: " + summary
        if normalize(block) not in normalized:
            kept.append(block)
    return source.rstrip() + "\n\n" + "\n\n".join(kept)


def texts():
    nodes = verify(Path(CONFIG["source_root"]))
    summaries = load(BASE / "summaries.json")["records"]
    byid = {s["id"]: s for s in summaries}
    if set(byid) != {n["id"] for n in nodes}:
        raise RuntimeError("Summary candidate mismatch")
    out = []
    for n in nodes:
        s = byid[n["id"]]
        if s["source_sha256"] != n["source_sha256"]:
            raise RuntimeError("Summary source mismatch")
        t0 = s["T0"]
        t1 = t0 + "\nSummary: " + s["summary"]
        out.append(
            {
                "id": n["id"],
                "A": n["source"],
                "B": combine(n["source"], t0),
                "C": combine(n["source"], t1),
                "T": t1,
            }
        )
    return out


def key(text, kind):
    return digest(
        json.dumps(
            [CONFIG["model"], CONFIG["dimension"], CONFIG["dtype"], kind, False, digest(text)]
        )
    )


def byte_bound(text):
    # Conservative byte-level estimate incl. server input-type prefix allowance.
    # Not a claim of exact model tokenizer counts. Actual usage comes from API.
    return len(text.encode("utf-8")) + 64


def tasks():
    frozen()
    ts = texts()
    qs = load(BASE / "questions.json")
    work = {}
    for n in ts:
        for group in ("A", "B", "C", "T"):
            text = n[group]
            work[key(text, "document")] = ("document", text)
    for q in qs:
        for condition in ("zh", "expanded"):
            text = q[condition]
            work[key(text, "query")] = ("query", text)
    return work


class API:
    def __init__(self):
        LOCAL.mkdir(exist_ok=True)
        self.path = LOCAL / "ledger.json"
        self.ledger = (
            load(self.path)
            if self.path.exists()
            else {
                "attempts": 0,
                "reserved_tokens": 0,
                "usage_tokens": 0,
                "successes": 0,
                "errors": [],
                "api_seconds": 0,
            }
        )
        self.secret = os.environ.get("VOYAGE_API_KEY")
        if not self.secret:
            raise RuntimeError(
                "VOYAGE_API_KEY is not visible to this process; do not paste it in chat"
            )

    def call(self, batch, kind):
        bound = sum(byte_bound(t) for t in batch)
        if any(byte_bound(t) > 32000 for t in batch):
            raise RuntimeError(
                "Over conservative 32K bound: resolve long node explicitly; no truncation"
            )
        payload = json.dumps(
            {
                "input": batch,
                "model": CONFIG["model"],
                "input_type": kind,
                "output_dimension": CONFIG["dimension"],
                "output_dtype": CONFIG["dtype"],
                "truncation": False,
            }
        ).encode()
        for attempt in range(CONFIG["retries"] + 1):
            nxt = self.ledger["reserved_tokens"] + bound
            if (
                self.ledger["attempts"] >= CONFIG["max_requests"]
                or nxt > CONFIG["max_estimated_tokens"]
                or nxt * CONFIG["price_per_million_usd"] / 1e6 > CONFIG["max_cost_usd"]
            ):
                raise RuntimeError("Explicit request/token/cost ceiling reached")
            delay = CONFIG.get("min_interval_seconds", 0) - (
                time.time() - self.ledger.get("last_attempt_epoch", 0)
            )
            if delay > 0:
                time.sleep(min(delay, 60))
            self.ledger["last_attempt_epoch"] = time.time()
            self.ledger["attempts"] += 1
            self.ledger["reserved_tokens"] = nxt
            dump(self.path, self.ledger)  # Reservation survives unknown/lost responses.
            start = time.perf_counter()
            req = urllib.request.Request(
                CONFIG["endpoint"],
                data=payload,
                headers={
                    "Authorization": "Bearer " + self.secret,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=90) as response:
                    raw = response.read()
                data = json.loads(raw)
            except urllib.error.HTTPError as exc:
                code = exc.code
                # Inspect error classification in memory only; never log response or headers.
                body = exc.read().decode("utf-8", errors="replace").lower()
                billing_exhausted = any(
                    s in body
                    for s in (
                        "insufficient credit",
                        "insufficient balance",
                        "insufficient fund",
                        "payment required",
                        "billing_error",
                        "quota exhausted",
                        "credits exhausted",
                    )
                )
                fatal = code in (401, 402, 403) or billing_exhausted
                rate_hint = "rate limit" in body or "tokens per minute" in body
                limits = re.findall(
                    r"(\d[\d,]*)\s*(?:tokens? per min(?:ute)?|TPM|requests? per min(?:ute)?|RPM)",
                    body,
                    re.I,
                )
                self.ledger["errors"].append(
                    {
                        "http_status": code,
                        "fatal": fatal,
                        "billing_exhausted": billing_exhausted,
                        "rate_limit_hint": rate_hint,
                        "numeric_limits": limits,
                        "payment_method_hint": "payment method" in body,
                    }
                )
                dump(self.path, self.ledger)
                if fatal or code != 429 or attempt == CONFIG["retries"]:
                    raise RuntimeError(
                        f"Voyage HTTP {code}; stopped (fatal/non-retryable/finite retry limit)"
                    ) from None
                time.sleep(min(2 ** (attempt + 1), 16))
                continue
            except (urllib.error.URLError, TimeoutError) as exc:
                self.ledger["errors"].append(
                    {
                        "transport_error": True,
                        "outcome_unknown": True,
                        "type": type(exc).__name__,
                        "reason_type": type(getattr(exc, "reason", None)).__name__,
                    }
                )
                dump(self.path, self.ledger)
                raise RuntimeError(
                    "Transport failed; reserved budget retained; no automatic repayment"
                ) from None
            elapsed = time.perf_counter() - start
            if data.get("model") != CONFIG["model"]:
                raise RuntimeError("Response model mismatch")
            rows = sorted(data["data"], key=lambda r: r["index"])
            if [r["index"] for r in rows] != list(range(len(batch))):
                raise RuntimeError("Incomplete response")
            vectors = [r["embedding"] for r in rows]
            arr = np.asarray(vectors, dtype=np.float64)
            if (
                arr.shape != (len(batch), 1024)
                or not np.isfinite(arr).all()
                or np.any(np.linalg.norm(arr, axis=1) == 0)
            ):
                raise RuntimeError("Invalid embedding response")
            self.ledger["usage_tokens"] += data["usage"]["total_tokens"]
            self.ledger["successes"] += 1
            self.ledger["api_seconds"] += elapsed
            dump(LOCAL / "responses" / f"{self.ledger['attempts']:04d}.json", data)
            for t, v in zip(batch, vectors, strict=True):
                dump(LOCAL / "vectors" / (key(t, kind) + ".json"), v)
            dump(self.path, self.ledger)
            return vectors


def probe():
    t = "def add(a, b):\n    return a + b\n"
    estimate = {
        "phase": "minimal-probe",
        "texts": 1,
        "token_byte_bound": byte_bound(t),
        "list_cost_upper_usd": byte_bound(t) * 0.12 / 1e6,
        "truncation": False,
    }
    dump(BASE / "probe-estimate.json", estimate)
    print(json.dumps(estimate), flush=True)
    API().call([t], "document")
    dump(
        BASE / "probe-result.json",
        {
            "status": "passed",
            "model": CONFIG["model"],
            "dimension": 1024,
            "dtype": "float",
            "truncation": False,
        },
    )
    print("Minimal connectivity passed; no credentials logged")


def estimate():
    work = tasks()
    missing = [
        (k, kind, t)
        for k, (kind, t) in work.items()
        if not (LOCAL / "vectors" / (k + ".json")).exists()
    ]
    bound = sum(byte_bound(t) for _, _, t in missing)
    report = {
        "unique_texts": len(work),
        "uncached_texts": len(missing),
        "conservative_token_byte_bound": bound,
        "heuristic_tokens_bytes_div_4": sum(len(t.encode()) for _, _, t in missing) / 4,
        "estimated_list_cost_upper_usd": bound * 0.12 / 1e6,
        "heuristic_list_cost_usd": bound / 4 * 0.12 / 1e6,
        "max_text_byte_bound": max(byte_bound(t) for _, _, t in missing) if missing else 0,
        "ceilings": {
            k: CONFIG[k] for k in ("max_requests", "max_estimated_tokens", "max_cost_usd")
        },
        "billing": ("Provider usage priced at list rate; account invoice/free tier unavailable."),
    }
    dump(BASE / "index-estimate.json", report)
    print(json.dumps(report), flush=True)
    if report["max_text_byte_bound"] > 32000:
        raise RuntimeError("Long node needs explicit handling")
    if bound > CONFIG["max_estimated_tokens"] or bound * 0.12 / 1e6 > CONFIG["max_cost_usd"]:
        raise RuntimeError("Plan exceeds ceilings")
    return missing


def index():
    missing = estimate()
    api = API()
    for kind in ("document", "query"):
        batch = []
        size = 0
        for _, k, t in missing:
            if k != kind:
                continue
            if batch and (
                size + byte_bound(t) > CONFIG["batch_bytes"] or len(batch) >= CONFIG["batch_items"]
            ):
                verify(Path(CONFIG["source_root"]))
                api.call(batch, kind)
                print(
                    (
                        f"cached {api.ledger['successes']} batches, "
                        f"{api.ledger['usage_tokens']} usage tokens"
                    ),
                    flush=True,
                )
                batch = []
                size = 0
            batch.append(t)
            size += byte_bound(t)
        if batch:
            verify(Path(CONFIG["source_root"]))
            api.call(batch, kind)
    verify(Path(CONFIG["source_root"]))
    print("Index complete", flush=True)


def vec(t, kind):
    return load(LOCAL / "vectors" / (key(t, kind) + ".json"))


def evaluate():
    frozen()
    data = texts()
    ids = [n["id"] for n in data]
    labels = {x["id"]: x for x in load(BASE / "annotations.json")["items"]}
    matrices = {}
    for group in ("A", "B", "C", "T"):
        a = np.asarray([vec(n[group], "document") for n in data], dtype=np.float64)
        matrices[group] = a / np.linalg.norm(a, axis=1, keepdims=True)
    start = time.perf_counter()
    bm = BM25([n["T"] for n in data])
    bm_build = time.perf_counter() - start
    records = []
    # No parameter selection: both splits evaluated once with same frozen rules.
    for q in load(BASE / "questions.json"):
        label = labels[q["id"]]
        entry = label["entries"]
        relevant = [x["id"] for x in label["related"]]
        for condition in ("zh", "expanded"):
            vector = np.asarray(vec(q[condition], "query"), dtype=np.float64)
            vector /= np.linalg.norm(vector)
            routes = {}
            latencies = {}
            for group, a in matrices.items():
                start = time.perf_counter()
                scores = a @ vector
                order = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))[:50]
                routes[group] = [ids[i] for i in order]
                latencies[group] = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            routes["BM25"] = bm.rank(q[condition], ids)
            latencies["BM25"] = (time.perf_counter() - start) * 1000
            for group, other in [("D", "T"), ("E", "BM25")]:
                start = time.perf_counter()
                routes[group] = rrf(routes["A"], routes[other])[:50]
                latencies[group] = (
                    (time.perf_counter() - start) * 1000 + latencies["A"] + latencies[other]
                )
            ovs = {
                a + "-vs-" + b: [overlap(routes[a], routes[b], k) for k in (5, 10, 50)]
                for a, b in [("A", "T"), ("A", "BM25"), ("T", "BM25")]
            }
            rescue = {}
            for other, fusion in [("T", "D"), ("BM25", "E")]:
                union = set(routes["A"]) | set(routes[other])
                only = set(routes[other]) - set(routes["A"])
                good = only & set(relevant)
                rescue[other] = {
                    "union_length": len(union),
                    "union_recall": len(union & set(relevant)) / len(relevant),
                    "code_route_recall50": len(set(routes["A"]) & set(relevant)) / len(relevant),
                    "text_unique_correct": sorted(good),
                    "text_unique_unlabelled": sorted(only - set(relevant)),
                    "rescued_into_fusion_top10": sorted(good & set(routes[fusion][:10])),
                }
            records.append(
                {
                    "question": q["id"],
                    "split": q["split"],
                    "condition": condition,
                    "metrics": {g: metrics(r, entry, relevant) for g, r in routes.items()},
                    "overlaps": ovs,
                    "rescue": rescue,
                    "latency_ms": latencies,
                    "rankings": routes,
                }
            )
    aggregates = []
    for condition in ("zh", "expanded"):
        for split in ("development", "heldout", "all"):
            rs = [
                r
                for r in records
                if r["condition"] == condition and (split == "all" or r["split"] == split)
            ]
            for group in ("A", "B", "C", "D", "E", "T", "BM25"):
                aggregates.append(
                    {
                        "condition": condition,
                        "split": split,
                        "group": group,
                        "n": len(rs),
                        **{
                            m: sum(r["metrics"][group][m] for r in rs) / len(rs)
                            for m in rs[0]["metrics"][group]
                        },
                        "mean_local_query_ms": sum(r["latency_ms"][group] for r in rs) / len(rs),
                    }
                )
    dump(LOCAL / "complete-rankings.json", records)
    # Top-10 and metrics are intentionally reviewable; complete Top-50 cache stays local.
    public = [{**r, "rankings": {g: v[:10] for g, v in r["rankings"].items()}} for r in records]
    dump(BASE / "results" / "per-question.json", public)
    dump(BASE / "results" / "aggregate.json", aggregates)
    ledger = load(LOCAL / "ledger.json")
    report = {
        "model": CONFIG["model"],
        "dimension": 1024,
        "dtype": "float",
        "candidate_count": len(ids),
        "matrices": 4,
        "logical_float32_vector_bytes": len(ids) * 4 * 1024 * 4,
        "cpu_float64_matrix_bytes": sum(a.nbytes for a in matrices.values()),
        "cache_json_bytes": sum(p.stat().st_size for p in (LOCAL / "vectors").glob("*.json")),
        "bm25_build_ms": bm_build * 1000,
        "api": ledger,
        "list_price_equivalent_usd": ledger["usage_tokens"] * 0.12 / 1e6,
        "actual_billed_usd": None,
        "python": __import__("sys").version,
        "numpy": np.__version__,
    }
    dump(BASE / "results" / "run.json", report)
    verify(Path(CONFIG["source_root"]))
    print(json.dumps(report), flush=True)


def selftest():
    assert unique(["b", "a", "b"]) == ["b", "a"]
    assert rrf(["a", "a", "b"], ["b", "c"]) == ["b", "a", "c"]
    assert rrf(["b"], ["a"]) == ["a", "b"]
    assert rrf([], []) == []
    m = metrics(["x", "b", "a"], ["a"], ["a", "b"])
    assert m["Hit@5"] == 1 and m["MRR@10"] == 1 / 3 and m["Recall@5"] == 1
    assert overlap([], [], 5)["jaccard"] is None
    assert overlap(["a"], ["a", "b"], 5)["overlap_over_k"] == 0.2
    assert BM25(["nothing"]).rank("绝无匹配", ["a"]) == []
    ts = tokenize_bm25("库存版本 FooBar snake_case")
    assert "库存" in ts and "foo" in ts and "bar" in ts and "snake" in ts and "case" in ts
    assert combine('def f():\n    "hello"', "hello\nhello\nmeta").startswith("def f():")
    a = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert list(np.argsort(-(a @ np.array([1.0, 0.0])))) == [0, 1]
    print("10 deterministic dedup/RRF/metric/empty/tokenization/cosine checks passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=["probe", "estimate", "index", "evaluate", "selftest"])
    args = parser.parse_args()
    try:
        globals()[args.step]()
    except Exception as exc:
        # Only sanitized errors emitted; never urllib Request repr/headers/environment.
        if isinstance(exc, RuntimeError):
            print(str(exc), flush=True)
        else:
            print("Stopped:", type(exc).__name__, flush=True)
        raise SystemExit(1) from None
