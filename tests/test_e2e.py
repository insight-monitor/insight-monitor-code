"""End-to-end test: Capture → API → store → retrieve → display."""
import pytest
from unittest.mock import MagicMock
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from fastapi.testclient import TestClient

from backend.config import settings
from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import EventRepository, SessionRepository, IntentRepository


@pytest.mark.integration
def test_e2e_session_flow(tmp_path, monkeypatch):
    """Test full flow: create session → send events → close → inference → retrieve."""
    db_path = str(tmp_path / "test_e2e.db")
    settings.db_path = db_path

    from backend.main import app
    from backend.pipeline.inference_pipeline import InferencePipeline
    from backend.services.llm_service import LLMService

    db = Database(db_path)
    event_repo = EventRepository(db)
    session_repo = SessionRepository(db)
    intent_repo = IntentRepository(db)

    import backend.routes.events
    import backend.routes.sessions
    backend.routes.events.event_repo = event_repo
    backend.routes.sessions.session_repo = session_repo
    backend.routes.sessions.event_repo = event_repo
    backend.routes.sessions.intent_repo = intent_repo

    with TestClient(app) as client:
        session_id = f"e2e-session-{uuid4()}"

        session_repo.create({
            "id": session_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "app_sequence": [],
            "event_count": 0,
            "screenshot_count": 0,
            "avg_clicks_per_min": None,
            "avg_keystrokes_per_min": None,
            "active_apps": [],
            "status": "open",
        })

        event_ids = []
        for i in range(3):
            eid = str(uuid4())
            event_ids.append(eid)
            resp = client.post("/events", json={
                "event_id": eid,
                "event_type": "window_focus",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "e2e-test",
                "window_title": f"Test window {i}",
                "process_name": "code",
                "pid": 1234,
                "session_id": session_id,
            })
            assert resp.status_code == 200, f"Failed to post event: {resp.text}"

        get_resp = client.get("/events?limit=10")
        assert get_resp.status_code == 200
        assert len(get_resp.json()["events"]) >= 3

        close_resp = client.post(f"/sessions/{session_id}/close")
        assert close_resp.status_code == 200
        assert close_resp.json()["status"] == "closed"

        mock_llm = MagicMock(spec=LLMService)
        mock_llm.generate_structured.return_value = (
            '{"session_type": "applied_learning"}',
            {
                "session_type": "applied_learning",
                "goal": "Development session",
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
            },
        )

        pipeline = InferencePipeline(db, llm_service=mock_llm)
        intent = pipeline.process_session(session_id)
        assert intent is not None, "Inference should return an IntentRecord"
        assert intent.session_type in ("skill_development", "applied_learning", "peer_collaboration", "ambiguous", "personal")
        assert 0.0 <= intent.goal_confidence <= 1.0
        assert intent.goal is not None

        session_detail = client.get(f"/sessions/{session_id}").json()
        assert "intent" in session_detail, "Session should have intent after inference"
        assert session_detail["intent"]["session_type"] == intent.session_type
        assert session_detail["intent"]["goal"] == intent.goal
        assert session_detail["session_type"] == intent.session_type
        assert session_detail["goal"] == intent.goal
        assert session_detail["confidence"] == intent.goal_confidence

        sessions_list = client.get("/sessions").json()
        assert sessions_list["count"] >= 1
        found = next((s for s in sessions_list["sessions"] if s["id"] == session_id), None)
        assert found is not None, "Session should appear in list"
        assert found["session_type"] == intent.session_type
        assert found["goal"] == intent.goal
        assert found["confidence"] == intent.goal_confidence

        intent_only = client.get(f"/sessions/{session_id}/intent").json()
        assert intent_only["session_id"] == session_id
        assert intent_only["record_id"] is not None

    settings.db_path = str(BASE / "backend" / "data" / "insight_monitor.db")