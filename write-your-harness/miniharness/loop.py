"""The invariant: call the model, maybe run tools, append observations, repeat.

Everything else in this package is optional. If you can rewrite this file from
memory, you can write a harness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .compact import compact_tool_results
from .guards import GuardError, Guards
from .plugins import NoopPlugin
from .tools import Toolbelt
from .types import Message, tool_result


@dataclass
class RunResult:
    messages: list[Message]
    events: list[dict[str, Any]] = field(default_factory=list)
    stop_reason: str = "completed"


def run_agent(
    model: Any,
    tools: Toolbelt,
    messages: list[Message],
    *,
    guards: Guards | None = None,
    plugins: list[Any] | None = None,
    compact_after_chars: int | None = 12_000,
) -> RunResult:
    """Run until the model stops calling tools, or a guard fires."""
    guards = guards or Guards()
    plugins = plugins or [NoopPlugin()]
    events: list[dict[str, Any]] = []

    def emit(kind: str, **payload: Any) -> None:
        event = {"type": kind, **payload}
        events.append(event)
        for plugin in plugins:
            on_event = getattr(plugin, "on_event", None)
            if on_event:
                on_event(event)

    emit("agent_start")
    try:
        while True:
            guards.before_step()
            if compact_after_chars is not None:
                messages[:] = compact_tool_results(messages, max_chars=compact_after_chars)
            for plugin in plugins:
                before = getattr(plugin, "before_model", None)
                if before:
                    messages[:] = before(messages)
            emit("turn_start", step=guards.steps)
            reply = model.complete(messages, tools.schemas())
            messages.append(reply)
            emit("model_end", step=guards.steps, n_tools=len(reply.tool_calls))
            if not reply.tool_calls:
                emit("agent_end", reason="no_tools")
                return RunResult(messages=messages, events=events, stop_reason="completed")
            for call in reply.tool_calls:
                guards.before_tool(call)
                emit("tool_start", name=call.name, id=call.id)
                result = tools.run(call)
                for plugin in plugins:
                    after = getattr(plugin, "after_tool", None)
                    if after:
                        result = after(call, result)
                messages.append(tool_result(call, result))
                emit("tool_end", name=call.name, id=call.id, chars=len(result))
    except GuardError as err:
        note = Message(role="assistant", content=f"[{err.code}] {err.detail}")
        messages.append(note)
        emit("agent_end", reason=err.code)
        return RunResult(messages=messages, events=events, stop_reason=err.code)
