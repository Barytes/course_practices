"""对齐官方 model/model_lora.py。实现见教材第 17 章。"""

from torch import nn


class LoRA(nn.Module):
    def __init__(self, in_features, out_features, rank):
        super().__init__()
        # self.rank / self.A / self.B

    def forward(self, x):
        ...


def apply_lora(model, rank=16):
    ...


def load_lora(model, path):
    ...


def save_lora(model, path):
    ...


def merge_lora(model, lora_path, save_path):
    ...
