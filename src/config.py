import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def _list_env(name: str) -> List[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class AppConfig:
    email: str = field(default_factory=lambda: os.getenv("BETTER_EMAIL", ""))
    password: str = field(default_factory=lambda: os.getenv("BETTER_PASSWORD", ""))
    headless: bool = field(default_factory=lambda: _bool_env("BETTER_HEADLESS", False))
    user_data_dir: str = field(
        default_factory=lambda: os.getenv("BETTER_USER_DATA_DIR", "./.chromium-profile")
    )
    venue_name: str = field(default_factory=lambda: os.getenv("BETTER_VENUE", "Sugden Sports Centre"))
    preferred_times: List[str] = field(default_factory=lambda: _list_env("BETTER_PREFERRED_TIMES"))
    polling_start: str = field(default_factory=lambda: os.getenv("BETTER_POLLING_START", "21:59:55"))
    target_days_ahead: int = field(default_factory=lambda: int(os.getenv("BETTER_DAYS_AHEAD", "7")))
    base_url: str = field(default_factory=lambda: os.getenv("BETTER_BASE_URL", "https://www.better.org.uk/"))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("BETTER_TIMEOUT", "20")))

    def validate(self) -> None:
        missing = []
        if not self.email:
            missing.append("BETTER_EMAIL")
        if not self.password:
            missing.append("BETTER_PASSWORD")
        if missing:
            raise ValueError(f"缺少必要环境变量: {', '.join(missing)}")
