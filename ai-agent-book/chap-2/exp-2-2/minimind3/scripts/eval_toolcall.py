"""对齐官方 scripts/eval_toolcall.py。对照教材第 17 章。"""


def get_tools(names):
    ...


def init_model(args):
    ...


def parse_tool_calls(text):
    ...


def parse_tool_call_from_text(content):
    ...


def execute_tool(call, arguments=None):
    ...


def generate(model, tokenizer, messages, tools, args):
    ...


def chat_api(client, messages, tools, args, stream=True):
    ...


def run_case(prompt, tools, args, model=None, tokenizer=None, client=None):
    ...


def main():
    ...


if __name__ == "__main__":
    main()
