"""均方根归一化。对齐官方 RMSNorm。实现见教材第 4 章。"""

from __future__ import annotations

import torch
from torch import nn


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        # self.eps
        # self.weight  # nn.Parameter，形状 [dim]，初始全 1

    def norm(self, x: torch.Tensor) -> torch.Tensor:
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...
