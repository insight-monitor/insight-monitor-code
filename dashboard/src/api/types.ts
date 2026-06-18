// Mirror of backend Pydantic models
// IntentRecord from: backend/models/intent_record.py
// SessionContext from: backend/models/session_context.py
// RawEvent from: backend/models/raw_event.py
// Last synced: 2026-06-17

export type SessionType =
  | "skill_development"
  | "applied_learning"
  | "peer_collaboration"
  | "ambiguous"
  | "personal"

export type EventType =
  | "window_focus"
  | "screenshot"
  | "input_activity"
  | "url_context"
  | "session_boundary"

export interface RawEvent {
  event_id: string
  event_type: EventType
  timestamp: string
  source: string
  window_title?: string
  process_name?: string
  pid?: number
  screenshot_path?: string
  screenshot_thumbnail?: string
  clicks_per_min?: number
  keystrokes_per_min?: number
  url?: string
  browser_tab_title?: string
  session_id?: string
  session_boundary_type?: string
}

export interface SessionContext {
  session_id: string
  start_time: string
  end_time?: string
  duration_seconds?: number
  app_sequence: string[]
  event_count: number
  screenshot_count: number
  avg_clicks_per_min?: number
  avg_keystrokes_per_min?: number
  active_apps: string[]
  status: string
}

export interface AppSummary {
  duration_min: number
  focus_pct: number
}

export interface IntentRecord {
  record_id: string
  session_id: string
  timestamp: string
  session_type: SessionType
  goal: string
  goal_confidence: number
  friction_points: string[]
  friction_confidence?: number
  category: string
  category_confidence: number
  tags: string[]
  evidence: string[]
  alternatives: string[]
  app_summary: Record<string, AppSummary>
  raw_timeline_summary: string
  raw_llm_response?: string
}

export interface SessionWithIntent extends SessionContext {
  intent?: IntentRecord
}

export interface HealthResponse {
  status: string
}

export interface SessionListResponse {
  sessions: SessionContext[]
  count: number
}
