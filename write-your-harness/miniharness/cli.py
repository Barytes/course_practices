"""CLI: demo, eval, live chat, living-map."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .eval import default_scripted_model, run_eval
from .guards import Guards
from .loop import run_agent
from .model import OpenAICompatModel, load_script
from .tools import Toolbelt, Workspace
from .types import system, user
from .watch import render, snapshot


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE = ROOT / "labs" / "broken_calc"


def _print_messages(messages) -> None:
    for msg in messages:
        if msg.role == "system":
            continue
        if msg.role == "assistant":
            if msg.content:
                print(f"\n⏺ {msg.content}")
            for call in msg.tool_calls:
                preview = next(iter(call.args.values()), "")
                print(f"  → {call.name}({str(preview)[:60]})")
        elif msg.role == "tool":
            first = (msg.content or "").splitlines()[0][:80]
            print(f"    ⎿ {first}")
        elif msg.role == "user":
            print(f"\n❯ {msg.content[:200]}")


def cmd_demo() -> int:
    from .types import Message, ToolCall

    result = run_eval(DEFAULT_FIXTURE, default_scripted_model())
    reconstructed = [
        Message(
            role=raw["role"],
            content=raw.get("content") or "",
            tool_calls=[ToolCall(**c) for c in raw.get("tool_calls") or []],
            tool_call_id=raw.get("tool_call_id"),
            name=raw.get("name"),
        )
        for raw in result.trajectory
    ]
    _print_messages(reconstructed)
    print("\n" + ("PASS" if result.passed else "FAIL"))
    print(result.grader_output[-400:])
    print(f"workdir: {result.workdir}")
    return 0 if result.passed else 1


def cmd_eval(args: argparse.Namespace) -> int:
    fixture = Path(args.fixture)
    if args.script:
        model = load_script(args.script)
    else:
        model = default_scripted_model()
    result = run_eval(fixture, model)
    print("PASS" if result.passed else "FAIL")
    print(f"stop={result.stop_reason}")
    print(result.grader_output[-600:])
    return 0 if result.passed else 1


def cmd_run(args: argparse.Namespace) -> int:
    ws = Workspace(Path(args.workspace).resolve())
    belt = Toolbelt(ws, allow_bash=not args.no_bash)
    if args.script:
        model = load_script(args.script)
    else:
        model = OpenAICompatModel(model=args.model)
    messages = [
        system(f"Concise coding assistant. Workspace: {ws.root}"),
        user(args.prompt),
    ]
    result = run_agent(messages=messages, model=model, tools=belt, guards=Guards(max_steps=args.max_steps))
    _print_messages(result.messages)
    print(f"\nstop={result.stop_reason}")
    if args.save:
        Path(args.save).write_text(
            json.dumps({"messages": [m.to_dict() for m in result.messages], "events": result.events}, indent=2),
            encoding="utf-8",
        )
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    data = snapshot(n=args.n)
    text = render(data)
    print(text)
    if args.save:
        Path(args.save).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="miniharness", description="A 200-line teaching harness.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="scripted repair of labs/broken_calc")

    p_eval = sub.add_parser("eval", help="run the toy SWE eval")
    p_eval.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    p_eval.add_argument("--script", default="")

    p_run = sub.add_parser("run", help="one-shot prompt against a workspace")
    p_run.add_argument("prompt")
    p_run.add_argument("--workspace", default=".")
    p_run.add_argument("--script", default="")
    p_run.add_argument("--model", default=None)
    p_run.add_argument("--max-steps", type=int, default=16)
    p_run.add_argument("--no-bash", action="store_true")
    p_run.add_argument("--save", default="")

    p_watch = sub.add_parser("watch", help="pull GitHub releases for the six reference repos")
    p_watch.add_argument("-n", type=int, default=8)
    p_watch.add_argument("--save", default="")

    args = parser.parse_args(argv)
    if args.cmd == "demo":
        return cmd_demo()
    if args.cmd == "eval":
        return cmd_eval(args)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "watch":
        return cmd_watch(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
