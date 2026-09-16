"""对齐官方 trainer/train_tokenizer.py。对照教材第 2.5 章与官方脚本。"""

DATA_PATH = "../dataset/sft_t2t_mini.jsonl"
TOKENIZER_DIR = "../model_learn_tokenizer/"
VOCAB_SIZE = 6400
SPECIAL_TOKENS_NUM = 36


def get_texts(data_path):
    ...


def train_tokenizer(data_path, tokenizer_dir, vocab_size, special_tokens_num=SPECIAL_TOKENS_NUM):
    ...


def eval_tokenizer(tokenizer_dir):
    ...


if __name__ == "__main__":
    ...
