"""注意力。对齐官方 repeat_kv 与 Attention。实现见教材第 5–9 章。"""

from __future__ import annotations

import torch
from torch import nn

from .config import MiniMindConfig


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    """x: [batch, seq, num_key_value_heads, head_dim] -> 头维重复 n_rep 次。"""
    ...


class Attention(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        # self.num_key_value_heads
        # self.n_local_heads
        # self.n_local_kv_heads
        # self.n_rep
        # self.head_dim
        # self.is_causal
        # self.q_proj / k_proj / v_proj / o_proj   # 均无 bias
        # self.q_norm / k_norm                     # RMSNorm(head_dim)
        # self.attn_dropout / resid_dropout / dropout
        # self.flash

    def forward(
        self,
        x: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        past_key_value: tuple[torch.Tensor, torch.Tensor] | None = None,
        use_cache: bool = False,
        attention_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor] | None]:
        ...
