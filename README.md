<div align="center">
  <h1>🪟 Insight Monitor</h1>
  <p><strong>Contextual Activity Intelligence</strong></p>
  <p>Monitoring that understands <em>intent</em>, not just apps.</p>
  <hr>
</div>

---

## 📋 Project Status — MVP 14-Day Plan (Jun 15 → Jun 29)

### ✅ Completed

| Day | Date | Key Deliverables | Team |
|:---:|:---:|---|---|
| **1** | Jun 15 | Project scaffold, Pydantic models, Poetry setup, React scaffold, Capture agent skeleton | All |
| **2** | Jun 16 | Window tracker (xdotool/xprop), URL context, SQLite schema + repos, POST/GET events & sessions, E2E test | A, B |
| **3** | Jun 17 | *Pending* | |
| **4** | Jun 18 | *Pending* | |
| **5** | Jun 19 | *Pending — Integration checkpoint* | |
| **6** | Jun 20 | *Pending — Inference pipeline* | |
| **7** | Jun 21 | *Pending — E2E with real LLM* | |
| **8-14** | Jun 22-29 | Dashboard, demo prep | |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Layer 1 — Capture Agent (Python)                        │
│  Runs on user's machine (Linux/Windows)                  │
│  Polls OS APIs: window title, screenshots, input         │
│  Produces RawEvents → POST to local FastAPI              │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP (localhost:8002)
┌────────────────────────▼─────────────────────────────────┐
│  Layer 2 — Backend API (FastAPI + SQLite)                │
│  Receives RawEvents, stores in SQLite                    │
│  SessionBuilder groups events into sessions              │
│  On session close: builds SessionContext                 │
│  Calls Gemini API for intent inference                   │
├────────────────┬──────────────────────┬──────────────────┤
│                │                      │                  │
│         SQLite DB               Gemini 2.0 Flash         │
│    (raw_events,              (multimodal: screenshots    │
│     sessions,                 + text context)            │
│     intent_records)                                      │
└────────────────┬─────────────────────────────────────────┘
                 │ REST API
┌────────────────▼─────────────────────────────────────────┐
│  Layer 3 — Dashboard (React + Vite + TailwindCSS)        │
│  Fetches sessions and intent records via REST            │
│  Displays timeline, classifications, screenshots         │
└──────────────────────────────────────────────────────────┘
```

---

## 🧱 Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Capture Agent** | Python | ≥3.11 | OS-level hooks (xdotool, mss, pynput) |
| **Backend API** | FastAPI | 0.137+ | REST API with automatic OpenAPI docs |
| **Database** | SQLite | — | Zero-config file-based storage |
| **LLM** | Gemini 2.0 Flash | — | Multimodal inference (screenshots + text) |
| **Frontend** | React + TypeScript | 18 / 5 | Dynamic dashboard |
| **Bundler** | Vite | 8.x | Dev server and build tool |
| **Styling** | TailwindCSS | 4.x | Utility-first CSS |
| **Package mgmt** | Poetry | 2.x | Python dependency management |
| **Process mgmt** | concurrently | 10.x | Run backend + frontend in one terminal |

---

## 📁 Project Structure

```
insight-monitor/
│
├── capture/                          # 🟦 Layer 1 — Capture Agent (Python)
│   ├── agent.py                      #   Main loop: polls OS APIs, sends events
│   ├── window_tracker.py             #   xdotool + xprop wrapper (window focus, URL context)
│   ├── screenshot_capture.py         #   mss wrapper (periodic screenshots)
│   ├── input_monitor.py              #   pynput (clicks/min, keystrokes/min, no content)
│   └── event_sender.py               #   HTTP client → POST events to API
│
├── backend/                          # 🟩 Layer 2 — Backend API (Python/FastAPI)
│   ├── backend/
│   │   ├── main.py                   #   FastAPI app entry point
│   │   ├── models/                   #   Pydantic schemas
│   │   │   ├── raw_event.py          #     RawEvent, EventType
│   │   │   ├── session_context.py    #     SessionContext (aggregation)
│   │   │   └── intent_record.py      #     IntentRecord (LLM output)
│   │   ├── storage/
│   │   │   ├── database.py           #     SQLite connection manager (WAL mode, thread-safe)
│   │   │   └── repositories.py       #     CRUD: EventRepo, SessionRepo, IntentRepo
│   │   ├── pipeline/                 #   🔜 SessionBuilder + PromptBuilder + IntentParser
│   │   │   ├── session_builder.py    #     (pending Day 4)
│   │   │   ├── prompt_builder.py     #     (pending Day 6)
│   │   │   └── intent_parser.py      #     (pending Day 6)
│   │   ├── services/
│   │   │   └── llm_service.py        #   🔜 Gemini API client (pending Day 6)
│   │   └── routes/
│   │       ├── health.py             #   GET /health
│   │       ├── events.py             #   POST /events, POST /batch, GET /events
│   │       └── sessions.py           #   GET /sessions, GET /sessions/{id}, intent
│   ├── pyproject.toml                #   Poetry config
│   └── poetry.lock
│
├── dashboard/                        # 🟨 Layer 3 — Frontend (React + Vite + Tailwind)
│   ├── src/
│   │   ├── App.tsx                   #   Main component (session list placeholder)
│   │   ├── main.tsx                  #   Entry point
│   │   └── index.css                 #   TailwindCSS import
│   ├── vite.config.ts                #   Vite + proxy /api → localhost:8002
│   ├── tsconfig.json
│   └── package.json
│
├── scripts/                          # 🛠️ Utility scripts
│   ├── simulate_session.py           #   Generate Riwi/BPO realistic events
│   ├── seed_db.py                    #   Populate SQLite with sample sessions
│   └── run-backend.sh                #   Poetry wrapper (sets PATH, handles port)
│
├── frontend/                         # 📚 Reference: legacy Vanilla JS frontend
│
├── .env.example                      # Environment variables reference
├── .gitignore
├── package.json                      # Root scripts (npm run dev = both services)
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

```bash
python3 --version   # ≥ 3.11
node --version      # ≥ 20
npm --version       # ≥ 9
```

### Install dependencies

```bash
# Python backend
cd ~/Escritorio/insight\ monitor/backend
export PATH="$HOME/.local/bin:$PATH"    # Add poetry to PATH (or add to ~/.bashrc)
poetry install
cd ..

# Dashboard
cd dashboard
npm install
cd ..
```

### Run everything (one terminal)

```bash
cd ~/Escritorio/insight\ monitor
npm run dev
```

| Service | URL | Notes |
|---|---|---|
| Backend API | `http://localhost:8002` | FastAPI with auto-reload |
| Swagger Docs | `http://localhost:8002/docs` | Interactive API documentation |
| Dashboard | `http://localhost:5173` | React dev server, proxies `/api` to backend |

Press **Ctrl+C** to stop all services.

### Load test data

```bash
cd ~/Escritorio/insight\ monitor
npm run seed        # Creates 2 sample sessions in SQLite
npm run simulate    # Sends simulated Riwi/BPO events to the API
```

---

## 🌐 API Reference

All endpoints available at `http://localhost:8002`. Full interactive docs at `/docs`.

### Endpoints

| Method | Path | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Health check + agent status | ✅ |
| `POST` | `/events` | Ingest a single RawEvent | ✅ |
| `POST` | `/events/batch` | Ingest multiple RawEvents | ✅ |
| `GET` | `/events` | List recent events (`?limit=50`) | ✅ |
| `GET` | `/events/session/{id}` | Events for a specific session | ✅ |
| `GET` | `/sessions` | List sessions (`?status=open&limit=50`) | ✅ |
| `GET` | `/sessions/{id}` | Session detail with intent | ✅ |
| `GET` | `/sessions/{id}/intent` | Session intent record only | ✅ |

### Data Models

```python
# RawEvent — atomic unit of captured activity
{
  "event_id": "uuid",
  "event_type": "window_focus|screenshot|input_activity|url_context|session_boundary",
  "timestamp": "2026-06-16T10:00:00Z",
  "source": "capture-agent",
  "window_title": "Visual Studio Code",
  "process_name": "code",
  "pid": 1234,
  "screenshot_path": "/data/screenshots/...png",
  "clicks_per_min": 15.5,
  "keystrokes_per_min": 42.3,
  "url": "https://developer.mozilla.org/..."
}

# SessionContext — aggregated view of a work session
{
  "session_id": "uuid",
  "start_time": "2026-06-16T09:00:00Z",
  "end_time": "2026-06-16T10:30:00Z",
  "duration_seconds": 5400,
  "app_sequence": ["code", "firefox", "discord"],
  "event_count": 47,
  "status": "closed"
}

# IntentRecord — AI inference output with confidence scoring
{
  "record_id": "uuid",
  "session_id": "uuid",
  "session_type": "applied_learning",
  "goal": "Build React component with API integration",
  "goal_confidence": 0.85,
  "friction_points": ["Switched between 3 tabs to find API reference"],
  "category_confidence": 0.78,
  "evidence": ["VS Code open", "MDN docs open"]
}
```

---

## 👥 Team Guide — Continuing Development

### Role A — Capture Agent (Python)

Current state: **Skeleton working, needs Linux testing**

- `capture/agent.py` — Main loop polls OS APIs every 5s, sends typed events
- `capture/window_tracker.py` — Uses `xdotool` + `xprop` for window info + browser tab titles
- `capture/screenshot_capture.py` — `mss` screenshots at configurable interval (default 30s)
- `capture/input_monitor.py` — `pynput` counters for clicks/min and keystrokes/min (no content)

**Next:** Test on real Ubuntu machine, fix Wayland compatibility, run `capture/agent.py` as daemon.

### Role B — Backend API (FastAPI + SQLite)

Current state: **Working with all CRUD routes**

- `backend/backend/main.py` — FastAPI app with CORS, all routers included
- `backend/backend/routes/events.py` — Event ingestion (single + batch) and retrieval
- `backend/backend/routes/sessions.py` — Session listing and detail with intent
- `backend/backend/storage/database.py` — SQLite singleton with WAL mode, thread-safe
- `backend/backend/storage/repositories.py` — Full CRUD for events, sessions, intent_records

**Pending (Day 4-5):** `pipeline/session_builder.py` — group RawEvents into sessions by time gaps.

### Role C — Inference Pipeline (Gemini API)

Current state: **Models defined, pipeline pending**

- `backend/backend/models/` — Pydantic models validated and ready
- `backend/pipeline/session_builder.py` — 🔜 Gap detection (8 min inactivity = session boundary)
- `backend/pipeline/prompt_builder.py` — 🔜 Gemini prompt templates for Riwi mode
- `backend/services/llm_service.py` — 🔜 Gemini API client with retry + error handling
- `backend/pipeline/intent_parser.py` — 🔜 Parse structured JSON from Gemini response

**Start with:** `session_builder.py`, then `llm_service.py`, then `prompt_builder.py` + `intent_parser.py`.

### Role D — Frontend (React + TypeScript + Tailwind)

Current state: **Scaffolded, needs UI components**

- `dashboard/src/App.tsx` — Basic layout (header with agent status, empty session list)
- `dashboard/src/index.css` — TailwindCSS ready
- `dashboard/vite.config.ts` — Proxy `/api` → `localhost:8002`

**Pending (Day 8-10):**
- Session list table with type, duration, confidence
- Session detail view with timeline
- Color-coded confidence badges (green/yellow/red)
- Agent status indicator
- API client module (`dashboard/src/api/`)

---

## 🧪 Testing

### Smoke tests (after `npm run dev`)

```bash
# Health
curl http://localhost:8002/health

# POST event
curl -X POST http://localhost:8002/events \
  -H "Content-Type: application/json" \
  -d '{"event_id":"test-1","event_type":"window_focus","timestamp":"2026-06-16T10:00:00","source":"manual","window_title":"Test","process_name":"bash","pid":999}'

# GET events
curl http://localhost:8002/events?limit=5

# GET sessions
curl http://localhost:8002/sessions
```

### Seed data

```bash
npm run seed      # Populate SQLite with 2 sample sessions
npm run simulate  # Send simulated Riwi + BPO events to API
```

---

## 🧭 MVP Use Cases

### Riwi Learning Environment (Primary Demo)

| Activity | Naive Classification | Insight Monitor |
|---|---|---|
| YouTube tutorial | ❌ Distraction | ✅ Skill development (with IDE + docs) |
| Discord chat | ❌ Distraction | ✅ Peer collaboration (during project) |
| Reading docs | ❌ Low activity | ✅ Research / self-learning |
| ChatGPT | ❌ Cheating | ✅ Learning tool (when for understanding) |

### BPO / Call Center

| Activity | Classification |
|---|---|
| CRM + SAP + softphone | Active customer call |
| Post-call documentation | Task wrap-up |

### Personal Productivity

- Discover focus patterns
- Track progress over weeks
- Full data control — your data stays yours

---

## 🧭 Error Philosophy

> **The cost of a false accusation exceeds the cost of a missed detection.**

| Error | Tolerance | Behavior |
|---|---|---|
| Productive work → marked distraction | Near zero | Default to ambiguous |
| Actual distraction missed | Acceptable | Better unclassified than wrong |
| Sensitive data persisted | Never | Aggressive redaction |

---

## 📚 Docs

Full project documentation and decision records:
**[github.com/insight-monitor/insight-monitor-docs](https://github.com/insight-monitor/insight-monitor-docs)**

### Key documents

| Document | Description |
|---|---|
| [MVP 14-Day Plan](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-14-Day-Plan.md) | Day-by-day execution plan |
| [MVP Definition](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Definition.md) | Core promise and success criteria |
| [MVP Architecture](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Architecture.md) | Technical architecture decisions |
| [MVP Included](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Included.md) | What we're building |
| [MVP Excluded](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Excluded.md) | What we're not building (yet) |
| [MVP Scaling Path](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Scaling-Path.md) | Post-MVP roadmap |
| [Narrative / Founding Story](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/100-NARRATIVE/Founding-Story.md) | Why this project exists |
| [Core Principles](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/100-NARRATIVE/Core-principles.md) | Inviolable design principles |
| [Stance on Surveillance](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/100-NARRATIVE/Stance-on-Surveillance.md) | Ethical foundation |

---

## 📝 Scripts Reference

| Command | Description |
|---|---|
| `npm run dev` | Start backend + dashboard in one terminal |
| `npm run backend` | Start backend only |
| `npm run dashboard:dev` | Start dashboard only |
| `npm run seed` | Load test sessions into SQLite |
| `npm run simulate` | Simulate Riwi/BPO activity events |
| `npm run dashboard:build` | Production build of dashboard |

---

<div align="center">
  <small>Insight Monitor — Private — All rights reserved</small>
</div>
