"""对齐官方 trainer/trainer_utils.py。"""

def get_model_params(model, config):
    ...


def is_main_process():
    ...


def Logger(content):
    ...


def get_lr(current_step, total_steps, lr):
    ...


def init_distributed_mode():
    ...


def setup_seed(seed: int):
    ...


def lm_checkpoint(lm_config, weight="full_sft", model=None, optimizer=None, epoch=0, step=0, wandb=None, save_dir="../checkpoints", **kwargs):
    ...


def init_model(lm_config, from_weight="pretrain", tokenizer_path="../model", save_dir="../out", device="cuda"):
    ...


class SkipBatchSampler:
    def __init__(self, sampler, batch_size, skip_batches=0):
        ...

    def __iter__(self):
        ...

    def __len__(self):
        ...


class LMForRewardModel:
    def __init__(self, model_path, device="cuda", dtype=None):
        ...

    def get_score(self, messages, response):
        ...


def safe_math_eval(expression):
    ...
