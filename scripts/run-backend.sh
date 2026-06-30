#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export BACKEND_PORT=${BACKEND_PORT:-8002}

cd "$BACKEND_DIR"

case "${1:-start}" in
  seed)
    poetry run python "$REPO_ROOT/scripts/seed_db.py"
    ;;
  simulate)
    poetry run python "$REPO_ROOT/scripts/simulate_session.py"
    ;;
  start|*)
    poetry run uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
    ;;
esac
