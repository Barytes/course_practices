
from __future__ import annotations

import sys
from pathlib import Path
import json

BOOK_ROOT = Path(__file__).resolve().parents[2]
if str(BOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(BOOK_ROOT))

from client import get_llm_client
from providers import get_provider


def llm_response(
    messages: str | list[dict],
    *,
    tools: list[dict] | None = None,
    model: str | None = None,
    provider: str | None = None,
    max_tokens: int = 1024,
):
    """Call the configured provider and return the assistant message."""
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    cfg = get_provider(provider)
    client = get_llm_client(cfg)
    kwargs: dict = {
        "model": model or cfg.resolve_default_model(),
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message

import ast
import io
import math
from contextlib import redirect_stdout

BENCH = Path(__file__).resolve().parent / "context-ablation-1-1"
TOOLS = json.loads((BENCH / "tools.json").read_text(encoding="utf-8"))
CURRENCY_FIXTURES = json.loads(
    (BENCH / "currency-fixtures.json").read_text(encoding="utf-8")
)["fixtures"]

SYSTEM_PROMPT = """
You are a helpful assistant that can use tools to help the user.
"""


def parse_pdf(url: str):
    return {"error": "parse_pdf is not used by this task"}


_CURRENCY_ALIASES = {
    "EUR": {"EUR", "EURO", "EUROS", "€"},
    "GBP": {"GBP", "POUND", "POUNDS", "£", "STERLING"},
    "JPY": {"JPY", "YEN", "¥", "円"},
    "USD": {"USD", "US$", "US", "DOLLAR", "DOLLARS", "$"},
}


def _currency_code(value: str) -> str:
    raw = str(value).strip().upper()
    for code, aliases in _CURRENCY_ALIASES.items():
        if raw in aliases:
            return code
    return raw


def _parse_amount(amount) -> float:
    if isinstance(amount, (int, float)):
        return float(amount)
    text = str(amount).lower().replace(",", "").replace("_", "").strip()
    multiplier = 1.0
    if "million" in text or text.endswith("m"):
        text = text.replace("million", "").rstrip("m").strip()
        multiplier = 1_000_000
    elif "billion" in text or text.endswith("b"):
        text = text.replace("billion", "").rstrip("b").strip()
        multiplier = 1_000_000_000
    return float(text) * multiplier


def convert_currency(amount, from_currency, to_currency):
    amount = _parse_amount(amount)
    from_currency = _currency_code(from_currency)
    to_currency = _currency_code(to_currency)
    candidates = {amount, amount * 1_000, amount * 1_000_000}
    for item in CURRENCY_FIXTURES:
        args = item["arguments"]
        if (
            float(args["amount"]) in candidates
            and args["from_currency"].upper() == from_currency
            and args["to_currency"].upper() == to_currency
        ):
            return item["result"]
    return {"error": "no fixture for this conversion"}


def calculate(expression: str):
    allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed.update({"abs": abs, "round": round, "min": min, "max": max})
    tree = ast.parse(expression.replace("^", "**"), mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in allowed:
            return {"error": f"name not allowed: {node.id}"}
    return {"expression": expression, "result": eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, allowed)}


def code_interpreter(code: str):
    namespace = {
        "__builtins__": {
            "abs": abs,
            "sum": sum,
            "min": min,
            "max": max,
            "round": round,
            "len": len,
            "list": list,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "print": print,
        },
        "math": math,
    }
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exec(code, namespace)
    result = namespace.get("result")
    if result is None:
        for name in ("total", "sum", "output", "answer", "final"):
            if name in namespace:
                result = namespace[name]
                break
    return {
        "result": result,
        "output": buffer.getvalue() or None,
        "success": True,
    }


TOOL_FUNCTIONS = {
    "parse_pdf": parse_pdf,
    "convert_currency": convert_currency,
    "calculate": calculate,
    "code_interpreter": code_interpreter,
}

def agent(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = llm_response(messages, tools=TOOLS)

    turn = 1
    while response.tool_calls:
        print(f"Turn {turn}: {response.content}")
        turn += 1
        messages.append(response)
        for tool_call in response.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  call {name}{args}")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"  -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result if isinstance(result, str) else json.dumps(result),
            })
        response = llm_response(messages, tools=TOOLS)

    return response.content

def agent_without_tool(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = llm_response(messages)

    return response.content

def agent_without_thought(user_message: str):
    def without_reasoning(message):
        data = message.model_dump() if hasattr(message, "model_dump") else dict(message)
        data.pop("reasoning_content", None)
        data.pop("reasoning", None)
        return {
            "role": "assistant",
            "content": data.get("content") or "",
            "tool_calls": data.get("tool_calls"),
        }
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = llm_response(messages, tools=TOOLS)

    turn = 1
    while response.tool_calls:
        print(f"Turn {turn}: {response.content}")
        turn += 1
        messages.append(without_reasoning(response))
        for tool_call in response.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  call {name}{args}")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"  -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result if isinstance(result, str) else json.dumps(result),
            })
        response = llm_response(messages, tools=TOOLS)

    return response.content

def agent_without_history(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = llm_response(messages, tools=TOOLS)

    for turn in range(1, 6):  # 没有历史时会重复同一调用，必须封顶
        if not response.tool_calls:
            return response.content
        print(f"Turn {turn}: {response.content}")
        for tool_call in response.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  call {name}{args}")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"  -> {result}")
            # 执行但不写回 messages
        response = llm_response(messages, tools=TOOLS)

    return response.content

def agent_without_tool_result(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = llm_response(messages, tools=TOOLS)

    for turn in range(1, 6):  # 没有历史时会重复同一调用，必须封顶
        if not response.tool_calls:
            return response.content
        print(f"Turn {turn}: {response.content}")
        messages.append(response)
        for tool_call in response.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  call {name}{args}")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"  -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": "",  # 只调用不返回结果
            })
        response = llm_response(messages, tools=TOOLS)

    return response.content

def grade(final_answer: str) -> bool:
    expected = json.loads((BENCH / "expected.json").read_text(encoding="utf-8"))
    text = (final_answer or "").replace(",", "").replace("$", "").replace(" ", "")
    return bool(final_answer) and all(
        n in text for n in expected["upstream_expected_numbers"]
    )

def main():
    print("====== Agent =======")
    agent_response = agent((BENCH / "task.txt").read_text(encoding="utf-8"))
    print(f"Final response: {agent_response}")
    print("correct:", grade(agent_response))

    print("====== Agent without tool =======")
    agent_response = agent_without_tool((BENCH / "task.txt").read_text(encoding="utf-8"))
    print(f"Final response: {agent_response}")
    print("correct:", grade(agent_response))

    print("====== Agent without thought =======")
    agent_response = agent_without_thought((BENCH / "task.txt").read_text(encoding="utf-8"))
    print(f"Final response: {agent_response}")
    print("correct:", grade(agent_response))

    print("====== Agent without history =======")
    agent_response = agent_without_history((BENCH / "task.txt").read_text(encoding="utf-8"))
    print(f"Final response: {agent_response}")
    print("correct:", grade(agent_response))

    print("====== Agent without tool result =======")
    agent_response = agent_without_tool_result((BENCH / "task.txt").read_text(encoding="utf-8"))
    print(f"Final response: {agent_response}")
    print("correct:", grade(agent_response))

if __name__ == "__main__":
    main()
