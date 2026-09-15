"""Model protocol + two implementations: scripted (labs) and OpenAI-compatible (optional live)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Protocol

from .types import Message, ToolCall


class Model(Protocol):
    def complete(self, messages: list[Message], tools: list[dict[str, Any]]) -> Message:
        """Return one assistant message. May contain tool_calls."""


class ScriptedModel:
    """Replay a predetermined list of assistant turns. No network.

    Each item is a dict: {"content": str, "tool_calls": [{"name", "args"}, ...]}.
    Tool call ids are assigned as call_1, call_2, ...
    """

    def __init__(self, script: list[dict[str, Any]]):
        self.script = list(script)
        self.index = 0
        self._n = 0

    def complete(self, messages: list[Message], tools: list[dict[str, Any]]) -> Message:
        del messages, tools
        if self.index >= len(self.script):
            return Message(role="assistant", content="(script ended)")
        turn = self.script[self.index]
        self.index += 1
        calls = []
        for spec in turn.get("tool_calls") or []:
            self._n += 1
            calls.append(
                ToolCall(
                    id=spec.get("id") or f"call_{self._n}",
                    name=spec["name"],
                    args=dict(spec.get("args") or {}),
                )
            )
        return Message(role="assistant", content=turn.get("content") or "", tool_calls=calls)


def load_script(path: str) -> ScriptedModel:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("script json must be a list of assistant turns")
    return ScriptedModel(data)


class OpenAICompatModel:
    """Minimal chat-completions client. Needs OPENAI_API_KEY (or OPENAI_COMPAT_KEY)."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model or os.environ.get("MODEL", "gpt-4.1-mini")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_COMPAT_KEY") or ""

    def complete(self, messages: list[Message], tools: list[dict[str, Any]]) -> Message:
        if not self.api_key:
            raise RuntimeError("set OPENAI_API_KEY to use the live model")
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [_to_openai(m) for m in messages],
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API {err.code}: {detail[:800]}") from err
        choice = body["choices"][0]["message"]
        calls = []
        for raw in choice.get("tool_calls") or []:
            fn = raw["function"]
            args = fn.get("arguments") or "{}"
            if isinstance(args, str):
                args = json.loads(args or "{}")
            calls.append(ToolCall(id=raw["id"], name=fn["name"], args=args))
        return Message(role="assistant", content=choice.get("content") or "", tool_calls=calls)


def _to_openai(message: Message) -> dict[str, Any]:
    if message.role == "tool":
        return {
            "role": "tool",
            "tool_call_id": message.tool_call_id,
            "content": message.content,
        }
    if message.role == "assistant" and message.tool_calls:
        return {
            "role": "assistant",
            "content": message.content or None,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": json.dumps(call.args, ensure_ascii=False),
                    },
                }
                for call in message.tool_calls
            ],
        }
    return {"role": message.role, "content": message.content}
