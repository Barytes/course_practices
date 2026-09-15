import math
from dataclasses import dataclass

@dataclass
class MiniMindConfig:
    hidden_size: int = 768
    num_hidden_layers: int = 8
    vocab_size: int = 6400
    num_attention_heads: int = 8
    num_key_value_heads: int = 4
    max_position_embeddings: int = 32768
    rms_norm_eps: float = 1e-6
    rope_theta: float = 1e6
    hidden_act: str = "silu"
    dropout: float = 0.0
    flash_attn: bool = True
    tie_word_embeddings: bool = True
    use_moe: bool = False
    num_experts: int = 4
    num_experts_per_tok: int = 1
    router_aux_loss_coef: float = 5e-4
    norm_topk_prob: bool = True
    inference_rope_scaling: bool = False
    rope_scaling: dict | None = None

    def __post_init__(self):
        assert self.hidden_size % self.num_attention_heads == 0
        assert self.num_attention_heads % self.num_key_value_heads == 0
        self.head_dim = self.hidden_size // self.num_attention_heads
        # 官方：math.ceil(hidden_size * math.pi / 64) * 64
        self.intermediate_size = math.ceil(self.hidden_size * math.pi / 64) * 64
        self.moe_intermediate_size = self.intermediate_size
        if self.inference_rope_scaling and self.rope_scaling is None:
            self.rope_scaling = {
                "type": "yarn", "factor": 16,
                "original_max_position_embeddings": 2048,
                "beta_fast": 32, "beta_slow": 1, "attention_factor": 1.0,
            }

if __name__ == "__main__":
    cfg = MiniMindConfig()
    print("head_dim =", cfg.head_dim)            # 96
    print("intermediate_size =", cfg.intermediate_size)  # 2432
    print("每个查询头共用的键值头重复倍数 =",
          cfg.num_attention_heads // cfg.num_key_value_heads)  # 2
