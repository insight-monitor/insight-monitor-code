// Frontend-specific types and re-exports from generated backend types
// Backend models are auto-generated: run `npm run generate:types` in dashboard/
// Source: backend/domain/entities/*.py

export {
  type RawEvent,
  type SessionContext,
  type IntentRecord,
  type SessionType,
  type EventType,
} from "./generated-types";

export interface AppSummary {
  duration_min: number;
  focus_pct: number;
}

export interface SessionWithIntent extends SessionContext {
  intent?: IntentRecord;
}

export interface SessionListResponse {
  sessions: SessionContext[];
  count: number;
}