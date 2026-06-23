---
title: Database MVP Scope vs Complete DER
type: conceptual
domain: data-model
priority: high
status: accepted
version: 1.0.0
---

# Database Architecture: MVP vs Full DER

This document clearly defines the data architecture boundaries between the **MVP (Minimum Viable Product)** currently in development and the long-term vision captured in the **Complete Entity-Relationship Diagram (ERD)**.

## Phase 1: The Desktop MVP (Current State)

The MVP focus (Day 1 & 2) is to test the closed loop of **Local Capture → Local AI Inference**. To avoid over-engineering and accelerate development, a simplified temporary architecture has been adopted.

**MVP schema characteristics:**
- **Engine:** Local SQLite (`insight_monitor.db`).
- **Mode:** WAL (Write-Ahead Logging) for safe concurrency between threads.
- **Scope:** Strictly single-user. The local machine equals the entire context.

### Implemented Tables (The "What" of the MVP)

1. **`raw_events`**: Unifies the concepts of event, active window, and capture log into a single temporary atomic record.
2. **`sessions`**: Groups work time windows, omitting any foreign key relationships to users, companies, or cloud agents.
3. **`intent_records`**: Stores the local AI inference result in a denormalized format.

*(Refer to `database-schema.md` for the exact SQLite schema).*

---

## Phase 2: Cloud Enterprise (The Complete ERD)

The official ERD documents the **target cloud architecture**, which will be needed once the system becomes a Multi-Tenant SaaS platform.

![Complete Entity-Relationship Diagram](img/der-complete.png)

**ERD schema characteristics:**
- **Engine:** Robust relational database (e.g., MySQL/PostgreSQL).
- **Mode:** Centralized server.
- **Scope:** Multi-tenant (Companies -> Users -> Multiple Agents/Teams).

### Post-MVP Modules

The following modules documented in the ERD will **NOT be part of the MVP** and will be built in later phases:

1. **Organizational Module**: `company`, `user`, `role`, and `user_role` tables.
2. **Agents Module**: Capture client registration by machine (`agent`).
3. **Privacy Module**: Redaction engine and censorship rules (`privacy_rule`, `sensitive_detection`).
4. **Reports & Audit Module**: Pre-computed analytical histories (`report`) and system access logs (`audit`).
5. **Strict Normalization**: Separation of base `event` from `screenshot`, `ocr_text`, and `active_window` metadata.

## Future Migration Strategy

The current `raw_events` and `sessions` design includes locally generated UUID identifiers. In Phase 2, a Sync Agent service will take these local SQLite records and insert them into the central MySQL cluster, injecting the foreign UUIDs for `user_id` and `agent_id` corresponding to the device's authentication token.
