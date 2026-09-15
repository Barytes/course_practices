# course_practices

这是我做各种课程作业的练习仓库。

在线阅读：[barytes.github.io/course_practices](https://barytes.github.io/course_practices/)。若 404，到仓库 [Settings → Pages](https://github.com/Barytes/course_practices/settings/pages) 把 Source 设成 `gh-pages`。

| 教材 | 仓库路径 | 网页 |
| --- | --- | --- |
| 从零实现 MiniMind-3 | `ai-agent-book/chap-2/exp-2-2/minimind-textbook/` | [minimind](https://barytes.github.io/course_practices/minimind/) |
| 写自己的 Harness | `write-your-harness/textbook/` | [harness](https://barytes.github.io/course_practices/harness/) |
| 人类造的最后一代 AI | `rsi-html-tutorial/` | [rsi](https://barytes.github.io/course_practices/rsi/) |

## ai-agent-book

对应教程：[深入理解 AI Agent](https://bojieli.github.io/ai-agent-book/)（[bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book)）。

当前练习从第 1 章起步，例如 `ai-agent-book/chap.1/exp-1-1/` 里的上下文消融实验。第 2 章 MiniMind 手把手教材也可以下载同目录里的 `minimind-3.epub`。

## rsi-html-tutorial

白话 HTML 教程，对齐综述 [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement](https://arxiv.org/abs/2609.11873)。用浏览器打开 `rsi-html-tutorial/index.html` 即可，不必启动服务。第五部按参考文献把每项工作的实现与难点摊成卡片；附录对应综述 Table 12 的工业地图。重新生成第五部页面：`python3 rsi-html-tutorial/rebuild.py`。
