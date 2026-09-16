"""对齐 jingyaogong/minimind 的 model/model_minimind.py。

按章往本文件追加，不要拆成 config.py / attention.py。
第 1 章 MiniMindConfig · 第 4 章 RMSNorm · 第 5–9 章 Attention
第 8 章 RoPE · 第 10 / 13 章 FeedForward / MOEFeedForward
第 11 章 MiniMindBlock · 第 3 / 12 / 16 章 MiniMindModel / MiniMindForCausalLM
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import nn
from transformers import GenerationMixin, PreTrainedModel, PretrainedConfig
from transformers.activations import ACT2FN
from transformers.modeling_outputs import MoeCausalLMOutputWithPast


class MiniMindConfig(PretrainedConfig):
    model_type = "minimind"

    def __init__(self, hidden_size=768, num_hidden_layers=8, use_moe=False, **kwargs):
        super().__init__(**kwargs)
        # 代表每个token那个向量的大小，即词嵌入向量的大小
        # 同时也是残差主通道的宽度，层与层之间一直是hidden_size
        self.hidden_size = hidden_size
        # 隐藏层数量：堆了多少个结构相同的 Transformer 块
        # 每个块里包含一个自注意力层和一个前馈层
        # x
        #  ├─ RMSNorm → Attention(GQA) → 加回 x
        #  └─ RMSNorm → FeedForward(SwiGLU / MoE) → 加回 x
        #  → 交给下一层
        # 教材的记法：x ← x + Attention(RMSNorm(x))
        #           x ← x + FeedForward(RMSNorm(x))
        self.num_hidden_layers = num_hidden_layers
        # 是否使用MOE
        self.use_moe = use_moe
        # 丢弃率：每个模块的输出张量里每个元素被置为零的概率
        self.dropout = kwargs.get("dropout", 0.0)
        # 词表的大小
        self.vocab_size = kwargs.get("vocab_size", 6400)
        # begin of sequence 这个token的id
        self.bos_token_id = kwargs.get("bos_token_id", 1)
        # end of sequence 这个token的id
        self.eos_token_id = kwargs.get("eos_token_id", 2)
        # 是否使用flash attention
        self.flash_attn = kwargs.get("flash_attn", True)
        # 注意力头的数量，默认是8
        self.num_attention_heads = kwargs.get("num_attention_heads", 8)
        # K/V头的数量，默认是4
        self.num_key_value_heads = kwargs.get("num_key_value_heads", 4)
        # 一个注意力头的宽度：那个头里的Q/K/V向量的大小，默认是hidden_size//num_attention_heads
        self.head_dim = kwargs.get("head_dim", self.hidden_size // self.num_attention_heads)
        # 激活函数，默认是silu
        self.hidden_act = kwargs.get("hidden_act", "silu")
        # 前馈（MLP/SwiGLU）中间那一维有多宽
        # 注意力进出都是 768。前馈是每个 token 自己先升维、再压回来：768 → intermediate_size → 768
        # 这一维越大，每层「读完之后想」的容量越大，参数也主要花在这里（教材：八层前馈约 45M，注意力约 14M）。
        self.intermediate_size = kwargs.get("intermediate_size", math.ceil(hidden_size * math.pi / 64) * 64)
        # 最多按多少个位置算位置信息：默认 32768，表示配置上最长上下文大约 32k 个 token。
        # MiniMind 不用绝对位置编号表，而是预先算好 RoPE 的 cos/sin，长度就是这个值：precompute_freqs_cis(..., end=32768)。
        # 第 t 个 token 用第 t 个频率，再和 Q/K 旋转。
        self.max_position_embeddings = kwargs.get("max_position_embeddings", 32768)
        # RMSNorm的epsilon，默认是1e-6
        # 归一化系数RMSNorm(x) = sqrt(mean(x^2)+eps)，输出y=(x/RMSNorm(x))*weight，weight是可学习的参数
        # epsilon额外加一个小数，避免分母为零
        self.rms_norm_eps = kwargs.get("rms_norm_eps", 1e-6)
        # ?
        self.rope_theta = kwargs.get("rope_theta", 1e6)
        # 是否共享词嵌入矩阵
        # 词嵌入矩阵将token id映射为词嵌入向量，即从vocab_size维度映射到hidden_size维度
        # 而在LLM输出的最后，需要将hidden_size维度映射回vocab_size维度，即再做一次线性映射
        # 将最后的输出映射回vocab_size的logits（未归一化分数），表示下一个token是哪个token的分数，经过softmax后得到概率
        # 如果tie_word_embeddings为True，则这两个功能使用同一个词嵌入矩阵，减少一份参数
        # 否则，使用两个不同的词嵌入矩阵
        self.tie_word_embeddings = kwargs.get("tie_word_embeddings", True)
        # ？
        self.inference_rope_scaling = kwargs.get("inference_rope_scaling", False)
        # ？
        self.rope_scaling = {
            "beta_fast": 32,
            "beta_slow": 1,
            "factor": 16,
            "original_max_position_embeddings": 2048,
            "attention_factor": 1.0,
            "type": "yarn",
        } if self.inference_rope_scaling else None
        # MoE专家数量
        self.num_experts = kwargs.get("num_experts", 4)
        # 每个token选多少个专家（top-k）
        self.num_experts_per_tok = kwargs.get("num_experts_per_tok", 1)
        # MoE中间层的大小
        self.moe_intermediate_size = kwargs.get("moe_intermediate_size", self.intermediate_size)
        self.norm_topk_prob = kwargs.get("norm_topk_prob", True)
        self.router_aux_loss_coef = kwargs.get("router_aux_loss_coef", 5e-4)


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        # RMSNorm(x) = sqrt(mean(x^2)+eps)，这是一个归一化系数
        # 将x向量中每个分量平方，再将所有分量的平方求平均、开平方
        # 随后再按维度相乘，得到最终的输出：y = (x/RMSNorm(x))*weight
        # x中的每个分量除以归一化系数，得到归一化后的分量，再乘以weight，得到最终的输出
        # weight是可学习的参数，初始化为1，大小跟x的维度相同
        # weight为1时，就等价于x/RMSNorm(x)。
        # 纯 x / rms(x) 会把这个 token 的 768 维钉在「RMS≈1」上，
        # 各维相对大小虽然还在，但整体音量被强制拉齐。
        # 后面的 Attention/FFN 有时需要某几维更响（更重要）、某几维更弱。
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)

    def forward(self, x):
        return (self.weight * self.norm(x.float())).type_as(x)


def precompute_freqs_cis(dim: int, end: int = int(32 * 1024), rope_base: float = 1e6, rope_scaling: dict = None):
    freqs, attn_factor = 1.0 / (rope_base ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim)), 1.0
    if rope_scaling is not None: # YaRN: f'(i) = f(i)((1-γ) + γ/s), where γ∈[0,1] is linear ramp
        orig_max, factor, beta_fast, beta_slow, attn_factor = (
            rope_scaling.get("original_max_position_embeddings", 2048), rope_scaling.get("factor", 16),
            rope_scaling.get("beta_fast", 32.0), rope_scaling.get("beta_slow", 1.0), rope_scaling.get("attention_factor", 1.0)
        )
        if end / orig_max > 1.0:
            inv_dim = lambda b: (dim * math.log(orig_max / (b * 2 * math.pi))) / (2 * math.log(rope_base))
            low, high = max(math.floor(inv_dim(beta_fast)), 0), min(math.ceil(inv_dim(beta_slow)), dim // 2 - 1)
            ramp = torch.clamp((torch.arange(dim // 2, device=freqs.device).float() - low) / max(high - low, 0.001), 0, 1)
            freqs = freqs * (1 - ramp + ramp / factor)
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    freqs_cos = torch.cat([torch.cos(freqs), torch.cos(freqs)], dim=-1) * attn_factor
    freqs_sin = torch.cat([torch.sin(freqs), torch.sin(freqs)], dim=-1) * attn_factor
    return freqs_cos, freqs_sin


def apply_rotary_pos_emb(q, k, cos, sin, unsqueeze_dim=1):
    # 对每个 token、每个头的 96 维 Q/K 做平面旋转（V 不转）。
    # 不是把整张 Q/K 矩阵转一下；也不是 theta = t / 32768 * 360°。
    # 96 维 = 48 对 (x,y)。位置 t 上第 i 对转 t * omega_i 弧度，每对转速不同。
    #
    # Q = 我要找什么，K = 我是谁，都从该 token 的 hidden 投影出来，所以都带语义。
    # 点积 Q·K 才是「关系/匹配分数」。RoPE 只改 Q/K 朝向（长度不变），
    # 让分数同时取决于：内容像不像 × 相对距离合不合适。
    # 真正写进下一层的内容是 V，不转。W_Q/W_K 从一开始就按「后面会转」来学。
    #
    # 若整条向量只转一个角，0° 和 360° 会重叠。这里 48 对转速不同：
    # 快的像秒针（看近处，转几圈正常），慢的像时针（看远处；rope_theta=1e6 让最慢的更慢）。
    # 某一对上距离 5 和 5+一圈可能像；48 个钟不会同时指到同一格。
    # 真正起作用的是两位置的角度差 n-m，不是绝对转到哪。
    def rotate_half(x): return torch.cat((-x[..., x.shape[-1] // 2:], x[..., : x.shape[-1] // 2]), dim=-1)
    q_embed = ((q * cos.unsqueeze(unsqueeze_dim)) + (rotate_half(q) * sin.unsqueeze(unsqueeze_dim))).to(q.dtype)
    k_embed = ((k * cos.unsqueeze(unsqueeze_dim)) + (rotate_half(k) * sin.unsqueeze(unsqueeze_dim))).to(k.dtype)
    return q_embed, k_embed


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    # 输入x：经过投影+view后的K、V，大小是[batch_size, seq_len, num_key_value_heads, head_dim]
    # n_rep：每套K/V复印几份
    # 输出：大小是[batch_size, seq_len, num_key_value_heads * n_rep, head_dim]
    # 即把每套 K/V 向量沿头维复制 n_rep 份，对齐到Q头数
    # 复印的是算出来的 K/V 激活 [B,T,4,96] → [B,T,8,96]，不是把 k_proj 权重复制 8 份
    # 4 个 KV 头仍是 4 组不同权重；只是组内 2 个 Q 共用同一份 K/V 向量（查询不同、索引共享）
    bs, slen, num_key_value_heads, head_dim = x.shape
    if n_rep == 1: return x
    return (x[:, :, :, None, :].expand(bs, slen, num_key_value_heads, n_rep, head_dim).reshape(bs, slen, num_key_value_heads * n_rep, head_dim))


class Attention(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        # 在config里num_attention_heads和num_key_value_heads不同，是实现了Grouped-Query Attention（GQA）这种机制
        # ----Single-Head Attention----
        # Attention(Q,K,V) = softmax(QK^T/sqrt(d_k))V
        # Q = x*WQ, x的大小是[batch_size, seq_len, hidden_size],
        # WQ的大小是[hidden_size, hidden_size], 所以Q的大小是[batch_size, seq_len, hidden_size]
        # 对于一个batch中的seq_len个token向量，它对应的Query向量是hidden_size维的
        # K, V同理，一个token向量对应的Key向量和Value向量大小都是hidden_size维的
        # 在单头注意力中，只有一个Q、一个K、一个V矩阵。
        # x -> Q -> K -> V --> output
        # ----Multi-Head Attention----
        # head_i = Attention(x*WQi, x*WKi, x*WVi), Attention(Q,K,V) = softmax(QK^T/sqrt(d_h))V, d_h=hidden_size/h
        # MHA = Concat(head_1, head_2, ..., head_num_attention_heads) * WO
        # 其中WO是权重矩阵，将所有注意力头输出的拼接映射回hidden_size维度
        # 将num_attention_heads个Attention的输出拼接起来，再做一次线性映射，得到最终的输出。
        # 输入矩阵x的大小是[batch_size, seq_len, hidden_size]
        # 每个attention head中，Q，K，V的大小都是[batch_size, seq_len, hidden_size//num_attention_heads]
        # 拼接后的大小是[batch_size, seq_len, hidden_size]
        # 相当于一个输入x过了多个attention，然后每个attention的输出拼接起来做一个线性变换
        # 那线性变换有什么用呢？类似于加权求和（a1x1+a2x2+...+anxn），把每个头的输出混合起来。
        # 在整个MHA里，Q、K、V矩阵的数量都是一样的，就是num_attention_heads个。
        # x -> Q1 -> K1 -> V1 -|
        #   -> Q2 -> K2 -> V2 --> WO --> output
        #   ...
        #   -> Qn -> Kn -> Vn -|
        # ---- Multi-Query Attention（MQA）----
        # MQA只使用一个K、V头，Q头和MHA一样，但是K、V头是共享的。
        # head_i = Attention(x*WQi, x*WK, x*WV) = softmax(QiK^T/sqrt(d_h))V, d_h=hidden_size/h
        # MQA = Concat(head_1, head_2, ..., head_num_attention_heads) * WO
        # x -> Q1 -|          -> head1  -|
        #   -> Q2 --> K -> V -|-> head2 --> WO --> output
        #   ...   
        #   -> Qn -|          -> headn  -|
        # 显存小：同样上下文长度，K/V 只存一套
        # 解码更快：decode 常被「把 cache 从显存搬到计算单元」卡住，cache 更小，带宽压力更低，token 生成更快。
        # K/V 投影更省：W_K、W_V 从 [d, h·d_h] 变成 [d, d_h]，参数和算量都少一点。
        # 代价是表达力：MHA 里每个 Q 头有自己的 K/V，各查各的；MQA 里 8 个 Q 只能检索同一份索引，质量通常会掉一点。
        # ----Grouped-Query Attention（GQA）----
        # GQA是MHA和MQA的折中：Q头数量仍是h，K/V头数量是n_kv（1 <= n_kv <= h）。
        # 每 n_rep = h / n_kv 个Q头共用一套K、V。MiniMind默认 h=8, n_kv=4, n_rep=2。
        # head_i = Attention(x*WQi, x*WK_{i//n_rep}, x*WV_{i//n_rep}) = softmax(Qi Kg^T/sqrt(d_h)) Vg
        #          其中 g = i // n_rep，d_h = hidden_size / h
        # GQA = Concat(head_1, head_2, ..., head_h) * WO
        # 每个Q头：[B, T, d_h]，共h个；每个K/V头：[B, T, d_h]，只有n_kv套。
        # x -> Q1 -|              -> head1 -|
        #   -> Q2 --> K1 -> V1 -|-> head2 -|
        #   -> Q3 -|              -> head3 -|
        #   -> Q4 --> K2 -> V2 -|-> head4 --> WO --> output
        #   ...
        #   -> Qn -|              -> headn -|
        # n_kv = h 时退回MHA（每套Q独占K/V）；n_kv = 1 时就是MQA（全部Q共用一套K/V）。
        # 优点：KV cache大约是MHA的 n_kv/h（这里4/8=0.5），解码省显存、省带宽。
        # 相对MQA表达力更强：有n_kv套索引，不是所有Q挤着查同一份K/V。

        # --------代码解释--------
        # GQA需要定义的参数: 
        # 1)num_attention_heads: 注意力头的数量（Q头的数量）
        # 2)num_key_value_heads: K/V头的数量，所有Q头使用的K/V头的数量总和
        # 3)n_rep: 每套K/V复印几份（每组里几个Q），n_rep = n_q / n_kv；组数是 n_kv 不是 n_rep
        
        # 定义kv头的数量，如果config里没有指定，则默认和Q头数量相同，即退化成多头注意力
        self.num_key_value_heads = config.num_attention_heads if config.num_key_value_heads is None else config.num_key_value_heads
        # 定义注意力头的数量，即Q头的数量
        self.n_local_heads = config.num_attention_heads
        # 定义kv头的数量，即Q头分多少个组，每组分到一套kv
        self.n_local_kv_heads = self.num_key_value_heads
        # 每套K/V沿头维复制几次，对齐到Q头数；组数=n_kv，组内Q个数=n_rep
        self.n_rep = self.n_local_heads // self.n_local_kv_heads
        # 一个注意力头的宽度：那个头里的Q/K/V向量的大小，默认是hidden_size//num_attention_heads
        self.head_dim = config.head_dim
        # 是否是因果注意力，即只允许看到前面的token，不能看到后面的token
        self.is_causal = True

        # 定义Q投影矩阵
        # 为什么不是直接定义成[hidden_size, head_dim]的形状，然后前向复制8份？
        # 那样得到的是同一份 Q 复印 8 次，不是 8 个查询头。
        # 除非你定义q_proj1, q_proj2, ..., q_proj8，但那样就太麻烦了。
        # 所以直接定义成[hidden_size, num_attention_heads * head_dim]的形状
        # 直接包括了num_attention_heads份不同权重，每份是[hidden_size, head_dim]的形状
        # 然后前向传播时展平(.view()方法)：
        # x:      [B, T, hidden_size]                 # [B, T, 768]
        # Q:      [B, T, n_q * head_dim]              # [B, T, 768]
        # view →  [B, T, n_q, head_dim]               # [B, T, 8, 96]
        self.q_proj = nn.Linear(config.hidden_size, config.num_attention_heads * self.head_dim, bias=False)
        # K/V投影矩阵
        # 定义成[hidden_size, num_key_value_heads * head_dim]的形状
        # k_proj/v_proj里面有num_key_value_heads份不同权重，每份是[hidden_size, head_dim]的形状
        # 然后前向传播时展平(.view()方法)：
        # x:      [B, T, hidden_size]                 # [B, T, 768]
        # K/V:    [B, T, n_kv * head_dim]              # [B, T, 4*96]
        # view →  [B, T, n_kv, head_dim]               # [B, T, 4, 96]
        # view 之后 repeat_kv：把每套 K/V 向量沿头维复制 n_rep=n_q/n_kv 份，对齐到 8 个 Q 头
        # 复印的是算出来的 K/V 激活 [B,T,4,96] → [B,T,8,96]，不是把 k_proj 权重复制 8 份
        # 4 个 KV 头仍是 4 组不同权重；只是组内 2 个 Q 共用同一份 K/V 向量（查询不同、索引共享）
        self.k_proj = nn.Linear(config.hidden_size, config.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(config.hidden_size, config.num_key_value_heads * self.head_dim, bias=False)
        # o投影矩阵：GQA=concat(head_1, head_2, ..., head_num_attention_heads) * WO
        # head_i的大小是[B, T, head_dim]，所以concat后的大小是[B, T, num_attention_heads * head_dim]
        # WO的大小就是[num_attention_heads * head_dim, hidden_size]，将所有注意力头输出的拼接映射回hidden_size维度
        self.o_proj = nn.Linear(config.num_attention_heads * self.head_dim, config.hidden_size, bias=False)

        # QK-Norm 归一化 Q/K
        # RMSNorm在过完Q头和K头之后做，所以dim=self.head_dim
        # q_proj/k_proj 之后、并且 view 成 [B, T, heads, head_dim] 之后
        # 对每个头的 96 维做 RMS
        # 顺序是：投影 → view 成头 → QK-Norm → 再 RoPE
        # 目的是防止QK^T/sqrt(d_h)过大，导致softmax只关注一个位置
        self.q_norm = RMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = RMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)
        self.dropout = config.dropout
        self.flash = hasattr(torch.nn.functional, 'scaled_dot_product_attention') and config.flash_attn

    def forward(self, x, position_embeddings, past_key_value=None, use_cache=False, attention_mask=None):
        # 基础的GQA骨架
        # head_i = Attention(x*WQi, x*WK_{i//n_rep}, x*WV_{i//n_rep}) = softmax(Qi Kg^T/sqrt(d_h)) Vg
        #          其中 g = i // n_rep，d_h = hidden_size / h
        # GQA = concat(head_1, head_2, ..., head_num_attention_heads) * WO
        batch_size, seq_len, _ = x.shape
        # 先投影Q，K，V
        xq, xk, xv = self.q_proj(x), self.k_proj(x), self.v_proj(x)
        # 投影之后view成头
        xq = xq.view(batch_size, seq_len, self.n_local_heads, self.head_dim)
        xk = xk.view(batch_size, seq_len, self.n_local_kv_heads, self.head_dim)
        xv = xv.view(batch_size, seq_len, self.n_local_kv_heads, self.head_dim)
        # qk_norm
        # 为什么先 QK-Norm，再 repeat_kv？
        # k_norm 作用在每个 K 头自己的 head_dim 维上。真正不同的 K 只有 n_local_kv_heads 个.
        # repeat 只是把这 n_local_kv_heads 份向量复印成 n_local_kv_heads*n_rep 份，给 n_local_heads 个 Q 用。
        # 先 norm 再复印：算 n_local_kv_heads 次，n_local_heads*n_rep 份结果两两相同。
        # 先复印再 norm：算 n_local_heads*n_rep 次，结果一样，纯浪费。
        # 更深入的原因是KV cache 必须存 n_local_kv_heads 头，不能存 n_local_heads 头
        # 投影 → view → QK-Norm → RoPE → 把 4 套 K/V 写入 cache → 再 repeat 成 n_local_heads 份去算注意力
        xq, xk = self.q_norm(xq), self.k_norm(xk)

        # RoPE：在注意力之前按位置旋转 Q 和 K（V 不转）
        # 必须先转再拼：新 token 用新位置的 cos/sin；cache 里的旧 K 已经转过，不能再转。
        # 必须先qknorm再RoPE：归一化会按维度重新缩放，把 RoPE 刚安排好的相对角度拧掉。
        cos, sin = position_embeddings
        xq, xk = apply_rotary_pos_emb(xq, xk, cos, sin)

        # KV Cache：把 4 套 K/V 写入 cache
        # 如果kv cache是none，那么x的size就是[batch_size, 从头到尾所有的token序列，hidden_size]。
        # 如果不是none，那么x的size是[batch_size, 新增的token序列，hidden_size]
        # past_key_value是tuple，第一个元素是key，第二个元素是value
        # 其中key的size是[batch_size, 上一轮的seq_len, n_local_kv_heads, head_dim]
        # value的size是[batch_size, 上一轮的seq_len, n_local_kv_heads, head_dim]
        if past_key_value is not None:
            xk = torch.cat([past_key_value[0], xk], dim=1)
            xv = torch.cat([past_key_value[1], xv], dim=1)
        past_kv = (xk, xv) if use_cache else None
        
        # K/V沿头维复制n_rep份
        # 变成了[batch_size, seq_len, n_local_kv_heads * n_rep, head_dim]
        # 为什么要transpose(1, 2)？
        # Q的size是：[batch_size, seq_len, n_local_heads, head_dim]
        # K的size是：[batch_size, seq_len, n_local_kv_heads*n_rep=n_local_heads, head_dim]
        # V同理
        # transpose(1, 2)之后
        # Q的size变成[batch_size, n_local_heads, seq_len, head_dim]
        # K的size变成[batch_size, n_local_heads, seq_len, head_dim]
        # V同理
        # K的转置transpose(-2, -1)之后
        # K的size变成[batch_size, n_local_heads, head_dim, seq_len]
        # 最终QK^T才会形成[batch_size, n_local_heads, seq_len, seq_len]这样token到token的注意力权重矩阵
        xq, xk, xv = (xq.transpose(1, 2), repeat_kv(xk, self.n_rep).transpose(1, 2), repeat_kv(xv, self.n_rep).transpose(1, 2))
        # 手工路径是：显式算出 [B, 头, T, T] 的分数矩阵，再 softmax，再乘 V。
        # T 一大，这张表就是显存杀手。
        # PyTorch 的 scaled_dot_product_attention（常被称作 SDPA）在 GPU 上
        # 会尽量走 Flash Attention 一类内核：
        # 分块计算，不把完整分数矩阵写进显存，数学结果与「缩放点积 + 因果 softmax + 乘 V」相同。
        # 带缓存时查询长度与键长度不等，因果掩码必须是「左边全看见、右下角再上三角」那种不规则形状，
        # 不能简单地 is_causal=True。
        if (self.flash and seq_len > 1 and (not self.is_causal or past_key_value is None)
                and (attention_mask is None or torch.all(attention_mask == 1))):
            output = F.scaled_dot_product_attention(
                xq, xk, xv,
                dropout_p=self.dropout if self.training else 0.0,
                is_causal=self.is_causal,
            )
        else:
            # 算注意力
            # 计算注意力权重：scores = QK^T/sqrt(d_h), 大小[batch_size, n_local_heads, seq_len, seq_len]
            scores = (xq @ xk.transpose(-2, -1)) / math.sqrt(self.head_dim)
            # 因果掩码：注意力权重矩阵中，把i>j的位置都设为-inf，这样softmax之后这些位置的权重都为0
            # 防止当前token看到未来的token
            # scores 形状 [B, heads, T_q, T_k]：行是当前这些 Q，列是所有 K（含 cache 里的历史）。
            # seq_len 是这一次 x 的长度（T_q），不是 cache 总长
            # [:, :, :, -seq_len:] 只切最右边 T_q 列（刚算出来的那一段 K），加上三角 -inf
            # triu(..., diagonal=1)：严格上三角，不含对角线 → 不能看右边的未来，可以看自己。
            # 左边历史列故意不动：decode 时新 Q 必须能看见 cache 里所有旧 K。
            # 无 cache 时 T_q = T_k，-seq_len: 就是整块，等价于普通因果上三角。
            # 有 cache 时例如 T_q=1, T_k=5，右下角是 1×1，上三角为空，新 token 看见全部历史 + 自己。
            # 若 T_q=2, T_k=5：
            #      K0  K1  K2  K3  K4     ← 左三列历史，右两列是本步
            # Q3    ✓   ✓   ✓   ✓   ×     ← 只在右下 2×2 里遮未来
            # Q4    ✓   ✓   ✓   ✓   ✓
            if self.is_causal: 
                scores[:, :, :, -seq_len:] += torch.full((seq_len, seq_len), float("-inf"), device=scores.device).triu(1)
            # padding 掩码（attention_mask）
            # batch 里句子长短不一，短句右边会 pad。
            # attention_mask 一般是 [B, T_k]，1 是真 token，0 是 pad。
            # unsqueeze(1).unsqueeze(2) 
            # 变成 [B, 1, 1, T_k]，加到所有头、所有 Q 上：
            # pad 那些 列 变成 -1e9，谁也不能去attend 填充位。
            # 因果是「同一句里别看后面」；这条是「别看空白」。
            if attention_mask is not None: scores += (1.0 - attention_mask.unsqueeze(1).unsqueeze(2)) * -1e9
            # softmax(QK^T/sqrt(d_h))V
            # 大小[batch_size, n_local_heads, seq_len, head_dim]
            output = F.softmax(scores, dim=-1) @ xv
        # 再reshape成[batch_size, seq_len, hidden_size]
        output = output.transpose(1, 2).reshape(batch_size, seq_len, -1)  # [B, T, 768]
        # o_project的大小是[num_attention_heads * head_dim=hidden_size, hidden_size]
        # 所以output的大小是[batch_size, seq_len, hidden_size]
        output = self.resid_dropout(self.o_proj(output))
        # 返回输出
        return output, past_kv



class FeedForward(nn.Module):
    def __init__(self, config: MiniMindConfig, intermediate_size: int = None):
        super().__init__()
        intermediate_size = intermediate_size or config.intermediate_size
        self.gate_proj = nn.Linear(config.hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, config.hidden_size, bias=False)
        self.up_proj = nn.Linear(config.hidden_size, intermediate_size, bias=False)
        self.act_fn = ACT2FN[config.hidden_act]

    def forward(self, x):
        return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))


class MOEFeedForward(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        # self.config / gate / experts / act_fn / aux_loss

    def forward(self, x):
        ...


class MiniMindBlock(nn.Module):
    def __init__(self, layer_id: int, config: MiniMindConfig):
        super().__init__()
        self.self_attn = Attention(config)
        # 两条岔路各一个 RMSNorm、各学一套 gamma：注意力和前馈需要的尺度可以不同
        self.input_layernorm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        # 稠密改 MoE 只换 mlp，Attention 不用改
        self.mlp = FeedForward(config) if not config.use_moe else MOEFeedForward(config)

    def forward(self, hidden_states, position_embeddings, past_key_value=None, use_cache=False, attention_mask=None):
        # x --> RMSNorm --> Attention-----+--->hidden_states----->RMSNorm-->FeedForward-+->hidden_states
        #    |                            |          |                                  |
        #    -----------------------------|          -----------------------------------|
        # 键值缓存按层分开放：8 层就有 8 份互不相同的 K/V。
        # 进来的 past_key_value 只属于本层；返回的 present_key_value 写回列表第 layer_id 格。
        residual = hidden_states
        hidden_states, present_key_value = self.self_attn(
            self.input_layernorm(hidden_states), position_embeddings,
            past_key_value, use_cache, attention_mask
        )
        hidden_states += residual
        # 第二条残差必须加在「注意力之后的 hidden」上。若加在前馈输入（norm 后、没加过 attn）上，
        # 注意力结果进不了前馈这条岔路，少一截「读完再想」。
        hidden_states = hidden_states + self.mlp(self.post_attention_layernorm(hidden_states))
        return hidden_states, present_key_value


class MiniMindModel(nn.Module):
    # 主干：token id → 嵌入 → 8 层 Block → 最终 RMSNorm。还没有 lm_head。
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        self.config = config
        self.vocab_size, self.num_hidden_layers = config.vocab_size, config.num_hidden_layers
        # [vocab, hidden] 查表：id → 768 维。和 lm_head 可共享同一块权重。
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.dropout = nn.Dropout(config.dropout)
        # 8 个结构相同、权重不同的 MiniMindBlock。l 是 layer_id，给 cache 列表对格用。
        self.layers = nn.ModuleList([MiniMindBlock(l, config) for l in range(self.num_hidden_layers)])
        # 8 层之后、映到词表之前，再拉一次音量
        self.norm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        # RoPE 频率表：dim 必须是 head_dim=96，不是 768。persistent=False 不写进 checkpoint。
        freqs_cos, freqs_sin = precompute_freqs_cis(dim=config.head_dim, end=config.max_position_embeddings, rope_base=config.rope_theta, rope_scaling=config.rope_scaling)
        self.register_buffer("freqs_cos", freqs_cos, persistent=False)
        self.register_buffer("freqs_sin", freqs_sin, persistent=False)

    def forward(self, input_ids, attention_mask=None, past_key_values=None, use_cache=False, **kwargs):
        batch_size, seq_length = input_ids.shape
        # transformers 的 DynamicCache 带 .layers，这里只要「每层一份 (K,V)」的列表
        if hasattr(past_key_values, 'layers'): past_key_values = None
        past_key_values = past_key_values or [None] * len(self.layers)
        # 已缓存的序列长度 = 新 token 真正的位置起点。有 cache 时不能从 0 切 RoPE。
        start_pos = past_key_values[0][0].shape[1] if past_key_values[0] is not None else 0
        hidden_states = self.dropout(self.embed_tokens(input_ids))
        # Recompute RoPE buffers lost during meta-device init (transformers>=5.x)
        if self.freqs_cos[0, 0] == 0:
            freqs_cos, freqs_sin = precompute_freqs_cis(dim=self.config.head_dim, end=self.config.max_position_embeddings, rope_base=self.config.rope_theta, rope_scaling=self.config.rope_scaling)
            self.freqs_cos, self.freqs_sin = freqs_cos.to(hidden_states.device), freqs_sin.to(hidden_states.device)
        # 只取「这一段 input」对应的 cos/sin，例如 decode 一步就是 freqs[start_pos:start_pos+1]
        position_embeddings = (self.freqs_cos[start_pos:start_pos + seq_length], self.freqs_sin[start_pos:start_pos + seq_length])
        presents = []
        # 第 l 层只用 past_key_values[l]，返回的 present 写回 presents[l]
        for layer, past_key_value in zip(self.layers, past_key_values):
            hidden_states, present = layer(
                hidden_states,
                position_embeddings,
                past_key_value=past_key_value,
                use_cache=use_cache,
                attention_mask=attention_mask
            )
            presents.append(present)
        hidden_states = self.norm(hidden_states)
        # 稠密时没有 MOEFeedForward，sum 的初始值 0；MoE 时把各层 aux_loss 加起来
        aux_loss = sum([l.mlp.aux_loss for l in self.layers if isinstance(l.mlp, MOEFeedForward)], hidden_states.new_zeros(1).squeeze())
        return hidden_states, presents, aux_loss


class MiniMindForCausalLM(PreTrainedModel, GenerationMixin):
    config_class = MiniMindConfig
    # 保存/加载时把 lm_head.weight 和 embed_tokens.weight 当成同一份
    _tied_weights_keys = {"lm_head.weight": "model.embed_tokens.weight"}
    def __init__(self, config: MiniMindConfig = None):
        self.config = config or MiniMindConfig()
        super().__init__(self.config)
        self.model = MiniMindModel(self.config)
        # 768 → 6400 个分数（logits，还不是概率）
        self.lm_head = nn.Linear(self.config.hidden_size, self.config.vocab_size, bias=False)
        # 同一块 [vocab, hidden]：查表用它，预测下一个词也用它，省一份参数
        if self.config.tie_word_embeddings: self.model.embed_tokens.weight = self.lm_head.weight
        self.post_init()

    def forward(self, input_ids, attention_mask=None, past_key_values=None, use_cache=False, logits_to_keep=0, labels=None, **kwargs):
        hidden_states, past_key_values, aux_loss = self.model(input_ids, attention_mask, past_key_values, use_cache, **kwargs)
        # logits_to_keep=0 表示整段；生成时常常只要最后几个位置，少算 lm_head
        slice_indices = slice(-logits_to_keep, None) if isinstance(logits_to_keep, int) else logits_to_keep
        logits = self.lm_head(hidden_states[:, slice_indices, :])
        loss = None
        if labels is not None:
            # 错位：位置 t 的 logits 预测的是 labels[t+1]（下一个 token）
            x, y = logits[..., :-1, :].contiguous(), labels[..., 1:].contiguous()
            loss = F.cross_entropy(x.view(-1, x.size(-1)), y.view(-1), ignore_index=-100)
        return MoeCausalLMOutputWithPast(loss=loss, aux_loss=aux_loss, logits=logits, past_key_values=past_key_values, hidden_states=hidden_states)
    
    # https://github.com/jingyaogong/minimind/discussions/611
    @torch.inference_mode()
    def generate(self, inputs=None, attention_mask=None, max_new_tokens=8192, temperature=0.85, top_p=0.85, top_k=50, eos_token_id=2, streamer=None, use_cache=True, num_return_sequences=1, do_sample=True, repetition_penalty=1.0, **kwargs):
        # 接龙：第一轮把 prompt 整段算完填 cache；之后每步只送 1 个新 token。
        input_ids = kwargs.pop("input_ids", inputs).repeat(num_return_sequences, 1)
        attention_mask = attention_mask.repeat(num_return_sequences, 1) if attention_mask is not None else None
        past_key_values = kwargs.pop("past_key_values", None)
        finished = torch.zeros(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
        if streamer: streamer.put(input_ids.cpu())
        for _ in range(max_new_tokens):
            # 有 cache 时只切还没算过的后缀，避免把历史 K/V 再算一遍
            past_len = past_key_values[0][0].shape[1] if past_key_values else 0
            outputs = self.forward(input_ids[:, past_len:], attention_mask, past_key_values, use_cache=use_cache, **kwargs)
            attention_mask = torch.cat([attention_mask, attention_mask.new_ones(attention_mask.shape[0], 1)], -1) if attention_mask is not None else None
            # 只用最后一个位置的 6400 维分数。温度除在 softmax 之前：越小越认死理。
            logits = outputs.logits[:, -1, :] / temperature
            if repetition_penalty != 1.0:
                # 已经出现过的 token：正分压小、负分更负，降低重复
                for i in range(input_ids.shape[0]):
                    seen = torch.unique(input_ids[i]); score = logits[i, seen]; logits[i, seen] = torch.where(score > 0, score / repetition_penalty, score * repetition_penalty)
            if top_k > 0: 
                # 只保留分数最高的 k 个，其余 -inf
                logits[logits < torch.topk(logits, top_k)[0][..., -1, None]] = -float('inf')
            if top_p < 1.0:
                # 按概率从大到小累加，超过 p 的丢掉；mask[...,0]=0 保证至少留最大的那个
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                mask = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1) > top_p
                mask[..., 1:], mask[..., 0] = mask[..., :-1].clone(), 0
                logits[mask.scatter(1, sorted_indices, mask)] = -float('inf')
            next_token = torch.multinomial(torch.softmax(logits, dim=-1), num_samples=1) if do_sample else torch.argmax(logits, dim=-1, keepdim=True)
            if eos_token_id is not None: next_token = torch.where(finished.unsqueeze(-1), next_token.new_full((next_token.shape[0], 1), eos_token_id), next_token)
            input_ids = torch.cat([input_ids, next_token], dim=-1)
            past_key_values = outputs.past_key_values if use_cache else None
            if streamer: streamer.put(next_token.cpu())
            if eos_token_id is not None:
                finished |= next_token.squeeze(-1).eq(eos_token_id)
                if finished.all(): break
        if streamer: streamer.end()
        if kwargs.get("return_kv"): return {'generated_ids': input_ids, 'past_kv': past_key_values}
        return input_ids


if __name__ == "__main__":
    cfg = MiniMindConfig()
    print("head_dim =", cfg.head_dim)
    print("intermediate_size =", cfg.intermediate_size)
