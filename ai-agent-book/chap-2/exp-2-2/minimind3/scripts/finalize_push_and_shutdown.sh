#!/usr/bin/env bash
# 等预训练报告写完 → 提交推送 → 成功后关机。SSH 断开不影响。
trap '' HUP
set -uo pipefail

ROOT="/root/autodl-tmp/course_practices"
MM="${ROOT}/ai-agent-book/chap-2/exp-2-2/minimind3"
RESULT="${MM}/train_results"
LOG="${RESULT}/finalize.log"
STATUS="${RESULT}/STATUS.txt"
REPORT="${RESULT}/REPORT.md"

mkdir -p "${RESULT}"
exec >>"${LOG}" 2>&1

say() {
  echo "[$(date -Iseconds)] $*"
  echo "$*" > "${STATUS}.finalize"
}

say "STEP=waiting_for_report pid=$$"

while [ ! -f "${REPORT}" ]; do
  now="$(cat "${STATUS}" 2>/dev/null || true)"
  case "${now}" in
    STEP=pip\ FAILED*|STEP=verify\ FAILED*)
      say "STEP=aborted because ${now}"
      exit 1
      ;;
  esac
  sleep 30
done

say "STEP=report_found waiting_for_train_exit"
# 报告写完后 run_pretrain 还会很快退出；再等主训练进程消失
for i in $(seq 1 60); do
  if ! pgrep -f "python -u train_pretrain.py" >/dev/null 2>&1 \
     && ! pgrep -f "eval_llm.py" >/dev/null 2>&1; then
    break
  fi
  sleep 10
done
sleep 5

say "STEP=git_commit"
cd "${ROOT}"
git add .gitignore \
  ai-agent-book/chap-2/exp-2-2/minimind3/scripts/bootstrap_install_and_train.sh \
  ai-agent-book/chap-2/exp-2-2/minimind3/scripts/run_pretrain_and_report.sh \
  ai-agent-book/chap-2/exp-2-2/minimind3/scripts/make_pretrain_report.py \
  ai-agent-book/chap-2/exp-2-2/minimind3/scripts/finalize_push_and_shutdown.sh \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/REPORT.md \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/loss.png \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/loss.csv \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/eval_qa.txt \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/machine_info.txt \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/train.log \
  ai-agent-book/chap-2/exp-2-2/minimind3/train_results/STATUS.txt \
  || true

if git diff --cached --quiet; then
  say "STEP=nothing_to_commit trying_push"
else
  git -c user.name="Barytes" -c user.email="975255330@qq.com" commit -m "$(cat <<'EOF'
Add MiniMind-3 pretrain results from AutoDL V100.

Record machine config, wall time, loss curve, and continuation eval; keep weights and jsonl data off git.
EOF
)"
fi

say "STEP=git_push"
export GIT_TERMINAL_PROMPT=0
git remote set-url origin git@github.com:Barytes/course_practices.git
export GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
if timeout 180 git push origin HEAD; then
  say "STEP=push_ok shutting_down"
  sync
  sleep 3
  shutdown -h now
  exit 0
fi

say "STEP=push_failed instance_kept_running"
echo "git push failed; not shutting down. See ${LOG}"
exit 2
