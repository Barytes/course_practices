# -*- coding: utf-8 -*-
"""Build papers-index.html: all 217 bibliography entries linked to tutorial cards."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from _gen import FOOT, HEAD, h2, p

ROOT = Path(__file__).resolve().parent
REFS = (ROOT / "references.md").read_text(encoding="utf-8", errors="replace")

CARD_FILES = [
    "papers-b0.html",
    "papers-l1.html",
    "papers-l2.html",
    "papers-l3.html",
    "papers-l4.html",
    "papers-l5.html",
    "papers-apps.html",
    "papers-surveys.html",
    "industry-catalog.html",
    "ch04-b0.html",
    "ch05-l1.html",
    "ch06-l2.html",
    "ch07-l3.html",
    "ch08-l4.html",
    "ch09-l5.html",
    "ch10-science.html",
    "ch11-embodied.html",
    "ch12-swe.html",
    "ch13-healthcare.html",
    "ch14-industry.html",
    "ch01-why.html",
    "ch02-hci.html",
    "ch03-loop.html",
]


def parse_refs(text: str):
    entries = re.split(r"\n\* ", text)
    out = []
    for e in entries[1:]:
        lines = [ln.strip() for ln in e.splitlines() if ln.strip()]
        key = lines[0]
        title = ""
        for ln in lines[1:]:
            if ln.startswith(("External", "Cited", "Note:", "In ", "Lecture", "Proceedings", "Transactions", "arXiv preprint", "pp.", "[", "Vol.", "Bangkok", "https://")):
                continue
            if re.match(r"^(\d{2}\. )?[A-Z]\. ", ln) and ":" not in ln[:40] and "http" not in ln:
                continue
            if ln.startswith("01. AI") or ln.startswith("DeepSeek-AI"):
                continue
            title = ln.replace("$\\\\tau$", "tau").replace("$\\tau$", "tau").rstrip(".")
            break
        arxiv = ""
        m = re.search(r"(?:arXiv:|External Links: )(\d{4}\.\d{4,5})", e)
        if m:
            arxiv = m.group(1)
        link = ""
        m = re.search(r"\]\((https://[^)]+)\)", e)
        if m:
            link = m.group(1)
        cited = ""
        m = re.search(r"Cited by:\s*(.+)", e)
        if m:
            cited = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group(1))
            cited = re.sub(r"\s+", " ", cited).strip()
        out.append(dict(key=key, title=title, arxiv=arxiv, link=link, cited=cited, raw=e[:800]))
    return out


def load_cards():
    cards = []
    for fname in CARD_FILES:
        path = ROOT / fname
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(
            r'<div class="work" id="([^"]+)">\s*<h3>(.*?)</h3>(.*?)</div>\s*(?=<div class="work"|<h2|</article>)',
            html,
            flags=re.S,
        ):
            cid, h3, body = m.group(1), m.group(2), m.group(3)
            text = re.sub(r"<[^>]+>", " ", h3 + " " + body)
            text = re.sub(r"\s+", " ", text)
            cards.append(dict(file=fname, cid=cid, title=re.sub(r"<[^>]+>", "", h3), text=text.lower()))
    return cards


STOP = {
    "self", "from", "with", "large", "survey", "open", "towards", "toward", "evaluating",
    "evaluation", "technical", "report", "agents", "agent", "model", "models", "learning",
    "language", "recursive", "improvement", "based", "using", "via", "for", "and", "the",
    "a", "an", "of", "in", "on", "to", "into", "over", "their", "its", "can", "how",
}


def tokens(title: str):
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", title)
    return [w for w in words if w.lower() not in STOP]


HINTS = {
    "AI et al. (2025)": ["yi", "01.ai"],
    "Hu et al. (2025)": ["adas"],
    "Hu et al. (2024)": ["evomac"],
    "Yin et al. (2025)": ["gödel agent", "godel agent"],
    "Robeyns et al. (2025)": ["sica"],
    "Shang and Yang (2026)": ["hdso"],
    "Schmidhuber (2003)": ["gödel machine", "godel machine"],
    "Yao et al. (2024)": ["tau-bench", "τ-bench"],
    "Li et al. (2024)": ["datacomp"],
    "Wen et al. (2026)": ["weak-to-strong", "评测利用"],
    "Dong and Ma (2025)": ["stp"],
    "Hebbar et al. (2026)": ["sia"],
    "Jeong et al. (2026)": ["agentnas"],
    "Liang et al. (2026)": ["pahf"],
    "Wang and Meyerzon (2026)": ["dropbox", "dash"],
    "Zeng et al. (2026)": ["repo"],
    "Du et al. (2025)": ["标准化病人", "evo-patient", "coevolution"],
    "Huang et al. (2026b)": ["记忆综述", "agent memory", "long-horizon"],
    "Li et al. (2025a)": ["llm-as-a-judge", "评判"],
    "Li et al. (2026a)": ["serp", "replanning", "导航"],
    "Li et al. (2025c)": ["tissuelab", "医学成像"],
    "Li (2026)": ["self-correction", "自我纠正"],
    "Lu and Xia (2026)": ["c/c++", "性能优化"],
    "Lu et al. (2026b)": ["ttte", "tool evolution", "工具演化"],
    "Wu et al. (2024)": ["continual learning", "持续学习"],
    "Xu et al. (2026)": ["dynamic graph", "动态图"],
    "Ye et al. (2026)": ["ai-for-ai", "ai4ai", "improver"],
}


def match(entry, cards):
    hits = []
    if entry["arxiv"]:
        for c in cards:
            if entry["arxiv"] in c["text"]:
                hits.append((100, c))
    key = entry["key"]
    last = re.split(r"[,\s]", key)[0].lower()
    ym = re.search(r"\((\d{4}[a-z]?)\)", key)
    year = ym.group(1) if ym else ""
    tks = [t.lower() for t in tokens(entry["title"])[:8]]
    head = entry["title"].split(":")[0].strip().lower()
    hints = HINTS.get(key, [])
    for c in cards:
        score = 0
        blob = c["text"]
        if last and len(last) >= 3 and last in blob and year and year.lower() in blob:
            score += 12
        if head and 2 <= len(head) <= 40 and head in blob:
            score += 20
        for t in tks:
            if len(t) >= 4 and t in blob:
                score += 3
        for h in hints:
            if h.lower() in blob:
                score += 25
        if score >= 12:
            hits.append((score, c))
    # unique by file#id
    best = {}
    for score, c in sorted(hits, key=lambda x: -x[0]):
        k = c["file"] + "#" + c["cid"]
        if k not in best:
            best[k] = (score, c)
        if len(best) >= 3:
            break
    return [v[1] for v in best.values()]


def main():
    entries = parse_refs(REFS)
    cards = load_cards()
    rows = []
    n_linked = 0
    for i, e in enumerate(entries, 1):
        ms = match(e, cards)
        if ms:
            n_linked += 1
        links = "；".join(
            f"<a href='{c['file']}#{c['cid']}'>{c['title']}</a>" for c in ms
        ) or "<span class='faint'>见同行卡片或综述原文引用处</span>"
        href = e["link"] or (f"https://arxiv.org/abs/{e['arxiv']}" if e["arxiv"] else "")
        title = e["title"] or e["key"]
        t_html = f"<a href='{href}'>{title}</a>" if href else title
        arx = f"<code>{e['arxiv']}</code>" if e["arxiv"] else "—"
        rows.append(
            f"<tr data-row><td>{i}</td><td>{e['key']}</td><td>{t_html}</td>"
            f"<td>{arx}</td><td>{links}</td></tr>"
        )

    body = []
    body.append(
        p(
            f"综述参考文献共 <strong>{len(entries)}</strong> 条。本页生成时有 <strong>{n_linked}</strong> 条能自动链到教程卡片"
            f"（用 arXiv 编号或「作者+年份+题名关键词」匹配）。点第三列看原文，点最后一列看实现展开。"
            f"工业产品若不在参考文献表里，请到 <a href='industry-catalog.html'>工业地图</a>。"
        )
    )
    body.append(
        """<div class="search-box"><input data-filter-table type="search" placeholder="按作者、题名、arXiv 过滤……"></div>
<table class="plain bib">
<thead><tr><th>#</th><th>文献键</th><th>题名</th><th>arXiv</th><th>教程卡片</th></tr></thead>
<tbody>
"""
        + "\n".join(rows)
        + "</tbody></table>"
        + """
<script>
document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector("[data-filter-table]");
  if (!input) return;
  const trs = [...document.querySelectorAll("[data-row]")];
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    trs.forEach((tr) => {
      tr.style.display = !q || tr.innerText.toLowerCase().includes(q) ? "" : "none";
    });
  });
});
</script>
"""
    )

    html = HEAD.format(
        title="217 篇参考文献总表",
        kicker="第五部 · 每篇工作",
        h1="综述引用的每一项工作：总表",
        lead="先在这里按作者或系统名搜索，再跳进对应卡片看实现路径和技术难点。主线章节讲清楚「为什么分在这一级」，卡片负责把代码、权重、评测拆开。",
        box="这一页是目录，不是替代第 0–3 章。没有改进环的三问，表格只是论文名清单。",
    )
    # HEAD already includes a work-filter search box that would confuse this page.
    html = html.replace(
        '<div class="search-box"><input data-filter type="search" placeholder="按系统名、作者、技术词过滤……"></div>\n',
        "",
    )
    out = ROOT / "papers-index.html"
    out.write_text(html + "".join(body) + FOOT, encoding="utf-8")
    print("wrote", out.name, "entries", len(entries), "linked", n_linked, "cards", len(cards))


if __name__ == "__main__":
    main()
