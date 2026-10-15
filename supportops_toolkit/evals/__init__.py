"""Deterministic evaluation runner and regression gates."""

__all__ = ["EvalReport", "RegressionError", "run_evals"]


def __getattr__(name):
    if name in __all__:
        from . import runner

        return getattr(runner, name)
    raise AttributeError(name)
