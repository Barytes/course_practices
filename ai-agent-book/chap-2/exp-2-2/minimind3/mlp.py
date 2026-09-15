"""前馈与混合专家。对齐官方 FeedForward / MOEFeedForward。实现见教材第 10、13 章。"""

from __future__ import annotations

import torch
from torch import nn

from .config import MiniMindConfig


class FeedForward(nn.Module):
    def __init__(self, config: MiniMindConfig, intermediate_size: int | None = None):
        super().__init__()
        # self.gate_proj  # hidden -> intermediate，无 bias
        # self.up_proj    # hidden -> intermediate，无 bias
        # self.down_proj  # intermediate -> hidden，无 bias
        # self.act_fn     # 官方用 ACT2FN[config.hidden_act]，教学可用 F.silu

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...


class MOEFeedForward(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        # self.config
        # self.gate     # hidden -> num_experts，无 bias
        # self.experts  # nn.ModuleList[FeedForward]，长度 num_experts
        # self.act_fn
        # self.aux_loss  # forward 里写入

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...
