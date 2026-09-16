"""对齐官方 dataset/lm_dataset.py。实现见教材第 14、15 章。"""

from torch.utils.data import Dataset


def pre_processing_chat(conversations, add_system_ratio=0.2):
    ...


def post_processing_chat(prompt_content, empty_think_ratio=0.2):
    ...


class PretrainDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_length=512):
        super().__init__()

    def __len__(self):
        ...

    def __getitem__(self, index):
        ...


class SFTDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length=1024):
        super().__init__()

    def __len__(self):
        ...

    def create_chat_prompt(self, conversations):
        ...

    def generate_labels(self, input_ids):
        ...

    def __getitem__(self, index):
        ...


class DPODataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=4096):
        super().__init__()

    def __len__(self):
        ...

    def generate_loss_mask(self, input_ids):
        ...

    def __getitem__(self, index):
        ...


class RLAIFDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length=1024, thinking_ratio=0.5):
        super().__init__()

    def __len__(self):
        ...

    def create_chat_prompt(self, conversations):
        ...

    def __getitem__(self, index):
        ...


class AgentRLDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length=1024):
        super().__init__()

    def __len__(self):
        ...

    def parse_conversations(self, conversations):
        ...

    def __getitem__(self, index):
        ...


if __name__ == "__main__":
    pass
