# Contributing to Insight Monitor

**Welcome!** This guide covers everything you need to contribute effectively: architecture, development workflow, testing, PR process, and review standards.

---

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/insight-monitor/insight-monitor-code.git
cd insight-monitor-code

# 2. Backend dependencies
cd backend && poetry install && cd ..

# 3. Frontend dependencies
cd frontend && npm install && cd ..

# 4. Run tests to verify setup
cd backend && poetry run pytest -m unit -q
```

---

## Architecture Overview

Insight Monitor follows **Clean Architecture** with strict dependency inversion:

```
domain/           → Pure business logic (NO external deps)
application/      → Use cases (orchestration, NO infra)
infrastructure/   → Concrete implementations (SQLite, Gemini, etc.)
interfaces/       → Delivery mechanisms (FastAPI, Capture agent)
```

**Dependency Rule**: `domain ← application ← infrastructure` (interfaces depend on application)

### Key Directories

| Layer | Path | Responsibility |
|-------|------|----------------|
| Domain | `backend/domain/` | Entities, value objects, domain events, services |
| Application | `backend/application/` | Use cases, ports (interfaces), DTOs |
| Infrastructure | `backend/infrastructure/` | SQLite repos, InMemory repos, DI container, Unit of Work |
| Interfaces (HTTP) | `backend/routes/` | FastAPI routers (thin, DI only) |
| Interfaces (CLI) | `capture/` | Capture agent (Python, HTTP to API) |
| Frontend | `frontend/` | React + TypeScript + Tailwind |

### Forbidden Imports (CI Enforced)
- `domain/` importing from `application/`, `infrastructure/`, `interfaces/`
- `application/` importing from `infrastructure/`, `interfaces/`
- `infrastructure/` importing from `interfaces/`

---

## Development Workflow

### 1. Branching Strategy (GitFlow)

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Stable releases only | PR + Review + CI |
| `develop` | Integration branch | CI required |
| `refactor/arch-X-*` | Architecture tasks | PR to `develop` |
| `feat/*` | New features | PR to `develop` |
| `fix/*` | Bug fixes | PR to `develop` |
| `docs/*` | Documentation | PR to `develop` |

**Rules**:
- Branch from `develop`
- One topic per branch
- Rebase onto `develop` before PR
- Squash & merge via PR

### 2. Commit Convention

Use **Conventional Commits**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Adding tests |
| `chore` | Tooling, deps, CI |
| `ci` | CI configuration |

**Examples**:
```
feat(api): add session close endpoint
fix(capture): handle Wayland window detection
refactor(domain): extract SessionClassifier service
test(unit): add BuildSessionsUseCase tests
```

### 3. Pull Request Process

1. **Create PR** targeting `develop`
2. **PR Title**: `ARCH-X: Imperative summary` (for architecture) or `feat/fix/refactor: summary`
3. **PR Body**: Copy acceptance criteria from issue as checklist
4. **Link Issue**: `Closes #<issue-number>`
5. **CI Must Pass**: All checks green
6. **Review**: At least 1 approval (self-approval allowed if reviewer is author)
7. **Merge**: Squash & merge, branch deleted

---

## Code Standards

### Python (Backend)

**File**: `.ai-context/CODING_STANDARDS.md`

```python
# Types: ALWAYS
def find_session(event: RawEvent, sessions: list[Session]) -> Session | None:
    ...

# Imports: Absolute from backend root
from backend.domain.entities.session import Session
from backend.application.ports.repositories import SessionRepositoryPort

# Errors: Custom exceptions
class SessionNotFoundError(Exception): ...

# Async: For I/O only
async def execute(self) -> Result: ...

# No globals, no singletons
# Use DI: __init__(self, repo: SessionRepositoryPort)
```

**Quality Gates** (run before push):
```bash
cd backend
poetry run mypy --strict .
poetry run ruff check .
poetry run pytest -m unit --tb=short -q
```

### TypeScript (Frontend)

**File**: `.ai-context/CODING_STANDARDS.md`

- Strict mode: `tsconfig.json` strict: true
- Types generated from Pydantic (ARCH-9) — never manual sync
- Components: Functional + hooks only
- State: `react-query` (server), `zustand` (client UI)

**Quality Gates**:
```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

---

## Testing Strategy

### Test Types

| Type | Location | Runs | Isolation |
|------|----------|------|-----------|
| Unit | `backend/tests/` + `@pytest.mark.unit` | < 2s | InMemory repos, no DB, no network |
| Integration | `backend/tests/` + `@pytest.mark.integration` | ~30s | Real SQLite, real API |
| E2E | `tests/` | Manual | Full stack |

### Writing Tests

**Unit Test** (use case with InMemory repos):
```python
@pytest.mark.unit
def test_should_create_session_from_unassigned_event(self, event_repo, session_repo):
    event_repo.insert({"event_id": "ev-1", "event_type": "focus", ...})
    use_case = BuildSessionsUseCase(event_repo, session_repo)
    use_case.execute()
    assert len(session_repo.find_all()) == 1
```

**Integration Test** (full API with DI overrides):
```python
@pytest.mark.integration
def test_should_return_200_when_creating_valid_event(self, client):
    response = client.post("/events", json={"event_id": "ev-1", ...})
    assert response.status_code == 200
```

### Coverage Targets
- Domain: > 90%
- Use Cases: > 80%
- Run: `poetry run pytest --cov=backend/domain --cov=backend/application`

---

## Architecture Patterns

### Use Case Pattern
Every business operation = one Use Case class:
```python
class IngestEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event: RawEvent) -> str:
        event_dict = event.model_dump()
        event_dict["timestamp"] = event.timestamp.isoformat()
        self.event_repo.insert(event_dict)
        return event.event_id
```

**Rules**:
- Single responsibility
- Input DTO → Output DTO
- Depend ONLY on ports (protocols)
- No framework imports (FastAPI, SQLAlchemy, etc.)

### Repository Pattern
Ports in `application/ports/`, implementations in `infrastructure/`:
```python
# Port (application/ports/repositories.py)
class IEventRepository(Protocol):
    def insert(self, event: dict) -> int: ...
    def find_by_session(self, session_id: str) -> list[dict]: ...

# SQLite Implementation (infrastructure/db/sqlite/repositories.py)
class EventRepository(IEventRepository):
    def __init__(self, db: Database): ...

# InMemory Implementation (infrastructure/db/in_memory/repositories.py)
class InMemoryEventRepository(IEventRepository):
    def __init__(self): ...
```

### Dependency Injection
Composition root in `infrastructure/di.py`:
```python
@lru_cache(maxsize=1)
def get_db() -> Database:
    return Database(settings.db_path)

def get_event_repository() -> IEventRepository:
    return EventRepository(get_db())

def get_ingest_event_use_case() -> IngestEventUseCase:
    return IngestEventUseCase(get_event_repository())
```

Routes use FastAPI `Depends`:
```python
@router.post("")
async def create_event(
    event: RawEvent,
    use_case: IngestEventUseCase = Depends(get_ingest_event_use_case)
):
    return {"status": "ok", "event_id": use_case.execute(event)}
```

### Transaction Boundaries
Use `UnitOfWork` for atomic operations:
```python
from backend.infrastructure.db.sqlite.unit_of_work import UnitOfWork

with UnitOfWork(db) as uow:
    uow.events.insert(event)
    uow.sessions.create(session)
    uow.commit()  # explicit commit
# Auto-rollback on exception
```

---

## Security Checklist (Every PR)

- [ ] No hardcoded secrets, API keys, passwords
- [ ] All inputs validated with Pydantic
- [ ] PII redacted before LLM calls (see `.ai-context/ERROR_PHILOSOPHY.md`)
- [ ] Parameterized SQL only (`?` placeholders)
- [ ] No PII in logs (window titles, URLs redacted)
- [ ] Dependencies audited (`pip-audit`, `npm audit`)

---

## Documentation Standards

### Code Documentation
- **Public APIs**: Google-style docstrings
- **Private methods**: Inline comments if complex
- **Architecture decisions**: ADR in `docs/architecture/adr/`

### When to Update Docs
| Change | Docs to Update |
|--------|----------------|
| New use case | `ARCHITECTURE.md`, `PORT_CONTRACTS.md` |
| New entity/VO | `DOMAIN_MODEL.md` |
| API change | `API_CONTRACTS.md`, run ARCH-9 generation |
| Security rule | `SECURITY_RULES.md`, `ERROR_PHILOSOPHY.md` |
| Coding standard | `CODING_STANDARDS.md` |

---

## Review Standards (For Reviewers)

When reviewing a PR, verify:

### Architecture
- [ ] Layer boundaries respected (no forbidden imports)
- [ ] Use cases depend only on ports, not concrete implementations
- [ ] No new singletons or global state
- [ ] Domain logic in domain layer, not in routes or pipelines

### Code Quality
- [ ] `mypy --strict` passes
- [ ] `ruff check` passes
- [ ] Type hints everywhere (Python)
- [ ] Custom exceptions, no bare `except:`
- [ ] Conventional commit messages

### Testing
- [ ] Unit tests for new use cases (`@pytest.mark.unit`)
- [ ] InMemory repos used in unit tests (no real DB)
- [ ] Mock pattern: `MagicMock(spec=PortProtocol)`
- [ ] Coverage targets met

### Security
- [ ] No secrets committed
- [ ] Input validation at all boundaries
- [ ] PII redaction before LLM
- [ ] Parameterized SQL

### Documentation
- [ ] `.ai-context/` files updated if contracts changed
- [ ] ADR created for architectural decisions
- [ ] API contracts updated if endpoints changed

---

## Common Tasks

### Add a New Use Case
1. Create port in `application/ports/` (if new dependency)
2. Implement use case in `application/use_cases/`
3. Add to `infrastructure/di.py`
4. Create route in `backend/routes/` using `Depends`
5. Write unit tests with InMemory repos
6. Update `PORT_CONTRACTS.md` and `ARCHITECTURE.md`

### Add a New Entity
1. Define in `domain/entities/` (Pydantic model)
2. Add value objects in `domain/value_objects/`
3. Create repository port in `application/ports/repositories.py`
4. Implement SQLite + InMemory repositories
5. Register in `infrastructure/di.py`
6. Run ARCH-9 type generation: `npm run generate:types`

### Modify Database Schema
1. Update `infrastructure/db/sqlite/database.py` `_init_schema()`
2. Add migration in `_migrate()`
3. Update repository methods
4. Update `docs/data-model/database-schema.md`

---

## Getting Help

- **Architecture questions**: Check `.ai-context/ARCHITECTURE.md`, `PORT_CONTRACTS.md`
- **Domain logic**: Check `.ai-context/DOMAIN_MODEL.md`
- **Security**: Check `.ai-context/SECURITY_RULES.md`, `ERROR_PHILOSOPHY.md`
- **Blocked > 30 min**: Update `AGENT_HANDOFF.md`, comment on GitHub issue with `@orchestrator`

---

## References

- `.ai-context/` — Source of truth for all standards
- `docs/architecture/` — Architecture docs, ADRs, current state
- `docs/development/testing.md` — Testing guide
- GitHub Issues — Task tracking (ARCH-1 through ARCH-11)
- PR #43, #45, #46 — Recent architecture migration references