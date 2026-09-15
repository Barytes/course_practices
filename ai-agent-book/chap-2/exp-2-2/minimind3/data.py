"""数据。对齐官方 dataset/lm_dataset.py。实现见教材第 14、15 章。"""

from __future__ import annotations

from torch.utils.data import Dataset


def pre_processing_chat(conversations, add_system_ratio: float = 0.2):
    ...


def post_processing_chat(prompt_content, empty_think_ratio: float = 0.2):
    ...


class PretrainDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_length: int = 512):
        super().__init__()
        # self.tokenizer / self.max_length / self.samples

    def __len__(self) -> int:
        ...

    def __getitem__(self, index: int):
        """返回 (input_ids, labels)，pad 位置 labels 为 -100。"""
        ...


class SFTDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length: int = 1024):
        super().__init__()
        # self.tokenizer / self.max_length / self.samples
        # self.bos_id  # tokenizer(f'{bos}assistant\\n')
        # self.eos_id  # tokenizer(f'{eos}\\n')

    def __len__(self) -> int:
        ...

    def create_chat_prompt(self, conversations) -> str:
        ...

    def generate_labels(self, input_ids: list[int]) -> list[int]:
        ...

    def __getitem__(self, index: int):
        ...


class DPODataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length: int = 4096):
        super().__init__()

    def __len__(self) -> int:
        ...

    def generate_loss_mask(self, input_ids: list[int]) -> list[int]:
        ...

    def __getitem__(self, index: int) -> dict:
        ...


class RLAIFDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length: int = 1024, thinking_ratio: float = 0.5):
        super().__init__()

    def __len__(self) -> int:
        ...

    def create_chat_prompt(self, conversations) -> str:
        ...

    def __getitem__(self, index: int) -> dict:
        ...


class AgentRLDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length: int = 1024):
        super().__init__()

    def __len__(self) -> int:
        ...

    def parse_conversations(self, conversations):
        ...

    def __getitem__(self, index: int) -> dict:
        ...
