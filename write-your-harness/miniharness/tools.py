"""The six coding-agent tools, confined to a workspace root.

Inspired by the nanocode surface (read/write/edit/glob/grep/bash), rewritten
for teaching: paths cannot escape the workspace. bash still runs a shell —
see chapter 6 and 12 for why that is not a sandbox.
"""

from __future__ import annotations

import glob as globlib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .types import ToolCall

Handler = Callable[[dict[str, Any]], str]


@dataclass
class Workspace:
    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root).resolve()

    def resolve(self, raw: str) -> Path:
        path = Path(raw)
        full = path.resolve() if path.is_absolute() else (self.root / path).resolve()
        root_s = os.path.normcase(str(self.root))
        full_s = os.path.normcase(str(full))
        if full_s != root_s and not full_s.startswith(root_s + os.sep):
            raise PermissionError(f"path escapes workspace: {raw}")
        return full


def _read(ws: Workspace, args: dict[str, Any]) -> str:
    path = ws.resolve(args["path"])
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    offset = int(args.get("offset") or 0)
    limit = int(args.get("limit") or len(lines))
    selected = lines[offset : offset + limit]
    return "".join(f"{offset + i + 1:4}| {line}" for i, line in enumerate(selected)) or "(empty)"


def _write(ws: Workspace, args: dict[str, Any]) -> str:
    path = ws.resolve(args["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"], encoding="utf-8")
    return "ok"


def _edit(ws: Workspace, args: dict[str, Any]) -> str:
    path = ws.resolve(args["path"])
    text = path.read_text(encoding="utf-8")
    old, new = args["old"], args["new"]
    if old not in text:
        return "error: old_string not found"
    count = text.count(old)
    replace_all = bool(args.get("all"))
    if not replace_all and count > 1:
        return f"error: old_string appears {count} times, must be unique (use all=true)"
    path.write_text(text.replace(old, new) if replace_all else text.replace(old, new, 1), encoding="utf-8")
    return "ok"


def _glob(ws: Workspace, args: dict[str, Any]) -> str:
    pattern = args["pat"]
    base = ws.resolve(args["path"]) if args.get("path") else ws.root
    files = globlib.glob(str(base / pattern), recursive=True)
    files = [f for f in files if Path(f).is_file()]
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    rel = [str(Path(f).resolve().relative_to(ws.root)) for f in files]
    return "\n".join(rel) or "none"


def _grep(ws: Workspace, args: dict[str, Any]) -> str:
    pattern = re.compile(args["pat"])
    base = ws.resolve(args["path"]) if args.get("path") else ws.root
    hits: list[str] = []
    for filepath in globlib.glob(str(base / "**"), recursive=True):
        p = Path(filepath)
        if not p.is_file():
            continue
        try:
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pattern.search(line):
                    rel = p.resolve().relative_to(ws.root)
                    hits.append(f"{rel}:{n}:{line}")
                    if len(hits) >= 50:
                        return "\n".join(hits)
        except OSError:
            continue
    return "\n".join(hits) or "none"


def _bash(ws: Workspace, args: dict[str, Any], timeout: float = 30.0) -> str:
    cmd = args["cmd"]
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=ws.root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"(timed out after {timeout:.0f}s)"
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode:
        out = out.rstrip() + f"\n(exit {proc.returncode})"
    return out.strip() or "(empty)"


TOOL_DOCS: dict[str, tuple[str, dict[str, str]]] = {
    "read": ("Read a file with line numbers", {"path": "string", "offset": "number?", "limit": "number?"}),
    "write": ("Write content to a file", {"path": "string", "content": "string"}),
    "edit": (
        "Replace old with new. old must be unique unless all=true",
        {"path": "string", "old": "string", "new": "string", "all": "boolean?"},
    ),
    "glob": ("Find files by glob pattern, newest first", {"pat": "string", "path": "string?"}),
    "grep": ("Search files for a regex", {"pat": "string", "path": "string?"}),
    "bash": ("Run a shell command in the workspace", {"cmd": "string"}),
}


class Toolbelt:
    def __init__(self, workspace: Workspace, allow_bash: bool = True, bash_timeout: float = 30.0):
        self.workspace = workspace
        self.allow_bash = allow_bash
        self.bash_timeout = bash_timeout

    def names(self) -> list[str]:
        names = ["read", "write", "edit", "glob", "grep"]
        if self.allow_bash:
            names.append("bash")
        return names

    def schemas(self) -> list[dict[str, Any]]:
        result = []
        for name in self.names():
            description, params = TOOL_DOCS[name]
            properties = {}
            required = []
            for pname, ptype in params.items():
                optional = ptype.endswith("?")
                base = ptype.rstrip("?")
                json_type = {"number": "integer", "boolean": "boolean"}.get(base, "string")
                properties[pname] = {"type": json_type}
                if not optional:
                    required.append(pname)
            result.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": description,
                        "parameters": {"type": "object", "properties": properties, "required": required},
                    },
                }
            )
        return result

    def run(self, call: ToolCall) -> str:
        name, args = call.name, call.args
        ws = self.workspace
        try:
            if name == "read":
                return _read(ws, args)
            if name == "write":
                return _write(ws, args)
            if name == "edit":
                return _edit(ws, args)
            if name == "glob":
                return _glob(ws, args)
            if name == "grep":
                return _grep(ws, args)
            if name == "bash":
                if not self.allow_bash:
                    return "error: bash is disabled"
                return _bash(ws, args, timeout=self.bash_timeout)
            return f"error: unknown tool {name}"
        except Exception as err:  # noqa: BLE001 — tool errors must become observations
            return f"error: {err}"
