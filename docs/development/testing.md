# Testing Guide

## Running Tests

```bash
cd backend
poetry run pytest -v
```

The `-v` flag prints every individual test function and its result.

### Test markers

The project uses pytest custom markers:

```bash
# Unit tests only — uses InMemory repos, no disk I/O, no network (< 2s)
poetry run pytest -m unit -v

# Integration tests only — uses real SQLite on disk
poetry run pytest -m integration -v

# All tests
poetry run pytest -v
```

## Test Structure

All tests live in `backend/tests/` (unit + integration) and `tests/` (E2E):

| File | Tests | Marker | What it covers |
|------|-------|--------|----------------|
| `test_health.py` | 14 | `unit` | Health endpoint + agent heartbeat functions |
| `test_unit_pipeline.py` | 24 | `unit` | PromptBuilder, IntentParser, LLMService, InferIntentUseCase |
| `test_unit_use_cases.py` | 10 | `unit` | IngestEvent, BuildSessions, GetSession use cases |
| `test_unit_routes.py` | 12 | `unit` | Event, Session, Tickets route endpoints via TestClient |
| `test_unit_tickets.py` | 20 | `unit` | ManageTicketsUseCase full CRUD + comments + stats |
| `test_wayland_window_tracker.py` | 19 | `unit` | WaylandWindowTracker, display detection, factory |
| `test_event_sender.py` | 9 | `unit` | EventSender.send_heartbeat + CaptureAgent heartbeat delegation |
| `test_new_components.py` | 7 | `unit` + 1 `integration` | LLM services, inference pipeline with mock/real LLM |
| `test_e2e.py` | 1 | `integration` | Full flow: events → session → inference → API |
| `scripts/test_e2e_gemini.py` | — | manual | Real LLM E2E test (run manually) |

**Total: ~116 tests.**

## Naming Convention

Every test function **must** follow this pattern:

```
test_should_<expected behavior>_when_<condition>
```

Examples:

```python
def test_should_return_200_with_event_id_when_posting_valid_event(self, client):
def test_should_reject_invalid_event_type(self):
def test_should_return_empty_list_when_no_sessions_exist(self, client):
def test_should_ignore_duplicate_event_id(self, event_repo):
```

This makes test output self-documenting. A failure reads as:
```
FAILED test_should_return_404_when_session_does_not_exist
```

### Rules

1. **Start with** `test_should_`
2. **Describe the expected outcome**, not the action
3. **End with the precondition** after `_when_`
4. Use **complete sentences** — no abbreviations

| Instead of | Write |
|------------|-------|
| `test_empty` | `test_should_return_empty_list_when_no_events_exist` |
| `test_create_event` | `test_should_return_200_with_event_id_when_posting_valid_event` |
| `test_not_found` | `test_should_return_404_when_session_does_not_exist` |

## Writing Tests

### API tests (integration)

Test the full request-response cycle through FastAPI's `TestClient` with DI overrides (InMemory repositories):

```python
@pytest.mark.integration
def test_should_return_200_when_creating_valid_event(self, client):
    response = client.post("/events", json={
        "event_id": str(uuid4()),
        "event_type": "window_focus",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "test",
    })
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == {"status": "ok", "event_id": ...}
```

### Use case tests (unit)

Test use cases directly with InMemory repository fixtures — zero disk, zero network:

```python
@pytest.mark.unit
def test_should_insert_event_and_return_event_id(self, event_repo):
    raw = RawEvent(
        event_id="ev-test-01",
        event_type=EventType.WINDOW_FOCUS,
        timestamp=datetime.now(timezone.utc),
        source="capture-agent",
    )
    use_case = IngestEventUseCase(event_repo)
    result = use_case.execute(raw)
    assert result == "ev-test-01"
    assert len(event_repo.find_recent()) == 1
```

### Docstrings

Every test class and test function must have a docstring explaining what it validates:

```python
class TestCreateEvent:
    """POST /events — single event ingestion."""

    def test_should_return_200_with_event_id_when_posting_valid_event(self, client):
        """A valid event body returns status ok and the assigned event_id."""
```

## How CI Runs Tests

The file `.github/workflows/ci.yml` defines 5 jobs. The relevant one for tests is **python-test**:

```yaml
python-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: abatilo/actions-poetry@v3
      - run: poetry install
      - run: poetry run pytest -v --tb=short
```

It runs automatically on:
- Every push to `develop`
- Every pull request targeting `develop` or `main`

Check results at: `https://github.com/insight-monitor/insight-monitor-code/actions`

## Adding a New Test

1. Pick the right file (or create a new `test_*.py`)
2. Name it `test_should_<behavior>_when_<condition>`
3. Add a class docstring describing the endpoint/module
4. Add a function docstring describing the specific case
5. Add the appropriate marker: `@pytest.mark.unit` (no disk/network, uses InMemory repos) or `@pytest.mark.integration` (uses SQLite or real IO)
6. Run `poetry run pytest -v` to verify it passes
7. Run `poetry run ruff check .` to verify lint passes