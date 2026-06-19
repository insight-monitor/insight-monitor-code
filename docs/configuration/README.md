---
title: Configuration Model
type: reference
domain: configuration
priority: high
status: review
version: 0.1.0
---

# Configuration Model

## Configuration layers (lowest to highest priority)

### 1. System defaults
Hardcoded baseline: application categories, signal types, inference thresholds. Not modifiable by the user. Defined by the application source code.

### 2. Organization policies (enterprise only)
Applied by administrators: minimum required signals during working hours, mandatory redaction rules, allowed configuration range for employees.

### 3. User preferences
User-defined context: role, objectives, app classifications, schedule. Stored locally by default. Can be synced if user opts in.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `INSIGHT_DB_PATH` | `backend/data/insight_monitor.db` | SQLite database path |
| `INSIGHT_CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `INSIGHT_API_VERSION` | `0.1.0` | API version string |
| `GEMINI_API_KEY` | — | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model identifier |
| `INFERENCE_TIMEOUT_SEC` | `30` | LLM call timeout |
| `INFERENCE_MAX_RETRIES` | `3` | LLM call retry count |
| `SESSION_INACTIVITY_GAP_MIN` | `8` | Minutes of inactivity to split sessions |
| `BACKEND_PORT` | `8002` | Server port |

See `.env.example` in the project root for a template.

## Configuration delivery methods

### Method A: GUI/Interface (recommended for future)
Dedicated settings panel in the application.

### Method B: Environment variables (current MVP)
All configuration is via environment variables and `.env` file.

## Configuration scope

| Setting | Enterprise | Personal |
|---|---|---|
| App classification | Limited range | Full control |
| Objectives | May be required | Optional |
| Schedule | Enforced hours | Flexible |
| Custom prompts | Not allowed | Allowed within limits |
| Data retention | Defined by org | User-defined |
| Export/delete data | Limited by policy | Full rights |
