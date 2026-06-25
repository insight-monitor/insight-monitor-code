"""Tests for Pydantic model validation (RawEvent, IntentRecord)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.domain.entities.raw_event import RawEvent, EventType
from backend.domain.entities.intent_record import IntentRecord


class TestRawEvent:
    """RawEvent model — required fields, optional fields, type validation."""

    def test_should_accept_valid_event_with_all_fields(self):
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

    def test_should_accept_event_with_only_required_fields(self):
        event = RawEvent(
            event_id=str(uuid4()),
            event_type=EventType.SCREENSHOT,
            timestamp=datetime.now(timezone.utc),
            source="capture-agent",
        )
        assert event.window_title is None
        assert event.clicks_per_min is None

    def test_should_reject_invalid_event_type(self):
        with pytest.raises(ValidationError, match="event_type"):
            RawEvent(
                event_id=str(uuid4()),
                event_type="invalid",
                timestamp=datetime.now(timezone.utc),
                source="test",
            )

    def test_should_reject_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RawEvent()


class TestIntentRecord:
    """IntentRecord model — session types, confidence ranges, field validation."""

    def test_should_accept_valid_intent_record(self):
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
        "skill_development",
        "applied_learning",
        "peer_collaboration",
        "ambiguous",
        "personal",
    ])
    def test_should_accept_all_valid_session_types(self, session_type):
        IntentRecord(
            record_id=str(uuid4()),
            session_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_type=session_type,
            goal="test",
            goal_confidence=0.5,
        )

    def test_should_reject_invalid_session_type(self):
        with pytest.raises(ValidationError, match="session_type"):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="invalid_type",
                goal="test",
                goal_confidence=0.5,
            )

    def test_should_reject_goal_confidence_above_one(self):
        with pytest.raises(ValidationError, match="goal_confidence"):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="ambiguous",
                goal="test",
                goal_confidence=1.5,
            )

    def test_should_reject_category_confidence_above_one(self):
        with pytest.raises(ValidationError, match="category_confidence"):
            IntentRecord(
                record_id=str(uuid4()),
                session_id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                session_type="ambiguous",
                goal="test",
                goal_confidence=0.5,
                category_confidence=1.5,
            )
