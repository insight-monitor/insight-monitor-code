const API_BASE = "/api"

export interface Health {
  status: string
  agent: string
  version: string
}

export interface Session {
  id: string
  start_time: string
  end_time: string | null
  duration_seconds: number | null
  app_sequence: string
  event_count: number
  screenshot_count: number
  avg_clicks_per_min: number | null
  avg_keystrokes_per_min: number | null
  active_apps: string
  session_type: string | null
  goal: string | null
  confidence: number | null
  status: string
  created_at: string
}

export interface RawEvent {
  id: number
  event_id: string
  event_type: string
  timestamp: string
  source: string
  window_title: string | null
  process_name: string | null
  pid: number | null
  screenshot_path: string | null
  clicks_per_min: number | null
  keystrokes_per_min: number | null
  url: string | null
  session_id: string | null
}

export interface SessionDetail extends Session {
  events: RawEvent[]
  intent?: IntentRecord
}

export interface SessionListResponse {
  sessions: Session[]
  count: number
  total: number
}

export interface IntentRecord {
  record_id: string
  session_id: string
  timestamp: string
  session_type: string
  goal: string
  goal_confidence: number
  friction_points: string[]
  friction_confidence: number | null
  category: string
  category_confidence: number
  tags: string[]
  evidence: string[]
  alternatives: string[]
  app_summary: Record<string, unknown>
  raw_timeline_summary: string
  raw_llm_response: string | null
  created_at: string
}

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail || `API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export interface SessionFilters {
  status?: string
  limit?: number
  offset?: number
  start_date?: string
  end_date?: string
}

export async function getHealth(): Promise<Health> {
  return request<Health>("/health")
}

export async function getSessions(
  filters: SessionFilters = {}
): Promise<SessionListResponse> {
  const params = new URLSearchParams()
  if (filters.status) params.set("status", filters.status)
  if (filters.limit != null) params.set("limit", String(filters.limit))
  if (filters.offset != null) params.set("offset", String(filters.offset))
  if (filters.start_date) params.set("start_date", filters.start_date)
  if (filters.end_date) params.set("end_date", filters.end_date)
  return request<SessionListResponse>(`/sessions?${params.toString()}`)
}

export async function getSession(
  id: string
): Promise<SessionDetail> {
  return request<SessionDetail>(`/sessions/${id}`)
}
