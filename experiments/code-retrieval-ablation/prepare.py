"""AST/source preparation only. Never imports game modules or reads question labels."""

import ast
import hashlib
import io
import json
import platform
import sys
import tokenize
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOCAL = BASE / ".local"


def digest(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def extract(root):
    manifest, nodes = [], []
    for path in sorted((root / "src").rglob("*.py")):
        if path.is_symlink():
            raise RuntimeError("Source symlinks forbidden")
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        rel = path.relative_to(root).as_posix()
        manifest.append({"path": rel, "sha256": digest(raw), "bytes": len(raw)})
        lines = text.splitlines(keepends=True)
        tree = ast.parse(text, filename=rel, type_comments=True)
        comments = [
            (t.start[0], t.string)
            for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type == tokenize.COMMENT
        ]
        module_doc = ast.get_docstring(tree, clean=False) or ""

        def walk(
            parent,
            owners=(),
            classes=(),
            class_docs=(),
            *,
            lines=lines,
            text=text,
            rel=rel,
            raw=raw,
            module_doc=module_doc,
            comments=comments,
        ):
            for item in ast.iter_child_nodes(parent):
                if isinstance(item, ast.ClassDef):
                    walk(
                        item,
                        owners + (item.name,),
                        classes + (item.name,),
                        class_docs + (ast.get_docstring(item, clean=False) or "",),
                    )
                elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = min([item.lineno] + [d.lineno for d in item.decorator_list])
                    # Include contiguous same-indent leading comments; no blank-line crossing.
                    indent = len(lines[item.lineno - 1]) - len(lines[item.lineno - 1].lstrip())
                    while start > 1:
                        prev = lines[start - 2]
                        if (
                            prev.strip().startswith("#")
                            and len(prev) - len(prev.lstrip()) == indent
                        ):
                            start -= 1
                        else:
                            break
                    source = "".join(lines[start - 1 : item.end_lineno])
                    # Keep the literal header incl. multiline arguments, annotations and defaults.
                    toks = list(
                        tokenize.generate_tokens(
                            io.StringIO("".join(lines[item.lineno - 1 : item.end_lineno])).readline
                        )
                    )
                    depth = 0
                    stop = None
                    for t in toks:
                        if t.type == tokenize.OP:
                            if t.string in "([{":
                                depth += 1
                            elif t.string in ")]}":
                                depth -= 1
                            elif t.string == ":" and depth == 0:
                                stop = t.end
                                break
                    header_lines = lines[item.lineno - 1 : item.end_lineno]
                    signature = (
                        "".join(header_lines[: stop[0] - 1]) + header_lines[stop[0] - 1][: stop[1]]
                    ).strip()
                    qual = ".".join(owners + (item.name,))
                    node_id = f"{rel}::{qual}@{item.lineno}"
                    # Facts use literal source segments, never ast.unparse. Exclude nested bodies.
                    direct = []

                    def visit(n, direct=direct):
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            return
                        direct.append(n)
                        for ch in ast.iter_child_nodes(n):
                            if not isinstance(
                                ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                            ):
                                visit(ch)

                    for body in item.body:
                        visit(body)

                    def seg(n, text=text):
                        return ast.get_source_segment(text, n) or ""

                    calls = list(
                        dict.fromkeys(seg(n.func) for n in direct if isinstance(n, ast.Call))
                    )
                    returns = list(
                        dict.fromkeys(
                            seg(n.value)
                            for n in direct
                            if isinstance(n, (ast.Return, ast.Yield)) and n.value
                        )
                    )
                    stores = list(
                        dict.fromkeys(
                            seg(n)
                            for n in direct
                            if isinstance(n, (ast.Attribute, ast.Subscript))
                            and isinstance(n.ctx, ast.Store)
                        )
                    )
                    nodes.append(
                        {
                            "id": node_id,
                            "path": rel,
                            "qualname": qual,
                            "class": ".".join(classes),
                            "line": item.lineno,
                            "start": start,
                            "end": item.end_lineno,
                            "signature": signature,
                            "source": source,
                            "source_sha256": digest(source),
                            "file_sha256": digest(raw),
                            "module_doc": module_doc,
                            "class_docs": class_docs,
                            "docstring": ast.get_docstring(item, clean=False) or "",
                            "comments": [
                                {"line": n, "text": s}
                                for n, s in comments
                                if start <= n <= item.end_lineno
                            ],
                            "facts": {
                                "calls": calls,
                                "returns": returns,
                                "stores": stores,
                                "raises": list(
                                    dict.fromkeys(
                                        seg(n.exc)
                                        for n in direct
                                        if isinstance(n, ast.Raise) and n.exc
                                    )
                                ),
                            },
                        }
                    )
                    walk(item, owners + (item.name, "<locals>"), classes, class_docs)
                else:
                    walk(item, owners, classes, class_docs)

        walk(tree)
    if len({n["id"] for n in nodes}) != len(nodes):
        raise RuntimeError("Duplicate node ID")
    return manifest, nodes


def verify(root):
    saved = json.loads((BASE / "source-manifest.json").read_text(encoding="utf-8"))
    paths = sorted((root / "src").rglob("*.py"))
    current = [
        {
            "path": p.relative_to(root).as_posix(),
            "sha256": digest(p.read_bytes()),
            "bytes": p.stat().st_size,
        }
        for p in paths
    ]
    if current != saved["files"]:
        raise RuntimeError("SOURCE DRIFT: refreeze corpus, labels and summaries; do not mix")
    return (
        json.loads((LOCAL / "nodes.json").read_text(encoding="utf-8"))
        if (LOCAL / "nodes.json").exists()
        else extract(root)[1]
    )


if __name__ == "__main__":
    root = Path(sys.argv[2]).resolve()
    if sys.argv[1] == "prepare":
        manifest, nodes = extract(root)
        if (BASE / "source-manifest.json").exists():
            verify(root)
        dump(
            BASE / "source-manifest.json",
            {
                "version": "ast-source-v1",
                "parser": f"CPython {platform.python_version()} ast/tokenize",
                "root": str(root),
                "files": manifest,
                "node_count": len(nodes),
                "node_ids_sha256": digest("\n".join(n["id"] for n in nodes)),
            },
        )
        dump(LOCAL / "nodes.json", nodes)
        dump(
            LOCAL / "synopsis.json",
            [
                {k: n[k] for k in ("id", "qualname", "signature", "docstring", "facts")}
                for n in nodes
            ],
        )
        print(
            json.dumps(
                {
                    "files": len(manifest),
                    "nodes": len(nodes),
                    "max_source_bytes": max(len(n["source"].encode()) for n in nodes),
                }
            )
        )
    elif sys.argv[1] == "verify":
        print("verified", len(verify(root)))
