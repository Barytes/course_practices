"""对齐官方 trainer/rollout_engine.py。实现见教材第 17 章。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from torch import Tensor


def compute_per_token_logps(model, input_ids: Tensor, n_keep: int, attention_mask: Optional[Tensor] = None) -> Tensor:
    ...


@dataclass
class RolloutResult:
    output_ids: Tensor
    completion_ids: Tensor
    per_token_logps: Tensor
    completions: List[str]
    prompt_lens: Tensor
    completion_mask: Tensor


class RolloutEngine(ABC):
    tokenizer = None

    @abstractmethod
    def rollout(self, prompt_ids: Tensor, attention_mask: Tensor, num_generations: int, max_new_tokens: int, temperature: float = 0.8) -> RolloutResult:
        ...

    @abstractmethod
    def update_policy(self, model):
        ...


class TorchRolloutEngine(RolloutEngine):
    def __init__(self, policy_model, tokenizer, device: str = "cuda", autocast_ctx=None):
        ...

    def rollout(self, prompt_ids: Tensor, attention_mask: Tensor, num_generations: int, max_new_tokens: int, temperature: float = 0.8) -> RolloutResult:
        ...

    def update_policy(self, model):
        ...


class SGLangRolloutEngine(RolloutEngine):
    def __init__(self, base_url: str, model_path: str, shared_ckpt_path: str = "./sglang_ckpt", timeout: int = 120):
        ...

    def rollout(self, prompt_ids: Tensor, attention_mask: Tensor, num_generations: int, max_new_tokens: int, temperature: float = 0.8) -> RolloutResult:
        ...

    def update_policy(self, model):
        ...

    def flush_cache(self) -> bool:
        ...

    def health(self) -> bool:
        ...


def create_rollout_engine(
    engine_type: str = "torch",
    policy_model=None,
    tokenizer=None,
    device: str = "cuda",
    autocast_ctx=None,
    sglang_base_url: str = None,
    sglang_model_path: str = None,
    sglang_shared_path: str = None,
) -> RolloutEngine:
    ...
