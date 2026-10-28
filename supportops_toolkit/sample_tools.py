"""Deterministic SupportOps tools backed by local fixtures."""

from .tools import ToolError, tool

INVOICES = {"inv-100": {"invoice_id": "inv-100", "amount": 42.50, "status": "paid", "customer_id": "cus-1"}}
ARTICLES = {
    "refund-policy": "Refunds under 100 dollars may be requested within 30 days. Escalate exceptions.",
    "delivery-policy": "Delivery status is available from the carrier after dispatch.",
}
REFUND_LIMIT = 100.0


@tool(schema_in={"type": "object", "required": ["invoice_id"], "properties": {"invoice_id": {"type": "string", "minLength": 1}}, "additionalProperties": False},
      schema_out={"type": "object", "required": ["invoice_id", "amount", "status", "customer_id"]})
def lookup_invoice(invoice_id: str) -> dict:
    try:
        return dict(INVOICES[invoice_id])
    except KeyError as exc:
        raise ToolError("not_found", "Invoice was not found") from exc


@tool(schema_in={"type": "object", "required": ["invoice_id", "amount", "reason"], "properties": {
    "invoice_id": {"type": "string", "minLength": 1}, "amount": {"type": "number", "minimum": 0, "maximum": REFUND_LIMIT}, "reason": {"type": "string", "minLength": 3, "maxLength": 200}}, "additionalProperties": False},
      schema_out={"type": "object", "required": ["status", "invoice_id", "amount"]})
def issue_refund(invoice_id: str, amount: float, reason: str) -> dict:
    invoice = lookup_invoice(invoice_id=invoice_id)
    if invoice["status"] != "paid" or amount > invoice["amount"]:
        raise ToolError("refund_denied", "Refund exceeds paid invoice balance")
    return {"status": "approved_pending_human", "invoice_id": invoice_id, "amount": float(amount), "reason": reason}


@tool(schema_in={"type": "object", "required": ["query"], "properties": {"query": {"type": "string", "minLength": 2, "maxLength": 200}}, "additionalProperties": False},
      schema_out={"type": "object", "required": ["matches"]})
def search_kb(query: str) -> dict:
    terms = set(query.lower().split())
    scored = [
        (key, text, len(terms & set(text.lower().split())))
        for key, text in ARTICLES.items()
    ]
    ranked = sorted(
        (item for item in scored if item[2] > 0),
        key=lambda item: (-item[2], item[0]),
    )
    return {
        "matches": [
            {
                "id": key,
                "source_id": f"kb:{key}",
                "text": text,
                "trust": "untrusted",
            }
            for key, text, _score in ranked[:2]
        ]
    }
