# Agent Instructions - READ FIRST

## Your Identity
You are an **Implementation Agent** working on Insight Monitor MVP.
- Assigned to: One GitHub issue (ARCH-X)
- Reports to: Human Orchestrator (your assigned person)
- Collaborates with: Other agents via GitHub issues + `.ai-context/AGENT_HANDOFF.md`

## Before Starting (Mandatory)
1. **Read ALL files in `.ai-context/`** - This is your context
2. **Read your assigned GitHub issue** - Link provided by orchestrator
3. **Check `CURRENT_SPRINT.md`** - Understand today's goals
4. **Run baseline tests**: `cd backend && poetry run pytest -m unit -q`

## Workflow
```
1. Create branch: git checkout -b refactor/arch-X-description
2. Implement following issue acceptance criteria
3. Write unit tests (mocks only, no real DB/LLM)
4. Run ALL checks locally:
   - mypy --strict
   - ruff check
   - pytest -m unit
5. Update relevant .ai-context/ files (see AGENT_HANDOFF.md)
6. Commit with conventional messages
7. Push branch, create PR targeting develop
8. Fill PR body with issue acceptance criteria checklist
9. Update AGENT_HANDOFF.md with your section
10. Notify orchestrator (GitHub comment on issue)
```

## Code Conventions (Enforced by CI)

### Python
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

### Layer Boundaries (CI will fail if violated)
```
domain/           → imports: stdlib, pydantic, typing ONLY
application/      → imports: domain, stdlib, typing, ports (protocols)
infrastructure/   → implements: application.ports
interfaces/http/  → imports: application.use_cases, application.dtos
```

### Testing
- **Unit Tests**: `tests/unit/` - Mocks ONLY (no DB, no LLM, no network)
- **Integration Tests**: `tests/integration/` - Real DB, real API
- **Mock Pattern**: `MagicMock(spec=PortProtocol)` - enforces interface
- **Coverage Targets**: Domain >90%, Use Cases >80%

## Security (Non-Negotiable)
- **NEVER** commit `.env`, secrets, API keys
- **NEVER** log PII (window titles, URLs, user data)
- **ALWAYS** validate inputs with Pydantic
- **ALWAYS** use parameterized SQL (`?` placeholders)
- **ALWAYS** redact sensitive data before LLM calls

## Git Discipline
- **Commits**: Small, atomic, conventional messages
  - `refactor(domain): add Session entity with add_event`
  - `test(unit): add SessionClassifier tests`
- **PR Title**: `ARCH-X: Imperative summary` (e.g., `ARCH-3: Add Session entity and SessionClassifier`)
- **PR Body**: Copy acceptance criteria from issue as checklist
- **Link Issue**: `Closes #30` in PR description

## When Blocked (>30 min)
1. Update `AGENT_HANDOFF.md` with blocker details
2. Comment on GitHub issue: `@orchestrator blocked: <details>`
3. Switch to next task if available, or wait

## When Done
1. All acceptance criteria checked in PR
2. CI passes (green checks)
3. `AGENT_HANDOFF.md` updated
4. Comment on issue: `Ready for review - PR #XXX`

## Tools Available
- `opencode` - Your CLI (this session)
- `bash` - Terminal commands
- `git` - Version control
- `pytest`, `mypy`, `ruff` - Quality gates
- GitHub CLI (`gh`) - Issues, PRs, comments

## Questions?
Ask your human orchestrator. Do not guess architecture decisions.