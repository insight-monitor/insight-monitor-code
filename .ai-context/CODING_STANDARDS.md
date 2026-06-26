# Coding Standards (Enforced by CI)

## Python (Backend)
- **Type Hints**: Required everywhere. `mypy --strict` must pass.
- **Formatting**: `ruff format` (Black-compatible)
- **Linting**: `ruff check` (includes isort, flake8, pyupgrade)
- **Imports**: Absolute from `backend.` root. No relative imports across layers.
- **Async**: Use `async/await` for I/O. Background tasks in `main.py` lifespan.
- **No Globals**: No module-level singletons. Use DI container.
- **Error Handling**: Custom exceptions per module. No bare `except:`.
- **Docstrings**: Google style for public APIs (classes, functions, methods).
- **Module Docstrings**: Required at top of every file — one sentence describing purpose and key exports.
- **Private Methods**: Docstring only if logic is non-obvious; prefer self-documenting names.
- **Inline Comments**: Rare. Explain *why* (constraints, business rules), not *what*.

## TypeScript (Frontend)
- **Strict Mode**: `tsconfig.json` strict: true
- **Formatting**: Prettier (via `npm run format`)
- **Linting**: ESLint (via `npm run lint`)
- **Types**: Generated from Pydantic (ARCH-9). Never manual sync.
- **Components**: Functional + hooks. No class components.
- **State**: `react-query` (server), `zustand` (client UI only)
- **Doc Comments**: TSDoc for public APIs (functions, classes, interfaces, types).
- **Module Comments**: One-line file header describing purpose.
- **Inline Comments**: Minimal. Prefer clear naming and type signatures.

## Commenting Principles (Both Languages)
- **Self-documenting code > comments** — rename before commenting.
- **Comment *why*, not *what*** — explain intent, constraints, edge cases.
- **No redundant comments** — if code reads like English, don't annotate it.
- **Examples belong in tests**, not signatures.

### Examples

```python
# Good: module docstring
"""Intent classification pipeline for user activity sessions."""

# Good: public API docstring
def classify_intent(events: list[RawEvent], context: SessionContext) -> IntentRecord:
    """Classify user intent from a sequence of raw events.

    Args:
        events: Chronological raw events within a session window.
        context: Aggregated session metadata (duration, app switches, etc.).

    Returns:
        Structured intent record with confidence and reasoning.

    Raises:
        ClassificationError: If LLM response is malformed or low confidence.
    """
    ...

# Bad: redundant inline comment
events = events.filter(e => e.timestamp > cutoff)  # filter old events

# Good: explains business constraint
# Keep only events within the active session window (30min inactivity timeout)
events = events.filter(e => e.timestamp > cutoff)
```

```typescript
// Good: module header
/** Intent inference pipeline — orchestrates LLM classification and session building. */

// Good: TSDoc for public API
/**
 * Classifies user intent from a sequence of raw events.
 * @param events - Chronological raw events within a session window
 * @param context - Aggregated session metadata
 * @returns Structured intent record with confidence and reasoning
 * @throws ClassificationError if LLM response is malformed or low confidence
 */
export async function classifyIntent(
  events: RawEvent[],
  context: SessionContext
): Promise<IntentRecord> { ... }

// Bad: redundant comment
const filtered = events.filter(e => e.timestamp > cutoff); // filter old events
```

## Git Conventions
- **Branch**: `refactor/arch-X-description` | `feat/description` | `fix/description` | `docs/description`
- **Commits**: Conventional Commits
  - `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `ci:`
  - Scope optional: `feat(api): add session endpoint`
- **PR Title**: `ARCH-X: Imperative summary` (links issue)
- **PR Body**: Checklist from issue acceptance criteria

## Layer Boundaries (Enforced by Architecture Tests)
```python
# FORBIDDEN imports (will fail CI):
# domain/ importing from application/, infrastructure/, interfaces/
# application/ importing from infrastructure/, interfaces/
# infrastructure/ importing from interfaces/

# ALLOWED:
# infrastructure/ implements application.ports
# interfaces/ depends on application.use_cases
```

## Security Rules
- **No Secrets**: Never commit API keys, tokens, passwords. Use `.env` (gitignored).
- **Input Validation**: Pydantic models at ALL boundaries (API, CLI, LLM response).
- **PII Redaction**: Window titles, URLs → redact before LLM (see ERROR_PHILOSOPHY.md).
- **SQL Injection**: Never string-interpolate SQL. Use parameterized queries.
- **Dependencies**: `pip-audit` / `npm audit` in CI. Pin versions in lockfiles.