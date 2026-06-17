import type {
  HealthResponse,
  SessionContext,
  SessionWithIntent,
  SessionListResponse,
} from "./types"

const API_BASE = "http://localhost:8000"

async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export function getHealth(): Promise<HealthResponse> {
  return fetcher<HealthResponse>("/health")
}

export function getSessions(status?: string): Promise<SessionListResponse> {
  const params = status ? `?status=${status}` : ""
  return fetcher<SessionListResponse>(`/sessions${params}`)
}

export function getSession(id: string): Promise<SessionWithIntent> {
  return fetcher<SessionWithIntent>(`/sessions/${id}`)
}

export function getSessionIntent(id: string): Promise<import("./types").IntentRecord> {
  return fetcher<import("./types").IntentRecord>(`/sessions/${id}/intent`)
}
