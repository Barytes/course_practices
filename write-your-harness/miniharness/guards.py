"""Hard stops: step budget, repeated-tool fingerprint, optional path policy.

These are harness jobs. Do not ask the model to 'please stop looping'.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .types import ToolCall


class GuardError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def fingerprint(call: ToolCall) -> str:
    blob = json.dumps({"name": call.name, "args": call.args}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


@dataclass
class Guards:
    max_steps: int = 20
    max_repeats: int = 3
    _seen: list[str] = field(default_factory=list)
    steps: int = 0

    def before_step(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise GuardError("step_limit", f"stopped after {self.max_steps} model calls")

    def before_tool(self, call: ToolCall) -> None:
        fp = fingerprint(call)
        self._seen.append(fp)
        if self.max_repeats > 0 and len(self._seen) >= self.max_repeats:
            window = self._seen[-self.max_repeats :]
            if len(set(window)) == 1:
                raise GuardError(
                    "repeat_loop",
                    f"same tool+args repeated {self.max_repeats} times: {call.name}",
                )
