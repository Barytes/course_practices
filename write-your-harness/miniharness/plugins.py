"""A tiny plugin seam. Production systems (pi, dsh) have richer events;
the idea is the same: the loop stays small, extra behavior hangs off hooks.
"""

from __future__ import annotations

from typing import Any, Protocol

from .types import Message, ToolCall


class Plugin(Protocol):
    def before_model(self, messages: list[Message]) -> list[Message]:
        return messages

    def after_tool(self, call: ToolCall, result: str) -> str:
        return result

    def on_event(self, event: dict[str, Any]) -> None:
        return None


class NoopPlugin:
    def before_model(self, messages: list[Message]) -> list[Message]:
        return messages

    def after_tool(self, call: ToolCall, result: str) -> str:
        return result

    def on_event(self, event: dict[str, Any]) -> None:
        return None


class EventLog:
    """Collects loop events. This is the baby version of 'observability'."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def before_model(self, messages: list[Message]) -> list[Message]:
        return messages

    def after_tool(self, call: ToolCall, result: str) -> str:
        return result

    def on_event(self, event: dict[str, Any]) -> None:
        self.events.append(event)
