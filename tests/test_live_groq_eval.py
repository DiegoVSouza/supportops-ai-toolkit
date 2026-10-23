import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from scripts.run_live_groq_eval import (
    MODEL,
    classify_error,
    configured_keys,
    load_root_env,
    parse_assessment,
    retry_delay,
    run_with_rotation,
    verify_model_available,
)


class LiveGroqTests(unittest.TestCase):
    def test_root_env_loader_reads_without_logging_values(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as directory:
            Path(directory, ".env").write_text("GROQ_" + "API_KEY" + "=" + "test-value\n", encoding="utf-8")
            with patch("scripts.run_live_groq_eval.LAB_ROOT", Path(directory)):
                values = load_root_env({"LLM_MODE": "live"})
        self.assertEqual(values["GROQ_API_KEY"], "test-value")

    def test_configured_keys_are_deduplicated_without_identifiers(self):
        keys = configured_keys(
            {
                "GROQ_API_KEY": "one",
                "GROQ_API_KEY_1": "two",
                "GROQ_API_KEY_2": "one",
                "GROQ_API_KEY_3": "",
                "GROQ_API_KEY_4": "four",
            }
        )
        self.assertEqual(keys, ["one", "two", "four"])

    def test_mode_is_explicit_in_cli_contract(self):
        from scripts.run_live_groq_eval import require_live_mode

        with self.assertRaisesRegex(RuntimeError, "LLM_MODE=live"):
            require_live_mode({"LLM_MODE": "fake"})
        require_live_mode({"LLM_MODE": "live"})

    def test_only_retryable_errors_rotate_and_exhaust_once(self):
        clients = [object(), object()]
        factory = Mock(side_effect=clients)
        operation = Mock(side_effect=[TimeoutError("private detail"), TimeoutError("private detail")])
        sleep = Mock()
        with self.assertRaisesRegex(RuntimeError, "retryable failures exhausted") as raised:
            run_with_rotation(["secret-a", "secret-b"], factory, operation, sleep=sleep, jitter=lambda: 0)
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(operation.call_count, 2)
        self.assertEqual(sleep.call_count, 1)
        self.assertNotIn("private detail", str(raised.exception))
        self.assertEqual(classify_error(SimpleNamespace(status_code=401)), (False, "http_error", 401))
        self.assertEqual(classify_error(SimpleNamespace(status_code=429)), (True, "http_error", 429))

    def test_rate_limit_rotates_once_after_retry_after(self):
        class RateLimited(Exception):
            status_code = 429
            headers = {"retry-after": "1"}

        factory = Mock(side_effect=[object(), object()])
        operation = Mock(side_effect=[RateLimited(), "ok"])
        sleep = Mock()
        result, rotated = run_with_rotation(
            ["secret-a", "secret-b"], factory, operation, sleep=sleep, jitter=lambda: 0
        )
        self.assertEqual((result, rotated), ("ok", 1))
        sleep.assert_called_once_with(1.0)

    def test_nonretryable_error_does_not_rotate(self):
        class Unauthorized(Exception):
            status_code = 401

        factory = Mock(return_value=object())
        with self.assertRaisesRegex(RuntimeError, "non-retryable provider failure"):
            run_with_rotation(
                ["secret-a", "secret-b"], factory,
                Mock(side_effect=Unauthorized("must not escape")), sleep=Mock()
            )
        self.assertEqual(factory.call_count, 1)

    def test_retry_after_is_bounded_and_invalid_values_use_backoff(self):
        self.assertIsNone(retry_delay(0, {"retry-after": "30"}, jitter=lambda: 0))
        self.assertEqual(retry_delay(0, {"retry-after": "1.5"}, jitter=lambda: 0), 1.5)
        self.assertEqual(retry_delay(1, {"retry-after": "not-a-number"}, jitter=lambda: 0), 1.0)

    def test_model_catalog_requires_requested_model(self):
        verify_model_available(SimpleNamespace(data=[SimpleNamespace(id=MODEL)]))
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            verify_model_available(SimpleNamespace(data=[SimpleNamespace(id="other")]))

    def test_assessment_is_structurally_validated(self):
        result = parse_assessment(
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "submit_assessment",
                            "arguments": json.dumps(
                                {"decision": "answer", "tool": "lookup_invoice", "escalate": False}
                            ),
                        }
                    }
                ]
            }
        )
        self.assertEqual(result, {"decision": "answer", "tool": "lookup_invoice", "escalate": False})
        with self.assertRaisesRegex(ValueError, "invalid decision"):
            parse_assessment(
                {"tool_calls": [{"function": {"name": "submit_assessment", "arguments": '{"decision":"maybe"}'}}]}
            )


if __name__ == "__main__":
    unittest.main()
