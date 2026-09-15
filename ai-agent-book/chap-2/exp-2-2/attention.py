"""最小因果注意力：Q 检索 K，再按分数提取 V。"""

import torch
import torch.nn.functional as F


class CharTokenizer:
    def __init__(self, corpus: list[str]):
        # 定义特殊字符：填充、未知、开始、结束
        specials = ["<pad>", "<unk>", "<bos>", "<eos>"]
        chars = sorted(set[str]("".join(corpus)))
        vocab = specials + [c for c in chars if c not in specials]
        self.stoi = {char: i for i, char in enumerate(vocab)}
        self.itos = {i: char for i, char in enumerate(vocab)}
        self.pad_id = self.stoi["<pad>"]
        self.unk_id = self.stoi["<unk>"]
        self.bos_id = self.stoi["<bos>"]
        self.eos_id = self.stoi["<eos>"]


    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(char, self.unk_id) for char in text]

    def decode(self, ids: list[int]) -> str:
        skip = [self.pad_id, self.bos_id, self.eos_id]
        return "".join(self.itos[id] for id in ids if id not in skip)

    def pad(self, batch: list[list[int]]) -> torch.Tensor:
        # 右侧补 pad，真实 token 靠左，方便因果注意力从位置 0 读起
        max_len = max(len(ids) for ids in batch)
        padded = [ids + [self.pad_id] * (max_len - len(ids)) for ids in batch]
        return torch.tensor(padded, dtype=torch.long)  # [B, S]

class TokenEmbedding(torch.nn.Module):
    # token embedding layer就是一张查找表，输入token id，输出token embedding
    # 表的大小是vocab_size * d_model，即词表里词的数量*每个词嵌入向量的维度
    def __init__(self, vocab_size: int, d_model: int):
        super().__init__()
        self.tok = torch.nn.Embedding(vocab_size, d_model)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # input_ids: [B, S]
        return self.tok(input_ids)  # [B, S, D]

# 还要位置信息。没有位置时，"天气北京的" 和 "北京的天气" 在注意力看来只是同一袋向量
# （因果掩码会带来一点顺序，但不够）
class PositionalEmbedding(torch.nn.Module):
    def __init__(self, max_len: int, d_model: int):
        super().__init__()
        self.pos = torch.nn.Embedding(max_len, d_model)

    def forward(self, x: torch.Tensor, start_pos: int = 0) -> torch.Tensor:
        # x: [B, S, D]
        B, S, _ = x.shape
        positions = torch.arange(start_pos, start_pos + S, device=x.device)
        return x + self.pos(positions)  # [B, S, D]

def causal_mask(q_len: int, k_len: int, device: torch.device) -> torch.Tensor:
        # True 表示「禁止看」
        q_pos = torch.arange(k_len - q_len, k_len, device=device)[:, None]  # [q_len, 1]
        k_pos = torch.arange(k_len, device=device)[None, :]                 # [1, k_len]
        return k_pos > q_pos  # [q_len, k_len]

class Attention(torch.nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model
        self.q = torch.nn.Linear(d_model, d_model)
        self.k = torch.nn.Linear(d_model, d_model)
        self.v = torch.nn.Linear(d_model, d_model)
        self.out = torch.nn.Linear(d_model, d_model)

    def forward(self, x, pad_mask=None):
        # x: [B, S, D]
        q, k, v = self.q(x), self.k(x), self.v(x)
        scale = self.d_model ** 0.5
        scores = q @ k.transpose(-2, -1) / scale

        q_len, k_len = q.size(-2), k.size(-2)
        causal = self.causal_mask(q_len, k_len, x.device)  # [S, S]，True=禁止
        scores = scores.masked_fill(causal, float("-inf")) # 未来格子 → -inf
        if pad_mask is not None:
            scores = scores.masked_fill(pad_mask[:, None, :], float("-inf"))

        weights = F.softmax(scores, dim=-1) # 对每一行做 softmax：weights[i].sum() == 1
        return self.out(weights @ v), weights

class MultiHeadAttention(torch.nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.Wq = torch.nn.Linear(d_model, d_model, bias=False)
        self.Wk = torch.nn.Linear(d_model, d_model, bias=False)
        self.Wv = torch.nn.Linear(d_model, d_model, bias=False)
        self.Wo = torch.nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, k_cache=None, v_cache=None):
        # x: [B, S, D]
        B, S, _ = x.shape
        q = self.Wq(x).view(B, S, self.n_heads, self.d_head).transpose(1, 2)
        k = self.Wk(x).view(B, S, self.n_heads, self.d_head).transpose(1, 2)
        v = self.Wv(x).view(B, S, self.n_heads, self.d_head).transpose(1, 2)

        if k_cache is not None:
            k = torch.cat([k_cache, k], dim=2)
            v = torch.cat([v_cache, v], dim=2)

        Dh = self.d_head
        scores = q @ k.transpose(-2, -1) / (Dh ** 0.5)
        q_len, k_len = q.size(-2), k.size(-2)
        mask = causal_mask(q_len, k_len, x.device)
        scores = scores.masked_fill(mask, float("-inf"))
        weights = F.softmax(scores, dim=-1)
        ctx = weights @ v
        out = ctx.transpose(1, 2).contiguous().view(B, S, -1)
        return self.Wo(out), k, v

class Block(torch.nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.ln1 = torch.nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ln2 = torch.nn.LayerNorm(d_model)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(d_model, 4 * d_model),
            torch.nn.GELU(),
            torch.nn.Linear(4 * d_model, d_model),
        )

    def forward(self, x, k_cache=None, v_cache=None):
        h, k, v = self.attn(self.ln1(x), k_cache, v_cache)
        x = x + h
        x = x + self.ffn(self.ln2(x))
        return x, k, v

class TinyLM(torch.nn.Module):
    def __init__(self, vocab_size, d_model, n_heads, n_layers, max_len):
        super().__init__()
        self.embed = TokenEmbedding(vocab_size, d_model)
        self.pos = PositionalEmbedding(max_len, d_model)
        self.blocks = torch.nn.ModuleList(
            [Block(d_model, n_heads) for _ in range(n_layers)]
        )
        self.ln_f = torch.nn.LayerNorm(d_model)
        self.lm_head = torch.nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, caches=None, start_pos=0):
        # input_ids: [B, S]
        # caches: None 或 list[(k, v)]，长度 = n_layers
        x = self.pos(self.embed(input_ids), start_pos=start_pos)
        new_caches = []
        for i, block in enumerate(self.blocks):
            k_c = v_c = None
            if caches is not None:
                k_c, v_c = caches[i]
            x, k, v = block(x, k_c, v_c)
            new_caches.append((k, v))
        logits = self.lm_head(self.ln_f(x))  # [B, S, vocab]
        return logits, new_caches

@torch.no_grad()
def generate_naive(model, tokenizer, text, max_new_tokens):
    ids = torch.tensor([tokenizer.encode(text)], dtype=torch.long)
    for _ in range(max_new_tokens):
        logits, _ = model(ids)          # TinyLM 返回 (logits, caches)
        next_id = logits[:, -1].argmax(-1, keepdim=True)
        ids = torch.cat([ids, next_id], dim=1)
    return tokenizer.decode(ids[0].tolist())


@torch.no_grad()
def generate_cached(model, tokenizer, text, max_new_tokens):
    ids = torch.tensor([tokenizer.encode(text)], dtype=torch.long)
    # 1) prefill
    logits, caches = model(ids, caches=None, start_pos=0)
    next_id = logits[:, -1].argmax(-1, keepdim=True)
    ids = torch.cat([ids, next_id], dim=1)

    # 2) decode
    for _ in range(max_new_tokens - 1):
        logits, caches = model(next_id, caches=caches, start_pos=ids.size(1) - 1)
        next_id = logits[:, -1].argmax(-1, keepdim=True)
        ids = torch.cat([ids, next_id], dim=1)
    return tokenizer.decode(ids[0].tolist())

def main():
    corpus = [
        "北京的天气怎么样",
        "今天会下雨吗？",
        "Hello, world!",
    ]
    tokenizer = CharTokenizer(corpus)
    model = TinyLM(vocab_size=len(tokenizer.stoi), d_model=128, n_heads=8, n_layers=6, max_len=100)
    torch.manual_seed(0)
    text = "北京的天气怎么样，今天适合出门吗？"
    a = generate_naive(model, tokenizer, text, max_new_tokens=8)
    torch.manual_seed(0)
    # 权重相同的另一份调用
    b = generate_cached(model, tokenizer, text, max_new_tokens=8)
    print(a)
    print(b)
    print(a == b)
    assert a == b

    ids_a = torch.tensor([tokenizer.encode("北京的天气怎么样")])
    ids_b = torch.tensor([tokenizer.encode("今天的天气怎么样")])  # 只改了开头
    _, cache_a = model(ids_a)
    _, cache_b = model(ids_b)
    # 第 0 层、第 0 个 key 已经不同
    print(cache_a[0][0][:, :, 0])
    print(cache_b[0][0][:, :, 0])
    assert not torch.allclose(cache_a[0][0][:, :, 0], cache_b[0][0][:, :, 0])

if __name__ == "__main__":
    main()
