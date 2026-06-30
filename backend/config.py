import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


class Settings:
    def __init__(self):
        self.db_path: str = os.getenv(
            "INSIGHT_DB_PATH",
            str(Path(__file__).resolve().parent / "data" / "insight_monitor.db"),
        )
        self.cors_origins: list[str] = os.getenv(
            "INSIGHT_CORS_ORIGINS",
            "http://localhost:5173",
        ).split(",")
        self.api_version: str = os.getenv("INSIGHT_API_VERSION", "0.1.0")
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
        self.api_key: str | None = os.getenv("API_KEY")
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.llm_base_url: str | None = os.getenv("LLM_BASE_URL")
        self.inference_timeout_sec: int = int(
            os.getenv("INFERENCE_TIMEOUT_SEC", "30")
        )
        self.inference_max_retries: int = int(
            os.getenv("INFERENCE_MAX_RETRIES", "3")
        )
        self.session_inactivity_gap_min: int = int(
            os.getenv("SESSION_INACTIVITY_GAP_MIN", "8")
        )


settings = Settings()
