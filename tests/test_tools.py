import time
import unittest

from supportops_toolkit.sample_tools import issue_refund, lookup_invoice, search_kb
from supportops_toolkit.tools import ToolError, classify_error, get_tool, tool


class ToolContractTests(unittest.TestCase):
    def test_registry_and_sample_tool_success(self):
        self.assertEqual(get_tool("lookup_invoice"), lookup_invoice)
        self.assertEqual(lookup_invoice(invoice_id="inv-100")["amount"], 42.5)
        self.assertTrue(search_kb(query="refund policy")["matches"])

    def test_input_shape_and_refund_bounds(self):
        with self.assertRaises(ToolError):
            lookup_invoice(invoice_id="inv-100", unexpected=True)
        with self.assertRaises(ToolError):
            issue_refund(invoice_id="inv-100", amount=100.01, reason="customer request")
        with self.assertRaises(ToolError):
            issue_refund(invoice_id="inv-100", amount=43, reason="too much")

    def test_unknown_invoice_and_output_validation(self):
        with self.assertRaisesRegex(ToolError, "not found"):
            lookup_invoice(invoice_id="missing")
        @tool(schema_in={"type": "object"}, schema_out={"type": "integer"})
        def bad_output():
            return "not an integer"
        with self.assertRaises(ToolError):
            bad_output()

    def test_retry_transient_but_fail_fatal(self):
        calls = {"count": 0}
        @tool(schema_in={"type": "object"}, schema_out={"type": "integer"}, retries=2, base_delay_s=0)
        def transient():
            calls["count"] += 1
            if calls["count"] < 3:
                raise ConnectionError("temporary")
            return 7
        self.assertEqual(transient(), 7)
        self.assertEqual(calls["count"], 3)
        self.assertEqual(classify_error(ToolError("fatal", "bad")), "fatal")
        self.assertEqual(classify_error(ConnectionError()), "retryable")
        @tool(schema_in={"type": "object"}, schema_out={"type": "integer"}, retries=5, base_delay_s=0)
        def fatal():
            raise ValueError("permanent")
        with self.assertRaises(ToolError):
            fatal()

    def test_timeout_and_invalid_configuration(self):
        @tool(schema_in={"type": "object"}, schema_out={"type": "integer"}, timeout_s=0.01, base_delay_s=0)
        def slow():
            time.sleep(0.05)
            return 1
        with self.assertRaisesRegex(ToolError, "exceeded"):
            slow()
        with self.assertRaises(ValueError):
            tool(schema_in={}, schema_out={}, timeout_s=0)


if __name__ == "__main__":
    unittest.main()
