"""Settings, read from environment variables (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else value


@dataclass(frozen=True)
class Settings:
    # Qdrant
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", ""))
    qdrant_api_key: str | None = field(default_factory=lambda: _env("QDRANT_API_KEY"))
    collection: str = field(default_factory=lambda: _env("QDRANT_COLLECTION", "sentinel_corpus"))

    # Embeddings
    provider: str = field(default_factory=lambda: _env("EMBED_PROVIDER", "google").lower())  # google | euri | fake
    embed_model: str = field(default_factory=lambda: _env("EMBED_MODEL", "gemini-embedding-2"))
    embed_dim: int = field(default_factory=lambda: int(_env("EMBED_DIM", "3072")))
    embed_batch_size: int = field(default_factory=lambda: int(_env("EMBED_BATCH_SIZE", "16")))
    embed_pause_s: float = field(default_factory=lambda: float(_env("EMBED_PAUSE_SECONDS", "0.5")))
    gemini_api_key: str | None = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    euri_api_key: str | None = field(default_factory=lambda: _env("EURI_API_KEY"))
    euri_base_url: str = field(default_factory=lambda: _env("EURI_BASE_URL", "https://api.euron.one/api/v1/euri"))

    # Chunking
    chunk_size: int = field(default_factory=lambda: int(_env("CHUNK_SIZE", "900")))
    chunk_overlap: int = field(default_factory=lambda: int(_env("CHUNK_OVERLAP", "150")))

    # Paths
    raw_dir: Path = ROOT / "data" / "raw"
    processed_dir: Path = ROOT / "data" / "processed"
    cache_dir: Path = ROOT / "data" / "cache"
    results_dir: Path = ROOT / "results"


def get_settings() -> Settings:
    return Settings()
