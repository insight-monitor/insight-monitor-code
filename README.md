# Insight Monitor — Contextual Activity Intelligence

Monitoring that understands *intent*, not just apps.

---

## Project Status — MVP 14-Day Plan (Jun 15 → Jun 29)

```
MVP Progress: ████████░░░░░░░░ 4/14 days (28%)
Days: [1][2][3][4] [5] [6] [7] [8─14]
      ✅✅✅✅ 🔜 🔜 🔜 🔜
```

### Day 1 — Jun 15 — Project Scaffold ✅
- Pydantic models (`RawEvent`, `SessionContext`, `IntentRecord`)
- Poetry project setup + FastAPI app skeleton with CORS
- SQLite schema (WAL mode, thread-safe) + CRUD repositories
- React + Vite + TailwindCSS scaffold
- Capture agent skeleton (main loop, event sender)
- Root scripts with concurrently

### Day 2 — Jun 16 — Window Tracking + API Routes ✅
- Window tracker (`xdotool` + `xprop`, browser tab detection, URL extraction)
- `GET /health`, `POST /events`, `GET /events` endpoints
- `GET /sessions`, `GET /sessions/{id}`, `GET /sessions/{id}/intent` endpoints
- Simulate session script (Riwi/BPO realistic events)
- Seed DB script

### Day 3 — Jun 17 — Screenshot + Input Monitor + Batch API ✅
- Screenshot capture (`mss`, configurable interval via env)
- Input frequency monitor (`pynput`: clicks/min, keystrokes/min)
- `POST /events/batch` endpoint
- `GET /sessions` with status filter + limit
- Frontend API client module + live health check indicator
- Capture agent: env var support, graceful shutdown, port fix
- Fix Vite proxy (`/api` rewrite → backend)

### Day 4 — Jun 18 — Session Builder + Close Detection ✅
- Session builder: groups RawEvents by time + inactivity gap (8 min default)
- Auto-close detection (gap > threshold → close), explicit `POST /sessions/{id}/close`
- `GET /sessions/{id}` now includes events array + intent
- Background task runs session builder every 30s
- Frontend session list table (status, duration, events, apps)

### Day 5-14 — Jun 19-29 🔜
- Inference pipeline (LLM service, prompt builder, intent parser)
- Dashboard detail views, confidence badges, timeline
- Unit/integration tests, BPO/Riwi demo scenarios
- Final dry run + stakeholder presentation

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

### Run everything

```bash
npm run dev
```

| Service | URL | Notes |
|---|---|---|
| Backend API | `http://localhost:8002` | FastAPI with auto-reload |
| Swagger Docs | `http://localhost:8002/docs` | Interactive API documentation |
| Dashboard | `http://localhost:5173` | React dev server, proxies `/api` to backend |

### Load test data

```bash
npm run seed        # Creates 2 sample sessions in SQLite
npm run simulate    # Sends simulated Riwi/BPO events to the API
```

---

## Project Structure

```
├── capture/              Layer 1 — Capture Agent (Python)
│   ├── agent.py          Main loop: polls OS APIs, sends events
│   ├── window_tracker.py xdotool + xprop (window focus, URL context)
│   ├── screenshot_capture.py  mss wrapper (periodic screenshots)
│   ├── input_monitor.py  pynput (clicks/min, keystrokes/min)
│   └── event_sender.py   HTTP client → POST events to API
│
├── backend/              Layer 2 — Backend API (Python/FastAPI)
│   ├── backend/
│   │   ├── main.py       FastAPI app entry point
│   │   ├── config.py     Environment-based settings
│   │   ├── models/       Pydantic schemas (RawEvent, SessionContext, IntentRecord)
│   │   ├── storage/      SQLite connection (WAL mode) + CRUD repositories
│   │   ├── pipeline/     Pending: session builder, prompt builder, intent parser
│   │   ├── services/     Pending: LLM service (Gemini API client)
│   │   └── routes/       health, events, sessions
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
├── frontend/             Legacy reference (see docs/development/legacy-frontend.md)
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

---

## Team Guide

### Capture Agent (Python) — Working (requires X11)
Files: `capture/`. Captures screenshots (`mss`), input frequency (`pynput`), window focus + browser tabs (`xdotool` + `xprop`). Sends events to API via HTTP. Configurable via env vars. Requires Linux with X11 (not Wayland).

### Backend API (FastAPI + SQLite) — Working with all CRUD routes + session builder
Files: `backend/backend/`. Includes background session builder (auto-close after inactivity gap), batch ingest, and manual close endpoint.

### Inference Pipeline (Gemini API) — Models defined, pipeline pending
Files: `backend/pipeline/` + `backend/services/`. Next: llm_service, prompt_builder, intent_parser.

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
