"""Cheap context compaction: shrink old tool results, keep the live tail intact.

Real systems summarize with another model call. For the lab, truncation is
enough to feel the trade-off: you save tokens, you lose detail.
"""

from __future__ import annotations

from .types import Message


def total_chars(messages: list[Message]) -> int:
    n = 0
    for msg in messages:
        n += len(msg.content or "")
        for call in msg.tool_calls:
            n += len(call.name) + len(str(call.args))
    return n


def _clip(text: str, head: int, tail: int) -> str:
    if len(text) <= head + tail + 20:
        return text
    omitted = len(text) - head - tail
    return f"{text[:head]}\n… [{omitted} chars omitted] …\n{text[-tail:]}"


def compact_tool_results(
    messages: list[Message],
    *,
    max_chars: int = 12_000,
    keep_last_tools: int = 4,
    head: int = 240,
    tail: int = 160,
) -> list[Message]:
    if total_chars(messages) <= max_chars:
        return messages
    tool_idxs = [i for i, m in enumerate(messages) if m.role == "tool"]
    protected = set(tool_idxs[-keep_last_tools:])
    out: list[Message] = []
    for i, msg in enumerate(messages):
        if msg.role == "tool" and i not in protected:
            out.append(
                Message(
                    role="tool",
                    content=_clip(msg.content, head, tail),
                    tool_call_id=msg.tool_call_id,
                    name=msg.name,
                )
            )
        else:
            out.append(msg)
    return out
