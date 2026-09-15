"""Shared message types. The whole harness is just lists of these."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class Message:
    role: Role
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


def user(text: str) -> Message:
    return Message(role="user", content=text)


def system(text: str) -> Message:
    return Message(role="system", content=text)


def assistant(text: str = "", tool_calls: list[ToolCall] | None = None) -> Message:
    return Message(role="assistant", content=text, tool_calls=tool_calls or [])


def tool_result(call: ToolCall, content: str) -> Message:
    return Message(role="tool", content=content, tool_call_id=call.id, name=call.name)
