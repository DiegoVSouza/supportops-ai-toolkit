import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from scripts.run_live_groq_eval import (
    MODEL,
    classify_error,
    configured_keys,
    build_messages,
    load_root_env,
    parse_assessment,
    retry_delay,
    run_with_rotation,
    verify_model_available,
)


class LiveGroqTests(unittest.TestCase):
    def test_gpt_oss_request_uses_low_reasoning_with_an_explicit_completion_cap(self):
        from scripts.run_live_groq_eval import _predict, MAX_COMPLETION_TOKENS

        client = Mock()
        _predict(client, {"text": "Synthetic invoice policy question."})
        arguments = client.chat.completions.create.call_args.kwargs
        self.assertEqual(arguments["reasoning_effort"], "low")
        self.assertEqual(arguments["max_completion_tokens"], MAX_COMPLETION_TOKENS)
        self.assertNotIn("max_tokens", arguments)

    def test_root_env_loader_reads_without_logging_values(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as directory:
            Path(directory, ".env").write_text(
                "GROQ_" + "API_KEY" + "=" + "test-value\n", encoding="utf-8"
            )
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
        self.assertEqual(keys, ["two", "one", "four"])

    def test_mode_is_explicit_in_cli_contract(self):
        from scripts.run_live_groq_eval import require_live_mode

        with self.assertRaisesRegex(RuntimeError, "LLM_MODE=live"):
            require_live_mode({"LLM_MODE": "fake"})
        require_live_mode({"LLM_MODE": "live"})

    def test_only_retryable_errors_rotate_and_exhaust_once(self):
        clients = [object(), object()]
        factory = Mock(side_effect=clients)
        operation = Mock(
            side_effect=[TimeoutError("private detail"), TimeoutError("private detail")]
        )
        sleep = Mock()
        with self.assertRaisesRegex(
            RuntimeError, "retryable failures exhausted"
        ) as raised:
            run_with_rotation(
                ["secret-a", "secret-b"],
                factory,
                operation,
                sleep=sleep,
                jitter=lambda: 0,
            )
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(operation.call_count, 2)
        self.assertEqual(sleep.call_count, 1)
        self.assertNotIn("private detail", str(raised.exception))
        self.assertEqual(
            classify_error(SimpleNamespace(status_code=401)), (False, "http_error", 401)
        )
        self.assertEqual(
            classify_error(SimpleNamespace(status_code=429)), (True, "http_error", 429)
        )

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
                ["secret-a", "secret-b"],
                factory,
                Mock(side_effect=Unauthorized("must not escape")),
                sleep=Mock(),
            )
        self.assertEqual(factory.call_count, 1)

    def test_retry_after_is_bounded_and_invalid_values_use_backoff(self):
        self.assertIsNone(retry_delay(0, {"retry-after": "30"}, jitter=lambda: 0))
        self.assertEqual(retry_delay(0, {"retry-after": "1.5"}, jitter=lambda: 0), 1.5)
        self.assertEqual(
            retry_delay(1, {"retry-after": "not-a-number"}, jitter=lambda: 0), 1.0
        )

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
                                {
                                    "decision": "answer",
                                    "tool": "lookup_invoice",
                                    "escalate": False,
                                }
                            ),
                        }
                    }
                ]
            }
        )
        self.assertEqual(
            result, {"decision": "answer", "tool": "lookup_invoice", "escalate": False}
        )
        with self.assertRaisesRegex(ValueError, "invalid decision"):
            parse_assessment(
                {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "submit_assessment",
                                "arguments": '{"decision":"maybe"}',
                            }
                        }
                    ]
                }
            )

    def test_prompt_explains_read_only_lookup_vs_refund_action(self):
        prompt = build_messages(
            {"text": "Paid invoice under policy, customer asks within 30 days"}
        )[0]["content"]
        self.assertIn("lookup_invoice is a read-only lookup", prompt)
        self.assertIn("issue_refund is a downstream action", prompt)
        self.assertIn("does not identify an invoice or verified balance", prompt)

    def test_completed_domain_mismatch_is_not_a_retryable_provider_error(self):
        factory = Mock(return_value=object())
        operation = Mock(return_value={"tool": "issue_refund"})
        response, rotated = run_with_rotation(
            ["secret-a", "secret-b"], factory, operation, sleep=Mock()
        )
        self.assertEqual(response, {"tool": "issue_refund"})
        self.assertEqual(rotated, 0)
        self.assertEqual(operation.call_count, 1)


class LegacyEntryPointGuardTests(unittest.TestCase):
    def test_live_entry_refuses_before_credentials_provider_or_artifact(self):
        from unittest.mock import patch

        from scripts.run_live_groq_eval import main

        with (
            patch("scripts.run_live_groq_eval.load_root_env") as credentials,
            patch("scripts.run_live_groq_eval._new_client") as provider,
            patch("scripts.run_live_groq_eval.Path.write_text") as write,
        ):
            self.assertEqual(main({"LLM_MODE": "live"}), 2)
        credentials.assert_not_called()
        provider.assert_not_called()
        write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
