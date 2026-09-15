"""
Minimal (byte-level) Byte Pair Encoding tokenizer.

Algorithmically follows along the GPT tokenizer:
https://github.com/openai/gpt-2/blob/master/src/encoder.py

But:
- Does not handle the regular expression splitting pattern.
- Does not handle any special tokens.
"""

from .base import Tokenizer, get_stats, merge


class BasicTokenizer(Tokenizer):

    def __init__(self):
        super().__init__()

    # train: 根据文本训练tokenizer，生成merges和vocab
    # text: 文本
    # vocab_size: 词表大小
    # verbose: 是否打印详细信息
    # 目的：把text成vocab_size个编码，并记录合并历史
    # 逻辑：将text转化为utf-8编码的整数列表，然后合并出现次数最多的pair为一个新的编码，直到达到vocab_size。
    def train(self, text, vocab_size, verbose=False):
        # 确保词表大小至少为256，即大于等于UTF-8的码点数（256）。
        assert vocab_size >= 256
        num_merges = vocab_size - 256

        # 将text转化为UTF-8编码的整数列表
        text_bytes = text.encode("utf-8") # 将text转化为utf-8编码的原始字节
        ids = list(text_bytes) # 将原始字节转化为整数列表
        
        # merges: 记录合并的历史，(int, int) -> int
        # vocab: 记录编码对应的原始字节，int -> bytes, 初始化为utf-8编码的原始字节
        merges = {}
        vocab = {idx: bytes([idx]) for idx in range(256)}
        # 迭代合并ids中出现次数最多的pair为一个新的编码，直到达到vocab_size。
        for i in range(num_merges):
            # 先统计ids中各个pair的出现次数（get_stats函数）
            stats = get_stats(ids)
            # 找到出现次数最多的pair
            pair = max(stats, key=stats.get)
            # 创建一个新的编码表示这个pair
            idx = 256 + i
            # 更新ids（merge函数）
            ids = merge(ids, pair, idx)
            # 更新merges
            merges[pair] = idx
            # 更新vocab
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
            # 打印信息
            if verbose:
                print(f"merge {i+1}/{num_merges}: {pair} -> {idx} ({vocab[idx]}) had {stats[pair]} occurrences")
        self.merges = merges
        self.vocab = vocab

    # decode: 根据编码解码为文本
    # ids: 编码的列表
    # 目的：将编码的列表解码为文本
    # 逻辑：将编码转换为原始字节，然后按UTF-8解码为文本
    def decode(self, ids):
        # given ids (list of integers), return Python string
        # >>> 填空：每个编号查 self.vocab 得到 bytes，拼起来，再按 UTF-8 解开。
        # 某个词元可能只是半个汉字，所以 decode 时要用 errors="replace"。
        text_bytes = b"".join(self.vocab[i] for i in ids)
        return text_bytes.decode("utf-8", errors="replace")

    def encode(self, text):
        # given a string text, return the token ids
        text_bytes = text.encode("utf-8") # raw bytes
        ids = list(text_bytes) # list of integers in range 0..255
        while len(ids) >= 2:
            # >>> 填空：按 merges 的出生顺序焊，不是按当前这句话里哪一对最多。
            stats = get_stats(ids)
            # 为什么pair不是ids[i:i+2]？因为并不符合train过程中形成的编码。
            # 例如：abc -> {(a,b):258, (b,c):257} -> a257
            # 那么编码过程从ab开始，就会变成258c，而不是a257。
            pair = min(stats, key=lambda p: self.merges.get(p,float("inf")))
            if pair not in self.merges:
                break
            # 4. 否则 idx = self.merges[pair]，ids = merge(ids, pair, idx)
            idx = self.merges[pair]
            ids = merge(ids, pair, idx)
        return ids


# tok = BasicTokenizer()
# text = "aaabdaaabac"
# tok.train(text, vocab_size=256 + 3, verbose=True)
# print(tok.encode(text))          # [258, 100, 258, 97, 99]
# print(tok.decode([258, 100, 258, 97, 99]))  # aaabdaaabac

