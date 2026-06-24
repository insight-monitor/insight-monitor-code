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
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function getHealth(): Promise<Health> {
  return request<Health>("/health")
}

export async function getSessions(
  status?: string,
  limit: number = 50
): Promise<{ sessions: Session[]; count: number }> {
  const params = new URLSearchParams()
  if (status) params.set("status", status)
  params.set("limit", String(limit))
  return request<{ sessions: Session[]; count: number }>(
    `/sessions?${params.toString()}`
  )
}

export async function getSession(
  id: string
): Promise<SessionDetail> {
  return request<SessionDetail>(`/sessions/${id}`)
}
