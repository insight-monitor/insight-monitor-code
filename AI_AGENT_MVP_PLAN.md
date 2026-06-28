# AI Agent MVP Execution Plan — Days 9-14

**Status**: ARCH-1 through ARCH-11 are **CLOSED**. ARCH-0 (#41) remains open — legacy `pipeline/` folder is still active alongside the new Clean Architecture use cases.

**Branch**: `chore/ai-agent-mvp-plan`
**Target**: Complete the MVP (Days 9-14 of 14-day plan)
**Key Shifts**:
- ARCH issues (1-11) ✅ Solved — focus is now on **finishing the migration** and **real-time tracking**
- LLM Provider: **OpenAI** (default — Gemini dropped due to free API reliability issues)
- Real-time tracking: Currently **mock/simulated** — needs **Wayland support** and **agent heartbeat** (#55)

---

## 1. What's Done (ARCH-1 through ARCH-11)

All architecture restructuring issues from the original plan are closed:

| Issue | Status | Description |
|-------|--------|-------------|
| ARCH-1 (#30) | ✅ Closed | Database singleton removed — DB injected explicitly |
| ARCH-2 (#31) | ✅ Closed | Repository port interfaces in `application/ports/repositories.py` |
| ARCH-3 (#32) | ✅ Closed | Domain layer (`domain/entities/`, `domain/value_objects/`, `domain/events/`, `domain/services/`) |
| ARCH-4 (#33) | ✅ Closed | Application layer with use cases (IngestEvent, BuildSessions, InferIntent, CloseSession, GetSession, ListSessions) |
| ARCH-5 (#34) | ✅ Closed | SQLite + InMemory repository implementations |
| ARCH-6 (#35) | ✅ Closed | DI Composition Root in `infrastructure/di.py` |
| ARCH-7 (#36) | ✅ Closed | Unit of Work transaction boundaries |
| ARCH-8 (#37) | ✅ Closed | Capture agent resilience (buffer, retry with backoff, graceful shutdown) |
| ARCH-9 (#38) | ✅ Closed | TypeScript types auto-generated from Pydantic via `scripts/generate_types.py` |
| ARCH-10 (#39) | ✅ Closed | Architecture docs updated (`current-state.md`, ADRs) |
| ARCH-11 (#40) | ✅ Closed | Unit tests with InMemory repos; `pytest -m unit` < 2s |

### What Still Remains

**ARCH-0 (#41) — Master Plan**: The legacy `backend/pipeline/` directory still exists and is still wired into `main.py` as background tasks (`SessionBuilder`, `InferencePipeline`). The migration is **partially complete** — use cases exist and are used by API routes, but background tasks bypass them.

**Dual execution path currently**:
1. **Legacy background tasks** (started in `main.py` lifespan): `SessionBuilder` + `InferencePipeline` poll SQLite directly every 30s/60s
2. **Clean Architecture use cases** (via API routes): called through DI container

---

## 2. Remaining Work (Days 9-14)

### Day 9: ARCH-0 Completion — Remove Legacy Pipeline

**Goal**: Eliminate the dual execution path. Background tasks should use the Clean Architecture use cases.

| Task | Owner | Description | Issue |
|------|-------|-------------|-------|
| Absorb pipeline into use cases | Backend Lead | Move `session_builder.py` logic into `BuildSessionsUseCase` | #41 |
| Absorb inference into use cases | Backend Lead | Move `inference_pipeline.py` logic into `InferIntentUseCase` | #41 |
| Replace `main.py` background tasks | Backend Lead | Use APScheduler or FastAPI lifespan calling use cases via DI | #41 |
| Remove `backend/pipeline/` directory | Backend Lead | Delete after all logic is absorbed | #41 |
| Integration tests | QA Lead | Test background tasks now use use cases | #41 |

**Definition of Done**:
- [ ] `backend/pipeline/` directory deleted
- [ ] `main.py` background tasks call use cases (not legacy pipeline classes)
- [ ] All existing tests pass
- [ ] E2E smoke test: Capture → API → Dashboard

### Day 10: Real-Time Tracking — Wayland Support + Agent Health

**Goal**: Replace mock/simulated data with real-time capture on modern Ubuntu (Wayland). Add agent heartbeat so the dashboard shows real agent status.

| Task | Owner | Description | Issue |
|------|-------|-------------|-------|
| Wayland window tracker | Capture Agent Lead | GNOME Shell DBus fallback in `capture/window_tracker.py` | #55 |
| Display server auto-detect | Capture Agent Lead | Instantiate correct tracker based on `$XDG_SESSION_TYPE` | #55 |
| Agent heartbeat | Backend Lead | Periodic `agent_heartbeat` events every 30s + `GET /health` returns `agent_status` | #55 |
| Dashboard agent status | Frontend Lead | Show "Capture Agent: Online v{version}" / "Offline" next to backend dot | #55 |
| Fallback to `xdotool` on X11 | Capture Agent Lead | Keep existing X11WindowTracker as fallback | #55 |

**Definition of Done**:
- [ ] Capture agent captures window titles on Ubuntu 22.04/24.04 Wayland (GNOME)
- [ ] Auto-detects display server and uses correct backend
- [ ] Dashboard shows real agent status (Online / Offline), not just API status
- [ ] X11 fallback still works

### Day 11: Self-Hosted Deployment — Systemd Services

**Goal**: Three systemd user services so the entire stack starts on boot without manual intervention.

| Task | Owner | Description | Issue |
|------|-------|-------------|-------|
| Backend systemd service | Infrastructure Lead | `insight-backend.service` — runs uvicorn on :8002 after network | #55 |
| Capture systemd service | Infrastructure Lead | `insight-capture.service` — runs agent, depends on backend | #55 |
| Dashboard systemd service | Infrastructure Lead | `insight-dashboard.service` — runs Vite on :5173 | #55 |
| Install script | Infrastructure Lead | `scripts/install-systemd-services.sh` — idempotent setup | #55 |
| Docs | Documentation Lead | Update platform support, add auto-start section to README | #56 |

**Definition of Done**:
- [ ] All three services start on machine boot
- [ ] Dependency chain: capture → backend → network, dashboard → backend
- [ ] Services degrade gracefully (backend fail ≠ capture agent crash)
- [ ] `scripts/install-systemd-services.sh` works idempotently

### Day 12: Testing & Quality Assurance

**Goal**: Comprehensive integration + E2E tests. Ensure real-time data flows end-to-end.

| Task | Owner | Description | Issue |
|------|-------|-------------|-------|
| Integration tests for SQLite | QA Lead | Real DB tests for all repositories | #54 |
| Integration tests for use cases | QA Lead | Use cases with real SQLite | #54 |
| E2E test: Capture → API → Dashboard | QA Lead | Full pipeline test with real agent events | — |
| Verify database-schema.md matches code | QA Lead | Sync schema docs with actual migrations | #54 |
| Test OpenAI integration | QA Lead | LLM service with real OpenAI calls (sparingly) | — |

**Definition of Done**:
- [ ] `pytest -m integration` passes
- [ ] E2E test: capture agent sends events → API stores → dashboard displays
- [ ] `database-schema.md` matches actual SQLite schema

### Day 13: Documentation & Polish

**Goal**: All docs reflect reality. Known issues are documented.

| Task | Owner | Description | Issue |
|------|-------|-------------|-------|
| Real-time monitoring visibility doc | Documentation Lead | What appears in Dashboard vs Terminal | #53 |
| Platform compatibility docs | Documentation Lead | Wayland support, systemd deployment | #56 |
| Legacy frontend clarification | Documentation Lead | `frontend/` vs `dashboard/` in all docs | #52 |
| Readme and setup docs update | Documentation Lead | Project initialization, DB setup, run modes | #51 |
| CI docs-consistency checks | CI Lead | Automated checks to prevent doc drift | #61 |

**Definition of Done**:
- [ ] #53, #56, #52, #51 closed
- [ ] All docs match current implementation
- [ ] CI checks for doc consistency

### Day 14: Final Integration & MVP Demo

**Goal**: Everything works end-to-end. Demo-ready.

| Task | Owner | Description |
|------|-------|-------------|
| Final E2E smoke test | All | Capture agent → API → Session building → Intent inference → Dashboard |
| Bug bash | All | Fix remaining issues |
| MVP demo prep | All | Tag `mvp-complete`, prepare demo script |
| Buffer | All | Absorb any delays from previous days |

**Definition of Done**:
- [ ] Capture agent works on Wayland and X11
- [ ] Dashboard shows live agent status + sessions with intent
- [ ] All three systemd services auto-start
- [ ] `pytest` passes (unit + integration)
- [ ] Tag `mvp-complete`

---

## 3. LLM Provider: OpenAI (Default)

The project currently supports both `openai` and `gemini` providers, configured via `LLM_PROVIDER` in `.env`.

**Current state**:
- Default: `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`
- Gemini support still exists in `services/llm_service.py` but is **not recommended** — free API tier had reliability issues
- `backend/.env.example` already defaults to OpenAI

**No code changes needed** — the switch is already in place at the config level. Ensure `API_KEY` in `.env` is set to an OpenAI key.

---

## 4. Real-Time Tracking: Current State

Currently the project uses **simulated/mock data** for development:
- `npm run simulate` sends predefined events to the API
- `npm run seed` creates sample sessions directly in SQLite
- The capture agent works only on **X11** — fails silently on Wayland (default Ubuntu 22.04+)

**To achieve real-time tracking**, the capture agent needs:
1. Wayland support (GNOME Shell DBus API) — #55
2. Agent heartbeat → dashboard shows real status — #55
3. Systemd auto-start on boot — #55

---

## 5. Open Issues Summary

| Issue | Title | Status | Priority |
|-------|-------|--------|----------|
| #41 | ARCH-0: Master Plan | OPEN | 🔴 Critical |
| #55 | Wayland support + systemd services | OPEN | 🔴 Critical |
| #53 | Real-time monitoring visibility docs | OPEN | 🟡 High |
| #54 | database-schema.md sync | OPEN | 🟡 High |
| #56 | Platform compatibility docs | OPEN | 🟡 High |
| #52 | Legacy frontend clarification | OPEN | 🟡 High |
| #51 | Readme/setup docs update | OPEN | 🟡 High |
| #59 | Missing /api/tickets endpoints | OPEN | 🟡 High |
| #61 | Docs-consistency CI checks | OPEN | 🟢 Medium |
| #12-17 | Days 9-14 MVP Roadmap | OPEN | 🟢 Medium |

---

## 6. Dependency Graph (Days 9-14)

```
DAY 9                         DAY 10                        DAY 11                        DAY 12-14
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│ ARCH-0 completion    │      │ Wayland tracker (#55) │      │ Systemd services     │      │ Testing + Polish     │
│ Remove pipeline/     │ ──→  │ Agent heartbeat (#55) │ ──→  │ (#55)                │ ──→  │ + MVP Demo           │
│ Background tasks →   │      │ Dashboard agent       │      │ Install script       │      │                      │
│ use cases            │      │ status (#55)          │      │ Docs (#56)           │      │ Tag mvp-complete     │
└──────────────────────┘      └──────────────────────┘      └──────────────────────┘      └──────────────────────┘

PARALLEL (Any Day): #53 (monitoring docs), #54 (schema sync), #52 (legacy frontend), #51 (setup docs), #61 (CI checks)
```

---

## 7. Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Wayland testing requires physical access | High | Test on CI with Xvfb + merge Wayland code with X11 fallback |
| Pipeline removal breaks existing features | Medium | Keep pipeline/ until Day 9 tests pass; delete only after green CI |
| OpenAI API cost for testing | Low | Use cached responses in unit tests; real calls only in integration |
| Time overrun | Medium | **Cut scope**: Deploy with simulated data + X11 only; Wayland as post-MVP |

### MVP Minimum (If Desperate)
- ARCH-0 complete (pipeline removed)
- OpenAI integration working
- X11 capture agent + simulated data
- Dashboard shows sessions with intent
- Integration tests pass

---

## 8. Context Files

| File | Purpose | Owner |
|------|---------|-------|
| `.ai-context/ARCHITECTURE.md` | Target Clean Architecture layers | Backend Lead |
| `.ai-context/CURRENT_SPRINT.md` | Daily goals and status | All (updated daily) |
| `.ai-context/DOMAIN_MODEL.md` | Entities, VOs, events, services | Backend Lead |
| `.ai-context/PORT_CONTRACTS.md` | Repository, LLM, EventBus interfaces | Backend Lead |
| `.ai-context/CODING_STANDARDS.md` | Python/TS conventions, git, security | All |
| `.ai-context/AGENT_INSTRUCTIONS.md` | Agent startup & workflow | All |
| `.ai-context/AGENT_HANDOFF.md` | Agent-to-agent context transfer | All |
| `COLABORATORS.md` | Pre-commit hooks, setup guide | All |

---

## 9. Quick Reference

```bash
# Set up
cd backend
poetry install
cp .env.example .env  # Edit API_KEY to your OpenAI key

# Run
npm run dev           # Full stack (backend :8002 + dashboard :5173)
npm run capture       # Capture agent (separate terminal)
npm run seed          # Load sample sessions

# Test
cd backend
poetry run pytest -m unit -q
poetry run pytest -m integration -q

# Quality
poetry run mypy --strict .
poetry run ruff check .
```
