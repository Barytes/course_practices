"""MiniMind-3 手写包。类名、成员名、函数签名对齐 jingyaogong/minimind 的 model_minimind.py。"""

from .config import MiniMindConfig
from .norm import RMSNorm
from .rope import precompute_freqs_cis, apply_rotary_pos_emb, rotate_half
from .attention import Attention, repeat_kv
from .mlp import FeedForward, MOEFeedForward
from .block import MiniMindBlock
from .model import MiniMindModel, MiniMindForCausalLM
from .data import PretrainDataset, SFTDataset

__all__ = [
    "MiniMindConfig",
    "RMSNorm",
    "precompute_freqs_cis",
    "apply_rotary_pos_emb",
    "rotate_half",
    "repeat_kv",
    "Attention",
    "FeedForward",
    "MOEFeedForward",
    "MiniMindBlock",
    "MiniMindModel",
    "MiniMindForCausalLM",
    "PretrainDataset",
    "SFTDataset",
]
