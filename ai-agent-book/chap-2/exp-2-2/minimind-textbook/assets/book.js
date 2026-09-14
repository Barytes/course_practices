const CHAPTERS = [
  { file: "index.html", title: "封面与目录", short: "封面", part: "开始" },
  { file: "ch00-how-to-read.html", title: "如何读这本书", short: "阅读方法", part: "开始" },
  { file: "ch01-what-we-build.html", title: "我们要造什么", short: "全貌", part: "第一部 · 全貌" },
  { file: "ch02-tokens.html", title: "词、编号与分词器", short: "分词", part: "第一部 · 全貌" },
  { file: "ch03-embeddings.html", title: "词嵌入与权重共享", short: "嵌入", part: "第一部 · 全貌" },
  { file: "ch04-rms-norm.html", title: "均方根归一化", short: "归一化", part: "第二部 · 积木" },
  { file: "ch05-attention.html", title: "注意力：查询、键、值", short: "注意力", part: "第二部 · 积木" },
  { file: "ch06-kv-cache.html", title: "因果掩码与键值缓存", short: "KV Cache", part: "第二部 · 积木" },
  { file: "ch07-gqa.html", title: "多头与分组查询注意力", short: "分组查询", part: "第二部 · 积木" },
  { file: "ch08-rope.html", title: "旋转位置编码", short: "位置编码", part: "第二部 · 积木" },
  { file: "ch09-qk-norm.html", title: "查询键归一化与高效计算", short: "QK 归一化", part: "第二部 · 积木" },
  { file: "ch10-swiglu.html", title: "SwiGLU 前馈网络", short: "前馈", part: "第二部 · 积木" },
  { file: "ch11-block.html", title: "一层 Transformer", short: "一层", part: "第三部 · 拼装" },
  { file: "ch12-minimind3.html", title: "拼装 MiniMind-3", short: "Dense 模型", part: "第三部 · 拼装" },
  { file: "ch13-moe.html", title: "拼装 MiniMind-3-MoE", short: "混合专家", part: "第三部 · 拼装" },
  { file: "ch14-pretrain.html", title: "损失、数据与预训练", short: "预训练", part: "第四部 · 训练" },
  { file: "ch15-sft.html", title: "对话模板与监督微调", short: "监督微调", part: "第四部 · 训练" },
  { file: "ch16-generate.html", title: "生成：采样与加速推理", short: "生成", part: "第四部 · 训练" },
  { file: "ch17-beyond.html", title: "LoRA、偏好优化与强化学习", short: "后训练", part: "第四部 · 训练" }
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
  let html = `<a class="rail-brand" href="index.html">从零实现 MiniMind-3</a>
    <p class="rail-sub">手把手教材 · 对齐 2026.04 主线</p>`;
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
