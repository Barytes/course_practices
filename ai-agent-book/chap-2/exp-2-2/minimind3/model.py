"""整网。对齐官方 MiniMindModel / MiniMindForCausalLM。实现见教材第 3、12、16 章。"""

from __future__ import annotations

import torch
from torch import nn

from .config import MiniMindConfig


class MiniMindModel(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        # self.config
        # self.vocab_size / self.num_hidden_layers
        # self.embed_tokens  # nn.Embedding(vocab_size, hidden_size)
        # self.dropout
        # self.layers        # nn.ModuleList[MiniMindBlock]
        # self.norm          # RMSNorm(hidden_size)
        # self.freqs_cos / self.freqs_sin  # register_buffer，persistent=False

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        past_key_values: list | None = None,
        use_cache: bool = False,
        **kwargs,
    ) -> tuple[torch.Tensor, list, torch.Tensor]:
        """返回 hidden_states, presents, aux_loss。"""
        ...


class MiniMindForCausalLM(nn.Module):
    """官方还继承 PreTrainedModel, GenerationMixin；教学版用 nn.Module 即可。"""

    def __init__(self, config: MiniMindConfig | None = None):
        super().__init__()
        # self.config
        # self.model     # MiniMindModel
        # self.lm_head   # Linear(hidden_size, vocab_size, bias=False)
        # tie_word_embeddings 时：embed_tokens.weight = lm_head.weight

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        past_key_values: list | None = None,
        use_cache: bool = False,
        logits_to_keep: int = 0,
        labels: torch.Tensor | None = None,
        **kwargs,
    ):
        """官方返回 MoeCausalLMOutputWithPast；教学版可返回 (loss, aux_loss, logits, past_key_values)。"""
        ...

    @torch.inference_mode()
    def generate(
        self,
        inputs: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        max_new_tokens: int = 8192,
        temperature: float = 0.85,
        top_p: float = 0.85,
        top_k: int = 50,
        eos_token_id: int = 2,
        streamer=None,
        use_cache: bool = True,
        num_return_sequences: int = 1,
        do_sample: bool = True,
        repetition_penalty: float = 1.0,
        **kwargs,
    ) -> torch.Tensor:
        """实现见教材第 16 章。官方写在本类里，不要另开 generate.py。"""
        ...

class EmbedAndHead(nn.Module):
    def __init__(self, config: MiniMindConfig):
        super().__init__()
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        if config.tie_word_embeddings:
            self.embed_tokens.weight = self.lm_head.weight
        self.drop = nn.Dropout(config.dropout)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        hidden = self.drop(self.embed_tokens(input_ids))
        return self.head(hidden)