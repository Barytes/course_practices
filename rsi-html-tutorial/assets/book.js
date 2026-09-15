const CHAPTERS = [
  { file: "index.html", title: "封面与目录", short: "封面", part: "开始" },
  { file: "ch00-how-to-read.html", title: "如何读这份教程", short: "阅读方法", part: "开始" },
  { file: "glossary.html", title: "术语表：把每个词说成人话", short: "术语表", part: "开始" },
  { file: "ch01-why.html", title: "为什么需要递归自我改进", short: "为什么", part: "第一部 · 全貌" },
  { file: "ch02-hci.html", title: "HCI：把能力进度画成一条尺子", short: "HCI 尺子", part: "第一部 · 全貌" },
  { file: "ch03-loop.html", title: "改进环：九个零件与 RSI 定义", short: "改进环", part: "第一部 · 全貌" },
  { file: "ch04-b0.html", title: "B0：只改这次答案", short: "B0", part: "第二部 · 五级阶梯" },
  { file: "ch05-l1.html", title: "L1：按说明书执行改进", short: "L1 执行", part: "第二部 · 五级阶梯" },
  { file: "ch06-l2.html", title: "L2：自己决定怎么改", short: "L2 策略", part: "第二部 · 五级阶梯" },
  { file: "ch07-l3.html", title: "L3：自己决定下一课学什么", short: "L3 经验", part: "第二部 · 五级阶梯" },
  { file: "ch08-l4.html", title: "L4：上线以后继续改自己", short: "L4 适应", part: "第二部 · 五级阶梯" },
  { file: "ch09-l5.html", title: "L5：改进「改进器」本身", short: "L5 元改进", part: "第二部 · 五级阶梯" },
  { file: "ch10-science.html", title: "科学发现里的 RSI", short: "科学", part: "第三部 · 四个场景" },
  { file: "ch11-embodied.html", title: "具身智能里的 RSI", short: "具身", part: "第三部 · 四个场景" },
  { file: "ch12-swe.html", title: "软件工程里的 RSI", short: "软件", part: "第三部 · 四个场景" },
  { file: "ch13-healthcare.html", title: "医疗里的 RSI", short: "医疗", part: "第三部 · 四个场景" },
  { file: "ch14-industry.html", title: "工业实践：六家现场怎么做", short: "工业", part: "第四部 · 落地与缺口" },
  { file: "ch15-challenges.html", title: "八个未解难题与怎么读证据", short: "难题", part: "第四部 · 落地与缺口" },
  { file: "papers-index.html", title: "217 篇参考文献总表", short: "文献总表", part: "第五部 · 每篇工作" },
  { file: "papers-b0.html", title: "引用工作深挖 · B0 与相邻范式", short: "深挖 B0", part: "第五部 · 每篇工作" },
  { file: "papers-l1.html", title: "引用工作深挖 · L1 执行自治", short: "深挖 L1", part: "第五部 · 每篇工作" },
  { file: "papers-l2.html", title: "引用工作深挖 · L2 策略自治", short: "深挖 L2", part: "第五部 · 每篇工作" },
  { file: "papers-l3.html", title: "引用工作深挖 · L3 经验自治", short: "深挖 L3", part: "第五部 · 每篇工作" },
  { file: "papers-l4.html", title: "引用工作深挖 · L4 部署适应", short: "深挖 L4", part: "第五部 · 每篇工作" },
  { file: "papers-l5.html", title: "引用工作深挖 · L5 元改进", short: "深挖 L5", part: "第五部 · 每篇工作" },
  { file: "papers-apps.html", title: "引用工作深挖 · 科学 / 具身 / 软件 / 医疗", short: "深挖场景", part: "第五部 · 每篇工作" },
  { file: "papers-surveys.html", title: "引用工作深挖 · 评测、综述与基础设施", short: "深挖评测", part: "第五部 · 每篇工作" },
  { file: "industry-catalog.html", title: "附录：工业地图里的公司与产品", short: "工业地图", part: "第五部 · 每篇工作" }
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
  let html = `<a class="rail-brand" href="index.html">人类造的最后一代 AI</a>
    <p class="rail-sub">递归自我改进白话教程 · 对齐 arXiv:2609.11873</p>`;
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
  const cur = rail.querySelector("a.current");
  if (cur) cur.scrollIntoView({ block: "center", inline: "nearest" });
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

function installHead() {
  const viewport = document.querySelector('meta[name="viewport"]');
  if (viewport) {
    viewport.setAttribute("content", "width=device-width, initial-scale=1, viewport-fit=cover");
  }
}

function menu() {
  const btn = document.querySelector(".menu-btn");
  const rail = document.querySelector(".rail");
  if (!btn) return;
  btn.setAttribute("aria-expanded", "false");
  btn.setAttribute("aria-controls", "book-rail");
  if (rail && !rail.id) rail.id = "book-rail";

  let backdrop = document.querySelector(".nav-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("button");
    backdrop.className = "nav-backdrop";
    backdrop.type = "button";
    backdrop.setAttribute("aria-label", "关闭目录");
    document.body.appendChild(backdrop);
  }

  const setOpen = (open) => {
    document.body.classList.toggle("nav-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.textContent = open ? "关闭" : "目录";
  };

  btn.addEventListener("click", () => {
    setOpen(!document.body.classList.contains("nav-open"));
  });
  backdrop.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });
  if (rail) {
    rail.addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });
  }
}

function filterWorks() {
  const input = document.querySelector("[data-filter]");
  if (!input) return;
  const works = [...document.querySelectorAll(".work")];
  const apply = () => {
    const q = input.value.trim().toLowerCase();
    works.forEach((w) => {
      const hit = !q || w.innerText.toLowerCase().includes(q);
      w.style.display = hit ? "" : "none";
    });
  };
  input.addEventListener("input", apply);
  const q0 = new URLSearchParams(location.search).get("q");
  if (q0) {
    input.value = q0;
    apply();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  installHead();
  renderRail();
  renderPager();
  enhanceCode();
  menu();
  filterWorks();
});
