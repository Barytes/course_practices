const CHAPTERS = [
  { file: "index.html", title: "封面与目录", short: "封面", part: "开始" },
  { file: "ch00-how-to-read.html", title: "这本书为什么不是一本书", short: "读法", part: "开始" },
  { file: "glossary.html", title: "术语表：把每个词说成人话", short: "术语表", part: "开始" },
  { file: "files.html", title: "动手地图：文件、模块、函数", short: "动手地图", part: "开始" },
  { file: "ch01-what-we-build.html", title: "我们要造什么", short: "全貌", part: "第一部 · 骨架" },
  { file: "ch02-nanocode.html", title: "扫一眼 nanocode", short: "nanocode", part: "第一部 · 骨架" },
  { file: "ch03-loop.html", title: "亲手写循环", short: "循环", part: "第一部 · 骨架" },
  { file: "ch04-tools.html", title: "工具面：六件套还是只给 bash", short: "工具", part: "第二部 · 零件" },
  { file: "ch05-context.html", title: "上下文怎么长、怎么瘦", short: "上下文", part: "第二部 · 零件" },
  { file: "ch06-guards.html", title: "护栏：权限、循环、预算", short: "护栏", part: "第二部 · 零件" },
  { file: "ch07-cli.html", title: "接上 CLI 与轨迹", short: "CLI", part: "第二部 · 零件" },
  { file: "ch08-mini-swe.html", title: "评测为什么要极简 scaffold", short: "mini-swe", part: "第三部 · 评测" },
  { file: "ch09-eval.html", title: "玩具评测：假仓库、假 issue", short: "玩具评测", part: "第三部 · 评测" },
  { file: "ch10-pi.html", title: "pi：可扩展的极简生产级", short: "pi", part: "第四部 · 取舍" },
  { file: "ch11-opencode.html", title: "opencode：可观测性与重构", short: "opencode", part: "第四部 · 取舍" },
  { file: "ch12-codex.html", title: "codex：工业级约束", short: "codex", part: "第四部 · 取舍" },
  { file: "ch13-dsh.html", title: "deepseek-harness：万物皆插件", short: "dsh", part: "第四部 · 取舍" },
  { file: "ch14-assemble.html", title: "拼成你自己的 harness", short: "拼装", part: "第五部 · 往后" },
  { file: "ch15-living.html", title: "发布即过时：以后怎么自学", short: "动态学习", part: "第五部 · 往后" }
];

function currentFile() {
  const path = decodeURIComponent(location.pathname || "");
  const name = path.split("/").pop();
  return name && name.endsWith(".html") ? name : "index.html";
}

function renderRail() {
  const rail = document.querySelector("[data-toc]");
  if (!rail) return;
  const here = currentFile();
  let html = `<a class="rail-brand" href="index.html">写自己的 Harness</a>
    <p class="rail-sub">对照开源仓库 · 快照 2026-09-15</p>`;
  let lastPart = "";
  for (const ch of CHAPTERS) {
    if (ch.part !== lastPart) {
      html += `<h2>${ch.part}</h2>`;
      lastPart = ch.part;
    }
    const cls = ch.file === here ? "current" : "";
    html += `<a class="${cls}" href="${ch.file}">${ch.short}</a>`;
  }
  rail.innerHTML = html;
}

function renderPager() {
  const pager = document.querySelector("[data-pager]");
  if (!pager) return;
  const here = currentFile();
  const i = CHAPTERS.findIndex((c) => c.file === here);
  if (i < 0) return;
  const prev = CHAPTERS[i - 1];
  const next = CHAPTERS[i + 1];
  pager.innerHTML = `
    ${prev ? `<a href="${prev.file}"><span class="label">上一章</span>${prev.title}</a>` : `<span></span>`}
    ${next ? `<a class="next" href="${next.file}"><span class="label">下一章</span>${next.title}</a>` : `<span></span>`}
  `;
}

function enhanceCode() {
  document.querySelectorAll("figure.code").forEach((fig) => {
    const cap = fig.querySelector("figcaption");
    const pre = fig.querySelector("pre code, pre");
    if (!cap || !pre) return;
    if (cap.querySelector(".copy")) return;
    const btn = document.createElement("button");
    btn.className = "copy";
    btn.type = "button";
    btn.textContent = "复制";
    btn.addEventListener("click", async () => {
      const text = (fig.querySelector("pre") || pre).innerText;
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "已复制";
        setTimeout(() => (btn.textContent = "复制"), 1200);
      } catch {
        btn.textContent = "复制失败";
      }
    });
    cap.appendChild(btn);
  });
}

function menu() {
  const btn = document.querySelector(".menu-btn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    document.body.classList.toggle("nav-open");
  });
  document.querySelectorAll(".rail a").forEach((a) => {
    a.addEventListener("click", () => document.body.classList.remove("nav-open"));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderRail();
  renderPager();
  enhanceCode();
  menu();
});
