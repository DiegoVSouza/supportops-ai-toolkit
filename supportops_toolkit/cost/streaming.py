"""Tiny adapter that yields chunks while accumulating the final text."""

from collections.abc import Iterable, Iterator


def stream_text(chunks: Iterable[str]) -> Iterator[str]:
    for chunk in chunks:
        if not isinstance(chunk, str):
            raise TypeError("stream chunks must be strings")
        yield chunk


def collect_stream(chunks: Iterable[str]) -> str:
    return "".join(stream_text(chunks))
