"""Small independent tests; never imports or runs the game."""

import ast
import json
import tempfile
import unittest
from pathlib import Path

from prepare import LOCAL, dump, extract
from retrieval import BM25, combine, metrics, overlap, rrf, tokenize_bm25


class RetrievalTests(unittest.TestCase):
    def test_rrf_dedup_and_rank_one(self):
        self.assertEqual(rrf(["x", "x", "y"], ["y", "z"]), ["y", "x", "z"])
        self.assertEqual(rrf(["b"], ["a"]), ["a", "b"])
        self.assertEqual(rrf([], []), [])

    def test_route_limit(self):
        route = [str(n).zfill(3) for n in range(60)]
        self.assertEqual(len(rrf(route)), 50)
        self.assertNotIn("050", rrf(route))

    def test_metrics(self):
        value = metrics(["bad", "entry", "related"], ["entry"], ["entry", "related", "missing"])
        self.assertEqual(value["Hit@5"], 1)
        self.assertEqual(value["MRR@10"], 0.5)
        self.assertEqual(value["Recall@10"], 2 / 3)
        self.assertEqual(metrics(["x"] * 10 + ["entry"], ["entry"], ["entry"])["MRR@10"], 0)

    def test_overlap_short_and_empty(self):
        value = overlap(["a"], ["a", "b"], 5)
        self.assertEqual((value["length_a"], value["length_b"]), (1, 2))
        self.assertEqual(value["overlap_over_k"], 0.2)
        self.assertEqual(value["jaccard"], 0.5)
        self.assertIsNone(overlap([], [], 10)["jaccard"])

    def test_bm25_chinese_and_identifiers(self):
        tokens = tokenize_bm25("库存版本 HTTPServer snake_case")
        self.assertTrue({"库存", "版本", "http", "server", "snake", "case"} <= set(tokens))
        index = BM25(["库存版本更新", "普通地图"])
        self.assertEqual(index.rank("库存", ["a", "b"]), ["a"])
        self.assertEqual(index.rank("zzzzz", ["a", "b"]), [])

    def test_combine_preserves_source(self):
        source = '@decorator\ndef f(x):\n    """hello doc"""\n    # useful comment\n    return x\n'
        combined = combine(source, "def f(x):\n\nhello doc\n\nnew context")
        self.assertTrue(combined.startswith(source.rstrip()))
        self.assertEqual(combined.count("hello doc"), 1)
        self.assertIn("# useful comment", combined)
        with_summary = combine(source, "hello doc\nSummary: returns its input")
        self.assertEqual(with_summary.count("hello doc"), 1)
        self.assertIn("Summary: returns its input", with_summary)

    def test_atomic_json_and_lf(self):
        LOCAL.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=LOCAL) as temp:
            target = Path(temp) / "cache.json"
            dump(target, {"label": "中文"})
            self.assertNotIn(b"\r\n", target.read_bytes())
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"label": "中文"})
            dump(target, {"new": 2})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"new": 2})
            self.assertFalse(target.with_name("cache.json.tmp").exists())

    def test_parser_nested_classes_decorators_comments(self):
        LOCAL.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=LOCAL) as temp:
            root = Path(temp)
            (root / "src").mkdir()
            source = (
                '"""模块背景"""\nclass A:\n    """class context"""\n'
                "    # preceding comment\n    @deco(\n        1\n    )\n"
                '    async def same(self, x: str = "汉字") -> str:\n'
                '        """function context"""\n        # ordinary comment\n'
                "        def inside(y):\n            return y\n"
                "        return inside(x)\nclass B:\n    def same(self):\n        return 2\n"
            )
            (root / "src" / "sample.py").write_text(source, encoding="utf-8")
            manifest, nodes = extract(root)
            self.assertEqual(len(nodes), 3)
            self.assertEqual(len({n["id"] for n in nodes}), 3)
            outer, inner, other = nodes
            self.assertIn("@deco(", outer["source"])
            self.assertIn("# preceding comment", outer["source"])
            self.assertIn("# ordinary comment", outer["source"])
            self.assertEqual(inner["qualname"], "A.same.<locals>.inside")
            self.assertEqual(outer["module_doc"], "模块背景")
            self.assertEqual(outer["class_docs"], ("class context",))
            self.assertIn('"汉字"', outer["signature"])
            self.assertEqual(inner["facts"]["returns"], ["y"])
            self.assertNotEqual(outer["id"], other["id"])
            self.assertEqual(ast.parse(source).body[1].body[1].lineno, outer["line"])


if __name__ == "__main__":
    unittest.main()
