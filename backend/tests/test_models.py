from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.models.raw_event import RawEvent, EventType
from backend.models.intent_record import IntentRecord


class TestRawEvent:
    def test_valid_raw_event(self):
        data = {
            "event_id": str(uuid4()),
            "event_type": EventType.WINDOW_FOCUS,
            "timestamp": datetime.now(timezone.utc),
            "source": "capture-agent",
            "window_title": "VS Code",
            "process_name": "code",
            "pid": 1234,
            "clicks_per_min": 15.5,
            "keystrokes_per_min": 42.3,
        }
        event = RawEvent(**data)
        assert event.event_type == EventType.WINDOW_FOCUS
        assert event.pid == 1234
        assert event.screenshot_path is None

    def test_minimal_raw_event(self):
        event = RawEvent(
            event_id=str(uuid4()),
            event_type=EventType.SCREENSHOT,
            timestamp=datetime.now(timezone.utc),
            source="capture-agent",
        )
        assert event.window_title is None

    def test_invalid_event_type(self):
        with pytest.raises(ValidationError):
            RawEvent(
                event_id=str(uuid4()),
                event_type="invalid",
                timestamp=datetime.now(timezone.utc),
                source="test",
            )

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RawEvent()


class TestIntentRecord:
    def test_valid_intent_record(self):
        record = IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type="applied_learning",
            goal="Build React component",
            goal_confidence=0.85,
        )
        assert record.session_type == "applied_learning"
        assert record.category == "ambiguous"

    @pytest.mark.parametrize("session_type", [
        "skill_development", "applied_learning",
        "peer_collaboration", "ambiguous", "personal",
    ])
    def test_valid_session_types(self, session_type):
        IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type=session_type,
            goal="test",
            goal_confidence=0.5,
        )

    def test_invalid_session_type(self):
        with pytest.raises(ValidationError):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="invalid_type",
                goal="test",
                goal_confidence=0.5,
            )

    def test_goal_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="ambiguous",
                goal="test",
                goal_confidence=1.5,
            )

    def test_category_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="ambiguous",
                goal="test",
                goal_confidence=0.5,
                category_confidence=1.5,
            )
