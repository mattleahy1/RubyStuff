#!/usr/bin/env bash
# Job Search Agent runner — safe to call from cron or manually
# Usage:
#   ./run_job_search.sh              # Full daily search
#   ./run_job_search.sh --dry-run    # Test connectivity, skip Claude
#   ./run_job_search.sh --top 20     # Show top stored results
#   ./run_job_search.sh --report     # Regenerate report

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/job_search_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

# ── Environment ──────────────────────────────────────────────────────────────
# Load ANTHROPIC_API_KEY from .env if present and not already exported
if [[ -f "$SCRIPT_DIR/.env" ]] && [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  # shellcheck disable=SC1091
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "  Option 1: export ANTHROPIC_API_KEY=sk-ant-..."
  echo "  Option 2: create $SCRIPT_DIR/.env containing ANTHROPIC_API_KEY=sk-ant-..."
  exit 1
fi

# ── Python venv ──────────────────────────────────────────────────────────────
VENV="$SCRIPT_DIR/.venv"
if [[ ! -d "$VENV" ]]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
fi

PYTHON="$VENV/bin/python"

# ── Run ──────────────────────────────────────────────────────────────────────
echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting job search agent" | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
"$PYTHON" -m job_search.agent "$@" 2>&1 | tee -a "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') — Done" | tee -a "$LOG_FILE"
