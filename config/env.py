import os
from pathlib import Path

from dotenv import load_dotenv


def load_env(env_path: Path | None = None) -> None:
    """Load environment variables from the project .env file."""
    if env_path is None:
        project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / ".env"

    load_dotenv(env_path)


def get_env(key: str, *, required: bool = True) -> str | None:
    """Read an environment variable, optionally raising if missing."""
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value
