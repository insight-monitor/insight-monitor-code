---
title: MVP Scaling Path
type: concept
domain: architecture
priority: medium
status: review
version: 2.0.0
updated: 2026-06-25
---

# MVP Scaling Path

This document describes what the MVP does NOT do yet — but what the architecture preserves so that future additions don't require rewrites.

## Architecture Decisions That Survive Scaling

### 1. Clean Architecture with Dependency Inversion

The backend follows Clean Architecture: Domain → Application → Infrastructure, with strict dependency inversion. Inner layers define ports (interfaces); outer layers implement them. This means:
- SQLite can be swapped for PostgreSQL or any other database by implementing the same port interfaces
- The LLM service can be replaced (Gemini → Claude → local model) without touching use cases
- New use cases can be added without modifying existing code
- Unit tests use InMemory repositories — zero disk, zero network, zero shared state

### 2. Decoupled layers via HTTP

The three layers (Capture, API, Dashboard) communicate over HTTP. This means:
- The capture agent can be replaced (e.g., Electron app with more UI) without touching backend
- The dashboard can be swapped for a mobile app without changing inference
- Multiple capture agents can post to the same API instance (multi-device support)

### 3. Pydantic models as the schema contract

All data structures (`RawEvent`, `SessionContext`, `IntentRecord`) are defined as Pydantic entities in `domain/entities/`. The TypeScript types in the frontend mirror them manually (ARCH-9 pending). When the schema evolves:
- Add a field to Pydantic → auto-generated OpenAPI spec → regenerate TypeScript types
- Manual synchronization between Python and TypeScript is still required until ARCH-9 is implemented

### 4. Configuration-driven capture

The capture agent reads all parameters from environment variables (interval, paths, thresholds). Adding new signal types post-MVP:
- Add the capture module
- Add the handler in `agent.py`
- No hardcoded values to untangle

### 5. Capture agent resilience (ARCH-8)

The capture agent now survives backend restarts with:
- **Local buffer** (up to 500 events) when backend is unreachable
- **Exponential backoff** retries (1s → 2s → 4s)
- **Auto-flush** on reconnect
- **Graceful shutdown** — flushes buffer before closing

### 6. Prompt as the product (current limitation)

The inference prompt is built programmatically by `PromptBuilder`, not a standalone template file. This is a known limitation — changing classification categories or adding new use cases requires code changes, not just prompt edits. A future iteration should externalize the prompt into a version-controlled template file.

## Post-MVP Roadmap

### Immediate (Weeks 3-4 after MVP)

| Feature | Why |
|---|---|
| ARCH-9: TypeScript type generation from Pydantic | Eliminate manual TypeScript sync; reduce frontend bugs |
| Browser extension for full URLs | More accurate URL context than tab titles |
| Multi-tenant isolation | Need to serve > 1 customer |
| WebSocket-based real-time updates | Better dashboard experience |
| Confidence model refinement | Calibrate confidence scores against user feedback |

### Medium-term (Months 2-3)

| Feature | Why |
|---|---|
| LanceDB + semantic search | Query historical sessions in natural language |
| Anomaly detection engine | Rule-based + statistical anomaly on URL/domain patterns |
| macOS capture agent | Broaden market reach |
| Externalize prompt to template file | Enable prompt-only classification changes without code deploys |

### Long-term (Months 4-6)

| Feature | Why |
|---|---|
| GUI installer (MSI/DEB/DMG) | Non-technical deployment |
| Centralized management server | Fleet-wide configuration and monitoring |
| Celery worker for async inference | Background processing for report generation |
| User contestability UI | Feedback loop for improving accuracy |
| Integration APIs (webhooks) | Connect to Slack, Jira, HR systems |

## What NOT to Preserve

The Clean Architecture migration (ARCH-0) addressed several anti-patterns. What remains to be replaced:

| Current | Replace With | When |
|---|---|---|
| SQLite | PostgreSQL or SQLite with replication | Multi-user or multi-instance deployment |
| Gemini Flash | Domain-fine-tuned model or smaller local model | Inference volume or privacy requirements grow |
| HTTP polling | WebSocket | Real-time dashboard adopted by supervisors |
| Single process FastAPI | Docker Compose + multiple services | Need to scale API, inference, and storage independently |
| CLI agent startup | Systemd service / Windows service | Agent must survive reboots and user logouts |
| Manual TypeScript sync (ARCH-9) | Auto-generation from Pydantic | Immediately (next sprint) |
| Pipeline modules (`pipeline/`) | Full migration to use case classes | As each pipeline function is absorbed by a use case |
| Synchronous inference (ADR-0003) | Celery/Redis for async queue | When inference volume exceeds sync capacity |
