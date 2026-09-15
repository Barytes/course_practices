# 填空：自己写完 minbpe

源码来自 [karpathy/minbpe](https://github.com/karpathy/minbpe)（MIT）。只下载了包和测试，没有克隆整个仓库。搜 `# >>> 填空` 就能找到所有要写的位置。

在本目录执行：

```bash
pip install -r requirements.txt pytest
pytest -v tests/test_tokenizer.py
```

先把 Step 1 写完，只跑维基那道例题：

```bash
pytest -v tests/test_tokenizer.py::test_wikipedia_example
```

`recover_merges` / `bpe`、存盘 `save`/`load`、GPT-4 词表加载已经留下。你要写的是算法本身。

Step 1、2 写完后，可在本目录跑 `python train.py`：用 `tests/taylorswift.txt` 训 512 词表，写出 `models/basic.vocab` 和 `models/regex.vocab`，方便肉眼看合并是否合理。

---

### Step 1 · `get_stats` / `merge` / `BasicTokenizer`

文件：`minbpe/base.py`、`minbpe/basic.py`

- `get_stats`：`[1, 2, 3, 1, 2] -> {(1, 2): 2, (2, 3): 1, (3, 1): 1}`
- `merge`：从左到右、互不重叠。`aaa` 焊一次 `(a,a)` 得到 `[aa] a`
- `train`：UTF-8 → 反复焊最常见对 → 记下 `merges` 和 `vocab`
- `encode`：按 merge **编号从小到大**焊，不是按当前频率
- `decode`：编号查成字节，`errors="replace"`

对照：`text = "aaabdaaabac"`，`vocab_size=256+3`，编码应是 `[258, 100, 258, 97, 99]`。

### Step 2 · `RegexTokenizer`

文件：`minbpe/regex.py`

先用正则把文本切成「字母 / 数字 / 标点 / 空白」块，**合并绝不跨块**。统计时把所有块的 `get_stats` 加总，真正 `merge` 时只在各自块里替换。再写 `encode_ordinary`。

### Step 3 · 对齐 GPT-4

文件：`minbpe/gpt4.py`

`__init__` 已经从 tiktoken 的 `cl100k_base` 恢复了 merges，并算好 `byte_shuffle`。你只需在 `_encode_chunk` 里先打乱字节，在 `decode` 里再打回去。

### Step 4 · 特殊标记（可选）

`register_special_tokens`、`RegexTokenizer.decode` 对特殊编号的分支、`encode(..., allowed_special=...)` 里用捕获组把特殊标记切出来单独换成编号。

没有 `allowed_special="all"` 时，字符串里一旦出现 `<|endoftext|>`，tiktoken 会报错。这是安全问题，不是风格问题。

### Step 5

许多非 OpenAI 模型用 SentencePiece，在 Unicode 码点上跑 BPE，而不是 UTF-8 字节。不必做进作业。
