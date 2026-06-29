// Re-export types from client.ts (source of truth for backend-derived types)
export type { RawEvent, IntentRecord, Session } from "./client";

export interface AppSummary {
  duration_min: number;
  focus_pct: number;
}

export interface SessionWithIntent extends Session {
  intent?: IntentRecord;
}

export interface SessionListResponse {
  sessions: Session[];
  count: number;
}
