import unittest

from supportops_toolkit.cost.cache import ExactCache, SemanticCache
from supportops_toolkit.cost.routing import ModelRouter, TaskProfile, TokenBudget
from supportops_toolkit.cost.streaming import collect_stream, stream_text
from cost.report import build_report


class CostUtilityTests(unittest.TestCase):
    def test_exact_cache_order_capacity_and_hits(self):
        cache = ExactCache(max_entries=2)
        cache.put({"b": 2, "a": 1}, "first")
        self.assertEqual(cache.get({"a": 1, "b": 2}), "first")
        cache.put("second", 2)
        cache.get({"a": 1, "b": 2})
        cache.put("third", 3)
        self.assertIsNone(cache.get("second"))
        self.assertEqual(cache.hits, 2)
        with self.assertRaises(ValueError):
            ExactCache(0)

    def test_semantic_lexical_similarity_and_namespace(self):
        cache = SemanticCache(threshold=0.6)
        cache.put("refund policy deadline", "source-1", namespace="tenant-a")
        self.assertEqual(cache.get("refund deadline", namespace="tenant-a"), "source-1")
        self.assertIsNone(cache.get("refund deadline", namespace="tenant-b"))
        self.assertEqual((cache.hits, cache.misses), (1, 1))
        with self.assertRaises(ValueError):
            SemanticCache(threshold=0)

    def test_router_escalates_on_complexity_risk_or_requirement(self):
        router = ModelRouter()
        self.assertEqual(router.pick(TaskProfile()), "model-cheap")
        self.assertEqual(router.pick(TaskProfile(complexity=4)), "model-strong")
        self.assertEqual(router.pick(TaskProfile(risk=4)), "model-strong")
        self.assertEqual(router.pick(TaskProfile(require_strong=True)), "model-strong")
        with self.assertRaises(ValueError):
            router.pick(TaskProfile(complexity=0))

    def test_token_budget_bounds_and_remaining(self):
        budget = TokenBudget(10)
        budget.consume(7)
        self.assertEqual(budget.remaining, 3)
        budget.consume(3)
        with self.assertRaises(ValueError):
            budget.consume(1)
        with self.assertRaises(ValueError):
            budget.consume(-1)

    def test_streaming_and_cost_report_pending_or_real_delta(self):
        self.assertEqual(list(stream_text(["safe ", "stream"])), ["safe ", "stream"])
        self.assertEqual(collect_stream(["safe ", "stream"]), "safe stream")
        with self.assertRaises(TypeError):
            collect_stream(["ok", 3])
        self.assertEqual(build_report()["status"], "PENDING")
        report = build_report({"requests": 5, "cost_usd": 1.0}, {"requests": 4, "cost_usd": 0.8})
        self.assertEqual(report["delta"]["requests"], -1)
        self.assertAlmostEqual(report["delta"]["cost_usd"], -0.2)
        self.assertEqual(report["delta"]["tokens"], "PENDING")


if __name__ == "__main__":
    unittest.main()
