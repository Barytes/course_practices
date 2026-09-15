"""A toy SWE-style eval: copy a fixture, run the agent, then run the tests.

This is not SWE-bench. It is the control-flow of SWE-bench: isolated workspace,
one issue, one trajectory, a deterministic grader.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .guards import Guards
from .loop import RunResult, run_agent
from .model import ScriptedModel, load_script
from .tools import Toolbelt, Workspace
from .types import Message, system, user


@dataclass
class EvalResult:
    passed: bool
    stop_reason: str
    grader_output: str
    workdir: str
    trajectory: list[dict[str, Any]]


def run_eval(
    fixture: Path,
    model: Any,
    *,
    issue_file: str = "ISSUE.md",
    test_cmd: str | None = None,
    max_steps: int = 12,
    allow_bash: bool = True,
) -> EvalResult:
    fixture = Path(fixture).resolve()
    test_cmd = test_cmd or f"{sys.executable} -m unittest test_calc.py -v"
    issue = (fixture / issue_file).read_text(encoding="utf-8").strip()
    tmp = Path(tempfile.mkdtemp(prefix="miniharness-eval-"))
    work = tmp / "repo"
    shutil.copytree(fixture, work, ignore=shutil.ignore_patterns("scripts", "__pycache__"))
    belt = Toolbelt(Workspace(work), allow_bash=allow_bash)
    messages = [
        system("You are a coding agent. Fix the issue. Do not modify tests."),
        user(issue),
    ]
    run: RunResult = run_agent(model, belt, messages, guards=Guards(max_steps=max_steps))
    grader = subprocess.run(
        test_cmd,
        shell=True,
        cwd=work,
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = (grader.stdout or "") + (grader.stderr or "")
    traj_path = tmp / "trajectory.json"
    payload = {
        "stop_reason": run.stop_reason,
        "passed": grader.returncode == 0,
        "messages": [m.to_dict() for m in run.messages],
        "events": run.events,
        "grader": out,
    }
    traj_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return EvalResult(
        passed=grader.returncode == 0,
        stop_reason=run.stop_reason,
        grader_output=out,
        workdir=str(work),
        trajectory=payload["messages"],
    )


def run_eval_from_script(fixture: Path, script_path: Path, **kwargs: Any) -> EvalResult:
    return run_eval(fixture, load_script(str(script_path)), **kwargs)


def default_scripted_model() -> ScriptedModel:
    """Used by tests when the json fixture is not passed explicitly."""
    return ScriptedModel(
        [
            {
                "content": "I'll read the issue and the implementation.",
                "tool_calls": [
                    {"name": "read", "args": {"path": "ISSUE.md"}},
                    {"name": "read", "args": {"path": "calc.py"}},
                ],
            },
            {
                "content": "add() subtracts. Replacing with addition.",
                "tool_calls": [
                    {
                        "name": "edit",
                        "args": {
                            "path": "calc.py",
                            "old": "return a - b  # BUG: should add",
                            "new": "return a + b",
                        },
                    }
                ],
            },
            {
                "content": "Running tests.",
                "tool_calls": [
                    {"name": "bash", "args": {"cmd": f"{sys.executable} -m unittest test_calc.py -v"}}
                ],
            },
            {"content": "Tests passed. Done."},
        ]
    )
