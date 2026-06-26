#!/usr/bin/env bash
export BACKEND_PORT=${BACKEND_PORT:-8002}
export PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd):$PYTHONPATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-start}" in
  seed)
    python3 "$ROOT/scripts/seed_db.py"
    ;;
  simulate)
    python3 "$ROOT/scripts/simulate_session.py"
    ;;
  start|*)
    python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
    ;;
esac
