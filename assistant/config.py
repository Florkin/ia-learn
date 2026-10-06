"""Course settings, read from the environment and an optional .env file at the repository root."""

import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / ".data"
CORPUS_DIR = ROOT / "corpus"

OLLAMA_URL = "http://localhost:11434/v1"
OPENROUTER_URL = "https://openrouter.ai/api/v1"


def _load_dotenv(path: Path) -> None:
    """Minimal .env reader: KEY=VALUE lines, # comments. Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _env(name: str, default: str = "") -> str:
    # An empty value in .env means "use the default".
    return os.environ.get(name) or default


@dataclass(frozen=True)
class Settings:
    learner: str
    chat_base_url: str
    chat_api_key: str
    chat_model: str
    embed_base_url: str
    embed_api_key: str
    embed_model: str
    openrouter_api_key: str
    hosted_models: tuple[str, ...]
    finetune_backend: str
    finetune_iters: int


def load_settings() -> Settings:
    _load_dotenv(ROOT / ".env")
    apple_silicon = sys.platform == "darwin" and platform.machine() == "arm64"
    hosted = _env("HOSTED_MODELS", "openai/gpt-6-luna,qwen/qwen3.7-flash,anthropic/claude-sonnet-5.5")
    return Settings(
        learner=_env("LEARNER"),
        chat_base_url=_env("CHAT_BASE_URL", OLLAMA_URL),
        chat_api_key=_env("CHAT_API_KEY", "ollama"),
        chat_model=_env("CHAT_MODEL", "granite4.1:3b"),
        embed_base_url=_env("EMBED_BASE_URL", OLLAMA_URL),
        embed_api_key=_env("EMBED_API_KEY", "ollama"),
        embed_model=_env("EMBED_MODEL", "bge-m3"),
        openrouter_api_key=_env("OPENROUTER_API_KEY"),
        hosted_models=tuple(m.strip() for m in hosted.split(",") if m.strip()),
        finetune_backend=_env("FINETUNE_BACKEND", "mlx" if apple_silicon else "peft"),
        finetune_iters=int(_env("FINETUNE_ITERS", "200")),
    )


settings = load_settings()
