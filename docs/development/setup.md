# Development Setup

## Prerequisites

```bash
python3 --version   # >= 3.11
node --version      # >= 20
npm --version       # >= 9
```

## Install dependencies

```bash
# Python backend
cd backend
export PATH="$HOME/.local/bin:$PATH"
poetry install
cd ..

# Dashboard
cd dashboard
npm install
cd ..

# Root (for concurrently)
npm install
```

## Run Modes

| Mode | Command | What Runs | Port(s) | Use Case |
|------|---------|-----------|---------|----------|
| **Full stack (dev)** | `npm run dev` | Backend + Dashboard | 8002, 5173 | Daily development |
| **Backend only** | `npm run backend` | FastAPI + auto-reload | 8002 | API work, testing |
| **Frontend only** | `npm run dashboard:dev` | Vite dev server | 5173 | UI work (needs backend running) |
| **Capture agent** | `npm run capture` | Python agent → API | — | Real monitoring (needs backend) |
| **Seed test data** | `npm run seed` | SQLite ← sample sessions | — | Dashboard dev without agent |
| **Simulate events** | `npm run simulate` | HTTP → API → SQLite | — | Test inference pipeline |
| **DB viewer (sqlite-web)** | `cd infrastructure/db-mvp && docker compose up -d` | Web UI for SQLite | 8081 | Browse raw tables, run SQL |

## Database (SQLite) — Auto-Created

The database file `backend/data/insight_monitor.db` is **auto-created** when the backend starts for the first time (via `Database._init_schema()` in `backend/infrastructure/db/sqlite/database.py`). No separate database server is needed.

> **Note**: The `infrastructure/db-mvp/` docker-compose starts **sqlite-web** (a web UI viewer at `http://localhost:8081`), **NOT a database server**. It mounts the existing SQLite file for inspection.

## Legacy Frontend Notice

⚠️ **Note**: The `frontend/` directory contains a legacy "AI Support Desk" application (Vanilla JS) that is **not part of Insight Monitor**. It is kept for reference only. The current dashboard is in `dashboard/` (React + TypeScript + Tailwind). See [legacy-frontend.md](legacy-frontend.md).

## Load test data

```bash
npm run seed        # Creates sample sessions in SQLite
npm run simulate    # Sends simulated Riwi/BPO events to the API
```

## Scripts reference

| Command | Description |
|---|---|
| `npm run dev` | Start backend + dashboard in one terminal |
| `npm run backend` | Start backend only |
| `npm run dashboard:dev` | Start dashboard only |
| `npm run seed` | Load test sessions into SQLite |
| `npm run simulate` | Simulate Riwi/BPO activity events |
| `npm run dashboard:build` | Production build of dashboard |
| `npm run capture` | Start the capture agent |
| `npm run generate:types` | Generate TS types from Pydantic models |