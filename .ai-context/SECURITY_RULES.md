# Security Rules (Enforced by CI + Agent Compliance)

## Secrets Management
- **NEVER** hardcode API keys, tokens, passwords, connection strings
- Use `.env` files (gitignored) for local development
- Use environment variables in production
- `.env.example` documents required variables
- Rotate keys if accidentally committed

## Input Validation
- **All boundaries** validated with Pydantic:
  - API requests (`backend/routes/`)
  - CLI arguments (`capture/agent.py`)
  - LLM responses (`backend/pipeline/intent_parser.py`)
  - Database reads (repositories parse JSON safely)
- Reject unknown fields (`ConfigDict(extra='forbid')`)

## PII Protection
- **Window Titles/URLs**: May contain credentials, health info, private comms
- **Redaction Before LLM**: Strip/mask:
  - `://user:pass@` → `://[REDACTED]@`
  - Email regex → `[EMAIL]`
  - Phone regex → `[PHONE]`
  - Credit card / SSN patterns → `[REDACTED]`
  - Health keywords (configurable) → `[HEALTH]`
- **Screenshots**: Stored locally only. Never sent to LLM in MVP.
- **Input Metrics**: Aggregate only (clicks/min, keystrokes/min). No keystroke logging.

## SQL Safety
- **Parameterized Queries Only**: `cursor.execute("SELECT * FROM t WHERE id = ?", (id,))`
- **No String Interpolation**: `f"SELECT * FROM t WHERE id = {id}"` → BANNED
- Repositories use `?` placeholders exclusively

## Dependency Security
- `pip-audit` in CI (backend)
- `npm audit` in CI (frontend)
- Lockfiles committed: `poetry.lock`, `package-lock.json`
- No `*` version ranges in `pyproject.toml` / `package.json`

## Network
- **CORS**: Restricted to configured origins (`INSIGHT_CORS_ORIGINS`)
- **Rate Limiting**: 100 req/min per IP (FastAPI middleware post-MVP)
- **Timeouts**: HTTP clients 10s, LLM 30s
- **No SSRF**: Capture agent only calls configured `API_URL`

## Logging
- **No Secrets in Logs**: Filter `Authorization`, `api_key`, `password` headers
- **No PII in Logs**: Redact window titles, URLs in log output
- **Structured Logging**: JSON format for parsing
- **Levels**: DEBUG (dev), INFO (prod), WARNING/ERROR (alerts)

## Frontend
- **No API Keys in Browser**: All LLM calls via backend
- **CSP Headers**: `default-src 'self'; script-src 'self'`
- **HTTPS Only**: Production enforcement
- **No localStorage for Sensitive Data**: Session data in memory only