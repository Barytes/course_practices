#!/usr/bin/env bash
# SSH 断开后仍继续：安装依赖 → 预训练 → loss 图 → 续写评测
trap '' HUP
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RESULT="${ROOT}/train_results"
REQ="${ROOT}/requirements.txt"
PYTHON="${PYTHON:-/root/miniconda3/bin/python}"
PIP="${PIP:-/root/miniconda3/bin/pip}"

mkdir -p "${RESULT}" /root/autodl-tmp/pip-tmp
export TMPDIR=/root/autodl-tmp/pip-tmp
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false

status() { echo "[$(date -Iseconds)] $*"; echo "$*" > "${RESULT}/STATUS.txt"; }

status "STEP=pip installing requirements"
"${PIP}" install -r "${REQ}" matplotlib
PIP_EXIT=$?
echo "pip_exit=${PIP_EXIT}" | tee "${RESULT}/pip_exit.txt"
if [ "${PIP_EXIT}" -ne 0 ]; then
  status "STEP=pip FAILED exit=${PIP_EXIT}"
  exit "${PIP_EXIT}"
fi

status "STEP=verify torch/transformers/datasets"
"${PYTHON}" - <<'PY'
import torch, transformers, datasets, matplotlib
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
print("transformers", transformers.__version__)
print("datasets", datasets.__version__)
assert torch.cuda.is_available(), "CUDA not available"
PY
if [ $? -ne 0 ]; then
  status "STEP=verify FAILED"
  exit 1
fi

status "STEP=pretrain"
bash "${ROOT}/scripts/run_pretrain_and_report.sh"
TRAIN_EXIT=$?
status "STEP=done train_exit=${TRAIN_EXIT}"
exit "${TRAIN_EXIT}"
