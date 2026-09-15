"""Pedagogical PTC: the model sees one tool, `run_code`, plus a generated SDK.

DeepSeek Harness's real PTC is TypeScript (or Python) against a generated
`.d.ts`, with a proper code runtime. This file is the 40-line version of that
idea: hide the six tools behind a Python script so one model turn can compose
several host calls.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Any

from .tools import Toolbelt, TOOL_DOCS
from .types import ToolCall


def sdk_stub() -> str:
    lines = [
        "# Host-provided SDK. Your script may call these functions.",
        "class tools:",
    ]
    for name, (doc, params) in TOOL_DOCS.items():
        args = ", ".join(p for p in params)
        lines.append(f"    @staticmethod")
        lines.append(f"    def {name}({args}):")
        lines.append(f"        \"\"\"{doc}\"\"\"")
        lines.append(f"        ...")
        lines.append("")
    lines.append("# Write a script. Print what you want the model to see next.")
    return "\n".join(lines)


class _Proxy:
    def __init__(self, belt: Toolbelt):
        self._belt = belt

    def __getattr__(self, name: str):
        def call(**kwargs: Any) -> str:
            return self._belt.run(ToolCall(id=f"ptc_{name}", name=name, args=kwargs))

        if name in self._belt.names() or name in TOOL_DOCS:
            return call
        raise AttributeError(name)


def run_code(belt: Toolbelt, source: str) -> str:
    stdout, stderr = io.StringIO(), io.StringIO()
    ns = {"tools": _Proxy(belt), "__name__": "__ptc__"}
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(source, ns, ns)  # noqa: S102 — teaching runtime, not a sandbox
    except Exception as err:  # noqa: BLE001
        return f"error: {type(err).__name__}: {err}"
    out = (stdout.getvalue() + stderr.getvalue()).strip()
    return out or "(script finished with no output)"


def ptc_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "run_code",
                "description": "Run a Python script that may call the host SDK `tools.*`. Print results.",
                "parameters": {
                    "type": "object",
                    "properties": {"source": {"type": "string"}},
                    "required": ["source"],
                },
            },
        }
    ]


class PtcToolbelt:
    """Drop-in lookalike: schemas() exposes only run_code; run() dispatches to exec."""

    def __init__(self, inner: Toolbelt):
        self.inner = inner
        self.workspace = inner.workspace

    def names(self) -> list[str]:
        return ["run_code"]

    def schemas(self) -> list[dict[str, Any]]:
        return ptc_schema()

    def run(self, call: ToolCall) -> str:
        if call.name != "run_code":
            return f"error: unknown tool {call.name}"
        return run_code(self.inner, call.args.get("source") or "")
