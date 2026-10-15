# Architecture

P02 is a local Python toolkit for tool contracts, guardrails, deterministic evaluation, and cost-control utilities. Tool handlers validate arguments and results against a documented JSON Schema subset. Retryable failures must be explicitly marked safe; ambiguous timeouts and generic transport failures fail closed without an automatic retry.

`ExecutionLimits` can be passed to a tool call to count steps and bound the call by the remaining wall-clock budget. Model token usage is supplied by the caller at the LLM boundary through `consume(tokens=...)`; P02 has no integrated agent/LLM runtime, so whole-run token enforcement remains incomplete. All default evaluation and guardrail checks use local fake fixtures. Cost, latency, and model-quality measurements remain pending until comparable authorized runs exist.
