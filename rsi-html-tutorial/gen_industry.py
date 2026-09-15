# -*- coding: utf-8 -*-
"""Build industry-catalog.html from Table 12 plus the six in-text case studies."""
from __future__ import annotations

import re
from pathlib import Path

from _gen import FOOT, HEAD, h2, p, work

ROOT = Path(__file__).resolve().parent
TABLE = (ROOT / "table12.md").read_text(encoding="utf-8")

ARCH_LEAD = {
    "A": (
        "A. 前沿大模型与通用智能体实验室",
        "这些公司的主业是底座模型和通用智能体。RSI 只是能力前线之一，不是公司唯一故事。读的时候先看「改的是一次研究任务，还是会留下去的配方 / 评测 / 技能」。",
    ),
    "B": (
        "B. 以 RSI / AI4AI 为公司主题",
        "自我改进、用 AI 做 AI、递归改进，写进了公司或实验室的公开主张。标题很满，证据仍要回到：留下了什么、下一轮是否真用上了改过的改进器。",
    ),
    "C": (
        "C. 自动科研与科学发现",
        "产品是自动做实验、写假设、产知识。RSI 相关性来自「实验环能不能自己转」，不一定来自改改进器。反馈贵、验证难，是这一类的共同卡点。",
    ),
    "D": (
        "D. 智能体优化、评测与学习基础设施",
        "不直接卖「会自己改自己的模型」，而是卖反馈、技能、强化学习环境、评测器、模拟器。没有这些零件，前面几类的环转不起来。",
    ),
    "E": (
        "E. 具身、世界模型与持续适应",
        "持久适应绑在机器人、世界模型、环境或测试时学习上。物理试验贵且可能不可逆，所以「留下什么」常常是政策、世界模型和技能，而不是随手改评测器。",
    ),
    "F": (
        "F. 持久记忆与个人 AI",
        "跨任务记忆、身份或可复用技能是主基底。先问记忆有没有录取门，再问它会不会把错偏好写成长期人格。",
    ),
}

HARD_BY_TAG = [
    ("unverified", "公开材料几乎只有公司名或口号，技术边界还没被第三方核对。不要把融资新闻读成实现。"),
    ("L5", "一旦改的是改进器、评测器或研究政策，分数可能变得不可比，也可能奖励钻空子。结构上「改过的机制被下一轮调用」和有效上「能造出更强后继者」是两件事。"),
    ("L4", "上线反馈会把偶发成功写成长期规则。没有回归评测、权限边界和人审，错经验会进入每一位后续用户。"),
    ("L3", "课程跟着学习者走时，系统可能反复出含糊题、窄题，或强化评测器自己的错。正确性和「对当前模型有用」不是一回事。"),
    ("L2", "目标、预算、录取标准仍是人写的。智能体很会找捷径：挑随机种子、改评测、抽测试标签。公开博客很少展示防黑客层。"),
    ("L1", "说明书错了会规模化复制。技能包和云 API 会过期。看起来全自动，其实步骤、阈值、合并规则仍在人手里。"),
    ("B0", "很强的当场搜索不等于自我改进。任务一结束，搜索树和中间批评通常扔掉。留下的若只是「这道题的答案」，下一题还要从头来。"),
]


def hard_for(tag: str) -> str:
    t = tag.lower()
    for key, msg in HARD_BY_TAG:
        if key.lower() in t:
            return msg
    return "公开细节有限。先用三问：环在哪闭合、留下什么、人还控哪一步。"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return (s or "item")[:80]


EXTRA = {
    "AlphaEvolve": dict(
        problem="在固定题目上搜更好的算法、内核或系统代码。它非常能出成绩，但综述把它标成 B0：搜到的是「这道题的程序」，不是「以后怎么搜程序」的改进器被改写并继承。",
        steps=[
            "人指定问题和评价方式（正确性、速度、业务指标）。",
            "语言模型对现存程序做变异，生成候选代码。",
            "自动评测器在任务专用测试上打分，进化库留下有希望的个体。",
            "最好的程序被用回内部系统（例如训练内核、集群调度）。搜的控制器本身通常保持固定。",
        ],
        impl="公开博客描述的是「LLM + 进化数据库 + 任务评测」。矩阵乘法、数据中心调度等内部成果说明：当评测便宜且客观时，程序搜索可以超过人手调。它没有展示「下一次搜内核时，用的已经是改过的搜索策略」。",
        extra="和 STOP / DGM 对照：那些系统把「改进器源码」当成被改对象。AlphaEvolve 改的是任务程序。",
    ),
    "GPT-Red": dict(
        problem="用自我对打提高模型抗攻击能力：一边生成攻击，一边训练防御，再评价，再打。",
        steps=[
            "攻击策略生成对抗样本或红队策略。",
            "防御侧在这些样本上训练或更新策略。",
            "评价鲁棒性，把结果喂回下一轮攻防。",
            "留下的是红队政策、对抗数据和更硬的防御，不是改「什么叫安全」的总章程。",
        ],
        impl="这是 L2：成功定义（更鲁棒）外部给定，AI 决定下一轮攻击/防御怎么出。技术难点是：训练分布上的攻击 ≠ 真实世界攻击；生成攻击本身有安全与滥用风险，必须隔离。",
    ),
    "Deep Research": dict(
        problem="长时间检索、浏览、综合，给出带证据的研究报告。",
        steps=["拆问题。", "搜索并浏览网页。", "交叉核对。", "写成报告。"],
        impl="综述标 B0：证据和中间笔记主要服务这一次研究任务。会话结束，通常没有把「以后如何做研究」的 harness 改掉并留给下一用户。多智能体研究系统同理。",
    ),
    "Eureka": dict(
        problem="人用自然语言描述机器人要学的技能，模型自己写奖励函数代码，再在仿真里用强化学习练政策。",
        steps=[
            "读任务描述，生成奖励函数 Python 代码。",
            "在 Isaac 一类仿真器里用固定 RL 算法训练。",
            "把训练曲线读回给语言模型，反思后改写奖励。",
            "重复直到政策达标。奖励代码和政策权重留下。",
        ],
        impl="L2：人提供仿真、RL 算法和任务描述；AI 决定奖励写成什么样。奖励黑客很常见——奖励涨了，动作看起来却在投机。ASPIRE 是同一实验室后续的奖励/政策设计线。",
    ),
    "AlphaChip": dict(
        problem="把芯片布局当成可学习政策：放置、打分、学习、把学到的先验迁到新芯片。",
        steps=["把布局状态编码给政策。", "放置并打分。", "强化学习更新。", "迁移到相关芯片。"],
        impl="综述标 L2 相邻：设计政策会学，但「什么叫好的芯片」仍由电子设计自动化指标和人定约束给出。迁移不等于改了布局搜索的元算法。",
    ),
    "AI Co-Scientist": dict(
        problem="用多智能体辩论、排序、精炼来搜科学假设和提案。",
        steps=["生成假设。", "多智能体辩论与打分。", "排序后精炼。", "交给科学家审。"],
        impl="L2 相邻：假设空间里的策略搜索。实验是否真做、如何验收，仍大量在人与实验室一侧。和 HypoForge 那种「改以后如何提假设的技能」不是同一级证据。",
    ),
    "Self-improving tax agents": dict(
        problem="税务生产系统：把从业者纠正变成字段级证据，失败聚成评测，编码智能体在有界表面修产品。",
        steps=[
            "结构化记录人的纠正。",
            "把反复失败聚成评测目标。",
            "智能体查轨迹、评测和仓库，提出补丁。",
            "针对性评测 + 回归 + 人审 PR。不能改架构。",
        ],
        impl="这是正文 Tax AI 案例的产品名。有界 L4：上线反馈进入长期状态，但可编辑面和发布权仍在工程师。详见 papers-l4.html 的 Tax AI 卡和第 8、14 章。",
    ),
    "AIDE2": dict(
        problem="让研究智能体去改研究智能体的 harness，并把通过的版本留给后续研究。",
        steps=["外层用当前 harness 搜更好的 harness。", "用私有分数和成本预算录取。", "另测外层搜索是否因此变快。"],
        impl="正文和第 9 章已展开：100 步 7 次录取；外层改进器效率优势不显著。标 L5 候选，有效性未立。详见 papers-l5.html。",
    ),
    "Darwin Godel Machine": dict(
        problem="开放档案里生长会改自己代码的编码智能体。",
        steps=["按外部规则抽父代。", "自我改代码。", "沙箱跑 SWE-bench / Polyglot。", "有趣则入档。"],
        impl="L5 过渡代表。档案维护和父代选择不在自我修改范围内。详见第 9 章和 papers-l5.html。",
    ),
    "Signals": dict(
        problem="从生产编码智能体的会话里挖失败簇，再开补丁 PR，让产品智能体下次少犯同类错。",
        steps=["采集会话。", "聚类失败。", "生成补丁。", "评测后进入产品。"],
        impl="工业 L4：部署反馈改长期行为。难点是会话隐私、失败归因、以及补丁会不会过拟合内部用户。公开的是产品叙事，不是完整实验协议。",
    ),
    "Agent Skills": dict(
        problem="把可复用的技能、脚本和资源做成智能体可发现、可加载的基底。",
        steps=["把流程写成技能包。", "运行时发现并加载。", "在真实任务里复用。"],
        impl="L1 使能器：没有技能包，L1/L4 的「留下说明书」就没有载体。技能内容仍主要由人写；自动改技能并验收，才靠近 L2/L4。",
    ),
    "When AI builds itself": dict(
        problem="把最强形式的 RSI 说成：AI 自主设计并开发自己的后继者。",
        steps=["公开路线图，而不是一个已发布的自修改仓库。"],
        impl="综述当作 L5 目标而非当前能力。时间表未给。读的时候不要和工作室里已经能改 harness 的有界实验混为一谈。",
    ),
    "R1": dict(
        problem="用可验证奖励和大量自生成推理轨迹，把推理政策从冷启动拉起来。",
        steps=["冷启动或自生成推理。", "用可检查的对错信号做强化学习。", "可选：再蒸馏到小模型。"],
        impl="L2：验题器和训练配方仍是人设计的。Math-V2 把同一思路扩到更强的形式/竞赛数学。它不是 L5，因为改进器（RL 配方、验题器）没有被后轮改写继承。",
    ),
    "R-Zero": dict(
        problem="没有外部答案标签时，用 Challenger–Solver 自博弈出题。",
        steps=["Challenger 出题。", "Solver 多样本作答。", "用一致性构造不确定性奖励。", "伪标签训练 Solver。"],
        impl="和第 7 章、papers-l3.html 是同一条工作。一致性是难度代理，不是正确性。",
    ),
    "Argus": dict(
        problem="长地平线智能体：计划、写代码、审查，并把经验写回，下一次带着环境与记忆继续。",
        steps=["在工作区里计划并执行。", "审查。", "经验写回记忆 / 环境设置。"],
        impl="Theseus 正文案例的产品线。环境是否可验证，决定经验有没有用。和第 14 章的干净工作区实验一起读。",
    ),
    "SetupX": dict(
        problem="专门把「把环境搭到能跑」当成可学习、可写回的对象。",
        steps=["尝试重建环境。", "记录失败。", "把成功设置写回。", "后续任务复用。"],
        impl="综述标 L3：学习者状态进入「下一回环境怎么搭」。工作区噪声实验说明：环境状态能比模型能力更先卡住智能体。",
    ),
    "HyperAgents": dict(
        problem="任务智能体和元智能体的代码都可以改，想把「如何生成智能体」迁到新域。",
        steps=["改任务代码与元代码。", "档案评价。", "迁移时冻结元机制以隔离。"],
        impl="L5 候选。200 次迭代未给出迁移初始化的显著最终优势。详见 papers-l5.html。",
    ),
    "Self-Taught Evaluator": dict(
        problem="让评判模型在合成偏好上自我训练，少依赖昂贵的人类偏好标注。",
        steps=["生成候选。", "模型当判官。", "用结果再训判官。", "迭代。"],
        impl="L2：判官变强了，但「什么叫好」的种子信号和迭代协议仍外部。判官与被评模型同族时，会一起漂。这是第 9 章 RQGM 要处理的问题的工业前身。",
    ),
    "autoresearch": dict(
        problem="固定数据、评价和预算，智能体只改训练程序，指标变好才留下。",
        steps=["编辑 train.py。", "受预算训练。", "读验证指标。", "变好则保留。"],
        impl="第 6 章教学标本。Karpathy 公开仓库可核对。Wen 等人报告过自动研究里的评测利用，读的时候要一起看。",
    ),
    "Skill optimization loop": dict(
        problem="从编码智能体的反馈里重写技能、指令和例子，再评价是否更好。",
        steps=["挖失败反馈。", "重写技能。", "用内部评测录取。"],
        impl="工业 L2：技能文件是可编辑状态，成功定义仍是人的评测。和 Foundry Agent Optimizer、Dropbox+GEPA 同类。",
    ),
}


FEATURED = [
    work(
        "feat-theseus",
        "Theseus（正文案例）",
        "环境–数据–模型共演化 · 见第 14 章",
        "L2–L3 现场",
        "前提：环境让知识可访问、动作可验证；任务执行产生学习证据；更强模型扩大能探索的问题。每一轮应给后续轮贡献可复用能力。",
        [
            "把 refinement 经验变成环境 refinement 任务，训练环境模型。",
            "智能体在重建环境里找真正难点，生成针对性训练数据。",
            "这些数据训练任务模型。",
            "更强模型支持下一轮环境和任务生成。",
        ],
        "干净工作区通过率 +21.7–51.6 个百分点；带 Collection Map + Event Log 的重建环境量规 +18.65–39.67 个百分点。这是共演化的第一步，不是完整环已经转起来。",
        "必须把「桌子收拾干净」和「人变聪明」分开量。范围蔓延说明环境变丰富也会诱导过度动作。",
        "环境制品、验证模块、任务数据。",
        "共演化日程、量规、完整学习周期是否启动。",
        extra="产品线在表中对应 Argus、SetupX。",
    ),
    work(
        "feat-lark",
        "Lark / 飞书（正文案例）",
        "企业数据底座 · 第 14 章",
        "L1–L2 数据环",
        "智能体要改进自己，先要有不断演化的数据基底。企业里文档、消息、会议持续产生新信息。",
        [
            "构造企业知识图谱（实体、事件、人、时间），并检查授权。",
            "绝对判断丢掉明显不可用输出，再用 GSB 比较决定是否晋升。",
            "失败归因到时间不一致、查询被扭曲、源质量差等，映射到具体改进。",
            "人定义标准、审关键样本、批重要变更。",
        ],
        "相对 RAG 基线，人评可用性 52%→65%，自动评 47%→56%。自动评委与人约 84% 一致，分歧多半因为自动评委更严。",
        "图谱错误会直接传进答案。时间敏感问题必须按查询时过滤，避免用到未来信息。",
        "图谱、评价标准、归因后的数据。",
        "标准、关键样本、重要变更。",
    ),
    work(
        "feat-humanlaya",
        "Humanlaya（正文案例）",
        "交付驱动的数据质检 RSI · 第 14 章",
        "有界 L4 / 外环 L5 苗头",
        "生产单元是复杂多文件任务包。内环修当前批次，外环改质检系统自己。",
        [
            "Quality Checker → Refiner → Delivery Checker 修当前包。",
            "交付后汇总审查、客户反馈、下游使用。",
            "对质检系统提出带版本的修改，在未参与产生该修改的包上评价，加人审再晋升。",
        ],
        "V0→V4：关键缺陷包 9.0%→3.7%，人工 48→27 分钟。扫描 PDF 案例：把抽取失败误当成文档质量差，于是新规则进入下一版本。",
        "外环改的是质检器，已经碰到「改进机制」；人仍握最终批准。留出评价必须真的没参与产生该修改。",
        "带版本的质检指令、技能、few-shot。",
        "人审与最终发布。",
    ),
    work(
        "feat-modelbest",
        "ModelBest / Forge 工程（正文案例）",
        "工业 AI 工程自动化 · 第 14 章",
        "L2 工程搜索",
        "实现训练框架、优化内核、配并行，执行反馈相对客观，可能比开放式研究更早自治。",
        [
            "人和 AI 维护含规格、评价、经验的知识库。",
            "智能体建立高层架构后进入 AutoResearch：实现、测正确性与性能、修瓶颈。",
            "成功内核并入主路径；经验写回知识库给下一项目。",
        ],
        "ForgeTrain：约 8 小时匹配 Megatron-LM v0.15；MiniCPM4 MFU 有公开公司数字。ForgeStencil 把方法扩到科学计算内核。",
        "对比的「工程师月」是估算。知识库质量决定搜索空间。这是公司报告，不是独立复现的 L5。",
        "训练框架 / 内核代码 + 知识库。",
        "规格、评价、架构约束。",
    ),
    work(
        "feat-hyra",
        "腾讯混元 Hyra（正文案例）",
        "经验驱动搜索 · 第 14 章",
        "L2；评测器 refinement 碰到 L5 问题",
        "不把人手工作流写死，而给宽解空间，用实验证据指导下一次搜索。Experience Bank 存代码、日志、分数、评测器反馈。",
        [
            "Context Agent 重组灵感上下文。",
            "多个 Proposal Agent 在隔离沙箱里构造新解。",
            "结果写回银行。",
            "若评测器不完整或被利用，可用积累经验修订评价机制再继续搜。",
        ],
        "nanochat 验证 BPB 0.9015 vs 0.9109；nanoGPT Speedrun 76.4s vs 77.5s；SOL-ExecBench 0.771 vs 0.754。",
        "公开材料没有 RQGM 那么明确的独立锚。修订评测器后旧分如何作废、如何重评，是你要追问的。",
        "经验银行 + 可能被修订的评测机制。",
        "停止规则、预算、评测器治理是否独立。",
    ),
    work(
        "feat-ara",
        "Agent-Native Research Lab / ARA（正文案例）",
        "可验证研究文物 · 第 14 章",
        "研究基础设施",
        "后继智能体需要失败实验、中间证据、可执行规格，而不是只给人看的论文。",
        [
            "ARA 同时保留科学逻辑、代码、探索图、原始证据。",
            "rit 协议把声称锚到执行轨迹，从日志重新抽取结果。",
            "分析声称可用 Lean 4 等检查。只有过门的声称进入共享研究状态。",
        ],
        "对先前工作问答 93.7% vs 论文 72.4%；RE-Bench 复现 57.4%→64.4%。硅设计实例用工业 EDA 做可综合验证。",
        "形式验证不能证明规格表达了人真正想要的能力。保密数据下只能部分重放。",
        "可继承研究文物。",
        "验证门、哪些声称可以进共享状态。",
    ),
]


def parse_table(md: str):
    arch = None
    company = ""
    rows = []
    for raw in md.splitlines():
        if not raw.startswith("|"):
            continue
        cells = [c.strip() for c in raw.split("|")]
        # leading/trailing empties from the surrounding pipes
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if not cells:
            continue
        if cells[0].startswith("Company"):
            continue
        m = re.match(r"^([A-F])\.\s+(.+)$", cells[0])
        if m and (len(cells) == 1 or (len(cells) > 1 and not cells[1])):
            arch = m.group(1)
            continue
        if len(cells) < 6:
            continue
        co, product, sub, target, ai, tag = cells[:6]
        link = ""
        last = cells[-1] if cells else ""
        mlink = re.search(r"\((https://[^)]+)\)", raw)
        if mlink:
            link = mlink.group(1)
        if co:
            company = co
        rows.append(
            dict(
                arch=arch or "A",
                company=company,
                product=product,
                sub=sub,
                target=target,
                ai=ai,
                tag=tag,
                link=link,
            )
        )
    return rows


def card(row: dict) -> str:
    product = row["product"]
    company = row["company"]
    tag = row["tag"]
    extra = EXTRA.get(product, {})
    url = row["link"]
    meta = f"{esc(company)} · 公开快照 2026-09"
    if url:
        meta += f" · <a href='{esc(url)}'>来源</a>"
    star = "公开身份或技术边界仍待更强核对。" if "*" in company else ""
    problem = extra.get(
        "problem",
        f"{esc(company)} 的「{esc(product)}」放在「{esc(row['sub'])}」里。"
        f"要动的制品主要是：{esc(row['target'])}。"
        f"AI 被公开写成会做：{esc(row['ai'])}。"
        + (" " + star if star else "")
        + " 多数条目没有开源仓库，下面的步骤是把公开字段翻译成改进环，便于和 B0–L5 对照，而不是内部实现的逐行复现。",
    )
    if extra.get("steps"):
        steps = extra["steps"]
    else:
        bits = [b.strip() for b in row["ai"].split(";") if b.strip()]
        if not bits:
            bits = ["按公开材料执行该产品所声称的动作"]
        steps = [f"公开材料写明这一步由 AI 做：{esc(b)}。" for b in bits]
        steps.append("把结果写进「改进对象」列出的制品。下一任务能不能看见，要看 RSI 标签，不要看产品名里有没有 self-improve。")
        steps.append("人通常仍握产品方向、发布权和评测口径；公开博客很少把「每一次迭代的否决权」写清楚。")
    impl = extra.get(
        "impl",
        "把这一行当成现场索引：先看改进对象和 AI 控哪一段，再跳到正文或第五部里同名的学术系统（若有）。"
        "「cand.」= 看起来像这一级但证据不足；「adj.」= 相邻基础设施；「target」= 明确的未来目标而不是已展示能力。",
    )
    keep_ai = esc(row["target"])
    keep_h = "目标、权限、发布、评测口径（公开材料未证明已交出）。"
    if "undisclosed" in row["target"].lower() or "unverified" in tag.lower():
        impl = "几乎没有可核对的技术描述。教程保留这一行，只为了地图完整，不当作实现证据。"
        steps = ["公开来源无法列出实现步骤。", "等待可审计的技术报告或代码后再对照三问。"]
        keep_ai = "未披露。"
        keep_h = "全部未知。"
    return work(
        slug(company + "-" + product),
        f"{esc(product)}",
        meta,
        tag,
        problem,
        steps,
        impl,
        extra.get("hard") or hard_for(tag),
        keep_ai,
        keep_h,
        extra=extra.get("extra", ""),
    )


def main():
    rows = parse_table(TABLE)
    companies = {r["company"] for r in rows}
    body = []
    body.append(
        p(
            f"综述 Appendix B Table 12：按公司类型（不是按国家）排列，一行一个产品或代表工作。"
            f"解析得到 <strong>{len(rows)}</strong> 条产品行、约 <strong>{len(companies)}</strong> 家公司/团队。"
            f"RSI 标签是映射到本教程的 B0–L5，不是公司自己的官方自称。"
            f"带 * 的条目，综述自己说身份或技术边界还要更强核对。"
        )
    )
    body.append(h2("正文里展开的六家（比表更细）"))
    body.append(
        p(
            "第 14 章的 Theseus、Lark、Humanlaya、ModelBest、Hyra、ARA，有的在表里只有产品名，有的根本不在 72 家里。"
            "下面先把这六家的实现环再摊一次，再进入完整地图。"
        )
    )
    body.extend(FEATURED)

    last_arch = None
    for row in rows:
        if row["arch"] != last_arch:
            title, lead = ARCH_LEAD.get(row["arch"], (row["arch"], ""))
            body.append(h2(title))
            body.append(p(lead))
            last_arch = row["arch"]
        body.append(card(row))

    wrap_body = "".join(body)
    html = HEAD.format(
        title="附录：工业地图里的公司与产品",
        kicker="第五部 · 每篇工作",
        h1="72 家公司与产品：公开快照怎么读",
        lead="一张表想告诉你：自我改进已经从论文走进产品名。真正有用的读法仍然是三问。标签旁的 cand. / adj. / target 比口号重要。",
        box="上方六家来自综述正文，有数字和方法。下方按 Table 12 原表展开。用搜索框找公司或产品。Exploit / 红队类条目只写评测含义，不写攻击步骤。",
    )
    out = ROOT / "industry-catalog.html"
    out.write_text(html + wrap_body + FOOT, encoding="utf-8")
    print("wrote", out, "rows", len(rows), "companies", len(companies), "bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
