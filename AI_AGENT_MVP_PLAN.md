# AI Agent MVP Execution Plan

**Branch**: `chore/ai-agent-mvp-plan`
**Target**: MVP in 3 Days (Days 7-9 of 14)
**Team**: 4 Persons × 4 Parallel Agents = 16 Agent Slots
**Context**: `.ai-context/` (source of truth for all agents)

---

## 1. Team Structure & Agent Assignment

| Person | Role | Agents | Primary Issues | Backup Issues |
|--------|------|--------|----------------|---------------|
| **Person A** | Backend Lead + Orchestrator | Agent 1, 2 | ARCH-1, ARCH-2, ARCH-7, ARCH-10 | ARCH-6 |
| **Person B** | Domain/Application Lead | Agent 1, 2 | ARCH-3, ARCH-4 | ARCH-5 |
| **Person C** | Infrastructure Lead | Agent 1, 2 | ARCH-5, ARCH-6 | ARCH-2 |
| **Person D** | Frontend/QA Lead | Agent 1, 2 | ARCH-9, ARCH-11 | ARCH-10 |

**Each person orchestrates 2 agents simultaneously** (4 OpenCode sessions per person).
Total: 8 parallel agents working on critical path.

---

## 2. Dependency Graph (Critical Path)

```
DAY 7                          DAY 8                          DAY 9
┌─────────────────────────────────────────────────────────────────────┐
│ ARCH-1 (A1) ──→ ARCH-2 (A2) ──→ ARCH-3 (B1) ──→ ARCH-4 (B2)       │
│   │              │              │              │                    │
│   │              │              │              ├→ ARCH-5 (C1)       │
│   │              │              │              ├→ ARCH-6 (C2)       │
│   │              │              │              ├→ ARCH-9 (D1)       │
│   │              │              │              │                    │
│   │              │              │              └→ ARCH-7 (A1)       │
│   │              │              │                 │                │
│   │              │              │                 ├→ ARCH-11 (D2)   │
│   │              │              │                 ├→ ARCH-10 (A2)   │
│   │              │              │                 │                │
│   └──────────────┴──────────────┴─────────────────┘                │
│                    INTEGRATION & MVP DEMO                           │
└─────────────────────────────────────────────────────────────────────┘

PARALLEL (Optional): ARCH-8 (Capture Resilience) - Post-MVP if time
```

**Key**: ARCH-X must complete before dependents start. Agents wait for PR merge.

---

## 3. Daily Execution Plan

### Day 7 (Foundation) - 2026-06-25

| Time | Person A (2 Agents) | Person B (2 Agents) | Person C (2 Agents) | Person D (2 Agents) |
|------|---------------------|---------------------|---------------------|---------------------|
| 0-2h | A1: ARCH-1 impl<br>A2: ARCH-1 tests | B1: ARCH-3 entities<br>B2: ARCH-3 VOs | C1: Prep infra<br>C2: Prep DI | D1: Prep TS gen<br>D2: Prep test infra |
| 2-4h | A1: ARCH-1 PR<br>A2: ARCH-2 ports | B1: ARCH-3 events<br>B2: ARCH-3 classifier | C1: SQLite repo stubs<br>C2: Container stub | D1: datamodel-codegen setup<br>D2: test/unit structure |
| 4-6h | A1: Review A2 PR<br>A2: ARCH-2 PR | B1: ARCH-3 PR<br>B2: ARCH-3 tests | C1: InMemory repo stubs<br>C2: Container wiring | D1: Generation script<br>D2: Mock fixtures |
| 6-8h | **Merge ARCH-1, ARCH-2**<br>Update context | **Merge ARCH-3**<br>Update context | **Ready for Day 8** | **Ready for Day 8** |

**Day 7 Gates** (must pass before Day 8):
- [ ] `Database` no singleton, DI works
- [ ] `application/ports/repositories.py` exists
- [ ] `domain/` complete with tests
- [ ] All CI green on `develop`

### Day 8 (Application + Integration) - 2026-06-26

| Time | Person A | Person B | Person C | Person D |
|------|----------|----------|----------|----------|
| 0-2h | A1: ARCH-7 design<br>A2: ARCH-10 docs | B1: ARCH-4 use cases (Ingest, BuildSessions)<br>B2: ARCH-4 use cases (InferIntent, Close, Get, List) | C1: ARCH-5 SQLite impl<br>C2: ARCH-5 InMemory impl | D1: ARCH-9 generation<br>D2: ARCH-11 unit test patterns |
| 2-4h | A1: ARCH-7 impl<br>A2: ADR templates | B1: ARCH-4 PR<br>B2: ARCH-4 tests | C1: ARCH-5 PR<br>C2: ARCH-6 container impl | D1: ARCH-9 PR<br>D2: ARCH-11 test files |
| 4-6h | **Integration test**<br>Fix conflicts | **Merge ARCH-4** | **Merge ARCH-5, ARCH-6** | **Merge ARCH-9** |
| 6-8h | **E2E Smoke Test**<br>Capture→API→Dashboard | Update context | Update context | Update context |

**Day 8 Gates**:
- [ ] 6 use cases work with mocked ports
- [ ] SQLite + InMemory repos implement ports
- [ ] `container.py` wires all deps
- [ ] FastAPI routes use `Depends`
- [ ] TypeScript types generated
- [ ] E2E flow works

### Day 9 (Hardening + MVP) - 2026-06-27

| Time | All Persons (All Agents) |
|------|--------------------------|
| 0-2h | A1: ARCH-7 transactions<br>A2: ARCH-10 current-state.md<br>B1: Bug fixes<br>B2: Bug fixes<br>C1: Bug fixes<br>C2: Bug fixes<br>D1: ARCH-11 unit tests<br>D2: ARCH-11 coverage |
| 2-4h | Final integration testing<br>All PRs merged |
| 4-6h | **MVP Demo Prep**<br>Tag `mvp-architecture-complete` |
| 6-8h | Buffer / Presentation |

**Day 9 Gates**:
- [ ] Transactions atomic in use cases
- [ ] Docs reflect reality
- [ ] Unit tests >90% domain, >80% use cases
- [ ] E2E works: Capture → Dashboard shows intent
- [ ] All CI green

---

## 4. Human Orchestrator Responsibilities (Each Person)

### Before Each Day
- [ ] Review `CURRENT_SPRINT.md` for day's goals
- [ ] Assign agents to issues via GitHub comments
- [ ] Verify `.ai-context/` is current (pull `develop`)

### During Day (Continuous)
- [ ] Monitor agent PRs (GitHub notifications)
- [ ] **Architectural Review** (5 min/PR):
  - Layer boundaries respected?
  - Ports used correctly?
  - No singleton/globals?
  - Security rules followed?
- [ ] Merge approved PRs to `develop`
- [ ] Update `.ai-context/` after merges (or delegate to agent)
- [ ] Resolve merge conflicts (see Section 6)
- [ ] Unblock agents (decisions, clarification)

### End of Day
- [ ] Update `CURRENT_SPRINT.md` status
- [ ] Update `AGENT_HANDOFF.md` summary
- [ ] Tag `develop` if day complete: `git tag day-7-complete`
- [ ] Sync with other persons (15 min async via GitHub)

---

## 5. AI Agent Responsibilities

### Mandatory Startup (Each Session)
```bash
# 1. Read context
cat .ai-context/ARCHITECTURE.md
cat .ai-context/CODING_STANDARDS.md
cat .ai-context/DOMAIN_MODEL.md
cat .ai-context/PORT_CONTRACTS.md
cat .ai-context/SECURITY_RULES.md

# 2. Read assigned issue
gh issue view <issue-number>

# 3. Check sprint status
cat .ai-context/CURRENT_SPRINT.md

# 4. Run baseline tests
cd backend && poetry run pytest -m unit -q
```

### Implementation Rules
- **One issue = one branch = one PR**
- **Follow `.ai-context/AGENT_INSTRUCTIONS.md` exactly**
- **Update context files** when changing contracts (see `AGENT_HANDOFF.md`)
- **Write tests FIRST** (TDD preferred)
- **Run CI locally before push**: `mypy --strict && ruff check && pytest -m unit`

### PR Requirements
- Title: `ARCH-X: <imperative>`
- Body: Checklist from issue acceptance criteria
- Labels: `architecture`, `needs-review`
- Links: `Closes #<issue>`

### When Done
- Update `AGENT_HANDOFF.md` with your section
- Comment on issue: `Ready for review - PR #XXX`
- Wait for human approval

---

## 6. Merge Conflict Strategy

### Prevention
- **Small PRs** (<300 lines changed)
- **Short-lived branches** (merge same day)
- **Rebase daily**: `git fetch origin && git rebase origin/develop`
- **Communicate** in `AGENT_HANDOFF.md` when touching shared files

### Shared Files (High Conflict Risk)
| File | Owner | Coordination |
|------|-------|--------------|
| `.ai-context/ARCHITECTURE.md` | Person A | Only A updates |
| `.ai-context/PORT_CONTRACTS.md` | Person A/B | A owns, B proposes via PR |
| `.ai-context/DOMAIN_MODEL.md` | Person B | Only B updates |
| `.ai-context/API_CONTRACTS.md` | Person D | Only D updates (auto-gen) |
| `backend/container.py` | Person C | Only C updates |
| `backend/main.py` | Person C | Only C updates |

### Conflict Resolution
1. Agent detects conflict on rebase → **STOP**
2. Update `AGENT_HANDOFF.md` with conflict details
3. Tag human orchestrator: `@person-a conflict in ARCHITECTURE.md`
4. Human resolves, pushes resolution
5. Agent rebases and continues

### Emergency: Force Push Protection
- Branch protection: Require PR, require CI, require review
- No force push to `develop` or `main`
- If `develop` broken: Revert commit, fix in new branch

---

## 7. Continuous Integration Pipeline

### GitHub Actions (`.github/workflows/ai-agent-ci.yml`)
```yaml
# Runs on every PR to develop
# Jobs: backend, frontend, security
# Must pass before merge
```

### Local Pre-Push (Agent runs)
```bash
cd backend
poetry run mypy --strict .
poetry run ruff check .
poetry run pytest -m unit --tb=short -q

cd ../dashboard
npm run typecheck
npm run lint
npm run build
```

### Quality Gates (Non-Negotiable)
| Check | Threshold |
|-------|-----------|
| mypy --strict | 0 errors |
| ruff check | 0 errors |
| pytest -m unit | 100% pass, <30s |
| pytest -m integration | 100% pass |
| npm run typecheck | 0 errors |
| npm run build | Success |
| Secret scan (gitleaks) | 0 findings |

---

## 8. Communication Protocol

### GitHub Issues (Primary)
- **Agent → Orchestrator**: Comment on issue with `@person-x`
- **Orchestrator → Agent**: Assign issue, comment with direction
- **Cross-team**: Comment on dependent issue

### AGENT_HANDOFF.md (Async Context)
- Updated by agents at key milestones
- Read by downstream agents before starting
- Single source of truth for decisions

### Daily Sync (15 min async)
- Each person posts status in `CURRENT_SPRINT.md` issue comments
- Format: `Person X: Day N - Done: ARCH-1,2 | In Progress: ARCH-3 | Blocked: -`

---

## 9. Tool Setup (Per Person)

### Windows (PowerShell)
```powershell
# Install tools
winget install Git.Git
winget install Python.Python.3.11
winget install OpenJS.NodeJS.LTS
# Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
# OpenCode
# Follow https://opencode.ai/install
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y git python3.11 python3.11-venv nodejs npm
curl -sSL https://install.python-poetry.org | python3 -
# OpenCode per docs
```

### Environment Variables (All)
```bash
export NVIDIA_API_KEY="your-free-key"
export INSIGHT_DB_PATH="./backend/data/insight_monitor.db"
export GEMINI_API_KEY="your-key"  # For LLM tests
```

### OpenCode Multi-Session (Per Person - 4 terminals)
```bash
# Terminal 1: Orchestrator view
opencode

# Terminal 2-5: Agents (tmux/screen recommended)
tmux new-session -d -s agent-1 'cd insight-monitor-code && opencode --session backend-1'
tmux new-session -d -s agent-2 'cd insight-monitor-code && opencode --session backend-2'
tmux new-session -d -s agent-3 'cd insight-monitor-code && opencode --session frontend-1'
tmux new-session -d -s agent-4 'cd insight-monitor-code && opencode --session qa-1'

# Attach to monitor
tmux attach -t agent-1
```

### Warp.dev (Optional - Better Terminal)
- Free for individuals
- AI-powered command suggestions
- Session sharing for pair debugging
- Install: `curl -fsSL https://warp.dev/install.sh | sh`

---

## 10. Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Agent writes bad code | High | Strict CI + 5-min human arch review |
| Context drift | Medium | `.ai-context/` updated at each merge |
| NVIDIA API limit | Low | Fallback: Ollama local (CodeLlama 7B) |
| Integration fails Day 9 | Medium | Daily smoke tests from Day 7 |
| TS/backend drift | Medium | ARCH-9 runs on every backend PR |
| Time overrun | High | **Cut scope**: Defer ARCH-7,8,11 to post-MVP |
| Merge conflicts | Medium | Small PRs, daily rebase, file ownership |

### MVP Minimum (If Desperate)
- ARCH-1,2,3,4,6 ONLY
- Capture agent works (no resilience)
- Dashboard shows sessions + intent
- Unit tests for domain + use cases
- Docs updated

---

## 11. Immediate Action Items (Do Now)

### Person A (Backend Lead)
1. [ ] Create `.github/workflows/ai-agent-ci.yml` from template
2. [ ] Set up branch protection on `develop`
3. [ ] Assign ARCH-1, ARCH-2 to agents via GitHub comments
4. [ ] Launch Agent 1, 2 sessions

### Person B (Domain Lead)
1. [ ] Review `DOMAIN_MODEL.md` for completeness
2. [ ] Assign ARCH-3 to agents
3. [ ] Launch Agent 1, 2 sessions

### Person C (Infra Lead)
1. [ ] Review `PORT_CONTRACTS.md` for completeness
2. [ ] Prepare `container.py` skeleton
3. [ ] Launch Agent 1, 2 sessions (wait for Day 8)

### Person D (Frontend/QA Lead)
1. [ ] Set up `datamodel-codegen` in dashboard
2. [ ] Create `tests/unit/` structure
3. [ ] Launch Agent 1, 2 sessions (wait for Day 8)

### All Persons
1. [ ] Clone repo, checkout `chore/ai-agent-mvp-plan`
2. [ ] Install dependencies: `cd backend && poetry install && cd ../dashboard && npm ci`
3. [ ] Verify CI runs: `gh workflow run ai-agent-ci.yml`
4. [ ] Read `.ai-context/AGENT_INSTRUCTIONS.md`

---

## 12. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Unit test speed | <30s | `pytest -m unit` |
| Domain coverage | >90% | `pytest --cov=backend/domain` |
| Use case coverage | >80% | `pytest --cov=backend/application` |
| Type safety | 0 errors | `mypy --strict` |
| Lint | 0 errors | `ruff check` / `npm run lint` |
| Build | Success | `npm run build` |
| E2E flow | Works | Manual: Capture→Dashboard |
| Security | 0 findings | `gitleaks` + `trufflehog` |
| Docs current | Yes | `CURRENT_SPRINT.md` + ADRs |

---

## 13. Reference Links

- **Master Issue**: #41 (ARCH-0)
- **Architecture Issues**: #30-#40
- **Context Dir**: `.ai-context/`
- **Sprint Tracking**: `CURRENT_SPRINT.md`
- **Handoff Log**: `AGENT_HANDOFF.md`

---

## 14. Start Command

When ready, each person runs:
```bash
cd insight-monitor-code
git checkout chore/ai-agent-mvp-plan
git pull origin chore/ai-agent-mvp-plan

# Launch agents (adjust for your 4 sessions)
tmux new-session -d -s a1 'opencode --session agent-1'
tmux new-session -d -s a2 'opencode --session agent-2'
tmux new-session -d -s a3 'opencode --session agent-3'
tmux new-session -d -s a4 'opencode --session agent-4'

# Give first prompt to each agent:
# "Read .ai-context/AGENT_INSTRUCTIONS.md. Your issue is #XX. Begin."
```

**Good luck. Ship the MVP.**
