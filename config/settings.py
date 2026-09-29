import os
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr


class Settings(BaseModel):
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    max_react_steps: int = Field(default=3, ge=1, le=10)
    event_store_path: Path = Path("simulation_events.jsonl")
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        key = os.getenv("DEEPSEEK_API_KEY")
        return cls(
            deepseek_api_key=SecretStr(key) if key else None,
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            event_store_path=Path(os.getenv("EVENT_STORE_PATH", "simulation_events.jsonl")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
