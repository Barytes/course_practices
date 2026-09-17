#!/usr/bin/env python3
"""Parse pretrain logs, plot loss, and write a training report."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

LOG_RE = re.compile(
    r"Epoch:\[(\d+)/(\d+)\]\((\d+)/(\d+)\), loss: ([\d.]+), "
    r"logits_loss: ([\d.]+), aux_loss: ([\d.]+), lr: ([\d.eE+-]+), "
    r"epoch_time: ([\d.]+)min"
)


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:  # noqa: BLE001
        return f"(unavailable: {exc})"


def parse_log(log_path: Path) -> list[dict]:
    rows = []
    global_step = 0
    if not log_path.exists():
        return rows
    for line in log_path.read_text(errors="replace").splitlines():
        m = LOG_RE.search(line)
        if not m:
            continue
        global_step += 1
        rows.append(
            {
                "global_step": global_step,
                "epoch": int(m.group(1)),
                "epochs": int(m.group(2)),
                "step": int(m.group(3)),
                "iters": int(m.group(4)),
                "loss": float(m.group(5)),
                "logits_loss": float(m.group(6)),
                "aux_loss": float(m.group(7)),
                "lr": float(m.group(8)),
                "epoch_eta_min": float(m.group(9)),
            }
        )
    return rows


def plot_loss(rows: list[dict], png_path: Path) -> None:
    import matplotlib.pyplot as plt

    xs = [r["global_step"] for r in rows]
    ys = [r["loss"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, ys, color="#2563eb", linewidth=1.4)
    ax.set_xlabel("log step (every log_interval)")
    ax.set_ylabel("loss")
    ax.set_title("MiniMind-3 pretrain loss")
    ax.grid(True, alpha=0.3)
    if ys:
        ax.annotate(
            f"start {ys[0]:.3f}\nend {ys[-1]:.3f}",
            xy=(xs[-1], ys[-1]),
            xytext=(-80, 30),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="#111827"),
            fontsize=9,
        )
    fig.tight_layout()
    fig.savefig(png_path, dpi=140)
    plt.close(fig)


def write_csv(rows: list[dict], csv_path: Path) -> None:
    if not rows:
        csv_path.write_text("global_step,epoch,step,loss,logits_loss,aux_loss,lr\n")
        return
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "global_step",
                "epoch",
                "epochs",
                "step",
                "iters",
                "loss",
                "logits_loss",
                "aux_loss",
                "lr",
                "epoch_eta_min",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", required=True)
    parser.add_argument("--start_iso", default="")
    parser.add_argument("--end_iso", default="")
    parser.add_argument("--duration_sec", type=int, default=0)
    parser.add_argument("--train_exit", type=int, default=0)
    parser.add_argument("--eval_file", default="")
    parser.add_argument("--train_cmd", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    rows = parse_log(result_dir / "train.log")
    write_csv(rows, result_dir / "loss.csv")
    if rows:
        plot_loss(rows, result_dir / "loss.png")

    try:
        import torch

        torch_ver = torch.__version__
        cuda_ok = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda_ok else "N/A"
        cuda_ver = torch.version.cuda
        cap = torch.cuda.get_device_capability(0) if cuda_ok else None
        bf16 = torch.cuda.is_bf16_supported() if cuda_ok else False
    except Exception as exc:  # noqa: BLE001
        torch_ver = f"unavailable ({exc})"
        cuda_ok = False
        gpu_name = "N/A"
        cuda_ver = "N/A"
        cap = None
        bf16 = False

    nproc = os.cpu_count() or "unknown"
    mem = run(["bash", "-lc", "free -h | awk '/Mem:/ {print $2}'"])
    disk = run(["bash", "-lc", "df -h /root/autodl-tmp / | awk 'NR==1 || /autodl-tmp/ || /overlay/'"])
    nvidia = run(["nvidia-smi", "-L"])
    driver = run(
        [
            "bash",
            "-lc",
            "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader",
        ]
    )

    first_loss = rows[0]["loss"] if rows else None
    last_loss = rows[-1]["loss"] if rows else None
    duration = args.duration_sec
    h, rem = divmod(duration, 3600)
    m, s = divmod(rem, 60)

    eval_text = ""
    if args.eval_file and Path(args.eval_file).exists():
        eval_text = Path(args.eval_file).read_text(errors="replace")

    md = []
    md.append("# MiniMind-3 预训练结果")
    md.append("")
    md.append(f"- 生成时间：{dt.datetime.now().isoformat(timespec='seconds')}")
    md.append(f"- 训练开始：{args.start_iso or 'N/A'}")
    md.append(f"- 训练结束：{args.end_iso or 'N/A'}")
    md.append(f"- 训练耗时：{h}h {m}m {s}s（{duration} 秒）")
    md.append(f"- 训练进程退出码：{args.train_exit}")
    md.append("")
    md.append("## 机器与软件")
    md.append("")
    md.append(f"- 主机名：{platform.node()}")
    md.append(f"- 系统：{platform.platform()}")
    md.append(f"- Python：{platform.python_version()} ({sys.executable})")
    md.append(f"- CPU 逻辑核数：{nproc}")
    md.append(f"- 内存：{mem}")
    md.append(f"- GPU：{gpu_name}")
    md.append(f"- nvidia-smi：`{driver}`")
    md.append(f"- GPU 列表：{nvidia}")
    md.append(f"- PyTorch：{torch_ver}")
    md.append(f"- CUDA（PyTorch 编译）：{cuda_ver}；`torch.cuda.is_available()`={cuda_ok}")
    md.append(f"- Compute capability：{cap}；`is_bf16_supported()`={bf16}")
    md.append("- 数据盘：`/root/autodl-tmp`（AutoDL 数据盘）")
    md.append("")
    md.append("```")
    md.append(disk)
    md.append("```")
    md.append("")
    md.append("## 训练配置")
    md.append("")
    md.append("单卡预训练，命令：")
    md.append("")
    md.append("```bash")
    md.append(args.train_cmd or "python train_pretrain.py --from_weight none")
    md.append("```")
    md.append("")
    md.append("主要超参（与 `train_pretrain.py` 默认值一致，除非下面单独说明）：")
    md.append("")
    md.append("- `--from_weight none`：从头训练")
    md.append("- `epochs=2`")
    md.append("- `hidden_size=768`，`num_hidden_layers=8`")
    md.append("- `batch_size=32`，`accumulation_steps=8`（等效全局 batch 256）")
    md.append("- `max_seq_len=340`")
    md.append("- `learning_rate=5e-4`，cosine 调度（见 `get_lr`）")
    md.append("- `dtype=float16`：Tesla V100 无原生 BF16，未使用脚本默认的 `bfloat16`")
    md.append("- `num_workers=4`：降低 DataLoader 进程占用")
    md.append("- 数据：`minimind3/dataset/pretrain_t2t_mini.jsonl`")
    md.append("- 权重输出：`minimind3/out/pretrain_768.pth`（体积大，未纳入 Git）")
    md.append("")
    if args.notes:
        md.append("### 备注")
        md.append("")
        md.append(args.notes)
        md.append("")
    md.append("## Loss")
    md.append("")
    if first_loss is None:
        md.append("日志中没有解析到 loss 行，请查看 `train.log`。")
    else:
        md.append(f"- 记录点数：{len(rows)}")
        md.append(f"- 起始 loss：{first_loss:.4f}")
        md.append(f"- 结束 loss：{last_loss:.4f}")
        md.append(f"- 最后一步：epoch {rows[-1]['epoch']}/{rows[-1]['epochs']} step {rows[-1]['step']}/{rows[-1]['iters']}")
        md.append("")
        md.append("曲线见同目录 `loss.png`，数值见 `loss.csv`。")
        md.append("")
        md.append("![pretrain loss](loss.png)")
    md.append("")
    md.append("## 测试续写 / 问答")
    md.append("")
    md.append("预训练模型主要做续写，不是对齐后的问答。下面是 `eval_llm.py` 自动测试输出。")
    md.append("")
    md.append("```")
    md.append(eval_text.strip() or "(no eval output)")
    md.append("```")
    md.append("")

    (result_dir / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {result_dir / 'REPORT.md'}  points={len(rows)}")


if __name__ == "__main__":
    main()
