#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BACKEND_PORT=${BACKEND_PORT:-8002}

case "${1:-start}" in
  seed)
    poetry run python ../scripts/seed_db.py
    ;;
  simulate)
    poetry run python ../scripts/simulate_session.py
    ;;
  start|*)
    poetry run uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
    ;;
esac
