<div align="center">
  <h1>Insight Monitor</h1>
  <p><strong>Contextual Activity Intelligence</strong></p>
  <p>Monitoring that understands <em>intent</em>, not just apps.</p>
</div>

---

## Overview

Insight Monitor is a full-stack system that collects endpoint activity data and uses **multimodal AI** to infer task context, work relevance, and probable user intent. Unlike traditional monitoring tools that classify by application or domain name (e.g., "YouTube = distraction"), Insight Monitor evaluates context — combining window titles, screenshots, input patterns, and temporal sequences — to produce **probabilistic, evidence-based classifications**.

### Core Philosophy

- **Transparency.** What is collected, why, and what is inferred — all visible to the monitored person.
- **Challengeability.** Every conclusion has an evidence trace and can be disputed.
- **Uncertainty as a feature.** Every inference carries a confidence score (0.0–1.0). The system reports what it does not know.
- **Individual benefit.** The monitored person must gain from the system's presence.
- **No false binaries.** Nothing is "productive" or "unproductive" in absolute terms — always contextual.

### Key Differentiator

| Approach | Example | Result |
|---|---|---|
| Naive monitoring | YouTube open → | Marked as distraction |
| Insight Monitor | YouTube + VS Code + MDN docs → | Classified as **work-relevant research** (confidence: 0.85) |
| Insight Monitor | YouTube + full-screen entertainment + no input → | Classified as **personal / probable break** |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Layer 1 — Capture Agent (Python)                        │
│  Runs on user's machine (Linux/Windows)                  │
│  Polls OS APIs: window title, screenshots, input         │
│  Produces RawEvents → POST to local FastAPI              │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP (localhost:8000)
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
│                │                                         │
│                │ REST API                                │
┌────────────────▼─────────────────────────────────────────┐
│  Layer 3 — Dashboard (React + Vite + TailwindCSS)        │
│  Fetches sessions and intent records via REST            │
│  Displays timeline, classifications, screenshots         │
└──────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Capture Agent** | Python 3.11+ | OS-level hooks for window tracking, screenshots, input monitoring |
| **Backend API** | FastAPI + Uvicorn | REST API with automatic OpenAPI docs |
| **Database** | SQLite | Zero-config, file-based storage |
| **LLM** | Gemini 2.0 Flash | Native multimodal inference (screenshots + text) |
| **Frontend** | React 18 + TypeScript | Dynamic dashboard with real-time updates |
| **Bundler** | Vite | Fast dev server and build tool |
| **Styling** | TailwindCSS | Utility-first CSS framework |

---

## Project Structure

```
insight-monitor/
├── capture/                        # Layer 1 — Capture agent
│   ├── agent.py                    # Main loop: poll OS APIs, send events
│   ├── window_tracker.py           # xdotool/xprop wrapper for window focus
│   ├── screenshot_capture.py       # mss wrapper for periodic screenshots
│   ├── input_monitor.py            # pynput-based input frequency capture
│   └── event_sender.py             # HTTP client for POSTing events to API
│
├── backend/                        # Layer 2 — API + Storage
│   ├── backend/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── models/                 # Pydantic schemas
│   │   │   ├── raw_event.py        # RawEvent, EventType enums
│   │   │   ├── session_context.py  # Session aggregation model
│   │   │   └── intent_record.py    # LLM inference output model
│   │   ├── storage/
│   │   │   ├── database.py         # SQLite connection manager
│   │   │   └── repositories.py     # CRUD for events, sessions, intents
│   │   ├── pipeline/               # Session building + inference
│   │   │   ├── session_builder.py  # Groups RawEvents into sessions
│   │   │   ├── prompt_builder.py   # Builds Gemini prompt with context
│   │   │   └── intent_parser.py    # Parses Gemini JSON response
│   │   ├── services/
│   │   │   └── llm_service.py      # Gemini API client
│   │   └── routes/
│   │       ├── health.py           # GET /health
│   │       ├── events.py           # POST /events, GET /events
│   │       └── sessions.py         # GET /sessions, GET /sessions/{id}
│   ├── pyproject.toml              # Poetry project configuration
│   └── poetry.lock
│
├── dashboard/                      # Layer 3 — Frontend
│   ├── src/
│   │   ├── App.tsx                 # Main application component
│   │   ├── main.tsx                # Entry point
│   │   └── index.css               # TailwindCSS imports
│   ├── vite.config.ts              # Vite config with proxy to backend
│   ├── tsconfig.json               # TypeScript configuration
│   └── package.json                # npm dependencies
│
├── scripts/
│   ├── simulate_session.py         # Generate realistic BPO/Riwi test data
│   └── seed_db.py                  # Populate SQLite with sample sessions
│
├── frontend/                       # Reference: legacy Vanilla JS frontend
├── .env.example                    # Environment variable reference
├── .gitignore
├── README.md
└── package.json                    # Root npm scripts
```

---

## API Reference

The backend provides a REST API with automatic OpenAPI documentation at `http://localhost:8000/docs`.

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check and agent status |
| `POST` | `/events` | Ingest a single RawEvent |
| `POST` | `/events/batch` | Ingest multiple RawEvents |
| `GET` | `/events` | List recent events |
| `GET` | `/events/session/{id}` | List events for a session |
| `GET` | `/sessions` | List sessions (optional status filter) |
| `GET` | `/sessions/{id}` | Session detail with intent |
| `GET` | `/sessions/{id}/intent` | Session intent record only |

### Data Models

**RawEvent** — the atomic unit of captured activity:
```json
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
```

**SessionContext** — aggregated view of a work session:
```json
{
  "session_id": "uuid",
  "start_time": "2026-06-16T09:00:00Z",
  "end_time": "2026-06-16T10:30:00Z",
  "duration_seconds": 5400,
  "app_sequence": ["code", "firefox", "discord", "code"],
  "event_count": 47,
  "status": "closed"
}
```

**IntentRecord** — AI inference output with confidence scoring:
```json
{
  "record_id": "uuid",
  "session_id": "uuid",
  "session_type": "applied_learning",
  "goal": "Build React component with API integration",
  "goal_confidence": 0.85,
  "friction_points": ["Switched between 3 tabs to find API reference"],
  "category": "skill_development",
  "category_confidence": 0.78,
  "evidence": ["VS Code open", "MDN docs open"]
}
```

---

## Getting Started

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 20 or higher
- **Poetry** (Python package manager)
- **Linux** (Ubuntu 20.04/22.04 recommended) with `xdotool`, `xprop`, `wmctrl`

### Installation

```bash
# 1. Install Python dependencies
cd backend
poetry install
cd ..

# 2. Install frontend dependencies
cd dashboard
npm install
cd ..
```

### Running

Start the backend (terminal 1):
```bash
cd backend
poetry run uvicorn backend.main:app --reload --port 8000
```

Start the dashboard (terminal 2):
```bash
cd dashboard
npm run dev
```

Open **http://localhost:5173** in your browser.

### Generate Test Data

```bash
# Populate SQLite with sample sessions
export PATH="$HOME/.local/bin:$PATH" && cd backend && poetry run python ../scripts/seed_db.py

# Simulate realistic activity events
export PATH="$HOME/.local/bin:$PATH" && cd backend && poetry run python ../scripts/simulate_session.py
```

---

## Use Cases

### Riwi Learning Environment

In a software bootcamp (like Riwi), the same activity can mean different things depending on context:

| Activity | Without Context | With Insight Monitor |
|---|---|---|
| YouTube tutorial | Distraction | **Skill development** (if paired with IDE + docs) |
| Discord chat | Distraction | **Peer collaboration** (if during project work) |
| Reading documentation | Low activity | **Research / self-learning** |
| ChatGPT | Cheating | **Learning tool** (if used for understanding) |

### BPO / Call Center

| Activity | Classification |
|---|---|
| CRM + SAP + softphone simultaneously | **Active customer call** |
| Post-call documentation | **Task wrap-up** |
| Browser research during call | **Work-relevant inquiry** |

### Personal Productivity

- Discover when you actually focus best
- See what tasks drain vs. energize you
- Track progress over weeks, not just days
- All data stays yours — full control over sharing

---

## MVP Scope

### Included

- Active window tracking with `xdotool` / `xprop`
- Periodic screenshots with `mss` (configurable interval)
- Input frequency monitoring (clicks/min, keystrokes/min) — no content capture
- URL context from browser tab titles
- SQLite storage for events, sessions, and intent records
- REST API with event ingestion and session retrieval
- Session builder with inactivity gap detection (8 min default)
- Gemini-powered intent inference (multimodal: screenshots + text)
- React dashboard with session list and detail views
- Simulation scripts for test data generation

### Excluded (Post-MVP)

| Feature | Planned |
|---|---|
| Wayland support | `ydotool` fallback; full portal API support |
| Browser extension for full URLs | Chrome/Firefox extension post-MVP |
| Multi-tenant isolation | Add tenant_id + middleware |
| WebSocket real-time updates | When sub-second updates needed |
| User authentication (JWT) | Hardcoded demo mode for MVP |
| macOS / Windows native support | Secondary targets |
| GUI installer (MSI/DEB) | Package with PyInstaller |
| Report generation (PDF/CSV) | Celery-based worker |

---

## Confidence Model

Every inference carries a confidence score in the range **[0.0, 1.0]**:

| Range | Classification | Display |
|---|---|---|
| ≥ 0.8 | High confidence | Green badge with cited evidence |
| 0.5 – 0.79 | Moderate confidence | Yellow badge, alternatives included |
| 0.3 – 0.49 | Low confidence | Red badge, marked as uncertain |
| < 0.3 | Insufficient evidence | Grey badge, "insufficient data" |

---

## Error Philosophy

> **The cost of a false accusation exceeds the cost of a missed detection.**

| Error Type | Tolerance | Behavior |
|---|---|---|
| False positive (productive work → distraction) | Near zero | Default to ambiguous, never accuse |
| False negative (actual distraction → missed) | Acceptable | Better no classification than wrong |
| Sensitive data persisted | Never | Aggressive redaction, even at cost of losing context |

---

## Documentation

Full project documentation and decision records are available at:
**[github.com/insight-monitor/insight-monitor-docs](https://github.com/insight-monitor/insight-monitor-docs)**

Key documents:
- [MVP Definition](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Definition.md)
- [MVP Architecture](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-Architecture.md)
- [MVP 14-Day Plan](https://github.com/insight-monitor/insight-monitor-docs/tree/topic/MVP/700-MVP/MVP-14-Day-Plan.md)

---

## License

Private — Insight Monitor. All rights reserved.
