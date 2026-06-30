import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from backend.services.prompt_builder import PromptBuilder
from backend.services.intent_parser import IntentParser, IntentParserError
from backend.application.use_cases.infer_intent import InferIntentUseCase
from backend.services.llm_service import LLMService, LLMServiceError
from backend.domain.entities.intent_record import IntentRecord

pytestmark = pytest.mark.unit


class TestPromptBuilder:
    def test_build_returns_string_with_system_instruction(self):
        pb = PromptBuilder()
        session = {"id": "sess-1", "start_time": "2026-01-01T00:00:00", "duration_seconds": 300, "app_sequence": [], "active_apps": [], "event_count": 1, "screenshot_count": 0}
        prompt = pb.build(session, [])
        assert isinstance(prompt, str)
        assert "SYSTEM INSTRUCTION" in prompt
        assert "SESSION TYPE" in prompt

    def test_build_includes_session_info(self):
        pb = PromptBuilder()
        session = {"id": "sess-abc", "start_time": "2026-06-01T10:00:00", "end_time": "2026-06-01T10:30:00", "duration_seconds": 1800, "app_sequence": ["code", "firefox"], "active_apps": ["code", "firefox"], "event_count": 10, "screenshot_count": 2}
        prompt = pb.build(session, [])
        assert "sess-abc" in prompt
        assert "code" in prompt
        assert "firefox" in prompt
        assert "1800" in prompt

    def test_build_includes_events(self):
        pb = PromptBuilder()
        session = {"id": "sess-1", "start_time": "2026-01-01T00:00:00", "duration_seconds": 300, "app_sequence": [], "active_apps": [], "event_count": 1, "screenshot_count": 0}
        events = [{"timestamp": "2026-01-01T00:00:00", "event_type": "window_focus", "process_name": "code", "window_title": "main.py"}]
        prompt = pb.build(session, events)
        assert "window_focus" in prompt
        assert "code" in prompt
        assert "main.py" in prompt

    def test_build_with_user_context(self):
        pb = PromptBuilder(user_context={"role": "student", "interests": ["programming"]})
        session = {"id": "sess-1", "start_time": "2026-01-01T00:00:00", "duration_seconds": 300, "app_sequence": [], "active_apps": [], "event_count": 1, "screenshot_count": 0}
        prompt = pb.build(session, [])
        assert "student" in prompt
        assert "programming" in prompt

    def test_build_handles_json_string_app_sequence(self):
        pb = PromptBuilder()
        session = {"id": "sess-1", "start_time": "2026-01-01T00:00:00", "duration_seconds": 300, "app_sequence": '["code","terminal"]', "active_apps": [], "event_count": 1, "screenshot_count": 0}
        prompt = pb.build(session, [])
        assert "code" in prompt
        assert "terminal" in prompt


class TestIntentParser:
    def test_parse_valid_response(self):
        parser = IntentParser()
        response = {"session_type": "applied_learning", "goal": "Build feature", "goal_confidence": 0.9, "evidence": ["VS Code open"], "category": "applied_learning", "category_confidence": 0.85}
        record = parser.parse(response, "sess-123")
        assert isinstance(record, IntentRecord)
        assert record.session_type == "applied_learning"
        assert record.goal == "Build feature"
        assert record.goal_confidence == 0.9
        assert record.session_id == "sess-123"

    def test_parse_raises_on_missing_required(self):
        parser = IntentParser()
        with pytest.raises(IntentParserError, match="missing required fields"):
            parser.parse({"session_type": "applied_learning"}, "sess-123")

    def test_parse_raises_on_invalid_session_type(self):
        parser = IntentParser()
        with pytest.raises(IntentParserError, match="Invalid session_type"):
            parser.parse({"session_type": "invalid_type", "goal": "x", "goal_confidence": 0.5, "evidence": [], "category": "x", "category_confidence": 0.0}, "sess-123")

    def test_parse_raises_on_invalid_evidence_type(self):
        parser = IntentParser()
        with pytest.raises(IntentParserError, match="'evidence' must be a list"):
            parser.parse({"session_type": "ambiguous", "goal": "x", "goal_confidence": 0.0, "evidence": "not a list", "category": "ambiguous", "category_confidence": 0.0}, "sess-123")

    def test_parse_with_optional_fields(self):
        parser = IntentParser()
        response = {"session_type": "skill_development", "goal": "Learn Python", "goal_confidence": 0.8, "friction_points": ["slow wifi"], "friction_confidence": 0.3, "tags": ["python", "learning"], "evidence": ["tutorial open"], "category": "skill_development", "category_confidence": 0.75, "alternatives": ["study JS"], "app_summary": {"primary_apps": ["browser"], "total_context_switches": 5, "estimated_typing_intensity": "low"}, "raw_timeline_summary": "Short session"}
        record = parser.parse(response, "sess-456", raw_text='{"session_type": "skill_development"}')
        assert record.session_type == "skill_development"
        assert len(record.friction_points) == 1
        assert record.friction_confidence == 0.3
        assert "python" in record.tags
        assert record.app_summary["primary_apps"] == ["browser"]
        assert record.raw_timeline_summary == "Short session"
        assert record.raw_llm_response == '{"session_type": "skill_development"}'

    def test_parse_handles_none_confidence(self):
        parser = IntentParser()
        response = {"session_type": "personal", "goal": "Check email", "goal_confidence": 0.5, "evidence": ["email client open"], "category": "personal", "category_confidence": 0.5}
        record = parser.parse(response, "sess-789")
        assert record.friction_confidence is None


class TestLLMService:
    def test_parse_json_response_valid(self):
        assert LLMService._parse_json_response('{"a": 1}') == {"a": 1}

    def test_parse_json_response_with_markdown(self):
        assert LLMService._parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}

    def test_parse_json_response_invalid_raises(self):
        with pytest.raises(LLMServiceError, match="Failed to parse"):
            LLMService._parse_json_response("not json")

    def test_init_with_custom_values(self):
        svc = LLMService(api_key="test-key", model="test-model", timeout_sec=30, max_retries=2)
        assert svc.api_key == "test-key"
        assert svc.model == "test-model"

    def test_generate_structured_parses_response(self):
        svc = LLMService(api_key="test-key")
        svc.generate = MagicMock(return_value='{"session_type": "ambiguous"}')
        raw, parsed = svc.generate_structured("test prompt")
        assert raw == '{"session_type": "ambiguous"}'
        assert parsed == {"session_type": "ambiguous"}

    def test_generate_structured_raises_on_bad_json(self):
        svc = LLMService(api_key="test-key")
        svc.generate = MagicMock(return_value="bad json")
        with pytest.raises(LLMServiceError):
            svc.generate_structured("test")


class TestInferIntentUseCase:
    def test_execute_for_session_not_found_returns_none(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value=None)
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=MagicMock(),
            intent_repo=MagicMock(),
            llm_service=MagicMock(),
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        assert use_case.execute_for_session("unknown") is None

    def test_execute_for_session_existing_intent_skips(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value={"id": "sess-1", "status": "closed"})
        mock_intent_repo = MagicMock()
        mock_intent_repo.find_by_session = MagicMock(return_value={"record_id": "existing"})
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=MagicMock(),
            intent_repo=mock_intent_repo,
            llm_service=MagicMock(),
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        assert use_case.execute_for_session("sess-1") is None

    def test_execute_for_session_no_events_skips(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value={"id": "sess-1", "status": "closed"})
        mock_intent_repo = MagicMock()
        mock_intent_repo.find_by_session = MagicMock(return_value=None)
        mock_event_repo = MagicMock()
        mock_event_repo.find_by_session = MagicMock(return_value=[])
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=mock_event_repo,
            intent_repo=mock_intent_repo,
            llm_service=MagicMock(),
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        assert use_case.execute_for_session("sess-1") is None

    def test_execute_for_session_llm_error_returns_none(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value={"id": "sess-1", "status": "closed"})
        mock_intent_repo = MagicMock()
        mock_intent_repo.find_by_session = MagicMock(return_value=None)
        mock_event_repo = MagicMock()
        mock_event_repo.find_by_session = MagicMock(return_value=[{"event_id": "e1"}])
        mock_llm = MagicMock()
        mock_llm.generate_structured.side_effect = Exception("API error")
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=mock_event_repo,
            intent_repo=mock_intent_repo,
            llm_service=mock_llm,
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        assert use_case.execute_for_session("sess-1") is None

    def test_execute_for_session_parser_error_returns_none(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value={"id": "sess-1", "status": "closed"})
        mock_intent_repo = MagicMock()
        mock_intent_repo.find_by_session = MagicMock(return_value=None)
        mock_event_repo = MagicMock()
        mock_event_repo.find_by_session = MagicMock(return_value=[{"event_id": "e1"}])
        mock_llm = MagicMock()
        mock_llm.generate_structured.return_value = ('{"bad": "json"}', {"bad": "json"})
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception("parse error")
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=mock_event_repo,
            intent_repo=mock_intent_repo,
            llm_service=mock_llm,
            prompt_builder=MagicMock(),
            intent_parser=mock_parser,
        )
        assert use_case.execute_for_session("sess-1") is None

    def test_execute_for_session_success(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_by_id = MagicMock(return_value={"id": "sess-1", "status": "closed"})
        mock_intent_repo = MagicMock()
        mock_intent_repo.find_by_session = MagicMock(return_value=None)
        mock_event_repo = MagicMock()
        mock_event_repo.find_by_session = MagicMock(return_value=[{"event_id": "e1", "timestamp": "2026-01-01T00:00:00"}])

        mock_intent = IntentRecord(
            record_id="r1", session_id="sess-1",
            timestamp=datetime.now(timezone.utc),
            session_type="applied_learning", goal="Build feature",
            goal_confidence=0.85, evidence=["VS Code open"],
            category="applied_learning", category_confidence=0.8,
        )

        mock_llm = MagicMock()
        mock_llm.generate_structured.return_value = ('{}', {})
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_intent

        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=mock_event_repo,
            intent_repo=mock_intent_repo,
            llm_service=mock_llm,
            prompt_builder=MagicMock(),
            intent_parser=mock_parser,
        )

        result = use_case.execute_for_session("sess-1")
        assert result is not None
        assert result.session_type == "applied_learning"
        assert result.goal == "Build feature"
        mock_intent_repo.create.assert_called_once()

    def test_execute_for_all_closed_counts_processed(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_all = MagicMock(return_value=[{"id": "sess-1"}, {"id": "sess-2"}])
        intent1 = IntentRecord(record_id="r1", session_id="sess-1", timestamp=datetime.now(timezone.utc), session_type="applied_learning", goal="test", goal_confidence=0.5, evidence=[], category="applied_learning", category_confidence=0.5)
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=MagicMock(),
            intent_repo=MagicMock(),
            llm_service=MagicMock(),
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        use_case.execute_for_session = MagicMock(side_effect=[intent1, None])
        assert use_case.execute_for_all_closed() == 1

    def test_execute_for_all_closed_zero_when_none(self):
        mock_session_repo = MagicMock()
        mock_session_repo.find_all = MagicMock(return_value=[])
        use_case = InferIntentUseCase(
            session_repo=mock_session_repo,
            event_repo=MagicMock(),
            intent_repo=MagicMock(),
            llm_service=MagicMock(),
            prompt_builder=MagicMock(),
            intent_parser=MagicMock(),
        )
        assert use_case.execute_for_all_closed() == 0
