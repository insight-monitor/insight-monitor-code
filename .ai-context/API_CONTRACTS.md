# API Contracts (Generated from Pydantic via ARCH-9)

## Base URL
- Dev: `http://localhost:8002`
- API Prefix: `/api` (proxied by Vite)

## Endpoints

### Health
```
GET /health
Response: { "status": "ok", "agent": "insight-monitor", "version": "0.1.0" }
```

### Events
```
POST /events
Request: RawEvent (see types)
Response: { "status": "ok", "event_id": "uuid" }

POST /events/batch
Request: RawEvent[]
Response: { "status": "ok", "count": int }

GET /events
Query: limit=50
Response: { "events": RawEvent[], "count": int }

GET /events/session/{session_id}
Response: { "session_id": "uuid", "events": RawEvent[], "count": int }
```

### Sessions
```
GET /sessions
Query: status=open|closed, limit=50
Response: { "sessions": Session[], "count": int }

GET /sessions/{session_id}
Response: SessionDetail (Session + events + intent?)

GET /sessions/{session_id}/intent
Response: IntentRecord | 404

POST /sessions/{session_id}/close
Response: { "status": "closed"|"already_closed", "session_id": "uuid" }
```

## TypeScript Types (Generated - dashboard/src/api/generated/)
```typescript
// RawEvent
interface RawEvent {
  event_id: string;
  event_type: "window_focus" | "screenshot" | "input_activity" | "url_context" | "session_boundary";
  timestamp: string; // ISO 8601
  source: string;
  window_title?: string;
  process_name?: string;
  pid?: number;
  screenshot_path?: string;
  screenshot_thumbnail?: string;
  clicks_per_min?: number;
  keystrokes_per_min?: number;
  url?: string;
  browser_tab_title?: string;
  session_id?: string;
  session_boundary_type?: string;
}

// Session (from API)
interface Session {
  id: string;
  start_time: string;
  end_time: string | null;
  duration_seconds: number | null;
  app_sequence: string[]; // parsed JSON
  event_count: number;
  screenshot_count: number;
  avg_clicks_per_min: number | null;
  avg_keystrokes_per_min: number | null;
  active_apps: string[]; // parsed JSON
  session_type: string | null;
  goal: string | null;
  confidence: number | null;
  status: "open" | "closed";
  created_at: string;
}

// IntentRecord
interface IntentRecord {
  record_id: string;
  session_id: string;
  timestamp: string;
  session_type: "skill_development" | "applied_learning" | "peer_collaboration" | "ambiguous" | "personal";
  goal: string;
  goal_confidence: number;
  friction_points: string[];
  friction_confidence: number | null;
  category: string;
  category_confidence: number;
  tags: string[];
  evidence: string[];
  alternatives: string[];
  app_summary: Record<string, unknown>;
  raw_timeline_summary: string;
  raw_llm_response: string | null;
  created_at: string;
}
```

## Generation (ARCH-9)
- Script: `scripts/generate_types.py`
- Runs: `datamodel-codegen` on `backend/models/*.py`
- Output: `dashboard/src/api/generated/`
- CI: Fails if generated types differ from committed