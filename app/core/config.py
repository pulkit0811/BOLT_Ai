from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    provider: str = "mock"
    model: str = "gpt-5.5"
    endpoint: str = ""
    timeout: float = 60.0
    streaming: bool = True
    api_key: str = ""

    @classmethod
    def from_environment(cls) -> AppConfig:
        return cls(
            provider=os.getenv("AI_PROVIDER", "mock").strip().lower() or "mock",
            model=os.getenv("AI_MODEL", "gpt-5.5").strip() or "gpt-5.5",
            endpoint=os.getenv("AI_API_ENDPOINT", "").strip(),
            timeout=_read_timeout(os.getenv("AI_REQUEST_TIMEOUT", "60")),
            streaming=_read_bool(os.getenv("AI_STREAMING", "true")),
            api_key=os.getenv("AI_API_KEY", "").strip(),
        )

    @staticmethod
    def default_database_path() -> Path:
        root = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or str(Path.home())
        return Path(root) / "BoltAI" / "bolt_ai.db"


def _read_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_timeout(value: str) -> float:
    try:
        return max(5.0, min(300.0, float(value)))
    except ValueError:
        return 60.0
