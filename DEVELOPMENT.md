# Development Quick Reference

## Common Commands

### Backend

```bash
cd backend

# Install deps
poetry install

# Run server (port 8002 per run-backend.sh)
poetry run uvicorn backend.main:app --reload --port 8002

# Tests
poetry run pytest -m unit -v          # Unit tests only (<2s)
poetry run pytest -m integration -v   # Integration tests
poetry run pytest -v                  # All tests

# Quality gates
poetry run mypy --strict .
poetry run ruff check .
poetry run ruff format .

# Database
poetry run python ../scripts/seed_db.py
```

### Frontend

```bash
cd dashboard

# Install deps
npm install

# Dev server
npm run dev

# Build
npm run build

# Quality gates
npm run typecheck
npm run lint

# Generate types from backend (ARCH-9)
npm run generate:types
```

### Root

```bash
# Generate types (ARCH-9)
npm run generate:types

# Run all (needs concurrently)
npm run dev
```

---

## Run Modes Quick Ref

| Mode | Command | What Runs | Port(s) |
|------|---------|-----------|---------|
| Full stack (dev) | `npm run dev` | Backend + Dashboard | 8002, 5173 |
| Backend only | `npm run backend` | FastAPI + auto-reload | 8002 |
| Frontend only | `npm run dashboard:dev` | Vite dev server | 5173 |
| Capture agent | `npm run capture` | Python agent → API | — |
| Seed test data | `npm run seed` | SQLite ← sample sessions | — |
| Simulate events | `npm run simulate` | HTTP → API → SQLite | — |
| DB viewer | `cd infrastructure/db-mvp && docker compose up -d` | sqlite-web | 8081 |

---

## Project Structure

```
insight-monitor-code/
├── .ai-context/              # Source of truth for standards
│   ├── ARCHITECTURE.md
│   ├── CODING_STANDARDS.md
│   ├── AGENT_INSTRUCTIONS.md
│   ├── PORT_CONTRACTS.md
│   ├── DOMAIN_MODEL.md
│   ├── SECURITY_RULES.md
│   ├── ERROR_PHILOSOPHY.md
│   ├── API_CONTRACTS.md
│   ├── CURRENT_SPRINT.md
│   ├── AGENT_HANDOFF.md
│   └── BRAND_GUIDELINES.md
├── backend/
│   ├── application/          # Use cases, ports, DTOs
│   ├── domain/               # Entities, VOs, events, services
│   ├── infrastructure/       # SQLite, InMemory, DI
│   ├── routes/               # FastAPI routers (thin)
│   ├── services/             # LLM service, prompts, intent parser
│   ├── services/             # LLM service
│   ├── config.py             # Settings
│   ├── main.py               # FastAPI app entry
│   ├── tests/                # Unit + integration tests
│   └── pyproject.toml
├── capture/                  # Capture agent (Python)
├── dashboard/                # React + TS + Tailwind (CURRENT frontend)
├── scripts/                  # Utility scripts
├── tests/                    # E2E tests
├── frontend/                 # ⚠️ LEGACY — AI Support Desk (Vanilla JS, NOT Insight Monitor)
├── CONTRIBUTING.md           # Full contribution guide
└── README.md
```

---

## Test Commands Quick Ref

```bash
# Backend unit tests only (fast, no DB)
cd backend && poetry run pytest -m unit -q

# Backend integration tests (real SQLite)
cd backend && poetry run pytest -m integration -q

# Frontend type check
cd dashboard && npm run typecheck

# Frontend lint
cd dashboard && npm run lint

# All quality gates
cd backend && poetry run mypy --strict . && poetry run ruff check .
cd dashboard && npm run typecheck && npm run lint
```

---

## Git Workflow Quick Ref

```bash
# Start new work
git checkout develop
git pull origin develop
git checkout -b refactor/arch-X-description

# Commit
git add .
git commit -m "refactor(domain): extract SessionClassifier"

# Push & PR
git push origin refactor/arch-X-description
gh pr create --base develop --title "ARCH-X: Description" --body "Closes #X"

# Sync with develop
git fetch origin
git rebase origin/develop

# Before merge: rebase, run all checks
```

---

## Branch Prefixes

| Prefix | Use For |
|--------|---------|
| `refactor/arch-X-*` | Architecture tasks (ARCH-1 to ARCH-11) |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation |
| `test/*` | Test additions |
| `chore/*` | Tooling, deps, CI |
| `ci/*` | CI configuration |

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `.ai-context/ARCHITECTURE.md` | Layer structure, dependency rules |
| `.ai-context/CODING_STANDARDS.md` | Python/TS conventions, quality gates |
| `.ai-context/PORT_CONTRACTS.md` | Repository, LLM, EventBus port interfaces |
| `.ai-context/DOMAIN_MODEL.md` | Entities, VOs, events, business rules |
| `.ai-context/SECURITY_RULES.md` | Secrets, PII, SQL safety, logging |
| `.ai-context/ERROR_PHILOSOPHY.md` | Classification rules, confidence thresholds |
| `.ai-context/API_CONTRACTS.md` | REST endpoints, TS types |
| `backend/infrastructure/di.py` | Composition root (DI wiring) |
| `backend/infrastructure/db/sqlite/database.py` | SQLite database and schema |

---

## Environment Variables

Create `.env` in `backend/` (copy from `.env.example`):

```bash
GEMINI_API_KEY=your-key
INSIGHT_DB_PATH=./data/insight_monitor.db
INSIGHT_CORS_ORIGINS=http://localhost:5173
SESSION_BUILDER_POLL_SECONDS=30
```

---

## Database (SQLite) — Auto-Created

The database file `backend/data/insight_monitor.db` is **auto-created** when the backend starts for the first time (via `Database._init_schema()`). No separate DB server needed. The `infrastructure/db-mvp/` docker-compose starts **sqlite-web** (viewer at :8081), not a database server.

---

## Debugging Tips

### Backend Not Starting?
- Check `GEMINI_API_KEY` is set (or inference disabled)
- Check port **8002** not in use
- Check SQLite DB path writable

### Tests Failing?
- Unit: Ensure InMemory repos used, no real DB
- Integration: Check `tmp_path` fixture for fresh DB
- Type errors: Run `mypy --strict` locally

### Types Out of Sync?
```bash
npm run generate:types
# Check dashboard/src/api/generated-types.ts
```

### Capture Agent Not Sending?
- Check `API_URL` env var (default: http://localhost:8002)
- Check backend health: `curl http://localhost:8002/health`
- Check X11 display: `xdotool getactivewindow`

---

## Real-Time Monitoring Visibility Quick Ref

| Interface | URL / Command | Key Visibility |
|-----------|---------------|----------------|
| Dashboard | `http://localhost:5173` | Agent status, sessions table (type, goal, confidence), 10s poll |
| Capture Agent | `npm run capture` | Events sent (window_focus, screenshot, input_activity) every 5s |
| Backend | `npm run backend` | Uvicorn access logs, background task cycles |
| sqlite-web | `http://localhost:8081` | Raw tables: `raw_events`, `sessions`, `intent_records` |

---

## Useful Links

- [CONTRIBUTING.md](CONTRIBUTING.md) — Full guide
- `.ai-context/` — Standards source of truth
- `docs/architecture/current-state.md` — Honest architecture assessment
- `docs/architecture/adr/` — Architecture Decision Records
- GitHub Issues — ARCH-1 through ARCH-11