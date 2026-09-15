# Shared HTML helpers for RSI tutorial paper pages.
HEAD = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="assets/book.css">
</head>
<body>
<button class="menu-btn" type="button">目录</button>
<div class="shell">
  <aside class="rail" data-toc></aside>
  <main class="paper">
    <header class="chap-head">
      <p class="kicker">{kicker}</p>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
    </header>
    <article class="prose">
      <div class="plain-box">
        <p class="label">这一页怎么用</p>
        <p>{box}</p>
      </div>
      <div class="search-box"><input data-filter type="search" placeholder="按系统名、作者、技术词过滤……"></div>
"""

FOOT = """
    </article>
    <nav class="pager" data-pager></nav>
  </main>
</div>
<script src="assets/book.js"></script>
</body>
</html>
"""

def badge(level):
    key = level.split()[0].lower().replace("–", "-")
    cls = "b0"
    if key.startswith("l1"):
        cls = "l1"
    elif key.startswith("l2"):
        cls = "l2"
    elif key.startswith("l3"):
        cls = "l3"
    elif key.startswith("l4"):
        cls = "l4"
    elif key.startswith("l5"):
        cls = "l5"
    return f'<span class="badge {cls}">{level}</span>'

def work(wid, title, meta, level, problem, steps, impl, hard, keep_ai, keep_human, extra=""):
    lis = "\n".join(f"<li>{s}</li>" for s in steps)
    extra_html = f"<p>{extra}</p>" if extra else ""
    return f"""
<div class="work" id="{wid}">
  <h3>{title}</h3>
  <p class="meta">{badge(level)} {meta}</p>
  <h4>它想解决什么</h4>
  <p>{problem}</p>
  <h4>实现怎么走</h4>
  <ol>{lis}</ol>
  <p>{impl}</p>
  {extra_html}
  <div class="hard"><p class="label">技术难点</p><p>{hard}</p></div>
  <div class="keep">
    <div><div class="k">改了 / 留下什么</div>{keep_ai}</div>
    <div><div class="k">人还控什么</div>{keep_human}</div>
  </div>
</div>
"""

def h2(text):
    return f"<h2>{text}</h2>\n"

def p(text):
    return f"<p>{text}</p>\n"
