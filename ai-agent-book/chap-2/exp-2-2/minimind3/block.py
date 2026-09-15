"""一层 Transformer。对齐官方 MiniMindBlock。实现见教材第 11 章。"""

from __future__ import annotations

import torch
from torch import nn

from .config import MiniMindConfig


class MiniMindBlock(nn.Module):
    def __init__(self, layer_id: int, config: MiniMindConfig):
        super().__init__()
        # self.self_attn                 # Attention
        # self.input_layernorm           # RMSNorm(hidden_size)
        # self.post_attention_layernorm  # RMSNorm(hidden_size)
        # self.mlp                       # FeedForward 或 MOEFeedForward

    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        past_key_value: tuple[torch.Tensor, torch.Tensor] | None = None,
        use_cache: bool = False,
        attention_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor] | None]:
        ...
