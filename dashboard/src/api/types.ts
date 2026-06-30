import type { RawEvent, IntentRecord, Session } from "./client";

export type { RawEvent, IntentRecord, Session };

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
