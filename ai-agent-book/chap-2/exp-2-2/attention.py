"""最小因果注意力：Q 检索 K，再按分数提取 V。"""

import torch
import torch.nn.functional as F


class Tokenizer:
    def __init__(self, corpus: list[str]):
        # 定义特殊字符：填充、未知、开始、结束
        specials = ["<pad>", "<unk>", "<bos>", "<eos>"]
        chars = sorted(set[str]("".join(corpus)))
        vocab = specials + chars
        self.stoi = {char: i for i, char in enumerate(vocab)}
        self.itos = {i: char for i, char in enumerate(vocab)}
        self.pad_id = self.stoi["<pad>"]
        self.unk_id = self.stoi["<unk>"]
        self.bos_id = self.stoi["<bos>"]
        self.eos_id = self.stoi["<eos>"]


    def endcode(self, text: str) -> list[int]:
        pass

    def decode(self, ids: list[int]) -> str:
        pass


def main():
    pass


if __name__ == "__main__":
    main()
