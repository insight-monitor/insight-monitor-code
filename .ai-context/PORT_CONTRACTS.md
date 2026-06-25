# Port Contracts (Application Layer Interfaces)

## Repository Ports (application/ports/repositories.py)

### EventRepositoryPort
```python
class EventRepositoryPort(Protocol):
    def insert(self, event: dict) -> int: ...
    def insert_batch(self, events: list[dict]) -> None: ...
    def find_by_session(self, session_id: str) -> list[dict]: ...
    def find_recent(self, limit: int) -> list[dict]: ...
    def find_unassigned(self, conn: Any = None) -> list[dict]: ...  # For BuildSessionsUseCase
    def assign_session(self, event_id: str, session_id: str, conn: Any = None) -> None: ...
```
**Returns**: Parsed Python objects (lists/dicts), **never JSON strings**.

### SessionRepositoryPort
```python
class SessionRepositoryPort(Protocol):
    def create(self, session: dict) -> str: ...
    def save(self, session: Session, conn: Any = None) -> None: ...  # Insert or update
    def find_by_id(self, session_id: str, conn: Any = None) -> Session | None: ...
    def find_all(self, status: str | None = None, limit: int = 50, conn: Any = None) -> list[Session]: ...
    def find_open_sessions(self, conn: Any = None) -> list[Session]: ...
```
**Returns**: Domain `Session` entities (not dicts).

### IntentRepositoryPort
```python
class IntentRepositoryPort(Protocol):
    def create(self, record: IntentRecord, conn: Any = None) -> str: ...
    def find_by_session(self, session_id: str, conn: Any = None) -> IntentRecord | None: ...
    def find_all(self, limit: int = 50, conn: Any = None) -> list[IntentRecord]: ...
```
**Returns**: Domain `IntentRecord` entities.

## LLM Port (application/ports/llm_port.py)
```python
class LLMPort(Protocol):
    def generate_structured(self, prompt: str) -> tuple[str, dict[str, Any]]: ...
    # Returns: (raw_text, parsed_json)
    # Raises: LLMServiceError (timeout, rate limit, parse error)
```

## Event Bus Port (application/ports/event_bus_port.py)
```python
class EventBusPort(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: type[DomainEvent], handler: callable) -> None: ...
    def publish_all(self, events: list[DomainEvent]) -> None: ...
```

## Prompt Builder Port (application/ports/prompt_port.py)
```python
class PromptBuilderPort(Protocol):
    def build(self, session: Session, events: list[RawEvent]) -> str: ...
```

## Intent Parser Port (application/ports/parser_port.py)
```python
class IntentParserPort(Protocol):
    def parse(self, llm_response: dict, session_id: SessionId, raw_text: str | None) -> IntentRecord: ...
    # Raises: IntentParserError
```