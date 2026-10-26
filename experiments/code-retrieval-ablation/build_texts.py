"""Source-only summary materialization. Does not open questions, answers or results."""

import json
import time
from pathlib import Path

from prepare import BASE, dump, verify

start = time.perf_counter()
config = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))
nodes = verify(Path(config["source_root"]))
authored = json.loads((BASE / "summary-semantics.json").read_text(encoding="utf-8"))
records = []
for n in nodes:
    # Source literal docstrings only: no architecture chapter injection.
    module = n["module_doc"][:400]
    cls = "\n".join(n["class_docs"])[:400]
    context = [
        {
            "kind": "module-docstring",
            "path": n["path"],
            "file_sha256": n["file_sha256"],
            "text": module,
        },
        {
            "kind": "class-docstrings",
            "path": n["path"],
            "file_sha256": n["file_sha256"],
            "text": cls,
        },
    ]
    blocks = [
        f"Path: {n['path']}\nQualified name: {n['qualname']}\nClass: {n['class'] or '(module)'}",
        n["signature"],
    ]
    if module:
        blocks.append("Module context: " + module)
    if cls:
        blocks.append("Class context: " + cls)
    if n["docstring"]:
        blocks.append(n["docstring"])
    t0 = "\n\n".join(blocks)
    records.append(
        {
            "id": n["id"],
            "source_sha256": n["source_sha256"],
            "file_sha256": n["file_sha256"],
            "summary": authored["summaries"][n["id"]],
            "T0": t0,
            "context": context,
        }
    )
dump(
    BASE / "summaries.json",
    {"version": "T0-T1-v1", "author": authored["author"], "source_only": True, "records": records},
)
dump(
    BASE / "summary-cost.json",
    {
        "semantic_authoring_started_at": authored["started_at"],
        "semantic_authoring_finished_at": authored["finished_at"],
        "materialize_seconds": time.perf_counter() - start,
        "records": len(records),
        "summary_utf8_bytes": sum(len(r["summary"].encode()) for r in records),
        "summary_characters": sum(len(r["summary"]) for r in records),
        "additional_generation_api_calls": 0,
        "additional_generation_api_cost_usd": 0,
        "codex_token_usage": None,
        "codex_cost_usd": None,
        "note": (
            "Authoring interval includes review and runner implementation; "
            "not isolated human labor or token billing. Current Codex used "
            "source and structural facts. This materializer receives no "
            "questions, labels or rankings. Same agent authored labels; "
            "not an independently blinded study."
        ),
    },
)
print("materialized", len(records), "source-bound summaries")
