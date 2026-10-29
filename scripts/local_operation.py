"""Single-attempt local synthetic retrieval, with committed provenance and accounting."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from supportops_toolkit.accounted_generation import OperationBlocked, _run

PROJECT = Path(__file__).resolve().parents[1]
LAB = PROJECT.parents[1]
MANIFEST = "artifacts/evals/live/local-operation-v1/manifest.json"
QUERY = "invoice status"
DOCS = [{"tenant": "fixture-local", "id": "invoice-status", "text": "The synthetic invoice status is pending. No refund or payment is performed."}]
CASES = [f"fixture-local-{index:02}" for index in range(1, 5)]


def git(project, *args):
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, timeout=15)
    if result.returncode:
        raise OperationBlocked("source_provenance")
    return result.stdout.decode().strip()


def fingerprint(project=PROJECT):
    paths = sorted(path for path in git(project, "ls-files").splitlines()
                   if path.startswith(("supportops_toolkit/", "scripts/", "tests/", "agent/", "evals/"))
                   or path in {"pyproject.toml", "uv.lock", "harness.yaml"})
    if not paths:
        raise OperationBlocked("source_provenance")
    git(project, "diff", "--quiet", "HEAD", "--", *paths)
    return hashlib.sha256(json.dumps([(path, hashlib.sha256((project / path).read_bytes()).hexdigest())
                                     for path in paths], separators=(",", ":")).encode()).hexdigest()


def validate(project=PROJECT):
    try:
        manifest = json.loads((project / MANIFEST).read_text())
        owner = json.loads((project / "evals/live-execution.json").read_text())
    except (OSError, ValueError):
        raise OperationBlocked("manifest_missing") from None
    if (manifest.get("project") != "p02" or manifest.get("campaign_id") != "local-operation-v1"
            or manifest.get("source_fingerprint") != fingerprint(project)
            or owner.get("execution_enabled") is not True
            or manifest.get("case_ids") != CASES
            or manifest.get("paid_usd") != 0):
        raise OperationBlocked("manifest_mismatch")
    candidate = manifest.get("candidate")
    if not isinstance(candidate, str) or len(candidate) != 40:
        raise OperationBlocked("candidate_missing")
    git(project, "merge-base", "--is-ancestor", candidate, "HEAD")
    # Compare actual candidate files, not merely an ancestor commit label.
    paths = git(project, "ls-files", "supportops_toolkit", "scripts", "tests", "agent", "evals",
                "pyproject.toml", "uv.lock", "harness.yaml").splitlines()
    git(project, "diff", "--quiet", candidate, "--", *paths)
    return manifest


class LazySession:
    provenance = "live"

    def __init__(self, factory):
        self.factory, self.session = factory, None

    def preview(self, envelope):
        self.session = self.factory()
        return self.session.preview(envelope)

    def complete(self, envelope):
        return self.session.complete(envelope)


def execute(request_id, *, project=PROJECT):
    if os.getenv("LLM_MODE", "fake") != "live" or request_id not in CASES:
        raise OperationBlocked("explicit_synthetic_live_required")
    validate(project)
    sys.path.insert(0, str(LAB / "scripts/harness"))
    from live_free_account import machine_lease
    from live_provider_transport import ProviderSession
    policy = json.loads((LAB / "shared/policies/groq-free-campaign.json").read_text())
    if policy["projects"]["p02"]["requests"] != 310:
        raise OperationBlocked("allocation_not_migrated")
    path = project / "artifacts/evals/live/operations.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    with machine_lease(LAB / ".runtime/llm-live-readiness/campaign.lock"):
        # Recheck provenance while holding the same global execution lease.
        validate(project)
        session = LazySession(lambda: ProviderSession(LAB, "p02", policy))
        return _run(path, request_id, "fixture-local", QUERY, DOCS, session, campaign="local-operation-v1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request-id", choices=CASES)
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args()
    try:
        if args.fingerprint:
            print(json.dumps({"fingerprint": fingerprint()}))
        elif args.request_id:
            print(json.dumps(execute(args.request_id)))
        else:
            parser.error("--request-id or --fingerprint required")
        return 0
    except OperationBlocked as error:
        print(json.dumps({"status": "INCOMPLETE", "reason": str(error)}))
        return 2
    except Exception:
        print(json.dumps({"status": "INCOMPLETE", "reason": "operation_uncertain"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
