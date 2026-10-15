# ADR-001: Fail closed on indeterminate tool outcomes

## Status
Accepted — 2026-10-15

## Context
The tool wrapper used a Python thread future timeout and then retried the handler when configured. Cancelling a future cannot stop a handler that is already running. A timed-out write may therefore complete after the caller has decided to retry it. Generic network errors can also occur after a remote side effect has committed.

## Decision
Treat timeout and generic transport exceptions as fatal, outcome-indeterminate failures. Automatic retry is permitted only when an adapter raises `ToolError(retryable=True)` after establishing that repeating the operation is safe. `execution_limits=ExecutionLimits(...)` is an additive call option that consumes one tool step and bounds waiting by the remaining wall-clock budget. The supported schema subset is explicit and rejects unknown keywords; numbers exclude booleans and non-finite values.

## Consequences
Some transient failures now require adapter-specific classification or caller recovery. The in-process thread still cannot be forcibly terminated; process/service isolation is required for hard cancellation. P02 does not own an LLM runtime, so token limits require usage reporting at the caller's model boundary and whole-run token enforcement remains incomplete.

Package version advances from `0.1.0` to `0.2.0`. A local wheel and source/hash provenance must be recorded, and P05 must consume the exact artifact before its integration gate can pass. No external publication is authorized.
