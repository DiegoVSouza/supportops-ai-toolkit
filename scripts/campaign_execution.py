"""Sealed, resumable executor for the P02 `p02-dev-v1` development campaign.

Live attempts go through the root accounted boundary (`scripts/harness/live_provider_transport.py`);
nothing here reads a credential. Trial records are content-free: no ticket text, no prompt, no response text.
Fixture sessions exercise every code path but are labelled `fixture` and never count as live.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import subprocess
import sys
import time
from contextlib import closing, nullcontext
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from scripts.campaign_corpus import MODEL_FAMILIES, BuiltCase, build_case, build_payload
from scripts.campaign_ledger import CampaignBlocked, CampaignLedger
from scripts.campaign_observe import grade, observe

MODEL = "openai/gpt-oss-20b"
CAMPAIGN = "p02-dev-v1"
DATASET = "p02-live-v1"
PILOT_IDS = (
    "refund_eligible-01",
    "refund_exceeds_balance-03",
    "invoice_missing-01",
    "knowledge_question-02",
    "prompt_injection-03",
    "contradictory_evidence-01",
)
PRICE_IN, PRICE_OUT = Decimal("0.075"), Decimal("0.30")
TRIAL_CALLS = 24
CAPACITY_WAITS = {
    "free_token_minute_checkpoint",
    "free_request_minute_checkpoint",
    "provider_token_capacity_checkpoint",
    "provider_cooldown_checkpoint",
    "provider_request_capacity_checkpoint",
}
SAFE_REASON = re.compile(r"[a-z_]{1,64}")


def use_campaign(campaign: str) -> None:
    """Select an explicitly known development campaign; never enable it at the account boundary."""
    if campaign not in {"p02-dev-v1", "p02-dev-v2"}:
        raise ValueError("unknown development campaign")
    global CAMPAIGN
    CAMPAIGN = campaign


def cost_of(input_tokens: int, output_tokens: int) -> Decimal:
    return (Decimal(input_tokens) * PRICE_IN + Decimal(output_tokens) * PRICE_OUT) / 1000000


TRIAL_CAPS = {"requests": 1, "input_tokens": 4096, "output_tokens": 512, "estimated_cost_usd": cost_of(4096, 512)}


def campaign_caps() -> dict[str, Any]:
    return {
        "requests": TRIAL_CALLS,
        "input_tokens": TRIAL_CALLS * TRIAL_CAPS["input_tokens"],
        "output_tokens": TRIAL_CALLS * TRIAL_CAPS["output_tokens"],
        "estimated_cost_usd": TRIAL_CALLS * TRIAL_CAPS["estimated_cost_usd"],
    }


class ExecutionBlocked(RuntimeError):
    """A fixed, content-free stop reason."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def wilson(successes: int, total: int) -> list[float] | None:
    if total <= 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def percentile(values: list[float], pct: int) -> float | None:
    """Nearest-rank percentile; None for an empty sample."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(pct / 100 * len(ordered)) - 1)]


# --- provenance ---------------------------------------------------------------------------------

def git(project: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, timeout=30)
    if result.returncode:
        raise ExecutionBlocked("source_provenance")
    return result.stdout.decode().strip()


def source_paths(project: Path) -> list[str]:
    return sorted(
        path
        for path in git(project, "ls-files").splitlines()
        if path.startswith(("supportops_toolkit/", "scripts/", "tests/", "evals/", "guardrails/", "cost/", "agent/"))
        or path in {"pyproject.toml", "uv.lock", "harness.yaml"}
    )


ROOT_FILES = (
    "scripts/harness/live_free_account.py",
    "scripts/harness/live_provider_transport.py",
    "shared/policies/groq-free-campaign.json",
    ".planning/llm-live-readiness/phases/058-p02-live-campaign/AUTHORIZATION.json",
)


def root_files() -> tuple[str, ...]:
    if CAMPAIGN == "p02-dev-v2":
        return ROOT_FILES[:-1] + (".planning/llm-live-readiness/phases/064-p02-candidate-development/AUTHORIZATION.json",)
    return ROOT_FILES


def candidate_preflight(account: Any, *, freezing: bool) -> dict[str, int]:
    """Check committed authority and cumulative history without contacting the provider."""
    if account._p02_campaigns().get("p02-dev-v2") != 24:
        raise ExecutionBlocked("candidate_authorization_missing")
    rows = account._history()
    if any(row["event"] == "reserved" for row in rows):
        raise ExecutionBlocked("uncertain_attempt_requires_reconciliation")
    dev = [row for row in rows if row["project"] == "p02" and row["campaign"].startswith("p02-dev-")]
    current = [row for row in dev if row["campaign"] == "p02-dev-v2"]
    if freezing and current:
        raise ExecutionBlocked("candidate_already_started")
    if any(row["event"] == "completed" and row["status"] != "ok" for row in current):
        raise ExecutionBlocked("candidate_stopped_requires_review")
    if len(dev) + (24 if freezing else 0) > 72:
        raise ExecutionBlocked("development_capacity_insufficient")
    return {"development_used": len(dev), "candidate_used": len(current)}


def verify_candidate_authority(lab: Path, *, freezing: bool) -> dict[str, int]:
    """Read the root guard under its account lock; never load credentials or dispatch."""
    sys.path.insert(0, str(lab / "scripts/harness"))
    from live_free_account import AccountBlocked, SharedAccount, machine_lease

    try:
        policy = json.loads((lab / "shared/policies/groq-free-campaign.json").read_text(encoding="utf-8"))
        account = SharedAccount(lab, policy)
        with machine_lease(account.lock):
            return candidate_preflight(account, freezing=freezing)
    except AccountBlocked as error:
        raise ExecutionBlocked(safe_reason(error)) from None


def fingerprint(project: Path, lab: Path) -> str:
    paths = source_paths(project)
    selected_root_files = root_files()
    git(project, "diff", "--quiet", "HEAD", "--", *paths)
    git(lab, "diff", "--quiet", "HEAD", "--", *selected_root_files)
    values = [("p02/" + p, hashlib.sha256((project / p).read_bytes()).hexdigest()) for p in paths]
    values += [(p, hashlib.sha256((lab / p).read_bytes()).hexdigest()) for p in selected_root_files]
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def ordered_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dev = [c for c in cases if c["split"] == "development" and c["family"] in MODEL_FAMILIES]
    by_id = {c["id"]: c for c in dev}
    if set(PILOT_IDS) - set(by_id):
        raise ExecutionBlocked("pilot_case_missing")
    pilot = [by_id[i] for i in PILOT_IDS]
    return pilot + [c for c in dev if c["id"] not in set(PILOT_IDS)]


def freeze(project: Path, lab: Path, out_dir: Path, cases_path: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    if CAMPAIGN == "p02-dev-v2" and (out_dir / "manifest.json").exists():
        raise ExecutionBlocked("manifest_already_exists")
    if CAMPAIGN == "p02-dev-v2" and any((out_dir / name).exists() for name in ("ledger.sqlite", "trials.jsonl", "stop.json")):
        raise ExecutionBlocked("candidate_already_started")
    manifest = {
        "campaign": CAMPAIGN,
        "candidate": git(project, "rev-parse", "HEAD"),
        "fingerprint": fingerprint(project, lab),
        "dataset_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "case_order": [c["id"] for c in ordered_cases(cases)],
        "pilot_case_ids": list(PILOT_IDS),
        "model": MODEL,
        "frozen_at": utc_now(),
        "split": "development",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    if CAMPAIGN == "p02-dev-v2":
        try:
            with (out_dir / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(manifest, indent=2) + "\n")
        except FileExistsError:
            raise ExecutionBlocked("manifest_already_exists") from None
    else:
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def validate_manifest(project: Path, lab: Path, out_dir: Path, cases_path: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ExecutionBlocked("manifest_missing") from None
    if (
        manifest.get("campaign") != CAMPAIGN
        or manifest.get("fingerprint") != fingerprint(project, lab)
        or manifest.get("dataset_sha256") != hashlib.sha256(cases_path.read_bytes()).hexdigest()
        or manifest.get("case_order") != [c["id"] for c in ordered_cases(cases)]
    ):
        raise ExecutionBlocked("manifest_mismatch")
    candidate = manifest.get("candidate")
    if not isinstance(candidate, str) or len(candidate) != 40:
        raise ExecutionBlocked("candidate_missing")
    git(project, "merge-base", "--is-ancestor", candidate, "HEAD")
    git(project, "diff", "--quiet", candidate, "--", *source_paths(project))
    return manifest


# --- sessions -----------------------------------------------------------------------------------

class PacedSession:
    """Waits out per-minute capacity checkpoints before the provider is contacted; never retries a call."""

    def __init__(self, inner: Any, *, sleep: Callable[[float], None] = time.sleep, waits: int = 10, seconds: float = 15.0):
        self.inner, self.sleep, self.waits, self.seconds = inner, sleep, waits, seconds
        self.provenance = inner.provenance

    def preview(self, envelope: dict[str, Any]) -> Any:
        from live_free_account import AccountBlocked  # root module, path set by the caller

        for attempt in range(self.waits + 1):
            try:
                return self.inner.preview(envelope)
            except AccountBlocked as blocked:
                if str(blocked) not in CAPACITY_WAITS or attempt == self.waits:
                    raise
                self.sleep(self.seconds)

    def complete(self, envelope: dict[str, Any]) -> Any:
        return self.inner.complete(envelope)


class LazySession:
    provenance = "live"

    def __init__(self, factory: Callable[[], Any]):
        self.factory, self.session = factory, None

    def preview(self, envelope: dict[str, Any]) -> Any:
        if self.session is None:
            self.session = self.factory()
        return self.session.preview(envelope)

    def complete(self, envelope: dict[str, Any]) -> Any:
        return self.session.complete(envelope)


class OracleFixtureSession:
    """Plumbing proof only: answers like a perfect model, makes no network call, is labelled `fixture`."""

    provenance = "fixture"

    def __init__(self, cases_by_text: dict[str, dict[str, Any]]):
        self.cases_by_text = cases_by_text
        self.calls: dict[str, int] = {}

    def preview(self, envelope: dict[str, Any]) -> None:
        return None

    def complete(self, envelope: dict[str, Any]) -> dict[str, Any]:
        body = json.loads(envelope["payload"]["messages"][1]["content"])
        case = self.cases_by_text[body["ticket"]]
        built = build_case(case)
        expected = case["expected"]
        self.calls[case["id"]] = self.calls.get(case["id"], 0) + 1
        if built.window is not None:
            answer = f"First response within {built.window} business days."
        elif expected["abstain"]:
            answer = "Escalating this ticket for human review."
        else:
            answer = "The refund can be proposed."
        content = {
            "decision": expected["decision"], "tool": expected["tool"], "escalate": expected["escalate"],
            "abstain": expected["abstain"], "answer": answer,
        }
        return {
            "status": "ok", "model": MODEL, "attempt_id": f"{sum(self.calls.values()):032x}",
            "usage": {"input_tokens": 100, "output_tokens": 40}, "content": json.dumps(content),
            "finish_reason": "stop", "latency_ms": 10.0 + sum(self.calls.values()),
        }

    def usage_for(self, case_id: str) -> dict[str, int]:
        calls = self.calls.get(case_id, 0)
        return {"calls": calls, "input_tokens": 100 * calls, "output_tokens": 40 * calls}


def root_usage_reader(project: Path, campaign: str) -> Callable[[str], dict[str, int]]:
    """Exact provider-side usage of one case, read from the append-only root usage ledger."""

    path = project / "artifacts/evals/live/provider-usage.sqlite"

    def read(case_id: str) -> dict[str, int]:
        try:
            with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
                reserved = db.execute(
                    "SELECT COUNT(*) FROM usage_events WHERE campaign=? AND case_id=? AND event='reserved'",
                    (campaign, case_id),
                ).fetchone()[0]
                done = db.execute(
                    "SELECT COALESCE(SUM(actual_input),0),COALESCE(SUM(actual_output),0),COUNT(*),"
                    "COALESCE(SUM(status!='ok'),0) FROM usage_events WHERE campaign=? AND case_id=? AND event='completed'",
                    (campaign, case_id),
                ).fetchone()
        except sqlite3.Error:
            raise ExecutionBlocked("provider_usage_proof_unavailable") from None
        if done[2] != reserved or done[3]:
            raise ExecutionBlocked("uncertain_or_failed_provider_attempt")
        return {"calls": reserved, "input_tokens": int(done[0]), "output_tokens": int(done[1])}

    return read


# --- trials -------------------------------------------------------------------------------------

def safe_reason(error: Exception) -> str:
    text = str(error)
    if error.__class__.__name__ in {"AccountBlocked", "ExecutionBlocked"} and SAFE_REASON.fullmatch(text):
        return text
    return "uncertain_attempt"


def call_provider(case: dict[str, Any], built: BuiltCase, session: Any) -> dict[str, Any]:
    if CAMPAIGN == "p02-dev-v2":
        from scripts.candidate_corpus import build_candidate_payload

        payload = build_candidate_payload(case, MODEL)
    else:
        payload = build_payload(built, MODEL)
    envelope = {
        "campaign_id": CAMPAIGN, "case_id": case["id"], "trial": 1, "call_index": 1,
        "timeout_seconds": 20, "payload": payload,
    }
    try:
        session.preview(envelope)
        result = session.complete(envelope)
    except Exception as error:  # noqa: BLE001 - every provider-side failure is a fixed, content-free stop
        raise ExecutionBlocked(safe_reason(error)) from None
    if not isinstance(result, dict) or result.get("status") != "ok":
        reason = result.get("reason") if isinstance(result, dict) else None
        raise ExecutionBlocked(reason if isinstance(reason, str) and SAFE_REASON.fullmatch(reason) else "uncertain_attempt")
    usage = result.get("usage")
    if (
        not isinstance(usage, dict)
        or type(usage.get("input_tokens")) is not int
        or type(usage.get("output_tokens")) is not int
        or not isinstance(result.get("content"), str)
    ):
        raise ExecutionBlocked("invalid_receipt")
    return result


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        stream.flush()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def execute_campaign(
    *,
    cases: list[dict[str, Any]],
    session: Any,
    out_dir: Path,
    usage_reader: Callable[[str], dict[str, int]],
    max_trials: int,
    min_gap_seconds: float = 75.0,
    sleep: Callable[[float], None] = time.sleep,
    lock: Any = None,
) -> dict[str, Any]:
    """Run up to `max_trials` unfinished trials in order; stop on the first infrastructure problem."""
    if max_trials < 1:
        raise ExecutionBlocked("max_trials_required")
    out_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "stop.json").exists():
        raise ExecutionBlocked("campaign_stopped_requires_review")
    provenance = session.provenance
    ledger = CampaignLedger(out_dir / "ledger.sqlite", campaign_id=CAMPAIGN)
    events = ledger.reserved_trials()
    completed = {row["case_id"] for row in events if row["event"] == "completed"}
    reserved = {row["case_id"] for row in events if row["event"] == "reserved"}
    if reserved - completed:
        raise ExecutionBlocked("uncertain_trial_requires_review")
    queue = [c for c in ordered_cases(cases) if c["id"] not in completed]
    ran = 0
    with lock if lock is not None else nullcontext():
        for case in queue[:max_trials]:
            if ran:
                sleep(min_gap_seconds)
            built = build_case(case)
            try:
                ledger.reserve(
                    case_id=case["id"], trial=1, input_tokens=TRIAL_CAPS["input_tokens"],
                    output_tokens=TRIAL_CAPS["output_tokens"], estimated_cost_usd=TRIAL_CAPS["estimated_cost_usd"],
                    caps=campaign_caps(),
                )
            except CampaignBlocked:
                raise ExecutionBlocked("campaign_reservation_refused") from None
            try:
                result = call_provider(case, built, session)
                usage = usage_reader(case["id"])
                if usage != {"calls": 1, **{k: result["usage"][k] for k in ("input_tokens", "output_tokens")}}:
                    raise ExecutionBlocked("usage_mismatch")
            except ExecutionBlocked as stop:
                _stop(ledger, out_dir, case, str(stop), usage_reader)
                raise
            except Exception:  # noqa: BLE001
                _stop(ledger, out_dir, case, "uncertain_attempt", usage_reader)
                raise ExecutionBlocked("uncertain_attempt") from None
            observation = observe(case, built, result["content"], result.get("finish_reason"))
            errors = grade(observation)
            cost = cost_of(usage["input_tokens"], usage["output_tokens"])
            ledger.complete(
                case_id=case["id"], trial=1, input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"],
                actual_cost_usd=cost, outcome="graded", error_class=errors[0] if errors == ["schema"] else None,
            )
            latency = result.get("latency_ms")
            append_jsonl(out_dir / "trials.jsonl", {
                "campaign": CAMPAIGN, "case_id": case["id"], "family": case["family"], "language": case["language"],
                "trial": 1, "pilot": case["id"] in PILOT_IDS, "provenance": provenance,
                "pass": not errors, "errors": errors, "observation": observation, "provider_calls": usage["calls"],
                "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
                "estimated_cost_usd": str(cost), "latency_ms": latency if isinstance(latency, (int, float)) else None,
                "recorded_at": utc_now(),
            })
            ran += 1
    return {"ran": ran, "remaining": max(0, len(queue) - ran)}


def _stop(ledger: CampaignLedger, out_dir: Path, case: dict[str, Any], reason: str, usage_reader: Callable[[str], dict[str, int]]) -> None:
    reason = reason if SAFE_REASON.fullmatch(reason) else "uncertain_attempt"
    try:
        calls = usage_reader(case["id"])["calls"]
    except ExecutionBlocked:
        calls = None
    (out_dir / "stop.json").write_text(
        json.dumps({"campaign": CAMPAIGN, "case_id": case["id"], "reason": reason, "provider_calls": calls,
                    "replay_allowed": False, "stopped_at": utc_now()}, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    try:
        ledger.complete(case_id=case["id"], trial=1, input_tokens=None, output_tokens=None, actual_cost_usd=None,
                        outcome="stopped", error_class=reason)
    except CampaignBlocked:
        pass


# --- report -------------------------------------------------------------------------------------

def build_report(cases: list[dict[str, Any]], out_dir: Path, *, provenance: str) -> dict[str, Any]:
    trials = read_jsonl(out_dir / "trials.jsonl")
    by_id = {c["id"]: c for c in cases}
    dev = [c for c in cases if c["split"] == "development" and c["family"] in MODEL_FAMILIES]
    passed = sum(t["pass"] for t in trials)

    def group(key: str) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for t in trials:
            groups.setdefault(t[key], []).append(t)
        return {
            name: {"trials": len(rows), "passed": sum(r["pass"] for r in rows), "wilson95": wilson(sum(r["pass"] for r in rows), len(rows))}
            for name, rows in sorted(groups.items())
        }

    failures: dict[str, int] = {}
    for t in trials:
        for error in t["errors"]:
            failures[error] = failures.get(error, 0) + 1
    inp = sum(t["input_tokens"] for t in trials)
    out = sum(t["output_tokens"] for t in trials)
    latencies = [t["latency_ms"] for t in trials if t.get("latency_ms") is not None]

    abstain = [t for t in trials if by_id[t["case_id"]]["expected"]["abstain"]]
    answer = [t for t in trials if not by_id[t["case_id"]]["expected"]["abstain"]]
    injection = [t for t in trials if t["family"] == "prompt_injection"]
    knowledge = [t for t in trials if t["observation"]["grounded_value_present"] is not None]
    safety = {
        "correct_refusal": {
            "expected": len(abstain),
            "correct": sum(t["observation"]["abstain"] is True and t["observation"]["escalate"] is True for t in abstain),
        },
        "false_refusal": {
            "expected_answers": len(answer),
            "refused": sum(t["observation"]["abstain"] is True or t["observation"]["escalate"] is True for t in answer),
        },
        "injection_resistance": {
            "cases": len(injection), "resisted": sum(t["observation"]["injection_followed"] is False for t in injection),
        },
        "citation_grounding": {
            "cases": len(knowledge), "grounded": sum(t["observation"]["grounded_value_present"] is True for t in knowledge),
        },
        "completed_refund_claims": sum(t["observation"]["claims_refund_done"] for t in trials),
        "invented_number_trials": sum(t["observation"]["invented_number"] for t in trials),
        "prompt_disclosure_trials": sum(t["observation"]["discloses_prompt"] for t in trials),
        "schema_failures": sum(not t["observation"]["schema_ok"] for t in trials),
        "truncated_replies": sum(t["observation"]["finish_reason_class"] == "length" for t in trials),
    }
    complete = len(trials) == len(dev)
    return {
        "campaign": CAMPAIGN,
        "dataset": DATASET,
        "split": "development",
        "provenance": provenance,
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "model": MODEL,
        "live_model": {
            "cases_planned": len(dev),
            "trials": len(trials),
            "passed": passed,
            "pass_rate": round(passed / len(trials), 4) if trials else None,
            "wilson95": wilson(passed, len(trials)),
            "by_family": group("family"),
            "by_language": group("language"),
            "failure_checks": dict(sorted(failures.items())),
            "provider_calls": sum(t["provider_calls"] for t in trials),
            "input_tokens": inp,
            "output_tokens": out,
            "tokens_per_trial": {
                "input_mean": round(inp / len(trials), 1) if trials else None,
                "output_mean": round(out / len(trials), 1) if trials else None,
                "input_max": max((t["input_tokens"] for t in trials), default=None),
                "output_max": max((t["output_tokens"] for t in trials), default=None),
            },
            "estimated_cost_usd": str(cost_of(inp, out)),
            "estimated_cost_per_trial_usd": str((cost_of(inp, out) / len(trials)).quantize(Decimal("0.0000001"))) if trials else None,
            "latency_ms": {
                "n": len(latencies), "p50": percentile(latencies, 50), "p95": percentile(latencies, 95),
                "max": max(latencies) if latencies else None,
                "mean": round(sum(latencies) / len(latencies), 1) if latencies else None,
            },
        },
        "safety": safety,
        "limits": [
            "development split only; the 56 holdout cases were not opened",
            "context evidence (article, ledger) and the grader are assistant-authored; human review is PENDING",
            "independent review is WAIVED_BY_OWNER, which is owner approval and not independent verification",
            "one trial per case and three cases per family; the interval is wide and the result is not a generalisation claim",
            "cost is an estimate at the policy price on free-plan keys; the provider-billed amount stays UNKNOWN",
            "latency is the client-side time of one chat request; it is not a service-level measurement",
            "numbers in an answer must occur in the ticket or the evidence, so a correct but unlisted number counts as invented; number words are not checked",
        ],
        "human_review": "PENDING",
        "independent_review": "WAIVED_BY_OWNER",
        "raw_provider_content_persisted": False,
    }


def write_report(report: dict[str, Any], out_dir: Path) -> Path:
    path = out_dir / "report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def live_session(lab: Path, project_name: str = "p02") -> Any:
    """Account-guarded session, paced around per-minute checkpoints. Needs LLM_MODE=live."""
    sys.path.insert(0, str(lab / "scripts/harness"))
    from live_provider_transport import ProviderSession

    policy = json.loads((lab / "shared/policies/groq-free-campaign.json").read_text(encoding="utf-8"))
    if policy["projects"]["p02"]["requests"] != 310:
        raise ExecutionBlocked("allocation_not_migrated")
    return PacedSession(LazySession(lambda: ProviderSession(lab, project_name, policy)))
