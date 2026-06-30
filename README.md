# Insight Monitor — Contextual Activity Intelligence

Monitoring that understands *intent*, not just apps.

---

## Quick Start

### Prerequisites

```bash
python3 --version   # >= 3.11
node --version      # >= 20
npm --version       # >= 9
```

### Install dependencies

```bash
cd backend && poetry install && cd ..
cd dashboard && npm install && cd ..
npm install
```

### Run Modes

| Mode | Command | What Runs | Port(s) | Use Case |
|------|---------|-----------|---------|----------|
| **Full stack (dev)** | `npm run dev` | Backend + Dashboard | 8002, 5173 | Daily development |
| **Backend only** | `npm run backend` | FastAPI + auto-reload | 8002 | API work, testing |
| **Frontend only** | `npm run dashboard:dev` | Vite dev server | 5173 | UI work (needs backend running) |
| **Capture agent** | `npm run capture` | Python agent → API | — | Real monitoring (needs backend) |
| **Seed test data** | `npm run seed` | SQLite ← sample sessions | — | Dashboard dev without agent |
| **Simulate events** | `npm run simulate` | HTTP → API → SQLite | — | Test inference pipeline |
| **DB viewer (sqlite-web)** | `cd infrastructure/db-mvp && docker compose up -d` | Web UI for SQLite | 8081 | Browse raw tables, run SQL |

### Database (SQLite) — Auto-Created

The database file `backend/data/insight_monitor.db` is **auto-created** when the backend starts for the first time (via `Database._init_schema()` in `backend/infrastructure/db/sqlite/database.py`). No separate database server is needed.

> **Note**: The `infrastructure/db-mvp/` docker-compose starts **sqlite-web** (a web UI viewer at `http://localhost:8081`), **NOT a database server**. It mounts the existing SQLite file for inspection.

### Load test data

```bash
npm run seed        # Creates sample sessions in SQLite
npm run simulate    # Sends simulated Riwi/BPO events to the API
```

---

## Project Structure

```
├── capture/              Layer 1 — Capture Agent (Python)
│   ├── agent.py          Main loop: polls OS APIs, sends events
│   ├── window_tracker.py xdotool + xprop (window focus, URL context)
│   ├── screenshot_capture.py  mss wrapper (periodic screenshots)
│   ├── input_monitor.py  evdev (clicks/min, keystrokes/min) with pynput fallback
│   └── event_sender.py   HTTP client → POST events to API
│
├── backend/              Layer 2 — Backend API (Clean Architecture)
│   ├── application/      Use Cases (IngestEvent, BuildSessions, InferIntent, GetSession)
│   ├── domain/           Entities (RawEvent, IntentRecord, SessionContext) and Ports (Repository interfaces)
│   ├── infrastructure/   SQLite/InMemory repos, DI Composition Root (di.py), Unit of Work
│   ├── routes/           FastAPI routers (health, events, sessions) using DI
│   ├── pipeline/         Legacy: session builder, inference pipeline, prompt builder, intent parser
│   ├── services/         LLM service (Gemini API client)
│   ├── tests/            Unit tests (InMemory repos) and integration tests
│   ├── config.py         Centralized settings (pydantic-settings)
│   ├── main.py           FastAPI app entry point
│   ├── pyproject.toml
│   └── data/             SQLite database (gitignored)
│
├── dashboard/            Layer 3 — Frontend (React + TypeScript + Vite + TailwindCSS)
│   ├── src/
│   │   ├── App.tsx       Main component
│   │   ├── main.tsx      Entry point
│   │   └── api/          API client + TypeScript types
│   └── vite.config.ts    Dev server on :5173, proxies /api → :8002
│
├── scripts/              simulate_session.py, seed_db.py, run-backend.sh
├── frontend/             ⚠️ LEGACY — AI Support Desk (Vanilla JS, NOT Insight Monitor)
│                         See docs/development/legacy-frontend.md
├── docs/                 Technical documentation
├── .env.example
└── package.json          Root scripts (npm run dev = both services)
```

---

## API Reference

Full interactive docs at `http://localhost:8002/docs`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check + agent status |
| `POST` | `/events` | Ingest a single RawEvent |
| `POST` | `/events/batch` | Ingest multiple RawEvents |
| `GET` | `/events` | List recent events (`?limit=50`) |
| `GET` | `/events/session/{id}` | Events for a specific session |
| `GET` | `/sessions` | List sessions (`?status=open&limit=50`) |
| `GET` | `/sessions/{id}` | Session detail with events + intent |
| `POST` | `/sessions/{id}/close` | Manually close a session |
| `GET` | `/sessions/{id}/intent` | Session intent record only |

---

## Scripts Reference

| Command | Description |
|---|---|
| `npm run dev` | Start backend + dashboard in one terminal |
| `npm run backend` | Start backend only |
| `npm run dashboard:dev` | Start dashboard only |
| `npm run seed` | Load test sessions into SQLite |
| `npm run simulate` | Simulate Riwi/BPO activity events |
| `npm run capture` | Start the capture agent (screenshots + input monitor) |
| `npm run dashboard:build` | Production build of dashboard |
| `npm run generate:types` | Generate TS types from Pydantic models |

---

## Real-Time Monitoring: What You See Where

| Component | Interface | What's Visible | Refresh / Frequency |
|-----------|-----------|----------------|---------------------|
| **Dashboard** | `http://localhost:5173` | Live agent status (green/red), sessions table with: status, start time, duration, event count, apps, inferred type, goal, confidence | Auto-polls every **10 seconds** |
| **Capture Agent** | Terminal (`npm run capture`) | Startup confirmation, each event sent (window_focus, screenshot, input_activity) — logged at INFO level | Continuous (window/input every 5s, screenshot every 30s) |
| **Backend API** | Terminal (`npm run backend`) | Uvicorn access logs (HTTP requests), startup banner | Per request + background task cycles |
| **sqlite-web** | `http://localhost:8081` (after `docker compose up -d` in `infrastructure/db-mvp/`) | Raw tables: `raw_events`, `sessions`, `intent_records` — run SQL, export CSV | Real-time (reads DB file directly) |

### Typical Development Flow
1. **Start backend + dashboard**: `npm run dev` → see dashboard at :5173
2. **Start capture agent**: `npm run capture` (separate terminal) → see events being sent
3. **Watch dashboard**: Sessions appear as agent sends events → session builder groups them → inference runs → type/goal/confidence populate
4. **Debug data**: Open sqlite-web at :8081 to query raw tables

---

## Team Guide

### Capture Agent (Python) — Working (requires X11)
Files: `capture/`. Captures screenshots (`mss`), input frequency (`evdev` with `pynput` fallback on Linux), window focus + browser tabs (`xdotool` + `xprop` on X11 / GNOME extension on Wayland). Sends events to API via HTTP. Configurable via env vars. Requires Linux (X11 and Wayland supported).

### Backend API (FastAPI + SQLite + Clean Architecture) — Working with all CRUD routes + session builder
Files: `backend/`. Includes Clean Architecture layers (Domain, Application, Infrastructure), DI composition root, unit of work for transaction boundaries, background session builder, batch ingest, inference pipeline (LLM service, prompt builder, intent parser), and manual close endpoint.

### Inference Pipeline (Gemini API) — Implemented
Files: `backend/pipeline/` + `backend/services/`. Includes `LLMService` (Gemini API client), `PromptBuilder` (system prompt assembly), `IntentParser` (LLM JSON response parsing), and `InferIntentUseCase` orchestrating all three.

### Frontend (React + TypeScript + Tailwind) — Live health indicator + session list
Files: `dashboard/`. Shows live backend status, session table (status, duration, events, apps). Next: detail view, confidence badges, timeline.

---

## Testing

```bash
# Smoke tests (after npm run dev)
curl http://localhost:8002/health
curl -X POST http://localhost:8002/events \
  -H "Content-Type: application/json" \
  -d '{"event_id":"test-1","event_type":"window_focus","timestamp":"2026-06-16T10:00:00","source":"manual","window_title":"Test","process_name":"bash","pid":999}'
curl http://localhost:8002/events?limit=5
curl http://localhost:8002/sessions
```

---

## Technical Documentation

Architecture, data model, inference framework, API reference, setup guide, and branching strategy live in the **`docs/`** directory:

| Document | Location |
|---|---|
| Architecture | `docs/architecture/README.md` |
| Current state | `docs/architecture/current-state.md` |
| ADR (decisions) | `docs/architecture/adr/` |
| Scaling path | `docs/architecture/scaling-path.md` |
| Error philosophy | `docs/architecture/error-philosophy.md` |
| Data acquisition | `docs/data-model/acquisition.md` |
| Database schema | `docs/data-model/database-schema.md` |
| Inference framework | `docs/inference/` |
| Configuration | `docs/configuration/README.md` |
| API reference | `docs/api/README.md` |
| Capture agent | `docs/capture-agent/README.md` |
| Development setup | `docs/development/setup.md` |
| Git branching | `docs/development/branching.md` |
| Legacy frontend | `docs/development/legacy-frontend.md` |

Non-technical documentation (narrative, use cases, limitations, risks) lives in [insight-monitor-docs](https://github.com/insight-monitor/insight-monitor-docs).