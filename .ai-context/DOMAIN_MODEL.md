# Domain Model (Source of Truth for ARCH-3)

## Entities

### Session
```python
# domain/entities/session.py
@dataclass
class Session:
    id: SessionId
    start_time: Timestamp
    end_time: Timestamp | None = None
    app_sequence: list[str] = field(default_factory=list)
    active_apps: list[str] = field(default_factory=list)
    event_count: int = 0
    screenshot_count: int = 0
    status: SessionStatus = SessionStatus.OPEN
    session_type: SessionType | None = None
    goal: str | None = None
    confidence: float | None = None
    _domain_events: list[DomainEvent] = field(default_factory=list, repr=False)

    def add_event(self, event: RawEvent, threshold: InactivityThreshold) -> None:
        """Update session state with new event. Check for closure."""
        # Logic from SessionBuilder._update_session_on_event + _check_close
        ...

    def close(self) -> None:
        if self.status == SessionStatus.CLOSED:
            return
        self.status = SessionStatus.CLOSED
        self.end_time = Timestamp.now()
        self._domain_events.append(SessionClosed(self.id))

    def classify(self, session_type: SessionType, goal: str, confidence: float) -> None:
        self.session_type = session_type
        self.goal = goal
        self.confidence = confidence
        self._domain_events.append(IntentInferred(self.id, session_type, goal, confidence))

    def pop_domain_events(self) -> list[DomainEvent]:
        events = self._domain_events
        self._domain_events = []
        return events
```

### IntentRecord
```python
# domain/entities/intent_record.py
@dataclass
class IntentRecord:
    record_id: RecordId
    session_id: SessionId
    timestamp: Timestamp
    session_type: SessionType
    goal: str
    goal_confidence: float
    friction_points: list[str] = field(default_factory=list)
    friction_confidence: float | None = None
    category: str = "ambiguous"
    category_confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    app_summary: dict = field(default_factory=dict)
    raw_timeline_summary: str = ""
    raw_llm_response: str | None = None
```

### RawEvent
```python
# domain/entities/raw_event.py
@dataclass
class RawEvent:
    event_id: EventId
    event_type: EventType
    timestamp: Timestamp
    source: str
    window_title: str | None = None
    process_name: str | None = None
    pid: int | None = None
    screenshot_path: str | None = None
    screenshot_thumbnail: str | None = None
    clicks_per_min: float | None = None
    keystrokes_per_min: float | None = None
    url: str | None = None
    browser_tab_title: str | None = None
    session_id: SessionId | None = None
    session_boundary_type: str | None = None
```

## Value Objects
- `SessionId(str)` - UUID, validates format
- `EventId(str)` - UUID, validates format
- `RecordId(str)` - UUID, validates format
- `Timestamp(datetime)` - ISO 8601, timezone-aware (UTC)
- `InactivityThreshold(int)` - Minutes, > 0, default 8
- `SessionStatus(Enum)` - OPEN, CLOSED
- `SessionType(Enum)` - SKILL_DEVELOPMENT, APPLIED_LEARNING, PEER_COLLABORATION, AMBIGUOUS, PERSONAL
- `EventType(Enum)` - WINDOW_FOCUS, SCREENSHOT, INPUT_ACTIVITY, URL_CONTEXT, SESSION_BOUNDARY, USER_AWAY, USER_BACK

## Domain Events
```python
# domain/events/session_events.py
@dataclass(frozen=True)
class SessionCreated:
    session_id: SessionId
    start_time: Timestamp

@dataclass(frozen=True)
class SessionClosed:
    session_id: SessionId
    end_time: Timestamp
    duration_seconds: float

@dataclass(frozen=True)
class IntentInferred:
    session_id: SessionId
    session_type: SessionType
    goal: str
    confidence: float
```

## Domain Services
### SessionClassifier
```python
# domain/services/session_classifier.py
class SessionClassifier:
    def __init__(self, threshold: InactivityThreshold):
        self.threshold = threshold

    def find_session_for_event(
        self, 
        event: RawEvent, 
        open_sessions: list[Session]
    ) -> Session | None:
        """Match event to existing session by time gap."""
        # Logic from SessionBuilder._find_session_for_event
        ...

    def should_close_session(self, session: Session, now: Timestamp) -> bool:
        """Check if session exceeded inactivity threshold."""
        # Logic from SessionBuilder._check_close
        ...
```

## Business Rules (from ERROR_PHILOSOPHY.md)
1. **False Positive Tolerance**: Near zero for productivity classification
2. **Sensitive Data**: Aggressive redaction even at context loss
3. **Default Stance**: Ambiguous > Misclassified
4. **Session Closure**: Inactivity > threshold (configurable, default 8 min)
5. **Intent Inference**: Only on CLOSED sessions, once per session