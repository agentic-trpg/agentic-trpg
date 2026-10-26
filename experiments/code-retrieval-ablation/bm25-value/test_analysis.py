"""Deterministic boundary tests; synthetic data only, no game/API calls."""

import copy
import unittest
from unittest.mock import patch

from analyze import aggregate, analyze, delta, quota_analysis, supplement, unique_analysis
from rerank import request_pair, validate_scores
from retrieval import metrics


class AnalysisTests(unittest.TestCase):
    def test_dedup_against_selected_prefix_not_full_vector(self):
        vector = [f"v{i}" for i in range(50)]
        lexical = ["v0", "v41", "v41", "outside"]
        mixed = supplement(vector, lexical, 40, 10)
        self.assertEqual(mixed, vector[:40] + ["v41", "outside"])
        row = quota_analysis(vector, lexical, 40, 10, 50, ["v41"], ["v41", "v49", "outside"])
        self.assertEqual(row["tail_already_in_baseline"], ["v41"])
        self.assertEqual(row["tail_truly_outside_baseline"], ["outside"])
        self.assertEqual(row["added_correct"], ["outside"])
        self.assertEqual(row["lost_correct"], ["v49"])
        self.assertEqual(row["net_correct"], 0)
        self.assertEqual(row["mixed"]["length"], 42)

    def test_unique_candidates_and_bm25_original_rank(self):
        row = unique_analysis(["a", "b"], ["b", "c", "d"], ["b", "d"])
        self.assertEqual(row["bm25_unique"], ["c", "d"])
        self.assertEqual(row["bm25_unique_correct"], [{"id": "d", "bm25_rank": 3}])
        self.assertEqual(row["bm25_unique_unlabelled"], ["c"])
        self.assertEqual(row["overlap"]["jaccard"], 1 / 4)
        self.assertEqual(row["union_recall"], 1)

    def test_gains_losses_and_net_are_related_not_entries_only(self):
        row = delta(["entry", "old"], ["other", "new"], ["entry", "old", "new"], ["entry"])
        self.assertEqual(row["added_correct"], ["new"])
        self.assertEqual(row["lost_correct"], ["entry", "old"])
        self.assertEqual(row["net_correct"], -1)
        self.assertEqual(row["lost_entries"], ["entry"])

    def test_short_empty_and_no_padding(self):
        self.assertEqual(supplement([], [], 7, 3), [])
        self.assertEqual(supplement(["a"], [], 7, 3), ["a"])
        self.assertEqual(supplement([], ["b", "b", "c"], 7, 3), ["b", "c"])
        self.assertIsNone(unique_analysis([], [], ["a"])["overlap"]["jaccard"])
        self.assertEqual(metrics([], ["a"], ["a"])["Recall@10"], 0)

    def test_top10_order_and_metric_semantics(self):
        vector = [f"v{i}" for i in range(10)]
        lexical = ["v0", "entry", "v9", "rel", "extra"]
        row = quota_analysis(vector, lexical, 7, 3, 10, ["entry"], ["entry", "rel", "v8"])
        self.assertEqual(row["selected"], vector[:7] + ["entry", "v9", "rel"])
        self.assertEqual(row["mixed"]["Hit@5"], 0)
        self.assertEqual(row["mixed"]["Hit@10"], 1)
        self.assertEqual(row["mixed"]["MRR@10"], 1 / 8)
        self.assertEqual(row["mixed"]["Recall@10"], 2 / 3)
        self.assertEqual(row["lost_correct"], ["v8"])

    def test_real_results_original_labels_and_aggregate_proportions(self):
        from analyze import HERE, load

        original = load(HERE.parent / "annotations.json")
        snapshot = copy.deepcopy(original)
        # Tests run from the committed artifacts, even when vector caches are absent.
        records = load(HERE / "results" / "per-question.json")
        questions = load(HERE.parent / "questions.json")

        def original_only(path):
            if path.name == "questions.json":
                return questions
            if path.name == "annotations.json":
                return original
            raise AssertionError("Analysis must not read supplemental review or any other labels")

        with patch("analyze.load", side_effect=original_only):
            rows = analyze(records)
        self.assertEqual(original, snapshot)
        groups = aggregate(rows)
        for group in groups:
            rs = [
                r
                for r in rows
                if r["condition"] == group["condition"]
                and (group["split"] == "all" or r["split"] == group["split"])
            ]
            expected = sum(bool(r["unique"]["C"]["bm25_unique_correct"]) for r in rs) / len(rs)
            self.assertEqual(group["unique"]["C"]["benefited_fraction"], expected)
            self.assertEqual(
                group["quotas"]["40+10"]["net_correct_pairs"],
                sum(r["quotas"]["40+10"]["net_correct"] for r in rs),
            )
        # Supplementary review is never read by analyze/aggregate: even an invented
        # posthoc positive is not part of the original metric denominators.
        invented_review = {"items": [{"id": "invented", "relevant": True}]}
        self.assertNotIn(invented_review["items"][0]["id"], rows[0]["original_related"])
        label = next(x for x in original["items"] if x["id"] == rows[0]["question"])
        self.assertEqual(rows[0]["original_related"], [x["id"] for x in label["related"]])

    def test_rerank_pair_no_answer_or_retrieval_scores_and_stable_ties(self):
        record = {
            "question": "Q",
            "condition": "zh",
            "rankings": {"C": ["b", "a"]},
            "quotas": {"40+10": {"selected": ["a", "c"]}},
        }
        requests = request_pair(
            record,
            "query",
            {"a": "source a", "b": "source b", "c": "source c"},
            {"model": "test", "version": "1"},
        )
        self.assertEqual(requests[0]["node_ids"], ["a", "b"])
        self.assertEqual(requests[0]["request"]["query"], requests[1]["request"]["query"])
        self.assertEqual(
            set(requests[0]["request"]),
            {"model", "version", "query", "documents", "truncation", "return_scores_for_all"},
        )
        pack = {
            "settings": {"model": "test", "version": "1"},
            "settings_sha256": "hash",
            "requests": requests,
        }
        scores = {
            "model": "test",
            "version": "1",
            "settings_sha256": "hash",
            "results": [
                {
                    **{k: r[k] for k in ("question", "condition", "arm", "request_key")},
                    "scores": [{"index": 1, "score": 1}, {"index": 0, "score": 1}],
                }
                for r in requests
            ],
        }
        self.assertEqual(validate_scores(pack, scores)[("Q", "zh", "R1")], ["a", "b"])
        invalid = copy.deepcopy(scores)
        invalid["results"][0]["scores"][0]["index"] = 0
        with self.assertRaises(AssertionError):
            validate_scores(pack, invalid)
        invalid = copy.deepcopy(scores)
        invalid["results"][0]["request_key"] = "wrong"
        with self.assertRaises(AssertionError):
            validate_scores(pack, invalid)


if __name__ == "__main__":
    unittest.main()
