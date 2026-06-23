# Testing Guide

## Running Tests

```bash
cd backend
poetry run pytest -v
```

The `-v` flag prints every individual test function and its result.

## Test Structure

All tests live in `backend/tests/`:

| File | Tests | What it covers |
|------|-------|----------------|
| `test_health.py` | 1 | `GET /health` endpoint |
| `test_models.py` | 10 | Pydantic model validation (RawEvent, IntentRecord) |
| `test_events.py` | 13 | `POST/GET /events`, `/events/batch`, `/events/session/{id}` |
| `test_sessions.py` | 10 | `GET /sessions`, `GET /sessions/{id}`, close, intent |
| `test_repositories.py` | 17 | Database CRUD, JSON field parsing, edge cases |

**Total: 62 tests.**

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

### API tests

Test the full request-response cycle through FastAPI's `TestClient`:

```python
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

### Repository tests

Test database logic directly through the repository class:

```python
def test_should_insert_event_and_retrieve_by_find_recent(self, event_repo):
    event_id = str(uuid4())
    event_repo.insert({"event_id": event_id, ...})
    events = event_repo.find_recent()
    assert len(events) == 1
    assert events[0]["event_id"] == event_id
```

### Model tests

Test Pydantic validation with `pytest.raises`:

```python
def test_should_reject_invalid_event_type(self):
    with pytest.raises(ValidationError, match="event_type"):
        RawEvent(event_id="...", event_type="invalid", ...)
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
5. Run `poetry run pytest -v` to verify it passes
6. Run `poetry run ruff check .` to verify lint passes
