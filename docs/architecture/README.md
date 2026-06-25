---
title: MVP Architecture
type: reference
domain: architecture
priority: critical
status: accepted
version: 2.0.0
---

# MVP Architecture

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────┐
│  Layer 1 — Capture Agent (Python)                   │
│  Runs on user's machine (Linux)                     │
│  Polls OS APIs: window title, screenshots, input    │
│  Produces RawEvents → POST to local FastAPI         │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP (localhost:8002)
┌───────────────────────▼─────────────────────────────┐
│  Layer 2 — Backend API (FastAPI + Clean Arch)       │
│  Routes call Use Cases (Application Layer)          │
│  BuildSessionsUseCase groups events into sessions   │
│  InferIntentUseCase calls Gemini API for intent     │
│  Repositories (Infrastructure Layer) persist data   │
└──────────────┬──────────────────────┬───────────────┘
               │                     │
               ▼                     ▼
        SQLite DB              Gemini 2.0 Flash
    (raw_events,               (multimodal:
     sessions,                  screenshots +
     intent_records)            text context)
               │
               │ REST API
┌──────────────▼──────────────────────────────────────┐
│  Layer 3 — Dashboard (React + Vite + TailwindCSS)   │
│  Fetches sessions and intent records via REST       │
│  Displays timeline, classifications, screenshots    │
└─────────────────────────────────────────────────────┘
```

## Technology Choices

| Layer | Technology | Justification |
|---|---|---|
| Capture agent | Python 3.11+ | Best ecosystem for OS-level hooks (`xdotool`, `pynput`, `mss`) |
| Backend API | FastAPI + Uvicorn | Fast to build, Pydantic integration, automatic OpenAPI docs |
| Database | SQLite | Zero-config, file-based, sufficient for single-user MVP |
| LLM | Gemini 2.0 Flash | Native multimodal, cheapest API, 1M token context |
| Frontend | React + TypeScript + Vite | Fast dev experience, strong typing |
| Styling | TailwindCSS 4.x | Utility-first CSS without overhead |
| Package management | Poetry 2.x | Dependency management + virtualenv in one tool |

## Platform Support

| Platform | MVP Support | Status |
|---|---|---|
| Linux (Ubuntu 20.04/22.04) | **Primary target** | Full support with `xdotool`, `xprop` |
| Windows 10/11 | Not in MVP | `pywin32` as conditional fallback for post-MVP |
| macOS | Not supported | Excluded from MVP scope |

## Key Design Decisions

### Why SQLite over LanceDB/PostgreSQL
SQLite requires no server process, no Docker container, zero configuration. For a single-user MVP where sessions number in the hundreds, SQLite is faster and simpler.

### Why synchronous inference instead of Celery/Redis
The inference pipeline runs once per session close, not continuously. Synchronous execution keeps the architecture simple and removes two infrastructure dependencies (Redis + Celery worker).

### Why Gemini over Claude
Gemini 2.0 Flash provides native multimodal support (screenshots + text in one API call) at significantly lower cost than Claude or GPT-4o. Google's free tier ($0.15/1M input tokens) allows extensive testing during development.

### Why tab titles over full URLs
Reading Chrome's SQLite database is unreliable on Linux (locked files, Snap/Flatpak isolation). The window title from `xdotool` provides sufficient page-level context for the LLM to infer intent. A browser extension for full URL capture can be added post-MVP.

## Directory Structure

```
insight-monitor/
├── capture/                    # Layer 1 — Capture agent
│   ├── agent.py                # Main loop: poll OS APIs
│   ├── window_tracker.py       # xdotool wrapper
│   ├── screenshot_capture.py   # mss wrapper
│   ├── input_monitor.py        # pynput frequency capture
│   └── event_sender.py         # POST RawEvents to API
│
├── backend/                    # Layer 2 — API + Storage (Clean Architecture)
│   ├── application/            # Application Layer
│   │   └── use_cases/          # IngestEvent, BuildSessions, InferIntent, GetSession
│   ├── domain/                 # Domain Layer
│   │   ├── entities/           # RawEvent, SessionContext, IntentRecord
│   │   └── ports/              # Repository interfaces
│   ├── infrastructure/         # Infrastructure Layer
│   │   ├── db/                 # SQLite and InMemory implementations
│   │   └── di.py               # Dependency Injection Composition Root
│   ├── routes/                 # Presentation Layer
│   │   ├── events.py           # POST/GET /events, /events/batch, /events/session/{id}
│   │   ├── sessions.py         # GET /sessions, /sessions/{id}, /sessions/{id}/intent, POST /sessions/{id}/close
│   │   └── health.py           # GET /health
│   ├── pipeline/               # Legacy: session builder, inference pipeline, prompt builder, intent parser
│   ├── services/               # LLM service (Gemini API client)
│   ├── main.py                 # FastAPI app entry point
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── data/                   # SQLite database (gitignored)
│
├── dashboard/                  # Layer 3 — Frontend
│   ├── src/
│   │   ├── App.tsx             # Main component
│   │   ├── main.tsx            # Entry point
│   │   ├── index.css           # TailwindCSS import
│   │   └── api/                # API client + TypeScript types
│   ├── vite.config.ts          # Vite + proxy /api → localhost:8002
│   └── package.json
│
├── scripts/
│   ├── simulate_session.py     # Generate test data
│   ├── seed_db.py              # Populate sample sessions
│   └── run-backend.sh          # Poetry wrapper
│
├── frontend/                   # Legacy reference (see docs/development/legacy-frontend.md)
├── docs/                       # Technical documentation
├── .env.example
├── package.json
└── README.md
```

## Architecture Documentation

| Document | Description |
|---|---|
| `current-state.md` | Honest assessment of the current architecture after ARCH-0 restructuring |
| `adr/` | Architecture Decision Records — historical record of key decisions |
| `scaling-path.md` | Post-MVP roadmap and architecture decisions that survive scaling |
| `error-philosophy.md` | Error handling principles and classification philosophy |

## Port Reference

| Service | Port | Notes |
|---|---|---|
| Backend API | `8002` | Configurable via `BACKEND_PORT` env var |
| Dashboard dev server | `5173` | Proxies `/api` → backend at `8002` |
| Swagger docs | `8002/docs` | Auto-generated by FastAPI |
