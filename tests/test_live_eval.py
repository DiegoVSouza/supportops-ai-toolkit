import json
import unittest
from unittest.mock import patch

from scripts.run_live_free_eval import (
    MODEL,
    parse_model_reply,
    parse_tool_arguments,
    verify_zero_price_model,
)


class Response:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.value).encode()


class LiveEvalTests(unittest.TestCase):
    def test_parses_json_object_and_validates_contract(self):
        response = parse_model_reply(
            '```json\n{"decision":"answer","tool":"search_kb",'
            '"answer":"Refunds are within policy.","escalate":false}\n```'
        )
        self.assertEqual(response["tool"], "search_kb")
        self.assertFalse(response["escalate"])

    def test_rejects_invalid_model_shape(self):
        with self.assertRaisesRegex(ValueError, "invalid decision"):
            parse_model_reply('{"decision":"maybe","tool":"search_kb","answer":"x","escalate":false}')

    def test_parses_required_tool_call_arguments(self):
        prediction = parse_tool_arguments(
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "submit_assessment",
                            "arguments": '{"decision":"answer","tool":"search_kb",'
                            '"answer":"Refunds under policy.","escalate":false}',
                        }
                    }
                ]
            }
        )
        self.assertEqual(prediction["decision"], "answer")

    def test_verifies_zero_price_from_authenticated_catalog(self):
        body = {
            "data": [
                {"id": MODEL, "pricing": {"prompt": "0", "completion": "0"}}
            ]
        }
        with patch("scripts.run_live_free_eval.urlopen", return_value=Response(body)):
            entry = verify_zero_price_model("test-key")
        self.assertEqual(entry["id"], MODEL)

    def test_refuses_nonzero_catalog_price(self):
        body = {
            "data": [
                {"id": MODEL, "pricing": {"prompt": "0.1", "completion": "0"}}
            ]
        }
        with patch("scripts.run_live_free_eval.urlopen", return_value=Response(body)):
            with self.assertRaisesRegex(RuntimeError, "nonzero"):
                verify_zero_price_model("test-key")


if __name__ == "__main__":
    unittest.main()
