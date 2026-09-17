#!/usr/bin/env bash
# MiniMind-3 单卡预训练 + loss 图 + 续写评测。用 screen 调用，SSH 断开不影响。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RESULT="${ROOT}/train_results"
TRAINER="${ROOT}/trainer"
PYTHON="${PYTHON:-python}"

mkdir -p "${RESULT}" "${ROOT}/out" "${ROOT}/checkpoints"
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false

START_ISO="$(date -Iseconds)"
START_TS="$(date +%s)"

{
  echo "===== MiniMind-3 pretrain start ${START_ISO} ====="
  echo "host=$(hostname)  python=$(command -v "${PYTHON}")"
  "${PYTHON}" - <<'PY'
import torch, platform, os
print("python", platform.python_version())
print("torch", torch.__version__, "cuda", torch.version.cuda)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu", torch.cuda.get_device_name(0), "cap", torch.cuda.get_device_capability(0))
    print("bf16_supported", torch.cuda.is_bf16_supported())
    print("vram_gb", round(torch.cuda.get_device_properties(0).total_mem / 1024**3, 2) if hasattr(torch.cuda.get_device_properties(0), "total_mem") else round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
print("pid", os.getpid())
PY
  nvidia-smi
  echo "data:"
  ls -lh "${ROOT}/dataset/pretrain_t2t_mini.jsonl"
} | tee "${RESULT}/machine_info.txt"

TRAIN_CMD="${PYTHON} -u train_pretrain.py --from_weight none --dtype float16 --num_workers 4"
echo "CMD: ${TRAIN_CMD}" | tee -a "${RESULT}/machine_info.txt"

cd "${TRAINER}"
set +e
${PYTHON} -u train_pretrain.py --from_weight none --dtype float16 --num_workers 4 \
  2>&1 | tee "${RESULT}/train.log"
TRAIN_EXIT=${PIPESTATUS[0]}
set -e

END_ISO="$(date -Iseconds)"
END_TS="$(date +%s)"
DURATION=$((END_TS - START_TS))
echo "===== train finished exit=${TRAIN_EXIT} ${END_ISO} duration=${DURATION}s =====" | tee -a "${RESULT}/train.log"

cd "${ROOT}"
set +e
printf '0\n' | ${PYTHON} -u eval_llm.py --weight pretrain --device cuda --max_new_tokens 256 \
  > "${RESULT}/eval_qa.txt" 2>&1
EVAL_EXIT=$?
set -e
echo "eval_exit=${EVAL_EXIT}" >> "${RESULT}/eval_qa.txt"

${PYTHON} "${ROOT}/scripts/make_pretrain_report.py" \
  --result_dir "${RESULT}" \
  --start_iso "${START_ISO}" \
  --end_iso "${END_ISO}" \
  --duration_sec "${DURATION}" \
  --train_exit "${TRAIN_EXIT}" \
  --eval_file "${RESULT}/eval_qa.txt" \
  --train_cmd "${TRAIN_CMD}" \
  --notes "在 AutoDL 数据盘 /root/autodl-tmp 上训练；screen 会话名 mm。V100 使用 float16。权重未提交 Git。"

echo "DONE train_exit=${TRAIN_EXIT} eval_exit=${EVAL_EXIT} result=${RESULT}"
exit ${TRAIN_EXIT}
