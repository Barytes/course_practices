"""对齐官方 scripts/serve_openai_api.py。对照教材第 17 章。"""


def init_model(args):
    ...


class ChatRequest:
    ...


class CustomStreamer:
    ...


def parse_response(text):
    ...


def generate_stream_response(messages, temperature, top_p, max_tokens, tools=None, open_thinking=False):
    ...


if __name__ == "__main__":
    ...
