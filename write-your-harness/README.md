# 写自己的 Harness

对照开源仓库的 Agent 工程教材。快照日期：**2026-09-15**。过时是设计，不是事故。

## 这是什么

一本把循环写进手指的教材，外加一份标准库就能跑的教学 harness。每章按「人话 → 超小例子 → 代码 → 可跳过的深度」写，小白第一遍只看黑底框也能往下做。

- 前半本：亲手写出循环、六件套工具、压缩、护栏、玩具评测。
- 后半本：不背框架，读 [nanocode](https://github.com/1rgs/nanocode)、[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)、[pi](https://github.com/earendil-works/pi)、[opencode](https://github.com/anomalyco/opencode)、[codex](https://github.com/openai/codex)、[deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) 的取舍和 releases。

用书籍研究 Agent，发布即过时。这里只训练两件事：循环写得动，仓库读得动。

## 怎么读

用浏览器打开 [`textbook/index.html`](textbook/index.html)，或看网页版 [barytes.github.io/course_practices/harness](https://barytes.github.io/course_practices/harness/)。请先读第 0 章、术语表和动手地图。第一遍跳过「先别管」；第二遍再读对照仓库的问题清单。

## 怎么跑

需要 Python 3.11+。核心零第三方依赖。

```bash
cd write-your-harness
python tests/test_miniharness.py
python -m miniharness demo
python -m miniharness watch          # 拉六个仓库的 GitHub releases
```

`demo` 不需要 API key：脚本模型会在临时目录里修好 `labs/broken_calc` 的 `add()`。

可选：设置 `OPENAI_API_KEY`（以及 `OPENAI_BASE_URL` / `MODEL`）后：

```bash
python -m miniharness run "列出 Python 文件" --workspace .
```

没有操作系统沙箱。不要对不可信输入打开 bash。

## 目录

| 路径 | 作用 |
| --- | --- |
| `textbook/` | HTML 教材 |
| `miniharness/` | 教学 harness |
| `labs/broken_calc/` | 玩具 SWE 夹具 |
| `tests/` | 零件测试 |
