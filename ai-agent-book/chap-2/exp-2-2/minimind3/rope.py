"""旋转位置编码。对齐官方 precompute_freqs_cis / apply_rotary_pos_emb。实现见教材第 8 章。"""

from __future__ import annotations

import torch


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """官方写在 apply_rotary_pos_emb 内部；教学上单独列出。"""
    ...


def apply_rotary_pos_emb(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    unsqueeze_dim: int = 1,
) -> tuple[torch.Tensor, torch.Tensor]:
    ...


def precompute_freqs_cis(
    dim: int,
    end: int = 32 * 1024,
    rope_base: float = 1e6,
    rope_scaling: dict | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    ...
