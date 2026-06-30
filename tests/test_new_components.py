import pytest
import sys
from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from backend.services.llm_service import LLMService, LLMServiceError
from backend.services.prompt_builder import PromptBuilder
from backend.services.intent_parser import IntentParser, IntentParserError
from backend.application.use_cases.infer_intent import InferIntentUseCase
from backend.infrastructure.db.sqlite.database import Database


@pytest.mark.unit
def test_llm_parse_json_response():
    valid = '{"a": 1}'
    assert LLMService._parse_json_response(valid) == {"a": 1}

    with_markdown = '```json\n{"a": 1}\n```'
    assert LLMService._parse_json_response(with_markdown) == {"a": 1}

    invalid = "not json"
    try:
        LLMService._parse_json_response(invalid)
        assert False, "Should have raised LLMServiceError"
    except LLMServiceError:
        pass


@pytest.mark.unit
def test_llm_service_init():
    svc = LLMService(api_key="dummy_key")
    assert svc.api_key == "dummy_key"
    assert svc.model is not None


@pytest.mark.unit
def test_prompt_builder_build():
    pb = PromptBuilder()
    session = {
        "id": "test-session",
        "start_time": "2026-01-01T00:00:00",
        "end_time": "2026-01-01T00:30:00",
        "duration_seconds": 1800,
        "app_sequence": ["code", "firefox"],
        "active_apps": ["code", "firefox"],
        "event_count": 5,
        "screenshot_count": 0,
    }
    events = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_type": "window_focus",
            "process_name": "code",
            "window_title": "main.py",
        }
    ]
    prompt = pb.build(session, events)
    assert isinstance(prompt, str)
    assert "SYSTEM INSTRUCTION" in prompt
    assert "SESSION TYPE (the primary classification)" in prompt
    assert "CATEGORY (a secondary, more specific classification)" in prompt
    assert "test-session" in prompt
    assert "OUTPUT FORMAT" in prompt
    assert "session_type" in prompt
    assert "goal_confidence" in prompt


@pytest.mark.unit
def test_intent_parser_success():
    parser = IntentParser()
    response = {
        "session_type": "applied_learning",
        "goal": "Build API endpoint",
        "goal_confidence": 0.85,
        "evidence": ["VS Code open for 30 min"],
        "category": "applied_learning",
        "category_confidence": 0.8,
    }
    record = parser.parse(response, "sess-123")
    assert record.session_type == "applied_learning"
    assert record.goal == "Build API endpoint"
    assert record.goal_confidence == 0.85
    assert record.session_id == "sess-123"


@pytest.mark.unit
def test_intent_parser_missing_required():
    parser = IntentParser()
    try:
        parser.parse({"session_type": "applied_learning"}, "sess-123")
        assert False, "Should have raised IntentParserError"
    except IntentParserError:
        pass


@pytest.mark.unit
def test_intent_parser_invalid_type():
    parser = IntentParser()
    try:
        parser.parse(
            {
                "session_type": "invalid_type",
                "goal": "test",
                "goal_confidence": 0.5,
                "evidence": [],
            },
            "sess-123",
        )
        assert False, "Should have raised IntentParserError"
    except IntentParserError:
        pass


@pytest.mark.integration
def test_infer_intent_use_case_process_session(tmp_path):
    db_path = str(tmp_path / "test_infer.db")
    db = Database(db_path)

    from backend.infrastructure.db.sqlite.repositories import SessionRepository, EventRepository, IntentRepository
    SessionRepo = SessionRepository
    EventRepo = EventRepository
    IntentRepo = IntentRepository

    SessionRepo(db).create(
        {
            "id": "sess-123",
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-01T00:30:00",
            "duration_seconds": 1800.0,
            "app_sequence": [],
            "event_count": 1,
            "screenshot_count": 0,
            "avg_clicks_per_min": None,
            "avg_keystrokes_per_min": None,
            "active_apps": [],
            "session_type": None,
            "goal": None,
            "confidence": None,
            "status": "closed",
        }
    )

    EventRepo(db).insert(
        {
            "event_id": str(uuid4()),
            "event_type": "window_focus",
            "timestamp": "2026-01-01T00:00:00",
            "source": "test",
            "window_title": "Test",
            "process_name": "code",
            "pid": 123,
            "screenshot_path": None,
            "screenshot_thumbnail": None,
            "clicks_per_min": None,
            "keystrokes_per_min": None,
            "url": None,
            "browser_tab_title": None,
            "session_id": "sess-123",
            "session_boundary_type": None,
        }
    )

    mock_llm = MagicMock(spec=LLMService)
    mock_response = {
        "session_type": "applied_learning",
        "goal": "Build API endpoint",
        "goal_confidence": 0.85,
        "evidence": ["VS Code open"],
        "friction_points": [],
        "friction_confidence": None,
        "category": "applied_learning",
        "category_confidence": 0.8,
        "tags": [],
        "alternatives": [],
        "app_summary": {},
        "raw_timeline_summary": "",
    }
    mock_llm.generate_structured.return_value = (
        '{"session_type": "applied_learning"}',
        mock_response,
    )

    pipeline = InferIntentUseCase(
        session_repo=SessionRepo(db),
        event_repo=EventRepo(db),
        intent_repo=IntentRepo(db),
        llm_service=mock_llm,
        prompt_builder=PromptBuilder(),
        intent_parser=IntentParser(),
    )
    result = pipeline.execute_for_session("sess-123")

    assert result is not None
    assert result.session_type == "applied_learning"
    assert result.goal == "Build API endpoint"
    assert result.goal_confidence == 0.85

    stored = IntentRepo(db).find_by_session("sess-123")
    assert stored is not None
    assert stored["session_type"] == "applied_learning"
    assert stored["goal"] == "Build API endpoint"


if __name__ == "__main__":
    print("=" * 60)
    print("Testing new backend components")
    print("=" * 60)

    test_llm_parse_json_response()
    print("[OK] LLMService._parse_json_response")

    test_llm_service_init()
    print("[OK] LLMService.__init__")

    test_prompt_builder_build()
    print("[OK] PromptBuilder.build")

    test_intent_parser_success()
    print("[OK] IntentParser.parse success")

    test_intent_parser_missing_required()
    print("[OK] IntentParser.parse missing required fields")

    test_intent_parser_invalid_type()
    print("[OK] IntentParser.parse invalid session_type")

    # Note: Integration test requires pytest tmp_path fixture
    # test_infer_intent_use_case_process_session()
    # print("[OK] InferIntentUseCase.execute_for_session")

    print("=" * 60)
    print("All unit tests passed")
    print("=" * 60)