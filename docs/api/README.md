# API Reference

Full interactive API documentation is available at `http://localhost:8002/docs` (Swagger UI) when the backend is running.

## Endpoints

| Method | Path | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Health check + agent heartbeat status + version | ✅ |
| `POST` | `/heartbeat` | Record agent heartbeat (from capture agent) | ✅ |
| `POST` | `/events` | Ingest a single RawEvent | ✅ |
| `POST` | `/events/batch` | Ingest multiple RawEvents | ✅ |
| `GET` | `/events` | List recent events (`?limit=50&offset=0`) | ✅ |
| `GET` | `/events/session/{id}` | Events for a session (`?limit=20&offset=0`) | ✅ |
| `GET` | `/sessions` | List sessions (`?status=open&limit=50`) | ✅ |
| `GET` | `/sessions/{id}` | Session detail + paginated events (`?limit=20&offset=0`) | ✅ |
| `GET` | `/sessions/{id}/intent` | Session intent record only | ✅ |
| `POST` | `/sessions/{id}/close` | Manually close a session | ✅ |
| `GET` | `/tickets` | List tickets (`?status=open&limit=50&offset=0`) | ✅ |
| `POST` | `/tickets` | Create a ticket | ✅ |
| `GET` | `/tickets/stats` | Ticket statistics (total, open, in_progress, resolved, closed) | ✅ |
| `GET` | `/tickets/{id}` | Ticket detail with comments | ✅ |
| `PUT` | `/tickets/{id}` | Update ticket (title, description, status, priority) | ✅ |
| `DELETE` | `/tickets/{id}` | Delete ticket and its comments | ✅ |
| `POST` | `/tickets/{id}/comments` | Add comment to a ticket | ✅ |

## Data Models

### RawEvent — atomic unit of captured activity
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

### SessionContext — aggregated view of a work session
```json
{
  "session_id": "uuid",
  "start_time": "2026-06-16T09:00:00Z",
  "end_time": "2026-06-16T10:30:00Z",
  "duration_seconds": 5400,
  "app_sequence": ["code", "firefox", "discord"],
  "event_count": 47,
  "status": "closed"
}
```

### IntentRecord — AI inference output with confidence scoring
```json
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
