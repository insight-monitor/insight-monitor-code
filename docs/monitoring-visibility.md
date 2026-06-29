# Real-Time Monitoring Visibility

What you see where — Dashboard (frontend) vs Terminal (capture agent / backend).

## Dashboard (`http://localhost:5173`)

| Component | What's Visible | Refresh Frequency |
|-----------|---------------|-------------------|
| **Agent Status** | Green/red dot + "Capture Agent: Online vX.Y.Z" / "Offline" | Every 10 seconds (polls `/health`) |
| **Session List** | Table with status, start time, duration, event count, apps, inferred type, goal, confidence | Every 10 seconds (polls `/sessions`) |
| **Session Detail** | Event timeline with icons, intent card (type, goal, confidence, tags), "Load More" pagination (20 events/page) | On click (polls `/sessions/{id}`) |
| **Health Endpoint** | API status + agent heartbeat status (`/health`) | Every 10 seconds |

## Terminal — Capture Agent (`npm run capture`)

| Log | What's Visible | Frequency |
|-----|---------------|-----------|
| Startup | API URL, capture interval | Once at start |
| Window events | Window title, process name, PID | Every 5 seconds |
| Screenshot events | Screenshot path | Every 30 seconds (default) |
| Input events | Clicks/min, keystrokes/min | Every 5 seconds |
| Heartbeat | Sent silently to backend | Every 30 seconds |
| Shutdown | "Capture agent stopped" | Once on exit |

## Terminal — Backend API (`npm run backend`)

| Log | What's Visible | Frequency |
|-----|---------------|-----------|
| Startup | Provider, model, DB path | Once at start |
| HTTP requests | Method, path, status code | Per request |
| Session builder | Events processed count | Every 30 seconds |
| Inference | Closed sessions processed | Every 60 seconds |
| Errors | Session builder / inference errors | On error |

## sqlite-web (`http://localhost:8081`)

| Table | Contents |
|-------|----------|
| `raw_events` | All captured events (window_focus, screenshot, input_activity, agent_heartbeat) |
| `sessions` | Session metadata (start/end time, duration, apps, type, goal, confidence) |
| `intent_records` | LLM classification results (session type, goal, friction points, tags) |
| `tickets` | Support tickets |
| `ticket_comments` | Ticket comments |

## Event Types

| Type | Source | Purpose |
|------|--------|---------|
| `window_focus` | Capture agent | Window title, process, PID, URL |
| `screenshot` | Capture agent | Screenshot path |
| `input_activity` | Capture agent | Clicks/min, keystrokes/min |
| `agent_heartbeat` | Capture agent | Agent liveness check (every 30s) |

## Health Checks

`GET /health` returns:
```json
{
  "status": "ok",
  "agent": {
    "status": "online" | "offline",
    "version": "0.1.0",
    "last_seen": "2026-06-27T12:00:00Z" | null
  },
  "api_version": "0.1.0"
}
```

- Agent considered **online** if heartbeat received within last 60 seconds
- Agent considered **offline** if no heartbeat in last 60 seconds
- Dashboard updates agent status every 10 seconds
