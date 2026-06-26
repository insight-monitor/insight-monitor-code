# Coding Standards (Enforced by CI)

## Python (Backend)
- **Type Hints**: Required everywhere. `mypy --strict` must pass.
- **Formatting**: `ruff format` (Black-compatible)
- **Linting**: `ruff check` (includes isort, flake8, pyupgrade)
- **Imports**: Absolute from `backend.` root. No relative imports across layers.
- **Async**: Use `async/await` for I/O. Background tasks in `main.py` lifespan.
- **No Globals**: No module-level singletons. Use DI container.
- **Error Handling**: Custom exceptions per module. No bare `except:`.
- **Docstrings**: Google style for public APIs. Private methods: inline comments if complex.

## TypeScript (Frontend)
- **Strict Mode**: `tsconfig.json` strict: true
- **Formatting**: Prettier (via `npm run format`)
- **Linting**: ESLint (via `npm run lint`)
- **Types**: Generated from Pydantic (ARCH-9). Never manual sync.
- **Components**: Functional + hooks. No class components.
- **State**: `react-query` (server), `zustand` (client UI only)

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